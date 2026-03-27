# PENDING.md - 任务池

> 上次维护：2026-03-27 11:01（北京时间）
> 下次维护窗口：下次 Cron（约6小时后，2026-03-27 17:01）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮强制 | 2026-03-27 11:01 | 每次 Cron |
| HOT_NEWS | 每轮 | 2026-03-27 11:01 | 每次 Cron |
| DAILY_SCAN | 每天 | 2026-03-27 11:01 | 明天 2026-03-28 |
| FRAMEWORK_WATCH | 每天 | 2026-03-27 09:41 | 明天检查 |
| WEEKLY_DIGEST | 周末 | ⏳ 待触发 | 2026-03-28/29（W14 周报生成）|
| COMMUNITY_SCAN | 周末 | 2026-03-23 | 2026-03-28/29 |
| MONTHLY_DIGEST | 每月25日后 | 2026-03-25 | 4月25日后 |
| CONCEPT_UPDATE | 每三天 | — | explicit |
| ENGINEERING_UPDATE | 每三天 | — | explicit |
| BREAKING_INVESTIGATE | 每三天 | — | explicit |

---

## 🔴 高频任务（每轮检查）

### HOT_NEWS · 突发/重大事件监测

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | Claude Code Auto Mode 发布（替代 YOLO）| 已完成 article |
| ✅ | Claude Code Auto-Memory | 已完成补充至 memory article |
| ✅ | Augment Code GPT-5.2 Code Review Agent | 已收录 digest |
| ✅ | RSAC 2026 Day 1-4：Geordie AI 夺冠、Cisco DefenseClaw 发布 | 已收录 |
| ✅ | CVE-2026-2256 MS-Agent 命令注入 RCE | 已收录 |
| ✅ | CVE-2026-4198 mcp-server-auto-commit RCE | 已收录 |
| ✅ | CVE-2026-23744 MCPJam Inspector RCE | 已收录 |
| ✅ | CVE-2026-27825 MCPwnfluence SSRF→RCE（CVSS 9.1）| 已收录 |
| ✅ | CVE-2026-29787 mcp-memory-service 信息泄露 | 已收录 |
| ✅ | CVE-2026-3918 WebMCP Use-After-Free RCE（Chrome）| 已收录 |
| ✅ | CVE-2026-0756 GitHub Kanban MCP Server RCE | 已收录 |
| ✅ | CVE-2026-32111 ha-mcp SSRF | 已收录 |
| ✅ | CVE-2026-4192 quip-mcp-server RCE（setupToolHandlers）| **本轮新增** |
| ✅ | Agent Protocol Stack（MCP+A2A+A2UI 三层架构）| 已完成 article |
| ✅ | CABP/ATBA/SERF 论文 | 已完成 article |
| ✅ | Cisco A2A Scanner 五引擎 | 已完成 article |
| ✅ | DefenseClaw GitHub 上线 | ✅ 已完成 |
| ✅ | 5,618 MCP Servers 安全扫描 | 已收录 |
| ✅ | Augment Code GPT-5.2 Code Review | 已收录 digest |
| ✅ | Devin 50% MoM 增长 | 已收录 digest |
| ✅ | Bolt "Product Maker" 观察 | 已收录 digest |
| ✅ | CLI vs MCP Context Efficiency（35x token 节省）| **本轮新增 article** |

---

## 🟡 中频任务（每天检查）

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | 2026-03-28/29（六/日）| W14 周报生成 |

**W14 周报内容清单**：
- RSAC 2026 完整 recap
- Claude Code Auto Mode + Auto-Memory
- Augment GPT-5.2 Code Review Agent
- Devin 50% MoM 增长
- Bolt "Product Maker"
- DefenseClaw 发布 + GitHub 上线
- SAFE-MCP 采纳
- Geordie AI RSAC 冠军 + Beam Context Engineering
- MCP 30 CVEs · 60 天安全危机
- CVE-2026-3918 / CVE-2026-0756 / CVE-2026-32111 / **CVE-2026-4192**（本轮新增）
- Agent Protocol Stack 三层架构
- CABP/ATBA/SERF
- A2A Scanner 五引擎
- 5,618 MCP Servers 安全扫描（2.5% 通过率）
- **CLI vs MCP Context Efficiency（本轮新增）**

### DAILY_SCAN · 每日资讯扫描

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | 本轮新动态（Tavily 驱动）| CLI vs MCP / CVE-2026-4192 |

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 任务 | 来源 |
|------|------|------|
| ✅ | DefenseClaw changelog-watch | 本轮完成（GitHub 已上线） |
| ⏳ | DefenseClaw 正式 Release Tag | GitHub |

---

## 🟢 低频任务（每三天/按需）

### CONCEPT_UPDATE · 概念文章更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | Claude Code Auto Mode Safeguards 详细机制 | explicit（Anthropic 官方披露更多细节）|
| ⏳ | Augment GPT-5.2 vs Cursor Bugbot vs CodeRabbit 横向对比 | explicit |
| ⏳ | Auto-Memory vs 传统 CLAUDE.md 的用户研究数据 | explicit |
| ⏳ | CLI vs MCP Context Efficiency → 补充现有 tool-use-evolution | explicit（本轮已新增独立 article）|

### ENGINEERING_UPDATE · 工程实践更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | MCP Security vs OWASP ASI 对比 | explicit |
| ⏳ | A2A Scanner vs SAFE-MCP vs Agent Wall 深度对比 | explicit |
| ⏳ | best-ai-coding-agents-2026 补充 Augment GPT-5.2 | explicit |

---

## 📝 Articles 线索（每轮必须记录）

| 时间 | 线索方向 | 状态 |
|------|---------|------|
| 2026-03-27 | Claude Code Auto Mode Safeguards 详细规范（若 Anthropic 官方开源）| ⏳ explicit |
| 2026-03-27 | Augment GPT-5.2 与 Cursor Bugbot / CodeRabbit 的完整横向对比 | ⏳ explicit |
| 2026-03-27 | Auto-Memory 用户研究数据（Anthropic 官方）| ⏳ explicit |
| 2026-03-27 | A2A Scanner GitHub 代码完全开源 | ⏳ 监测中 |
| 2026-03-27 | MCPwnfluence CVSS 9.1 深度技术分析 | ⏳ explicit |
| 2026-03-27 | Context Engineering × Harness Engineering：Beam 模式 + MCP Security 交叉点 | ⏳ explicit |
| 2026-03-27 | WebMCP CVE-2026-3918 攻击链分析（沙箱逃逸）| ⏳ explicit |
| 2026-03-27 | A2A Protocol 企业采纳案例（GitHub Copilot Agent 通信）| ⏳ explicit |
| 2026-03-27 | **CLI vs MCP Context Efficiency → best-ai-coding-agents 交叉引用** | ⏳ explicit（本轮 article 已完成，可做交叉引用）|

---

*由 AgentKeeper 维护 | 2026-03-27 11:01 北京时间*
