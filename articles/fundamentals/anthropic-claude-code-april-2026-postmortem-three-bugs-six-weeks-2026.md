# Claude Code 质量下降的真正原因：Anthropic 六周故障复盘

> 本文分析 Anthropic 2026 年 4 月 23 日发布的 Claude Code 质量报告复盘文档，揭示三个独立产品层 bug 如何在六周内让用户认为模型能力退化。核心洞察：**模型本身没有问题，问题是 harness 层对推理 effort、上下文缓存和提示词的系统性变更**。这对于任何构建 agentic 系统的人都是一次值得深挖的工程教训。

---

## 事件背景：用户反馈 vs 根因分析

2026 年 3-4 月，Claude Code 用户大量反馈模型表现变差——代码质量下降、响应变笨、记忆丢失。Anthropic 收到反馈后立即确认：**API 层和推理层未受影响**。经过调查，团队定位到三个独立的产品层变更，它们各自在不同时间段影响了不同比例的流量，叠加后呈现出"广泛且不一致的性能退化"。

> "We never intentionally degrade our models, and we were able to immediately confirm that our API and inference layer were unaffected."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

所有三个问题已在 2026 年 4 月 20 日（v2.1.116）修复。Anthropic 同时为所有订阅用户重置了用量限制。

---

## 第一个 Bug：默认推理 effort 从高降到中

### 时间线

- **2 月**：发布 Opus 4.6 时，将 Claude Code 默认推理 effort 设为 `high`
- **问题**：用户反馈 high 模式下模型思考时间过长，UI 偶尔冻结，导致不均衡的延迟和 token 消耗
- **3 月 4 日**：Anthropic 将默认 effort 改为 `medium`，理由是内部测试表明 medium 在大多数任务上智能水平略低但延迟显著改善，且有助于最大化用户用量限制
- **4 月 7 日**：用户反馈强烈——宁愿默认更高智能、简单任务时再选择低 effort。Anthropic 回滚此变更

### 技术细节

effort 参数决定了模型在 test-time-compute 曲线上的哪个点：更多思考 = 更高智能，但也有更长延迟。Anthropic 在产品层选择哪个点作为默认，并提供其他选项让用户自行调节。

将默认从 `high` 改为 `medium` 后，尽管有一系列设计迭代（启动通知、内联 effort 选择器、恢复 ultrathink），大多数用户保留了 medium 默认。这导致明显感知到的智能下降。

> "In our internal evals and testing, medium effort achieved slightly lower intelligence with significantly less latency for the majority of tasks...As a result, we rolled out a change making medium the default effort."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

### 教训

这是一个典型的**产品决策权衡**案例：在延迟和智能之间做取舍时，用户实际偏好与 A/B 测试结果不符。Anthropic 的内部 evals 和用户实际反馈之间存在差距。

---

## 第二个 Bug：缓存优化导致推理历史被持续丢弃

### 时间线

- **3 月 26 日**：Anthropic 部署了一个效率优化——当会话空闲超过 1 小时后，清除旧的 thinking sections，减少恢复时的 token 成本
- **4 月 10 日**：修复完成

### 技术细节

Anthropic 使用 prompt caching 来降低连续 API 调用的成本。缓存工作方式：当模型发出 API 请求时，将输入 tokens 写入缓存；一段时间不活跃后，prompt 从缓存中被驱逐，为其他 prompts 让出空间。

设计意图很简单：如果会话空闲超过 1 小时，恢复时可以清除旧的 thinking sections（因为该请求本来就会 cache miss），减少发送到 API 的未缓存 tokens 数量。但实现出现了 bug：

**实际行为**：清除操作在会话剩余的每个 turn 都执行，而不是只执行一次。

> "Instead of clearing thinking history once, it cleared it on every turn for the rest of the session. After a session crossed the idle threshold once, each request for the rest of that process told the API to keep only the most recent block of reasoning and discard everything before it."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

### 级联效应

这个 bug 产生了多个连锁问题：

1. **记忆丢失**：Claude 继续执行，但越来越不知道自己为什么选择这样做——这表现为用户报告的"遗忘、重复、奇怪的工具选择"
2. **缓存 miss 叠加**：由于持续丢弃 thinking blocks，随后的请求也导致 cache miss——这可能解释了用户报告的"用量限制消耗比预期更快"
3. **跨 turn 复合**：如果在 Claude 正在执行工具使用时发送后续消息，会在损坏的标志下启动一个新 turn，所以甚至当前 turn 的推理也被丢弃

