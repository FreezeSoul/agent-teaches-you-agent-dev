# 更新历史

> 每轮 Cron 执行的记录，按时间倒序排列。

## 2026-03-26 17:01（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `digest/breaking/2026-03-26-cve-2026-0756-github-kanban-mcp-rce.md` 新增——GitHub Kanban MCP Server 命令注入 RCE（CVE-2026-0756），OS Command Injection（CWE-78），位于 create_issue 函数 shell 字符串拼接；与此前 CVEs 的关键区分：经典 shell 元字符拼接，通过 GitHub issue 内容 prompt injection 触发，可横向移动至 CI/CD
- `articles/community/skill-registry-ecosystem-clawhub-composio.md` 新增——深度解读 Skill Registry Ecosystem：Skills 作为"AI 新软件包"的治理缺失问题、三大注册表（ClawHub / Agent Skills / JFrog Agent Skills Registry）横向对比、Skills 与 MCP 生态位差异分析；JFrog 判断框架：Skills = 2010 年代开源包；Cisco DefenseClaw 同时扫描 Skills + MCP Servers
- `digest/weekly/2026-W14.md` 更新——新增 CVE-2026-0756 条目 + Skill Registry Ecosystem 条目 + 本周数据更新
- `README.md` 更新——badge 时间戳 + Skill 章节新增 Skill Registry Ecosystem 条目

**Articles 产出**：1 篇（Skill Registry Ecosystem ClawHub Composio）

**重大变更**：无新框架目录

**本轮反思**：
- 做对了：准确识别 CVE-2026-0756 与此前 MCP CVEs 的本质区别（命令注入类型不同），而非简单并列；Skill Registry 角度选用了 JFrog "Skills = 新开源包" 判断框架，形成清晰的知识结构
- 需改进：DefenseClaw GitHub 明日（3/27）才开源，本轮只能记录为 PENDING；CVE-2026-0756 披露于 1/9，属"旧闻"级别，是否归并至 MCP Security Crisis 文章待下轮决策

<!-- INSERT_HISTORY_HERE -->

## 2026-03-26 11:01（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `digest/breaking/2026-03-26-cve-2026-3918-chrome-webmcp-use-after-free.md` 新增——Chrome WebMCP Use-After-Free RCE（CVE-2026-3918），内存安全漏洞，影响 Chrome < 146.0.7680.71；这是 MCP 生态中首个浏览器级 RCE（区别于此前的 MCP Server 命令注入漏洞）
- `articles/community/agent-protocol-stack-mcp-a2a-a2ui.md` 新增——深度解读 MCP + A2A + A2UI 三层协议栈叠加架构：职责矩阵、组合工作流示例、三大结构性缺口（身份模型/可观测性/错误传播）、安全攻击面分析；参考 Subhadip Mitra "TCP/IP Moment" 框架；评分 16/20
- `digest/weekly/2026-W14.md` 更新——新增 CVE-2026-3918 WebMCP 条目 + Agent Protocol Stack 条目 + 本周关注更新 + 本周数据更新
- `README.md` 更新——badge 时间戳 + Orchestration 章节新增 Agent Protocol Stack 条目

**Articles 产出**：1 篇（Agent Protocol Stack MCP A2A A2UI）

**重大变更**：无新框架目录

**本轮反思**：
- 做对了：发现了 WebMCP CVE（CVE-2026-3918），补充了 MCP 生态从 Server 漏洞到浏览器级漏洞的完整图谱；Agent Protocol Stack 是演进链中的重要概念（三层协议叠加），填补了 Orchestration 章节对 A2A/MCP 组合深度的不足
- 需改进：部分优质文章（subhadipmitra.com）使用代理 web_fetch 失败，需记录此源需要使用 agent-browser 方式访问



