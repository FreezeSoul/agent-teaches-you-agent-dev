# AI 抗性评估的设计陷阱：Anthropic 三轮迭代的工程教训

**核心主张**：当 AI 能够完整解决一个评估题时，传统「技术能力筛选」的假设便已失效——不是题目太简单，而是评估范式需要从「找答案」切换到「验证无法被委托的判断力」。

---

## 评估范式的失效：从「找答案」到「验证判断力」

2024 年，Anthropic 性能优化团队面临一个前所未有的问题。他们的 take-home 测试（模拟加速器代码优化）运行了 18 个月，Help 了 hire 数十名工程师，但 Claude Opus 4 在 2 小时限制内已经能击败几乎所有人类申请者。

这不仅仅是「AI 太强」的技术问题，而是**评估范式的根本性危机**。

当 AI 能够在限定时间内完整解决一个技术评估题时，该评估题便失去了区分人类能力差异的功能。对于性能工程师这类岗位，面试官仍然需要招到真正的人才，但传统的「出一道难题，看看谁能解出来」的模式已经失效。

Anthropic 的 Tristan Hume 在官方工程博客中记录了这个过程，标题为「Designing AI resistant technical evaluations」。这不是一篇关于 AI 安全的文章，而是一篇关于**如何在 AI 越来越强的时代保持技术评估有效性**的实战复盘。

---

## 第一代评估：一个真实的性能优化问题

2023 年 11 月，Anthropic 刚拿到新的 TPU 和 GPU 集群，急需 hired 性能工程师。他们需要一个能在周末完成的评估，能够在 2-4 小时内完成，同时能够捕获真实性能优化工作的复杂性。

Tristan 设计了一个 Python 模拟器，模拟一个类似 TPU 的加速器。申请者需要优化一段并行树遍历代码，机器有以下特征：

- **手动管理的 scratchpad 内存**（与 CPU 不同，accelerator 需要 explicit memory management）
- **VLIW**（每周期多个执行单元并行，需要高效的指令打包）
- **SIMD**（每条指令操作多个元素）
- **多核并行**（跨核心分配工作）

任务描述原文：

> "The task is a parallel tree traversal, deliberately not deep learning flavored, since most performance engineers hadn't worked on deep learning yet and could learn domain specifics on the job."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

申请者从一个完全串行的实现开始，逐步 exploit 机器的并行性。先 warmup 是多核并行，然后选择处理 SIMD 向量化或 VLIW 指令打包。原始版本还包含一个需要调试的 bug，锻炼申请者构建工具的能力。

设计原则非常清晰：

1. **代表性**：问题应该让申请者尝到实际工作的味道
2. **高信号**：避免依赖单一洞察的问题，确保申请者有充分的机会展示综合能力
3. **无特定领域知识要求**：有良好基础的人可以在工作中学习 specifics
4. **有趣**：快速开发循环、有趣的问题、创造性空间

第一代评估运行了 18 个月，效果很好。GitHub 上有 1000 多名申请者完成了测试，招聘到了大多数现有性能工程团队成员。反馈非常正面——许多申请者超过了 4 小时限制，因为他们很享受这个过程。

**然后 Claude Opus 4 击败了它。**

---

## 第二代评估：增加深度，缩短时间

2025 年 5 月，Tristan 测试了预发布的 Claude Opus 4。结果：

> "It came up with a more optimized solution than almost all humans did within the 4-hour limit."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

修复方案很直接：找到 Claude Opus 4 开始遇到困难的地方，作为新版本的起点。Tristan 编写了更干净的 starter code，添加了新的机器 features 以增加深度，并移除了多核（因为 Claude 已经解决了它，而这只会减缓开发循环）。

时间限制也从 4 小时缩短到 2 小时。

版本 2 强调聪明的优化洞察力胜于调试和代码量。这让它服务了**几个月**。

然后 Claude Opus 4.5 击败了它。

---

## Claude Opus 4.5 的具体失败过程

测试预发布 Claude Opus 4.5 时，Tristan 观察到：

> "It solved the initial bottlenecks, implemented all the common micro-optimizations, and met our passing threshold in under an hour."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

然后它停下来，确信自己遇到了无法克服的内存带宽瓶颈。大多数人类也会得同样的结论。但是有一些聪明的技巧可以 exploit 问题结构来 workaround 那个瓶颈。当 Tristan 告诉 Claude 可能的 cycle count 时，它思考了一会儿然后找到了那个技巧。它调试、调优并实现了进一步的优化。到 2 小时 mark 时，它的分数与该时间限制内最佳人类性能匹配——而那个人重度使用了 Claude 4 with steering。

