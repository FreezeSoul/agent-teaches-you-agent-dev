# SurePath AI 推出 MCP 策略控制：企业级 MCP 安全治理

**发布时间**：2026-03-12  
**来源**：[PRNewswire](https://www.prnewswire.com/news-releases/surepath-ai-advances-real-time-model-context-protocol-mcp-policy-controls-to-govern-ai-actions-302709875.html)

## 背景

随着 MCP 协议快速成为 AI 工作流的核心支柱，SurePath AI 指出：企业正在重蹈 ChatGPT 早期"快速采纳、缺乏监督"的覆辙。MCP 打开了从生成式 AI 客户端到企业核心系统的直接通路，引入了全新的攻击面。

## 核心能力：MCP Policy Controls

### 本地 MCP 管控
- **MCP Tool Discovery**：通过拦截 MCP payload 监控 AI 工具中的 MCP 使用情况，自动移除违反策略或能力要求的工具（如非只读工具）
- **MCP Tool Block List**：明确封禁特定 MCP 工具，从 payload 中移除后再到达后端服务
- **MCP Tool Allow List**：白名单机制，确保特定工具始终可用
- **Allow Read-Only**：自动放行所有只读 MCP 工具，简化低风险工具策略管理

### 远程 MCP 安全
- 维护已知 MCP 服务器与端点的目录catalog
- 所有受保护的 MCP 流量必须经过 SurePath AI 平台，在传输层应用访问控制
- **供应链威胁检测**：识别冒充合法工具或试图数据外泄的未知 MCP 工具

## 安全警示

> "MCP 是从生成式 AI 客户端到企业运营系统的直接通道。AI 现在可以代表最终用户发出真实命令并完成身份认证……多个 Agent 连接混合的本地和远程 MCP 服务器，可能造成数据横移和蔓延的混乱路径。"

## 对 Agent 工程的意义

这是首个企业级 MCP 安全产品，表明 MCP 已被主流企业采纳但同时面临严峻安全挑战。与 NIST AI Agent Standards Initiative（2026-03-19）形成呼应：治理与安全正在成为 Agent 生产部署的基础设施需求。

> 来源：[SurePath AI PR](https://www.prnewswire.com/news-releases/surepath-ai-advances-real-time-model-context-protocol-mcp-policy-controls-to-govern-ai-actions-302709875.html)
