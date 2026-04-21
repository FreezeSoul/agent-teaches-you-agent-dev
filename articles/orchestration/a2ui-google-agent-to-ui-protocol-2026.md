# A2UI 协议深度解析：Agent 如何「生成」而非「返回」用户界面

> **核心判断**：A2UI（Agent to UI）和 AG-UI 不是同一个协议，也不是竞争关系——它们解决的是不同层次的问题。A2UI 定义 Agent 生成的 UI 组件声明规范（表示层），AG-UI 定义 Agent 后端到前端应用的通信协议（传输层）。理解了这两者的分工，才真正理解了整个 Agent 协议栈的第三层为什么需要两个协议。

---

## 名字相近的两个协议：为什么需要澄清

在当前 Agent 协议栈的讨论中，A2UI 和 AG-UI 因为名字相似，经常被混淆。已有文章中对此只有一句话概括，但这造成了理解缺口：

- **AG-UI**（Agent-User Interaction Protocol，CopilotKit 主推）—— 定义 Agent 后端如何将事件流推送到前端，以及如何接收用户的实时输入
- **A2UI**（Agent to UI Protocol，Google 主推）—— 定义 Agent 生成的 UI 组件声明格式，让客户端能用原生组件渲染这些界面

两者解决的问题在不同的协议层次。如果把 Agent 系统类比为一个餐厅：
- **AG-UI** 是点餐系统（如何把你的需求传达给厨房、如何接收厨房的实时进度更新）
- **A2UI** 是厨房做出来的菜本身（具体是什么菜、长什么样、用什么餐具装）

本文聚焦 A2UI。

---

## A2UI 解决的核心问题

### Agent 如何「安全」地向用户返回可交互界面

当一个 Agent 需要向用户展示一个订餐表单、地图控件、数据图表时，传统方案有两种：

1. **返回文本描述**：「请填写日期为明天，人数为2，时间为19:00」——体验极差
2. **返回 HTML/JS 代码块**（通过 iframe 或代码块渲染）——安全隐患巨大，样式难以与应用统一

A2UI 的思路是：Agent 不返回代码，也不返回最终渲染结果，而是返回一份**结构化的组件声明**。这份声明由客户端的原生渲染器负责解析，渲染成平台原生的 UI 组件。

这类似于 Flutter 的声明式 UI 理念，但语言变成了 JSON，渲染端变成了多种多样的客户端（Web、Mobile、Desktop）。

### 跨平台渲染的核心价值

一个 Agent 的响应，可以在不修改任何代码的情况下，在不同平台的渲染器中呈现一致的体验：

| 渲染器 | 平台 | 现状 |
|--------|------|------|
| Lit Web Components | Web（React/Vue/Angular）| 官方维护 |
| React | Web | 社区 |
| Angular | Web | 社区 |
| Flutter | iOS / Android / Web | Google 官方 |
| Markdown Renderer | 跨平台 | 官方 |

这意味着 Agent 开发者只需要生成一种格式（A2UI JSON），而不是针对每个平台单独写适配代码。

---

## A2UI 的技术规格

### 邻接表模型：为什么 JSON 结构是扁平的

A2UI 组件的 JSON 结构采用了**邻接表（Adjacency List）模型**，而不是嵌套树结构。这是 A2UI 最重要的设计决策之一。

传统嵌套结构的问题：
```json
{
  "type": "Column",
  "children": [
    {
      "type": "Text",
      "text": "Hello"
    },
    {
      "type": "Row",
      "children": [...]
    }
  ]
}
```

A2UI 邻接表结构：
```json
{
  "surfaceUpdate": {
    "components": [
      {
        "id": "root",
        "component": {
          "Column": {
            "children": {"explicitList": ["greeting", "buttons"]}
          }
        }
      },
      {
        "id": "greeting",
        "component": {
          "Text": {"text": {"literalString": "Hello"}}
        }
      },
      {
        "id": "buttons",
        "component": {
          "Row": {"children": {"explicitList": ["cancel-btn", "ok-btn"]}}
        }
      },
      {
        "id": "ok-btn",
        "component": {
          "Button": {
            "child": "ok-text",
            "action": {"name": "confirm"}
          }
        }
      }
    ]
  }
}
```

