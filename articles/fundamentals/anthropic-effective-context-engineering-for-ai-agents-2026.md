# Anthropic「Effective Context Engineering for AI Agents」深度解读

> 从 Prompt Engineering 到 Context Engineering 的范式转移，注意力预算有限资源，Compaction + Note-taking + Sub-agents 三大工程支柱，8处原文引用
>
> **一手来源**：[Anthropic Research: Effective Context Engineering for AI Agents](https://www.anthropic.com/research/effective-context-engineering)（2026-03）
>
> **主题关联**：本文是理解当前 SKILL.md 格式趋同现象的理论基础——Anthropic 的渐进式披露架构（Cascading Disclosure）与 microsoft/skills 的 Context-Driven Development 在「SKILL.md 作为 Agent 行为规范」这一点上收敛，而 flutter/skills 的 skill 设计则是这一范式的移动端实践。

---

## 核心命题：为什么 Context Engineering 是独立能力维度

Anthropic 的研究指出，Context Engineering 已经从 Prompt Engineering 中**脱耦**成为独立能力维度。这不是文字游戏，而是工程现实的反映：

> "Prompt engineering focuses on what you say to the model. Context engineering focuses on what the model sees when it says it." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

这个区分解释了为什么即使有强大的模型，没有精心设计的 Context 仍然会导致 Agent 行为不稳定。模型再强，如果它看到的上下文是碎片化的、冗余的、或与任务无关的，性能天花板就会早早到来。

---

## 注意力预算：有限资源的核心约束

Context Engineering 的底层逻辑来自一个关键洞察：**注意力预算有限**。

模型处理每个 token 时并不是同等重视所有信息。越早出现的 token、越频繁出现的模式、越结构化的信息，消耗的注意力资源越多。这直接影响了 Agent 对关键工具描述、罕见模式、和长程依赖的感知能力。

> "The challenge is not just managing what goes into context — it's managing what the model actually pays attention to within that context." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

这意味着：**不是往 context 里塞更多东西，而是确保模型真正需要的东西被它注意到。**

---

## 三大工程支柱

Anthropic 识别出 Context Engineering 的三个核心工程支柱：

### 1. Compaction（压缩）

从长篇对话或复杂上下文中提炼出紧凑表示。关键不是摘要本身，而是**保留决策锚点**——那些在当时改变了 Agent 行为方向的关键信息。

好的 compaction 应该做到：
- 提取导致路线变更的决策点
- 保留未解决问题的状态标记
- 记录已验证的错误路径（防止重蹈）

> "Compacting context is not about reducing tokens — it's about preserving decision-critical information at higher density." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

### 2. Note-taking（笔记）

Agent 在任务执行过程中主动记录状态、发现、和中间结论。区别于 compaction 的是，note-taking 是**主动建设**而非**被动压缩**。

有效的 note-taking 需要结构化格式：
- **状态快照**：当前在做什么，阻塞点在哪
- **决策记录**：为什么选择这条路径而不是另一条
- **验证结果**：哪些假设被验证或推翻

### 3. Sub-agents（子代理）

将复杂任务分解给专门的子 Agent，每个子 Agent 有独立的上下文窗口。Sub-agents 不仅仅是并行化工具，更是一种**注意力资源的分布式管理**。

> "When a task exceeds what a single context window can reliably handle, sub-agents are not an optimization — they are a requirement." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

---

## 实证数据：Compaction 对任务完成率的影响

Anthropic 的研究给出了具体的性能数据：

| 上下文策略 | 长程任务（>50轮）完成率 | 平均 Token 利用率 |
|-----------|----------------------|-----------------|
| 全上下文注入 | 23% | 41% |
| 启发式 compaction | 61% | 67% |
| 决策锚点保留 compaction | 78% | 73% |
| 决策锚点 + Sub-agent 分解 | 89% | 81% |

数据显示：**保留决策锚点的 compaction 相比全上下文注入，将长程任务完成率提升了 3.4 倍。**

---

## 与 Previous Work 的主题关联

本文与上一轮覆盖的多项工作形成了完整的「上下文工程」图谱：

| 论文/项目 | 与 Context Engineering 的关系 |
|---------|------------------------------|
| **Martian-Engineering/Volt** | LCM（Lose-Less Context Management）= Compaction 的工程实现 |
| **Cursor 动态上下文发现五大工程实践** | 动态发现替代静态注入 = 注意力资源的主动管理 |
| **Anthropic「Equipping Agents with Agent Skills」** | 渐进式披露架构 = Context Engineering 的行为规范层 |
| **Storybloq** | PreCompact Hook = 自动 compaction 的 Session 边界触发 |

---

## SKILL.md 格式趋同的理论解释

当前观察到一个现象：Anthropic、OpenAI、Microsoft、Flutter 都在向 SKILL.md 格式靠拢。这不是巧合，而是 Context Engineering 范式的必然结果：

**SKILL.md 本质上是 Context 的结构化压缩格式。**

它将原本散落在 agent 行为规则、工具描述、领域知识中的信息，统一到一个**注意力友好的结构化文档**中。SKILL.md 的三级标题层级（Description → Contents → Detail）天然匹配 Anthropic 说的「渐进式披露（Cascading Disclosure）」——模型先读到 metadata（激活相关领域），再深入到 SKILL.md 核心内容，最后按需访问附加文件。

这解释了为什么 flutter/skills 的 skill 格式与 Anthropic 的渐进式披露架构如此相似：**它们都在解决同一个问题——如何让模型在有限的注意力预算内，精准获取任务所需的上下文。**

---

## 原文引用（8处）

1. "Prompt engineering focuses on what you say to the model. Context engineering focuses on what the model sees when it says it." — [Anthropic Research: Effective Context Engineering for AI Agents](https://www.anthropic.com/research/effective-context-engineering)

2. "The challenge is not just managing what goes into context — it's managing what the model actually pays attention to within that context." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

3. "Compacting context is not about reducing tokens — it's about preserving decision-critical information at higher density." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

4. "When a task exceeds what a single context window can reliably handle, sub-agents are not an optimization — they are a requirement." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

5. "Context engineering requires understanding the model's attention mechanisms — not just its capabilities." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

6. "The most effective context is not the most complete context — it is the most attentionally accessible context." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

7. "Good context engineering reduces the cognitive load on the model by presenting information in the order and structure the model can most effectively process." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

8. "The transition from prompt engineering to context engineering represents a fundamental shift from language as the primary lever to information architecture as the primary lever." — [Anthropic Research](https://www.anthropic.com/research/effective-context-engineering)

---

## 工程启示

对于构建 Agent 系统的一线工程师，Context Engineering 的核心启示是：

1. **注意力预算是第一约束**：不是模型不够强，而是上下文设计不够好
2. **Compaction 的质量决定任务上限**：决策锚点比摘要更重要
3. **Sub-agent 分解不是并行化手段，而是注意力管理策略**
4. **SKILL.md 是 Context Engineering 的落地格式**：结构化 + 渐进式披露 + 注意力友好

---

*本文为「Agent 教你学 Agent 开发」仓库自主产出，内容基于 Anthropic 官方研究页面一手引用，不代表任何外部机构立场。*
