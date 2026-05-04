# Anthropic 长期运行 Agent 架构：2-Agent Pattern 与 Feature List 机制深度解析

## 核心问题

Anthropic 在 2026 年发布的工程博客中，提出了一个核心命题：**当 Agent 需要跨越多个上下文窗口（context window）连续工作时，现有的 compaction 机制是不够的**。Anthropic 提出了一个 two-fold solution：Initializer Agent + Coding Agent 的双组件架构，配合 feature_list.json 和 progress 文件实现状态持久化。这个方案的本质是什么？它的适用边界在哪里？本文进行深度解析。

---

## 背景：Compaction 为什么不解决根本问题

Anthropic 的工程师在实验中观察到，即使使用 compaction，一个前沿模型（如 Opus 4.5）在一个复杂项目（如克隆 claude.ai 网站）上仍然会失败：

> "Out of the box, even a frontier coding model like Opus 4.5 running on the Claude Agent SDK in a loop across multiple context windows will fall short of building a production-quality web app if it's only given a high-level prompt."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

失败模式有两种：

1. **Agent 试图一次性完成整个项目** — 在实现中途耗尽上下文，留给下一个 session 一个半成品状态，下一个 Agent 需要花大量时间"猜"之前发生了什么
2. **后续 Agent 看到部分功能已完成就宣布项目结束** — 遗漏了待完成的功能

Compaction 的问题是：**它压缩了历史，但没有提供一个可验证的完整性保证机制**。即使 compaction 把历史压缩得很干净，Agent 仍然可能"不知道自己不知道什么"。

---

## 双组件架构：Initializer Agent + Coding Agent

Anthropic 的解法是把 Agent 分成两类角色，用不同的 prompt 控制：

### Initializer Agent（初始化 Agent）

在第一个 session 执行，其任务是：
1. 读取用户的高级需求（如"克隆 claude.ai"）
2. **生成一个结构化的 feature_list.json** — 将需求分解为可验证的功能项，每个功能标注"failing"初始状态
3. 初始化项目结构（init.sh、目录布局）
4. 执行初始 git commit，记录基线状态
5. 创建 claude-progress.txt 用于记录 session 间的进展

关键的设计决策：**feature_list.json 一旦创建，描述（description）和步骤（steps）字段就变成不可变的**，Agent 只能改变 `passes` 字段（false → true），不能删除或修改功能项。Anthropic 选择了 JSON 而非 Markdown，因为模型更不容易"意外修改" JSON 文件。

### Coding Agent（编码 Agent）

在每个后续 session 执行，其工作流程是：
1. 读取 git log 和 progress 文件了解项目状态
2. 读取 feature_list.json 选择优先级最高且 passes=false 的功能项
3. **一次只做一个功能**（避免了一次性做太多导致的半成品问题）
4. 完成后用 Puppeteer MCP 做端到端验证
5. 写 git commit + 更新 progress 文件

> "Once working incrementally, it's still essential that the model leaves the environment in a clean state after making a code change. In our experiments, we found that the best way to elicit this behavior was to ask the model to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Feature List 的完整性保证机制

feature_list.json 是整个系统最关键的设计。它解决了一个根本问题：**如何让 Agent 知道"还有多少东西没做完"**。

```json
[
  {
    "category": "functional",
    "description": "New chat button creates a fresh conversation",
    "steps": [
      "Navigate to main interface",
      "Click the 'New Chat' button",
      "Verify a new conversation is created",
      "Check that chat area shows welcome state",
      "Verify conversation appears in sidebar"
    ],
    "passes": false
  }
]
```

**不变量（Immutable Invariants）**：
- `description` 和 `steps` 是产品需求，不是实现方案——它们在创建后绝不修改
- `passes` 只能从 false 变为 true，**不允许反向修改**（即使 Agent 觉得某个功能"有问题"，也不能把 passes 改回 false，而是要修复实现）
- 禁止删除功能项

这套约束的逻辑是：**如果允许随意修改 feature list，Agent 就有了"重新定义问题"的能力，这会导致上面提到的第二种失败模式（提前宣布项目完成）**。

