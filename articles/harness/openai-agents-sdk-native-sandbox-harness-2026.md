# OpenAI Agents SDK：原生沙箱与可迁移 Harness 设计

## 核心主张

OpenAI 新版 Agents SDK 的发布揭示了一个明确趋势：**Agent 的执行层正在从"模型调用的附加品"演变为独立的基础设施层**。通过将 harness（模型编排）、sandbox（安全执行）和 manifest（环境描述）三者解耦，OpenAI 提供了一套从本地原型到生产部署的完整执行框架。这与 Cursor Cloud Agents 的"突破本地天花板"形成技术路径上的呼应——两者都在解决同一根本矛盾：如何在保持 Agent 自主性的同时，确保执行的可预测性和生产级可靠性。

## 背景：现有方案的权衡困境

OpenAI 在博客中直接指出了当前 Agent 开发的三类方案及其固有缺陷：

> "Model-agnostic frameworks are flexible but do not fully utilize frontier models capabilities; model-provider SDKs can be closer to the model but often lack enough visibility into the harness; and managed agent APIs can simplify deployment but constrain where agents run and how they access sensitive data."
> — [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这句话点出了核心矛盾：**框架灵活性与模型能力之间存在根本张力**。Model-provider SDK 最接近模型，但 visibility into harness（对 harness 的可见性）不足；managed agent APIs 简化了部署，但限制了 Agent 的运行位置和数据访问方式。

## 原生 Harness：Aligning Execution with Model's Natural Operating Pattern

OpenAI 新版 Agents SDK 的第一个核心能力是**更强大的 harness**。这个 harness 不是简单的模型调用封装，而是对 Agent 工作流程的系统性编排层：

**可配置内存（Configurable Memory）**：Agent 可以在长程任务中保持上下文连续性，不必在每个 turn 都重新加载历史。

**Sandbox-aware orchestration**：Orchestrator 感知沙箱环境状态，能够在沙箱生命周期内协调 Agent 的行为。

**Codex-like filesystem tools**：文件系统操作工具，与 Codex 在代码场景中积累的能力对齐。

**标准化原语集成**：MCP（Model Context Protocol）、Skills（渐进式披露）、AGENTS.md（自定义指令）、Shell 工具、Apply Patch 工具等。

最关键的一句话是：

> "The harness also helps developers unlock more of a frontier model's capability by aligning execution with the way those models perform best. That keeps agents closer to the model's natural operating pattern, improving reliability and performance on complex tasks—particularly when work is long-running or coordinated across a diverse set of tools and systems."
> — [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这里提出了一个重要概念：**Model's natural operating pattern**。不同模型有不同的最优执行模式——有些模型在长程任务中表现出"context anxiety"（Anthropic 的发现），有些模型在特定 tool-use 序列上表现更稳定。Harness 的职责之一是**让执行模式与模型的自然运作模式对齐**，而不是强迫模型适应基础设施的约束。

## 原生沙箱执行：Separating Harness from Compute

新版 Agents SDK 的第二个核心能力是**原生沙箱执行**。这是 OpenAI 方案中最具生产级特征的部分：

**内置沙箱提供商支持**：Blaxel、Cloudflare、Daytona、E2B、Modal、Runloop、Vercel。开发者可以选择适合自己场景的提供商，也可以自带沙箱。

**Workspace Manifest 抽象**：这是我认为最有价值的创新设计。Manifest 是一份描述 Agent 工作空间的声明式文档：

```yaml
# workspace manifest 示意结构
name: clinical-records-agent
mount:
  - local: ./input-data
    remote: /workspace/inputs
  - s3: my-bucket/results
    target: /workspace/outputs
environment:
  python: "3.11"
  dependencies:
    - pandas
    - openai
output_dir: /workspace/outputs
```

这个抽象解决了三个问题：

1. **跨提供商可迁移性**：开发者可以在本地用 Docker 沙箱原型开发，部署时切换到 Cloudflare 或 Vercel 的生产环境
2. **环境可预期性**：模型知道输入在哪、输出在哪、如何组织长程任务的工作空间
3. **资源声明**：不需要在代码里写死环境配置，Manifest 是自包含的部署描述

## 安全性：Separating Harness and Compute

OpenAI 明确提出了安全架构原则：

> "Agent systems should be designed assuming prompt-injection and exfiltration attempts. Separating harness and compute helps keep credentials out of environments where model-generated code executes."
> — [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这与 Anthropic 在 Managed Agents 中的设计哲学一致：**harness（包含凭证和编排逻辑）和 compute（模型生成代码的执行环境）必须物理分离**。即使攻击者通过 prompt injection 获取了执行权限，也无法直接访问存储凭证的基础设施层。

**持久化与恢复（Durable Execution）**：

> "When the agent's state is externalized, losing a sandbox container does not mean losing the run. With built-in snapshotting and rehydration, the Agents SDK can restore the agent's state in a fresh container and continue from the last checkpoint if the original environment fails or expires."
> — [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这直接解决了长时间 Agent 任务的核心风险：容器丢失导致任务中断。Snapshotting + Rehydration 机制让 Agent 可以在新的容器实例中从上一个检查点恢复，而不是从头开始。

## 可扩展性：One Sandbox or Many

> "Agent runs can use one sandbox or many, invoke sandboxes only when needed, route subagents to isolated environments, and parallelize work across containers for faster execution."
> — [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这意味着 Agent 架构可以从简单的单 Agent 线性任务，扩展到多 Agent 并行执行。每个 subagent 可以路由到隔离的沙箱环境，实现真正的并行处理。

## 与 Cursor Cloud Agents 的技术对话

Cursor 的 Amplitude 案例揭示了同类问题的另一种解法。Amplitude 的 CTO Curtis Liu 说：

> "Most AI coding tools give you more code. Cursor gives you more useful production software. The ability to run agents that can effectively parallelize work, test their own changes, and take a feature from idea to production is the difference."
> — [Cursor Blog: Amplitude ships 3x more production code with Cursor](https://cursor.com/blog/amplitude)

两者在技术方向上的对比：

| 维度 | OpenAI Agents SDK | Cursor Cloud Agents |
|------|-------------------|---------------------|
| **沙箱抽象** | Manifest 声明式跨提供商 | 平台托管 VM |
| **状态持久化** | Snapshotting + Rehydration | 内置检查点 |
| **扩展模型** | Subagent → 隔离沙箱 | Fleet 调度层 |
| **集成重点** | 多提供商生态（7个沙箱商） | 自有工具链深度集成 |
| **开发者入口** | Python/TypeScript SDK | IDE 内置 + Automations |

两者都解决了同一个根本问题：**本地资源约束限制了 Agent 的并行性和自主性**，但解决路径不同：OpenAI 选择建立可迁移的 Manifest 标准，让 provider 生态竞争；Cursor 选择深度集成，在自有平台上提供端到端体验。

## 适用边界

**适合使用 OpenAI Agents SDK 的场景**：
- 需要在多个云提供商之间迁移或混用沙箱环境
- 需要细粒度控制 Agent 的执行环境和资源声明
- 已有现有云提供商（AWS S3、GCS、R2）数据流，需要将 Agent 接入这些数据源
- 对数据主权有要求，需要将 Agent 部署在特定云区域

**更适合其他方案的场景**：
- 深度绑定 Cursor 工具链（Skills、Rules、Bugbot），Cursor Cloud Agents 提供更完整的开发体验
- 需要最快时间从原型到可用的端到端方案，OpenAI 的 Manifest 学习曲线相对较高
- 已有自建沙箱基础设施，只需要一个轻量 harness 层

## 已知局限

1. **Python优先**：新版能力首先在 Python 发布，TypeScript 支持"planned for future release"
2. **Provider 成熟度差异**：Blaxel、Runloop 等新兴提供商与 Cloudflare、Modal 的企业级 SLA 存在差距
3. **Manifest 学习成本**：声明式配置虽然灵活，但对于简单场景可能过度设计
4. **与 Cursor 的生态竞争**：当团队已经深度使用 Cursor 时，迁移到 OpenAI Agents SDK 需要重新组织工作流

## 结论

OpenAI 新版 Agents SDK 代表了 Agent 基础设施的一个明确演进方向：**harness 不再是模型的附庸，而是独立的设计层**。通过 Manifest 抽象，OpenAI 正在推动沙箱环境的标准化，这可能解决多云部署的可迁移性问题。

对于 Agent 开发者的实际建议是：**在工具链选型时，将 OpenAI Agents SDK 视为 harness 层的基础设施选项，与 Cursor Cloud Agents、Cloudflare Sandboxes 等方案并列评估**，而非孤立地只看"哪个模型更强"。真正决定生产级 Agent 可靠性的，是 harness 对执行的控制能力，而不是模型本身的原始能力。