# GAN 启发的三代理架构：Harness 设计的范式突破

## 核心论点

Anthropic 在「Harness design for long-running application development」中提出了一个关键洞察：Agent 的自我评价（self-evaluation）是一个根本性缺陷，而解决方案是将「干活」和「评判」彻底分离为两个独立 Agent，形成 Generator-Evaluator 的对抗式架构。这一设计借鉴自生成对抗网络（GAN）的核心思想，在 Agent 领域开创了一个新的范式。

---

## 1. 为什么传统的单 Agent 架构必然失败

### 1.1 两种典型的失败模式

Anthropic 在早期实验中观察到，使用单个 Agent 执行复杂长周期任务时，存在两种系统性的失败模式：

**失败模式一：过度自信的自我评价**

> "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这是一个根本性的问题。Agent 在执行任务时会对自己生成的内容产生「所有权偏好」，导致评估时系统性地给出过高评价。这种现象在主观任务（如设计）中最明显，但在有明确验收标准的客观任务中同样存在。

**失败模式二：上下文焦虑与过早终止**

> "Some models also exhibit 'context anxiety,' in which they begin wrapping up work prematurely as they approach what they believe is their context limit."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

当 Agent 感觉到上下文窗口即将耗尽时，会倾向于提前宣布任务完成，而不是继续追求更好的结果。这导致输出质量的系统性衰减。

### 1.2 传统解决方案的局限

此前 Anthropic 提出的「Initializer Agent + Coding Agent」两组件架构（参见「Effective harnesses for long-running agents」）解决了「任务分解」和「跨会话状态传递」的问题，但仍然没有解决「自我评价失真」这个根本性缺陷。

 compaction（压缩）可以缓解上下文焦虑，但：

> "While compaction preserves continuity, it doesn't give the agent a clean slate, which means context anxiety can still persist."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

Compaction 本质上是在同一个 Agent 的连续性（continuity）和清晰度（clean slate）之间的妥协。当 Agent 意识到自己在被压缩时，上下文焦虑仍然会发生。

---

## 2. 核心设计：三代理架构

### 2.1 Generator-Evaluator 的 GAN 逻辑

Anthropic 从生成对抗网络（GAN）中汲取灵感，设计了一个三代理系统：

| Agent | 角色 | 职责 |
|-------|------|------|
| **Planner** | 任务规划者 | 将用户的高层需求扩展为完整的产品规格说明书（Product Spec） |
| **Generator** | 代码生成者 | 按 Feature 逐个实现，每次实现后自我评估，然后交 QA |
| **Evaluator** | 质量评审者 | 使用 Playwright MCP 访问真实运行的应用，逐项评分并给出详细反馈 |

GAN 的核心思想是：让两个神经网络互相对抗，一个生成（Generator），一个判别（Discriminator），在对抗中共同进化。这里的 Evaluator 扮演了 Discriminator 的角色，而 Generator 则在Evaluator 的反馈下持续改进。

关键区别在于：

> "Separating the agent doing the work from the agent judging it proves to be a strong lever to address this issue."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

分离本身并不能完全消除 Evaluator 对 LLM 生成内容的宽容倾向，但「调优一个独立的 Evaluator 使其持怀疑态度」比「让 Generator 对自己的工作保持批判」要容易得多。一旦外部反馈存在，Generator 就有了一个具体的改进目标。

### 2.2 Planner 的设计哲学

Planner 接收用户一句话级别的需求，输出完整的产品规格说明书。这个设计背后有一个关键洞察：

> "If the planner tried to specify granular technical details upfront and got something wrong, the errors in the spec would cascade into the downstream implementation."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

Planner 应该关注「产品是什么」而不是「技术怎么实现」。让各个 Agent 在执行过程中自己决定技术路径，而不是从顶层规格中推导。约束的是产出物（Deliverables），而不是实现路径。

这种设计将「规格错误」的修复成本降到了最低：Generator 发现技术路径走不通时，可以直接调整实现方式，而不必去修改规格。

### 2.3 Generator 的增量实现策略

