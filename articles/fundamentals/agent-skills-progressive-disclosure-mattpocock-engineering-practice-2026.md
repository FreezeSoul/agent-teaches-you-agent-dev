# 从渐进式披露到技能生态系统：Agent Skills 的架构演进与工程实践

## 核心主张

> **我认为：Agent Skills 正在从「SKILL.md 规范」演变为一个完整的技能生态系统——而理解这个演进的关键是「渐进式披露」设计哲学。Matt Pocock 的 `skills` 库提供了一个来自一线的观察窗口：真实工程师如何将 decades of experience 压缩进可组合的技能单元，以及这与 Anthropic 的 Agent Skills 架构设计之间的内在联系。**

---

## 1. 问题的本质：为什么 Agent 需要技能封装

当一个通用 LLM Agent 被部署到实际业务场景时，面临一个根本矛盾：通用模型擅长处理开放问题，但业务场景需要 Agent 在特定领域达到「专业级」表现。

传统的解法是**训练专门的 Agent 模型**——但这意味着每次业务逻辑变化都需要重新训练，成本极高且无法快速迭代。

Anthropic 提出的 Agent Skills 范式提供了一条不同的路：**将领域知识从模型权重转移到外部技能包**，Agent 在需要时动态加载，无需重新训练。

> "Skills extend Claude's capabilities by packaging your expertise into composable resources for Claude, transforming general-purpose agents into specialized agents that fit your needs."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

但这里的工程挑战是：**上下文窗口是有限的**。当你安装了 100 个 Skills，每个 Skill 有 2000 tokens，光元数据就能填满整个上下文。Anthropic 的解决方案是**渐进式披露（Progressive Disclosure）**——而这正是理解整个 Agent Skills 生态系统的核心。

---

## 2. 渐进式披露：三层架构的工程原理

### 2.1 三层结构的动机

Anthropic 的设计通过**三层结构**解决上下文窗口的有限性问题：

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Skill Metadata（系统提示词级别）                   │
│  name + description，每个 Skill 只占用 ~50 tokens            │
│  → Agent 启动时全部加载，用于判断「是否需要触发这个 Skill」   │
└─────────────────────────────────────────────────────────────┘
                              ↓ Agent 判断需要时按需加载
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: SKILL.md Body（上下文按需注入）                   │
│  完整指令内容，可能包含多个章节和步骤                       │
└─────────────────────────────────────────────────────────────┘
                              ↓ Agent 判断需要更深入时