## 2026-03-26 05:01（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/community/mcp-security-crisis-30-cves-60-days.md` 新增——深度解读 MCP 安全危机：30 CVEs 60 天、38% 服务器零认证、43% 命令注入、CVSS 9.1 的 MCPwnluence RCE 链；评分 18/20，Harness Engineering 演进链核心补充
- `digest/breaking/2026-03-25-cve-2026-29787-mcp-memory-service-info-disclosure.md` 新增——CVE-2026-29787，mcp-memory-service < 10.21.0 信息泄露漏洞，Medium 级别，影响多 Agent 共享记忆后端
- `digest/weekly/2026-W14.md` 更新——新增 RSAC 2026 Day 4 完整 recap（Jamie Foxx 闭幕、Cisco Change Agents 四阶段演进、1Password Agent Security Platform）、MCP 30 CVEs 危机追踪、Microsoft Post-Day Forum（今日 3/26）、CVE-2026-29787 收录
- `README.md` 更新——badge 时间戳 + MCP 章节新增 MCP Security Crisis 条目 + Harness Engineering 章节新增条目

**Articles 产出**：1 篇（MCP Security Crisis 30 CVEs 60 Days）

**重大变更**：无新框架目录

**本轮反思**：
- 做对了：MCP 60 天 30 CVEs 危机是重大趋势事件，产出高质量分析文章，填补了 Harness Engineering 演进链中"MCP 协议级安全"这一重要空白
- 需改进：RSAC Day 4 官方 recap 因网站 403 无法直接获取，通过多源综合还原了主要内容

## 2026-03-25 23:01（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/community/geordie-ai-beam-context-engineering.md` 新增——深度解读 Geordie AI（RSAC 2026 Innovation Sandbox 冠军）+ Beam Context Engineering 三阶段闭环（实时行为映射 → 上下文感知评估 → 自适应修复），评 16/20
- `frameworks/microsoft-agent-framework/changelog-watch.md` 更新——新增 RC 状态完整信息（A2A + AG-UI + MCP 三协议原生支持）
- `digest/weekly/2026-W14.md` 更新——新增 RSAC Day 4 SANS keynote 追踪（Day 4 进行中）+ Beam Community 文章收录 + 本周数据更新
- `README.md` 更新——badge 时间戳 + Harness Engineering 章节新增 Geordie AI Beam 条目 + 演进链更新

**Articles 产出**：1 篇（Geordie AI Beam Context Engineering）

**重大变更**：无新框架目录

**本轮反思**：
- 做对了：发现 Geordie AI Beam 作为 Context Engineering 实践案例，适合纳入 Harness Engineering 演进链
- 需改进：RSAC Day 4 官方 recap 尚未发布（明天补充）；Microsoft Agent Framework 是 3 月发布的重要框架，需更主动监测

---

## 2026-03-25 17:01（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/engineering/microsoft-agent-framework-interview-coach.md` 新增——深度解读 Microsoft Agent Framework（Semantic Kernel + AutoGen 合并），Interview Coach 五 Agent Handoff + MCP 外置工具 + Aspire 编排生产实践
- `frameworks/microsoft-agent-framework/` 新增——overview.md + changelog-watch.md
- `frameworks/README.md` 更新——新增 Microsoft Agent Framework 表格条目 + 对比表条目
- `digest/weekly/2026-W14.md` 更新——新增 2 条框架对比全景 + RSAC Day 4 进行中
- README.md badge 时间戳更新至 17:01

**Articles 产出**：1 篇（Microsoft Agent Framework Interview Coach）

**重大变更**：新增 Microsoft Agent Framework 框架追踪

**本轮反思**：
- 做对了：本轮主动发现了 Microsoft 官方 Interview Coach 文章，深度价值高（评分 18/20），产出完整
- 需改进：框架动态追踪可以更主动（Microsoft Agent Framework 是 3 月发布的，本轮才首次发现）

---



## 2026-03-25 12:40（北京时间）

**状态**：✅ 成功

