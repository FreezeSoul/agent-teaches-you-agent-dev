# awesome-harness-engineering：AI-Boost 维护的 Harness Engineering 聚合知识库

## 来源

- **原始链接**：https://github.com/ai-boost/awesome-harness-engineering
- **维护方**：ai-boost
- **许可证**：CC0（公共领域贡献）
- **引用来源**：GitHub README

---

## 项目概述

awesome-harness-engineering 是一个围绕 **Harness Engineering** 这一新兴工程学科的精选资源列表，聚焦于设计 AI Agent 支架（scaffolding）的工具、模式、评估、内存、MCP、权限、可观测性和编排。

> "Harness engineering is the discipline of designing the scaffolding — context delivery, tool interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds an AI agent and determines whether it succeeds or fails on real tasks."

项目的核心观点：**本文档聚焦于 harness，而非模型**。每一个组件的存在都是因为模型本身无法单独完成这些任务——而最好的 harness 设计会预判这些组件将随着模型能力的提升逐渐变得不再必要。

---

## 目录结构

项目将资源按以下维度组织：

| 分类 | 说明 |
|------|------|
| **Foundations** | 定义 harness 工程是什么、为什么重要的经典文献 |
| **Design Primitives** | Agent Loop、Planning、Context Delivery、Tool Design 等核心设计原语 |
| **Skills & MCP** | MCP (Model Context Protocol) 相关资源 |
| **Permissions & Authorization** | 权限与授权系统设计 |
| **Memory & State** | 记忆与状态管理 |
| **Task Runners & Orchestration** | 任务运行器与编排 |
| **Verification & CI Integration** | 验证与 CI 集成 |
| **Observability & Tracing** | 可观测性与追踪 |
| **Debugging & Developer Experience** | 调试与开发者体验 |
| **Human-in-the-Loop** | 人在回路 |
| **Reference Implementations** | 参考实现 |
| **Security, Sandbox & Permissions** | 安全、沙箱与权限 |
| **Evals & Verification** | 评估与验证 |
| **Templates** | 模板（如 AGENTS.md） |

---

## 核心 Foundation 文章摘录

### 1. OpenAI Harness Engineering

> "Harness engineering as a discipline: how to design the scaffolding that lets Codex and similar agents operate reliably in an agent-first world."

### 2. Anthropic "Building Effective Agents"

Anthropic 的 Agent 架构基础指南，覆盖：
- 何时使用 Workflow vs. Agent
- 如何组合原语

### 3. Martin Fowler "Harness Engineering"

> "Three interlocking systems — context engineering (curating what the agent knows), architectural constraints (deterministic linters and structural tests), and entropy management (periodic agents that repair documentation drift)."

### 4. LangChain "The Anatomy of an Agent Harness"

LangChain 将 harness 分解为五个原语：
- **Filesystem**：持久化状态 + Agent 协作面
- **Code Execution**：无需预设计解决方案的自主问题解决
- **Sandbox**：隔离 + 验证
- **Memory**：跨会话持久化
- **Context Management**：对抗"上下文腐烂"的压缩

### 5. Microsoft "How We Build Azure SRE Agent"

> "35,000+ production incidents autonomously handled, reducing time-to-mitigation from 40.5 hours to 3 minutes."

---

## 重点资源推荐

### Reference Implementations

| 项目 | 说明 | 亮点 |
|------|------|------|
| **AutoAgent** (kevinrgu/autoagent) | 2026 年 4 月开源，自动化 harness 工程循环 | 给定任务和基准，自动化迭代 system prompts、tool 配置、agent 编排 |
| **OpenHands** | 最架构完整的开源 coding agent | Runtime/Sandbox 隔离、EventStream 消息总线、Agent Controller 三层 harness 设计 |
| **VoltAgent/awesome-ai-agent-papers** | 363+ 篇 2026 年 arXiv 论文 | 按 Multi-Agent (51)、Memory & RAG (56)、Eval & Observability (79)、Agent Tooling (95)、AI Agent Security (82) 分类 |
| **bradAGI/awesome-cli-coding-agents** | 80+ 终端原生 AI coding agents 目录 | 含 session managers、parallel runners、autonomous loop infrastructure、credential vaults |

### Templates

| 模板 | 说明 |
|------|------|
| **AGENTS.md** | 项目级 agent 指令规范：约定、约束、工具权限 |

---

## 与本仓库的关联

本项目与 Agent Engineering 仓库的 `harness/` 和 `frameworks/` 目录高度相关：

1. **harness/ 目录补充**：awesome-harness-engineering 的分类框架可以补充 harness/ 目录的索引结构
2. **Foundations 文献**：Anthropic/OpenAI/LangChain 的 harness 基础文章适合作为 harness/ 目录的核心参考文献
3. **Microsoft Azure SRE Agent 案例**：可与已有的 Azure SRE Agent 相关文章形成生产级案例对比

---

## 相关文献

- [awesome-harness-engineering GitHub](https://github.com/ai-boost/awesome-harness-engineering)
- [AGENTS.md 模板](https://github.com/ai-boost/awesome-harness-engineering/blob/main/templates/AGENTS.md)
- [Anthropic Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)
- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)

---

*本篇由 AgentKeeper 自动整理，来源：GitHub awesome-harness-engineering（ai-boost，CC0 许可证）*
