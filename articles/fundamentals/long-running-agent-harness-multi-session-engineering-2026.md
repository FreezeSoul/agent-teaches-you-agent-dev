# 多会话 Agent 的工程挑战：Anthropic 的 Harness 设计实践

> 本文深入解析 Anthropic Engineering 发布的「多会话 Agent Harness 设计」，剖析跨越多个上下文窗口实现持续编码的工程难题与解决方案。

## 核心问题：长时任务与有限上下文窗口的根本矛盾

当 AI Agent 被要求完成横跨数小时甚至数天的复杂任务时，一个根本性矛盾浮现：**上下文窗口是有限的，而复杂项目无法在单个窗口内完成**。

Anthropic 工程师在内部实验中遇到了两种典型的 Agent 失败模式：

**失败模式一：Agent 试图一次性完成所有工作**

> "Often, this led to the model running out of context in the middle of its implementation, leaving the next session to start with a feature half-implemented and undocumented."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

即便启用了上下文压缩（compaction），Agent 在上下文耗尽后，下一个 Agent 实例接收到的是不完整的、缺乏清晰指令的状态。

**失败模式二：Agent 过早宣布任务完成**

在某些功能已经构建完成后，后续的 Agent 实例会环顾四周，看到已经有进展，就直接宣布工作完成。

## 双 Agent 解决方案：Initializer Agent + Coding Agent

Anthropic 的解法是将单一 Agent 循环拆分为两个明确分工的 Agent：

```
┌─────────────────────────────────────────────────────────┐
│ Initializer Agent（第 0 个会话）                         │
│ 任务：在第一个会话设置完整的初始环境                       │
│ 产出：                                                  │
│   - init.sh：启动开发服务器                              │
│   - claude-progress.txt：进度日志                        │
│   - feature_list.json：完整功能列表（200+ 条目）          │
│   - 初始 git commit：记录初始化文件状态                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Coding Agent（第 1-N 个会话）                            │
│ 任务：每次会话只推进一个功能，同时留下干净的代码状态        │
│ 行为模式：                                              │
│   1. 读取 progress 文件了解上次进度                       │
│   2. 阅读 feature_list.json 选择最高优先级未完成功能      │
│   3. 实现该功能，提交 git commit                          │
│   4. 更新 progress 文件                                   │
└─────────────────────────────────────────────────────────┘
```

> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## Feature List：对抗「一次性完成」倾向的结构化机制

Initializer Agent 会根据用户初始需求生成一个包含 200+ 条功能描述的结构化 JSON 文件。每条功能条目格式如下：

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

关键设计决策：**所有功能初始状态均为 `passes: false`，且 Agent 只被允许修改 `passes` 字段**。Anthropic 工程师明确禁止 Agent 删除或编辑测试描述：

> "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."

选择 JSON 而非 Markdown 格式的原因：**模型对 JSON 文件的不当修改或覆盖的抵抗力更强**。

## 增量推进的闭环：feature_list.json + git commit + progress file

三个构件形成完整的增量推进闭环：

| 构件 | 作用 | Agent 操作 |
|------|------|-----------|
| `feature_list.json` | 功能状态跟踪 | 每次只标记一个 feature 为 `passes: true` |
| `git commit` | 可回归的代码快照 | 每完成一个功能即提交，含描述性 commit message |
| `claude-progress.txt` | 会话间上下文传递 | 记录已完成工作和下一步计划 |

这种设计解决了一个关键问题：**当 Agent 在新的会话中醒来时，它需要一种快速了解项目状态的方式**。传统的上下文压缩传递的信息不够清晰，而这三个构件让 Agent 能够在几个基本步骤内搞清楚状况。

## 测试闭环：Browser Automation 作为端到端验证

Anthropic 发现的第三个常见失败模式：**Agent 在没有端到端验证的情况下标记功能为完成**。

解决方案是显式提供浏览器自动化工具（Puppeteer MCP Server），让 Agent 能够像真实用户一样与 Web 应用交互：

> "In the case of building a web app, Claude mostly did well at verifying features end-to-end once explicitly prompted to use browser automation tools and do all testing as a human user would."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这带来了显著的性能提升，但仍有已知局限：Claude 的视觉能力存在限制，且某些浏览器原生 alert 弹窗无法通过 Puppeteer 检测到。

## 典型会话的 Agent 对话流

一个标准会话以以下对话序列开始：

```
[Assistant] I'll start by getting my bearings and understanding the current state of the project.
[Tool Use] <bash - pwd>
[Tool Use] <read - claude-progress.txt>
[Tool Use] <read - feature_list.json>
[Assistant] Let me check the git log to see recent work.
[Tool Use] <bash - git log --oneline -20>
[Assistant] Now let me check if there's an init.sh script to restart the servers.
[Starts the development server]
[Assistant] Excellent! Now let me navigate to the application and verify that some fundamental features are still working.
<Tests basic functionality>
```

**先测试再实现**——这是 Anthropic 发现的最重要的最佳实践之一。如果应用处于损坏状态，Agent 应该先修复破坏的代码，而不是继续添加新功能。

## 工程判断：多 Agent 架构的开放问题

Anthropic 的工程师明确指出，当前方案仍有未解决的开放问题：

> "Most notably, it's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

Anthropic 认为，专门化的 Agent（测试 Agent、质量保障 Agent、代码清理 Agent）可能在软件开发生命周期的各个子任务上表现更好。当前方案使用的是**同一套 system prompt + tools**，仅在初始 prompt 上有所不同。

## 对比 Cursor Long-Running Agents 的设计差异

Anthropic 的方案与 Cursor 的 Long-Running Agents 研究存在一个关键差异：

| 维度 | Anthropic 方案 | Cursor 方案 |
|------|----------------|-------------|
| 核心机制 | Feature List + Progress File + Git | 规划审批 + 多 Agent 交叉检查 |
| 会话间状态 | 显式进度文件 + git history | 规划文档 + 任务队列 |
| 验证方式 | Puppeteer MCP 端到端测试 | Agent 自我验证 + 输出检查 |
| 任务分解 | 单 Agent 增量推进 | 多 Agent 协作分工 |

> 笔者认为，两种方案代表了对「多 Agent」架构的不同理解：Anthropic 强调**单一 Agent 的有序延续**（通过结构化构件实现会话间的记忆传递），而 Cursor 强调**多 Agent 的并行协作**（通过规划审批和交叉检查实现质量保障）。

## 核心工程洞察

**1. Harness 组件是临时的，但选择是永久的**

Anthropic 明确指出：每个 harness 组件的存在都是因为模型当前做不到。当模型改进时，这些组件会变得不再必要。但反过来想：**在选择 harness 架构时，实际上也在影响模型的训练方向**，因为模型可能对特定 harness 产生适应性。

**2. 结构化约束 > 自然语言指导**

禁止删除 feature 条目的约束比「请仔细测试」这样的自然语言指导有效得多。当约束可以被验证时，它才真正起作用。

**3. 「先测试再实现」是长时任务的元规则**

无论使用何种架构，长时 Agent 都应该在实现新功能前先验证现有功能的完整性。这适用于所有类型的 Agent 系统。

---

## 引用来源

- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Anthropic Engineering Blog，2026
- [Expanding our long-running agents research preview](https://www.cursor.com/blog/long-running-agents) — Cursor Blog，2026
- [Build agents that run automatically](https://www.cursor.com/blog/automations) — Cursor Blog，2026
