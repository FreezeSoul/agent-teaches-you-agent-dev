# Anthropic Managed Agents：面向未来的 Meta-Harness 架构设计

## 核心问题

当一个 Agent 系统需要支撑数年乃至更久的生命周期时，如何设计一个能适应「尚未设想的程序」的架构？Anthropic 的解法是**将 Agent 的核心组件虚拟化为稳定接口**，使 Brain、Hands、Session 都可以独立替换，而不影响整体系统的稳定性。

> "Decades ago, operating systems solved this problem by virtualizing hardware into abstractions—process, file—general enough for programs that didn't exist yet. The abstractions outlasted the hardware."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

---

## 问题起源：Pet 运维模式带来的困境

Anthropic 最初将 Session、Harness 和 Sandbox 全放在单一容器内。这种紧耦合设计带来了两个核心问题：

### 问题一：Session 的脆弱性

容器死亡 → Session 丢失。每次容器无响应，都需要工程师手动进入容器调试——但容器内同时持有用户数据，这种「调试」本质上是隐私风险的来源。

### 问题二：安全边界固化

当所有组件共处一室时，Claude 生成的任何不可信代码都能访问同一容器内的凭据。一次 Prompt Injection 成功，攻击者就能利用这些凭据启动新的无限制会话。

> 笔者的判断：**Pet 模式是 Agent 服务化的最大障碍**。当系统需要 scale 到数十个并发会话时，手工维护单个容器的思路必然崩溃。必须转向 Cattle 模式——容器是可替换的，而不是需要修复的。

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
┌──────────────────────────────────────────────────────┐
│              Session（持久化日志）                   │
│  ├─ Append-only event stream                        │
│  ├─ 可被任意 Brain 读取（断点重连）                  │
│  └─ 存储在 Session 内，而非 Sandbox 内               │
└──────────────────────────────────────────────────────┘
```

### Hands 如何变成 Cattle

当 Harness 不再位于容器内部，容器就变成了一个**工具**——`execute(name, input) → string`。当容器死亡，Harness 捕获的是一次工具调用失败，而非系统崩溃。Claude 可以选择重试，系统只需用标准配方重新初始化一个新容器：

```python
# 容器死亡 → 工具调用失败 → Harness 决策是否重试
try:
    result = execute("sandbox", {"action": "run", "code": "..."})
except ContainerDiedError:
    # 触发标准 recipe 重建容器
    provision({"resources": "standard"})
    # 重试
    result = execute("sandbox", {"action": "run", "code": "..."})
```

> "If the container died, the harness caught the failure as a tool-call error and passed it back to Claude. If Claude decided to retry, a new container could be reinitialized with a standard recipe."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

### Session 与 Context Window 的本质区别

Anthropic 明确区分了两个概念：

- **Context Window**：Claude 的工作内存，有限且需要主动压缩/丢弃
- **Session**：持久化的 Event Log，存储在 Claude 外部，可按需查询

```
Context Window（有限，可丢失）：
┌─────────────────────────────────┐
│  System + Messages + Tool Results │
│  ← 需要 compaction，丢什么由模型决定 │
└─────────────────────────────────┘

Session（持久，可查询）：
┌─────────────────────────────────────────────────────┐
│  getEvents(offset=-100) → 取最近100条事件           │
│  getEvents(before=feature_start) → rewind          │
│  ← 任意变换后传给 Context Window                    │
└─────────────────────────────────────────────────────┘
```

这意味着 Context 管理逻辑（如何组织、压缩、裁剪）被推入 Harness 层，而 Session 只负责**可靠存储和按需检索**。两者关注点分离对未来模型的适配至关重要。

---

## 安全边界：Token 从不进入 Sandbox

在紧耦合设计中，不可信代码和凭据共处一室。Anthropic 通过两种模式确保凭据永远不可达：

### 模式一：Auth Bundle（轻量级）

凭据与资源绑定，在容器初始化时注入。典型案例是 Git：

```
Sandbox 初始化时：
  1. 用 repo 的 access token clone 仓库
  2. 将 token 写入本地 git remote
  3. 容器内的 git push/pull 正常工作
  4. Claude 从不「看到」token——它只调用 git 命令
```

### 模式二：Vault + Proxy（高安全场景）

对于需要动态获取的 OAuth token：

```
Claude → MCP Proxy（带 session token）→ Vault → External Service
         ↑ 代理层注入凭据           ↑ 保险箱  ↑ 外部服务
         Claude 永远不知道 token 是什么
