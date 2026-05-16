# 第三纪元来临：Cloud Agents 带来的开发者关系重构

> 来源：[Cursor Blog — The third era of AI software development](https://cursor.com/blog/third-era)（2026-02-26）
> 主题关联：Anthropic Skills 项目推荐（Agent Skills 标准化生态）

---

## 这篇文章要回答什么问题

**为什么 AI 编程正在从「人盯着 AI 干活」转向「人定义问题，AI 自主完成」？这个转变对开发者意味着什么？**

过去几年我们经历了两个阶段：
- **第一纪元**：Tab 自动补全，一个按键一个按键地写代码
- **第二纪元**：同步 Agent，Prompt → Response → Prompt → Response，开发者全程在场

现在 Cursor 断言，第三纪元已经到来——Agent 自主完成更大任务、更长时间跨度的开发工作，人类角色从「操作者」变成「定义者和评审者」。

笔者认为，这个判断不仅描述了 Cursor 的产品方向，更揭示了 2026 年 AI Coding 领域的核心结构性转变：**开发者的生产力单位不再是「代码行」，而是「任务闭环」**。

---

## 第三纪元的三个结构性特征

### 1. 从同步循环到异步长时任务

第二纪元的核心约束是同步性——Agent 在本地机器上运行，与开发者争夺计算资源，开发者必须在每个步骤介入才能控制方向。这意味着实际可并行的 Agent 数量极为有限。

第三纪元的解法是**云端虚拟机**：
- 每个 Cloud Agent 运行在独立 VM 上
- 开发者可以同时 hand off 多个任务，然后去处理其他事
- Agent 自主迭代、测试，直到输出可评审的结果

> "Each runs on its own virtual machine, allowing a developer to hand off a task and move on to something else."

这对开发效率的影响是根本性的：**人类的时间片从「连续监控」变为「间歇性评审」**。当你可以同时跑 5 个 Agent 跑 2 小时而不需要盯着，开发者实际上获得了并行时间扩展。

### 2. Artifact 交付模式替代 Diff 评审模式

同步 Agent 交付的是 Diff——一行行的代码变更，需要开发者自己 mental model 构建整体效果。Cloud Agent 的异步长时任务交付的是 **Artifact**：

- 运行日志
- 视频录屏（Agent 实际操作过程的回放）
- 实时预览（前端产物直接可见）

> "Artifacts and previews give you enough context to evaluate output without reconstructing each session from scratch."

这是一个交付模型的根本切换。Diff 要求开发者重建上下文；Artifact 提供了直观的评估起点。Cursor 的判断是：**当开发者不需要重建上下文，他们的时间就可以用来定义更复杂的问题**。

### 3. 开发者行为的三段式转变

Cursor 内部数据显示，采用第三纪元工作方式的开发者呈现一致的行为模式：

1. **Agent 写出几乎 100% 的代码**
2. **开发者的时间花在：拆解问题 → 评审 Artifact → 给出反馈**
3. **同时启动多个 Agent，而非手把手盯完一个再盯下一个**

> "They spin up multiple agents simultaneously instead of handholding one to completion."

这个行为模式意味着：开发者的核心能力从「写代码」变成「定义问题 + 评估结果」。这不只是效率工具的升级，而是**开发者角色的重新定义**。

---

## 云端 Agent 的技术架构：Fleet 级编排

Cursor 明确提出「Factory」隐喻——不再是单 Agent 辅助单开发者，而是 **Agent Fleet 编排**：

- 多个专业化 Agent 同时工作
- 每个 Agent 配备独立工具集和上下文
- 人类通过「定义问题 + 设置评审标准」来管理 Fleet

这与 Anthropic 在 Managed Agents 中提出的 **Brain/Hands Decoupling**（大脑与执行解耦）形成底层呼应：Fleet 编排本质上是一个分布式 Harness 系统，人只介入在高层的 Review 和 Steering 环节。

Fleet 级编排的核心工程挑战：
- **资源调度**：多 VM 级别的并行启动和管理
- **上下文一致性**：多个 Agent 之间的 shared context 如何维护
- **结果聚合**：多个 Agent 的 Artifact 如何统一评审
- **环境一致性**：Flaky test 在单开发者场景只是小麻烦，在 Fleet 场景会成为阻断性问题

---

## 第三纪元的工程成熟度缺口

Cursor 清醒地指出了当前的核心挑战：

> "At industrial scale, a flaky test or broken environment that a single developer can work around turns into a failure that interrupts every agent run."

这揭示了一个重要的工程不对称：**单 Agent 调试通过的能力，不等于 Fleet 级稳定运行的能力**。

具体来说，第三纪元工作方式的工程成熟度缺口包括：

| 维度 | 第二纪元（同步 Agent） | 第三纪元（Cloud Agent Fleet） |
|------|---------------------|------------------------------|
| 环境问题容忍度 | 高（开发者可随时接管修复）| 低（环境问题会阻断整个 Fleet run）|
| 测试稳定性要求 | 中（单线程可逐步验证）| 高（并行 Agent 需要可重复的 baseline）|
| 上下文管理 | 简单（单 Agent 单 session）| 复杂（多 Agent 跨天/跨 session）|
| 结果评审粒度 | 细（行级别 Diff）| 粗（Artifact 级别评估）|

这意味着：**第三纪元的工程挑战不是让 Agent 跑得更快，而是让环境更稳定、让 Agent 的输出更容易评估**。

---

## Skills：让 Agent 自主工作的装备系统

Cursor 在这篇文章中提出了一个关键概念：「 equipping agents with the tools to work independently」。这里的关键词是 **equipping**——就像给人类工匠配备专业工具，给 Agent 装备专业 Skills 是第三纪元的核心基础设施。

Anthropic 官方 Skills 仓库（`anthropics/skills`）提供了这个问题的参考实现：

- **SKILL.md 极简格式**：统一的 Skill 定义格式，让任何兼容 Agent（Claude Code / Codex / Cursor 等）都能加载和使用
- **生产级文档能力**：`skills/docx`、`skills/pdf`、`skills/pptx`、`skills/xlsx` 提供专业文档生成的完整实现，这些不是 demo，是真正在生产使用的技能
- **Plugin 市场集成**：Claude Code 可以通过 `/plugin marketplace add anthropics/skills` 直接安装整套技能库

> "Skills teach Claude how to complete specific tasks in a repeatable way, whether that's creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks."

这个模式的核心价值是**可复用性**——当一个 Skill 被定义并测试通过后，所有接入的 Agent 都可以使用，消除了每个项目重复配置相同能力的需求。

NVIDIA AI Blueprints 的 Video Search and Summarization 项目遵循同样的 **agentskills.io 标准**，提供了视频理解、搜索、告警等技能封装，与 Anthropic Skills 形成跨厂商的技能互操作示范。

---

## 笔者的判断

**第三纪元不是技术突破，而是一种工作方式的制度化**。

第二纪元让我们知道「让 Agent 自主工作」是可能的；第三纪元告诉我们「让 Agent Fleet 自主工作」需要的是完全不同的工程基础设施——环境稳定性、Artifact 驱动的评审、Skills 化的能力复用。

笔者认为，Cursor 在这篇文章中透露的判断（一年后绝大多数开发工作将由 Agent 完成）与工程现实之间存在张力。**真正的瓶颈不是 Agent 的能力，而是环境稳定性、可评估性和跨 Agent 上下文共享**。这些问题解决之前，Agent 产出的代码仍然需要大量人工 review 和修复。

但方向是明确的：**第三纪元已经发生，正在进行。问题是我们的工程基础设施能否跟上这个转变的速度**。

---

## 原文引用

> "A third era of AI software development is emerging as autonomous cloud agents take on larger tasks independently, over longer timescales, with less human direction."

> "Cursor is no longer primarily about writing code. It is about helping developers build the factory that creates their software."

> "We think yesterday's launch of Cursor cloud agents is an initial but important step in that direction."

---

*相关主题：Cloud Agent Harness（第 5/6 纪元演进路径）、Agent Skills 标准化（工具层抽象）*