**本轮新增**：
- articles/concepts/context-engineering-for-agents.md 新增 Section 9-12（五层生产模式 + 深度对比表 + 局限性分析）
- digest/weekly/2026-W14.md 新增 3 条：Microsoft Agent Framework、MCP 2026 路线图、Context Engineering 五层模式
- README.md：更新 Context Engineering 一句话描述

**Articles 产出**：1 篇（追加至现有文章）

**重大变更**：无

**本轮反思**：
- 做对了：追加至现有文章而非创建重复内容
- 需改进：Microsoft Agent Framework 发现较晚

---

## 2026-03-25 11:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- `frameworks/langchain/changelog-watch.md` 新增 langchain-anthropic 1.4 条目：AnthropicPromptCachingMiddleware 正式发布，对 system message 和 tool definitions 应用显式缓存（Explicit Cache Control）
- `digest/weekly/2026-W14.md` 新增 2 条 DAILY_SCAN：PointGuard AI MCP Security Gateway（企业级 MCP 安全网关，与 SAFE-MCP/Agent Wall 形成三层次）、State of Context Engineering in 2026（Medium 工程实践视角）
- `resources/tools/README.md` 新增 PointGuard AI Gateway 至「MCP 安全工具」章节，与 SAFE-MCP/Agent Wall/DefenseClaw 并列

**重大变更**：无

**提交记录**：（待 git push）

---

## 2026-03-25 05:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增周报 `digest/weekly/2026-W14.md`（5条初始条目）：Geordie AI 夺冠 RSAC 2026 Innovation Sandbox、Cisco DefenseClaw 发布（3/27 GitHub）、SAFE-MCP 获 Linux Foundation + OpenID Foundation 采纳（80+ 攻击技术、MITRE ATT&CK 映射）、RSAC 2026 Agentic AI 安全峰会总结（MCPwned + OWASP ASI Top 10）、Agent Wall 开源 MCP 防火墙
- 月报 `digest/monthly/2026-03.md` 扩展至 3/25：新增 RSAC 2026（Geordie AI + DefenseClaw）、MCP CVE-per-week 趋势（连续第四周）、SAFE-MCP 采纳、Claude Opus 4.6 + LangChain 生态整理、企业 Agent 密集发布（腾讯 ClawBot、AWS+SailPoint、Microsoft Copilot Cowork、Agentforce 8亿美元 ARR）
- `frameworks/langchain/changelog-watch.md` 新增 langchain-core 1.2.22 条目：安全补丁（pypdf/tinytag 升级）+ flow_structure() 序列化器
- `frameworks/crewai/changelog-watch.md` 新增 v1.11.1 条目：补丁更新
- `resources/tools/README.md` 新增「MCP 安全工具」章节：SAFE-MCP / Agent Wall / SurePath / DefenseClaw
- README.md badge 更新至 W14，weekly 入口从 W13 切换至 W14

**提交记录**：（待 git push）

---

## 2026-03-25 00:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- W13 周报新增第 25 条：Ramp AI Index 2026年3月——Anthropic 在企业 AI 采购中首次全面超越 OpenAI

---

## 2026-03-24 23:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 Breaking News：`digest/breaking/2026-03-24-cve-2026-4198-mcp-server-auto-commit-rce.md`——CVE-2026-4198，hypermodel-labs mcp-server-auto-commit 1.0.0 命令注入 RCE，位于 getGitChanges 函数，本地攻击向量，修复 commit f7d992c8；MCP 生态本月第三起 CVE，CVE-per-week 趋势延续
- W13 周报新增第 42 条（CVE-2026-4198）和第 43 条（Switas 7大Agent突破文章），周报共43条
- .agent/ 目录全量更新（PENDING.md / REPORT.md）

**提交记录**：（待 git push）

---

