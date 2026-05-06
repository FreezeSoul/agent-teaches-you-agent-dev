# Anthropic 两组件 Harness 架构：Initializer Agent + Coding Agent 模式深度解析

## 核心主张

本文要证明：**Anthropic 的两组件 Harness 架构（Initializer Agent + Coding Agent）是目前最具可复现性的长时运行 Agent 工程方案**——它用「初始化 Agent」解决上下文冷启动问题，用「增量 Coding Agent」确保每个 session 都能产生可合并的进展，用「Feature List + Progress File」实现跨会话状态传递。这套方案的核心洞察是：**让 Agent 留下「下一个 Agent 能读懂」的结构化产物，而非依赖模型自己记住上下文。**

---

## 背景：长时运行 Agent 的根本矛盾

### 上下文窗口的有限性与任务的无限性

当 Agent 被要求完成一个需要「数小时甚至数天」的超大任务时，context window 的有限性与任务的无限性之间存在根本矛盾。这个矛盾在两个层面爆发：

**第一层：Agent 试图「一 shotshot」整个任务**
Anthropic 的实验发现，即使在配置了 compaction（上下文压缩）的 Claude Agent SDK 上跑 Opus 4.5，如果只给一个高层 prompt（比如「build a clone of claude.ai」），Agent 会试图在单次上下文窗口内完成整个应用，结果：
- 在实现中途耗尽上下文，留下半成品特性
- 下一个 session 不知道之前做了什么，花大量时间「猜测」代码状态

**第二层：Agent 容易「提前宣布胜利」**
在某些 feature 已经构建完成后，后续 session 的 Agent 会「环顾四周」，看到已有进展，然后宣布任务完成——实际上还有大量 feature 未实现。

> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这个「key insight」揭示了 Anthropic 的核心解法：**不是让模型「记住」，而是让 Agent 留下「下一个 Agent 能读懂」的产物。**

---

## 两组件架构的详细设计

### 组件一：Initializer Agent——建立「第一个 Agent 的上下文」

Initializer Agent 只在**第一个 session** 运行，其职责是构建整个项目的初始化环境：

1. **claude-progress.txt**（进度文件）：记录「谁做了什么、做到了什么程度」
2. **feature_list.json**（特性列表）：结构化记录所有需要的 feature，每个 feature 有 `description`、`steps`、`passes` 字段
3. **init.sh**（启动脚本）：一键启动开发服务器
4. **初始 git commit**：建立版本历史，让后续 Agent 可以回滚

```json
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
```

JSON 格式是关键选择——Anthropic 发现相比 Markdown，JSON 更不容易被模型错误修改或覆盖。

**Initializer 的 Prompt 策略**：不同于普通的 Coding Agent，Initializer Agent 接收的是「展开的高层 spec」，它需要将用户的模糊需求转化为 200+ 个可测试的 feature 条目，每个条目标记为「failing」。

### 组件二：Coding Agent——增量推进，每个 session 都有产出

每个后续 session 由 Coding Agent 驱动，其工作流程是：

1. **读取状态**：`pwd` → `claude-progress.txt` → `feature_list.json` → `git log`
2. **验证环境**：运行 `init.sh` 启动服务器，用 Puppeteer MCP 做端到端验证
3. **选择一个 feature**：从 feature_list.json 中选最高优先级的「passes: false」条目
4. **实现并测试**：确保端到端验证通过后，将该 feature 的 `passes` 改为 `true`
5. **留下产物**：git commit + 更新 claude-progress.txt

> "We refer to these as separate agents in this context only because they have different initial user prompts. The system prompt, set of tools, and overall agent harness was otherwise identical."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这说明「Initializer Agent」和「Coding Agent」本质上是**同一套 harness 的两个不同 prompt 配置**，而不是两个独立的 Agent 系统。

---

## 四个核心失败模式的系统性解决

### 失败模式一：Agent 一 shot 实现整个应用

| 问题 | 解法 |
|------|------|
| Agent 试图在一个 context window 内完成所有功能 | Feature List 将任务分解为 200+ 个独立可测试的 feature，强制逐个完成 |
| 半成品 feature 无法被后续 Agent 理解 | JSON 格式的 feature_list.json 提供清晰的「完成标准」 |

### 失败模式二：Agent 提前宣布任务完成

