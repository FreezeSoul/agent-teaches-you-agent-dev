# Anthropic Claude Code April 23 Postmortem：三个独立问题导致的质量回退

## 来源

- **原始链接**：https://www.anthropic.com/engineering/april-23-postmortem
- **发布时间**：2026 年 4 月 23 日
- **官方标题**：An update on recent Claude Code quality reports
- **引用来源**：Anthropic Engineering Blog

---

## 事件概述

2026 年 3-4 月，Claude Code 用户广泛报告响应质量下降。Anthropic 经过调查，于 4 月 23 日发布正式报告，将问题归因于**三个独立的、互不相关的变更**，而非模型能力本身下降。

> "We traced recent reports of Claude's responses to three separate changes that affected Claude Code, the Claude Agent SDK, and Claude Coworker. The API was not impacted."

所有三个问题已于 4 月 20 日（v2.1.116）修复完毕。

---

## 三个独立问题详解

### 问题一：Reasoning Effort 默认值变更

| 项目 | 详情 |
|------|------|
| **变更日期** | 2026 年 3 月 4 日 |
| **变更内容** | 将 Claude Code 的默认 reasoning effort 从 `high` 改为 `medium` |
| **变更原因** | 用户反馈 Opus 4.6 在 high 模式下延迟过高，UI 有"冻结"感 |
| **回退日期** | 2026 年 4 月 7 日（用户反馈表明更偏好高智能） |
| **影响版本** | Sonnet 4.6、Opus 4.6 |

**技术背景**：

Claude Code 通过 `effort` 参数控制思考时间与延迟之间的 tradeoff。OpenAI 风格的推理模型在「思考越长→输出越好」的曲线上的不同点，Anthropic 在产品层选择了 medium 作为默认值以减少延迟和 token 消耗。

**问题本质**：

内部测试表明 medium 达到了略低的智能水平但显著降低了延迟。然而大多数用户保留了这个默认值，导致 Claude Code 感觉"不如以前聪明"。

> "We reverted on April 7. All users now default to xhigh effort for Opus 4.7, and high effort for all other models."

**教训**：
- 降低智能以换取延迟是一个危险的 tradeoff，需要更广泛的用户反馈
- 默认值的变更应经过更长的 soak period 和渐进 rollout

---

### 问题二：缓存优化导致的 Thinking 历史清除 Bug

| 项目 | 详情 |
|------|------|
| **变更日期** | 2026 年 3 月 26 日 |
| **变更内容** | 引入清除旧 thinking 的逻辑（针对空闲超过 1 小时的会话）以减少恢复时的延迟 |
| **Bug** | 原计划一次性清除变成了**每轮都清除**，持续丢弃除最新块外的所有 reasoning |
| **发现日期** | 约 4 月 10 日 |
| **修复版本** | v2.1.101 |
| **影响版本** | Sonnet 4.6、Opus 4.6 |

**技术机制**：

Anthropic 使用 prompt caching 来降低 API 调用成本。当会话空闲超 1 小时后，缓存自然失效，此时清理旧 thinking 是合理的优化。

设计使用了 `clear_thinking_20251015` API header 配合 `keep:1`，意图是恢复时不再发送旧的 reasoning，从而节省 uncached tokens。

**Bug 的复合效应**：

1. 每次 API 调用都会触发「仅保留最新 reasoning 块」的行为
2. 这导致后续请求全部 cache miss
3. 用户感受到「遗忘」和「重复」——Claude 不知道之前为什么做了那个选择
4. 复合效应：cache miss 导致 usage limits 消耗速度超出预期

**根因分析**：

这个 bug 跨越了 Claude Code 的上下文管理、Anthropic API 和 extended thinking 的交界面。它通过了：
- 多人代码审查
- 自动化代码审查
- 单元测试
- 端到端测试
- 自动化验证
- 内测（dogfooding）

Anthropic 指出两个无关的实验让问题难以复现：
1. 一个服务端消息队列相关的内部实验
2. 一个 thinking 显示方式的变化掩盖了 bug 在大多数 CLI 会话中的表现

**关键发现**：

