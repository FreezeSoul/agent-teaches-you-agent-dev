# Agent Teams UI：像 CTO 一样管理 Agent 团队

## 定位破题

**一句话定义**：一个以「Kanban 看板」为界面的多 Agent 编排工具，让人类从「逐个管理 Agent」升级为「俯瞰 Agent 团队、自上而下发号施令」的 CTO 角色。

**场景锚定**：当你需要同时协调多个编码 Agent（比如一个做前端、一个做后端、一个做测试、一个做代码审查），且希望像管理人类工程师团队一样可视化它们的进度——这时你会想起 Agent Teams UI。

**差异化标签**：「桌面版 Multi-Agent 指挥中心」——不是网页工具，不是 API 调用，而是读取本地 Claude/Codex Session 状态后呈现的原生桌面应用。

---

## 体验式介绍

想象一个产品经理对着看板说：「这个 sprint 要重构登录模块。」

这句话通过系统传递出去，Kanban 看板上的「Todo」列立即出现了一张卡片。随后，后端 Agent 自动领取了后端重构任务，前端 Agent 领取了 UI 层任务，测试 Agent 领取了自动化测试任务——三者在各自的 worktree 分支上并行工作，偶尔互相发消息确认接口契约。

你不需要切换任何终端，不需要同时盯着 3 个 Claude Code 会话，不需要手动同步任何状态。你只需要坐在看板前喝咖啡，等着看哪些卡片的列从「In Progress」移动到「Review」，然后点进去看看 diff、接受或拒绝变更。

这就是 Agent Teams UI 呈现的体验。

**3 个让你「哇」的时刻**：

1. **零配置启动**：打开 App，自动检测本地 Claude Code 或 Codex 安装，引导完成 API key 配置，5 分钟内组建起第一个 Agent 团队
2. **Hunk 级 Code Review**：每个 Task 的 diff view 支持逐块（hunk）接受/拒绝——Agent 生成的代码不再是非黑即白的全接受，而是可以精细到每一段逻辑的选择性合并
3. **跨团队 Agent 通信**：不同团队之间的 Agent 可以互相发消息、协调任务依赖——这解决了多 Agent 协作中最难的可观测性问题

---

## 拆解验证

### 技术深度

Agent Teams UI 的核心架构设计：

**数据层**：读取 `~/.claude/` 下的 Session logs、todos、tasks 数据，将散落在文件系统里的 Agent 状态聚合为 Kanban 看板视图。

