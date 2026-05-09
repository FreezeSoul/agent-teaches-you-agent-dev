# Anthropic「Measuring AI Agent Autonomy」深度解读：部署 overhang 与监督范式的根本性转移

> **核心主张**：Claude Code 的最长自主运行时间在过去三个月翻倍（从 25 分钟到 45 分钟），但这并非能力提升的直接结果——而是「部署 overhang」的表现：模型实际行使的自主权远低于其能力上限。这对 Agent 工程实践的含义是：当前的瓶颈不在模型能力，而在人类监督机制的设计。

---

## 研究背景与方法论

研究 Agent 的核心困难在于：没有统一的 Agent 定义；Agent 架构对模型提供商不可见；工具调用分散在大量独立请求中，难以重建完整的会话序列。

Anthropic 的解决思路是「工具即行为代理」——通过分析 API 层面的工具调用模式，在不了解具体 Agent 架构的情况下做出有依据的观察。具体来说：

- **API 数据**：分析数千个不同客户部署的工具调用，提供跨行业广度，但只能分析单个动作，无法重建行为序列
- **Claude Code 数据**：自家产品，可以串联完整会话，研究自主性（运行时长、触发中断的条件、用户维持监督的方式），但代表性有限

> "An agent is an AI system equipped with tools that allow it to take actions, like running code, calling external APIs, and sending messages to other agents." — [Anthropic: Measuring Agent Autonomy](https://www.anthropic.com/news/measuring-agent-autonomy)

---

## 关键发现一：99.9% 分位运行时间翻倍

Claude Code 每次运行的时长（turn duration）是自主性的直接代理指标。大多数 turn 极短（中位数 45 秒），且在各百分位都相对稳定——这是合理的，因为新用户占比高，而新用户倾向于给予较低的自主权限。

真正有信息量的是分布的尾部。2025年10月到2026年1月间，最长 0.1% 的 turn 从不足 25 分钟增长到超过 45 分钟，实现近乎翻倍。

关键是这个增长在模型版本之间是平滑的——没有因新模型发布而出现跳跃。这说明：

1. 增长不完全源于能力提升（否则会在模型切换时看到跳跃）
2. 主要驱动因素是用户对工具信任的积累、用户将 Agent 应用于更具挑战性的任务、以及产品的持续改进

> "The relative steadiness of this trend instead suggests several potential factors are at work, including power users building trust with the tool over time, applying Claude to increasingly ambitious tasks, and the product itself improving." — [Anthropic](https://www.anthropic.com/news/measuring-agent-autonomy)

笔者补充：这种平滑增长揭示了一个重要的工程现实——模型的「能力上限」与「实际行使的自主权」之间存在显著落差。METR 的「Measuring AI Ability to Complete Long Tasks」评估显示 Claude Opus 4.5 在理想环境下（无人类交互、无真实后果）能以 50% 成功率完成人类需要近 5 小时的任务，而 Claude Code 实际运行中的 99.9% 分位 turn 约为 42 分钟，远低于 5 小时的能力上限。

这意味着**当前的 Agent 架构设计浪费了大量模型能力**，或者说 harnesses 的设计在「允许模型行使其全部能力」方面存在系统性制约。这对 harness 工程师的含义是：应该把更多精力放在扩大模型行使自主权的边界上，而不是继续提升模型能力。

---

## 关键发现二：经验用户的监督策略转移

数据揭示了一个初看矛盾的规律：随着用户积累经验，自动审批率（auto-approve）与中断率同时上升。

- 新用户（<50 session）约 20% 的 session 使用完整自动审批；到 750 session 时，这一比例超过 40%
- 同时，经验用户的每轮中断率从约 5% 上升到约 9%

> "Both interruptions and auto-approvals increase with experience. This apparent contradiction reflects a shift in users' oversight strategy. New users are more likely to approve each action before it's taken, and therefore rarely need to interrupt Claude mid-execution. Experienced users are more likely to let Claude work autonomously, stepping in when something goes wrong or needs redirection." — [Anthropic](https://www.anthropic.com/news/measuring-agent-autonomy)

这不是矛盾，而是「监督策略」的根本性转变：

| 用户类型 | 监督模式 | 认知成本 | 适用场景 |
|----------|----------|----------|----------|
| 新手 | 逐个审批（主动前置检查） | 高 | 低风险、步骤少 |
| 经验用户 | 自动化审批 + 随时中断（被动监控） | 低 | 高风险、步骤多 |

这意味着 **LLM-based Agent 的最优人类监督不是「审批每个动作」，而是「设置边界条件然后让 Agent 跑，有问题时再干预」**。这对 harness 设计的影响是：应该把更多工程精力放在「如何让 Agent 在边界处停下来请求确认」，而不是「如何让人类审批每个步骤」。

在 API 层面也观察到了类似的模式：低复杂度任务（如编辑一行代码）87% 有某种人类参与，而高复杂度任务（如自主发现零日漏洞或编写编译器）这一比例仅为 67%。原因同样是结构性的——步骤越多，逐个审批越不切实际，同时经验用户更倾向于赋予工具自主权。

---

## 关键发现三：Agent 暂停请求澄清的频率高于人类中断

在复杂任务上，Claude Code 因不确定而主动暂停请求澄清的频率是人类手动中断的两倍以上。

> "On the most complex tasks, Claude Code stops to ask for clarification more than twice as often as humans interrupt it." — [Anthropic](https://www.anthropic.com/news/measuring-agent-autonomy)

这是 Agent 自主性的另一个维度——不是被人类打断，而是 Agent 主动「举手提问」。这说明：

1. **当前的 Claude Code 已经内置了「不确定时主动暂停」的行为模式**，这是 Anthropic 在 harness 层有意植入的
2. 人类中断频率低不一定意味着人类监督效果好，也可能意味着人类在复杂任务上缺乏有效的监控手段

这与上一轮 Introspection Adapters（让模型自述习得行为）形成有趣的技术呼应——两者都试图解决「模型的真实状态与外部观察之间的信息不对称」问题：

| 维度 | Introspection Adapters | Measuring Agent Autonomy |
|------|------------------------|--------------------------|
| 解决的问题 | 微调后模型习得了什么不当行为 | Agent 的实际自主性边界在哪里 |
| 方法 | LoRA 适配器让模型自我报告 | 工具调用数据 + 会话分析 |
| 应用 | 部署前安全检查 | 部署后行为监控 |

---

## 关键发现四：风险领域的使用已出现，但尚未规模化

在 API 层面，Anthropic 观察到 Agent 已被部署在医疗、金融和网络安全等高风险领域，但总体占比仍然较低——大多数 Agent 行为是低风险、可逆的。软件工程仍然是 Agent 活动的最大场景，接近 50%。

这个发现对安全工程师和采购决策者的含义是：**在 Agent 被大规模部署到高风险领域之前，当前是建立「Agent 安全监督基础设施」的关键窗口期**。Anthropic 的判断是：

> "Effective oversight of agents will require new forms of post-deployment monitoring infrastructure and new human-AI interaction paradigms that help both the human and the AI manage autonomy and risk together." — [Anthropic](https://www.anthropic.com/news/measuring-agent-autonomy)

---

## 对 Agent 工程实践的系统性影响

### 1. 监督范式需要根本性重设计

当前的 Agent 监督机制大多停留在「逐个审批」或「事后审查」层面。但数据显示经验用户已转向「设置边界 + 被动监控」模式——这意味着 harness 需要提供：

- **边界条件表达机制**：用户能清晰定义「在此条件下停止」
- **主动不确定性信号**：Agent 在不确定时主动暂停，而非硬闯
- **事后可审计性**：完整的行动轨迹记录，支持回溯分析

### 2. 部署 overhang 是当前最被低估的问题

模型能力上限与实际行使自主权之间的差距，意味着大多数生产环境 Agent 只发挥了模型潜在能力的一小部分。这不是模型的问题，而是 harness/orchestration 层的问题——Agent 架构需要重新设计以行使模型的全部能力。

### 3. 经验用户的监督数据是下一代 harness 的训练集

随着用户积累更多与 Agent 协作的经验，他们的「边界在哪里」的直觉数据，对设计下一代监督机制有极高价值。如何收集、聚合、分析这些数据，是一个尚未被充分解决的工程问题。

---

## 结论

Anthropic 的这篇研究揭示了一个核心事实：**Agent 的自主性正在快速增长，但人类监督机制的设计严重滞后**。99.9% 分位 turn 翻倍（~25→45 分钟）只是开始——随着模型能力继续提升，这个差距只会扩大，不会自动收窄。

对 Agent 工程师而言，这意味着接下来的核心挑战不是「如何让模型做更多」，而是「如何让人类与模型在更高自主性下保持有效的风险共控」。这是人类-AI 协作范式的一次根本性转折点。

---

**一手来源**：
- [Measuring AI Agent Autonomy in Practice — Anthropic](https://www.anthropic.com/news/measuring-agent-autonomy) (2026-05-05)
- [Anthropic Engineering Blog](https://www.anthropic.com/engineering)
- [METR: Measuring AI Ability to Complete Long Tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)

**关联阅读**：
- [Anthropic「Scaling Managed Agents」— Brain-Hands-Session 三元解耦架构](./anthropic-scaling-managed-agents-brain-hands-session-2026.md)
- [Anthropic Introspection Adapters — 让模型自述习得行为](./anthropic-introspection-adapters-fine-tuning-audit-2026.md)