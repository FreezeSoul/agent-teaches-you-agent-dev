# AI Coding Agent 的工程化范式转移：从 Prompt Tricks 到 Durable Engineering System

> "The biggest failure mode in agent-driven development is not intelligence — it is **system instability**."
> — [Harness Craft README](https://github.com/YuxiaoWang-520/harness-craft)

## 核心论点

2026 年的 AI Coding Agent 领域正在发生一场根本性范式转移：从前两年的「prompt tricks」时代（靠更聪明的提示词解决问题），切换到「engineering systems」时代（靠持久化工程结构保障 Agent 工作质量）。这个转移的驱动因素不是模型能力不足，而是当任务跨越多个上下文窗口时，prompt 层无法解决的三类系统失效：上下文丢失、多 Agent 碰撞、进度不可验证。Harness Craft 作为这个范式转移的代表性工程实现，提供了完整的解决方案。

## Prompt Tricks 时代的终结

回看 2024-2025 年，AI Coding 社区的主流方法是「prompt engineering」——通过更长的 system prompt、更精细的 few-shot 示例、更复杂的指令层级来提升 Agent 效果。这种方法的局限在长程任务中暴露无遗：

| Prompt-First Workflow | System-First Workflow |
| --- | --- |
| Context lives in chat history | Context is written to repo-local artifacts |
| Completion is based on model confidence | Completion is based on evidence and checks |
| Multi-agent work is ad hoc | Roles, ownership, and review gates are explicit |
| Long tasks drift across sessions | Long tasks resume from structured state |
| Handoffs are fragile | Handoffs are built into the workflow |

这张对比表揭示了 prompt tricks 的核心问题：**对话历史是脆弱的存储介质**。当 Agent 需要跨越多个上下文窗口工作时，所有依赖 chat history 的上下文都面临「上下文窗口耗尽」的风险——一旦模型开始遗忘之前讨论过的架构决策、用户偏好、当前进度，整个系统就会退化到「每个会话都从零开始」的状态。

## 系统性失效的三层根因

Harness Craft 文档精确识别了长程 Agent 失败的三类根因，这些不是 prompt 可以解决的：

**第一层：上下文脆弱性（Context Fragility）**
> "The agent understood the repo yesterday and acts like it has amnesia today."
> "Plans, validation status, and handoff context live only inside chat transcripts."

当 agent 依赖 chat history 作为唯一上下文载体时，session 切换就等于上下文丢失。这是 prompt tricks 无法解决的架构问题。

**第二层：多 Agent 边界失效（Multi-Agent Boundary Failure）**
> "Multiple agents look busy, but their changes collide and review quality is weak."

没有明确边界的多 Agent 协作会产生两类问题：文件编辑冲突（多个 Agent 同时修改同一文件的不同部分）和质量门控失效（review 没有结构化的触发机制）。这是协调协议问题，不是模型问题。

**第三层：进度感知的模型自欺（Confidence-Based Completion）**
> "The agent feels done, while the repository is still not in a deliverable state."

模型对「完成」的主观感知与实际代码质量之间存在系统性偏差。这是自我评估的盲点，需要外部验证机制来纠正。

## 四 flagship Skills：工程化的四层干预

Harness Craft 的核心贡献是将 Agent 工作流拆解为四个独立的工程化层，每层解决一类系统性失效：

### 1. `repo-bootstrap`：上下文持久化层

这个 Skill 的核心洞察是：**repo 理解不应该活在 chat history 里**。它将 repo 认知拆分为六个持久化产物：

| 文件 | 职责 | 为什么不能合并 |
| --- | --- | --- |
| `.harness/state.json` | 机器可读的单点真相 | 需要被脚本读取，不能是自然语言 |
| `.harness/memory.md` | 进行中的工作记忆 | 与 repo 事实混合后会变成无结构日记 |
| `.harness/prompt.md` | 用户意图和约束 | 任务语义不应该与 repo 结构耦合 |
| `.harness/repowiki.md` | repo 操作事实（目录/命令/环境） | 长期事实不应该被 session 噪声污染 |
| `.harness/plan.md` | 设计方法/风险/验证路径 | 未来行动不等于过去执行 |
| `.harness/checklist.md` | 执行账本/验证状态 | 真实进度不应该被改写成设计散文 |

关键设计原则：**「自动化不能替代理解」**。脚本可以自动检测语言、框架、命令、配置文件和目录结构——但这只构建了骨架，不提供深度理解。这种设计使系统更诚实，更容易在 Agent 之间传递。

### 2. `longrun-dev`：长程执行控制层

> "Most agent demos excel at showing how work *starts*. The real difficulty is controlling how work *continues*."

这个 Skill 识别了长程任务最常见的失败模式：

- Agent 不知道上次离开时进展到哪里
- 基线已经被破坏，但 Agent 继续在损坏的基础上构建
- 功能范围在多轮中静默漂移
- 进度只是叙事性的，没有结构
- 模型「感觉」完成了，但系统没有任何完成证据

解法是将长程任务的状态从「对话资产」转变为「repo 资产」。生成的产物包括：

- `.longrun/init.sh`：依赖设置和冒烟检查
- `.longrun/feature_list.json`：功能定义及其通过/失败状态
- `.longrun/progress.md`：仅追加的会话进度日志
- `.longrun/session_state.json`：当前恢复状态和会话信息

**最重要的控制约束**：「One feature per session」——将范围扩展限制到最低限度。设计文档指出，这个约束是最高杠杆的控制点，因为高级失败模式的根本原因不是 Agent「不能」工作，而是做了太多、范围太广、超过了原始任务边界。

### 3. `agent-team-dev`：多 Agent 治理层

> "The hardest problem in multi-agent systems is not parallel capacity — it is boundary governance."

这个 Skill 维持一个小型、明确的拓扑结构，而不是让多 Agent 协作自由发展：

| 角色 | 写入范围 | 职责 | 分离原因 |
| --- | --- | --- | --- |
| Team Lead | 集成和仲裁 | 任务契约、人员配置、冲突解决、最终验证 | 必须保持单点真相 |
| Solution Architect | 只读 | 设计简报、风险热点、文件影响图 | 设计必须先于变更 |
| Feature Engineer | 生产代码 | 最小安全实现补丁 | 将实现与其他问题隔离 |
| Test Engineer | 测试代码 | 测试覆盖率、回归保护 | 使验证成为独立责任 |
| Reviewer/Verifier | 只读 | 审查集成结果 | 避免对半成品无焦点反馈 |

关键设计原则：**「多 Agent 不等于更智能，等于必须先治理」**。Mode A/B/C 三种模式根据风险级别选择 staffing 规模，Mode C（Full Safety）最多使用 3-4 个子 Agent，这是上限而非默认选项。

### 4. `learn`：知识累积层

> "Every conversation between a developer and an agent contains high-value knowledge: corrections, patterns, facts, preferences. Without a learning system, this knowledge evaporates when the session ends."

这个 Skill 的核心设计：**对话是未被利用的知识金矿**。四种知识类型按优先级排列：

1. **纠正（Corrections）** — 用户纠正了 Agent 的方法（最高价值）。代表 Agent 犯过的错误，必须永不重复。
2. **模式（Patterns）** — 重复的工作流或编码约定。
3. **事实（Facts）** — 项目/环境特定的事实。
4. **偏好（Preferences）** — 用户的个人风格选择。

强度演化模型：

```
New knowledge created → strength: weak, confirmed: 0
  ↓ Applied once without user correction
strength: weak, confirmed: 1
  ↓ Applied again without correction
strength: medium, confirmed: 2
  ↓ Repeatedly validated
strength: strong, confirmed: 4+
  ↓ User explicitly confirms ("yes, exactly")
strength: strong (immediate jump)
```

关键设计决策：**不自动提升**。只有当项目级条目达到 `strength = strong` 且其内容不包含项目特定引用时，系统才会**建议**提升——但用户始终确认。为什么不自动提升？因为虚假提升的成本（污染全局范围）远超过遗漏提升的成本（在另一个项目中再教一次）。

## Skills vs Rules：双层干预架构

Harness Craft 提供了两个互补系统，每个解决不同层面的问题：

| | Skills | Rules |
| -- | --- | --- |
| **类比** | Playbook（ playbook） | Constitution（宪法） |
| **加载方式** | 按需加载（`/skill-name`） | 始终开启的护栏，每次会话 |
| **上下文成本** | 仅在调用时加载完整文本 | 始终加载（每个都很短） |
| **适用场景** | 长工作流（TDD、E2E、深研究…） | 短全局约束（风格、安全、git…） |

**简言之**：Rules 是 Agent 的**本能**。Skills 是 Agent 的**学习专长**。Claude Code 和 Codex 以不同方式暴露始终开启层，但设计目标是相同的。

15 条 Rules 覆盖：编码风格、安全性、测试、git 工作流、代码审查、开发工作流、模式、性能、Agents 自动分派、学习知识加载、钩子最佳实践。

## 与「规则 → 模型」范式转移的呼应

Harness Craft 的四层架构与本仓库之前分析的「模型驱动的 Harness 演进」（2026-05-12 15:57 轮次）形成深度呼应：

**模型驱动 Harness 的核心主张**：2026 年上半年四大 AI 厂商（Anthropic×2、Cursor、OpenAI）都在将原本依赖规则的 harness 逻辑迁移给模型本身——Auto Mode（权限判断）、Managed Agents（上下文管理）、Autoinstall（环境准备）、Auto-review（审批分流）。

**Harness Craft 的对应对角线**：不是在 harness 层面用模型替代规则，而是在 Skill 层引入工程化持久化来解决模型无法自我纠正的系统性失效——上下文丢失由 `repo-bootstrap` 解决，进度感知由 `longrun-dev` 的证据系统解决，多 Agent 碰撞由 `agent-team-dev` 的角色边界解决。

两者并非竞争关系，而是互补的两层：
- **模型驱动 Harness**：在 Agent 执行层，用模型替代规则处理不确定性
- **Harness Craft 工程系统**：在 Agent 治理层，用持久化工程结构解决模型无法自愈的结构性失效

## 工程化范式转移的判断性结论

**前提**：当 AI Coding 任务从「一次性生成」转向「长程维护」，prompt tricks 的边际效益趋近于零。

**核心变化**：Agent 工作质量不再取决于 prompt 质量，而是取决于工程系统的完整性——上下文持久化能力、执行状态管理能力、协作边界治理能力、知识累积能力。

**工程启示**：

1. **Harness 不仅仅是安全护栏**：传统认知里 harness = 权限控制 + 安全边界。Harness Craft 证明 harness 应该是「完整的工作系统」，包含上下文管理、执行控制、协作治理。
2. **Skills 是 Agent 的专长层**：不是 prompt，是持久化的操作手册。好的 Skill 使 Agent 在没有详细指令的情况下也能正确执行。
3. **Rules 是 Agent 的本能层**：始终开启的护栏，不需要用户主动调用。Rules 的设计应该遵循「最小干预原则」——只在必要时触发。
4. **系统稳定性优先于智能上限**：当 Agent 进入长程任务时，系统不稳定是比模型不够聪明更常见的失败原因。

> "These are not prompt problems. They are **engineering system problems**."
> — [Harness Craft README](https://github.com/YuxiaoWang-520/harness-craft)

---

**关联项目**：[YuxiaoWang-520/harness-craft](./harness-craft-86stars-2026.md) — 46 Skills + 15 Rules 的 Agent 工程化完整解决方案，与本文形成「范式转移 → 工程实现」的完整闭环。

**关联主题**：本文与「模型驱动的 Harness 演进」（2026-05-12 15:57）形成双轨覆盖：前者聚焦 Agent 治理层的工程化结构，后者聚焦 Agent 执行层的模型驱动进化。两者共同指向 2026 年的核心趋势：**Harness Engineering 作为独立学科的崛起**。