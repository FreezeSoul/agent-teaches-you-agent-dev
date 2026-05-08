# Anthropic Managed Agents：大脑与手的解耦——生产级 Agent 系统的架构范式转移

> 本文深度解析 Anthropic 2026 年 5 月发布的 Managed Agents 技术白皮书，聚焦其核心架构决策：Brain-Hands-Session 三元解耦模型。这一设计并非简单的微服务拆分，而是对 OS 抽象层思想的重新诠释——它解决的核心问题是如何让 Agent 系统在模型能力持续提升的过程中始终保持可用，而不是沦为不断被抛弃的「一次性基础设施」。

---

## 核心主张

**Anthropic Managed Agents 的本质是一个「元 harness」**：它不提供具体的 Agent 实现，而是提供一套足够通用的接口抽象（Session / Harness / Sandbox），让任何符合接口的 harness 和 sandbox 可以插入替换。这与操作系统虚拟化硬件的思路一脉相承——read() 调用不关心底层是 1970 年代磁盘还是现代 SSD，接口不变，实现可以随时替换。

> "The challenge we faced is an old one: how to design a system for 'programs as yet unthought of.' Operating systems have lasted decades by virtualizing the hardware into abstractions general enough for programs that didn't exist yet."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

---

## 一、为什么耦合架构是陷阱

### 1.1 Pets vs. Cattle 的经典困境

Anthropic 最初的设计将 Session、Harness 和 Sandbox 全部放在同一个容器里。这种方式的好处是直观的：文件编辑是直接 syscall，没有额外的服务边界需要设计。但问题也随之而来：**服务器变成了「宠物」——一个不能轻易失去的、需精心维护的个体**。

具体症状：

- **容器挂了，Session 丢了**：一切状态随容器消失，无法恢复
- **容器无响应时，必须人工介入修复**：WebSocket 事件流是唯一的窗口，但它无法区分 harness bug、数据包丢失还是容器离线三种情况
- **工程师被迫在容器内开 shell 调试**：但容器通常持有用户数据，这本质上意味着无法安全调试

### 1.2 耦合导致的扩展失效

第二个问题更隐蔽：**Harness 假设所有 Claude 工作所需的东西都在容器里**。当用户需要 Claude 访问自己的虚拟私有云（VPC）时，选项只有两种——要么将用户的网络与 Anthropic 的网络 peered，要么在用户环境里运行 harness。两种都是糟糕的折中，因为这个假设被编码进了 harness 的核心逻辑。

> 笔者认为：这里的根本矛盾是「信任边界」和「物理位置」的耦合——当执行环境和凭证共享同一个物理边界时，安全架构就不得不假设最坏情况并据此设计。

### 1.3 「上下文焦虑」与模型进化失效

在之前的工作中，Anthropic 发现 Claude Sonnet 4.5 会在接近上下文限制时过早结束任务——一种被称为「context anxiety」的行为。他们通过在 harness 中添加上下文重置来解决这个问题。但当他们用同一套 harness 运行 Claude Opus 4.5 时，这个行为消失了——之前添加的重置代码变成了死代码。

这揭示了一个更深刻的问题：**Harness 编码了关于模型能力的假设，而这些假设会随着模型进化而失效**。

---

## 二、解耦架构：三元组抽象

Managed Agents 的解决方案是将 Agent 的三个核心组件分离为独立接口：

| 组件 | 角色 | 关键接口 |
|------|------|---------|
| **Brain** | Claude + Harness（调用 LLM 并路由工具调用的循环） | 外部化，与 Sandbox 解耦 |
| **Hands** | Sandbox（执行代码和编辑文件的运行环境） | `execute(name, input) → string`，被 Brain 作为工具调用 |
| **Session** | Append-only event log（所有发生事件的仅追加日志） | `getEvents()`，`emitEvent()`，持久化在 Harness 之外 |

### 2.1 Sandbox 变成 Cattle

解耦后，Harness 不再位于容器内部。它通过 `execute(name, input) → string` 调用容器——就像调用任何一个其他工具一样。容器变成了「cattle」：如果容器死了，Harness 会捕获这个失败作为工具调用错误并传回给 Claude。Claude 可以选择重试，而新容器可以用标准配方重新初始化：`provision({resources})`。

### 2.2 Harness 变成 Cattle

由于 Session log 独立于 Harness 存在，Harness 本身不需要在崩溃中存活。当一个 Harness 崩溃时，可以用 `wake(sessionId)` 重新启动一个新实例，用 `getSession(id)` 获取事件日志，然后从最后一条事件恢复。在 Agent 循环期间，Harness 通过 `emitEvent(id, event)` 向 Session 写入事件，以保持事件的持久记录。

