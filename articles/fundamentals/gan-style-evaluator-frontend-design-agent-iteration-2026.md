# GAN 风格评估器：如何让 AI 生成不可预测的创意设计

**发布于**：2026-05-12 | **演进阶段**：Stage 4 · Paradigms | **分类**：fundamentals/

## 开篇

> **核心问题**：当 AI 生成的内容没有标准答案时（如「什么是好的设计」），如何建立有效的质量反馈机制，让 AI 不只是自我美化地评价自己的工作？
>
> **核心结论**：Anthropic 的实验证明，将 GAN（生成对抗网络）的核心思想引入 Agent 架构——**分离生成器和独立评估器**——可以有效解决 Agent 的「自我评价过于宽容」问题。评估器通过明确的、编码了设计原则的评分标准，对生成器的输出进行结构化打分，而生成器则依据反馈进行迭代优化。这种「生成-评估-迭代」的循环推动了设计的持续进化，最终产生了真正令人惊喜的创意输出。

---

## 1. 背景：AI 在主观任务上的自我评价失真

在构建长程 Agent 的过程中，Anthropic 团队遇到了一个棘手的问题：**当要求 Agent 评估自己生成的工作时，Agent 倾向于自信地赞扬，而非客观地批评**。

这个问题在代码领域有二进制检查（测试通过/失败）作为锚定，但在设计领域，答案更加主观：「这个布局是否精致」「这个色彩是否协调」「整体是否有个性」——这些都是主观判断，而 Agent 在这些判断上系统性地表现出了「宽容偏差」。

