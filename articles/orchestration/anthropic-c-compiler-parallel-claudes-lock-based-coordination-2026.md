# 并行自治 Agent 的协调之道：Anthropic C 编译器 2000 Session 复盘

**发布于**：2026-05-09 | **演进阶段**：Stage 7 · Orchestration | **分类**：orchestration/

## 开篇

> **核心问题**：当 16 个 Agent 在没有中心协调者的情况下并行工作，它们如何知道该做什么、如何避免重复劳动、以及如何确保整体质量？
>
> **核心结论**：Anthropic 的 C 编译器实验证明了**无中心协调的并行自治 Agent**在工程上是可行的。关键不在于 Agent 有多智能，而在于**测试框架足够精确**——当测试是完美的，Agent 自主推进就是安全的。这与 Cursor 的 Planner/Worker 层级架构代表了两种截然不同的多 Agent 协作范式。

---

## 1. 为什么需要并行 Agent

Nicholas Carlini 在 Anthropic Safeguards 团队的实验动机很直接：**测试 LLM Agent 的能力边界**。

他选择了一个极具挑战性的任务：从零构建一个能编译 Linux 内核的 C 编译器。之所以选择编译器，是因为编译器是一个需要精确正确性的系统——任何小的语义错误都会导致生成的程序行为异常。这是一个完美的能力边界测试场景。

> "I’ve been using the C Compiler project as a benchmark across the entire Claude 4 model series. As I did with prior projects, I started by drafting what I wanted: a from-scratch optimizing compiler with no dependencies, GCC-compatible, able to compile the Linux kernel, and designed to support multiple backends."
> — [Anthropic Engineering: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)

最终，16 个 Agent 并行工作近 2000 个 Claude Code Session，消耗 20 万美元 API 成本，产出了一个 10 万行的 Rust 编译器，能在 x86、ARM 和 RISC-V 上编译 Linux 6.9。

---

## 2. 无中心协调的架构设计

### 2.1 Ralph Loop：自主推进的基础

Carlini 设计的 harness 核心是一个简单的无限循环：

```bash
#!/bin/bash
while true; do
  COMMIT=$(git rev-parse --short=6 HEAD)
  LOGFILE="agent_logs/agent_${COMMIT}.log"
  
  claude --dangerously-skip-permissions \
    -p "$(cat AGENT_PROMPT.md)" \
    --model claude-opus-X-Y &> "$LOGFILE"
done
```

这个 loop 的本质是：**每次 Session 结束后立即启动新的 Session，不等待人类干预**。每个 Agent 被丢进一个全新的 Docker 容器，里面只有一个 Git 仓库的副本和一份 AGENT_PROMPT.md。

> "When it finishes one task, it immediately picks up the next. The loop runs forever."

这与传统的 Human-in-the-loop 模式截然不同。传统模式认为 Agent 需要人类在每个关键节点做决策；而 Ralph Loop 的前提是：**如果测试足够好，Agent 可以自主判断什么时候算"完成"**。

### 2.2 Git 文件锁：分布式任务分配

16 个 Agent 如何分配任务而不冲突？Carlini 使用了一个精巧的机制：**Git 文件锁**。

每个 Agent 在开始一个任务前，先在 `current_tasks/` 目录下创建一个锁文件：

```bash
# Agent A 声明要做的任务
echo "Agent A is working on: parse_if_statement" > current_tasks/parse_if_statement.txt
git add current_tasks/parse_if_statement.txt
git commit -m "Lock: parse_if_statement"
git push
```

如果两个 Agent 同时尝试声明同一个任务，Git 的原子性保证只有一个会成功。失败的 Agent 会看到自己的 push 被拒绝，然后重新选择其他任务。

> "If two agents try to claim the same task, git's synchronization forces the second agent to pick a different one."

这个机制的优雅之处在于：**它把冲突检测的任务外包给了 Git**。不需要中心化的任务队列，不需要复杂的分布式锁协议，只需要一个共享的 Git 仓库。

### 2.3 自主合并：冲突处理的边界

当 Agent 完成一个任务后，它会：
1. 从 upstream 拉取其他 Agent 的变更
2. 自动解决合并冲突（"Claude is smart enough to figure that out"）
3. 推送自己的变更
4. 删除自己的锁文件

这里的"自动合并"是真正考验 Agent 能力的环节。当两个 Agent 修改了同一个文件的相邻部分时，Git 的三向合并可以自动完成。但当修改重叠时，Carlini 观察到 Claude 能够理解冲突并做出合理的取舍。

---

## 3. 测试框架：质量保障的核心

### 3.1 测试必须是近乎完美的

Carlini 在复盘中反复强调一个观点：**Agent 会自主解决任何你给它定义的问题，但如果你的测试是错的，Agent 会精确地解决错误的问题**。

