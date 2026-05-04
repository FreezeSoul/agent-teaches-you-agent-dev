# Codex Agent Loop 内部架构：Harness 工程实践深度解读

## 核心论点

OpenAI 的 Codex CLI 不是简单地将 LLM 包装成"问答式"工具，而是一套精密的 **Agent Harness 架构**——它将模型推理、工具调用、上下文管理、状态持久化组合为统一的执行循环。理解这个循环的内部机制，是理解"为什么有的 Agent 能可靠地完成数小时复杂任务，而有的连一个完整功能都写不出来"的关键。

---

## 1. Agent Loop 的本质：不止于"问-答-循环"

### 1.1 传统认知 vs 工程现实

大多数人对 Agent Loop 的理解是：

```
用户输入 → LLM 推理 → LLM 输出 → 执行工具 → 循环
```

这个图足够准确，但隐藏了工程实现中的关键复杂性。Codex 的官方博客明确指出：

> "At the heart of every AI agent is something called 'the agent loop.' A simplified illustration of the agent loop looks like this..."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

但 Codex 的实现远比"简化图"复杂。它涉及：
- **多层次的 Prompt 构建**（system / developer / user / assistant 角色的优先级控制）
- **SSE 流式事件处理**（`response.output_item.added` 等事件如何转换为下一轮输入）
- **上下文窗口的动态管理**（随对话增长，Prompt 长度线性膨胀）
- **Prompt Caching 机制**（利用"旧 Prompt 是新 Prompt 的前缀"这一特性实现缓存）

### 1.2 Codex 的三层执行上下文

Codex 执行一次完整的 Agent Turn，需要三层信息输入：

```json
{
  "instructions": "system/developer 消息，模型上下文的核心控制",
  "tools": "模型可调用的工具列表（含 MCP servers、自定义工具）",
  "input": [
    {"type": "message", "role": "developer", "content": "沙箱描述（仅限 Codex shell tool）"},
    {"type": "message", "role": "developer", "content": "用户 config.toml 中的 developer_instructions"},
    {"type": "message", "role": "user", "content": "AGENTS.md / AGENTS.override.md 聚合内容"},
    {"type": "message", "role": "user", "content": "Skill metadata + 使用说明"},
    {"type": "message", "role": "user", "content": "用户原始输入"}
  ]
}
```

官方原文的关键设计决策：

> "Every element of input is a JSON object with type, role, and content. The role indicates how much weight the associated content should have and is one of the following values (in decreasing order of priority): system, developer, user, assistant."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

这说明 **角色优先级是服务器端决定的**，而非客户端。这种设计让 OpenAI 可以在不修改客户端的情况下调整模型的注意力分配策略。

---

## 2. Prompt 构建的工程细节

### 2.1 为什么 Prompt 不是"一句话"？

对于最终用户，Codex 的输入就是一条自然语言指令。但在 Harness 层面，这条指令被拆解为多个独立的 `input item`，按优先级排列：

| 优先级 | Role | 来源 | 何时包含 |
|--------|------|------|---------|
| 1 | `developer` | sandbox mode 模板（workspace_write.md / on_request.md） | 始终（仅影响 Codex shell tool） |
| 2 | `developer` | `config.toml` 的 `developer_instructions` | 可选 |
| 3 | `user` | `AGENTS.override.md` / `AGENTS.md` | 存在时 |
| 4 | `user` | `project_doc`（从 Git 根目录向上搜索） | subject to 32 KiB limit |
| 5 | `user` | Skill metadata + 使用说明 | 配置了 skills 时 |
| 6 | `user` | 用户原始消息 | 始终 |

官方原文说明了这种分层的目的：

> "In general, more specific instructions appear later: Contents of AGENTS.override.md and AGENTS.md in $CODEX_HOME... look in each folder from the Git/project root of the cwd up to the cwd itself..."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

这意味着 **越靠近用户输入的指令权重越高**——项目级 AGENTS.md 覆盖全局 AGENTS.md，Skill metadata 覆盖项目级配置。这是一个精密的覆盖（override）机制，而非简单的拼接。