Generator 使用「冲刺（Sprint）」模式工作：

1. 从 Product Spec 中选择一个 Feature
2. 实现它
3. 自我评估
4. 提交给 Evaluator

> "I applied a similar model here, instructing the generator to work in sprints, picking up one feature at a time from the spec."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

与早期「Initializer Agent」方案不同，这里的 Generator 是连续Session而非多Session重启的。Opus 4.5 本身已经去除了上下文焦虑问题，因此不需要上下文重置机制。Agent SDK 的自动 compaction 负责处理上下文增长。

### 2.4 Evaluator 的四维评分体系

Evaluator 使用 Playwright MCP 访问真实运行的应用（而非静态代码审查），按四个维度评分：

| 维度 | 含义 | 权重 |
|------|------|------|
| **Design Quality** | 设计是否作为一个整体而非碎片集合？颜色、字体、布局、图像是否形成了独特的调性？ | 高 |
| **Originality** | 是否有自定义决策的证据，还是模板布局/library 默认/AI 生成图案？ | 高 |
| **Craft** | 技术实现：字体层级、间距一致性、颜色和谐度、对比度 | 中 |
| **Functionality** | 可用性：用户能否理解界面在做什么、找到主要操作、完成基本任务？ | 中 |

有趣的是，Anthropic 明确将「AI slop」Patterns 作为 Originality 的惩罚项：

> "Unmodified stock components—or telltale signs of AI generation like purple gradients over white cards—fail here."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

Design Quality 和 Originality 的权重高于 Craft 和 Functionality，因为 Claude 在后两者上本来就是强项（前两个维度容易滑向平庸）。

---

## 3. 迭代过程中的关键发现

### 3.1 迭代模式的非线性特征

评估迭代通常会改善结果，但改善的模式不是线性的：

> "Later implementations tended to be better as a whole, but I regularly saw cases where I preferred a middle iteration over the last one."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这与 GAN 训练中的模式类似：对抗性训练可能导致.generator 过度拟合判别器的偏好，导致某些「中间解」反而更符合人类审美。实现复杂性会随着轮次增加，Generator 会根据 Evaluator 的反馈尝试更激进的方案。

### 3.2 提示词措辞对输出的强烈影响

> "The wording of the criteria steered the generator in ways I didn't fully anticipate. Including phrases like 'the best designs are museum quality' pushed designs toward a particular visual convergence."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这个发现对 Harness 设计有重要启示：评分标准的措辞会直接影响 Generator 的行为方向。Harness 设计者不能只关注评分维度的定义，还要关注每条标准中的措辞暗示。

### 3.3 创意跳跃：第十次迭代的突变

在一个案例中，第九次迭代产生了一个「dark-themed landing page for a fictional museum」，在第十次迭代时：

> "It scrapped the approach entirely and reimagined the site as a spatial experience: a 3D room with a checkered floor rendered in CSS perspective, artwork hung on the walls in free-form positions, and doorway-based navigation between gallery rooms instead of scroll or click."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这是单一提示无法产生的创意跳跃。Generator 在多轮反馈后完成了「范式转换」，这正是 GAN 式迭代的价值所在。

---

## 4. 向全栈开发的泛化

### 4.1 三代理到 SDLC 的自然映射

将 GAN 模式泛化到全栈开发时，Generator-Evaluator 循环与软件开发生命周期（SDLC）有着自然的结构对应：

| GAN 领域 | SDLC 领域 | 对应关系 |
|----------|-----------|----------|
| Generator | 开发者 | 写代码 |
| Discriminator | Code Review / QA | 评审代码 |
| 迭代训练 | Sprint 循环 | 持续改进 |

这意味着 GAN 启发的架构不是一个特例，而是一种通用模式——任何有明确验收标准的任务都可以用「生成-评审」的二元结构来改进。

### 4.2 Evaluator 的双重职责

Evaluator 在全栈开发中有两个职责：

1. **Bug 检测**：使用 Playwright MCP 遍历应用，识别 UI 缺陷、API 问题、数据库状态错误
2. **设计质量评审**：按四个维度（Product Depth / Functionality / Visual Design / Code Quality）评分

