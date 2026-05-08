# doobidoo/mcp-memory-service: 多框架统一的 Agent 持久记忆后端

> 项目地址：https://github.com/doobidoo/mcp-memory-service
> GitHub: 1,811 ⭐ | Python | Apache-2.0 | v10.50.0

## 定位破题

**谁该关注**：使用 LangGraph / CrewAI / AutoGen 构建复杂 Agent 管道的团队，或需要跨会话共享记忆的独立 Agent（Claude Desktop / Cursor / OpenCode）。

**解决什么问题**：每个 Agent run 从零开始 → Agents 在 5ms 内检索先前决策，实现多 Agent 跨管道共享因果知识图谱。

**差异化标签**：唯一一个同时支持 REST API + MCP + OAuth 2.0 + CLI + Web Dashboard 的自托管记忆服务，支持 Remote MCP（可在浏览器端 claude.ai 使用）。

---

## 体验式介绍

当你用 CrewAI 构建多 Agent 协作系统时，每个 Agent 的记忆是独立的。任务 A 的 Agent 学到的知识，任务 B 的 Agent 无法复用。传统的解法是给每个 Agent 接 Redis + Pinecone，然后写一堆 glue code。

**mcp-memory-service 的体验**：你只需启动一个服务：

```bash
pip install mcp-memory-service
python -m mcp_memory_service.server
```

然后在你的 LangGraph Agent 中：

```python
from mcp_memory_service import MemoryService

memory = MemoryService()

# Agent 做决策时存储
memory.store_decision(
    agent_id="planner",
    decision="选择使用索引扫描而非全表扫描",
    context={"query": "...", "table_size": "10M rows"},
    tags=["query-optimization", "postgres"]
)

# 另一个 Agent 在 5ms 内检索相关记忆
context = memory.retrieve(
    query="postgres query optimization",
    agent_id="executor",
    limit=5
)
```

**"哇时刻"**：5ms 检索延迟 + 因果知识图谱 + 自研推理路径记录——Agent 不是简单地存储文本，而是存储决策链路（包括"为什么选择 A 而非 B"），这让 Agent 的推理可解释、可追溯。

---

## 拆解验证

### 核心技术设计

**三层存储架构**：
1. **向量嵌入**（Semantic Search）：基于文本相似性检索
2. **因果知识图谱**（Causal KG）：存储"因为 X 所以 Y"的决策链路
3. **标引存储**（Tag + Metadata）：快速精确查找

**多框架适配**：

> "Works with LangGraph · CrewAI · AutoGen · any HTTP client · Claude Desktop · OpenCode"

每个框架的集成方式：
- **LangGraph**：通过 Python SDK 直接调用
- **CrewAI**：MCP Tool 接口
- **AutoGen**：HTTP client + REST API
- **Claude Desktop**：本地 MCP Server
- **Cursor**：MCP Server 集成
- **OpenCode**：远程 MCP 支持

### 传输层全覆盖

mcp-memory-service 的独特之处是支持所有主流传输协议：

| 协议 | 用途 | 场景 |
|------|------|------|
| REST API | 任何 HTTP 客户端 | 通用集成 |
| MCP (Model Context Protocol) | Claude/Cursor/OpenCode 桌面集成 | 本地 Agent |
| MCP Streamable HTTP | Remote MCP | 浏览器端 claude.ai |
| SSE (Server-Sent Events) | 实时推送 | Dashboard |
| OAuth 2.0 + DCR | 企业认证 | 自托管生产环境 |

### 远程 MCP 的突破

大多数 MCP Server 只能用于桌面应用（如 Claude Desktop），但 mcp-memory-service 支持 Remote MCP，这意味着：

> "✅ Use persistent memory directly in your browser (no Claude Desktop required)
> ✅ Works on any device (laptop, tablet, phone)
> ✅ Enterprise-ready (OAuth 2.0 + HTTPS + CORS)
> ✅ Self-hosted OR cloud-hosted (your choice)"

这是工程上的突破——让浏览器的 Claude.ai 能够访问需要自托管的企业记忆服务。

### 与 Cursor App Stability 的主题关联

Cursor 的文章强调本地 Agent 的内存限制（本地开发机遇到 OOM），而 mcp-memory-service 的远程 MCP 能力正好提供了另一种路径：**不依赖本地资源，将记忆层外部化到独立服务**。

这与 Cursor Engineering 的理念形成互补：
- Cursor：通过 Cloud Agents 突破本地资源天花板
- mcp-memory-service：通过远程 MCP 将记忆层从 Agent 进程解耦

两者共同指向同一个工程目标：**让 Agent 不受本地资源限制地运行**。

### 社区健康度

- **版本活跃度**：v10.50.0（最新 release 为 v10.49.x 序列），说明维护活跃
- **Issue 响应**：5 个 open issues，团队定期处理
- **下载量**：PyPI 持续有下载量
- **文档完善度**：完整的 Remote MCP Setup Guide、OAuth Setup、5-Minute Tutorial

---

## 行动引导

### 快速上手（3 步）

```bash
# Step 1: 安装
pip install mcp-memory-service

# Step 2: 启动服务（默认 localhost:8765）
python -m mcp_memory_service.server

# Step 3: 在你的 Agent 中集成
# Python: from mcp_memory_service import MemoryService
# Claude Desktop: 在 MCP Server 配置中指向 localhost:8765
```

### 进阶：Remote MCP（浏览器端 claude.ai）

```bash
# 启动带 Remote MCP 的服务
MCP_STREAMABLE_HTTP_MODE=1 MCP_SSE_PORT=8765 python -m mcp_memory_service.server

# 用 Cloudflare Tunnel 暴露（获得 HTTPS）
cloudflared tunnel --url http://localhost:8765

# 在 claude.ai Settings → Connectors → Add Connector
```

### 生产部署

- **OAuth 2.0 + DCR**：企业级认证
- **Let's Encrypt**：自动 HTTPS 证书
- **Docker Compose**：一键部署
- **监控**：内置 Dashboard + 语义搜索 + API docs

---

## 竞品对比

| 项目 | 协议支持 | 多框架 | 远程 MCP | 因果 KG | 自托管 |
|------|---------|--------|----------|---------|-------|
| **mcp-memory-service** | REST+MCP+SSE | LangGraph/CrewAI/AutoGen | ✅ | ✅ | ✅ |
| LangChain Memory | 仅 Python SDK | 仅 LangChain | ❌ | ❌ | ✅ |
| Redis + Pinecone | 自定义 API | 自定义 | ❌ | ❌ | ✅ |
| Claude Memory (云) | 官方 API | 仅 Claude | ❌ | ❌ | ❌（商业闭源）|

---

## 一句话总结

**mcp-memory-service 是多 Agent 协作的记忆基础设施**：1,811 ⭐，支持 REST/MCP 双协议，5ms 检索因果知识图谱，让任何框架的 Agent 跨会话共享决策上下文。

**关联文章**：[Cursor App Stability Engineering](../harness/cursor-app-stability-engineering-oom-reduction-2026.md) — 本地资源约束下的 Agent 稳定性问题，与远程 MCP 的解耦思路形成互补。

---

**引用来源**：
- [GitHub: doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service)
- [Remote MCP Setup Guide](https://github.com/doobidoo/mcp-memory-service/blob/master/docs/remote-mcp-setup.md)
- [5-Minute claude.ai Setup Tutorial](https://doobidoo.github.io/mcp-memory-service/blog/remote-mcp-tutorial.html)