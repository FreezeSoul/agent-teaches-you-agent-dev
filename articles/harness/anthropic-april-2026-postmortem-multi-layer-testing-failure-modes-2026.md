# Anthropic April 2026 Postmortem：为何多层级测试仍然漏过 Agent 系统的结构性缺陷

**核心主张**：Anthropic 2026年4月的 Claude Code 质量回退事件揭示了一个被低估的问题——**Agent 系统中的缺陷具有跨层交叉的特性**，单个组件的正确性无法保证系统整体正确性。三个独立缺陷分别在 Context Management 层、API 层和 Prompt 层触发，却都在多层测试中"通过"后才上线。这个案例说明：Agent 工程的测试基础设施必须从「验证单个组件」转向「监控跨层交互的异常信号」。

**读者画像**：有 Agent 开发经验，理解 Harness 和 context window 概念，想了解为什么「所有测试都通过了」Agent 系统仍然会在生产环境出现严重缺陷。

**核心障碍**：传统软件测试假设缺陷来自「某个组件坏了」，但 Agent 系统的缺陷往往来自「多个正确组件的错误交互」——这种缺陷模式在单组件测试中完全不可见。

---

## 1. 事件回顾：三个缺陷，三种触发机制

2026年3月至4月间，Claude Code 用户报告质量下降。Anthropic 追踪到三个完全独立的缺陷：

### 1.1 缺陷 1：默认推理 Effort 的错误权衡（3月4日）

Claude Code 上线 Opus 4.6 时将默认推理 effort 设置为 `high`，但用户反馈高推理模式下 UI 偶发冻结、延迟过高。团队将其改为 `medium` 以降低延迟。

> "In our internal evals and testing, medium effort achieved slightly lower intelligence with significantly less latency for the majority of tasks. It also didn't suffer from the same issues with occasional very long tail latencies for thinking, and it helped maximize users' usage limits."
> — [Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)

问题是：**内部 evals 显示"略低智能 + 显著低延迟"是可接受的权衡，但用户的实际判断相反**——他们宁可等待也不愿接受降智。4月7日回滚。

### 1.2 缺陷 2：缓存优化导致的级联性 Context 丢失（3月26日）

团队为降低空闲会话恢复的延迟，设计了一个"空闲超过1小时清除旧 thinking 块"的优化。使用 `clear_thinking_20251015` API header + `keep:1` 参数。

实现 bug：清除逻辑对每个后续请求都触发，而不是只触发一次。

> "Instead of clearing thinking history once, it cleared it on every turn for the rest of the session. After a session crossed the idle threshold once, each request for the rest of that process told the API to keep only the most recent block of reasoning and discard everything before it."
> — [Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)

后果是灾难性的叠加效应：
- 每次请求都丢失之前的 reasoning history
- 如果用户在 Claude 执行工具调用时发消息，该轮次的 reasoning 也被丢弃
- 最终 Claude 失去对「自己为什么选择这样做」的记忆，表现为「遗忘、重复、奇怪的工具选择」
- 持续丢失 thinking blocks 也导致持续的 cache miss，用户的 usage limits 消耗速度异常

这个 bug 的关键特征：**它只在「会话空闲后恢复」这个 corner case 下触发**。

### 1.3 缺陷 3：Prompt 长度限制损伤编码智能（4月16日）

Opus 4.7 比前代更冗长（这是其更高智能的副产品）。团队在 system prompt 中添加了一条指令：

> "Length limits: keep text between tool calls to ≤25 words. Keep final responses to ≤100 words unless the task requires more detail."

多个星期内部测试 + 原有 eval 套件均未发现回归。4月16日随 Opus 4.7 上线。4月20日回滚——因为 ablation（逐行移除 prompt 指令以理解每行影响）发现了 3% 的智能下降。

---

## 2. 为什么多层测试都漏过了？

这是本次 postmortem 最具工程价值的问题。三个缺陷都通过了什么测试？

| 测试类型 | 缺陷1 | 缺陷2 | 缺陷3 |
|---------|--------|--------|--------|
| 人类代码审查 | ✅ | ✅ | ✅ |
| 单元测试 | ✅ | ✅ | ✅ |
| 端到端测试 | ✅ | ✅ | ✅ |
| 自动化验证 | ✅ | ✅ | ✅ |
| Dogfooding（团队自用）| ✅ | ❌（被其他实验压制）| ✅ |
| 内部 usage | ✅ | ❌（无法复现 corner case）| ✅ |
| 原有 eval 套件 | ✅ | ✅ | ❌（eval 覆盖不足）|

### 2.1 跨层交互缺陷的不可测试性

缺陷2是教科书式的跨层交互失败：

```
Harness 逻辑（Claude Code 层）
    ↓ 发送 clear_thinking API header
Anthropic API 层
    ↓ 触发 extended thinking 行为
Context Management 层
```

Bug 在 Harness 层引入，但在 API+Thinking+Context 三层交互时才显现。单层测试（无论是 harness 单元测试还是 API 功能测试）都无法触发这个缺陷。

> 官方原文：
> "This bug was at the intersection of Claude Code's context management, the Anthropic API, and extended thinking. The changes it introduced made it past multiple human and automated code reviews, as well as unit tests, end-to-end tests, automated verification, and dogfooding."
> — [Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)

### 2.2 Corner Case 的探测困境

缺陷2只在「会话空闲超过1小时」后首次恢复时触发。这是一个低频 corner case：

