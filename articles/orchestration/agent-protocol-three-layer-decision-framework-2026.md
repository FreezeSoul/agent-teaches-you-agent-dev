# Agent Protocol 三层架构决策指南：为什么你选错了协议

## 核心问题

大多数团队在选择 Agent 协议时，实际上在同时做三个互不相关的决策，却把它们混为一谈：

- **垂直集成**：Agent 如何连接到工具和数据？
- **水平协调**：多个 Agent 之间如何协作？
- **交互层**：Agent 如何向用户界面暴露状态？

把这三个问题当一个回答，是生产环境中 Agent 集成频频失败的根本原因。

本文构建一个三层的 Agent 接口栈模型，帮助你在 2026 年的协议生态中做出正确的架构决策。

---

## 为什么协议选择是三个问题，不是一个

### 单协议思维的陷阱

当你把 MCP 当作 A2A 的替代品，会发生什么？

一个调度 Agent 通过 MCP 调用子 Agent 的工具——但这在概念上等同于"通过 HTTP API 调用一个微服务"。MCP 的请求-响应模型无法表达"任务已提交，请等待完成"这类长生命周期状态。当你的调度 Agent 需要知道子 Agent 什么时候真正完成了某个复杂任务，MCP 告诉你"请求已发送"，然后就沉默了。

反过来，如果你把 A2A 用于单 Agent 的工具调用问题，你需要为每个工具写一个 Agent Card、实现完整的状态机、处理 SSE 订阅——而你其实只需要一个 `tools/call` 接口。

两种失败模式的代价都在生产环境暴露后才显现，修复成本极高。

### 三层模型的历史先例

这不是新问题。1990 年代的"TCP/IP vs OSI"七层模型之争，最终以 TCP/IP 胜出告终——不是因为它技术上更优雅，而是因为它有 BSD Unix 上运行的代码和实际部署的产品。OSI 是委员会设计的完美理论，TCP/IP 是工程师在真实网络中迭代出来的实践。

VHS vs Betamax 是另一个案例：Betamax 的画质更好，但 VHS 通过开放授权建立了更广泛的生态系统，最终吞噬了市场。

MCP 和 A2A 的竞争也在遵循同样的规律。关键不是"哪个协议更好"，而是"每个协议解决哪一层的问题"。

---

## 三层 Agent 接口栈

### 第一层：工具接入层（MCP）

**解决的问题**：一个 Agent 如何连接外部工具、数据源和 API？

MCP 的核心抽象是**客户端-服务器模型**：Host（运行 LLM 的应用）通过 MCP Client 连接到一个或多个 MCP Server，每个 Server 暴露一组工具。Host 持有所有授权决策权，Server 只在 Host 授予权限后才能访问数据。

这个设计的核心假设是**单 Agent 场景**：一个 Claude Code Agent 需要调用 GitHub、Slack、内部数据库——MCP 是完美的选择。你只需要为每个数据源写一个 MCP Server，所有兼容 MCP 的 Host 都可以使用。

**局限性**：MCP 的信任模型是集中式的。当多个 Agent 需要共享同一个工具 Server 时，"哪个 Agent 的权限适用"这个问题没有干净的回答。有些团队用"每个 Agent 独立实例"的方案绕过去，但这是运营上的额外复杂度，不是架构上的解决方案。

MCP 没有任务生命周期概念——它处理的是离散调用，不是"委托任务→等待完成→收集结果"这类长时工作。

### 第二层：Agent 协调层（A2A）

**解决的问题**：多个 Agent 之间如何协作，即便它们来自不同的框架、不同的供应商？

A2A 的核心抽象是**对等身份模型**：每个 Agent 发布一个 JSON 格式的 Agent Card，描述自己的能力和认证要求。其他 Agent 通过发现机制找到它，然后通过定义好的任务生命周期（`submitted → working → input-required → completed/failed`）进行协作。整个过程不需要知道对方 Agent 内部用什么框架、有什么工具。