**邻接表模型的优势**（A2UI 官方文档原话）：

> Flat structure, easy for LLMs to generate—this is why A2UI protocol is so LLM-friendly

具体来说：
- **可流式生成**：Agent 可以逐步生成组件，不需要在第一次响应中就完成整棵树的结构
- **可增量更新**：只发送变化的部分，不需要重绘整个界面
- **ID 引用无歧义**：每个组件有全局唯一 ID，更新时不需要遍历树结构定位
- **循环引用安全**：邻接表天然避免了嵌套 JSON 的循环引用问题

### 四种核心消息类型

A2UI 定义了四种核心消息类型，覆盖 UI 生成的完整生命周期：

| 消息类型 | 作用 | 典型使用场景 |
|----------|------|-------------|
| `surfaceUpdate` | 定义或更新 UI 组件 | 创建表单、更新按钮文字 |
| `dataModelUpdate` | 更新应用状态 | 填入用户选择的日期、填充下拉列表 |
| `beginRendering` | 通知客户端开始渲染 | 表单所有字段都已准备好 |
| `deleteSurface` | 清理已完成的 UI 表面 | 工作流结束，移除临时界面 |

### 数据绑定：UI 结构与状态的分离

A2UI 的另一个核心设计是**数据绑定机制**（基于 JSON Pointer，RFC 6901）。UI 结构和数据是分离的：

```json
// 固定值
{"text": {"literalString": "Welcome"}}

// 数据绑定（引用外部状态）
{"text": {"path": "/booking/date"}}

// 日期选择器绑定
{"DateTimeInput": {
  "value": {"path": "/booking/date"},
  "enableDate": true
}}
```

当状态更新时，绑定到该路径的 UI 组件自动更新，不需要 Agent 重新生成整个界面。

### 安全设计：声明式而非可执行

A2UI 官方明确声明其核心价值之一是**安全设计**：

> Declarative data format, not executable code. Agents can only use pre-approved components from your catalog—no UI injection attacks.

Agent 只能使用预先定义的组件目录中的组件，不能动态生成任意代码。组件目录（Component Catalog）由应用开发者维护，控制 Agent 能展示哪些 UI 模式。

---

## A2UI vs AG-UI：一张图说清楚关系

```
┌─────────────────────────────────────────────────────┐
│                   用户可见层                          │
│  ┌───────────────────────────────────────────────┐  │
│  │  A2UI 组件声明（"渲染这个按钮、这个日期选择器"） │  │
│  │  AG-UI 事件流（"正在执行、工具已调用、需要确认"）│  │
│  └───────────────────────────────────────────────┘  │
│           ↑ A2UI 渲染 + AG-UI 状态同步               │
└─────────────────────────────────────────────────────┘

A2UI: Agent → UI组件声明（表示层）
AG-UI: Agent ↔ 前端通信（传输层）
MCP:  Agent → 工具/数据（接入层）
A2A:  Agent ↔ Agent（协作层）
```

**两者的互补关系**：

- **AG-UI** 负责把 Agent 的执行状态实时同步给前端，同时把用户的输入（确认、取消、上下文注入）实时传回给 Agent
- **A2UI** 负责把 Agent 的 UI 表达渲染成原生组件

实际集成时，两者可以一起使用——A2UI 生成 UI 组件声明，通过 AG-UI 传输到前端，前端同时渲染组件并处理 AG-UI 的状态同步事件。

Google ADK 同时支持 A2UI 和 AG-UI，两者共存于同一个工作流中，这正是这种互补关系的最佳例证。

---

## 生产落地案例

### Google ADK + A2UI 的餐厅预订 Demo

A2UI 官方 Quickstart 是一个完整的餐厅查找应用，展示了 A2UI 的实际工作流：

1. 用户向 Agent 发送自然语言请求（"我想找一家意大利餐厅"）
2. Agent 逐步生成 A2UI 消息：搜索表单 → 餐厅列表卡片 → 详情弹窗
3. A2UI 消息通过 SSE 流式传输到前端
4. 前端 Lit 渲染器逐步渲染（用户看到界面逐步构建）
5. 用户点击「选择餐厅」→ `select_restaurant` action 事件传回 Agent
6. Agent 继续生成下一步的 A2UI 组件

### Landscape Architect Demo

