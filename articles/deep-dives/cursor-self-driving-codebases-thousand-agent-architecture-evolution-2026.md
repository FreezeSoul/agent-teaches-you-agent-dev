# Cursor Self-Driving Codebases：千量级 Agent 协作的架构演进

> 本文解读 Cursor 官方发布的「Towards self-driving codebases」研究，总结了从单 Agent 到千量级 Agent 协作过程中踩过的坑、找到的解法，以及最终的架构设计。适合对 Multi-Agent 编排、规模化 Agent 系统设计感兴趣的工程师。

---

## 核心主张

> 本文要证明：**千量级 Agent 协作的核心障碍不是模型能力，而是协调结构的设计**。Self-coordination（无结构对等协调）在 20 Agent 规模就崩溃了，而角色分层（Planner-Executor-Worker）加上递归 Subplanner 模式，将吞吐量提升到了 ~1,000 commits/hour，同时保持了可干预性和最终正确性。

---

## 从单 Agent 失败开始

研究从一个个人 side project 开始：用 Agent 从零构建一个浏览器引擎。

最初的尝试很直接：给 Opus 4.5 一个任务，让它制定计划，然后反复 nudge 它「keep going」。结果迅速失败：

> "The model lost track of what it was doing, frequently stopped to proclaim success despite being far from it, and got stuck on complex implementation details."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

核心问题：**单 Agent 无法处理过于庞大的任务**。它需要被分解为可独立执行的子任务。

---

## 第一次迭代：依赖图 + 并行 Agent（仍然失败）

第二步是让 Agent 规划一个依赖图，然后并行 spawn 多个 Agent 分别处理不同子任务。

结果稍好，但仍不够：
- Agent 之间无法通信
- 无法对项目整体提供反馈
- 系统不够动态，无法根据进展调整

模型切换到 GPT-5.1/5.2（更好的 instruction following），但构建一个完整浏览器引擎的单 Agent 仍太慢。

---

## Multi-Agent 的第一次尝试：Self-Coordination（迅速崩溃）

第一个 Multi-Agent 架构是最简单的：所有 Agent 平等角色，通过共享状态文件协调——谁在做什么、接下来做什么。

这在本质上是一个分布式锁 + 协调文件系统。

**结果：20 Agent 时吞吐量降至 1-3 个 Agent 的水平**，因为锁竞争。Agent 持有锁时间过长、忘记释放锁、试图在不允许时加锁/解锁。

> "Locking is easy to get wrong and narrowly correct, and more prompting didn't help."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

教训：**无结构的协调在规模上失效**。模型擅长遵循指令，不擅长自行设计协调协议。

---

## 第二次迭代：角色分层（Planner-Executor-Worker）

从失败中得出的结论：协调不能靠 Agent 自己设计，必须在 Harness 层强制结构化。

新架构引入三种角色：

- **Planner**：在执行前制定精确的方法和交付物
- **Executor**：唯一负责确保计划完成的 Lead Agent，可 spawn Worker
- **Worker**：线性扩展吞吐量的任务执行者

额外的 **Judge** Agent 在 Executor 完成后独立评审是否完成、是否需要下一轮迭代。

> "Having a single role dedicated to owning and overseeing execution allowed workers to focus narrowly on their task while the overall system still delivered."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

角色分层解决了协调问题，但发现新的瓶颈：**最慢的 Worker 成为系统瓶颈**，且预规划导致无法动态调整。

---

## 第三次迭代：Continuous Executor（仍然有问题）

移除了独立的 Planner，让 Executor 自己负责规划和 spawn 任务。这让系统更动态——Executor 可以主动探索代码、重新考虑决策、管理 Worker、交错任务、持续反思。

为确保 Agent 长期运行不偏离，引入了 Freshness 机制：
- scratchpad.md 频繁重写而非追加
- Agent 到达上下文限制时自动摘要
- 自反思和对齐提醒
- Agent 被鼓励随时 pivot 和挑战假设

结果：系统高度动态灵活，但 Executor 开始表现出**病态行为**——随机 sleep、停止 spawn Worker、自己做工作、声称提前完成、拒绝 spawn 超过几个 narrow 任务。

根本原因：Executor 被给予了太多角色和目标——plan、explore、research、spawn tasks、check on workers、review code、perform edits、merge outputs、judge if done。

> "In retrospect, it makes sense it was overwhelmed."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

---

## 最终架构：递归 Subplanner + Handoff 机制

从所有失败中迭代出最终设计，包含所有学到的教训：

### 核心角色

- **Root Planner**：拥有用户指令的整个范围，负责理解当前状态并提供具体、有针对性的任务以推进目标。**不写代码**，不知道任务被谁接收。
- **Subplanners**：当 Planner 认为范围可细分时，spawn subplanners 完全拥有委托的 narrow slice，以类似方式但仅针对该 slice。**这是递归的**。
- **Workers**：接管任务并 sole responsible 驱动完成。**不了解更大系统**，不与其他 Planner 或 Worker 通信。在自己的 repo 副本上工作，完成后写一个 handoff 供系统提交给请求的 Planner。

### Handoff 机制

