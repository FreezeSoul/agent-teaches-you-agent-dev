# Agentic Coding 时代的人才评估悖论：为什么 AI 能解决的问题越多，评估人的能力就越难

> 核心论点：Anthropic 的工程团队用四年时间迭代出一个结论——当模型的解题能力超越人类后，传统评估设计的核心假设（"谁解决问题更好，谁就更优秀"）就会失效。在 Agentic Coding 时代，人才评估的真正问题不是「AI 能否解决」，而是「在给定约束下，AI 和人类的边界在哪里」。

---

## 问题的起源：一次失败的评估设计

2023 年 11 月，Anthropic 的性能工程团队面临一个具体问题——他们需要大规模招聘性能工程师，但现有的面试流程无法处理大量候选人。Tristan Hume 花了两周设计了一个上机测试：让候选人在一个模拟加速器上优化一段并行树遍历代码，4 小时，工具随意用。

这个设计的核心假设是：

1. **长时间窗口**：真实工作中的性能优化通常需要数小时，而非 50 分钟的面试
2. **AI 辅助兼容性**：题目明确允许使用 AI 工具，考察候选人在真实工作环境中的表现
3. **高区分度**：题目有足够深度，即使最强的候选人也在 4 小时内无法完成所有优化

最初这个设计运行良好——1000 名候选人完成测试，数十人入职，其中一些最高绩效的工程师直接从本科毕业就通过了测试。

**但问题从 2025 年 5 月开始显现**：Claude Opus 4 在 2 小时限制内给出的解答比几乎所有人类候选人都更优化。

