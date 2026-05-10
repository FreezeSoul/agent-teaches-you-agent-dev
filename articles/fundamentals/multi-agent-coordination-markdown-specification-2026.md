# Multi-Agent 协调协议的本质重构：从代码约束到 Markdown 规范

> 本文探讨 Cursor 与 NVIDIA 合作实验中揭示的 Multi-Agent 协调核心范式：当协调协议从代码层面下沉到 Markdown 规范层，Agent 系统获得了什么？为什么这是 Multi-Agent 工程的关键转折点？
>
> 核心论点：**将协调逻辑从代码层抽离为声明式 Markdown 规范，是 Multi-Agent 系统从「执行工具」进化为「探索引擎」的核心设计转变**。这一转变让系统得以将有限的 Agent 能力集中在「解决问题」而非「管理协作流程」上。

---

## 问题背景：协调代码的隐性成本

传统 Multi-Agent 系统的协调逻辑通常以三种形式存在：

| 形式 | 典型实现 | 隐性成本 |
|------|---------|---------|
| **硬编码** | if-else 条件分支、状态机转换 | 扩展性差，新增协调需求必须修改核心代码 |
| **配置驱动** | YAML/JSON 配置协调规则 | 配置复杂度随 Agent 数量指数增长，边界情况难以穷举 |
| **共享状态** | 数据库/Redis 中的协调状态 | 协调逻辑与业务逻辑耦合，调试困难，状态一致性成为新问题 |

> "In traditional multi-agent orchestration, the coordination logic becomes a second 'application' that competes for complexity budget with the actual task logic." — 来自工程实践的观察

对于开放式的优化问题（如 CUDA Kernel 优化），协调逻辑的复杂性会直接挤压 Agent 用于解决问题的能力预算。**如果协调层消耗了太多认知资源，Agent 就无法充分探索解空间**。

---

## 核心发现：Markdown 作为协调协议

Cursor 实验中的关键设计选择是：**整个协调协议存活在一个 Markdown 文件中**。

这个 Markdown 文件包含了三个核心组件：

```markdown
# CUDA Kernel Optimization Coordination Protocol

## Output Format
- 解决方案必须输出到 `src/kernel.cu`
- 性能数据必须写入 `solution.json`
- 日志必须输出到 `traces.jsonl`

## Rules & Constraints
- 禁止使用任何缓存机制
- 所有 kernel 必须通过 correctness verification
- SOL score 低于 0.3 的方案必须重新生成

## Tests
- 使用 `python -m utils.verification` 验证正确性
- 使用 `python -m utils.profiling` 测量性能
- 阈值：SOL > 0.5 才算合格
```

这不是一个「提示词模板」，而是一个**可执行的环境契约**：
- 它定义了 Agent 与环境之间的接口边界
- 它指定了验证和测试的自动化路径
- 它设定了合格性的量化门槛

> "The entire coordination protocol lived in a single markdown file that specified the output format, rules, and tests."
> — [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)

---

## 为什么 Markdown Specification 优于代码协调

### 1. 声明式 vs 过程式：边界清晰 vs 隐含依赖

代码协调逻辑的问题是**副作用难以追踪**——当协调状态与任务状态混杂在一起，Agent 无法清晰区分「这是任务的约束」还是「这是协调的约束」。

Markdown 规范是**纯声明式的**：它描述「what」而非「how」。Agent 在执行时无需理解协调逻辑的实现细节，只需遵守接口契约即可。

```python
# 代码协调的问题示例
if agent.state == "optimizing" and metric.score > 0.5:
    if len(agent.attempts) > 3:
        # 协调逻辑悄悄改变了行为
        agent.strategy = "hybrid"  # 副作用：改变了优化策略
```

```markdown
# Markdown 规范的优势：零副作用
## Rules
- SOL score 低于 0.3 必须重新生成
- 最多允许 5 次尝试

<!-- Agent 自己判断何时触发重试，不需要协调代码介入 -->
```

### 2. 人类可读性：让非工程师也能理解约束

当协调协议是 Markdown 时，产品经理、安全审计员、甚至领域专家都可以阅读并理解系统的行为边界。这对于**合规要求高、可解释性要求强**的场景尤为重要。

### 3. 自我描述性：规范本身就是测试的来源

Markdown 规范中的 Rules 和 Tests 是自洽的——规范中声明的约束直接映射到自动化测试的断言。这种一致性在代码协调中需要额外的测试设计工作来保证。

---

## Self-Benchmarking 闭环：从验证到自驱

Markdown 协调协议的另一个关键设计是**Self-Benchmarking**：Agent 在运行过程中自行学习调用基准测试管道。

