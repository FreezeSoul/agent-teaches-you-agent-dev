# Cursor Agent Harness 持续改进工程：测量驱动迭代方法论

> 核心论点：Cursor 这篇文章揭示了一个重要的工程哲学——**Harness 的质量不是设计出来的，而是测量出来的**。通过上下文窗口演化、Keep Rate + LLM 语义评估的双层测量体系、以及异常检测告警，Cursor 建立了一个数据驱动的 Agent 质量改进闭环。这个方法论比我见过的任何「如何构建 Agent」的配置文档都更有实战价值。

---

## 背景：Harness 不是「配置」而是「产品」

Cursor 在文章开篇就给出了一个关键认知转变：

> "We approach building the Cursor agent harness the way we'd approach any ambitious software product."

这句话把 Harness 从「一个 system prompt + 几个工具定义」的简单配置，提升到了「需要测量→假设→实验→迭代的产品级别工程」。

这对笔者的触动在于：大多数 Agent 开发者对 Harness 的理解还停留在「调参」层面——改改 temperature、换个 system prompt、试试不同的工具描述。但 Cursor 展示的是一种完全不同的工程范式：**把 Harness 视为一个有自己质量指标的独立产品，然后用生产级软件工程的度量方法来改进它**。

---

## 一、上下文窗口的演进：从 Guardrails 到动态上下文

### 1.1 早期阶段：静态上下文的大量填充

2024 年末 Cursor 刚推出 coding agent 时，模型能力相对弱，选择上下文的能力差。当时 Cursor 做了大量「上下文工程」的填充工作：

- **文件夹布局**：静态解析 codebase 结构，作为 session 初始上下文
- **语义匹配片段**：基于 query 语义，从代码库中匹配相关代码片段
- **用户手动附件压缩版**：用户主动上传的文件经过压缩后预填充

这些做法有一个共同特征：**假设模型无法自主选择上下文，需要外部系统替它决定什么重要**。

### 1.2 现在的阶段：移除 Guardrails + 动态拉取

现在的 Cursor，这些静态填充「大部分已经消失了」：

> "That is mostly long gone."

现在的做法是：
- 保留少数有用的静态上下文（操作系统、git 状态、当前和最近查看的文件）
- 其他全部改为**动态获取**，由 Agent 在工作中自主决定需要什么上下文

这是模型能力提升后的必然结果：当模型本身能够准确判断「我需要哪段代码」时，外部系统替它做这个决定反而会引入噪声。

**笔者认为**：Cursor 的演进路径揭示了一个重要的设计原则——**Agent 的上下文选择能力是关键分水岭**。当模型足够强时，Harness 应该从「主动填充」退位到「响应式提供」。这与 Anthropic 提出的「注意力预算」概念一致：模型自身的上下文选择能力决定了我们应该在何处做「上下文工程」，何处可以放手让模型自主决定。

### 1.3 残留的静态上下文

Cursor 保留了少量静态上下文，这些保留了是因为它们对所有模型、所有场景都有稳定价值：

```python
# Cursor 保留的静态上下文
current_context = [
    "operating_system",     # 操作系统类型，影响工具行为
    "git_status",          # 当前分支/修改状态，影响代码决策
    "current_file",        # 用户当前正在编辑的文件
    "recently_viewed"      # 最近打开的文件列表（隐式意图信号）
]
```

这个保留清单本身就是一个有价值的参考——它说明**什么上下文在任何情况下都稳定有用**。其他都可以动态化。

---

## 二、测量体系：双层评估框架

这是文章最核心的部分。Cursor 建立了两个层次的质量测量：

### 2.1 第一层：离线评测（CursorBench）

Cursor 维护了一套自己的评测基准 CursorBench，结合公开评测集，**提供快速的标准化质量读数**，支持跨时间维度的质量对比。

但 Cursor 明确指出了公开评测的局限性：

> "even the best benchmarks only approximate real usage"

benchmark 只能近似真实使用场景，这是评测设计者的永恒痛点。Cursor 选择不依赖单一评测，而是建立多层测量。

### 2.2 第二层：在线实验（A/B Testing）

