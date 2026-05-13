# Cursor Agent Harness 工程实践：测量驱动的质量迭代方法论

> 本文聚焦：AI Coding Agent 的 harness 层工程实践
> 核心论点：Cursor 的 harness 质量迭代不依赖单一信号，而是构建了「离线基准 + 在线实验 + 异常检测」三层测量体系，实现数据驱动的持续改进

---

## 引言

Cursor 在 2026-04-30 发布了「Continually improving our agent harness」工程博客，揭示了一个关键事实：**当 AI Coding Agent 进入生产级质量竞争时，harness 本身的质量成为决定性因素**——而非模型本身。

Cursor 指出：

> "We approach building the Cursor agent harness the way we'd approach any ambitious software product. Much of the work is vision-driven, where we start with an opinion about what the ideal agent experience should look like."

这是一个重要的认知转变：harness 不是「让模型跑起来」的胶水层，而是**产品级系统**，需要工程化的质量迭代方法。

---

## 一、测量体系：三层信号的完整设计

Cursor 的测量体系分为三层，从不同维度捕获 agent 质量信号。

### 1.1 离线基准：CursorBench

公开基准提供标准化的快速评估能力：

> "We maintain public benchmarks alongside our own eval suite, CursorBench, which gives us a fast, standardized read on quality and lets us compare across time."

CursorBench 的价值在于：**快速、标准、可跨时间对比**。这是所有持续改进的基础设施。

### 1.2 在线实验：A/B 测试 + 多维度指标

Cursor 坦承公开基准的局限性：

> "But even the best benchmarks only approximate real usage, meaning we'd miss important signals if we relied on them entirely."

因此 Cursor 运行在线 A/B 测试，测量指标分为两类：

**直接指标**（方向性有用，但不足以回答「质量到底好不好」）：
- 延迟（Latency）
- Token 效率（Token efficiency）
- 工具调用次数（Tool call count）
- 缓存命中率（Cache hit rate）

**质量指标**（真正回答 agent 是否有价值）：
1. **Keep Rate**：用户代码库中 agent 生成的代码在固定时间窗口后的保留比例。保留率高意味着用户无需手动调整或要求 agent 修复，初步质量好。
2. **用户满意度信号**：用 LLM 读取用户对 agent 初始输出的响应，判断是否满意。用户进入下一特性是强正向信号；用户粘贴堆栈跟踪是强负向信号。

Cursor 的经验：
> "Sometimes these online tests tell us to shelve an idea that seems promising. In one experiment, we tried a more expensive model for context summarization and observed it made a negligible difference in agent quality that wasn't worth the higher cost."

这验证了 **在线实验的价值：发现那些在理论分析中看起来合理、但实际无效甚至有害的优化**。

### 1.3 异常检测：工具级质量监控

Cursor 建立了工具级错误分类体系：

| 分类 | 含义 | 性质 |
|------|------|------|
| **Unknown Error** | harness 本身的 bug | 永远需要告警 |
| **InvalidArguments** | 模型错误（参数/输入有误） | 预期行为 |
| **UnexpectedEnvironment** | 上下文窗口矛盾 | 预期行为 |
| **ProviderError** | 供应商宕机（GenerateImage/WebSearch 等） | 预期行为 |
| **UserAborted** | 用户取消 | 预期行为 |
| **Timeout** | 超时 | 预期行为 |

**告警策略**：
- Unknown Error 率：任何工具超过固定阈值即告警（因为 unknown = bug）
- Expected Error 率：通过**异常检测**发现显著偏离基线的情况

> "We compute baselines per-tool and per-model, because different models may mess up tool calls at different rates."

关键设计：**基线是 per-tool 和 per-model 的**，因为不同模型在不同工具上的错误率天然不同，必须分别建模。

---

## 二、追踪与修复：自动化的问题发现流程

Cursor 在长程 agent 的错误累积问题上给出了重要观察：

> "Tool call errors can be extremely harmful to a session in Cursor. While the agent can often self-correct, errors remain in context, wasting tokens and causing 'context rot,' where accumulated mistakes degrade the quality of the model's subsequent decisions."

这就是「context rot」问题：错误在上下文链中累积，导致后续决策质量下降。

Cursor 的解决方案是**自动化的问题发现与修复循环**：

> "We also run a weekly Automation equipped with a skill that teaches the model how to search through our logs, surface issues that are new or recently spiked, and create or update tickets in a backlog with an investigation."

即：让 Cloud Agent 每周自动扫描日志，发现新出现或突然增长的问题，并创建或更新 tickets 进入 backlog 等待调查。

Cursor 还提到：

> "Over the course of a focused sprint earlier this year, we drove unexpected tool call errors down by an order of magnitude."

这个「order of magnitude」的改善说明：**工具错误率对 agent 质量有非线性影响**，降低一个数量级意味着 context rot 的大幅缓解。

---

## 三、模型适配：Harness 的深度定制

Cursor 揭示了一个重要事实：不同模型有本质性的行为差异，harness 必须适配这些差异。

