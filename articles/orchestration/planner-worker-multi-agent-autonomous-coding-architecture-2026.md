# Planner/Worker 架构：长时自主编码的多 Agent 协作模式

**发布于**：2026-05-01 | **演进阶段**：Stage 7 · Orchestration | **分类**：orchestration/

## 开篇

> **核心问题**：当一个代码库需要数百个 Agent 并发工作数周时，如何让它们不打架、不重复、不停滞？Cursor 用 100 万行代码和 1 万次提交做了回答——答案是**放弃平等协作，转向角色分层**。
>
> **核心结论**：Planner/Worker 分层架构解决了 flat 多 Agent 协作的三个根本性失败：锁竞争导致的吞吐量塌陷、缺乏全局视野导致的 risk-aversion、以及单点瓶颈导致的脆弱性。这个模式已经在 Cursor 自己的代码库上验证：3 周完成 26.6 万行 +/19.3 万行 - 的 Solid→React 迁移。

---

## 1. 为什么 flat 协作必然失败

### 1.1 动态协调的锁瓶颈

Cursor 团队一开始选择了最直觉的方案：**动态协调**，即所有 Agent 通过一个共享文件来协调——每个人先查看别人在做什么，声明自己要做的任务，然后更新状态。

他们用锁机制来防止两个人抢同一个任务。这个方案有四个相互关联的失败模式：

> "Agents would hold locks for too long, or forget to release them entirely. Even when locking worked correctly, it became a bottleneck. Twenty agents would slow down to the effective throughput of two or three, with most time spent waiting."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

锁持有时间过长或遗漏释放，直接把并发退化为串行。20 个 Agent 变成了 2-3 个的吞吐量。

### 1.2 锁失败后的乐观并发控制

他们尝试用乐观并发控制替代锁：读取状态自由，但写入时如果状态已被他人修改则失败。这比锁更简单和健壮，但仍然存在更深层的问题。

### 1.3 Flat 结构的根本缺陷：无层次导致 Risk-Aversion

即使解决了并发正确性问题，flat 结构还有一个致命的 Emergent 行为问题：

> "With no hierarchy, agents became risk-averse. They avoided difficult tasks and made small, safe changes instead. No agent took responsibility for hard problems or end-to-end implementation. This led to work churning for long periods of time without progress."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

没有层次结构，Agent 会自发地变成**风险厌恶型**——优先选择安全的小改动，回避困难问题。没有人对 end-to-end 实现负责。结果是大量工作被反复 churn，但没有实质性进展。

### 1.4 与 Anthropic "Pet vs Cattle" 的共鸣

Anthropic 在 Managed Agents 中也遇到了类似问题。他们把 session、harness、sandbox 全耦合在一个容器里，容器变成了那只"pet"——不能丢失，不能重启，需要护士式看护。

Cursor 的 flat Agent 结构本质上是另一个维度的"pet"：每个 Agent 都承载全局状态，任何一个失败都会影响整体。解决方案同样是**去耦合**：把规划职责和执行职责分开，让它们可以独立失败、独立重启。

---

## 2. Planner/Worker 架构的核心设计

### 2.1 角色分离

Cursor 设计的 Pipeline 将职责严格分离：

| 角色 | 职责 | 行为特征 |
|------|------|---------|
| **Planner** | 持续探索代码库，创建任务；可生成子 Planner 实现递归规划 | 探索性，主动发现任务 |
| **Worker** | 专注于完成分配的任务，不与其他 Worker 协调 | 执行性，被动接受任务 |
| **Judge Agent** | 在每个周期结束时判断是否继续 | 元控制，决定循环终止 |

> "Planners continuously explore the codebase and create tasks. They can spawn sub-planners for specific areas, making planning itself parallel and recursive. Workers pick up tasks and focus entirely on completing them. They don't coordinate with other workers or worry about the big picture."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

Planner 可以递归生成子 Planner，这意味着规划本身也是并行的——不同区域的代码库可以由不同的子 Planner 独立探索。

### 2.2 为什么这个结构有效

**第一**：Worker 不需要全局视野，只需要局部完成能力。这解决了 flat 结构中的 risk-aversion 问题——困难任务由 Planner 分配，Worker 只管执行。

