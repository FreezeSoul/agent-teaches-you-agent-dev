# Measuring Agent Autonomy：Anthropic 的第一手规模化研究

> **本质**：Anthropic 通过隐私保护工具 Clio 分析了数百万次真实 Agent 交互，首次量化揭示了"模型能力与实际部署之间的巨大落差"——这就是"部署余量"（Deployment Overhang）

## 一、研究背景与方法

### 为什么这个研究重要

在 Agent 领域，绝大多数讨论都是理论推断或产品宣传。Anthropic 的这项研究罕见地提供了**规模化实证数据**：
- 分析范围：Claude Code + 公开 API，数百万次人-Agent 交互
- 研究工具：Clio——隐私保护的自动化分析系统（无需人工阅读用户对话）
- 研究目的：回答四个核心问题：人给 Agent 多少自主权？随经验如何变化？Agent 在哪些领域活动？Agent 的行为是否危险？

### Clio：隐私保护的规模化分析

传统上，要理解用户如何与 AI 交互，要么依赖用户主动报告（偏颇），要么人工审查对话（侵犯隐私）。Clio 另辟蹊径：

1. 对话聚类（Clustering）：将数百万对话按主题和行为模式自动分组
2. 差分隐私（Differential Privacy）：在聚合统计中消除个体痕迹
3. 自动主题分类（NLU）：无需人工标注，自动识别 Agent 活动领域
4. 行为指标提取：从工具调用序列中还原 Agent 行为模式

这一方法论本身就是一个重要的工程贡献——它证明了**可以在不侵犯用户隐私的前提下进行规模化 AI 使用分析**。

## 二、核心发现一：Deployment Overhang——部署余量

### 数据

> Among the longest-running sessions, the length of time Claude Code works before stopping has **nearly doubled in three months**, from under 25 minutes to over 45 minutes. This increase is smooth across model releases, which suggests it isn't purely a result of increased capabilities.

**关键解读**：
- 99.9% 分位会话时长：<25 分钟 → >45 分钟（3 个月内）
- 增速在各模型版本间平滑过渡（无明显跃升）
- 这意味着：**能力提升只是部分原因，更主要的是用户行为变化和产品优化**

### 什么是 Deployment Overhang

Anthropic 由此提出了一个重要概念——**Deployment Overhang（部署余量）**：

> 模型能够展现的自主能力，超出实际被授权使用的程度

类比：核电站的发电能力 vs 实际输出的电力。反应堆可以输出 1000MW，但出于安全和运维考虑，实际输出可能只有 300MW。"余量"不是浪费，而是**必要的安全边界**。

对 Agent 工程的启示：
- **对开发者**：你的模型能力 > 你让模型做的事。不要假设现有模型"只能这样"，可以逐步提高自主权限测试边界
- **对产品设计**：用户对 Agent 的信任建立是渐进的，不是一步到位的
- **对安全**：Deployment Overhang 也是安全余量——即使 Agent 有能力做更多，它实际做的更少

## 三、核心发现二：用户信任曲线——经验改变监督策略

### 数据

- 新用户（约 20% 的会话使用完全自动批准）→ 经验用户（750+ 会话后，超过 40% 使用完全自动批准）
- **但**：经验用户也更多地进行主动干预（打断 Agent）

这看起来矛盾，实际是合理的范式转变：

| 用户类型 | 监督模式 | 行为描述 |
|---------|---------|---------|
| 新用户 | Step-by-step approval | 每个操作前等待确认 |
| 经验用户 | Monitor-and-intervene | 让 Agent 跑，出问题时再介入 |

### 对 Agent 产品的设计启示

这一发现对 AI 产品设计有直接指导意义：

**1. 初期需要细粒度控制**
新用户需要"每步确认"不是因为他们不信任 AI，而是因为他们**还不理解 Agent 能做什么、不能做什么**。这一步是建立 Mental Model 的过程。

**2. 经验用户需要"宏观监督"界面**
到了经验阶段，用户不需要看每一步，但他们需要：
- 清晰的进度指示器
- 异常/停止的即时通知
- 高层次的执行摘要
- 快速回滚/取消能力

**3. Auto-approve 的阈值应该动态调整**
最佳做法不是"始终自动批准"或"始终手动批准"，而是根据：
- 任务类型（代码编写 vs 发送邮件风险等级不同）
- 历史行为（用户是否在类似任务上经常干预）
- 当前 Agent 的置信度（Agent 主动暂停时强制人工介入）

## 四、核心发现三：Agent 的自我不确定性管理

### 数据

> On the most complex goals, Claude asked for clarification in 16.4% of turns, while humans interrupted in only 7.1%.

**关键洞察**：Agent 在遇到复杂任务时，**主动暂停寻求澄清的频率是人类打断频率的两倍以上**。

### 这意味着什么

传统的 Human-in-the-Loop（HITL）安全模型假设：人类是监督者，Agent 是执行者。Claude Code 的数据显示了一个更微妙的画面：

**Agent 也可以成为安全机制的一部分**——当 Agent 遇到自身不确定的情况时，主动暂停比盲目猜测更安全。