### 排查难度

这个 bug 特别难以发现的原因：

> "Two unrelated experiments made it challenging for us to reproduce the issue at first: an internal-only server-side experiment related to message queuing; and an orthogonal change in how we display thinking suppressed this bug in most CLI sessions."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

两个不相关的内部实验干扰了问题重现：
- 一个内部服务端实验（与消息队列相关）
- 一个改变 thinking 显示方式的正交变更（这在大多数 CLI 会话中抑制了这个 bug）

加上只在边缘情况（stale sessions）发生、重现难度大，Anthropic 花了一周多才发现并确认根本原因。

### 技术交叉点

这个 bug 位于 Claude Code 上下文管理、Anthropic API 和 extended thinking 的交叉点。它通过了多层人类和自动化代码审查，包括单元测试、端到端测试、自动化验证和 dogfooding——但仍然在生产中暴露。

> "This bug was at the intersection of Claude Code's context management, the Anthropic API, and extended thinking. The changes it introduced made it past multiple human and automated code reviews, as well as unit tests, end-to-end tests, automated verification, and dogfooding."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

---

## 第三个 Bug：减少冗长的系统提示词变更

### 时间线

- **4 月 16 日**：Anthropic 添加了一个系统提示词指令来减少冗长
- **4 月 20 日**：回滚，因为与其他提示词变更结合后伤害了编码质量

### 影响范围

影响了 Sonnet 4.6、Opus 4.6 和 Opus 4.7——这是三个独立问题中唯一影响 Opus 4.7 的。

---

## 为什么这看起来像"模型变笨"

三个变更各自在不同时间影响了不同比例的流量：

| 变更 | 部署时间 | 影响模型 | 回滚时间 |
|------|---------|---------|---------|
| 默认 effort 改为 medium | 3/4 | Sonnet 4.6, Opus 4.6 | 4/7 |
| 缓存优化 bug | 3/26 | Sonnet 4.6, Opus 4.6 | 4/10 |
| 减少冗长的提示词 | 4/16 | Sonnet 4.6, Opus 4.6, Opus 4.7 | 4/20 |

由于每个变更影响不同的流量切片、在不同时间表上，聚合效果看起来像"广泛、不一致的退化"。Anthropic 承认：

> "While we began investigating reports in early March, they were challenging to distinguish from normal variation in user feedback at first, and neither our internal usage nor evals initially reproduced the issues identified."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

---

## 外部视角：模型没问题，harness 有问题

Simon Willison 在其博客中指出了这个 postmortem 对 agent 系统构建者的重要意义：