这解决的是**跨组织、跨框架边界**的问题。当你的调度 Agent 需要委托任务给第三方 Agent——比如外部供应商提供的 GPT-agent——你无法通过 MCP 调用它的内部工具，因为那需要信任整个外部系统。A2A 的设计让你在不了解 Agent 内部实现的情况下完成协作。

IBM 的竞争协议 ACP 在 2025 年 8 月合并进入 A2A，标志着行业在水平协调层的收敛。

**局限性**：A2A 的 Agent Card 发现机制为协作增加了发现复杂度。对于单 Agent 或紧耦合的多 Agent 系统，直接函数调用永远比通过 A2A 发消息更简单。A2A 的价值只在跨边界时才会体现。

### 第三层：交互层（AG-UI / A2UI）

**解决的问题**：运行中的 Agent 如何向用户界面暴露中间状态？

这一层目前没有稳定的标准。AG-UI 和 A2UI 分别从不同角度尝试解决这个问题：

- **AG-UI**：定义了 Agent 后端到前端应用的通信协议（传输层），支持流式中间结果、结构化组件渲染、澄清对话等交互模式
- **A2UI（Google Agent to UI Protocol）**：定义了 Agent 生成 UI 组件的声明格式（表示层），让 LLM 可以流式生成 UI 组件

这一层是 2026 年 Agent 工程中**最不成熟但需求最迫切**的缺口。每个有实际用户的生产 Agent 部署都在解决"如何让用户看到 Agent 正在做什么"这个问题，但目前都是定制方案。

---

## 协议选择决策树

### 何时选 MCP（工具接入层）

**选 MCP 当**：
- 你在构建单 Agent 系统，需要接入多个外部工具
- 你需要标准化的工具描述，让多个 AI Provider（Claude、GPT、Gemini）可以使用同一套工具
- 你有内部的 REST API 需要暴露给 Agent，但没有时间写完整的 SDK

**不选 MCP 当**：
- 你需要跨 Agent 的任务状态追踪（MCP 没有这个概念）
- 你需要让多个 Agent 共享同一个工具实例（信任模型不支持）
- 你在与外部不受控的 Agent 系统对接（A2A 的场景）

### A2A Agent Card 的结构示例

一个标准 A2A Agent Card 包含以下关键字段（省略认证和安全方案细节）：

```json
{
  "name": "code-review-agent",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "skills": [
    { "id": "pull-request-review", "name": "PR Review", "description": "Analyzes code changes in a pull request and provides review comments" },
    { "id": "vulnerability-scan", "name": "Security Scan", "description": "Runs SAST tools against code changes" }
  ],
  "authentication": {
    "schemes": ["bearer"],
    "credentials": "https://api.example.com/auth"
  }
}
```

这个 JSON 文档是你向外部系统暴露的唯一接口——Agent Card 写得不清楚，外部 Agent 就无法正确调用你。

**Agent Card 的三个核心字段**：

1. **`capabilities`**：声明你的 Agent 支持哪些 A2A 能力（流式、推送、状态历史）。不支持流式的 Agent 不应该在 `capabilities.streaming` 里声明 `true`，否则调用方会按流式设计，实际收到同步响应后行为不可预测。

2. **`skills`**：你的 Agent 能处理哪些任务。外部调度 Agent 根据这个列表决定是否把任务发给你——这个字段是能力发现的全部依据。描述太宽泛（"I can do anything"）等于没有描述，太具体又限制了调用方的使用场景。

3. **`authentication`**：外部 Agent 如何认证自己。A2A 支持 Bearer Token、Webhook HMAC 等多种方案，但大多数实现问题出在**没有明确指定范围**：同一个 API Key 有时候能调用所有工具，有时候只能调用部分。Agent Card 的 `authentication` 字段必须说清楚这个边界。

### 何时选 A2A（Agent 协调层）

**选 A2A 当**：
- 你有两个以上的独立 Agent 需要协作
- 至少有一个 Agent 是外部的或跨团队的
- 你需要追踪跨 Agent 的任务生命周期
- 你在构建跨组织的 Agent 工作流

