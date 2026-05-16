# Anthropic Managed Agents：解耦设计如何让 Agent 架构「活」得更久

> 原文：[Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)（Anthropic Engineering Blog，2026-04-08）

---

## 核心问题：Harness 为何会过时

Anthropic 在这篇博客里揭示了一个关键矛盾：**模型在进化，但 harness 中的假设不一定跟着变**。

他们举了一个很具体的例子：Claude Sonnet 4.5 时代，因为担心上下文接近上限时会「焦虑」（context anxiety）导致任务提前终止，所以他们在 harness 里加了 context reset 机制。但同样的 harness 放到 Claude Opus 4.5 上运行时，这个行为消失了——context reset 变成了「死代码」。

> "We found that the behavior was gone. The resets had become dead weight."

这句话点出了问题的本质：**当你发现 harness 里某段逻辑「不再需要」了，说明它曾经服务的那个模型假设已经过时了**。而问题的关键不在于某段代码该不该删，而在于整个架构是否能容纳这种变化。

Managed Agents 的解法是把 Agent 的核心组件（session、harness、sandbox）变成**接口**，而不是实现——操作系统曾经用同样的思路，让 software 摆脱了 hardware 的束缚。

---

## 三层解耦：brain、hands、session

Anthropic 的解决方案是把 Agent 分解成三个独立接口：

### 1. Session：append-only log

```python
# 每次交互只追加，不修改
emitEvent(id, event)  # 写入 session
getSession(id)        # 读取 session
```

Session 是一个纯粹的日志系统，与具体怎么执行解耦。当 harness 崩溃重启后，只需要调用 `wake(sessionId)` + `getSession(id)` 就能恢复到崩溃前的状态，继续执行。

这解决了一个根本问题：**harness 不再需要「活」着**。之前的架构里，harness 和 session 耦合在同一进程，一旦容器崩溃，整个 session 就丢了。现在 session 是外部持久化的，harness 可以随时重建。

### 2. Harness：Agent loop，不再是宠物

```python
# harness 调用 container（以及其他工具）作为普通工具
execute(name, input) → string  # 调用 sandbox
provision({resources})         # 创建新 container

# 关键：当 container 失败时，harness 把它当作工具调用失败处理
# Claude 收到错误后决定是否重试，重试时会初始化新的 container
```

Harness 变成了 cattle（牲口），不是 pet（宠物）。容器挂了？没关系，当作工具调用失败处理，Claude 决定重试，新容器自动上线。

### 3. Sandbox：执行环境，可以替换

```python
# sandbox 是被 harness 调用的外部资源
execute(name, input) → string
```

Sandbox 不知道自己被哪个 harness 调用，harness 也不知道 sandbox 是什么实现。任何符合接口的资源都可以插进来——本地容器、远程 VPC、企业私有基础设施……

---

## Pet vs Cattle：一个经典的运维隐喻在 Agent 时代的复活

Anthropic 指出他们最初把 session、harness、sandbox 全部放进同一个容器，结果制造了一个「pet」：如果容器挂了，session 也丢了；如果容器无响应，工程师只能打开 shell 进入容器调试——而这个容器里往往还有用户数据，根本不允许这样操作。

```
旧架构（Pet）：
┌─────────────────────────────┐
│  Container (Pet)             │
│  ├── Session (in-memory)     │
│  ├── Harness (in-process)   │
│  └── Sandbox (local)        │
│                             │
│  ❌ Container dies → session lost
│  ❌ Can't debug without entering container
│  ❌ Can't connect to customer's VPC
└─────────────────────────────┘
```

```
新架构（Cattle）：
┌──────────────────────────────────────┐
│  Session (外部持久化)                  │
│  ├── emitEvent() ← harness 写入       │
│  └── getSession()                     │
│                                       │
│  Harness (可重建)                     │
│  ├── wake(sessionId)                  │
│  └── for each turn: emit → call API   │
│                                       │
│  Sandbox ← 被当作工具调用              │
│  └── execute(name, input) → string    │
│      (可以是任何符合接口的实现)        │
└──────────────────────────────────────┘

✅ Container dies → tool-call error → Claude retry → new container
✅ Harness dies → new harness → wake(sessionId) → resume
✅ 任何资源都可以成为 sandbox
```

这个思路在分布式系统里并不新鲜——Netflix 早在 2010 年代就用「no pet servers」原则改造了他们的基础设施。但把它引入 Agent 架构设计，Anthropic 是第一次系统性地说清楚的。

---

## 一个反直觉的教训：AI Agent 的工程问题，本质上是分布式系统问题

这篇文章最值得记下的结论是：**当模型能力提升后，之前用来弥补模型短板的 harness 逻辑可能会变成冗余**。

这意味着 harness 必须设计成可演进的：当你发现某段假设不再成立时，能轻易地把它去掉，而不是被它困住。Anthropic 的解耦架构提供了这个能力——因为每个组件都是可替换的，所以即使模型出了新能力，旧的假设可以被逐个退役。

这个教训对任何在做 Agent 架构的人是适用的：**不要把当前的模型能力假设写死在 harness 里，要让它们可以撤退**。

---

**引用来源**

> "A common thread across this work is that harnesses encode assumptions about what Claude can't do on its own. However, those assumptions need to be frequently questioned because they can go stale as models improve."

> "Decoupling the brain from the hands meant the harness no longer lived inside the container. It called the container the way it called any other tool: execute(name, input) → string. The container became cattle."

---

*归档目录：`harness/` | 来源：Anthropic Engineering Blog | 2026-05-16*