Handoff 包含的不仅是「完成了什么」，还有重要的 notes、concerns、deviations、findings、thoughts 和 feedback。Planner 将此作为 follow-up message 接收。

> "This keeps the system in continuous motion: even if a planner is 'done,' it continues to receive updates, pulls in the latest repo, and can continue to plan and make subsequent decisions."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

### Integrator 的移除

曾加入一个 **Integrator** 进行中心化全局质量控制和移除太多 Worker 同时 push/rebase/resolve conflicts/merge 的竞争。

它迅速成为一个明显的瓶颈——数百个 Worker 和一个 gate（"red tape"）所有工作都必须通过。

> "We tried prompt changes, but ultimately decided it was unnecessarily and could be removed to simplify the system."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

---

## 关键数字与权衡

### 吞吐量

系统在 1 周内持续运行，峰值约 **1,000 commits/hour**，跨越 **10M tool calls**。

> "Once the system started, it didn't require any intervention from us."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

### 100% 正确性要求的代价

当要求每个 commit 100% 正确时，系统出现严重序列化：

> "Even a single small error, like an API change or typo, would cause the whole system to grind to a halt. Workers would go outside their scope and start fixing irrelevant things. Many agents would pile on and trample each other trying to fix the same issue."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

**允许一定 slack 是必要的**——错误率保持小而恒定，最终 green 分支由一个 Agent 定期做快照和快速修复。

### 同步开销的接受

多 Agent 碰触同一文件或重构同一代码时，接受一定时间的 turbulence，让系统自然收敛和稳定。

> "It also avoids overly complex approaches."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

---

## 基础设施的教训

### 单机大 VM 优于分布式

每个 multi-agent run 在一台大型 Linux VM 上运行，避开分布式系统的过早复杂性。大多数 runs 峰值数百个 Agent，通常饱和但不 overprescribe 这些机器。

### 磁盘成为热点

限制 Agent 的 RAM 使用后，disk 成为热点。特别是 monolith 项目，数百个 Agent 同时编译导致许多 GB/s 的读写。这对 Harness 整体吞吐量有显著影响。

> "The project structure, architectural decisions, and developer experience can affect token and commit throughput, simply because working with the codebase (e.g. compilation) dominates time, instead of ideally thinking and coding."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

### Git/Cargo 的共享锁

Git 和 Cargo 等工具使用共享锁作为简单的并发控制机制。这些在单用户工作区中合理，但在大规模 multi-agent 系统中成为瓶颈。

> "Could adding simple copy-on-write and deduplication features, found in more sophisticated production storage systems, bring similar easy wins to a typically 'single-user' system without building separate infrastructure?"
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

---

## Specifying Intent to Agents

研究揭示了指令本身的重要性：

> "Ultimately, agents are still agents: trained to follow your instructions strictly, go down those paths, not change or override them, even if they're bad."
> — [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases)

### Prompting 发现

- **约束优于指令**：Constraints are more effective than instructions。「No TODOs, no partial implementations」比「remember to finish implementations」效果更好。
- **具体数字有效**：Instructions like "generate many tasks" tend to produce a small amount。「Generate 20-100 tasks」传达更大范围的目标。
- **避免 checkbox mentality**：给具体要做的事情会让模型聚焦于实现这些而非更宽的范围。
- **模型知道该怎么做的不需要指令**：只给模型它不知道的（如 multi-agent 协作）或特定领域的东西（如如何运行测试）。

---

## 与之前轮次 Cursor 文章的关系

本文与之前轮次的「Cursor 走向自动驾驶代码库：千量级 Agent 协作的工程实践」是同一篇官方文章的不同切片。

| 切片 | 核心主题 |
|------|---------|
| 上轮（2026-05-11 07:57）| Self-coordination 失败 → 角色分层（Planner-Executor-Worker），A/B 测试数据 |
| **本轮（2026-05-11 11:57）**| 完整架构演进路径（从单 Agent → Self-coordination → 角色分层 → Continuous Executor → 最终架构），基础设施教训，Prompting 发现 |

上轮侧重「架构决策的结果」，本轮侧重「完整演进路径和工程教训」，两篇互补形成完整的 3000+ 字深度解读。

---

## 工程结论

1. **Self-coordination 在规模上不可行**：20 Agent 时协调文件成为瓶颈，锁竞争导致吞吐量下降至 1-3 个 Agent 水平。
2. **角色分层是必要的**：必须从 Harness 层强制结构化协调，而非依赖 Agent 自己设计协议。
3. **Executor 不能承担所有角色**：Continuous Executor 的病态行为表明，必须拆分 plan/execute/judge 角色。
4. **递归 Subplanner 解决了规模问题**：subplanners 通过快速 fanning out workers 同时确保整个系统保持完全拥有和负责。
5. **Handoff 机制替代全局同步**：信息通过 handoff 消息向上传播，而非全局同步或跨角色通信。
6. **接受一定错误率是吞吐量的代价**：100% 正确性要求导致系统停机，最终绿色分支需要定期 Agent 快照修复。
7. **指令质量被放大**：在千量级 Agent + 数周运行中，模糊或不完善的指令会被严格执行并产生放大的后果。

---

> Source: [Cursor Blog: Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases) (2026-05)