**不选 A2A 当**：
- 你的所有 Agent 都在同一个进程内（直接内存调用，永远更快）
- 你的多 Agent 系统是紧耦合的，不需要跨边界协作
- 你只有单 Agent（引入 A2A 的 Agent Card 复杂度毫无必要）

### 何时考虑 AG-UI / A2UI（交互层）

**考虑当**：
- 你的 Agent 需要向用户展示流式中间结果
- 你的 Agent 需要在运行中接受用户的澄清反馈
- 你在构建面向最终用户的 Agent 产品

**现状**：2026 年，AG-UI 和 A2UI 都是相对早期的项目，还没有形成 MCP 和 A2A 那样的生态规模。如果你的产品需要稳定的交互层，建议持续关注但谨慎在生产环境重度依赖。

---

## 四种部署拓扑下的协议选择

### 拓扑一：单框架、内部部署

所有 Agent 运行在同一个技术栈内（如全部用 LangGraph 或全部用 CrewAI）。

**协议策略**：用 MCP 做工具集成。框架原生抽象（LangGraph 的 `ToolNode`、CrewAI 的 `Tool`）用于内部工具调用，因为它们提供了更好的类型安全和调试体验。MCP 的价值在于"一次实现，多个 Host 复用"——当你需要接入任何框架都支持的外部工具时，MCP Server 是最低成本的选择。

**不要做**：为了可移植性把框架原生抽象全部替换成 A2A/MCP 接口——内部代码永远可以在切换框架时重构，但为内部代码引入协议抽象带来的复杂度是纯粹的浪费。

### 拓扑二：多框架、内部部署

不同团队使用不同框架（如数据团队用 LangGraph，安全团队用 CrewAI），但都在同一组织内。

**协议策略**：MCP 用于所有需要跨框架复用的工具集成。A2A 用于跨框架边界的 Agent 协作。只有**协议边界处**才引入标准协议，内部实现全部用框架原生能力。

**不要做**：试图让整个系统从一开始就是"协议无关"设计。只有真正跨框架的接口才值得抽象；内部架构追求协议无关只会损失框架特定能力（LangGraph 的 checkpointing、CrewAI 的 role assignment）。

### 拓扑三：跨组织部署

Agent 需要与外部组织的 Agent 系统对接。

**协议策略**：A2A 是必要项——它专门设计来处理"看不到对方 Agent 内部"的问题。你的内部实现可以继续用任何框架，但与外部系统对接的接口必须是 A2A。

**关键设计**：外部暴露的 Agent Card 必须包含完整的 OpenAPI 安全方案描述，因为 A2A Agent Card 引用 OpenAPI 来处理认证。A2A Agent Card 写得好不好，直接决定了与外部系统对接的成功率。

### 拓扑四：受监管行业

金融、医疗、法律等需要合规的领域。

**协议策略**：Linux Foundation 已经在 2025 年 12 月成立 Agentic AI Foundation（AAIF），共同管理 MCP 和 A2A 规范。AAIF 治理意味着这两个协议都有正式的版本管理和弃用政策，降低了"供应商锁定后协议被放弃"的风险。这对受监管行业的采购和合规评估非常重要。

**额外考虑**：你的 MCP Server 的 OpenAPI 规范质量和你的 A2A Agent Card 的安全方案，都需要纳入合规审计范围——协议文档的清晰度直接影响 Agent 的行为可预测性，而行为可预测性是合规的基础。

---

## 性能与安全：两个关键工程问题

### 性能方面

MCP 的一个常见性能声称是"实现 MCP 的组织报告部署速度提升 40-60%"。这个数字在多篇博客文章中被引用，但没有找到一手来源——没有调研、没有案例研究、没有具名公司。在有实际数据之前，应该把这个数字当作营销内容而非工程基准。

A2A 和 MCP 都支持 SSE 用于流式场景。如果你需要向用户展示增量进度，从一开始就设计支持流式。不要在同步协议表面上后期改造流式能力。

### 安全方面

**MCP 安全是 2026 年的重大工程问题**。2026 年前两个月内，安全研究人员为 MCP Server 提交了约 30 个 CVE，包括：

