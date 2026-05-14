# Cursor Agent Harness 模型亲和性工程与多 Agent 编排的未来

## 核心论点

> **Agent 的性能由 Harness 和 Model 共同决定，而两者的匹配程度取决于「模型训练时形成的原生习惯」——工具格式、提示风格、中途切换模型时的上下文适配，构成了一套可以被系统性调优的「模型亲和性」工程。这套工程实践在 2026 年已从手工调优演进为可复制的方法论，并预示了多 Agent 编排将成为下一个 Harness 挑战的核心战场。**

---

## 一、模型亲和性：为什么同一个工具格式会伤害特定模型

### 1.1 工具格式的「训练即认知」现象

Cursor 工程师在博客中揭示了一个关键观察：**OpenAI 模型训练时使用的是基于 patch 的编辑格式，而 Anthropic 模型训练时使用的是字符串替换格式**。

这意味着：

| 模型 | 原生训练工具格式 | 使用非原生格式的成本 |
|------|----------------|------------------|
| OpenAI 系列 | Patch/diff 格式 | 额外的 reasoning token 消耗 + 更高错误率 |
| Anthropic 系列 | String replacement | 额外的 reasoning token 消耗 + 更高错误率 |

这不是一个「偏好」问题，而是一个「认知习惯」问题——模型在预训练阶段形成的工具使用模式，直接影响了它在推理时调用该工具的效率。