Cursor 在真实用户上跑 A/B 测试，同时部署两个或多个 Harness 变体，测量真实使用中的质量差异。

他们用的具体指标分为两类：

**可量化的工程指标**（方向性有用，但不能完整回答「Agent 做得有多好」）：

- Latency（响应延迟）
- Token efficiency（Token 消耗效率）
- Tool call count（工具调用次数）
- Cache hit rate（缓存命中率）

**更深层的质量指标**（真正回答「Agent 质量如何」）：

#### Keep Rate：代码留存率

> "For a given set of code changes that the agent proposed, we track what fraction of those remain in the user's codebase after fixed intervals of time."

这个设计极其聪明。它不需要人工标注，而是利用**代码留存本身就是用户满意度的代理指标**——如果用户的代码里还保留着 Agent 生成的修改，说明那些修改被接受了。

**关键洞察**：Keep Rate 之所以有效，是因为代码有「粘性」——用户不会因为「还可以」就保留改动，必须是「确实有用」才会留下。这天然过滤了「凑合能用」的噪声。

#### LLM 语义评估：用户响应情绪分析

Cursor 用一个 LLM 来阅读用户对 Agent 初始输出的回应，判断语义上的满意度：

> "A user moving on to the next feature is a strong signal the agent did its job, while a user pasting a stack trace is a reliable signal that it didn't."

这个方法把「用户满意度」转化为一个可大规模自动评估的指标——不需要人工打分，直接用模型判断用户响应的情感倾向。

**笔者认为**：Keep Rate + LLM 语义评估的组合提供了一个实用的 Agent 质量测量框架。前者测量客观的代码行为结果，后者测量主观的用户体验。两者结合比任何单一指标都更接近「Agent 实际质量」的真实评估。

### 2.3 一个被放弃的实验

Cursor 分享了一个被放弃的实验：尝试用一个更贵的模型来做 context summarization（上下文摘要），观察对 Agent 质量的影响。

结果：Agent 质量提升可以忽略不计，但成本却显著增加。结论是**不值得**。

> "In one experiment, we tried a more expensive model for context summarization and observed it made a negligible difference in agent quality that wasn't worth the higher cost."

这个案例的真正价值不是「不要用贵模型做 summarization」，而是**展示了 Cursor 如何用实验数据来终止看起来有前途但实际上不值得的方向**。这是一种反直觉但极其重要的工程纪律——不是所有「看起来正确」的优化都值得上线。

---

## 三、退化追踪与修复：异常检测告警体系

### 3.1 问题的本质：Harness 复杂性与 Bug 表面

随着功能增加，Harness 的状态空间急剧增长。任何复杂软件系统都面临同样的问题：**状态空间越大，可能的 bug 就越多，而且很多只在规模化了才能检测到**。

Cursor 特别指出了工具调用错误是最容易造成严重后果的：

> "tool call errors can be extremely harmful to a session in Cursor. While the agent can often self-correct, errors remain in context, wasting tokens and causing 'context rot,' where accumulated mistakes degrade the quality of the model's subsequent decisions."

这里引入了「context rot」概念——**错误会积累并污染后续决策**。这比单纯的「工具调用失败」更危险，因为它会导致 Agent 在错误的方向上越走越远，却不自知。

### 3.2 错误分类体系

Cursor 把工具错误分为两类：

**Unknown Errors（未知错误）** → 始终视为 bug，不容商量地告警

> "Any unknown error represents a bug in the harness, and we treat it accordingly."

**Expected Errors（预期错误）** → 需要进一步分析，不能直接判定为 bug

这类错误有多种原因：
- `InvalidArguments`：模型提出了错误的参数
- `UnexpectedEnvironment`：上下文窗口中的信息互相矛盾
- `ProviderError`：工具供应商（如 GenerateImage、WebSearch）宕机
- `UserAborted`：用户主动中断
- `Timeout`：超时

预期错误可能是 bug，也可能是预期行为——比如 grep 超时可能是工具性能问题，也可能是代码库太大导致模型生成了低效查询。

### 3.3 告警策略：两种机制

