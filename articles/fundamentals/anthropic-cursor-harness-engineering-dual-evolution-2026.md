# Anthropic vs Cursor：Harness 工程的双轨演化路径

## 核心主张

本文要证明：**Anthropic 和 Cursor 在 Agent Harness 工程上走出了两条截然不同的路径——平台优先 vs 用户优先——但最终都在解决同一个问题：如何让 Agent 在长程任务中保持高质量输出，同时保持可测量、可干预、可修复的能力。**

---

## 背景：Harness 为什么重要

Anthropic 在 2024 年底的工程博客中提出了一个核心观点：`building effective agents` 关键在于 harness 设计——即围绕模型的外层架构，包括上下文管理、工具定义、错误恢复机制。Cursor 在 2026 年的「第三Era」博客中同样指出：

> "The future of AI-assisted software engineering will be multi-agent. Instead of running every subtask through a single agent, the system will learn to delegate across specialized agents and subagents... Making that work well is fundamentally a harness challenge."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

这说明 **Harness 已经从「可选的外层包装」演变为「决定 Agent 能力上限的核心架构」**。

---

## 双轨路径的根因差异

### Anthropic：平台层抽象

Anthropic 的 harness 设计以 **API 平台为核心**。Claude Code 的 harness 本质上是 Anthropic API 的客户端层，负责：

1. **上下文窗口管理**：Prompt caching、thinking block 压缩、idle session 清理
2. **工具格式适配**：string replacement（Anthropic 训练格式）vs patch-based（OpenAI 训练格式）
3. **模型特异性**：不同模型（Opus/Sonnet/Haiku）有不同的行为特征，需要不同的 harness 配置

关键证据来自 April 2026 Postmortem：

> "We use prompt caching to make back-to-back API calls cheaper and faster for users. Claude writes the input tokens to the cache when it makes an API request, then after a period of inactivity the prompt is evicted from cache, making room for other prompts."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

**Anthropic 的 harness 是「平台能力的封装器」**——它把 API 层的缓存管理、模型调度、错误处理包装成对上层应用透明的接口。应用的 harness 设计空间主要在「如何组合这些封装」。

### Cursor：应用层定制

Cursor 的 harness 设计以 **用户场景为核心**。Cursor 的 harness 直接面向开发者的实际工作流：

1. **上下文窗口演化**：从 Guardrails（限制模型行为）→ 动态上下文发现（模型自主拉取）
2. **在线/离线测量**：CursorBench 公开基准 + Keep Rate + 用户语义反馈
3. **多模型支持**：每个模型有专属 harness 配置，工具格式与训练方式匹配

Cursor 的核心洞察是：

> "We maintain public benchmarks alongside our own eval suite, CursorBench, which gives us a fast, standardized read on quality and lets us compare across time. But even the best benchmarks only approximate real usage, meaning we'd miss important signals if we relied on them entirely."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

**Cursor 的 harness 是「场景解决方案的交付器」**——它把 AI 能力包装成开发者熟悉的界面（编辑、PR、Artifact），并在每个交互点埋入质量测量机制。

---

## 关键分歧点

### 1. 上下文管理的哲学

| 维度 | Anthropic | Cursor |
|------|-----------|--------|
| **起点** | 平台 API 的能力边界 | 开发者实际场景的痛点 |
| **演进方向** | 压缩成本 + 降低延迟 | 扩展能力 + 提高质量 |
| **关键机制** | Prompt caching + 缓存逐出策略 | 动态上下文发现 + 模型自主拉取 |
| **失败模式** | 配置性降级（effort 回退/缓存污染/system prompt 压缩） | 上下文焦虑（Context Anxiety）——模型在上下文窗口满时拒绝工作 |

Cursor 发现的「Context Anxiety」现象值得深入分析：

> "For example, we observed one model develop what we came to call context anxiety: As its context window filled up, it would start refusing work, hedging that the task seemed too big. We were able to reduce the behavior through prompt adjustments."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

Anthropic 的 April Postmortem 揭示了平台层的问题——缓存污染导致上下文逐段丢失，这本质上与 Cursor 的 Context Anxiety 是同一问题的不同层级：前者是「平台层上下文丢失」，后者是「模型层上下文感知过载」。

### 2. 测量驱动 vs 理论驱动

**Anthropic 的方法**是「理论驱动 + 回测验证」：

> "As part of the investigation, we back-tested Code Review against the offending pull requests using Opus 4.7. When provided the code repositories necessary to gather complete context, Opus 4.7 found the bug, while Opus 4.6 didn't."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

Anthropic 用最新模型（Opus 4.7）来回测之前版本（4.6）未能发现的 bug，这说明 **模型能力本身就包含了代码审查能力**——问题在于 harness 是否提供了足够的上下文让模型发挥这种能力。

**Cursor 的方法**是「在线实验 + 量化信号」：

> "We measure agent quality in these tests through a variety of metrics. Some are straightforward like latency, token efficiency, tool call count, and cache hit rate... The first is the "Keep Rate" of agent-generated code. For a given set of code changes that the agent proposed, we track what fraction of those remain in the user's codebase after fixed intervals of time."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

Cursor 的 Keep Rate 是一个天才的指标——它把「模型输出质量」转化为「用户是否需要手动修改代码」。这个指标的优势在于：
- 直接反映用户体验（不需要事后分析 feedback）
- 量化且可复现（固定的检查时间窗口）
- 跨模型可比（不同模型的 Keep Rate 可以横向对比）

