# Anthropic Managed Agents：Brain/Hands/Session 架构解析

> **核心问题**：为什么大多数 Agent 原型能跑、生产环境却千疮百孔？Anthropic 用 Managed Agents 给出了一个系统性答案——不是修修补补，而是把整个架构推翻重来。
>
> **读完能得到什么**：理解 Brain/Hands/Session 三元组抽象的工程动机、Session 作为外部上下文的设计原理、以及这个架构如何同时解决安全、可观测性和水平扩展三个问题。

---

## 一、问题的根源：单体 Agent 为什么跑不通

最直觉的 Agent 架构是把所有东西塞进一个容器：Session 状态、编排循环（harness loop）、代码执行环境。原型阶段这没问题。

但一旦进入生产，问题接踵而至：

| 问题 | 后果 |
|------|------|
| 容器崩溃 | Session 数据全丢，任务必须从头重来 |
| 调试困难 | 所有状态混在一起，无法重现特定执行节点 |
| 扩展性差 | 每个 Agent 独占容器，空闲时也在烧钱 |
| **安全问题** | LLM 和代码执行环境共存，Prompt Injection 的后果不只是"输出了错误答案"——而可能是**凭据被盗** |

最后一行的安全问题最为致命。传统架构中，LLM 的 API Key 和代码执行环境在同一个容器里。一旦 Prompt Injection 攻击成功，攻击者不只是操控了 Agent 的输出——而是可以直接拿到可以调用真实资源的凭据。blast radius 是一个完整的企业账户。

这不是靠"加一层 Prompt 过滤"能解决的问题。安全必须从架构层面强制。

---

## 二、解法：三个虚拟化组件

Anthropic 的答案是把 Agent 拆成三个独立组件，每个有独立的生命周期：

### 2.1 Session — 持久化记忆

```
Append-only event log
Lives outside Claude's context window
Supports: getEvents(), rewind, slice, positional access
```

Session 是整个系统的单一真实数据源（Single Source of Truth）。**所有**发生的事件都被记录在这里。关键点：Session 和 Context Engineering（上下文工程）是两个不同的问题域——Session 负责持久化和可恢复性，Context Engineering 负责从大量事件中筛选出当前需要的内容送入 Context Window。

Session 的接口设计很克制：只支持追加、rewind 和位置访问。这不是 RAG，不需要语义检索。Harness 在每次调用 Claude 前从 Session 中**按需读取**相关子集做上下文组装。

### 2.2 Harness — 无状态编排器

```
Calls Claude API → routes tool calls → writes to Session
Stateless by design → crash and recover from Session
Transforms Session events → Claude's context window
```

Harness 是整个架构中最关键的设计决策：**无状态化**。任何一个 Harness 实例可以从任何一个 Session 恢复，继续上次中断的地方。这意味着水平扩展是免费的——不需要分布式锁、不需要粘性 Session，新实例启动即用。

Harness 的职责是：调用 Claude API → 接收工具调用指令 → 操作 Sandbox 执行 → 将结果写入 Session → 循环。循环本身不持有任何状态。

### 2.3 Sandbox — 可抛投执行环境

```
Container-based isolated execution
"Cattle, not pets" — disposable, replaceable
Lazy initialization — provisioned only when needed
```

Sandbox 是"可抛投的"（disposable）。这一点和传统架构有根本区别——传统架构里容器是"宠物"，要小心维护；Managed Agents 里 Sandbox 是"牛"，病了直接杀掉换新的，不用debug。

更重要的是**延迟初始化**（lazy initialization）：Sandbox 只在 Agent 真正需要执行代码时才启动。没有任务时就空着，不消耗资源。

---

## 三、Brain vs Hands：核心抽象

三个组件的组合产生了两个更高层次的抽象：

```
Brain = Claude + Harness（推理与决策）
Hands = Sandbox + Tools（执行与操作）
Session = Event Log（记忆与持久化）
```

