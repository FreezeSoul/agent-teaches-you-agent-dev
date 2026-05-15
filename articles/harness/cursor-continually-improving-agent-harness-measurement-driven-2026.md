# Cursor Harness 自我改进机制：Keep Rate + 异常检测 + 自动化软件工厂

> 本文分析 Cursor 2026-04-30 发布的《Continually improving our agent harness》，揭示 AI Coding Agent Harness 的持续改进工程体系——以「代码保留率（Keep Rate）」为结果指标、「per-tool per-model 异常检测」为预警机制、「自动化软件工厂」为执行闭环，构建 Harness 的自我改进循环。

---

## 核心论点

Harness 工程的核心挑战不是「如何设计」，而是「如何知道改进是否有效」。Cursor 的答案是：**构建完整的三层测量体系**，将模糊的「Agent 质量」分解为可量化、可对比、可追溯的具体指标。这三层分别是：结果指标（Keep Rate + 用户满意度语义分析）、过程指标（工具调用错误率、上下文 rot）、以及 A/B 测试基础设施。**没有测量就没有改进。**

---

## 背景：Harness 改进的两条路径

Cursor 将 Harness 改进分为两条路径：

**路径一：愿景驱动（Vision-driven）**
从「理想的 Agent 体验应该是什么样的」出发，形成假设，运行实验，用量化信号验证。这要求有正确的在线和离线检测手段，才能判断一个改动是否真的让 Harness 变得更好。

**路径二：模型适配（Model customization）**
当获得新模型的早期访问权限时，花数周时间根据模型的强度和特点定制 Harness，直到同一个模型在我们特别调优的 Harness 中明显更快、更聪明、更高效。

两条路径的共同基础是：**测量**。

Cursor 原文：

> "We approach building the Cursor agent harness the way we'd approach any ambitious software product. Much of the work is vision-driven, where we start with an opinion about what the ideal agent experience should look like."

---

## 第一层测量：Keep Rate——代码质量的结果指标

### 什么是 Keep Rate

Keep Rate 追踪 Agent 提议的代码变更在用户代码库中的「留存比例」：

- **采样时刻**：固定时间间隔（如 24 小时、7 天）
- **计算方式**：变更仍保留在代码库中的比例
- **信号含义**：用户是否需要手动调整 Agent 输出，或需要迭代让 Agent 修复

Keep Rate 反映「用户没有回退」，但不反映「用户主动复用」。一个 Keep Rate 80% 的 Agent 可能是用户懒得改而非真正满意。需要配合第二个指标。

### 第二个指标：用户满意度语义分析

用语言模型分析用户对 Agent 初始输出的响应，捕捉语义上的用户满意度：

- **强正向信号**：用户转向下一个功能 → Agent 完成了工作
- **强负向信号**：用户粘贴错误堆栈 → Agent 没有完成工作

这两个指标的组合才能完整捕捉 Agent 质量。

| 指标 | 优点 | 局限 |
|------|------|------|
| **Keep Rate** | 客观、可量化 | 只能捕捉「没被回退」，无法捕获「主动满意」 |
| **用户满意度语义分析** | 捕捉深层满意度 | 需要额外 LLM 调用，成本更高 |

### 放弃的实验：昂贵的上下文摘要模型

Cursor 做过一个实验：用更昂贵的模型做上下文摘要。结果对 Agent 质量的影响微乎其微，不值得额外成本。**测量让这个结论清晰**——没有 A/B 测试，这个判断可能只是直觉。

---

## 第二层测量：工具调用错误的分类体系

### 为什么工具调用错误特别有害

工具调用错误可能对会话造成极大伤害。虽然 Agent 常能自我纠正，但错误仍留在上下文中，浪费 tokens 并导致「上下文腐烂」（context rot）—— 累积的错误会降低模型后续决策的质量。

### 错误分类的工程化方法

Cursor 将工具调用错误分为「已知错误」和「未知错误」：

