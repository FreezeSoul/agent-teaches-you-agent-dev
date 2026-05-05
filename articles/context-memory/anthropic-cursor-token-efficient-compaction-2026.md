# 注意力预算与 Token 高效压缩：Anthropic 和 Cursor 共同指向的长程 Agent 进化方向

> **核心论点**：长程 Agent 的核心挑战不是「扩大上下文窗口」，而是如何在有限注意力预算内做出「压缩什么、保留什么」的高质量决策。Anthropic 的注意力预算理论与 Cursor 的自概括训练（Compaction-in-the-Loop）从不同角度得出一致结论——未来的长程 Agent 必须具备「 learned context compression」能力，而非依赖更大的上下文窗口。

---

## 1. 长程 Agent 的上下文困境：注意力稀缺

当 Agent 运行时长从几分钟扩展到数小时，任务复杂度从单轮对话升级为多阶段工程，传统的上下文管理方式面临根本性挑战。

Anthropic 在「Effective Context Engineering for AI Agents」中明确指出了这一问题的本质：

> "Context, therefore, must be treated as a finite resource with diminishing marginal returns. Like humans, who have limited working memory capacity, LLMs have an 'attention budget' that they draw on when parsing large volumes of context."
> — [Anthropic Engineering: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

LLM 基于 Transformer 架构，每个 token 可以 attend 到上下文中的所有其他 token，形成 n² 的配对关系。当上下文长度增加，模型捕获这些全局配对关系的能力被稀释——这不是一个「硬边界」，而是一个性能梯度：模型在长上下文上仍可用，但信息检索和长距离推理的精度会下降。

> "This creates a natural tension between context size and attention focus."
> — 同上

**核心困境**：上下文窗口增长的速度（每年约 2x）远不及 Agent 轨迹扩张的速度（复杂任务可达数十万 token）。依赖更大的上下文窗口来解决长程任务，在工程上不可持续。

---

## 2. Anthropic 的解法：最小高信噪比 token 集

Anthropic 提出的解决方案框架是「找到最小的高信噪比 token 集」：

### 2.1 System Prompt 的 Goldilocks Zone

System prompt 的编写存在两个极端失败模式：

- **过度工程化**：工程师在 prompt 中硬编码复杂的 if-else 逻辑，试图精确控制 Agent 行为。这造成脆弱性和维护复杂度随时间指数增长。
- **过度抽象**：提供模糊的高层次指导，LLM 无法从中获得具体的输出信号，或错误地假设共享上下文。

> "The optimal altitude strikes a balance: specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics to guide behavior."
> — 同上

Anthropic 建议将 system prompt 组织为清晰的分区（`<background_information>`、`<instructions>`、`## Tool guidance`、`## Output description` 等），使用 XML 标签或 Markdown 标题区分。但格式本身不是关键——**目标是最小化地提供完整指导**，而非堆砌内容。

### 2.2 注意力稀缺的结构性来源

为什么注意力是稀缺的？Anthropic 给出了 Transformer 架构层面的解释：

1. **n² 配对关系**：每个 token 与其他所有 token 的交互导致计算成本二次方增长
2. **训练数据分布偏差**：训练数据中短序列远多于长序列，模型在长上下文上缺乏专项优化
3. **位置编码插值的代价**：通过位置编码插值（如 RoPE）可以让模型处理更长序列，但这会导致 token 位置理解的精确度下降

> "Techniques like position encoding interpolation allow models to handle longer sequences by adapting them to the originally trained smaller context, though with some degradation in token position understanding."
> — 同上

这意味着：**上下文窗口的扩大并不等价于能力的等比例提升**。超过某个阈值后，上下文越长，有效信息的密度反而越低。

---

## 3. Cursor 的解法：Compaction-in-the-Loop 训练

Cursor 在「Training Composer for Long Horizons」中给出了截然不同但互补的答案——不是优化 context 的内容，而是**训练模型学会压缩**。

### 3.1 传统压缩方法的局限

当前主流的上下文压缩技术有两类：

| 压缩方式 | 实现原理 | 核心缺陷 |
|---------|---------|---------|
| **Prompt-based Summarization** | 通过一个大型 summarization prompt 让另一个模型压缩上下文 | prompt 本身长达数千 token；输出压缩结果平均 >5000 token；压缩质量高度依赖 prompt 设计 |
| **Sliding Context Window** | 丢弃旧上下文，保留最近的 token | 关键信息被一同丢弃，Agent 在长程任务中失去连续性 |

> "These approaches to compaction share the downside that they can cause the model to forget critical information from the context, reducing its efficacy as it advances through long-running tasks."
> — [Cursor Blog: Training Composer for Long Horizons](https://cursor.com/blog/self-summarization)

### 3.2 Self-Summarization：将压缩作为训练行为

Cursor 的 Composer 模型采用了一种根本不同的方法：**将压缩能力本身作为模型的训练目标**，而非作为 harness 的后处理步骤。

自概括过程如下：

1. Composer 生成直到达到固定 token 长度触发器
2. 插入合成查询，要求模型概括当前上下文
3. 模型获得 scratch space 来思考最佳摘要，然后生成压缩后的上下文
4. 循环回到第 1 步，使用压缩后的上下文继续

> "Each training rollout can involve multiple generations chained together by summaries, rather than a single prompt–response pair. This means the self-summaries themselves are part of what gets rewarded."
> — 同上

关键在于：**在训练中引入压缩环节，使模型学会判断「什么信息值得保留」**。奖励信号同时惠及 agent 的正常轨迹和那些使其成为可能的自概括行为。

### 3.3 Token 效率的量化对比

Cursor 的实验表明，经过压缩训练的 Composer 与高度调优的 baseline 对比：

| 指标 | Baseline (Prompt-based) | Composer (Self-Summarization) |
|------|------------------------|------------------------------|
| Summarization prompt 长度 | 数千 token，十几节精心措辞 | 仅需「Please summarize the conversation」|
| 输出压缩大小 | 平均 >5000 token | 平均 ~1000 token |
| 压缩错误率降低 | — | 50%（相比精心设计的 baseline）|
| KV cache 复用 | 否 | 是（复用先前 token 的中间计算）|

> "Self-summary consistently reduces the error from compaction by 50%, even compared to the targeted baseline approach, while using one-fifth of the tokens and reusing the KV cache."
> — 同上

这个结果的意义是深远的：**模型自己学会的压缩，比专门设计的压缩提示更高效。**这不是 prompt engineering 的胜利，而是 learned compression 的胜利。

---

## 4. 两者交汇：Learned Context Compression 是答案

Anthropic 的「注意力作为有限预算」理论，和 Cursor 的「Compaction-in-the-Loop」训练方法，从两个角度指向同一个结论：

**长程 Agent 的核心竞争力不在于上下文窗口大小，而在于压缩质量。**

具体体现为：

### 4.1 压缩目标的一致性

| 维度 | Anthropic 视角 | Cursor 视角 |
|------|--------------|-----------|
| 压缩原则 | 最小高信噪比 token 集 | 模型自判断关键信息 |
| 评估标准 | 注意力预算利用效率 | 任务完成质量 + 压缩效率 |
| 实现路径 | Prompt 设计与上下文curation | 强化学习中的压缩训练 |

### 4.2 失败模式的对应

两者都指出了同一种失败模式的风险：**压缩过程中丢失关键信息**。

- Anthropic 观察到上下文窗口增长导致信息检索精度下降
- Cursor 记录了传统 sliding window 和 summarization 方法导致 Agent 在长程任务中失去能力

这意味着：单纯的上下文管理不够，需要模型本身具备「知道什么该记住」的能力。

### 4.3 进化方向的判断

> 笔者认为：Anthropic 和 Cursor 的技术收敛不是巧合。随着 Agent 任务复杂度提升，「扩大窗口」策略将在工程和成本上遇到不可逾越的瓶颈。而「学会压缩」策略的核心优势在于：**压缩质量随训练提升，而成本随模型推理效率优化下降**。这条路径的天花板更高。

从另一个角度看，这场收敛也揭示了一个更根本的设计哲学转变：

- **窗口时代**：假设上下文足够大，信息保留就不是问题
- **压缩时代**：假设注意力永远是稀缺资源，必须学会取舍

---

## 5. 工程落地建议

基于上述分析，对于构建长程 Agent 的工程实践：

### 5.1 从「加载什么」转向「压缩什么」

不要只关注「如何让上下文更长」，而是思考「模型如何在压缩时保留关键信息」。这意味着：

- 在 Agent 评估体系中加入「压缩后任务完成度」指标
- 关注模型在多次压缩循环后的任务连贯性，而非单次上下文大小

### 5.2 System Prompt 的最小化原则

Anthropic 的 Goldilocks Zone 原则：**prompt 应该给出行为边界和目标，而非实现步骤**。具体操作：

- 使用分区结构（Background / Instructions / Tool Guidance / Output Format）
- 每个分区只包含「足以指导行为」的最小信息
- 避免在 prompt 中硬编码状态机或复杂逻辑

### 5.3 考虑 Compaction-in-the-Loop 的训练范式

对于需要极长程能力的场景（如编译器、游戏 AI、复杂系统工程），考虑：

- 训练时在压缩点注入 reward signal，同时优化 agent 行为和压缩质量
- 使用模型自身的压缩能力，而非外部 summarization 模型
- 评估标准从「context length」转向「compression ratio + task success rate」

### 5.4 检查清单：长程 Agent 上下文工程自检

```
[ ] 是否将上下文视为有限预算，而非无限资源？
[ ] System prompt 是否达到「最小必要信息」标准？
[ ] 是否测量了「上下文利用率」而非仅「上下文大小」？
[ ] 压缩策略是否有反馈机制（压缩质量影响任务结果）？
[ ] 是否考虑了多次压缩后的信息丢失累积问题？
```

---

## 6. 结论

Anthropic 和 Cursor 从工程实践和训练方法两个维度，共同指向了一个明确的技术方向：

**长程 Agent 的瓶颈不是上下文窗口大小，而是「在注意力约束下做出高质量压缩决策」的能力。**

未来的 Agent 架构将更多采用「learned compression」而非「larger context」策略。这不仅是技术选择，更是一种关于智能体如何管理有限认知资源的基础假设。

当整个行业从「窗口竞赛」转向「压缩能力竞赛」，那些在训练阶段就将压缩作为一等公民的 Agent，将展现出越来越显著的长期优势。

---

## 参考来源

- [Anthropic Engineering: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Cursor Blog: Training Composer for Long Horizons](https://cursor.com/blog/self-summarization)
- [Cursor Blog: The Third Era of AI Software Development](https://cursor.com/blog/third-era)