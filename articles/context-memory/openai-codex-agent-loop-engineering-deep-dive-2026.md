# OpenAI Codex Agent Loop 工程解析：上下文管理、Compaction 与 Prompt Caching 的深度实现

## 核心主张

本文要证明：Codex CLI 的核心工程挑战不是"如何调用模型"，而是**如何在有限上下文窗口内维持一个可持续运转的 Agent 循环**。OpenAI 的解法不是让模型更聪明，而是让 Harness 承担更多责任——通过精心设计的 Prompt Caching、Compaction 机制和上下文窗口管理，让 Agent 在数百个 Turn 的长程任务中依然保持上下文连贯性。

## 一、问题的本质：Agent Loop 的代价是上下文膨胀

OpenAI 在博客中直白地指出：

> "Because the agent can execute tool calls that modify the local environment, its 'output' is not limited to the assistant message. In many cases, the primary output of a software agent is the code it writes or edits on your machine."

这段话点出了软件 Agent 的本质矛盾：**每一次 Turn 的"输出"不仅是消息，还包括对本地环境的修改**——新建文件、修改配置、执行测试。这些副作用让 Agent 的工作具有累积性，但也让上下文窗口成为一个不断膨胀的容器。

具体来说，每一次 Turn 包含：
1. 用户输入（追加到对话历史）
2. Assistant 消息（包含上一 Turn 的最终回复）
3. 所有 Tool Call 及其结果（一个 Turn 可能产生几十甚至上百个 Tool Call）

> "You might be asking yourself, 'Wait, isn't the agent loop quadratic in terms of the amount of JSON sent to the Responses API over the course of the conversation?' And you would be right."

**这就是 Codex 面对的核心工程问题**：Agent Loop 的代价是 O(n²) 的 token 增长，而 API 的上下文窗口有硬性上限。

## 二、Codex 的 Prompt 构建机制

### 2.1 三层输入结构

Codex 不是简单地把用户输入塞给模型，而是构建了一个**分层结构的 Prompt**。每个 Inference 请求的 JSON Payload 包含三个关键字段：

```json
{
  "instructions": "system/developer message - 框架级系统提示",
  "tools": "[Tool1, Tool2, ...] - 模型可调用的工具列表",
  "input": "[Item1, Item2, ...] - 对话历史 + 用户输入"
}
```

在 Input 层面，Codex 在发送用户消息之前会插入以下内容（按优先级排序）：

1. **Developer Message（role=developer）**：描述沙箱配置，**仅适用于 Codex 提供的 Shell 工具**，MCP 工具需自行负责 Guardrails
2. **Developer Instructions（Optional）**：来自用户 `config.toml` 的 `developer_instructions`
3. **User Instructions（Optional）**：从多个来源聚合的用户指令：
   - `$CODEX_HOME` 下的 `AGENTS.override.md` 和 `AGENTS.md`
   - 从 Git 根目录到当前目录路径上每个文件夹的配置文件（最多 32 KiB）
   - Skills 相关的元数据和说明

> "In general, more specific instructions appear later: Contents of AGENTS.override.md and AGENTS.md in $CODEX_HOME... If any skills have been configured: a short preamble about skills, the skill metadata for each skill, a section on how to use skills."

**这个设计揭示了一个关键原则**：Prompt 中越具体的信息越靠后，因为模型对上下文的权重分布是不均匀的——**越靠后的内容对模型的影响力越强**。

### 2.2 Responses API 的 Prompt 排序控制权

Codex 通过 HTTP POST 请求发送 JSON Payload 给 Responses API，但 Prompt 的最终排序由**服务器端决定**：

> "As you can see, the order of the first three items in the prompt is determined by the server, not the client."

Server 端的 Prompt 顺序为：
1. System message（Content 由服务器控制）
2. Tools（由客户端提供）
3. Instructions（由客户端提供）
4. Input（来自 JSON Payload）

这意味着 Codex 必须精心设计 `instructions` 和 `input` 的内容，才能在服务器决定的排序下依然保持正确的语义优先级。

## 三、Prompt Caching：线性化 O(n²) 的代价

### 3.1 Cache Hit 的条件

Codex 的团队明确指出：

> "Generally, the cost of sampling the model dominates the cost of network traffic, making sampling the primary target of our efficiency efforts. This is why prompt caching is so important, as it enables us to reuse computation from a previous inference call. When we get cache hits, sampling the model is linear rather than quadratic."

