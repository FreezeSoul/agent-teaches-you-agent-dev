# GSD-2：让 Agent 无人监管运行数月的生产级 Harness

**核心论点**：Anthropic 的 Initializer/Coding Agent 双组件架构揭示了长程 Agent 的核心挑战——跨 session 的状态持久化与增量推进机制。GSD-2 是这一工程思想的开源生产级实现：通过 DB 权威的运行时状态、无人值守的 Auto Pipeline、和结构化的 Milestone/Slice 机制，让单个 Agent 可以真正"一次命令，离去数月，回来时项目已完整交付"。

**项目**：[gsd-build/GSD-2](https://github.com/gsd-build/GSD-2)，7,269 ⭐，2026-05-09 刚更新（持续活跃）

**主题关联**：Anthropic「长程 Agent Harness 架构」→ GSD-2 是该架构原则的生产级工程实现

---

## P - Positioning（定位破题）

GSD-2 是一个**自主编码 Agent 的生产级 Harness 系统**，构建在 [Pi SDK](https://github.com/badlogic/pi-mono) 之上，直接拥有 TypeScript 级别的 Agent harness 控制权。

> "GSD is now a standalone CLI built on the Pi SDK, which gives it direct TypeScript access to the agent harness itself. That means GSD can actually _do_ what v1 could only _ask_ the LLM to do: clear context between tasks, inject exactly the right files at dispatch time, manage git branches, track cost and tokens, detect stuck loops, recover from crashes, and auto-advance through an entire milestone without human intervention."

**一句话定义**：一个让 AI Coding Agent 能够真正实现"一次命令，几个月不管"的生产级自律执行框架。

**场景锚定**：当你需要交付一个完整功能模块/应用，但不想每天盯着 Agent 进度；当你有明确的需求文档，但需要 Agent 在数周内自主完成开发、测试、PR 提交全流程。

**差异化标签**：DB 权威状态 + Auto Pipeline + 无人值守 Milestone 交付

---

## S - Sensation（体验式介绍）

想象你运行这样一条命令：

```bash
gsd new-project --deep "我要一个支持多租户的 SaaS 后台"
```

然后你离开去度假。几周后你回来，看到的是：

- 一个完整的多租户 SaaS 后台，有数据库 schema、API 路由、权限体系
- Git history 干净，每个 Milestone 有结构化 commit message
- 单元测试覆盖率达标，PR 已准备好 review
- `gsd.db` 中记录了每一次 dispatch、每一次 lease 获取、每一个决策的完整审计日志

这不是科幻。这是 GSD-2 v2.79（最新版本）的实际能力。

**你感受到的"哇时刻"**：

> "DB-authoritative runtime state — workers, leases, dispatches, and a command queue are now first-class DB rows, replacing ad-hoc files for cross-process auto coordination."

GSD-2 把整个运行时状态（Worker 调度、Lease 管理、Dispatch 队列）全部放进 SQLite DB。这意味着：
- Agent 崩溃重启后，可以精确恢复到最后一个 Milestone 的状态
- 不再有"断点续跑时不知道上次的 context 在哪"的问题
- 多个并发 Worktree 的状态不会互相污染

---

## E - Evidence（拆解验证）

### 技术深度：三个核心系统

#### 1. DB 权威的运行时状态（v2.79 最新特性）

```sql
-- GSD-2 的数据库 schema 包含：
-- workers, leases, dispatches, command_queue
-- milestone_id, slice_id, task_status
-- metrics_ledger (原子写入，防止并发腐败)
```

> "Stuck-state migration — `copyPlanningArtifacts` / `reconcile` deleted; auto-mode writers canonicalize through the DB instead of mirroring artifacts to disk."

这解决了 Anthropic 文章中提到的"Agent 重启后不知道上个工作状态"的核心痛点。GSD-2 的解法是：**DB 是唯一的真相来源**，不再有 `.paused-session.json` 或 `auto.lock` 文件导致的 TOCTOU 竞态。

#### 2. Auto Pipeline 的委托策略

```bash
# 委托策略由 DB 中的 delegation_policy 表定义
# 每个工具调用都有 background-safety policy verdict
# reactive-execute 默认：≥3 个 ready task 时触发并行调度
```

> "Reactive-execute default — auto-dispatch defaults to reactive-execute when ≥3 ready tasks are queued, replacing the always-sequential fallback."

这意味着 GSD-2 不是简单的"顺序执行任务"，而是**根据任务队列状态动态决定执行策略**——有足够的并行度时自动并行，任务稀缺时退回顺序执行。

#### 3. Deep Planning Mode（Phase 11）

```
/gsd new-project --deep
# 会触发:
# - research-decision dispatch unit
# - research-project dispatch unit
# - project-shape-aware discuss depth（根据项目规模调整调研深度）
# - gated approval flows（会在 Milestone 中暂停，而非中止）
```

> "EVAL-REVIEW system — `/gsd eval-review` command, pre-ship soft warning when EVAL-REVIEW status is incomplete."

这体现了 GSD-2 的工程成熟度：**不只在代码层面工作，还在质量保障层面引入了结构化的 Review 机制**。

### 社区健康度

| 指标 | 数值 | 说明 |
|------|------|------|
| GitHub Stars | 7,269 | 持续增长，2026-05-09 刚更新 |
| 最新版本 | v2.79 | 高频迭代（v2.72 → v2.73 → ... → v2.79）|
| 架构成熟度 | 生产级 | DB 权威状态、Atomic metrics 写入、单写入器 invariant |
| 平台覆盖 | macOS/Linux/Windows | 跨平台支持，含 Windows 路径修复 |

### 与 Anthropic 方案的对应关系

| Anthropic 文章中的概念 | GSD-2 的实现 |
|------------------------|-------------|
| Initializer Agent | `gsd new-project` 时触发 deep planning + research dispatch |
| Coding Agent | 每个 Milestone 的 executor agent |
| Feature List (JSON) | DB 中的 `milestone_features` 表 + Slice 作为任务单元 |
| Progress File | `claude-progress.txt` → `gsd.db` 的 metrics_ledger |
| Git commit hygiene | 原子提交、user hooks 执行、milestone-tagged commits |
| End-to-end testing | Puppeteer MCP（或其他 MCP 工具）集成 |

> "Anthropic prompt-cache preserved — `pi-coding-agent` and `gsd` no longer thrash the cache on dispatch."

GSD-2 还修复了 Anthropic 在 prompt caching 上的一个具体工程问题——这说明 GSD-2 团队在深度跟随 Anthropic 的 Agent 工程实践。

---

## T - Threshold（行动引导）

### 快速上手（3 步）

```bash
# 1. 安装
npm install -g gsd-pi@latest

# 2. 初始化项目（deep 模式 = 启用完整 research + approval flow）
gsd new-project --deep "我的项目需求"

# 3. 启动无人值守模式
gsd auto
# 然后你可以离开——GSD-2 会：
# - 通过 DB 持久化所有状态
# - 在每个 Milestone 自动 commit
# - 在遇到 approval gate 时暂停等你回来确认
# - 检测 stuck loops 并尝试恢复
```

### 适合的贡献方向

- **Extension 生态**：GSD-2 有完整的 Extensions API，目前已有 `@gsd-extensions/google-search`，可以贡献更多技能扩展
- **MCP 集成**：GSD-2 的 MCP 支持仍在快速演进，可以参与工具发现和路由的优化
- **DB Schema 演进**：随着 auto-mode 复杂度提升，schema 设计和迁移有大量工程工作

### 持续关注的价值

GSD-2 的 roadmap 明确指向**更强的自主性**——从"一次命令运行几天"到"真正无人监督的长期编码 Agent"。如果你关注 AI Coding Agent 的工程前沿，这个仓库是必跟的。

---

## 关联索引

**相关 Article**：
- `articles/harness/anthropic-effective-harnesses-long-running-agents-initializer-pattern-2026.md` — Anthropic 双组件 Harness 架构原理解析

**相关 Projects**：
- `context-mode-mksglu-98-percent-context-reduction-2026.md` — 另一个上下文优化方向，与 GSD-2 的 dispatch-context 优化互补

---

**引用来源**：

> "One command. Walk away. Come back to a built project with clean git history."
> — [GSD-2 README](https://github.com/gsd-build/GSD-2)

> "DB-authoritative runtime state — workers, leases, dispatches, and a command queue are now first-class DB rows, replacing ad-hoc files for cross-process auto coordination."
> — [GSD-2 README - v2.79 Changelog](https://github.com/gsd-build/GSD-2)

> "GSD is now a standalone CLI built on the Pi SDK, which gives it direct TypeScript access to the agent harness itself. That means GSD can actually _do_ what v1 could only _ask_ the LLM to do: clear context between tasks, inject exactly the right files at dispatch time, manage git branches, track cost and tokens, detect stuck loops, recover from crashes, and auto-advance through an entire milestone without human intervention."
> — [GSD-2 README](https://github.com/gsd-build/GSD-2)