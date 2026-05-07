# Anthropic Agent Skills 渐进式披露架构：让通用 Agent 获得专业化能力的工程方法论

> 笔者认为：Agent Skills 的本质不是「塞更多知识给模型」，而是一套**按需加载的上下文分发机制**——在正确的时间点，把正确的信息给到正确的层级。这篇文章要回答的核心问题是：Anthropic 如何用「渐进式披露」解决通用 Agent 专业化的矛盾，以及这套设计背后的工程逻辑。

---

## 1. 问题的本质：通用 Agent 与专业化之间的张力

构建 Agent 时有一个根本矛盾：**通用模型擅长一切，但又什么都不精**。Claude 知道 PDF 是什么，但不会填表；能理解代码，但不知道你们项目的 lint 规则。要解决这个问题，有两条路：

- **路 A**：为每个场景从头训练/微调专用 Agent → 成本高、无法组合、版本分裂
- **路 B**：在通用 Agent 之上外挂知识/工具 → 上下文爆炸、触发混乱、难以维护

Anthropic 选择了**路 C**：不是塞更多知识，而是**建立一套信息分发协议，让 Agent 按需获取**，并将其命名为 **Agent Skills**。

> "Skills extend Claude's capabilities by packaging your expertise into composable resources for Claude, transforming general-purpose agents into specialized agents that fit your needs."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

## 2. 渐进式披露：三层级信息架构

Agent Skills 的核心设计哲学是**渐进式披露（Progressive Disclosure）**。类比一本好的手册：首先是目录让你知道有什么，然后是各章节概要，最后是附录细节。Agent 也按这个逻辑加载信息。

### 2.1 第一层：元数据（系统级提示词）

Skill 目录中的 `SKILL.md` 文件**必须**以 YAML frontmatter 开头，包含 `name` 和 `description`：

```yaml
---
name: pdf
description: Manipulate PDF documents - fill forms, extract text, merge files
---
```

这部分内容在 Agent **启动时**就预加载到系统提示词中，提供的是**全局索引**——让 Agent 知道「这个 Skill 大概是什么、什么时候可能用到」，但**不加载具体内容**。

> "At startup, the agent pre-loads the name and description of every installed skill into its system prompt. This metadata is the first level of progressive disclosure: it provides just enough information for Claude to know when each skill should be used without loading all of it into context."

### 2.2 第二层：SKILL.md 主体（按需加载）

当 Agent 在执行任务过程中判断某个 Skill  relevant 时，它会主动读取对应 Skill 目录下的 `SKILL.md` **完整内容**。这是第二层信息——具体指令和操作流程。

以 PDF Skill 为例，`SKILL.md` 主体可能包含：
- 如何检测 PDF 是否为可填写表单
- 如何提取表单字段
- 如何用 Python 脚本填写表单并输出

```markdown
## Filling PDF Forms

When the user asks to fill a form:

1. First, run the extract_form_fields.py script to list all form fields
2. For each field, determine the appropriate value from the user's request
3. Call fill_form.py with the field-value mapping
4. Output the path to the completed PDF

## Important Notes
- ...
```

> "The actual body of this file is the second level of detail. If Claude thinks the skill is relevant to the current task, it will load the skill by reading its full SKILL.md into context."

### 2.3 第三层：额外文件（场景化按需导航）

随着 Skill 复杂度增长，单个 `SKILL.md` 可能过大，或者某些上下文只在特定场景下才需要。解决方案是**在 Skill 目录下 bundle 额外文件**，从 `SKILL.md` 中引用它们：

```
pdf-skill/
├── SKILL.md          ← 核心文件，包含主要工作流
├── reference.md      ← PDF 格式参考（按需加载）
└── forms.md          ← 表单填充详细说明（只在使用表单功能时加载）
```

Agent 从 `SKILL.md` 的引用中**主动发现并导航到这些额外文件**，而不是无脑加载全部内容。

> "Skills can bundle additional files within the skill directory and reference them by name from SKILL.md. These additional linked files are the third level (and beyond) of detail, which Claude can choose to navigate and discover only as needed."

---

## 3. 为什么渐进式披露能解决上下文窗口问题

传统方案把专业知识全部塞进上下文窗口，等价于「让一个人记住整本字典然后做阅读理解」。Anthropic 的方案本质上是**上下文窗口的分时复用**：

| 层级 | 何时加载 | 加载位置 | 上下文占比 |
|------|---------|---------|-----------|
| 元数据 | Agent 启动时 | 系统提示词 | ~1% |
| SKILL.md 主体 | Agent 主动判断 relevant 时 | 工作上下文 | ~10-30% |
| 额外文件 | Agent 在 SKILL.md 内部发现 relevant 时 | 工作上下文 | ~5-15% |

这意味着：Agent 可以在一个拥有 20 个 Skill 的环境中工作，而活跃占用的上下文始终控制在最小范围。

> "Agents with a filesystem and code execution tools don't need to read the entirety of a skill into their context window when working on a particular task. This means that the amount of context that can be bundled into a skill is effectively unbounded."

