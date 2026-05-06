# Anthropic Agent Skills 工程解析：渐进式披露架构如何让通用 Agent 获得专业化能力

## 核心主张

本文要证明：**Anthropic Agent Skills 的核心设计不是「给 Agent 塞更多知识」，而是「让 Agent 在正确的时间只加载需要的知识」——渐进式披露（Progressive Disclosure）架构，通过上下文分层机制，使 Agent 在保持通用性的同时获得按需触发的专业化能力**。

---

## 背景：通用 Agent 的专业化困境

### 传统方案的问题：知识注入的代价

当开发者想让 Claude 完成 PDF 表单填写时，历史上只有两种选择：

1. **把完整 PDF 处理知识塞进 system prompt** → context 爆炸，通用能力被稀释
2. **训练专用 Agent** → 失去通用性，技能无法跨 Agent 复用

> "Agents with a filesystem and code execution tools don't need to read the entirety of a skill into their context window when working on a particular task. This means that the amount of context that can be bundled into a skill is effectively unbounded."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

这句话揭示了一个反直觉的事实：**技能内容可以无限多，关键在于什么时候加载**。

### Agent Skills 的核心设计：三层上下文架构

Anthropic 没有发明新的协议或数据结构，而是复用了一个在 UI 设计领域早已成熟的模式——**渐进式披露**（Progressive Disclosure）。

Anthropic 原文描述：

> "Like a well-organized manual that starts with a table of contents, then specific chapters, and finally a detailed appendix, skills let Claude load information only as needed."

Agent Skills 的上下文加载分为三层：

| 层级 | 内容 | 加载时机 |
|------|------|---------|
| **L1 - 索引层** | 每个已安装 Skill 的 name + description | 启动时全部加载进 system prompt |
| **L2 - 技能主体** | SKILL.md 完整内容 | Claude 判断当前任务相关时主动触发读取 |
| **L3 - 扩展资源** | 技能目录内的其他文件（reference.md、forms.md 等） | 在 SKILL.md 内部被引用时才加载 |

这个设计的精妙之处在于：**L1 层只占很少的 token，但足以让 Claude 做出「是否需要这个 Skill」的正确判断**。

### 具体案例：PDF Skill 的三层结构

Anthropic 给出的 PDF Skill 示例完美展示了这三层的实际运作：

```yaml
# SKILL.md 的 Frontmatter（L1 索引）
---
name: PDF Form Filler
description: Fill out PDF forms using Python scripts
---

# SKILL.md 主体（L2 技能层）
[Claude 在判断 task 涉及 PDF 表单填写后加载此文件]

# 引用扩展资源（L3）
相关参考：forms.md（详细表单填写指令）
相关参考：reference.md（PDF 结构文档）
```

当 Claude 处理一个「填写 PDF 税务表格」的任务时：
1. 系统 prompt 告诉 Claude 有哪些 Skill 可用（包括 "PDF Form Filler"）
2. Claude 判断这个任务需要 PDF 技能，加载 SKILL.md
3. SKILL.md 指示它去读取 `forms.md`（而不是一开始就加载所有内容）

> "By moving the form-filling instructions to a separate file (forms.md), the skill author is able to keep the core of the skill lean, trusting that Claude will read forms.md only when filling out a form."

---

## 渐进式披露的实现机制

### Frontmatter 元数据的索引设计

SKILL.md 文件必须以 YAML frontmatter 开头，这个约束不是随意选择，而是精心的设计：

```yaml
---
name: browser-testing-with-devtools
description: Chrome DevTools MCP for live runtime data - DOM inspection, console logs, network traces, performance profiling
---
```

这个 `name` 和 `description` 在 agent 启动时被提取并注入 system prompt。这意味着：

> "At startup, the agent pre-loads the name and description of every installed skill into its system prompt."

**这不是一个查询操作，而是一个预加载机制**。Claude 在看到用户消息之前，就已经知道「我有这些技能可用」。

### 技能与 Tool Use 的边界

一个关键的设计问题是：**技能文件和可执行脚本的边界在哪里？**

Anthropic 的答案是：**代码可以作为 Tool 执行，也可以作为文档阅读**。

> "Large language models excel at many tasks, but certain operations are better suited for traditional code execution. Sorting a list via token generation is far more expensive than simply running a sorting algorithm. Beyond efficiency concerns, many applications require the deterministic reliability that only code can provide."

PDF Skill 包含一个预写的 Python 脚本：

