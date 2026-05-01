# Anthropic 多窗口 Agent 架构深度解析：从单会话到无限迭代

## 核心问题

当 AI Agent 被要求完成需要数小时乃至数天的复杂任务时，如何让 Agent 在离散的会话之间保持连续性，每次新会话能够从上一次中断的地方继续工作，而非从头开始或迷失方向？

Anthropic 在 2026 年发布的这篇工程博客给出了系统性解法：**Initializer Agent + Coding Agent 双组件架构**，通过结构化的环境管理和进度追踪机制，使 Agent 能够在多个上下文窗口之间持续推进。

> "The core challenge of long-running agents is that they must work in discrete sessions, and each new session begins with no memory of what came before."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## 问题拆解：Agent 跨会话失败的两种典型模式

Anthropic 团队在使用 Claude Agent SDK 处理多窗口任务时，观察到两种典型的失败模式：

### 模式一：一次完成太多（One-shot 陷阱）

Agent 在单一会话中尝试实现过多功能，导致：
- 在实现中途耗尽上下文窗口，留下半成品功能
- 下一个会话从混乱状态启动，需要大量时间「恢复现场」
- 即使有 compaction 机制，下一个会话接收的指令也不总是清晰无误

### 模式二：过早宣布完成

在部分功能已实现后，后续 Agent 实例查看进度后误判「工作已完成」而停止。

> 笔者的工程经验：在实际项目中，过早宣布完成往往是 Prompt 约束不足导致的——当 Agent 看到已有一堆代码时，它倾向于认为「基础工作已经完成，剩下的只是细节优化」。

## 双组件架构：Initializer Agent + Coding Agent

Anthropic 提出的解法是将 Agent 生命周期分为两个阶段：

### 阶段一：Initializer Agent（仅首次运行）

第一个会话使用专门的初始化 Prompt，要求模型完成三项核心工作：

1. **init.sh 脚本**：包含启动开发服务器、运行基础验证测试的命令
2. **claude-progress.txt**：记录所有 Agent 会话的进度日志
3. **初始 git commit**：展示已添加的文件集合

关键产物是 **feature_list.json**，包含完整的功能需求清单：

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

所有功能初始标记为 `passes: false`，后续 Coding Agent 必须逐一验证并标记。

### 阶段二：Coding Agent（每次会话）

每个后续会话遵循标准化的「启动→工作→收尾」流程：

**启动阶段**：
```
[Tool Use] <bash - pwd>
[Tool Use] <read - claude-progress.txt>
[Tool Use] <read - feature_list.json>
[Tool Use] <bash - git log --oneline -20>
[Tool Use] <bash - ./init.sh>  # 启动开发服务器
```

**验证环节**：启动后立即运行端到端测试，确认应用状态正常后才开始新功能开发。

**工作环节**：每次只处理一个 feature，遵循增量开发原则。

**收尾环节**：更新 feature_list.json 中的 passes 字段，提交 git commit，更新 progress 文件。

> "The best way to elicit this behavior was to ask the model to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file."
> — Anthropic Engineering

## 关键工程机制

### 1. feature_list.json：功能状态机

选择 JSON 而非 Markdown 格式的原因：**模型对 JSON 文件的不当修改概率更低**。

```json
// 功能状态流转
{ "passes": false } → 实现功能 → { "passes": true }
```

Prompt 中的强约束：
> "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."

### 2. claude-progress.txt：跨会话状态传递

每次会话结束时写入进度摘要：
```
=== Session 3 Complete ===
- Implemented chat session persistence (feature #12, passes: true)
- Fixed race condition in message delivery
- Added localStorage backup for offline mode
- Next session priority: feature #15 (notification system)
```

### 3. Puppeteer MCP：端到端测试能力

Anthropic 为 Agent 提供了 Puppeteer MCP Server，使 Agent 能够像真实用户一样操作浏览器：

> "Providing Claude with these kinds of testing tools dramatically improved performance, as the agent was able to identify and fix bugs that weren't obvious from the code alone."

