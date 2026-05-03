# Gas Town：多 Agent 工作空间编排的工业级实现

**核心主张**：Gas Town 不是又一个「用 Agent 写代码」的工具，它是**多 Agent 协作的操作系统**——通过 Git Worktree 做状态持久化、Beads 做工作追踪、Witness/Deacon/Dogs 做健康监控，实现了 20-30 个 Agent 并行工作而不失控。这与 Cursor 第三时代的「多 Agent Fleet」理念形成呼应，但 Gas Town 更接近底层框架，而 Cursor 更接近终端用户产品。

**读者画像**：已经有单 Agent 使用经验，正在探索「如何同时跑多个 Agent」或「如何让 Agent 持续运行」的工程师。

**核心障碍**：当你想同时跑多个 Agent（每个处理不同任务）时，很快会遇到：上下文丢失、会话状态无法持久、Agent 之间无法协调、出了问题无法追踪。

---

## T - Target：谁该关注 Gas Town

**目标用户画像**：
- 正在从「单 Agent 串行」迁移到「多 Agent 并行」的团队
- 有大规模代码库维护需求（多模块、多仓库同时迭代）
- 希望 Agent 能在后台持续运行，而不是每次重启都「失忆」
- 需要对多个 Agent 的工作进度有集中可视化的团队负责人

**技术水平要求**：
- 熟悉命令行操作，有 tmux 使用经验更佳
- 理解 Git Worktree 机制（Gas Town 用它做隔离工作区）
- 有多 Agent 协作需求，而非单 Agent 增强场景

---

## R - Result：能带来什么具体改变

| 对比维度 | 无 Gas Town | 有 Gas Town |
|---------|------------|-------------|
| 多 Agent 并行规模 | 3-5 个本地会话（资源争抢） | 20-30 个 Agent 并行（独立 VM/容器） |
| Agent 重启后状态 | 完全丢失，需要重建上下文 | 通过 Git Hooks 自动恢复 |
| 工作追踪方式 | 人工记录或脑子记 | Beads 分类账本，结构化可查 |
| Agent 协调方式 | 人类在多个窗口切换监督 | Mayor 统一协调，Agent 间通过 Mailbox Handoff |
| 问题发现方式 | 等 Agent 跑完了才知道 | Witness/Deacon 实时监控，发现卡顿立即报警 |
| 工作复用 | 换一个会话完全重来 | Seance 查询上一个 Session 的决策和发现 |

