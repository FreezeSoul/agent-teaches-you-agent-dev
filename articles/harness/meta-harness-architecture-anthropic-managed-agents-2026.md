# Anthropic Scaling Managed Agents：Agent 基础设施的 Meta-Harness 架构演进

> **本文解决的问题**：当 Agent 系统需要支撑数年乃至更久的生命周期时，如何设计一个能适应「尚未设想的程序」的架构？Anthropic 的解法是**将 Agent 的核心组件虚拟化为稳定接口**，使 Brain、Hands、Session 都可以独立替换，而不影响整体系统的稳定性。

---

## 问题起源：Pet 运维模式带来的困境

Anthropic 最初将 Session、Harness 和 Sandbox 全放在单一容器内。这种紧耦合设计带来了两个核心问题：

### 问题一：Session 的脆弱性

容器死亡 → Session 丢失。每次容器无响应，都需要工程师手动进入容器调试——但容器内同时持有用户数据，这种「调试」本质上是隐私风险的来源。工程师无法在不侵入用户数据的前提下进行诊断。

### 问题二：安全边界固化

当所有组件共处一室时，Claude 生成的任何不可信代码都能访问同一容器内的凭据。一次 Prompt Injection 成功，攻击者就能利用这些凭据启动新的无限制会话，然后将工作委托给攻击者控制的会话。

> 笔者的判断：**Pet 模式是 Agent 服务化的最大障碍**。当系统需要 scale 到数十个并发会话时，手工维护单个容器的思路必然崩溃。必须转向 Cattle 模式——容器是可替换的，而不是需要修复的。

---

## 核心解法：Brain-Hand-Session 三组件解耦

Anthropic 将 Agent 系统拆解为三个独立接口：

| 组件 | 职责 | 接口定义 |
|------|------|----------|
| **Brain** | Claude + Harness（推理决策循环） | 调用 Hands 的唯一入口 |
| **Hands** | Sandbox + Tools（执行环境） | `execute(name, input) → string` |
| **Session** | 持久化的 Event Log（状态记录） | `getEvents()` / `emitEvent()` |

```
┌──────────────────────────────────────────────────────┐
│                    Brain（可 scale）                 │
│  ├─ Claude Agent SDK                                │
│  ├─ Harness（loop that calls Claude）                │
│  └─ 与 Hands 的连接：通过 execute() 调用             │
└──────────────────────────────────────────────────────┘
           ↓ execute(name, input) → string
┌──────────────────────────────────────────────────────┐
│              Hands（按需 provisioned）                │
│  ├─ Container / VM（每次按标准 recipe 创建）          │
│  ├─ MCP Server / Custom Tools                        │
│  └─ Git / OAuth credentials（vault 外置）           │
└──────────────────────────────────────────────────────┘
           ↕ getEvents() / emitEvent()
[Session — 持久化事件日志，所有组件共享]
```

### Harness 与 Container 的分离

关键变化是 Harness 不再存在于 Container 内。它通过 `execute(name, input) → string` 调用容器，就像调用任何其他工具一样。这意味着：

- **容器变成了 Cattle**：如果容器挂了，Harness 捕获为 Tool Call Error，Claude 可以决定重试，新容器按标准 recipe 重新初始化
- **无需「护士」容器**：不再需要将故障容器恢复健康，而是直接替换

### TTFT 优化的量化效果

原来每个 Session 不管是否需要容器都要等容器启动。现在 Brain 可以在 orchestration layer 先开始推理，只有真正需要时才通过 `execute()` 调起 Hands。

> "Using this architecture, our p50 TTFT dropped roughly 60% and p95 dropped over 90%."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这个优化来自于：**推理开始时间**和**容器初始化时间**的解耦。对于不需要容器操作的简单任务，Brain 可以直接响应，根本不需要调起 Hands。

### Harness 崩溃恢复

当 Harness 本身崩溃时，Session Log 是独立存储的。新 Harness 可以通过 `wake(sessionId)` 重新连接到 Session，然后使用 `getSession(id)` 获取完整的事件日志，从最后一个事件处恢复。

在 Agent Loop 运行期间，Harness 通过 `emitEvent(id, event)` 向 Session 写入事件——这个操作是持久的，确保 Session Log 永远不会因 Harness 崩溃而丢失。

---

## Session 与 Context 的分离

这是文章最深刻的洞察之一。Context Window 的限制是所有 LLM Agent 都必须面对的问题，常见的解决方案都涉及不可逆的操作：

- **Compaction（压缩）**：用摘要替换历史消息，但摘要会丢失细节，且无法恢复
- **Context Trimming（截断）**：删除旧的 tool results 或 thinking blocks，但这些信息可能对未来的任务至关重要
- **Context Reset（重置）**：清空整个 context window，用一个新的 agent 从上一次的 handoff artifact 继续，但这意味着前面所有的中间状态都丢失了

