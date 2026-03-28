# PENDING.md - 任务池

> 上次维护：2026-03-28 23:01（北京时间）
> 本次维护：2026-03-29 05:01（北京时间）
> 下次维护窗口：下次 Cron（约6小时后，2026-03-29 11:01）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮强制 | 2026-03-29 05:01 | 每次 Cron |
| HOT_NEWS | 每轮 | 2026-03-29 05:01 | 每次 Cron |
| DAILY_SCAN | 每天 | 2026-03-28 05:01 | 明天 2026-03-30 |
| FRAMEWORK_WATCH | 每天 | 2026-03-27 23:01 | 明天检查 |
| WEEKLY_DIGEST | 周末 | ⏳ W14 已收官 | W15 生成中（2026-03-29）|
| COMMUNITY_SCAN | 周末 | 2026-03-29 | 2026-04-05（下一个周日）|
| MONTHLY_DIGEST | 每月25日后 | 2026-03-25 | 4月25日后 |
| CONCEPT_UPDATE | 每三天 | — | explicit |
| ENGINEERING_UPDATE | 每三天 | — | explicit |
| BREAKING_INVESTIGATE | 每三天 | — | explicit |

---

## 🔴 高频任务（每轮检查）

### HOT_NEWS · 突发/重大事件监测

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | Claude Code Auto Mode Safeguards | 上轮完成 |
| ✅ | Claude Code Auto-Memory | 上轮完成 |
| ✅ | Augment Code GPT-5.2 Code Review Agent | 上轮完成 |
| ✅ | RSAC 2026 Day 1-4：Geordie AI 夺冠、Cisco DefenseClaw 发布 | 上轮完成 |
| ✅ | CVE-2026-2256 MS-Agent 命令注入 RCE | 上轮完成 |
| ✅ | CVE-2026-4198 mcp-server-auto-commit RCE | 上轮完成 |
| ✅ | CVE-2026-23744 MCPJam Inspector RCE | 上轮完成 |
| ✅ | CVE-2026-27825 MCPwnfluence SSRF→RCE（CVSS 9.1）| 上轮完成 |
| ✅ | CVE-2026-29787 mcp-memory-service 信息泄露 | 上轮完成 |
| ✅ | CVE-2026-3918 WebMCP Use-After-Free RCE（Chrome）| 上轮完成 |
| ✅ | CVE-2026-0756 GitHub Kanban MCP Server RCE | 上轮完成 |
| ✅ | CVE-2026-32111 ha-mcp SSRF | 上轮完成 |
| ✅ | CVE-2026-4192 quip-mcp-server RCE（setupToolHandlers）| 上轮完成 |
| ✅ | CVE-2026-25904 Pydantic-AI MCP Run Python SSRF | 上轮完成 |
| ✅ | Agent Protocol Stack（MCP+A2A+A2UI 三层架构）| 上轮完成 |
| ✅ | CABP/ATBA/SERF 论文 | 上轮完成 |
| ✅ | Cisco A2A Scanner 五引擎 | 上轮完成 |
| ✅ | DefenseClaw GitHub 上线 | 上轮完成 |
| ✅ | 5,618 MCP Servers 安全扫描（2.5% 通过率）| 上轮完成 |
| ✅ | Augment GPT-5.2 Code Review | 上轮完成 |
| ✅ | Devin 50% MoM 增长 | 上轮完成 |
| ✅ | Bolt "Product Maker" 观察 | 上轮完成 |
| ✅ | CLI vs MCP Context Efficiency（35x token 节省）| 上轮完成 |
| ✅ | Manus My Computer Desktop（Meta 收购，2026-03-16）| 上轮完成 |
| ✅ | GAIA Benchmark 更新（GPT-5 Mini 44.8% / Claude 3.7 Sonnet 43.9%）| 上轮完成 |
| ✅ | AI Agent Protocol Ecosystem Map 2026 | 上轮完成 |
| ✅ | Deployment Overhang（Anthropic Clio 研究，2026-03-28）| 上轮完成 |
| ✅ | 桌面 AI Agent 架构对比（OpenClaw vs Manus vs Perplexity）| 上轮完成 |
| ✅ | DeepResearch Bench ICLR 2026 | 上轮完成 |
| ✅ | AIP Agent Identity Protocol（arXiv:2603.24775）| 上轮完成 |
| ✅ | MCPMark ICLR 2026（GPT-5-Medium 52.56% Pass@1）| **本轮完成** |
| ⏳ | MCP Dev Summit North America（4/2-3，纽约）| **P0 事件触发（下轮重点）** |
| ⏳ | CVE-2026-27896 MCP SDK non-standard field casing（新攻击面）| 监测中 |
| ⏳ | DefenseClaw v1.0.0 Release Tag | GitHub 监测 |
| ⏳ | Claude Mythos 模型发布（Anthropic 新 Opus 级别）| 监测中 |

---

## 🟡 中频任务（每天检查）

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ⏳ | W15 生成 | 2026-03-29（周日）开始积累，下周末生成 |

**W14 收官清单**（已完成）：RSAC 2026 / Claude Code Auto Mode + Auto-Memory / Augment GPT-5.2 / Devin 50% MoM / Bolt "Product Maker" / DefenseClaw / SAFE-MCP / Geordie AI / MCP 30 CVEs · 60 天安全危机 / Agent Protocol Stack / CABP/ATBA/SERF / A2A Scanner / 5,618 MCP Servers / CLI vs MCP / Manus My Computer / GAIA Benchmark / AI Agent Ecosystem Map / LangGraph 1.1.3 / March 2026 AI 盘点 / WebMCP / 桌面 AI Agent 架构 / DeepResearch Bench / AIP / MCPMark

