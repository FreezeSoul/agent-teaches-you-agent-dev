# Anthropic Managed Agents 安全边界设计：从 Credential 隔离到 Meta-Harness 架构

## 核心论点

> **Anthropic 在 Managed Agents 中实现了一个结构性安全方案：通过对 "brain"（Claude + harness）与 "hands"（sandbox + tools）的解耦，让模型生成的不可信代码永远无法触及凭证体系。这一设计不是依赖"模型足够聪明不泄露凭证"，而是通过架构约束使凭证在物理上不可达。结合 TTFT 60% 的性能收益，这个解耦模式同时实现了安全与性能的提升。**

---

## 一、问题：耦合架构下的 Prompt Injection 致命性

在 Managed Agents 之前，Anthropic 的架构将所有组件放在单一容器中：session、agent harness 和 sandbox 共享环境。好处是文件编辑是直接系统调用，没有服务边界需要设计。

但代价是安全边界彻底失效：

> "In the coupled design, any untrusted code that Claude generated was run in the same container as credentials—so a prompt injection only had to convince Claude to read its own environment. Once an attacker has those tokens, they can spawn fresh, unrestricted sessions and delegate work to them."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这是一个结构性的安全漏洞，不依赖于模型是否"足够可靠"——当模型生成的代码与凭证共存于同一容器，攻击面就已经存在。

---

## 二、解决方案：三元解耦架构

Anthropic 的答案是将三个组件完全解耦：

### 2.1 Brain（大脑）：Claude + Harness

Brain 负责推理和决策，包含 Claude 模型和运行 Agent 循环的 harness。这一层是**无状态的**——当 harness 崩溃时，一个新的实例可以通过 `wake(sessionId)` 重新启动，从 `getSession(id)` 恢复事件日志后继续工作。

> "Because the session log sits outside the harness, nothing in the harness needs to survive a crash. When one fails, a new one can be rebooted with wake(sessionId), use getSession(id) to get back the event log, and resume from the last event."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

Harness 通过 `emitEvent(id, event)` 向外部 session 写入事件，保持持久记录的同时自身保持无状态。

### 2.2 Hands（手脚）：Sandbox + Tools

Sandbox 是代码执行的地方——Claude 生成的所有代码都在这里运行。Brain 通过标准工具接口调用 sandbox：

```
execute(name, input) → string
```

Sandbox 是** cattle**（可替代的）而非 **pet**（需要维护的个体）：

> "Decoupling the brain from the hands meant the harness no longer lived inside the container. It called the container the way it called any other tool: execute(name, input) → string. The container became cattle. If the container died, the harness caught the failure as a tool-call error and passed it back to Claude. If Claude decided to retry, a new container could be reinitialized with a standard recipe: provision({resources})."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

### 2.3 Session（账本）：Append-Only 事件日志

Session 是独立的持久层，记录所有事件。它的核心价值在于**可查询性**：

> "The interface, getEvents(), allows the brain to interrogate context by selecting positional slices of the event stream. The interface can be used flexibly, allowing the brain to pick up from wherever it last stopped reading, rewinding a few events before a specific moment to see the lead up, or rereading context before a specific action."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这不是 Claude 的 context window，而是一个外部上下文对象。Harness 可以对获取的事件进行任意转换（上下文组织、prompt cache 优化），而 session 本身只保证持久性和可查询性。

---

## 三、安全边界：Credential 永远不在 Sandbox 可达范围内

解耦的直接安全价值是 credential 隔离。Anthropic 使用两种模式确保 tokens 永远不会从 sandbox 可达：

### 模式一：Auth Bundling with Resource

对于 Git 操作，Anthropic 在 sandbox 初始化时直接用仓库的访问令牌克隆 repo，并将其接入本地 git remote。Git push/pull 在 sandbox 内正常工作，但**Agent 本身从不处理 token**。

### 模式二：Vault + Dedicated Proxy for OAuth

对于自定义工具，Anthropic 支持 MCP，并将 OAuth tokens 存储在独立 vault 中：

> "Claude calls MCP tools via a dedicated proxy; this proxy takes in a token associated with the session. The proxy can then fetch the corresponding credentials from the vault and make the call to the external service. The harness is never made aware of any credentials."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

关键在于：即使是运行 harness 的基础设施，也不知道凭证在哪里。凭证存在于 vault 中，由专用 proxy 持有，harness 只通过 session 关联的 token 调用 proxy。

---

## 四、性能收益：解耦带来的 60%/90% TTFT 提升

解耦不仅改善了安全，还带来了惊人的性能收益。核心原因是**按需 provisioning**：

> "Decoupling the brain from the hands means that containers are provisioned by the brain via a tool call (execute(name, input) → string) only if they are needed. So a session that didn't need a container right away didn't wait for one. Inference could start as soon as the orchestration layer pulled pending events from the session log."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

之前，每个 session 即使从不使用 sandbox，也必须经历完整的容器启动代价（clone repo、boot process、fetch pending events）。这些等待时间直接体现为 **TTFT（Time-to-First-Token）**——用户最敏感的延迟指标。

解耦后的结果是：

| 指标 | 改善幅度 |
|------|----------|
| p50 TTFT | **下降约 60%** |
| p95 TTFT | **下降超过 90%** |

扩展到 many brains 只需要启动多个无状态 harness，按需连接 hands。

---

## 五、Many Hands：每个 Brain 可以连接多个执行环境

解耦还解锁了一个新能力：每个 brain 可以连接多个 hands：

> "Decoupling the brain from the hands makes each hand a tool, execute(name, input) → string: a name and input go in, and a string is returned. That interface supports any custom tool, any MCP server, and our own tools. The harness doesn't know whether the sandbox is a container, a phone, or a Pokémon emulator."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这意味着 Claude 必须能够推理多个执行环境并决定将工作发送到哪个——这是一个比单 shell 操作更难的认知任务，但也更强大。更重要的是，**brains 可以相互传递 hands**，实现多智能体协作。

---

## 六、Meta-Harness：接口即契约，实现即弃

Managed Agents 的设计哲学是**接口即契约，实现即弃**：

> "We designed the interfaces so that these can be run reliably and securely over long time horizons. But we make no assumptions about the number or location of brains or hands that Claude will need."
> — [Anthropic Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这个思路与操作系统虚拟化硬件的思路完全一致——read() 命令不在乎访问的是 1970 年代的磁盘组还是现代 SSD。Managed Agents 虚拟化了 session（状态）、harness（控制流）和 sandbox（执行），使得任何未来的实现都可以替换其中任何一个而不影响其他。

Claude Code 是一个优秀的 harness，Anthropic 自己在各种任务中广泛使用它。Task-specific agent harnesses 在窄领域也表现出色。Managed Agents 可以容纳所有这些，适配 Claude 随时间推移的智能增长。

---

## 七、与 Cursor Harness 定制化的主题关联

Anthropic 的解耦架构与 Cursor 的模型定制化策略形成了一个共同趋势：**harness 从业经验证金（best practice collection）演变为独立工程学科**。

Cursor 发现不同模型需要不同的工具格式（OpenAI patch-based vs Anthropic string replacement），并在 harness 层面对每个模型进行深度定制。Anthropic 则通过解耦让 harness 本身成为可替换组件。

两者共同指向的结论是：**Agent 的能力 = Model × Harness**，而 Harness Engineering 是一个需要独立投入的工程维度。
