# 多体系统架构范式：从「宠物」容器到「脑-手」解耦

> 本文分析 AI Agent 系统架构的核心演进方向：**将推理引擎（Brain/Harness）与执行环境（Hands/Sandbox）解耦**，形成可独立扩展、故障隔离、安全边界清晰的多体系统架构。通过 Anthropic Managed Agents、OpenAI Codex CLI、Cursor 3 三个官方实现，验证这一架构范式的收敛趋势。

---

## 1. 问题的起源：为什么 Agent 系统需要解耦

### 1.1 Pets vs Cattle：早期架构的代价

Anthropic 在 [Managed Agents](https://www.anthropic.com/engineering/managed-agents) 的工程实践中记录了一个典型问题：早期将所有组件（Session、Harness、Sandbox）塞进同一个容器。

> "We started by placing all agent components into a single container, which meant the session, agent harness, and sandbox all shared an environment."

这种「宠物模式」（Pet Mode）带来的代价：
- **单点故障传播**：容器崩溃 = Session 丢失 = 所有上下文丢失
- **无法弹性扩展**：每个 Brain 独占一个容器，即使该 Brain 不执行任何推理也得等待容器就绪
- **调试窗口封闭**：WebSocket event stream 无法定位故障来源（harness bug / packet drop / container offline 表现一致）

> 官方原文：
> "To figure out what went wrong, an engineer had to open a shell inside the container, but because that container often also held user data, that approach essentially meant we lacked the ability to debug."

### 1.2 第二代问题：耦合限制扩展性

即使解决了「宠物」问题，耦合架构还有第二个限制：当团队需要 Claude 对接自己的 VPC（虚拟私有云）资源时，必须让容器与目标网络对等互联。Anthropic 记录：

> "When customers asked us to connect Claude to their virtual private cloud, they had to either peer their network with ours, or run our harness in their own environment."

这是一个架构级别的约束：**Harness 假设所有资源都在容器内部**，这个假设在分布式企业场景下失效。

---

## 2. 解耦方案：Brain-Hands-Session 三元架构

### 2.1 三元组件定义

Anthropic 引入操作系统思想，将 Agent 系统虚拟化为三层抽象：

| 组件 | 职责 | 类比 OS 概念 |
|------|------|-------------|
| **Brain** | 推理引擎 + Harness 循环 | 进程调度器 |
| **Hands** | 执行环境（容器/Sandbox/工具） | 硬件/外设 |
| **Session** | 持久化事件日志，Brain 的外部记忆 | 磁盘 |

> 官方原文：
> "Decades ago, operating systems solved this problem by virtualizing hardware into abstractions—process, file—general enough for programs that didn't exist yet. The abstractions outlasted the hardware. The read() command is agnostic as to whether it's accessing a disk pack from the 1970s or a modern SSD."

Managed Agents 正是用同样的思想虚拟化 Agent 组件：

> "We virtualized the components of an agent: a session (the append-only log of everything that happened), a harness (the loop that calls Claude and routes Claude's tool calls to the relevant infrastructure), and a sandbox (an execution environment where Claude can run code and edit files)."

### 2.2 接口契约：Tool Call 作为统一边界

三元组件之间的交互通过标准化的 Tool Call 接口：

```typescript
// Brain → Hands 的标准化调用
execute(name: string, input: string): string

// Hands → Brain 的事件上报
emitEvent(id: string, event: Event)

// Brain → Session 的持久化
getSession(id: string): EventLog

// 恢复时 Brain 从 Session 重新构建状态
wake(sessionId: string)
```

这个接口的设计意图是：**接口稳定，实现可替换**。Harness 可以是 Claude Code，可以是定制化领域智能体，可以是未来的任何实现——只要它遵循这个接口契约。

---

## 3. 解耦的红利：从架构收益到产品体验

### 3.1 Time-to-First-Token (TTFT) 大幅下降

Anthropic 的实测数据：

| 指标 | 解耦前 | 解耦后 | 改善幅度 |
|------|--------|--------|---------|
| p50 TTFT | 基线 | 下降约 60% | -60% |
| p95 TTFT | 基线 | 下降超过 90% | -90%+ |

原因：解耦后容器按需启动。初始不需执行 Sandbox 的会话，Brain 直接从 Session 读取事件日志并开始推理，无需等待容器就绪。

> 官方原文：
> "Using this architecture, our p50 TTFT dropped roughly 60% and p95 dropped over 90%. Scaling to many brains just meant starting many stateless harnesses, and connecting them to hands only if needed."

### 3.2 多 Hand 扩展：认知分工成为可能

随着模型能力提升，单容器瓶颈从「优势」变为「限制」：

> "We also wanted the ability to connect each brain to many hands. In practice, this means Claude must reason about many execution environments and decide where to send work—a harder cognitive task than operating in a single shell."

解耦后每个 Hand 是一个 Tool，Brain 可以将任务分发到多个 Sandboxes，且每个 Hand 可以被多个 Brain 共享（ brains can pass hands to one another）。

### 3.3 安全边界结构化

耦合架构的核心安全缺陷：Untrusted Code 和 Credentials 共处一室。

> "In the coupled design, any untrusted code that Claude generated was run in the same container as credentials—so a prompt injection only had to convince Claude to read its own environment."

解耦方案通过 Vault 模式从根本上消除这个问题：

- Git credentials：在 Sandbox 初始化时注入，本地 git remote 可正常工作，但 Agent 永远不接触 token 本身
- OAuth tokens：存放在 Vault，Agent 通过专用 MCP Proxy 访问，Proxy 持有 session-associated token，Harness 完全不知晓凭据存在

---

## 4. OpenAI Codex CLI：Rust 实现的工程对照

OpenAI 的 [Codex CLI](https://github.com/openai/codex) 提供了另一种 Brain-Hands 解耦的工程视角。

### 4.1 Agent Loop 的分层设计

Codex CLI 的 Agent Loop 分三层：

1. **Harness Layer**：Rust 实现，负责 Loop 控制、Session 管理、Prompt 构建
2. **Model Provider Layer**：通过 Responses API 调用 Claude / GPT / Ollama，支持多种认证方式（ChatGPT Login / API Key / --oss 模式）
3. **Sandbox Layer**：通过 `execute()` Tool 调用独立的沙箱执行环境

Codex 的 sandbox 设计细节在 [sandbox.md](https://github.com/openai/codex/blob/main/docs/sandbox.md) 中记录：

> "If Codex runs tools like `git`, package managers, or test runners, those commands inherit the same sandbox boundaries. Instead of asking you to confirm every low-risk command, Codex can read files, make edits, and run routine project commands within the boundary you already approved."

这是一个用户感知层面的差异：**不是让用户逐个批准命令，而是预授权整个沙箱边界**。

### 4.2 Prompt Caching：对会话增长的优化

Codex 文档中记录了一个关键实现细节：

> "In particular, note how the old prompt is an exact prefix of the new prompt. This is intentional, as this makes subsequent requests much more efficient because it enables us to take advantage of prompt caching."

这个设计与 Session 作为外部存储的思路一致——不是在 Brain 内部管理上下文增长，而是让 Session 持久化+增量扩展。

### 4.3 Windows 原生沙箱实验

Codex 正在开发 Windows 原生文件系统+网络沙箱：

> "If you use the CLI on native Windows, you can enable a highly experimental filesystem and network sandbox. Once it's stable, Codex agent mode will run more securely within well-defined boundaries."

这是 Hands 层实现多样化的一个信号——不只是 Docker 容器，还有 OS 级别的沙箱隔离。

---

## 5. Cursor 3：产品层对 Brain-Hands 架构的用户体验映射

Cursor 3 的发布将 Brain-Hands 解耦从基础设施层带到了用户体验层。

### 5.1 多workspace + Cloud/Local Agent 统一视图

Cursor 3 的架构核心是「All your agents in one place」：

- 多 repo 布局：Agent 工作空间与项目结构解耦
- Local ↔ Cloud 无缝 handoff：工作会话可以在本地和云端之间迁移

> 官方原文：
> "Move an agent session from cloud to local when you want to make edits and test it on your own desktop. In the reverse direction, you can move an agent session from local to cloud to keep it running while you're offline."

这直接对应了 Anthropic 提出的 **Brain 和 Hands 独立扩展** 模型：Brain（推理引擎）在云端，Hands（执行环境）在本地，用户在两者之间按需迁移会话。

### 5.2 Cloud Agents 的 Demo/Screenshot 验证机制

Cloud Agents 产生 Demo 和 Screenshot 供人类验证，这是对「Long-Horizon 任务中 Human-in-the-Loop」需求的工程回应。Cursor 将验证结果反馈到 Agent 循环中，实现 Human-AI 协作的闭环。

---

## 6. 架构收敛：从三个官方实现看行业方向

| 维度 | Anthropic Managed Agents | OpenAI Codex CLI | Cursor 3 |
|------|--------------------------|------------------|---------|
| **Brain/Harness** | Claude + 外部 Harness 循环 | Responses API + Rust Harness | Composer 2 + Cloud Agents |
| **Hands/Sandbox** | 按需容器（execute Tool） | 沙箱边界预授权 | 本地/云端双环境 |
| **Session** | 外部事件日志，持久化 | Prompt 增量，前缀缓存 | 会话迁移（Local↔Cloud）|
| **安全模型** | Vault + MCP Proxy 凭据隔离 | 文件系统+网络沙箱 | 工作区隔离 |
| **扩展方向** | Many Brains → Many Hands | 多 provider + 多 sandbox | 多 repo + fleet agents |

三家公司的共同演进方向：
1. **Harness 与 Execution 分离** 是确定的工程方向
2. **Session 作为外部化上下文存储** 是解决长程任务上下文增长的标准方案
3. **安全边界从「逐命令审批」演化为「预授权沙箱边界」**

---

## 7. 工程实践建议

### 7.1 设计检查清单

在设计新 Agent 系统时，应该明确回答：

- [ ] Brain 和 Hands 是否可以独立故障、独立重启？
- [ ] Session 是否持久化到 Brain 外部？还是存储在 Harness 内存中？
- [ ] 凭据是否永远不在 Agent 可访问的上下文中？
- [ ] Sandbox 是否按需启动？还是会话开始时就要全部就绪？
- [ ] 支持多少个 Brain 共享同一个 Hand？

### 7.2 已知局限

**Harness 假设会过时**：Anthropic 记录了一个关键观察——Harness 设计时做的假设会随着模型能力提升而失效：

> "harnesses encode assumptions about what Claude can't do on its own. However, those assumptions need to be frequently questioned because they can go stale as models improve."

2024年的有效设计（如 Sonnet 4.5 的 context resets）在 2025年（Opus 4.5）可能成为 dead weight。解耦架构的价值在于：当假设失效时，只需替换 Harness 实现，而不需要重建 Session 和 Hands。

**多 Hand 的认知负担**：Anthropic 明确指出多 Hand 对 Claude 提出了更高的认知要求。架构上支持多 Hand 不等于模型能有效利用多 Hand——这是产品设计需要解决的问题。

---

## 8. 结论

从三家的官方实现来看，Agent 系统架构正在向「虚拟化三元组」收敛：

- **Brain/Harness** 是智能决策层，负责推理、规划、工具调用路由
- **Hands/Sandbox** 是执行能力层，按需扩展，与 Brain 解耦
- **Session** 是外部化上下文，解决长程任务的上下文窗口限制

这个架构的核心价值不是某个具体实现细节，而是 **接口稳定而实现可替换** 的设计哲学——这正是操作系统数十年验证过的方法论在 AI Agent 领域的重新应用。

> 官方原文引用：
> "The challenge we faced is an old one: how to design a system for 'programs as yet unthought of.' Operating systems have lasted decades by virtualizing the hardware into abstractions general enough for programs that didn't exist yet."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

---

**相关资源**：
- [Anthropic Managed Agents](https://www.anthropic.com/engineering/managed-agents)
- [OpenAI Codex CLI](https://github.com/openai/codex)
- [OpenAI Codex Agent Loop](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [Cursor 3](https://cursor.com/blog/cursor-3)
- [Cursor Cloud Agents](https://cursor.com/agents)