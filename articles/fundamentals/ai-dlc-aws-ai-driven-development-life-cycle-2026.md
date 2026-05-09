# AI-DLC 方法论：AWS 开源的结构化 Agent 开发生命周期框架

> **核心问题**：当前 AI 辅助开发的最大问题不是「AI 能力不够」，而是「人类缺乏结构化方式来引导和约束 AI」。AI-DLC 提出了一种以方法论驱动的解决路径——将软件开发生命周期重构为「三个阶段、若干门控、人类始终在环」的结构化流程，让 AI coding agent 的输出从不可预测的「vibe coding」变为可预期、可控制、可审计的工程实践。
>
> **读完得到什么**：理解 AI-DLC 的核心理念（方法论优先、门控驱动、始终在环），三阶段各自解决的工程问题，以及它与现有 Agent 框架的本质区别——它不是又一个 Agent 框架，而是所有 Agent 框架之上的一层元方法论。

---

## 1. 为什么需要结构化的 Agent 开发方法论

### 1.1 Vibe Coding 的甜头与陷阱

AI coding agent 的出现让「vibe coding」成为可能——用自然语言描述需求，Agent 自动生成代码。Cursor 的 Subagent、Claude Code 的 autonomous mode、OpenAI Codex 的 agent loop 都让这个过程变得越来越顺畅。

但「vibe coding」有一个根本缺陷：**它把软件的正确性建立在 Agent 的上下文感知能力和当次推理质量上，而这两者都是高度不可预测的**。同一个需求，在不同的对话上下文、不同的 Agent 状态、甚至不同的对话顺序下，可能产出完全不同的结果。这不是模型的 bug，而是 vibe coding 范式本身的结构性问题——没有结构化的约束，Agent 的行为完全由概率决定。

