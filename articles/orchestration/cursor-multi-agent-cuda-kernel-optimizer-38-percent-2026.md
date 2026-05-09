# Cursor 多智能体系统 38% 加速：CUDA Kernel 优化的工程方法论解析

> 本文深度解析 Cursor 与 NVIDIA 合作的多智能体系统如何在 3 周内完成 235 个 CUDA Kernel 优化，实现 38% Geomean Speedup 的工程方法论。重点不在于「达到什么结果」，而在于「如何做到」—— 从 Planner/Worker 架构到 Self-Benchmarking 闭环的系统性设计。

---

## 核心主张

多智能体系统在开放式优化问题上能超越单 Agent，因为其核心能力是**探索训练数据分布之外的解空间**。Cursor 的实验验证了一个关键结论：在最具挑战性的 Kernel 优化问题上，多智能体系统的 solution 比肩甚至超越领域专家，证明多智能体架构将成为软件构建的默认范式。

---

## 问题背景：为什么 Kernel 优化是 Agent 能力的试金石

评估长时运行的多智能体系统，有一个最佳方式：**给出开放式的优化问题，且问题的正确答案连工程师自己都不知道**。

Kernel 优化问题恰好满足这个条件：

1. **可测量的目标**：性能指标明确，迭代有方向
2. **超越简单 diff**：不是修复已知的 bug，而是寻找未知更好的解
3. **硬件相关**：需要理解 GPU 架构、内存层次、指令调度——这是连 AI 模型都缺乏训练数据的问题

> "Today, engineers optimize kernels by breaking models into individual math operations and tuning each one separately. This makes the problem manageable but leaves performance on the table because piecemeal optimization misses potential gains from optimizing across the entire system simultaneously."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

现有 GPU 性能被「手工简化」所限制，工程师无法探索完整解空间。

---

## 实验设置：235 个真实问题 + 27 块 Blackwell B200

NVIDIA 提供了 SOL-ExecBench 基准测试框架：

- **问题来源**：从 124 个生产开源模型（DeepSeek、Qwen、Gemma、Kimi、Stable Diffusion 等）提取 235 个优化问题
- **硬件**：27 块 NVIDIA Blackwell B200 GPU
- **问题类型**：
  - L1：94 个单算子 Kernel（Attention、RoPE、RMSNorm 等）
  - L2：82 个多算子融合 Kernel（完整 Decoder Layer、MoE Routing 等）
  - Quant：33 个量化 Kernel（FP8、NVFP4）
  - FlashInfer-Bench：26 个与 FlashInfer 基准对比的问题

> "SOL-ExecBench is an effective evaluator that compares kernel performance against existing software baselines and theoretical hardware performance limits. If agents use cheating tactics like caching and deliver performance beyond what a B200 can support, the pipeline invalidates the result."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

SOL（Speed-of-Light）分数是关键指标：0.5 = 优化的 PyTorch Baseline，1.0 = 硬件极限。**防作弊设计确保了结果的可信度**。

---

## 系统架构：Planner + Worker + Self-Benchmarking 闭环

整个协调协议存活在一个 Markdown 文件中（不是代码），这本身就值得关注：

```
┌─────────────────────────────────────────────────────────────┐
│                    Single Markdown File                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Output     │  │ Rules       │  │ Tests               │  │
│  │ Format     │  │ Constraints │  │ Validation         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Planner Agent                            │
│  职责：分布任务 + 动态重平衡 Worker 的工作负载                 │
│  依据：性能指标                                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                 Autonomous Worker Agents                    │
│  数量：多个并行 Worker                                       │
│  能力：独立编写 Kernel → 调用 Benchmark → 获取分数            │
│  特征：无需人工干预，持续 测试→调试→优化 循环                  │
└─────────────────────────────────────────────────────────────┘
```

**Self-Benchmarking 闭环**是系统最关键的设计：Agent 在运行过程中自行学习调用基准测试管道，系统持续测试、调试、优化 Kernel——全程无开发者介入。