Brain 和 Hands 之间的接口是什么？只有一个方法：

```
execute(name, input) → string
```

这是整个契约。Harness 不需要知道 Hands 背后是一个容器、一台手机还是一个模拟器。只要实现了这个接口，就是合法的"Hands"。

这个抽象的直接工程价值是**多态性**：Hands 的实现可以随时替换——本地容器换远程虚拟机、换移动端——Brain 的代码不需要改。

更重要的是：**Brains 可以把 Hands 互相传递**。这为多 Agent 协作提供了基础——一个 Brain 可以把自己的某个执行能力（Hands）传递给另一个 Brain，让对方直接操作自己的工具。

---

## 四、Session 作为外部上下文：解决 Context Window 焦虑

Context Window 是有限的，但 Agent 任务可以是小时级甚至天级的。这是一个结构性问题，不是靠增大 Window 能解决的（窗口再大也会有溢出的任务）。

Managed Agents 的解法是：**Session 作为外部上下文**。

```
Session (all events, full history)
  → Harness transforms (选择性读取)
  → Claude context window (relevant subset only)
```

这产生了一个重要的分离：

- **可恢复存储**（Recoverable Storage）：Session 全量日志，负责持久化
- **上下文工程**（Context Engineering）：Harness 的职责，负责从全量中筛选相关子集

两者不再是同一件事。这个分离让系统可以优雅地处理跨 Context Window 的长时任务——不需要把所有历史硬塞进 Window，只需要让 Harness 知道"当前最相关的是什么"。

> 笔者认为：这解决了之前工程 blog 中提到的"Context Anxiety"问题（Claude Sonnet 4.5 在感知到 Context Window 快满时会提前结束任务）。当 Session 是外部的、可选择性读取的时候，Harness 可以主动管理上下文注入策略，而不是让模型自己去猜"还剩多少空间"。

---

## 五、安全：架构层面的强制，而非策略层面的呼吁

传统 Agent 架构中，安全靠的是"不要把 Key 放在代码里""不要相信 Tool 输出"这类规则。规则的问题是：人会忘，规则会过时，有漏洞的代码一个 assert 没写好就全穿。

Managed Agents 的安全设计是**架构强制**的：

| 原则 | 实现方式 |
|------|---------|
| 凭据不进入 Sandbox | Git Token 在初始化时直接 wire 到本地 remote，Agent 永远碰不到；MCP Tools 通过专用代理访问，Token 是 Session-scoped 的；OAuth Token 存在 secure vault 里 |
| 即使 Sandbox 被攻破 | 攻击者拿到的是空壳，凭据不在那里 |
| 执行环境隔离 | 每个 Sandbox 是独立容器，隔离的不是进程，是整个网络和凭据空间 |

这解决的不只是 Prompt Injection 的后果，而是直接消除了攻击面。安全是架构的**自然结果**，而不是额外叠加的检查清单。

---

## 六、性能数据：延迟降低一个数量级

Decoupling 的性能收益是真实的：

| 指标 | 改善 |
|------|------|
| p50 TTFT | ~60% 降低 |
| p95 TTFT | >90% 降低 |

p95 的改善才是重点。Tail Latency 降低 90% 意味着在高峰期用户体验不会断崖式下降。这对于需要长时间运行的 Agent 任务（代码审查、数据处理、多步骤分析）尤为关键。

背后的原因：Lazy Init 意味着 Hands 不需要提前启动。Brain 可以先推理、后启动 Hands。传统的单体架构必须整个容器一起跑，空闲时间全在烧钱。

---

## 七、多 Hands 与多 Brain：水平扩展的完整图景

三个组件的独立生命周期，使得扩展不是修修补补，而是系统性的：

- **多 Brain**：无状态的 Harness 实例可以任意水平扩展，用 Session 作为协调点
- **多 Hands**：每个 Tool 实现 `execute(name, input) → string`，天然支持异构执行环境
- **Brain-to-Brain Hand-off**：一个 Brain 可以把自己的 Hands 传递给另一个 Brain，实现真正的跨 Agent 能力共享
- **MCP 天然支持**：任何 MCP Server 都可以作为 Hands 接入

