# Anthropic 的 2026 年四月事后分析：三个改动如何造成不可见的智能退化

> **核心主张**：Anthropic 2026 年 4 月的事后分析揭示了一个关键工程教训——**Agent 系统的智能退化很少来自模型本身，而几乎总是来自 Harness 层的三类隐蔽改动**：默认参数的下游效应、缓存清理逻辑的实现 Bug，以及系统提示词中看似无害的字数限制指令。这篇文章深度拆解这三个改动的机制链，以及 Anthropic 给出的修复框架。

**来源**：[Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)（2026-04-23）

---

## 一、问题表象：用户感知到的「不可见退化」

2026 年 3-4 月，Anthropic 陆续收到用户报告，称 Claude Code 的回复质量下降。这些报告有两个特点：

1. **时间跨度不一致**：三个 issue 分别发生在 3 月 4 日、3 月 26 日和 4 月 16 日，时间线不重叠
2. **难以内部复现**：Anthropic 的内部使用和评估流程最初都没有重现用户发现的问题

这导致问题初期被当作「正常反馈波动」处理，直到用户通过 `/feedback` 命令提供了具体的可复现案例，问题才被定位。

> "We never intentionally degrade our models, and we were able to immediately confirm that our API and inference layer were unaffected."
> — [Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)

**关键洞察**：Agent 系统的质量下降经常是**聚合效应**——多个无害改动的叠加，造成整体感知退化，单个改动看都不严重，但累积效果足以改变用户体验。

---

## 二、改动一：默认推理努力度从 High 降至 Medium

### 背景

Claude Opus 4.6 在 Claude Code 中发布时，默认推理努力度设为 `high`。随后 Anthropic 收到反馈：High 模式下模型偶尔会思考过长，导致 UI 看起来像冻结了一样。

### 决策逻辑

Anthropic 内部测试表明，Medium 努力度在大多数任务上只有略微更低的智能水平，但显著降低了延迟和 Token 使用量。此外，Medium 模式避免了 High 模式偶尔出现的超长尾延迟问题，有助于最大化用户的 usage limits。

因此他们在 3 月 4 日将默认值切换为 Medium effort，并通过产品内对话框解释了这个决策。

### 后果

用户并不买账。大量用户反馈：他们宁愿接受更高延迟，也希望默认更高智能。Anthropic 随后通过多次 UI 设计迭代尝试让用户意识到可以切换努力度（启动通知、内联努力度选择器、恢复 ultrathin 模式），但大多数用户仍然停留在 Medium effort。

4 月 7 日，Anthropic 撤销了这个决策：Opus 4.7 默认 xhigh effort，其他模型默认 high effort。

### 工程教训

| 维度 | 教训 |
|------|------|
| **默认值的杠杆效应** | 用户很少主动调整默认设置，默认值决定了大多数用户体验 |
| **延迟 vs 智能的权衡** | 用户愿意为更高智能接受更高延迟，但开发者不一定愿意为低延迟接受更低智能 |
| **UI 提示的不充分性** | 多次设计迭代仍然无法驱动用户修改默认值——默认值的改变应该更保守 |

---

## 三、改动二：缓存优化引发的级联 Bug

### 设计目标

Anthropic 使用 **Prompt Caching** 来降低连续 API 调用的成本：当用户会话闲置超过 1 小时后，恢复时缓存会已经失效，此时可以清理旧有的 thinking blocks 来减少发送到 API 的未缓存 Token 数量。

设计逻辑是合理的：idle 超过 1 小时的会话重新激活时，清理旧 thinking 并从新开始，可以降低恢复成本。

### 实现 Bug

Anthropic 用 `clear_thinking_20251015` API header 配合 `keep:1` 参数来实现这个逻辑。但实现中有一个 Bug：

**正确逻辑**：当会话跨越 idle 阈值时，清除一次 thinking history。
**实际逻辑**：当会话跨越 idle 阈值后，**每个后续请求**都会清除 thinking history，而不仅是一次。

结果是一个级联效应：
- 第一轮：会话跨越 idle 阈值，thinking history 被清除一次
- 第二轮：新一轮请求再次携带 `keep:1` 标志，继续清除 thinking history
- 后续轮次：**连当前轮的 thinking 也在被清除**

Claude 继续执行，但越来越**失去了对「为什么选择这么做」的记忆**——表现为遗忘、重复和无意义的工具调用。

> "This surfaced as the forgetfulness, repetition, and odd tool choices people reported."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/april-23-postmortem)

### 为什么这个 Bug 难以发现

1. **单元测试未覆盖**：这个逻辑跨越 Claude Code 的上下文管理层和 Anthropic API 的扩展思考机制，边界条件未被测试覆盖
2. **两个不相干的实验干扰**：
   - 一个内部服务端消息队列实验
   - 一个正交的 thinking 显示方式改动，抑制了这个 Bug 在大多数 CLI 会话中的可见性
3. **角落情况**：只在「会话闲置超过 1 小时后重新激活」这个特定场景触发
4. **4 月 10 日修复**（v2.1.101），历时超过一周才定位根因

### 工程教训

| 维度 | 教训 |
|------|------|
| **跨层交互的 Bug** | 这个 Bug 跨越 Claude Code 的上下文管理、API header 语义和扩展思考三个层面，任何单一层次的测试都无法捕获 |
| **隐藏状态累积** | 级联式的上下文丢失比一次性丢失更难诊断——每次只丢失一点，需要多轮才能观察到明显异常 |
| **正交改动的干扰** | 看似无关的改动可能抑制了另一个改动的可见性——这是并行开发的风险 |
| **back-testing 的价值** | Anthropic 用 Opus 4.7 的 Code Review 工具测试了问题 PR，Opus 4.7 能找到这个 Bug，说明更强模型对这类「上下文完整性」问题更敏感 |

