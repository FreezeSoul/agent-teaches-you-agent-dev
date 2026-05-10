# Anthropic GAN-Style 三代理架构：让 AI 编码从「能跑」到「能用」

> **核心问题**：为什么 AI 编码 Agent 在单次生成时表现不错，但面对长程任务时容易「跑偏」甚至「自我感觉良好」？Anthropic Labs 的 Prithvi Rajasekaran 在 2026 年 3 月的一篇工程博客中提出了一个 GAN 启发的三代理架构——Planner、Generator、Evaluator——将生成与评估分离，让对抗反馈驱动质量提升。本文深度解析这一架构的设计原理、工程实现和关键洞察。

---

## 背景：单代理的两大失败模式

Anthropic 在此前的「长程 Agent 高效 Harness 设计」实验中已经解决了一个核心问题：上下文焦虑（context anxiety）——当模型感觉自己接近上下文窗口上限时，会提前收尾工作而非继续任务。他们通过 Initializer Agent + Context Reset 机制绕过了这个问题。

但即便如此，更复杂的任务中 Agent 仍然会逐渐失控。Rajasekaran 识别出两个持续存在的失败模式：

### 失败模式 1：上下文坍缩

上下文窗口填充时，模型对长程任务的 coherence（连贯性）下降。这是 Transformer 架构固有的注意力预算约束——随着 token 增加，远期信息的重要性被稀释。Anthropic 之前的 Context Engineering 文章（2025年9月）详细分析了这一现象，并提出 Compaction（压缩）和 Sub-agent Architectures（多代理架构）作为解法。

### 失败模式 2：自我评估失效