**Cache Hit 的条件是 Exact Prefix Match**——只有当新请求的 Prompt 与上一次请求的 Prefix 完全一致时，才能触发缓存。这意味着：

**Static Content**（如 instructions、examples）应该放在 Prompt 开头
**Variable Content**（如用户特定信息、Tool Results）应该放在 Prompt 结尾

> "Cache hits are only possible for exact prefix matches within a prompt. To realize caching benefits, place static content like instructions and examples at the beginning of your prompt, and put variable content, such as user-specific information, at the end."

### 3.2 导致 Cache Miss 的操作

Codex 列出了会导致缓存失效的操作：

- 在对话中途**更改可用工具列表**
- **更换模型**（因为模型特定的 instructions 会改变 Prompt 的第三项）
- **更改沙箱配置、Approval Mode 或当前工作目录**

### 3.3 MCP 工具的缓存陷阱

这里有一个特别值得注意的工程细节。MCP 协议支持服务器通过 `notifications/tools/list_changed` 通知客户端工具列表发生了变化。如果 Codex 在长对话中间响应这个通知，会导致：

> "Honoring this notification in the middle of a long conversation can cause an expensive cache miss."

Codex 的解法是：**不在中途更改工具列表，而是通过追加新消息来反映配置变更**。例如沙箱配置变更会插入新的 `role=developer` 消息，工作目录变更会插入新的 `role=user` 消息。这样做的好处是保持了 Prompt 的前缀不变，从而维持缓存命中。

**这与 Anthropic 的方案形成了有趣的对比**：Anthropic 的长程 Agent 通过 Initializer Agent 在初始阶段就确定完整的 Feature List，避免中途变更；而 Codex 则通过"追加而非修改"的策略，在必须变更时也尽量维持缓存。

## 四、Compaction：上下文窗口的终极解法

### 4.1 从手动到自动

当 token 数量超过某个阈值时，Codex 必须对对话进行压缩（Compaction）。最早的实现在 2024 年需要用户**手动调用 `/compact` 命令**，触发一次 summarization 请求，然后用生成的摘要替换原有的对话历史。

后来 Responses API 演进出了专门的 `/responses/compact` 端点，返回一个压缩后的 Item 列表用于继续对话。这个端点的设计使得压缩过程更加高效，避免了之前"用同一条对话历史来压缩自己"的逻辑困境。

### 4.2 为什么需要 Compaction

即使有 Prompt Caching，上下文窗口的硬性上限依然存在。Codex 面对的场景是：

- 一个 Turn 内可能有**数百个 Tool Call**（每个 Tool Call 及其结果都是独立的 JSON 对象）
- 对话历史增长是**单调递增**的，没有自然衰减机制
- 某些任务（如大型代码库重构）天然会产生大量的中间状态

> "Our general strategy to avoid running out of context window is to compact the conversation once the number of tokens exceeds some threshold."

### 4.3 Compaction 的信息损失问题

Compaction 本质上是一个**有损压缩**操作。当 Codex 用 summarization 模型压缩对话历史时，必然会丢失某些细节信息。OpenAI 在博客中没有详细讨论这个问题，但从工程实践来看：

- 压缩后的摘要需要保留"关键决策点"（为什么选择某个方案、放弃了什么替代方案）
- Tool Call 的具体参数可能需要被抽象为更高级别的描述
- 中间状态（文件内容、测试结果）如果与最终产物无关，应该被丢弃

**这个问题的严重程度取决于任务性质**：对于需要大量探索性尝试的任务，Compaction 的信息损失可能导致 Agent 在后续 Turn 中"不知道之前为什么放弃了某个方向"。

## 五、Context Window 与 Zero Data Retention 的矛盾

### 5.1 Stateless 的代价

Codex 有一个有趣的设计决策：**不依赖 `previous_response_id` 参数来维护状态**。

> "While the Responses API does support an optional `previous_response_id` parameter to mitigate this issue, Codex does not use it today, primarily to keep requests fully stateless and to support Zero Data Retention (ZDR) configurations."

使用 `previous_response_id` 需要服务器端维护状态，这与 ZDR（Zero Data Retention）配置冲突——如果服务器需要维护状态，就意味着它必须存储用户的数据。Codex 选择不使用这个参数，以保证：
1. 请求完全无状态
2. 支持 ZDR 客户的数据主权要求

### 5.2 隐私与性能的权衡

OpenAI 提到了一个关键细节：