这给多 Agent 协作提供了一套干净的物理层协议——不需要规定"Agent 之间怎么通信"，只需要规定"Brain 和 Hands 之间的接口是什么"。

---

## 八、已知局限

尽管这是目前最完整的生产 Agent 基础设施设计，以下问题仍未解决：

**1. Session 是扁平的 Event Log**

Anthropic 的 Session 是一个 Append-only 日志，适合恢复和重放，但对于**语义关系查询**不够用。当一个 Agent 需要知道"这个客户的所有历史工单和当前合同之间的关系"时，Event Log 无法回答这个问题。这需要更结构化的知识图谱层。

**2. Hands 的接口过于简单**

`execute(name, input) → string` 的抽象力很强，但无法表达复杂的能力描述（比如这个 Tool 支持流式输出、那个 Tool 是异步的）。随着 Hands 生态扩大，接口契约需要更丰富的元数据。

**3. 定价模型仍需市场验证**

$0.08/session-hour + 标准 Token 费率对于高频场景成本不低。早期客户（Notion、Rakuten、Asana）报告 10x 部署加速，但这是建立在这些公司有充足预算的前提下——中小团队能否接受这个定价曲线，还有待观察。

**4. 多 Agent 协调层缺失**

Managed Agents 提供了 Brain-to-Brain Hand-off 的基础能力，但如何做全局协调、如何处理冲突、如何做分布式事务，都没有答案。这不是 Managed Agents 的问题，而是整个行业在 Multi-Agent 协调层上还没有共识。

---

## 九、工程建议

基于这个架构，以下是笔者认为值得借鉴的工程实践，无论你是否使用 Managed Agents：

**1. 让 Harness 真正无状态**

如果你在实现自己的 Agent 编排系统，第一件事是把编排循环的状态全部外置到某个持久化存储（不一定是 Session，也可以是 Redis/Postgres），让 Harness 实例可以随时重启、任意扩展。无状态设计是水平扩展的前提。

**2. 用接口抽象替代具体实现**

把 Tool 执行抽象成 `execute(name, input) → string` 这样的简单契约。你的 Harness 不应该知道也不应该关心这个 Tool 是本地 Bash、远程 MCP Server 还是云函数。接口的稳定性决定了你换底的灵活性。

**3. 凭据必须和执行环境物理隔离**

即使你不做完整的 Brain/Hands 分离，至少要把 API Key、OAuth Token 这些凭据放在 Sandbox 绝对访问不到的地方（比如独立的 Secret Manager），而不是通过环境变量注入进去。环境变量在容器逃逸场景下是可见的。

**4. 把 Context Window 管理的决策权交给 Harness**

不要让模型自己去感知 Context Window 的容量。Harness 应该主动决定每次送入多少历史、怎么压缩、什么时候触发重置。这是你能设计的，不是模型能猜准的。

---

## 参考文献

- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) — Anthropic 官方工程博客（第一手来源，核心参考）
- [Claude Managed Agents Architecture: Decoupling Brain from Hands](https://dev.to/_46ea277e677b888e0cd13/anthropic-managed-agents-architecture-decoupling-brain-from-hands-for-scalable-ai-agents-295k) — DEV Community 详细解读
- [The Architectural Genius of Anthropic's Managed Agents](https://www.epsilla.com/blogs/anthropic-managed-agents-decoupling-brain-hands-enterprise-orchestration) — Epsilla 视角分析，Session 作为语义图的延伸讨论
- [Breakdown of Claude Managed Agents - Reddit](https://www.reddit.com/r/ClaudeCode/comments/1sg2e29/) — 社区讨论与定价信息
- [Claude Managed Agents 文档](https://platform.claude.com/docs/en/managed-agents/overview) — API 接入文档