### 2.2 Skill System 的引入

当用户配置了 Skills 时，Codex 会自动在 Prompt 中插入：

1. 一段关于如何使用 Skills 的前言（preamble）
2. 每个 Skill 的 metadata（描述、功能、适用场景）
3. Skill 的详细使用说明

官方原文描述了这个机制的实现位置：

> "If any skills have been configured: a short preamble about skills, the skill metadata for each skill, a section on how to use skills."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

这个设计让 Skills 可以在不修改核心 Agent Loop 的前提下扩展模型的能力边界——Skills 是 Prompt 层级的扩展，而非修改模型本身。

---

## 3. SSE 流式事件与状态转换

### 3.1 服务器返回的不是"最终答案"

Codex 使用 **Server-Sent Events（SSE）** 接收模型的响应。关键在于：模型返回的是**增量事件流**，而非一次性完整输出。

每个事件都有 `type`，Codex 将这些事件转换为内部事件对象：

- `response.output_text.delta` → 用于 UI 流式显示
- `response.output_item.added` → 追加到下一轮 Prompt 的输入中

### 3.2 工具调用的状态保存

当模型请求调用工具时，Codex 执行工具并将结果追加到 Prompt 中。官方描述了这个过程：

> "Suppose the first request to the Responses API includes two response.output_item.done events: one with type=reasoning and one with type=function_call. These events must be represented in the input field of the JSON when we query the model again with the response to the tool call."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

这个机制意味着：**每一轮的工具调用和结果，都被完整记录在 Prompt 历史中**，模型可以基于完整的执行轨迹做出决策。

### 3.3 关键设计：Prompt 前缀特性

官方指出了一个极其重要的实现细节：

> "Note that the old prompt is an exact prefix of the new prompt. This is intentional, as this makes subsequent requests much more efficient because it enables us to take advantage of prompt caching."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

这解释了为什么 Codex 的实现不使用 `previous_response_id` 参数——**通过让新 Prompt 完全包含旧 Prompt，服务器可以利用 KV-Cache 加速后续推理**。这是一种在"无状态请求"和"上下文连续性"之间取得平衡的工程选择。

---

## 4. 上下文窗口管理的挑战

### 4.1 对话增长是 O(n) 的问题

官方直接承认了这个架构的代价：

> "You might be asking yourself, 'Wait, isn't the agent loop quadratic in terms of the amount of JSON sent to the Responses API over the course of the conversation?' And you would be right."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

每一次工具调用都会将结果追加到 Prompt 中，导致：
- 第 1 轮：发送 `P` tokens
- 第 2 轮：发送 `P + T1` tokens
- 第 3 轮：发送 `P + T1 + T2` tokens
- ...
- 第 N 轮：发送 `P + (N-1) * avg_tool_output` tokens

这意味着**长周期任务的成本随工具调用次数线性增长**，且存在上下文窗口耗尽的风险。

### 4.2 为什么不使用 previous_response_id？

OpenAI 的 Responses API 提供了 `previous_response_id` 参数来解决这个问题，但 Codex 主动选择不使用它：

> "While the Responses API does support an optional previous_response_id parameter to mitigate this issue, Codex does not use it today, primarily to keep requests fully stateless and to s..."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

官方选择**无状态请求**的代价是上下文重复传输，收益是**服务端状态管理的复杂性被彻底消除**。这是一个典型的工程权衡：性能 vs 可调试性/可部署性。

---

## 5. 多工具集成：MCP 的角色

### 5.1 工具来源的三层结构

Codex 的工具系统不只有内置工具，还支持外部扩展：

```
工具来源：
1. Codex CLI 内置工具（shell, read, edit, etc.）
2. Responses API 原生工具（由 OpenAI 服务器提供）
3. MCP Servers（用户通过 MCP 协议接入的自定义工具）
```

官方原文明确说明了 MCP 的定位：

> "For Codex, this includes tools that are provided by the Codex CLI, tools that are provided by the Responses API that should be made available to Codex, as well as tools provided by the user, usually via MCP servers."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

