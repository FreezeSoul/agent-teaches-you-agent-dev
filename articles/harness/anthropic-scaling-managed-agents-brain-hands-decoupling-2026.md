# Anthropic Managed Agents：解耦 Brain 与 Hands 的架构突破

> 原文：Anthropic Engineering Blog — [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)（2026-04-08）

## 核心论点

Anthropic 提出：Harness 层的核心问题不是"Claude 能做什么"，而是"Harness 的假设何时失效"。随着模型能力提升，早期对工具和执行环境的假设会变得陈旧。**解耦 Brain（推理与决策）与 Hands（执行与操作）是解决这个问题的主流方向**。

---

## 一、为什么耦合架构注定失败

Anthropic 最初将所有组件放入单一容器（session + harness + sandbox 共处），这是"宠物模式"（pets vs cattle）的典型陷阱：

> "When we coupled everything into one container, the server became that pet; if a container failed, the session was lost. If a container was unresponsive, we had to nurse it back to health."
> — Anthropic Engineering Blog

这种架构带来三个核心问题：

**1. 单点故障导致全量状态丢失**
- 容器崩溃 → Session 丢失 → 所有上下文不可恢复
- 调试窗口唯一：WebSocket event stream，但无法区分 harness bug / packet drop / container offline

**2. 资源访问耦合到特定网络拓扑**
- 客户要求连接 Claude 到自己的 VPC，必须 peer 网络或本地运行 harness
- 假设"所有资源都在容器附近"成为扩展性杀手

**3. 安全边界与资源耦合**
- 在同一容器中运行未信任代码与凭据
- Prompt injection 只需说服 Claude 读取自己的环境即可获取 tokens

---

## 二、解耦方案：三个接口的抽象层

Anthropic 的解决方案是虚拟化 Agent 组件：

```
Session（append-only log of all events）
     ↑ getEvents() / emitEvent()
Brain（Claude + Harness loop）
     ↑ execute(name, input) → string
Sandbox（Execution environment: containers, tools, external services）
```

### 1. Session：Context 对象而非 Context Window

长程任务超过模型 context window 时，标准方案（compaction / memory / trimming）都涉及不可逆的上下文取舍：

> "Prior work has explored ways to address this by storing context as an object that lives outside the context window."
> — Anthropic Engineering Blog

Managed Agents 的 Session 提供了外部化的 Context 对象：
- `getEvents()`：允许 Brain 查询任意位置的事件切片（rewind / resume）
- 任何 transformation 可以由 harness 在传入 Claude context 前执行（context organization / prompt cache optimization）
- **关键设计**：上下文存储（session）与上下文管理（harness）的关注点分离

### 2. Brain → Hands 的工具化接口

```typescript
// execute(name, input) → string
// 一个 name + input 进，返回 string
// 不关心 sandbox 是什么：container / phone / Pokémon emulator
```

解耦带来了两个关键收益：

**TTFT 改善（Time-to-First-Token）**：
- 原本每个 session 都必须等待容器完全provision（包括 clone repo / boot process / fetch pending events）
- 解耦后：如果 session 不需要容器，不等待
- 结果：p50 TTFT 下降约 60%，p95 TTFT 下降超过 90%

**容错恢复**：
- 容器死亡 → harness 捕获为 tool-call 错误 → 传给 Claude → Claude 决定重试
- 新容器可通过 `provision({resources})` 重新初始化
- harness 本身也变成 cattle：session log 外部化后，harness 不需要 survive crash

### 3. Security Boundary：Tokens Never Reach Sandbox

```
┌─────────────────────────────────────────────────┐
│                    Sandbox                      │
│   (Claude 生成的未信任代码在这里执行)             │
└─────────────────────────────────────────────────┘
          ↑ No tokens reach here
          ↑
┌─────────────────────────────────────────────────┐
│                  MCP Proxy                       │
│  (session token → fetch credentials from vault) │
└─────────────────────────────────────────────────┘
          ↑
    ┌─────────────┐
    │    Vault    │
    │ (OAuth/git tokens, 永远不在 sandbox 内)     │
    └─────────────┘
```

Git 的处理方式：每个仓库的 access token 在 sandbox 初始化时注入本地 git remote，Claude 执行的代码永远不接触 token。

---

## 三、"Many brains, many hands" 的扩展路径

### Many Brains

> "Decoupling the brain from the hands solved one of our earliest customer complaints."
> — Anthropic Engineering Blog

