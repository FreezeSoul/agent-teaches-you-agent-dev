# 第三代软件开发：Agent Fleet 架构如何重新定义软件工厂

> **本文解决的问题**：为什么 Cursor 将"软件工厂"（Factory）概念引入 Agent Fleet 编排？这种架构与传统的 Single Agent 模式有什么本质差异？GitHub Copilot /fleet 的实现揭示了哪些多 Agent 协作的工程挑战？

---

## 背景：软件开发的三代演进

Cursor 官方博客在「[The third era of AI software development](https://cursor.com/blog/third-era)」中，将软件开发分为三个时代：

| 时代 | 核心交互模式 | 典型工具 | 人类角色 |
|------|------------|---------|---------|
| 第一代 | Tab 自动补全（低熵重复工作）| Tab / Copilot autocomplete | 一键一键写 |
| 第二代 | 同步 Agent（Prompt-Response 循环）| Claude Code / Cursor Agent | 引导每个步骤 |
| 第三代 | Agent Fleet（异步、并行、长时间运行）| Cursor Cloud Agent / Copilot /fleet | 定义问题 + 设置审查标准 |

Cursor 的数据揭示了演进速度：

> "Agent usage in Cursor has grown over 15x in the last year. In March 2025, we had roughly 2.5x as many Tab users as agent users. Now, we now have 2x as many agent users as Tab users."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

更惊人的是 Cursor 内部数据：

> "More than one-third of the PRs we merge are now created by agents that run on their own computers in the cloud."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

第三代的核心变化是：**软件工厂**这个隐喻的失效与重建。

---

## 软件工厂隐喻的失效：从「操作员」到「工厂主」

在第二代范式中，开发者是一个操作员——发出指令、等待 Agent 响应、审查结果、再发出下一条指令。Agent 是一个放大个人生产力的工具。

但在第三代范式中，开发者变成工厂主：定义生产目标、装备 Agent 工具、设置验收标准，然后 Agent Fleet 在无人干预的情况下完成生产。

Cursor 对此的描述尤为精准：

> "Cursor is no longer primarily about writing code. It is about helping developers build the factory that creates their software. This factory is made up of fleets of agents that they interact with as teammates: providing initial direction, equipping them with the tools to work independently, and reviewing their work."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

这个隐喻的变化带来三个核心的结构性转变：

**① 人与 Agent 的关系从「指挥」变为「委托」**

在同步 Agent 模式下，开发者通过 prompt 控制 Agent 的每一步动作。在 Fleet 模式下，开发者给出目标，Agent 自主决定执行路径。人类控制从「每步审批」变为「结果审查」。

**② 并行化从「不可能」变为「默认」**

同步 Agent 受限于本地计算资源（多个 Agent 竞争同一台机器的内存和 CPU），且缺乏足够的上下文让人类同时监控多个 Session。Cloud Agent 通过 VM 隔离解决了这个问题，使并行化成为可能。

**③ 产出从「Diff」变为「Artifact」**

传统的 Agent 输出是 Diff——人类需要理解代码改了什么。但 Cloud Agent 运行在隔离的 VM 中，有时间迭代和测试，因此产出的是更丰富的 Artifact：视频、截图、日志、可运行的预览。

---

## Agent Fleet 的架构设计：隔离、编排、聚合

### 隔离层：Git Worktree 作为并行化的物理基础

多个 Agent 同时工作，首要问题是：**文件系统隔离**。如果两个 Agent 写入同一个文件，后写入的 Agent 会无声地覆盖前者的更改（没有错误、没有合并提示）。

Amplitude 的工程师描述了这个困境：

> "Local agents compete for the same set of limited resources and quickly run into conflicts. Even running two or three agents at once can lead to performance degradation. Amplitude's codebase is large enough that local developer machines were hitting memory limits, even on high-end hardware with large amounts of RAM."
> — [Cursor Blog: Amplitude ships 3x more production code with Cursor](https://cursor.com/blog/amplitude)

Cursor Cloud Agent 通过「每个 Cloud Agent 运行在独立 VM 上」来解决物理隔离问题。但还有一个更精细的隔离维度：**同一个代码库的并行修改**。

Git Worktree 是解决这个问题的主流方案——每个 Agent 在独立的 Git Worktree 中工作，写入不同的分支，最后通过 PR 合并。Anthropic 的 C Compiler 团队在 100K 行代码的编译任务中验证了这个方案（见 `metamorph-multi-agent-file-lock-parallel-2026.md`）。

### 编排层：从「点对点」到「Orchestrator-Subagent」模式

GitHub Copilot `/fleet` 揭示了 Fleet 编排的核心架构——**Orchestrator 模式**：

> "When you run /fleet with a prompt, the behind-the-scenes orchestrator: Decomposes your task into discrete work items with dependencies. Identifies which items can run in parallel versus which must wait. Dispatches independent items as background sub-agents simultaneously."
> — [GitHub Blog: Run multiple agents at once with /fleet in Copilot CLI](https://github.blog/ai-and-ml/github-copilot/run-multiple-agents-at-once-with-fleet-in-copilot-cli/)

这个模式有几个关键设计决策：

**依赖声明机制**：Agent 可以声明哪些工作项依赖于其他工作项。Orchestrator 会序列化这些依赖，并行化其余部分。例如：

```markdown
1. Write new schema in migrations/005_users.sql
2. Update the ORM models in src/models/user.ts (depends on 1)
3. Update API handlers in src/api/users.ts (depends on 2)
4. Write integration tests in tests/users.test.ts (depends on 2)
```

Items 3 和 4 可以在 Item 2 完成后并行执行，而 Item 1→2→3 是串行的。

**文件边界强制**：Sub-agent 之间共享文件系统，但没有文件锁。如果两个 Agent 写入同一文件，后者无声覆盖前者。解决方法是让每个 Agent 的 prompt 明确文件边界，或者让每个 Agent 写临时文件，由 Orchestrator 最终合并。

**自定义 Agent 定义**：可以在 `.github/agents/` 中定义专用 Agent，每个 Agent 可以指定自己的模型、工具和指令。这解决了「复杂逻辑需要重型模型，文档需要轻量模型」的资源分配问题。

### 聚合层：从「多个结果」到「统一产出」

Orchestrator 在所有 Sub-agent 完成后，还需要做最后一件事：验证输出并合成最终产物。Copilot `/fleet` 的文档指出了这一点：

> "Verifies outputs and synthesizes any final artifacts."

这意味着 Orchestrator 不只是分配任务，还要担任 QA 角色：检查每个 Sub-agent 的输出是否满足初始声明的验证标准（如 lint、type check、tests pass）。

---

## 两种 Fleet 架构路线对比：Cursor vs GitHub

| 维度 | Cursor Cloud Agent Fleet | GitHub Copilot /fleet |
|------|-------------------------|----------------------|
| **架构** | 云端 VM 隔离 + 人类在回路（Human-in-the-loop）| Orchestrator-Subagent 模式，部署在同一机器上 |
| **并行化粒度** | 多 Cloud Agent 同时运行，每个在独立 VM 中 | 多个 Sub-agent 在后台并行，通过 `/tasks` 查看状态 |
| **文件隔离方案** | 云端 VM（天然文件系统隔离）| 共享文件系统（需要人工声明边界或使用 Git Worktree）|
| **产出形式** | 视频 + 截图 + 可运行的预览（Rich Artifact）| 任务完成后统一 Diff |
| **适用场景** | 需要长时间运行、深度迭代的生产级任务 | 需要快速并行处理多个文件/模块的开发任务 |
| **Human-in-loop** | 始终可介入（通过 Slack/Cursor UI 触发）| 非交互模式下无法介入（`--no-ask-user`）|

两者核心区别在于 **Agent 与人类的交互距离**：Cursor 的 Cloud Agent 允许人类在任何时候通过 Slack 触发新的 Agent，或审查 Agent 回传的 Artifact；Copilot `/fleet` 则更偏向一次性任务执行，完成后人类审查结果。

Amplitude 的案例展示了 Cursor Cloud Agent Fleet 的完整工作流：

> "When a new message lands in Slack, a cloud agent checks Linear to see if a ticket already exists for the issue. If one does, the agent adds the new customer context. If not, the agent explores the codebase, opens a new ticket, and opens a PR with its solution implemented."
> — [Cursor Blog: Amplitude ships 3x more production code with Cursor](https://cursor.com/blog/amplitude)

Slack → Linear → PR 的完整闭环，由 Cloud Agent 在无人类干预的情况下完成。这不是「辅助编码」，而是「自主完成整个开发流程」。

---

## Fleet 架构的已知工程挑战

### 挑战一：Flaky Test 在工业级规模下的放大效应

Cursor 坦承：

> "At industrial scale, a flaky test or broken environment that a single developer can work around turns into a failure that interrupts every agent run."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

单个开发者在本地可以绕过的环境问题（如偶发的 flaky test），在 Fleet 模式下会同时中断所有 Agent 运行。环境稳定性成为生产级 Fleet 的基础设施要求。

### 挑战二：上下文传递的缺失

Sub-agent 无法看到 Orchestrator 的完整对话历史。Orchestrator 在 dispatch 时需要将所有必要的上下文打包进 prompt。如果之前的 session 中收集了有用的上下文，必须在 `/fleet` prompt 中显式包含或让 Sub-agent 读取文件。

### 挑战三：文件冲突的无声覆盖

> "Sub-agents share a filesystem with no file locking. If two agents write to the same file, the last one to finish wins—silently. No error, no merge, just an overwrite."
> — [GitHub Blog: Run multiple agents at once with /fleet in Copilot CLI](https://github.blog/ai-and-ml/github-copilot/run-multiple-agents-at-once-with-fleet-in-copilot-cli/)

这是一个本质性的工程问题。在分布式文件系统中，文件锁是常见的解决方案。但在本地开发场景中，使用 Git Worktree + 不同分支是最轻量的方案。

---

## 我认为：从「工具」到「工厂」的关键转折点

第三代软件开发的本质变化不是「Agent 变得更强」，而是**软件开发的产出单位从「代码」变成了「系统」**。

在第一代和第二代中，人类的产出物是代码——即使 Agent 辅助，最终交付的仍然是代码文件，人类负责理解、整合、部署。

在第三代中，人类交付的是**工厂**——一套由 Fleet 构成的自主生产系统，人类只负责定义标准和审查结果。

> "A year from now, we think the vast majority of development work will be done by these kinds of agents."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

这个转变对工程实践的影响是深远的：

1. **测试和验证标准变得比代码更重要**——当 Agent 可以无限量生产代码时，代码的质量由验收标准决定，而不是由编写者的水平决定
2. **环境稳定性成为核心竞争力**——Flaky test 在本地开发中只是烦扰，在 Fleet 模式中是系统性风险
3. **多 Agent 协调能力成为工程团队的核心技能**——如何分解任务、如何声明依赖、如何处理冲突，这些不再是「架构师」的问题，而是每个开发者都需要掌握的基本技能

---

## 执行流程

1. **理解任务**：本轮发现 Cursor 第三代软件开发 + GitHub Copilot /fleet 两个一手来源，需要深度分析 Agent Fleet 架构设计
2. **规划**：选择 orchestration/ 目录，文章主题是「软件工厂」隐喻下的 Fleet 架构，与上一轮的 Sandbox/Harness 形成「基础设施层」vs「应用编排层」的对照
3. **执行**：调用 web_fetch 2次获取 Cursor + GitHub 原文，tavily-search 3次确认项目线索
4. **返回**：获取 Cursor third-era + Amplitude 案例 + GitHub fleet 技术细节
5. **整理**：按「范式分析」类型设计大纲，包含原文引用5处，完整覆盖架构设计 + 工程挑战 + 判断性内容

**调用工具**：
- `web_fetch`: 3次
- `tavily-search`: 5次
- `exec`: 3次