# RSAC 2026：AI 安全峰会聚焦 Agentic AI 新纪元

> 来源: [RSAC Conference](https://www.rsaconference.com/library/machine-learning-artificial-intelligence) | [Security.com](https://www.security.com/expert-perspectives/rsac-2026-forecasts) | [RSAC Innovation Sandbox](https://www.rsaconference.com/library/press-release/finalists-announced-for-rsac-innovation-sandbox-contest-2026)  
> 时间: 2026-03-23

## 大会概述

RSAC 2026（RSA Conference）于 **3 月 23-26 日** 在旧金山 Moscone 中心举行，主题为"AI vs. AI: How to Reshape Defense Faster than Attackers Reshape Offense"。本次大会标志着安全行业正式进入 **Agentic AI 时代**——AI Agent 不仅是防御工具，也成为攻击目标。

## Agentic AI 核心议题

**Sessions 重点推荐**：

| 时间（PDT） | 主题 | 演讲者 |
|------------|------|--------|
| 3月23日 1:10 PM | Agentic AI 与 Increased Autonomy 的挑战 | Google Cloud、Microsoft 安全专家 |
| 3月23日 | AI vs. AI: 如何比攻击者更快重塑防御 | RSA Conference |
| 会期全程 | Microsoft AI 安全栈全层保护 + Agentic AI | Microsoft 安全团队 |

## Innovation Sandbox 焦点：Token Security

RSAC 2026 Innovation Sandbox 决赛圈出现了一个值得关注的方向：**Agentic AI 安全治理**。

**Token Security** 是十强决赛选手之一，定位为"Identity-First Security for Agentic AI"，核心能力：

- **AI Agent 生命周期治理**：发现、管理、治理每一个 AI Agent 和非人类身份（Non-Human Identity）
- **Intent-Based Access Controls**：基于意图的访问控制
- **企业级 Agent 身份管理**：管理企业环境中的非人类身份

这反映出企业安全市场正在形成的新需求：随着 AI Agent 部署规模扩大，"AI Agent 的身份与权限管理"正在成为一个独立赛道。

## 行业趋势信号

RSAC 2026 释放的关键信号：

> *"行业正从被动防御转向主动的、以 Agent 为核心的安全架构。"*

- **Cisco 主题演讲**："Reimagining Security for the Agentic Workforce"——AI Agent 以机器速度和无限规模部署，对传统安全基础架构形成挑战
- **Gartner 2026 十大战略技术趋势**：AI Security Platforms 入选
- **Microsoft**：提供覆盖 AI 栈全层的安全产品，深度集成 Agentic AI 能力

## Day 1 重磅：OWASP Top 10 for Agentic Applications 正式发布

**RSAC 2026 第一天**（3月23日），OWASP GenAI Security Summit 正式发布 **[OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)**，由 Karen Katz（OWASP Top 10 for Agentic AI Lead，SAP AI Security VP）和 Ron Del Rosario 联合主讲。

**这份清单的独特价值**：区别于传统 OWASP Top 10，这份框架专门针对 Agentic AI 系统的独特风险——自主决策、工具组合、跨会话记忆、多 Agent 协作。核心原则是最小代理权（Least Agency）：只授予 Agent 完成受限任务所需的最少自主权。

**十大风险速览**（ASI01-ASI10）：

| ID | 风险 | 核心威胁 |
|----|------|---------|
| ASI01 | Agent Goal Hijack | 通过恶意内容篡改 Agent 目标 |
| ASI02 | Tool Misuse & Exploitation | Agent 以不安全方式使用合法工具 |
| ASI03 | Identity & Privilege Abuse | Agent 滥用继承的高权限凭证 |
| ASI04 | Agentic Supply Chain Vulnerabilities | 被污染的工具/插件/MCP 服务器 |
| ASI05 | Unexpected Code Execution | Agent 不安全生成或执行代码 |
| ASI06 | Memory & Context Poisoning | 污染 RAG 数据库和 Agent 记忆 |
| ASI07 | Insecure Inter-Agent Communication | 多 Agent 系统欺骗和消息篡改 |
| ASI08 | Cascading Failures | 规划链中的小错误指数级放大 |
| ASI09 | Human-Agent Trust Exploitation | 用户对 Agent 输出过度信任 |
| ASI10 | Rogue Agents | 被入侵 Agent 在正常外表下执行有害操作 |

详细内容见专题文章：**articles/engineering/owasp-top-10-agentic-applications-2026.md**

## Day 1 重磅：MCPwned——Azure MCP 服务器 RCE 漏洞研究

Token Security 安全研究员 Ariel Simon（曾任职于以色列国防军网络部队 Unit 81）在 RSAC 2026 Day 1 演讲「**HT-R02**」，披露 **Microsoft Azure MCP 服务器的远程代码执行（RCE）漏洞**。

**漏洞概要**：
- **攻击面**：MCP 服务器作为 LLM 访问企业基础设施的桥梁，引入了新的攻击面
- **漏洞路径**：Azure MCP 服务器存在 RCE 漏洞，未认证攻击者只要有网络访问权限，即可：
  1. 在 MCP 服务器上执行任意命令
  2. 提取 Azure 凭证
  3. 完全接管受害者组织的 **Azure + Entra ID** 环境
- **根因**：MCP 采用加速，但安全控制未能同步跟上

**对 Agent 开发者的警示**：
- MCP 服务器是企业 AI Agent 的核心信任边界，一旦沦陷直接影响云环境
- 需对 MCP 服务器实施严格的**认证、授权和权限治理**
- 使用 MCP 时必须假设服务器可能被攻击者控制——最小权限原则是关键

> 来源：[Token Security 官方公告](https://www.token.security/news/token-security-researcher-to-present-mcpwned-vulnerability-research-at-rsac-2026) | RSAC 2026 Session HT-R02

---

## Day 2 重点议题（3月23日）

### Cisco：从聊天机器人到变革型 Agent

**时间**：3月23日 2:20-3:10 PM PDT  
**地点**：Moscone South Esplanade 153

Cisco 在 RSAC 2026 Day 2 发表主题演讲"**From Chatbots to Change Agents: Securing Agentic AI**"。

核心观点：
- AI Agent 的演进路径：Reactive（响应式）→ Conversational（对话式）→ Autonomous（自主式）→ **Change Agents（变革型）**
- Change Agents 具备"业务自我转型"能力——不只是执行任务，而是驱动业务流程本身的改变
- 安全挑战随之指数级增长：Agent 自主性越高，攻击面越大

### Microsoft：AI 安全栈全层保护

Microsoft 在 RSAC 2026 展示覆盖 AI 栈全层的安全产品矩阵：
- **Azure AI Foundry**：统一的 AI 安全配置与监控
- **Purview + AI Hub**：数据治理与 AI 使用合规
- **Defender AI**: AI 驱动的威胁检测，覆盖 AI 栈每一层

### Innovation Sandbox：结果待出

RSAC 2026 Innovation Sandbox 十强已公布，**结果将在大会期间宣布**。

十强中值得 Agent 开发者关注的方向：
- **Token Security**（身份优先安全 for Agentic AI）
- 传统云安全方向（Wiz、SentinelOne 等）

## Day 2 重磅：Geordie AI 赢得 RSAC 2026 Innovation Sandbox

**更正说明**：本节内容已于 2026-03-24 依据 RSAC 官方公告更正。

**RSAC 2026 Innovation Sandbox 创新大奖正式揭晓**——**Geordie AI** 从十强中脱颖而出，荣获 **"Most Innovative Startup 2026"** 大奖。

**Geordie AI 核心方向**：企业级 AI Agent 安全与治理平台，专注于：
- **Agent 实时发现与监控**：对企业内部 AI Agent 进行实时行为追踪
- **风险情报分析**：全链路可视化 + 风险评分
- **策略合规治理**：基于策略的 Agent 行为管控

> ⚠️ 此前版本误标注 Charm Security 获奖，特此更正。正确信息以 RSAC 官方公告和 [RSAC Innovation Sandbox 主页](https://www.rsaconference.com/usa/programs/innovation-sandbox) 为准。

## 与 Agent 开发的关联

RSAC 2026 对 Agent 开发者的意义：

1. **安全左移**：Agentic AI 安全正从概念走向产品化（Token Security 等初创公司进入决赛）
2. **身份治理成为标配**：未来 Agent 系统需要内置身份与权限管理机制
3. **对抗性测试常态化**：红队方法论正在被引入 Agent 系统评估（参考"Agents of Chaos"研究）
4. **Cisco 信号**：Agent 正在从"执行工具"进化为"变革驱动者"——自主性边界在扩展，安全架构需要相应升级

## 延伸阅读

- [RSAC 2026 Conference Agenda](https://www.rsaconference.com/library/machine-learning-artificial-intelligence)
- [RSAC Innovation Sandbox 2026 Finalists](https://www.rsaconference.com/library/press-release/finalists-announced-for-rsac-innovation-sandbox-contest-2026)
- [Token Security - RSAC Top 10 Finalist](https://www.token.security/news/token-security-top-10-finalist-for-rsac-2026-innovation-sandbox-contest)

---
*由 AI 自动生成 | 内容基于公开资讯整理*
