# 第三代 AI 软件开发：云端 Agent 工厂范式的兴起

> 本文明的真正意义：不是工具进化，而是人类角色的根本性重构

## 引言

2026 年 2 月 26 日，Cursor 在官方博客发表了一篇标题平淡的文章，却预言了软件产业最深刻的一次变革：**「The third era of AI software development」**。

文章的核心主张并非什么惊人之语——它只是宣告了一个已在发生的事情：

> "Many of us at Cursor are already working this way. More than one-third of the PRs we merge are now created by agents that run on their own computers in the cloud."

但这句话的重量远超字面。三分之一的 PR 由云端 Agent 自动创建，这意味着 **软件生产的单位已从「人/日」切换到了「Agent/任务」**。这不是效率提升，而是范式转移。

本文要回答的问题是：**「第三代」究竟是什么，它与前两代的本质区别在哪里，以及这一转变对 Agent 工程实践意味着什么。**

---

## 三代论的结构性意义

Cursor 的「三代论」不是营销叙事，而是对实际产业演进的精确建模：

| 阶段 | 时期 | 核心隐喻 | 人类角色 | Agent 能力边界 |
|------|------|----------|----------|----------------|
| **第一代**：Tab | 2023-2024 | 自动化打字机 | 每行代码的决策者 | 低熵重复填充 |
| **第二代**：Synchronous Agents | 2024-2026 | 异步助理 | 每步操作的审核者 | 多步规划，但仍需同步交互 |
| **第三代**：Cloud Agents + Factory | 2026+ | 自动化工厂 | 工厂主（定义问题+设置标准） | 并行、长程、异步、自主交付 |

三代论的核心不是「Agent 越来越聪明」，而是 **人类与 Agent 的交互模式发生了结构性改变**：从「每步指导」到「最终验收」，这意味着人类从执行者变成了架构师。

---

## 第二代的瓶颈：为什么同步 Agent 不是终态

Cursor 博客中有一句关键的话：

> "But this form of real-time interaction, combined with the fact that synchronous agents compete for resources on the local machine, means it is only practical to work with a few at a time."

这句话指出了同步 Agent 范式的两个根本性瓶颈：

### 2.1 资源竞争：本地计算的枷锁

当 Agent 运行在用户本地机器上时，它与用户共享 CPU、内存和网络带宽。用户打开 IDE、运行测试、编译项目——这些操作都在抢占 Agent 的资源。在 Cursor 的数据中，同步 Agent 只能同时运行「几个」，这个数字的上限不是模型能力决定，而是 **本地硬件资源的天花板**。

这意味着：

- 任务并行度受限于物理硬件
- Agent 的「思考时间」直接占用用户等待时间
- 多个长程任务无法同时进行

### 2.2 人机同步：人类成为 Bottleneck

同步 Agent 的本质是「人类每步等待 Agent 回复 → 人类审核 → 人类批准 → Agent 继续」。这在结构上将人类变成了 Agent 工作流中的 Gatekeeper。Cursor 明确指出：

> "The human role shifts from guiding each line of code to defining the problem and setting review criteria."

但这个转变只有在 Agent 不再需要人类同步参与才能实现。第二代 Agent 之所以做不到，是因为 **Agent 返回的是 diff（代码变更）——这需要人类重新理解上下文才能评估**。

---

## 第三代的核心机制：云端 Agent + Artifacts

Cursor 对第三代的核心设计是「每个 Agent 运行在独立虚拟机上，交付的是 artifacts（工件）而非 diffs」。这个设计的工程含义远超表面。

### 3.1 独立 VM = 完全隔离的执行环境

在同步 Agent 模式下，Agent 在用户本地环境中操作。这意味着：

- Agent 的工具调用受本地权限约束
- 环境配置与用户共享，难以标准化
- 多个 Agent 并行会竞争本地资源

云端 Agent 的解法是 **每个任务分配独立 VM**。这带来了几个关键改变：

**资源弹性**：任务 A 用 8 核 32G，任务 B 用 2 核 8G，按需分配，互不干扰。

**环境标准化**：VM 可以预先配置好 Agent 所需的全部依赖和环境变量，每次启动都是一致的基线状态。

**并行可行**：10 个任务 → 10 个 VM → 完全并行，人类可以同时启动所有任务然后去做其他事情。

### 3.2 Artifacts > Diffs：评估成本的质变

Cursor 提出的核心产品洞察是：**Agent 应该交付可预览的 artifacts（视频、日志、Live Preview），而不是需要人类逐行理解的代码 diffs**。

这个设计背后的逻辑是：

