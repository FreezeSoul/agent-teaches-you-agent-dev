# Storybloq：跨会话上下文持久化 —— 将每次编程变成积累而非重置

## 定位

**Storybloq** 解决的是 AI 编程助手最根本的体验断裂问题：**每次新会话都是从零开始**。它通过一个文件约定（`.story/`）+ CLI + MCP Server + `/story` Skill 的组合，让 Claude Code 在每次启动时自动加载项目的完整上下文—— tickets、issues、roadmap、session handovers、lessons learned——形成跨会话的连续性。

> "Every new session starts from zero. The model doesn't know what was built yesterday, what's broken, what decisions were made, or what to work on next."
> — [Storybloq README](https://github.com/Storybloq/storybloq)

---

## 体验

想象这样的场景：

**周一**：你让 Claude Code 实现用户认证模块。它完成了 `auth.ts` 和测试，但还有两个未解决的边缘情况。你输入 `/story handover`，Storybloq 自动生成一份 session 总结，包含决策记录、阻塞点和下一步。然后你关闭了电脑。

**周二**：你打开一个新 session，输入 `/story`。Storybloq 读取 `.story/` 目录，加载最新 handover，自动告诉你：「T-002 和 T-003 还未完成，ISS-001 阻塞了 T-003，昨天的决策：使用 JWT 而非 Session-Cookie」。Claude Code 直接从昨天的断点继续。

这就是 Storybloq 的核心价值：**将每次编程 session 从独立的"事件"变成可累积的"建设块"**。

---

## 架构拆解

Storybloq 不是一个单一工具，而是一套组合：

### 1. `.story/` 文件约定

每个项目有一个 `.story/` 目录，包含结构化的 JSON 文件：

```
.story/
├── config.json         项目配置 + recipe 覆盖
├── roadmap.json        阶段顺序 + 元数据
├── tickets/            T-001.json, T-002.json, ...
├── issues/             ISS-001.json, ISS-002.json, ...
├── notes/              N-001.json, N-002.json, ...
├── lessons/            L-001.json, ...            ← 沉淀的决策和反模式
├── handovers/          YYYY-MM-DD-<slug>.md        ← 每次 session 的交接文档
└── snapshots/          状态快照（gitignored）
```

所有文件通过 git 跟踪，意味着项目的历史记录和决策记录和代码本身一起被版本化管理。

### 2. MCP Server（43 个工具）

Storybloq 注册为一个 MCP Server，Claude Code 可以直接调用 43 个工具，无需 subprocess 开销。这些工具分为三类：

- **只读类**：读取 tickets、issues、handover、status、blockers
- **写入类**：创建/更新 tickets、issues、lessons、handover
- **自主模式**：驱动 autonomous state machine（`storybloq_autonomous_guide`）

关键的是，这些工具直接操作 `.story/` 文件系统，Claude Code 无需理解内部格式，只需要调用 Skill 即可。

### 3. `/story` Skill

安装后，Claude Code 中可以直接调用 `/story` 命令：

- **`/story`**：加载项目状态，读取最新 handover，列出 open tickets 和 issues，总结近期变化
- **`/story auto T-001 T-002`**：自主模式，驱动 ticket 从 plan → plan review → implement → tests → code review → commit，在每个 checkpoint 生成 handover
- **`/story handover`**：生成当前 session 的 handover 文档

### 4. PreCompact Hook（自动快照）

当 Claude Code 触发 context compaction（上下文压缩）时，Storybloq 自动执行 `storybloq snapshot --quiet`，在压缩前保存当前状态。这意味着 `recap`（回顾）永远反映的是最新状态，不会因为压缩而丢失工作进度。

> "`setup-skill` installs the `/story` skill globally to `~/.claude/skills/story/`, registers this package as an MCP server, and configures a PreCompact hook that auto-snapshots state before context compaction."
> — [Storybloq README](https://github.com/Storybloq/storybloq)

---

## 主题关联：Session 连续性与环境自动化的互补

这篇文章与本轮收录的「Cursor Composer 自举技术：RL 训练环境中环境自动化」形成互补：

**autoinstall** 解决的是「如何让 RL 训练环境从零自动生成」，核心是「环境 provisioning 的自动化」。

**Storybloq** 解决的是「如何让编程 session 从零散的独立事件变成可积累的建设过程」，核心是「上下文和决策的跨会话持久化」。

两者的共同主题是：**减少人工准备成本，让 Agent 的工作流能够跨越时间边界延续**。autoinstall 面向的是训练基础设施，Storybloq 面向的是开发工作流。但两者都在解决同一个问题——当 Agent 需要处理一个需要多天、多 session 完成的大型任务时，如何确保上下文不丢失、决策不重复、劳动不浪费。

---

## 项目健康度

| 指标 | 数值 |
|------|------|
| **GitHub Stars** | 217 ⭐（2026-04-17 创建，1个月） |
| **语言** | TypeScript |
| **License** | PolyForm Noncommercial 1.0.0 |
| **npm 包** | @storybloq/storybloq |
| **平台** | CLI + MCP Server + Mac App |

关注的关键信号：
- 43 个 MCP 工具 + autonomous mode + multi-lens review 集成，说明项目工程化程度较高
- Mac App 单独产品且有 App Store 可见性，说明团队在商业化路径上有思考
- lessons/ 目录设计（沉淀决策和反模式）是与其他 context 管理工具的差异化亮点

---

## 快速上手

```bash
# 安装
npm install -g @storybloq/storybloq@latest

# 初始化项目
cd your-project
storybloq init --name "your-project"

# 安装 /story skill（CLI 会自动引导）
storybloq setup-skill

# 在 Claude Code 中使用
/story                    # 加载状态 + 最新 handover
/story auto T-001 T-002  # 自主模式驱动 ticket 完成
/story handover           # 生成当前 session 的 handover
```

---

## 何时关注

- 当你在一个需要多天完成的大型项目中频繁使用 Claude Code
- 当你发现每次打开 Claude Code 都需要花时间重新解释上下文
- 当你想要积累项目决策和经验教训，而不是每次都重新摸索
- 当你在使用其他 context 管理工具（如 CLAUDE.md、记忆系统）但希望有更结构化的方案

---

## 关联项目

| 项目 | 关系 |
|------|------|
| **Cursor Composer Autoinstall**（本仓库 Article） | 互补：环境 provisioning 自动化 vs 上下文/session 连续性 |
| **Claude Code Memory Setup**（lucasrosati） | 互补：Obsidian 知识图谱层 vs Storybloq 文件层 |
| **Storybloq Lenses**（@storybloq/lenses） | 配套：8 个并行 specialized reviewers 的 code review MCP Server |

---

*本推荐文章属于 projects/ 目录，关联 Article：`articles/fundamentals/cursor-composer-autoinstall-bootstrapping-rl-training-2026.md`*