# Anthropic 双组件 Harness 架构：Initializer Agent + Coding Agent 的工程实践

## 核心问题

如何让 Agent 在跨多个上下文窗口的长时间任务中保持一致的进展？

Anthropic 在 2026 年发布的工程文章中提出了一个关键洞察：**单一大一统 Agent 无法有效处理超长时间跨度的复杂任务**，必须通过多角色分工来解决。这是继 Claude Code Postmortem 之后，Anthropic 在 Harness 工程领域的又一次重要实践输出。

---

## 问题分析：长时间运行 Agent 的双重失败模式

Anthropic 观察到，即使使用 Opus 4.5 这样的前沿模型，在跨多个上下文窗口的长时间任务中也会出现两种典型的失败模式：

### 失败模式一：One-Shot 过度

Agent 倾向于一次性完成整个任务，而不是分阶段推进。这导致：

- 在实现中途耗尽上下文窗口
- 下一个 Agent Session 面对的是一个半成品且无文档的状态
- 需要花费大量时间"考古"之前的工作

> 官方原文：
> "The agent tended to try to do too much at once—essentially to attempt to one-shot the app. Often, this led to the model running out of context in the middle of its implementation, leaving the next session to start with a feature half-implemented and undocumented."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

### 失败模式二：过早宣布完成

在部分功能实现后，Agent 会"环顾四周"，看到已有进展就认为任务完成了，忽略剩余的未完成功能。

---

## 双组件解决方案：Initializer Agent + Coding Agent

Anthropic 的解决方案是将 Agent 角色分离为两个专门的组件：

### 组件一：Initializer Agent

首次运行时使用，专门负责：

| 职责 | 具体产出 |
|------|---------|
| 环境初始化 | `init.sh` 启动脚本 |
| 进度追踪 | `claude-progress.txt` 进度日志 |
| 特性规范 | `feature_list.json` 功能清单（200+ 项） |
| 版本控制 | 初始 git commit 记录 |

**关键设计：feature_list.json**

这是一个结构化的 JSON 文件，每个功能包含：

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

Anthropic 选择 JSON 而非 Markdown 的原因是：**模型对 JSON 文件的不当修改概率更低**。这体现了 Harness 设计中对模型行为不确定性的规避。

### 组件二：Coding Agent

每次 Session 使用，专门负责：

1. **启动时恢复状态**：读取 `claude-progress.txt` 和 git log
2. **增量工作**：每次只实现一个 feature
3. **测试验证**：使用 Puppeteer MCP 进行端到端测试
4. **收尾工作**：git commit + 进度更新

> 官方原文：
> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 关键机制解析

### 1. Feature List 的双重作用

Feature List 既是对任务的完整分解，也是对进度的客观记录：

- **约束 One-Shot 行为**：Agent 必须在清单中选择下一个要实现的 feature，无法"一口气做完"
- **防止过早完成**：已实现的 feature 必须通过端到端测试才能标记为 `passes: true`

### 2. 端到端测试的必要性

Anthropic 发现，Agent 在代码修改后倾向于"自我感觉良好"但实际功能不工作。解决方案是提供 Browser 自动化工具（Puppeteer MCP）让 Agent 像真实用户一样操作界面。

> 官方原文：
> "In the case of building a web app, Claude mostly did well at verifying features end-to-end once explicitly prompted to use browser automation tools and do all testing as a human user would."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**已知限制**：Claude 无法看到浏览器原生的 alert modal，导致依赖这些 modal 的功能 bug 率较高。

### 3. Git 作为状态恢复机制

Git commit history + git revert 提供了：
- 可审计的进度记录
- 错误代码的快速回滚
- 并行试验的安全隔离

---

## 失败模式与解决方案对照表

| 失败模式 | Initializer Agent 行为 | Coding Agent 行为 |
|---------|----------------------|------------------|
| One-Shot 过度 | 建立 feature list 分解任务 | 每次只选一个 feature 实现 |
| 环境状态混乱 | 初始化 git repo + progress 文件 | 启动时读取状态，收尾时 commit |
| 过早宣布完成 | 建立 feature list 定义完成标准 | 端到端测试验证后才标记 passes |
| 不知道如何运行 | 编写 init.sh 启动脚本 | 启动时执行 init.sh |

---

## 与 Claude Code Postmortem 的关联

本篇文章与上轮产出的 Claude Code April 2026 Postmortem 形成互补：

| 维度 | Claude Code Postmortem | 双组件 Harness |
|------|----------------------|----------------|
| **问题域** | 已有产品的质量回归 | 新架构设计 |
| **关注点** | 三个独立问题的根因 | 系统性工程解决方案 |
| **产出** | 警示录（工程教训） | 设计模式（工程实践） |
| **演进关系** | 修复 → 预防 | 预防 → 架构 |

两者共同构成了 Anthropic 在 Harness 工程领域的完整视图：**问题诊断 + 架构设计**。

---

## 未来方向：多 Agent 专业分工

Anthropic 在文章结尾提出了一个开放问题：

> "It’s still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture. It seems reasonable that specialized agents like a testing agent, a quality assurance agent, or a code cleanup agent, could do an even better job at sub-tasks."

这指向了一个明确的演进方向：

```
当前：Initializer Agent + Coding Agent（双角色）
未来：Initializer + Coding Agent + Testing Agent + QA Agent + Code Cleanup Agent（多角色）
```

每个专门的 Agent 负责软件开发生命周期中的一个特定阶段，通过协作完成复杂任务。这与 Cursor 的 Planner/Worker 架构（已在 [Planner/Worker 双组件架构分析](./planner-worker-multi-agent-autonomous-coding-architecture-2026.md) 中记录）形成了技术路线上的共鸣。

---

## 工程判断

### 适用场景

- ✅ 超长周期任务（数小时到数天）
- ✅ 需要跨 Session 保持一致性
- ✅ 任务可被分解为离散的 feature

### 不适用场景

- ❌ 短时一次性任务（反而增加复杂度）
- ❌ 难以定义明确完成标准的任务
- ❌ 需要实时人类反馈的探索性任务

### 核心启示

> 笔者认为：双组件架构的核心价值不在于"多 Agent"，而在于**引入了任务分解和状态恢复的显式机制**。任何一个长时间运行的 Agent 系统，都需要回答两个问题："下一步做什么？"和"如何从中断处继续？"。Anthropic 选择了 Feature List + Git History 这套组合，正是将工程实践中的人类工作模式（任务清单 + 版本控制）显式化给 Agent。

---

## 参考文献

- [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic Claude 4 Prompting Guide: Multi-context window workflows](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#multi-context-window-workflows)
- [Anthropic Claude Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [claude-quickstarts: autonomous-coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
