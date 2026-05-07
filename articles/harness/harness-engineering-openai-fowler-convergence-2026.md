# Agent Harness 工程：从OpenAI实战到Fowler框架的系统性解读

## 核心论点

Harness Engineering 不是"给 Agent 加几个工具"那么简单。OpenAI 的五个月实战（0 行人写代码，百万行程序）和 Martin Fowler 的分析框架 convergence 在同一个结论上：**Agent 的可靠性由 Harness 决定，而非模型本身**；构建 Harness 是一门持续的工程实践，不是一次性配置。

---

## 1. 为什么这个问题在 2026 年变得无法回避

2026 年，AI Coding Agent 已经进入生产环境。但行业普遍存在一个认知错位：把 Agent 能力不足归咎于模型，而忽略了**Harness 层**的决定性作用。

Anthropic 的 2026 Agentic Coding Trends Report 明确指出：

> "Harness setup alone can swing benchmarks by 5+ percentage points."
> — [Anthropic: 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)

这句话的深层含义是：**换了更好的模型，Harness 设计差依然会让你失望；但一个设计精良的 Harness，可以让普通模型超越预期**。这不是理论推断——LangChain 的案例显示，光优化 Harness 就让他们的 Coding Agent 从第 30 名跃升至 Terminal Bench 2.0 前五，没有换模型。

当 Agent 开始真正替代人类工程师执行长时间自主任务时，这个认知转变就从"学术讨论"变成了"生死攸关"。

---

## 2. OpenAI 的实证：五个月，0 行人写代码

### 2.1 实验设定与惊人结果

OpenAI 的 Harness Engineering 文章记录了一次极端实验：在五个月内，用完全由 Codex 生成的代码构建一个内部产品（每日内部用户 + 外部 alpha 测试者），**人类工程师直接贡献的代码行数为零**。

结果：
- 约 **100 万行代码**（应用逻辑、基础设施、工具、文档、CI 配置）
- 约 **1500 个 PR** 合并
- 团队从 3 人增长到 7 人
- 平均每人每天 **3.5 个 PR**，且随着团队成长吞吐量反而上升
- 人类从未直接审查代码（Agent-to-Agent review 是常态）
- 单次 Codex 运行时常高达 **6 小时**（通常在人类睡眠时运行）

### 2.2 "Humans Steer, Agents Execute" 的真正含义

OpenAI 将此哲学总结为："人类掌舵，Agent 执行。"但实战经验揭示了这句话的工程内涵：

> "Humans interact with the system almost entirely through prompts: an engineer describes a task, runs the agent, and allows it to open a pull request."
> — [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)

这不是说"写好 Prompt 就够了"。实战中，人类工程师的核心工作变成了：

1. **识别能力缺失**：当 Agent 失败时，问题几乎从不是"再试一次"，而是"缺少什么能力"
2. **让能力对 Agent 可见**：将工具、抽象、内部结构构建到 Agent 可访问的形式中
3. **构建反馈循环**：让 Agent 能自我修正，而非依赖人类介入每个环节

关键在于：人类工程师不再写代码，而是**构建 Agent 能工作的环境**。

### 2.3 教训一：不要把 AGENTS.md 当作百科全书

这是 OpenAI 最重要的实战经验之一。

他们最初尝试了"一个大 AGENTS.md"的方案，效果符合预期地糟糕：

| 问题 | 机制 |
|------|------|
| 上下文拥挤 | 巨型指令文件挤占了任务、代码和相关文档的空间 |
| 引导失效 | 当所有内容都标记为"重要"时，就没有重点了 |
| 内容腐化 | 单体手册迅速变成过时规则的坟墓 |
| 不可验证 | 单个文件无法进行机械检查（覆盖率/新鲜度/所有权） |

他们的解决方案是把 **AGENTS.md 降级为目录**，真正的知识存储在 `docs/` 目录中：

> "Instead of treating AGENTS.md as the encyclopedia, we treat it as the table of contents."
> — [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)

一个约 100 行的 AGENTS.md 作为入口索引，指向 docs/ 中的深层文档：架构文档、质量文档、计划文档。**渐进式披露**（Progressive Disclosure）在这里不是最佳实践，而是避免 Agent 上下文超载的必要机制。

### 2.4 教训二：让应用本身对 Agent 可见

随着代码吞吐量增加，人类 QA 能力成为瓶颈。他们的解决方案是让**应用 UI、日志、指标本身对 Codex 可读**：

