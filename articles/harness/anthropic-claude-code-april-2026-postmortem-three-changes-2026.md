# Anthropic Claude Code 质量回退三因素分析：Harness 变更如何悄悄损害 Agent 智能

> 核心问题：Anthropic 在 2026 年 4 月收到大量 Claude Code 质量下降的报告，调查后发现是三个独立的变更各自贡献了一部分问题，每个都在不同的时序上影响不同的流量切片，造成了「广泛且不一致」的下降假象。本文深度拆解这三个变更的技术细节、工程决策链条，以及背后的 harness 设计教训。

---

## 背景：看似「模型变差」，实则三次独立变更

2026 年 3-4 月，Anthropic 收到了大量用户反馈称 Claude 的响应质量变差。但调查结果表明：**API 本身没有受到影响，模型本身没有降级**——问题出在 Claude Code 产品层的三个独立变更上。

> "We never intentionally degrade our models, and we were able to immediately confirm that our API and inference layer were unaffected."
> — [Anthropic Engineering Blog: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

这三个变更各自影响不同的流量切片、在不同的时间表上发生，叠加效果看起来像是「全面性的、不一致的」下降。这使得问题在早期难以与正常用户反馈波动区分开来，即使进行了调查，内部用量和 eval 也没有在最初复现用户识别的问题。

---

## 变更一：默认推理努力度从 High 降到 Medium

### 决策背景

当 Anthropic 在 2026 年 2 月发布 Opus 4.6 时，将默认推理努力度设置为 `high`。但随后收到用户反馈：在 high 模式下，模型有时会思考过长时间，导致 UI 看似冻结，且延迟和 token 消耗对于这些用户不成比例。

Anthropic 的核心逻辑是：更长的思考时间 = 更好的输出，而 effort levels 让用户自己设置这个权衡点。他们在测试时发现 `medium effort` 在大多数任务上智力略低但延迟显著减少，且不受同样偶发的长尾延迟问题困扰，还能最大化用户的使用限额。

于是他们在 3 月 4 日悄悄将默认努力度从 `high` 改为 `medium`，并通过产品内对话框解释了这一变更的理由。

### 实际结果

用户很快报告 Claude Code「感觉没那么聪明了」。Anthropic 采取了一系列设计迭代来让用户更清楚地了解当前的 effort 设置（启动通知、内联 effort 选择器、恢复 ultrathin），但大多数用户保留了 `medium` 默认值。

在收到更多客户反馈后，Anthropic 在 4 月 7 日撤回了这一决定。现在所有用户默认使用 `xhigh effort`（Opus 4.7）和其他模型的 `high effort`。

### 工程教训

这个案例揭示了一个典型的**产品层权衡错误**：将基础设施优化（延迟、token 节省）置于默认智能体验之上。Medium effort 在内部测试中看起来合理，但用户的实际反馈表明，对于编码任务来说，默认的智能降级是不可接受的。

> "We shipped a number of design iterations to make the current effort setting clearer...but most users retained the medium effort default."
> — Anthropic Engineering Blog

---

## 变更二：缓存优化 Bug 导致每轮都丢弃推理历史

### 设计意图

当 Claude 推理任务时，其推理过程通常保留在对话历史中，这样在后续每轮中 Claude 都能看到它做出编辑和工具调用的原因。

Anthropic 使用 **prompt caching** 来降低用户成本。Claude 在发出 API 请求时将输入 token 写入缓存，一段不活跃期后提示从缓存中清除，为其他提示腾出空间。

3 月 26 日，他们设计了一个效率改进：如果会话空闲超过一小时，清除旧的推理部分。既然请求无论如何都会是缓存未命中，可以从请求中修剪不必要的消息以减少发送到 API 的未缓存 token 数量。然后恢复发送完整的推理历史。

### 实现 Bug

为了实现这个逻辑，他们使用了 `clear_thinking_20251015` API 头部配合 `keep:1`。

**实现出现了 Bug**：不是只清除一次推理历史，而是在会话的每一轮都清除。对于会话，一旦跨过空闲阈值，每个后续请求都告诉 API 只保留最近的推理块并丢弃之前的所有内容。

这个 bug 会复合：如果用户在 Claude 正在执行工具使用时发送后续消息，会在损坏的标志下开始新的一轮，因此甚至连当前回合的推理也被丢弃。Claude 会继续执行，但越来越缺乏关于为什么选择做某事（the "why"）的记忆。这表现为用户报告的「遗忘、重复和奇怪的工具选择」。

由于这会持续丢弃后续请求中的推理块，这些请求也会导致缓存未命中。Anthropic 认为这就是驱动「使用限额消耗比预期快」单独报告的原因。

### 发现难度分析

这个 bug 处于 Claude Code 的上下文管理、Anthropic API 和扩展推理的交叉点。它通过了多轮人类和自动化代码审查、单元测试、端到端测试、自动化验证和 dogfooding。由于这只发生在边缘情况（stale sessions）中，而且难以复现，Anthropic 花了超过一周才发现并确认根本原因。

两个不相关的实验使得他们最初难以复现这个问题：
1. 一个内部服务器端的消息排队实验
2. 一个正交的变化抑制了这个 bug 在大多数 CLI 会话中的表现

### Codex 4.7 的 Code Review 发现该 Bug

作为调查的一部分，Anthropic 在有问题的 Pull Request 上使用 Opus 4.7 进行了 Code Review 测试。**当提供收集完整上下文所需的代码仓库时，Opus 4.7 发现了这个 bug，而 Opus 4.6 没有发现**。

Anthropic 正在为此落地支持额外的仓库作为代码审查的上下文。

### 修复与后续

此 bug 于 4 月 10 日在 v2.1.101 中修复。

### 工程教训

这个案例是**跨层交互 bug 的教科书**：bug 跨越 Claude Code（前端产品层）、Anthropic API（中间件层）和扩展推理（模型层）三个层级。它说明了：
1. 即使通过了所有常规测试，跨层交互产生的 bug 仍可能逃脱检测
2. 边缘情况（stale sessions）需要专门的测试策略
3. 更强的 LLM-as-reviewer（用 Opus 4.7 查 Opus 4.6 的代码）是未来发现这类 bug 的有效手段

---

## 变更三：系统提示词变更导致智力量化下降

### 背景

Claude Opus 4.7 有一个值得注意的行为特征：相对于其前身，它倾向于更冗长。这在硬问题上使其更聪明，但也产生了更多输出 token。

Anthropic 有一系列工具来减少冗长：模型训练、提示工程和改进的产品内思考 UX。但在发布前调优 Claude Code 时，他们向系统提示词添加了一行导致不成比例的影响的内容：

```
"Length limits: keep text between tool calls to ≤25 words. Keep final responses to ≤100 words unless the task requires more detail."
```

### 测试与发布

经过多周的内部测试和在他们运行的评估集上没有回归后，Anthropic 感觉对这一更改有信心，并在 4 月 16 日与 Opus 4.7 一起发布。

### Ablation 发现问题

在调查过程中，使用更广泛的评估集运行了更多 ablation（从系统提示词中移除行以了解每行的影响）。其中一个评估对 Opus 4.6 和 4.7 都显示了 3% 的下降。他们在 4 月 20 日作为发布的一部分立即撤回了提示词。

### 工程教训

这个案例说明**系统提示词的每一行都可能有巨大的智能影响**，而且小规模测试集无法捕捉边缘情况的影响。3% 的下降听起来很小，但对于生产级别的编码 agent 来说，这意味着每个任务失败的可能性显著增加。

---

## 三个变更的相互作用分析

| 变更 | 变更时间 | 影响模型 | 问题表现 | 发现难度 |
|------|---------|---------|---------|---------|
| 默认推理努力度 | 3月4日 | Opus 4.6, 4.6 | 感觉不够聪明（Medium vs High） | 低（用户反馈明确） |
| 缓存清除 Bug | 3月26日 | Opus 4.6, 4.6 | 遗忘性、重复性、奇怪的工具选择 | 高（边缘情况+跨层交互） |
| 系统提示词 | 4月16日 | Opus 4.6, 4.6, 4.7 | 编码质量下降 | 中（ablation 发现） |

三个变更各自影响不同的流量切片、在不同的时间表上发生，aggregate effect 看起来像是 broad, inconsistent degradation。

---

## Anthropic 的后续行动

针对这些问题，Anthropic 宣布了以下改进：

1. **更大的内部员工覆盖**：让更大比例的内部员工使用完全相同的 Claude Code 公开版本（而不是用来测试新功能的内部版本）

2. **改进了 Code Review 工具**：内部使用的 Code Review 工具已改进，并会发布给客户。Opus 4.7 在代码审查中比 Opus 4.6 更容易发现这类 bug，现在他们将为代码审查添加额外仓库作为上下文

3. **更严格的系统提示词变更控制**：
   - 对 Claude Code 的每个系统提示词变更运行 per-model eval 套件
   - 持续 ablation 以了解每行的影响
   - 建立了新工具使提示词变更更容易审查和审计
   - 在 CLAUDE.md 中添加了指导，确保 model-specific 的变更被 gate 到特定模型
   - 对于任何可能影响智能的变更，添加 soak periods、更广泛的 eval 套件和 gradual rollouts

---

## 对 Agent Harness 工程的启示

### 1. 上下文管理是脆弱的

三个 bug 中有两个（缓存清除 bug、默认推理努力度）直接涉及上下文管理层。这提醒我们：Agent 的「记忆」和「推理质量」不仅仅取决于模型本身，还深深植根于产品层的上下文管理设计。

任何影响 context window 使用的变更都可能以非线性的方式影响输出质量——即使表面上看起来是「小优化」。

### 2. 跨层交互需要专门的测试策略

缓存清除 bug 处于 Claude Code（前端）、Anthropic API（中间件）和模型层（扩展推理）的交叉点。它通过了所有常规测试（包括 unit tests、e2e tests、automated verification 和 dogfooding），但只在边缘情况下触发。

这意味着：**Agent harness 需要针对跨层交互 bug 的专门测试策略**——不仅仅是功能测试，还要有故障模式测试、边界条件测试和长时间空闲会话的恢复测试。

### 3. 默认值的改变是最危险的变更

三个变更中最微妙的是将默认推理努力度从 `high` 改为 `medium`。这不是一个 bug，只是一个「合理」的权衡决策，但它对用户体验的影响远超预期。

在 Agent 的语境下，**默认行为就是用户期望的行为**。改变默认值不仅仅是技术决策，它实际上重新定义了产品的智能基准线。

### 4. 系统提示词变更需要全面评估

系统提示词中的一行（约 20 个 token）「Length limits: keep text between tool calls to ≤25 words」导致 3% 的编码质量下降。这说明**系统提示词中的每个约束都可能以意想不到的方式影响模型行为**。

建议：任何系统提示词的变更都应该：
- 在多个模型版本上测试（而不仅仅是最新的）
- 运行更广泛的评估集（而不仅仅是标准 benchmarks）
- 有明确的 soak period 和回滚计划

---

## 总结

Anthropic 2026 年 4 月的这个 postmortem 揭示了一个重要事实：**Agent 的智能体验是 harness 各层协同的结果，而非模型本身的固有属性**。当感知到「模型变差」时，根因可能在于：

- 产品层的默认参数（推理努力度）
- 上下文管理层的一个缓存清除逻辑 bug
- 系统提示词中的一个长度限制指令

这些变更每一个单独看起来都「合理」，但组合起来产生了系统性退化。这对 Agent 开发者意味着：**harness 的每一次变更都需要被视为潜在的「智能破坏者」，需要严格的评估、回滚计划和跨层测试**。

> "This isn't the experience users should expect from Claude Code." — Anthropic Engineering Blog

用户对 Agent 的信任建立在一致的智能体验之上。任何削弱这种体验的变更——无论多么微小——都需要极度谨慎地处理。

---

*来源：[Anthropic Engineering Blog: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) | 2026-04-23*