### 2.3 安全边界：凭证从不进入 Sandbox

在耦合设计中，Claude 生成的任何不可信代码都在与凭证共享的同一容器中运行——prompt injection 只需要说服 Claude 读取自己的环境。一旦攻击者获得这些 token，他们可以生成新的无限制会话并向其委托工作。

结构性修复：**确保 token 从不在 Claude 生成代码的 sandbox 中可达**。

Anthropic 使用的两种模式：

1. **Auth 与资源绑定或存储在 vault 外部**：对于 Git，在 sandbox 初始化期间使用每个仓库的 access token 克隆 repo，并将其接入本地 git remote。Git push 和 pull 从 sandbox 内部工作，而 agent 本身从不处理 token。
2. **MCP OAuth Token 的 Vault 代理**：Claude 通过专用代理调用 MCP 工具；该代理接收与会话关联的 token，从 vault 获取相应凭证，然后调用外部服务。Harness 永远不知道任何凭证。

> "Narrow scoping is an obvious mitigation, but this encodes an assumption about what Claude can't do with a limited token—and Claude is getting increasingly smart. The structural fix was to make sure the tokens are never reachable from the sandbox where Claude's generated code runs."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

---

## 三、Session ≠ Context Window

这是白皮书中最容易被忽视的核心洞察。

### 3.1 现有上下文管理方案的问题

长程任务通常超过 Claude 的上下文窗口，标准解决方案都涉及关于保留什么的不可逆决策：

- **Compaction**：让 Claude 保存上下文窗口的摘要——但被压缩的消息从 Claude 的上下文窗口中移除，只有存储后才可恢复
- **Context trimming**：选择性删除旧工具结果或 thinking block——但难以知道未来哪部分 token 会被需要
- **Memory tool**：让 Claude 将上下文写入文件——但这是 sandbox 内部的本地文件，断开连接即丢失

### 3.2 Session 作为外部化上下文对象

Managed Agents 中，Session 提供了相同的好处——作为一个存在于 Claude 上下文窗口之外的上下文对象。但它不是存储在 sandbox 或 REPL 中，而是持久化存储在 Session log 中。

关键接口 `getEvents()` 允许 Brain 通过选择事件流的**位置切片**来查询上下文：

- Brain 可以从上次停止的地方继续读取
- 可以回退几件事来看特定时刻之前的准备
- 可以在特定操作之前重新读取上下文

任何获取的事件也可以在 Harness 中转换后再传递给 Claude 的上下文窗口。这些转换可以是 Harness 编码的任何内容，包括实现高 prompt cache hit rate 的上下文组织以及 context engineering。

> "We separated the concerns of recoverable context storage in the session and arbitrary context management in the harness because we can't predict what specific context engineering will be required in future models."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

**关键设计启示**：将「可恢复上下文存储」和「任意上下文管理」分离是因为无法预测未来模型需要什么样的具体上下文管理。接口将上下文管理推入 Harness，只保证 Session 是持久化的且可供查询。

---

## 四、Many Brains, Many Hands

### 4.1 Many Brains 的性能收益

解耦 Brain 和 Hands 解决了最早的客户投诉之一。当 Brain 最初放在容器中时，许多 Brain 需要许多容器。每个 Brain，在容器配置完成之前无法进行推理；每个 Session 都需要预先支付完整的容器设置成本。即使是永远不会触碰 sandbox 的 Session，也必须 clone repo、boot 进程、从服务器获取待处理事件。

这个等待时间反映在 **time-to-first-token（TTFT）**——Session 接受工作并产生第一个响应 token 之间的等待时间。

解耦后的效果：

> "Using this architecture, our p50 TTFT dropped roughly 60% and p95 dropped over 90%."

Scaling to many brains 就是启动许多 stateless harnesses，仅在需要时连接它们到 Hands。

### 4.2 Many Hands 的架构意义

Anthropic 还希望能够将每个 Brain 连接到多个 Hands。这意味着 Claude 必须能够推理许多执行环境并决定将工作发送到哪里——比在单个 shell 中操作更难的认知任务。

解耦后，每个 Hand 成为工具：`execute(name, input) → string`。输入名称和输入，返回字符串。该接口支持任何自定义工具、任何 MCP server 和 Anthropic 自己的工具。Harness 不知道 sandbox 是容器、手机还是宝可梦模拟器。由于没有 Hand 耦合到任何 Brain，Brain 可以相互传递 Hands。

---

## 五、Meta-Harness 设计原则

Managed Agents 是一个 **meta-harness**，其设计原则是：