| 输出形式 | 人类评估所需时间 | 认知负担 | 适用场景 |
|----------|-----------------|----------|----------|
| **Diffs** | ~5-15 分钟理解上下文 | 高（需要重新构建上下文） | 小改动、同步 review |
| **Artifacts（截图/视频/预览）** | ~10-30 秒 | 低（直接感知结果） | 大型任务、异步 review |
| **Live Preview** | 实时 | 极低（直接交互） | UI/视觉类任务 |

Artifact 的本质是 **将代码变更「编译」成人类可直接评估的结果**。这消除了人类重新理解代码上下文的成本——你不需要理解 Agent 怎么做的，你只需要看它做出来的结果是否正确。

Cursor 在博客中描述的转变是：

> "They spend their time breaking down problems, reviewing artifacts, and giving feedback."

人类的角色从「代码评审者」变成了「产品验收者」。

---

## 工厂范式的工程含义：从 Agent 到 Fleet

Cursor 博客中的一句话点明了核心：

> "Cursor is no longer primarily about writing code. It is about helping developers build the factory that creates their software."

这意味着 **Agent 不再是工具，而是工厂的机械臂**。「工厂」这个隐喻的工程含义是：

### 4.1 Fleet Management：多 Agent 协调

当开发者可以同时启动多个云端 Agent 时，核心问题变成了 **如何管理 Agent 的生命周期**——分配任务、监控进度、处理失败、汇总结果。

这对应 Anthropic 在「Scaling Managed Agents」中描述的「Many brains, many hands」架构：

```python
# Anthropic 架构中的 Brain/Hands 分离
execute(name, input) → string  # 每个 sandbox 是一个可按需分配的 "hand"
```

Cursor 的云端 Agent 实际上是在应用相同的设计哲学：**Agent（brain）不再绑定到特定的执行环境（hand），而是通过标准化的接口与可插拔的环境交互**。

### 4.2 质量门禁：从人工 Review 到 Criteria-Based Validation

当 Agent 以 artifacts 而非 diffs 交付时，人类验收的方式也必须改变。Cursor 描述的新工作流是：

> "They spin up multiple agents simultaneously instead of handholding one to completion."

这意味着 **质量控制从「逐行检查」变成了「定义验收标准」**。开发者需要明确回答：
- 这个任务的完成标准是什么？
- 什么样的输出算是「正确」？
- 什么样的结果是「不可接受」？

这与 Augment Code 的 AGENTS.md 研究形成了有趣的呼应：好的配置文档（AGENTS.md/Definition of Done）相当于给 Agent 一个质量门禁标准，当 Agent 自主运行在云端时，这个门禁变得尤为重要。

### 4.3 容错与恢复：工业级可靠性的要求

Cursor 提到了一个小问题，但这个问题的工程重量被严重低估：

> "At industrial scale, a flaky test or broken environment that a single developer can work around turns into a failure that interrupts every agent run."

在工厂范式中，**一个 flaky test 不是「麻烦」，而是「生产线停产」**。当 Agent 24 小时无人值守运行时，所有在人工操作环境下可以接受的「小问题」都会变成系统性风险。

这对应 Anthropic 在「Harness Design for Long-Running Applications」中反复强调的原则：harness 必须能够优雅地处理失败、自动重试、在必要时回滚状态。这在云端 Agent 工厂中变成了基础设施级别的需求。

---

## Anthropic 的镜像：第三代 Agent 工程的另一个视角

Cursor 的「三代论」在 Anthropic 的工程博客中能找到清晰的镜像。Anthropic 在「Scaling Managed Agents」中描述的架构设计，本质上是在解决同一个问题——**如何让 Agent 能够长程、可靠、规模化地运行**。

Anthropic 提出的 Brain/Hands/Session 分离架构：

> "We virtualized the components of an agent: a session (the append-only log of everything that happened), a harness (the loop that calls Claude and routes Claude's tool calls to the relevant infrastructure), and a sandbox (an execution environment where Claude can run code and edit files)."

这个设计的核心洞察是 **接口稳定性 > 实现稳定性**。Operating Systems 能够存活几十年，是因为它们把硬件抽象成了稳定的接口（read/write/execute），而不是依赖于某个特定的硬盘型号。

同理，Cloud Agent 工厂的核心不是 Agent 有多聪明，而是 **Agent 与环境之间的接口是否足够稳定和通用**。当这个接口稳定后，底层的 Agent 实现（Claude Code / Codex / 任何未来的 Agent）就可以自由替换，而不影响上层的工作流。

---

## 「第三代」对 Agent 工程实践的启示

Cursor 的「第三代」不是一个需要等待的未来——它已经在 Cursor 内部发生了（35% PR 由云端 Agent 创建）。这意味着 Agent 工程的实践者现在就需要思考以下问题：

### 5.1 你的工具还能在工厂环境中工作吗？

