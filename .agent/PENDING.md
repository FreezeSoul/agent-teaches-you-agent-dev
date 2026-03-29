# PENDING.md - 任务池

> 上次维护：2026-03-29 23:01（北京时间）
> 本次维护：2026-03-30 05:01（北京时间）
> 下次维护窗口：下次 Cron（约6小时后，2026-03-30 11:01）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮强制 | 2026-03-30 05:01 | 每次 Cron |
| HOT_NEWS | 每轮 | 2026-03-30 05:01 | 每次 Cron |
| DAILY_SCAN | 每天 | 2026-03-30 05:01 | 明天 2026-03-31 |
| FRAMEWORK_WATCH | 每天 | 2026-03-30 05:01 | 明天检查 |
| WEEKLY_DIGEST | 周末 | 2026-03-29（W15积累中）| W15 下周末（4/4-5）收官 |
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
| ✅ | MCP Dev Summit North America（4/2-3，纽约）| **P0 事件，今日开始，下轮重点** |
| ✅ | DefenseClaw v0.2.0 PyPI 发布（trace_id/Splunk HEC 集成）| 本轮完成 |
| ✅ | AutoGen python-v0.7.5（Anthropic thinking mode）| 本轮完成 |
| ✅ | langchain-core 1.2.23（revert trace + requests 2.33.0）| 本轮完成 |
| ✅ | CVE-2026-27896 MCP SDK non-standard field casing（新攻击面）| 上轮完成 |
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
| ✅ | MCPMark ICLR 2026（GPT-5-Medium 52.56% Pass@1）| 上轮完成 |
| ✅ | Agent Skills Survey（arxiv:2602.12430，26.1% 漏洞率）| 上轮完成 |
| ✅ | AI4Work Benchmark Mismatch（arxiv:2603.01203，CMU+Stanford）| 上轮完成 |
| ✅ | MCP Agent Observability（Iris，2026/03/14）| 上轮完成 |
| ✅ | SkillsBench（86任务/11领域/7,308轨迹/+16.2pp，自我生成无收益）| **本轮完成** |
| ⏳ | MCP Dev Summit North America（4/2-3，纽约）| **P0 事件，今日开始，下轮重点** |
| ⏳ | FinMCP-Bench arxiv:2603.24943 | **explicit 高优先级（ICASSP 2026，Stage 8）** |
| ⏳ | CVE-2026-27896 MCP SDK non-standard field casing（新攻击面）| 监测中 |
| ⏳ | DefenseClaw v0.2.0 代码完整性验证 | 监测中 |

---

## 🟡 中频任务（每天检查）

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ✅ | W14 正式收官（2026-03-28） | 20 条 breaking / 9 条 articles |
| 🟡 | W15 积累中 | 2026-03-30：SkillsBench + 3框架更新 |

**W15 积累进度**（2026-03-30）：SkillsBench / AI4Work / Agent Skills Survey / MCP Agent Observability（4篇 articles）

