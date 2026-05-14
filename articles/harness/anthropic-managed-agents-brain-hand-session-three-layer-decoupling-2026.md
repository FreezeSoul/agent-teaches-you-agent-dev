# Anthropic Managed Agents：脑手分离架构与多脑多手机器人设计解析

## 核心主张

> 本文要证明：Anthropic 的 Managed Agents 通过将 Agent 拆解为「脑（Brain）」「手（Hands）」「会话（Session）」三个正交维度，实现了 multi-agent 系统的可扩展性、安全性和长期运行能力的根本性突破。这是自 OS 虚拟化思想以来，Agent 架构领域最清晰的抽象层次突破。

---

## 一、耦合设计的结构性缺陷

### 1.1 Pets vs Cattle：被忽视的运维代价

Anthropic 在构建 Managed Agents 的第一版时，采用了所有组件共享单一容器的设计方案：Session、Harness 和 Sandbox 共处一室。文件编辑是直接 syscall，没有服务边界需要设计。这种「一体化」设计在初期带来了开发的便利性。

然而，随着部署规模扩大，运维问题开始暴露。按照云计算的经典隐喻，这个服务器成了一只 **「pet」**——命名化、手工照料、不可替代。当容器崩溃，Session 数据随之丢失；当容器无响应，工程师必须登入容器内部进行诊断。但登入本身意味着访问用户数据——这在安全层面构成了一个无法绕过的困境：调试能力和数据隔离成了鱼与熊掌。