> "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."
> — [Anthropic Engineering: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这是关键发现：**Agent 无法可靠地评估自己输出的质量**。即使有可验证的测试结果，Agent 仍然倾向于高估自己的工作。更严重的是，对于设计这类主观任务，根本没有二进制通过/失败的判断标准。设计上"感觉精致"还是"看起来通用"是完全主观的，但 Agent 总是给出过于宽容的评价。

---

## GAN 启发的核心洞察

### 从图像生成到代码生成

Generative Adversarial Networks（GAN）的核心机制是：两个神经网络——Generator 和 Discriminator——相互对抗。Generator 试图产生"假数据"来骗过 Discriminator，Discriminator 试图区分真实与生成。每个都在逼迫对方变得更强。这种对抗压力是 GAN 的关键：没有它，Generator 就会停止优化。

Rajasekaran 将这一思路迁移到多代理编码架构：

- **Generator**：负责生成代码/设计
- **Evaluator**：负责评估输出质量，给出结构化反馈
- **Planner**：负责将高层需求分解为可执行的规格说明

但这里有一个重要的区别：**Evaluator 不是纯粹的对抗者**。它更像是高级工程师在 code review，而不是拳击比赛的对手。它产生的是 Generator 可操作的详细反馈，而非简单的通过/失败信号。

### 为什么分离有效

单一 Agent 被要求同时承担规划、生成、评估时，会遇到「上下文污染」（context contamination）问题——任务压缩到单一 prompt 后，模型对每个任务的注意力都会下降。

更根本的问题是**认知偏见**：

> "Authors miss errors in their own writing that a fresh reader catches immediately. In language models, the effect is even more pronounced because the model's generation process is partly autocomplete: it continues patterns, which makes it likely to reproduce the same reasoning error in both the generation and evaluation steps."
> — [MindStudio: The Planner-Generator-Evaluator Pattern](https://www.mindstudio.ai/blog/planner-generator-evaluator-pattern-gan-inspired-ai-coding/)

Agent 生成代码时，部分过程是自动补全——模型延续既有模式。这意味着它很可能在评估时也重复同样的推理错误，而不是发现它们。分离确保 Evaluator 以「新人视角」看代码，因为它根本没有参与生成过程。

---

## 工程实现：Frontend Design 实验

### 让主观质量变得可评分

在设计领域建立可评分标准是第一步。Rajasekaran 定义了四个评估维度：

| 维度 | 问题 | Claude 默认表现 |
|------|------|---------------|
| **Design Quality** | 设计是否像整体而非零件拼凑？ | 通常不佳，容易产出碎片化结果 |
| **Originality** | 有无自定义决策痕迹，还是模板化？ | 容易生成「AI slop」模式（紫色渐变+白卡等） |
| **Craft** | 技术执行：排版层级、间距一致性、色彩和谐、对比度 | 默认表现良好，失败意味着基础功有问题 |
| **Functionality** | 可用性：用户能否理解界面、找到主操作、完成任务 | 默认表现良好 |

关键是：**设计质量和原创性是最需要干预的维度**。Claude 默认就能做好技术能力和可用性，但在设计品味上容易走安全路线——产出功能完整但视觉平庸的结果。

评估标准明确penalized「AI slop」模式，并通过权重设置推模型去冒险：

> "Including phrases like 'the best designs are museum quality' pushed designs toward a particular visual convergence, suggesting that the prompting associated with the criteria directly shaped the character of the output."

标准中的措辞会直接影响输出风格——这是 Prompt Engineering 的深层应用。

### 迭代反馈循环

评估不是一次性事件，而是一个循环过程：

```
Generator → 创建 HTML/CSS/JS 前端
    ↓
Evaluator → 使用 Playwright MCP 导航页面、截图、研究实现
    ↓
Evaluator → 对每个维度打分 + 写详细批评
    ↓
Generator → 根据反馈迭代（5-15 次循环）
```

关键设计：**Evaluator 主动操作实时页面，而不是评分静态截图**。这让它能发现只有在交互时才暴露的问题。完整运行可能长达 4 小时。

另一个策略性指令：Generator 在每次评估后要做战略决策——如果分数趋势良好就继续当前方向，如果方法不行就彻底转向不同美学。

### 一个惊人的设计迭代案例

在为一个虚构的荷兰艺术博物馆设计网站时：

- **第9次迭代**：产出干净、深色主题的着陆页，符合预期但没有惊喜
- **第10次迭代**：Generator 彻底推翻之前方向，将网站重新想象为「空间体验」——用 CSS perspective 渲染的 3D 房间、棋盘格地板、画廊墙上自由放置的艺术品、用门口导航代替滚动或点击

> "It was the kind of creative leap that I hadn't seen before from a single-pass generation."

这正是 GAN 风格反馈循环的威力：持续的外部压力逼迫 Generator 走出局部最优，去寻找真正创新的解决方案。

---

## 扩展到全栈开发

### 架构设计

将 GAN 风格模式应用到完整应用开发时，三个代理各司其职：

**Planner Agent**：
- 将 1-4 句简单需求扩展为完整产品规格说明
- 被要求保持野心，聚焦产品上下文和高层技术设计
- **不做细节实现规范**：因为如果规划阶段有错误，会级联到下游实现。让代理控制交付物而非路径，让他们自己找到路径
- 主动将 AI 功能编织进产品规格

**Generator Agent**：
- 一次处理一个功能，敏捷式工作（Sprint）
- 每完成一个 Sprint 后自我评估，然后交给 QA
- 配备 Git 版本控制

**Evaluator Agent**：
- 使用 Playwright MCP 点击运行中的应用，测试 UI 特性、API 端点、数据库状态
- 对每个 Sprint 的 bug 和标准（产品深度、功能性、视觉设计、代码质量）进行评分
- **每个标准都有硬阈值**：任何一项低于阈值，Sprint 失败，Generator 获得详细反馈

### Sprint Contract：连接规格和可测试实现

关键的桥接机制：**Sprint Contract**。Generator 和 Evaluator 在每个 Sprint 开始前协商「完成标准」——具体实现细节和验证方式。

流程：
1. Generator 提出它将构建什么、如何验证成功
2. Evaluator 审查提案，确保 Generator 在构建正确的东西
3. 两者迭代直到达成一致
4. Generator 按合同构建，完成后交给 QA

这填补了产品规格（高层次、意图驱动）和可测试实现之间的空白。

### 与之前架构的对比

| 特性 | 之前的长程 Harness | 新架构 |
|------|-----------------|--------|
| 初始化 | Initializer Agent 分解规格为任务列表 | Planner Agent 自动化规格扩展 |
| 上下文管理 | 需要 Context Reset（Sonnet 4.5 的 context anxiety）| Opus 4.5 基本消除 context anxiety，无需 reset |
| Agent 数量 | 2（Initializer + Coding） | 3（Planner + Generator + Evaluator） |
| 评估方式 | 无专门评估 | GAN 风格的分离 Evaluator |
| 迭代控制 | 无 | Sprint Contract 定义具体完成标准 |

---

## 真实对比数据

这是最具说服力的实验结果：

| Harness 类型 | 时长 | 成本 |
|------------|------|------|
| Solo Agent | 20 min | $9 |
| **Full GAN Harness** | 6 hr | $200 |

**GAN Harness 比单代理贵 20 倍以上**——但输出质量立即可见的差异。

Solo 运行时的问题：
- 面板固定高度浪费空间，大部分视口空置
- 工作流僵硬，没有引导用户先创建 sprites 和 entities
- 游戏本身损坏——实体出现在屏幕上但没有响应输入
- 代码中实体定义和游戏运行时的连接断裂

Full Harness 的表现：
- 面板合理利用全视口，界面有一致视觉身份
- Sprite 编辑器更丰富——更干净的调色板、更好的颜色选择器、更可用的缩放控制
- **Play Mode 真的能玩**——物理有粗糙边缘但核心机制有效，单代理版本完全做不到
- 内置 Claude 集成，可以通过 prompt 生成游戏各部分

> "The harness was over 20x more expensive, but the difference in output quality was immediately apparent."

---

## 工程判断：什么时候值得 GAN Harness？

### 成本/收益权衡

6 小时 $200 对比 20 分钟 $9——这是巨大的成本差异。GAN Harness 不是银弹，它适用于：

**值得的场景**：
- 高质量要求、长程任务、复杂系统
- 主观质量（设计品味）无法通过简单测试验证
- 关键系统，需要确保每个 Sprint 达标

**不值得的场景**：
- 快速原型、一次性脚本
- 明确可自动化测试的功能
- 低风险、非生产环境

### 何时单代理足够

Claude Opus 4.5 消除 context anxiety 后，许多场景下单代理已经够用。但对于主观质量和长程复杂任务，GAN 结构提供了单代理无法提供的质量保证机制。

### 关键工程经验

**标准措辞影响输出风格**：包含「museum quality」这样的短语会推动设计向特定视觉收敛。这意味着评估标准本身是一种 Prompt Engineering 工具。

**迭代不总是线性**：分数通常在迭代中改善，但作者经常发现自己更喜欢中间迭代而非最后一次。实现复杂性倾向于随轮次增加。

**第一轮输出已显著改善**：即使没有任何反馈，第一轮输出已经明显优于无任何 prompt engineering 的基线——说明标准和相关语言本身就已经引导模型远离通用默认值。

---

## 架构关联：它在 Agent 演进路径中的位置

| Agent 演进阶段 | 关键能力 | 本架构的对应 |
|---------------|---------|------------|
| Single Agent | 上下文管理、长程记忆 | Context Reset → Opus 4.5 自动压缩 |
| Multi-Agent | 角色分离、协作协调 | Planner/Generator/Evaluator 职责分离 |
| Harness Engineering | 环境设计、质量保证 | GAN 风格反馈循环、Sprint Contract |

这不是某个阶段的替代，而是**每个演进层级都沉淀了新的工程能力**。从单代理到 GAN Harness，反映了 Agent 工程从「让模型自己做到」向「通过架构约束推动质量」的范式转移。

---

## 结论

Anthropic 的 GAN 风格三代理架构揭示了一个核心原理：**生成和评估必须分离**。单一 Agent 无法可靠评估自己的输出——无论是主观的设计质量还是客观的代码正确性。通过引入独立的 Evaluator，建立了对抗反馈循环，逼迫 Generator 持续改进而非自我满足。

但这不是免费的——它带来 20 倍的成本增加和 18 倍的时间延长。工程决策需要评估任务的复杂性、质量要求和资源约束。

对于需要高质量、长程自主编码的场景，这个架构提供了一个可工程化的质量保证机制。标准的设计、迭代的反馈循环、清晰的完成定义——这些是将 AI 编码从「能跑」提升到「能用」的关键工程杠杆。

---

**一手来源**：
- [Anthropic Engineering: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（2026年3月）
- [MindStudio: The Planner-Generator-Evaluator Pattern](https://www.mindstudio.ai/blog/planner-generator-evaluator-pattern-gan-inspired-ai-coding/)
- [FreeCodeCamp: How to Apply GAN Architecture to Multi-Agent Code Generation](https://www.freecodecamp.org/news/how-to-apply-gan-architecture-to-multi-agent-code-generation/)