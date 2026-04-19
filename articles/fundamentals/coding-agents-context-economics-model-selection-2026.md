# 上下文经济学：2026 编程 Agent 选型框架

> **来源**: [Coding Agents in Feb 2026](https://calv.info/agents-feb-2026) (calv.info, Calvin French-Owen)
> **分类**: fundamentals
> **标签**: context-management、model-selection、coding-agent、harness-engineering
> **一手来源**: Calvin French-Owen（帮助发布 Codex Web 产品，曾任职于 Google/Notion）

---

## 一句话总结

2026 年编程 Agent 的选型核心不是「哪个模型最强」，而是**你的时间约束决定模型选择**：长时间 autonomous run 选 Claude Code（Opus），需要正确性时.flip to Codex。

---

## 背景：Agent 能力的核心瓶颈是什么

大多数关于编程 Agent 的讨论聚焦于模型能力（benchmark 分数、上下文窗口大小、工具调用准确率）。但对于实际使用这些工具的工程师来说，有一个更根本的约束：**时间**。

Calvin French-Owen 在 2026 年 2 月的一篇第一手分析中指出：

> 「我现在选择编程 Agent 的首要因素是**我有多少时间**——我想让它 autonomous run 一晚上完成 80% 的草稿，还是在白天和我协作完成？」

这个视角将模型选择从「能力竞赛」重新框架为**上下文经济学**：上下文窗口是有限资源，不同模型在不同时间约束下有不同的 ROI。

---

## 核心洞察一：上下文管理的三大工程约束

### 1.1 Chunking 是不可避免的

如果任务「太大」放不进上下文窗口，Agent 会在里面长时间打转，给出质量很差的结果。这不是一个可以通过提升模型能力来解决的问题——因为模型的上下文窗口永远有限，而代码库的规模增长没有上限。

**工程含义**：好的 Agent 使用习惯需要主动拆分任务边界。plans/ 目录（每个任务一个计划文件）成为标准工程模式。

### 1.2 Compaction 是有损的

当上下文快满时，Agent 需要压缩历史信息。Compaction 过程中的选择——保留哪些、丢弃哪些——决定了压缩后推理质量。经验数据显示：**压缩越多，性能退化越明显**。

**工程含义**：与其依赖压缩，不如设计 Agent 工作流使得上下文始终保持在「聪明区」—— Dex Horthy 称之为「dumb zone」的概念：上下文窗口后半段更容易出现性能衰退，因为模型在短上下文数据上训练更充分。

### 1.3 你不知道你不知道什么

如果某个相关文件或依赖不在上下文里，Agent 可能会完全朝意料之外的方向走。没有任何机制能告知工程师「模型漏看了什么」。

**工程含义**：代码库的结构设计本身就是 Harness 的一部分。模块化、可渐进披露的架构设计能够减少 Agent 遗漏关键信息的概率。OpenAI 有一篇工程博客专门讨论如何通过 Markdown 文件结构实现这一点。

---

## 核心洞察二：Opus vs Codex 性能对比矩阵

Calvin French-Owen 同时使用 Claude Code（Opus）和 Codex 作为主力工具，以下是他的一手观察：

| 维度 | Claude Code（Opus）| Codex |
|------|-------------------|-------|
| **速度** | 快（上下文效率高）| 慢（sub-agent 并行不如 Opus）|
| **正确性** | 较低（偶发 import 遗漏、off-by-one）| 高（Bug 率显著更低）|
| **Sub-agent 并行** | 优秀（频繁并发启动子任务）| 一般（实验性 sub-agent 模式）|
| **工具使用** | 优（gh、git、MCP server）| 较弱（CLI 工具常被"脚本化"而非直接调用）|
| **代码解释** | 优（人类可读的 PR 描述、架构图）| 一般 |
| **上下文效率** | 极高（可在多窗口间高效分发）| 较低 |

**Opus 的典型失误**：通过单元测试但忘了添加到顶层 `<App>` 渲染；不明显的 off-by-one 错误； dangling references；隐蔽的竞态条件。

**关键洞察**：Opus 的上下文处理效率使其在 autonomous run 场景（长时间、多文件）中有优势；Codex 的正确性优势在需要精确输出的场景（最终代码审查）更明显。

---

## 核心洞察三：时间驱动的工作流模式

基于上述对比，Calvin French-Owen 总结出他的实际工作流：

```
Claude Code（Opus）→ 规划、terminal 操作、git 管理
        ↓ （准备开始实际编码）
Codex → 精确实现、代码审查、PR 准备
```

**「Start with Claude Code, keep it open as a pane, then flip to Codex when I'm ready to actually start the coding.」**

这不是「哪个更好」的问题，而是**不同时间约束下的最优选择**：

| 场景 | 推荐选择 | 原因 |
|------|---------|------|
| 夜间 autonomous run（80% 草稿即可）| Claude Code（Opus）| 速度快，sub-agent 并行效率高 |
| 短时间精确实现 | Codex | Bug 率低，代码质量高 |
| 架构规划、代码解释 | Claude Code（Opus）| 人类可读输出质量高 |
| 大型重构 | Claude Code（Opus）→ Codex | 先规划再精确实现 |
| 关键业务代码审查 | Codex | Bug 率低，更可靠 |

---

## 工程实践：上下文高效的代码库设计

### 目录结构

Calvin French-Owen 的代码库结构（可参考）：

```
my-repo/
  plans/           ← 每个任务一个计划文件（按编号）
  apps/            ← 不同服务的代码
  (turborepo + bun)  ← monorepo 管理
```

Plans 文件夹的作用：允许 Agent 选择性读取和记忆，而不是把整个对话历史塞进上下文。这使得 **context-resumption** 和 **context-efficient task continuation** 成为可能。

### Claude Code 的 Permission Model 优势

Opus（Claude Code）在权限模型上有优势：命令前缀清晰，CLI 工具白名单容易配置。Codex 倾向于「脚本化」CLI 命令（`for ... in gh`），使得细粒度权限控制更困难。

### 基础设施选择

- **Cloudflare Durable Objects**：数据库分区预建，按需唤醒，不担心并发写入。在 Agent 处理小块数据的场景下天然适配。
- **Ghostty**：Mitchell Hashimoto 的终端，原生、快速、多 pane 支持（替代 tmux 多实例）。

---

## 这个框架与现有知识的区别

本文与仓库内已有文章的关系：

| 已有文章 | 本文补充维度 |
|---------|------------|
| `desktop-ai-agent-architectural-comparison-2026.md`（三种桌面 Agent 对比）| 从「产品对比」→ 到「同一人的多工具 workflow」|
| `context-engineering-for-agents.md`（上下文工程原则）| 从「原则」→ 到「有数据的实践验证」|
| `open-models-crossed-threshold-agent-eval-2026.md`（开源/闭源 Agent 评测）| 从「模型能力评测」→ 到「工程师视角的选型决策框架」|
| `multi-model-routing-coding-agents-role-based-2026.md`（多模型路由）| 从「路由机制」→ 到「时间约束驱动的 routing mental model」|

---

## 局限性与适用边界

1. **个人经验局限**：Calvin French-Owen 的观察来自 greenfield 代码库（相对小、轻量）。在大型生产代码库中，Opus 的上下文效率问题可能更突出，或者 Codex 的速度劣势更明显。

2. **模型快速迭代**：2026 年 2 月的观察可能在 4 月已过时。模型能力差距在快速收窄。

3. **工具链差异**：Claude Code 和 Codex 是高度特定的工具链。这些观察不一定能推广到其他 Agent 系统。

---

## 工程建议

> **笔者的判断**：上下文经济学这个框架最有价值的地方不是 Opus vs Codex 的具体数据，而是将**时间约束**引入 Agent 选型决策的思维模式。对于任何在生产环境中使用多个 Agent 工具的工程师，建议：
>
> 1. 明确你的时间约束（autonomous time budget）
> 2. 在这个约束下评估上下文效率 vs 输出正确性的 trade-off
> 3. 不要追求单一 Agent 覆盖所有场景——多工具 workflow 才是长期答案

---

## 参考文献

- [Coding Agents in Feb 2026](https://calv.info/agents-feb-2026) — Calvin French-Owen 第一手实践分析（本文核心来源）
- [Dex Horthy — The Dumb Zone](https://www.youtube.com/watch?v=rmvDxxNubIg&t=355s) — 上下文窗口「后半段」性能衰退的概念来源
- [OpenAI Harness Engineering Blog](https://openai.com/index/harness-engineering/) — 通过 Markdown 文件结构实现可渐进披露架构
- [Claude Code Architecture Deep Analysis](../desktop-ai-agent-architectural-comparison-2026.md) — Claude Code 的 Harness 架构分析
