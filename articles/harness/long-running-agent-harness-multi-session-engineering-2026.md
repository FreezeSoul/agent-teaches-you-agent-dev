# 长时 Agent 架构：Anthropic 的多窗口连续工程实践

## 核心问题

当 AI Agent 被要求完成需要数小时乃至数天的复杂任务时，如何让 Agent 在离散的会话之间保持连续性？每次新会话能够从上一次中断的地方继续工作，而非从头开始或迷失方向？

Anthropic 在 2026 年的这篇工程博客给出了系统性解法：**Initializer Agent + Coding Agent 双组件架构**，通过结构化的环境管理和进度追踪机制，使 Agent 能够在多个上下文窗口之间持续推进。

> "The core challenge of long-running agents is that they must work in discrete sessions, and each new session begins with no memory of what came before."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

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

Anthropic 的解决方案将 Agent 生命周期分为两个阶段：

```
┌─────────────────────────────────────────────────────┐
│              Initializer Agent（首次会话）           │
│  ├─ 解析用户原始 Prompt                             │
│  ├─ 生成结构化 Feature List（JSON 格式）            │
│  ├─ 创建 init.sh 启动脚本                          │
│  ├─ 创建 claude-progress.txt 进度追踪文件          │
│  └─ 提交初始 git commit（留下完整的基线状态）       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Coding Agent（所有后续会话）             │
│  ├─ 读取 git log + progress.txt 了解当前状态       │
│  ├─ 运行 init.sh 启动开发服务器                    │
│  ├─ 执行端到端测试验证基础功能是否正常             │
│  ├─ 从 Feature List 选择一个未完成的 Feature       │
│  ├─ 实现该 Feature 并更新 progress.txt             │
│  └─ 提交 git commit + 结束会话                     │
└─────────────────────────────────────────────────────┘
```

### 为什么必须是 JSON 格式的 Feature List

Anthropic 最初尝试用 Markdown 管理 Feature List，发现模型容易随意修改或删除条目。改用 JSON 后，模型对文件的操作变得更加可预测：

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

Coding Agent 只能通过修改 `passes` 字段标记功能完成，禁止删除或编辑测试步骤。Anthropic 明确告知 Agent：**"It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."**

---

## 关键机制 1：环境准备的三层文件结构

_initializer agent_ 创建三个核心文件，它们共同构成跨会话的「记忆中枢」：

### 1. init.sh — 可复现的开发环境

```bash
#!/bin/bash
# init.sh - 初始化开发环境
cd /workspace/project
npm install
npm run dev &
sleep 3
echo "Dev server running on port 3000"
```

每次新会话启动时，运行 init.sh 确保开发服务器处于可用状态。

### 2. claude-progress.txt — 进度叙事

```text
[Session 3] 2026-05-01 14:30
- Completed: User authentication flow (JWT-based)
- Completed: Session management with Redis
- In Progress: Real-time notifications via WebSocket
- Next: Chat interface implementation
```

Agent 通过阅读 progress.txt 立即了解项目当前状态，无需遍历整个代码库。

### 3. feature_list.json — 功能验收清单

JSON 格式的结构化功能描述，每个功能包含验收步骤。Agent 只能标记 `passes: true/false`，不能修改功能定义本身。

---

## 关键机制 2：会话启动的标准化流程

每个 Coding Agent 会话启动时，Anthropic 明确要求执行以下标准化步骤：

```
[Assistant] I'll start by getting my bearings and understanding the current state of the project.
[Tool Use] <bash - pwd>
[Tool Use] <read - claude-progress.txt>
[Tool Use] <read - feature_list.json>
[Assistant] Let me check the git log to see recent work.
[Tool Use] <bash - git log --oneline -20>
[Assistant] Now let me check if there's an init.sh script to restart the servers.
<Starts the development server>
[Assistant] Excellent! Now let me navigate to the application and verify that some fundamental features are still working.
<Tests basic functionality>
```

这一流程解决了两个问题：

1. **消除「迷失感」**：新会话不需要猜測项目当前状态
2. **尽早发现破损状态**：在实现新 Feature 前先验证现有功能是否正常，避免「越修越乱」

---

## 关键机制 3：端到端测试作为验收标准