**第二**：Planner 和 Worker 可以独立失败和重启。一个 Worker 卡住，不影响其他 Worker；一个 Planner 崩溃，其他子 Planner 继续工作。

**第三**：Judge Agent 提供了一个架构化的终止判断，避免了"Agent 不知道什么时候该停"的问题。

### 2.3 Anthropic 的任务锁机制：另一种分层思路

Anthropic 的 Nicholas Carlini 在用 16 个并行 Claude 实例构建 C 编译器时，也采用了分层策略，但实现不同：

> "A new bare git repo is created, and for each agent, a Docker container is spun up with the repo mounted to /upstream. Each agent clones a local copy to /workspace, and when it's done, pushes from its own local container to upstream. To prevent two agents from trying to solve the same problem at the same time, the harness uses a simple synchronization algorithm: Claude takes a 'lock' on a task by writing a text file to current_tasks/... If two agents try to claim the same task, git's synchronization forces the second agent to pick a different one."
> — [Anthropic Engineering: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)

Anthropic 的方案是通过 git 的 merge conflict 机制来处理锁冲突——如果两个 Agent 同时修改同一个任务，后修改的那个会因 conflict 被迫重试。这是一个**基于文件系统语义的乐观锁**，而不是主动的协调协议。

两种方案的本质区别：

| 维度 | Cursor Planner/Worker | Anthropic 任务锁 |
|------|----------------------|-----------------|
| 协调方式 | 集中式规划 + 分散执行 | 分散锁获取 + git merge 强制串行 |
| 任务分配 | Planner 主动分配 | Agent 自行竞争 |
| 全局视野 | Planner 持有 | 无（每个 Agent 独立决策）|
| 失败恢复 | 层次化（Judge 决定）| 每个 Agent 独立重试 |

---

## 3. 实证结果：从浏览器到 React 迁移

### 3.1 极端规模验证

Cursor 用这个架构做了三个极端规模实验：

**构建一个浏览器（1 周，100 万行代码，1000 个文件）**：

> "To test this system, we pointed it at an ambitious goal: building a web browser from scratch. The agents ran for close to a week, writing over 1 million lines of code across 1,000 files."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

**Solid→React 迁移（3 周，+26.6 万/-19.3 万行变更）**：

> "Another experiment was doing an in-place migration of Solid to React in the Cursor codebase. It took over three weeks with +266K/-193K edits. It still needs careful review, but was passing our CI and early checks."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

**视频渲染优化（25x 加速 + 运动模糊特效）**：

> "A long-running agent made video rendering 25x faster with an efficient Rust version. It also added support to zoom and pan smoothly with natural spring transitions and motion blurs, following the cursor."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

### 3.2 模型选择：GPT-5.2 显著优于 Opus 4.5

> "Model choice matters for extremely long-running tasks. We found that GPT-5.2 models are much better at extended autonomous work: following instructions, keeping focus, avoiding drift, and implementing things precisely and completely. Opus 4.5 tends to stop earlier and take shortcuts when convenient, yielding back control quickly."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

这是一个重要的工程结论：**不是越贵的模型越适合长时自主任务**。GPT-5.2 的"follow through"特性（持续执行而不提前交还控制权）对于 multi-week 任务至关重要。

更重要的是，Cursor 发现不同模型适合不同角色：

> "We also found that different models excel at different roles. GPT-5.2 is a better planner than GPT-5.1-Codex, even though the latter is trained specifically for coding."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

这意味着 **Planner/Worker 架构天然适合模型异构部署**——Planner 用更贵的强推理模型，Worker 用更便宜的执行模型。

### 3.3 Anthropic 的专项 Agent 角色

Anthropic Carlini 的实验中也有类似的角色分化意识：

> "LLM-written code frequently re-implements existing functionality, so I tasked one agent with coalescing any duplicate code it found. I put another in charge of improving the performance of the compiler itself, and a third I made responsible for outputting efficient compiled code. I asked another agent to critique the design of the project from the perspective of a Rust developer."
> — [Anthropic Engineering: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)

相比 Cursor 的 Planner/Worker 统一框架，Anthropic 的方案更偏向**按能力分配专责 Agent**，是一种更细粒度的角色分化。

