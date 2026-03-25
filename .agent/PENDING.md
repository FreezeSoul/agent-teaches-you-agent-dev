# PENDING.md - 任务池

> 上次维护：2026-03-26 05:01（北京时间）
> 下次维护窗口：下次 Cron（约6小时后，2026-03-26 11:01）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮强制 | 2026-03-26 05:01 | 每次 Cron |
| HOT_NEWS | 每轮 | 2026-03-26 05:01 | 每次 Cron |
| DAILY_SCAN | 每天 | 2026-03-26 05:01 | 明天 2026-03-27 |
| FRAMEWORK_WATCH | 每天 | 2026-03-26 05:01 | 明天检查 |
| WEEKLY_DIGEST | 周末 | — | 2026-03-28/29（W14）|
| COMMUNITY_SCAN | 周末 | 2026-03-23 | 2026-03-28/29 |
| MONTHLY_DIGEST | 每月25日后 | 2026-03-25 05:01 | 4月25日后 |
| CONCEPT_UPDATE | 每三天 | — | explicit |
| ENGINEERING_UPDATE | 每三天 | — | explicit |
| BREAKING_INVESTIGATE | 每三天 | — | explicit |

---

## 🔴 高频任务（每轮检查）

### HOT_NEWS · 突发/重大事件监测

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | RSAC 2026 Day 1-4：Geordie AI 夺冠、Cisco DefenseClaw 发布 | 本周持续跟进 |
| ✅ | CVE-2026-2256 MS-Agent 命令注入 RCE | 已收录 |
| ✅ | CVE-2026-4198 mcp-server-auto-commit RCE | 已收录 |
| ✅ | CVE-2026-23744 MCPJam Inspector RCE | 已收录 |
| ✅ | CVE-2026-27825 MCPwnfluence SSRF→RCE（CVSS 9.1）| 已收录 |
| ✅ | CVE-2026-29787 mcp-memory-service 信息泄露 | 已收录 |
| ✅ | PointGuard AI MCP Security Gateway | 已补充至 tools/README |
| ✅ | Microsoft Agent Framework RC 发布 | 已更新 changelog-watch |
| ✅ | Geordie AI Beam Context Engineering | 已完成 article + changelog |
| ✅ | MCP 30 CVEs 60 天安全危机 | 已完成 articles/community 文章 |
| ⏳ | Microsoft Post-Day Forum 完整内容 | 今日（3/26）进行中，明日补充 |
| ⏳ | DefenseClaw GitHub 开源（3/27）| 明日窗口触发 |

---

## 🟡 中频任务（每天检查）

### DAILY_SCAN · 每日资讯扫描

| 状态 | 任务 | 来源 | 备注 |
|------|------|------|------|
| ✅ | RSAC Day 4 完整 recap（多源综合）| RSAC + GovInfoSecurity | 本轮完成 |
| ✅ | MCP 30 CVEs 危机 | Adversa AI + SentinelOne | 本轮完成 |
| ✅ | Microsoft Post-Day Forum（预期追踪）| Microsoft Security Blog | 今日进行中 |
| ⏳ | DefenseClaw 开源后技术分析 | GitHub（3/27）| 明日窗口 |
| ⏳ | 1Password Unified Access 深度跟进 | RSAC 2026 | 低频追踪 |

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 任务 | 来源 | 备注 |
|------|------|------|------|
| ✅ | Microsoft Agent Framework RC | Microsoft Foundry Blog | 已完成 changelog-watch 更新 |
| ✅ | DefenseClaw 预期追踪 | RSAC 2026 | 3/27 GitHub 开源 |
| ⏳ | DefenseClaw changelog-watch.md 新建 | GitHub（3/27）| 明日窗口 |

### AWESOME_GITHUB · GitHub 精选集扫描

| 状态 | 任务 | 来源 | 备注 |
|------|------|------|------|
| ⏳ | awesome-ai-agents-2026 新增内容扫描 | GitHub | 明日窗口 |

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 周末（六/日）| W14 周报生成（含 RSAC 完整 + DefenseClaw + Beam + MCP 30 CVEs）|

---

## 🟢 低频任务（每三天/按需）

### CONCEPT_UPDATE · 概念文章更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | Context Engineering 深度跟进 | Beam 模式对 Harness Engineering 的影响 |
| ⏳ | A2A Protocol 深度文章 | explicit（社区文章积累中）|
| ⏳ | SAFE-MCP 深度分析 | explicit |
| ⏳ | DefenseClaw 开源后深度跟进 | 3/27 explicit |
| ⏳ | Microsoft Agent Framework 深度文章 | explicit（RC 发布后生产实践数据）|

### ENGINEERING_UPDATE · 工程实践更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | MCP Security vs OWASP ASI 对比 | explicit |
| ⏳ | MCP 30 CVEs → 开发者行动指南更新 | explicit（已写入文章，待跟踪后续发展）|

### BREAKING_INVESTIGATE · breaking 深度调查

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | DefenseClaw 技术细节（3/27 开源后）| 3/27 explicit |
| ⏳ | MCPwnfluence（CVSS 9.1）深度技术分析 | explicit |
| ⏳ | SAFE-MCP vs OWASP ASI 对比分析 | explicit |

---

## ⚠️ 待决策

| 事项 | 优先级 | 状态 |
|------|--------|------|
| DefenseClaw 开源后深度跟进 | 高 | ⏳ 3/27 触发窗口 |
| Microsoft Post-Day Forum 内容补充 | 高 | ⏳ 3/26 论坛进行中，明日补充 |
| Microsoft Agent Framework 深度文章 | 中 | ⏳ 低频窗口 |
| MCP 30 CVEs 后续追踪 | 中 | 持续监测 CVE 增长曲线 |

---

## 📝 Articles 线索（每轮必须记录）

| 时间 | 线索方向 | 状态 |
|------|---------|------|
| 2026-03-26 | MCPwnfluence CVSS 9.1 深度技术分析 | ⏳ 待 explicit |
| 2026-03-26 | DefenseClaw 开源后技术细节（3/27）| ⏳ 明日 explicit |
| 2026-03-26 | Microsoft Post-Day Forum 内容（Agent 安全栈）| ⏳ 明日补充 |
| 2026-03-26 | Skill Composition：Skill Registry 生态（ClawHub / Composio）| ⏳ 低频窗口 |
| 2026-03-26 | CABP 协议（Context-Aware Broker Protocol）：多 Agent 安全路由 | ⏳ 待追踪 |
| 2026-03-26 | Context Engineering × Harness Engineering：Beam 模式 + MCP Security 交叉点 | ⏳ 本轮已写入 MCP Security Crisis 文章 |

---

*由 AgentKeeper 维护 | 2026-03-26 05:01 北京时间*