**关键洞察**：渐进式披露把「信息量」和「上下文占用」解耦了。一个 Skill 可以包含无限多的专业知识，但只有被实际触发的那部分才占上下文。

---

## 4. Skills 与代码执行：超越提示词的边界

Agent Skills 的另一个重要设计维度是**捆绑可执行代码**。某些操作（排序、文件处理、数学计算）用 Token 生成效率极低且不可靠，交给确定性代码更合适。

PDF Skill 中包含一个 `extract_form_fields.py` 脚本：

```python
#!/usr/bin/env python3
"""Extract all form field names from a PDF."""
import sys
import pdfplumber

def main(pdf_path: str):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for annot in page.annotations:
                if annot.get('/Subtype') == '/Widget':
                    field_name = annot.get('/T')
                    print(f"Field: {field_name}")

if __name__ == '__main__':
    main(sys.argv[1])
```

Agent 可以直接执行这个脚本，而**不需要把脚本内容或 PDF 内容加载到上下文**：

> "Claude can run this script without loading either the script or the PDF into context. And because code is deterministic, this workflow is consistent and repeatable."

**设计原则**：代码作为工具时，Agent 只负责「何时调用」，不负责「如何实现」；代码作为文档时，Agent 可以读取理解后自行实现类似逻辑。

---

## 5. 与 MCP 的关系：技能层与协议层的互补

Anthropic 在文章中明确回答了 Skills 与 MCP（Model Context Protocol）的关系：

> "We're especially excited about the opportunity for Skills to help organizations and individuals share their context and workflows with Claude. We'll also explore how Skills can complement Model Context Protocol (MCP) servers by teaching agents more complex workflows that involve external tools and software."

**协议层（MCP）**负责「工具发现与调用接口标准化」——解决的是「Agent 如何找到并使用外部工具」的问题。

**技能层（Skills）**负责「复杂工作流的指令组织」——解决的是「Agent 如何按照人类专家的流程完成专业任务」的问题。

两者的关系可以类比为：
- MCP = USB 接口协议（定义如何物理连接设备）
- Skills = 设备使用手册（告诉你这个设备怎么用才能发挥最大价值）

---

## 6. 安全考量：Skill 的信任边界

Skills 通过指令和代码扩展 Agent 能力，但这也意味着**恶意 Skill 可能引入环境漏洞或诱导 Agent 执行非预期操作**。Anthropic 给出了明确的安全建议：

1. **只从可信来源安装 Skill**
2. **使用前必须审计**：检查 Skill 目录下的所有文件，特别关注代码依赖和外部网络请求
3. **注意指令中的外部网络连接**：如果 Skill 指示 Agent 连接某个外部 API，需要判断该 API 是否可信

> "When installing a skill from a less-trusted source, thoroughly audit it before use. Start by reading the contents of the files bundled in the skill to understand what it does, paying particular attention to code dependencies and bundled resources like images or scripts."

---

## 7. 工程实践建议：如何构建有效的 Skill

### 7.1 从评估开始，而非从文档开始

**反模式**：先写一堆使用文档，然后塞给 Agent。
**正确姿势**：让 Agent 在真实任务上跑，观察哪里卡住了或需要额外上下文，然后**针对性构建 Skill**。

> "Identify specific gaps in your agents' capabilities by running them on representative tasks and observing where they struggle or require additional context. Then build skills incrementally to address these shortcomings."

### 7.2 监控 Skill 名称和描述的触发效果

Skill 的 `name` 和 `description` 是 Agent 判断「是否使用这个 Skill」的唯一依据。这部分措辞需要基于真实监控数据迭代——如果 Agent 总是在不该用的时候触发，或该用的时候不触发，说明描述需要调整。

### 7.3 让 Agent 参与 Skill 的构建

> "As you work on a task with Claude, ask Claude to capture its successful approaches and common mistakes into reusable context and code within a skill."

这本质上是**让 Agent 记录自己的成功模式**，形成可复用的 Skill。这是未来「Agent 自我进化」的基础——Agent 能创建、编辑和评估自己的 Skills。

---

## 8. 关键结论

Agent Skills 给我们最重要的工程启示是：**专业化不等于固定专一，而是动态按需**。

- **不是为每个场景训练一个 Agent**，而是在通用 Agent 上建立一套「按需加载专业知识」的信息分发机制
- **渐进式披露把上下文窗口和信息量解耦**，让一个 Agent 可以拥有无限多的专业知识，但只在需要时占用对应上下文
- **Skill 的核心价值是「人给 Agent 的专家知识封装」**，而非工具注册，这是「人类专家经验」复用的最佳形式
- **Skills 与 MCP 是互补的**，协议层解决接口标准化，技能层解决工作流组织

> "Skills are a simple concept with a correspondingly simple format. This simplicity makes it easier for organizations, developers, and end users to build customized agents and give them new capabilities."
> — Anthropic Engineering

---

*来源：[Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)（Barry Zhang, Keith Lazuka, Mahesh Murag）*