这是一个关键问题：**最优策略变成了将任务委托给 Claude Code**。

---

## 核心困境：禁止 AI 不是答案

有人建议禁止 AI 辅助。Tristan 不想这样做。原因不仅是执行挑战：

> "I had a sense that given people continue to play a vital role in our work, I should be able to figure out some way for them to distinguish themselves in a setting with AI—like they'd have on the job."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

他还担心，如果将标准提高到「显著超越 Claude Code 独自能做的事情」，结果可能更糟：

> "A human trying to steer Claude would likely be constantly behind, understanding what Claude did only after the fact. The dominant strategy might become sitting back and watching."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

最终，现在的性能工程师的工作更像是：**艰难的调试、系统设计、性能分析、弄清楚如何验证系统正确性、以及让 Claude 的代码更简单更优雅**。这些东西很难用客观的方式测试，需要大量时间或共同上下文。

---

## 第一次尝试：不同的优化问题

Tristan 意识到 Claude 可以帮助他快速实现任何设计的东西，这促使他尝试开发一个更难的 take-home。他选择了一个基于他实际在 Anthropic 做过的更棘手的内核优化的问题：一个高效的数据转置问题。Claude Opus 4.5 找到了一个他甚至没有想到的出色优化。

通过仔细分析，它意识到可以转置整个计算而不是想办法转置数据，并相应地重写了整个程序。

在人类工程师的实际案例中，这个方法不会 work，所以 Tristan 打补丁了问题以移除那个方法。然后 Claude 取得了进展但找不到最有效的解决方案。看起来他找到了新问题，只需要希望人类申请者能足够快地解决它。

但他用 Claude Code 的 "ultrathink" 特性检查了一下，结果它解决了它——它甚至知道修复 bank conflicts 的技巧。

**教训**：对于工程师在许多平台上努力过的数据转置和 bank conflicts 问题，Claude 有大量训练数据可以借鉴。Tristan 从第一性原理找到了解决方案，而 Claude 可以借鉴更大的经验工具箱。

---

## 第二次尝试：走向更 out-of-distribution

Tristan 需要一个 Claude 的更大经验库难以胜过人类推理的问题：**足够 out-of-distribution**。不幸的是，这与他想要像真实工作的目标冲突。

他想到了他喜欢的不寻常优化问题：**Zachtronics 游戏**。这些编程益智游戏使用不寻常的高度受限指令集，强制你以非常规方式编程。例如，在 Shenzhen I/O 中，程序被分割到多个通信芯片，每个芯片只能容纳大约 10 条指令和一两个状态寄存器。聪明的优化通常涉及将状态编码到指令指针或分支标志中。

他设计了一个新的 take-home，包含使用微小高度受限指令集的益智游戏，优化解决方案以获得最少的指令数。没有可视化或调试工具。Starter code 只检查解决方案是否有效。构建调试工具是测试的一部分——你可以插入精心制作的 print 语句，或者让编码模型在几分钟内生成一个交互式调试器。

关于工具投资判断是信号的一部分。

测试结果：**Claude Opus 4.5 失败了**。

Tristan 填充了更多益智游戏并让同事验证不那么了解问题的工程师仍然可以胜过 Claude。早期结果令人鼓舞：分数与申请者过去工作质量高度相关，最能干的同事得分比任何申请者都高。

> "I'm still sad to have given up the realism and varied depth of the original. But realism may be a luxury we no longer have. The original worked because it resembled real work. The replacement works because it simulates novel work."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

---

## 为什么 Zachtronics 风格的评估能 work

关键区别在于**分布外（out-of-distribution）的程度**。

第一代评估虽然包含真实工作，但也包含了大量常见的优化模式——SIMD 向量化、多核并行、内存带宽优化。这些正是 AI 训练数据中大量的内容。Claude 可以在这些领域借鉴大量的人类经验。

而 Zachtronics 风格的指令集是如此小和受限，以至于它实际上强制了一种非常规的编程方式。人类和 AI 都没有大量的直接经验。解决方案更多依赖于**对约束的创造性利用**，而不是应用已知的优化模式。

这不是说企业应该去用 Zachtronics 风格的评估。它只说明了**分布外程度**是 AI 抗性的关键维度。如果评估内容与 AI 训练数据高度重叠，AI 会胜出。如果评估内容足够新颖，AI 会遇到困难。

---

## 一个开放挑战：性能基准数据