> "Instead of losing context when agents restart, Gas Town persists work state in git-backed hooks, enabling reliable multi-agent workflows."
> — [Gas Town GitHub README](https://github.com/gastownhall/gastown)

---

## I - Insight：它凭什么做到这些

### 核心架构设计

Gas Town 的架构设计围绕**状态持久化**展开，这是它与其他多 Agent 方案的根本差异。

**1. Git Worktree 隔离（Hook）**

每个 Rig（即项目）使用独立的 Git Worktree，Agent 的工作直接写入 Worktree 而不影响主分支。这解决了：
- 多 Agent 同时操作同一仓库时的分支冲突
- Agent 工作可审核、可回滚、可追溯
- Agent 崩溃后，工作状态不丢失

**2. Beads 分类账本**

Beads 是 Gas Town 的工作单元抽象，格式为 `gt-abc12` 这样的 ID 前缀 + Git-backed 存储。Beads 的本质是**结构化的工作描述 + 状态追踪**，类似于轻量级的 Issue Tracker 内嵌在 Git 里。

**3. 三层看门狗（Witness / Deacon / Dogs）**

```
┌──────────────────────────────────────────┐
│  Deacon（全局巡逻监督者）                    │
│  ┌────────────────────────────────────┐  │
│  │  Witness（单 Rig 生命周期管理）       │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │  Polecat（实际工作的 Agent）   │  │  │
│  │  └──────────────────────────────┘  │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
        ↓ 触发
      Dogs（基础设施工人，执行清理/修复任务）
```

- **Witness**：监控单个 Rig 内的 Polecat，发现卡顿触发恢复
- **Deacon**：全局后台巡逻，协调跨 Rig 的资源分配
- **Dogs**：被 Deacon 派去执行具体任务的 Workers（如 Boot 做初始分类）

**4. Mayor 作为统一协调入口**

用户不需要记住各种 Agent 命令，只需要跟 Mayor（一个 Claude Code 实例）说话，告诉它你想完成什么。Mayor 理解工作空间的结构和 Agent 的能力，负责拆解任务并分配给相应的 Polecat。

> "Start here - just tell the Mayor what you want to accomplish."
> — [Gas Town GitHub README](https://github.com/gastownhall/gastown)

**5. Seance：跨 Session 的上下文继承**

`gt seance` 命令可以发现之前的 Agent Session，让当前 Agent 能查询上一个 Session 发现的上下文和决策。这解决了「上一个 Agent 发现了什么重要信息，换一个 Session 后完全丢失」的问题。

---

## P - Proof：谁在用、效果如何

| 指标 | 数据 |
|------|------|
| GitHub Stars | **14,914 ⭐**（持续增长中） |
| Forks | 1,359 |
| 编程语言 | Go（高性能，原生并发） |
| 最新更新 | 2026-05-03（活跃维护） |
| 依赖生态 | Git + Dolt + tmux + Claude Code/Codex/Copilot |
| 主要用户场景 | 多 Agent 并行的代码库维护、长时后台任务 |

**支持多种 Agent 运行时**：
- Claude Code（默认）
- OpenAI Codex
- GitHub Copilot CLI
- Gemini CLI（可扩展）

这意味着 Gas Town 不是一个 Claude 绑定的方案，团队可以根据需求选择或混用不同的 Agent 后端。

---

## 适用边界与竞品对比

### 何时用 Gas Town

- 需要同时处理 **5+ 个并行任务**的大型代码库维护
- 希望 Agent **持续在后台运行**而不占用本地资源
- 需要**结构化追踪多 Agent 工作进度**（不只是看 diff）
- 团队有 **tmux 使用经验**，习惯命令行工作流

### 何时不用 Gas Town

- 小型项目，单 Agent 串行就能完成
- 习惯 GUI 优先，不喜欢命令行操作
- 只需要「偶尔让 Agent 帮个忙」而非持续 Agent 工作流

### 与竞品的定位差异

| 方案 | 定位 | 核心优势 | 劣势 |
|------|------|---------|------|
| **Gas Town** | 多 Agent 工作空间 OS | 工业级规模（20-30 Agent）、Git-backed 状态持久化 | 需要 CLI 熟练，有一定学习曲线 |
| **Cursor 3** | 终端用户产品 | UI 友好、Cloud Agent 即开即用 | 对底层控制有限，不适合自托管 |
| **OpenAI Symphony** | Issue Tracker 编排协议 | 与 Linear 深度集成、任务驱动 | 依赖外部 Issue Tracker，需要一定工程集成能力 |
| **Claude Code（原生）** | 单 Agent 增强 | 无需额外工具、上手简单 | 多 Agent 并行需要手动管理 |

---

## 快速上手

### Step 1：安装 Gas Town

```bash
# macOS/Linux（Homebrew）
brew install gastown

# 或者 npm
npm install -g @gastown/gt

# 或者 Go 从源码编译
go install github.com/steveyegge/gastown/cmd/gt@latest
```

### Step 2：初始化工作空间

```bash
gt install ~/gt --git
cd ~/gt
```

### Step 3：添加项目 Rig

```bash
gt rig add myproject https://github.com/you/repo.git
```

### Step 4：启动 Mayor（统一协调入口）

```bash
gt mayor attach
```

然后直接告诉 Mayor 你想做什么，剩下的由 Mayor 协调 Agent 完成。

---

## 局限性与已知问题

1. **依赖复杂**：需要 Go 1.25+、Git 2.25+、Dolt、tmux，新用户环境配置成本高
2. **CLI-first 设计**：没有 GUI，对非 CLI 用户不友好
3. **概念密度高**：Mayor/Rig/Polecat/Hook/Bead/Convoy/Molecule 一整套术语体系，学习曲线陡
4. **macOS 限制**：Go 编译的二进制会被 macOS SIGKILL，需要通过 Homebrew 安装
5. **Dolt 依赖**：工作追踪依赖 Dolt（一个 Git-like 的 SQL 数据库），增加了运维复杂度

---

## 结论

Gas Town 代表了多 Agent 协作领域的**工业级框架**方向——不追求「一个命令让 AI 写代码」的酷炫，而是解决**「如何让 20-30 个 Agent 同时稳定运行」**这个真实的工程问题。

它的核心价值在于：
1. **Git Worktree 隔离**解决了多 Agent 并行时的状态冲突
2. **Beads 账本**解决了工作追踪的结构化问题
3. **三层看门狗**解决了大规模 Agent 集群的健康监控

如果你正在探索「多 Agent 并行工作」且有一定工程能力，Gas Town 是目前最完整的开源解决方案之一。但它的复杂性也说明：**多 Agent 协作的工程挑战还没有被「一键解决」，每个方案都在复杂度和能力之间做权衡**。

> 笔者认为：Gas Town 的架构设计值得多 Agent 框架开发者研究——它的分层（Hook/Bead/Convoy/Molecule）和健康监控体系是目前见过的最完整的工程实现。但对于大多数团队，Cursor 3 这样的产品方案可能是更好的起点，等需求复杂到 Cursor 3 满足不了时再考虑 Gas Town 或自建类似系统。

---

*来源：[Gas Town GitHub README](https://github.com/gastownhall/gastown)*