- **CVE-2026-26118**：Microsoft MCP Server 工具劫持（CVSS 8.8）
- **CVE-2026-5607**：mcp-browser-agent SSRF 漏洞
- **CVE-2026-20205**：Splunk MCP Server 信息泄露（明文暴露 session token）

这些 CVE 揭示了 MCP 的根本性安全挑战：**MCP Server 扩展了你的 AI Agent 的攻击面**。当你为 Agent 添加一个 MCP Server，你实际上是在让一个 AI Agent 有能力调用那个 Server 的所有接口。如果 Server 有漏洞，Agent 就可以利用那个漏洞。

这意味着 MCP 安全不只是"选择一个安全的 Server"，而是"为每个 MCP Server 实施最小权限原则"。一个设计良好的 MCP Server 应该只暴露 Agent 完成特定任务所需的最小接口集，而不是暴露整个数据库或整个文件系统。

---

## 协议碎片化的现状与下一步

### 规范层已收敛，实现层还在混乱

2025 年 12 月，Anthropic、OpenAI、Block 联合创立 AAIF（Linux Foundation 旗下），Google、Microsoft、AWS、Cloudflare、Bloomberg 作为白金会员加入。这个阵容基本上代表了 2026 年 Agent 基础设施的所有主要玩家。

**协议规范层面的碎片化已经基本解决**。行业收敛于 MCP（工具层）+ A2A（协调层）的双协议栈。

**但实现层的碎片化仍然严重**。两个都声称"完全支持 MCP"的系统，可能实现了不同的 spec 子集，对错误的处理方式不同，能力协商行为不一致——这些差异只在高负载下才会暴露。这是 2026 年 Agent 工程师最普遍面对的实际问题。

### AG-UI：第三层正在形成

如果 MCP 处理垂直工具集成，A2A 处理水平 Agent 协调，那么第三层——**人如何在 Agent 运行过程中保持参与**——目前没有稳定标准。

AG-UI 是目前这个方向上最活跃的项目。如果它能形成稳定规范并获得足够多的框架支持，将补完 Agent 接口栈的最后一块拼图。

---

## 架构决策检查清单

在设计你的 Agent 接口层之前，逐项确认：

- [ ] **明确回答**：你的 Agent 系统当前需要解决的是"垂直工具调用"、"水平 Agent 协作"还是"交互层"问题？这三个问题对应不同的协议选择
- [ ] **不提前抽象**：只在真实存在跨框架、跨组织边界的地方引入协议标准；内部架构用框架原生能力
- [ ] **MCP Server 最小权限**：每个 MCP Server 只暴露完成特定任务所需的最小接口集
- [ ] **A2A Agent Card 完整描述**：如果你的 Agent 需要与外部系统对接，Agent Card 的 OpenAPI 安全方案描述必须完整准确
- [ ] **流式设计前置**：如果你的用户需要看到 Agent 的中间处理进度，在架构设计阶段就纳入流式方案
- [ ] **持续跟踪 AG-UI**：2026 年内这个领域很可能会出现稳定标准，提前了解以便在合适时机接入

---

## 参考资料

- [Agent Protocol Fragmentation: Designing for A2A, MCP, and What Comes Next](https://tianpan.co/blog/2026-04-19-agent-protocol-fragmentation-a2a-mcp) — 2026-04-19，三层协议栈架构决策框架
- [MCP vs A2A in 2026: How the AI Protocol War Ends](https://philippdubach.com/posts/mcp-vs-a2a-in-2026-how-the-ai-protocol-war-ends/) — 2026，协议竞争历史类比与行业收敛分析
- [A2A Protocol and MCP: What Every AI Agent Needs in 2026](https://neomanex.com/posts/a2a-mcp-protocols) — 2026，协议互补关系
- [OX Security: The Mother of All AI Supply Chains - Critical Systemic Vulnerability at the Core of MCP](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/) — MCP 架构性安全漏洞分析
- [Anthropic + OpenAI donate Model Context Protocol and establish Agentic AI Foundation](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation) — MCP 规范治理归属
- [ACP joins A2A under Linux Foundation](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/) — 竞争协议合并信号