┌─────────────────────────────────────────────────────────────┐
│  Layer 3+: Additional Files（按需发现）                     │
│  reference.md、forms.md、scripts/ 等                        │
└─────────────────────────────────────────────────────────────┘
```

这个设计的核心洞察是：**Agent 不需要同时知道所有技能的完整内容，只需要知道「这个场景需要调用哪个技能」**。metadata 是索引，上下文是内容——就像一本书的目录和正文的关系。

### 2.2 渐进式加载的执行流程

以 PDF Skill 为例，看 Agent 如何使用 Skills：

1. **启动阶段**：Agent 的系统提示词包含所有已安装 Skills 的 name + description（Layer 1）
2. **任务解析**：用户说「帮我填这个表格」，Agent 看到 PDF skill description，决定触发
3. **SKILL.md 加载**：Agent 将 pdf/SKILL.md 读入上下文（Layer 2）
4. **条件性深入**：SKILL.md 引用了 `forms.md`，Agent 判断需要时主动读取（Layer 3）

这与传统的「全量加载」相比，节省了大量上下文 tokens。

> "If Claude thinks the skill is relevant to the current task, it will load the skill by reading its full SKILL.md into context."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 2.3 代码作为第三层：可执行技能

Skills 不仅仅可以是文档，还可以包含**可执行的代码**：

> "Large language models excel at many tasks, but certain operations are better suited for traditional code execution."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

PDF Skill 包含一个预写的 Python 脚本，用于提取 PDF 表单字段。Agent 可以在不将脚本或 PDF 加载进上下文的情况下直接运行它。这扩展了 Skill 的能力边界——从「告诉 Agent 怎么做」到「直接给 Agent 可执行的工具」。

---

## 3. Matt Pocock 的 Skills：来自一线的工程视角

在 Anthropic 定义 Agent Skills 架构的同时，Matt Pocock（Total TypeScript 作者）发布了他的 `skills` 库——一个将真实工程经验压缩为可组合技能的系统。

### 3.1 为什么这值得关注

Matt Pocock 的 Skills 不是概念验证，而是一个**经过实际使用打磨的技能集**：

- **60,000+ 开发者** 订阅了他的 newsletter关注技能更新
- **安装量** 涵盖 Claude Code、Codex、Cursor、Copilot 等所有主流 coding agent
- **实践驱动**：这些技能不是理论设计，而是从真实项目使用中提炼出来的

### 3.2 核心技能分类

Matt 的 skills 库分为几个类别：

**Engineering Skills（日常代码工作）**
- `/diagnose`：结构化诊断循环——复现→最小化→假设→验证→修复→回归测试
- `/tdd`：红-绿-重构循环，强制测试先行
- `/grill-with-docs`：苏格拉底式提问，帮助建立项目通用语言（ubiquitous language）
- `/improve-codebase-architecture`：发现代码库中的深度机会

**Productivity Skills（通用工作流）**
- `/grill-me`：彻底审查计划，在开始前解决所有分支
- `/caveman`：压缩通信模式，减少 75% token 使用同时保持技术精度

### 3.3 关键洞察：Skill 的本质是「强制流程」而非「建议」

Matt Pocock 多次强调这些技能的核心目标是**修复 AI 的常见失败模式**。他识别了 4 类主要失败：

> "The most common failure mode in software development is misalignment. You think the dev knows what you want. Then you see what they've built—and you realize it didn't understand you at all."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

解决方案是 `/grill-me`——在开始写代码之前，强制 AI 问足够多的问题，直到完全理解需求。

这与 Anthropic 的设计哲学完全一致：**渐进式披露解决的是上下文效率问题，而 Matt 的技能解决的是 AI 行为规范问题**。两者都在试图解决同一个根本问题——如何让通用 AI 在特定场景下表现得像一个专业的工程师。

---

## 4. 两种视角的交汇：技能系统的演进方向

### 4.1 从文档到工作流的演进

Anthropic 的 PDF Skill 示例展示的是**知识密集型技能**（如何填充表单）。Matt Pocock 的 Skills 展示的是**流程密集型技能**（如何做 TDD、如何诊断问题）。

两者的结合指向一个更大的图景：**未来的 Agent Skill 不仅仅是「告诉 Agent 知识」，而是「引导 Agent 通过正确的流程」**。

### 4.2 技能的「设计时」vs「运行时」

这里有一个重要的设计维度：

| 维度 | Anthropic Skills | Matt Pocock Skills |
|------|-----------------|-------------------|
| **设计时** | 技能作者定义触发条件和内容 | 技能作者定义工作流程和检查点 |
| **运行时** | Agent 根据任务动态判断是否加载 | 强制流程在特定阶段触发 |
| **触发机制** | Agent 自主判断（基于 description） | 系统级强制（不可跳过）|

Matt 的技能更接近「工程规范」——它们不只是建议，而是强制性的流程。Anthropic 的设计更接近「知识库」——Agent 可以在任意时刻选择加载。

这不代表两者有对错之分，而是代表**两种不同的应用场景**：知识密集型任务需要渐进式加载（避免上下文浪费），流程密集型任务需要强制执行（避免 AI 跳过关键步骤）。

### 4.3 技能生态的早期信号

Matt Pocock 的 skills 库已经包含 `/write-a-skill` 技能——教 AI 如何创建新的 Skills。这意味着技能系统正在**自我构建**：

> "As you work on a task with Claude, ask Claude to capture its successful approaches and common mistakes into reusable context and code within a skill."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

一旦 AI 能够创建 Skills，一个自我强化的循环就开始了：AI 使用 Skills → 发现 Skills 的不足 → 创建新的 Skills → 更好的 AI 表现。

---

## 5. 工程实践建议

### 5.1 何时用渐进式加载，何时用强制流程

**用渐进式加载（Anthropic Style）的场景**：
- 知识密集型任务（PDF 处理、API 调用、领域特定操作）
- 上下文窗口受限，需要最大化信息密度
- Agent 需要自主判断何时使用某个技能

**用强制流程（Matt Pocock Style）的场景**：
- 流程密集型任务（TDD、诊断、设计审查）
- 不允许 Agent 跳过关键步骤
- 需要在团队中保持一致的工程标准

### 5.2 构建新 Skill 的检查清单

根据两者的设计原则，一个好的 Skill 应该：

1. **有清晰的边界**：一个 Skill 应该对应一个明确的能力，不是万能的
2. **渐进式设计**：主体在 SKILL.md，详细内容在子文件
3. **可执行部分**：如果某操作是确定性的，用代码而非 prompt
4. **触发条件明确**：description 应该让 Agent 准确判断何时使用

### 5.3 避免的陷阱

- **过度封装**：把所有知识塞进一个 SKILL.md，失去渐进式加载的价值
- **过度依赖 prompt**：确定性的操作应该用代码实现
- **忽视测试**：Matt Pocock 的 `/write-a-skill` 强调测试新的 Skill

---

## 6. 结论与启示

Agent Skills 正在从单一的「SKILL.md 规范」演变为一个多层次的技能生态系统。Anthropic 提供了架构层面的设计哲学（渐进式披露），Matt Pocock 提供了工程实践层面的验证（真实技能集）。

对于构建 Agent 系统的工程师来说，这意味着：

**短期内**，我们可以直接使用 Matt Pocock 的技能集来提升现有 coding agent 的工程能力——这些技能是经过实战验证的，可以直接安装到 Claude Code、Codex、Cursor 等工具中。

**中期内**，Anthropic 的渐进式披露架构为构建专业化 Agent 提供了方法论——任何需要「按需加载领域知识」的场景都应该考虑这种设计。

**长期内**，当 AI 能够创建 Skills 时，我们将进入一个技能自我构建的时代——但在此之前，我们需要先建立对「好技能」的设计原则的共识。

> "Building a skill for an agent is like putting together an onboarding guide for a new hire."
> — [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

这个类比值得深思：当我们为 Agent 构建技能时，我们实际上是在做知识管理——把人类专家的经验封装成 Agent 可复用的形式。这不是一项技术任务，而是一项工程文化的实践。

---

## 参考来源

- [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [mattpocock/skills - GitHub](https://github.com/mattpocock/skills)
- [Matt Pocock: Skills Newsletter](https://www.aihero.dev/s/skills-newsletter)