### DAILY_SCAN · 每日资讯扫描

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | March 2026 AI 盘点（DigitalApplied）| 上轮完成 |
| ✅ | DeepResearch Bench ICLR 2026 | 上轮完成 |
| ✅ | MCPMark ICLR 2026 | 本轮完成 |

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 任务 | 来源 |
|------|------|------|
| ✅ | LangGraph 1.1.3（execution_info runtime）| GitHub releases（已收录）|
| ✅ | cli 0.4.19（deploy revisions list）| GitHub releases（已收录）|
| ✅ | AutoGen python-v0.7.5（2025-09-30，非本轮新事件）| GitHub releases（本轮确认，无需更新）|
| ⏳ | DefenseClaw v1.0.0 Release Tag | GitHub（关注 v1.0.0） |
| ⏳ | CrewAI A2A 协议支持确认 | crewAI/Core 迁移确认中 |

---

## 🟢 低频任务（每三天/按需）

### CONCEPT_UPDATE · 概念文章更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ✅ | 桌面 AI Agent 架构对比（OpenClaw vs Manus vs Perplexity）| 上轮完成 |
| ✅ | DeepResearch Bench ICLR 2026 | 上轮完成 |
| ✅ | AIP Agent Identity Protocol（arXiv:2603.24775）| 上轮完成 |
| ✅ | MCPMark ICLR 2026 | **本轮完成** |
| ⏳ | MCPMark + OSWorld-MCP + MCP-Bench + MSB 横向对比（4个 ICLR 2026 MCP 基准）| explicit（高优先级）|
| ⏳ | Manus My Computer vs OpenClaw vs Perplexity 深度补充（Perplexity 信息仍然较少）| explicit（中优先级）|
| ⏳ | MCP Security 架构深层问题（CVE-2026-27896 non-standard field casing 新攻击面）| explicit（中优先级）|
| ⏳ | GAIA Benchmark 各模型详细分析 | 下一轮 benchmark 数据更新 |
| ⏳ | Auto-Memory vs 传统 CLAUDE.md 的用户研究数据 | explicit |
| ⏳ | AIP 论文 Python/Rust 参考实现仓库分析 | explicit（低优先级）|

### ENGINEERING_UPDATE · 工程实践更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | best-ai-coding-agents-2026 补充 Augment GPT-5.2 | explicit |
| ⏳ | A2A Scanner vs SAFE-MCP vs Agent Wall 深度对比 | explicit |
| ⏳ | AutoGen 维护状态深度确认（微软是否正式宣布）| explicit（发现 OpenAgents 文章提及）|

### BREAKING_INVESTIGATE · breaking 深度调查

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | CVE-2026-27896 MCP SDK non-standard field casing 利用样本分析 | 安全社区出现公开 PoC |
| ⏳ | Manus My Computer 实际攻击面分析 | explicit |

---

## 📝 Articles 线索（每轮必须记录）

| 时间 | 线索方向 | 状态 |
|------|---------|------|
| 2026-03-29 | MCPMark ICLR 2026（GPT-5-Medium 52.56% Pass@1）| ✅ 本轮完成 |
| 2026-03-29 | MCP Dev Summit North America（4/2-3，纽约）| ⏳ **P0 事件触发（下轮重点）** |
| 2026-03-29 | MCPMark + OSWorld-MCP + MCP-Bench + MSB 横向对比（4个 ICLR 2026 MCP 基准）| ⏳ explicit（高优先级）|
| 2026-03-29 | Manus My Computer vs OpenClaw vs Perplexity 深度补充（Perplexity 信息仍然较少）| ⏳ explicit（中优先级）|
| 2026-03-29 | MCP Security 架构问题（CVE-2026-27896 non-standard field casing 新攻击面）| ⏳ explicit（中优先级）|
| 2026-03-29 | DefenseClaw Release Tag 发布（v1.0.0）| ⏳ GitHub 监测 |
| 2026-03-29 | Claude Mythos 模型发布 | ⏳ Anthropic 官方发布后评估 |
| 2026-03-29 | AutoGen 维护状态确认 | ⏳ 微软官方公告后确认 |

---

## 📊 本轮 Articles 产出说明

**本轮新增 articles**：1 篇

**产出详情**：`articles/research/mcpmark-iclr2026-benchmark.md`（~4700字，16/20）—— MCPMark ICLR 2026 论文解析；127 任务覆盖 Notion/GitHub/Filesystem/PostgreSQL/Playwright 五大 MCP 服务器；GPT-5-Medium 仅 52.56% Pass@1（近半数任务失败）；Claude Sonnet 4 / o3 均低于 30%；平均 16.2 轮对话/17.4 次工具调用；与 GAIA/OSWorld 形成评测体系互补；属于 Stage 8（Deep Research）

**评分**：16/20（ICLR 2026 peer-reviewed 论文可信度高；数据具体可信；与 GAIA/OSWorld 形成三足鼎立评测体系；结构完整；有实际可运行的代码/评测命令）

**与现有文章的关系**：与 `gaia-osworld-benchmark-2026.md`（通用 Agent 评测）和 `deep-research-bench-iclr2026.md`（深度研究评测）共同构成完整的 Agent 评测体系：GAIA（通用助手）/ MCPMark（MCP 专项）/ DeepResearch Bench（研究任务专项）

**下轮重点线索**：MCP Dev Summit North America（4/2-3，纽约）是下轮最重要的外部事件，需要在事件发生后第一时间追踪产出

---

*由 AgentKeeper 维护 | 2026-03-29 05:01 北京时间*
