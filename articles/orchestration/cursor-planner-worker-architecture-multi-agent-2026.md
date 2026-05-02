# Cursor Planner/Worker 架构：层级协调的 Multi-Agent 工程实践

## 核心问题

Cursor 在 2026 年 3 月发表的 [Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents) 揭示了一个关键工程结论：**Planner/Worker 分层架构**是解决 Multi-Agent 协调瓶颈的核心范式。这篇文章提供了 Anthropic C Compiler 并行实验以来最系统的 Multi-Agent 协调实证数据。

## Anthropic 的教训 vs Cursor 的演进

在 MetaMorph 分布式协调机制分析中，我们看到了 Anthropic 的实验性方案：多个 Agent 通过共享文件 + Git 文件锁进行分布式协调，优点是去中心化、无单点瓶颈，缺点是"风险规避"——没有层级结构的 Agent 会回避困难任务。

Cursor 的 Planner/Worker 架构给出了不同的答案：**引入层级结构，但让层级专注于不同职责**。

> "Our next approach was to separate roles. Instead of a flat structure where every agent does everything, we created a pipeline with distinct responsibilities. Planners continuously explore the codebase and create tasks. Workers pick up tasks and focus entirely on completing them."
> — [Cursor Engineering: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)

## 核心架构：三阶段循环

```
┌─────────────────────────────────────────────────────────────────┐
│                        PLANNER AGENT                            │
│  持续探索代码库，分解任务，生成 task queue                       │
│  可递归生成 sub-planner 实现并行规划                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Task Queue (共享状态)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       WORKER AGENTS (N个)                       │
│  并行消费 task queue，各自独立完成任务                           │
│  不协调、不通信、不关心全局视角                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        JUDGE AGENT                               │
│  评估本轮迭代是否达成目标，决定是否继续下一轮                    │
└─────────────────────────────────────────────────────────────────┘
```

### Planner 的职责

Planner 不执行，只规划：

- 持续探索代码库结构，理解模块边界
- 将大型任务分解为可并行的子任务
- 生成 task queue 并维护任务状态
- 可递归生成 sub-planner：针对特定领域（如网络层、UI层）创建专门的子规划器

> "Planners continuously explore the codebase and create tasks. They can spawn sub-planners for specific areas, making planning itself parallel and recursive."
> — Cursor Engineering Blog

### Worker 的职责

Worker 不规划，只执行：

- 从 task queue 消费任务
- 专注于单任务的端到端实现
- 不与其他 Worker 协调
- 完成后将结果 push 到共享分支

> "Workers pick up tasks and focus entirely on completing them. They don't coordinate with other workers or worry about the big picture."
> — Cursor Engineering Blog

### Judge 的职责

每个循环结束时，Judge Agent 判断是否继续：

- 评估当前迭代是否达成目标
- 决定是否需要下一轮迭代
- 防止无限循环

## 协调机制的演进：从失败中学习

Cursor 的博客揭示了 Planner/Worker 架构并非一蹴而就，而是经历了三次迭代：

### 第一次尝试：扁平结构 + 共享文件 + 锁

```
Agent A ──┐
Agent B ──┼──→ Shared File (协调状态) + File Lock
Agent C ──┘
```

**失败原因**：
- Agent 持有锁时间过长，或忘记释放
- 20 个 Agent 实际吞吐量降到 2-3 个的水平
- 单点锁成为瓶颈
- Agent 失败时锁无法释放，系统僵死

### 第二次尝试：乐观并发控制（无锁）

```
Agent A: read → 修改 → write（若状态未变则成功）
Agent B: read → 修改 → write（若状态已变则重试）
```

**失败原因**：
- 无层级结构导致 Agent 风险规避
- 无人对困难任务负责
- Agent 回避硬问题，只做小改动
- 团队长时间 churn 但无实质进展

### 第三次：Planner/Worker 分层 ✓

引入角色分离后，协调问题基本消失：

- Planner 承担协调压力
- Worker 只需埋头执行
- 不需要复杂的锁机制
- 可扩展到数百个并发 Worker

> "This solved most of our coordination problems and let us to scale to very large projects without any single agent getting tunnel vision."
> — Cursor Engineering Blog

## 关键工程数据

Cursor 提供了令人震惊的实证数据：

| 项目 | 数据 |
|------|------|
| 浏览器构建 | ~1 周，100 万行代码，1000 个文件 |
| Solid→React 迁移 | 3 周，+266K/-193K 行代码 |
| Rust 渲染优化 | 25x 加速，已合并上线 |
| Java LSP | 7.4K commits，550K LoC |
| Windows 7 模拟器 | 14.6K commits，1.2M LoC |
| Excel | 12K commits，1.6M LoC |
| 并发规模 | 数百个 Agent 同时运行于同一分支 |
| Token 消耗 | 数万亿 tokens，单一目标 |

## 模型选择的关键洞察

Cursor 发现了模型角色匹配的重要性：

> "We found that GPT-5.2 models are much better at extended autonomous work: following instructions, keeping focus, avoiding drift, and implementing things precisely and completely. Opus 4.5 tends to stop earlier and take shortcuts when convenient."