- 应用支持 per-git-worktree 启动，Codex 可以为每个变更启动一个独立实例
- Chrome DevTools Protocol 集成到 Agent 运行时，支持 DOM snapshots、截图、导航
- 日志、指标、traces 通过本地可观测性栈暴露给 Codex（LogQL、PromQL 查询）
- Agent 可以直接查询："确保服务启动在 800ms 内完成"——这类请求现在变得可操作了

**这揭示了一个关键的设计原则**：如果你希望 Agent 理解你的系统，你必须把系统构建成 Agent 能理解的形式。Google 的 Azure SRE Agent 也印证了这一点——将所有内容作为文件暴露（源代码、runbook、查询 schema、历史调查笔记）比专用工具效果更好，Intent Met 分数从 45% 升至 75%。

### 2.5 教训三：用结构性测试和 Linter 替代架构评审

在人类工程中，架构约束通常被认为是"重要但不紧急"的，被推迟到有大量工程师时才实施。但 OpenAI 的经验证明：**在 Coding Agent 时代，架构约束是前提条件，而非奢侈品**。

他们构建了一个严格的应用架构模型：每个业务域被划分为固定的一组层（Types → Config → Repo → Service → Runtime → UI），层间依赖方向被严格验证。这些约束通过**自定义 Linter**（由 Codex 生成！）和**结构性测试**来机械执行。

关键机制：错误消息被设计为向 Agent 上下文中注入修复指令——不是告诉 Agent "你违反了什么规则"，而是告诉它"如何修正这个问题"。

> "Agents are most effective in environments with strict boundaries and predictable structure."
> — [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)

### 2.6 教训四：引入"Entropy Management"——自动化的代码垃圾回收

完全 Agent 生成代码带来的新问题是：**Codex 会复制已有的模式，包括不均匀或次优的模式**。这导致技术债务随时间积累。

他们的解决思路类似"垃圾回收"：

- 将运营原则编码为机械性规则（例如：优先共享工具包而非手写辅助函数；数据处理必须有边界验证）
- 定期运行的 Codex 任务扫描这些偏差、更新质量评分、开启定向重构 PR
- 大部分可以在不到一分钟内审阅完毕，然后自动合并

> "Technical debt is like a high-interest loan: it's almost always better to pay it down continuously in small increments than to let it compound."
> — [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)

### 2.7 跨越临界点：端到端自主功能驱动

在五个月后，Codex 跨越了一个有意义的临界点：给定一个单一的 Prompt，Agent 现在可以：

1. 验证代码库当前状态
2. 重现报告的 bug
3. 录制展示失败的视频
4. 实现修复
5. 通过驱动应用来验证修复
6. 录制展示解决方案的视频
7. 开启 Pull Request
8. 响应 Agent 和人类的反馈
9. 检测并修复构建失败
10. **只在需要判断时才升级给人类**
11. 合并变更

这不代表所有场景都适用——它高度依赖于特定的代码库结构和工具。但它指向了一个方向：**当反馈循环完整时，Agent 可以实现端到端自主**。

---

## 3. Martin Fowler 的分析框架：Feedforward + Feedback

### 3.1 核心框架：Guide 与 Sensor

OpenAI 的经验是实证性的，而 Martin Fowler 在他的 Harness Engineering 文章中提供了系统性的分析框架，两者的结论形成了 strong convergence。

他将 Coding Agent 的 Harness 分解为两种控制机制：

**Guide（Feedforward Controls，前馈控制）**：
- 在 Agent 行动**之前**引导它
- 目标是在第一次尝试时就提高得到好结果的概率
- 示例：AGENTS.md 中的编码约定、引导新项目初始化的 Skill

**Sensor（Feedback Controls，反馈控制）**：
- 在 Agent 行动**之后**观察它
- 帮助 Agent 自我修正
- 特别强大的形式：当传感器输出针对 LLM 消费优化时——例如包含修正指令的自定义 Linter 消息（这是一种正向的 prompt 注入）

> "Separately, you get either an agent that keeps repeating the same mistakes (feedback-only) or an agent that encodes rules but never finds out whether they worked (feedforward-only)."
> — [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)

### 3.2 执行类型：Computational vs Inferential

Guide 和 Sensor 都可以通过两种方式执行：