```

> "The harness is never made aware of any credentials."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

---

## Scale 效果：TTFT 降低 60%~90%

解耦带来的不仅是运维简化，还有显著的性能收益：

| 指标 | 紧耦合设计 | 解耦后 |
|------|-----------|--------|
| **p50 TTFT** | 基线 | **降低 ~60%** |
| **p95 TTFT** | 基线 | **降低 >90%** |
| 并发 Brain 数 | 受容器数限制 | **无上限**（stateless harness）|

性能提升的根源：**推理不再等待容器初始化**。在紧耦合设计中，每个 Session 都需要等待容器启动才能开始推理；在解耦设计中，编排层直接从 Session Log 提取待处理事件，推理可以立即开始，容器按需才启动。

---

## Meta-Harness 设计哲学

Managed Agents 的核心定位是**一个能容纳不同 Harness 的系统**，而非一个特定场景的最优解：

> "We expect harnesses to continue evolving. So we built Managed Agents: a hosted service... through a small set of interfaces meant to outlast any particular implementation—including the ones we run today."

这意味着：
- **Claude Code** 是 Managed Agents 可以容纳的一种 Harness
- **Task-specific Agent**（如 Specialized Coding Agent）也是可容纳的
- **未来尚未设想的 Harness** 同样可以接入

接口是稳定的（Session / Brain / Hands），实现是可替换的——这是操作系统虚拟化的标准思路在 Agent 领域的应用。

---

## 与其他解耦方案的对比

| 维度 | Anthropic Managed Agents | Cursor Multi-Agent Kernel | OpenClaw |
|------|--------------------------|--------------------------|----------|
| **解耦维度** | Brain / Hands / Session | Planner / Worker | Skill / Tool / Memory |
| **Session 持久化** | ✅ 原生 Event Log | ❌ 依赖协调协议 | ✅ Memory 分层 |
| **Token 安全** | ✅ Vault+Proxy 分离 | ❌ Sandbox 内嵌 | ✅ 分层权限 |
| **Harness 可替换性** | ✅ Meta-harness 设计 | ❌ 内核紧耦合 | ✅ Skill 组合 |
| **Scale 路径** | Stateless harness + 按需 Hands | 分层 Planner 分发 | Skill Registry + 并发 |

---

## 适用边界与未解问题

### 适用场景

- **长时多会话任务**：跨天、跨周的长周期任务，Session 持久化是刚需
- **多租户隔离**：不同客户的 Brain 不能共享同一容器，需要严格安全边界
- **需要接入多种工具链**：MCP / 自定义 Tools / 外部服务的统一接入层

### 尚未完全解决的开放问题

1. **Many Hands 的认知负载**：Claude 需要主动决定将任务分发到哪个 Hand，这要求模型具备更复杂的调度能力——这是未来模型能力的要求
2. **跨 Brain 的 Hands 共享**：Brains 可以互相传递 Hands，但这要求更复杂的所有权管理机制
3. **特定领域的泛化**：当前 demo 主要面向 Web 开发，其他领域需要验证

---

## 一句话结论

Anthropic Managed Agents 展示了**操作系统虚拟化思维在 Agent 架构中的应用**：通过 Brain-Hands-Session 三组件解耦 + Session 外部化 + Vault 凭据分离，实现了一个能容纳不同 Harness 的 Meta-Harness 系统。TTFT 降低 60%~90% 的性能收益是解耦带来的额外红利，而安全边界的结构化加固则是面向多租户生产部署的基础设施要求。

---

## 原文引用

> "Decades ago, operating systems solved this problem by virtualizing hardware into abstractions—process, file—general enough for programs that didn't exist yet. The abstractions outlasted the hardware. The read() command is agnostic as to whether it's accessing a disk pack from the 1970s or a modern SSD."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

> "Managed Agents follow the same pattern. We virtualized the components of an agent: a session, a harness, and a sandbox. This allows the implementation of each to be swapped without disturbing the others."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

> "By coupling everything into one container, we ran into an old infrastructure problem: we'd adopted a pet. In the pets-vs-cattle analogy, a pet is a named, hand-tended individual you can't afford to lose, while cattle are interchangeable."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

> "Decoupling the brain from the hands meant the harness no longer lived inside the container. It called the container the way it called any other tool: execute(name, input) → string."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)
