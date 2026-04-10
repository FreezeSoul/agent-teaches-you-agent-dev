# AgentDM：MCP 与 A2A 协议桥接的工程实践

## 核心问题

当一个组织同时运行多个 Agent 时，它们通常来自不同的框架、不同的运行时、甚至不同的供应商。在这种异构环境下，Agent 之间的通信成了实际问题：Claude Code agent 和 Windsurf agent 之间怎么直接对话？Cursor agent 如何向一个外部托管的 GPT-agent 发送结构化任务？

现行的解决方案有几类：

- **共享运行时编排**：所有 agent 运行在同一个进程内，通过内存直接调用。LangGraph 的 `AgentExecutor`、CrewAI 的 `Crew` 都属于此类。好处是延迟最低，坏处是所有 agent 必须使用同一套技术栈。
- **Hub-Spoke 中枢模式**：一个中央编排 agent 通过各自框架的 SDK 连接所有子 agent。AutoGen 的 `GroupChatManager` 是典型代表。问题是中央编排点变成了单点故障，且每个框架都要写适配代码。
- **协议层直接通信**：agent 通过标准协议直接寻址彼此，不需要共享运行时或中央编排。MCP 和 A2A 分别解决了工具调用和 agent 间通信的协议标准问题——但这两个协议并不直接兼容。

AgentDM 尝试解决的是第三类方案中 MCP 和 A2A 之间的协议边界问题：让一个纯 MCP agent 能够向 A2A agent 发送消息，反之亦然，全程不需要修改 agent 本身的代码。

## AgentDM 的架构

AgentDM 是一个托管的消息平台，同时实现了 MCP server 和 A2A client（服务端点）。它的核心机制是**协议翻译**：将 MCP 的工具调用语义映射为 A2A 的任务下发语义，反向亦然。

### MCP 端：暴露的三个工具

AgentDM 在 MCP 侧暴露三个工具，agent 通过标准的 MCP `tools/call` 接口使用：

```
send_message(recipient: string, content: string)
  → 向指定 @alias 的 agent 发送消息
  
read_messages(limit?: number)
  → 读取收件箱中的消息（返回消息 ID 和内容）
  
message_status(message_id: string)
  → 查询某条消息的投递状态和已读回执
```

这是标准的 MCP 工具调用范式——任何 MCP-compatible agent 不需要安装任何 SDK，只需要往 `mcpServers` 配置里加一个 server URL 即可。

### A2A 端：Agent Card 发现

在 A2A 侧，每个注册到 AgentDM 的 agent 都会自动生成一个标准 A2A Agent Card，其中声明了它的能力、认证方式和接口描述。这意味着：

- 外部 A2A agent 可以通过标准的 A2A `agent Cards` 发现机制找到 AgentDM 侧的 agent
- 来自外部 A2A 系统的任务请求会被 AgentDM 转换为 MCP 工具调用，投递给目标 MCP agent
- MCP agent 响应时，AgentDM 再将响应映射回 A2A 的 `Task Submit/Update` 消息格式

### 协议翻译的数据流

```
MCP Agent (@researcher)
    │ send_message("@analyst", "请分析Q1销售数据")
    ▼
AgentDM Grid Server (协议翻译层)
    │ 1. 查询目标 @analyst 的 A2A Agent Card
    │ 2. 将 MCP 消息体包装为 A2A TaskSubmitRequest
    ▼
A2A Agent (@analyst，运行在另一个组织)
    │ 处理任务，返回 TaskSubmitResponse
    ▼
AgentDM Grid Server (协议翻译层)
    │ 将 A2A 响应映射为 MCP 工具返回结果
    ▼
MCP Agent (@researcher)
    │ read_messages() 收取 @analyst 的响应
```

这个流程的关键设计在于：**MCP agent 完全不知道它在与 A2A agent 通信**。它只调用了 `send_message()`，而 AgentDM 处理了所有协议层的转换工作。

### 资源（Resources）和提示（Prompts）

除了工具，AgentDM 还通过 MCP Resources 接口暴露了两个只读数据源：

```
agentdm://agents
  → 列出当前账户下的所有 agent（带 @alias 和描述）
  
agentdm://channels
  → 列出所有频道及其成员
```

Prompts 方面提供了三个预构建工作流：`compose_message`（按语气起草）、`analyze_inbox`（按优先级摘要）和 `respond_to_message`（生成回复草稿）。这些是 MCP Prompts 规范的标准用法，适用于需要 agent 自动化处理收件箱的场景。

