# DeepResearch Bench：ICLR 2026 深度研究智能体评测框架解析

> **本质**：DeepResearch Bench 是 ICLR 2026 收录的学术基准，通过 100 个博士级研究任务和双维度评估框架（RACE + FACT），系统性衡量深度研究智能体的研究质量与信息检索能力。该基准揭示了一个关键发现：领先模型在不同评估维度上各有专长，没有绝对的「最优」深度研究智能体。

## 一、背景：深度研究智能体为何需要专用基准

深度研究智能体（Deep Research Agents, DRAs）正在成为 LLM 应用中最实用的方向之一。给定一个开放性研究任务，DRA 能够自主编排多轮网页探索、定向检索和综合合成，输出具备研究员水准的引用密集型报告——将数小时的人工调研压缩到分钟级别。

然而，一个核心问题始终缺乏答案：**如何系统性地衡量 DRA 的研究能力？**

传统的问答基准（如 MMLU、HellaSwag）无法评估：

- 多轮信息收集与合成的完整性
- 引用信息的准确性与可追溯性
- 报告结构的逻辑性和可读性
- 对模糊指令的理解与执行能力

更关键的是，现有基准依赖静态数据集，无法反映真实研究场景的开放性和复杂性。

## 二、基准构建：100 个博士级任务的诞生

DeepResearch Bench 的设计目标是测试 DRA 的**能力上限**，而非平均水准。具体构建流程：

### 2.1 数据来源与主题分布

研究团队分析了 96,147 条真实用户查询（来自启用 Web 搜索的 LLM Chatbot），筛选出需要深度研究能力的 44,019 条查询，最终归纳为 **22 个主题领域**。

主题分布反映真实需求：

| 占比最高领域 | 含义 |
|-------------|------|
| Science & Technology | 科技类研究最多 |
| Business & Finance | 商业与金融次之 |

这一分布直接指导了 100 个任务的主题配比，确保基准与实际使用场景一致。

### 2.2 任务质量：博士级标准

每个任务由**拥有博士学位或 5 年以上经验的资深从业者**精心设计，涵盖：

- 新兴技术分析（如某新架构的优缺点研究）
- 综合市场调研（如某行业的竞争格局）
- 科学文献综述（如某领域最新进展追踪）

100 个任务中，**50 个中文 + 50 个英文**，覆盖中英文研究场景，避免单一语言偏差。

## 三、评估框架：RACE + FACT 双维度设计

这是 DeepResearch Bench 最重要的方法论贡献——两套互补的评估框架，分别衡量**报告质量**和**信息检索能力**。

### 3.1 RACE：研究报告质量评估

RACE（Reference-based Adaptive Criteria-driven Evaluation framework with Dynamic Weighting）框架评估 DRA 生成的研究报告，包含四个维度：

| 维度 | 全称 | 含义 |
|------|------|------|
| **Comp.** | Comprehensiveness | 覆盖研究主题的全面程度 |
| **Depth** | Depth | 对核心问题的分析深度 |
| **Inst.** | Instruction-Following | 对用户指令的遵循程度 |
| **Read.** | Readability | 报告的可读性与逻辑性 |

### 3.2 FACT：信息检索能力评估

FACT（Framework for Factual Abundance and Citation Trustworthiness）框架评估 DRA 的信息收集能力：

| 维度 | 全称 | 含义 |
|------|------|------|
| **C. Acc.** | Citation Accuracy | 引用准确性——是否正确引用了真实来源 |
| **E. Cit.** | Effective Citations | 有效引用数量——引用中真正支撑报告论点的数量 |

FACT 的设计极具洞察力：DRA 容易生成「幻觉引用」（引用不存在的论文或错误归因），因此 **引用准确性** 和 **有效引用数量** 必须分开衡量。

## 四、核心实验结果

### 4.1 RACE 结果：综合研究质量

| 模型 | Overall | Comp. | Depth | Inst. | Read. |
|------|---------|-------|-------|-------|-------|
| **Gemini-2.5-Pro Deep Research** | **48.88** | **48.53** | **48.50** | 49.18 | **49.44** |
| **OpenAI Deep Research** | 46.98 | 46.87 | 45.25 | **49.27** | 47.14 |
| Perplexity Deep Research | 42.25 | 40.69 | 39.39 | 46.40 | 44.28 |
| Grok Deeper Search | 40.24 | 37.97 | 35.37 | 46.30 | 44.05 |

**关键发现**：

