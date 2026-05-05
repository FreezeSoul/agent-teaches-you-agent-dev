# 长程 Agent 治理核心机制：Initializer Agent 与 Coding Agent 分离架构

**核心论点**：Anthropic 在 2026 年发布的工程实践中，揭示了长程 Agent 治理的核心矛盾——单 Agent 跨上下文窗口执行时会出现「过度承诺」和「提前退出」两种失败模式。解决方案是将 Agent 角色拆分为 Initializer Agent（初始化环境）+ Coding Agent（增量执行），通过结构化工件（feature list + progress file）实现跨会话状态桥接。

> "We developed a two-fold solution to enable the Claude Agent SDK to work effectively across many context windows: an initializer agent that sets up the environment on the first run, and a coding agent that is tasked with making incremental progress in every session, while leaving clear artifacts for the next session."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 1. 长程 Agent 的两种核心失败模式

当要求一个 Agent 完成复杂任务（如「构建一个类似 claude.ai 的完整 Web 应用」）时，即使具备上下文压缩能力，Agent 在跨多个上下文窗口执行时仍会表现出两种系统性失败：

### 失败模式 1：过度承诺（One-shotting）

Agent 倾向于在一个会话中尝试完成所有功能，导致：
- 代码写到一半耗尽上下文，留下半完成的 feature
- 下一个 Agent 需要猜测之前的状态，花费大量时间「让基础应用重新运行」
- 上下文压缩并不能完美传递「下一步该做什么」的指令

### 失败模式 2：提前退出（Premature Victory）

在项目进行一段时间后，后来的 Agent 实例看到已有进展，认为任务已完成，直接退出。

> "After some features had already been built, a later agent instance would look around, see that progress had been made, and declare the job done."

### 根本原因

这两个问题的根源在于**缺乏明确的进度追踪机制**。人类工程师通过 shift handover（交接班）传递状态，而 Agent 在每个新会话开始时「失忆」——没有任何关于「已完成什么」「还剩什么」「上次离开时环境是否干净」的元信息。

---

## 2. 双 Agent 架构：Initializer + Coding Agent

Anthropic 的解决方案是将 Agent 角色拆分为两个专门阶段：

### 2.1 Initializer Agent（初始化阶段）

仅在第一次会话运行，使用专门的 prompt 要求模型：
1. **创建 feature list**：将用户的高层需求拆解为结构化 JSON 文件，列出所有 end-to-end 功能（如「用户可以打开新对话、输入查询、按下回车、看到 AI 响应」），每个 feature 标记 `passes: false`
2. **创建 init.sh**：启动开发服务器的脚本，确保每次新会话都能快速恢复运行环境
3. **创建 claude-progress.txt**：记录进度日志的文件
4. **提交初始 git commit**：保存原始文件状态，便于回溯