---

## 4. 最反直觉的结论：简化才是关键

Cursor 团队在实验过程中发现：

> "Many of our improvements came from removing complexity rather than adding it. We initially built an integrator role for quality control and conflict resolution, but found it created more bottlenecks than it solved. Workers were already capable of handling conflicts themselves."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

他们最初设计了一个 **Integrator** 角色来做质量控制和冲突解决，结果反而制造了更多瓶颈。移除这个角色之后，系统反而更顺畅了。

> "The right amount of structure is somewhere in the middle. Too little structure and agents conflict, duplicate work, and drift. Too much structure creates fragility."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

这个结论对 Harness 设计者有重要启示：**架构的复杂度不是线性收益的**。Planner/Worker 已经足够解决 flat 结构的三个根本问题，再加 Integrator 就过犹不及。

---

## 5. Prompt Engineering 的决定性作用

Cursor 团队最后指出了一个让很多人意外的结论：

> "A surprising amount of the system's behavior comes down to how we prompt the agents. Getting them to coordinate well, avoid pathological behaviors, and maintain focus over long periods required extensive experimentation. The harness and models matter, but the prompts matter more."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

在数百个并发 Agent 运行数周的场景下，**Prompt 是最高杠杆的优化点**。这与大多数 Agent 开发者"先选框架、再调模型"的直觉相反。

具体的 Prompt 优化方向包括：
- 如何让 Agent 在长时间运行中保持目标不漂移（drift）
- 如何让 Worker 避免 pathological 行为（如过度持有资源）
- 如何让 Planner 保持探索而不陷入无限规划

---

## 6. 尚未解决的工程问题

Cursor 坦诚列出了当前系统的局限：

> "Multi-agent coordination remains a hard problem. Our current system works, but we're nowhere near optimal. Planners should wake up when their tasks complete to plan the next step. Agents occasionally run for far too long. We still need periodic fresh starts to combat drift and tunnel vision."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

三个未解决问题：
1. **Planner 唤醒机制**：Planner 应该在任务完成后主动唤醒做下一步规划，而不是被动等待
2. **Agent 超时控制**：部分 Agent 运行时间远超合理范围，缺乏有效的实时终止机制
3. **周期性 Fresh Start**：仍需要定期重启来对抗 drift 和 tunnel vision

这些问题指向了 Planner/Worker 架构的下一阶段演进方向。

---

## 7. 与 Harness Engineering 的关联

Planner/Worker 架构本质上是一个 **Harness 设计模式**，而不是某个框架的特性。它的核心价值在于：

1. **把"协调问题"转化为"角色设计问题"**：不是优化协调算法，而是减少需要协调的 Agent 数量
2. **把"全局状态"转化为"局部状态"**：Worker 只关心自己被分配的任务，不关心全局
3. **把"动态发现"转化为"层次化分配"**：Planner 负责全局探索，Worker 负责局部执行

从 Anthropic 的 Brain/Hand/Session 解耦视角看，Planner 对应 Brain（推理和规划），Worker 对应 Hand（执行），Judge Agent 则是一个元控制层。这些角色之间的接口设计才是关键。

---

## 总结

Planner/Worker 架构证明了：**多 Agent 并发不是协调算法的竞争，而是角色设计的竞争**。

Flat 结构的三个根本性失败——锁竞争导致的吞吐量塌陷、无层次导致的 risk-aversion、以及单点导致的脆弱性——都可以通过角色分层来解决。但层级设计也有上界：Integrator 这样的过度设计反而会重新引入瓶颈。

Cursor 的 100 万行代码浏览器、3 周 Solid→React 迁移、25x 视频渲染加速，都证明了这套架构的生产可行性。而"Prompt 才是最高杠杆"这个结论，对于所有 Agent 开发者来说，是一个值得记住的优先级提醒。

---

**相关工程实践**：
- 如果你正在设计多 Agent 协作系统，优先考虑角色分层，而不是协调算法的优化
- 模型选择应根据角色定制：Planner 用强推理模型，Worker 用成本效益更高的模型
- 简化是关键：先移除不必要的协调机制，再考虑增加新角色
- Prompt 的投入回报率在长时任务中远高于框架或模型的调整