> "Data from `~/.claude/` (session logs, todos, tasks). The desktop app works with local runtime/session state."
> — [Agent Teams UI README](https://github.com/777genius/claude_agent_teams_ui)

这是一个聪明的设计决策：**不重新发明 Agent Runtime，而是复用现有 Claude/Codex 的 Session 管理能力**，在 UI 层做聚合和可视化。

**编排层**：Agent 之间通过「创建任务」「指派任务」「发消息」「留评论」四种机制协调。所有协调事件都记录在 Kanban 卡片的时间线（workflow history）里。

**Token 监控**：内置高级上下文监控系统，可以实时看到每个 Task 的 token 消耗、context window 使用率、各类内容占比（工具输出 / 推理文本 / 团队协调消息）。

> "Advanced context monitoring system — comprehensive breakdown of what consumes tokens at every step: user messages, Claude.md instructions, tool outputs, thinking text, and team coordination."
> — [Agent Teams UI README](https://github.com/777genius/claude_agent_teams_ui)

**环境隔离策略**：支持 per-agent git worktree（可选），避免多 Agent 并行写入同一分支导致的 Git 冲突。

### 竞品对比

| Feature | Agent Teams | Gastown | Paperclip | Cursor | Claude Code CLI |
|---|---|---|---|---|---|
| **跨团队通信** | ✅ 原生跨团队消息 | ⚠️ 跨 rig 协调 | ⚠️ 公司级组织工作 | N/A | ❌ |
| **Agent 间消息** | ✅ 原生实时邮箱 | ✅ 邮箱 + 交接 | ⚠️ 评论 + @提及 | ❌ | ✅ 团队邮箱，无 UI |
| **Hunk 级 review** | ✅ 接受/拒绝单块 | ❌ | ❌ | ✅ | ❌ |
| **全自主运行** | ✅ Agent 端到端创建/分配/review | ✅ 市长 + 恢复 | ✅ 心跳 + 治理 | ⚠️ 后台 Agent | ✅ 实验性 CLI 团队 |
| **零配置启动** | ✅ 引导式运行时检测 | ❌ 需要 Go/Git/Dolt/Beads/tmux | ⚠️ npx + 嵌入式 Postgres | ✅ | ⚠️ CLI + 环境变量 |
| **Kanban 看板** | ✅ 5 列，实时 | ❌ 仪表盘，非看板 | ✅ 7 列，拖放 | ❌ | ❌ |
| **Flexible autonomy** | ✅ 每步审批 + 通知 | ✅ 门控 + 升级 + 恢复 | ✅ 审批 + 暂停 + 终止 | ⚠️ 后台 Agent 自动运行命令 | ✅ 权限 + 钩子 |
| **价格** | **免费开源**，需 provider 访问 | 免费开源，需运行时计划 | 免费开源，需自托管 + 基础设施 | 免费 + 付费使用 | Claude 订阅或 API 使用 |

> Fact sources checked on May 5, 2026: [Gastown README](https://github.com/gastownhall/gastown), [Paperclip README](https://github.com/paperclipai/paperclip), [Cursor Bugbot](https://docs.cursor.com/en/bugbot), [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams).
> — [Agent Teams UI README](https://github.com/777genius/claude_agent_teams_ui)

### 社区健康度

| 指标 | 数值 |
|------|------|
| GitHub Stars | 855 |
| Forks | 191 |
| 最新更新 | 2026-05-06 |
| CI 状态 | ✅ 通过 |
| 许可证 | AGPL-3.0 |
| 多平台支持 | macOS (Apple Silicon + Intel) / Windows / Linux (AppImage/.deb/.rpm/.pacman) |

---

## 行动引导

### 快速上手（3 步）

1. **下载安装**：访问 [GitHub Releases](https://github.com/777genius/claude_agent_teams_ui/releases/latest)，选择你的平台（macOS/Windows/Linux）
2. **启动引导**：首次启动时，App 自动检测本地 Claude Code / Codex Runtime，引导完成认证
3. **组建团队**：选择一个本地项目，创建团队，定义角色（通过 provisioning prompt），Agent 自动开始在 Kanban 上领取任务

### 适合的贡献方向

- **MCP Server 集成**：扩展 Agent 的外部工具能力（已有一个内置 `mcp-server`）
- **新的 Provider 适配**：除 Claude/Codex 外，支持更多 LLM Provider 作为 Team Member
- **企业功能**：SSO/权限控制/审计日志（目前缺失的企业级功能）

### 路线图关注点

根据 README 中的设计文档结构，以下功能值得关注：
- 深度 Session 分析（per-task log 与代码变更的自动匹配）
- Post-compact 上下文恢复（Context 压缩后的运营状态保持）
- 预算控制（目前仅有可视化，尚无硬上限）

---

## 关联分析

**为什么这篇文章出现在 Agent Engineering 仓库里？**

Agent Teams UI 是 Cursor 3「统一多 Agent 工作空间」理念的**开源实现验证**：

| 维度 | Cursor 3 | Agent Teams UI |
|------|----------|----------------|
| **核心抽象** | Sidebar 统一 Agent 入口 | Kanban 统一 Agent 任务 |
| **交互模式** | 人 ↔ Agent（直接）| 人 ↔ Agent（通过看板）|
| **代码 review** | Diffs view 统一验收 | Hunk 级 review |
| **环境隔离** | 本地 ↔ 云端无缝迁移 | Per-agent git worktree |
| **生态扩展** | Marketplace（MCP/Skills）| MCP Server 集成 |
| **自主程度** | Cloud Agent 长时间运行 | 团队 Agent 端到端协作 |

两者都在解决同一个根本问题：**当 Agent 数量增长时，人类如何保持有效控制？** Cursor 3 提供了商业产品的答案，Agent Teams UI 提供了开源社区的答案。

如果你正在落地多 Agent 协作系统，Agent Teams UI 是目前开源生态中**最完整的 Agent 团队可视化方案**，而 Cursor 3 则代表了商业产品在这一方向上的最终形态。

---

*本文 source: [GitHub: 777genius/claude_agent_teams_ui](https://github.com/777genius/claude_agent_teams_ui) | 2026-05*