Anthropic 在 GitHub 上发布了原始 take-home（[anthropics/original_performance_takehome](https://github.com/anthropics/original_performance_takehome)），并给出了明确的性能基准：

| 解决方案 | Cycle Count |
|---------|------------|
| Claude Opus 4，测试时计算 harness 多小时后 | 2164 |
| Claude Opus 4.5，休闲 Claude Code 会话，约匹配 2 小时最佳人类性能 | 1790 |
| Claude Opus 4.5，测试时计算 harness 2 小时 | 1579 |
| Claude Sonnet 4.5，测试时计算超过 2 小时 | 1548 |
| Claude Opus 4.5，11.5 小时 harness | 1487 |
| Claude Opus 4.5，在改进的测试时计算 harness 多小时后 | 1363 |

关键洞察：**即使使用大量测试时计算，Claude Opus 4.5 的最佳性能仍然无法匹配人类在无限时间下的最佳表现**。人类在无限时间下能够达到更低（更好）的 cycle count。

这意味着：

> "Human experts retain an advantage over current models at sufficiently long time horizons."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

这个开放挑战的本质是：**如果你能在 cycle count 上优化到 1487 以下，击败 Claude 发布时的最佳性能，请发送你的代码和简历**。

---

## 对 Agent 工程实践的启示

这个案例对 Agent 评估系统有直接启示：

### 1. 评估设计的分布外原则

如果你在构建一个评估 Agent 能力的基准，核心问题不是「题目有多难」，而是「题目与 AI 训练数据的重叠程度」。高重叠意味着 AI 可以借鉴大量人类经验；低重叠意味着 AI 必须更多地依赖推理而不是记忆。

MemoryAgentBench（ICLR 2026）的设计遵循了类似逻辑：它评估的是 Agent 的记忆能力（检索、学习、理解、选择性遗忘），这些问题本身就是分布外的——因为它们依赖于特定的 session 历史，而 AI 训练数据中没有这样的东西。

### 2. 时间约束是关键变量

从性能基准可以看出：Claude Opus 4.5 在 2 小时限制内匹配最佳人类性能，但人类在无限时间下仍然胜出。这意味着：

- **短期任务**（<2 小时）：AI 已经能在许多领域匹配或超越人类
- **长期任务**（>数小时）：人类仍然有优势

对于评估设计，这意味着时间限制是控制 AI 优势范围的关键杠杆。如果你想在评估中保留人类信号，时间限制应该足够短以至于 AI 无法完全解决问题，但又足够长以至于人类有机会展示判断力。

### 3. 工具建设能力是难以自动化的维度

在 Zachtronics 风格的评估中，构建调试工具的能力是信号的一部分。Tristan 写道：

> "Building debugging tools is part of what's being tested: you can either insert well-crafted print statements or ask a coding model to generate an interactive debugger in a few minutes. Judgment about how to invest in tooling is part of the signal."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

工具投资判断——在哪里投资调试能力，在哪里投资核心解决方案——是 AI 难以复制的维度，因为它涉及对问题的深层理解和优先级判断。

### 4. 评估与工作的范式需要对齐

最终，Tristan 放弃了原来的评估，因为它太像真实工作了。在真实工作中，AI 可以处理大部分执行工作。而新的 Zachtronics 风格评估更像是模拟**新颖的工作**——在这种情况下，人类判断力仍然不可或缺。

这不是说所有评估都应该这样做。而是说：**评估设计时需要明确目标：你要评估的是 AI 辅助下人类仍需负责的哪些维度**。

---

## 结论：评估的范式转移

当 AI 能够完整解决一个技术评估题时，评估的核心假设便已失效。Anthropic 的三轮迭代揭示了一个清晰的模式：

1. **真实工作风格评估**（v1/v2）→ 在 AI 能力增长后被击败
2. **分布外约束风格评估**（v3）→ 能够维持人类信号，但失去了真实工作的代表性

Tristan 明确指出：

> "Realism may be a luxury we no longer have."
> — [Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

对于 Agent 开发者来说，这意味着：

- 如果你在构建评估基准，问自己：AI 能在合理时间内完整解决这个问题吗？如果是，你需要重新设计
- 如果你在构建 Agent，问自己：你的工具建设判断是否足够好，能够在 AI 辅助下仍保持人类判断的独特价值？

最终，**AI 抗性的本质不是禁止 AI，而是设计一个 AI 无法完整替代人类判断的评估维度**。Anthropic 的开放挑战表明，在足够长的时间范围内，人类专家仍然保持优势——这正是 Agent 系统中「人类判断仍然不可替代」的最有力证据。

---

**一手来源**：[Anthropic Engineering: Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)（2026 年发布，Tristan Hume，Anthropic 性能优化团队负责人）