# Cursor 的 Harness 评估方法论：Keep Rate、异常检测与 A/B 测试

> 原文：[Cursor Blog - Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)（2026-04-30）  
> 主题标签：`#harness-engineering` `#eval` `#measurement` `#cursor`

---

## 为什么这篇文章重要

Cursor 在 2026-04-30 的博客中首次系统披露了其 Agent Harness 的工程方法论。不是展示新功能，而是**展示他们如何判断一个改动是否真的让 Agent 变得更好**。

这在 AI Agent 领域是稀缺信息。大多数团队依赖主观感受或 benchmark 数字，但 Cursor 展示了**生产级 harness 评估的完整测量栈**：

- 离线 eval（CursorBench）捕捉能力基线
- 在线 A/B 测试验证真实使用场景
- **Keep Rate**：跟踪代码在用户代码库中的存活比例
- **LLM 语义满意度分析**：用模型判断用户是否真的满意
- 异常检测 + 自动化 ticket 创建驱动持续改进

这些方法直接解决了「harness 改动是否有效」这个核心问题。

---

## 一、评估的两层架构：离线 Eval + 在线实验

### 离线 Eval：快速标准化读数

Cursor 维护 [CursorBench](https://cursor.com/blog/cursorbench) 作为离线评估套件，目标是：

> "gives us a fast, standardized read on quality and lets us compare across time"

离线 eval 的价值是**速度**和**标准化**——每次代码提交可以快速跑一遍，捕捉回归。但 Cursor 明确指出：

> "even the best benchmarks only approximate real usage, meaning we'd miss important signals if we relied on them entirely"

这说明离线 eval 是必要条件，但不是充分条件。

### 在线实验：A/B 测试真实用户

Cursor 在生产环境运行**双盲 A/B 测试**，将 harness 变体并行部署在真实用户流量上。在线实验的优势是捕捉真实使用场景中的信号，但代价是：
- 需要足够的流量才能达到统计显著性
- 实验周期长（数天到数周）
- 有用户影响风险

关键洞察：**两层评估是互补的**，离线 eval 负责快速迭代，在线实验负责验证假设。两者缺一都会产生盲区。

---

## 二、在线实验的核心指标

Cursor 坦承「fuzzier but more important questions」——这些是真正难测量的东西。

### 2.1 Keep Rate：代码存活率

```
Keep Rate = 用户代码库中仍保留的 Agent 生成代码的比例
```

这是一个**事后验证指标**，在固定时间窗口后检查：

| 情况 | 信号解读 |
|------|----------|
| 代码被大量手动修改 | Agent 初始质量不足 |
| 用户要求 Agent 修复 | Agent 第一次没做对 |
| 用户直接进入下一个功能 | Agent 完成了任务 |

Keep Rate 的核心洞察：**用户是否需要回头收拾残局**。低 Keep Rate 说明 Agent 在第一次响应中产生了大量用户不接受或不满意的代码。

这个指标比「代码是否编译/通过测试」更接近真实价值——代码可以通过测试但仍然不是用户想要的。

### 2.2 LLM 语义满意度分析

Cursor 使用**模型来评估用户的反馈语义**：

> "A user moving on to the next feature is a strong signal the agent did its job, while a user pasting a stack trace is a reliable signal that it didn't"

这不是简单的文本匹配或情绪分析，而是让 LLM 阅读用户对 Agent 输出的响应，捕捉语义层面的满意/不满意信号。

这种方法的优点：
- 能捕捉「还不错但不是用户想要的」这类细粒度不满
- 不依赖用户主动打分（用户几乎不填反馈表单）
- 可规模化部署（模型自动分析所有对话）

### 2.3 常规工程指标

| 指标 | 用途 |
|------|------|
| 延迟（Latency） | 端到端响应时间，影响用户体验 |
| Token 效率 | 上下文窗口利用率，关联成本 |
| 工具调用次数 | 反映 Agent 是否高效达成目标 |
| 缓存命中率 | 影响成本和首轮响应速度 |

这些是**方向性指标**，帮助判断改动的副作用，但不能单独证明质量提升。

---

## 三、降级追踪与自动修复闭环

### 3.1 工具错误的分类体系

Cursor 将 Agent 工具调用错误分为两大类：

**Unknown Errors（未知错误）**：
- 始终视为 Bug
- 设置固定阈值告警，任何未知错误率上升都触发调查

**Expected Errors（预期错误）**：
- `InvalidArguments`：模型调用参数错误
- `UnexpectedEnvironment`：上下文窗口中的矛盾
- `ProviderError`：外部服务宕机（GenerateImage、WebSearch 等）
- `UserAborted`、`Timeout` 等

### 3.2 异常检测：超越固定阈值

固定阈值告警的问题：不同模型有不同基线，用同一阈值会漏报或误报。

Cursor 的解法：

> "We compute baselines per-tool and per-model, because different models may mess up tool calls at different rates"

按工具 × 模型建立基线，然后检测**异常偏离**——这比固定阈值更敏感，能捕捉到「错误率比该模型的正常水平显著上升」的情况。

### 3.3 自动化问题发现与 ticket 创建

Cursor 部署了一个**每周运行的 Cloud Agent**，配备专用 Skill：
1. 搜索生产日志
2. 发现新出现或 spike 的错误
3. 自动在 backlog 中创建或更新 ticket

这个机制的意义是：**将人工巡检变成了自动化监控**，让工程团队从救火模式转为预防模式。

Cursor 报告了一个具体成果：

> "Over the course of a focused sprint earlier this year, we drove unexpected tool call errors down by an order of magnitude"

一个 Sprint 将意外工具调用错误降低了一个数量级——这只有在有精确测量体系支撑下才可能实现。

---

## 四、Context Window 的演进：从护栏到动态拉取

Cursor 坦诚回顾了 Context Window 策略的演变，这段历史本身就是一份有价值的工程记录。

### 2024 年（早期）：大量护栏

模型能力较弱时期，Cursor 主动添加了大量上下文工程护栏：

- 每次编辑后向 Agent 展示 lint 和类型错误
- 当 Agent 请求行数过少时，自动重写其文件读取请求
- 限制 Agent 单轮最大工具调用次数
- 提供大量静态上下文（代码库布局、语义匹配片段、用户手动附加文件的压缩版本）

### 2026 年（现在）：动态上下文

> "we've adapted to increasing model capability by knocking down guardrails and providing more dynamic context, which can be fetched by the agent while it works"

现在的策略：
- 保留少量有用的静态上下文（操作系统、git status、当前/最近查看文件）
- 大规模减少静态上下文，改为**动态按需拉取**
- Agent 在工作过程中主动发现和请求所需上下文

这是一个**模型能力提升 → 护栏降低 → 上下文动态化**的技术演进路径。护栏不是「更好的设计」，而是「在模型能力不足时的工程补偿」。

---

## 五、Model-Specific 的深度定制

Cursor 明确指出其 harness 抽象层可以**为每个模型深度定制**，并且这种定制「goes very deep」。

### 工具格式的原生适配

核心例子：

| 模型 | 训练使用的编辑格式 | 原因 |
|------|------------------|------|
| OpenAI 模型 | **Patch-based 格式** | 训练时使用 |
| Anthropic 模型 | **String replacement** | 训练时使用 |

> "Either model could use either tool, but giving it the unfamiliar one costs extra reasoning tokens and produces more mistakes"

这个细节说明：**工具格式不是中性的——它影响模型的推理开销和错误率**。这是 harness 定制深度的最小切入点。

### Provider 和版本级别的自定义 Prompt

Cursor 观察到不同模型的「性格」差异：

- **OpenAI 模型**：更 literal 和 precise，instruction following 更严格
- **Claude 模型**：更 intuitive，对 imprecise 指令更宽容

这些差异会影响 Prompt 措辞、例子数量、指令精度等——都需要在 harness 层适配。

### 「Context Anxiety」：Harness 缓解 Model Quirk 的案例

Cursor 提到了一个具体的模型 quirks 案例：

> "we observed one model develop what we came to call context anxiety: As its context window filled up, it would start refusing work, hedging that the task seemed too big. We were able to reduce the behavior through prompt adjustments"

这个案例说明：**即使在 2026 年，模型仍会展现非预期的行为模式**。Harness 的角色不仅是「给模型好的工具」，还要「识别和缓解模型的非预期行为」。

---

## 六、Mid-Chat 模型切换的工程挑战

当用户在对话中途切换模型时，Cursor 面临两个挑战：

### 6.1 对话历史分布偏移

切换后，新模型面对的是「由另一个模型生成的对话历史」，这与它训练时的数据分布不同。

Cursor 的处理：
- 添加自定义指令，告知模型「你正在接管一个 mid-chat session」
- 引导模型**不调用**对话历史中出现但当前模型工具集中不存在的工具

### 6.2 缓存失效

> "caches are provider- and model-specific, so switching means a cache miss and a slower, more expensive first turn"

Cursor 尝试用**会话摘要**来缓解这个问题，但这又引入了新问题：

> "if the user is deep into a complex task, the summary can lose important details"

这个权衡说明：**会话摘要是一种信息压缩，而压缩必然有损失**。对于复杂任务，这个损失不可接受。

Cursor 的实际建议：

> "We generally recommend staying with one model for the duration of a conversation unless you have a reason to switch"

这与 Augment 的「好习惯积累」研究形成有趣的对比——两者都在关注长程 Agent 的上下文质量问题，但是从不同角度切入。

---

## 七、未来方向：Harness 是多 Agent 编排的核心

Cursor 对未来的判断非常明确：

> "The future of AI-assisted software engineering will be multi-agent. Instead of running every subtask through a single agent, the system will learn to delegate across specialized agents and subagents"

而关键推论是：

> "The ability to orchestrate that kind of coordination **will live in the harness** rather than any single agent"

这意味着：
- **Agent 是执行单元**（做具体任务）
- **Harness 是编排层**（决定派发哪个 Agent、如何 Framing 任务、如何缝合结果）

这与 Anthropic 的「Brain/Hands 解耦」一脉相承，但更具体地指向了**多 Agent 场景下的 Harness 职责**：

| 职责 | 说明 |
|------|------|
| 派发决策 | 判断哪个 Agent 适合当前子任务 |
| Framing | 根据 Agent 优势调整任务描述方式 |
| 结果缝合 | 将多个 Agent 的输出整合为连贯的工作流 |
| 上下文传递 | 管理跨 Agent 的信息流 |

---

## 工程启示

### 1. 测量先于优化

Cursor 的方法论核心是：**没有测量就没有改进**。Keep Rate、LLM 语义分析、异常检测基线——这些构成了一套完整的测量栈，使得「优化」这件事有据可依。

对于构建自己 Agent 系统的团队，这意味着：
- 先建立基线（baseline measurement）
- 再引入改动（controlled change）
- 最后验证效果（comparison against baseline）

跳过测量直接优化，等于盲人骑瞎马。

### 2. Expected vs Unknown 错误的分类哲学

Cursor 将错误分为「预期的」和「未知的」，并对后者设置严格告警——这体现了**防御性工程思维**：任何异常都应该被调查，而不是被忽视。

这对 Agent 系统特别重要，因为模型的行为空间是巨大的，某些错误模式只有在生产规模下才会显现。

### 3. 护栏是技术债，不是设计选择

Cursor 明确指出，早期的护栏是「因为模型能力不足的工程补偿」，而现在模型能力提升后被逐步移除。这说明**护栏应该被视为技术债**，随着模型能力演进应该被主动偿还，而不是永久保留。

### 4. Harness 定制深度决定 Agent 上限

工具格式、Prompt 策略、异常处理——Cursor 在这些维度上对不同模型做深度定制。这说明**Agent 的最终表现是 Model + Harness 的联合产物**，而非模型本身的独立属性。

同样的模型，在不同深度的 Harness 下，可能展现出显著不同的能力水平和行为特征。

---

## 总结

Cursor 这篇文章提供了一个重要的一手视角：**如何在生产环境中持续改进 Agent Harness**。

核心方法论：
- **离线 + 在线两层评估**：快速迭代 + 真实验证
- **Keep Rate + LLM 语义分析**：捕捉真实用户价值
- **异常检测 + 自动化 ticket**：将人工巡检变为自动化监控
- **per-model 深度定制**：Harness 与模型的联合优化
- **多 Agent 编排是 Harness 的核心职责**：Agent 是执行单元，Harness 是协调层

这套方法论对于任何正在构建 Agent 系统的团队都具有参考价值：测量体系建设是第一步，也是最难的一步，但它决定了系统能否持续改进。

---

*来源：[Cursor Blog - Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)，2026-04-30*
