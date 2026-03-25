# 更新历史

> 每轮 Cron 执行的记录，按时间倒序排列。

<!-- INSERT_HISTORY_HERE -->

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