> "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."
> — [Anthropic Engineering: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

### 1.1 宽容偏差的根源

为什么 Agent 会过度宽容自己的输出？Anthropic 团队认为有两个主要原因：

**第一，模型本身的训练目标并非「批评」**。LLM 在预训练和微调中接收的反馈信号主要来自人类对齐过程，而人类对齐通常奖励「有帮助」和「积极正面」的回应，而非「严格批判」。

**第二，Agent 对自己的工作有「认知承诺」**。一旦生成了某个输出，Agent 会在后续推理中无意识地倾向于维护这个输出的合理性，而非指出其缺陷。这与心理学中的「承诺升级」效应类似。

### 1.2 从 GAN 获得灵感

生成对抗网络（GAN）的核心思想是两个网络的对抗：生成器 G 产生假样本，判别器 D 区分真实样本和生成样本。通过对抗训练，G 的输出质量不断提升。

Anthropic 团队将这个思想迁移到了 Agent 架构设计：**用独立的评估器 Agent 代替 GAN 中的判别器，用生成器 Agent 代替 GAN 中的生成器**。关键改变在于：

- 生成器和评估器是**完全独立的 Agent 实例**
- 评估器有**明确的评分标准**，而非主观的「感觉」
- 评估结果作为**可操作的反馈**返回给生成器

---

## 2. 评估器的设计：让主观标准变得可操作

### 2.1 四条评分标准的工程化

在尝试用 Agent 评估前端设计时，Anthropic 团队发现直接问「这个设计好不好」是无效的——Agent 总是回答「很好」。但当将问题分解为**具体的、可观察的标准**时，评价变得可靠得多。

他们定义了四条评分标准：

| 标准 | 问题 | 权重 |
|------|------|------|
| **设计质量（Design Quality）** | 设计是否像一个有机整体，而非零件的堆砌？颜色、排版、布局、图像等细节是否共同创造了统一的 mood 和 identity？ | 高 |
| **原创性（Originality）** | 是否有定制化决策的证据，还是使用的是模板布局、库默认值和 AI 生成图案？人类设计师能否识别出有意识的创作选择？ | 高 |
| **工艺（Craft）** | 技术执行质量：排版层次、间距一致性、色彩和谐、对比度。这是对能力的检查，而非对创造力的检查 | 中 |
| **功能性（Functionality）** | 独立于美学的可用性。用户能否理解界面做什么、找到主要操作、在不猜测的情况下完成任务？ | 中 |

> "Is this design beautiful? Is hard to answer consistently, but 'does this follow our principles for good design?' gives Claude something concrete to grade against."

注意设计质量和原创性被赋予了**更高权重**，而 Claude 默认表现良好的工艺和功能性权重较低。这个权重分配是刻意的——Anthropic 团队希望推动模型在设计质量和原创性上冒险，而非在已经擅长的技术上继续堆砌。

### 2.2 Few-shot 校准评估器

仅仅给出评分标准是不够的。Anthropic 团队还使用了 **few-shot 示例** 来校准评估器的判断：

```python
# 评估示例（部分）
设计A：「一个带有渐变紫色背景和白色卡片的标准 AI 生成布局」
评分：Design Quality 2/5, Originality 1/5, Craft 4/5, Functionality 4/5
理由：「遵循模板默认值，无独特视觉 identity，原创性极低」

设计B：「一个带有手绘风格插图和不对称网格的杂志风 landing page」
评分：Design Quality 4/5, Originality 5/5, Craft 3/5, Functionality 3/5
理由：「有明确的设计语言和创意选择，但工艺细节有瑕疵」
```

这种 few-shot 校准有两个作用：

1. **减少分数漂移**：确保评估器在不同迭代之间的判断标准一致
2. **对齐人类偏好**：让评估器的判断更接近 Anthropic 团队的真实审美标准

> "I calibrated the evaluator using few-shot examples with detailed score breakdowns. This ensured the evaluator's judgment aligned with my preferences, and reduced score drift across iterations."

---

## 3. 生成器-评估器循环的运行机制

### 3.1 循环结构

完整的 GAN 风格 Agent 循环包含以下步骤：

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 生成器 Agent 基于用户 Prompt 创建初始设计方案            │
│    ↓                                                       │
│ 2. 评估器 Agent 获得 Playwright MCP 工具，可与设计交互      │
│    （点击、截图、导航）                                     │
│    ↓                                                       │
│ 3. 评估器在真实浏览器环境中检查实现，再对每个标准打分      │
│    ↓                                                       │
│ 4. 评估器写出详细批评，指出具体问题                        │
│    ↓                                                       │
│ 5. 反馈传回生成器                                          │
│    ↓                                                       │
│ 6. 生成器根据反馈决定：继续优化当前方向 or 转向新方向       │
│    ↓                                                       │
│ 7. 回到步骤 2，直到评分达标或达到迭代上限（5-15次）        │
└─────────────────────────────────────────────────────────────┘
```

关键细节：**评估器不是评分静态截图，而是在真实浏览器环境中与页面交互后再评分**。这意味着评估器可以看到动态效果、hover 状态、响应式布局等实际表现。

### 3.2 战略决策点：坚持还是转向

生成器在每次评估后被要求做出**战略决策**，而非机械地按照反馈修复：

- 如果分数趋势良好，**继续深化当前方向**
- 如果方向不奏效，**彻底转向全新的美学方向**

> "I also instructed the generator to make a strategic decision after each evaluation: refine the current direction if scores were trending well, or pivot to an entirely different aesthetic if the approach wasn't working."

这个设计是为了避免「局部最优陷阱」——如果一个设计方向只能带来渐进改进，生成器应该有意识地切换到完全不同的方向，尝试全新的解决方案。

### 3.3 迭代轨迹的不可预测性

GAN 风格循环产生的一个有趣结果是**迭代轨迹的不可预测性**。Anthropic 团队观察到的典型模式**不是线性改进**，而是包含跳跃和转向的复杂轨迹：

- 迭代之间可能出现**分数下降**（当生成器探索新方向时）
- 设计可能在某个中间迭代达到最优，而非最后一次迭代
- 最令人惊喜的输出往往来自**方向的突然转变**

> "Later implementations tended to be better as a whole, but I regularly saw cases where I preferred a middle iteration over the last one."

---

## 4. 实验结果：从「安全输出」到「创意突破」

### 4.1 基线表现

在没有任何干预的情况下，Claude 默认生成的前端设计倾向于「安全、模板化」的输出——技术上功能正常，但视觉上毫无特色。Anthropic 团队特别指出了典型的 AI 生成设计特征：

> "Unmodified stock components—or telltale signs of AI generation like purple gradients over white cards—fail here."

换句话说，没有引导的 Agent 会产出「一眼就能认出来是 AI 生成的」设计。

### 4.2 GAN 风格循环的效果

通过 GAN 风格评估循环，生成的设计在以下维度显著改善：

| 维度 | 改善表现 |
|------|---------|
| 设计质量 | 产生了真正的视觉 identity，而非零件堆砌 |
| 原创性 | 减少了模板依赖，出现了有意图的创作决策 |
| 迭代后期的突变 | 在某个迭代点上突然产生「创意跳跃」，放弃当前方向进入全新方向 |

### 4.3 一个令人惊喜的案例：荷兰艺术博物馆网站

在一个典型案例中，Anthropic 团队让 Agent 设计一个荷兰艺术博物馆的网站。

**第 1-9 次迭代**：产生了预期的 dark-themed landing page，视觉上精致但符合预期。

**第 10 次迭代**：生成器决定彻底放弃之前的方向，完全重构了整个设计方案——变成了一个**空间体验**：3D room with CSS perspective rendering、画作以自由形式挂在墙上、门框式导航替代了传统的滚动/点击导航。

> "It was the kind of creative leap that I hadn't seen before from a single-pass generation."

这正是 GAN 风格评估的价值所在：生成器在前 9 次迭代中积累了对「好设计」的理解，然后在评估器的推动下，产生了在单一生成中永远不会出现的**创意突破**。

---

## 5. 标准措辞对输出的隐性影响

### 5.1 意外发现：评分标准的语言本身塑造了输出

Anthropic 团队发现了一个微妙但重要的现象：**评分标准的措辞会直接影响生成器的行为**，而这种影响有时候超出预期。

> "The wording of the criteria steered the generator in ways I didn't fully anticipate. Including phrases like 'the best designs are museum quality' pushed designs toward a particular visual convergence."

这意味着评分标准不只是一个「判断工具」，也是一个「引导工具」。标准的语言会在生成器的决策过程中被内化，从而影响生成方向的选择。

### 5.2 工程启示：评分语言是 Harness 的一部分

这个发现对 Agent 设计有重要启示：**Harness 中的每一个组件——包括看似中立的评分标准——都会影响 Agent 的行为**。当设计评分标准时，开发者实际上是在用语言编码偏好，而这些偏好会以非预期的方式影响最终输出。

---

## 6. 从前端设计到全栈开发：GAN 风格的泛化

### 6.1 三 Agent 架构的最终设计

将 GAN 风格评估应用到全栈开发时，Anthropic 团队设计了完整的三 Agent 系统：

| Agent | 职责 | 与 GAN 类比 |
|------|------|------------|
| **Planner** | 将简单 prompt 扩展为完整 product spec | —（新增）|
| **Generator** | 每次一个 feature 地实现，sprint 模式 | GAN 生成器 |
| **Evaluator** | 用 Playwright 测试运行中的应用，检查功能和设计 | GAN 判别器 |

### 6.2 架构的关键洞察

**第一，Context Reset 不再必要**：之前的 long-running harness 需要 context reset 来对抗「context anxiety」问题（模型在接近 context limit 时会过早收尾）。但在这个新架构中，Opus 4.5 本身已经解决了这个问题，所以可以使用连续的 Agent session，配合 Claude Agent SDK 的自动 compaction。

**第二，评估器的阈值机制**：每个评分标准都有硬阈值，如果任何一项低于阈值，sprint 就标记为失败，生成器收到详细反馈后重试。这确保了质量底线。

**第三，Planner 的克制**：Planner 被指示「保持野心但关注产品上下文和高层次技术设计，而非详细的技术实现」。这是为了避免「过度规划导致的错误级联」——如果 Planner 在早期就指定了错误的技术路径，这个错误会级联到整个实现过程。

---

## 7. 工程实践检查清单

如果你计划将 GAN 风格评估应用于自己的 Agent 项目，以下是 Anthropic 团队的经验总结：

### 7.1 评估器设计

- [ ] 将模糊的「质量」概念分解为**具体的、可观察的标准**
- [ ] 为每个标准分配与你的目标一致的权重（不要平均分配）
- [ ] 使用 few-shot 示例校准评估器，减少判断漂移
- [ ] 给评估器提供**真实环境交互能力**（如 Playwright MCP），而非只给静态截图

### 7.2 生成器设计

- [ ] 在每次迭代后要求生成器做出**战略决策**（坚持 vs 转向）
- [ ] 允许方向彻底转变，而非只是渐进式改进
- [ ] 考虑设置迭代上限（5-15 次），避免无限循环

### 7.3 标准措辞

- [ ] 意识到评分标准的语言会**隐性塑造生成器的行为**
- [ ] 在部署前测试标准措辞的效果
- [ ] 「museum quality」这类短语会推动设计向特定方向收敛

### 7.4 阈值设计

- [ ] 为每个标准设置**硬阈值**，低于阈值的输出必须重做
- [ ] 阈值应该是可量化的，而非「感觉还行」
- [ ] 确保阈值设置不会过于严苛导致无限重试

---

## 结语

GAN 风格评估器解决了 Agent 系统中的一个根本性问题：当没有客观标准时，Agent 如何避免自我宽容，建立有效的质量反馈？

答案在于**分离原则**——让评价者与执行者独立存在，用明确的、编码了设计原则的标准替代模糊的「质量判断」，用可量化的阈值替代「感觉」。这不是消除主观性，而是**将主观偏好结构化**——让它可以被评估、迭代和优化。

这个原则的适用范围不限于前端设计。任何涉及主观判断的 Agent 任务——文案撰写、架构设计、用户体验评审——都可以从 GAN 风格的生成器-评估器分离中受益。

---

## 关联阅读

- [Anthropic Engineering: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) — 另一个并行多 Agent 协调实验
- [Cursor: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) — 另一个多维质量测量体系
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Long-running Agent 的 Harness 设计基础