# MCP Apps：MCP 从工具协议到应用平台的跨越

> 2026 年 1 月，MCP 官方博客宣布 MCP Apps 作为首个官方 MCP 扩展正式上线。工具可以返回交互式 UI 组件——仪表盘、表单、可视化、多步骤工作流——直接渲染在对话界面中。Claude、ChatGPT、Goose、VS Code、JetBrains 均已支持。本文拆解 MCP Apps 的技术设计、与 MCP-UI/OpenAI Apps SDK 的关系、以及它对 MCP 生态定位的根本性改变。

---

## 引言：MCP 的工具边界正在溶解

MCP（Model Context Protocol）最初被设计为一个工具协议：让 Agent 连接外部工具，获取数据，执行操作。它的核心隐喻是"USB-C 端口"——统一工具接入标准。

但这个定位正在被扩展。

2026 年 1 月 26 日，MCP 官方博客宣布 [MCP Apps 正式上线](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)，作为首个官方 MCP 扩展。工具不再只能返回文本和结构化数据——它可以声明一个 UI 资源，客户端渲染出一个完整的交互界面，用户在界面中的操作结果会传回给 Agent。

这个能力听起来简单，但它从根本上扩展了 MCP 的定位：从**工具协议**到**应用平台**。

---

## 痛点：工具返回的是数据，用户需要的是交互

考虑一个典型的数据分析 Agent 场景：

Agent 调用一个 MCP 工具查询销售数据库，返回了 200 行数据。模型可以总结这些数据，但用户实际上想做的事是：按地区筛选、点击某条记录查看详情、按收入排序。每一次这样的操作，在纯文本范式下都需要一次新的 prompt——"按收入排序""只看亚太区""查看 ID=47 的详情"。可以工作，但效率低，体验割裂。

MCP 团队在官方博客中描述的这个场景精确命中了问题核心：

> "These interactions would be less smooth as text exchanges, whereas MCP Apps make them natural — it's like using any other UI-based web app."

MCP Apps 要解决的就是这个**交互密度**问题——在 Agent 对话中嵌入原生应用体验，让用户和 Agent 共同处于一个上下文内，而不是不断在"对话"和"应用"之间跳转。

---

## 技术设计：三个核心组件

MCP Apps 的架构依赖 MCP 原有的三个能力：

### 1. UI 元数据声明

工具的 `_meta.ui.resourceUri` 字段声明该工具关联的 UI 资源：

```json
{
  "name": "visualize_data",
  "description": "Visualize data as an interactive chart",
  "inputSchema": {
    "type": "object",
    "properties": {
      "dataset": { "type": "string" }
    }
  },
  "_meta": {
    "ui": {
      "resourceUri": "ui://charts/interactive"
    }
  }
}
```

这里的 `ui://` 是新增的 URI scheme，用于客户端识别这是一个需要渲染的 UI 资源而非纯文本。

### 2. UI 资源服务

MCP 服务器通过 `ui://` scheme 提供打包的 HTML/JavaScript 内容。客户端获取后，在沙箱 iframe 中渲染：

```
MCP Server
  ├── tools/          ← 原有工具定义
  └── ui://charts/    ← 新增 UI 资源
        └── interactive/
              ├── index.html
              └── bundle.js
```

### 3. 双向通信：App API

UI 和 Agent 之间的通信通过 `postMessage` + JSON-RPC 实现。`@modelcontextprotocol/ext-apps` SDK 提供 `App` 类：

```javascript
import { App } from "@modelcontextprotocol/ext-apps";

const app = new App();
await app.connect();

// 接收 Agent 工具执行结果
app.ontoolresult = (result) => {
  renderChart(result.data);
};

// 从 UI 调用 Agent 工具
const response = await app.callServerTool({
  name: "fetch_details",
  arguments: { id: "123" },
});

// 更新 Agent 上下文
await app.updateModelContext({
  content: [{ type: "text", text: "User selected option B" }],
});
```

关键设计点：**UI 操作结果会更新 Agent 的上下文**，这意味着 UI 中的用户行为可以被模型感知并在下一轮对话中反映。这是 MCP Apps 与传统插件的本质区别——不是在对话旁边弹出一个网页，而是 UI 和 Agent 共享同一个执行上下文。

---

## MCP Apps 的前身：MCP-UI 和 OpenAI Apps SDK

MCP Apps 不是凭空出现的。它的设计建立在两个先行者的工程验证之上：

| 项目 | 创建者 | 定位 |
|------|--------|------|
| **MCP-UI** | Ido Salomon、Liad Yosef（MCP-UI 社区）| 将 UI 资源嵌入 MCP 工具的社区实现 |
| **OpenAI Apps SDK** | OpenAI | ChatGPT 内的交互式应用开发工具包 |

这两个项目都验证了一个核心假设：**在 Agent 对话中嵌入原生 UI 是真实需求，而且可以标准化**。

