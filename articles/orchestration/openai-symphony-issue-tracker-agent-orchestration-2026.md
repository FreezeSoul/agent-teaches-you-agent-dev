# Symphony：OpenAI 的开源规范，将 Issue Tracker 变为 Agent 编排控制平面

> **核心论点**：Symphony 代表了一种新的 Agent 工作范式——不再由人类监督每个 Agent 会话，而是让 Issue Tracker 成为控制平面，Agent 从中拉取任务并自主执行。这解决的不是「如何让 Agent 更快」而是「如何让人类不再成为 Agent 的瓶颈」。

> **来源**：本文核心内容基于 [OpenAI 官方博客 "An open-source spec for Codex orchestration: Symphony"](https://openai.com/index/open-source-codex-orchestration-symphony/) 以及 [Symphony SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md) 官方一手资料。

---

## 1. 问题的本质：人类的注意力成为瓶颈

在 Symphony 出现之前，即使是能力最强的编程 Agent（Codex、Claude Code、Cursor），仍然是**交互式工具**——人类在每个环节监督、引导、复查。

> "Each engineer would open a few Codex sessions, assign tasks, review the output, steer the agent, and repeat. In practice, most people could comfortably manage three to five sessions at a time before context switching became painful."
> — [OpenAI Engineering Blog](https://openai.com/index/open-source-codex-orchestration-symphony/)

这个瓶颈不是 Agent 能力的问题，而是**系统设计**的问题——我们在用管初级工程师的方式管理高能力的 Agent 团队，本质上是用人类的注意力去做本可以自动化的调度工作。

Symphony 的解决思路是：**重新思考工作是谁在驱动**。不是人类监督 Agent 完成每个任务，而是把 Issue Tracker（Linear）当作任务池，让 Agent 自己从里面拉取任务、并行执行、按时完成。

---

## 2. 核心机制：Issue Tracker 作为控制平面

Symphony 的设计哲学是将**任务抽象**而非**会话抽象**作为核心：

| 传统模式（会话驱动） | Symphony 模式（任务驱动） |
|---------------------|--------------------------|
| 人类打开多个 Agent 会话 | Agent 从 Issue Tracker 拉取任务 |
| 人类监督每个会话的执行 | Agent 在自己的 VM 中自主运行 |
| 会话完成 = 工作完成 | PR 合并 = 工作完成的证明 |
| 人类决定下一个任务 | Issue 状态变化触发下一阶段 |

Symphony 将 Linear 的 Issue Board 变成一个**持续运行的 Agent 编排控制台**：
- 每个 Open 状态的 Issue 获得一个专属 Agent
- Agent 在自己的隔离工作区持续运行，不占用本地资源
- Agent 可以创建新的 Issue（发现改进机会时），形成自生长的任务图
- DAG 依赖解析：被 Blocked 的任务自动等待，不会浪费计算资源

> "Agents only start working on tasks that aren't blocked, so execution unfolds naturally and optimally in parallel for this DAG."
> — [OpenAI Engineering Blog](https://openai.com/index/open-source-codex-orchestration-symphony/)

---

## 3. 技术架构：8 个核心组件

Symphony SPEC 定义了 8 个组件，分为 6 个抽象层次：

### 3.1 组件概览

```
┌─────────────────────────────────────────────────────────────┐
│  Policy Layer（仓库定义的 WORKFLOW.md）                      │
├─────────────────────────────────────────────────────────────┤
│  Configuration Layer（Config Layer，类型化配置访问）          │
├─────────────────────────────────────────────────────────────┤
│  Coordination Layer（Orchestrator，轮询循环/并发控制）        │
├─────────────────────────────────────────────────────────────┤
│  Execution Layer（Workspace Manager + Agent Runner）         │
├─────────────────────────────────────────────────────────────┤
│  Integration Layer（Issue Tracker Client for Linear）        │
├─────────────────────────────────────────────────────────────┤
│  Observability Layer（Logging + Optional Status Surface）   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

**Workspace 隔离**：每个 Issue 对应一个独立的文件系统工作区，Agent 的所有操作都在自己的目录内执行，不会污染其他任务的工作空间。这是将"Pet"（需要精心维护的个体）变成"Cattle"（可替换的单元）的关键。

**状态外部化**：Orchestrator 不维护持久数据库，状态来自 Linear 的 Issue 状态和文件系统。即使 Orchestrator 重启，也可以从 Issue Tracker 和 workspace 文件系统恢复到一致状态。

**Workflow as Code**：`WORKFLOW.md` 放在仓库根目录，团队版本控制 Agent 的运行时 prompt 和配置。这解决了「谁来维护 Agent 的指令」的问题——开发者即维护者。

---

## 4. 参考实现：为什么用 Elixir

Symphony 的参考实现选择了 Elixir，而不是更常见的 Python/TypeScript：

> "because when code is effectively free, you can finally pick languages for their strengths, like Elixir's concurrency"
> — [OpenAI Engineering Blog](https://openai.com/index/open-source-codex-orchestration-symphony/)

Elixir 的关键优势：
- **并发模型**：每个 Issue Agent 是独立的轻量级进程，调度开销极低
- **容错机制**（OTP）：Agent 失败不会级联影响其他任务
- **运维友好**：`mix run --daemon` 即可后台运行，原生监控/日志集成

但核心洞察是：**Symphony 首先是一个 SPEC.md**，不是一行代码。规范本身可以在任何语言中实现，Elixir 只是参考实现。这意味着团队可以用自己熟悉的工具链来构建符合 SPEC 的系统。

---

## 5. 与 Cursor Multi-Agent 范式的对比

| 维度 | Cursor AnySphere（GPU Kernel 优化） | OpenAI Symphony（任务编排） |
|------|-------------------------------------|---------------------------|
| **优化目标** | 多 Agent 协作完成 GPU Kernel 编译优化 | 多 Agent 从 Issue Tracker 并行拉取任务 |
| **协调机制** | Planner/Worker 单 Markdown 协议 | Linear Issue Tracker + DAG 依赖 |
| **执行环境** | 共享 GPU 资源，本地多 Agent | 独立云端 VM，每 Agent 独占环境 |
| **人类角色** | 实时 Review benchmark 结果 | 事后 Review PR + 视频 walkthrough |
| **典型场景** | 需要深度协作的性能优化任务 | 大规模特性开发 / 基础设施迁移 |

两条路线都在解决「人类成为瓶颈」的问题，但切入点不同：**Cursor 解决的是多 Agent 如何协作完成一个任务；Symphony 解决的是多个 Agent 如何并行完成多个任务**。

---

## 6. 从「严格状态机」到「目标导向」的设计教训

OpenAI 在构建 Symphony 过程中的一个关键洞察：

> "We learned that treating agents as rigid nodes in a state machine doesn't work well. Models get smarter and can solve bigger problems than the box we try to fit them in."
> — [OpenAI Engineering Blog](https://openai.com/index/open-source-codex-orchestration-symphony/)

早期版本的 Symphony 要求 Agent 严格按状态转换执行（`Todo` → `In Progress` → `Done`），结果发现这限制了模型的推理能力。改进后的方法是**给 Agent 目标而非步骤**——告诉 Agent 要完成什么，而不是如何一步步做。

> "The power of models comes from their ability to reason, so give them tools and context and let them cook."
> — [OpenAI Engineering Blog](https://openai.com/index/open-source-codex-orchestration-symphony/)

这对 Agent 系统设计有普遍意义：**越是把 Agent 框在预定义的状态机里，越是浪费模型的推理能力**。好的 Harness 应该给模型足够的上下文和目标，然后信任它能自己找到路径。

---

## 7. 实践影响：500% PR 增长背后的工作方式变革

OpenAI 内部的部分团队在采用 Symphony 后 3 周内 landed PR 数量增长了 **500%**，但更重要的是工作方式的转变：

- **探索成本趋近于零**：可以很便宜地让 Agent 去尝试一个想法或重构，满意就保留，不满意就丢弃，代价接近零
- **非工程师也能启动工作**：PM 和 Designer 直接在 Linear 里提需求，Agent 返回包含视频演示的 review packet，不需要懂技术
- **人类精力重新分配**：工程师不再花在监督 Agent 写代码，而是聚焦在真正需要判断力的复杂问题上

> "When agents write almost 100% of the code, and engineers spend their time breaking down problems, reviewing artifacts, and giving feedback — that is the new workflow."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

---

## 8. 适用边界与已知局限

Symphony 不是万能药：

**不适用的场景**：
- 模糊的、需要强判断力的任务仍然需要人类直接和 Agent 协作
- 高度敏感的安全环境（目前仍是低-key engineering preview）
- 不适合已有复杂 CI/CD 需要大量 human-in-the-loop 的场景

**已知的 trade-off**：
- 从实时监督转为 Issue 级别任务分配，失去了中途修正的能力
- Agent 有时产出会完全偏离目标，需要通过增加 guardrails 和 skills 来迭代改进
- 多 Agent 并行在生产规模下对 CI/环境稳定性要求极高（「一个 flaky test 在单开发者环境下可以绕过，但在工业规模下会中断每个 Agent run」）

---

## 结论：Agent 编排的新维度

Symphony 的核心贡献不是那个 Elixir 参考实现，而是一个**新的抽象层**：将 Issue Tracker 变成了 Agent 的控制平面。这个转变让人类的角色从「监督每个 Agent」变成「维护工作队列和验收标准」。

当这个模式普及后，软件开发的工作方式将从根本上改变：Agent 会像初级工程师一样从任务池中取活，持续运行在云端，人类更多扮演架构师和验收者的角色。

> **关键引用**：
> - [OpenAI Symphony 官方仓库](https://github.com/openai/symphony)
> - [OpenAI Engineering Blog: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/)
> - [SPEC.md 完整定义](https://github.com/openai/symphony/blob/main/SPEC.md)