> "A pet is a named, hand-tended individual you can't afford to lose, while cattle are interchangeable."
> — [Cloudscaling Blog: The History of Pets vs Cattle](https://cloudscaling.com/blog/cloud-computing/the-history-of-pets-vs-cattle/)

### 1.2 调试黑箱：WebSocket 流无法定位根因

当 Session 卡住时，工程师只能看到 WebSocket 事件流。但这个流无法区分三类失败：

- Harness 本身的 bug
- 事件流中的数据包丢失
- 容器本身离线

三者呈现给用户的是完全相同的状态：无响应。工程师唯一的调试手段是打开容器内部的 shell——而这在容器持有用户数据的环境下，意味着我们实际上**缺乏调试能力**。

### 1.3 网络耦合：Harness 假设所有资源都在本地

当企业客户要求将 Claude 连接到他们的 VPC 时，耦合设计的另一个缺陷暴露了：Harness 假设所有需要操作的资源都在容器内部。如果要连接外部 VPC，必须进行网络对等（peering），或者干脆将 Harness 部署在客户自己的环境中——这本质上是将整个架构迁移到客户侧，而非保持集中式管理。

---

## 二、解耦方案：Brain-Hand-Session 三层架构

### 2.1 接口抽象：虚拟化的经典回响

Anthropic 的解法来自一个有着数十年历史的计算思想：**虚拟化**。操作系统通过将硬件抽象为 `process`、`file` 等接口，使得 `read()` 系统调用可以读写 1970 年代磁盘包的数据，也可以读写现代 SSD——接口本身不关心后端实现。

Managed Agents 将 Agent 的各个组件也虚拟化为接口：

| 组件 | 角色 | 接口契约 |
|------|------|---------|
| **Session** | append-only log | `emitEvent(id, event)` / `getEvents()` |
| **Harness** | Agent loop 引擎 | `wake(sessionId)` / 调用 Claude 并路由工具调用 |
| **Sandbox** | 执行环境 | `execute(name, input) → string` / `provision({resources})` |

每个组件通过接口通信，对彼此的实现细节零假设。

### 2.2 Brain 脱离 Container：Harness 成为 Cattle

核心转变是 Harness 不再存活于容器内部。它通过工具调用协议 `execute(name, input) → string` 与容器通信。容器变成了**纯粹的 Cattle**：死亡时，Harness 捕获工具调用错误并将错误传递给 Claude，由 Claude 决定是否重试。重建容器只需调用 `provision({resources})`——不再需要「将失败的宠物治愈」。

### 2.3 Harness 恢复：零状态重启

当 Harness 本身崩溃时，由于 Session log 独立于 Harness 存在，**Harness 无需保存任何状态**。新 Harness 可以通过 `wake(sessionId)` 恢复：调用 `getSession(id)` 获取事件日志，从最后一条事件恢复。这种设计使得 Harness 的失败对用户完全透明。

> "Because the session log sits outside the harness, nothing in the harness needs to survive a crash."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

### 2.4 安全边界：凭证永远不在 Sandbox 可达范围内

耦合设计的一个根本性安全问题：**任何 Claude 生成的不可信代码都运行在持有凭证的同一容器内**。如果 Prompt injection 成功，攻击者只需让 Claude 读取自己的环境变量，即可获取所有凭据。之后的攻击路径是：获取 token → 启动新的未受限 Session → 委托工作。

Anthropic 的结构性解法是：**确保 token 永远无法从 Sandbox 的执行环境中被访问**。他们使用两种模式：

**Bundled Auth**：Auth 与资源绑定（如 Git 的 repo access token 在 Sandbox 初始化时注入本地 git remote，Agent 永远不接触 token）

**Vault + MCP Proxy**：OAuth token 存储在独立 Vault 中。Claude 通过 MCP 调用工具时，流量经过专用 Proxy。Proxy 持有与 Session 关联的 token，从 Vault 获取对应凭证后调用外部服务。Harness 本身对凭证完全无感知。

---

## 三、性能收益：60% / 90% 的 TTFT 降低

### 3.1 延迟根源：容器预置的串行等待

在耦合架构下，「多 Brain 必然多 Container」：每个 Brain 必须等待自己的容器完全预置后才能开始推理。即便 Session 永远不需要 Sandbox（纯推理任务），也要等待完整的容器启动流程：clone repo、boot process、从服务器获取待处理事件。这段死时间直接体现在 **TTFT（Time-to-First-Token）** 指标上——这是用户最能感知到的延迟。

### 3.2 懒加载：Sandbox 按需初始化

解耦后，容器通过工具调用 `execute(name, input) → string` 按需启动。如果 Session 不需要容器（纯推理任务），推理立即开始——从 Session log 提取待处理事件后立刻开始 inference。使用该架构后，Anthropic 的数据：

- **p50 TTFT 下降约 60%**
- **p95 TTFT 下降超过 90%**

> "Using this architecture, our p50 TTFT dropped roughly 60% and p95 dropped over 90%."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

扩展到多个 Brain 只需启动多个无状态 Harness，在需要时才连接 Hands。

---

## 四、Session：超越上下文窗口的长期记忆

### 4.1 上下文窗口的不可逆决策问题

LLM 的上下文窗口长度有限，应对长时任务的常见方法（compaction、memory tool、context trimming）都涉及**不可逆的决策**：决定丢弃什么。

Compaction 的问题是：Harness 移除 compacted messages 后，这些信息在 Claude 的上下文窗口中不可恢复——除非在 compaction 前存储。之前的学术研究探索过将 context 存储为 REPL 内可编程访问的对象，而非在窗口内维护。

### 4.2 Session 作为外部上下文对象

Managed Agents 的 Session 提供了相同的能力，但以更持久的方式：**Context 作为独立于 Claude 上下文窗口的对象，持久存储在 Session log 中**。

接口 `getEvents()` 允许 Brain 查询事件流的任意位置切片。这意味着 Brain 可以：

- 从上次停止的位置继续读取
- 回退到某个特定时刻之前的事件（rewind），查看导致特定状态的完整上下文
- 在执行特定操作前重新读取上下文

Fetched events 还可以在 Harness 内进行转换后再传给 Claude 的上下文窗口，包括为高 Prompt Cache 命中率的上下文组织，以及任意上下文工程逻辑。

> "We separated the concerns of recoverable context storage in the session and arbitrary context management in the harness because we can't predict what specific context engineering will be required in future models."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这种关注点分离意味着：Session 只保证 context 的持久性和可查询性，context 工程的职责完全推给 Harness——而 Harness 是可以随模型能力演进而迭代的。

---

## 五、多脑多手：从单 Agent 到 Agent 舰队

### 5.1 多脑（Many Brains）：横向扩展的工程

解耦 Brain 和 Hand 之后，连接每个 Brain 到多个 Hand 成为可能。Anthropic 的设计让每个 Hand 通过 `execute(name, input) → string` 接口暴露——一个 name 和 input 进入，返回一个 string。这个接口支持：

- 任意自定义工具
- 任何 MCP server
- Anthropic 自有工具

Harness 不知道也不需要知道 Sandbox 是容器、手机还是精灵宝可梦模拟器。这种抽象使得「大脑」可以连接任何执行环境。

关键是：**没有任何 Hand 与任何 Brain 耦合**。这意味着 Brain 可以将 Hands 传递给其他 Brain——这是 multi-agent 协作的核心基础设施。

### 5.2 多手（Many Hands）：跨环境任务分发

从单容器切换到多 Hand 后，Claude 需要在多个执行环境间进行推理，决定将工作发送到哪个环境——这是一个比在单一 Shell 中操作难得多的认知任务。Anthropic 选择在模型能力不足时先采用单容器，当模型能力提升后再升级到多 Hand 架构，而不是提前设计一个无法利用的架构。

> "We started with the brain in a single container because earlier models weren't capable of this. As intelligence scaled, the single container became the limitation instead."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

---

## 六、Meta-Harness：面向未来的架构设计

### 6.1 接口即契约，实现即消耗品

Managed Agents 是一个 **meta-harness**：一个对具体 Harness 实现「不抱持偏见」的系统。它的核心价值在于接口的稳定性——即便 Harness 背后的模型、Sandbox 的实现、甚至 Session 的存储方式都发生变化，这些接口依然成立。

Anthropic 明确表示：

- Claude Code 是一个优秀的 Harness，Anthropic 在各种任务中广泛使用它
- 任务专属的 Agent Harness 在窄领域内表现优异
- Managed Agents 可以容纳任何一种

### 6.2 面向模型的架构演进

文章最后一句话点明了设计哲学的核心：

> "Meta-harness design means being opinionated about the interfaces around Claude... But we make no assumptions about the number or location of brains or hands that Claude will need."

对接口保持观点鲜明（opinionated），对具体实现保持不可知（agnostic）——这是让架构经久耐用的关键。

---

## 七、与现有 Harness 设计的关系

### 7.1 Model-Agnostic 的成功验证

Anthropic 自己在 [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) 中描述的 Agent 设计原则，与 Managed Agents 的接口抽象在精神上一脉相承：通过让 Harness 与模型解耦，让同一个系统能够适应模型能力的持续提升。

### 7.2 安全设计的分层思路

OpenAI 在 [Building Codex Windows Sandbox](https://github.com/features/security) 中采用的无提权架构，与 Anthropic 的「凭证永远不在 Sandbox 可达范围内」原则相通——都是在架构层面解决安全边界问题，而非依赖模型的不完美自律。

---

## 结论与启示

Managed Agents 的 Brain-Hand-Session 三层架构揭示了一个核心洞察：**Agent 系统的可扩展性瓶颈往往不在模型能力，而在架构抽象层次**。

耦合设计在模型能力有限时是合理的——它降低了复杂度，但随着模型能力提升，耦合反而成为瓶颈。解耦的价值不在于「更好的设计」，而在于它使系统能够**随模型能力演进而演进**，而不需要推翻重来。

对 Agent 开发者的启示是：在设计 Harness 时，应将「 Brain 需要什么」和「 Hands 能提供什么」分开考虑，让 Session 成为一个独立可查询的长期记忆源，而非仅作为上下文窗口的延伸。这才是真正面向未来的 Agent 架构。

---

**引用来源**：

> "The challenge we faced is an old one: how to design a system for 'programs as yet unthought of.' Operating systems have lasted decades by virtualizing the hardware into abstractions general enough for programs that didn't exist yet."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

> "Managed Agents is a meta-harness in the same spirit, unopinionated about the specific harness that Claude will need in the future."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)