Cursor 提到的关键挑战是：

> "More broadly, we still need to make sure agents can operate as effectively as possible, with full access to tools and context they need."

当前的很多 Agent 工具（主要是本地 CLI 工具）是针对本地开发环境设计的。当 Agent 迁移到云端 VM 后：

- 文件系统路径假设不再成立
- 本地进程调用（subprocess）不再可用
- GUI 工具无法在无头环境中运行

这直接对应 Anthropic 在 Managed Agents 中解决的「pet vs cattle」问题：云端 Agent 需要的工具必须能在标准化、可复原的云端环境中运行。

### 5.2 你准备好异步验收了吗？

当 Agent 以 artifacts 交付而非 diffs 时，开发者的验收流程必须重新设计：

**传统流程**：
```
Human → 提出需求 → 等待 Agent 完成 → 逐行 Review diff → 反馈 → 重复
```

**第三代流程**：
```
Human → 定义问题和验收标准 → 启动多个 Agent → 做其他事情 → 收到通知 → 审查 artifacts → 通过或打回
```

这个转变要求开发者具备更强的 **问题定义能力**（你需要明确知道什么是「完成」），以及 **更放手的心态**（你不能控制每一步具体怎么实现）。

### 5.3 你的安全模型准备好了吗？

Anthropic 在「Scaling Managed Agents」中明确指出了这个挑战：

> "In the coupled design, any untrusted code that Claude generated was run in the same container as credentials—so a prompt injection only had to convince Claude to read its own environment."

当 Agent 运行在云端工厂中时，安全边界的设计会直接影响 Agent 能够运行的场景。云端 Agent 工厂需要：

- 严格的凭证隔离（凭证永远不在 Agent 可读的 sandbox 中）
- 网络边界的精细化控制（Agent 只能访问任务所需的后端服务）
- 完整的操作审计（所有 Agent 行为都有可追溯的日志）

这正是 OpenAI 在「Running Codex Safely at OpenAI」中描述的核心挑战：企业部署 Agent 的安全要求与 Agent 的自主能力之间需要精确的平衡。

---

## 结论：工厂范式的真正意义

Cursor 的「第三代」文章最深刻的一句话被淹没在文中段落的末尾：

> "A year from now, we think the vast majority of development work will be done by these kinds of agents."

这句话如果预测准确，意味着软件开发产业的生产函数即将改变：

- 产出不再受限于工程师数量
- 质量控制从「人工审查」转向「标准定义」
- 工程师的核心能力从「写代码」变成「设计问题」

但这个转变真正重要的不是「大部分代码由 Agent 写」，而是 **人类在软件开发中的角色发生了不可逆的改变**：

- 工程师从执行者变成架构师
- 验收从逐行审查变成标准定义
- 创新从「实现细节」迁移到「问题建模」

对于 Agent 工程实践者而言，这意味着 **现在投入精力学习的不是「如何使用 Agent」，而是「如何设计能让 Agent 自动运行的工厂」**——这也是 Cursor 将公司定位从「AI 编程工具」切换到「AI 软件工厂平台」的原因。

> "We think yesterday's launch of Cursor cloud agents is an initial but important step in that direction."

这句话的真正含义是：工具战争已经结束了，工厂战争才刚刚开始。

---

## 参考来源

> "When we started building Cursor a few years ago, most code was written one keystroke at a time. Tab autocomplete changed that and opened the first era of AI-assisted coding." — [The third era of AI software development](https://cursor.com/blog/third-era), Cursor Blog, Feb 26, 2026

> "Thirty-five percent of the PRs we merge internally at Cursor are now created by agents operating autonomously in cloud VMs." — [The third era of AI software development](https://cursor.com/blog/third-era), Cursor Blog, Feb 26, 2026

> "The human role shifts from guiding each line of code to defining the problem and setting review criteria." — [The third era of AI software development](https://cursor.com/blog/third-era), Cursor Blog, Feb 26, 2026

> "Cursor is no longer primarily about writing code. It is about helping developers build the factory that creates their software." — [The third era of AI software development](https://cursor.com/blog/third-era), Cursor Blog, Feb 26, 2026

> "We virtualized the components of an agent: a session, a harness, and a sandbox... The abstractions on top stayed stable while the implementations underneath changed freely." — [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents), Anthropic Engineering, Apr 8, 2026

> "We do not run Codex with open-ended outbound access. Our managed network policy allows expected destinations, blocks destinations we do not want Codex reaching, and requires approval for unfamiliar domains." — [Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/), OpenAI Blog, May 8, 2026

> "As coding agents like Codex become integrated into development workflows, security teams need tools specifically designed for managing this shift." — [Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/), OpenAI Blog, May 8, 2026