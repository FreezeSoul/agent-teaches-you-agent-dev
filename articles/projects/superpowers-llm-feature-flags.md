# Superpowers：用技能框架让 AI 编程从「能写」进化到「会做」

## 项目背景与解决的问题

软件开发最大的浪费，不是代码写错了，而是方向写偏了——在错误的方向上跑很远才发现这是个错误。

AI 编程工具（Claude Code、Cursor、Codex 等）的出现，让「写代码」这件事变得前所未有地高效。但当我们把一个 AI 助手丢进一个真实项目，让它自己跑上几个小时，常见的结果是：代码写了很多，技术债务积累得更快；PR 拉了一堆，质量问题一堆；plan 变化无常，上下文丢失于无形。

问题的根源不在于模型不够强，而在于**没有结构化的开发方法论支撑 AI 的行为**。

**Superpowers** 正是为此而生。它不是一个配置包，不是一个 prompt 模板，而是一套**完整的 AI 原生软件开发方法论**，通过可组合的技能（Skills）在编码 agent 的工作流中嵌入强制性的质量门禁，把 TDD、YAGNI、DRY 这些工程原则从「建议」变成「AI 必须遵守的流程」。

作者 Jesse Vincent 是 Perl/Web.pm 的原作者，Ticketmaster/Prime Radiant 的 founder，在工程工坊（engineering rigor）这件事上有数十年的积累。这套系统诞生于他自己在真实项目中使用 AI 编程的实践检验，而非理论设计。

## 核心能力与技术架构

### 技能触发系统：强制流程而非建议流程

Superpowers 的核心机制是**在特定工作流阶段自动触发对应技能**。这意味着 AI agent 不会在「写代码」之前跳过设计步骤——因为触发机制是内置在系统层面的，不是靠 agent 自己的判断。

完整的技能体系分为以下几类：

**设计阶段**
- `brainstorming`：在写代码前激活，用苏格拉底式提问帮你澄清需求，设计文档结构化输出，用户确认后才能进入下一阶段
- `writing-plans`：将工作分解为 2-5 分钟粒度的任务，每个任务有精确的文件路径、完整代码和验证步骤

**执行阶段**
- `subagent-driven-development` / `executing-plans`：启动子 agent 执行任务，采用两级审查机制（先检查是否符合规范，再检查代码质量）
- `test-driven-development`：强制执行 RED-GREEN-REFACTOR 循环——先写失败测试，看它失败，写最少量代码让它通过，然后重构。任何写在测试之前的代码都会被删除。
- `systematic-debugging`：4 阶段根因分析（症状→假设→验证→定位），包含防御性编程和基于条件的等待技术

**协作阶段**
- `requesting-code-review`：按优先级报告问题，严重阻塞性问题是强制处理的
- `finishing-a-development-branch`：验证测试后提供选项（合并/PR/保留/丢弃），自动清理工作树

### 跨平台支持

Superpowers 支持所有主流 AI 编程工具：
- Claude Code（官方插件市场和 Superpowers 独立市场）
- OpenAI Codex CLI / Codex App
- Cursor（通过插件市场）
- OpenCode
- GitHub Copilot CLI
- Gemini CLI

这意味着无论你用哪个工具，都能获得一致的软件工程方法论。

### Git Worktree 集成

`using-git-worktrees` 技能在设计批准后激活，为每个功能分支创建隔离的工作空间，验证干净的测试基线，避免并行开发时的上下文污染。

## 与同类项目对比

| 维度 | Superpowers | Cursor Rules / 通用 System Prompt | 其他 Agent Harnes 配置 |
|------|------------|----------------------------------|----------------------|
| **流程约束力** | 强制性（触发式） | 建议性（取决于模型遵循度） | 建议性 |
| **TDD 强制执行** | ✅ 内置 RED-GREEN-REFACTOR | ❌ | ❌ |
| **子 Agent 协调** | ✅ 两级审查机制 | ❌ | 部分 |
| **跨平台支持** | 6+ 平台 | 单平台 | 单平台 |
| **spec-first 设计** | ✅ brainstorming + 确认流程 | ❌ | ❌ |
| **学习曲线** | 中等（需要适应流程） | 低（直接用） | 低 |

Superpowers 和 Everything Claude Code（另一个高星项目）是互补关系：ECC 侧重于 harness 层面的性能优化（token、记忆、安全），Superpowers 侧重于开发流程的质量门禁。两者可以叠加使用。

## 适用场景与局限

### 适用场景

- **复杂的多文件项目**：当 AI 需要在多个模块之间保持一致性时，TDD 和 spec-first 流程能有效防止「各自为政」的碎片化代码
- **团队 AI 编程规范**：为团队中的所有 AI 编程用户提供一致的工程标准，减少代码审查摩擦
- **需要长时间自主工作的 AI Agent**：subagent-driven-development 机制可以让 AI 在数小时内自主工作而不偏离计划
- **对代码质量有要求的产品项目**：TDD 强制执行特别适合那些不能接受技术债务累积的项目

### 局限

- **流程开销**：对于简单的单文件脚本或一次性任务，Superpowers 的流程显得有些过于重型
- **跨 Agent 协作的稳定性**：subagent-driven-development 在复杂项目中可能遇到 agent 间上下文传递的问题
- **非英文场景**：brainstorming 等技能默认使用英文提问，在非英语团队中的体验可能受影响
- **上手需要时间**：需要理解这套方法论才能有效使用，不像简单的配置包那样拿来即用

## 一句话推荐

如果你在使用 AI 编程工具时遇到过「AI 跑偏了」「代码质量不稳定」「没有结构化流程支撑」的问题，Superpowers 是一套经过实战验证的方法论，值得认真研究。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/obra/superpowers`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：12/15