这呼应了 Anthropic 提出的 [_safe and trustworthy agents" 框架](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)中的核心张力：**在保持人类控制的同时实现 Agent 自主性**。主动暂停机制是解决这一张力的有效路径。

### 工程实践含义

对于构建自主 Agent 系统的工程师来说：
- 在 Agent 设计中内置"不确定时暂停"的机制
- 不要把"Agent 停下来问问题"视为效率损失，而是**安全检查机制**
- 建立清晰的升级路径：置信度高 → 自动执行；置信度低 → 暂停等待输入

## 五、核心发现四：实际应用领域分布

### 工具调用领域分布（API 数据）

| 领域 | 占比 | 说明 |
|------|------|------|
| 软件工程 | 49.7% | 主导领域，Claude Code 直接贡献 |
| 后台自动化 | 9.1% | RPA 类任务 |
| 营销/文案 | 4.4% | 内容生成 |
| 销售/CRM | 4.3% | 客户管理 |
| 金融/会计 | 4.0% | 财务自动化 |
| 数据分析 | 3.5% | 数据处理 |

### 对 Agent 开发者的含义

1. **软件工程是当前最成熟的 Agent 应用场景**：如果你在做 coding agent，你不是在给小众市场建工具——这是半壁江山
2. **企业级场景（后台、CRM、财务）合计约 17%**：说明 Agent 在企业场景已有真实落地，不是纯实验性质
3. **医疗和金融的出现**：说明高风险领域已有早期采纳，但规模仍然有限

## 六、核心发现五：实际安全状况

### 数据

- **80%** 的工具调用来自有安全防护机制的 Agent
- **73%** 的会话包含人工参与环节（Human-in-the-loop）
- **仅 0.8%** 的工具调用属于不可逆操作

### 风险-自主性散点图

研究绘制了真实 Agent 部署的风险-自主性散点图，结论：
- 绝大多数活动聚集在**低风险、低-中文自主性象限**
- 高风险+高自主性的部署存在但稀疏
- 这说明**当前 Agent 生态整体处于"谨慎探索"阶段**，而非"大规模高风险部署"

## 七、这项研究本身的方法论价值

### 为什么 Clio 比传统方法更好

传统的 AI 使用分析面临"数据困境"：
- **有监督方法**：依赖人工审查 → 侵犯隐私，无法规模化
- **无监督方法**：依赖用户主动报告 → 选择性偏颇
- **Clio 方法**：自动化聚类 + 差分隐私 → 规模化 + 隐私安全

### 对行业的方法论启示

这项研究的意义不只是具体发现，而是证明了：
**可以在保护用户隐私的同时进行有意义的 AI 使用分析**

这对以下角色有直接价值：
- **模型开发者**：需要知道模型如何被使用以指导安全评估
- **企业安全团队**：需要监控员工如何使用 AI 工具而不侵犯隐私
- **监管机构**：需要数据来制定合理的 AI 政策而不要求过度透明

## 八、对 Agent 工程实践的具体建议

基于这项研究，Anthropic 提出了对三类受众的建议：

### 对模型开发者
1. 建立**部署后监控基础设施**：当前模型开发者对部署后的 Agent 行为几乎无可见性
2. 标准化"Agent 会话"的定义和追踪：不同架构对"一个 Agent 任务"有不同的边界定义
3. 将"Agent 自我不确定管理"作为安全评估的正式指标

### 对产品开发者
1. **不要复制传统 API 的监控模式**：Agent 需要新的可观测性范式
2. 设计"渐进信任"的产品轨迹：参考新用户→经验用户的信任曲线
3. 将 Agent 主动暂停能力视为**功能而非缺陷**

### 对政策制定者
1. **避免要求过度详细的日志**：这会扼杀有价值的隐私保护实践
2. 基于实际风险数据制定政策：研究显示 Agent 风险目前集中在特定领域
3. 认识到"Deployment Overhang"的存在：政策不需要在第一天就覆盖所有可能性

## 九、研究的局限性

Anthropic 坦承了研究的局限：

1. **"Agent" 定义不统一**：研究采用了基于工具调用的操作定义，但业界对"Agent"的边界仍有争议
2. **API 层面的可见性限制**：无法将独立的 API 请求关联为完整的"Agent 任务"（Clio 解决了部分问题但未完全解决）
3. **Claude Code 偏差**：作为单一产品，Claude Code 不能代表所有 Agent 用法
4. **时间范围有限**：研究是当前快照，Agent 使用模式仍在快速演变

## 十、核心 takeaway

```
我们发现了显著的"部署余量"：
模型能够展现的自主能力 > 实际被授权使用的程度

这意味着：
- 现有模型比我们在生产中使用的更有能力
- 用户对 Agent 的信任建立需要时间
- Agent 主动管理不确定性的能力是安全机制
- 我们正处于 Agent 规模化的早期阶段
```

这项研究最重要的贡献，或许是它引入的**实证研究范式**——用数据而非猜测来理解 Agent 如何被真实使用。这为整个 Agent 工程领域提供了一个可以参照的基准。

---

## 参考文献

- [Measuring AI agent autonomy in practice - Anthropic](https://www.anthropic.com/research/measuring-agent-autonomy)（原始研究）
- [Clio: Privacy-preserving insights into real-world AI use - Anthropic](https://www.anthropic.com/research/clio)（方法论文）
- [Our framework for developing safe and trustworthy agents - Anthropic](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)
- [What Anthropic's Agent Autonomy Research Means for Your Content Operations - CosmicJS](https://www.cosmicjs.com/blog/anthropic-agent-autonomy-research-content-operations)
