# Cursor Agent Harness 改进工程：测量驱动的持续优化

> 本文分析 Cursor 2026-04-30 发布的 agent harness 改进方法论，揭示 AI Coding 平台如何在多模型、多版本、多场景的复杂环境下，通过测量驱动的迭代实现持续质量提升。

---

## 核心论点

Agent harness 的质量直接决定了 Agent 的能力上限。但 harness 优化不是一次性工程，而是**在模型能力、用户需求、系统复杂度三个维度上持续迭代的测量驱动过程**。Cursor 这篇文章的核心价值在于：**它公开了一个生产级 AI Coding 平台如何系统性地度量、诊断、修复 harness 问题的完整方法论**，这对于所有构建 Agent 系统的工程师都是稀缺的一手参考资料。

---

## 背景：Harness 的本质与挑战

Cursor 指出，harness 和模型共同决定了 Agent 的表现。但「好」本身是难以定义的——它涉及多个维度的权衡：速度 vs 质量、成本 vs 能力、稳定性 vs 灵活性。

> "The harness and the model together determine how good the agent is, but 'good' is hard to pin down."
> — [Cursor Engineering Blog: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)

Cursor 的方法论核心是：**用数据驱动的方式找到「好」的定义，然后用系统化的测量持续逼近它**。

---

## 上下文窗口的演进：从 Guardrails 到 Dynamic Context

### 早期的 Context 工程：大量静态上下文

Cursor 早期（2024 年末）的 harness 设计包含了大量静态上下文：
- 代码库的文件夹布局
- 与查询语义匹配的代码片段
- 用户手动附加的文件的压缩版本
- Lint 和类型错误的 guardrails（每次编辑后都显示给 Agent）
- Agent 可以调用的最大工具数量限制

### 演进的动力：模型能力提升

随着模型能力的提升，许多早期设计的 guardrails 不再必要。模型现在更擅长自主选择上下文，因此 Cursor 逐步移除了这些限制：

- 不再强制显示 lint 错误（模型自己知道检查）
- 不再重写 Agent 的文件读取请求（模型知道自己需要多少行）
- 不再限制最大工具调用数

### 核心转变：从「给 Agent 限制」到「让 Agent 自己拉取」

这个演进揭示了一个重要规律：**随着模型能力提升，harness 的角色从「约束者」变成「赋能者」**。好的 harness 不再是告诉 Agent「你不能做什么」，而是提供工具让 Agent 在需要时能够自己获取正确的上下文。