- **内部测试困难**：开发者不会让会话空闲1小时再测试
- **Evals 不覆盖**：大多数自动化 evals 不会模拟长 idle 周期
- **Dogfooding 被压制**：另一个正交的基础设施实验压制了这个 bug 在大多数 CLI 会话中的可见性

> 官方原文：
> "Two unrelated experiments made it challenging for us to reproduce the issue at first: an internal-only server-side experiment related to message queuing; and an orthogonal change in how we display thinking suppressed this bug in most CLI sessions."
> — [Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)

### 2.3 Eval 覆盖不足的结构性问题

缺陷3暴露了 eval 设计的根本局限：

- 原有 eval 套件设计时没有覆盖「system prompt 中存在长度限制」的场景
- 当你改变模型输出长度的分布时，某种类型的任务会系统性变差——但你的 eval 必须专门针对这类任务才能检测到
- 更大范围的 ablation（在 broader eval 套件上逐行移除 prompt）才发现了 3% 的下降

> 笔者认为：Eval 套件存在「先验覆盖偏差」——你能检测到的退步类型，就是你在设计 eval 时预期到的类型。对于「意外交互效应」，即使造成重大损伤，也很难被现有 evals 发现。

---

## 3. Opus 4.7 Code Review 能力：讽刺性的发现

在调查缺陷2时，Anthropic 用 Opus 4.7 的 Code Review 功能回测了引入 bug 的 Pull Request：

> "When provided the code repositories necessary to gather complete context, Opus 4.7 found the bug, while Opus 4.6 didn't."

这是讽刺性的发现：一个旨在提升代码质量的功能，在自身导致质量下降之前，先发现了导致质量下降的 bug。

这揭示了一个有趣的可能性：**更强推理能力的模型在「完整上下文」下能发现其他较弱模型忽略的缺陷**。这个观察与「extended thinking」能力的研究方向一致——更多的 reasoning 预算使得模型能看到更长的因果链。

---

## 4. 防止类似缺陷的工程实践

### 4.1 系统性改变需要渐进式 rollout + soak period

Anthropic 承诺对任何「可能以智能换取其他属性」的系统 prompt 变更：

- 运行更大范围的 per-model eval 套件
- 增加 soaking period（让变更在真实流量中运行一段时间再判断）
- 渐进式 rollout（5% → 20% → 50% → 100%）

### 4.2 Prompt 变更的可审计性

团队新建了 tooling 使 prompt 变更更易于审查和审计：

- 每次 prompt 变更的结构化 diff
- 变更影响的 eval 覆盖范围记录
- 模型特定变更的 gated rollout（针对特定模型而不是批量部署）

### 4.3 长期：让更强模型参与 Code Review

> 笔者认为：这个发现暗示了未来 AI 辅助测试的方向——不是让模型运行已有的测试套件，而是让模型（尤其是具有更强 reasoning 能力的模型）作为「变更的审查者」，主动寻找测试未覆盖的 corner case。

---

## 5. 工程启示：测试基础设施的范式转变

### 5.1 从组件测试到交互信号监控

传统软件测试范式：
```
组件A → 组件B → 组件C
测试：A正确？B正确？C正确？
```

Agent 系统的测试范式需要：
```
Harness ←→ API ←→ Model ←→ Context
         ↑
    监控异常交互信号
```

关键是**主动探测跨层交互的异常**，而不是假设单层正确就能保证系统正确。

### 5.2 Corner Case 的系统性暴露策略

| 策略 | 说明 |
|------|------|
| 随机化测试 | 在测试中随机注入 idle 周期、网络延迟、资源竞争 |
| 故障注入 | 主动制造组件间通信的异常（延迟、丢失、乱序）|
| 基于属性的测试 | 定义 Agent 系统的 invariants（如：输出长度变化 < 20% 不应导致任务成功率下降 > 5%）|
| 影子模式部署 | 新版本在影子模式下接收真实流量，不影响用户，监控偏差 |

### 5.3 Eval 的先验覆盖与主动扩展

Eval 套件需要定期被挑战：

- 每季度增加「基于上季度事故的」负面测试案例
- 将 postmortem 中的缺陷模式转化为自动化回归测试
- 用更强模型发现现有 evals 的盲区

---

## 6. 结论

Anthropic 的 April 2026 Postmortem 揭示了一个核心矛盾：**Agent 系统的能力越强、越复杂，就越难通过传统测试保证其正确性**。

三个缺陷都通过了所有常规测试，原因是：
1. 跨层交互缺陷在单层测试中不可见
2. Corner case 的组合爆炸使得系统性测试困难
3. Eval 套件存在先验覆盖偏差

解法不是「更多测试」，而是：
- **测试基础设施从组件验证转向交互监控**
- **Corner case 暴露的系统化方法**（随机化、故障注入、影子模式）
- **用更强模型发现较弱模型的盲区**（Opus 4.7 发现 Opus 4.6 的 bug）

> 官方原文引用：
> "We are also adding tighter controls on system prompt changes. We will run a broad suite of per-model evals for every system prompt change to Claude Code, continuing ablations to understand the impact of each line, and we have built new tooling to make prompt changes easier to review and audit."
> — [Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)

---

**相关资源**：
- [Anthropic Engineering: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)
- [Claude Code Documentation: Code Review](https://code.claude.com/docs/en/code-review)
- [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