> "Methodology first. AI-DLC is fundamentally a methodology, not a tool. Users shouldn't need to install anything to get started."
> — [AI-DLC README](https://github.com/awslabs/aidlc-workflows)

这句话击中了当前 AI coding tools 的核心问题：把工具做得很复杂，但方法论极度匮乏。Anthropic 的 Building Effective Agents、OpenAI 的 Harness Engineering、Martin Fowler 的 harness engineering 文章都在讨论同一件事——**Agent 的能力边界主要由周围的 scaffolding 决定，而不是模型本身**。AI-DLC 的回答是：这个 scaffolding 需要被结构化为一套方法论，而不只是各种工具和 prompt 的堆砌。

### 1.2 三个工程现实问题

**问题一：Context 累积导致推理质量下降**。Agent 在长会话中会积累大量上下文，这些上下文在多轮交互后会产生「context rot」——后续的推理质量下降，因为重要的工程约束被稀释在噪声中。

**问题二：人类无法真正「在环」**。当前的 AI coding tools 大多将人类放在 loop 之外——只在最终输出后给一个 review 的机会。但此时改动成本已经很高，如果输出的架构设计有根本性问题，review 阶段发现已经太晚了。

**问题三：缺乏跨平台的统一方法论**。Claude Code 用 `CLAUDE.md`，Cursor 用 Rules (`*.mdc`)，OpenAI Codex 用 `AGENTS.md`，Amazon Q Developer 用 Rules，Kiro 用 Steering Files——每个平台都有自己约定的配置/规则文件格式，但**没有任何方法论层来告诉 Agent 应该在什么阶段做什么、什么时候该停下来等人确认**。

---

## 2. AI-DLC 的三阶段架构

AI-DLC 将软件生命周期划分为三个阶段，每个阶段有明确的入口条件、产出物和退出门控。

### 2.1 Inception Phase：确定「做什么」和「为什么」

Inception 是需求和架构阶段，目标是**在写任何代码之前**让人类和 Agent 对「做什么、为什么做」达成共识。

核心产出物：
- 需求分析和验证文档
- User Story 创建
- 应用程序设计（包含工作单元分解，用于支持后续并行开发）
- 风险评估和复杂度评价

**关键设计决策**：需求确认通过结构化的问答文件完成，而非实时对话。AI-DLC 将问题写入 markdown 文件（如 `aidlc-docs/inception/requirements/requirement-verification-questions.md`），人类填写 `[Answer]` 标记。多个选项的问题用字母标注，可以组合答案（如 `B and C — rate limiting at both API Gateway level and application level`），也可以选 `X` 表示「以上都不是」。

这个机制解决了一个关键问题：**让 AI 暂停等待输入，而不是在上下文不完整时就开始臆测**。传统的 vibe coding 中，Agent 遇到不明确的需求会「猜一个」，然后用户可能到代码 review 阶段才发现不对。AI-DLC 的问答文件机制强制在这个猜测发生之前就明确分歧。

### 2.2 Construction Phase：设计和实现

Construction 是将设计转化为代码的阶段。每个工作单元经过一系列设计阶段（条件触发）后进入代码生成。

AI-DLC 的设计阶段包括：
- 功能设计（业务逻辑、领域模型、数据schema）
- 非功能需求（NFR）识别
- NFR 设计（应用 NFR 模式）
- 基础设施设计（映射到具体云服务）

关键门控机制：**每个设计阶段产出的文档需要人类明确 approval 才能进入下一阶段**。这解决了我在 1.2 节中提到的「人类无法真正在环」问题——人类在架构设计被固化之前介入，而不是在代码生成之后。

> "Carefully review the execution plan to see which stages will run. Carefully review the artifacts and approve each stage to maintain control."
> — [AI-DLC README: Usage](https://github.com/awslabs/aidlc-workflows)

### 2.3 Operations Phase：部署与监控

Operations 阶段覆盖部署自动化、基础设施配置、监控设置和生产就绪性验证。该阶段尚处于建设阶段，但在 Azure SRE Agent（微软）等生产级 Agent 系统中，同类的「部署+监控」门控已经被证明对防止 Agent 失控至关重要。

---

## 3. 始终在环：人类是决策者，不是最终 review 者

### 3.1 门控驱动的设计

AI-DLC 最重要的设计原则不是「让 AI 更快」，而是**「让人类在关键决策点必须有明确的输入」**。具体体现在：

**Approvel Gates（审批门控）**：每个阶段结束时，Agent 呈现一个 completion message，人类有两个选项：
- **Request Changes** — 要求修改
- **Approve and Continue** — 接受输出并进入下一阶段

**上下文清晰时机**：「始终在环」不是让人类全程盯着 AI 工作，而是**在正确的时机要求明确的决策**。AI-DLC 的设计把人类决策点放在：
1. 需求理解阶段（问答文件）
2. 架构/设计方案完成时（文档 approval）
3. 阶段切换时（Approvel Gate）

### 3.2 Context 管理的最佳实践

AI-DLC 的 Working with AIDLC 文档特别强调了 context 管理的重要性，提出了一个反直觉的建议：**在每个门控点之后，主动要求 context reset（开启新的对话上下文）**，原因是：

> "If you let context accumulate across multiple gates, the AI starts working from a compressed or partially lost version of earlier instructions and artifacts. Output quality degrades in ways that are subtle and hard to diagnose."

这个建议直接揭示了一个当前 AI coding tools 忽视的问题：**长上下文的降级是渐进的、不易察觉的**。用户通常不会注意到 context rot，直到输出质量严重下降。AI-DLC 的解法是**主动 reset**，而不是依赖 Agent 自己判断何时该压缩上下文。

**正确的恢复方式**：当 context 需要 reset 时，AI-DLC 不依赖 AI 自己在对话中恢复状态，而是通过一个状态文件 `aidlc-docs/aidlc-state.md` 记录当前进度，让新的上下文可以从持久化文件中精确恢复。

---

## 4. 自适应复杂度：同一个方法论，大小项目通用

### 4.1 复杂度自适应的实现方式

AI-DLC 没有为不同规模的项目设计不同的流程——它设计了一个**自适应深度**的机制。Agent 根据项目的复杂度自动决定执行多少个设计阶段。

具体来说，每个 Construction 阶段的工作单元会**根据复杂度评估**决定是否经过所有设计阶段还是直接进入代码生成。简单 CRUD 端点可能跳过功能设计直接生成代码；涉及分布式系统或安全敏感的模块会执行完整的设计链路。

这解决了敏捷方法论中的一个经典问题：**为小任务写大文档的成本往往超过任务本身**。AI-DLC 的解法不是「小任务用轻量方法，大任务用重量方法」，而是让同一个流程自适应地决定深度。

### 4.2 扩展机制：Opt-In 规则系统

AI-DLC 有一个扩展系统，允许在任何已有的核心流程上**叠加额外的约束规则**。扩展以两种文件形式存在：

- **规则文件**（如 `security-baseline.md`）：具体的约束内容
- **Opt-In 文件**（如 `security-baseline.opt-in.md`）：用户选择是否启用该扩展

扩展的加载机制：AI-DLC 在工作流启动时扫描 `extensions/` 目录，找到所有 `*.opt-in.md` 文件，在需求分析阶段向用户呈现，用户选择启用后才加载对应规则。

内置的扩展包括：
- 安全基线扩展（Security Baseline）
- _property-based testing 扩展（Property-Based Testing）

> "Extensions without a matching `*.opt-in.md` file are always enforced."

这个设计让组织可以将自己的安全、合规或 API 标准变成**每个项目自动加载的默认约束**，而不需要每次手动注入——这是企业采用 AI coding tools 时最需要的机制。

---

## 5. 支持所有主流 AI Coding Agents

### 5.1 平台适配层设计

AI-DLC 的核心方法论与具体 Agent 无关，它通过**平台适配层**将同一套流程映射到不同的工具：

| 平台 | 规则文件位置 | 配置方式 |
|------|------------|---------|
| Claude Code | `CLAUDE.md` 或 `.claude/CLAUDE.md` | 直接复制核心工作流文件 |
| Cursor | `.cursor/rules/ai-dlc-workflow.mdc` | MDC 格式 + frontmatter |
| Kiro | `.kiro/steering/aws-aidlc-rules/` | Steering files |
| Amazon Q Developer | `.amazonq/rules/aws-aidlc-rules/` | Q Rules |
| Cline | `.clinerules/` | Rules 文件 |
| GitHub Copilot | `.github/copilot-instructions.md` | Custom instructions |
| OpenAI Codex | `AGENTS.md` | Codex 原生约定 |
| 其他 Agent | 项目根目录 | 通用的 `AGENTS.md` |

> "AI-DLC works with any coding agent that supports project-level rules or steering files. The general approach: place `aws-aidlc-rules/` wherever your agent reads project rules from."
> — [AI-DLC README: Other Agents](https://github.com/awslabs/aidlc-workflows)

这种设计的工程意义：**方法论是可以移植的**。一个团队今天用 Claude Code，明天切换到 Cursor，不需要重新学习 AI-DLC 流程，只需要修改规则文件的存放位置。

### 5.2 六个安全扫描器的 CI/CD 集成

AI-DLC 的 scripts 目录包含一个 `aidlc-evaluator/` Python 框架，与六种安全扫描器集成：

| 扫描器 | 检测目标 | 失败条件 |
|--------|---------|---------|
| Bandit | Python SAST | 高置信度发现 |
| Semgrep | 多语言 SAST | 任何发现（PR 只检新增）|
| Grype | 依赖 CVE | 高危/严重 CVE |
| Gitleaks | Git 历史中的 secrets | 任何非基线的 secret |
| Checkov | IaC 错误配置 | 任何检查失败 |
| ClamAV | 恶意软件 | 任何检测 |

这是 AI-DLC 作为生产级方法论的核心证据之一：**它不只是在代码生成层引入结构，还在质量 gate 引入了真实的安全验证**。

---

## 6. 评估框架：让 Agent 的工程产出可量化

### 6.1 aidlc-evaluator 的设计

`aidlc-evaluator` 框架（位于 `scripts/aidlc-evaluator/`）是 AI-DLC 的质量验证层。它采用 `uv` 管理依赖，提供了 pytest-based 的测试框架。

这个评估器解决了一个根本问题：**如何量化 AI coding agent 的工程产出**。大多数 Agent 评测集中在「能否完成任务」，但 AI-DLC 的评估器引入了「完成任务的过程是否符合工程标准」的维度——代码是否通过安全扫描、是否符合组织的代码规范、是否在指定的架构约束内实现。

### 6.2 与 SWE-bench 等基准测试的关系

现有的 Agent 评测基准（如 SWE-bench、GAIA）主要评估**结果正确性**。AI-DLC 的评估框架则关注**过程合规性**——即使 Agent 产出了「看起来正确」的代码，如果它违反了组织的安全策略或架构约束，仍然应该在评估阶段被检测出来。

这是一个重要的角度补充：**好的 AI coding agent harness 不只需要能完成任务，还需要按照指定的工程规范完成任务**。

---

## 7. 与现有 Harness Engineering 的关系

### 7.1 元方法论 vs 工具框架

Martin Fowler 的 Harness Engineering 文章描述了三个相互锁定的系统：context 工程（curating what the agent knows）、architectural constraints（deterministic linters 和 structural tests）、entropy management（定期修复文档漂移的 Agent）。

AI-DLC 与这个框架的对应关系：
- **Context 工程** → AI-DLC 的 `aidlc-docs/` 目录结构（需求文档、设计文档、状态文件）作为持久化的上下文载体，对抗 context rot
- **Architectural constraints** → AI-DLC 的安全扩展和 NFR 设计阶段
- **Entropy management** → AI-DLC 的 Operations Phase（监控和可观测性设置）

### 7.2 Anthropic 的「始终在环」 vs AI-DLC 的「结构化在环」

Anthropic 在 Building Effective Agents 中提到了 human-in-the-loop 的重要性，但主要是作为「避免 Agent 失控」的安全网。AI-DLC 则将 human-in-the-loop 变成了**结构化的审批流程**——每个阶段产出具体的文档，人类在进入下一阶段前必须明确 approval。

> 笔者认为：AI-DLC 的这个设计将「human oversight」从隐式安全机制变为显式工程流程，这是它与现有 Agent 框架最本质的区别。Anthropic 的 harness 设计告诉开发者「你可以加 human oversight」，AI-DLC 告诉开发者「human oversight 必须发生在这些具体的 gate 上」。

---

## 8. 局限性

AI-DLC 也有其局限：

**局限性一：方法论的学习曲线**。AI-DLC 的核心价值是结构化，但结构化意味着需要遵循其约定的文件结构和问答格式。这对小型项目（个人项目、一次性脚本）来说可能过于重量。但这是设计选择——AI-DLC 的目标场景是「需要工程化管理的软件开发」，对于「快速原型验证」确实有更好的工具。

**局限性二：平台适配的维护成本**。每个新平台需要对应的适配方式，如果某个 Agent 工具更新了自己的规则文件规范，现有的 AI-DLC 适配可能需要更新。

**局限性三：Operations Phase 尚未完成**。当前的 AI-DLC v0.1.8 的 Operations Phase 主要是框架设计，生产级的部署、监控和可观测性能力还没有完全实现。对于需要端到端工程流程的团队来说，还需要等待 Operations Phase 的完善。

---

## 9. 适用场景判断

**推荐使用 AI-DLC 的场景**：
- 团队采用 AI coding agent 进行生产级软件开发
- 需要在 AI 生成代码之前有架构/设计审查流程
- 组织有安全、合规或代码规范要求需要 AI 遵守
- 同时使用多个 AI coding 平台（Claude Code、Cursor、Copilot 等）

**不推荐 AI-DLC 的场景**：
- 个人快速原型验证
- 完全的一次性脚本编写
- 团队已有一套成熟的 AI coding guidelines 且运行良好

---

## 10. 核心结论

AI-DLC 的核心贡献不是发明了新技术，而是**将散落在不同工具和最佳实践中的工程原则结构化为一套可移植的方法论**。

它的三个最重要的设计：

1. **问答文件机制**：强制在 Agent 开始「猜」之前明确需求歧义
2. **门控驱动的 human-in-the-loop**：将 human oversight 从隐式安全网变为显式工程流程
3. **平台适配层**：同一套方法论可以通过适配层运行在任何支持 project rules 的 Agent 上

这三个设计共同解决了一个根本问题：**如何让 AI coding agent 的输出变得可预期、可控制、可审计**。这不是通过更好的模型或更好的 prompt做到的，而是通过**结构化的人类决策点和强制性的审查门控**实现的。

> "We never vibe code. We always know where we are, where we're going, and what we've decided."
> — AI-DLC Working with AIDLC 文档中隐含的设计哲学

---

**执行流程**：
1. **理解任务**：Cron 触发，每2小时一次自主仓库更新，遵循 SKILL.md 定义的维护流程
2. **规划**：先检查 .agent/ 目录（PENDING.md / REPORT.md）获取上下文，然后 pull 最新代码解决冲突
3. **执行**：Tavily 搜索 Anthropic/OpenAI/Cursor 官方博客，发现 Anthropic April 23 Postmortem（Claude Code 质量回退事件），同时 GitHub Trending 发现 awslabs/aidlc-workflows（1,847 ⭐，1.8k）——发现主题关联：质量回退事件（evalu 体系不完善）→ AI-DLC 方法论（结构化 human-in-the-loop + evaluator 框架）
4. **返回**：获取到完整的 awslabs/aidlc-workflows README（3000+ 字）以及 WORKING-WITH-AIDLC 文档（800+ 行）
5. **整理**：完成 Article（AI-DLC 方法论分析，~3500 字，5 处原文引用）和 Project 推荐（awslabs/aidlc-workflows，~1500 字，4 处 README 原文引用）

**调用工具**：
- `read`: 3次（SKILL.md、PENDING.md、REPORT.md）
- `exec`: 15次（git pull、git stash、Tavily 搜索、curl 获取 README、GitHub API 查询等）
- `web_fetch`: 1次（Anthropic April 23 Postmortem 文章）
- `write`: 2次（Article + Project 推荐）
- `edit`: 1次（更新 .agent/ state.json）