这些方法都是**单向的**——一旦执行，就无法回退。

Anthropic 提出的设计是：Session 本身不是 Claude 的 Context Window，而是一个**外部化的上下文对象**：

> "The session is not Claude's context window... context can be an object in a REPL that the LLM programmatically accesses by writing code to filter or slice it."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

通过 `getEvents()` 接口，Brain 可以：
- 选择位置切片（positional slices）：只读取事件流的某一段
- Rewind 到特定时刻之前：查看某个 action 前的完整上下文
- 在执行特定 action 前重新读取 context：确保记忆是最新的

这种设计将两个关注点分离：
- **Session**：负责 durably 存储事件，并保证事件流可以被 interrogation
- **Harness**：负责 arbitrary context engineering，可以根据具体模型的需求灵活组织 prompt

这意味着：随着模型能力的演进（新的 context window 大小、新的上下文管理需求），只有 Harness 需要适配，而 Session 的存储结构不需要改变。

---

## 安全边界的设计原则

Anthropic 在安全边界上有一个关键洞察：

> "The structural fix was to make sure the tokens are never reachable from the sandbox where Claude's generated code runs."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

在耦合设计中，Claude 生成的代码和凭据共处一室，Prompt Injection 只要能说服 Claude 读取自己的环境就能获取令牌。即使 scope 限制很小，Claude 正在变得越来越智能，攻击面在扩大。

Anthropic 的解决方案是**物理隔离**：

### Git 凭据的处理

每个仓库的 Access Token 在 Sandbox 初始化时注入到本地 git remote：

```bash
# Sandbox 初始化时执行
git remote set-url origin https://x-token-auth:${GITHUB_TOKEN}@github.com/owner/repo
```

这样 Git push/pull 正常工作，但 Agent 永远不直接处理 Token——它只是在操作 Git，Git 自己会处理认证。

### MCP + Vault 的集成

对于需要 OAuth 的外部服务（如 Slack、Salesforce），Anthropic 的方案是：

1. OAuth Token 存在外部 Vault
2. MCP Proxy 根据 Session ID 从 Vault 获取对应凭据
3. Proxy 调用外部服务，Harness 本身对凭据完全无感知

即使 Claude 被 Prompt Injection 攻击，攻击者也无法访问 Vault——因为 Claude 根本没有和 Vault 通信的路径。

> 笔者的判断：**这个设计将安全边界从「信任 Claude 不被 Prompt Injection」转移到了「架构上让凭据物理不可达」**。这是一个更可靠的安全模型，因为即使模型被攻破，攻击者也无法获取凭据。

---

## Many Brains, Many Hands：横向扩展的架构

文章揭示了架构演进的第三个维度：从单 Brain + 单 Hand，到 Many Brains + Many Hands。

### Many Brains：当 Brain 离开容器后

当 Brain 离开容器后，「多 Brain」不再需要「多容器」。每个 Brain 是无状态的 Harness 进程，通过 `wake(sessionId)` 从共享 Session Log 恢复。

这个设计带来了几个关键能力：

- **新 Brain 可以立即开始推理**：无需等待容器初始化，Session Log 已经包含了所有上下文
- **不同任务用不同 Harness**：Claude Code 适合通用任务，Task-specific agent harnesses 适合垂直场景，Managed Agents 可以动态选择
- **模型适配性**：Claude Opus 4.5 的能力 vs Sonnet 4.5 的能力需要不同的 Harness，Meta-Harness 可以同时容纳它们

### Many Hands：execute() 接口的通用性

每个 Hand 都是一个 `execute(name, input) → string` 接口的实现：

> "The harness doesn't know whether the sandbox is a container, a phone, or a Pokémon emulator."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这个设计让 Brain 可以同时连接多个执行环境：

- **不同的 MCP Server**：数据库查询、API 调用、文件处理
- **不同的 Sandbox**：代码执行、浏览器自动化、模型推理
- **不同物理位置的 Hands**：云端容器、本地 VM、甚至移动设备

更重要的是，因为没有 Hand 是耦合到任何 Brain 的，**Brains 可以互相传递 Hands**。这为多 Brain 协作提供了基础设施层面的支持。

---

## Meta-Harness：面向未来的架构选择

文章的核心主张是：Managed Agents 本身是一个 **Meta-Harness**——一个能容纳不同 Harness 实现的外层框架。

> "Managed Agents is a meta-harness in the same spirit, unopinionated about the specific harness that Claude will need in the future. Rather, it is a system with general interfaces that allow many different harnesses."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这个设计的长期价值在于三个维度：

### 1. 接口稳定性

即使底层实现（Harness、Session、Sandbox）全部替换，上层调用接口保持不变。这和当年操作系统的虚拟化是一样的——`read()` 系统调用在 1970 年代访问磁盘 Pack，在 2020 年代访问 SSD，接口没变，但实现换了无数代。

