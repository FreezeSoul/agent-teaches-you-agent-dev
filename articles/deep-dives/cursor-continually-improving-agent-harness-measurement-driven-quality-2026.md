# Cursor Agent Harness 持续改进工程：测量驱动的 Agent 质量优化

> **核心问题**：当 Agent Harness 变得复杂时，如何在引入新模型、新功能时持续保持质量，而不是在迭代中逐渐腐化？Cursor 的答案是——测量一切，让数据驱动每一个决策。
>
> **读完能得到什么**：理解 Cursor 的 Harness 改进工程实践——双层评估体系（离线+在线）、Keep Rate 质量指标、Tool Call 错误→Context Rot 链路、以及多模型 Harness 定制化的具体方法。

---

## 一、从 Guardrails 到动态上下文：Context Window 的演进逻辑

Cursor Agent 的 Context Window 管理经历了显著的范式转变。这个演进本身就揭示了模型能力与 Harness 设计之间的动态关系。

### 1.1 早期的护栏模式

2024 年底，Cursor 首次推出编码 Agent 时，模型在自主选择上下文方面能力较弱。为此，Cursor 投入了大量上下文工程来创建护栏：

- 每次编辑后向 Agent 展示 Lint 和类型错误
- 当 Agent 请求的代码行数过少时，自动重写其文件读取请求
- 限制 Agent 单轮可以调用的最大工具数量

这些都是**强制性的外部约束**，用来弥补模型自主能力的不足。

### 1.2 当前的动态上下文模式

这些护栏在 2025 年初大部分已被移除。Cursor 现在提供少量静态上下文（操作系统、Git 状态、当前和最近查看的文件），而将主要精力放在**动态上下文获取**上——让 Agent 在工作时主动拉取所需的上下文。

