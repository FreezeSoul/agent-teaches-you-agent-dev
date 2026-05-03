# Agentic Loop 与 Long-Running Agent 的工程挑战：Anthropic 双组件 Harness 架构深度解析

**核心主张**：长时运行 Agent 的核心挑战不是上下文窗口不足，而是**会话边界导致的状态丢失与目标偏移**。Anthropic 通过Initializer Agent + Coding Agent 的双组件分工，配合 Feature List JSON 和增量进度模式，将这一工程难题转化为可执行的状态管理协议。

**读者画像**：有 Agent 开发经验，理解 ReAct / Tool Use 基础机制，但未系统处理过长时多会话场景的工程师。

**核心障碍**：大多数 Agent 框架默认每次会话是「从零开始」——没有机制保证下一会话能继承上一会话的「清洁状态」，导致项目进度丢失或 Agent 重复劳动。

---

## 1. 为什么「上下文压缩」不够：长时运行 Agent 的两个失效模式

Anthropic 在 Claude Agent SDK 的实验中发现，即使启用了上下文压缩（compaction），纯通用 Agent 在多会话场景下仍会陷入两类失效：

**失效模式一：Agent 试图单次完成整个项目**

典型表现：从高层次 prompt（如「构建一个 claude.ai 克隆」）出发，Agent 在单次上下文中试图实现全部功能，导致：
- 上下文在实现中途耗尽，下一会话面对的是「半完成、未归档」的状态
- 下一会话 Agent 需要「猜」前一个会话做了什么，花费大量时间恢复基础可运行状态

> "Even with compaction, which doesn't always pass perfectly clear instructions to the next agent."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**失效模式二：Agent 过早宣告项目完成**

在某些功能已实现后，新会话的 Agent 会环视代码库，看到已有进度，直接声明任务完成——忽略未完成的部分。

这两个失效模式的根因不是模型能力不足，而是 **Harness 缺乏「会话边界协议」**：没有机制告诉每一会话「你已经做到哪一步」「还需要做什么」「如何判定完成」。

---

## 2. 双组件架构：Initializer Agent 与 Coding Agent 的职责分离

Anthropic 的解决方案是将长时运行场景拆分为两个不同角色的 Agent：

### 2.1 Initializer Agent（初始化 Agent）

**触发时机**：项目第一次运行，即第一个上下文窗口。

**职责**：基于用户的高层次 prompt，搭建完整的初始环境，包括：

| 产物 | 作用 |
|------|------|
| `init.sh` | 可执行的开发环境启动脚本（启动本地服务、初始化依赖） |
| `feature_list.json` | 结构化的功能清单，包含所有需要实现的功能项，每项标记 `passes: false` |
| `claude-progress.txt` | 进度日志，记录每个会话完成的工作 |
| 初始 git commit | 展示已添加文件的快照 |

Feature List JSON 的格式示例：

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

**设计原则**：Initializer 的核心目标是建立「完整的功能地图」，让后续 Coding Agent 始终有明确的未完成项可查询。Anthropic 选择 JSON 而非 Markdown，因为模型对 JSON 的修改行为更可预测（不易出现意外覆盖）。

### 2.2 Coding Agent（编码 Agent）

**触发时机**：除第一次外的所有会话。

**职责**：在每个会话中：
1. 读取 `claude-progress.txt` 和 git log，恢复上一会话的工作状态
2. 运行 `init.sh` 启动开发服务器，验证当前应用是否处于可运行状态（baseline 测试）
3. 从 `feature_list.json` 中选择**最高优先级且 passes=false** 的功能项
4. 实现该功能，进行端到端测试
5. 将 `passes` 改为 `true`，提交 git commit，更新 progress 文件

**增量进度的关键约束**：Anthropic 要求 Coding Agent 只在上一功能通过测试后才开始下一个，且必须留下「可合并到主分支」状态的代码——无重大 bug、代码有序、有关键文档。

> "By 'clean state' we mean the kind of code that would be appropriate for merging to a main branch: there are no major bugs, the code is orderly and well-documented."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 3. Feature List JSON：让 Agent 自我追踪进度的结构化协议

Feature List 是整个双组件架构的核心数据载体。它的设计解决了三个问题：

### 3.1 防止「过早完成」

传统的进度追踪（如简单的 TODO 列表）容易被 Agent 在发现已有部分实现后跳过。Feature List 的设计强制每个功能项都必须显式标记为 `passes: true` 才能算完成——且这个标记必须经过实际测试验证。

Anthropic 的 prompt 约束：

> "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."

禁止删除或修改测试条目，违者视为功能不完整。

### 3.2 提供增量粒度的任务分配

Feature List 将大型项目拆解为可独立验证的功能单元。每次 Coding Agent 只处理一个 `passes: false` 的条目，避免了「试图一次做完」的原发倾向。

在 claude.ai 克隆的案例中，Initializer 生成了超过 200 个功能项，每项都有明确的验证步骤。这使得整个项目可以通过「逐个击破」完成，而非在单个长上下文中挣扎。

### 3.3 作为跨会话的上下文摘要

Feature List 是比压缩后的原始代码更高效的工作状态摘要。每个新会话的 Agent 只需读取 Feature List，就能快速判断「还剩什么要做」，而不必重新遍历整个代码库。

---

## 4. 清洁状态协议：Git 提交与 Progress 文件的工程契约

除了 Feature List，Anthropic 还要求每个 Coding Agent 在会话结束时：

1. **提交带有描述性信息的 git commit**：记录本次完成的工作
2. **更新 claude-progress.txt**：简述本次做了什么、下一步是什么

