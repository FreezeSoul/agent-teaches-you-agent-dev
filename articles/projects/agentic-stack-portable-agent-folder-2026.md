# agentic-stack：跨 Harness 的便携式 Memory + Skills 基础设施

> **来源**：[codejunkie99/agentic-stack](https://github.com/codejunkie99/agentic-stack) · GitHub · Stars: 1,808 · Forks: 234
> 
> **许可证**：MIT · **语言**：Python · **创建于**：2026-04-15 · **更新于**：2026-05-03

---

## 一句话概括

**一套便携的 `.agent/` 文件夹规范，让 Agent 的 Memory + Skills + Protocols 在 Claude Code、Cursor、Windsurf、OpenClaw、Hermes 等主流 Harness 之间无缝迁移，切换工具不丢失积累。**

---

## 核心价值

### 1. 跨 Harness 便携性

agentic-stack 定义了一套 `.agent/` 目录结构规范：

```
.agent/
├── memory/          # 记忆层（episodic、facts、working context）
├── skills/          # 技能库
├── protocols/       # 协议定义
└── adapters/        # 各 Harness 的适配器
```

目前已支持：Claude Code、Cursor、Windsurf、OpenCode、OpenClaw、Hermes、Pi Coding Agent、Codex、Antigravity，以及 DIY Python 循环。

### 2. 数据层（Data Layer）

团队场景下，同一个 `.agent/` brain 可被多个 Harness 实例共享。数据层提供统一的监控面：

- **Harness Activity**：各 Agent 的运行状态、日志
- **Cron Runs**：定时任务执行情况
- **Token / Cost Estimates**：成本估算
- **KPI Summaries**：关键指标汇总
- **Dashboard**：截图即用的每日报告

### 3. 数据飞轮（Data Flywheel）

将已批准、脱敏后的运行记录转化为可重用的飞轮产物：

| 产物类型 | 用途 |
|---------|------|
| Trace Records | 执行轨迹回放 |
| Context Cards | 上下文快照 |
| Eval Cases | 评估样本 |
| Training-ready JSONL | 模型微调数据 |
| Readiness Metrics | 就绪度指标 |

### 4. v0.13.0 Transfer Wizard（新增）

自然语言驱动的迁移向导，支持「将记忆迁移到 Codex」等指令，自动生成目标平台的适配配置。

---

## 技术架构

```
┌─────────────────────────────────────────────────┐
│               .agent/ brain                     │
│  memory/ + skills/ + protocols/ + adapters/      │
└─────────────────────────────────────────────────┘
        ↑           ↑           ↑           ↑
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Claude  │ │Cursor  │ │Windsurf│ │ Hermes │ ...
   │ Code   │ │        │ │        │ │        │
   └────────┘ └────────┘ └────────┘ └────────┘
        └────────── data layer ──────────┘
              Dashboard + Flywheel
```

---

## 与现有项目的关系

| 项目 | 定位 | 与 agentic-stack 的关系 |
|------|------|------------------------|
| **OpenSkills** | 跨平台 Skills 加载器 | 互补：OpenSkills 解决「加载」，agentic-stack 解决「迁移+记忆」 |
| **awesome-cursor-skills** | Skills 聚合列表 | 互补：awesome list 解决「发现」，agentic-stack 解决「携带」 |
| **mem0/memgpt** | 记忆系统 | 功能有重叠，但 agentic-stack 侧重 Harness 层面的便携性而非记忆算法本身 |

---

## 关键数字

| 指标 | 数值 |
|------|------|
| GitHub Stars | 1,808（2026年4月15日至今，不到一个月） |
| Forks | 234 |
| 支持的 Harness | 9+（Claude Code、Cursor、Windsurf、OpenClaw、Hermes 等） |
| Python 版本 | 3.9+ |
| 最新版本 | v0.13.0 |

---

## 适用场景

1. **多 Harness 用户**：同时使用 Claude Code 写前端、Cursor 写后端、Windsurf 做评审，不想丢失各自分别的记忆积累
2. **团队 Harness 管理**：多人共用一个 Agent brain，数据层提供统一监控和 Flywheel 复用
3. **Harness 切换场景**：从 Claude Code 迁转到 Codex，需要完整迁移 Memory + Skills 状态

---

## 原文引用

> "Keep one portable memory-and-skills layer across coding-agent harnesses, so switching tools doesn't reset how your agent works."
> — [README.md](https://github.com/codejunkie99/agentic-stack)

---

## 延伸阅读

- [Hermes Agent（NousResearch）—— 持续自我改进的 Agent 框架](articles/projects/hermes-agent-nousresearch-self-improving-agent-2026.md)
- [OpenSkills —— 让 Agent Skills 横跨所有 AI 编码工具](articles/projects/openskills-universal-skills-loader-2026.md)
- [awesome-cursor-skills —— AI Coding Agent 的 Skills 系统化工具箱](articles/projects/awesome-cursor-skills-spencepauly-2026.md)