当 brain 在容器中时，每个 brain 需要独立的容器，扩展时必须等待容器 provisioning。解耦后：
- Containers are provisioned by the brain **only if needed** via tool call
- Many stateless harnesses can start independently
- Each brain can fail/replace without affecting others

### Many Hands

> "Decoupling the brain from the hands makes each hand a tool... The harness doesn't know whether the sandbox is a container, a phone, or a Pokémon emulator."
> — Anthropic Engineering Blog

从 single-container 扩展到 multi-hand 的驱动力：随着模型智能提升，单容器变成了限制而非优势。每个 hand 是 `execute(name, input) → string` 的工具实现，brain 可以推理多执行环境并决定工作分发。

关键特性：no hand is coupled to any brain，brains 可以相互传递 hands（hand-off）。

---

## 四、Meta-Harness 设计思想

Anthropic 将 Managed Agents 定性为"meta-harness"：

> "The challenge we faced is an old one: how to design a system for 'programs as yet unthought of.' Operating systems have lasted decades by virtualizing the hardware into abstractions general enough for programs that didn't exist yet."
> — Anthropic Engineering Blog

类比操作系统：read() / write() 是与硬件解耦的接口，这些接口足够通用，可以跨越 1970 年代磁盘到现代 SSD。

Meta-harness 的设计原则：
1. **Opinionated about interfaces, not implementations** — 期望 Claude 需要操作 state（session）和执行 computation（sandbox）
2. **Unopinionated about specific harness** — Claude Code 是 harness 的一种形式，task-specific harness 适合 narrow domains，Managed Agents 可以容纳任何形式
3. **Interfaces accommodate future** — 不假设 brain/hands 的数量或位置

---

## 五、架构决策的取舍分析

### 成功的架构决策

| 决策 | 收益 |
|------|------|
| 分离 Session 到外部 | 任意时刻可恢复，harness 可重启 |
| Brain/Hands 工具化接口 | 60-90% TTFT 改善，多 hands 可扩展 |
| Vault-based 凭据管理 | 结构性安全，tokens 永不到达 sandbox |
| MCP proxy 模式 | OAuth tokens 与 harness 隔离 |

### 已知的权衡

**延迟换解耦**：HTTP 调用比本地 syscalls 慢，但换来的是故障隔离和弹性扩展。

**接口的版本治理**：接口必须稳定，但如果未来的 Claude 需要不同接口（如更底层的内存访问），当前接口可能成为限制。Anthropic 的赌注是"session + execute"足够基础，能跨多代模型演进。

---

## 六、对 Agent 工程实践的启示

### 1. 评估 Harness 生命周期的假设

每个 Harness 都有隐式假设：
- 模型 context limit 是多少
- 工具调用的开销
- 容器启动时间

> "We found that Claude Sonnet 4.5 would wrap up tasks prematurely as it sensed its context limit approaching — a behavior sometimes called 'context anxiety.' We addressed this by adding context resets to the harness. But when we used the same harness on Claude Opus 4.5, we found that the behavior was gone. The resets had become dead weight."
> — Anthropic Engineering Blog

**Harness 版本需要与模型版本协同演进**，而不是一次性写死。

### 2. 考虑你的"hand"是否应该是 tool

如果你的 Agent 需要操作外部资源（数据库 / 文件系统 / 第三方 API），思考：是否应该将资源访问从"直接在 harness 内调用"改为"通过 tool interface 访问"？

优势：
- 资源访问可以被 retry / timeout / circuit break
- 安全边界可以更清晰地定义
- 资源可以独立扩展

### 3. 安全边界的设计优先级

Anthropic 的安全修复不是"添加更多 guardrails"，而是"结构性隔离"：tokens 永远不在 untrusted code 路径上。

---

## 结论

Anthropic Managed Agents 的核心贡献是：将"单一 Agent 系统"重新设计为"一组通过稳定接口交互的解耦组件"。Session、Brain、Hands 三层分离，使得每一层都可以独立演进、替换和扩展。

对于 Agent 开发者，这个架构的启示是：**当你设计 harness 时，不要假设你的实现会永远正确**。问自己：如果模型能力提升 10 倍，这个 harness 的哪些假设会失效？如果你的 sandbox 和你的 brain 耦合在一起，解耦它们。

> "We made no assumptions about the number or location of brains or hands that Claude will need."
> — Anthropic Engineering Blog

---

*本文关联项目推荐：[iammm0/execgo — Agent Action Harness（8 Stars）](https://github.com/iammm0/execgo) — 执行内核的具体实现，Brain/Hands 架构的"hands"层*