# 多 Agent 架构系统性优势：开放性优化任务中的协作设计

## 核心问题

当 Agent 系统面对**没有确定答案、需要在巨大解空间中持续探索**的开放性优化任务时，单一 Agent 的局限性在哪里？多 Agent 协作架构如何系统性突破这一瓶颈？

2026 年初，Cursor 和 Anthropic 分别给出了答案：Cursor 的多 Agent 系统在 235 个 CUDA kernel 优化问题上取得 38% 的几何平均加速；Anthropic 的双组件架构使 Claude Agent SDK 能够在跨越数天的长时任务中持续推进。这两项工作从不同角度揭示了同一原理——**多 Agent 架构的优势不在于「多个 Agent 一起做同一件事」，而在于「不同 Agent 做不同的事、通过结构化协议协作」**。

---

## 单一 Agent 的两个典型失败模式

Anthropic 在实验中发现，即使使用前沿模型 Opus 4.5，单一 Agent 在长时任务中仍会表现出两种典型失败：

### 模式 1：过度承诺（One-shot 陷阱）

Agent 倾向于在单一会话中尝试实现过多功能，导致：
- 在实现中途耗尽上下文窗口，留下半成品
- 后续 Agent 从混乱状态启动，需要大量时间「恢复现场」

### 模式 2：过早终止

在部分功能已实现后，Agent 看到已有代码便误判「工作已完成」而停止。

> "Even with compaction, which doesn't always pass perfectly clear instructions to the next agent." 
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

Cursor 在 kernel 优化任务中观察到了类似的模式：单 Agent 在遇到复杂 kernel 时倾向于使用已知解法而非探索新路径。

---

## 从单 Agent 到多 Agent：两种协作范式

### 范式 1：Anthropic 的 Initializer + Coding 双组件

Anthropic 将 Agent 生命周期分为两个阶段，每个阶段使用不同角色的 Agent：

```
┌─────────────────────────────────────────────────────┐
│              Initializer Agent（首次会话）           │
│  ├─ 解析用户原始 Prompt                             │
│  ├─ 生成结构化 Feature List（JSON）                │
│  ├─ 创建 init.sh 启动脚本                          │
│  └─ 提交初始 git commit（留下完整的基线状态）       │
└─────────────────────────────────────────────────────┘
                         ↓（各自专注单一职责）
┌─────────────────────────────────────────────────────┐
│              Coding Agent（所有后续会话）             │
│  ├─ 从 Feature List 选择一个未完成的 Feature        │
│  ├─ 实现 + 端到端测试验证                          │
│  └─ 提交 git commit + 更新 progress.txt             │
└─────────────────────────────────────────────────────┘
```

关键设计：**两个 Agent 使用相同的工具集和 Harness，但初始 prompt 不同**。这使得专业化成为可能，而无需引入多 Agent 通信协议的复杂度。

### 范式 2：Cursor 的 Planner + Worker 架构

Cursor 在 kernel 优化任务中部署了更复杂的多 Agent 架构：

> "The multi-agent system solved all 235 GPU kernel optimization problems in a single run by deploying a planner agent that distributed and rebalanced work across autonomous workers based on performance metrics."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

整个协调协议存放在**一个 markdown 文件**中，指定了输出格式、规则和测试。Workers 独立调用 benchmark pipeline，创建「测试→调试→优化」的闭环。

两种范式的核心区别：

| 维度 | Anthropic 双组件 | Cursor Planner+Worker |
|------|-----------------|----------------------|
| Agent 角色 | 2 种（Initializer / Coding）| 2+ 种（Planner + N Workers）|
| 协调机制 | 结构化文件（feature_list.json）| 协调协议 markdown |
| 反馈闭环 | Puppeteer E2E 测试 | Benchmark pipeline |
| 任务类型 | 功能实现（可枚举）| 开放优化（不可枚举）|

---

## 开放性优化问题：多 Agent 的决定性优势

为什么 kernel 优化任务需要多 Agent？

**问题结构**：kernel 优化没有标准答案，需要在巨大的解空间中持续探索。单个模型擅长在训练数据分布内的狭窄任务，但面对需要 novel API 或硬件级推理的问题时表现不足。

> "Single agent systems struggle here because models are best at narrowly scoped tasks they have already seen during training. We see the kernel optimization experiment as further validation that multi-agent architectures will quickly become the default approach to building software because they can tackle novel problems that fall far outside training data distribution."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

Cursor 的实验中，Agent 需要同时处理：
- **CUDA C++ with inline PTX**：直接操作寄存器和 ISA 级别指令
- **CuTe DSL**：全新的高层可组合抽象，几乎没有公开训练数据

这要求 Agent 必须从文档中学习 novel API 并独立推理硬件特性——这是单一 Agent 难以完成的任务。

### 核心机制：协调协议即知识载体

Cursor 的协调协议存在一个 markdown 文件中，包含：
1. 输出格式规范
2. 测试规则
3. Benchmark 调用方式

Workers 通过读取协调协议理解任务边界，Planner 根据性能指标动态分发和重平衡工作。这种设计的优雅之处在于**协调协议本身成为了系统知识的形式化载体**——它不依赖任何 Agent 的内部状态，可以在任何新会话中被即时加载。

---

## 两种失败模式的系统性解决

| 失败模式 | Anthropic 解决方案 | Cursor 解决方案 |
|---------|-------------------|----------------|
| One-shot 陷阱 | Feature List 约束每次只做一个 Feature | Planner 动态分发任务，Worker 只做子任务 |
| 过早终止 | JSON 强制验收 + Puppeteer E2E 测试 | SOL-ExecBench 自动化验证，必须超过基线 |
| 环境不一致 | init.sh 自动重建 | 协调协议规范 benchmark 环境 |
| 解空间探索不足 | N/A（任务可枚举）| 多个 Worker 并行探索不同方向 |

---

## 工程落地检查清单

如果你正在构建需要处理开放性优化任务的 Agent 系统：

- [ ] **任务是否可枚举？** 是 → Anthropic 双组件足够；否 → 需要 Planner+Worker
- [ ] **是否有自动化验收标准？** 没有 → 多 Agent 架构收益降低
- [ ] **协调协议是否形式化？** 应存放在独立文件中，而非依赖 Agent 记忆
- [ ] **Feedback Loop 是否存在？** 持续测试→调试→优化闭环是关键
- [ ] **Worker 是否有边界约束？** 防止 Worker 尝试超越其职责范围的任务

---

## 原文引用

> "The key insight here was finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history. Inspiration for these practices came from knowing what effective software engineers do every day."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

> "The multi-agent system solved all 235 GPU kernel optimization problems in a single run by deploying a planner agent that distributed and rebalanced work across autonomous workers based on performance metrics."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

> "Single agent systems struggle here because models are best at narrowly scoped tasks they have already seen during training. We see the kernel optimization experiment as further validation that multi-agent architectures will quickly become the default approach to building software because they can tackle novel problems that fall far outside training data distribution."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

> "Even with compaction, which doesn't always pass perfectly clear instructions to the next agent."
> — [Anthropic Engineering: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)