| 问题 | 解法 |
|------|------|
| 后续 Agent 看到已有进展就停止 | Feature List 提供了完整的功能清单，Agent 必须逐个验证每个 feature 的 `passes: true` |
| Agent 自我验证能力不足 | 强制使用 Puppeteer MCP 做端到端浏览器测试，不能只靠代码检查 |

### 失败模式三：Agent 把环境留在「脏状态」

| 问题 | 解法 |
|------|------|
| 代码有 bug 或未完成就结束 session | `init.sh` + 端到端测试确保每次 session 开始时验证环境是否正常 |
| 进展没有被记录 | 每次 session 必须 git commit + 更新 claude-progress.txt |

### 失败模式四：Agent 不知道「怎么运行这个项目」

| 问题 | 解法 |
|------|------|
| 首个 Agent 需要花时间理解项目结构 | init.sh 提供一键启动脚本 |
| 后续 Agent 需要从零理解环境 | git log + claude-progress.txt 让 Agent 在 3 步内了解项目状态 |

---

## 端到端测试的关键作用

Anthropic 的实验揭示了一个容易被忽视的问题：**Agent 的自我验证能力是有限的**。在代码里看起来正确的功能，端到端验证时可能完全不能用。

解决方案是**强制端到端测试**——Anthropic 要求 Coding Agent 使用 Puppeteer MCP 服务器，通过真实浏览器自动化来验证功能：

> "Providing Claude with these kinds of testing tools dramatically improved performance, as the agent was able to identify and fix bugs that weren't obvious from the code alone."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这意味着 harness 必须给 Agent 提供**超越代码本身的可观测性工具**——浏览器自动化、日志分析、截图对比等。没有这些工具，Agent 只能在「代码看起来对」的层面停止，无法进入「功能实际可用」的层面验证。

---

## 工程可复用性评估

### 这套方案适合什么场景

- **大型全栈 Web 应用**：有明确的 UI 行为可以端到端验证
- **多周目的开发迭代**：需要跨越多天、多人协作的长时项目
- **Feature 数量可枚举**：能用 JSON 结构化描述的项目

### 这套方案的局限性

| 局限性 | 说明 |
|--------|------|
| **面向「有清晰交付标准」的任务** | 如果任务的目标本身是模糊的（比如「探索这个代码库」），feature list 的思路难以应用 |
| **需要每轮端到端测试基础设施** | Puppeteer MCP 或等效的可观测工具是必要条件 |
| **尚未证明对非 Web 领域的泛化** | Anthropic 明确表示当前 demo 优化目标是全栈 Web 开发，其他领域需要验证 |
| **单一 General-purpose Agent vs 专用 Agent 未有结论** | 当前方案使用同一个 Coding Agent，未来可能出现「测试 Agent」「代码清理 Agent」等分工 |

> "Most notably, it's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture."
> — [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这是当前方案的开放问题：通用 Agent vs 专用 Agent 的多 Agent 架构，哪个更优还没有答案。

---

## 与同类方案的对比

### vs. OpenAI Harness Engineering 实验

OpenAI 的百万行代码实验（`openai-harness-engineering-million-lines-zero-manual-code-2026.md`）和 Anthropic 的两组件架构都关注「如何让 Agent 完成超大项目」，但切入角度不同：

| 维度 | Anthropic 两组件 | OpenAI 实验 |
|------|-----------------|------------|
| **核心问题** | 跨 session 状态传递 | 人类角色的根本转变 |
| **工程化程度** | 高度结构化，feature list + progress file | 强调「人类给意图，Agent 执行」 |
| **工具依赖** | 强依赖端到端测试工具（Puppeteer MCP）| 更强调工具链和环境定义 |
| **验证方式** | 每轮端到端验证 + feature passes | 无明确验证机制描述 |

### vs. Cursor Fleet 模式

Cursor 的多 Agent Fleet 模式强调**并行和人类俯瞰**，Anthropic 的方案强调**串行增量推进**。两者并不矛盾——Cursor 适合「并行探索多个方向」，Anthropic 适合「按优先级逐个完成 feature」。

---

## 下一步

如果你正在构建长时运行的 Agent Harness，以下方向值得深入：

- [Anthropic 官方 Quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Claude 4 Prompting Guide: Multi-context Window Workflows](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#multi-context-window-workflows)
- 结合 InsForge 等 Backend-as-a-Service 平台，让 Agent 能独立完成包含数据库、认证、存储的全栈后端开发

---

*本文 source: [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 2026-05*
