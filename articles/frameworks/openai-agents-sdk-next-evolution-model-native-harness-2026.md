# OpenAI Agents SDK Next Evolution：Model-Native Harness 与 Native Sandbox Execution

## 来源

- **原始链接**：https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- **发布时间**：2026 年 4 月
- **官方标题**：The next evolution of the Agents SDK
- **引用来源**：OpenAI 官方开发者博客

---

## 核心摘要

OpenAI 发布了 Agents SDK 的重大更新，引入两个核心能力：**Model-Native Harness** 和 **Native Sandbox Execution**。前者让 agent 的执行模式与模型的自然运作模式对齐，后者提供内置的沙箱执行环境。

> "We’re introducing new capabilities to the Agents SDK that give developers standardized infrastructure that is easy to get started with and is built correctly for OpenAI models: a model-native harness that lets agents work across files and tools on a computer, plus native sandbox execution for running that work safely."

---

## 一、背景：现有 Agent 系统的 tradeoff

OpenAI 在文章中指出了当前 Agent 系统范式的三种选择及其局限：

| 方案 | 优点 | 缺点 |
|------|------|------|
| Model-agnostic 框架 | 灵活性高 | 无法充分利用前沿模型能力 |
| Model-provider SDK | 接近模型 | 对 harness 缺乏足够可见性 |
| Managed Agent API | 简化部署 | 约束 agent 运行位置和数据访问方式 |

OpenAI 认为这三者之间的 tradeoff 源于**基础设施的缺失**——开发者需要的是一套"模型原生"的标准基础设施，而不是在灵活性与能力之间妥协。

---

## 二、Model-Native Harness

### 设计目标

Harness 是 agent 的执行环境（指令、工具、权限、追踪）。OpenAI 新版 harness 的核心目标：

> "The harness also helps developers unlock more of a frontier model's capability by aligning execution with the way those models perform best."

即让 agent 的执行模式与模型表现最好的方式对齐，使 agent 更接近模型的自然运作模式，提高复杂任务的可靠性和性能。

### 核心原语（Primitives）

Harness 整合了逐渐成为前沿 Agent 系统标准的原语：

| 原语 | 技术实现 | 说明 |
|------|----------|------|
| **Tool Use** | MCP (Model Context Protocol) | 通过 MCP 协议使用工具 |
| **渐进式披露** | Skills (agentskills.io) | 通过技能实现能力渐进披露 |
| **自定义指令** | AGENTS.md | 项目级 agent 指令规范 |
| **代码执行** | Shell Tool | 通过 shell 工具执行代码 |
| **文件编辑** | Apply Patch Tool | 应用补丁方式编辑文件 |

> "These primitives include tool use via MCP, progressive disclosure via skills, custom instructions via AGENTS.md, code execution using the shell tool, file edits using the apply patch tool, and more."

### 可配置内存（Configurable Memory）

Harness 现在支持可配置内存，允许开发者定制 agent 的记忆机制。

### Sandbox-Aware Orchestration

Harness 支持沙箱感知的编排，与 Native Sandbox Execution 联动。

### 与 Codex 的对齐

Harness 提供了与 Codex 风格类似的文件系统工具，使 agent 能够在计算机上跨文件操作。

---

## 三、Native Sandbox Execution

### 设计动机

很多有用的 agent 需要一个工作空间，能够读写文件、安装依赖、运行代码、安全使用工具。当前的做法是开发者自己拼装这些能力，既困难又容易出错。

> "Native sandbox support gives developers that execution layer out of the box, instead of forcing them to piece it together themselves."

### 支持的沙箱提供商

新版 Agents SDK **内置支持**以下沙箱提供商：

- **Blaxel**
- **Cloudflare**
- **Daytona**
- **E2B**
- **Modal**
- **Runloop**
- **Vercel**

开发者可以自带沙箱，也可以直接使用内置支持。

### Manifest 抽象

为使工作空间在不同提供商之间可移植，SDK 引入了 **Manifest** 抽象：

> "To make those environments portable across providers, the SDK also introduces a Manifest abstraction for describing the agent's workspace."

Manifest 可以：
- 挂载本地文件
- 定义输出目录
- 从存储提供商引入数据：AWS S3、Google Cloud Storage、Azure Blob Storage、Cloudflare R2

### Sandbox 与 Compute 分离的安全含义

> "Agent systems should be designed assuming prompt-injection and exfiltration attempts. Separating harness and compute helps keep credentials out of environments where model-generated code executes."

这一原则将凭证与模型生成的代码执行环境分离，是安全架构的核心。

### 持久化执行（Durable Execution）

通过 **Snapshotting 和 Rehydration**：

> "With built-in snapshotting and rehydration, the Agents SDK can restore the agent's state in a fresh sandbox and continue from the last checkpoint if the original environment fails or expires."

### 可扩展性（Scalability）

Agent 运行可以：
- 使用单一沙箱或多个沙箱
- 仅在需要时调用沙箱
- 将子 agent 路由到隔离环境
- 跨容器并行化工作加速执行

---

## 四、定价与可用性

> "These new Agents SDK capabilities are generally available to all customers via the API and use standard API pricing, based on tokens and tool use."

- **Python 版本**：已正式发布
- **TypeScript 版本**：计划未来支持
- **未来计划**：code mode 和 subagents 能力将同时支持 Python 和 TypeScript

---

## 五、工程分析

### 与 Anthropic Claude Code Harness 的对比

| 维度 | OpenAI Agents SDK | Anthropic Claude Code |
|------|-------------------|----------------------|
| **Harness 定位** | Model-native，对齐模型执行模式 | 产品内的 agent 执行环境 |
| **Sandbox 支持** | 原生内置（7+ 提供商） | 依赖外部环境 |
| **持久化执行** | Snapshotting + Rehydration | 无明确对应机制 |
| **Workspace 抽象** | Manifest（跨提供商可移植） | 无对应抽象 |
| **多 Agent 支持** | Handoffs + Tools | Multi-Agent via MCP |

### 关键洞察

1. **Model-Native 作为差异化方向**：OpenAI 明确选择"模型原生"而非"模型无关"，与 Anthropic 的路线形成对比——后者更强调模型无关的灵活性，前者强调榨取模型最大能力。

2. **Sandbox 作为一等公民**：不同于大多数框架将 sandbox 视为可选项，OpenAI 将其作为 SDK 的内置原语，这反映了生产级 agent 系统对安全隔离的硬需求。

3. **Manifest 的可移植性价值**：workspace 描述的标准化（类比容器镜像的 Dockerfile）是走向生产的基础，值得关注。

4. **Harness 与 Compute 分离的安全原则**：这是值得在 `harness/` 目录下补充的核心工程原则——将控制层（harness）与执行层（sandbox compute）分离，是防御 prompt injection 的架构基础。

---

## 相关文献

- [OpenAI Agents SDK 官方文档](https://developers.openai.com/api/docs/guides/agents)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [AGENTS.md 规范](https://agents.md)
- [agentskills.io](https://agentskills.io)
- [Daytona Sandbox](https://daytona.io)
- [E2B Sandbox](https://e2b.dev)

---

*本篇由 AgentKeeper 自动整理，来源：OpenAI 官方开发者博客（2026 年 4 月）*