Anthropic 发现了 Agent 的一个典型缺陷：**Agent 倾向于认为代码能跑就是功能正常**。即使功能实际有 bug，Agent 也可能因为没有完整走查用户交互流程而误判为完成。

解决方案是**强制端到端测试**。Anthropic 使用 Puppeteer MCP Server 让 Agent 通过自动化浏览器测试完整的功能流程：

```javascript
// Agent 被要求执行以下测试作为每次会话的第一步
await page.goto('http://localhost:3000');
await page.click('#new-chat');
await page.fill('#message-input', 'Hello');
await page.click('#send-button');
const response = await page.waitForSelector('.ai-response');
// 只有测试通过，才认为上一轮遗留状态正常
```

> "Providing Claude with these kinds of testing tools dramatically improved performance, as the agent was able to identify and fix bugs that weren't obvious from the code alone."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 工程权衡：单 Agent 还是多 Agent

Anthropic 坦承这个 demo 仍然使用单一 Coding Agent，但指出了一个开放问题：

> "It's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture. It seems reasonable that specialized agents like a testing agent, a quality assurance agent, or a code cleanup agent, could do an even better job at sub-tasks."

这与 Cursor 在多 Agent 内核优化中的发现形成呼应——**Planner Agent + Worker Agent 的分工模式**，在复杂长时任务上优于单一 Agent 的全量覆盖。

---

## 与现有方案的对比

| 维度 | 单会话 Agent（无结构化） | Anthropic 双组件架构 | Cursor Planner + Worker |
|------|------------------------|---------------------|------------------------|
| 跨会话连续性 | ❌ 每次从头开始 | ✅ 三层文件结构 | ✅ 协调协议 + 测试循环 |
| One-shot 陷阱 | ❌ 必然发生 | ✅ Feature List 约束 | ✅ 分发 + 重平衡机制 |
| 过早宣布完成 | ❌ 常见 | ✅ JSON 强制验收 | ✅ 独立 benchmark 验证 |
| 环境一致性 | ❌ 依赖手动恢复 | ✅ init.sh 自动重建 | ✅ 标准化启动流程 |
| 测试验收 | ❌ 单元测试为主 | ✅ Puppeteer 端到端 | ✅ SOL-ExecBench 自动化 |

---

## 适用边界与已知局限

### 适用场景

- 需要数小时乃至数天的复杂代码生成任务
- 项目中途需要暂停、恢复的场景（如人工审核、资源限制）
- 多开发者协作环境，需要 AI 编程工具与人类工程师交接

### 尚未解决的局限

1. **视觉识别限制**：Claude 通过 Puppeteer 看不到浏览器原生的 alert modal，导致依赖这些特性的功能更容易出现 bug
2. **Feature List 维护负担**：随着项目规模增长，JSON 文件可能变得难以维护，需要增量压缩策略
3. **通用化程度**：当前 demo 针对全栈 Web 开发优化，其他领域（如科学计算、金融建模）需要定制化适配

> 笔者认为，这个方案的核心价值在于**将工程管理中的「交接文档」机制引入 Agent 系统**——与其让下一个 Agent 靠猜測，不如强制当前 Agent 留下结构化的、可验证的交接产物。

---

## 一句话结论

Anthropic 通过 Initializer Agent + Coding Agent 双组件架构 + 三层文件结构（init.sh / progress.txt / feature_list.json）+ 强制端到端测试，解决了长时 Agent 的跨会话连续性问题。这是目前最具工程落地性的长时 Agent Harness 方案。

---

## 原文引用

> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history. Inspiration for these practices came from knowing what effective software engineers do every day."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

> "We developed a two-fold solution to enable the Claude Agent SDK to work effectively across many context windows: an initializer agent that sets up the environment on the first run, and a coding agent that is tasked with making incremental progress in every session, while leaving clear artifacts for the next session."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

> "This decomposes the problem into two parts. First, we need to set up an initial environment that lays the foundation for all the features that a given prompt requires, which sets up the agent to work step-by-step and feature-by-feature."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

> "The most ambitious tasks in software are open-ended, without a clear solution. Single agent systems struggle here because models are best at narrowly scoped tasks they have already seen during training."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)