> "Either model could use either tool, but giving it the unfamiliar one costs extra reasoning tokens and produces more mistakes. So in our harness, we provision each model with the tool format it had during training."
> — [Cursor Engineering Blog: Continually improving our agent harness](https://www.cursor.com/blog/continually-improving-agent-harness)

### 1.2 提示风格的分化：精确指令 vs 直觉推理

模型不仅在工具格式上存在差异，在提示风格上也存在显著分化：

| 维度 | OpenAI 模型 | Anthropic 模型（Claude） |
|------|-----------|----------------------|
| 指令遵循 | 更_literal_，精确指令执行更稳定 | 更_intuitive_，对不精确指令有更强容错性 |
| 提示工程敏感性 | 高（需要更结构化的指令） | 中等（能理解隐含意图） |
| 错误恢复 | 倾向于重复错误策略 | 倾向于主动探索替代方案 |

Cursor 的做法是为不同 Provider 甚至不同版本模型配置**独立的 system prompt 模板**。这不仅仅是「调整措辞」，而是根据模型的信息处理习惯重新组织提示结构。

### 1.3 「Context Anxiety」：模型特异性缺陷的 Harness 补偿

Cursor 团队在调优过程中发现了一个模型特异性缺陷的典型案例——他们称之为「Context Anxiety」：

**现象**：当模型的上下文窗口填充到一定程度时，它开始拒绝任务，声明「任务看起来太大」。

**根因**：这不是能力不足，而是模型在预训练阶段形成的一种「上下文饱和时的自我保护模式」——当输入密度过高时，模型倾向于保守估计自己的能力边界。

**Harness 补偿方案**：通过 prompt 调整降低这种行为，而非修改模型本身。

> 笔者认为：「Context Anxiety」揭示了一个重要的工程原则——**模型缺陷不一定需要通过模型更新来解决**，在许多情况下，Harness 层面的提示工程可以有效地引导模型绕过其原生缺陷。这要求 Harness 工程师深入理解模型的训练分布，而不仅仅是使用模型。

---

## 二、中途切换模型：Harness 的跨模型状态迁移

### 2.1 问题本质：对话历史与模型训练的分布偏移

当用户在对话中途切换模型时，Cursor 面临一个独特的工程挑战：**新的模型需要在由另一个模型生成的对话历史上继续工作，而这个对话历史对于新模型来说是 out-of-distribution（分布外）的**。

具体问题：
1. **工具调用不兼容**：旧模型使用的工具可能不在新模型的工具集中
2. **上下文格式差异**：新模型看到的对话状态可能与其训练时的上下文格式不一致
3. **缓存失效**：Provider 和模型级别的缓存不共享，切换后面临「冷启动」

### 2.2 Cursor 的三层层级解决方案

**层级一：自动 Harness 切换**

当用户切换模型时，Cursor 自动切换到该模型对应的 harness 配置，包括：
- 该模型的专用 system prompt
- 该模型的工具列表和格式
- 该模型的上下文填充策略

**层级二：Mid-chat 接管指令（Steering Prompts）**

Cursor 添加自定义指令，告诉新模型「你正在中途接管一个由其他模型发起的对话」，并引导它：
- 不调用对话历史中存在但自己工具集中没有的工具
- 对历史对话状态保持宽容，优先理解当前任务而非纠正历史

> "These instructions also steer it away from calling tools that appear in the conversation history but aren't part of its own tool set."
> — [Cursor Engineering Blog: Continually improving our agent harness](https://www.cursor.com/blog/continually-improving-agent-harness)

**层级三：对话摘要（Cache Penalty 缓解）**

切换时的缓存未命中是不可避免的。Cursor 尝试通过**在切换时生成对话摘要**来缓解：

```python
# 切换时执行的伪代码
summary = summarize_conversation(
    history=current_history,
    target_model=new_model,  # 针对新模型的偏好调整摘要格式
    max_tokens=new_model.context_window * 0.3  # 摘要不超过窗口的30%
)
# 新模型从摘要开始，而非完整的原始历史
```

但这个方案存在一个**根本性限制**：如果用户正在深入一个复杂任务，摘要会丢失关键细节。Cursor 的建议是：「除非有明确理由，否则在一个对话中保持使用同一个模型」。

### 2.3 Subagent 作为替代方案

针对中途切换模型的各种问题，Cursor 给出了一个更优雅的解法：**使用 Subagent**。

Subagent 从一个全新的上下文窗口开始，而非试图在「分布偏移的对话历史」上继续工作。这意味着：
- 不存在工具不兼容问题
- 不存在上下文格式差异
- 不存在缓存失效问题

这是用「空间换兼容性」的思路——当需要在同一个会话中处理多个不同类型任务时，Subagent 比跨模型切换更可靠。

---

## 三、多 Agent 编排：Harness 的下一个主战场

### 3.1 从单 Agent 到多 Agent 的范式转移

Cursor 工程师在博客中描述了他们眼中的未来：

> "Instead of running every subtask through a single agent, the system will learn to delegate across specialized agents and subagents: one for planning, another for fast edits, and a third for debugging, each scoped to what it does best."
> — [Cursor Engineering Blog: Continually improving our agent harness](https://www.cursor.com/blog/continually-improving-agent-harness)

这个愿景涉及三个层面的分工：
1. **规划 Agent**：理解复杂任务，拆解为子任务
2. **执行 Agent**：执行具体编辑和实现
3. **调试 Agent**：验证结果，处理异常

### 3.2 多 Agent 系统的 Harness 挑战

Cursor 明确指出，**多 Agent 协作的核心挑战是 Harness 工程**，而非 Agent 本身：

| 挑战 | 单 Agent | 多 Agent |
|------|---------|---------|
| 任务分发 | 无 | 需要「调度 Agent」判断哪个子 Agent 适合当前任务 |
| 上下文传递 | 单一上下文窗口 | 需要在子 Agent 之间传递任务上下文 |
| 工具协调 | 线性工具调用 | 需要避免重复操作和资源冲突 |
| 结果整合 | 直接输出 | 需要「缝合」多个子 Agent 的输出为连贯结果 |

### 3.3 调度 Agent 的设计要求

Cursor 指出了一个关键角色：**调度 Agent（Orchestrator）**——负责决定：
1. **分发**：哪个子 Agent 应该处理当前任务？
2. **帧任务**（Frame the Task）：如何向子 Agent 的 harness 传递任务，使其能发挥该 Agent 的优势？
3. **缝合**：如何将多个子 Agent 的结果整合为一个连贯的最终输出？

> 笔者认为：调度 Agent 的设计要求揭示了为什么多 Agent 编排是「Harness 问题」而非「模型问题」——模型决定「能否执行任务」，而 Harness 决定「任务如何被分解、传递和重组」。这是架构层面的设计，而非微调层面的调优。

---

## 四、工程启示：Harness 工程师的实践框架

基于 Cursor 的实践经验，以下是我总结的 Harness 工程关键原则：

### 4.1 模型亲和性配置清单

对于每个支持的模型，Harness 应记录以下亲和性配置：

```
Model Affinity Profile:
├── tool_format: [patch | string_replacement | custom]
├── prompt_style: [literal | intuitive | hybrid]
├── context_window_strategy: [prefill | dynamic_fetch | compressed]
├── mid_chat_switch_handling: [steering_prompt | summary | block]
└── known_quirks:
    ├── context_anxiety: [prompt_adjustment | disable]
    ├── over_hedging: [confidence_boost | example_injection]
    └── tool_call_bloat: [limit | summarize | priorize]
```

### 4.2 错误分类与自适应基线

Cursor 的 Tool Error 分类体系提供了一个可复用的错误处理框架：

- **Unknown Error**：总是属于 Harness bug → 触发告警
- **Expected Errors**：按原因分类
  - `InvalidArguments`：模型工具调用参数错误
  - `UnexpectedEnvironment`：上下文窗口内的不一致
  - `ProviderError`：外部工具服务宕机

基线应**按工具和模型分别计算**，因为不同模型在不同工具上的错误率天然存在差异。

### 4.3 Keep Rate 作为产品质量指标

Keep Rate 不应该仅仅是一个「内部指标」，而应该成为**产品级质量指标**：

- **Keep Rate < 50%**（24h）：说明 Agent 的一次性完成度存在严重问题
- **Keep Rate 50-70%**（24h）：存在改进空间，重点优化上下文填充策略
- **Keep Rate > 90%**（24h）：Agent 可以处理的任务复杂度边界需要扩展

---

## 总结：Harness 工程的专业化

Cursor 的工程实践揭示了一个重要趋势：**Harness 工程正在从「基础设施」升级为「专业学科」**。

这个升级体现在三个层面：

1. **测量体系的成熟**：从模糊的「用户满意度」到可量化的 Keep Rate、错误分类和 LLM 满意度打分
2. **模型亲和性的系统性**：从「用一个 harness 配置服务所有模型」到为每个模型定制工具格式、提示风格和错误处理策略
3. **多 Agent 编排的前瞻布局**：从单 Agent 的工具调用优化到多 Agent 调度和结果缝合的架构设计

> 笔者认为：Harness 工程的下一个十年，竞争的核心将不再是「如何让单个 Agent 更好地工作」，而是「如何在多个 Agent 之间建立可靠的任务传递和结果整合机制」。Cursor 已经在这个方向上开始投入，而大多数 Agent 框架目前尚未充分关注这一层。