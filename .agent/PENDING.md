# PENDING.md - 任务池

> 上次维护：2026-03-23 23:01（北京时间）
> 下次维护窗口：下次 Cron（约6小时后，2026-03-24 17:01）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| HOT_NEWS | 每轮 | 2026-03-24 11:01 | 每次 Cron |
| DAILY_SCAN | 每天 | 2026-03-23 11:01 | 明天 2026-03-25 |
| FRAMEWORK_WATCH | 每天 | 2026-03-23 23:01 | 明天检查 |
| WEEKLY_DIGEST | 周末 | — | 2026-03-28/29（W14） |
| COMMUNITY_SCAN | 周末 | 2026-03-23 | 2026-03-28/29 |
| MONTHLY_DIGEST | 每月25日后 | — | 2026-03-28+ |
| CONCEPT_UPDATE | 每三天 | — | explicit |
| ENGINEERING_UPDATE | 每三天 | — | explicit |
| BREAKING_INVESTIGATE | 每三天 | — | explicit |

---

## 🔴 高频任务（每轮检查）

### HOT_NEWS · 突发/重大事件监测

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | RSAC 2026 Day 1：Geordie AI 夺魁、Cisco DefenseClaw 发布 | 本轮完成 |
| ⏳ | RSAC 2026 Day 2/3/4 | 大会 3/26 结束，持续追踪 |
| ⏳ | DefenseClaw 3/27 GitHub 开源 | 高优先级，跟进深度分析 |

---

## 🟡 中频任务（每天检查）

### DAILY_SCAN · 每日资讯扫描

| 状态 | 任务 | 来源 | 备注 |
|------|------|------|------|
| ⏳ | 每日 Agent 技术动态 | Tavily 最近24h | 明天执行 |

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 任务 | 来源 | 备注 |
|------|------|------|------|
| ⏳ | LangChain / CrewAI / AutoGen | GitHub releases | 明天检查 |

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 周末（六/日）| W14 周报生成，W13 已有 38 条 |

### COMMUNITY_SCAN · 社区文章筛选

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 周末（六/日）| 待周末窗口 |

---

## 🟢 低频任务（每三天/按需）

### MONTHLY_DIGEST · 月报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 每月25日后 | 当前在窗口期（3/25+） |

### CONCEPT_UPDATE · 概念文章更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | A2A Protocol 深度文章 | explicit（本轮发现多篇相关社区文章）|
| ⏳ | Charles Chen "MCP is Dead; Long Live MCP!" | explicit |
| ⏳ | MCP "Rise and Relative Fall" (Andrew Baker) | explicit |

### ENGINEERING_UPDATE · 工程实践更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | OpenAI Agents SDK vs Anthropic MCP 对比 | explicit |

### BREAKING_INVESTIGATE · breaking 深度调查

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | DefenseClaw 技术细节（3/27 开源后）| 3/27 explicit |
| ⏳ | OpenClaw CVE-2026-25253 技术细节 | explicit |
| ⏳ | MCPwned 漏洞深度分析 | explicit |

---

## ⚠️ 待决策

| 事项 | 优先级 | 状态 |
|------|--------|------|
| RSAC 2026 Day 2+ 追踪方案（securityboulevard 被 block）| 高 | ⏳ agent_browser 待验证 |
| A2A Protocol 独立成篇 | 中 | ⏳ 评估中 |
| DefenseClaw 开源后深度跟进 | 高 | ⏳ 3/27 触发 |
| W14 周报结构优化 | 中 | ⏳ 周末前评估 |

---

*由 AgentKeeper 维护 | 2026-03-24 11:01 北京时间*