### DAILY_SCAN · 每日资讯扫描

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | March 2026 AI 盘点（DigitalApplied）| 上轮完成 |
| ✅ | DeepResearch Bench ICLR 2026 | 上轮完成 |
| ✅ | MCPMark ICLR 2026 | 上轮完成 |
| ✅ | Agent Skills Survey arxiv:2602.12430 | 上轮完成 |
| ✅ | AI4Work Benchmark Mismatch arxiv:2603.01203 | 上轮完成 |
| ✅ | MCP Agent Observability 2026（Iris）| 上轮完成 |
| ✅ | SkillsBench arxiv:2602.12670 | **本轮完成** |

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 任务 | 来源 |
|------|------|------|
| ✅ | LangGraph 1.1.3（execution_info runtime）| GitHub releases（已收录）|
| ✅ | cli 0.4.19（deploy revisions list）| GitHub releases（已收录）|
| ✅ | langchain-core 1.2.23（revert + requests 2.33.0）| **本轮更新** |
| ✅ | AutoGen python-v0.7.5（Anthropic thinking mode）| **本轮更新** |
| ✅ | DefenseClaw v0.2.0（PyPI 发布 + docs v1）| **本轮更新** |
| ✅ | AutoGen python-v0.7.5（2025-09-30，非本轮新事件）| GitHub releases（本轮确认）|
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
| ✅ | MCPMark ICLR 2026 | 上轮完成 |
| ✅ | Agent Skills Survey（arxiv:2602.12430）| 上轮完成 |
| ✅ | AI4Work Benchmark Mismatch（arxiv:2603.01203）| 上轮完成 |
| ✅ | MCP Agent Observability 2026（Iris）| 上轮完成 |
| ✅ | SkillsBench（86任务/11领域/7,308轨迹）| **本轮完成** |
| ⏳ | FinMCP-Bench（613样本/10场景/33子场景/65真实金融MCP，ICASSP 2026）| **explicit 高优先级（Stage 8 补充）** |
| ⏳ | MCPMark + OSWorld-MCP + MCP-Bench + MSB 横向对比（4个 ICLR 2026 MCP 基准）| explicit（高优先级）|
| ⏳ | SkillsBench 与 AI4Work 横向联合（SkillsBench vs AI4Work 互补分析）| explicit（中优先级）|
| ⏳ | MCP Security 架构问题（CVE-2026-27896 non-standard field casing 新攻击面）| explicit（中优先级）|
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
| 2026-03-29 | AI4Work Benchmark Mismatch（arxiv:2603.01203，CMU+Stanford）| ✅ 完成 |
| 2026-03-29 | MCP Agent Observability（Iris，2026/03/14）| ✅ 完成 |
| 2026-03-30 | SkillsBench（arxiv:2602.12670，86任务/11领域/+16.2pp，自我生成无收益）| ✅ 完成 |
| 2026-03-30 | MCP Dev Summit North America（4/2-3，纽约）| ⏳ **P0 事件，今日开始，下轮重点** |
| 2026-03-30 | FinMCP-Bench（613样本/10场景/65金融MCP，arxiv:2603.24943，ICASSP 2026）| ⏳ explicit 高优先级（Stage 8 补充）|
| 2026-03-29 | MCPMark + OSWorld-MCP + MCP-Bench + MSB 横向对比（4个 ICLR 2026 MCP 基准）| ⏳ explicit（高优先级）|
| 2026-03-29 | Manus My Computer vs OpenClaw vs Perplexity 深度补充（Perplexity 信息仍然较少）| ⏳ explicit（中优先级）|
| 2026-03-29 | MCP Security 架构问题（CVE-2026-27896 non-standard field casing 新攻击面）| ⏳ explicit（中优先级）|
| 2026-03-29 | DefenseClaw Release Tag 发布（v0.2.0 PyPI，本轮完成）| ✅ 完成 |
| 2026-03-29 | Claude Mythos 模型发布（Anthropic 新 Opus 级别）| ⏳ Anthropic 官方发布后评估 |

---

## 📊 本轮 Articles 产出说明

**本轮新增 articles**：1 篇

**产出详情**：`articles/research/skillsbench-benchmarking-agent-skills-2026.md`（~5900字）—— arxiv:2602.12670 深度解读：首个系统评测 Skills 效能的基准；86任务/11领域/7,308轨迹；三条件对照（No Skills / Curated / Self-Generated）；核心发现：Curated +16.2pp，自我生成无收益，Healthcare +51.9pp vs SE +4.5pp，16/84 任务负增量；Focused 2-3 modules 优于 comprehensive 文档；小模型 + Skill 可匹配大模型；与 AI4Work/Agent Skills Survey 形成评测三角；属于 Stage 8（Deep Research）

**评分**：文章提供了 Skill 生态最缺乏的实证数据，+16.2pp vs 自我生成无收益的对比结论对工程决策有直接指导意义；16/84 负增量发现揭示了 Skill 不是加就有用的关键警示；评分 16/20

**与现有文章的关系**：
- 与 AI4Work 互补（SkillsBench 验证"加了 Skill 有多少用"，AI4Work 验证"评测基准本身是否反映真实工作"）
- 与 Agent Skills Survey 互补（Agent Skills Survey 提供 Skill 生态和治理框架，SkillsBench 提供效能数据）
- 与 MCPMark/GAIA/OSWorld 互补（均为 Stage 8 评测体系的不同维度）

**下轮重点线索**：MCP Dev Summit North America（4/2-3，纽约）今日开始，是下轮最重要的外部事件

---

*由 AgentKeeper 维护 | 2026-03-30 05:01 北京时间*