> "Note that ZDR customers do not sacrifice the ability to benefit from proprietary reasoning messages from prior turns, as the associated encrypted_content can be decrypted on the server. (OpenAI persists a ZDR customer's decryption key, but not their data.)"

这意味着 ZDR 客户可以通过加密内容的方式让服务器保留"计算能力"而不保留"数据"。但这与 Codex 不使用 `previous_response_id` 的决策放在一起看，似乎存在一定的张力——如果服务器不需要维护状态，如何实现加密内容的跨请求复用？

**这个问题值得进一步关注**，因为它涉及到 Agent 系统在隐私敏感场景下的工程可行性。

## 六、与 Anthropic 方案的横向对比

| 维度 | OpenAI Codex | Anthropic Claude Code |
|------|-------------|---------------------|
| **上下文管理策略** | Compaction（压缩历史） | Initializer（前置初始化）+ Feature List |
| **多 Agent 协作** | 单 Agent Loop | Planner/Worker 双 Agent 架构 |
| **长程任务保障** | 手动 `/compact` 或自动压缩 | 等待批准 + 多 Agent 互检 |
| **缓存策略** | Prompt Caching（前缀匹配） | 长期记忆（外部知识图谱）|
| **隐私模式** | Zero Data Retention 支持 | 企业级数据隔离 |

从对比可以看出，**两者的核心差异在于"上下文管理的时机"**：

- Anthropic 选择在**开始前**通过 Initializer 确立完整的上下文结构，减少运行时的上下文增长
- OpenAI 选择在**运行中**通过 Compaction 管理上下文膨胀，保留更多细节直到必须压缩

**哪种方案更好取决于场景**：对于需要灵活适应的长程任务，Anthropic 的结构化方式更稳定；对于需要快速启动的短程任务，OpenAI 的方式更轻量。

## 七、工程实践启示

### 7.1 Prompt Caching 的最佳实践

根据 Codex 的经验：
- **Static Content 靠前**：instructions、examples、system prompts
- **Variable Content 靠后**：user input、tool results
- **避免中途变更工具**：提前确定完整的工具列表
- **用追加代替修改**：配置变更通过新消息追加，而非修改历史消息

### 7.2 Context Window 的监控

Codex 团队必须监控可能导致缓存失效的操作：

> "The Codex team must be diligent when introducing new features in the Codex CLI that could compromise prompt caching."

对于 Agent 开发者来说，这意味着需要**持续监控 Prompt 长度的增长趋势**，在接近上下文窗口上限之前主动触发 Compaction。

### 7.3 Compaction 的设计

如果你的 Agent 系统需要支持长程任务，需要考虑：
1. **阈值设定**：何时触发压缩？（太早浪费上下文，太晚可能超出窗口）
2. **压缩粒度**：是压缩整个历史，还是只压缩 oldest 的 Turn？
3. **保留什么**：压缩后的摘要需要包含"可恢复的决策上下文"，而非只是最终状态

## 结语：Harness 的责任边界

OpenAI 博客的最后一句话值得反复咀嚼：

> "We hope this post gives you a good view into the role our agent (or 'harness') plays in making use of an LLM."

**Harness 的责任不是让模型更强，而是让模型在有限的上下文窗口内发挥最大的作用**。这意味着 Harness 需要承担：

- **上下文管理**：何时压缩、保留什么、丢弃什么
- **缓存优化**：如何最大化缓存命中率
- **状态维护**：如何在 Stateless 和状态复用之间取得平衡
- **错误恢复**：当 Compaction 导致信息损失时如何重建上下文

这些都不是模型本身能解决的问题——它们是 Harness 工程的范畴，也是 AI Agent 系统设计的核心挑战。

---

**执行流程**：
1. **理解任务**：本轮仓库维护，需要产出 Article + Project，且必须主题关联
2. **规划**：扫描一手来源（Anthropic/OpenAI/Cursor）发现值得深度分析的主题；OpenAI Codex Agent Loop 文章符合要求
3. **执行**：web_fetch 获取原文 + GitHub API 获取项目信息
4. **返回**：获取 Codex Agent Loop 工程细节 + Mirage 项目信息（1612 Stars）
5. **整理**：撰写 Article（Codex Agent Loop 工程解析）+ Project 推荐（Mirage VFS），主题关联：上下文管理与工具抽象

**调用工具**：
- `exec`: 10次
- `web_fetch`: 2次
