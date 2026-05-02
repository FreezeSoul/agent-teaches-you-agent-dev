# Multi-Agent 开放域优化：CUDA Kernel 38% 加速的工程复盘

**发布于**：2026-05-02 | **演进阶段**：Stage 7 · Orchestration | **分类**：orchestration/

## 开篇

> **核心问题**：如何评估一个长时运行的 Multi-Agent 系统在**没有标准答案的开放域问题**上的真实能力？
>
> **核心结论**：Cursor 用 235 个 GPU Kernel 优化问题的实验给出了答案——Multi-Agent 架构不仅能解决开放域优化问题，而且在 19% 的问题上超过了人类领域专家。关键在于**可测量的目标函数、持续反馈的 Benchmark 循环、以及 Planner 的全局协调**。

---

## 1. 为什么 Kernel 优化是 Multi-Agent 的试金石

### 1.1 开放域问题的评估困境

评估长时运行的 Multi-Agent 系统，最大挑战是**我们不知道正确答案在哪里**。传统软件测试有明确的 diff 可以对比，但当任务目标是"让这段代码更快"，而不是"让这段代码符合某段参考答案"时，如何判断 Agent 的输出是否真的更好？

> "One of the best ways to evaluate long-running, multi-agent systems is to give them open-ended optimization problems where even we don't know the right answer. Kernel optimization problems meet this criteria: they provide measurable objectives that the system can iteratively optimize against, instead of targeting a simple known diff."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

Kernel 优化问题恰好满足这个条件：可量化（运行时间、SOL 分数）、有理论上限（硬件极限）、问题空间巨大（穷举不可能）。

### 1.2 为什么 Kernel 优化特别困难

GPU Kernel 优化是一个长期被人类专家垄断的领域，原因有三：

**第一**：需要 deep hardware 理解。CUDA C++ 写 kernel 需要理解寄存器分配、shared memory 调度、warp 分组、tensor core 利用率——这些知识散落在 NVIDIA 文档和经验中，没有标准教材。

**第二**：问题空间远超人工探索能力。一个 2048×2048 的矩阵乘法，不同的 tiling strategy、unrolling factor、pipelines 度组合有上百万种可能。

**第三**：端到端优化需要跨层思考。PyTorch eager 模式 → CUDA kernel → PTX assembly → 硬件指令，这是大多数工程师一辈子不会接触的层次。

> "Fully performant matrix multiplication kernels (GEMMs) require inline PTX (akin to assembly language), pipelining, and staging within a kernel. As a result, writing fast GEMMs has been historically siloed to highly experienced kernel experts."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

---

## 2. 实验设计：235 个真实问题，3 周，27 块 GPU

### 2.1 问题来源：SOL-ExecBench 基准测试集

Cursor 与 NVIDIA 合作，使用 **SOL-ExecBench** 生成优化问题。关键设计决策：

> "NVIDIA used SOL-ExecBench to generate 235 optimization problems from over 124 production open-source models such as Deepseek, Qwen, Gemma, Kimi, and Stable Diffusion. As opposed to synthetic data or toy kernels, each problem is a real-world constraint on training or inference workloads for a variety of model architectures: LLMs, diffusion, vision, audio, video, and multi-modal hybrids."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

**这个设计的价值**：不是用玩具问题测试 Multi-Agent，而是在生产级问题上验证。124 个开源模型覆盖了当前 AI 领域的主流架构，意味着这些问题代表了真实的训练/推理瓶颈。

### 2.2 评估指标：SOL 分数

采用 **Speed-of-Light (SOL) 分数**作为核心评估指标：

> "SOL scores represent how good a solution is compared to theoretical hardware limits on a logarithmic curve. A score of 0.5 represents the optimized PyTorch baseline and 1.0 is the performance limit."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

SOL 分数的设计解决了"作弊检测"问题——如果 Agent 用 caching 等手段给出超出硬件极限的结果，SOL 验证会自动 invalidate。这个指标比单纯的 speedup ratio 更难被绕过。

### 2.3 运行环境：27 块 NVIDIA Blackwell 200 GPU

