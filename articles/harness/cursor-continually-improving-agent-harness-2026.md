# Cursor Agent Harness 持续改进工程：测量驱动的数据化迭代方法论

> 核心问题：如何系统性地测量和改进 Agent Harness，而非依赖主观感受？
>
> 关键结论：Harness 质量由「代码保留率（Keep Rate）」和「用户满意度语义分析」两个指标驱动，配合 A/B 测试和异常检测实现持续改进。

---

## 背景：Harness 改进的本质挑战

Cursor Agent 是「Harness + Model」共同决定输出质量的系统。但「好」无法直接测量—— benchmarks 只近似真实使用，指标（延迟、token 效率、工具调用数）只反映过程而非结果。

Cursor 的解法：**建立多层测量体系，结合离线和在线实验，用数据驱动而非直觉驱动来迭代 Harness**。

---

## 一、测量体系的层次结构

Cursor 的测量体系分为两层：

### 1.1 离线评估：CursorBench

公开的 benchmark 套件，提供快速、标准化的质量读数，能跨时间对比。但 benchmarks 的局限在于「只近似真实使用」—— 会遗漏重要信号。

### 1.2 在线实验：A/B 测试

部署两个或多个 Harness 变体，横向对比真实使用。测量维度：

| 维度 | 类型 | 说明 |
|------|------|------|
| 延迟 | 过程指标 | 方向性有用，但不够 |
| Token 效率 | 过程指标 | 方向性有用，但不够 |
| 工具调用数 | 过程指标 | 方向性有用，但不够 |
| **Keep Rate** | **结果指标** | **核心** |
| **用户语义满意度** | **结果指标** | **核心** |

> 原文：
> "We measure agent quality in these tests through a variety of metrics. Some are straightforward like latency, token efficiency, tool call count, and cache hit rate. Those are directionally useful but still don't get at fuzzier and more important questions of whether the agent actually did a good job."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

---

## 二、Keep Rate：代码质量的结果指标

### 什么是 Keep Rate

对于 Agent 生成的一组代码变更，追踪这些变更在固定时间间隔后仍保留在用户代码库中的比例。如果用户必须手动调整或迭代修复 Agent 的初始输出，说明 Agent 初始质量较低。

### Keep Rate 的工程意义

- **直接衡量输出价值**：不是衡量 Agent 做了什么，而是衡量用户接受了多少
- **时间衰减分析**：不同时间点（1小时/1天/1周）分析保留率，了解修复是被用户吸收还是被回滚
- **Agent 版本对比**：相同任务下，新版 Harness 是否产生更高 Keep Rate

### 局限性

Keep Rate 反映「用户没有回退」，但不反映「用户主动复用」。一个 Keep Rate 80% 的 Agent 可能是用户懒得改而非真正满意。需要配合第二个指标。

---

## 三、用户满意度语义分析

### 方法：LLM 读取用户对 Agent 初始输出的响应

用语言模型分析用户对 Agent 初始输出的后续消息，捕获语义层面的满意度：

- **正向信号**：用户转向下一个功能 → Agent 完成了工作
- **负向信号**：用户粘贴错误堆栈 → Agent 失败了