A2UI 官方还提供了一个更复杂的 Demo：用户上传一张园林平面图，Agent 自动生成一套 UI 控件（面积计算器、植物选择面板、预算估算表），全部通过 A2UI 流式生成和渲染。这个 Demo 展示了 A2UI 在复杂多步骤 Agent 工作流中的实际价值。

### 企业级采用

A2UI 已在以下生产系统中使用：
- **Google Gemini Enterprise**（部分功能）
- **Opal**（生产级应用）
- **Flutter GenUI SDK**（Google 官方 Flutter 渲染器）

---

## A2UI 在 Agent 演进路径中的位置

在 Agent 演进路径框架中，A2UI 处于 **Stage 6（Tool Use）和 Stage 7（Orchestration）** 的交叉点——它既是 Agent 对外的「工具调用」（调用 UI 渲染能力），也是 Agent 与用户协作的「编排层」。

更准确的定位是：**Stage 7 的人机协作基础设施层**。A2UI 的确认机制（通过 `action` 字段触发回调）和 AG-UI 的 `ConfirmationRequested` 事件处理的是同一个问题的不同层次：A2UI 负责「确认按钮长什么样」，AG-UI 负责「如何把用户点击确认这个事件传回给 Agent」。

---

## 已知局限

1. **v0.8 稳定版才刚发布**：A2UI 的组件模型还在演进中，v0.9 会加入 createSurface、client-side functions 等新特性。早期采用者需要承担协议变更的风险。

2. **组件目录需要手工维护**：Agent 不能动态创建任意 UI，只能从预定义的组件目录中选择。这意味着每个应用都需要一个「A2UI 组件目录」，需要前端开发者的参与。

3. **与 AG-UI 的职责边界需要架构决策**：在同一个应用中，何时用 A2UI 生成 UI，何时用 AG-UI 事件驱动，需要架构层面的设计决策，没有标准答案。

4. **渲染器质量参差不齐**：官方 Lit 渲染器成熟度较高，但 Flutter 渲染器和其他社区渲染器的成熟度不一。

---

## 判断与结论

> **工程建议**：如果你在 Google ADK 生态内构建应用，A2UI 是默认选择，配合 AG-UI 使用可以获得完整的「生成 UI + 状态同步」能力。如果你使用其他框架（如 LangGraph），需要确认目标框架对 A2UI 的支持程度——目前 CopilotKit 的 AG-UI 集成更成熟，而 A2UI 更偏向 Google 生态。

A2UI 的本质是：**把 UI 生成变成一种结构化、安全、可流式输出的声明式语言**。这与 MCP 把工具调用标准化为 JSON-RPC 的思路一脉相承——只不过 A2UI 把这个标准化推到了离用户更近的表示层。

---

## 参考资料

- [A2UI Official Site](https://a2ui.org/) — 官方首页，包含规范、渲染器列表和 Demo
- [A2UI GitHub - google/A2UI](https://github.com/google/A2UI) — 规范定义（v0.8 稳定版）、渲染器实现、传输层说明
- [Introducing A2UI - Google Developers Blog](https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/) — 官方发布博客，v0.8 稳定版说明
- [A2UI + Google ADK Technical Interviewer Demo - GitHub Discussion](https://github.com/google/A2UI/discussions/390) — ADK + A2UI 完整实现示例
- [A2UI v0.8 Specification](https://a2ui.org/specification/v0.8-a2ui/) — 完整规范（组件类型、消息格式、数据绑定语法）
- [A2UI vs AG-UI - CopilotKit 官方](https://www.copilotkit.ai/ag-ui-and-a2ui) — AG-UI 与 A2UI 关系官方说明
- [Mete Atamel - A2UI with ADK](https://atamel.dev/posts/2026/03-30_a2ui_with_adk/) — A2UI + ADK 代码示例与架构解析
- [DEV Community - A2UI Complete Guide](https://dev.to/czmilo/the-complete-guide-to-a2ui-protocol-building-agent-driven-uis-with-googles-a2ui-in-2026-146p) — 工程实践指南
- [Google Cloud Next 2026 - ADK + A2UI Session](https://www.googlecloudevents.com/next-vegas/session/3920503/) — 表单、图表、实时控件的完整 Demo
