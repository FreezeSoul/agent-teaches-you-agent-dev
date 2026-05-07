# Generator-Evaluator 架构：多 Agent 评估模式从 GAN 到生产级应用的演进

> **核心论点**：Anthropic 的 GAN 启发架构（Planner/Generator/Evaluator）与 Cursor 的 38% GPU kernel 优化实战，共同揭示了一个明确的方向——**分离评估者与执行者**是释放 Agent 生产力的关键杠杆。本文深度解析这一架构模式的原理、实现路径与工程边界。

---

## 一、问题的本质：为什么 Agent 无法自我纠错

在探讨多 Agent 评估架构之前，需要先理解这一模式出现的根本原因。

Anthropic 在 2026 年 5 月发布的工程博客中，清晰地陈述了一个核心观察：

> "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."
> — [Anthropic Engineering: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这个现象并非偶然。LLM 的预训练机制使其倾向于生成"合理"的回复，而自我评估时，这种倾向会被放大——Agent 无法像人类一样感受到"这不对"的直觉。这种**自我偏袒偏差**（self-serving bias）在创意性任务（如前端设计）中尤为严重，在可验证任务中同样存在。

更根本的问题是：**执行与评估在认知上存在冲突**。执行者关注"如何完成"，评估者关注"是否正确"。当同一个 Agent 同时扮演两个角色时，它很难同时保持建设性和批判性。

官方原文将这一问题的机制描述得极为精准：

> "Separating the agent doing the work from the agent judging it proves to be a strong lever to address this issue. The separation doesn't immediately eliminate that leniency on its own; the evaluator is still an LLM that is inclined to be generous towards LLM-generated outputs. But tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work."
> — [Anthropic Engineering: Harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这意味着：关键不在于"消除"偏差，而在于**让偏差变得可工程化**——通过调优一个独立的 Evaluator，使其比 Generator 更具批判性。

---

## 二、GAN 启发的架构起源

Anthropic 的 Prithvi Rajasekaran 在设计前端设计 Agent 时，从生成对抗网络（GAN）中获得了灵感。

GAN 的核心思想是：两个网络——Generator 和 Discriminator——相互对抗，Generator 生成样本，Discriminator 判别真伪，两者通过对抗性训练共同提升。

映射到 Agent 系统：

| GAN 组件 | Agent 架构对应 | 职责 |
|---------|--------------|------|
| Generator | Generator Agent | 生成前端代码/应用代码 |
| Discriminator | Evaluator Agent | 评估生成质量，给出改进方向 |
| 对抗性训练 | Generator-Evaluator 迭代循环 | 通过外部反馈驱动 Generator 提升 |

GAN 的一个关键洞察是：**Discriminator 的判别能力必须被单独训练**——如果 Generator 自己学着"更挑剔"，它会同时变得更会"伪装"。同理，Agent 的自我评估能力无法通过自我改进获得提升，必须有一个独立的 Evaluator 来承担这一职责。

---

## 三、三 Agent 架构的完整设计

### 3.1 架构组件

Anthropic 的生产级实现采用三 Agent 架构，而非简单的两者分离：

```
┌─────────────────────────────────────────────────────┐
│                    Planner Agent                      │
│  · 将简单 prompt 扩展为完整产品规格说明               │
│  · 保持高层次的 product context，不陷入技术细节        │
│  · 主动寻找 AI 功能集成机会                           │
└─────────────────────────────────────────────────────┘
                            ↓ 输出：16-feature spec
┌─────────────────────────────────────────────────────┐
│                   Generator Agent                     │
│  · 一次只实现一个功能（sprint 模型）                   │
│  · 完成后自我初步评估                                │
│  · 与 Evaluator 协商 sprint contract                 │
└─────────────────────────────────────────────────────┘
                            ↓ 输出：实现代码 + self-critique
┌─────────────────────────────────────────────────────┐
│                   Evaluator Agent                    │
│  · 使用 Playwright MCP 直接操作运行中的应用           │
│  · 按验收标准逐项评分                                │
│  · 不达标则触发 Generator 返工                        │
└─────────────────────────────────────────────────────┘
```

### 3.2 Sprint Contract 机制

三 Agent 架构中，最关键的设计是 **Sprint Contract（冲刺合同）**。

Generator 和 Evaluator 在每个 sprint 开始前协商 contract：
- Generator 提出"我要构建什么"和"如何验证"
- Evaluator 审核 Contract 是否与产品规格一致
- 双方迭代直到达成共识

这解决了一个关键问题：产品规格是高层次的，而验收标准必须是可测试的。Contract 是连接两者的桥梁。

Anthropic 的原文描述了这一机制的工作方式：

> "Before each sprint, the generator and evaluator negotiated a sprint contract: agreeing on what 'done' looked like for that chunk of work before any code was written. This existed because the product spec was intentionally high-level, and I wanted a step to bridge the gap between user stories and testable implementation."
> — [Anthropic Engineering: Harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)

### 3.3 评分标准的工程化设计

Evaluator 的评估标准需要被刻意设计，而非让 LLM 自由发挥。Anthropic 为前端设计场景设计了四个评分维度，并赋予不同权重：

| 维度 | 权重 | 设计意图 |
|------|------|---------|
| Design Quality | 高 | 整体感而非零件拼凑，惩罚"AI 味"设计 |
| Originality | 高 | 自定义决策 vs 模板 defaults，惩罚紫色渐变卡片等 AI 生成特征 |
| Craft | 中 | 技术执行（typography、spacing、contrast），基本能力检测 |
| Functionality | 中 | 可用性独立于美学，完成核心用户任务 |

权重的设计反映了核心洞察：**Claude 默认在 Craft 和 Functionality 上表现良好，但在 Design Quality 和 Originality 上倾向于保守**。通过提高后者的权重，驱动模型承担更多美学风险。

---

## 四、Cursor 38% 加速的实战验证

多 Agent 评估架构的价值，最终需要通过实证来检验。Cursor 在 2026 年与 NVIDIA 合作的项目提供了目前最有力的证据。

### 4.1 实验设计

Cursor 的多 Agent 系统接受了 235 个 CUDA kernel 优化问题，这些问题来自 124 个真实生产模型（DeepSeek、Qwen、Gemma、Kimi、Stable Diffusion），使用 NVIDIA SOL-ExecBench 基准测试在 27 块 Blackwell 200 GPU 上进行评估。

关键实验设计决策：要求 Agent 用两种语言编写解决方案——
- **CUDA C + inline PTX**：直接操作寄存器和 ISA 级别的指令，测试 Agent 是否能在硬件最底层进行推理
- **CuTe DSL**：高层可组合抽象，在公开训练数据中几乎不存在，测试 Agent 是否能从文档中学习全新 API

### 4.2 结果数据

| 指标 | 数值 |
|------|------|
| Geomean Speedup | **38%**（对比单 Agent baseline）|
| 优化超过 2x 的问题比例 | 19%（45/235）|
| 最优 SOL Score（接近硬件极限）| 0.9722（接近理论上限 1.0）|
| 人工优化 Baseline 超越 | BF16 Grouped Query Attention 实现 SOL 0.9722，领先 FlashInfer |

这些结果的含义超出数字本身：
- 手工 kernel 优化是高度专业化的工作，通常需要数月甚至数年的经验积累
- 多 Agent 系统在 3 周内完成了这一规模的优化
- 优化问题集是开放式的——没有标准答案，系统必须自己探索解决方案空间

Cursor 官方对这一结果的评价：

> "The most ambitious tasks in software are open-ended, without a clear solution. Single agent systems struggle here because models are best at narrowly scoped tasks they have already seen during training. We see the kernel optimization experiment as further validation that multi-agent architectures will quickly become the default approach to building software because they can tackle novel problems that fall far outside training data distribution."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://www.cursor.com/blog/multi-agent-kernels)

### 4.3 协作模式分析

Cursor 的多 Agent 系统采用了 Planner + Workers 的协调模式：

```
┌──────────────────────────────────────────┐
│           Planner Agent                   │
│  · 分配和动态平衡工作负载                  │
│  · 基于性能指标重新分配任务                │
│  · 协调整个基准测试循环                   │
└──────────────────────────────────────────┘
                    ↓
    ┌───────────┬───────────┬───────────┐
    │ Worker 1  │ Worker 2  │ Worker N  │
    │ 自主优化  │ 自主优化  │ 自主优化   │
    │ kernel   │ kernel   │ kernel    │
    └───────────┴───────────┴───────────┘
                    ↓
    ┌────────────────────────────────────┐
    │       Benchmarking Pipeline         │
    │  自动测试→调试→优化循环，无人工介入  │
    └────────────────────────────────────┘
```

这种模式的精髓在于：**规划与执行分离**。Planner 负责协调，Workers 负责具体优化，基准测试管道提供客观的性能反馈。整个协调协议存在于一个 markdown 文件中，定义了输出格式、规则和测试方式。

---

## 五、工程实践中的关键发现

### 5.1 Context Reset vs Compaction 的权衡

Anthropic 的早期工作使用了 Context Reset（重置上下文窗口 + 结构化handoff artifact），这是因为早期模型存在"Context Anxiety"——当感知到上下文快满时，会提前结束工作。

这一现象的机制是：

> "Some models also exhibit 'context anxiety,' in which they begin wrapping up work prematurely as they approach what they believe is their context limit. Context resets—clearing the context window entirely and starting a fresh agent, combined with a structured handoff that carries the previous agent's state and the next steps—addresses both these issues."
> — [Anthropic Engineering: Harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)

关键发现是：**Compaction（压缩）和 Reset 不是可以互换的**。Compaction 在原位置总结对话历史，保留连续性，但不提供干净的 slate；Reset 提供干净 slate，但需要依赖 handoff artifact 携带足够状态。

当使用 Opus 4.5 时，Context Anxiety 基本消失，可以完全放弃 Reset，改为单一连续 session + 自动 compaction。

### 5.2 Evaluator 调优比 Generator 更容易

这是 GAN 启发模式的一个反直觉发现：**独立调优一个批判性的 Evaluator，比让 Generator 学会自我批判更容易**。

原因在于：
1. Generator 的批判性思维会与生成能力产生干扰——当 Generator 被训练得更会批评时，它的生成也会变得更保守
2. 外部 Evaluator 提供了一个稳定的、可以迭代改进的反馈目标
3. Generator 面对具体反馈时的迭代效率，远高于面对模糊的"自我反思"指引

### 5.3 迭代不是线性改善

GAN 模式的另一个关键发现是：**迭代改善不是线性的**。

> "Later implementations tended to be better as a whole, but I regularly saw cases where I preferred a middle iteration over the last one."
> — [Anthropic Engineering: Harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)

某些迭代会产生"急转弯"式的美学跳跃（an aesthetic turn），而非逐步改进。这在设计上是有价值的，但意味着评估标准需要能够识别这种非线性改善。

---

## 六、与 Planner/Worker 架构的关系

Generator-Evaluator 架构与之前讨论的 Planner/Worker 架构是互补而非替代的关系：

| 维度 | Planner/Worker | Generator/Evaluator |
|------|--------------|---------------------|
| 关注点 | 工作分配与协调 | 质量评估与改进 |
| 核心问题 | "谁来做什么" | "做得够好吗" |
| 通信方式 | 消息传递/任务队列 | 文件/结构化 Contract |
| 典型应用 | 并行 kernel 优化 | 设计/架构/功能验收 |
| Agent 间关系 | 协作（cooperative） | 对抗（adversarial） |

两者可以叠加使用：Planner 负责任务分配，多个 Worker 并行执行，每个 Worker 内部使用 Generator-Evaluator 循环确保质量。这是 Cursor kernel 优化系统的实际架构。

---

## 七、适用边界与反模式

### 7.1 适用场景

Generator-Evaluator 架构特别适合以下场景：
- **开放式优化问题**：没有标准答案，需要探索解决方案空间
- **主观质量评估**：设计美感、代码可读性等无法自动化验证的标准
- **长时运行任务**：需要多个迭代才能收敛的问题
- **多层评估标准**：不同维度的质量要求需要独立的评估逻辑

### 7.2 不适用场景

- **简单确定性任务**：单次执行就能完美完成，无需迭代
- **评估标准完全客观且可自动化**：如编译成功、测试通过——这些应该由机器自动检测，而非 LLM Evaluator
- **成本敏感的一次性任务**：三 Agent 架构的 token 消耗是单 Agent 的 10-20 倍

### 7.3 反模式：过度工程化的 Evaluator

最常见的反模式是为每个维度都创建独立 Evaluator，导致系统过于复杂。Anthropic 的建议是：

> "We recommend working to curate a set of diverse, canonical examples that effectively portray the expected behavior of the agent. For an LLM, examples are the 'pictures' worth a thousand words."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

Evalutor 的评分标准应该是**少量关键维度的刻意设计**，而非试图覆盖所有质量标准。

---

## 八、行动启示

1. **在 Agent 项目中引入独立的 Evaluator**：不要依赖 Agent 自我评估，尤其是在质量敏感的场景（设计、架构、安全）
2. **通过 GAN 思想理解分离的价值**：关键不是消除偏差，而是让偏差变得可调优、可迭代
3. **使用 Sprint Contract 桥接规格与验收**：高层次的产品规格必须通过 Contract 转化为可测试的验收标准
4. **Planner/Worker + Generator/Evaluator 可以叠加**：复杂系统中，两者结合使用效果更好
5. **成本换质量是有意识的工程决策**：三 Agent 架构的成本是单 Agent 的 10-20 倍，这笔投资只值得开放式问题

> 笔者认为：2026 年是 Agent 架构分水岭——从单 Agent 迭代，进化到多 Agent 对抗性评估，是生产级 Agent 系统的必备能力。

---

**引用来源**：
- [Anthropic Engineering: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://www.cursor.com/blog/multi-agent-kernels)
- [GitHub: Cursor kernel optimization results](https://github.com/anysphere/kernel-optimization-results)
