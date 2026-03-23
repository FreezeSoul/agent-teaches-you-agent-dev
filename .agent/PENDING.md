# PENDING.md - 任务池

> 上次维护：2026-03-23 08:14（北京时间）
> 下次维护窗口：2026-03-28（周末）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| HOT_NEWS | 有就处理 | 2026-03-23 | 每次 Cron |
| WEEKLY_DIGEST | 周末（六/日）| — | 2026-03-28/29 |
| MONTHLY_DIGEST | 每月25日后 | — | 2026-03-28 后 |
| FRAMEWORK_WATCH | 每周一 | — | 每周一 |
| COMMUNITY_SCAN | 周末（六/日）| — | 2026-03-28/29 |
| CONCEPT_UPDATE | 按需 | — | explicit |
| ENGINEERING_UPDATE | 按需 | — | explicit |
| BREAKING_INVESTIGATE | 按需 | — | explicit |

---

## 🔴 高频任务（每次Cron检查）

### HOT_NEWS · 突发/重大事件监测

| 状态 | 任务 | 备注 |
|------|------|------|
| ⏳ | RSAC 2026 Day 2 追踪 | Innovation Sandbox 结果待出 |

---

## 🟡 中频任务（按日历窗口执行）

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 周末 | 本周 breaking ≥ 3 条时生成 |

### MONTHLY_DIGEST · 月报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 每月25日后 | 当前接近窗口期（3月28日后）|

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 每周一 | LangGraph / CrewAI / AutoGen |

### COMMUNITY_SCAN · 社区文章筛选

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 周末 | 英文 Tavily + 中文 agent-browser（待启用）|

---

## 🟢 低频任务（explicit trigger 执行）

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | Charles Chen "MCP is Dead; Long Live MCP!" | explicit |
| ⏳ | A2A Protocol 深度文章 | explicit |
| ⏳ | OpenAI Agents SDK vs Anthropic MCP | explicit |

---

## ⚠️ 待决策

| 事项 | 优先级 | 状态 |
|------|--------|------|
| 中文社区（知乎/B站）纳入 COMMUNITY_SCAN | 高 | ⏳ 待 FSIO 确认 |

---

*由 AgentKeeper 维护 | 2026-03-23 08:14 北京时间*