> "If you're building agentic systems it's worth reading this article in detail — the kinds of bugs that affect harnesses are deeply complicated, even if you put aside the inherent non-deterministic nature of the models themselves."
> — [Simon Willison, April 24, 2026](https://simonwillison.net/2026/Apr/24/recent-claude-code-quality-reports/)

他还提到自己经常有 Claude Code 会话空闲超过一小时再返回——这类 stale session 正是第二个 bug 的触发条件：

> "I frequently have Claude Code sessions which I leave for an hour (or often a day or longer) before returning to them. Right now I have 11 of those...I estimate I spend more time prompting in these 'stale' sessions than sessions that I've recently started!"
> — [Simon Willison](https://simonwillison.net/2026/Apr/24/recent-claude-code-quality-reports/)

---

## 工程教训：Harness 质量是独立的能力维度

### 教训 1：harness 变更可以比模型变更更危险

当用户报告"AI 变笨了"时，第一反应通常是怀疑模型能力退化。但在这个案例中，模型完全没有问题——问题出在 harness 层对推理 effort、缓存行为和提示词的系统性变更。这些变更在隔离时可能看似合理，但组合效应产生了严重的负面效果。

### 教训 2：边缘 case 是 harness bug 的主要来源

第二个 bug 只在特定边缘情况触发（会话空闲超过 1 小时后的第一个 turn），这使得它难以通过常规测试发现。harness 系统因为需要处理多种上下文状态、多种会话恢复场景，所以比单纯调用模型 API 的系统有更多的边缘 case。

### 教训 3：多个实验同时存在会掩盖问题

Anthropic 提到两个"不相关的实验"让问题难以重现。在实际开发中，多个正交变更同时存在是常态，这使得单一变量的故障排查变得复杂。隔离测试环境和清晰的变更日志对于快速定位 harness 问题至关重要。

### 教训 4：用户感知与内部指标可能不一致

将默认 effort 从 high 改为 medium 的决策基于内部 evals 和测试，但用户实际偏好不同。Anthropic 承认 "neither our internal usage nor evals initially reproduced the issues"。这提醒我们：对于涉及用户体验的系统，AB 测试和早期用户反馈比纯内部指标更有价值。

### 教训 5：harness 的状态空间远大于模型调用

Claude Code 的 harness 需要管理：推理 effort、缓存策略、提示词内容、thinking 显示方式、上下文历史、工具状态——这些变量之间的组合产生了巨大的状态空间。模型 API 本身是稳定的，但 harness 的状态空间可以产生远大于模型能力波动的用户体验变化。

---

## 复盘方法的工程价值

Anthropic 在调查过程中使用 Claude Code 的 Code Review 功能来 back-test 造成问题的 PR：

> "As part of the investigation, we back-tested Code Review against the offending pull requests using Opus 4.7."
> — [Anthropic Engineering: April 23 Postmortem](https://www.anthropic.com/engineering/april-23-postmortem)

这展示了使用 agent 系统来验证 agent 系统本身的可能性——用 AI 辅助排查 AI 系统的问题。这种 meta-testing 方法在复杂系统中比传统调试更有效。

---

## 对 Agent 开发者的行动建议

### 监控层面

1. **Harness 层指标**：不要只监控模型 API 的延迟和错误率，还要监控 token 消耗速率（异常消耗可能是缓存 bug 的信号）、会话重建率（频繁重建可能是上下文丢失的信号）
2. **会话级可观测性**：在 agent 系统中，跟踪每个会话的上下文窗口使用率、工具调用成功率、任务完成率——这些指标比单纯的 API 层指标更能反映用户体验
3. **变更日志与灰度**：每次 harness 配置变更都需要独立的 changelog，并逐步推广而非全量部署

### 架构层面

1. **隔离 harness 状态**：将推理 effort、缓存策略、会话状态作为显式配置项而非隐式默认值
2. **幂等性设计**：工具调用和 API 请求应该幂等，以便在异常情况下安全重试
3. **边缘 case 测试**：不仅要测试 Happy Path，还要测试空闲会话恢复、多会话并发、长时间运行会话等边缘场景

### 认知层面

1. **模型能力 vs harness 配置**：当用户报告 AI 表现下降时，系统性排查应该包括：模型层（API 状态）+ harness 层（配置/缓存/提示词）+ 环境层（网络/工具状态）
2. **Agentic 系统的调试复杂度**：Agent 系统中的 bug 比简单 API 调用更难追踪，因为问题可能是级联的、延迟的、多因素组合的

---

## 结论

Claude Code 的六周质量下降事件是一次罕见的公开复盘——Anthropic 将内部事故分析的完整过程公开。这对于整个 Agent 工程领域都有重要的参考价值：模型本身没有问题，问题是 harness 层对推理 effort、上下文缓存和提示词的系统性变更。

这次事件的核心教训是：**harness 是独立的能力维度**。当你在构建 agentic 系统时，harness 的质量——上下文管理、缓存策略、提示词工程——可以产生比模型能力本身更大的用户体验变化。

> "This isn't the experience users should expect from Claude Code." — Anthropic

这也是任何构建生产级 Agent 系统的人需要记住的：用户期望的是稳定可靠的智能体表现，而这种稳定性来自对 harness 每一层变动的系统性管控。

---

**引用来源**：
- [Anthropic Engineering: An update on recent Claude Code quality reports (2026-04-23)](https://www.anthropic.com/engineering/april-23-postmortem)
- [Simon Willison: An update on recent Claude Code quality reports (2026-04-24)](https://simonwillison.net/2026/Apr/24/recent-claude-code-quality-reports/)

**相关资源**：
- [Anthropic Extended Thinking Documentation](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)
- [Anthropic Prompt Caching Documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) — 精选 harness 工程资源