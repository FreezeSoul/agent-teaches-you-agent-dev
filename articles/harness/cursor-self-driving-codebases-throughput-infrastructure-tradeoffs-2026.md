# Cursor「走向自动驾驶代码库」：吞吐量工程与基础设施权衡

> **核心主张**：Cursor 的千量级 Agent 实验揭示了一个反直觉的发现——追求 100% 提交正确性反而导致吞吐量坍缩，放弃全局一致性的局部冲突反而提升了系统整体效率。同时，磁盘而非 CPU 成为多 Agent 并行的真正瓶颈，暴露了开发工具链在并发场景下的根本性局限。

## 引言

2026 年 5 月 10 日，Cursor 发布了「[Towards Self-Driving Codebases](https://cursor.com/blog/self-driving-codebases)」工程报告，揭示了多 Agent 协作从「自协调」到「角色分层」的演进路径。本篇聚焦该报告的后半部分——**吞吐量工程与基础设施权衡**，这是前文「架构设计」段落未曾覆盖的内容。

本文的核心论点是：**千量级 Agent 并行系统与单用户开发工具有本质区别，传统的并发控制机制（锁、全局同步）反而成为瓶颈**。Cursor 的解决方案不是更复杂的协调机制，而是**主动接受局部错误和短暂混乱，让系统自然收敛**。

---

## 吞吐量数据：1000 Commits/Hour 的工程现实

Cursor 的系统峰值数据：

> "The system peaked at ~1,000 commits per hour across 10M tool calls over a period of one week. Once the system started, it didn't require any intervention from us."

**1000 commits/hour** 意味着平均每 3.6 秒完成一次提交。在这个规模下，Agent 之间几乎不需要协调——系统自动运转，一周内无人干预。

这个数字的工程背景值得注意：
- 运行在**单台大型 Linux VM**（而非分布式集群）
- 峰值时同时运行**数百个 Agent**（不是几千个同时活跃）
- 10M tool calls 是累积量，平均每 Agent 每小时约 1,000 次调用

### 为什么选择单台大机器而非分布式架构

Cursor 的选择基于一个关键洞察：

> "Rather than dealing with the complexity of distributed systems, we instead ran the harness on a single large Linux VM (Virtual Machine) with lots of resources."

这个决策的理由是：大多数运行时峰值在数百个 Agent，这些 Agent 会迅速耗尽单机资源，所以跨机器分布式反而增加不必要的复杂度。单台大机器让观测和状态共享更容易——这也是为什么「observability」被 Cursor 反复强调。

---

## 核心权衡一：提交正确性 vs 吞吐量

这是本文最反直觉的发现。

### 100% 正确性的代价

Cursor 最初要求每个提交都必须完全正确（100% correctness before every single commit）。结果：

> "Even a single small error, like an API change or typo, would cause the whole system to grind to a halt. Workers would go outside their scope and start fixing irrelevant things. Many agents would pile on and trample each other trying to fix the same issue."

一个微小的错误（比如一个 API 变更或拼写错误）就会导致整个系统停顿。更糟的是，多个 Agent 会同时尝试修复同一个问题，互相践踏，演变成「修复旋涡」而不是真正的工作。

这个现象的根源是：**在高度并行的 Agent 系统中，串行化正确性检查会创建全局瓶颈，而局部错误修复会触发级联的重复劳动**。

### 接受错误率的工程逻辑

Cursor 的解决方案是**放弃 100% 正确性，接受稳定的低错误率**：

> "This may indicate that the ideal efficient system accepts some error rate, but a final 'green' branch is needed where an agent regularly takes snapshots and does a quick fixup pass before release."

这揭示了一个重要的工程哲学：**完美是高效的敌人**。在千量级 Agent 并行系统中，追求每个提交的完美正确性反而导致极低的吞吐量。允许一定比例的错误（但保持稳定和可管理），让系统能够持续前进而不崩溃。

最终需要一个独立的「green branch」机制——定期有 Agent 做快照和修复清理，确保发布质量而不影响平时的吞吐量。

**笔者认为**：这个权衡对 Harness 设计有深远影响。对于长时间运行的 Agent 系统，**「最终一致性」比「即时一致性」更重要**。这与分布式数据库的 CAP 理论有有趣的类比——在高并发场景下，可用性（throughput）和最终一致性比强一致性更有价值。

---

## 核心权衡二：同步开销与局部冲突

### 显式同步机制的失效

Cursor 最初尝试了多种显式同步机制：

- **乐观并发控制**（lockless optimistic concurrency）：减少开销但无法消除混乱
- **Agent 显式等待机制**：Agent 几乎不使用
- **共享状态文件 + 锁**：锁竞争严重，20 个 Agent 降速到 1-3 个的吞吐量

Cursor 的结论：

> "We tried giving agents a tool to explicitly wait on another agent's work, but they rarely used it."

Agent 没有使用显式等待机制，说明**隐式的协作比显式的协调更难违反**——如果系统没有强制 Agent 等待，Agent 会继续工作（即使这意味着踩踏）。

### 接受局部湍流，自然收敛

Cursor 的应对策略是**不消除冲突，而是让系统接受冲突后的短期混乱**：

> "Sometimes multiple agents touch the same file or refactor the same code. Instead of trying to stamp these out completely or overengineer a solution, we accept some moments of turbulence and let the system naturally converge and settle over a short period of time."

这背后有几个原因：

| 因素 | 说明 |
|------|------|
| **Token 开销** | 冲突会消耗额外的 tokens，但比过度工程的同步机制更省 |
| **Agent 能力差异** | 模型能处理的协调复杂度有限，复杂的锁机制反而导致死锁或饥饿 |
| **全局简单性** | 接受局部湍流让系统整体更简单、更可预测、更容易对齐模型 |

Cursor 的判断是：**局部冲突的代价比全局同步机制的复杂度更可接受**。这是一个重要的工程权衡——不是追求理论上的最优，而是选择实际可行的方案。

---

## 基础设施教训：磁盘是新的瓶颈

### 从 RAM 到磁盘的转移

Cursor 最初的性能优化聚焦于限制 Agent 的 RAM 使用。但很快发现：

> "After limiting RAM usage of agents, the disk became the hotspot. Especially with a monolith project, hundreds of agents compiling simultaneously would result in many GB/s reads and writes of build artifacts."

当 RAM 不再是瓶颈后，磁盘成为新的热点。尤其是 monolith 项目，数百个 Agent 同时编译会产生 GB/s 级别的读写。

这个现象揭示了一个重要的工程现实：

> "This had a significant impact on the overall throughput of the harness, which was an interesting lesson: the project structure, architectural decisions, and developer experience can affect token and commit throughput, simply because working with the codebase (e.g. compilation) dominates time, instead of ideally thinking and coding."

**项目结构、架构决策和开发者体验会影响 token 和提交吞吐量**，因为实际工作中「与代码库交互（如编译）」占据了大部分时间，而不是理想的「思考和编码」。

这对 Harness 设计有直接启示：**如果目标是通过增加 Agent 数量来提升吞吐量，需要考虑代码库结构的并发友好性**。

### 工具链的并发局限

Cursor 还发现了一些与开发工具相关的问题：

> "Many tools like Git and Cargo use shared locks, largely as a simple concurrency control mechanism. Could bringing well-established mechanisms from concurrent systems like databases make these work just as well in multi-agent systems?"

Git 和 Cargo 等工具使用共享锁作为简单的并发控制机制。但在多 Agent 场景下，这种机制导致了不必要的串行化。

Cursor 提出的问题是：**能否从并发数据库系统引入成熟的机制来改进这些工具**？

这是一个值得研究的方向——如果能让 Git 和 Cargo 等工具更好地支持高并发，多 Agent 系统的吞吐量会有显著提升。

### 复制与去重的机会

> "All agents have their own copy of the repo, but most files and artifacts are identical; could adding simple copy-on-write and deduplication gain efficiency?"

每个 Agent 都有自己独立的代码库副本，但大多数文件和产物是相同的。Cursor 提出了一个潜在的优化方向：**引入 copy-on-write 和去重机制**。

这个方向如果实现，可以显著减少磁盘 I/O 和存储开销。

**笔者认为**：Cursor 的基础设施教训揭示了多 Agent 系统与传统单用户开发工具之间的根本矛盾。Git 和 Cargo 等工具假设的是「少数用户、少量并发」，但多 Agent 系统是「大量 Agent、高度并发」。这种不匹配会显著限制系统吞吐量。

---

## 自协调到结构化角色的演进（续）

前文已覆盖 Cursor 从 Self-Coordination 到 Adding Structure 的演进，这里补充后续的关键发现。

### Continuous Executor 的病理行为

Cursor 尝试了 Continuous Executor 架构（Executor 同时负责规划和任务生成），但很快发现了病理行为：

> "The final design incorporates all of our learnings... The executor could now also plan how to deliver the goal in addition to spawning tasks. Since it was the sole agent, it didn't need to write a plan anywhere, stick to one static unchanging plan, or rigidly wait for all workers."

最终设计的关键是**分离 Planner 不再执行，执行者不再规划**：

> "A root planner owns the entire scope of the user's instructions. It's responsible for understanding the current state and delivering specific, targeted tasks that would progress toward the goal. It does no coding itself. It's not aware of whether its tasks are being picked up or by whom."

这个设计的核心洞察是：**规划者不知道任务被谁执行，执行者不知道整体目标**。这种分离避免了规划者被执行细节淹没，也避免了执行者被全局目标迷惑。

### Hand-off 机制的信息传递

Cursor 引入了一个关键的信息传递机制——**handoff 文档**：

> "Workers pick up tasks and are solely responsible for driving them to completion. They're unaware of the larger system. They don't communicate with any other planners or workers. They work on their own copy of the repo, and when done, they write up a single handoff that the system submits to the planner that requested the task."

Worker 完成任务后写一个 handoff 文档，提交给请求任务的 Planner。这个文档不仅包含「做了什么」，还包含：

- Important notes（重要笔记）
- Concerns（顾虑）
- Deviations（偏离）
- Findings（发现）
- Thoughts（思考）
- Feedback（反馈）

这让系统保持动态运动：**即使 Planner 完成了当前任务，它继续接收更新、拉动最新代码、继续规划和决策**。

**这个机制与 Autoinstall 的双代理两阶段设计有有趣的呼应**：Autoinstall 的 Goal-setting Agent 定义目标，Composer Agent 执行；Self-Driving Codebases 的 Planner 分发任务，Worker 执行并返回 handoff。两者都体现了「分离目标定义与执行实现」的原则。

---

## 与 Parameter Golf 的关联：AI Agent 的竞赛级应用

Cursor 的 Self-Driving Codebases 实验与 OpenAI Parameter Golf 挑战赛形成了有趣的对照。

OpenAI 的 Parameter Golf 参与者也大量使用了 AI coding agents：

> "The vast majority of submitters mentioned using agents as part of their work. That lowered the barrier to entry."

两个案例都显示：**AI coding agents 在大规模协作任务中展现出显著价值**。在 Parameter Golf 中，agents 帮助降低实验成本；在 Self-Driving Codebases 中，agents 让千量级并行工作成为可能。

但两个案例也揭示了相同的基础设施挑战：

| 维度 | Parameter Golf | Self-Driving Codebases |
|------|---------------|------------------------|
| **规模** | ~2,000 提交者 | ~1,000 Agent 并行 |
| **挑战** | 提交审核、归因、评分 | 锁竞争、错误级联、磁盘瓶颈 |
| **解决方案** | Codex-based triage bot | 接受错误率 + 自然收敛 |

两个项目都表明：**当 Agent 规模扩展到百量级或千量级时，传统的协调机制（人工审核、集中式同步）会成为瓶颈**。需要新的范式来处理这种规模下的协作。

---

## 工程启示：Harness 设计的原则

Cursor 的实验揭示了几个重要的 Harness 设计原则：

### 1. 分离目标定义与执行实现

无论是 Autoinstall 的 Goal-setting/Composer 双代理，还是 Self-Driving Codebases 的 Planner/Worker 分层，核心原则相同：**定义成功的人不应该执行成功**。

这让目标定义者专注于「什么是对的」，而不被「如何实现」分散注意力。

### 2. 接受错误率而非追求完美

> "The ideal efficient system accepts some error rate."

100% 正确性在高并发场景下是奢望。接受稳定的低错误率，让系统持续前进，比追求每个提交的完美更实际。

### 3. 本地化决策而非全局同步

> "Instead of trying to stamp these out completely or overengineer a solution, we accept some moments of turbulence and let the system naturally converge."

全局同步的开销往往大于本地冲突的代价。让系统接受短期混乱并自然收敛，比强制全局一致性更高效。

### 4. 基础设施是瓶颈，不是副作用

> "The project structure, architectural decisions, and developer experience can affect token and commit throughput."

在多 Agent 系统中，代码库结构、编译系统、工具链性能会影响整体吞吐量。这些不是「可以以后优化」的问题，而是**影响 Agent 并行效率的根本因素**。

---

## 结论：吞吐量即基础设施

Cursor 的千量级 Agent 实验揭示了一个核心发现：**当 Agent 规模扩展到数百甚至数千时，系统瓶颈从「Agent 协作」转移到「基础设施」**。

关键数据：
- 峰值 1,000 commits/hour，10M tool calls，一周无人干预
- 100% 正确性要求导致吞吐量坍缩，放弃后系统效率大幅提升
- 磁盘而非 CPU 成为多 Agent 并行的真正瓶颈
- Git/Cargo 等工具的共享锁限制了高并发场景下的吞吐量

这些发现对 Harness 设计有直接指导意义：
- **接受错误率**：不要追求每个提交的完美，设计定期修复机制
- **本地化冲突**：不要强制全局同步，让系统自然收敛
- **优化基础设施**：代码库结构、编译性能、工具链并发度是关键
- **分离规划与执行**：Planner 不执行，Worker 不规划，各司其职

Cursor 的实验证明了**千量级 Agent 并行是可行的**，但需要重新思考传统的软件工程假设。工具链、并发控制、正确性标准——这些在单用户场景下理所当然的设计，在多 Agent 场景下需要根本性的重新审视。

---

**关联阅读**：
- [Cursor Autoinstall：AI 模型训练的环境自举范式](../practices/cursor-bootstrapping-composer-autoinstall-2026.md)（双代理两阶段架构与本文的 Planner/Worker 分层形成呼应）
- [OpenAI Parameter Golf：AI Coding Agents 竞赛洞察](../fundamentals/openai-parameter-golf-ai-coding-agents-competition-insights-2026.md)（千量级 Agent 协作的竞赛视角）
- [Cursor 第三代 AI 软件开发：云端并行与人类角色转变](../ai-coding/cursor-third-era-cloud-agents-human-role-paradigm-shift-2026.md)（Human-in-the-loop 与自主性的平衡）