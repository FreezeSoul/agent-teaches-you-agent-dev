# mattpocock/skills — 来自真实工程师的 Agent Skills 实践集

## 核心问题

当 AI Agent 被广泛应用于软件开发时，常见的失败模式是**对齐偏差**：开发者以为 Agent 理解了他的需求，而 Agent 构建出的东西却完全不是预期。Matt Pocock 作为 TypeScript 专家和独立开发者，将二十年软件工程经验蒸馏为可组合的 Agent Skills，让 AI 编程从「 vibe coding 」进化到「 disciplined engineering 」。

## 为什么存在（项目背景）

大多数 AI 编程工作流（BMAD、GSD、Spec-Kit）试图将开发过程流程化，但代价是**剥夺了工程师的控制权**——当过程中出现 bug，工程师难以介入和解决。

> "Developing real applications is hard. Approaches like GSD, BMAD, and Spec-Kit try to help by owning the process. But while doing so, they take away your control and make bugs in the process hard to resolve."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

Matt Pocock 构建这些 skills 是为了**修复他观察到的 Claude Code、Codex 等工具的常见失败模式**，提供的是小型、易适配、可组合的工程实践工具集，适用于任何模型。

## 核心能力与技术架构

### 关键特性 1：垂直切片式任务分解

[/to-issues](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-issues/SKILL.md) skill 将任何 PRD/规范分解为独立的 GitHub Issues，每 issue 对应一个垂直切片（vertical slice）——从 UI 到数据库端到端打通，而不是横向按层切割（前端、后端、数据库分开处理）。

### 关键特性 2：带文档的批判性访谈

[/grill-with-docs](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) 在开始编码前强制 Agent 对开发者进行深度访谈，挑战计划的每个分支，同时更新 CONTEXT.md（共享语言文档）和 ADR（架构决策记录）。

这解决了**对齐偏差**的根本问题——不是等 Agent 做完后发现不对，而是在开始前就迫使开发者澄清需求。

### 关键特性 3：TDD 红绿重构循环

[/tdd](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md) 将测试驱动开发的 disciplined loop 注入 Agent 工作流：先写失败的测试 → 写代码修复测试 → 重构。帮助 Agent 获得持续的反馈循环，避免「 Agent 写完代码不知道自己写的是否正确」的问题。

### 关键特性 4：代码库架构持续改进

[/improve-codebase-architecture](https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md) 定期扫描代码库，识别模块深化的机会，结合 CONTEXT.md 中的领域语言和 docs/adr/ 中的架构决策，推动代码库在 AI 加速开发下持续保持良好设计。

### 关键特性 5：渐进式披露结构

Skills 使用**渐进式披露（Progressive Disclosure）** 结构：SKILL.md 只展示立即需要的指令，附件资源（文档、脚本、模板）按需加载。避免 Agent 被过多的上下文淹没，同时保持完整信息可用性。

## 安装与使用

```bash
# 一行安装
npx skills@latest add mattpocock/skills

# 在 Agent 中运行初始化
/setup-matt-pocock-skills

# Agent 会询问：
# - 使用哪个 Issue Tracker（GitHub / Linear / 本地文件）
# - Triage 时使用哪些标签
# - 文档保存位置
```

## 与同类项目对比

| 维度 | BMAD/GSD 流程 | mattpocock/skills |
|------|--------------|------------------|
| 控制权 | 流程拥有控制权 | 工程师保持控制权 |
| 错误处理 | 流程出错难以介入 | 技能可审计、可修改 |
| 反馈循环 | 弱（往往直到最终才发现问题）| 强（每个 skill 内置反馈循环）|
| 可组合性 | 固定流程 | 模块化，按需选用 |
| 工程纪律 | 依赖 Agent 自身能力 | 将工程师经验编码为技能 |

> 笔者的工程判断：mattpocock/skills 的核心价值在于**将软件工程的最佳实践显式化为 Agent 可执行的技能**，而非依赖 Prompt Engineering 隐式传递工程纪律。

## 适用场景与局限

**适用场景**：
- 需要持续迭代的真实项目（非一次性 demo）
- 团队有明确的工程标准（TypeScript、TDD、ADR）
- 开发者希望保持对代码库的控制权

**局限**：
- Skills 默认面向 TypeScript/前端项目，对其他技术栈需要适配
- 部分 Skills（如 grill-with-docs）需要开发者在场配合访谈，不适合纯异步场景
- 49k+ stars 中有相当一部分来自 Matt Pocock 的社区影响力，项目的新鲜感稀释了实际工程价值

## 一句话推荐

如果你的 Agent 经常「做出来的东西不是你要的」，mattpocock/skills 提供了一套**以工程师为中心的 Agent 工作框架**，通过结构化对齐（Triage、PRD、Grilling）和持续反馈（TDD、诊断）让 AI 编程真正可预测、可控制。

---

## 防重索引记录

- GitHub URL: https://github.com/mattpocock/skills
- 推荐日期: 2026-05-01
- 推荐者: ArchBot
- 关联文章: [Anthropic 多窗口 Agent 架构深度解析](./effective-harnesses-long-running-agents-2026.md)