## 2026-03-24 17:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 Breaking News：`digest/breaking/2026-03-24-cve-2026-2256-ms-agent-rce.md`——ModelScope MS-Agent CVE-2026-2256 命令注入 RCE 漏洞，受影响版本 v1.6.0rc1 及之前，修复版本 v1.6.0rc1+
- W13 周报新增第 39-41 条：CVE-2026-2256 MS-Agent、 CrewAI 3/24 ContextVars 补丁、LangChain 三项补丁合集
- frameworks/crewai/changelog-watch.md 新增 3/24 ContextVars 传播修复条目
- frameworks/langchain/changelog-watch.md 新增 langchain 1.2.13 / langchain-core 1.2.21 / langchain-openai 1.1.12 补丁更新

**提交记录**：（待 git push）

---

## 2026-03-24 11:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 Breaking News：`digest/breaking/2026-03-24-rsac-2026-day1-geordie-ai-defenseclaw.md`
  - RSAC 2026 Day 1 结果：Geordie AI 夺得 Innovation Sandbox "Most Innovative Startup 2026"大奖
  - Cisco DefenseClaw 开源 Agent 安全框架发布（基于 Nvidia OpenShell，3/27 GitHub 开源）
  - CrowdStrike / SentinelOne / Rubrik 等厂商 AI Agent 安全产品矩阵
- 修正 `2026-03-23-rsac-2026-agentic-ai-security.md` 中的错误：Charm Security → Geordie AI（正确 winner）

**提交记录**：`defenseclaw-commit-hash` — 🔥 Breaking: RSAC 2026 Day 1 结果 + Cisco DefenseClaw 发布

---

## 2026-03-23 23:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 Breaking News：`digest/breaking/2026-03-23-openclaw-cve-2026-25253-security-crisis.md`——OpenClaw CVE-2026-25253（CVSS 8.8）、ClawHavoc 供应链攻击，135K+ 实例暴露；系统当前版本 2026.3.13 已修复
- 新增 `frameworks/langchain/` 目录：`overview.md`（框架概览）+ `changelog-watch.md`（LangSmith Fleet 重命名 + LangChain×NVIDIA 合作）
- W13 周报新增 4 条（#35-38）：OpenClaw 安全危机、LangSmith Fleet、MCP Rise & Fall、NVIDIA 合作；周报共 38 条
- README 更新：badge 时间戳、LangChain 框架表格新增、Monthly 动态追加 4 条

**提交记录**：`8d59ba7`

---

## 2026-03-23 17:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- W13 周报新增第 28 条：**Microsoft AI Toolkit for VS Code v0.32.0**——AI Toolkit 与 Microsoft Foundry 扩展完全合并，本地/远程资源统一视图，Create Agent View 无代码入口，Foundry 侧边栏将于 6/1 退役

---

## 2026-03-23 11:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- `frameworks/crewai/changelog-watch.md` 全面重构：更新至 v1.11.0（v1.10.1→v1.11.0），补充 A2A Plus Auth、Plan-Execute 模式、gitpython CVE 修复、沙盒逃逸修复、ContextVars 跨线程传播等详细变更记录
- `digest/breaking/2026-03-23-rsac-2026-agentic-ai-security.md` 追加 Day 2 内容： Cisco "From Chatbots to Change Agents" 演讲核心观点、Microsoft AI 安全栈全层保护、Innovation Sandbox 结果待出
- `digest/weekly/2026-W13.md` 新增第 33 条（CrewAI v1.10.2a1→v1.11.0 安全与工程修复）和第 34 条（RSAC Day 2 Cisco Agent 演进路线图）

---

## 2026-03-23 10:32（北京时间）

**状态**：✅ 成功

**触发**：AWESOME_GITHUB 任务首次执行

**本轮新增**：
- `articles/community/` 新增 3 篇（best-ai-coding-agents-2026、praisonai-multi-agent-framework、hivemoot-colony-autonomous-teams）

---

## 2026-03-23 09:57（北京时间）

**状态**：✅ 成功

**触发**：FSIO diginfo.me 博客文章关键字触发（第三轮）

**本轮新增**：
- `articles/community/` 新增 4 篇（OpenClaw Architecture Deep Dive、Advanced RAG Patterns、Agentic RAG Enterprise Guide、Agent Benchmarks 2026 Guide）

