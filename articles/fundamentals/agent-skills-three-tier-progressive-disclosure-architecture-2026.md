# Agent Skills 三层渐进披露架构：从「全知模型」到「模块化技能体」

> **核心论点**：Agent Skills 的本质不是「指令文件」，而是一套**三层渐进披露机制**——通过 metadata → SKILL.md → linked files 的分层结构，让 Agent 能在有限 context window 内获得「理论上无限」的能力包。这不是文件格式问题，而是 Agent 与知识之间的一场架构革命。

**来源**：
- [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)（2025/12/18，更新 2026）
- [awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills)（4,494 ⭐，多语言维护）
- [microsoft/skills](https://github.com/microsoft/skills)（2,198 ⭐，132 个技能覆盖 Azure 全家桶）

**性质**：工程实践分析（Anthropic 官方博客 + GitHub 生态）
**评分**：16/20（来源：Anthropic 官方 + 社区验证 ⭐）
**演进阶段**：Stage 10（Skill）

---

## 一、为什么需要 Agent Skills：从「全知模型」的困境说起

当 GPT-4 在 2023 年问世时，业界认为只要模型足够大，就能解决一切问题。但随着 Agent 系统变得越来越复杂，一个根本矛盾浮现出来：

**模型知道一切，但 context window 装不下。**

一个专业的前端 Agent，需要知道 React 最佳实践、CSS 技巧、Figma 设计还原、Playwright 测试——这些知识加起来远超任何 context window 的容量。传统的解法有两种：

1. **把所有知识都塞进 system prompt** → context window 爆炸，模型性能急剧下降
2. **Fine-tuning** → 昂贵、慢、无法动态更新

Agent Skills 提供了第三种解法：**把知识外部化，让 Agent 按需加载**。

> 官方原文：
> "As model capabilities improve, we can now build general-purpose agents that interact with full-fledged computing environments. But as these agents become more powerful, we need more composable, scalable, and portable ways to equip them with domain-specific expertise."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

## 二、核心机制：三层渐进披露（Progressive Disclosure）

Agent Skills 的核心创新不是「SKILL.md 文件格式」，而是一套**三层渐进披露机制**。这是理解 Agent Skills 的关键。

### 2.1 第一层：Metadata（系统启动时预加载）

每个 Skill 的目录包含一个 `SKILL.md` 文件，其开头必须是 YAML frontmatter：

```yaml
---
name: pdf-skill
description: Give Claude the ability to fill out PDF forms interactively
---
```

这个 `name` 和 `description` 在 **Agent 启动时** 就预加载到 system prompt 中。这意味着 Claude 在开始工作前就知道「有哪些技能可用」，但**不知道具体内容**。

> 官方原文：
> "At startup, the agent pre-loads the name and description of every installed skill into its system prompt. This metadata is the first level of progressive disclosure: it provides just enough information for Claude to know when each skill should be used without loading all of it into context."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 2.2 第二层：SKILL.md 主体（按需加载）

当 Agent 判断某个 Skill 与当前任务相关时，它会主动读取完整的 `SKILL.md` 文件，将内容加载到 context window。这是第二层——**按需加载的完整指令**。

```markdown
# PDF Skill

## When to Use This Skill
- User asks to fill out or edit a PDF form
- User asks to extract information from a PDF

## Instructions
1. Run the extract_form_fields.py script to identify all form fields
2. For each field, use the appropriate filling strategy...
3. Save the completed PDF...

## Examples
[Real-world examples]
```

### 2.3 第三层：Linked Files（按需导航）

当一个 Skill 变得复杂时，SKILL.md 可以引用额外的文件：

```
pdf-skill/
├── SKILL.md          # 主指令
├── FORMS.md          # 表单填写指南（按需加载）
├── REFERENCE.md      # 详细 API 参考（按需加载）
└── scripts/
    └── fill_form.py  # 工具脚本（Claude 直接执行，无需加载到 context）
```

> 官方原文：
> "If Claude thinks the skill is relevant to the current task, it will load the skill by reading its full SKILL.md into context... Skills can bundle additional files within the skill directory and reference them by name from SKILL.md. These additional linked files are the third level (and beyond) of detail, which Claude can choose to navigate and discover only as needed."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 三层的本质意义

三层渐进披露解决了一个根本矛盾：**context window 的有限性 vs 知识的无限性**。

> 官方原文：
> "Agents with a filesystem and code execution tools don't need to read the entirety of a skill into their context window when working on a particular task. This means that the amount of context that can be bundled into a skill is effectively unbounded."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

这意味着：一个 Skill 的知识容量**理论上没有上限**。你可以在 Reference.md 里放 10 万字的详细文档，可以在 scripts/ 目录下放无限多的工具脚本——Agent 只需要在真正需要时加载真正需要的部分。

---

## 三、Skills 与 MCP 的关系：分层互补而非竞争

MCP（Model Context Protocol）和 Agent Skills 经常被一起提及，但它们解决的是**不同层次的问题**：

| 维度 | MCP（Model Context Protocol）| Agent Skills |
|------|---------------------------|-------------|
| **核心职责** | 连接（Agent ↔ 工具/数据的通信协议）| 赋能（领域知识的封装与按需加载）|
| **抽象层次** | 协议层（transport + schema）| 应用层（knowledge + procedure）|
| **加载方式** | 初始化时全部加载 | 渐进式披露（Progressive Disclosure）|
| **分发方式** | 远程 MCP 服务器，OAuth 认证 | 本地 SKILL.md 文件夹，可打包为 zip |
| **标准化程度** | 行业标准（Linux Foundation 支持）| 早期规范（SKILL.md 草案）|

> 官方原文（Anthropic 展望）：
> "We'll also explore how Skills can complement Model Context Protocol (MCP) servers by teaching agents more complex workflows that involve external tools and software."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

Anthropic 的判断是：**MCP 负责"用什么工具"，Skill 负责"如何使用工具完成任务"**。两者是垂直分层的关系，而非竞争关系。

---

## 四、Skill 的结构规范：从模板到最佳实践

### 4.1 最小结构

```
skill-name/
├── SKILL.md          # 必需：指令和元数据
└── scripts/          # 可选：辅助脚本
```

### 4.2 SKILL.md 模板

```markdown
---
name: my-skill-name
description: A clear description of what this skill does.
---

# My Skill Name

## When to Use This Skill
- Use case 1
- Use case 2

## Instructions
[Step-by-step instructions for the agent]

## Examples
[Real-world examples]
```

### 4.3 代码执行的双重用途

Skills 中的代码文件可以有两种用途：

1. **作为工具执行**：`scripts/fill_form.py` → Claude 通过 Bash 工具直接执行，不加载到 context
2. **作为参考文档**：`reference.md` → Claude 在需要时读取，加载到 context

> 官方原文：
> "Large language models excel at many tasks, but certain operations are better suited for traditional code execution. For example, sorting a list via token generation is far more expensive than simply running a sorting algorithm. Beyond efficiency concerns, many applications require the deterministic reliability that only code can provide."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

## 五、Skill 开发最佳实践

### 5.1 从评估开始

> 官方原文：
> "Start with evaluation: Identify specific gaps in your agents' capabilities by running them on representative tasks and observing where they struggle or require additional context. Then build skills incrementally to address these shortcomings."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 5.2 为可扩展性而设计

> 官方原文：
> "When the SKILL.md file becomes unwieldy, split its content into separate files and reference them. If certain contexts are mutually exclusive or rarely used together, keeping the paths separate will reduce the token usage."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 5.3 从 Claude 的视角迭代

> 官方原文：
> "Iterate with Claude: As you work on a task with Claude, ask Claude to capture its successful approaches and common mistakes into reusable context and code within a skill. If it goes off track when using a skill to complete a task, ask it to self-reflect on what went wrong."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

## 六、生态现状：Skills 正在成为新的 Plugin 生态

根据 awesome-agent-skills 的追踪，Skills 生态在 2026 年初呈现爆发态势：

### 6.1 多平台支持

| Agent | 平台 |
|-------|------|
| Claude Code | `/skills add <github-url>` |
| Claude.ai | 粘贴 raw SKILL.md URL |
| Codex (OpenAI) | developers.openai.com/codex/skills |
| GitHub Copilot | docs.github.com/copilot/concepts/agents/about-agent-skills |
| VS Code Agent | code.visualstudio.com/docs/copilot/customization/agent-skills |
| Antigravity | antigravity.google/docs/skills |
| Gemini CLI | geminicli.com/docs/cli/skills/ |
| Kiro | kiro.dev/docs/skills/ |
| Junie | junie.jetbrains.com/docs/agent-skills.html |

**9 个主流 AI Coding 平台已支持 Skills**，这意味着 Skills 已经跨越单一厂商锁定，形成事实上的互操作标准。

### 6.2 三大生态枢纽

| 平台 | URL | 功能 |
|------|-----|------|
| **SkillsMP Marketplace** | skillsmp.com | 自动索引 GitHub 上所有 Skill 项目，按分类/更新时间/stars 排序 |
| **skills.sh Leaderboard** | skills.sh | Vercel 运营的最流行 Skills 仓库排行榜 |
| **agent-skill.co** | agent-skill.co | awesome-agent-skills 的 live directory |

### 6.3 社区 Skills 分类

根据 awesome-agent-skills 的统计，社区 Skills 涵盖：
- Vector Databases（向量数据库专项技能）
- Marketing（营销工作流）
- Productivity and Collaboration（效率工具）
- Development and Testing（开发测试）
- Context Engineering（上下文工程）

---

## 七、安全考量：Skills 的双刃剑特性

> 官方原文：
> "Skills provide Claude with new capabilities through instructions and code. While this makes them powerful, it also means that malicious skills may introduce vulnerabilities in the environment where they're used or direct Claude to exfiltrate data and take unintended actions."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

Anthropic 的安全建议：
- **只从可信来源安装 Skills**
- 安装前**审计** Skill 内容（特别是 code dependencies 和 bundled scripts）
- 注意 Skill 指令中是否有连接「不可信外部网络源」的请求

---

## 八、未来方向：Agent 能自建 Skills

> 官方原文：
> "Looking further ahead, we hope to enable agents to create, edit, and evaluate Skills on their own, letting them codify their own patterns of behavior into reusable capabilities."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

这意味着：未来的 Agent 不仅使用 Skills，还能**从自己的成功经验中蒸馏出新的 Skills**。这是一个自举（bootstrap）循环——Agent 在工作中产生 Skills，Skills 又让 Agent 变得更强。

---

## 九、判断与结论

### Agent Skills 的本质

Agent Skills 不是一种「文件格式创新」，而是一套**知识外部化 + 按需加载的架构范式**。三层渐进披露机制解决的是：如何在有限 context window 内让 Agent 获得「理论上无限」的能力。

### 与 MCP 的互补关系

MCP（Model Context Protocol）负责「连接」，Agent Skills 负责「赋能」。两者是垂直分层关系——MCP 让 Agent 能访问工具，Skills 让 Agent 知道如何使用工具完成特定任务。

### 生态成熟度

Skills 生态已经跨越了「单一厂商」阶段。9 个主流 AI Coding 平台（Claude/Codex/Copilot/Gemini CLI/Kiro/Junie 等）已支持 Skills，形成了类似「npm registry」的 Skills Marketplace（SkillsMP、skills.sh）。这意味着 **Skills 已经从 Claude 专属特性演变为跨平台的 Agent 互操作标准**。

### 演进重要性

Agent Skills 代表着 Agent 系统架构的一个明确方向：**从全知模型走向模块化技能体**。随着模型能力继续提升，Skills 将成为 Agent 系统中最关键的可复用单元——它的重要性不亚于当年 npm 对 Node.js 生态的意义。

---

**引用来源**：
- [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [awesome-agent-skills - GitHub](https://github.com/heilcheng/awesome-agent-skills)（Hailey Cheng，维护者）
- [microsoft/skills - GitHub](https://github.com/microsoft/skills)