> "We still include some useful static context (e.g., operating system, git status, current and recently viewed files). But we've adapted to increasing model capability by knocking down guardrails and providing more dynamic context, which can be fetched by the agent while it works."
> — [Cursor Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

这个转变不是简单的功能删减，而是反映了模型能力的根本性提升——当模型能够自主判断"我需要什么上下文"时，外部强制约束就变成了限制。

### 1.3 工程意义

这个演进路径揭示了一个重要的工程原则：**Harness 是模型能力的函数**。同样的任务，随着模型能力提升，Harness 的实现可以而且应该简化。这意味着当新模型发布时，第一件事不是"加上更多功能"，而是"移除已经不再需要的护栏"。

> 笔者认为：这与 Anthropic 在 Managed Agents 中提到的"Context Anxiety"问题形成了有趣的对照——Anthropic 的解法是把上下文管理外置到 Harness 层；Cursor 的解法是让模型学会主动获取动态上下文。两种路线都指向同一个方向：模型和 Harness 的能力边界需要被显式建模，而不是模糊地混在一起。

---

## 二、双层评估体系：离线 Benchmark + 在线实验

Cursor 维护两套并行的质量评估体系，这两者的分工和互补值得深入分析。

### 2.1 离线评估：CursorBench + 公开基准

Cursor 维护自己的 [CursorBench](https://cursor.com/blog/cursorbench) 评测套件，作为快速、标准化的质量读数，同时跟踪公开基准的变化。

这些基准的问题在于：即使最好的基准也只能近似真实使用场景。如果完全依赖离线评测，会错过重要的信号。

### 2.2 在线实验：A/B 测试

Cursor 同时运行在线实验，部署两个或多个 Harness 变体，在真实使用上做 A/B 测试。

测量的指标包括：

| 指标类型 | 具体指标 | 说明 |
|---------|---------|------|
| 性能指标 | Latency、Token 效率、Tool Call 数量、Cache 命中率 | 方向性有用，但不能直接回答"Agent 是否做得好" |
| **Keep Rate** | Agent 生成代码在固定时间间隔后的保留比例 | 用户没有手动调整的比例，高保留率 = 高初始质量 |
| **语义满意度** | 用 LLM 读取用户对 Agent 初始输出的后续响应 | 用户直接进入下一功能 = 强信号表示 Agent 完成了任务；用户粘贴堆栈跟踪 = 可靠信号表示 Agent 失败 |

> "A user moving on to the next feature is a strong signal the agent did its job, while a user pasting a stack trace is a reliable signal that it didn't."

### 2.3 两种评估的互补关系

离线基准适合快速迭代和标准化比较，但无法捕捉真实使用中的细节；在线实验能反映真实质量，但成本高、周期长、信号噪声大。

Cursor 的实践是用离线基准做快速筛选，用在线实验做最终验证。只有在线实验显示指标显著提升时，才会上线变更。

**一个关键发现**：在一次实验中，Cursor 尝试用更昂贵的模型做上下文摘要，结果对 Agent 质量的提升可以忽略不计，不值得额外的成本。这说明**成本-效益分析**必须基于实际质量指标，而不是假设"更贵的模型 = 更好的效果"。

---

## 三、Tool Call 错误链路：Context Rot 的根因链

Cursor 发现工具调用错误是 Agent 质量退化的主要驱动因素，而且这个影响是复合的。

### 3.1 错误分类

Cursor 将工具调用错误分为两类：

**预期错误**（Expected Errors）：
- `InvalidArguments`：模型提出了不正确的编辑或试图读取不存在的文件
- `UnexpectedEnvironment`：上下文窗口中的矛盾
- `ProviderError`：工具供应商宕机（如 GenerateImage、WebSearch）

**未知错误**（Unknown Errors）：
- 任何不归入上述分类的错误 → **始终是 Harness 的 Bug**

### 3.2 Context Rot 链路

工具调用错误的影响不只是"这次调用失败了"：

```
Tool Call 失败 → 错误信息驻留上下文 → 模型后续决策质量下降 → 累积错误 → "Context Rot"
```

这是一个正反馈回路。虽然 Agent 通常能够自我纠正，但错误会残留在上下文中，浪费 Token 并导致模型后续决策质量逐渐下降。有时 Agent 在一次失败的工具调用后会完全脱轨。

### 3.3 异常检测

区分"Bug"和"预期行为"并不总是容易的。例如，grep 超时可能是工具的性能问题，也可能是代码库太大导致模型形成了低效的查询。

Cursor 的解法是**按工具和模型分别计算基线**，因为不同的模型可能有不同的工具调用错误率。在这个基础上，设置**异常检测警报**，当预期错误显著超过基线时触发。

### 3.4 自动化修复流程

Cursor 运行一个每周自动化流程，配备一个教模型如何在日志中搜索问题、发现新出现或最近飙升的问题并在待办事项中创建或更新的技能。Cursor 大量使用 Cloud Agents 同时触发多个问题的修复，甚至可以直接从 Linear 触发。

在今年早些时候的一个专注冲刺中，Cursor 将意外工具调用错误减少了一个数量级。

---

## 四、多模型 Harness 定制化

Cursor 的所有 Harness 抽象都是模型无关的，但可以为每个支持的模型进行深度定制。

### 4.1 工具格式匹配

不同公司的模型使用不同的工具格式进行训练：

- **OpenAI 模型**：使用基于 patch 的格式编辑文件
- **Anthropic 模型**：使用字符串替换格式

让模型使用它不熟悉的工具格式会消耗额外的推理 Token 并产生更多错误。因此 Cursor 为每个模型配置它训练时使用的工具格式。

### 4.2 提供商特定的提示定制

这个定制深入到自定义提示层面——不仅是不同的提供商，甚至同一提供商的不同模型版本也有不同的提示。例如，OpenAI 的模型往往更_literal_ 和精确的指令跟随，而 Claude 稍微更_intuitive_，对指令的精确性更宽容。

### 4.3 新模型适配流程

当获得新模型的早期访问权时，Cursor 从最接近的现有模型 Harness 开始迭代：

1. 运行离线评估，找出模型困惑的地方
2. 团队中的人使用它并暴露问题
3. 根据反馈调整 Harness
4. 迭代直到对可以发货的模型-Harness 组合感到满意

这个过程大部分是关于定制 Harness 以适应新模型的**优势**，但有时会发现需要用 Harness 来缓解的**真正的模型怪癖**。

例如，Cursor 观察到某个模型出现了他们称之为"context anxiety"的情况：当上下文窗口填满时，它会开始拒绝工作，对任务进行对冲，认为任务太大。Cursor 能够通过提示调整减少这种行为。

---

## 五、对话中模型切换的特殊挑战

支持用户在对话中途切换模型会带来特殊的设计挑战，因为不同的模型有不同的行为、提示和工具形状。

### 5.1 自动适配问题

当用户切换模型时，Cursor 自动切换到适当的 Harness，包含该模型的定制提示和工具集。然而，模型仍然需要将这些工具应用到由**不同模型生成**的对话历史上——这超出了它的训练分布。

### 5.2 Cursor 的解法

Cursor 添加自定义指令，告诉模型何时它正在接管另一个模型，并引导它避免调用出现在对话历史中但不在其自己的工具集中的工具。

第二个挑战是缓存是提供商和型号特定的，所以切换意味着缓存未命中和更慢、更昂贵的第一轮。Cursor 的实验是**在切换时总结对话**，提供模型一个干净的摘要来减少缓存惩罚。但如果用户深入一个复杂任务，摘要可能会丢失重要细节。

### 5.3 实际建议

Cursor 的一般建议是：**除非有理由切换，否则在对话期间坚持使用一个模型**。

另一个方法是使用子 Agent，它从一个全新的上下文窗口开始。Cursor 最近在 Harness 中添加了用户直接要求用特定模型运行子 Agent 的能力。

---

## 六、Harness 与多 Agent 未来

Cursor 认为 AI 辅助软件工程的未来将是多 Agent 的：

> "Instead of running every subtask through a single agent, the system will learn to delegate across specialized agents and subagents: one for planning, another for fast edits, and a third for debugging, each scoped to what it does best."

使这种协作良好的**根本上是 Harness 挑战**。系统需要知道要调度哪个 Agent、如何为其优势调整任务框架，以及如何将结果拼接成连贯的工作流。这种协调能力将存在于 Harness 中，而不是任何单个 Agent 中。

这意味着 Harness 工程对于 Agent 的成功一直很重要，而且只会变得越来越关键。

---

## 七、与 Anthropic Managed Agents 的架构对照

| 维度 | Cursor Harness 实践 | Anthropic Managed Agents |
|------|---------------------|--------------------------|
| 核心抽象 | 模型无关抽象 + 按模型定制 | Brain/Hands/Session 三元组 |
| 上下文策略 | 动态拉取（模型自主获取） | 外部 Session + Harness 选择性注入 |
| 质量保障 | Keep Rate + LLM 语义评分 + 异常检测 | 外部化 Session 实现可重现的调试 |
| 错误处理 | Tool Call 错误 → Context Rot → 自动化修复 | 错误作为 Tool Call 错误返回 Harness → 触发重试或重建 |
| 多模型支持 | 工具格式匹配 + 提供商特定提示定制 | 支持任何实现 execute 接口的 Hands |
| 扩展方向 | 多 Agent 协调（Planner/Editor/Debugger 分工）| 多 Brain + 多 Hands + Brain-to-Brain Hand-off |

两者都认识到：**Harness 是 Agent 质量的关键**，但在具体实现上走了不同的路线。Cursor 更偏向测量驱动和渐进改进，Anthropic 更偏向架构强制和组件解耦。

---

## 八、工程建议

### 1. 建立双层评估体系

如果你的 Agent 系统缺乏评估体系，第一步是建立**离线基准**（可以是 SWE-bench、CursorBench 或你自己设计的任务集）。在此基础上，当做出重大变更时，部署 A/B 测试来验证真实质量影响。不要假设直觉——"更贵的模型"或"更多上下文"不自动等于"更好的结果"。

### 2. 追踪 Tool Call 错误率作为领先指标

Tool Call 错误率是 Context Rot 的早期信号。建立错误分类（预期 vs 未知），对已知错误类型设置基线，对未知错误（始终是 Bug）设置警报。这个指标比最终质量指标更容易获取，但能预测质量退化。

### 3. 模型能力提升时，主动移除护栏

每年检查一次你的 Harness，找出那些"当年为了弥补模型能力不足而加的护栏"——当模型能力提升后，这些护栏可能已经变成了限制。移除护栏不是放弃控制，而是承认模型能力的进步。

### 4. 规划多 Agent 协调层

如果你在构建复杂任务的 Agent 系统，现在就开始思考协调层的职责：谁负责规划？谁负责执行？谁负责验证？这些角色之间的接口是什么？Cursor 的判断是"协调能力将存在于 Harness 中"，这意味着你的编排逻辑需要被显式建模，而不是留给各个 Agent 自己去协调。

---

## 参考文献

- [Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) — Cursor 官方工程博客（第一手来源，核心参考）
- [CursorBench: How we compare model quality in Cursor](https://cursor.com/blog/cursorbench) — Cursor 评测体系
- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) — Anthropic 官方工程博客，架构对照参考
- [Dynamic Context Discovery](https://cursor.com/blog/dynamic-context-discovery) — Cursor 动态上下文技术详解