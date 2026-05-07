# openai-agents-python：OpenAI 官方多 Agent 编排 SDK 的生产级实践

## Target（谁该关注）

- **水平**：有 Python 经验的 Agent 开发工程师，熟悉 OpenAI API 或 Anthropic Agent SDK
- **画像**：需要构建多 Agent 协作系统，但对 LangChain 等通用框架的复杂度感到冗余；或者从 Swarm/Handoff 实验转向生产级严肃架构的团队
- **前置条件**：Python 3.10+，对 Agent 概念有基本理解（Agent/Harness/Tool 的区分）

## Result（能带来什么）

> "Five primitives, a managed agent loop, MCP, tracing, sandbox agents, and an opinionated take on multi-agent orchestration."
> — [Antigravity Codes: OpenAI Agents Python SDK Guide](https://antigravity.codes/blog/openai-agents-python-guide)

具体能力：
- **Sandbox Agents**：隔离执行环境，Agent 生成的代码在沙箱中运行而非直接操作用户机器，适合长时任务和自动化场景
- **Handoffs**：Agent 之间的状态传递机制，让多 Agent 协作像接力棒一样传递上下文
- **Guardrails**：三层安全护栏（输入检查、输出检查、异常处理），企业级生产部署可用
- **MCP 完整支持**：Model Context Protocol 生态集成，连接外部工具和数据源
- **Tracing**：内置可观测性，调试多 Agent 状态流转

GitHub 热度：**685+ stars/day**（单日新增），属于 2026 年 GitHub Trending 高增长项目。

## Insight（凭什么做到）

OpenAI Agents SDK 不是又一个「LangChain 替代品」，而是 OpenAI 对**Agent 生产级基础设施**的官方答案。

### 设计哲学：Opinionated 而非 Configurable

OpenAI Agents SDK 的核心设计选择是**给你什么你就用什么**，而非提供一个让你组合一切的积木。

```
LangChain 思维：你自己组装 Agent + Memory + Tools + OutputParser + ...
OpenAI Agents SDK：给你一个完整的 Agent Loop，你只需要定义 Agent 和 Handoff 规则
```

> "Never gets serialised. Never reaches the model." — 这句话指出了问题所在：大多数框架让状态流经 LLM，但 LLM 不应该关心状态序列化。

OpenAI Agents SDK 解决了这个架构问题：**状态流转在模型之外完成**，LLM 只负责决策。

### Sandbox 的工程意义

Sandbox Agents 是该 SDK 与 Claude Code / Cursor 的核心差异点：

- **Claude Code/Cursor**：Agent 在用户本地环境运行（用户机器），有文件系统访问权限
- **OpenAI Agents SDK**：Agent 在云端沙箱运行，代码执行结果通过 API 返回

> "Sandbox agents, and an opinionated take on multi-agent orchestration." — 沙箱模式让 OpenAI Agents SDK 天然适合**无用户交互的长时自动化任务**，例如批量数据处理、自动化测试生成。

### Guardrails 的三层设计

```
Layer 1: InputGuardrail     — 检查用户输入是否合规
Layer 2: OutputGuardrail   — 检查模型输出是否合规  
Layer 3: ExceptionHandler  — 运行时异常的兜底处理
```

这种分层设计与 Anthropic 的 Harness 多层防御思路一致——**安全不是一次性的检查，而是多层次的纵深防御**。

## Evidence（拆解验证）

### 技术架构

OpenAI Agents SDK 的核心 primitive（5 个）：

```python
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput

# Primitives：
# 1. Agent — 定义单个 Agent 的指令和工具
# 2. Runner — 管理 Agent Loop，执行、恢复、追踪
# 3. Handoff — Agent 间状态传递
# 4. Guardrail — 输入/输出安全检查
# 5. Sandbox — 隔离执行环境
```

每个 primitive 的设计都指向**生产级严肃架构**而非实验性原型。

### 与竞品对比

| 框架 | 定位 | Sandbox | Guardrails | MCP |
|------|------|---------|------------|-----|
| **OpenAI Agents SDK** | 官方生产级 SDK | ✅ 原生 | ✅ 三层 | ✅ 完整 |
| **LangGraph** | 通用复杂编排 | ❌ 自行实现 | ❌ 自行实现 | ⚠️ 有限 |
| **CrewAI** | 多角色 Agent | ❌ 自行实现 | ❌ 自行实现 | ⚠️ 有限 |
| **AutoGen** | 对话式 Agent | ❌ 自行实现 | ❌ 自行实现 | ❌ |

### 实际使用场景

OpenAI Agents SDK 的典型场景：

1. **企业内部自动化**：客服 Agent + 知识库检索 Agent + 订单 Agent 协作，每类 Agent 专注单一职责，通过 Handoff 协作
2. **代码审查流水线**：Reviewer Agent（检查逻辑）+ Linter Agent（检查风格）+ Security Agent（检查漏洞），流水线并行执行
3. **长时数据处理**：Sandbox Agent 在隔离环境中执行 ETL，不影响用户机器

## Threshold（行动引导）

### 快速上手（3 步）

```bash
# 1. 安装
pip install openai-agents-python

# 2. 定义 Agent
from agents import Agent
agent = Agent(name="assistant", instructions="You are a helpful assistant.")

# 3. 运行
from agents import Runner
result = Runner.run(agent, input="Hello!")
```

### 贡献入口

OpenAI Agents SDK 是 OpenAI 官方的生产级项目，适合以下贡献方向：
- MCP 服务器集成（官方列表未覆盖的工具生态）
- Guardrail 规则库（行业特定的合规检查规则）
- Sandbox 环境适配（Docker/Kubernetes 集成）

### 路线图

根据 [OpenAI Agents SDK 官方文档](https://openai.github.io/openai-agents-python/)，SDK 正在向**企业级可观测性**方向迭代，包括：
- OpenTelemetry 原生集成
- 多租户隔离
- 持久化 Session 管理

## 关联主题

本文与 **Cursor Dynamic Context Discovery** 关联：两者都是 2026 年 Agent 工程实践的代表作——Cursor 解决「Context 如何高效管理」的问题，OpenAI Agents SDK 解决「多 Agent 如何安全协作」的问题。两者共同指向 **Agent 生产级基础设施** 这一核心主题。

> 官方原文引用：
> "Five primitives, a managed agent loop, MCP, tracing, sandbox agents, and an opinionated take on multi-agent orchestration."
> — [Antigravity Codes: OpenAI Agents Python SDK Guide](https://antigravity.codes/blog/openai-agents-python-guide)
