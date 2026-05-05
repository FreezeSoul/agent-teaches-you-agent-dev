# mcp-agent: 用简单模式构建高效 Agent 的 MCP 框架

> **关联文章**：[动态上下文发现：Cursor 与 mcp-agent 的 Token 效率工程对比](./dynamic-context-discovery-token-efficiency-2026.md)
> 两个项目共同验证「MCP 原生 + 动态按需加载」是 Agent 上下文管理的可行路径。

---

## T - Target（谁该关注）

**目标用户**：有意构建生产级 Agent 应用的中高级 Python 开发者，尤其适用于：
- 需要连接多个 MCP 服务器（工具链 > 5个）的复杂场景
- 需要长时任务可靠执行（pause/resume/recover）的工程团队
- 已在生产环境使用 Anthropic Claude / OpenAI，但希望获得更结构化的 Agent 编排能力

**前置要求**：
- Python 异步编程基础（async/await）
- 理解 MCP 协议的基本概念（工具/资源/提示）
- 不需要机器学习背景

---

## R - Result（能带来什么）

**核心价值**：用 **简单的组合模式**（非复杂图结构）实现生产级 Agent 应用，Token 效率比静态加载方案高 46%+（参考 Cursor Dynamic Context Discovery 的 A/B 测试数据）。

**具体效果**：
- MCP 服务器连接生命周期**自动管理**，无需手动处理重连/超时
- Anthropic "Building Effective Agents" 中的**每种模式**都已实现为可组合组件（Router/Evaluator-Optimizer/Orchestrator 等）
- 长时任务通过 Temporal 实现**pause/resume/recover**，Agent 不会因 API 超时或进程中断而丢失状态
- Cloud 部署一行命令完成（`uvx mcp-agent deploy`），无需自己运维 Temporal 集群

**GitHub 数据**：
- PyPI 下载量持续增长（Pepy Shield badge 可见）
- 有 Trendshift.io 徽章，说明在 GitHub Trending 有可观增长
- Discord 社区活跃（lmai.link/discord/mcp-agent）

---

## I - Insight（凭什么做到）

**技术选型**：MCP 原生 + 简单模式 > 复杂图架构