## 与现有方案的对比

从工程视角看，AgentDM 的核心价值主张是**零 SDK 集成**：不需要为每个目标 agent 写适配代码，只需要一个 MCP 配置项。

| 维度 | AgentDM | Shared Runtime (LangGraph) | Hub-Spoke (AutoGen) |
|------|---------|---------------------------|-------------------|
| 跨框架能力 | ✅ 任何 MCP client | ❌ 必须在同一进程 | ✅ 支持多框架 |
| 无需目标 agent 代码修改 | ✅ | ❌ 需要统一 SDK | ⚠️ 需要 hub SDK |
| 消息持久化 | ✅ 平台托管 | ❌（内存） | ❌（内存） |
| 协议标准化 | ✅ MCP+A2A | ❌ 私有协议 | ❌ 私有协议 |
| 延迟 | 中等（经过 AgentDM） | 最低（同进程） | 中等（有 hub 中转） |
| 供应商锁定 | ⚠️ 依赖 AgentDM 云 | 无 | 无 |

**笔者的判断**：AgentDM 本质上是一个受管理的消息中间件，用协议翻译换取了零集成成本。对于原型验证和跨组织 agent 通信场景，这是合理的工程取舍；但对于延迟敏感的生产系统，经过第三方服务器的消息路径会带来额外的网络跳数和供应商依赖风险，需要评估 SLA 是否可接受。

## 已知局限

1. **供应商锁定**：所有消息流经 AgentDM 的服务器。若平台出现可用性问题，agent 间通信即中断。文档声明 99.9% uptime SLA，但这是托管服务的风险。
2. **消息内容的可见性**：虽然官方声明不读取消息内容，但作为一个托管平台，技术上存在读取的可能性（即使做了传输加密，平台作为中间人仍可看到明文）。对消息内容敏感的场景不适用。
3. **A2A 功能依赖目标 agent 也支持 A2A**：如果目标 agent 不是 A2A-native，AgentDM 只能实现 MCP-to-MCP 的直接消息，不能提供完整的 A2A 能力（如任务状态流、Agent Card 发现）。
4. **认证机制**：目前支持 Bearer Token。生产级的企业认证（如 mTLS、OAuth 2.0）尚未在文档中明确说明。

## 快速启动

```json
// mcp_config.json（任何 MCP-compatible client 均适用）
{
  "mcpServers": {
    "agentdm": {
      "url": "https://api.agentdm.ai/mcp/v1/grid",
      "headers": {
        "Authorization": "Bearer <your-api-key>"
      }
    }
  }
}
```

1. 在 [app.agentdm.ai](https://app.agentdm.ai) 注册并创建 agent，获得 `@alias` 和 API key
2. 将上述配置添加到任意 MCP client（Claude Desktop、Cursor、Windsurf 等）
3. 通过 `send_message("@other-agent", "内容")` 直接发送消息

全程不需要安装任何 SDK，不需要写任何代码。

## 结论

AgentDM 的出现反映了一个真实的工程需求：当 agent 通信从单框架单进程扩展到跨组织、跨框架场景时，协议层的互操作性成为瓶颈。MCP 和 A2A 各司其职（工具调用 vs agent 间协调），但两者之间缺乏桥梁。AgentDM 尝试用"协议翻译中间件"解决这个问题。

它的工程取舍很清晰：用供应商依赖换取了零集成成本，用消息延迟换取了跨协议通信能力。这不是万能药，但对于跨组织 agent 通信、原型验证和 MCP-first 的多 agent 系统，是一条值得关注的路径。

> **工程建议**：在生产环境中评估 AgentDM 时，重点关注：(1) 消息内容的合规要求是否允许经过第三方平台；(2) AgentDM 的 SLA 是否满足你的可用性目标；(3) 目标协作 agent 是否原生支持 A2A（否则你只能得到一个更贵的 MCP 代理服务器）。

---

## 参考资料

- [AgentDM 官网](https://agentdm.ai/) — 产品介绍和文档
- [AgentDM – Agent to Agent Messaging over MCP and A2A (Show HN)](https://news.ycombinator.com/item?id=47703972) — Hacker News 讨论（2026-04-10）
- [A2A Protocol 规范 (GitHub)](https://github.com/a2aproject/A2A) — Google 主导的 Agent-to-Agent 通信协议规范
- [MCP 规范 (GitHub)](https://github.com/modelcontextprotocol/specification) — Anthropic 主导的 Model Context Protocol 规范
