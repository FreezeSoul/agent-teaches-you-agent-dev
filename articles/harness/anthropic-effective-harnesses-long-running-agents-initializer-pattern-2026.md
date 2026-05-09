# Anthropic 工程笔记：长程 Agent 的有效 Harness 设计

**核心论点**：长程 Agent 的核心挑战不是模型能力不足，而是**跨会话状态持久化**与**增量推进机制**的缺失。Anthropic 通过 Initializer Agent + Coding Agent 的双组件架构，结合 Feature List JSON + Progress File + Git 原子提交，构建了一套可让 Agent 在多会话环境下自主推进的 harness 框架。

**一手来源**：[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（Published Nov 26, 2025）

---

## 一、长程 Agent 的根本性挑战

Anthropic 在 Claude Agent SDK 实践中最核心的发现是：**compaction（上下文压缩）本身并不足以支撑真正的长程任务**。

即使模型具备 200K context window，单个任务无法在单一 context 内完成时，Agent 在跨 session 继续工作时面临两个主要失败模式：

### 1. One-Shot 失败（做太多）

> "The agent tended to try to do too much at once—essentially to attempt to one-shot the app. Often, this led to the model running out of context in the middle of its implementation, leaving the next session to start with a feature half-implemented and undocumented."

当 session 耗尽 context 时，下一个 Agent 进入的是一个**中间状态废墟**——功能半完成，文档缺失，下一个 Agent 只能靠猜测还原上下文，浪费大量时间"重新启动"。

### 2. 过早声明完成

> "After some features had already been built, a later agent instance would look around, see that progress had been made, and declare the job done."

当新 session 的 Agent 发现已有代码时，它会错误地评估"足够好了"，跳过未完成的功能。

> 笔者认为：这个失败模式揭示了一个深层问题——**Agent 缺乏对"完整功能"的外部定义**，只能依赖内部隐式的"看起来差不多了" heuristics。

---

## 二、双组件 Harness 架构

Anthropic 的解决方案是两阶段的**职责解耦**：

### Initializer Agent（初始化阶段）

第一个 session 执行专门的初始化 prompt，要求模型搭建：

```json
{
  "init.sh": "环境安装脚本",
  "claude-progress.txt": "进度日志",
  "git initial commit": "初始文件结构快照"
}
```

Initializer 的核心任务是编写一份**结构化的 Feature List**（JSON 格式），将用户的高层需求展开为数百个可测试的功能条目：

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

选择 JSON 而非 Markdown 是经过实验验证的决策——**模型对 JSON 的修改更克制，不容易出现过度重写**。

### Coding Agent（增量推进阶段）

每个后续 session 的 Coding Agent 被要求：

1. **一次只做一个 Feature**：从 Feature List 中取一个 `passes: false` 的条目
2. **实现后更新 passes 字段**：仅将 `passes` 从 `false` 改为 `true`，不做其他改动
3. **留下清洁状态**：每次 commit 必须满足"可直接合并到 main 分支"的质量标准

> "The best way to elicit this behavior was to ask the model to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file."

Git commit history + claude-progress.txt 共同构成了**跨 session 的状态同步协议**——下一个 Agent 通过 git diff 和 progress log 还原完整的工作上下文，而非依赖 potentially corrupted 的 memory。

---

## 三、Feature List 的双重价值

### 作为任务清单（解决"做什么"的问题）

Feature List 将"构建 claude.ai 克隆"这类模糊需求展开为 200+ 可测试项，为每个 Coding Agent 提供了**明确的行动边界**——不再需要"猜测还缺什么"，只需要按顺序遍历 `passes: false` 的条目。

### 作为完成度度量（解决"做到哪"的问题）

> "We use strongly-worded instructions like 'It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality.'"

这个约束保证了 Feature List 的**不可逆跟踪性**——每完成一个功能，就在 JSON 中留下一个 `passes: true` 的痕迹。这个记录本身成为了项目的结构化路线图。

---

## 四、测试闭环：Browser Automation Tools

Anthropic 发现 Claude 在端到端测试上存在显著弱点：

> "Absent explicit prompting, Claude tended to make code changes, and even do testing with unit tests or curl commands against a development server, but would fail recognize that the feature didn't work end-to-end."

解决方案是显式地为 Agent 提供**浏览器自动化工具**（Puppeteer MCP server），让 Agent 以真实用户视角截图验证功能：

> "Providing Claude with these kinds of testing tools dramatically improved performance, as the agent was able to identify and fix bugs that weren't obvious from the code alone."

这揭示了一个关键工程实践：**Agent 的自我验证必须使用与人类等价的测试工具，而非通过代码层面的 unit test 替代端到端验证**。

---

## 五、与 Planner/Worker 架构的系统性对比

Anthropic 的双组件架构（Initializer + Coding）与 Planner/Worker 模式有根本性差异：

| 维度 | Anthropic 双组件 | Planner/Worker |
|------|-----------------|----------------|
| **协调机制** | 无中心协调，Agent 通过 Feature List 自主发现任务 | 有中心 Planner 分配任务 |
| **任务发现** | Feature List 作为外部任务队列 | Planner 动态生成子任务 |
| **状态同步** | Git commit + progress file | 共享 memory/context |
| **失败恢复** | Git revert + 读取 progress log | 重新规划或重启 |
| **适用场景** | 任务边界明确（功能清单已知） | 任务边界模糊（需要动态分解） |

> 笔者认为：Anthropic 的方案在**任务清单可预先定义**的场景下更可靠（确定性高），而 Planner/Worker 在**探索性任务**下更灵活。两者并非替代关系，而是适用于不同任务形态的选择。

---

## 六、已知局限

Anthropic 坦承了当前方案的一些未解决问题：

1. **测试验证的局限性**：Claude 的测试能力仍有边界，某些边缘情况无法被自动发现
2. **Feature List 的维护成本**：Initializer 产出的 Feature List 质量依赖于模型对需求的理解深度
3. **增量粒度控制**：一次一个 feature 的模式在简单任务上可能过于低速

---

## 七、工程验收检查清单

当你要为一个长程 Agent 项目设计 harness 时，可用以下检查项：

- [ ] 是否为第一个 session 配置了专门的初始化 prompt？
- [ ] 是否有结构化的 Feature List（JSON）记录所有待完成功能？
- [ ] 每个 Coding Agent 是否被限制为一次只推进一个功能？
- [ ] Agent 是否通过 git commit + progress log 留下可审计的状态？
- [ ] 是否为 Agent 提供了端到端的浏览器自动化测试工具？
- [ ] 是否明确禁止 Agent 修改或删除 feature 条目？

---

**引用来源**：

> "We developed a two-fold solution to enable the Claude Agent SDK to work effectively across many context windows: an initializer agent that sets up the environment on the first run, and a coding agent that is tasked with making incremental progress in every session, while leaving clear artifacts for the next session."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

> "The best way to elicit this behavior was to ask the model to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)