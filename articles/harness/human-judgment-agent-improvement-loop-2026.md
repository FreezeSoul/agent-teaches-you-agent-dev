# Human Judgment in the Agent Improvement Loop：让专家知识进入 Agent 循环

> **核心问题**：很多组织的核心知识存在于员工的脑子里，不在文档里。Agent 如何获取这些「隐性知识」？答案是：**不直接获取，而是通过 Human-in-the-Loop 把专家判断变成自动化信号**。

本文是 [Anatomy of Agent Harness](https://github.com/FreezeSoul/agent-engineering-by-openclaw/blob/master/articles/harness/anatomy-of-agent-harness-2026.md) 的续篇。上文定义了 Agent = Model + Harness，提出 Harness 包含四大组件：文件系统、代码执行、沙箱、Memory/Search。

本文回答的问题更具体：**Harness 的这三个组件（Workflow Design、Tool Design、Agent Context）如何从 Human Judgment 中持续学习？** 答案不在于「让人类教 Agent」，而在于**把人类判断转化为可自动化的评估信号**。

---

## 从「人工审核所有输出」到「自动化评估 + 人工校准」

最直接的思路：部署 Agent 后，找专家人工审核所有输出。错了就纠正。

这个方案有两个致命问题：

1. **不可扩展**：专家时间有限，Agent 输出量大，人工审核成本指数级增长
2. **不同专家标准不一致**：不同专家对「什么是对的」可能有不同判断，Agent 无法学到稳定的标准

LangChain 与数百个组织合作部署 Agent 后发现的最有效模式是：

> **让人类帮助设计和校准自动化评估器，而不是逐条人工审核输出。**

换句话说：人类负责定义「什么是好」，Agent 系统负责规模化地判断「这一次是否好」。

这个模式的关键基础设施是 **LLM-as-Judge**——用一个 LLM 模拟专家的判断标准。但 LLM-as-Judge 本身需要校准，因为模型天然的判断倾向可能和领域专家不一致。LangSmith 的「Align Evaluator」功能正是解决这个问题的：让领域专家提供标注样本，然后用这些样本校准 LLM-as-Judge 的判断准确度。

---

## Agent 的三个可学习型组件

从 Harness 的角度，Agent 中有三个组件特别适合接收 Human Judgment 的输入：

### 1. Workflow Design（工作流设计）

LLM 目前擅长自主编排自己的行动序列——给一个自然语言指令和一组工具，模型会自动决定先调用什么再调用什么。

**但有些场景不适合让 LLM 自主决策：**

- **监管合规场景**：某些步骤必须按特定顺序执行，不能跳过
- **关键操作必须验证**：比如金融系统里最终答案必须经过风险合规检查才能返回用户
- **延迟敏感路径**：确定性代码路径比 LLM 调用延迟更低、Token 更省

在这类场景中，工作流的骨架由**确定性代码**定义，LLM 负责子步骤的生成和执行。代码保证关键步骤一定执行，LLM 提供灵活性。

**Human Judgment 的介入点**：风险/合规专家定义「什么检查必须通过」，工程师将其编码为自动检查规则。这些规则成为工作流的一部分，同时也作为 Agent Context 预加载，让 Agent 第一次就做对。

### 2. Tool Design（工具设计）

开发者负责实现 Agent 可调用的工具，但工具的**命名、参数描述、调用约束**直接影响 LLM 是否能正确选择和调用工具。

**一个核心权衡：灵活性 vs 安全性**

```
execute_sql(query: string)        # 最灵活，但最危险
parameterized_query(template, ...)  # 更安全，但能力受限
```

这个权衡没有通用答案，取决于业务场景的容错能力。**只有跑评估才能知道哪种设计更合适。**

**Human Judgment 的介入点**：

- 领域专家定义工具的调用约束（如：哪个角色可以执行写操作）
- 开发者提供多种工具设计方案
- 通过 A/B 评估确定哪种设计在实际场景中表现更好
- **只有所有利益相关方都认为可接受，才正式上线该工具**

### 3. Agent Context（Agent 上下文）

早期 Agent 只有 System Prompt + 工具定义。现在的趋势是给 Agent 提供**极其丰富的启动上下文**：文档、示例、领域规则、工作流说明……

Anthropic 的 Skills 标准是这种趋势的代表——不是在 System Prompt 里塞所有东西，而是让团队提前整理好文档和示例，Agent 在运行时按需获取。

**Human Judgment 的介入点**：

- **决定 Agent 启动时应该知道什么**：哪些知识是 Agent 执行任务必须具备的
- **组织这些知识的方式**：如何分块、如何层级化，让 Agent 在正确的时机获取正确信息
- **渐进式披露**：不是一开始就把所有上下文都塞给 Agent，而是按任务进展逐步提供

这是 Context Engineering 的核心 discipline，也是 Anthropic 在 2025-2026 年持续深耕的方向。

---

## Agent Improvement Loop：四阶段飞轮

将 Human Judgment 融入 Agent 开发，需要一个完整的迭代循环。LangChain 观察到的最成功模式分为四个阶段：

```
开发阶段 → 部署阶段 → 监控阶段 → 改进阶段 → (回到开发阶段)
```

### 阶段一：开发期——建立测试集和评估器

**工程师**提供初始用例和预期行为描述（来自需求文档）。**产品经理和领域专家**共同构建更完整的测试套件，覆盖核心行为和关键子组件。

具体做法（以 LangSmith 为例）：

1. 用 **Datasets** 功能手动创建「自然语言问题 + 正确答案」配对
2. 创建「好的代码/差的代码」示例集（领域专家定义质量标准）
3. 部署前用 **Evaluations** 功能跑测试
4. 技术和非技术团队成员都可以在 LangSmith UI 里审查评估结果、添加标注

**小规模人工审核的作用**：在开发期人工审核的价值不是找 Bug，而是**建立对 Agent 能力边界的共同认知**。这是后续自动化评估的隐含标准来源。

### 阶段二：部署期——上线后监控

部署后，传统的用户满意度调查有根本性缺陷：**用户说的和用户做的不一致**。LLM-as-Judge 可以在生产数据上持续运行，比调查问卷更准确地反映实际情况。

LangSmith 的自动化配置可以：

- **在线评估**：对每条生产交互跑 LLM-as-Judge 评分（如：用户是否表达了挫败感）
- **告警**：错误率、延迟、或评分骤降时自动触发
- **Annotation Queue**：将高置信度负样本推送给专家审核

```
用户消息 → Agent 处理 → LangSmith Trace → LLM-as-Judge 评分
                                              ↓
                                    评分过低 → 推入 Annotation Queue
                                              ↓
                                    领域专家审核标注
                                              ↓
                                    标注结果 → 改进 Eval + 改进 Agent
```

**Annotation Queue 是整个 Human Judgment 闭环的核心**。它的价值在于：专家不是在漫无目的地审所有输出，而是**只看系统标记出的高价值样本**。

### 阶段三：改进期——闭环回到开发

LangSmith 保存了 Annotation Queue 中专家的所有反馈。这些反馈同时用于：

1. **校准 LLM-as-Judge**：专家标注揭示了 Judge 的系统性偏差，可以调整 Prompt
2. **扩展 Datasets**：专家发现的边界案例加入训练集
3. **识别知识缺口**：哪些领域 Agent 完全不了解（需要补充 Context）

LangSmith 的 **Insights Agent** 可以分析大量 Trace 数据，自动发现人工不易察觉的模式和趋势。专家最终 Review Insights Report，对下一步改进方向达成共识。

---

## 核心工程教训

### 教训一：Eval 是 Harness 的训练数据

传统 ML 是「训练数据 → 模型权重更新」。Harness Engineering 是「Eval → Harness 配置更新」。

每个 Eval case 是对 Harness 的一次梯度信号：「这次 Harness 引导 Agent 走向正确行为了吗？」

Eval 的质量直接决定 Harness 的改进质量。和 ML 训练数据一样：

- **数量不够 → 过拟合**：Harness 在已知 case 上好，在未知 case 上差
- **标签不准 → 偏差**：Eval 本身衡量错了东西，Harness 优化方向错误
- **无 Holdout → 无法验证泛化**：所有 Eval 都参与优化 → 无法判断是否真正进步

### 教训二：Annotation Queue 的本质是「主动学习」

不是随机抽样本让人审核，而是**系统主动挑选高信息量样本**送审。

LLM-as-Judge 打了低分 → 送审。评分边界模糊 → 调整 Judge Prompt 后再跑。这是一种主动学习策略：让专家的有限时间总是花在最需要判断的地方。

### 教训三：Human Judgment 的价值在于「校准」而非「替代」

在 Agent Improvement Loop 中，Human Judgment 的最佳定位不是替代自动化评估，而是**提高自动化评估本身的准确性**。

具体来说：

- 专家定义评估维度（「这个场景下什么是好的 SQL」）
- 专家提供校准样本（5-10 个已标注的 case）
- LLM-as-Judge 在这些样本上校准后，规模化地判断所有其他 case

这解决了「规模化」和「专家标准」之间的根本矛盾。

---

## 适用边界

**Human Judgment Loop 特别适合：**

- 有明确领域知识的场景（如法律、金融、医疗）
- 隐性知识（非文档化但专家脑子里知道）占比高的任务
- 高价值决策场景（错误成本高，必须有人把关）

**不太适合的场景：**

- 领域知识完全不明晰（连专家自己都不确定什么是正确答案）
- 实时性要求极高（人工校准有延迟）
- 容错率高的任务（错了影响不大，不需要严格标准）

---

## 与 Anatomy of Agent Harness 的关系

本文的上篇定义了 Agent = Model + Harness，提炼出四大 Harness 组件。本文聚焦于：

**Harness 的三个组件（Workflow Design、Tool Design、Context）如何通过 Human-in-the-Loop 持续优化。**

关键补充观点：

1. **Harness 不是一次性设计好的静态容器，而是随 Agent 部署后持续进化的系统**
2. **Human Judgment 流入 Harness 的通道是 Eval，不是人工审核**
3. **Annotation Queue 是让 Human Judgment 可规模化的核心机制**

换句话说：Anatomy of Agent Harness 定义了「Harness 是什么」，本文定义了「Harness 如何从 Human Judgment 中学习」。

---

## 参考文献

- [Human judgment in the agent improvement loop](https://blog.langchain.com/human-judgment-in-the-agent-improvement-loop/)（LangChain Blog，APR 9, 2026）——本文核心来源
- [LangSmith Align Evaluator](https://docs.langchain.com/langsmith/improve-judge-evaluator-feedback)（LangChain Docs）——LLM-as-Judge 校准工具
- [LangSmith Annotation Queues](https://docs.langchain.com/langsmith/annotation-queues)（LangChain Docs）——高价值样本主动推送
- [Anthropic Skills](https://anthropic.skilljar.com/introduction-to-agent-skills)（Anthropic）——Context Engineering 的标准化实践
- [Traces: Start an Agent Improvement Loop](https://www.langchain.com/conceptual-guides/traces-start-agent-improvement-loop)（LangChain）——Agent Improvement Loop 原始概念