这解决了 Agent 常见的「代码看起来对，但运行时有问题」的盲区。

**已知局限**：Agent 的视觉能力有限，看不到浏览器原生的 alert 弹窗，导致依赖这些机制的功能测试质量较低。

### 4. Git 原子性作为进度回滚机制

```bash
# Agent 通过 git 回滚错误状态
git log --oneline -20  # 查看历史
git revert <commit>    # 安全回滚
git stash              # 临时保存未完成工作
```

## 失败模式对照表

| 失败模式 | 解决方案（Initializer） | 解决方案（Coding Agent） |
|---------|----------------------|------------------------|
| Agent 过早宣布完成 | 建立完整 feature_list.json | 会话开始时读取 feature list，一次只处理一个 feature |
| 环境状态混乱/有 bug | 建立初始 git repo + progress 文件 | 启动时读取 progress + git log，必要时回滚；提交前运行基础测试 |
| 功能测试不充分 | 明确告知需要端到端测试 | 明确告知必须验证功能 end-to-end，不能只依赖代码审查 |
| Agent 需要猜测如何运行应用 | 创建 init.sh 脚本 | 会话开始时读取并执行 init.sh |

## 为什么这不只是「好的实践」而是「必要基础设施」

从工程角度看，多窗口 Agent 的问题本质上是**状态管理问题**：

- 单会话 Agent：状态在内存中，无需显式管理
- 多窗口 Agent：**显式状态必须外化到持久存储**（文件系统、git）

Initializer Agent 的核心价值在于**提前建立状态外化的基础设施**，使后续 Coding Agent 的每次会话都能从良好定义的状态起点开始。

> 笔者认为：这也是为什么许多 Agent 框架在简单场景下工作良好，但在复杂长任务中快速崩溃的原因——它们缺少结构化的状态管理机制，而不是模型的推理能力不足。

## 与传统软件开发方法的类比

| 传统软件工程 | 多窗口 Agent 对应 |
|-------------|-----------------|
| 交接班（Shift Handoff）| 新会话启动 |
| 接班工程师阅读历史日志 | Agent 读取 progress.txt + git log |
| 任务卡片/Issue List | feature_list.json |
| 代码审查 | Puppeteer 端到端测试 |
| CI/CD 回滚机制 | git revert/stash |

## 适用边界与当前局限

**适用场景**：
- 需要数小时以上完成的长任务
- 功能可被明确拆解为独立单元的项目
- 已有代码库需要持续迭代的工作

**当前局限**：
1. **单 Agent vs 多 Agent 未有定论**：尚不清楚一个通用 Agent 还是多个专业化 Agent（测试 Agent、QA Agent、代码清理 Agent）效果更好
2. **视觉能力上限**：Agent 的视觉能力限制了某些 UI bug 的发现
3. **浏览器自动化工具限制**：Puppeteer MCP 看不到原生 alert 弹窗

## 结论

Anthropic 的这篇工程博客展示了一套完整的多窗口 Agent Harness 架构，核心贡献在于：

1. **问题建模**：将「Agent 在多会话间失去连续性」拆解为初始化失败 + 进度追踪失败两类问题
2. **结构化解法**：Initializer Agent 负责建立状态外化基础设施，Coding Agent 负责增量推进
3. **工程验证**：通过 claude.ai clone 示例验证了方案的有效性

> "This research demonstrates one possible set of solutions in a long-running agent harness to enable the model to make incremental progress across many context windows."
> — Anthropic Engineering

对于构建生产级 Agent 系统的工程师而言，这套架构的价值在于：**它不是让模型更聪明，而是让环境更有结构性**。当环境提供了清晰的状态表示（feature_list.json）、可靠的进度追踪（progress.txt）和可回滚的历史（git），Agent 就能在离散会话之间持续有效工作。

---

**引用来源**：
- [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（2026）
- [Anthropic Claude Agent SDK Quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Claude 4 Prompting Guide: Multi-context Window Workflows](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#multi-context-window-workflows)
