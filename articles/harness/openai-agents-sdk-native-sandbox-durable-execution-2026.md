# OpenAI Agents SDK：Harness 与 Sandbox 的工程重构——状态外部化与持久化的架构对比

> 本文分析 OpenAI Agents SDK 最新更新中的 Model-native Harness、Native Sandbox Execution 和 Manifest Abstraction 三大核心能力，并与 Anthropic 的 Two-agent Pattern 形成对比。

---

## 核心主张

> **笔者认为**：OpenAI 的更新揭示了一个重要趋势——Harness 层正在从「模型执行容器」演变为「可移植的持久化计算单元」。这与 Anthropic 的 Two-agent Pattern 指向同一个底层方向：**状态外部化**——但两者的解决路径不同：Anthropic 用双 Agent 协作弥补单 Agent 的完整性缺失，OpenAI 用 Sandbox + Snapshot 机制在单 Agent 框架内实现持久化和容错。两条路线都承认了「Agent 执行不可靠」这个事实，但给出了不同的工程答案。

---

## 1. 问题的本质：Harness 为何需要重构

OpenAI 在官方博客中直指问题核心：

> "The systems that exist today come with tradeoffs as teams move from prototypes to production. Model-agnostic frameworks are flexible but do not fully utilize frontier model capabilities; model-provider SDKs can be closer to the model but often lack enough visibility into the harness; and managed agent APIs can simplify deployment but constrain where agents run and how they access sensitive data."
>
> — [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这句话点出了三种既有方案的内在矛盾：框架灵活性与模型能力利用之间的张力、模型亲和性与 Harness 可见性之间的权衡、以及托管 API 的便利性与控制权之间的冲突。OpenAI 的解法是重新设计 Harness 层，使其既与模型行为模式对齐，又具备生产级的可观测性和可控性。

---

## 2. Model-native Harness：让执行贴近模型的自然模式

### 2.1 什么是「Model-native」

OpenAI 没有明确定义这个词，但在博文中给出了关键线索：

> "The updated Agents SDK supports sandbox execution natively, so agents can run in controlled computer environments with the files, tools, and dependencies they need for a task."
>
> — [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

Model-native 的核心含义是：**Harness 的执行方式与 frontier model 表现最优的工作方式对齐**。这意味着：

1. **工具调用模式与模型原生行为一致**：Codex-style filesystem tools（shell 工具、apply patch 工具）成为一等公民
2. **记忆系统可配置**：不是固定的 context window 策略，而是允许开发者根据任务特性配置内存管理方式
3. **与 Responses API 深度集成**：通过 `instructions`、`tools`、`input` 三个参数标准化 Agent 与模型的交互界面

关键设计决策：Harness 不再是模型的外层包装，而是模型执行生态的一部分。这意味着它直接影响了模型的行为可靠性——尤其是长时间运行的复杂任务。

### 2.2 与 Anthropic Two-agent Pattern 的本质差异

| 维度 | OpenAI Model-native Harness | Anthropic Two-agent Pattern |
|------|---------------------------|---------------------------|
| **架构** | 单 Agent + 外置 Sandbox | 双 Agent（Initializer + Coding Agent） |
| **完整性保证** | Snapshot/Rehydration 恢复 | Initializer Agent 的 feature_list.json 完整性检查 |
| **状态管理** | 外部化到 Manifest 描述的容器 | 外部化到 Planning Agent 的结构化状态 |
| **容错方式** | 容器失败 → 从 checkpoint 恢复 | 单 Agent 失败 → 重新初始化 |
| **模型对齐** | 执行模式贴合模型自然行为 | 任务分解贴合模型规划能力 |
| **适用场景** | 需要长时间运行、跨文件操作的生产任务 | 需要完整性保证的复杂编码任务 |

> 笔者的判断：OpenAI 的方案在「容错恢复」上更强（checkpoint 机制），但 Anthropic 的方案在「预防错误」上更彻底（双 Agent 交叉验证）。两者不是替代关系，而是适用于不同风险模型的选择。

---

## 3. Native Sandbox Execution：计算与权限的物理隔离

### 3.1 Sandbox 的工程价值

Sandbox 解决的是 Agent 执行安全性和隔离性的双重问题。OpenAI 描述了一个核心场景：

> "Many useful agents need a workspace where they can read and write files, install dependencies, run code, and use tools safely."
>
> — [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

Native Sandbox 的三个核心能力：

1. **隔离执行环境**：容器化的文件系统、工具链、依赖项，与宿主环境完全隔离
2. **多 provider 支持**：Blaxel、Cloudflare、Daytona、E2B、Modal、Runloop、Vercel——这意味着 Agent 执行不再锁定于单一基础设施
3. **凭证分离**：Harness 与计算层分离，凭证不会进入模型生成代码执行的容器

```python
# OpenAI Agents SDK 的 Sandbox 概念（伪代码表示）
sandbox_config = SandboxConfig(
    providers=["e2b", "modal", "blaxel"],  # 多 provider 支持
    manifest=Manifest(
        mount_local_files=["./src", "./config"],
        output_dirs=["./dist", "./logs"],
        storage="s3://my-bucket/agent-workspace/"
    ),
    snapshot_enabled=True,  # 持久化 checkpoint
    rehydration=True        # 从 checkpoint 恢复
)
```

### 3.2 Manifest Abstraction：可移植的工作空间描述

这是 OpenAI 更新中最具工程深度的设计。Manifest 是一个抽象层，描述了 Agent 工作空间的结构，使其在本地原型到生产部署之间保持一致：

> "This gives developers a consistent way to shape the agent's environment from local prototype to production deployment. It also gives the model a predictable workspace: where to find inputs, where to write outputs, and how to keep work organized across a long-running task."
>
> — [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

Manifest 的核心能力：

| 能力 | 说明 |
|------|------|
| **Local Files Mount** | 将本地文件挂载到 sandbox：`"./src"`、`"./config"` |
| **Output Directories** | 定义输出目录：`"./dist"`、`"./logs"` |
| **Cloud Storage Integration** | AWS S3、Google Cloud Storage、Azure Blob、Cloudflare R2 |
| **Provider Portability** | 同一 Manifest 在任意支持的 provider 上运行 |

这个设计解决了 AI Agent 开发中的一个关键摩擦：**本地能跑，生产挂掉**。Manifest 将环境描述与运行环境解耦，使得「本地开发 → 云端扩缩」成为标准路径而非特殊配置。

---

## 4. Durable Execution：Snapshotting 与 Rehydration

### 4.1 为什么需要持久化

OpenAI 指出了长时间运行 Agent 的核心风险：

> "When the agent's state is externalized, losing a sandbox container does not mean losing the run. With built-in snapshotting and rehydration, the Agents SDK can restore the agent's state in a fresh container and continue from the last checkpoint if the original environment fails or expires."
>
> — [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这里的关键概念是**状态外部化**——Agent 的执行状态不再与具体的容器绑定。当容器失败或过期时，Harness 从最后一个 checkpoint 恢复，在新的容器中继续执行。

这与 Anthropic 的 feature_list.json 机制形成了有趣的对照：

| 机制 | Anthropic Two-agent Pattern | OpenAI Agents SDK |
|------|---------------------------|-------------------|
| **状态外部化** | feature_list.json 记录增量变更 | Snapshot 记录完整状态 |
| **恢复方式** | 重新初始化 → 增量执行 | 从 checkpoint 恢复 → 继续执行 |
| **完整性保证** | Initializer 交叉验证 | 状态完整性由 Snapshot 保证 |
| **适用错误场景** | 单步失败、上下文溢出 | 容器崩溃、任务超时 |

> 笔者的判断：Anthropic 的方案在「增量任务」的上下文管理上更高效（不需要恢复整个状态），但 OpenAI 的方案在「长时间连续工作」的场景下更鲁棒（checkpoint 可精确到任意时刻）。

### 4.2 水平扩展能力

OpenAI 强调了 Sandbox 架构的扩展性：

> "Agent runs can use one sandbox or many, invoke sandboxes only when needed, route subagents to isolated environments, and parallelize work across containers for faster execution."
>
> — [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这意味着：
- **单 Agent 多 Sandbox**：复杂任务可以按阶段分配到不同容器
- **按需调用**：Harness 根据任务需求动态创建/销毁 sandbox
- **Subagent 隔离**：子 Agent 运行在独立容器中，与父 Agent 完全隔离
- **并行执行**：同一任务的多个子任务可以在不同容器中并行处理

---

## 5. 与 Anthropic Two-agent Pattern 的系统性对比

### 5.1 两条路线的分歧点

| 问题 | Anthropic 路线 | OpenAI 路线 |
|------|---------------|------------|
| **Agent 失效率** | 通过双 Agent 协作预防 | 通过 snapshot/rehydration 容错 |
| **完整性保证** | 结构化 feature list + 交叉验证 | 状态外部化 + checkpoint 恢复 |
| **架构复杂度** | 双 Agent 协作逻辑 | Sandbox 基础设施 |
| **适用规模** | 复杂单任务（编译器级别） | 长时多任务（生产级） |

### 5.2 收敛点：状态外部化

两条路线在根本上都指向同一个方向：**Agent 执行状态必须与具体运行时解耦**。

- Anthropic 的解法是规划 Agent 外部化 feature_list，编码 Agent 增量执行
- OpenAI 的解法是状态 externalized 到 Snapshot，容器失败可无缝切换

这个收敛不是偶然的。它反映了一个工程共识：**随着 Agent 执行时间跨度和任务复杂度的增长，「状态与运行时耦合」会成为整个系统的脆弱点**。两条路线选择了不同的技术手段来规避这个风险。

### 5.3 互补性

两种方案不是互斥的，可以组合使用：

1. **OpenAI Sandbox + Anthropic Two-agent**：在 OpenAI 的隔离容器中运行 Anthropic 的双 Agent 协作模式
2. **OpenAI Snapshot + Anthropic feature_list**：Snapshot 保证容器级恢复，feature_list 保证任务级完整性

---

## 6. 安全与生产的双重保障

OpenAI 特别强调了安全设计的核心原则：

> "Agent systems should be designed assuming prompt-injection and exfiltration attempts. Separating harness and compute helps keep credentials out of environments where model-generated code executes."
>
> — [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

这句话指出了安全设计的两个关键设计决策：

1. **Harness/Compute 分离**：凭证不进入模型生成代码执行的容器
2. **默认敌意假设**：Prompt injection 和数据泄露被视为必然威胁，而非意外

这个安全模型与 Anthropic 的观点高度一致，但 OpenAI 通过基础设施层面（Sandbox 隔离）而非组织策略层面（双 Agent 分权）来实现。

---

## 7. 已知局限与未解问题

OpenAI 的更新留下了几个重要的未解答问题：

1. **Checkpoint 一致性**：当 Agent 在 Snapshot 时刻的状态包含了对外部 API 的未决调用时，恢复后的 Rehydration 如何处理幂等性？
2. **Sandbox provider 锁定**：虽然支持多 provider，但 Manifest 的 provider-specific 配置（如 E2B 的 timeout vs Blaxel 的 cold start）在切换时是否需要修改？
3. **成本模型**：Snapshot 和 Rehydration 的频率如何影响实际使用成本？OpenAI 提到「standard API pricing, based on tokens and tool use」，但没有明确 Snapshot 存储和 Rehydration 的计费方式。

---

## 8. 结论：Harness 工程化的三个趋势

从 OpenAI Agents SDK 的更新中，可以识别出 Agent Harness 工程化的三个明确趋势：

1. **Model-native 优先**：Harness 不再是模型的外层包装，而是模型执行生态的一部分——Harness 的设计直接影响模型的行为可靠性
2. **状态外部化**：Agent 执行状态与具体运行时解耦——通过 Snapshot/Rehydration（OpenAI）或 Feature List（Anthropic）实现
3. **基础设施即代码**：Sandbox 环境通过 Manifest 描述，实现「开发时环境 = 生产时环境」的确定性保证

> **工程建议**：对于需要长时间连续工作且对容器失败容忍度高的任务，优先考虑 OpenAI Agents SDK 的 Sandbox + Snapshot 架构；对于需要任务级完整性保证且错误成本高的场景（如编译器级别任务），考虑 Anthropic Two-agent Pattern 或两者组合。

---

## 参考文献

1. [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) — OpenAI 官方博客，2026-04
2. [Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/) — OpenAI 官方博客，Michael Bolin，2026
3. [Sandbox Agents | OpenAI API](https://developers.openai.com/api/docs/guides/agents/sandboxes) — OpenAI 开发者文档

---

*关联文章*：
- [Anthropic Initializer + Coding Agent 双组件架构](./../harness/anthropic-initializer-coding-agent-two-component-harness-2026.md) — Anthropic 的 Two-agent Pattern 深度解析
- [Nonstop Agent](./projects/nonstop-agent-claude-long-running-harness-2026.md) — Anthropic Two-agent Pattern 的开源实现