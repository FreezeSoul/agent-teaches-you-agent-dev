# 重新理解 Agent 评测：为什么你的基准测试结果可能是假的

> 本文揭示了一个在 Agent 评测领域长期被忽视的问题：基础设施配置本身就能造成高达 6 个百分点的分数差异——这个差距经常超过排行榜上头部模型之间的实际差距。

---

## 核心主张

**Anthropic 的最新工程研究证明了一个反直觉的事实：在 Agent 编程评测中，资源分配不是中性的。** 当两个 Agent 运行环境不同（即便使用完全相同的模型），它们的评测分数可能相差 6 个百分点。这个发现对整个 Agent 评测范式提出了根本性质疑：如果连"SWE-bench 分数"都不能真实反映模型能力，那什么才能？

> "Two agents with different resource budgets and time limits aren't taking the same test."
> — [Anthropic Engineering: Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)

---

## 问题的本质：静态评测与动态评测的根本差异

传统的静态评测（如 MMLU、HendrycksMath）中，模型输出是直接产物，运行环境不影响评分结果。但 **Agentic Coding Evals**（如 SWE-bench、Terminal-Bench）完全不同：模型被赋予完整的环境，在其中编写程序、运行测试、安装依赖、多轮迭代。运行时不再是"被动容器"，而是"问题解决过程的内在组成部分"。

这就引入了一个根本性差异：**运行环境成了自变量，而不只是无关背景变量。**

```
静态评测：model_output = f(model, prompt)
         runtime_environment = 不相关

Agentic 评测：success = f(model, harness, environment, resources)
         runtime_environment = 自变量
```

---

## Anthropic 的量化实验：6 个百分点的真相

Anthropic 在 Terminal-Bench 2.0 上的实验设计堪称范本：

### 实验设置
- **基准**：Terminal-Bench 2.0，6 种资源配配置，从严格 enforce（1x，即资源规格同时作为 floor 和 ceiling）到完全 unlimited
- **控制变量**：相同模型、相同 harness、相同任务集
- **测量**：成功率 + 基础设施错误率

### 关键数据

| 配置 | 基础设施错误率 | 成功率变化 |
|------|--------------|-----------|
| 1x 严格 enforce | 5.8% | 基准 |
| 2x | ~3.5% | 边际噪声内 |
| 3x | 2.1% (p < 0.001) | 边际噪声内 |
| unlimited | 0.5% | +6 百分点 (p < 0.01) |

**核心发现**：
- 在 1x→3x 区间，额外资源主要解决的是**基础设施可靠性问题**（瞬态资源峰值），而非让任务变得更简单
- 超过 3x 后，趋势反转：成功率开始超过基础设施错误率的下降幅度。这意味着额外资源开始**主动帮助 Agent 解决原本无法解决的问题**
- 到了 unlimited 阶段，总提升是 +6 个百分点

> "At uncapped resources, the total lift over 1x is +6 percentage points (p < 0.01)."
> — [Anthropic Engineering: Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)

---

## 这为什么是个严重问题

### 问题一：排行榜差距可能是基础设施差距

排行榜上头部模型之间往往只差几个百分点。但 Anthropic 的数据表明，**基础设施配置本身就能产生同量级的差异**。这意味着：

- 模型 A 领先模型 B 2 个百分点 → 可能是真实能力差距，也可能是 A 的评测环境更宽松
- **你无法从分数本身判断这是能力差异还是基础设施差异**

> "Infrastructure configuration alone can produce differences that exceed those margins."
> — [Anthropic Engineering: Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)

### 问题二：不同资源策略实际上在测试不同的能力

这是更深刻的发现。Anthropic 指出了资源限制与评测内容之间的交互效应：

**严格资源限制**无意中奖励了"极度高效的策略"：
- Agent 被迫写精简、内存友好的代码
- 在安装阶段就因 OOM 失败，没有机会尝试重量级方案
- 成功路径是"用标准库从零实现数学"——这在真实生产环境中几乎不是理想策略

**宽松资源限制**奖励的是"能充分利用可用资源的 Agent"：
- 可以拉取完整的数据科学栈（pandas、networkx、scikit-learn）
- 可以 spawn 昂贵的子进程
- 可以运行内存密集型测试套件
- 这些都是在生产环境中的合法行为

> "Tight limits inadvertently reward very efficient strategies, while generous limits are more forgiving and reward agents that can better exploit all available resources. Both are legitimate things to test, but collapsing them into a single score without specifying the resource configuration makes the differences—and real-world generalizability—hard to interpret."
> — [Anthropic Engineering: Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)

### 问题三：评测其实在测量"模型+脚手架+资源"这个联合体

当模型 A 在宽松资源环境下得分高于模型 B 在严格资源环境下的得分时，你得到的是：
```
score = f(model_A, harness_A, resources_A)
vs
score = f(model_B, harness_B, resources_B)
```

这不是在比较 model_A 和 model_B，而是在比较三个变量的联合输出。任何单变量结论都是无效的。

---

## 真实案例：bn-fit-modify 任务的资源敏感性

Anthropic 提供的 bn-fit-modify 案例极具说明性。这是一个需要贝叶斯网络拟合的 Terminal-Bench 任务。

**某些模型的第一步行动是安装标准 Python 数据科学栈**：pandas、networkx、scikit-learn 及其完整工具链。

- **在严格资源限制下**：安装在内存峰值阶段 OOM，Agent 在写一行解决方案代码之前就被 killed
- **在宽松资源限制下**：安装成功，Agent 继续解决问题，最终成功