> "We also used SOL-ExecBench to benchmark multi-agent kernel solutions on 27 NVIDIA Blackwell 200 GPUs."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

---

## 3. 核心发现：38% 加速背后的三个关键数字

### 3.1 63% / 38% / 19%：三个层次的性能分布

| 指标 | 数值 | 含义 |
|------|------|------|
| **Problem Coverage** | 149/235 (63%) | Multi-Agent 优于 baseline 的问题比例 |
| **Geomean Speedup** | **38%** | 所有问题的几何平均加速 |
| **2x+ Improvements** | 45/235 (19%) | 超过 2 倍加速的问题比例 |

63% 的覆盖率说明 Multi-Agent 不是万能的——它解决了大部分问题，但有 37% 的问题没有超越 baseline。这与笔者对 Multi-Agent 系统的判断一致：**Multi-Agent 在广度探索上有优势，但在特定深度优化上可能不如针对性的人工方案**。

38% 的几何平均加速是核心指标，但不是最令人震惊的数字。

**真正令人震惊的是 19%**：这 45 个问题代表的是"人类专家已经花了很多时间优化但没有找到最优解"的问题，Multi-Agent 找到了 2x 以上的改进空间。

### 3.2 案例 1：Grouped Query Attention 实现 84% 加速

> "The agent used CUDA C++ to optimize this attention problem extracted from SGLang inference for Llama 3.1 8B. As the agent iterated on the kernel, it successfully employed specific hardware instructions for memory loading and math, added improved scheduling via persistent kernels, and hyper-optimized for input size."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

结果：**SOL score 0.9722（接近硬件极限）**、84% geomean speedup over FlashInfer baseline。更关键的是，这个 kernel 被实际部署到 SGLang 后，观察到 **3% 的 TTFT (Time To First Token) 提升**——端到端收益可测量。

### 3.3 案例 2：GEMM 小矩阵场景超越 cuBLAS

> "Cursor's multi-agent system generated a specialized CUDA C++ GEMM kernel from scratch, coming remarkably close (86%) to a meticulously tuned human baseline from the NVIDIA cuBLAS library. And on small-M test cases, which are especially important for LLM inference decode, the multi-agent system kernel outperformed the library by up to 9%."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

这个结果的意义：**在 LLM inference decode 的关键场景（小矩阵 GEMM）上，Multi-Agent 超越了 NVIDIA 自己的库**。这不是toy experiment，而是对生产软件的实质性贡献。

### 3.4 案例 3：NVFP4 MoE Linear 的量化融合

> "The agent correctly identified the quantization area as the primary bottleneck and accordingly fused scale calculation and rounding. Instead of scaling and then rounding during quantization, it used pre-computed threshold buckets to directly map FP32 values to FP4 codes."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

这个案例展示了 Multi-Agent 的**自适应能力**：它能识别不同类型问题需要不同的优化策略，而不是套用同一个模板。

---

## 4. Multi-Agent 架构：协调协议在一份 Markdown 文件里

### 4.1 Planner/Worker 架构的再次验证

本次实验与 Cursor 自己的代码库迁移实验（见 `planner-worker-multi-agent-autonomous-coding-architecture-2026.md`）使用相同的架构范式：

> "The multi-agent system solved all 235 GPU kernel optimization problems in a single run by deploying a planner agent that distributed and rebalanced work across autonomous workers based on performance metrics."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

关键设计：所有 Worker 独立调用 Benchmark 循环，创建**测试→调试→优化的持续反馈**，不需要人工干预。

### 4.2 协调协议的极简设计

最令人意外的技术细节：

> "The entire coordination protocol lived in a single markdown file that specified the output format, rules, and tests."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

整个协调协议——格式规范、规则、测试用例——都在一份 Markdown 里。这意味着：
- **协议即文档**：不需要额外的 DSL 或配置格式
- **版本控制友好**：协议变更可以用 git diff 查看
- **可读性强**：任何工程师都能理解协议在做什么

### 4.3 双语言实验：CUDA C+PTX vs CuTe DSL

