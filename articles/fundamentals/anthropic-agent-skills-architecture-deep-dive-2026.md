# Anthropic Agent Skills：让通用 Agent 获得专业能力的架构设计

## 核心问题

当一个通用 LLM Agent 被部署到实际业务场景时，面临一个根本矛盾：通用模型擅长处理开放问题，但业务场景需要 Agent 在特定领域达到「专业级」表现。如何在不修改模型权重的情况下，让通用 Agent 快速获得专业能力？

Anthropic 的答案是 **Agent Skills**：一套将领域知识封装为可复用技能包的标准和实现。本文从工程角度深度解析其设计原理，为构建专业化 Agent 系统提供可落地的参考。

---

## Agent Skills 的本质

> "A skill is a directory containing a SKILL.md file that contains organized folders of instructions, scripts, and resources that agents can discover and load dynamically to perform better at specific tasks."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

Agent Skills 不是一个新的模型架构，也不是一个定制化的 Agent 分支。它是一套**技能封装标准**——将人类的领域专业知识（流程、工具使用规范、最佳实践）打包成 Agent 可发现的模块。

**类比理解**：就像一个刚入职的工程师需要阅读岗位培训手册才能胜任工作，Agent 通过加载 Skills 获得「上岗培训」，而不是从头训练一个专属模型。

---

## 核心设计：渐进式披露（Progressive Disclosure）

### 3.1 为什么需要渐进式披露

Agent 的上下文窗口是有限的。当 Agent 被安装了 100 个 Skills，每个 Skill 有 2000 tokens，100 个 Skill 的元数据就能填满整个上下文窗口。

Anthropic 的设计通过**三层结构**解决这个问题：

```
┌──────────────────────────────────────────────────────┐
│  Layer 1:  Skill Metadata（系统提示词级别）           │
│  name + description，每个 Skill 只占用 ~50 tokens     │
└──────────────────────────────────────────────────────┘
                              ↓ Agent 判断是否需要触发
┌──────────────────────────────────────────────────────┐
│  Layer 2:  SKILL.md Body（按需加载到上下文）           │
│  完整指令内容，可能包含多个章节                        │
└──────────────────────────────────────────────────────┘
                              ↓ Agent 判断是否需要深入
┌──────────────────────────────────────────────────────┐
│  Layer 3+:  Additional Files（技能相关文件）            │
│  reference.md、forms.md 等，按需读取                  │
└──────────────────────────────────────────────────────┘
```

### 3.2 渐进式加载的执行流程

以 PDF Skill 为例，看 Agent 如何使用 Skills：

> "To start, the context window has the core system prompt and the metadata for each of the installed skills, along with the user's initial message. Claude triggers the PDF skill by invoking a Bash tool to read the contents of pdf/SKILL.md. Claude chooses to read the forms.md file bundled with the skill. Finally, Claude proceeds with the user's task now that it has loaded relevant instructions from the PDF skill."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

**关键洞察**：Agent 决定加载哪个 Skill 不是在请求时硬编码的，而是通过 **system prompt 中的元数据让 Agent 自己判断**。这让 Skills 的调用完全是动态的，由模型推理决定。

### 3.3 SKILL.md 的格式规范

```yaml
---
name: pdf-skill
description: Extract form fields from PDFs, fill out forms, and manipulate PDF documents
---

# PDF Skill

## Overview
This skill provides capabilities for working with PDF documents...

## Usage
When to use this skill...
```

只需要两个元数据字段：
- `name`：唯一标识符（小写 + 连字符）
- `description**：完整描述何时使用这个 Skill

---

## Skills 与上下文的协同

### 4.1 Skills vs. 系统提示词

传统的系统提示词是在部署时固定的。Skills 的不同在于：

| 维度 | 系统提示词 | Skills |
|------|-----------|--------|
| 加载时机 | Agent 启动时全部加载 | 按需动态加载 |
| 可组合性 | 需要修改提示词 | 目录叠加即可 |
| 共享复用 | 每次都要嵌入提示词 | 文件系统共享 |
| 规模化 | 100 个技能 = 200k tokens | 100 个技能 ≈ 5k tokens |

### 4.2 Skills 与代码执行的结合

Skills 不仅是文本指令，还可以包含可执行代码：

> "Skills can also include code for Claude to execute as tools at its discretion. Large language models excel at many tasks, but certain operations are better suited for traditional code execution. For example, sorting a list via token generation is far more expensive than simply running a sorting algorithm."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

PDF Skill 中包含一个 Python 脚本用于提取表单字段：

```python
# skills/pdf/scripts/extract_form_fields.py
import pdfplumber

def extract_form_fields(pdf_path: str) -> dict:
    """Extract all form fields from a PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        return {
            page: page.extract_form_fields()
            for page in pdf.pages
        }
```

Claude 可以调用这个脚本而不需要将其读入上下文——**代码既是工具，也是文档**。

---

## 与 MCP 的关系：互补而非竞争

Anthropic 在文章中明确了两者的定位：

> "We hope to enable agents to create, edit, and evaluate Skills on their own, letting them codify their own patterns of behavior into reusable capabilities."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

**MCP（Model Context Protocol）** 解决的是「Agent 如何连接外部工具和数据源」的问题。
**Skills** 解决的是「如何让 Agent 学会使用这些工具的领域知识」的问题。

```
MCP：提供工具的连接能力（how to connect）
Skills：提供工具的使用规范（how to use）
```

两者正交，Skills 可以包装 MCP 工具的使用规范，Skills 也可以包含执行代码的工具。

---

## 企业落地的工程建议

基于 Skills 的设计原理，以下是工程落地的关键建议：

### ① 从评估开始

> "Identify specific gaps in your agents' capabilities by running them on representative tasks and observing where they struggle or require additional context. Then build skills incrementally to address these shortcomings."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

**不要凭想象构建 Skills**。先运行 Agent 在真实任务上，观察它在哪里失败，再针对性地构建 Skill。

### ② 保持 Skill 的边界清晰

每个 Skill 应该只解决一个问题。多个互斥的场景应该拆成多个独立的 Skill，而不是塞到一个 Skill 里：

```
✅ 好的设计：pdf-skill（PDF 操作）
❌ 糟糕的设计：document-skill（PDF + Word + Excel + PPT）
```

### ③ 让 Claude 参与 Skill 构建

> "Iterate with Claude: As you work on a task with Claude, ask Claude to capture its successful approaches and common mistakes into reusable context and code within a skill."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

让 Claude 在完成任务的过程中**自己总结成功的模式**，而不是人类工程师凭空设计。

### ④ 安全审计不能省

> "We recommend installing skills only from trusted sources. When installing a skill from a less-trusted source, thoroughly audit it before use."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

Skills 可以执行代码，这是潜在的攻击面。企业必须建立 Skills 的安全审计流程。

---

## Agent Skills 的局限性

1. **跨平台兼容性**：Skills 是 Anthropic 推出的标准，目前主要支持 Claude 系列。但社区已有 OpenSkills 等跨平台实现
2. **复杂工作流支持有限**：Skills 适合流程相对固定的任务，对于需要动态规划的复杂工作流，MCP 或专门的 Agent 框架更合适
3. **版本管理缺失**：当前 Skills 没有版本控制机制，多个 Skills 之间的依赖管理需要人工维护

---

## 一手资料

- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — Anthropic 官方工程博客，完整介绍 Skills 设计原理
- [Agent Skills 官方 GitHub 仓库](https://github.com/anthropics/skills) — 包含示例 Skills 和规范定义
- [agentskills.io](https://agentskills.io) — Agent Skills 开放标准官网
- [Claude Skills 文档](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) — 官方使用文档