> "Claude will work autonomously to solve whatever problem I gave it. So it's important that the task verifier is nearly perfect."

这个洞察直指 Agent 系统的核心矛盾：**自主性意味着 Agent 会寻找任何到达目标的可能路径，但如果目标定义（测试）有漏洞，Agent 会走捷径**。

### 3.2 时间盲点：Agent 不知道什么时候该停下

LLM 的一个内在限制是**无法感知时间**。Carlini 观察到，如果不给定明确的边界，Agent 会花几个小时跑测试而不去做实际的代码改进。

他的解决方案是**随机采样**：

```bash
# 默认运行 1% 或 10% 的随机采样
# 采样是确定性的（每个 Agent 的采样固定），但跨 Agent 随机
./run_tests.sh --fast  # 运行 10% 采样
```

这样 Agent 可以在几秒内得到一个测试结果的近似，然后在完整测试集上验证最终方案。

### 3.3 上下文污染：日志必须结构化

每次 Session 开始时，Agent 被丢进一个全新的容器。这意味着它需要重新理解项目的当前状态。Carlini 发现 Agent 会花大量时间"定向"——理解代码库的结构、当前进度、待解决的问题。

为了减少上下文污染，Carlini 做了两件事：
1. **日志必须结构化**：错误信息要用 `ERROR: <reason>` 格式，这样 `grep` 可以快速定位
2. **预计算汇总统计**：不要让 Agent 自己去数有多少测试失败，而是直接告诉它 "42 failed, 158 passed"

> "If there are errors, Claude should write ERROR and put the reason on the same line so grep will find it."

---

## 4. 并行化的三个阶段

### 4.1 阶段一：测试套件阶段（并行 trivial）

当有很多独立的 failing test 时，并行化是 trivial 的——每个 Agent 选一个不同的测试去修复。

编译器项目从零开始时，测试套件有数百个独立测试，每个 Agent 可以独立选一个修复。这个阶段几乎没有协调开销。

### 4.2 阶段二：真实项目阶段（并行开始出现瓶颈）

当测试通过率达到 99%，项目转向编译真实开源软件（SQLite、Redis、libjpeg、QEMU 等）。这时并行化的收益开始下降——因为大多数测试已经通过，剩下的都是很难的边界情况。

### 4.3 阶段三：Linux 内核阶段（并行完全失效）

编译 Linux 内核是一个巨大的单任务，而不是一堆独立测试。每个 Agent 都会遇到同一个 bug，然后各自修复，结果互相覆盖。16 个 Agent 的并行度退化为 1。

> "Having 16 agents running didn't help because each was stuck solving the same task."

Carlini 的解决方案是引入 **GCC 作为 Oracle**：

```bash
# 随机选择 90% 的内核文件用 GCC 编译
# 只用 Claude 编译器编译剩余 10%
# 如果内核工作正常，问题不在 Claude 编译器负责的文件
# 如果失败，进一步缩小范围
```

这是一个经典的**差分测试**方法。它的本质是**将单任务分解为可并行的子任务**——不是"编译整个内核"，而是"分别编译这 N 个文件，看看哪些有问题"。

---

## 5. 角色分工：专业化的价值

### 5.1 为什么需要专门角色

LLM 生成的代码有一个普遍问题：**重复实现已有的功能**。Carlini 观察到，16 个 Agent 并行工作时，它们会各自实现同一个工具函数或数据结构。

解决方案是引入**专门角色**：

| 角色 | 职责 |
|------|------|
| Coalescer Agent | 合并重复代码 |
| Performance Agent | 优化编译器本身的性能 |
| Code Generator Agent | 专注生成高效的目标代码 |
| Critic Agent | 从 Rust 开发者的角度审视设计，做结构性改进 |
| Documentation Agent | 维护文档和进度文件 |

> "LLM-written code frequently re-implements existing functionality, so I tasked one agent with coalescing any duplicate code it found."

这个设计的洞察是：**专门化让 Agent 可以积累上下文**。通用 Agent 每轮都要重新理解所有上下文，而专门 Agent 可以在自己的领域内持续深入。

### 5.2 角色 vs 通用：能力边界

Carlini 的实验也揭示了角色专门化的能力边界：

- **专门化有效**：当任务有清晰边界时，专门 Agent 可以显著提高效率
- **专门化有限制**：当任务边界模糊时，专门 Agent 会过度优化自己的局部目标

比如 Critic Agent 可能会持续改进代码质量，而忽略了原本的编译器功能目标。

---

## 6. 与 Planner/Worker 架构的本质对比