### 5.2 沙箱安全的边界

一个容易被忽视的安全设计：只有 Codex 内置的 shell tool 被沙箱化，MCP 工具**不在 Codex 的沙箱保护范围内**：

> "That message is built from a template... other tools, such as those provided from MCP servers, are not sandboxed by Codex and are responsible for enforcing their own guardrails."
> — [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

这是 MCP 集成中的**安全边界意识**：如果 MCP 工具需要沙箱保护，该工具自身必须实现相应的安全机制。

---

## 6. 与 OpenAI Agents SDK 新增能力的关联

### 6.1 官方 Harness 的升级方向

OpenAI 同期发布的 Agents SDK 更新，揭示了官方对 Harness 工程化的理解：

> "The updated Agents SDK harness becomes more capable for agents that work with documents, files, and systems. It now has configurable memory, sandbox-aware orchestration, Codex-like filesystem tools, and standardized integrations with primitives that are becoming common in frontier agent systems."
> — [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这与 Codex Agent Loop 的设计高度一致：
- **Configurable memory** → 对应 Prompt 构建中的 `input` 聚合
- **Sandbox-aware orchestration** → 对应 `developer` role 沙箱描述机制
- **Codex-like filesystem tools** → 复用了 Codex 的工具设计经验

### 6.2 行业共识：Harness 是差异化壁垒

OpenAI 的官方表述揭示了一个行业现实：

> "Model-agnostic frameworks are flexible but do not fully utilize frontier models capabilities; model-provider SDKs can be closer to the model but often lack enough visibility into the harness; and managed agent APIs can simplify deployment but constrain where agents run and how they access sensitive data."
> — [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这说明 **Harness 工程是 AI Agent 系统的核心差异化**：
- 模型能力（Foundation Model）大家都能用 API 调用
- 但如何管理上下文、如何调度工具、如何保持状态，是每个 Agent 系统的独特壁垒

---

## 7. 对 Agent 开发者的启示

### 7.1 为什么理解 Harness 很重要？

笔者认为，理解 Agent Loop 的内部机制，对开发者有三个直接价值：

**① 能诊断"模型很强但 Agent 不可靠"的问题**
当你的 Agent 在长任务中表现不稳定时，问题很可能不在模型，而在 Harness 的上下文管理策略——是否设置了 32KiB 的 project_doc 上限？是否在合适时机清理历史？

**② 能设计更有效的 Skill/Instruction**
了解"more specific instructions appear later"的优先级规则，开发者可以精准控制模型的注意力分配——把关键约束放在项目级 AGENTS.md，而非全局配置。

**③ 能评估不同 Agent 框架的取舍**
OpenAI 选择"无状态 + 全量 Prompt 传输"而放弃 `previous_response_id`，意味着什么？意味着他们在**可调试性/简单性**和**性能/成本**之间做了明确选择。其他框架可能有不同的取舍。

### 7.2 一个具体的检查清单

基于本文分析，开发者可以自检：

- [ ] 你的项目 AGENTS.md 是否覆盖了全局 AGENTS.md 中的默认行为？
- [ ] 你的 MCP 工具是否实现了自己的沙箱/安全机制？
- [ ] 你的长周期任务是否在 32KiB project_doc limit 之内？
- [ ] 你的工具调用结果是否作为完整事件流被记录在 Prompt 历史中？

---

## 总结

Codex Agent Loop 的工程实现揭示了一个核心命题：**LLM 本身不构成可靠的软件工程 Agent，Harness 才是**。OpenAI 的实现中：

1. **Prompt 是分层组装的**（role 优先级由服务器控制）
2. **状态通过全量 Prompt 历史维护**（而非依赖 previous_response_id）
3. **工具调用被完整记录在执行轨迹中**（支持模型基于历史决策）
4. **MCP 工具的安全边界需要工具自身负责**（Harness 只保护内置工具）

这些设计决策，每一条都是工程权衡的结果。理解它们，比学习任何一个"最佳 Prompt 模板"都更有价值。