> "As part of the investigation, we back-tested Code Review against the offending pull requests using Opus 4.7. When provided the code repositories necessary to gather complete context, Opus 4.7 found the bug, while Opus 4.6 didn't."

这说明更强大的模型（ Opus 4.7 ）可以作为 Code Review 的工具发现这类 bug。Anthropic 决定改进其 Code Review 工具并向客户发布。

**教训**：
- 与缓存机制结合的逻辑需要 corner case 测试
- 跨层（产品层↔API 层）的 bug 难以通过单一组件的测试覆盖
- 更强大的模型可以辅助代码审查

---

### 问题三：System Prompt 长度限制指令

| 项目 | 详情 |
|------|------|
| **变更日期** | 2026 年 4 月 16 日 |
| **变更内容** | 添加 system prompt 指令："keep text between tool calls to ≤25 words. Keep final responses to ≤100 words" |
| **触发背景** | Claude Opus 4.7 比前代更冗长，需要调优 harness |
| **回退日期** | 2026 年 4 月 20 日 |
| **影响版本** | Sonnet 4.6、Opus 4.6、Opus 4.7 |

**变更意图**：

Opus 4.7 发布时，Anthropic 已知它比 Opus 4.6 更冗长（这是它更聪明的一面）。他们动用了多种手段（模型训练、prompting、产品 thinking UX 改进），其中一条 system prompt 指令导致了不成比例的智能下降。

**测试盲点**：

多周的内部测试和评估套件运行未发现回归。最终在更大范围的 ablation（逐行移除 system prompt 行以理解影响）中发现了 **3% 的下降**（Sonnet 4.6 和 Opus 4.7 均受影响），才触发回退。

**教训**：
- System prompt 中的每一条指令都可能 trade off 智能
- 针对特定模型的变更需要 gate 到该模型
- Ablition 测试应该覆盖更广泛的评估集

---

## 工程改进措施

Anthropic 宣布了以下改进，以防止类似问题再次发生：

### 1. 内部测试环境对齐

> "We'll ensure that a larger share of internal staff use the exact public build of Claude Code"

确保内部使用的版本与对外发布的版本一致。

### 2. 改进 Code Review 工具

将内部使用的改进版 Code Review 工具发布给客户。支持将额外代码仓库作为 context 输入。

### 3. System Prompt 变更管控

- 所有 system prompt 变更运行per-model 评估套件
- 继续 ablation 测试理解每行影响
- 构建新工具使 prompt 变更更易于审查和审计
- 将模型特定变更 gate 到对应模型

### 4. Intelligence Tradeoff 的渐进 rollout

> "For any change that could trade off against intelligence, we'll add soak periods, a broader eval suite, and gradual rollouts so we catch issues earlier."

---

## 工程警示录价值

### 1. Product Layer Bug 的危险性

三个问题都发生在**产品层**（Claude Code harness），而非 API 层。这说明即使模型本身没有问题，产品层的微调也可能严重影响用户体验。

### 2. 缓存与 Thinking 的交互

Prompt caching 与 extended thinking 的交互是一个容易被忽视的复杂边界。缓存失效后的行为与正常会话的行为可能不同。

### 3. System Prompt 的智能 Tradeoff

> "Length limits: keep text between tool calls to ≤25 words. Keep final responses to ≤100 words unless the task requires more detail."

这条看似无害的指令导致了不成比例的影响。System prompt 的每一条指令都是一种约束，需要仔细评估。

### 4. 评估套件的局限性

即使有自动化评估套件也可能漏掉 corner case。评估需要覆盖：
- 不同 effort 级别
- 不同会话状态（idle、active、mixed）
- 不同模型

### 5. 更强模型用于 Code Review

有趣的是，Opus 4.7 能够发现 Opus 4.6 无法发现的 bug。更强的模型可以用作 code review 工具。

---

## 相关文献

- [Anthropic April 23 Postmortem 原文](https://www.anthropic.com/engineering/april-23-postmortem)
- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [Anthropic Code Review 工具](https://code.claude.com/docs/en/code-review)
- [Prompt Caching Lessons](https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything)

---

*本篇由 AgentKeeper 自动整理，来源：Anthropic Engineering Blog（2026 年 4 月 23 日），作为工程警示录归档于 harness/ 目录。*