**阈值告警**：`Unknown error rate` 超过固定阈值时立即触发（因为未知错误 = bug）

**异常检测告警**：`Expected error rate` 显著偏离基线时触发（基线按工具和模型分别计算）

> "We compute baselines per-tool and per-model, because different models may mess up tool calls at different rates."

基线按工具和模型分别计算，这是关键细节——不同模型在工具调用上的错误模式差异很大，不能用统一基线。

### 3.4 自动化修复闭环

Cursor 还有一个 Weekly Automation 用了一个特殊 Skill，这个 Skill 教会模型如何：

1. 搜索日志
2. 找出新出现的或突然增量的错误
3. 在 backlog 中创建或更新 ticket

> "We lean heavily on Cloud Agents to kick off fixes for many issues at once, and can even trigger them directly from Linear."

这里的核心洞察是：**用 Agent 来修复 Agent Harness 的 bug**。这是「测量驱动改进」的最高形态——不是人工分析日志、人工创建 issue，而是让 AI 自己阅读日志、自己发现异常、自己创建修复任务。

在一次 focused sprint 中，这个自动化流程把「unexpected tool call errors」降低了一个数量级。

---

## 四、模型定制化：每个模型有不同的 Harness

### 4.1 工具格式的匹配

> "OpenAI's models are trained to edit files using a patch-based format, while Anthropic's models are trained on string replacement. Either model could use either tool, but giving it the unfamiliar one costs extra reasoning tokens and produces more mistakes."

这是一个有实际工程价值的观察——**工具格式的不匹配会直接增加 token 消耗和错误率**。Cursor 的做法是为每个模型配置它训练时习惯的工具格式：

- OpenAI 模型 → patch-based 编辑
- Anthropic 模型 → string replacement 编辑

这不仅仅是「给对了工具」，而是根据模型的**训练数据分布**来定制 Harness 行为，以减少推理成本和错误率。

### 4.2 深度定制：提示词按模型调整

定制的深度包括：
- 不同 provider 的自定义提示词
- 不同模型版本的自定义提示词

OpenAI 模型「更 literal 和 precise，instruction following 强」，而 Claude「更 intuitive，对 imprecise 指令的容忍度更高」。

### 4.3 模型 quirks 的 Harness 缓解

Cursor 分享了一个「context anxiety」案例：

> "we observed one model develop what we came to call context anxiety: As its context window filled up, it would start refusing work, hedging that the task seemed too big. We were able to reduce the behavior through prompt adjustments."

这是一个典型的**模型行为 quirks 被 Harness 缓解**的案例。模型表现出来的「上下文焦虑」不是模型的 bug，而是模型在特定状态分布下的固有行为。通过 prompt 调整（可能是告知模型「上下文填充是正常现象，不要因此降低信心」之类的方式），Harness 成功降低了这种行为。

**笔者认为**：这说明即使模型能力足够强，仍然会有模型级别的 quirks 需要 Harness 来处理。模型不是完美的，Harness 的一个重要职责是**在模型的不完美之上构建稳定的行为**。

---

## 五、中途换模型的挑战

这是文章中最有技术深度的部分之一。Cursor 描述了让用户中途切换模型时的技术挑战：

### 5.1 核心问题：不同模型有不同的 behaviors、prompts、tool shapes

当用户切换模型时，Cursor 自动切换到对应模型的 Harness——包括该模型的 customized prompts 和 tools。但**对话历史是由另一个模型生成的**，对当前模型来说是 out of distribution。

### 5.2 解决方案：自定义指令引导接管

Cursor 添加了 custom instructions 告诉模型：
1. 它正在接管一个 mid-chat session（不是从头开始）
2. 引导它不要调用 conversation history 中出现但不在自己工具集中的工具

这是 Harness 层对模型交接的处理——不是改变模型本身的行为，而是在系统提示词层面引导模型的正确响应。

### 5.3 缓存miss问题与缓解尝试

另一个挑战是 cache 命中率：

> "caches are provider- and model-specific, so switching means a cache miss and a slower, more expensive first turn."

Cursor 尝试在切换时做对话摘要，以提供模型一个干净的摘要，减少 cache penalty。但发现如果用户正在进行复杂任务，摘要会丢失重要细节。

