# MCP: Model Context Pitfalls in an Agentic World

> 来源：HiddenLayer（安全研究机构）
> 评分：4/5（实践 4 / 独特 4 / 质量 4）

## 核心观点

1. **权限管理缺陷**：MCP 依赖工具权限，但许多实现没有一致的用户审批机制——「一次授权，永不追问」，即使工具使用方式发生变化也不会重新提示。

2. **攻击面分析**：
   - **工具 typo 劫持**：攻击者注册与可信工具名称相似的恶意 MCP 服务器
   - **间接 prompt injection**：在共享文档中隐藏恶意命令
   - **工具组合泄漏**：多个工具组合使用可导致文件泄漏

3. **生产环境现状**：55 个独特服务器横跨 187 个实例，涵盖 Gmail、Google Drive、Jira、Supabase、YouTube，甚至开放 Postgres 服务器——安全机制普遍缺失。

4. **核心问题**：OpenAI Agent SDK 的 MCP 支持仅接受服务器列表，没有任何授权机制，授权完全依赖应用开发者实现。

## 独特价值

1. **安全公司视角**：非官方、独立的安全研究机构评估
2. **具体攻击场景**：每种攻击方式有实际案例支撑
3. **「ticking time bombs」比喻**：从业者视角的警告，而非技术宣传

## 一句话总结

> 安全公司揭秘 MCP 四大隐患：权限一次过、typo 劫持、prompt injection、工具组合泄漏——生产部署前必读。

## 原文

https://www.hiddenlayer.com/research/mcp-model-context-pitfalls-in-an-agentic-world

## 标签

#community #MCP #security #HiddenLayer #production-risks