| 维度 | Anthropic 并行自治 | Cursor Planner/Worker |
|------|-------------------|---------------------|
| **协调方式** | 无中心协调，Git 文件锁分布式分配 | Planner 中心化分配任务 |
| **任务来源** | Agent 自主选择"下一个最明显的任务" | Planner 根据全局视图分配 |
| **冲突处理** | Git 原子性保证 + Agent 自主合并 | Planner 动态重平衡 |
| **质量保障** | 测试框架驱动（外部验证） | Planner 监控 + 人工验收 |
| **适用场景** | 大量独立任务，边界清晰 | 任务有依赖关系，需要全局协调 |
| **失败模式** | 重复劳动（多 Agent 做同一任务） | 单点瓶颈（Planner 成为瓶颈） |
| **扩展性** | 线性扩展（任务足够多时） | 受 Planner 能力上限限制 |

> 笔者认为，这两种架构代表了**去中心化 vs 中心化**的经典权衡。Anthropic 的方案更优雅（不需要复杂的协调协议），但依赖高质量的测试框架。Cursor 的方案更可控（Planner 可以做全局优化），但引入了单点风险。

### 什么时候选哪种架构？

**选择并行自治**：
- 任务可以被分解为大量独立子任务
- 有高质量的自动化测试可以验证正确性
- 目标函数明确且可自动化评估

**选择 Planner/Worker**：
- 任务之间有复杂的依赖关系
- 需要全局视野来做优化决策
- 需要人来监督关键路径

---

## 7. 局限性与开放问题

### 7.1 已验证的局限性

实验揭示了 Opus 4.6 的几个能力边界：

1. **生成的代码效率低**：即使开启所有优化，输出代码的效率仍低于 GCC -O0
2. **16 位 x86 支持不完整**：无法生成 32k 以下的空间限制，需要调用 GCC
3. **Assembler 和 Linker 未完成**：Claude 开始自动化这部分，但仍有 bug
4. **新功能经常破坏已有功能**：99% 通过率之后，每加一个新功能都可能引入回归

> "New features and bugfixes frequently broke existing functionality."

### 7.2 为什么自动化完整编译器这么难？

Carlini 的分析指向一个核心问题：**长程一致性**。当代码库规模超过一定阈值，Agent 无法在有限的上下文窗口内保持对全局状态的准确理解。

这与当前 LLM 的上下文窗口大小直接相关。如果上下文窗口是 200k tokens，Agent 可以理解约 10 万行代码。但如果代码库增长到 50 万行，Agent 只能在"片段"级别工作，缺乏对全局的感知。

---

## 8. 对 Harness 工程的启示

### 8.1 测试即契约

Anthropic 的实验最重要的启示是：**在 Agent 系统中，测试不是质量保障手段，测试是 Agent 行为的定义**。

当测试是完美的，Agent 可以在没有监督的情况下自主工作。这意味着：
- 投资在测试框架上的时间，会成倍地回报在 Agent 效率上
- 测试的漏洞会精确地成为 Agent 的漏洞

### 8.2 协调协议的极简主义

Git 文件锁的实现启示我们：**好的协调协议应该是"足够好"而不是"完美"**。

Git 的冲突检测不是完美的，但它足够简单、足够可靠、足够可扩展。引入更复杂的分布式锁协议（比如 Raft 或 Paxos）可能会解决更多的冲突，但增加的系统复杂度可能抵消收益。

### 8.3 自主性的前提是环境无毒性

每个 Session 都在一个全新的 Docker 容器中启动，Agent 无法保留任何"状态"。这要求：
- 所有重要信息必须写入代码库（README、进度文件、决策日志）
- 环境的初始化必须是幂等的
- Agent 的每次启动都应该是"公平"的，不依赖任何历史遗留状态

---

## 结语

> "I expect the positive applications to outweigh the negative, but we're entering a new world which will require new strategies to navigate safely."
> — Nicholas Carlini

Anthropic 的 C 编译器实验证明了 **LLM Agent 在足够好的测试框架支撑下，可以完成真正复杂的工程任务**。但它也揭示了当前能力的关键瓶颈：**长程一致性和代码效率**。

这两种架构（并行自治 vs 层级协调）不是非此即彼的选择。真实世界的系统可能会结合两者——用 Planner/Worker 做高层任务分解，用并行自治执行大量独立子任务。

**关键问题不是"Agent 能不能做到"，而是"我们如何设计环境和测试，让 Agent 做到我们真正想要它做到的事情"**。

---

## 附录：核心资源

- **Anthropic C 编译器仓库**：[github.com/anthropics/claudes-c-compiler](https://github.com/anthropics/claudes-c-compiler)
- **Ralph Loop 原始实现**：见 Anthropic Engineering 博客原文
- **GCC Torture Test Suite**：[gcc.gnu.org/onlinedocs/gccint/Torture-Tests.html](https://gcc.gnu.org/onlinedocs/gccint/Torture-Tests.html)