**未知错误（Unknown Errors）**
→ 永远是 Harness 的 bug，任何未知错误率超过阈值就触发警报。

**已知错误（Expected Errors）**——又细分为：

| 错误类型 | 含义 |
|----------|------|
| `InvalidArguments` | 模型参数错误或上下文窗口矛盾 |
| `UnexpectedEnvironment` | 环境与预期不符 |
| `ProviderError` | 供应商服务中断（如 GenerateImage、WebSearch） |
| `UserAborted` | 用户中止 |
| `Timeout` | 操作超时 |

### Per-tool per-model 基线：异常检测的关键设计

Cursor 的关键设计决策：**基线是 per-tool per-model 计算的**，因为不同模型在不同工具上的错误率可能完全不同。

这解决了「grep 超时」的判断难题：可能是因为工具性能问题，也可能只是代码库太大导致模型查询低效。**只有当错误率显著偏离该工具+该模型的基线时，才触发异常警报。**

### 上下文腐烂的量化发现

通过工具错误率追踪，Cursor 发现：工具调用错误累积导致的「上下文腐烂」是可量化的。异常检测让这个问题被及时发现，而不是等到用户反馈才发现质量下降。

Cursor 原文：

> "Though metrics like tool call volume and error rate don't directly measure whether the agent did a good job, they act as indicators that can point to a broader issue."

---

## 第三层测量：A/B 测试基础设施

### 在线实验：Side-by-side 部署

Cursor 运行在线实验，将两个或多个 Harness 变体并排部署，A/B 测试真实使用。测试指标包括：

- **延迟（Latency）**
- **Token 效率（Token efficiency）**
- **工具调用次数（Tool call count）**
- **缓存命中率（Cache hit rate）**

这些是方向性指标，但仍然不够——无法直接回答「Agent 是否真的把工作做好」这个模糊但重要的问题。这才引出了 Keep Rate 和用户满意度语义分析。

---

## 自动化软件工厂：Harness 改进的执行闭环

### 每周自动化循环

Cursor 实现了一个自动化软件工厂：

1. **运行自动化 Agent**：配备专门处理日志分析的 Skill
2. **分析日志**：Agent 学习如何搜索日志，找出新的或最近激增的问题
3. **创建工单**：在 backlog 中创建或更新工单用于调查
4. **触发修复**：利用 Cloud Agents 批量推动修复，可以从 Linear 直接触发

Cursor 原文：

> "We also run a weekly Automation equipped with a skill that teaches the model how to search through our logs, surface issues that are new or recently spiked, and create or update tickets in a backlog with an investigation. We lean heavily on Cloud Agents to kick off fixes for many issues at once, and can even trigger them directly from Linear."

### 结果：一轮冲刺将意外工具调用错误降低一个数量级

在 2026 年初的一轮聚焦冲刺中，Cursor 将「意外工具调用错误」降低了一个数量级。**这不是手工修复的结果，而是自动化循环持续运行的结果。**

---

## 中途对话模型切换的工程挑战

### 问题描述

当用户中途切换模型时，Cursor 会自动切换到该模型对应的 Harness（包含定制的 prompts 和工具集）。但新模型面对的是由另一个模型生成的对话历史，这会导致分布偏移问题。

### Cursor 的解法

**解法一：自定义指令引导**

添加自定义指令，告诉模型「你正在从另一个模型手中接管对话」。指令还引导模型避免调用那些出现在对话历史中但不在自己工具集中的工具。

**解法二：对话摘要缓解缓存惩罚**

缓存是按提供商和模型特定的，切换意味着缓存未命中，首轮变慢且成本更高。Cursor 尝试在切换时对对话进行摘要，提供一个干净的摘要来减少缓存惩罚。

但如果用户正处于复杂任务深处，摘要可能丢失重要细节。

**Cursor 的实际建议**：除非有明确理由，否则建议在一个对话中保持使用同一模型。

**替代方案：Subagent**

绕过中途切换挑战的另一种方法是使用 Subagent——它从全新的上下文窗口开始。Cursor 最近为用户增加了直接要求用特定模型运行 Subagent 的能力。