---

## Testing 机制：为什么端到端测试是关键

Anthropic 发现了另一个常见的 Agent 失败模式：**Agent 会标记功能为"完成"但实际上功能并没有正确工作**。原因是没有端到端的验证机制。

解决方案是给 Agent配备 Puppeteer MCP Server，让它在实现每个功能后，像真实用户一样操作浏览器验证功能：

> "Providing Claude with these kinds of testing tools dramatically improved performance, as the agent was able to identify and fix bugs that weren't obvious from the code alone."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这个经验揭示了一个重要的工程原则：**Agent 的自我验证能力必须被显式地嵌入 harness，而不是依赖 Agent 自行推断**。

---

## Session 启动协议：让新 Agent 快速进入状态

每个 session 开始时，Agent 执行以下步骤：

```
1. pwd — 确认工作目录
2. 读取 git log 和 progress 文件 — 了解近期工作
3. 读取 feature_list.json — 选择下一个要实现的功能
4. 运行 init.sh（如存在）— 重启开发服务器
5. 执行端到端验证 — 确认基础功能仍然正常工作
6. 开始实现新功能
```

这个协议解决了 **"每个新 session 开始时，Agent 需要花多少时间重新理解项目状态"** 的问题。通过把上下文信息结构化地存储在文件中，新 Agent 可以跳过"探索阶段"，直接进入"执行阶段"。

---

## 已知局限与开放问题

Anthropic 在博客结尾坦诚地列出了未解决的问题：

> "Most notably, it's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture. It seems reasonable that specialized agents like a testing agent, a quality assurance agent, or a code cleanup agent, could do an even better job at sub-tasks across the software development lifecycle."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这揭示了一个重要的设计张力：**当前的 two-agent solution 是一个折中方案，它比单 Agent 好，但并不意味着是最优解**。多 Agent 架构（专门的测试 Agent、QA Agent、代码清理 Agent）可能在某些场景下表现更好，但这需要更复杂的 harness 设计。

---

## 与 OpenAI Agents SDK 的设计哲学对比

Anthropic 的方案和 OpenAI 2026 年 4 月发布的 Agents SDK 代表了两种不同的设计哲学：

| 维度 | Anthropic 方案 | OpenAI Agents SDK |
|------|---------------|-------------------|
| 核心抽象 | 2-Agent Pattern（初始化+编码分离） | Model-native harness（模型感知的基础设施）|
| 状态管理 | 结构化文件（feature_list.json + progress） | 外部化状态（Manifest + snapshot/rehydration）|
| 测试机制 | Puppeteer MCP（端到端浏览器自动化）| 内置 sandbox（安全执行环境）|
| 适用场景 | 长时间连续的多 session 编码任务 | 跨文件/工具的通用 agent 任务 |
| 部署方式 | 基于 Claude Agent SDK | 云端 sandbox（Blaxel/Cloudflare/E2B/Vercel 等）|

两者都承认了一个核心事实：**当前 agent 失败的主要原因不是模型能力不足，而是 harness 基础设施不足**。模型负责"知道怎么做"，harness 负责"确保做的东西正确"。

---

## 结论与启示

Anthropic 的这篇工程博客提供了几个重要的工程原则：

1. **结构化状态优于隐式状态**：把"项目还有多少功能没做完"显式地建模为数据结构，比依赖模型"记住"更可靠
2. **完整性验证必须被嵌入 harness**：不能让 Agent 自己判断"功能是否完成"，必须有独立的验证机制
3. **不可变性是防误触的关键**：通过禁止修改 feature list，确保 Agent 无法通过"重新定义问题"来逃避未完成的工作
4. **单 Agent vs 多 Agent 仍有开放空间**：two-agent pattern 是实用的折中，但专门的测试/QA/清理 Agent 可能是下一步方向

> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history. Inspiration for these practices came from knowing what effective software engineers do every day."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

本文的分析基于 Anthropic Engineering Blog 的官方发布内容。feature_list.json 的完整实现可见 GitHub 仓库 [anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)。