| 类型 | 特性 | 示例 | 适用场景 |
|------|------|------|---------|
| **Computational（计算型）** | 确定性，快速，CPU 执行 | 测试、Linter、类型检查、结构分析 | 每次变更都应运行，覆盖代码结构检查 |
| **Inferential（推理型）** | 语义分析，AI 代码评审，LLM-as-Judge，较慢且非确定性 | AGENTS.md 指导、AI 辅助代码审查 | 需要语义判断的场景，更昂贵但更强大 |

OpenAI 的实战完全印证了这个区分。他们的"Entropy Management"是 Computational Feedback（结构性测试 + Linter）；但他们的"Agent review"需要 Human-in-the-loop 或额外的 Agent——这是 Inferential Feedback。

### 3.3 三类 Regulation Categories

Fowler 进一步将 Harness  regulation 分为三个维度，每个维度的 harnessability 和 complexity 各不相同：

**① Maintainability Harness（可维护性 Harness）**
- 目标：调节代码质量和内部一致性
- 最容易实现：有大量现成的确定性工具
- Computational Sensor 可靠捕获结构性坏味道（重复代码、循环复杂度、缺失测试覆盖、架构漂移）
- Inferential Sensor 可以部分处理需要语义判断的问题（语义重复代码、冗余测试），但成本高且非确定性

**② Architecture Fitness Harness（架构Fitness Harness）**
- 目标：定义和检查应用的架构特征（相当于 Fitness Functions）
- 示例：描述性能需求的 Skill + 性能测试反馈；描述可观测性编码约定的 Skill + 调试说明
- 中等复杂度：需要为特定架构目标设计专门的 Guide 和 Sensor

**③ Behaviour Harness（行为 Harness）**
- 目标：指导和应用功能行为
- **最难实现**：目前最薄弱环节
- 当前常见模式：功能规格（feedforward）+ 检查 AI 生成的测试套件是否通过（feedback）
- 问题：这种模式对 AI 生成测试的质量有很高的信任度，但这个信任度目前还不太站得住脚

> "Correctness is outside any sensor's remit if the human didn't clearly specify what they wanted in the first place."
> — [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)

---

## 4. 两个视角的 Convergence：Harness Engineering 的完整图景

OpenAI 的实证 + Fowler 的框架，揭示了 Harness Engineering 的完整图景：

### 4.1 Harness 是控制论系统，不是配置清单

Fowler 明确指出 Harness 类似于**控制论调节器（cybernetic governor）**：

```
输入（目标状态）→ Harness（Guide + Sensor）→ Agent 行为 → 反馈 → 调节
```

OpenAI 的实践完全符合这个模型：他们的 Guide（AGENTS.md、Skills、Linter）设定目标状态；他们的 Sensor（测试套件、Entropy Management Agent）持续检测漂移并驱动修正。

### 4.2 "渐进式披露"是 Harness 的核心设计原则

OpenAI 的最大教训之一——不要把所有指令塞进一个 AGENTS.md——与 Fowler 的"Keep Quality Left"原则形成呼应：

- **渐进式披露**是避免上下文拥挤的必要手段
- **Quality Left**（质量左移）意味着越早检测问题成本越低——这要求在变更生命周期中分布 Feedforward 和 Feedback

### 4.3 Harness 是分层系统，不是单点工具

从 OpenAI 的经验和 Fowler 的框架，我们可以识别出四层 Harness：

| 层次 | 功能 | 示例 |
|------|------|------|
| **Layer 1: Context Delivery** | 把正确的上下文在正确的时间给 Agent | AGENTS.md 索引、docs/ 知识库、Skill metadata |
| **Layer 2: Constraint Enforcement** | 机械性规则验证，防止漂移 | Linter、结构性测试、架构边界检查 |
| **Layer 3: Self-Correction Loop** | Agent 能发现并修正自己的错误 | Entropy Management Agent、Self-verification prompts |
| **Layer 4: Goal Alignment** | 确保 Agent 的目标与人类期望一致 | End-to-end autonomous driving（OpenAI 的临界点）|

### 4.4 Harness Engineering 是持续实践，不是一次性配置

OpenAI 五个月的实战揭示了一个关键发现：

> "Building software still demands discipline, but the discipline shows up more in the scaffolding rather than the code."
> — [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)