> "In order to better gauge the multi-agent system's capabilities, we asked it to write its solutions in two languages in two separated runs, at opposite ends of the GPU abstraction spectrum: CUDA C with inline PTX (direct hardware access) vs CuTe DSL (high-level composable abstractions with minimal training data presence)."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

这个设计的目的是**探底 Multi-Agent 的能力边界**：
- CUDA C + inline PTX：测试 Agent 能否在硬件层面推理
- CuTe DSL：测试 Agent 能否从文档中学习全新的 API（CuTe 在公开训练数据中极少）

两个场景都成功了，说明 Multi-Agent **不只是复用训练数据中的知识，而是能真正学习和推理**。

---

## 5. 局限与开放问题

### 5.1 SOL 中位数 0.56：大量 room for improvement

> "While the multi-agent harness delivered a 38% geomean speedup over baselines, the median SOL score was still only 0.56, leaving significant room for further optimization."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

0.56 的 SOL 中位数意味着**还有 44% 的理论性能空间未被探索**。Cursor 自己的解释是计算资源受限：235 个问题、27 块 GPU，意味着平均每个问题不到 0.12 块 GPU。

### 5.2 资源瓶颈是 Multi-Agent 的普遍约束

这是一个重要的工程观察：**Multi-Agent 的能力与投入的计算资源成正比**。当问题数量增加、每个问题的探索深度增加时，需要更多 GPU 来支持更多并行 Worker。

这意味着 Multi-Agent 不是免费的午餐——它是** compute-intensive 的解决方案**，适合有充足算力的场景。

### 5.3 37% 的问题未能超越 Baseline

149/235 的问题成功率意味着还有 86 个问题 Multi-Agent 没有解决。Cursor 没有详细分析这些失败案例，这将是后续研究的重要方向。

---

## 6. 对 AI Agent 工程的意义

### 6.1 Multi-Agent 在开放域优化上有天花板

这次实验证明了 Multi-Agent 能解决"没有标准答案"的开放域问题，但同时也暴露了它的边界：中位数 SOL 0.56 意味着**它离理论极限还有很大距离**。

对于 AI Agent 工程的实践者，这意味着：**Multi-Agent 适合"探索性优化"场景（快速找到还不错的解），不适合"逼近理论极限"的场景（需要领域专家反复打磨）**。

### 6.2 Planner/Worker 架构的普遍有效性

从 Cursor 代码库迁移（千级文件、百万行规模）到 CUDA Kernel 优化（235 个独立问题），Planner/Worker 架构在截然不同的任务上都有效。这验证了架构的**通用性**：角色分层、规划与执行解耦、独立失败与重启——这些特性在多种任务类型上都是有效的。

### 6.3 协调协议的设计启示

一份 Markdown 文件承载整个协调协议，这是一个反直觉但正确的设计：**协议越简单，参与者（人类或 Agent）越容易理解和遵守**。

> 笔者认为：在 Multi-Agent 系统中，协议的可读性与系统的可靠性正相关。如果协调协议本身需要复杂的 parser 才能理解，那么它迟早会在边界case 上失败。Markdown 作为协议格式是一个值得关注的设计选择。

---

## 7. 可复用的检查清单

如果你想在某个领域验证 Multi-Agent 系统的能力，Cursor 的实验提供了一个可复用的模板：

**第一步：定义可测量的目标函数**
- 不要用"让代码更好"这种模糊目标
- 目标必须有数值化的评估指标（时间、准确率、SOL 分数）

**第二步：准备真实的问题集**
- 不要用 toy problem，用生产级问题
- 问题来源：主流开源项目的实际痛点

**第三步：构建验证循环**
- Agent 输出 → 评估 → 反馈 → Agent 调整
- 验证循环必须自动化，不依赖人工判断

**第四步：分配充足的计算资源**
- Multi-Agent 的能力上限与计算资源正相关
- 资源不足时，限制 Worker 数量和探索深度

**第五步：区分覆盖率与极致性能**
- 63% 的覆盖率说明"能解决大部分问题"
- 19% 的 2x+ 改进说明"能在特定问题上超越人类"
- 两者都需要报告，不能只报对自己有利的数字