---

## 2026-03-23 09:51（北京时间）

**状态**：✅ 成功

**触发**：FSIO diginfo.me 博客文章关键字触发（第二轮）

**本轮新增**：
- `articles/community/` 新增 4 篇（A2A Protocol、NVIDIA Sandbox Security Guide、Context Window Overflow、Multi-Agent Orchestration）

---

## 2026-03-23 09:49（北京时间）

**状态**：✅ 成功

**触发**：FSIO diginfo.me 博客文章关键字触发（第一轮）

**本轮新增**：
- `articles/community/` 新增 3 篇（harness-engineering-martin-fowler、7-agentic-design-patterns-mlmastery、top-claude-code-skills-composio）

---

## 2026-03-23 08:40（北京时间）

**状态**：✅ 成功

**触发**：COMMUNITY_SCAN 手工触发

**本轮新增**：
- `articles/community/` 新增 3 篇（MCP Pitfalls、Implementing MCP、MCP 全面研究）

---

## 2026-03-23 04:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 `articles/engineering/owasp-top-10-agentic-applications-2026.md`——OWASP Top 10 for Agentic Applications (2026) 完整解读
- W13 周报新增第 27 条：OWASP Top 10 for Agentic 2026 正式发布

---

## 2026-03-23 03:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 `RSAC 2026 Agentic AI 安全峰会` Breaking News（Day 1 OWASP GenAI Security Summit）

---

## 2026-03-23 02:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- `digest/breaking/2026-03-22-mcp-sdk-v127-ecosystem.md`——MCP SDK 生态 v1.27 深度解析

---

## 2026-03-22 22:01（北京时间）

**状态**：✅ 低变动周期（结构修复）

---

## 2026-03-22 21:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- W13 周报新增第 20-24 条（NVIDIA NemoClaw、Claude Code Review 多 Agent PR 审查、OpenAI Codex Security 审计、Microsoft Copilot Cowork、Google Project Mariner 重组）

---

## 2026-03-22 18:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 `USC 多智能体协同操纵` Breaking News
- 新增 `"Agents of Chaos" 论文深度解读`

---

## 2026-03-22 15:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 `Meta AI Agent Sev 1 安全事件` Breaking News
- W13 周报新增第 13-15 条

---

## 2026-03-22 13:01（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 `Claude Opus 4.6` Breaking News

---

## 2026-03-22 11:00（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 `Measuring Agent Autonomy in Practice` 文章解读

---

## 2026-03-22 10:00（北京时间）

**状态**：✅ 内容成功

**本轮新增**：
- 新增 `.agent/HISTORY.md`（本文件）
- 新增 `MemGPT 论文解读`
- 扩展技术演进时间线

---

## 2026-03-22 09:00（北京时间）

**状态**：✅ 完成

**本轮新增**：
- 首次月度回顾 `digest/monthly/2026-03.md`

---

## 2026-03-21（初始化日）

**状态**：✅ 完成

**重要里程碑**：

| 时间 | 提交 | 内容 |
|------|------|------|
| 16:21 | `3d4e921` | feat: initial commit — Agent技术知识库框架初始化 |
| 16:47 | `3357762` | feat: 完整项目结构初始化 v0.1.0 |
| 17:03 | `48bcf72` | 📚 第一波内容更新：框架对比/MCP/Memory/评测/Patterns |
| 18:36 | `bc3004e` | 📚 Anthropic 文章专题：Agent设计原则/Context Engineering/Claude Code架构 |
| 19:16 | `ed74180` | 🛠️ CrewAI/AutoGen 代码示例 + Agent避坑指南 |
| 19:33 | `6044b77` | 📚 RAG+Agent融合 + ReAct论文解读 |
| 20:25 | `d9e8b8e` | docs: 重写 README，公共技术工程风格 |

---

*由 AgentKeeper 维护 | 仅追加，不删除历史记录*
