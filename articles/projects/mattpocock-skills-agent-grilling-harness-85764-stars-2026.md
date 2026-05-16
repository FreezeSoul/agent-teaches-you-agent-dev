# mattpocock/skills：让 Agent 学会「先问清楚再动手」的技能体系

> **关联文章**：[Anthropic Managed Agents：解耦设计如何让 Agent 架构「活」得更久](./anthropic-managed-agents-decoupling-brain-hands-2026.md) — 本推荐与该文章共同探讨「如何设计不过时的 Agent harness」

---

## 一句话概括

mattpocock/skills 解决了一个教科书里不会写、但每个用 Agent 写过代码的人都踩过的坑：**Agent 和你「想的不一样」，然后花大力气做了错误的东西**。

---

## 为什么这个项目值得关注

### 85,764 stars 的爆发式增长说明什么

这个仓库 2026 年 2 月才创建，到 5 月中旬已经 85k+ stars、7,437 forks。对于一个纯 Shell/技能类仓库，这个速度是异常的。

异常增长的背后是真实的痛点：**用 Agent 写代码的人都在经历同样的失败模式**。

### Matt Pocock 定义的三个核心失败模式

他在 README 里明确指出：

> "Developing real applications is hard. Approaches like GSD, BMAD, and Spec-Kit try to help by owning the process. But while doing so, they take away your control and make bugs in the process hard to resolve."

**失败模式 #1：Agent 没有做你想要的**
- 症状：Agent 交付的代码和你预期的不一样
- 根因：沟通缺口（communication gap）
- 解法：grilling session —— 让 Agent 在动手前先问清楚

**失败模式 #2：Agent 太啰嗦**
- 症状：Agent 输出 20 个词而你只需要 1 个
- 根因：Agent 和 domain experts 说不同语言
- 解法：共享语言（ubiquitous language）—— 一份让 Agent 理解项目术语的文档

**失败模式 #3：Agent 不会应对边界情况**
- 症状：正常流程没问题，边界一塌糊涂
- 解法：SPEC.md —— 把规格写清楚，Agent 才能正确应对

这三条，每一个都直击当前 Agent 编程工具的核心痛点。

---

## 技术架构：技能体系的设计

### 安装方式（30秒上手）

```bash
npx skills@latest add mattpocock/skills
```

然后在 Agent 里运行 `/setup-matt-pocock-skills`，它会引导配置：
- issue tracker（GitHub / Linear / 本地文件）
- labels 策略（triage 技能用的）
- 文档存放位置

### 核心技能列表

| 技能 | 用途 |
|------|------|
| `/grill-me` | 非代码场景的对齐对话 |
| `/grill-with-docs` | 带文档的深度对齐 |
| `/spec` | 生成 SPEC.md |
| `/triage` | 根据 labels 分类 issues |
| ... | 还有更多 |

每个技能都是**小而可组合**的。Matt 刻意不用大而全的框架——他的设计哲学是：

> "These skills are designed to be small, easy to adapt, and composable. They work with any model."

这和 Anthropic 那篇文章的结论完全呼应：**好的 harness 应该是可拆卸的，而不是把所有逻辑绑在一起**。

---

## 为什么这个项目值得关注

### 1. 填补了「Prompt 之外」的能力空白

大多数 Agent 能力讨论集中在 prompt 优化，但 Matt 解决的是 prompt 解决不了的问题：**信息不对称**。grilling session 的本质是在动手前对齐期望，而不是在 prompt 里塞更多上下文。

### 2. 从「作者」视角而非「工具」视角做技能

> "They're based on decades of engineering experience. Hack around with them. Make them your own."

Matt 是 TypeScript 的核心贡献者，他的技能不是学术论文产物，而是从真实工程踩坑里长出来的。这让它们比大多数「AI 提示词集合」更有实战价值。

### 3. 极高的社区认可（85k stars）说明方向正确

对于 Agent 工具类项目，star 数量不是唯一指标，但 85k 说明这个方向被大量开发者验证过。

---

## 与 Managed Agents 文章的关联

Anthropic 那篇文章的核心洞察是：**模型能力提升后，之前弥补短板的 harness 逻辑会变成冗余**。因此好的 harness 必须是可演进的。

Matt Pocock 的技能体系恰好是这种思路的**实践版本**：每个技能独立、可替换、不绑架 Agent 的决策权。你可以在任何模型上用这些技能，也可以随时删掉某个不适合你的技能。

从这个角度说，Matt 的技能体系和 Anthropic 的三层解耦在哲学上是一致的——**不是给 Agent 套上更多约束，而是给 Agent 提供更好的决策信息**。

---

## 快速上手

```bash
# 1. 安装
npx skills@latest add mattpocock/skills

# 2. 在 Agent 里运行
/setup-matt-pocock-skills

# 3. 每次要写新功能前，先用 /grill-me 对齐
/grill-me
```

---

**引用来源**

> "Developing real applications is hard. Approaches like GSD, BMAD, and Spec-Kit try to help by owning the process. But while doing so, they take away your control and make bugs in the process hard to resolve."

> "These skills are designed to be small, easy to adapt, and composable. They work with any model. They're based on decades of engineering experience."

---

*归档目录：`projects/` | Stars: 85,764 | Forks: 7,437 | Language: Shell | MIT License | 2026-02-03 创建*