关键结论：

- **Planner 需要连续工作能力**：GPT-5.2 > Opus 4.5
- **同一模型不同角色表现不同**：GPT-5.2 作为 Planner 比 GPT-5.1-Codex 更好
- **按角色选模型**而非统一模型

> "We now use the model best suited for each role rather than one universal model."

## Cursor Agent Best Practices 的工程补充

同期的 [Best practices for coding with agents](https://cursor.com/blog/agent-best-practices) 提供了 Harness 工程的具体实践：

### Agent Harness 三组件

```
Harness = Instructions + Tools + Model
```

- **Instructions**：System prompt + rules
- **Tools**：File editing、codebase search、terminal execution
- **Model**：针对每个任务选择最优模型

> "Cursor's agent harness orchestrates these components for each model we support. We tune instructions and tools specifically for every frontier model."

### Rules vs Skills：静态上下文 vs 动态能力

Cursor 提出了 Rules 和 Skills 的区分：

**Rules**（`.cursor/rules/`）：始终加载的静态上下文

```markdown
# Commands
- `npm run build`: Build the project
- `npm run typecheck`: Run the typechecker

# Code style
- Use ES modules (import/export), not CommonJS

# Workflow
- Always typecheck after making changes
```

**Skills**（`.cursor/skills/`）：按需加载的动态能力

- Skill 是 SKILL.md 文件包
- 包含 custom commands、hooks、domain knowledge
- Agent 自行判断何时加载相关 Skill

> "Unlike Rules which are always included, Skills are loaded dynamically when the agent decides they're relevant."

### 扩展 Agent 的 Hook 机制

Cursor 提供了长时运行 Agent 的 Hook 系统：

```typescript
// .cursor/hooks/grind.ts
interface StopHookInput {
  conversation_id: string;
  status: "completed" | "aborted" | "error";
  loop_count: number;
}

if (input.status !== "completed" || input.loop_count >= MAX_ITERATIONS) {
  process.exit(0); // 停止循环
}

if (scratchpad.includes("DONE")) {
  process.exit(0);
} else {
  // 继续迭代
  console.log(JSON.stringify({
    followup_message: `[Iteration ${input.loop_count + 1}/${MAX_ITERATIONS}] Continue working.`
  }));
}
```

配合 `.cursor/hooks.json`：

```json
{
  "version": 1,
  "hooks": {
    "stop": [{ "command": "bun run .cursor/hooks/grind.ts" }]
  }
}
```

实现"运行直到测试通过"的自主迭代模式。

## 与 Anthropic MetaMorph 的架构对比

| 维度 | Cursor Planner/Worker | Anthropic MetaMorph |
|------|----------------------|---------------------|
| 协调模式 | 层级结构（中心规划） | 分布式（文件锁） |
| 层级数量 | Planner → Worker → Judge | 扁平（多个 Claude 等价） |
| 任务分配 | Planner 主动分配 | Worker 自选任务 |
| 冲突解决 | 通过层级规避 | 通过文件锁解决 |
| 瓶颈 | Planner 是潜在瓶颈 | 锁是潜在瓶颈 |
| 适用场景 | 大型项目、长周期任务 | 中型项目、快速并行 |

> 笔者认为：两者并非替代关系，而是适用于不同场景。Cursor 的层级结构适合"有一个明确目标但路径模糊"的大型项目；MetaMorph 的分布式锁适合"任务天然可分割且执行者能力均等"的场景。

## 工程启示录

### 做对了什么

1. **分离关注点**：Planner 和 Worker 的职责分离解决了协调问题
2. **Judge 防止无限循环**：引入评判机制让系统可以自主终止
3. **按角色选模型**：不是用一个最强模型，而是为每个角色选最适合的
4. **从失败中迭代**：三次尝试才找到正确架构

### 已知局限

> "Planners should wake up when their tasks complete to plan the next step. Agents occasionally run for far too long. We still need periodic fresh starts to combat drift and tunnel vision."

- Planner 无法主动唤醒，需等待固定周期
- Agent 有时会运行过长时间
- 需要周期性重启来对抗 drift 和 tunnel vision

### 核心结论

> "Can we scale autonomous coding by throwing more agents at a problem? The answer is more optimistic than we expected. Hundreds of agents can work together on a single codebase for weeks, making real progress on ambitious projects."

Multi-Agent 协调确实是难题，但层级结构提供了可行的解法。

---

**防重索引**：
- `articles/orchestration/planner-worker-multi-agent-autonomous-coding-architecture-2026.md`（已有）
- `articles/orchestration/metamorph-multi-agent-file-lock-parallel-2026.md`（已有）

**关联 Projects**：
- `articles/projects/awesome-cursor-skills-spencepauly-2026.md`（本轮新增，Skills 系统化工具库）

**来源**：
- [Cursor: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)
- [Cursor: Best practices for coding with agents](https://cursor.com/blog/agent-best-practices)
- [Cursor: Meet the new Cursor](https://cursor.com/blog/cursor-3)
- [Cursor: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)