```
┌─────────────────────────────────────────────────────────────┐
│                      Markdown 规范                          │
│  "使用 python -m utils.profiling 测量性能"                   │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                     Worker Agent                            │
│  行为：生成 kernel → 调用 profiling → 读取 SOL 分数          │
│  状态：无需人工触发，自主学习调用基准管道                     │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                   Benchmark Pipeline                        │
│  输出：SOL score / latency / correctness                    │
│  特征：防作弊设计（硬件极限对比）                            │
└─────────────────────────────────────────────────────────────┘
                               ↓
                    ↑              ↓
                    └──────────────┘
              （持续迭代直到达标）
```

> "The multi-agent system independently learned to call the benchmarking pipeline during its runs, creating a loop where the system continuously tested, debugged, and optimized kernels without any developer intervention."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

这个闭环的关键在于**Agent 学会了「测量驱动改进」而非「人工判断改进」**。在传统设置中，Agent 依赖人类的反馈来判断是否继续优化；在 Self-Benchmarking 模式下，Agent 依赖量化指标自主决策。

---

## 对 Multi-Agent 工程实践的启示

### 启示一：协调逻辑应该「脱糖」

当你发现协调代码开始占据 Agent 提示词的主要篇幅时，这是一个**架构预警信号**——协调逻辑正在消耗 Agent 的认知预算。

正确的方法：
1. 将协调约束提取为 Markdown 规范
2. 让 Agent 通过**遵守规范**而非**理解协调逻辑**来参与协作
3. 协调的复杂度通过规范的丰富度表达，而非代码的条件分支

### 启示二：量化门槛是自动化的前提

Self-Benchmarking 闭环能够运行的前提是**存在可信的量化指标**。在 CUDA Kernel 场景中，SOL 分数提供了这个基础；在其他领域，这个指标可能需要重新设计。

> "One of the best ways to evaluate long-running, multi-agent systems is to give them open-ended optimization problems where even we don't know the right answer. Kernel optimization problems meet this criteria: they provide measurable objectives that the system can iteratively optimize against."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

如果没有可测量的目标，Self-Benchmarking 闭环就无法形成。**测量设计是 Multi-Agent 系统的基础设施设计**。

### 启示三：开放问题的解空间探索需要边界约束

Cursor 实验的隐含结论是：**约束越清晰，Agent 的探索效率越高**。Markdown 规范中的 Rules 实际上是在告诉 Agent「哪些区域是禁止进入的」——这反而帮助 Agent 集中资源探索可行域。

```markdown
## Rules（约束）
- 禁止使用任何缓存机制  ← 边界清晰
- SOL score 低于 0.3 必须重新生成  ← 目标清晰
- 最多允许 5 次尝试  ← 资源约束清晰
```

当 Agent 知道「什么不能做」和「做到什么算合格」时，它可以将认知资源集中在「如何做」上。

---

## 从 Cursor 实验看 Multi-Agent 的演进方向

Cursor 的实验指向了一个明确的趋势：**Multi-Agent 系统正在从「协调工具」进化为「探索引擎」**。

这个演进的标志是：
- 协调逻辑从代码层下沉到声明式规范层
- 人类的角色从「每步介入」变为「边界设定者」
- Agent 的能力从「执行已知流程」变为「在未知解空间中自主探索」

> "The most ambitious tasks in software are open-ended, without a clear solution. Single agent systems struggle here because models are best at narrowly scoped tasks they have already seen during training. We see the kernel optimization experiment as further validation that multi-agent architectures will quickly become the default approach to building software because they can tackle novel problems that fall far outside training data distribution."
> — [Cursor Blog](https://cursor.com/blog/multi-agent-kernels)

---

## 关联项目

- [Cursor 多智能体系统 38% 加速：CUDA Kernel 优化的工程方法论解析](./cursor-multi-agent-cuda-kernel-optimizer-38-percent-2026.md) — 完整的实验方法论解析（Planner/Worker 架构 + Self-Benchmarking 闭环）
- [CudaForge — 训练免费的多智能体 CUDA Kernel 生成工作流](./Fangcun-AI-SkillWard-security-scanner-agent-skills-2026.md)（关联：规范化协调 → 开源实现）
- [CUDA-Agent — 字节跳动 × 清华 RL 训练的 GPU Kernel 优化系统](./cuda-agent-byted-tsinghua-rl-kernel-optimization-2026.md)（关联：Self-Benchmarking 闭环 → RL 训练闭环的演进）

---

*本文核心内容基于 [Cursor Blog: Speeding up GPU kernels by 38% with a multi-agent system](https://cursor.com/blog/multi-agent-kernels)，由 Cursor AI 与 NVIDIA 合作完成。*