> "We still include some useful static context (e.g., operating system, git status, current and recently viewed files). But we've adapted to increasing model capability by knocking down guardrails and providing more dynamic context, which can be fetched by the agent while it works."
> — [Cursor Engineering Blog](https://cursor.com/blog/continually-improving-agent-harness)

---

## 两类评测体系：Offline Benchmarks + Online Experiments

Cursor 的测量体系由两个互补的层次构成：

### 第一层：离线评测（CursorBench）

CursorBench 提供快速的标准化质量评估，让团队能够跨时间维度做对比。但 Cursor 明确指出，**即使是最好的 benchmark 也只能近似真实使用场景**，如果只依赖 CursorBench，会错过重要的信号。

### 第二层：在线实验（A/B Testing）

在线实验将两个或多个 harness 变体并行部署，通过 A/B 测试在真实使用中度量效果。Cursor 测量的指标包括：

**直接指标**：
- 延迟（Latency）
- Token 效率（Token efficiency）
- 工具调用次数（Tool call count）
- 缓存命中率（Cache hit rate）

**质量指标**：
- **Keep Rate**：Agent 生成的代码在固定时间后仍然留在代码库中的比例。这个指标捕捉「用户是否需要手动调整 Agent 的输出」
- **LLM Judge**：用语言模型阅读用户对 Agent 初始输出的后续响应，判断用户是否满意。如果用户继续做新功能，说明 Agent 完成了任务；如果用户粘贴了错误栈，说明 Agent 没有完成。

> "We measure agent quality in these tests through a variety of metrics. Some are straightforward like latency, token efficiency, tool call count, and cache hit rate. Those are directionally useful but still don't get at fuzzier and more important questions of whether the agent actually did a good job."

### 测量体系的工程挑战

这两个层次的结合本身就是工程挑战：
- **离线评测**需要标准化的数据集和评测流程
- **在线实验**需要能够同时运行多个 harness 变体的基础架构
- **指标设计**需要找到能够真正捕捉「质量」的代理变量

Cursor 的经验是：**有时在线测试会否定看起来有前途的想法**。比如，他们尝试用更贵的模型做上下文摘要，观察到对 Agent 质量的影响可以忽略不计，不值得增加的成本。这个发现只有在在线实验中才能得到。

---

## 追踪与修复退化：Tool Call 错误的系统性处理

### Tool Call 错误是最广泛的 Bug 来源

Agent 的工具调用是最大的 bug 表面积。工具调用错误可能造成严重后果：
- 错误会留在上下文中，造成「context rot」——累积的错误会降低后续决策的质量
- 有些错误会直接让 Agent 卡住或完全偏离轨道

### 错误分类体系

Cursor 将错误分为两个大类：

**预期错误**（Expected errors）：
- `InvalidArguments`：模型提出的错误参数
- `UnexpectedEnvironment`：模型对上下文的误判
- `ProviderError`：工具提供商的故障（如 GenerateImage、WebSearch 的服务中断）

**未知错误**（Unknown errors）：
- 代表 harness 中的 bug

### 告警机制设计

**规则告警**：当任何工具的未知错误率超过固定阈值时触发。因为未知错误总是 harness 的 bug。

**异常检测告警**：对于预期错误，需要判断「这是预期的行为还是 bug」。比如 grep 超时可能是工具性能问题，也可能是代码库太大导致模型形成了低效查询。

Cursor 的解法是：**按工具和模型分别计算基线**，因为不同模型在不同工具上的出错率不同。

### 自动化的 weekly automation

Cursor 运行一个每周一次的 Automation，它装备了一个 Skill，能够：
1. 搜索日志
2. 发现新出现的或最近激增的问题
3. 在 backlog 中创建或更新 ticket

然后 Cursor Cloud Agents 可以一次性触发多个修复。Cursor 将这个过程描述为「自动化的软件工厂」的一部分。

---

## 模型定制：同一 Harness 如何适配不同模型

### 工具格式的定制

OpenAI 的模型训练时使用 patch-based 格式编辑文件，Anthropic 的模型训练时使用 string replacement。**给模型一个它不熟悉的工具格式会额外消耗推理 token 并产生更多错误**。

因此 Cursor 的 harness 为每个模型提供它训练时使用的工具格式。

### Prompt 的定制

这个定制深入到 prompt 层面——不同的提供商、甚至同一提供商的不同版本，都可能有不同的行为特征：

> "OpenAI's models tend to be more literal and precise in their instruction following, whereas Claude is a bit more intuitive and more tolerant to imprecise instructions."

### 特殊模型 quirk 的处理

有时候模型会有真正的 quirks，harness 可以帮助缓解。比如 Cursor 观察到某个模型的「context anxiety」现象：当上下文窗口变满时，模型会开始拒绝工作，声称任务太大。通过 prompt 调整，Cursor 能够减少这种行为。

### 中途切换模型的挑战

当用户切换模型时，Cursor 自动切换到对应模型的 harness，包括该模型的定制 prompt 和工具。但模型还需要处理由另一个模型产生的对话历史——这超出了它训练时的分布。

Cursor 的解决方案：
1. **添加自定义指令**，告诉模型它正在中途接管另一个模型，并引导它不要调用对话历史中出现的但不属于自己工具集的工具
2. **对话摘要**：在切换时总结对话内容，提供干净的摘要减少缓存惩罚。但这会丢失细节，对于深入复杂任务的场景有局限

> "We generally recommend staying with one model for the duration of a conversation unless you have a reason to switch."

另一种解决方案是使用 subagent，它从全新的上下文窗口开始。

---

## 多 Agent 协作：Harness 的未来角色

Cursor 明确指出：

> "The future of AI-assisted software engineering will be multi-agent. Instead of running every subtask through a single agent, the system will learn to delegate across specialized agents and subagents: one for planning, another for fast edits, and a third for debugging, each scoped to what it does best."

而这种多 Agent 协作的编排能力将存在于 **harness 层而非单个 Agent 层**：
- 系统需要知道将哪个 Agent 分配到哪个任务
- 如何根据每个 Agent 的优势调整任务描述
- 如何将结果缝合为连贯的工作流

> "Making that work well is fundamentally a harness challenge... This means that, while harness engineering has always been important for agent success, it's only going to be more critical going forward."

---

## 对比：Anthropic vs Cursor 的 Harness 改进哲学

Anthropic 的 harness 文章（如 Building Effective Agents）强调的是**设计原则与接口抽象**——如何通过 Brain-Hand 解耦、Session 层设计来构建可靠的 Agent 系统。

Cursor 的这篇文章强调的是**测量驱动的持续迭代**——如何通过 CursorBench + Online Experiments 的双层测量体系，系统性地发现、诊断、修复 harness 问题。

两者都是一流的工程实践：Anthropic 提供了架构层面的设计哲学，Cursor 提供了工程实现的度量方法论。

---

## 未解决的问题与已知局限

1. **多 Agent 协调尚未详细展开**：Cursor 描述了多 Agent 的未来方向，但没有讨论多个 Agent 之间的协调冲突、资源竞争、deadlock 等问题
2. **对话摘要的局限**：切换模型时的对话摘要会丢失细节，Cursor 承认这对于复杂任务有局限，但尚未给出更好的解决方案
3. **subagent 的粒度**：subagent 的设计和使用场景还有很大的探索空间

---

## 对实践者的启示

**如果你在构建或优化 Agent 系统：**

1. **测量驱动是核心**：没有测量就没有优化。CursorBench + Online A/B Test 的双层体系是生产级 harness 的基本配置
2. **错误分类是自动化的基础**：将预期错误和未知错误分开处理，才能设计有效的告警和自动化修复流程
3. **模型定制要深入到 prompt 层面**：工具格式、prompt 风格、quirk 处理是模型适配的三个层次
4. **多 Agent 协作是 harness 的未来战场**：单 Agent 优化已经接近极限，多 Agent 编排能力将决定下一代 AI Coding 平台的质量上限
5. **Context 工程要随模型能力演进**：不要用 2024 年的 guardrails 限制 2026 年的模型，定期重新评估哪些限制已经不再需要