---

## 两种语言的端到端测试

为了验证系统的通用性，Cursor 要求系统用两种语言各跑一遍，且处于 GPU 抽象层次的两端：

| 语言 | 抽象层次 | 测试目标 |
|------|---------|---------|
| **CUDA C + Inline PTX** | 最低层（接近 ISA） | 系统能否在硬件层面推理？直接操作寄存器和指令 |
| **CuTe DSL** | 最高层（抽象库） | 系统能否仅通过文档学习全新的 API？验证从零泛化能力 |

> "CuTe DSL, which provides high-level composable abstractions with minimal presence in public training data, testing whether the system can learn novel APIs purely from provided documentation."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

CuTe DSL 在公开训练数据中几乎不存在，这意味着模型必须**仅靠提供的文档**学习新 API——这是对 Agent 泛化能力的硬核测试。

---

## 核心结果：38% 加速，19% 超过 2 倍提升

| 指标 | 结果 |
|------|------|
| **Geomean Speedup** | 1.38x（38%）vs PyTorch Baseline |
| **问题通过率** | 149/235（63%）优于 Baseline |
| **2x+ 提升占比** | 45/235（19%）|
| **SOL 中位数** | 0.56（硬件极限 = 1.0）|
| **公开结果仓库** | [anysphere/kernel-optimization-results](https://github.com/anysphere/kernel-optimization-results)（L1/L2/Quant/FlashInfer 分层结构）|

> "We report performance of the multi-agent system in two ways: Geomean speedup vs. PyTorch code that was optimized by a single agent as a baseline. Speed-of-Light (SOL) scores that represent how good a solution is compared to theoretical hardware limits on a logarithmic curve."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

Geomean 掩盖了分布的厚重尾部——19% 超过 2x，但中位数 SOL 仅 0.56，说明仍有巨大优化空间。

---

## 三个典型案例：系统如何「有机地」找到不同策略

Cursor 特别挑选了三个问题，展示系统如何自主生成不同的优化策略。

### 案例一：BF16 Grouped Query Attention with Paged Prefill

**场景**：LLM Inference 常见的 Prompt Stage 操作，优化后支持更长上下文、更高并发。

**Agent 策略**：
1. 使用 CUDA C++ 优化，迭代 Kernel 时成功应用了特定硬件指令（内存加载 + 数学指令）
2. 添加了 Persistent Kernels 调度优化
3. 针对输入尺寸进行了超优化

**结果**：SOL Score 0.9722（接近硬件极限），Geomean Speedup 84% vs Baseline。集成到 SGLang 后，LLaMA 3.1 8B 的 TTFT 提升 3%。

**关键洞察**：Attention 问题在 Prefill 过程中占 2-5%（取决于 serving 配置），3% 的 TTFT 提升在端到端场景中并非微不足道。

### 案例二：NVFP4 MoE Linear with Gating

**场景**：Qwen3 等 MoE 模型中常见的两 Kernel 模式，但输入/中间结果被量化为 4-bit floating point（NVFP4）。

**Agent 策略**：
1. 正确识别量化区域是主要瓶颈
2. 将缩放计算和取整融合（而非先缩放再取整）
3. **关键创新**：用预计算的 threshold buckets 直接将 FP32 映射到 FP4 codes——因为 NVFP4 只有 16 个可能的值，这是可行的

**结果**：39% Geomean Speedup，SOL Score 0.58。

### 案例三：BF16 Matrix Multiplication（GEMM）

**场景**：矩阵乘法是公认最难的优化问题之一，需要深度理解各种硬件单元和调度。

> "Fully performant matrix multiplication kernels (GEMMs) require inline PTX (akin to assembly language), pipelining, and staging within a kernel. As a result, writing fast GEMMs has been historically siloed to highly experienced kernel experts."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

**Agent 策略**：
1. 从零生成专用 CUDA C++ GEMM Kernel
2. 独立学习使用 Blackwell 特定指令
3. 优化内存读写以适配硬件
4. 针对精确 shape 进行超优化

**结果**：达到 NVIDIA cuBLAS 精心优化基准的 86%。**在小 shape 测试用例上（对 LLM Inference Decode 尤为重要），系统生成的 Kernel 反而比 cuBLAS 快 9%**。

> "This result points to multi-agent systems soon outperforming domain experts even on the hardest kernel problems."

---

## 工程意义：多智能体为何优于单智能体

### 传统单 Agent 的局限

单 Agent 系统在开放式问题上的根本缺陷：**模型擅长的是训练数据中已见过的狭窄任务**。

Kernel 优化问题需要的能力（硬件架构理解、指令级优化、跨组件联合调优）恰恰是训练数据稀缺的。

### 多智能体的优势

| 维度 | 单 Agent | 多智能体 |
|------|---------|---------|
| **解空间探索** | 受限于训练数据分布 | 可以探索训练之外的区域 |
| **计算资源扩展** | 受限于单一上下文窗口 | 横向扩展 Worker 数量 |
| **Specialization** | 一个 Agent 做所有事 | Planner 协调 + Worker 并行专项 |
| **迭代速度** | 串行优化 | 并行试错 + 动态重平衡 |

Cursor 在 27 块 GPU 上运行了「数百个问题 + Agent」，这个规模限制了充分发挥多智能体系统的潜力。**更多 GPU = 更深更 novel 的解决方案**。

> "The most ambitious tasks in software are open-ended, without a clear solution. Single agent systems struggle here because models are best at narrowly scoped tasks they have already seen during training."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

---

## 对 Agent 工程实践的启示

### 1. Planner/Worker 架构是复杂任务分解的标准范式

Cursor 的 Planner 根据性能指标动态分布和重平衡工作负载——这不是静态的任务分配，而是**在线优化**。这种模式已在多个场景验证（Anthropic C Compiler、Cursor Scaling Agents）。

### 2. Self-Benchmarking 闭环是自动化优化的基础设施

当系统能自主调用基准测试并根据分数迭代时，human-in-the-loop 就变成了**gate keeper** 而非**每步介入者**。这对vernight 自动化（overnight experimentation）尤其关键。

### 3. 测量驱动改进是工程可行的前提

SOL-ExecBench 提供了可信赖的评估标准（防作弊 + 硬件极限对比）。没有可信赖的测量，Agent 无法知道自己是否在进步。

> "One of the best ways to evaluate long-running, multi-agent systems is to give them open-ended optimization problems where even we don't know the right answer."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

---

## 结论与启示

Cursor 的实验证明了两件事：

1. **多智能体架构能解决训练数据分布之外的开放问题**：在 Kernel 这个硬核工程领域，系统达到了领域专家的 86-109%（小 shape case 超越 cuBLAS）
2. **自动化 benchmark + 迭代闭环是下一代 Agent 基础设施**：Self-Benchmarking 让 Agent 在无人值守的情况下持续改进

对于 Agent 工程师而言，这个案例最重要的启发不是「多智能体有多强」，而是**「多智能体 + 可信赖的测量 + 自动化迭代」等于什么**：等于一个可以在开放问题上持续探索未知解空间的系统。

> "The techniques we're researching here will soon inform Cursor's core product."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

这不仅是 Cursor 的研究方向——它指向的是软件构建的第三时代（the third era of software development），其中 Fleet of Agents 将自主交付改进。

---

## 关联项目

- [AutoAgent — 像 Autoresearch 但面向 Agent 工程](./autonoe-elct9620-long-running-agent-orchestrator-2026.md)：kevinrgu/autoagent，自动化迭代 Agent Harness 配置的元 Agent 框架
- [Anysphere Kernel Optimization Results](https://github.com/anysphere/kernel-optimization-results)：235 个 Kernel 的解决方案和指标，公开可复现

---

*本文核心内容基于 [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)，由 Cursor AI 与 NVIDIA 合作完成。*