---

## 上下文窗口的演进：从 Guardrail 到动态上下文

### 2024 年底的初始方法

2024 年底 Cursor 首次开发编码 Agent 时，模型在自主选择上下文方面差得多，团队投入大量上下文工程工作创建 Guardrail：

- 每次编辑后向 Agent 展示 lint 和类型错误
- 当 Agent 请求的行数太少时重写其文件读取
- 甚至限制 Agent 一次调用的最大工具数量

### 现在的状态

**大部分 Guardrail 已经移除。**

现在只保留一些有用的静态上下文（如操作系统、git 状态、当前和最近查看的文件），但通过增加模型能力，改为提供动态上下文——由 Agent 在工作时动态拉取。Cursor 之前有文章深入探讨过动态上下文发现技术。

Cursor 原文：

> "We still include some useful static context (e.g., operating system, git status, current and recently viewed files). But we've adapted to increasing model capability by knocking down guardrails and providing more dynamic context, which can be fetched by the agent while it works."

### 上下文焦虑（Context Anxiety）

Cursor 观察到一个有趣的现象：某些模型会表现出「上下文焦虑」——当上下文窗口填充时，模型开始拒绝工作，声称任务太大。通过 Prompt 调整减少了这种行为。

这与 Anthropic 之前提到的「上下文焦虑」问题呼应，但 Cursor 给出的是自己的缓解经验。

---

## 未来：Harness 是多 Agent 协调的核心

### 多 Agent 时代的 SE 未来

Cursor 认为 AI 辅助软件工程的未来是多 Agent 的：

- **规划 Agent**：负责任务规划
- **快速编辑 Agent**：负责快速文件修改
- **调试 Agent**：负责调试和修复

每个 Agent 专注于自己最擅长的事情，而不是所有事情都通过单一 Agent 处理。

### 这本质上是一个 Harness 挑战

Cursor 指出，关键在于 Harness 层：

> "The system needs to know which agent to dispatch, how to frame the task for that agent's strengths, and how to stitch the results into a coherent workflow. The ability to orchestrate that kind of coordination will live in the harness rather than any single agent."

**Harness 的角色从「工具包装」演变为「多 Agent 协调器」**。这意味着 Harness 工程的重要性只会增加，不会减少。

---

## 对比：Anthropic 的做法

Anthropic 在 April 2026 Postmortem 中强调的是「配置变更的系统性风险」——配置变更前后的回归测试、多层测试失败模式分析。

Cursor 的做法更接近「在线实验」——大量依赖 A/B 测试和在线指标，通过持续的小幅改进迭代积累优势。

两者代表两种不同的 Harness 改进哲学：

| 维度 | Cursor | Anthropic |
|------|--------|-----------|
| **改进驱动** | 在线实验 + A/B 测试 | 配置变更前的系统性验证 |
| **测量体系** | Keep Rate、用户满意度语义分析 | 离线 eval + 质量回归指标 |
| **自动化程度** | 高（每周自动化循环） | 中（配置变更审批流程） |
| **错误处理** | per-tool per-model 异常检测 | 多层测试 + postmortem |

Cursor 的方法更适合「快速迭代、持续测量」，Anthropic 的方法更适合「高风险变更前的严格验证」。

---

## 结论

Cursor 的《Continually improving our agent harness》揭示了 **Harness 工程的测量驱动本质**：

1. **Keep Rate + 用户满意度语义分析**：将「Agent 质量」分解为可量化的结果指标
2. **Per-tool per-model 异常检测**：用基线对比捕捉回归，比绝对阈值更准确
3. **A/B 测试基础设施**：让每个决策都有数据支撑，而不是靠直觉
4. **自动化软件工厂**：将改进闭环自动化，不用人工干预每个修复
5. **Harness 角色演进**：从「工具包装」到「多 Agent 协调器」

**没有测量就没有改进。** 这是 Harness 工程的第一性原理。