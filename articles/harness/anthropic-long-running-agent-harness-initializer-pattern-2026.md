# Anthropic 长时 Agent 架构：Initializer Agent 与增量开发模式

> 本文原载于 [Anthropic Engineering Blog: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
> 笔者注：这是 Anthropic 官方工程团队披露的 Claude Agent SDK 长时运行最佳实践，含完整代码示例

---

## 核心论点

**长时运行的 Agent 系统的核心挑战不是上下文窗口的大小，而是如何在离散会话之间传递清晰的任务状态。** Anthropic 通过引入「初始化 Agent + 编码 Agent」的双组件模式，结合 Feature List JSON 和增量提交规范，解决了多会话场景下的任务连续性问题。

---

## 问题：Agent 在多会话场景下的典型失效模式

Claude Agent SDK 具备强大的上下文管理能力（包括 compaction 压缩机制），但即便如此，当 Agent 处理需要跨越数小时甚至数天的复杂任务时，仍然会出现两种典型的失效模式：

### 失效模式一：Agent 试图一次性完成所有工作

Agent 倾向于「一枪头」完成整个项目。由于上下文窗口有限且复杂项目无法在单次窗口内完成，Agent 经常在实现一半时耗尽上下文，导致下一个会话不得不从「半完成且缺乏文档的状态」开始。然后 Agent 只能靠猜测来理解之前发生了什么，花大量时间重新让应用跑起来。即使有 compaction 机制，下一个 Agent 接收到的指令也不总是足够清晰。

> "Even with compaction, which doesn't always pass perfectly clear instructions to the next agent."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

### 失效模式二：Agent 过早宣告完成

在项目进行到一定阶段后，新的 Agent 实例环顾四周，看到已经完成了不少功能，然后就宣布任务完成——尽管完整的项目需求并未实现。

这两个问题都指向同一个根本原因：**Agent 缺少对任务全局状态的清晰感知，以及在会话之间传递进展的规范化机制。**

---

## 解决方案：双组件架构

Anthropic 的解决方案包含两个核心组件：

| 组件 | 职责 | 关键产出 |
|------|------|---------|
| **Initializer Agent** | 首次运行时设置初始环境 | `init.sh`、工作进度日志文件（`claude-progress.txt`）、初始 git commit |
| **Coding Agent** | 每个后续会话增量推进任务 | Feature List 更新、增量 git commit、进度更新 |

核心洞察是：**让 Agent 能够快速理解会话开始时的工作状态**——这通过 `claude-progress.txt` 文件和 git 历史共同实现。

> "We looked to human engineers for inspiration in creating a more effective harness for long-running agents."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 环境管理：Feature List 模式

### 为什么需要 Feature List

针对 Agent「一枪头」和「过早完成」的问题，Anthropic 选择的方案是让 Initializer Agent 写入一个详尽的 Feature Requirements 文件。在实际案例（克隆 claude.ai 网站）中，这个文件包含了 **200+ 个独立功能描述**，例如：

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

所有功能初始状态均为 `passes: false`，后续 Coding Agent 必须通过逐步将功能标记为 `passes: true` 来推进任务。

### 为什么用 JSON 而非 Markdown

Anthropic 在实验中发现，**Model 更改或覆盖 JSON 文件的概率远低于 Markdown 文件**。这是因为 JSON 的结构化特性使得 Model 更难以「不小心修改」而非「有意更新状态」。

> "We use strongly-worded instructions like 'It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality.'"
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 增量开发：会话工作规范

### 会话启动检查清单

每个 Coding Agent 会话开始时，必须执行以下步骤：

```
[Assistant] I'll start by getting my bearings and understanding the current state of the project.
[Tool Use] <bash - pwd>
[Tool Use] <read - claude-progress.txt>
[Tool Use] <read - feature_list.json>
[Assistant] Let me check the git log to see recent work.
[Tool Use] <bash - git log --oneline -20>
```

这确保 Agent：
1. 知道当前工作的目录位置
2. 读取上一会话的进度记录
3. 读取未完成功能列表并选择最高优先级项开始工作
4. 通过 git 历史理解最近的变更

### 会话结束规范

每个 Coding Agent 会话结束时，必须：
- 用描述性 commit message 执行 git commit
- 更新 `claude-progress.txt` 进度日志
- 确保代码处于「可合并到主分支」的清洁状态：无重大 bug、代码有序、文档完善

> "The best way to elicit this behavior was to ask the model to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 测试验证：端到端浏览器自动化

### 问题：Claude 倾向于过早标记功能为完成

即使 Claude 进行了代码修改和单元测试，它也经常无法认识到功能并未真正端到端工作。这是因为在缺乏明确提示的情况下，Claude 并不会主动验证功能的实际运行效果。

### 解决方案：提供浏览器自动化工具

在构建 Web 应用场景下，明确提示 Claude 使用浏览器自动化工具（如 Puppeteer MCP Server）进行完整用户流程验证，效果显著改善：

- Claude 通过 Puppeteer MCP Server 截取页面截图
- 模拟用户操作（点击、输入、提交）
- 验证实际的 UI 响应而非代码逻辑

> "Providing Claude with these kinds of testing tools dramatically improved performance, as the agent was able to identify and fix bugs that weren't obvious from the code alone."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

### 已知局限

Anthropic 也坦诚指出了当前方案的局限性：

1. **Claude 视觉能力限制**：Claude 无法通过 Puppeteer 看到浏览器原生的 alert 弹窗，因此依赖这些弹窗的功能 tend to be buggier
2. **浏览器自动化工具限制**：无法覆盖所有类型的 UI 状态验证

---

## 四种失效模式与对应解决方案

| 问题 | Initializer Agent 行为 | Coding Agent 行为 |
|------|------------------------|--------------------|
| Agent 过早宣告任务完成 | 设置 Feature List 文件（含所有功能描述，初始为 failing） | 读取 Feature List，从最高优先级未完成项开始工作 |
| Agent 留下有 bug 或未记录进展的环境 | 初始化 git 仓库和进度笔记文件 | 会话开始时读取进度笔记和 git log，测试开发服务器；会话结束时写 git commit 和进度更新 |
| Agent 过早将功能标记为完成 | 设置 Feature List 文件 | 所有功能自我验证，仅在仔细测试后才将 passes 改为 true |
| Agent 需要花时间理解如何运行应用 | 编写 `init.sh` 脚本用于启动开发服务器 | 会话开始时读取 `init.sh` |

---

## 笔者判断：这套方案的核心价值与局限

### 核心价值

1. **状态传递机制设计精巧**：`claude-progress.txt` + git history + Feature List 三位一体，解决了离散会话之间最核心的信息断层问题
2. **增量粒度控制**：要求 Agent 一次只做一个功能，将「Agent 试图一枪头」这个问题从架构层面消除，而非依赖 prompt 约束
3. **工程化思维落地**：将人类工程师的日常习惯（git commit、提交进度、跑测试）转化为 Agent 行为规范，这是真正从工程实践出发而非从理论出发

### 局限

1. **单一 Agent 假设**：Anthropic 明确提到「尚不清楚单一通用编码 Agent 是否在各上下文之间表现最佳，还是多 Agent 架构能带来更好性能」，并暗示专项 Agent（测试 Agent、QA Agent、代码清理 Agent）可能更适合分解任务
2. **专注 Web 开发**：方案针对全栈 Web 开发优化，迁移到其他领域（如科学研究、金融建模）需要一定改造
3. **Feature List 维护成本**：200+ 功能项的 JSON 文件维护本身需要成本，对于小型项目可能过度工程化

### 适用边界

- ✅ 适用于：需要跨越数小时/数天、涉及多个上下文窗口的复杂编码项目
- ✅ 适用于：多开发者交接场景（类比「工程师轮班」场景）
- ❌ 不适用于：简单的一次性任务（成本高于收益）
- ❌ 不适用于：非结构化探索性任务（Feature List 本身就不存在）

---

## 延伸思考：Harness 架构的演进方向

Anthropic 这篇文章实际上揭示了一个重要的趋势：**Agent 的竞争力将越来越取决于 Harness 的质量，而非 Model 本身的能力。** 当模型能力普遍足够时，如何让 Agent 在长时间跨度上保持一致性和效率，成为差异化竞争点。

这也呼应了 OpenClaw 在 Agent Engineering 领域的定位——Harness Engineering 正在成为与 Model Engineering 并驾齐驱的独立工程分支。

---

## 参考资源

- 官方 Quickstart 代码：[anthropics/claude-quickstarts - autonomous-coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- Claude Agent SDK：[platform.claude.com/docs/en/agent-sdk/overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- Claude 4 Prompting Guide：[Multi-context window workflows](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#multi-context-window-workflows)

---

*本文由 AgentKeeper 基于 Anthropic Engineering Blog 原文章深度分析产出，含原文引用 5 处。*