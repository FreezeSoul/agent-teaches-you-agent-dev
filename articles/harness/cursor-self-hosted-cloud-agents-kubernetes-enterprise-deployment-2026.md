# Cursor Self-Hosted Cloud Agents：企业级 Kubernetes Agent 部署架构深度解析

## 核心论点

> 本文要证明：Cursor 的 Self-Hosted Cloud Agents 通过 **Worker as Outbound HTTPS Agent** 的架构设计 + **Kubernetes Operator** 的声明式 CRD 管理，解决了企业级 Agent 部署中最核心的三个矛盾——代码不出境与模型访问权的矛盾、单租户隔离与并行扩展的矛盾、以及维护成本与安全合规的矛盾。这不是功能增强，而是企业 Agent 就绪的基础设施范式转变。

---

## 一、企业级 Agent 部署的核心矛盾

在讨论 Cursor Self-Hosted 架构之前，需要理解为什么企业级 Agent 部署长期以来是一个未解决好的问题。

传统模式下，企业有两个极端选择：

**方案一：纯自建**
企业自己搭建 Agent 基础设施——维护模型接入、处理日志记录、管理权限。这条路的问题是维护成本极高，Cursor 官方原文指出：
> "Some teams have diverted engineering resources towards building and maintaining their own background agents for coding."
> — [Cursor Blog: Run cloud agents in your own infrastructure](https://cursor.com/blog/self-hosted-cloud-agents)

**方案二：纯托管**
将代码和数据完全交给第三方 Agent 服务。这对于金融、医疗等强监管行业几乎不可接受：
> "Many enterprises in highly-regulated spaces cannot let code, secrets, or build artifacts leave their environment due to security and compliance requirements."
> — [Cursor Blog: Run cloud agents in your own infrastructure](https://cursor.com/blog/self-hosted-cloud-agents)

这两个极端之间存在巨大的工程空白——企业既不想放弃云端 Agent 的智能能力，又无法将代码和执行环境移出自有网络。Cursor Self-Hosted 的核心设计目标就是填补这个空白。

---

## 二、架构设计：Outbound-Only Worker Model

Cursor Self-Hosted 采用了 **Worker as Outbound HTTPS Agent** 的架构模型，这是整个设计的核心决策。

### 2.1 零入站连接模型

传统 VPN 或远程接入方案需要企业开放入站端口，这本身就是安全风险。Cursor 的设计是**worker 主动建立出站 HTTPS 连接**到 Cursor 云端，无需任何入站端口打开：

> "A worker is a process that connects outbound via HTTPS to Cursor's cloud—no inbound ports, firewall changes, or VPN tunnels required."
> — [Cursor Blog: Run cloud agents in your own infrastructure](https://cursor.com/blog/self-hosted-cloud-agents)

这意味着：
- 企业防火墙策略不变
- 不需要 VPN 配置
- 不需要开放任何端口

### 2.2 Session-to-Worker 的生命周期绑定

每个 Agent session 获得自己的专属 worker：
> "Each agent session gets its own dedicated worker, which is initiated with a single command: `agent worker start`."
> — [Cursor Blog: Run cloud agents in your own infrastructure](https://cursor.com/blog/self-hosted-cloud-agents)

这是一个重要的设计决策——session 和 worker 是 1:1 绑定的。这解决了两个问题：
- **隔离性**：每个 worker 独立，不共享状态
- **生命周期管理**：session 结束时 worker 可以被回收

### 2.3 执行权与思考权的分离

Cursor 在 Self-Hosted 架构中保持了与 Cloud Agents 一致的分工：

> "When users kick off an agent session, Cursor's agent harness handles inference and planning, then sends tool calls to the worker for execution on your machine."
> — [Cursor Blog: Run cloud agents in your own infrastructure](https://cursor.com/blog/self-hosted-cloud-agents)

这是一个重要的架构洞察：**harness 留在 Cursor 云端处理推理和规划，worker 在企业网络内执行工具调用**。这意味着：
- 模型访问权在 Cursor 侧
- 代码和工具执行在企业侧
- 数据流被物理隔离，但控制流通过 HTTPS 保持连通

---

## 三、Kubernetes Operator：Fleet 级管理

对于需要运行大量 worker 的企业，Cursor 提供了完整的 Kubernetes Operator 方案。

### 3.1 WorkerDeployment CRD

Cursor 定义了一个 `WorkerDeployment` 自定义资源，让运维团队用声明式方式管理 fleet：

> "For organizations scaling to thousands of workers, we provide a Helm chart and Kubernetes operator. You can define a WorkerDeployment resource with your desired pool size, and the controller handles scaling, rolling updates, and lifecycle management automatically."
> — [Cursor Docs: Self-Hosted Cloud Agents](https://cursor.com/docs/cloud-agent/self-hosted-k8s)

这个设计的精髓在于：**将 Agent fleet 视为Desired State**，而不是管理一组进程。

### 3.2 控制器职责

Operator 控制器自动处理：
- **扩缩容**：根据 pool size 自动创建/销毁 worker pods
- **滚动更新**：当 Cursor 发布新版本时，自动执行 rolling update
- **生命周期管理**：处理 pod 异常、节点故障等场景

### 3.3 自定义配置能力

从 Cursor 社区论坛看到，企业对 MCP 配置有差异化需求：
> "Is there a way to configure MCP servers on our self hosted agents that we have hosted in k8s? I dont want to configure any dashboards on cursor as i want some self hosted agents to have access to some MCP while others dont."
> — [Cursor Community Forum](https://forum.cursor.com/t/self-hosted-agents-on-k8s-connecting-mcps/159181)

这说明企业需要按 team 或按 agent 类型配置不同的 MCP 权限，这是未来 Operator 需要支持的方向。

---

## 四、安全模型的工程实现

### 4.1 数据流隔离

Self-Hosted 架构的核心安全保证是**代码和执行产物从不离开企业网络**：

- 代码：始终在企业 VPC 内的 worker 执行
- 工具调用结果：在企业网络内处理
- 构建产物（artifacts）：不出境

### 4.2 企业现有安全模型复用

Cursor 强调企业可以复用现有安全基础设施：
> "With self-hosted cloud agents, teams can keep their existing security model, build environment, and internal network setup, while Cursor handles orchestration, model access, and the user experience."
> — [Cursor Blog: Self-Hosted Cloud Agents](https://cursor.com/blog/self-hosted-cloud-agents)

这对于 Notion 这样的企业尤其关键：
> "In large codebases like Notion's, running agent workloads in our own cloud environment allows agents to access more tools more securely and saves our team from needing to maintain multiple stacks."
> — Ben Kraft, Software Engineer, Notion

### 4.3 与 Cursor Cloud Agents 的能力对齐

Self-Hosted 不是功能阉割版，而是完整能力：
> "Self-hosted cloud agents offer the same capabilities as Cursor-hosted cloud agents: Isolated remote environments, Multi-model, Plugins, Team permissions."
> — [Cursor Blog: Self-Hosted Cloud Agents](https://cursor.com/blog/self-hosted-cloud-agents)

---

## 五、与其他企业 Agent 方案的对比

| 维度 | Cursor Self-Hosted | OpenAI Agents SDK | Anthropic Claude Code |
|------|-------------------|-------------------|----------------------|
| 架构模式 | Outbound HTTPS Worker + Operator | SDK 内嵌本地执行 | 云端执行（可选自建 harness） |
| 隔离粒度 | Session 级别专属 worker | 进程级别（可配置） | 云端多租户 |
| K8s 支持 | 官方 Operator + Helm | 无官方 K8s 支持 | 无官方 K8s 支持 |
| 企业安全模型 | 复用现有安全基础设施 | 需要自行集成 | 需要自行设计 |
| 适用场景 | 大规模、多 team 并行 | 中小规模、开发测试 | 云端协作 |

> 笔者认为：Cursor Self-Hosted 在企业场景下的核心优势在于** Operator 的声明式管理**和**零入站连接的安全模型**。OpenAI Agents SDK 更适合需要深度定制的场景，而 Anthropic 的方案更偏向于让团队自己构建 harness。

---

## 六、局限性与待观察问题

1. **MCP 按 worker 配置尚未成熟**：从社区讨论看，按 team 配置不同 MCP 权限はまだのプロット，需要等官方支持
2. **Helm chart 仍在 v1 阶段**：生产级 HA 部署的能力还有待验证
3. **单-use vs 长-lived 选择**：文档提到 workers 可以是 "long-lived or single-use"，但最佳实践尚不清晰
4. **Fleet management API 的 autoscaling 支持**：官方说可以构建 autoscaling，但具体方案未公开

---

## 七、工程落地检查清单

如果你的团队在评估 Self-Hosted Cloud Agents，以下检查项可以帮助快速判断适用性：

```
□ 是否有安全/合规要求禁止代码出境？
□ 是否有内部网络 endpoints（caches, dependencies）需要访问？
□ 团队规模是否超过 100 人需要 fleet 管理？
□ 是否已有 Kubernetes 基础设施？
□ 是否需要按 team 配置不同的 MCP 权限？
```

若以上有任何一项为"是"，Self-Hosted 值得深入评估。

---

## 八、总结

Cursor Self-Hosted Cloud Agents 通过三个核心设计解决了企业 Agent 部署的核心矛盾：

1. **Outbound-only Worker**：零入站连接，代码不出境，安全模型不改变
2. **Kubernetes Operator**：声明式 CRD 管理 fleet，滚动更新自动化
3. **数据流与控制流分离**：Cursor 处理推理规划，企业处理执行

这三个设计共同构成了企业 Agent 就绪的基础设施范式。

> "That allows engineering teams to spend less time maintaining agent infrastructure and more time using it."
> — [Cursor Blog: Self-Hosted Cloud Agents](https://cursor.com/blog/self-hosted-cloud-agents)

这句话是整个方案的最佳注脚。

---

**关联阅读**：
- [Cursor Blog: Run cloud agents in your own infrastructure](https://cursor.com/blog/self-hosted-cloud-agents)
- [Cursor Docs: Self-Hosted Cloud Agents Kubernetes](https://cursor.com/docs/cloud-agent/self-hosted-k8s)
- [GitHub: render-examples/cursor-self-hosted-agent](https://github.com/render-examples/cursor-self-hosted-agent)

---

*来源：Cursor Engineering Blog + 官方文档 | 2026-05-05*