```json
// feature_list.json 示例结构
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

**关键设计决策**：使用 JSON 而非 Markdown 格式存储 feature list，因为模型更不容易意外修改或覆盖 JSON 文件。

### 2.2 Coding Agent（每个后续会话）

每个新会话的 Coding Agent 需要执行「热身程序」：

```
1. 运行 pwd 确认工作目录
2. 读取 git logs 和 progress files 了解最近工作
3. 读取 feature list，选择优先级最高的未完成 feature 开始工作
4. 启动开发服务器，通过 Puppeteer MCP 进行端到端测试，确认环境未被破坏
5. 实现一个 feature，进行测试，标记 passes: true
6. 结束前：git commit + 更新 progress file
```

> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history."

---

## 3. 四个核心失败模式的完整对照表

| 失败模式 | Initializer Agent 行为 | Coding Agent 行为 |
|---------|----------------------|-----------------|
| Agent 宣布任务完成过早 | 创建 feature list（基于输入 spec，包含所有端到端功能描述） | 读取 feature list，每次只选一个 feature 开始工作 |
| Agent 留下有 bug 或未记录代码的环境 | 创建初始 git repo + progress notes file | 读取 progress notes + git commit logs，启动时运行基本测试，结束时 git commit + 更新进度 |
| Agent 过早标记 feature 为完成 | 创建 feature list | 所有 feature 都要自我验证，只有经过仔细测试后才标记 passes |
| Agent 浪费时间理解如何运行应用 | 创建 init.sh 脚本（可运行开发服务器） | 启动时读取 init.sh |

---

## 4. 为什么这个架构有效：机制分析

### 4.1 渐进式披露（Progressive Disclosure）

双 Agent 架构通过「两次加载」实现渐进式信息披露：

- **第一层**：Agent 启动时，系统 prompt 仅加载每个 installed skill 的 `name` 和 `description`，让模型知道何时该触发某个 skill
- **第二层**：当模型判断某个 skill 相关时，读取完整的 `SKILL.md` 进入上下文
- **第三层**：如果 skill 包含额外文件（如 reference.md、forms.md），模型可以在需要时主动发现和读取

这与 feature list 机制完全一致——Agent 不需要在第一次启动就知道所有细节，而是随着任务推进逐步加载所需信息。

### 4.2 清洁状态（Clean State）要求

每次会话结束前要求 Agent 将环境恢复到「可合并到 main 分支」的状态：
- 无重大 bug
- 代码有序且有文档
- 其他开发者无需清理就能直接开始新功能开发

这解决了传统 Agent 循环中「每下一个 Agent 都得先收拾烂摊子」的资源浪费问题。

### 4.3 测试作为第一公民

Anthropic 发现，如果不明确要求使用浏览器自动化工具进行端到端测试，Claude 倾向于：
- 做代码修改
- 运行单元测试或 curl 命令
- 但无法识别 feature 实际上没有端到端工作

> "In the case of building a web app, Claude mostly did well at verifying features end-to-end once explicitly prompted to use browser automation tools and do all testing as a human user would."

这说明**测试不是开发的附属品，而是 Agent harness 的必需组件**。

---

## 5. 当前局限与开放问题

Anthropic 在文章中明确指出仍存在的挑战：

### 5.1 单 Agent vs 多 Agent 尚未定论

> "Most notably, it's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture. It seems reasonable that specialized agents like a testing agent, a quality assurance agent, or a code cleanup agent, could do an even better job at sub-tasks."

这是一个核心开放问题：通用 Agent 在所有场景下是否最优，还是应该引入专门的测试 Agent、QA Agent、代码清理 Agent？

### 5.2 视觉能力与浏览器自动化局限

Claude 无法通过 Puppeteer MCP 看到浏览器原生的 alert modal，导致依赖这类 modal 的 feature bug 率更高。

### 5.3 当前 Demo 的领域局限性

当前实现针对全栈 Web 开发优化，尚不清楚其他领域（如科学研究、金融建模）是否适用相同原则。

---

## 6. 工程实践建议

基于 Anthropic 的研究结论，对于构建长程 Agent 系统：

1. **Feature list 必须结构化**：用 JSON 而非 Markdown，避免模型意外修改
2. **每次会话必须包含热身 + 清洁退出**：热身读 progress/git，退出前 git commit + 更新进度
3. **测试工具必须作为一等公民**：不是可选项，而是 harness 的必需组件
4. **init.sh 是关键**：让每个新 Agent 能在 30 秒内确认环境是否损坏，而不是直接开始写代码
5. **考虑多 Agent 分工**：测试 Agent、QA Agent、代码清理 Agent 可能比通用 Agent 效果更好

---

## 7. 与 Agent Skills 的协同关系

值得注意的是，Anthropic 在 2026 年初发布的 [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) 与长程 Agent 治理在设计哲学上高度一致：

- **Agent Skills** 通过 SKILL.md 的 YAML frontmatter 实现「元信息加载 + 按需展开」的两阶段触发
- **双 Agent 架构** 通过 feature list + progress file 实现「状态摘要 + 完整上下文」的跨会话桥接

两者都遵循同一个核心原则：**不要在第一次加载时塞满上下文，而是让 Agent 在需要时主动发现和加载信息**。

---

## 参考文献

- [Effective harnesses for long-running agents - Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Equipping agents for the real world with Agent Skills - Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Autonomous Coding Quickstart - Anthropic GitHub](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)