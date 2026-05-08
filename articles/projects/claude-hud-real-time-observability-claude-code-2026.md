# jarrodwatts/claude-hud：Claude Code 的实时可观测性插件

## 核心问题：Agent 运行时的「黑箱」困境

当你的 Claude Code Agent 在后台跑了 30 分钟，读取了 47 个文件，执行了 23 次 grep，启动了 2 个 subagent——你如何在不干扰它的情况下知道它现在在做什么？

传统方案是开两个终端、分屏、或者靠日志回溯。但这些都打破了工作流的连续性。claude-hud 的答案是：**把状态直接写到你的终端底部**，永远可见，从不遮挡。

> "A Claude Code plugin that shows what's happening — context usage, active tools, running agents, and todo progress. Always visible below your input."

---

## TRIP 四要素

| 要素 | 内容 |
|------|------|
| **T - Target** | 使用 Claude Code 的开发者，尤其是运行长程任务（>10 分钟）或多 subagent 编排的用户 |
| **R - Result** | 无需切换窗口/终端，实时看到 Context 健康度（45%→100%）、工具活动、subagent 状态、Todo 进度；不打断工作流 |
| **I - Insight** | 利用 Claude Code 原生 statusline API（stdin JSON → plugin → stdout）而非独立窗口或 tmux，实现零成本集成 |
| **P - Proof** | GitHub 2026年3月 trending，日增长 +1,068 stars；jarrodwatts 总计 22k+ stars；中英双语文档 |

---

## 为什么这个项目重要（问题驱动）

### 问题 1：Context 焦虑

Claude Code 的 Context Window 有上限。当你看到它已经用了 80% 时，你面临一个选择：等它耗尽后失败，还是主动干预？

大多数情况下，你不知道它什么时候会到达那个临界点。claude-hud 的 Context Bar（绿→黄→红）让你**提前看到水位**，而不是事后补救。

### 问题 2：Subagent 迷雾

当你用 `/agent` 启动多个 subagent 时，主会话只知道「有 subagent 在跑」，但不知道：
- 它现在在执行什么工具？
- 已经跑了多久？
- 当前任务的上下文是什么？

claude-hud 的 Agent Tracking 解决了这个问题：

```
◐ explore [haiku]: Finding auth code (2m 15s)
```

你看到 subagent 的名称、模型、当前任务、运行时长。

### 问题 3：工具活动噪声

Claude Code 执行时会调用 Read/Grep/Edit/Bash 等工具，但主会话的输出只显示最终结果，不显示过程。如果你想知道「它读了哪些文件」，你需要回溯日志。

claude-hud 的工具活动条实时显示：

```
◐ Edit: auth.ts | ✓ Read ×3 | ✓ Grep ×2 ← Tools activity
```

---

## 技术架构：Native Statusline API 的正确用法

claude-hud 没有发明任何新东西——它只是正确地使用了 Claude Code 的 statusline 协议：

```
Claude Code → stdin JSON（transcript）→ claude-hud → stdout → 终端底部
```

这意味着：
- **零额外窗口**：HUD 出现在每个终端会话的底部
- **零 tmux 依赖**：不需要配置 split/pane
- **跨平台**：Linux/Mac/Windows 均支持（Linux 需要处理 /tmp tmpfs 问题）
- **Context 精准**：使用 Claude Code 原生 token 数据，而非估算值

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│ Claude Code                                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Transcript JSONL                                │   │
│  │ {"type":"tool","name":"Read","path":"auth.ts"}  │   │
│  │ {"type":"agent","name":"explore","status":"..."} │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↓ stdin JSON                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ claude-hud (plugin process)                    │   │
│  │  - Parse transcript for tool/agent activity    │   │
│  │  - Compute context health                       │   │
│  │  - Render statusline output                     │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↓ stdout                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Opus] │ my-project git:(main*)                 │   │
│  │ Context █████░░░░░ 45% │ Usage ██░░░░░░░ 25%   │   │
│  │ ◐ Edit: auth.ts | ✓ Read ×3 | ✓ Grep ×2        │   │
│  │ ◐ explore [haiku]: Finding auth code (2m 15s)  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 核心功能拆解

### 功能 1：多层级 Context 健康度

| 指标 | 含义 | 行动 |
|------|------|------|
| Context Bar | 当前 Context 使用 % | 超过 80% 考虑 `/clear` 或重开会话 |
| Usage Rate | 速率限制（1h 30m / 5h）| 接近上限时降低任务复杂度 |

### 功能 2：工具活动实时追踪

支持的工具类型：Read / Edit / Grep / Bash / WebSearch / Agent

每种工具都有执行状态（✓ 成功 / × 失败 / ◐ 进行中）和计数。

### 功能 3：Subagent 可见性

通过 `/agent` 启动的 subagent 会出现在 HUD 中，显示：
- Subagent 名称（explore / build / review 等）
- 使用的模型（[haiku] / [sonnet] 等）
- 当前任务描述
- 已运行时长

### 功能 4：Todo 进度追踪

当 Claude Code 用 `/todo` 创建任务列表时，HUD 显示：

```
▸ Fix authentication bug (2/5)
```

完成度 2/5，每完成一个自动更新。

---

## 竞品对比

| 方案 | 集成成本 | 信息完整度 | 侵入性 |
|------|----------|------------|--------|
| claude-hud | 5 行命令 | ⭐⭐⭐⭐⭐（原生数据）| 零（statusline）|
| 分屏 tmux | 高（需配置）| ⭐⭐⭐（日志回溯）| 中（占用屏幕空间）|
| 双终端 | 高（需切换）| ⭐⭐（结果查看）| 高（打断工作流）|
| 日志文件 | 无 | ⭐⭐（事后分析）| 低（但不实时）|

---

## 快速上手

```bash
# Step 1: 添加 Marketplace
/plugin marketplace add jarrodwatts/claude-hud

# Step 2: 安装插件
/plugin install claude-hud

# Step 3: 重载
/reload-plugins

# Step 4: 配置 Statusline
/claude-hud:setup
```

配置后有三个预设：
- **Full**：全部功能（工具/Agent/Todo/Git/Usage/Duration）
- **Essential**：活动行 + Git 状态，最小信息干扰
- **Minimal**：仅模型名 + Context Bar

---

## 与 OpenAI WebSocket Mode 的互补关系

claude-hud 解决的是 **Agent 运行时的可见性** 问题，而 OpenAI 的 WebSocket Mode 解决的是 **Agent 循环的延迟** 问题。两者是互补的：

| 维度 | WebSocket Mode（OpenAI）| claude-hud（Jarrod Watts）|
|------|-------------------------|--------------------------|
| **优化目标** | 基础设施延迟 | 运行时可观测性 |
| **关注者** | Agent 系统开发者 | Claude Code 用户 |
| **解决问题** | 「我的 Agent 为什么跑得慢」| 「我的 Agent 现在在做什么」|

当你同时具备低延迟（WebSocket）和高可观测性（claude-hud）时，你的 Agent 开发迭代速度会显著提升——你不仅跑得快，而且看得清。

---

**引用来源**：

> "Claude HUD uses Claude Code's native statusline API — no separate window, no tmux required, works in any terminal."
> — [jarrodwatts/claude-hud README](https://github.com/jarrodwatts/claude-hud)

> "Always visible below your input. Know exactly how full your context window is before it's too late."
> — [jarrodwatts/claude-hud README](https://github.com/jarrodwatts/claude-hud)