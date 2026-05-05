# Anthropic 工程实践：多 Agent 架构的四种范式与适用边界

**核心主张**：Multi-Agent 系统的架构选择不是技术偏好，而是任务特性的函数。Anthropic 的工程实践揭示了四种核心协调范式——层级式（Hierarchical）、并行式（Concurrent）、顺序式（Sequential）和 Supervisor 模式——每种都有明确的适用边界和失效条件。选错范式的代价是指数级的：层级式被强行并行化会导致任务碎片化，并行式被强行层级化会导致通信瓶颈。

**读者画像**：有 Agent 框架使用经验，理解单个 Agent 的工具调用和 Tool Use机制，但需要设计多 Agent 协作系统的架构师或高级工程师。

**核心障碍**：社区中多 Agent 架构的讨论往往停留在「用哪个框架」，而非「为什么这个架构适合这个任务」。选型决策缺乏系统性的比较框架。

---

## 1. 四种协调范式的定义与本质差异

### 1.1 层级式（Hierarchical）：中心节点做分解，Worker 做执行

层级式是 Anthropic 在 Claude Code 内部实践最多的模式。其核心思想是引入一个**中心协调者（Supervisor/Orchestrator）**，它不直接执行任务，而是负责任务分解、指派、结果收集和质量判断。

```
User Task
    ↓
[Supervisor Agent]
    ├── 分解为子任务 T1, T2, T3
    ├── 指派给专门的 Worker Agent
    │   ├── Worker-A → T1
    │   ├── Worker-B → T2
    │   └── Worker-C → T3
    ├── 收集结果
    └── 合成最终输出
```

> "We ended up running planners and sub-planners to create tasks, then having workers execute on them. The planners would reason about the overall structure, create a task graph, and assign subtasks to workers."
> — [Simon Willison: Scaling long-running autonomous coding](https://simonwillison.net/2026/jan/19/scaling-long-running-autonomous-coding/)

层级式的本质是**知识与执行的分离**。Supervisor 持有全局视图（知道有多少任务、依赖关系是什么），Worker 持有局部视图（只关心自己被分配的那部分）。这与软件工程中 Architect 和 Developer 的分工逻辑完全一致。

**适用场景**：
- 任务可明确分解为独立子任务
- 子任务之间有清晰的依赖关系树
- 需要一个「全局视角」来协调质量

**反模式**：
- 子任务之间高度耦合，需要频繁通信 → 并行通信会让 Supervisor 成为瓶颈
- 子任务需要共享中间状态 → Worker 的局部视图无法处理

### 1.2 并行式（Concurrent）：同一任务，多 Agent 同时处理

并行式的核心思想是多个 Agent 同时处理同一任务的不同部分或视角，最终通过投票、汇总或合成得出结论。Swarms 框架中的 `ConcurrentWorkflow` 是这一范式的典型实现。

```python
from swarms import Agent, ConcurrentWorkflow

# 三个分析师同时从不同角度处理同一公司
fundamental_analyst = Agent(system_prompt="分析财务数据...", model_name="gpt-5.4")
sentiment_analyst = Agent(system_prompt="分析市场情绪...", model_name="gpt-5.4")
technical_analyst = Agent(system_prompt="分析技术面...", model_name="gpt-5.4")

workflow = ConcurrentWorkflow(agents=[
    fundamental_analyst,
    sentiment_analyst,
    technical_analyst
])

result = workflow.run("分析 NVIDIA 2026 Q1 的投资价值")
```

> "TradingAgents is a multi-agent trading framework that mirrors the dynamics of real-world trading firms." — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)

**并行式的本质是「专家共识机制」**。不同 Agent 相当于不同领域的专家，parallel 处理后通过某种机制（投票、LLM 合成、规则判断）得出最终结论。TradingAgents 是这一范式的最佳案例：金融交易需要同时考虑基本面、情绪面、技术面，每个面都有专门的 Agent 分析。

**适用场景**：
- 任务可以同时从多个独立视角处理
- 需要「多数意见」或「综合判断」而非单一正确答案
- 各 Agent 输出可合成

**反模式**：
- 子任务有依赖关系（B 需要 A 的输出）→ 并行化后需要大量同步等待
- 任务不可分割，必须串行处理 → 并行化是伪并行

### 1.3 顺序式（Sequential）：A 的输出是 B 的输入

顺序式是最直觉的多 Agent 模式：Agent A 处理完输入，将输出作为 Agent B 的输入，依此类推。LangChain 的 LCEL（LangChain Expression Language）Chain 和 Swarms 的 `SequentialWorkflow` 都支持这种模式。

```
Input → [Agent-A: 提取关键信息] → [Agent-B: 结构化整理] → [Agent-C: 生成最终输出]
```