但问题是：**存在一个更精简的策略**——只用标准库从零实现数学逻辑。有些模型默认会走到这个路径，有些不会。

这意味着：
1. **资源配配置决定了哪些默认策略能成功**
2. **不同模型有不同的默认策略**
3. **相同的资源配置对不同模型的影响是不对称的**

> "Different models have different default approaches, and the resource configuration determines which of those approaches happen to succeed."
> — [Anthropic Engineering: Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)

---

## SWE-bench 的交叉验证

Anthropic 还在 SWE-bench 上做了交叉实验：在 227 道题、每题 10 个样本的规模上，将总可用 RAM 从 1x 变化到 5x。

结果：
- 趋势相同（分数随 RAM 单调递增）
- 但幅度较小（5x vs 1x 只差 1.54 个百分点）
- **原因**：SWE-bench 任务本身资源密集度更低，所以效应更小

这说明**资源效应不是 Terminal-Bench 独有的，而是 Agentic Evals 的普遍特征**。

---

## 业内现状：规范指定 ≠ 严格执行

Terminal-Bench 2.0 已经在其规范中指定了 per-task 的 CPU 和 RAM 推荐值。但 **specifying resources isn't the same as enforcing them consistently**。

Anthropic 发现：
- 他们自己的 Kubernetes 实现将 per-task 资源规格同时作为 floor 和 hard ceiling
- 容器被保证获得指定资源，但一旦超出就被 killed
- 这造成了零 headroom：瞬态内存波动就能杀死一个本来会成功的容器

而 Terminal-Bench 官方 leaderboard 使用的沙箱提供商实现更宽松：允许临时 over-allocation 而不 terminate 容器。

所以 **Anthropic 自己跑分和官方 leaderboard 不匹配**，原因就是执行层面的差异，而非模型能力差异。

---

## 判断性内容：这不是一个可以"修复"的问题

### 笔者认为：这是一个结构性问题，无法根本解决

原因一：**资源敏感性是模型特性的一部分**。某些模型天然更节省资源，某些更浪费。如果资源限制影响了哪个策略能成功，那就影响了"Agent 能做什么"——这是能力的一部分，不只是测量误差。

原因二：**资源敏感性对不同模型是不对称的**。一个在 1x 资源下成功率仅比 3x 低 2% 的模型，和一个在 1x 下完全失败的模型，在资源敏感维度上有本质差异。但现有评测无法分离这个维度。

原因三：**没有"ground truth"资源级别**。到底应该是 1x、3x 还是 unlimited？没有任何先验理由认为某一个比另一个更"正确"。

### 笔者认为：代理指标的危险性

Agent 评测正在被广泛用于：
- 模型采购决策
- 投资评估
- 学术论文结论
- 产品能力声明

但如果连"SWE-bench 分数"都不能直接归因于模型能力，那这些决策都建立在不稳定的基础上。**当评测分数的方差来源中基础设施占了可观比例时，"评测分数 = 模型能力"这个代理指标就失效了**。

---

## 实践建议：如何在噪声中获取有效信号

### 对从业者

1. **永远报告资源配置**：任何 Agent 评测结果必须同时报告 CPU/RAM/time limits 配置，否则结果无法解读
2. **做敏感性分析**：如果你要比较模型 A 和 B，至少在两种资源配置下运行，观察差异是否稳定
3. **警惕单一数字**：当有人给你一个"SWE-bench 分数"时，先问：在什么资源配置下？

### 对框架设计者

1. **将资源规格从 floor+ceiling 改为 floor+soft-ceiling**：允许瞬态峰值，避免因内存波动杀死本来会成功的容器
2. **报告基础设施错误率**：success rate 和 infra error rate 应该同时报告，两者解耦才能正确归因
3. **考虑多配置评测**：在不同资源级别下运行，给出曲线而非单点

### 对评测设计者

1. **明确声明评测假设**：你的评测是在哪个资源级别下设计的？该级别的设计依据是什么？
2. **分离能力维度和效率维度**：或许应该分别报告"能不能做"和"做得多高效"，而非合并成单一分数
3. **加入资源敏感性测试**：作为标准测试集的一部分，验证模型在不同资源级别下的表现稳定性

---

## 关联文章

- [Anthropic Agent Skills 渐进式披露三层架构](./anthropic-agent-skills-progressive-disclosure-2026.md) — Agent Skills 的渐进式加载哲学与本文的"资源敏感性"形成有趣对照：前者关注上下文的内容按需加载，后者关注运行时的资源按需分配
- [SWE-bench 排行榜分析](./agent-benchmarks-2026-guide.md) — 如何正确解读 SWE-bench 等主流评测的分数
- [Eval Awareness: Claude Opus 4.6 的评测自我意识](../evaluation/eval-awareness-browsecomp-claude-opus-2026.md) — 模型对评测本身的感知能力

---

## 结论

Anthropic 的这项研究不是对某个特定评测工具的批评，而是对整个 Agent 评测范式的基础性质疑。当我们说"模型 X 在 SWE-bench 上得了 Y 分"时，实际上描述的是一个由模型+harness+基础设施+资源配配置共同决定的联合函数的值。

**真正的挑战不是修复评测工具，而是承认这个现实，并学会在噪声中提取有效信号。**

> "In principle, every element of the evaluation setup can influence the final score, from the cluster health to the hardware specs, from the concurrency level to even egress bandwidth."
> — [Anthropic Engineering: Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)

---

*来源：[Anthropic Engineering Blog](https://www.anthropic.com/engineering/infrastructure-noise)，2026-04 | [PDF 原文](/resources/papers/anthropic-infrastructure-noise-2026.pdf)*
