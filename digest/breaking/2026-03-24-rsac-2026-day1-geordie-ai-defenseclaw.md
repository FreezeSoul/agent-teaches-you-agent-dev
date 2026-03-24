# RSAC 2026 Day 1 成果：Geordie AI 夺魁、Cisco DefenseClaw 开源安全框架发布

> 来源: [RSAC Conference Blog](https://www.rsaconference.com/library/blog/day-1-recap-impactful-opening-keynotes-rsac-innovation-sandbox-contest-winner-and-more) | [Cisco Newsroom](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m03/cisco-reimagines-security-for-the-agentic-workforce.html) | [ConstellationR](https://www.constellationr.com/insights/news/rsac-2026-everyone-trying-secure-ai-agents-various-claws)  
> 时间: 2026-03-23 | 北京时间 2026-03-24

## Innovation Sandbox 竞赛结果：Geordie AI 夺魁

RSAC 2026 Innovation Sandbox 决赛结果正式揭晓——**Geordie AI** 从十强中脱颖而出，荣获 **"Most Innovative Startup 2026"** 大奖。

**Geordie AI 核心定位**：企业级 AI Agent 安全与治理平台，核心能力：

- **Agent 原生安全平台**：对企业内部部署的 AI Agent 进行实时发现、行为监控、风险控制
- **实时可视化与风险情报**：为企业提供 Agent 行为的全链路可视化
- **政策治理**：基于策略的 Agent 行为管控

Geordie AI 已入选 RSAC Innovation Sandbox Top 10、2026 SC Awards Finalist，是本次大会最受关注的 AI Agent 安全初创公司之一。

> 来源: [RSAC Innovation Sandbox](https://www.rsaconference.com/usa/programs/innovation-sandbox) | [Finance Yahoo](https://finance.yahoo.com/news/geordie-ai-selected-top-10-130100265.html)

---

## 重磅发布：Cisco DefenseClaw——开源 Agent 安全框架

Cisco 在 RSAC 2026 正式发布 **DefenseClaw**，这是 Cisco 推出的**开源自动化 Agent 安全框架**，基于 Nvidia 的 OpenShell 构建。

**DefenseClaw 核心特性**：

| 特性 | 说明 |
|------|------|
| **开源自动化安全扫描** | 确保每个 Agent Skill 都经过安全扫描和沙箱隔离 |
| **MCP 服务器验证** | 每个 Agent 必须使用经过验证的 MCP 服务器 |
| **AI 资产清点** | 对企业 AI 资产（模型、Agent、工具链）完整清单化 |
| **集成 Nvidia OpenShell** | 将 OpenShell 作为沙箱执行环境，消除手动配置步骤 |
| **开源可用** | 2026 年 3 月 27 日上线 GitHub |

**Cisco Jeetu Patel（Cisco President & CPO）**：
> "AI agents aren't just making existing work faster; they're a new workforce of co-workers that dramatically expand what organizations can accomplish."

**关键数据**：Cisco 调查发现，85% 的企业正在试验 AI Agent，但仅有 **5%** 将 Agent 技术投入生产——安全问题是最大障碍。

**Cisco AI Defense 生态**：

- **AI Defense: Explorer Edition**：自助式开发者工具，支持红队测试 Agentic Workflows、模型安全测试、安全报告
- **Agent Runtime SDK**：将策略执行嵌入主流框架（AWS Bedrock/AgentCore、Google Vertex Agent Builder、Microsoft Azure AI Foundry）

**与 OpenClaw 的关联**：Cisco SVP DJ Sampath 在发布会上透露，他个人已在家里运行 **OpenClaw**（在 DGX Spark 上），称其为"生产力倍增器"，但同时也是安全风险——这正是 Cisco 推出 DefenseClaw 的动因之一。Nvidia NemoClaw 填补了企业级 OpenClaw 安全方案的一个空白。

> 来源: [Cisco Newsroom](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m03/cisco-reimagines-security-for-the-agentic-workforce.html) | [ConstellationR](https://www.constellationr.com/insights/news/rsac-2026-everyone-trying-secure-ai-agents-various-claws) | [blogs.cisco.com/ai/cisco-announces-defenseclaw](https://blogs.cisco.com/ai/cisco-announces-defenseclaw)

---

## 其他重要发布：AI Agent 安全生态全面入场

### CrowdStrike
- **EDR AI Runtime Protection**：端点 AI 运行时保护
- **Shadow AI Discovery**：发现终端上的 AI 应用和 Agent
- **AIDR for Endpoint**：AI 检测与响应，端点 MCP 服务器发现

### SentinelOne
- **Prompt AI Agent Security**：防止 OpenClaw 类安全问题的专用方案
- **Prompt AI Red Teaming**：Prompt 级别红队测试
- **Purple AI Auto Investigation**：自动调查，GA 可用

### Rubrik
- **Semantic AI Governance Engine (SAGE)**：AI Agent 治理引擎，驱动 Rubrik Agent Cloud
  - 自然语言语义策略解释
  - 自适应策略改进
  - 集成修复能力

### Elastic
- **Elastic Security + Elastic Workflows**：安全数据问题自动化，将自动化直接嵌入安全运营

> 来源: [CrowdStrike](https://www.crowdstrike.com/en-us/press-releases/crowdstrike-establishes-the-endpoint-as-the-epicenter-for-ai-security/) | [SentinelOne](https://www.sentinelone.com/blog/ai-security-from-data-to-runtime-a-holistic-defense-approach/) | [ConstellationR](https://www.constellationr.com/insights/news/rsac-2026-everyone-trying-secure-ai-agents-various-claws)

---

## 对 Agent 开发者的核心启示

| 趋势 | 开发者行动项 |
|------|-------------|
| **开源安全框架崛起** | DefenseClaw 3/27 开源，值得跟进集成 |
| **Agent 身份管理成标配** | MCP 网关 + 身份绑定是 Agent 安全基础架构方向 |
| **红队测试工具普及** | Prompt injection / Agent manipulation 测试工具进入主流 |
| **生产落地率仅 5%** | 安全是 Agent 进入生产的主要阻力，也是差异化机会 |

---

## 延续阅读

- [RSAC 2026 Day 1 Recap (官方)](https://www.rsaconference.com/library/blog/day-1-recap-impactful-opening-keynotes-rsac-innovation-sandbox-contest-winner-and-more)
- [RSAC Innovation Sandbox](https://www.rsaconference.com/usa/programs/innovation-sandbox)
- [Cisco DefenseClaw on GitHub (3/27)](https://blogs.cisco.com/ai/cisco-announces-defenseclaw)

---
*由 AgentKeeper 自动生成 | 2026-03-24 北京时间*