每个维度都有硬阈值（Hard Threshold）。如果任何一项低于阈值：

> "the sprint failed and the generator got detailed feedback on what went wrong."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这是一个明确的退出条件——Generator 必须修复问题才能继续，而不是绕过问题继续前进。

---

## 5. 与之前 Harness 设计的对比

| 维度 | 早期方案（Initializer+Coding） | GAN 三代理方案 |
|------|-------------------------------|----------------|
| **Agent 数量** | 2 | 3（Planner 额外加入）|
| **评价机制** | Feature List JSON 的 passes 字段 | Evaluator Agent 主动评分 |
| **上下文管理** | 显式 Session 重置（Opus 4.5 消除了需求）| 连续 Session + 自动 compaction |
| **自我评价问题** | 通过 JSON 结构化约束间接缓解 | 通过分离彻底解决 |
| **适用场景** | 复杂长周期任务 | 主观质量敏感场景（设计）+ 客观验收场景（全栈）|

> "Opus 4.5 largely removed that behavior on its own, so I was able to drop context resets from this harness entirely."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

上下文焦虑是模型特定的问题，Opus 4.5 已经从根本上消除，因此三代理架构不需要 Session 重置机制。

---

## 6. 工程实践要点

### 6.1 Evaluator 调优的关键技术

Few-shot examples 是调优 Evaluator 的核心技术：

> "I calibrated the evaluator using few-shot examples with detailed score breakdowns. This ensured the evaluator's judgment aligned with my preferences, and reduced score drift across iterations."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

提供详细评分分解的 Few-shot Examples 是让 Evaluator 产生一致判断的关键。这与 RLHF 中的人类反馈具有类似作用。

### 6.2 Playwright MCP 是 Evaluator 的必备能力

静态代码审查无法发现运行时问题：

> "Applications from earlier harnesses often looked impressive but still had real bugs when you actually tried to use them."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

Evaluator 必须能够「像用户一样」操作应用，而不仅仅是读取代码。Playwright MCP 提供了这个能力，使 Evaluator 能够：
- 点击 UI 元素验证功能
- 验证 API 端点响应
- 检查数据库状态

### 6.3 设计标准中的反模式约束

Originality 维度对「AI slop」的惩罚不是模糊的审美偏好，而是具体的反模式约束：

```json
{
  "originality": {
    "pass": "Evidence of custom decisions, deliberate creative choices",
    "fail": "Unmodified stock components, purple gradients over white cards, 
             other telltale signs of AI generation"
  }
}
```

这种具体的反模式定义比「设计要原创」这类抽象要求更有效，因为它提供了明确的失败信号。

---

## 7. 未解决的研究问题

Anthropic 明确指出了仍然开放的问题：

> "Most notably, it's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

当前实验使用相同的 Agent 代码（Agent SDK）实例化三个角色，只在 System Prompt 上有所区分。是否应该让 Specialized Agents（如专门的 Testing Agent、QA Agent、Code Cleanup Agent）来处理 SDLC 的子任务？

此外，GAN 三代理模式目前针对全栈 Web 开发进行了优化。能否泛化到其他领域（如科研、金融建模等长周期 Agent 任务）仍是开放问题。

---

## 8. 核心启示

**Generator-Evaluator 分离是解决 Agent 自我评价失真的根本方案。** 无论是 GAN 启发的对抗训练，还是 SDLC 中的 Code Review 本质上都利用了同一个洞察：独立的评审者比自我评审更可靠。

**评分标准的措辞会直接影响生成质量。** Harness 设计者需要同时关注评分维度的定义和每个维度中措辞的方向性影响。

**Evaluator 必须是主动交互式的，而非被动读取代码。** 静态代码审查无法发现真实的可用性问题，Playwright 式的运行时验证是 Evaluator 的必备能力。

> 本文是「Anthropic Agent Engineering」系列的第九篇，覆盖「Harness Design」主题下的三代理架构创新点。