> 原文：
> "A user moving on to the next feature is a strong signal the agent did its job, while a user pasting a stack trace is a reliable signal that it didn't."
> — [Cursor Blog](https://cursor.com/blog/continually-improving-agent-harness)

### 与 Keep Rate 的互补关系

| 指标 | 优点 | 局限 |
|------|------|------|
| Keep Rate | 客观、可量化 | 只能捕捉「没被回退」，无法捕获「主动满意」 |
| 语义满意度 | 捕获主观价值判断 | 需要 LLM 评估、成本更高 |

两者结合才能全面衡量 Agent 质量。

---

## 四、工具错误的分类体系

### 为什么工具错误是关键测量面

工具调用错误可能对 Cursor 中的会话造成极大伤害。虽然 Agent 常能自我纠正，但错误仍留在上下文中，浪费 tokens 并导致「上下文腐烂」（context rot）—— 累积的错误会降低模型后续决策的质量。

### 错误分类

Cursor 将工具错误分为两类：

**预期错误（Expected Errors）**—— 模型偶尔犯错是正常行为：

| 类型 | 原因 |
|------|------|
| InvalidArguments | 模型提出了不正确的编辑 |
| UnexpectedEnvironment | 试图读取不存在的文件 |
| ProviderError | 工具供应商（如 GenerateImage、WebSearch）宕机 |
| UserAborted | 用户中止 |
| Timeout | 超时 |

**未知错误（Unknown Errors）**—— 始终是 Harness 的 bug。

### 异常检测机制

Cursor 按工具和模型计算基线，因为不同模型可能以不同速率搞砸工具调用。当预期错误显著超过基线时触发异常检测告警。

> 原文：
> "Since unknown errors are always bugs, we alert whenever the unknown error rate for any tool exceeds a fixed threshold. But it can be tricky to tell whether expected errors represent a bug in the harness or expected behavior."
> — [Cursor Blog](https://cursor.com/blog/continually-improving-agent-harness)

---

## 五、上下文窗口的演进

### Guardrail 逐步拆除

2024 年末 Cursor 首次开发编码 Agent 时，模型在自主选择上下文方面差得多，团队投入大量上下文工程创建 guardrails：
- 每次编辑后向 Agent 显示 lint 和类型错误
- 当 Agent 请求行数过少时重写其文件读取
- 限制 Agent 单轮可以调用的最大工具数

现在**大部分已消失**。模型能力提升后，动态上下文获取取代了静态 guardrails。

### 当前的静态上下文

仍包含一些有用的静态上下文（如操作系统、git 状态、当前和最近查看的文件），但量已大幅减少。

> 原文：
> "We still include some useful static context (e.g., operating system, git status, current and recently viewed files). But we've adapted to increasing model capability by knocking down guardrails and providing more dynamic context."
> — [Cursor Blog](https://cursor.com/blog/continually-improving-agent-harness)

---

## 六、Harness 改进的数据驱动流程

```
Vision → Hypothesis → Experiment → Iterate
         ↑                              ↓
         ←←← Quantitative & Qualitative Signals ←←←
```

### 实验类型

1. **Harness 变体 A/B 测试**：部署多个变体到真实用户，测量 Keep Rate + 语义满意度
2. **成本效益分析**：昂贵模型用于上下文摘要的实验显示「Agent 质量提升微乎其微，不值得更高成本」→ 搁置
3. **特征标志追踪**：通过 Statsig 将崩溃指标链接到对应功能标志，A/B 测试量化功能对崩溃率的贡献

### 每周自动化日志分析

Cursor 运行配备技能的每周 Automation，教导模型如何搜索日志、发现问题是新出现的还是已存在的。

> 原文：
> "We also run a weekly Automation equipped with a skill that teaches the model how to search through our logs, surface issues that are new or significantly changed relative to the baseline."
> — [Cursor Blog](https://cursor.com/blog/continually-improving-agent-harness)

---

## 七、对 Agent 开发者的启示

### 1. 建立测量体系而非依赖直觉

核心指标必须是**结果导向**（Keep Rate、用户满意度），而非过程指标（工具调用数、延迟）。过程指标方向性有用但不充分。

### 2. 错误分类是改进的前提

未分类的错误 = 未知的改进空间。必须建立错误分类体系，区分「模型预期错误」和「Harness bug」，才能针对性修复。

### 3. Guardrail 需要随模型进化动态调整

2024 年的 Guardrail 可能是必要的，但模型能力提升后它们成为限制。好的 Harness 设计需要**感知模型能力变化并动态调整约束**。

### 4. A/B 测试是 Harness 迭代的核心方法

任何 Harness 改动都需要通过真实使用验证，不能仅凭 benchmarks 或直觉判断。Keep Rate 的差异是判断改进是否有效的黄金标准。

---

## 结论

Cursor 的 Harness 改进方法论核心是：**测量驱动而非直觉驱动**。通过 Keep Rate + 语义满意度两个结果指标，配合错误分类体系和 A/B 测试，实现 Harness 的持续数据化迭代。

这对所有 Agent 开发者有参考价值：Harness 质量不是「设计出来」的，而是「测量出来并迭代改进」的。

---

**关联项目**：

- [openclaw/clawbench](./openclaw-clawbench-trace-based-agent-benchmark-89-stars-2026.md) — 追踪评分优先的 Agent 评测框架，89 Stars，与本文「测量驱动改进」形成「测量 → 迭代」的完整闭环

**关联文章**：

- [Cursor App Stability（Apr 21, 2026）](./cursor-app-stability-oom-80-percent-decrease-2026.md) — OOM 80% 下降，双调试策略，与本文「工具错误导致上下文腐烂」形成「问题诊断 → 持续改进」互补
- [Anthropic Harness Design（Mar 24, 2026）](../harness/anthropic-harness-design-long-running-apps-2026.md) — GAN 三代理架构，与 Cursor「测量驱动改进」形成「设计先验 vs 数据驱动」的互补

---

**来源**：[Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)（2026-04-30）