这不是一个"设置好就忘掉"的工作。Harness 需要**持续迭代**：每当问题多次出现，Feedforward 和 Feedback 都需要改进。OpenAI 的团队曾经每周五花 20% 的时间手动清理"AI 垃圾"，这不可扩展——所以他们构建了自动化的 Entropy Management。

---

## 5. 工程实践建议

基于 OpenAI 实证和 Fowler 框架的 convergence，以下是构建 Production Harness 的关键实践：

### 5.1 Context 架构：从"大 AGENTS.md"到"知识图谱"

**错误模式**：把所有规则塞进一个 AGENTS.md 文件。

**正确模式**：
- AGENTS.md 作为**目录**（~100 行），指向 docs/ 中的深层文档
- 按主题分离知识：架构文档、质量文档、计划文档、设计决策
- 用 Linter 验证知识库的新鲜度和一致性

### 5.2 架构防护：结构性测试 + 自定义 Linter

**必须项**：不要假设 Agent 会自发保持架构一致性。

LangChain 的案例（仅改 Harness，从 Rank 30 到 Top 5）证明：**架构约束 + 验证循环 = 主要性能杠杆**。

实践建议：
- 定义清晰的架构层次和依赖方向
- 用 ArchUnit 或类似工具强制执行模块边界
- 自定义 Linter 包含**修复指令**（而非仅报告违规）

### 5.3 Self-Correction 循环：让 Agent 修正自己的输出

**关键机制**：
- Computational Feedback：Linter、测试、结构检查（每次 PR 运行）
- Inferential Feedback：AI 代码评审（较高成本，周期性运行）
- 连续漂移监控：Entropy Management Agent（定期扫描并开启修复 PR）

### 5.4 Behaviour Harness：目前最弱的环节

Fowler 明确指出："Correctness is outside any sensor's remit if the human didn't clearly specify what they wanted."

建议：
- 功能规格必须**具体且可验证**，而非模糊的需求描述
- 将 AI 生成测试与 Human-approved fixtures 结合（ Thoughtworks 同事的实践）
- 对于关键功能，考虑使用 formal verification 或 property-based testing 作为额外保障

### 5.5 监控"Harness 本身的健康度"

Fowler 提出的一个被普遍忽视的问题：**谁来监控监控者？**

我们需要一种评估 Harness 覆盖率和质量的方法，类似于代码覆盖率或 mutation testing 对测试的作用：

- 追踪 Feedback Sensor 的触发频率（从不高频触发可能是高质量，也可能是检测机制不足）
- 记录 Guide 和 Sensor 之间的矛盾（指令和反馈信号指向不同方向时会发生什么）
- 定期审计 Harness 的 coherence（随着时间推移，Guide 和 Sensor 是否保持同步？）

---

## 6. 结论与启示

OpenAI 的五个月实证和 Martin Fowler 的分析框架 convergence 揭示了一个清晰的结论：

**Harness Engineering 是 AI Agent 可靠性的决定性因素，而不是模型的附属品。**

这个结论有几个重要的 implication：

1. **购买更好的模型不会解决 Harness 设计差的问题**。Anthropic 的数据表明，Harness 配置可以将基准测试提高 5+ 个百分点——这是 Harness 的直接贡献。

2. **Harness 不是一次性配置，而是持续工程实践**。OpenAI 的 Entropy Management 和 Fowler 的"steering loop"都表明，随着问题模式的出现，Harness 需要不断迭代。

3. **Harness 的设计原则是控制论，而非工具列表**。Feedforward + Feedback 的双轨控制是核心框架；渐进式披露是避免上下文拥挤的必要手段。

4. **最难的挑战是 Behaviour Harness**。目前这个领域最薄弱——Functional Specification 如何具体化、如何验证 AI 生成测试的质量，都还需要更多工程实践来解决。

> "Our most difficult challenges now center on designing environments, feedback loops, and control systems that help agents accomplish our goal."
> — [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)

**下一步**：对于正在构建或使用 Coding Agent 的团队，问题的关键不是"你的模型是什么"，而是"你的 Harness 如何设计"。

---

## 参考来源

- [OpenAI: Harness Engineering — leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- [Martin Fowler: Harness Engineering for coding agent users](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
- [Anthropic: 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)
- [LangChain: Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
- [Microsoft: How We Build Azure SRE Agent with Agentic Workflows](https://techcommunity.microsoft.com/blog/appsonazureblog/how-we-build-azure-sre-agent-with-agentic-workflows/4508753)
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