这两份产物构成了跨会话的「双向恢复通道」：
- `git log`：可以追溯任意历史状态，发现错误实现时可以回滚
- `claude-progress.txt`：快速了解当前进度和下一步方向

> "We found that the best way to elicit this behavior was to ask the model to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

这与人类工程师在换班时的做法完全一致：交接时需要留下「可读的进度记录」和「可恢复的代码状态」。

---

## 5. 端到端测试作为会话启动仪式

Anthropic 的实验中发现了一个反直觉的设计：**每个 Coding Agent 在开始新功能之前，必须先运行一次基础功能的端到端测试，验证应用当前处于可用状态。**

在 Web 应用的场景中，这意味着：
- 启动本地开发服务器
- 使用 Puppeteer MCP 模拟用户操作（新建对话、发送消息、接收回复）
- 验证基础功能仍然正常

只有验证通过后，才开始新功能的实现。

> "If the agent had instead started implementing a new feature, it would likely make the problem worse."

这个设计背后是一个关键洞察：**长时运行 Agent 的累积状态损坏往往是无声的**。代码看起来没问题，但运行时行为已改变。如果 Agent 直接开始实现新功能，可能会在已损坏的基础上继续构建，导致问题扩大化。

Baseline 测试的作用是将「沉默的损坏」显式化为可见的失败，让 Agent 能立即修复，而非带着隐患前进。

---

## 6. 测试工具的关键作用：Puppeteer MCP 与视觉盲区

Anthropic 发现 Claude 在测试场景中的核心能力瓶颈不是「是否执行测试」，而是**能否识别端到端的实际功能是否正常**。

在没有明确引导的情况下，Claude 会：
- 执行单元测试或 curl 命令
- 但无法判断功能是否在真实用户场景下正常工作

明确要求使用浏览器自动化工具（Puppeteer MCP）后，Claude 能够：
- 识别渲染问题（如 CSS 加载失败）
- 发现 API 响应正常但 UI 未更新的问题
- 捕获截图作为调试证据

**已知的视觉盲区**：Claude 无法看到浏览器原生的 alert modal（`window.alert()` 弹窗），因此依赖这些 modal 的功能在测试中更容易出现漏测。这是浏览器自动化工具在当前阶段的固有局限。

---

## 7. 常见失效模式与解决方案总结

| 失效模式 | 根因 | 解决方案 |
|----------|------|----------|
| Agent 试图单次完成整个项目 | 缺少任务分解机制 | Initializer 生成 Feature List；Coding Agent 每次只做一个功能 |
| Agent 过早宣告完成 | 缺少明确的进度边界 | Feature List 中每项必须通过测试才标记 passes:true |
| 新会话 Agent 需要「猜」进度 | 缺少状态继承机制 | claude-progress.txt + git log 提供双向恢复通道 |
| 会话间状态损坏未被发现 | 缺少基线验证 | 每次会话开始前运行端到端测试作为 baseline |
| Agent 花费大量时间理解如何运行应用 | 环境信息未结构化 | init.sh 提供一键启动脚本 |

---

## 8. 未来方向：单 Agent 还是多 Agent？

Anthropic 明确指出现有方案的开放问题：

> "It's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture."

潜在方向包括：
- **专用测试 Agent**：专门负责端到端验证，与负责实现的 Coding Agent 并行工作
- **QA Agent**：检查 Feature List 中各项的测试覆盖度
- **代码清理 Agent**：在会话间隙执行清理工作，保证代码库始终处于可合并状态

此外，当前的方案针对全栈 Web 开发优化，如何泛化到科研、金融建模等场景仍是开放问题。核心原则（任务分解、清洁状态、增量验证）应可迁移，但具体工具链需要针对领域调整。

---

## 9. 与其他长时运行方案的架构对照

| 方案 | 状态管理 | 任务分配 | 会话恢复 |
|------|----------|----------|----------|
| **Anthropic 双组件** | Feature List JSON + Progress 文件 | 增量 feature-by-feature | git log + progress 文件 |
| **DeepSeek-TUI** | 侧 git 快照（turn-based） | Plan/Agent/YOLO 三模式 | `/restore` + `revert_turn` |
| **GenericAgent（约 3K 行）** | 技能从任务中结晶 | 无预定义角色，按需生成 | 无持久化（依赖 LLM 上下文） |

Anthropic 的方案强调**结构化的任务边界与验证协议**，DeepSeek-TUI 则通过 turn-based 快照提供更细粒度的回退能力。两者分别适用于「需要精确进度追踪的项目级任务」和「需要频繁上下文回退的探索式任务」。

---

## 结语：Harness 作为会话间的工程契约

本文的核心结论不是「双组件架构是最好的方案」，而是：**长时运行 Agent 的核心工程问题是如何在会话之间建立可靠的工程契约**。

Anthropic 通过三个设计回答了这个问题：
1. **任务边界协议**：Feature List 强制每项工作有明确边界和验证标准
2. **状态继承协议**：Progress 文件 + git log 让下一会话能准确恢复
3. **清洁状态协议**：每次会话必须留下可合并到主分支的代码

这三个协议将「依赖模型自发行为」转变为「依赖结构化工程约束」，这正是 Harness 区别于裸模型调用的本质。

---

**引用来源**

> "We developed a two-fold solution to enable the Claude Agent SDK to work effectively across many context windows: an initializer agent that sets up the environment on the first run, and a coding agent that is tasked with making incremental progress in every session."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

> "By 'clean state' we mean the kind of code that would be appropriate for merging to a main branch: there are no major bugs, the code is orderly and well-documented."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)