---

## 四、改动三：系统提示词中的字数限制

### 背景

Claude Opus 4.7 发布时有一个已知的行为特点：**倾向于更冗长的输出**。这在困难问题上更聪明，但也产生了更多输出 Token。

### 优化方案

Anthropic 在准备 Opus 4.7 的 Claude Code 版本时，决定添加一条系统提示词指令：

```
"Length limits: keep text between tool calls to ≤25 words. Keep final responses to ≤100 words unless the task requires more detail."
```

### 测试结果与后果

内部测试和评估没有发现回归。这个改动在 4 月 16 日随 Opus 4.7 发布。

然而，事后调查中，Anthropic 执行了更广泛的消融测试（移除系统提示词各行以理解每行影响），发现这条指令对 Opus 4.6 和 4.7 都造成了 **3% 的评估下降**——立即回滚到 4 月 20 日发布版本。

> "One of these evaluations showed a 3% drop for both Opus 4.6 and 4.7. We immediately reverted the prompt as part of the April 20 release."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/april-23-postmortem)

### 为什么内部测试未能捕获

- 消融测试套件不够广泛，没有覆盖这条特定指令的影响
- 3% 的下降在特定评估集上是信号，在其他评估集上被噪声掩盖
- **针对智能的改动需要更广泛的评估套件和 soak period**，而不是仅依赖常规回归测试

### 工程教训

| 维度 | 教训 |
|------|------|
| **系统提示词的风险** | 系统提示词中的指令可以产生 outsized effect on intelligence，且难以在窄范围测试中发现 |
| **消融测试的必要性** | 每次系统提示词改动都需要逐行消融测试，理解每行对智能的影响 |
| **字数限制的隐性代价** | 「简洁」指令可能被模型解读为「不输出推理过程」，从而影响解决复杂问题的质量 |
| **3% 的意义** | 在 Agent evals 中，3% 的差距可能是实际生产中的关键能力差距（如能否独立完成某个复杂任务） |

---

## 五、Anthropic 的系统性修复框架

### 1. 所有内部员工使用同一公开构建

之前部分内部员工使用带有未发布功能的特殊构建，无法反映公开版本的问题。现在强制所有内部使用公开构建。

### 2. 系统提示词变更的严格流程

Anthropic 宣布了新的系统提示词变更治理框架：

```
每次系统提示词变更：
① 对每个受影响模型运行全面评估套件（而非单一模型）
② 逐行消融测试，理解每行指令的影响
③ 新增 tooling 使提示词改动更易于审查和审计
④ 任何以智能交换简洁性/延迟的改动，增加 soak period + 渐进式 rollout
⑤ 模型特定改动必须 gate 到对应模型（通过 CLAUDE.md 配置）
```

### 3. 改用 Opus 4.7 进行 Code Review

Opus 4.7 在提供完整上下文时能发现 Opus 4.6 遗漏的 Bug。Anthropic 现在将 Opus 4.7 的 Code Review 工具用于验证内部 PR。

### 4. 用户反馈的直接接入

`/feedback` 命令是最终捕获这些问题的机制——用户的具体可复现示例是任何内部测试套件无法替代的。

---

## 六、三类改动的共性模式

| 改动类型 | 决策层级 | 风险特征 | 防护要求 |
|---------|---------|---------|---------|
| 默认参数 | 产品层 | 用户黏性强，默认值难以通过 UI 提示修改 | 默认值变更需要更保守的策略和更长的观察期 |
| 缓存清理 | 实现层 | 跨层 Bug，角落情况难以测试覆盖 | 边界条件测试 + 跨层集成测试 + 更广泛的 dogfooding |
| 系统提示词 | 指令层 | 指令的效果难以预测，消融测试是唯一可靠手段 | 逐行消融 + 广泛 eval + soak period |

---

## 七、> 笔者判断

Anthropic 的这份事后分析是 2026 年最有价值的 Agent 工程文档之一。它揭示了一个关键事实：

**Agent 系统的质量稳定性不是一个模型问题，而是一个系统工程问题。**

模型层面的改动（A/B 测试、版本切换）有成熟的工具链；Harness 层面的改动（参数默认值、缓存策略、系统提示词）则缺乏同等的工程严谨性。Anthropic 这次提出的「系统提示词变更治理框架」是行业稀缺的方法论，建议所有在生产环境部署 Agent 的团队对照自查。

三个改动的另一个共性是：**它们都是针对已知的某个问题的直接响应**——默认努力度是对 Latency 投诉的响应；缓存清理是对成本的响应；字数限制是对 Verbosity 投诉的响应。每一个单独的「优化」都是合理的，但它们在没有横向影响分析的情况下同时存在，最终叠加出不可接受的综合效果。

> 建议：任何 Agent 产品的改动流程应该加入「改动叠加分析」环节——当多个改动同时上线时，评估它们的交互效应，而不是假设各自独立。

---

**关联项目**：[asamassekou10/ship-safe](./asamassekou10-ship-safe-agent-permission-security-scanner-699-stars-2026.md) — Agent 安全扫描工具，与本文「系统性修复框架」形成「问题诊断 → 预防工具」的互补
