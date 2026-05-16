# czlonkowski/n8n-mcp：让 AI Agent 驱动 1,650 个工作流节点

> n8n-MCP 是一个 Model Context Protocol 服务器，为 AI 助手提供对 n8n 工作流自动化平台全部节点的深度访问能力。在 AI Coding 场景下，这意味着 Claude Code 可以直接驱动一个拥有 820+ 核心节点和 830+ 社区节点的工作流自动化生态——不只是调用 API，而是**以结构化方式理解和操作企业级工作流逻辑**。

---

## 亮点：这个项目解决了一个长期痛点

传统的 AI Agent 工具调用是「点对点」的：Agent 需要什么，就为它写什么 tool definition。但企业级工作流平台（n8n、Zapier、Make）拥有数百甚至数千个节点，每个节点有独特的参数结构和操作语义。为 Agent 手工维护这些 tool definitions 的成本极高，而且一旦节点更新，定义就失效了。

n8n-MCP 的解法是**协议层抽象**：不逐个定义 tool，而是让 Agent 通过 MCP 协议直接查询「n8n 平台知道什么节点、每个节点的参数是什么、能做什么操作」。

```
你的 Agent → n8n-MCP（MCP Server）→ n8n 节点生态（1,650 节点）
```

这相当于给 Agent 配备了一个「企业工作流工具书」，Agent 自己翻目录、自己查用法，而不是靠人类事先写好所有可能的工具卡片。

---

## 核心数据

| 维度 | 数值 |
|------|------|
| **GitHub Stars** | 20,962 |
| **n8n 节点覆盖** | 1,650（820 核心 + 830 社区） |
| **节点属性覆盖率** | 99% |
| **操作覆盖率** | 63.6% |
| **文档覆盖率** | 87%（官方 n8n 文档） |
| **AI 工具变体检测** | 265 个带完整文档的 AI-capable 工具 |
| **模板库** | 2,352 个工作流模板 |
| **快速体验** | dashboard.n8n-mcp.com（免安装，100 calls/天免费） |

---

## 技术原理

n8n-MCP 作为 MCP Server 运行，遵循 MCP 协议规范接入任何兼容 MCP 的 AI 客户端（Claude Code、Cursor、Windsurf 等）。

Server 侧维护了 n8n 节点的完整 schema 数据库，当 Agent 通过 MCP 协议查询时，返回结构化的节点定义：

```json
{
  "name": "n8n_node_http_request",
  "description": "Sends HTTP requests to external services",
  "parameters": {
    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
    "url": {"type": "string"},
    "headers": {"type": "object"},
    "body": {"type": "any"}
  },
  "operations": ["get", "post", "put", "delete"]
}
```

Agent 不需要预先知道这个节点存在——它可以通过 MCP 的工具发现机制，在需要时查询 n8n-MCP 获取当前任务所需的节点定义。

> "n8n-MCP serves as a bridge between n8n's workflow automation platform and AI models, enabling them to understand and work with n8n nodes effectively." — GitHub README

---

## 落地场景

### 场景一：AI Agent 驱动企业工作流自动化

用户说「帮我把这些客户记录同步到 HubSpot，并自动发送欢迎邮件」，Agent 通过 n8n-MCP 了解到 n8n 平台有 HubSpot 节点和 Email 节点，自动生成对应的 n8n workflow JSON 并通过 MCP 调用创建。

### 场景二：代码生成 + 工作流编排的双层 Agent

Claude Code 负责写业务逻辑代码，n8n-MCP 负责将代码接入企业的自动化基础设施。在 Cursor 的 Cloud Agent 场景下，这意味着**代码生成 Agent 和工作流编排 Agent 是分开的**，n8n-MCP 提供的是它们之间的「共同语言」。

### 场景三：AI 驱动的 workflow 调试

Agent 发现某个工作流节点报错，通过 n8n-MCP 查询该节点的完整参数 schema，判断是参数类型不匹配还是权限问题，直接在 Claude Code 中修改配置或生成新的 workflow 变体。

---

## 与 Claude Code Auto Mode 的关联

Claude Code Auto Mode 解决的是「Agent 执行动作时的安全性」问题——哪些动作可以放行，哪些需要阻断。

n8n-MCP 解决的是另一个维度的问题：**Agent 执行动作的能力边界**。当企业工作流需要通过 MCP 调用外部系统时，Agent 面临的不只是「能不能做」，还有「我怎么知道我有哪些可用的工作流节点」。

两者结合的想象空间：Auto Mode 负责判断「Agent 发出的 HTTP POST 是否危险」，n8n-MCP 负责让 Agent 知道「原来 n8n 平台上有这么多节点可以组合使用」。

---

## 竞品对比

| 项目 | 节点覆盖 | 协议 | Stars | 特点 |
|------|---------|------|-------|------|
| **n8n-MCP** | 1,650 | MCP | 20,962 | 最全面的 n8n 节点生态 |
| **mattpocock/skills** | 1,000+ | Claude Code | 74,875 | 通用 Skills 生态，偏代码生成 |
| **anthropics/skills** | 官方 | Claude Code | 689 | 官方 Skills，专注 Claude Code 集成 |

n8n-MCP 的差异化在于**企业工作流自动化**这个垂直领域，而不是通用编程能力。当 Agent 需要操作的不是代码文件，而是企业级 SaaS 服务和 API 连接时，n8n-MCP 是目前最完整的解决方案。

---

## 适用人群

✅ 有 n8n 基础，希望让 AI Agent 驱动自动化工作流的开发者  
✅ 企业内部有大量 n8n workflow，想要 AI Agent 参与管理和编排  
✅ 在 Cursor/Cursor 等 IDE 中做 AI Coding，需要连接企业后端系统的场景  
❌ 纯代码生成任务（用 mattpocock/skills 或 Claude Code 内置能力更合适）  
❌ 不使用 n8n 的团队

---

## 快速上手

```bash
# 方式一：免安装快速体验
# 访问 https://dashboard.n8n-mcp.com，免费额度 100 calls/天

# 方式二：本地 MCP Server
npm install -g n8n-mcp
n8n-mcp configure  # 配置 n8n 实例地址
# 然后在 Claude Code / Cursor 中配置 MCP 端点
```

> "Deploy in minutes to give Claude and other AI assistants deep knowledge about n8n's 1,650 workflow automation nodes (820 core + 830 community)." — GitHub README

---

**推荐理由**：n8n-MCP 将企业工作流自动化的广度（1,650 节点）和 AI Agent 的深度（通过 MCP 协议结构化查询）结合在一起，是目前 AI Agent 驱动企业工作流的最完整解决方案之一。在 Claude Code Auto Mode 解决了「动作安全性」问题后，n8n-MCP 解决的是「动作从哪里来」的问题——两者是企业级 Agent 落地的两个不同维度的答案。

**标签**：Tool Use · MCP · Workflow Automation · n8n
**来源**：[GitHub — czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp)
**Stars**：20,962（2026-05-16）
**归档**：`projects/`
**作者**：AgentKeeper