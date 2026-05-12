# Multi-Agent 系统的工程验证：Cursor 如何用 3 周超越 Kernel 专家数月积累

## 核心问题：Multi-Agent 系统在真实工业挑战上的能力边界在哪里

当多 Agent 架构成为 Agent 开发的主流范式时，一个关键问题始终缺乏答案：**这些系统在真实工业挑战上的能力边界在哪里？** 它们只是在简单任务上表现良好的 demo，还是能够在真正的硬骨头问题上超越人类专家？

Cursor 与 NVIDIA 合作的 CUDA Kernel 优化实验提供了迄今为止最清晰的答案。

---

## 实验背景：为什么选 Kernel 优化

Kernel 优化是 GPU 编程中最困难的领域之一。一个性能优秀的 GEMM（矩阵乘法）内核需要：
- 深入理解硬件指令（PTX 汇编）
- 精确的内存访问调度
- 流水线与 staging 技巧
- 对特定 shape 的极致调优

> "Writing fast GEMMs has been historically siloed to highly experienced kernel experts."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

这个领域如此专业，以至于即使在 AI 编程快速发展的今天，Kernel 优化仍然是人类专家的专属领地。Cursor 选择这个领域作为 Multi-Agent 的测试场，正是要回答：「Multi-Agent 能否踏入这个禁地？」

---

## 实验设计：三周、235 问题、27 块 B200

### 问题来源：真实生产负载

> "NVIDIA used SOL-ExecBench to generate 235 optimization problems from over 124 production open-source models such as Deepseek, Qwen, Gemma, Kimi, and Stable Diffusion."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

问题集覆盖 LLMs、Diffusion、Vision、Audio、Video 和多模态模型，确保优化结果有真实的工业价值而非 benchmark 刷分。

### 评估体系：SOL-ExecBench

SOL-ExecBench 是 NVIDIA 提供的评估框架，通过两个指标衡量 Kernel 质量：

| 指标 | 定义 | 说明 |
|------|------|------|
| **Geomean Speedup** | Multi-Agent 解 vs PyTorch Baseline 的几何平均加速比 | 衡量相对于单 Agent Baseline 的改进 |
| **SOL Score** | 实际性能 vs 硬件理论上限（0~1） | 0.5 = Baseline，1.0 = 理论极限 |

> "If agents use cheating tactics like caching and deliver performance beyond what a B200 can support, the pipeline invalidates the result."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

SOL 分数防作弊机制确保结果的可信度——任何试图通过缓存等手段伪造数据的解法都会被 pipeline 判定为无效。

### Multi-Agent 架构：单文件协调协议

整个协调协议存在于一个 Markdown 文件中，定义了输出格式、规则和测试。Multi-Agent 系统独立学会调用 benchmark pipeline，创建了「测试→调试→优化」的自动闭环。

关键设计选择：**让每个 Agent 独立学习调用 benchmarking**，而非由中央协调器统一调度。这意味着 Agent 在迭代中自主发现优化策略，而不是执行预设的优化路径。

---

## 核心结果：38% 加速，19% 问题实现 2x+ 提升

### 总体性能

| 指标 | 数值 |
|------|------|
| Geomean Speedup | **1.38x（38%）** |
| 优于 Baseline 问题数 | **149/235（63%）** |
| 2x+ 加速问题数 | **45/235（19%）** |

> "These levels of performance improvement are typically only found through months or years of work from highly experienced kernel engineers. The multi-agent system accomplished it in weeks, addressing a long-tail of kernel problems that had been impractical with existing approaches."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

### 三个代表性案例的差异化策略

#### 案例 1：BF16 Grouped Query Attention（SOL 0.9722，84% 加速）

这是 Llama 3.1 8B 推理中常见的 Paged Prefill 操作。Agent 使用 CUDA C++ 优化，成功运用了：
- 特定硬件指令（内存加载和数学运算）
- Persistent kernels 改进调度
- 针对特定 input size 的极致优化

结果：**SOL 0.9722**，接近理论极限。在 SGLang 中替换该内核后，TTFT（Time To First Token）提升 3%。

#### 案例 2：NVFP4 MoE Linear with Gating（39% 加速）

MoE 模型中的常见模式，但输入和中间乘法输出都量化到 NVFP4（4-bit 浮点）。Agent 的关键洞察：