### 3.1 工具格式的模型适配

> "OpenAI's models are trained to edit files using a patch-based format, while Anthropic's models are trained on string replacement. Either model could use either tool, but giving it the unfamiliar one costs extra reasoning tokens and produces more mistakes. So in our harness, we provision each model with the tool format it had during training."

这是第一层适配：**工具调用格式的匹配**。

### 3.2 指令遵循风格的差异

> "OpenAI's models tend to be more literal and precise in their instruction following, whereas Claude is a bit more intuitive and more tolerant to imprecise instructions."

这是第二层适配：**指令风格与容错度的匹配**。

### 3.3 特殊行为问题的发现与缓解

Cursor 披露了一个真实案例：

> "For example, we observed one model develop what we came to call context anxiety: As its context window filled up, it would start refusing work, hedging that the task seemed too big. We were able to reduce the behavior through prompt adjustments."

「Context anxiety」这个命名很精准：当上下文窗口接近满载时，模型开始拒绝工作，以任务太复杂为由推脱。Cursor 通过调整 prompt 降低了这一行为。

这说明：**模型会出现行为问题，这些问题可以通过 harness 层的干预来缓解**——模型的问题不一定要在模型层解决，可以在 harness 层补偿。

### 3.4 中途换模型的挑战

> "It's especially tricky to design the harness to support users switching models mid conversation, because different models have different behaviors, prompts, and tool shapes."

中途换模型的挑战来自三个层面：
1. **行为差异**：不同模型有不同的工具集，会调用对方有而自己没有的工具
2. **缓存失效**：缓存是 provider- 和 model-specific 的，换模型意味着 cache miss
3. **上下文分布**：对话历史由前一个模型产生，对新模型来说是 out-of-distribution

Cursor 的解法：
- 自动切换到对应模型的 harness（包含 customized prompts 和 tools）
- 添加 custom instructions 告诉模型「你正在中途接手另一个模型」，并引导它不要调用不属于自己工具集的工具
- 尝试过在切换时做 summarization 以减轻 cache penalty，但发现「如果用户在一个复杂任务中途，summary 会丢失关键细节」

Cursor 的建议：
> "We generally recommend staying with one model for the duration of a conversation unless you have a reason to switch."

---

## 四、未来方向：多 Agent 协作的核心战场

Cursor 明确指出：

> "The future of AI-assisted software engineering will be multi-agent. Instead of running every subtask through a single agent, the system will learn to delegate across specialized agents and subagents: one for planning, another for fast edits, and a third for debugging, each scoped to what it does best."

而关键的是：

> "Making that work well is fundamentally a harness challenge. The system needs to know which agent to dispatch, how to frame the task for that agent's strengths, and how to stitch the results into a coherent workflow. The ability to orchestrate that kind of coordination will live in the harness rather than any single agent."

**多 Agent 协作的能力在 harness 层，不在任何单一 agent 本身**。这是对 harness 角色的本质性重新定位：harness 不只是「运行单个 agent 的环境」，而是「多 agent 编排的智能层」。

---

## 五、工程教训

从 Cursor 的实践中可以提取以下工程教训：

### 教训 1：测量分层，避免单点依赖

离线基准（CursorBench）、在线实验（A/B 测试）、异常检测（per-tool per-model baselines）构成完整测量体系，任何单一信号都可能误导。

### 教训 2：工具错误率对 agent 质量有非线性影响

降低一个数量级的工具错误率可能带来数量级的质量提升，因为错误会在上下文中累积（context rot）。

### 教训 3：模型问题可以在 harness 层补偿

Context anxiety 等模型行为问题，可以通过 harness 的 prompt 调整来缓解，不必等待模型本身修复。

### 教训 4：Harness 是多 agent 协作的智能层

未来的竞争不在于「哪个模型更好」，而在于「哪个 harness 能更好地编排多 agent 协作」。这要求 harness 从「运行环境」升级为「编排决策层」。

---

## 附录：Cursor 在线实验的指标设计

| 指标类型 | 具体指标 | 用途 |
|---------|---------|------|
| 直接指标 | Latency, Token efficiency, Tool call count, Cache hit rate | 方向性参考，但不能回答「质量好不好」 |
| 质量指标-1 | Keep Rate（代码保留率） | 衡量 agent 初始输出的实际质量 |
| 质量指标-2 | 用户满意度信号（LLM 判断） | 语义级质量评估（用户进入下一特性 vs 粘贴堆栈跟踪） |

---

**引用来源**：
- [Cursor Engineering Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)（2026-04-30）
- [Cursor Blog: CursorBench](https://cursor.com/blog/cursorbench)
- [Cursor Blog: How we compare model quality in Cursor](https://cursor.com/blog/cursorbench)

---

*本文关联项目推荐*：[YutoTerashima/agent-safety-eval-lab](https://github.com/YutoTerashima/agent-safety-eval-lab) — Agent Trace 安全评测框架，与本文「测量驱动的质量迭代」主题形成「功能质量 vs 安全评测」的双视角闭环。