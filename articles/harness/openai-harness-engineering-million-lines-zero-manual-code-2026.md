# OpenAI Harness 工程实验：5 个月、百万行代码、零手写代码

> "Humans steer. Agents execute."
> — [OpenAI Harness Engineering Blog](https://openai.com/index/harness-engineering/)

## 背景：一次前所未有的工程实验

2025 年 8 月底，OpenAI 的一个工程团队在空仓库上开始了至今仍在进行的实验：用 **0 行手写代码** 构建一个内部产品。

五年后的今天，这个仓库包含约 **100 万行代码**，涵盖业务逻辑、基础设施、工具链、文档和内部开发工具。团队规模从最初的几人扩展到七名工程师。在整个开发过程中，人类从未直接提交过任何代码——每一行都来自 Codex。

> "We estimate that we built this in about 1/10th the time it would have taken to write the code by hand."
> — [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)

这不是概念验证。这是一个有**每日内部用户和外部 alpha 测试者**的真实产品，会打包、部署、出问题，然后被修复。唯一不同的是：所有代码都是 Codex 写的。

这个实验揭示了一个核心转变：**当软件工程团队的主要工作不再是写代码，而是设计环境、指定意图、构建反馈循环——工程本身的性质发生了根本变化。**

---

## 第一章：Agent-First 开发的工作重心转移

### 从"写代码"到"构建能力"

实验开始后，早期进展比预期**慢**。原因不是 Codex 能力不足，而是环境**定义不足**——Agent 缺乏所需的工具、抽象和内部结构来向高层目标推进。

关键洞察：**当进展卡住时，人类的反应几乎永远不是"再试一次"，而是"缺少什么能力，如何让 Agent 既能理解又能遵守这个能力"。**

这彻底改变了工程师的角色：

| 传统开发 | Agent-First 开发 |
|---------|----------------|
| 工程师写代码 | 工程师设计能力、规范和反馈循环 |
| 人类直接解决具体问题 | 人类识别缺失的能力，构建让 Agent 解决问题的环境 |
| 代码是主要输出 | **能力**是主要输出（工具、抽象、结构、CI 规则） |

> "The primary job of our engineering team became enabling the agents to do useful work."
> — [OpenAI](https://openai.com/index/harness-engineering/)

这一转变要求工程师具备一种全新的思维模式：不是"我会做什么"，而是"Agent 需要什么才能可靠地完成 X"。

### 深度优先的递归式构建

OpenAI 团队采用的工作方式是**深度优先**：将大目标分解为更小的构建块（设计、代码、审查、测试等），引导 Codex 构建这些块，然后使用它们解锁更复杂的任务。

这不是自上而下的架构设计，而是自底向上的能力积累。每解决一个问题，团队问的是：**"这个解决方案如何成为未来更复杂任务的基础？"**

这种模式的关键特征：
- **能力复用优先于一次性解决**：每个解决方案都要设计成能被未来任务复用的形式
- **环境构建优先于任务完成**：当任务失败时，几乎总是先去增强环境能力，而不是让 Agent 重试
- **反馈循环是核心基础设施**：让 Codex 能够自我审查和迭代

---

## 第二章：Agent 主导的知识管理体系

### "AGENTS.md 作为索引，而非百科全书"

Context 管理是大型复杂任务中 Agent 有效性的最大挑战之一。OpenAI 团队最早学到的教训之一是：

> "Give Codex a map, not a 1,000-page instruction manual."
> — [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)

他们尝试过"一个大 AGENTS.md 文件"的方式，结果在意料之中失败了：

- **Context 是稀缺资源**：一个巨大的说明文件会挤占任务、代码和相关文档的空间
- **过度指导等于无指导**：当所有事情都标记为"重要"时，Agent 无法判断优先级
- **知识快速腐化**：单一的说明文档变成过时规则的坟墓，Agent 无法判断哪些仍然有效
- **难以验证**：单一的大文件无法进行机械检查（覆盖率、新鲜度、所有权），漂移不可避免

解决方案是将 **docs/ 目录作为知识的系统记录**，而 AGENTS.md（约 100 行）作为**索引**存在。

### 知识库的分层结构

OpenAI 团队设计的仓库知识库包含以下层次：

```
docs/
├── design/              # 设计文档，含验证状态和核心信念定义
├── architecture/        # 顶层领域和包层次结构地图
├── quality/            # 产品质量等级和架构层评估，跟踪差距
└── plans/              # 执行计划（轻量的临时计划 vs 复杂工作的执行计划）

AGENTS.md               # 索引（~100行），包含指向更深层真实来源的指针
```

这种分层设计遵循**渐进式披露**原则：

> "Agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front."
> — [OpenAI](https://openai.com/index/harness-engineering/)

### 机械强制而非人工维护

团队通过两种机制保证知识库的有效性：

1. **专用 linter 和 CI 任务**：验证知识库是最新的、正确交叉链接的和结构正确的
2. **Doc-gardening Agent**：定期扫描过时或与实际代码行为不符的文档，并自动发起修复 PR

这解决了一个核心问题：当知识库靠人类维护时，它会因为人类认知负担而腐化；当知识库由 Agent 自我维护时，它能够保持与实际代码行为的一致性。

---

## 第三章：让应用层对 Agent 可见

### 扩展 Agent 的感知边界

当代码吞吐量增加后，团队发现**人类 QA 容量成为瓶颈**。解决方案不是增加更多人类 QA，而是让应用层本身对 Codex **直接可见**。

具体做法：

**UI 可操作性**：
- 每个 git worktree 可独立启动应用实例，Codex 可以为每个变更启动一个实例
- Chrome DevTools Protocol 被接入 Agent 运行时，支持 DOM snapshots、screenshots 和 navigation
- Codex 可以复现 bug、验证修复并直接推理 UI 行为

> "This enabled Codex to reproduce bugs, validate fixes, and reason about UI behavior directly."
> — [OpenAI](https://openai.com/index/harness-engineering/)

**可观测性栈**：
- Logs、metrics 和 traces 通过临时本地可观测性栈暴露给 Codex
- Codex 可以用 LogQL 查询日志，用 PromQL 查询 metrics
- 关键 prompt 变成可执行的约束（如"确保服务启动在 800ms 内完成"）

> "Agents can query logs with LogQL and metrics with PromQL. With this context available, prompts like 'ensure service startup completes in under 800ms' or 'no span in these four critical user journeys exceeds two seconds' become tractable."
> — [OpenAI](https://openai.com/index/harness-engineering/)

### 对工程实践的启示

这一设计背后的核心原则是：**Agent 能作用于什么，取决于什么对 Agent 可见**。

传统开发中，人类工程师通过日志、监控、调试工具来理解系统状态。而当 Agent 成为主要执行者时，这些工具必须被设计成 Agent 能够使用的方式——不仅仅是"能读取"，而是"能根据这些信息采取行动"。

这对工程实践意味着：
- 可观测性基础设施需要为 AI 消费而设计
- UI 测试需要通过 Agent 可执行的接口暴露
- 性能约束需要变成可验证的断言，而非模糊的质量目标

---

## 第四章：Agent-to-Agent 审查模式

### 消除人类 QA 瓶颈

随着代码产出的增加，人类 QA 容量成为瓶颈。团队采取的策略是**将几乎所有审查工作转移到 Agent-to-Agent 模式**。

典型工作流：

1. 人类描述任务 → 运行 Agent → Agent 打开 PR
2. Codex 被指示对自己的变更进行本地审查
3. 请求额外的特定 Agent 审查（本地 + 云端）
4. 响应人类或 Agent 的反馈
5. 迭代循环直到所有 Agent 审查者满意

这被团队称为 **Ralph Wiggum Loop**（引自一个不断重复"I'm helping"的角色）。

> "Humans may review pull requests, but aren't required to. Over time, we've pushed almost all review effort towards being handled agent-to-agent."
> — [OpenAI](https://openai.com/index/harness-engineering/)

### 人类审核的角色重新定义

在 Agent-to-Agent 主导的审查模式下，人类审核者变成了**异常处理者**而非**标准路径**：

- 当 Agent 审查者无法达成共识时，人类介入
- 当出现安全、合规或业务相关的判断时，人类介入
- 当系统出现未知模式时，人类介入判断

> "The agent-generated repository is optimized first for Codex's legibility." — OpenAI 强调"agent-legibility"成为设计原则：代码不只是为人类可读而设计，更为 Agent 可推理而设计。

这带来一个设计上的根本转变：**代码的结构和表述方式需要服务于 Agent 的推理模式**。一个对人类工程师清晰但 Agent 难以推理的代码结构，反而是次优的。

---

## 第五章：长时任务的可行性与反馈

### 6 小时连续运行

OpenAI 团队观察到 Codex 单次运行可以在单一任务上工作**长达 6 小时以上**——这通常发生在人类休息时。

> "We regularly see single Codex runs work on a single task for upwards of six hours (often while the humans are sleeping)."
> — [OpenAI](https://openai.com/index/harness-engineering/)

6 小时连续运行的能力意味着：
- **复杂的重构和跨多个子系统的工作**成为可能
- **夜间批量任务**成为实际的工程实践
- **深度调试**（需要多轮因果追溯的工作）不再受人类注意力限制

### 反馈回路的设计

长时任务的核心支撑是**可靠的反馈回路**：

- **增量验证**：每个子步骤完成后进行验证，而非在长序列末尾一次性检查
- **执行计划**：复杂工作被捕获在执行计划中，包含进度和决策日志，并 check-in 到仓库
- **持久化上下文**：活跃计划、已完成计划和已知技术债务都是版本控制的，并与代码同位置

这使得即使运行时间很长，Codex 也能保持在正确的轨道上，而不是在长序列中漂移。

---

## 核心洞察：Agent-First 开发的三大工程原则

### 1. 环境即产品

在传统开发中，环境（IDE、CI、基础设施）是支持工具。在 Agent-First 开发中，**环境本身成为主要产品**——人类工程师的输出不是代码，而是 Agent 能够高效工作的环境。

这意味着工程团队的 KPI 从"代码行数"转变为"Agent 完成任务的能力和质量"。

### 2. 知识管理是基础设施

知识库（docs/）不是文档工作，而是**使 Agent 能够推理业务领域的基础设施**。它的质量直接影响 Agent 的任务完成质量。

维护知识库的清洁度和准确性，需要与维护代码同等重要的工程纪律。

### 3. 可观测性是 Agent 的眼睛

如果 Agent 无法观察到系统的运行状态，它就无法在该状态上采取行动。让系统对 Agent 可见（通过日志、metrics、traces、UI 状态），是让 Agent 能够处理复杂任务的必要条件。

---

## 与其他 Harness 架构的对比

本文与本仓库中已有的几篇分析形成对照：

| 文章 | 核心主题 | 关键差异 |
|------|---------|---------|
| [OpenAI Agents SDK 2026 分析](./openai-agents-sdk-2026-model-native-harness-native-sandbox-2026.md) | Model-native harness 与原生沙箱 | 聚焦 SDK 层面的 harness 设计 |
| [Anthropic 双组件 Harness 分析](./anthropic-initializer-coding-agent-two-component-harness-2026.md) | Initializer + Coding Agent 双组件 | 聚焦 Agent 内部的职责分离 |
| [Claude Code Postmortem 分析](./anthropic-claude-code-april-2026-postmortem-engineering-alerts-2026.md) | 质量回归的工程警示 | 聚焦 harness 失效模式和修复 |

本文的独特贡献在于：**从组织流程和知识管理的宏观视角，分析 Agent-First 开发如何改变工程团队的运作方式**。它不关注单个 Agent 的架构设计，而是关注多个 Agent、人类工程师和知识系统如何协同工作。

---

## 结论与启示

OpenAI 的实验揭示了一个明确的方向：**当 Agent 变得足够可靠时，软件开发的工作重心将不可逆地转向"构建能力"而非"编写代码"**。

对于工程团队，这意味着：

- **重新定义工程师的核心能力**：不是"能写出好代码"，而是"能设计出让 Agent 可靠工作的环境"
- **投资知识管理作为竞争优势**：在 Agent-First 模式下，知识库的质量直接决定工程效率
- **将可观测性视为 Agent 的基础设施**：让系统状态对 Agent 可见是释放 Agent 能力的必要条件
- **设计 Agent-to-Agent 的协作模式**：人类从"执行者"变为"协调者"和"异常处理者"

> "Humans steer. Agents execute." 这个原则的深层含义是：人类的比较优势在于定义目标和判断价值，Agent 的比较优势在于大规模执行和信息处理。充分利用这种分工需要系统性地重新设计工程实践的每个环节。

---

**引用来源**：

- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — OpenAI Engineering Blog
- [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) — OpenAI Engineering Blog