> "Agents execute tasks in a linear chain; the output of one agent becomes the input for the next." — [Swarms Documentation](https://docs.swarms.world/en/latest/swarms/structs/sequential_workflow/)

**顺序式的本质是「流水线分工」**。每个 Agent 是一个专门的工站，负责将输入转化为更有价值的输出。这与软件开发中的「管道-过滤器」架构一致。

**适用场景**：
- 任务天然有先后顺序，后一步依赖前一步的输出
- 每个步骤需要不同的专业知识或 Prompt 策略
- 需要 human-in-the-loop 在步骤之间进行审批

**反模式**：
- 中间步骤失败导致整个流水线重启
- 长链条中误差累积（每步 90% 准确率，10 步后只剩 35%）

### 1.4 Supervisor 模式：单一 Agent 做全局调度决策

Supervisor 模式与层级式的核心区别在于：Supervisor 不只是做任务分解，而是**做调度决策**——它决定哪个 Worker 做什么、什么时候做、是否需要等待。Anthropic 的 deer-flow 实现中，Supervisor Agent 持有一个持久化记忆层，可以在多轮对话中保持任务状态。

```python
# Supervisor 模式的核心逻辑（概念性代码）
class SupervisorAgent:
    def __init__(self, workers):
        self.workers = workers  # Worker Agent 池
        self.memory = PersistentMemory()  # 持久化状态

    def process(self, task):
        # Supervisor 分析任务，决定分配给哪个 Worker
        sub_tasks = self.decompose(task)
        for sub_task in sub_tasks:
            worker = self.select_worker(sub_task)  # 基于 Worker 负载/专长选择
            result = worker.execute(sub_task)
            self.memory.store(sub_task, result)

        # Supervisor 合成最终结果
        return self.synthesize(self.memory.retrieve_all())
```

> "A Supervisor mode with persistent memory + Docker sandbox — ByteDance's open-source multi-agent orchestration framework." — [deer-flow 官方描述](https://github.com/bytedance/deer-flow)

**Supervisor 模式的本质是「带记忆的调度器」**。它与层级式的关键区别在于：层级式的 Supervisor 通常是静态的（任务分解是预先定义的），而 Supervisor 模式是动态的（每步都在做调度决策）。

---

## 2. 范式选择的决策矩阵

选择哪种架构，不是看「哪个更流行」，而是看任务本身的特性。以下是决策矩阵：

| 任务特性 | 层级式 | 并行式 | 顺序式 | Supervisor 模式 |
|---------|--------|--------|--------|----------------|
| **任务可分解性** | ✅ 高（树状分解） | ✅ 高（视角分解） | ✅ 高（流水线分解） | ⚠️ 中（需动态判断） |
| **子任务依赖** | 树状依赖 | 无依赖（独立视角） | 线性依赖 | 动态依赖 |
| **执行时间** | 中等（Supervisor 有开销） | 最短（真并行） | 最长（串行） | 变化大（取决于调度效率） |
| **一致性需求** | 高（Supervisor 保证） | 中（需合成机制） | 高（线性传递） | 高（Supervisor 控制） |
| **容错要求** | 中（Worker 失败可重试） | 低（多 Agent 互不影响） | 低（某步失败全链重启） | 高（Supervisor 可重新调度） |
| **典型场景** | 大型代码重构、多模块并行开发 | 投资分析、多视角评估 | 数据 ETL、内容生产流水线 | 复杂对话系统、长周期任务 |

### 2.1 反直觉的选型建议

**建议一：不要默认使用层级式**

层级式是最直觉的多 Agent 架构，但它有隐性成本：Supervisor 的能力决定了整个系统的上限。如果Supervisor 的全局视图不准确，或者任务分解有遗漏，整个系统效率反而低于单个 Agent。

> 笔者认为：在任务边界不清晰、探索性强的场景（如「帮我研究量子计算现状」），层级式反而不如单个 Agent + Long Context 直接处理——因为 Supervisor 的任务分解本身就是一种猜测。

**建议二：并行式是最好的起步选择**

如果不确定任务特性，从并行式开始是最低风险的选择。即使任务本身有轻微依赖，并行式的「分别处理 + 后期合成」通常也能得到合理结果。TradingAgents 的实践证明了这一点：基本面分析师、情绪分析师、技术分析师可以完全并行工作，最终通过讨论机制（GroupChat）合成决策。

**建议三：顺序式是「人类审批」场景的最优解**

如果需要在某个步骤停下来等待人类审批（如「代码审查后才能合并」），顺序式是唯一能优雅支持这一点的架构。其他架构在中间插入 human-in-the-loop 会破坏原有的并行或层级结构。

---

## 3. Swarms：企业级 Multi-Agent 编排的工程实现

在 GitHub 已有多个多 Agent 框架的情况下，Swarms（6,620 ⭐，895 forks）的差异化定位是**「开箱即用的生产级架构库」**，而非「让你从零搭框架」。

### 3.1 核心架构：七种预构建编排模式

Swarms 提供了七种经过生产验证的编排架构，这是其相对于 LangGraph/CrewAI/AutoGen 的核心差异：

| 架构 | 适用场景 | 核心机制 |
|------|---------|---------|
| `SequentialWorkflow` | 流水线任务（ETL、内容生产） | 线性链式传递 |
| `ConcurrentWorkflow` | 多视角并行分析 | 共享输入，并行执行 |
| `AgentRearrange` | 动态任务分配 | 表达式语言（`a->b,c`）描述依赖 |
| `GraphWorkflow` | 复杂依赖（DAG） | 节点=Agent，边=依赖 |
| `MixtureOfAgents (MoA)` | 专家合成 | 多个专家输出 → LLM 合成 |
| `GroupChat` | 协作决策 | 多方讨论 + 投票/共识 |
| `ForestSwarm` | 动态路由 | 任务 → 最适合的 Agent 树 |

### 3.2 与 Anthropic 四种范式的映射

Swarms 的架构矩阵恰好覆盖了前文讨论的四种范式：

- **层级式** → `GraphWorkflow`（有向无环图）+ `ForestSwarm`（动态选择子 Agent）
- **并行式** → `ConcurrentWorkflow` + `MixtureOfAgents`
- **顺序式** → `SequentialWorkflow`
- **Supervisor 模式** → `AgentRearrange`（通过表达式语言实现动态调度）+ `GroupChat`（带协调者的讨论）

> "Swarms provides a comprehensive suite of production-ready, prebuilt multi-agent architectures, including sequential, concurrent, and hierarchical systems." — [Swarms README](https://github.com/kyegomez/swarms)

### 3.3 企业级特性：MCP 兼容、x402 支付、技能系统

Swarms 的另一个差异化点是**企业基础设施集成**：

- **MCP 协议兼容**：可以与 Model Context Protocol 生态中的工具直接对接
- **x402 支付协议**：内置了 LLM API 的计量支付逻辑，适合需要按调用量收费的企业场景
- **Skills 系统**：支持将工作流程封装为可复用的「技能」，在多个 Swarm 之间共享

> 笔者认为：Swarms 的 x402 和 Skills 集成是其区别于学术向框架的关键。对于企业而言，「如何计量和计费」与「如何编排」同样重要，Swarms 在这两点上没有回避。

### 3.4 适用边界

**适合使用 Swarms 的场景**：
- 需要快速原型化一个多 Agent 系统，不想从 LangGraph 的状态机开始搭
- 需要在多个编排模式之间切换（今天用并行，明天发现需要 DAG，换起来容易）
- 企业场景，需要 MCP 兼容和计量计费能力

**不适合使用 Swarms 的场景**：
- 需要精细控制每个 Agent 的内部状态 → LangGraph 的状态机更合适
- 只需要简单的顺序 Chain → LangChain LCEL 或直接循环更简单
- 任务高度动态，需要自定义调度逻辑 → Supervisor 模式手写更清晰

---

## 4. 架构选型的工程检查清单

在实际项目中选型时，建议按以下顺序逐项确认：

```
[ ] 任务是否可分解？ → 否：单 Agent 即可，不要强行多 Agent
    ↓ 是
[ ] 子任务之间是否有强依赖？ → 是：排除纯并行式，考虑顺序式或 Supervisor
    ↓ 否
[ ] 是否需要多个独立视角同时评估？ → 是：并行式（Concurrent/MoA）
    ↓ 否
[ ] 是否有预定义的任务分解结构？ → 是：层级式（GraphWorkflow）
    ↓ 否
[ ] 是否需要动态调度 + 持久记忆？ → 是：Supervisor 模式（deer-flow 路径）
    ↓ 否
[ ] 是否需要 human-in-the-loop？ → 是：顺序式（SequentialWorkflow）
    ↓ 否
[ ] 使用 Swarms 的七种架构快速验证
```

> 笔者认为：这个检查清单的价值不在于「选对」，而在于「避免明显错误」。多 Agent 系统的最大浪费不是选错了框架，而是构建了一个过度复杂的系统来处理本可以用简单方式解决的任务。

---

## 5. 结论

Multi-Agent 架构选择的核心洞察是：**协调范式必须匹配任务的依赖结构**。层级式处理树状分解，并行式处理独立视角，顺序式处理线性依赖，Supervisor 模式处理动态调度。

Swarms 的价值在于它将这四种范式实现为可组合的预构建架构，并将企业级的计量、支付、技能复用能力纳入同一框架。对于需要快速搭建生产级多 Agent 系统的团队，这是目前最完整的开源选择。

> 关键判断：在 Agent 系统从「原型」走向「生产」的过程中，架构选择的重要性会被放大。一个在原型阶段表现良好的单 Agent 系统，在面对复杂任务时可能需要重构为多 Agent——而重构的成本远高于一开始就选择正确的架构。选择 Swarms 或 LangGraph 这样的框架的价值，不在于「不用写状态机」，而在于让架构调整变得可逆。