### 3. 模型切换的处理

当用户在中途切换模型时，两家的处理策略也不同：

> "When a user switches models, Cursor automatically switches to the appropriate harness, with that model's customized set of prompts and tools. However, the model still has to apply those tools to a conversation history that was produced by a different model and is out of distribution from what it was trained on."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

Cursor 会在模型切换时添加 **mid-chat takeover 指令**，告诉新模型「你现在在接手另一个模型的对话」，并引导它不要调用不在自己工具集中的工具。这个设计揭示了一个重要事实：

> "To address this, we add custom instructions that tell the model when it's taking over mid-chat from another model... A second challenge is that caches are provider- and model-specific, so switching means a cache miss and a slower, more expensive first turn."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

**Harness 必须处理「模型异构性」**——不同的训练方式（string replacement vs patch-based）、不同的上下文承载能力（Opus 200K vs Sonnet 128K）、不同的工具格式偏好，这些都会影响同一段对话在不同模型上的表现。

---

## 殊途同归：长程 Agent 的挑战

尽管路径不同，Anthropic 和 Cursor 都在解决同一个问题：**长程 Agent 的上下文质量维护**。

Anthropic 的解法是「平台层保障」：
- Prompt caching 的正确实现（避免 April bug）
- 缓存逐出策略的隔离性保证
- System prompt 变更的 eval 门槛

Cursor 的解法是「应用层保障」：
- 动态上下文发现（让模型自主拉取需要的上下文）
- 在线 Keep Rate 测量（实时感知上下文质量退化）
- 模型特异性定制（每个模型有不同的上下文处理策略）

> "Context rot" — where accumulated mistakes degrade the quality of the model's subsequent decisions — is one of the most insidious problems in long-running agents. The agent's tools are one of the broadest surfaces for bugs, and tool call errors can be extremely harmful to a session in Cursor.
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

Anthropic 的 April bug 正是 Context Rot 的教科书案例：

> "Claude would continue executing, but increasingly without memory of why it had chosen to do what it was doing. This surfaced as the forgetfulness, repetition, and odd tool choices people reported."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

---

## 工程实践建议

### 1. Context 管理原则

**Anthropic 的教训**（从 April Postmortem）：
- 缓存逐出逻辑必须严格一次性执行，不能在每次 turn 中重复触发
- System prompt 变更必须经过完整的 eval 流程，包括 ablation 分析
- Effort 参数的默认值变更需要充分的用户反馈周期

**Cursor 的建议**：
- 监控「工具调用错误率」作为 Context Rot 的先行指标
- 使用 Keep Rate 或类似的「输出质量留存率」指标
- 提前识别模型的 Context Anxiety 并通过 prompt 调整预防

### 2. 多模型支持的架构原则

> "All of our harness abstractions are model agnostic and can be heavily customized for every model we support. For instance, OpenAI's models are trained to edit files using a patch-based format, while Anthropic's models are trained on string replacement. Either model could use either tool, but giving it the unfamiliar one costs extra reasoning tokens and produces more mistakes."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

**核心原则**：工具格式必须与模型训练方式匹配。这是 0 以上的优化，不匹配则一定导致额外的 reasoning 损耗和更多的错误。

### 3. 质量测量的分层设计

| 层级 | 指标 | 来源 |
|------|------|------|
| 平台层 | 缓存命中率、API 延迟、Token 消耗 | Anthropic API |
| 应用层 | 工具调用成功率、错误类型分类 | Cursor Harness |
| 用户层 | Keep Rate、用户 feedback 语义分析 | 用户反馈 |

三层指标必须联合使用，缺任何一层都会导致「测量盲区」。

---

## 结论：Harness 工程的演化方向

Anthropic 和 Cursor 的双轨路径揭示了一个核心事实：**Harness 工程正在从「配置层」演化为「架构层」**。

过去，harness 是模型的「外包装」——配置一下工具描述、写写 system prompt。现在，harness 是「能力边界定义器」——它决定了模型能看到多少上下文、工具调用的错误恢复机制、长程任务的状态管理。

两条路径的汇合点是：**长程 Agent 的上下文质量维护**。无论是 Anthropic 的平台层保障还是 Cursor 的应用层测量，最终都在解决同一个问题——如何让 Agent 在长时间任务中不因为上下文累积而退化。

> "The future of AI-assisted software engineering will be multi-agent... The ability to orchestrate that kind of coordination will live in the harness rather than any single agent. This means that, while harness engineering has always been important for agent success, it's only going to be more critical going forward."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

**对 Agent 开发者的启示**：
1. **Harness 不是配置，是架构**——它决定了 Agent 的能力边界和质量上限
2. **测量优先于优化**——没有量化指标，优化无从下手
3. **模型特异性不是兼容性负担，是性能杠杆**——为每个模型定制 harness 是值得的工程投入

---

## 引用来源

1. [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem) — 配置性降级的根因分析，三类失效模式的详细记录
2. [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) — Cursor 的 Harness 工程方法论，测量驱动质量
3. [Cursor Blog: Cursor 3](https://cursor.com/blog/cursor-3) — 第三 Era 的产品定义，云端 Agent 工厂