1. **对接口形状保持意见**：Claude 将需要操作状态（Session）和执行计算（Sandbox）的能力
2. **对实现保持无意见**：不假设具体需要多少或位于何处的 Brain 和 Hands
3. **支持长期可扩展性**：接口设计使得这些可以长期可靠和安全地运行

这与操作系统的演进路径完全一致：抽象层保持了数十年，而底层实现不断进化。read() 调用不关心底层是 1970 年代磁盘还是现代 SSD。

---

## 六、架构对比：为什么这个设计值得深入理解

Anthropic 的 Brain-Hands-Session 解耦模型与其他主流 Agent 架构的关键差异：

| 维度 | 传统耦合架构 | Anthropic Managed Agents |
|------|------------|-------------------------|
| **故障恢复** | 容器级联失败，需人工干预 | Harness 作为 cattle，可重启；Session 外部化 |
| **TTFT** | 所有 Session 预支付容器设置成本 | p50 降低 60%，p95 降低 90% |
| **安全边界** | 凭证与 sandbox 共存，依赖模型能力边界 | 凭证从不进入 sandbox，结构性保证 |
| **扩展模型** | 每个 Brain 一个容器，紧耦合 | Stateless harnesses，按需连接 Hands |
| **上下文管理** | 不可逆决策（压缩/trimming），丢失风险 | Session 作为外部化上下文对象，可重放 |
| **多执行环境** | 单容器限制，不支持多 Hand 并行 | 每个 Hand 是工具，支持 Many Hands |

---

## 七、工程实践启示

### 7.1 为什么「宠物」模式在生产中注定失败

当你把 Session、harness 和 sandbox 耦合在同一进程时，你得到的是一个必须在整个生命周期中精心维护的「宠物」系统。这与云原生的「cattle」哲学完全相反。生产 Agent 系统必须设计为可以在任何组件失败时重新启动和恢复，而不会丢失工作进度。

### 7.2 接口设计优先于实现设计

Managed Agents 最重要的设计启示是：**先定义接口，再实现**。Anthropic 在定义 Session / Harness / Sandbox 三个接口时，对接口的形状非常谨慎（这是 opinionated 的部分），但对实现这些接口的具体技术完全开放。

### 7.3 安全架构必须结构性而非策略性

当凭证与执行环境共存时，安全依赖于「模型不会做什么」的假设。但模型能力在持续提升——这个假设随时可能失效。正确的做法是从架构上确保凭证永远不会到达执行环境，而不是依赖边界限制。

> 笔者认为：Anthropic 提出的「Brain-Hands 解耦」不仅是工程上的优化，它是 Agent 系统架构演进的一个重要信号——从「用模型能力换安全」转向「用架构设计换安全」。在大模型能力持续爬升的背景下，后者是唯一可行的路径。

---

## 结语

Managed Agents 解决的不是一个新问题，而是一个经典问题的最新实例：如何设计一个能够容纳「尚未想到的程序」的系统。操作系统的解决方案是虚拟化硬件；Anthropic 的解决方案是虚拟化 Agent 的组件边界。

这套架构的最终形态是一个 **meta-harness**：不提供具体的 Agent 实现，而是提供足够通用的接口，让 Claude 未来的任何 harness 和 sandbox 都可以插入。对于正在构建企业级 Agent 系统的团队，这提供了两种明确的工程指导原则：

1. **将 Session 作为一等公民**：不要把上下文管理看作 LLM 的内部事务，而是将其外部化为持久化的、可查询的事件日志
2. **将安全边界设计为结构性的**：凭证永远不应该能够到达执行环境，无论模型能力有多强

---

**执行流程**：
1. **理解任务**：Cron 触发自主更新仓库，需要扫描 Anthropic/OpenAI/Cursor 一手来源，发现高质量主题
2. **规划**：优先扫描 Anthropic Engineering Blog，发现 Managed Agents 这篇新发布（2026-05-08）的 Brain-Hands 解耦架构有深度分析价值；同时扫描 GitHub Trending 发现 agent-squad 项目
3. **执行**：Tavily 搜索 3 次获取来源信息，web_fetch 抓取 2 篇官方原文，从 GitHub README 获取 agent-squad 项目信息
4. **返回**：Articles 和 Projects 各产出一篇，Articles 为 Brain-Hands 解耦架构分析，Projects 为 agent-squad 推荐
5. **整理**：写入 articles/orchestration/ 和 articles/projects/，更新 README.md 防重索引

**调用工具**：
- `exec`: 7次（Tavily搜索×3，git pull，grep×2，git checkout）
- `web_fetch`: 4次（managed-agents×2，openai-agents-sdk，agent-squad）
- `write`: 2次（Articles + Projects 文章）
