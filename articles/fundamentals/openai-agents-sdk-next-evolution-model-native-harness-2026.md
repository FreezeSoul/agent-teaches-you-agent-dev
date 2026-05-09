# OpenAI Agents SDK 下一代进化：Model-Native Harness 与 Native Sandbox

> **核心主张**：OpenAI Agents SDK 的这次更新标志着"model-provider SDK"和"model-agnostic framework"之间的界限正在消失——两家最大的 AI 提供商正在向同一套工程范式收敛：分层 Harness + 可组合 Sandboxes + Skills 抽象。

**来源**：[OpenAI Blog: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)（2026-05）

---

## 一、问题域：为什么现有 Agent 系统都有 Trade-off

在深入分析 OpenAI 的新方案之前，需要先理解一个根本性问题：为什么 Agent 系统难以同时兼顾**灵活性**、**模型原生能力**和**生产级可靠性**？

OpenAI 博客原文指出了这个核心矛盾：

> "The systems that exist today come with tradeoffs as teams move from prototypes to production. Model-agnostic frameworks are flexible but do not fully utilize frontier model capabilities; model-provider SDKs can be closer to the model but often lack enough visibility into the harness; and managed agent APIs can simplify deployment but constrain where agents run and how they access sensitive data."

这段话揭示了三类系统的本质问题：

| 系统类型 | 核心优势 | 根本缺陷 |
|---------|---------|---------|
| Model-agnostic frameworks（如 LangChain） | 灵活性高，绑定任何模型 | 无法充分利用前沿模型特性 |
| Model-provider SDKs（如旧版 OpenAI Agents SDK） | 与模型更贴近 | 对 Harness 内部可见性不足 |
| Managed Agent APIs（如 Claude.ai） | 部署简单 | 约束运行环境，访问敏感数据受限 |

这三种 Trade-off 本质上源于**分层职责的混淆**——当一个系统试图同时解决"如何调用模型"和"如何管理 Agent 执行"两个问题时，必然在某一方做出牺牲。

---

## 二、解法：Harness 与 Compute 的分离

OpenAI 提出的核心解决方案是**将 Harness 层与 Compute 层彻底分离**：

> "Separating harness and compute helps keep credentials out of environments where model-generated code executes."

这个设计原则解决了三个核心问题：

### 2.1 安全：凭证不进入模型代码执行环境

在传统架构中，Agent 的工具调用（如访问数据库、调用外部 API）往往需要携带凭证。如果这些凭证存在于 Agent 的执行环境中，就存在被模型生成的代码意外泄露的风险。

通过分离设计：
- **Harness 层**：持有敏感凭证，负责决策和编排
- **Compute 层（Sandbox）**：只负责执行模型生成的代码，无法直接访问凭证

### 2.2 持久性：状态外部化与快照恢复

> "When the agent's state is externalized, losing a sandbox container does not mean losing the run. With built-in snapshotting and rehydration, the Agents SDK can restore the agent's state in a fresh container and continue from the last checkpoint if the original environment fails or expires."

这对长程 Agent 至关重要。当 Agent 执行一个需要数小时的任务时，如果容器崩溃导致状态丢失，整个任务需要从头开始。快照恢复机制允许 Agent 在新容器中从上次checkpoint继续。

### 2.3 可扩展性：动态沙箱分配

> "Agent runs can use one sandbox or many, invoke sandboxes only when needed, route subagents to isolated environments, and parallelize work across containers for faster execution."

一个 Agent 可以根据任务需求动态申请多个沙箱并行工作，或者将子 Agent 路由到隔离环境。

---

## 三、新增能力详解

### 3.1 可配置的 Memory

OpenAI 明确提到：

> "The updated Agents SDK harness becomes more capable for agents that work with documents, files, and systems. It now has configurable memory, sandbox-aware orchestration, Codex-like filesystem tools, and standardized integrations with primitives that are becoming common in frontier agent systems."

这里的"configurable memory"呼应了 OpenAI 前不久发布的 Codex Agent Loop 文章中的 Compaction 机制。但这次是在 SDK 层面的原生支持，而非用户自己实现。

### 3.2 Sandbox-Aware Orchestration

这是 OpenAI 提出的一个新概念。与传统将 Sandbox 视为黑盒不同，Sandbox-aware 意味着 Harness 能够理解 Sandbox 的状态，并据此做出编排决策。例如：

- 检测到某个 Sandbox 的资源即将耗尽，主动将任务迁移到新 Sandbox
- 根据任务性质选择不同隔离级别的 Sandbox（Kata Containers vs 轻量级容器）
- 在 Sandbox 之间传递状态和上下文

### 3.3 Codex-Like Filesystem Tools

Codex 是 OpenAI 的 AI 编程产品，其文件系统工具体验经过了大量生产验证。OpenAI 将这套工具集成到 Agents SDK 中，让所有基于该 SDK 的 Agent 都能获得同等的文件操作能力。

### 3.4 Primitive 标准化集成

> "These primitives include tool use via MCP, progressive disclosure via skills, custom instructions via AGENTS.md, code execution using the shell tool, file edits using the apply patch tool, and more."

