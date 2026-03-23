# PENDING.md - 任务池

> 上次维护：2026-03-23 11:01（北京时间）
> 下次维护窗口：下次 Cron（约3小时后）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| HOT_NEWS | 每轮 | 2026-03-23 11:01 | 每次 Cron |
| DAILY_SCAN | 每天 | 2026-03-23 11:01 | 明天 2026-03-24 |
| FRAMEWORK_WATCH | 每天 | 2026-03-23 11:01 | 每天检查 |
| WEEKLY_DIGEST | 周末 | — | 2026-03-28/29 |
| COMMUNITY_SCAN | 周末 | 2026-03-23 | 2026-03-28/29 |
| MONTHLY_DIGEST | 每月25日后 | — | 2026-03-28 后 |
| CONCEPT_UPDATE | 每三天 | — | explicit |
| ENGINEERING_UPDATE | 每三天 | — | explicit |
| BREAKING_INVESTIGATE | 每三天 | — | explicit |

---

## 🔴 高频任务（每轮检查）

### HOT_NEWS · 突发/重大事件监测

| 状态 | 任务 | 备注 |
|------|------|------|
| ⏳ | RSAC 2026 Innovation Sandbox 结果 | 预计 3/23-26 宣布，需持续追踪 |
| ⏳ | RSAC 2026 Day 3/4 新议题 | 大会进行中，3/24-26 持续追踪 |

---

## 🟡 中频任务（每天检查）

### DAILY_SCAN · 每日资讯扫描

| 状态 | 任务 | 来源 | 备注 |
|------|------|------|------|
| ⏳ | 每日 Agent 技术动态 | Tavily 最近24h | 明天执行 |

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 任务 | 来源 | 备注 |
|------|------|------|------|
| ✅ | CrewAI changelog | GitHub/Changelog | 本轮已重构至 v1.11.0 |
| ⏳ | LangGraph changelog | GitHub/官方 | 每天检查 |
| ⏳ | AutoGen changelog | GitHub/官方 | 每天检查 |

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 周末（六/日）| W13 周报已有 34 条，窗口：3/28-29 |

### COMMUNITY_SCAN · 社区文章筛选

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 周末（六/日）| 本轮未执行，待周末窗口 |

---

## 🟢 低频任务（每三天/按需）

### MONTHLY_DIGEST · 月报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 每月25日后 | 当前接近窗口期（3/28+） |

### CONCEPT_UPDATE · 概念文章更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | Charles Chen "MCP is Dead; Long Live MCP!" | explicit |
| ⏳ | A2A Protocol 深度文章 | explicit |

### ENGINEERING_UPDATE · 工程实践更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | OpenAI Agents SDK vs Anthropic MCP | explicit |

### BREAKING_INVESTIGATE · breaking 深度调查

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | MCPwned 漏洞深度分析 | explicit（RSAC Day 1 已收录） |

---

## ⚠️ 待决策

| 事项 | 优先级 | 状态 |
|------|--------|------|
| 中文社区抓取方案优化（知乎需JS渲染）| 中 | ⏳ 待优化 |
| RSAC Innovation Sandbox 结果收录 | 高 | ⏳ 等待宣布（大会 3/23-26） |

---

*由 AgentKeeper 维护 | 2026-03-23 11:01 北京时间*
