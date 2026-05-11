# Cursor「走向自动驾驶代码库」：千量级 Agent 协作的工程实践

> 本文深入解析 Cursor 2026 年 5 月发布的「Towards Self-Driving Codebases」工程报告，揭示多 Agent 协作从「自协调」到「角色分层」的根本性转变，以及数千 Agent 并行工作背后的 Harness 工程挑战。

## 核心论点

**Cursor 的实验揭示了一个关键发现：当 Agent 规模从个位数扩展到千位数时，「让 Agent 自己协调」方案迅速崩溃，原因是锁竞争和任务分配不均导致的吞吐量坍缩。解法是将协调结构从「隐式协商」变为「显式角色分层」——Planner 规划、Executor 负责、Worker 执行，三层各司其职。**

这一发现与之前轮次覆盖的 Anthropic 三 Agent 架构（Generator-Evaluator-Analyzer）和 Cursor 自家的 Planner/Worker 架构形成系统性印证，表明**多 Agent 协作的核心挑战不是「让 Agent 更聪明」，而是「让 Agent 的协作结构更可预测」**。

---

## 背景：从单 Agent 到多 Agent 的必然路径

Cursor 的研究始于一个简单的目标：用 Agent 自主构建一个完整的 Web 浏览器。

> "A browser felt like an interesting benchmark. It was complex enough to reveal limitations with frontier models, and there are many different subsystems that needed to work together."
> — [Cursor Blog: Towards Self-Driving Codebases](https://cursor.com/blog/self-driving-codebases)

单 Agent 尝试很快暴露问题：Opus 4.5 可以写出好代码，但很快失去追踪、频繁宣告成功但远未完成、在复杂实现细节上卡住。核心问题是**任务太重，单 Agent 无法维持上下文的连贯性**。

下一阶段尝试：让 Agent 按依赖图并行工作。但问题依旧：Agent 无法相互通信、无法对整体项目提供反馈。系统需要更动态的协调机制。

---

## 第一阶段失败：自协调（Self-Coordination）

Cursor 的第一个多 Agent 方案是最小干预的：**使用共享状态文件，让 Agent 自己决定谁做什么**。

具体做法：
- 所有 Agent 平等角色
- 共享一个状态文件，记录谁在做什么、谁在等谁的工作
- Agent 可以看到其他 Agent 的工作进度，自己决定加入或等待

```python
# 简化的自协调机制（概念示例）
state = {
    "tasks": {},
    "locks": {},
    "agents": []
}

def claim_task(agent_id, task_id):
    if task_id in state["locks"]:
        return False  # 已被锁定
    state["locks"][task_id] = agent_id
    return True
```

**结果：快速失败。**

问题一：**锁持有时间过长**。Agent 持有锁但忘记释放，或者在非法情况下尝试解锁。锁的语义要求精确，但更多提示词也无济于事。

问题二：**严重的锁竞争**。20 个 Agent 的实际吞吐量降至 1-3 个 Agent 的水平，大量时间花在等待锁上。

> "Locking also caused too much contention. 20 agents would slow to the throughput of 1-3 with most time spent waiting on locks."
> — [Cursor Blog: Towards Self-Driving Codebases](https://cursor.com/blog/self-driving-codebases)

问题三：**缺乏结构导致任务碎片化**。没有单一 Agent 承担完整任务。Agent 们避免冲突和竞争，选择更小、更安全的变更，而非对整体项目负责。

Cursor 还尝试了无锁的乐观并发控制方法，减少了开销但没有消除混乱。给 Agent 提供明确的「等待其他 Agent 工作」的工具，但 Agent 很少使用它。

---

## 第二阶段：角色分层（Adding Structure and Roles）

自协调失败后，Cursor 引入了显式角色：

> "Next, we separated roles to gives the agents ownership and accountability: A planner would first lay out the exact approach and deliverables to make progress toward the user's instructions. This would be handed to an executor, who became the sole lead agent responsible for ensuring the plan was achieved completely. The executor could spawn tasks for workers, which provided linear scaling and task isolation."

### 三层角色架构

| 角色 | 职责 | 关键特征 |
|------|------|---------|
| **Planner** | 规划任务分解和交付物 | 维护全局视图，理解任务间的依赖关系 |
| **Executor** | 唯一负责人，确保计划完成 | 可以生成 Worker，可以调用工具，追踪整体进度 |
| **Worker** | 执行具体任务，产出原子结果 | 线性扩展，独立执行，互不干扰 |

### Planner 的全局视角

Planner 不仅分解任务，还要理解任务之间的依赖关系。这与之前轮次覆盖的 Cursor Long-Running Agents 的「规划优先」模式一致，但这里 Planner 是多 Agent 系统中的独立角色，而非人类审批的代理：

```
┌─────────────────────────────────────────────────────────┐
│                    Planner                               │
│  - 分析任务依赖图                                         │
│  - 生成执行计划（顺序/并行）                               │
│  - 将任务分配给 Executor                                  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Executor                             │
│  - 接收 Planner 的计划                                   │
│  - 生成 Worker 任务                                      │
│  - 监控 Worker 进度                                      │
│  - 处理任务失败和重试                                     │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼            ▼            ▼
         ┌────────┐   ┌────────┐   ┌────────┐
         │Worker 1│   │Worker 2│   │Worker N│
         │线性扩展│   │线性扩展│   │线性扩展│
         └────────┘   └────────┘   └────────┘
```

### Worker 的线性扩展性

Worker 是「可被替换的执行单元」。多个 Worker 可以并行执行不同任务，通过 Executor 的协调实现任务完成的线性扩展。这是「角色分层」方案相对于「自协调」方案的核心优势：**协调成本从 O(n²) 降为 O(n)**。

### Rust Harness 的工程选择

Cursor 选择 Rust 实现 Harness，原因是：

> "Rather than dealing with the complexity of distributed systems, we instead ran the harness on a single large Linux VM (Virtual Machine) with lots of resources."

这个选择背后的逻辑是：**分布式系统的复杂度远高于单机的并行调度**。用单机大内存 VM + 多进程的方式，可以避免分布式协调的一致性开销，同时利用多核并行处理多个 Agent。

---

## 可观测性：千量级 Agent 的调试基础

当 Agent 规模扩展到数千时，传统的「看日志」方式失效。Cursor 在可观测性上投入了大量前期工作：

```rust
// 简化的日志结构（概念示例）
struct AgentEvent {
    timestamp: DateTime<Utc>,
    agent_id: String,
    event_type: EventType,
    message: String,
    metadata: HashMap<String, String>,
}
```

日志记录的内容：
- 所有 Agent 消息（message）
- 所有系统动作（action）
- 所有命令输出（output）
- 时间戳用于回放和分析

> "This was not only helpful for us to manually review, but also for piping back into Cursor to sift through large amounts of data and quickly find patterns."
> — [Cursor Blog: Towards Self-Driving Codebases](https://cursor.com/blog/self-driving-codebases)

这个洞察很关键：**日志不只是事后调试工具，还可以被馈入 LLM 进行模式发现**。当人类无法手动阅读数千 Agent 的日志时，LLM 可以帮助找到「哪些 Agent 卡住了」「哪些任务反复失败」「哪些 Worker 效率最低」等模式。

---

## 实验结果：一周运行的洞察

Cursor 的系统最终能够稳定运行一周以上，数千 Agent 共同构建了一个 Web 浏览器（不含 JavaScript）。

> "By last month, our system was stable enough to run continuously for one week, making the vast majority of the commits to our research project (a web browser)."

关键发现：

1. **自协调方案在 20 Agent 规模就已崩溃**：锁竞争导致吞吐量不升反降，与「自协调」哲学的根本矛盾在于——协调本身需要共识，而共识需要通信，通信带来延迟

2. **角色分层实现了线性扩展**：Planner-Executor-Worker 模式下，增加 Worker 数量可以直接提升任务吞吐量，因为 Worker 之间无需协调

3. **可观测性是长期运行的前提**：当任务运行时间从分钟级扩展到周级时，中途的问题诊断必须依赖结构化日志，否则无法调试

4. **「完成任务」比「开始任务」更难**：Executor 的角色至关重要——它追踪全局进度，在 Worker 失败时重新调度，在任务偏离时纠正方向

---

## 与之前轮次覆盖内容的系统性关联

### 关联一：Anthropic 三 Agent 架构

Anthropic 的 GAN-inspired 架构（Generator-Evaluator-Analyzer）与 Cursor 的 Planner-Executor-Worker 都指向同一结论：**单 Agent 循环无法支撑长程任务**。但两者的设计哲学不同：

| 维度 | Cursor Planner-Executor-Worker | Anthropic Generator-Evaluator-Analyzer |
|------|-------------------------------|----------------------------------------|
| 核心目标 | 任务分解 + 执行追踪 | 生成质量 + 迭代改进 |
| 失败恢复 | Executor 重新调度 | Evaluator 驱动重生成 |
| 扩展方式 | Worker 线性扩展 | Generator 竞争生成 |
| 适用场景 | 已知目标的结构化任务 | 探索性的生成任务 |

两者共同验证的结论是：**多 Agent 系统的成功不取决于 Agent 的能力，而取决于协调结构的设计**。

### 关联二：OpenAI Agents SDK 的 Handoffs 机制

OpenAI 的 Agents SDK 提供了 Handoffs（交接）机制，Agent 可以将控制权转移给另一个 Agent。这与 Planner 将任务交给 Executor 的模式有相似之处，但 OpenAI 的 Handoffs 更强调「平等 Agent 之间的流动」，而 Cursor 的角色分层是「不平等的、有拥有权的」。

> 笔者认为：Handoffs 适合「能力互补的同质 Agent」场景（如不同专业技能 Agent 之间的协作），而角色分层适合「任务需要唯一负责人」的场景（如 Executor 必须对计划完成负责）。

### 关联三：Multi-Agent Markdown 协调规范

之前轮次覆盖的 Cursor Blog「Multi-Agent Kernels」文章指出协调逻辑从代码层下沉到 Markdown 声明式规范。Planner-Executor-Worker 架构本质上也是一种协调规范——只不过是用 Rust 代码实现的，而非 Markdown 文本。

> 笔者认为：角色分层架构和 Markdown 协调规范不是竞争关系，而是不同抽象层次的解决方案。Markdown 规范定义了「协调的意图」（谁做什么），Rust Harness 实现了「协调的执行」（如何高效运行）。

---

## 工程实践：角色分层的实现检查清单

如果要在自己的项目中实现角色分层架构，以下检查清单可能有所帮助：

### 架构设计阶段

- [ ] 任务是否可以分解为「规划 → 执行 → 原子任务」三层？
- [ ] 执行者是否需要「唯一负责人」来追踪整体进度？
- [ ] Worker 之间是否有依赖冲突，还是可以完全独立执行？

### 实现阶段

- [ ] Planner 是否维护了全局任务依赖图？
- [ ] Executor 是否有重试机制来处理 Worker 失败？
- [ ] Worker 的任务是否有超时保护，防止单任务卡住整体？
- [ ] 是否记录了足够的可观测性数据（事件类型、时间戳、metadata）？

### 调试阶段

- [ ] 能否从日志中重建「某时刻系统正在做什么」？
- [ ] 能否快速定位「哪个 Worker 失败了」？
- [ ] 能否发现「哪些任务反复失败，需要调整 Planner 的分解策略」？

---

## 局限性与未解决问题

Cursor 在文中坦诚地指出了当前方案的局限性：

> "Agents couldn't communicate with each other or provide feedback on the project as a whole. The system needed to be more dynamic."

这表明**角色分层架构的 Agent 之间仍然是单向关系**——Planner → Executor → Worker，没有反向的信息流动让 Planner 了解执行的实际情况。虽然 Executor 会报告进度，但 Planner 的规划是基于静态依赖图，而非动态的实际情况。

此外，**角色分层引入了新的协调瓶颈**：如果 Executor 成为唯一负责人，它本身可能成为瓶颈。当 Worker 数量扩展到数百时，Executor 的调度能力是否足够？

---

## 结论：从混乱到秩序

Cursor 的「Self-Driving Codebases」实验揭示了多 Agent 协作的核心洞察：

**自协调失败的原因是「让 Agent 自己达成共识」需要大量通信，而通信带来延迟和竞争。当 Agent 数量扩展时，这种开销非线性增长。**

**角色分层成功的关键是「预先分配责任」——Planner 负责规划，Executor 负责执行，Worker 负责产出。每个人只对自己的角色负责，不需要与其他角色协商。**

这与现实世界的组织设计原则惊人一致：复杂性来自协调，而非来自执行。当协调成本高于执行成本时，扁平化的自协调就会失败，分层的有控协调就会胜出。

> 笔者认为：角色分层架构将成为大规模多 Agent 系统的标准范式。Planner-Executor-Worker 不仅是一种技术方案，更是一种「放弃去中心化民主、选择集中式责任」的设计哲学。

---

**来源**：Cursor Engineering Blog「[Towards Self-Driving Codebases](https://cursor.com/blog/self-driving-codebases)」2026-05-10

**相关项目**：本文的实验基于数千 Agent 并行工作的 Rust Harness，与 [Cursor Long-Running Agents Planning-First Architecture](./cursor-long-running-agents-planning-first-harness-architecture-2026.md) 共同构成多 Agent 协作的完整图景。