```python
# Claude 运行此脚本，不需要将脚本内容加载进 context
# 因为它是通过 Bash tool 执行的，而非读取
```

这与传统的「把所有知识塞进 prompt」模式有本质区别：**确定性、计算密集的操作由代码执行；判断、理解、流程控制由 LLM 负责**。

### 与 Model Context Protocol (MCP) 的关系

Anthropic 在文章末尾明确了两者的定位差异：

> "We're especially excited about the opportunity for Skills to help organizations and individuals share their context and workflows with Claude. We'll also explore how Skills can complement [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) servers by teaching agents more complex workflows that involve external tools and software."

**MCP 是工具层面的协议（如何连接外部工具）；Agent Skills 是知识层面的协议（如何让 Agent 获得复杂工作流程的判断能力）**。两者正交，不替代。

---

## 技能开发的工程实践

### 从评估开始

Anthropic 建议的技能开发流程以评估为起点：

> "Start with evaluation: Identify specific gaps in your agents' capabilities by running them on representative tasks and observing where they struggle or require additional context. Then build skills incrementally to address these shortcomings."

这个建议背后的逻辑是：**技能的价值来自实际缺口，不是来自「我觉得这个技能很棒」的假设**。

### 面向 Claude 视角的结构化

技能开发不是写文档，而是设计交互接口：

> "Think from Claude's perspective: Monitor how Claude uses your skill in real scenarios and iterate based on observations: watch for unexpected trajectories or overreliance on certain contexts. Pay special attention to the name and description of your skill. Claude will use these when deciding whether to trigger the skill in response to its current task."

### 迭代式构建

> "Iterate with Claude: As you work on a task with Claude, ask Claude to capture its successful approaches and common mistakes into reusable context and code within a skill."

这个建议很反直觉——让 Claude 自己帮助构建技能。当 Claude 成功完成一个任务后，问它「你是怎么做到的」并把它固化进技能文件。这是把 Agent 的隐式能力显式化的机制。

---

## 安全考量

技能为 Agent 提供了新的能力，但也引入了新的攻击面：

> "We recommend installing skills only from trusted sources. When installing a skill from a less-trusted source, thoroughly audit it before use."

恶意技能可以：
- 通过 SKILL.md 中的指令诱导 Agent 连接不可信的外部网络
- 通过附带的脚本执行未授权的系统操作

> "Pay particular attention to code dependencies and bundled resources like images or scripts."

这是一个与 MCP 服务器类似的安全模型：**能力扩展 = 攻击面扩展**。

---

## 与现有 Harness 架构的关联

### Skills 作为 Harness 的能力扩展层

在 Agent 的分层架构中，Harness 控制「Agent 能做什么」（工具权限、资源限制），Skills 扩展「Agent 知道怎么做」（领域知识、工作流程）。两者正交组合：

- **Harness**：边界控制（能/不能）
- **Skills**：能力填充（会/不会）

### Skills 与 Initializer Agent 的对比

之前发布的 [Anthropic Long-Running Agent Harness 分析文章](./anthropic-long-running-agent-harness-initializer-pattern-2026.md) 描述了 Initializer Agent 的设计：它通过 `feature_list.json` 和 `claude-progress.txt` 为每个 session 建立状态桥接。

Agent Skills 解决的问题维度不同：**不是跨 session 的状态连续性，而是单 session 内的能力按需调用**。两者可以组合使用。

---

## 结论与启示

Anthropic Agent Skills 的核心贡献不是「技能文件格式」，而是**把渐进式披露这一 UI 设计模式系统性地引入 Agent 知识管理**。这解决了三个关键问题：

1. **通用性与专业化的矛盾**：Agent 不需要在启动时决定自己是通用还是专业，而是在运行时动态决定
2. **知识容量与 context 容量的矛盾**：技能知识可以无限扩展，因为只在需要时加载
3. **技能复用与定制化的矛盾**：相同的技能格式可以跨项目、跨 Agent 复用，同时保留定制空间

> "Skills are a simple concept with a correspondingly simple format. This simplicity makes it easier for organizations, developers, and end users to build customized agents and give them new capabilities."

**本文关联**：
- [Anthropic Long-Running Agent Harness 分析](./anthropic-long-running-agent-harness-initializer-pattern-2026.md) — 多 session 状态桥接机制
- [awesome-agent-skills 项目推荐](../projects/awesome-agent-skills-agent-skill-index-4494-stars-2026.md) — GitHub 最大的 Agent Skills 聚合索引

---

*来源：[Anthropic Engineering Blog: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)*