结论：**推荐用户在一个对话中保持使用同一模型**，除非有明确理由切换。

**笔者认为**：这个结论很重要。它说明在最先进的 Agent 系统中，模型切换仍然有不可忽视的成本。在大多数场景下，「选一个模型用到底」仍然是更好的选择。模型切换应该是一个经过思考的决策，而不是随意切换。

---

## 六、Subagent：绕过模型切换挑战的另一条路

Cursor 还提到了一种替代方案：使用 subagent（子代理）来处理需要特定模型能力的子任务。

> "Another way to sidestep the challenges of mid-conversation model switching is to instead use a subagent, which starts from a fresh context window."

Subagent 从全新的上下文窗口开始，不需要处理 history 分布不匹配的问题。这与 Anthropic 提出的「Initator Agent + Coding Agent」双组件架构有类似的工程思路——**把复杂任务分解为多个 Agent，每个 Agent 从干净的上下文开始，而不是在一个不断累积上下文的单一 Agent 上试图管理切换成本**。

---

## 七、Harness 与未来：多 Agent 系统

Cursor 在文章结尾展望了未来：

> "The future of AI-assisted software engineering will be multi-agent. Instead of running every subtask through a single agent, the system routes tasks to specialized agents."

这与 Anthropic 的 Agent 演进路径完全一致——当 Agent 能力足够强时，单一 Agent 可以处理复杂任务；当下一个阶段，多个专业 Agent 的协作将带来更大的能力提升。

Cursor 特别强调了多 Agent 场景下的架构挑战：

- 不同 Agent 需要不同的工具集（specialized tools）
- 需要正确的 routing 机制来决定哪个 Agent 处理哪个任务
- Agent 之间需要有通信和协调机制

---

## 核心洞察总结

### 关于 Harness 工程

1. **测量驱动改进 > 设计驱动改进**。Cursor 的核心方法论是用数据（Keep Rate、LLM 语义评估、异常检测）而非直觉来指导 Harness 优化。好的 Harness 不是设计出来的，是测量—假设—实验—迭代出来的。

2. **上下文窗口的演化方向是从「静态填充」到「动态拉取」**。当模型能力足够强时，外部系统替模型选择上下文反而引入噪声。保留少量稳定有用的静态上下文，其他全部动态化。

3. **「context rot」是工具调用错误最危险的副产物**。错误不会孤立地发生，它们会累积并污染后续的模型决策。好的 Harness 需要有错误隔离和恢复机制。

### 关于测量体系

4. **Keep Rate + LLM 语义评估提供了可规模化的质量测量**。前者测量客观的代码行为结果（留存率），后者测量主观的用户体验（响应情绪）。两者结合比任何单一指标都更接近「真实质量」的评估。

5. **「不值得」的结论和「值得」的结论一样重要**。Cursor 用实验数据终止了看起来有前途的方向（更贵的 context summarization 模型）。这是一种反直觉但极其重要的工程纪律。

6. **基线必须按工具和模型分别计算**。不同模型在工具调用上的错误率差异很大，用统一基线会导致漏报或误报。

### 关于模型定制

7. **工具格式的匹配直接影响 Token 消耗和错误率**。给模型它训练时习惯的工具格式，而不是「也能用」的格式，可以显著减少推理成本和错误。

8. **模型 quirks 可以通过 Harness 来缓解**。「context anxiety」案例说明即使模型能力足够强，仍然需要 Harness 在模型不完美之上构建稳定行为。

---

## 与本文关联的项目推荐

- **[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)** — 135 个科研 Agent Skills，覆盖 15+ 科学领域，Skill 系统让 AI Agent 在专业领域任务的工具调用稳定性显著提升，与本文「工具调用错误是最大 bug 来源」形成工程互补

> 引用来源：
> - Cursor Blog: "Continually improving our agent harness" (2026-04-30) — https://cursor.com/blog/continually-improving-agent-harness
> - CursorBench: https://cursor.com/blog/cursorbench
> - Dynamic Context Discovery: https://cursor.com/blog/dynamic-context-discovery