注意这里的并列关系：**MCP**、**Skills**、**AGENTS.md** 被放在了同一层级，作为"frontier agent systems 的标准化原语"。这意味着 OpenAI 认可了 Skills 作为 Agent 能力扩展的标准方式——与 Anthropic 的 Agent Skills 方案不谋而合。

---

## 四、Native Sandbox 执行

### 4.1 七家官方支持

> "Developers can bring their own sandbox or use built-in support for Blaxel, Cloudflare, Daytona, E2B, Modal, Runloop, and Vercel."

这个列表涵盖了主流的云端沙箱提供商：
- **E2B**：最成熟的 AI Agent 沙箱运行时
- **Cloudflare**：边缘计算沙箱
- **Modal**：灵活的无服务器计算
- **Vercel**：前端/全栈部署平台

### 4.2 Manifest 抽象

> "To make those environments portable across providers, the SDK also introduces a Manifest abstraction for describing the agent's workspace."

Manifest 是 OpenAI 提出的一个关键抽象——它描述了 Agent 工作空间的结构，使得相同配置可以在不同沙箱提供商之间迁移。

Manifest 可以定义：
- 挂载的本地文件
- 输出目录位置
- 外部存储数据源（AWS S3、GCS、Azure Blob、Cloudflare R2）

### 4.3 便携性保障

> "This gives developers a consistent way to shape the agent's environment from local prototype to production deployment. It also gives the model a predictable workspace: where to find inputs, where to write outputs, and how to keep work organized across a long-running task."

这个设计解决了"本地开发 vs 生产部署"的环境一致性问题——同一套 Manifest 配置，既能在本地调试，又能在云端运行。

---

## 五、与 Anthropic 方案的横向对比

| 维度 | OpenAI Agents SDK（新） | Anthropic Agent SDK |
|------|----------------------|---------------------|
| **Harness 定位** | Model-native，深度集成前沿模型特性 | Model-agnostic，但针对 Claude 优化 |
| **Sandbox 支持** | 7家官方支持 + Manifest 抽象 | 通过 Agent SDK 的 Tool 抽象 |
| **Memory** | Configurable memory（SDK 层面） | Initializer + Coding Agent 双组件 |
| **持久化** | Snapshotting + Rehydration | Feature List + Progress File |
| **技能扩展** | Skills（与 Anthropic 相同术语） | Agent Skills（渐进式披露） |
| **多沙箱编排** | 原生支持 | 通过 Harness 设计间接支持 |
| **安全模型** | 凭证与执行分离 | 分层权限 + Auto Mode |

**关键观察**：Anthropic 和 OpenAI 正在向相同的工程范式收敛——都强调 Harness/Compute 分离、Skills 作为能力扩展标准、以及某种形式的检查点/持久化机制。

> 笔者认为：这种收敛不是偶然，而是"长程 Agent"作为场景对所有模型提供商的共同挑战。当 Agent 需要持续运行数小时、处理复杂任务、访问多种工具时，同样的工程问题（状态管理、安全隔离、资源调度）必然导致相似的解决方案。

---

## 六、Python First，TypeScript 稍后

> "The new harness and sandbox capabilities are launching first in Python, with TypeScript support planned for a future release."

这个发布策略反映了 OpenAI 的优先级——Python 仍然是 AI/ML 领域的主流语言，而 TypeScript 的支持意味着这些能力最终会进入前端/全栈开发场景。

---

## 七、启示与行动建议

### 7.1 对于 Agent 框架开发者

**Harness/Compute 分离**应该成为核心设计原则，而不是事后补救的安全加固。这意味着：
- 从架构层面将凭证管理和代码执行解耦
- 实现状态外部化，支持故障恢复
- 设计标准化的沙箱接口，支持多提供商

### 7.2 对于 Agent 使用者

关注 SDK 的**模型原生程度**——同样一个框架，对不同模型的优化程度可能差异巨大。Model-provider SDK（如 OpenAI Agents SDK）往往能更充分利用模型特性，但会牺牲一些灵活性。

### 7.3 对于 AI Coding 场景

Codex-like filesystem tools 进入 SDK 意味着：标准化文件操作能力正在成为所有 Agent 的标配，而非某个产品的独占特性。这对多 Agent 协作场景有重要意义——统一的文件系统抽象让 Agent 之间的协作更简单。

---

## 总结

OpenAI Agents SDK 的这次更新，本质上是将 Codex（OpenAI 的 AI 编程产品）中经过生产验证的工程实践标准化、并入通用 SDK。其核心贡献是：

1. **Harness/Compute 分离**的安全与可扩展性模型
2. **Manifest 抽象**的跨提供商便携性
3. **Skills/MCP/AGENTS.md** 作为 frontier agent primitives 的标准化确认

这些设计与 Anthropic 的方案高度收敛，标志着 Agent 工程正在形成一套公认的范式。

---

**关联阅读**：
- [Anthropic Engineering: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents-2024)
- [OpenAI Blog: Unrolling the Codex Agent Loop](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

*本文属于"AI Coding 工具链"系列，关注生产级 Agent 的工程实践。*