- **Gemini-2.5-Pro Deep Research** 在 Overall、Comp.、Depth、Read. 四个维度领先
- **OpenAI Deep Research** 在 Instruction-Following 维度最高（49.27），意味着对复杂指令的执行最精准
- 这说明**评估维度捕获了不同的能力**——没有模型在所有维度都是最优

### 4.2 FACT 结果：信息检索与引用能力

| 模型 | C. Acc. | E. Cit. |
|------|---------|---------|
| Gemini-2.5-Pro Deep Research | 81.44 | **111.21** |
| Perplexity Deep Research | **90.24** | 31.26 |
| OpenAI Deep Research | 77.96 | 40.79 |
| Claude-3.7-Sonnet w/Search | 93.68 | 32.48 |

**关键发现**：

- **Gemini-2.5-Pro Deep Research** 的有效引用数量远超其他模型（111.21 vs 40.79），信息收集能力最强
- **Perplexity Deep Research** 的引用准确性最高（90.24%），但有效引用数量较低——说明引用精准但量少
- **有趣的模式**：引用数量多 ≠ 引用准确；两者存在权衡

### 4.3 与 LLM + Search Tools 的对比

| 类别 | 代表模型 | RACE Overall |
|------|---------|-------------|
| Deep Research Agent | Gemini-2.5-Pro (48.88) | 最高 |
| LLM + Search Tools | Claude-3.7-Sonnet w/Search (40.67) | 差距明显 |

DRA 显著优于简单的「LLM + 搜索工具」组合，说明**自主编排多步研究流程**本身具有不可替代的价值。

## 五、局限性

DeepResearch Bench 也有其局限性：

1. **任务数量有限**：100 个任务虽然质量高，但覆盖范围仍有局限
2. **英文为主的互联网信息源**：模型在英文信息来源上的表现可能优于其他语言
3. **静态评估**：研究领域持续演进，基准需要持续更新
4. **企业场景缺失**：该基准偏向通用学术研究，未覆盖企业特有的私有数据/内部系统场景（DRBench 填补了这一空白，见下节）

## 六、DRBench：企业场景的补充

ICLR 2026 同时收录了 **DRBench**（ServiceNow, arXiv:2510.00172v2），聚焦企业深度研究场景：

- **核心定位**：评估 DRA 在企业环境中的复杂、多跳、洞察驱动的调研任务
- **特点**：100 个以用户角色和组织场景为基础的任务（persona-grounded），涵盖公共和私有数据源
- **开源**：GitHub: ServiceNow/drbench

DRBench 与 DeepResearch Bench 的关系是**互补而非竞争**：

| 基准 | 定位 | 任务特点 | 开源情况 |
|------|------|---------|---------|
| DeepResearch Bench | 学术通用 | 博士级研究任务，22 个领域 | 部分开源 |
| DRBench | 企业垂直 | persona-grounded，多跳洞察 | 完整开源 |

## 七、对 Agent 开发者的实践意义

### 7.1 选型决策

根据具体需求选择模型：

- **需要全面覆盖**（综合研究报告）→ Gemini-2.5-Pro Deep Research
- **需要精准遵循指令**（特定格式/约束）→ OpenAI Deep Research
- **需要高可信度引用**（事实核查场景）→ Perplexity Deep Research 或 Claude-3.7-Sonnet w/Search

### 7.2 系统设计启示

RACE + FACT 双框架揭示了一个重要的设计原则：**研究质量 ≠ 信息数量**。

在构建 DRA 系统时，应分别追踪：
- **报告质量指标**（RACE 维度）
- **引用质量指标**（FACT 维度）

避免单纯优化「引用数量」而忽视「引用准确性」。

### 7.3 评测基础设施

DeepResearch Bench 开源了 RACE 和 FACT 框架，开发者可以：

1. 使用 RACE 评估自己 DRA 的报告质量
2. 使用 FACT 追踪引用准确性
3. 结合两者建立内部评测流水线

## 八、参考文献

1. Du, M. et al. (2026). *DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents*. ICLR 2026. https://openreview.net/forum?id=hQ0K2Hhq7H
2. Abaskoh et al. (2026). *DRBench: A Realistic Benchmark for Enterprise Deep Research*. ICLR 2026. https://openreview.net/forum?id=IGYQ4c92e2
3. DeepResearch Bench Official: https://deepresearch-bench.github.io/
4. DRBench GitHub: https://github.com/ServiceNow/drbench
5. arXiv:2506.11763 (DeepResearch Bench)
6. arXiv:2510.00172v2 (DRBench)