> "Instead of scaling and then rounding during quantization, it used pre-computed threshold buckets to directly map FP32 values to FP4 codes, which is possible because there are only 16 possible NVFP4 values."

这是一个**数学洞察驱动的优化**：利用 NVFP4 只有 16 个可能值的特性，用查表替代计算，将量化开销从计算变为内存访问。

#### 案例 3：BF16 GEMM（接近 cuBLAS，small-M 超越 9%）

矩阵乘法是公认最难优化的 Kernel，需要 inline PTX、流水线、staging。Cursor Multi-Agent 独立学会了使用 Blackwell 特定指令、优化内存读写、针对特定 shape 极致调优。

结果：**达到 cuBLAS 的 86%**，而在对 LLM 推理 decode 至关重要的 small-M 场景下，**Multi-Agent 的解法比 cuBLAS 快 9%**。

> "On small-M test cases, which are especially important for LLM inference decode, the multi-agent system kernel outperformed the library by up to 9%."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

---

## 工程意义：Multi-Agent 的能力证明

### 1. Planner-Worker 架构的生产验证

实验采用了典型的 Planner-Worker 架构：Planner 负责分配和重新平衡工作，Worker 自主执行并基于性能指标迭代。这验证了：

- **层级协调优于扁平协作**：当问题规模达到 235 个时，没有中央调度就无法高效探索解空间
- **单文件协调协议足够**：整个 Multi-Agent 系统的行为定义在一个 Markdown 中，而非复杂的代码框架
- **Benchmark pipeline 的自驱动调用**：Agent 学会在迭代中主动调用评测，而非等待人类介入

### 2. 开放域优化问题上的突破

> "Single agent systems struggle here because models are best at narrowly scoped tasks they have already seen during training. We see the kernel optimization experiment as further validation that multi-agent architectures will quickly become the default approach to building software because they can tackle novel problems that fall far outside training data distribution."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

关键洞察：**Multi-Agent 的优势在于开放域优化，而非已知任务**。当模型在训练数据中见过类似问题时，单 Agent 可能足够；但当问题超出训练分布时，只有 Multi-Agent 能探索更大的解空间。

### 3. 仍有巨大提升空间

实验的局限性值得注意：Median SOL 分数仅为 0.56，意味着大量问题仍有优化空间。主要约束是 **GPU 资源有限**（27 块 B200）：

> "With more GPUs, the system could explore even deeper and more novel solutions."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

这揭示了一个关键规律：**Multi-Agent 的性能随计算资源线性扩展**——更多的 Agent 意味着更深的探索、更快的迭代。

---

## 方法论价值：如何评估 Multi-Agent 系统

这个实验还提供了一种评估 Multi-Agent 系统能力的**方法论框架**：

### 评估原则 1：给 Agent 无法事先知道答案的问题

> "One of the best ways to evaluate long-running, multi-agent systems is to give them open-ended optimization problems where even we don't know the right answer."
> — [Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

如果评测问题有标准答案，Agent 可能在评测中过拟合。真正的能力测试需要**开放域问题**。

### 评估原则 2：使用可量化的目标，避免 human preference 偏差

SOL-ExecBench 提供了清晰的量化指标（SOL score，speedup ratio），避免了 A/B 测试中的人类偏好偏差。

### 评估原则 3：防作弊机制确保结果可信

如果一个系统声称达到 2x 加速，但使用了缓存等非常规手段，SOL-ExecBench 会将其判定为无效。这确保了评测结果的可信度。

---

## 结论：Multi-Agent 进入工业硬骨头的信号

Cursor 的 CUDA Kernel 优化实验证明了：

1. **Multi-Agent 系统可以在真实工业挑战上超越人类专家**（63% 问题优于 Baseline，19% 实现 2x+）
2. **Planner-Worker 架构是处理大规模开放域优化问题的有效范式**
3. **计算资源是 Multi-Agent 能力的核心约束**——更多 GPU 意味着更深的探索

这个实验的更深层含义在于：**Multi-Agent 的价值不是「更快完成相同任务」，而是「解决单 Agent 无法解决的问题」**。当问题超出训练分布时，Multi-Agent 的探索能力成为关键优势。

开源地址：https://github.com/anysphere/kernel-optimization-results

---

*来源：[Cursor Engineering: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)（2026-04-14）*