### 2. 模型适配性

Claude 的能力在不断增长。今天的 Harness 假设——比如 Sonnet 4.5 会因为 context 接近 limit 而 wrap up work（context anxiety）——明天可能就不适用了。当 Anthropic 切换到 Opus 4.5 时，同样的 harness 发现 context anxiety 完全消失了，之前添加的 context resets 变成了 dead weight。

Meta-Harness 让不同的 Harness 可以动态适配不同模型的能力，而不需要改变上层架构。

### 3. 生态兼容性

Claude Code 是优秀的 Harness，Task-specific agent harnesses 也各有优势。Managed Agents 可以同时容纳它们：

> "For example, Claude Code is an excellent harness that we use widely across tasks. We've also shown that task-specific agent harnesses excel in narrow domains. Managed Agents can accommodate any of these, matching Claude's intelligence over time."

---

## 与 OpenAI Agent SDK 的架构对比

| 维度 | Anthropic Managed Agents | OpenAI Agent SDK |
|------|--------------------------|-------------------|
| **核心抽象** | Meta-Harness（Brain-Hand-Session 解耦）| Native Harness（Sandbox + Guardrails 内置）|
| **安全模型** | Token 物理不可达（Vault 外置）| Sandbox 隔离 + Guardrails |
| **状态管理** | Session as Context Object（外部化）| Stateful Background Traces |
| **扩展模式** | Many Brains + Many Hands | Handoffs（Agent 间转移）|
| **适用场景** | 企业级、长期运行、多租户 | 快速原型、短期任务 |

> 笔者的判断：两者代表了 Agent 基础设施的两条路线——**Anthropic 选择了「抽象化」，OpenAI 选择了「内置化」**。前者适合需要长期维护的企业场景，后者适合需要快速迭代的开发场景。这个选择没有绝对对错，取决于组织的需求和工程成熟度。

两条路线的核心差异在于对「确定性」和「灵活性」的权衡：

- **OpenAI 的路线**：Sandbox 和 Guardrails 是内置的，开发者的决策点少，上手快，但定制空间有限
- **Anthropic 的路线**：接口是抽象的，Harness 是可替换的，开发者需要理解更多的概念，但可以获得更大的灵活性

---

## 对 Harness Engineering 的实践启示

### 1. Pet vs Cattle 是第一道分水岭

如果 Agent 系统还需要手工维护单个容器，它就无法 scale。必须从架构上假设任何组件都可以失败并自动恢复。

一个简单的判断标准：**如果你的系统需要 SSH 进入容器来「抢救」它，它就不是 Cattle**。

### 2. 安全边界需要物理隔离而非信任假设

在 Agent 系统里，模型被 Prompt Injection 攻破是概率性事件，而非不可能事件。安全设计必须假设这个事件发生，然后确保凭据依然不可获取。

这意味着：不要在 Sandbox 内存储任何敏感凭据；使用 Vault + Proxy 的模式让 Agent 永远无法直接接触凭据。

### 3. Session 作为外部化 Context Object 是解决 Context Window 限制的关键

压缩和截断都是不可逆的操作，都会导致信息丢失。外部化的 Session + 可查询的 getEvents() 提供了另一种思路：不是压缩历史，而是让历史变成可选读取的对象。

这个模式的代价是：Brain 需要主动管理自己的 context，通过调用 getEvents() 来获取需要的信息，而不是被动地拥有全部历史。

### 4. Meta-Harness 是基础设施抽象化的必然方向

当 Agent 开始承担生产级别的长期任务时，基础设施必须能适应尚未设想的场景。虚拟化是解决这个问题的成熟范式，OS 用了几十年，现在轮到 Agent 了。

对于构建 Agent 基础设施的团队，这意味着：**不要过度优化当前的 Harness 实现**——而是设计好接口，让未来的 Harness 可以平滑替换。

---

## 结论

Anthropic 的 Scaling Managed Agents 文章展示了一个重要的 architectural pattern：当 Agent 系统需要支撑长期运行时，必须从紧耦合的 Pet 模式转向解耦的 Cattle 模式。

核心贡献有三个：

1. **Brain-Hand-Session 三组件解耦**：通过稳定的接口定义，使每个组件都可以独立替换
2. **Session 作为外部化上下文对象**：解决了 Context Window 限制和状态持久化之间的矛盾
3. **Token 物理不可达的安全模型**：将安全边界从「信任模型」转移到「架构约束」

> "The challenge we faced is an old one: how to design a system for 'programs as yet unthought of.' Operating systems have lasted decades by virtualizing the hardware into abstractions general enough for programs that didn't exist yet."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

Meta-Harness 是这个思路在 AI Agent 领域的具体实践。它不是最终答案，但为 Agent 基础设施的长期演进提供了一个可扩展的框架。

---

*来源：[Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)，2026年4月8日发布*