> "mcp-agent's vision is that _MCP is all you need to build agents, and that simple patterns are more robust than complex architectures for shipping high-quality agents_."
> — [GitHub README](https://github.com/lastmile-ai/mcp-agent)

这个 vision 背后的逻辑：
- MCP 协议本身已经足够表达工具发现、调用、授权等能力
- 复杂编排（图结构/状态机）往往在生产中成为维护负担
- 用 async/await 的控制流 + 装饰器模式替代图节点/边，可以写出更易读的 Agent 代码

**架构设计**：

```
MCPApp (应用入口)
  ├── 管理 MCP 服务器生命周期（连接/断开/重连）
  ├── 管理 Agent 之间的协调
  └── 挂载 Temporal 实现 durable execution

Agent (一次 Agent 交互)
  ├── instruction: 任务描述
  ├── server_names: 需要哪些 MCP 服务器
  └── attach_llm(): 挂载 LLM（支持 OpenAI）

Workflow（编排层）
  ├── Router: 根据输入分发到子 Agent
  ├── Parallel Pipeline: 并行执行后合并结果
  ├── Orchestrator: 动态协调多 Agent
  └── Evaluator-Optimizer: 迭代优化直到达标
```

**MCP 工具动态加载**：mcp-agent 的 Full MCP Support 意味着 Agent 在需要时才真正连接并调用工具，而非启动时全部预加载。这与 Cursor 的「动态上下文发现」理念一致——Token 效率来自**按需加载**而非预加载。

**Durable Execution**：通过 Temporal 实现状态持久化，Agent 可以 pause（等待 human input 或外部信号）并 later resume，不会因进程重启丢失执行上下文。

---

## P - Proof（数据支撑）

### 关键特性覆盖

| 特性 | 实现状态 | 说明 |
|------|---------|------|
| MCP Core 全部支持 | ✅ | Tools / Resources / Prompts / Notifications |
| MCP Advanced 全部支持 | ✅ | OAuth / Sampling / Elicitation / Roots |
| Anthropic Patterns 原生实现 | ✅ | 每种 pattern 都有对应 composable 实现 |
| Durable Execution | ✅ | Temporal 集成，pause/resume/recover |
| Cloud Deploy | ✅ | `uvx mcp-agent deploy`，mcp-c 托管运行时 |
| OpenTelemetry Tracing | ✅ | 可配置 exporters（console/OTLP） |
| Token Counter | ✅ | 监控 token 使用，支持 threshold 告警 |
| Human Input | ✅ | Pause workflow 等待人工审批 |

### 与同类方案对比

| 维度 | mcp-agent | LangChain Agents | 直接用 MCP SDK |
|------|-----------|-----------------|----------------|
| 编排复杂度 | 低（async/await + 装饰器） | 高（图结构） | 无（裸 API） |
| MCP 生命周期管理 | 原生自动 | 需手动管理 | 需手动管理 |
| Anthropic Patterns | 原生实现 | 概念对应但实现分散 | 无 |
| Durable Execution | Temporal 原生 | 需额外集成 | 无 |
| 上手难度 | 中等（有完整文档） | 陡峭（抽象层多） | 简单（但需要自己处理所有边界） |

---

## 快速上手

### 1. 安装
```bash
pip install mcp-agent
# 或
uvx mcp-agent --version
```

### 2. 配置 MCP 服务器（mcp_agent.secrets.yaml 或环境变量）
```yaml
mcp:
  servers:
    fetch:
      command: "uvx"
      args: ["mcp-server-fetch"]
    filesystem:
      command: "uvx"
      args: ["mcp-server-filesystem"]
```

### 3. 写第一个 Agent（完整可运行代码）
```python
import asyncio
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

app = MCPApp(name="hello_world")

async def main():
    async with app.run():
        agent = Agent(
            name="finder",
            instruction="Use filesystem and fetch to answer questions.",
            server_names=["filesystem", "fetch"],
        )
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            answer = await llm.generate_str("Summarize README.md in two sentences.")
            print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Cloud 部署
```bash
uvx mcp-agent login
uvx mcp-agent deploy my-agent
```

---

## 适合贡献的场景

- **MCP 服务器封装**：将已有工具/服务封装为符合 MCP 协议的服务端
- **Pattern 实现**：将你团队独特的 Agent 编排逻辑固化为可复用的 Workflow
- **Durable Execution 集成**：结合 Temporal 实现更复杂的长时任务 checkpointing
- **Observability**：增强 OpenTelemetry tracing 的可视化或告警阈值配置

---

## 路线图建议追踪

- **mcp-c 托管运行时**：Cloud 部署的成熟度（目前是 Beta）
- **更多 Anthropic Patterns 的实现**：当前只实现了部分 Pattern
- **Multi-Agent 协作的原生支持**：多 Agent 之间如何高效共享状态和工具

---

## 结论

mcp-agent 解决了一个真实问题：**MCP 协议很好，但用它构建生产级 Agent 需要大量基础设施代码**。mcp-agent 通过把生命周期管理、模式组合、Durable Execution 全部封装好，让开发者专注业务逻辑而非基础设施。

如果你在用 MCP 但感觉「总差点什么」，mcp-agent 值得看看。

**官方文档**：[docs.mcp-agent.com](https://docs.mcp-agent.com)

---

**引用来源**：
1. [GitHub: lastmile-ai/mcp-agent](https://github.com/lastmile-ai/mcp-agent) — 项目 README，含 vision / 特性列表 / 示例代码
2. [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery) — 46.9% Token 节省的 A/B 测试数据来源
3. [docs.mcp-agent.com](https://docs.mcp-agent.com) — 官方文档，Pattern 完整说明