> "We had a problem. We were about to release a model where the best strategy on our take-home would be delegating to Claude Code."
> — [Anthropic Engineering: Designing AI Resistant Technical Evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

---

## 核心悖论：AI 的优势恰恰是评估设计的致命缺陷

为什么让 Claude Opus 4 变得「更好」反而让评估变得更难？答案在于**约束条件的双重角色**。

### 1. 约束曾是保护，现在成了漏洞

传统面试设计用约束来保护人类：时间限制、问题复杂度、资源边界。这些约束让人类有机会在特定维度展示优势。当 AI 能在这些约束内完全超越人类时，约束的保护意义就消失了——它变成了一个规则，人类遵守它，AI 利用它。

### 2. AI 的「足够好」 vs 人类的「更好」

Claude Opus 4.5 在 2 小时内达到的解决方案质量已经与在同等时间内表现最好的人类相当（那个人还重度使用了 Claude 4 steering）。这不是「比人类更好」，而是「与最强人类持平」——但这个持平意味着什么？

> "For several months the take-home worked well — then Claude Opus 4.5 defeated that."
> — [Anthropic Engineering: Designing AI Resistant Technical Evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

Anthropic 的团队测试了一个更难的版本（基于真实 kernel 优化的数据转置问题），Claude Opus 4.5 找到了一个他们自己都没想到的优化方向——不是转置数据，而是转置整个计算。

**这是 AI 的典型优势**：在给定空间内找到人类想不到的解法。但这也意味着这个方向无法用于区分人类能力——因为没有任何人类能在相同约束下想到它。

### 3. 给 AI 时间，它会继续进步；给人时间，人类的优势在无限时间上

这是最关键的观察：当给 Claude Opus 4.5 无限时间并告知其可能的最高分数时，它能够收敛到那个分数。但人类的优势在于：在无限制时间内，最强人类的表现仍然超过 Claude Opus 4.5 的极限。

Anthropic 将这个问题作为开放挑战发布——如果你能在无限时间内打败 Opus 4.5，他们很愿意听。

> "If you can best Opus 4.5, we'd love to hear from you — details are at the bottom of this post."
> — [Anthropic Engineering: Designing AI Resistant Technical Evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

---

## 三次迭代揭示的工程设计原则

### 迭代一（v1 → v2）：增加问题深度

当 Claude Opus 4 在 4 小时内超越大多数人时，Anthropic 的反应是：

1. 缩短时间：4 小时 → 2 小时（减少 AI 探索空间）
2. 增加问题深度：找到 Claude Opus 4 开始遇到困难的地方，作为 v2 的起点
3. 移除 multicore（Claude 已经完全解决，无需考察）

这个迭代的原则是**用 AI 对抗 AI**——用更强的 AI 找到人类与 AI 边界的精确位置。

### 迭代二（v2 → v3）：从「更难」到「更奇怪」

当 Claude Opus 4.5 在 2 小时内与最强人类持平后，Anthropic 尝试了一个完全不同的方向——**寻找超出 AI 训练分布的问题**。

他们选择了 Zachtronics 游戏风格的问题——那些需要非常规推理、但仍然代表真实工作技能的问题。思路是：AI 在已知领域的经验远超过任何个体，但在未知/非常规领域，人类的推理能力可能保持优势。

> "I needed a problem where human reasoning could win over Claude's larger experience base: something sufficiently out of distribution."
> — [Anthropic Engineering: Designing AI Resistant Technical Evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

但这个方向与「代表性真实工作」的目标存在根本矛盾——真实工作的技能通常是有规律、可学习的，而这正是 AI 的优势所在。

### 迭代三：重新审视「评估的是什么」

在所有技术迭代都失效后，Anthropic 团队开始重新思考一个更根本的问题：**什么是性能工程师在真实工作中不可替代的部分？**

他们发现：

- **优化代码本身**：AI 已经能做得和最好的人类一样好
- **调试复杂系统**：这可能还能区分一段时间
- **系统设计**：需要在真实约束下做权衡，没有标准答案
- **验证正确性**：理解模型在做什么，为什么这样做，如何改进

这些都是 AI 辅助下的「人类判断力」问题，而非「人类执行能力」问题。

> "It's always been hard to design interviews that represent the job, but now it's harder than ever."
> — [Anthropic Engineering: Designing AI Resistant Technical Evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

---

## 对 Agentic Coding 时代的启示

### 1. 评估设计必须从「解决问题」转向「约束下的判断力」

当 AI 能解决任何给定的问题时，评估的核心应该是：**谁能在给定约束下做出更好的判断**。这意味着：

- 不再考察「能否找到解」，而是考察「能否判断什么值得优化」
- 不再考察「能否完成任务」，而是考察「能否理解 AI 的行为并指导它」
- 不再考察「单独的峰值能力」，而是考察「在长周期内的稳定判断质量」

### 2. Agentic Coding 的能力分层开始显现

基于 Anthropic 的经验，Agentic Coding 时代的能力分层正在形成：

| 层级 | 能力描述 | AI 可替代性 | 评估方式 |
|------|---------|------------|---------|
| **L1: 任务执行** | 接收明确指令，完成具体编码任务 | ✅ 完全可替代 | 传统 coding 面试已失效 |
| **L2: 工具协同** | 理解 AI 工具的能力边界，有效调度工具 | 🔄 部分可替代 | 需要在真实项目中观察 |
| **L3: 判断引导** | 在模糊需求下做出判断，引导 AI 方向 | ❌ 目前难以替代 | 模拟真实约束场景 |
| **L4: 系统设计** | 在复杂约束下设计系统，权衡取舍 | ❌ 目前难以替代 | Design review with AI |

### 3. 评估的「AI 抵抗性」将成为一个工程问题

Anthropic 的经验表明，评估设计现在需要主动考虑「这道题被 AI 解决的最优路径是什么」。这意味着：

1. **评估设计需要 AI 对抗性分析**：每道题在发布前，都要由最强 AI 试做，找到其失效点
2. **评估需要动态更新**：随着模型能力提升，评估题库必须持续迭代
3. **无限时间基准测试**：用无限时间的 AI 表现作为锚点，定义「人类独有」的空间

>笔者认为，这种评估设计思路会渗透到所有 Agentic Coding 相关的认证体系中——不只是 Anthropic 自己招聘，未来行业内的 Agentic Coding 能力认证，都需要类似的「AI 抵抗性」评估框架。

---

## 结论：评估的终极问题不是「人能做什么」，而是「人必须做什么」

当 AI 能完成几乎所有技术任务时，评估设计的核心问题不再是「我们如何找到最强的程序员」，而是「我们如何找到那些在 AI 辅助下仍然能做出正确判断的人」。

这个转变的影响远超招聘本身——它意味着：

1. **教育目标需要重新定义**：从「教会学生编程」到「教会学生在 AI 辅助下做判断」
2. **职业发展路径需要重塑**：从「执行能力」到「判断质量和方向感」
3. **团队结构需要调整**：AI 能做执行，但方向判断需要人类，而这种人类越来越少、越来越贵

Anthropic 的开放挑战（击败 Opus 4.5 的无限时间上限）本质上是提出了一个更深的问题：**在 AI 能做任何事的时代，什么是人类仍然不可替代的？**

这个问题目前没有答案。但可以确定的是，答案不在「谁写代码更好」这类传统评估维度里。

---

## 关联项目

本篇文章分析的 Agentic Coding 人才评估悖论，与 Mem0 v3 的新内存算法形成了一个有趣的呼应——**两者都在处理约束下的信息保留问题**：

Mem0 v3（2026 年 4 月）用 ADD-only 的约束设计解决了长程 Agent 内存质量问题：在无限累积的记忆中，不覆盖、只新增，让 AI 在回忆时能基于完整的演化历史做判断。这个约束（不删除）恰恰与评估设计中的约束（不超时）是同一类工程选择——**通过精心设计的约束，让系统在能力边界处仍然保持有效信号**。

详细分析见：[mem0-v3-memory-algorithm-loCoMo-91-6](./mem0-v3-memory-algorithm-loCoMo-91-6.md)

---

## 参考来源

- [Anthropic Engineering: Designing AI Resistant Technical Evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)
- [Anthropic Engineering Blog](https://www.anthropic.com/engineering)
- [Mem0 GitHub Repository](https://github.com/mem0ai/mem0)