MCP Apps 的工程意义是：将这两个独立实现的共识收敛为一个跨客户端的开放标准。Anthropic、OpenAI、MCP-UI 三方联合推动标准化，这本身就是 2026 年 AI Agent 生态的一个里程碑事件。

---

## 客户端支持：覆盖主流对话界面

MCP Apps 目前已在以下客户端上线：

| 客户端 | 支持状态 | 官方表态 |
|--------|---------|---------|
| **Claude**（Anthropic）| 已上线（Web + Desktop）| David Soria Parra（MCP 联合创始人）："第一次，MCP 工具开发者可以发布跨客户端的交互体验，而不需要写一行客户端特定代码" |
| **ChatGPT**（OpenAI）| 本周上线 | Nick Cooper（OpenAI）："我们很高兴支持这个新开放标准" |
| **Goose**（Block/Square）| 已上线 | Andrew Harvard（Block）："MCP Apps 支持我们相信的未来——用户通过一个可信 Agent 导航，而不是在碎片化的应用间切换" |
| **VS Code**（Microsoft）| VS Code Insiders 已支持 | Harald Kirschner（VS Code PM）："有了 MCP Apps，这个合约终于包含了缺失的人类交互步骤" |
| **JetBrains** | 探索中 | Denis Shiryaev（JetBrains）："在 JetBrains IDE 中引入 MCP Apps 扩展令人兴奋" |

这意味着一个 MCP App 开发者在 **Claude 开发的一个交互式图表**，可以直接在 ChatGPT、VS Code、Goose 中使用，无需任何适配。

---

## 安全模型：多层防护

在 Agent 对话中渲染来自 MCP 服务器的 HTML/JavaScript 是一个需要认真对待的安全问题。MCP Apps 的安全模型包含以下层次：

| 防护层 | 说明 |
|--------|------|
| **iframe 沙箱** | 所有 UI 内容运行在受限权限的沙箱 iframe 中，无法访问父窗口上下文 |
| **预声明模板** | Host 在渲染前可以审查 HTML 内容 |
| **可审计消息** | UI-to-host 通信走 JSON-RPC，可记录日志 |
| **用户授权** | Host 可要求 UI 触发的工具调用必须经过用户确认 |

MCP 官方建议用户继续主动审查 MCP 服务器的来源，而不是默认信任。这个安全模型的成熟度相比 2025 年的 MCP-UI 有了显著提升。

---

## 与 AG-UI / A2UI 的关系：协议栈的哪一层？

当前 Agent 交互领域有多个涉及 UI 的协议，它们的定位不同：

| 协议 | 层级 | 解决的问题 |
|------|------|-----------|
| **MCP** | 工具接入层 | Agent ↔ 外部工具 |
| **MCP Apps** | 工具返回层 | 工具返回的不仅是数据，还可以是交互式 UI |
| **A2UI**（Google）| 表示层 | Agent 生成 UI 组件声明，渲染由前端框架处理 |
| **AG-UI**（CopilotKit）| 传输层 | Agent 后端到前端应用的实时通信协议 |

**关键区分**：
- AG-UI/A2UI 的核心参与者是**后端 Agent** 和**前端应用**——协议定义的是 Agent 如何将动作传递给前端、如何接收前端事件
- MCP Apps 的核心参与者是**工具服务器**和**客户端 Host**——协议定义的是工具如何声明 UI 资源、UI 如何与 Host 通信

这两个维度是互补的：一个 Agent 可以通过 AG-UI 向前端推送状态更新，同时通过 MCP Apps 让工具返回可交互的仪表盘。

---

## 工程意义：MCP 的定位转变

MCP Apps 最重要的影响不是某个具体功能，而是它揭示的 MCP 定位转变：

**2024-2025 年**：MCP = 工具协议（Agent 调用外部工具的标准）
**2026 年起**：MCP = 应用平台（MCP Apps 让工具变成可嵌入的微型应用）

这个转变的经济意义是：MCP 生态可以从"工具市场"演进为"应用市场"。当工具可以返回交互式 UI，它就不再是单纯的 API 包装，而是一个完整的用户体验载体。开发者有动力开发更丰富的 MCP App，因为用户可以直接在对话中体验，而不需要引导用户去另一个网站或应用。

MCP 官方的措辞也印证了这个方向："MCP evolves from 'tools' into a real platform for agentic work"。

---

## 参考文献

- [MCP Apps 官方公告](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)（一手来源，MCP Apps 技术细节和客户端支持声明）
- [MCP Apps SEP-1865 提案](https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/)（一手来源，设计动机和 MCP-UI/OpenAI Apps SDK 背景）
- [MCP Apps ext-apps SDK](https://github.com/modelcontextprotocol/ext-apps)（官方 SDK，包含多个示例）
- [Medium: MCP Apps Is Now a Standard](https://medium.com/@takesy.morito/mcp-apps-is-now-a-standard-heres-what-it-means-and-how-i-implemented-it-fcf2c90ca669)（工程实现经验）
- [Spring AI + MCP Apps 集成](https://spring.io/blog/2026/03/18/mcp-apps)（企业级集成视角）
