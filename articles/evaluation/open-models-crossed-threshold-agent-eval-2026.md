# Open Models 跨越 Agent 任务门槛：GLM-5 / MiniMax M2.7 评测深度解析

> **核心问题**：Open Models（GLM-5、MiniMax M2.7）是否真的能在 Agent 任务上追平 Closed Frontier Models？追平的是哪些能力，差距又在哪里？这个答案如何改变生产环境中 Agent 的成本架构？
>
> **读完能得到什么**：一份有数据支撑的判断——Open Models 在 Agent 评测上现在处于什么位置，以及基于此的工程决策框架。

---

## 一、开篇：为什么这个阈值值得追踪

2026 年，闭源 Frontier Models（如 Claude Opus 4.6、GPT-5.4）一直在 Agent 评测榜上领先。行业默认的假设是：要在生产环境里可靠地跑 Agent（工具调用、文件操作、指令遵循），你需要用这些顶级闭源模型。

LangChain 的这篇评测（2026-04-13）第一次用**同一套评测框架、同一个 Harness、同样的评分标准**，系统地比较了开源模型和闭源模型在 Agent 任务上的表现。结果显示：GLM-5 和 MiniMax M2.7 在核心 Agent 能力上已经追平了闭源前沿模型——但只在特定能力维度上。

这不是"All AI are equal now"的营销论断，而是一个**有边界的、可操作的工程结论**。

---

## 二、为什么 Open Models 在 2026 年值得认真对待

### 2.1 成本与延迟的现实约束

在理论上，用最强的模型处理所有任务是最佳选择。实践中，成本和延迟让这个方案不可持续。

| 模型 | 类型 | Input ($/M tokens) | Output ($/M tokens) |
|------|------|-------------------|---------------------|
| Claude Opus 4.6 | Closed | $5.00 | $25.00 |
| Claude Sonnet 4.6 | Closed | $3.00 | $15.00 |
| GPT-5.4 | Closed | $2.50 | $15.00 |
| **GLM-5** (Baseten) | **Open** | **$0.95** | **$3.15** |
| **MiniMax M2.7** (OpenRouter) | **Open** | **$0.30** | **$1.20** |

按每天 10M 输出 tokens 计算：
- Opus 4.6：约 $250/天
- MiniMax M2.7：约 $12/天
- **年化差距：约 $87,000**

在高频 Agent 场景，这个成本差足以改变整个系统的经济模型。

### 2.2 推理加速改变延迟格局

Open Models 的另一个优势是推理加速生态成熟。OpenRouter 数据显示：

| 模型 +  Provider | 平均延迟 | 吞吐速度 |
|-----------------|---------|---------|
| GLM-5 (Baseten) | **0.65s** | **70 tokens/s** |
| Claude Opus 4.6 (Anthropic) | 2.56s | 34 tokens/s |

GLM-5 在 Baseten 上的延迟是 Opus 4.6 的 **1/4**，吞吐是 **2 倍以上**。这不是小优化，而是数量级差距。

这对交互式产品（需要快速响应的 Agent 应用）影响尤为显著。Groq、Fireworks、Baseten 这类专门为 LLM 优化的推理提供商，正在把 Open Models 的延迟差距变成竞争优势。

---

## 三、评测方法论：为什么这套框架值得关注

Deep Agents 的评测方法值得单独分析，因为它展示了 Agent 评测的核心挑战：**Agent 任务不只是答对，还要高效地答对**。

### 3.1 四指标评测体系

Deep Agents 定义了四个指标，覆盖 Agent 任务的完整质量图谱：

**① Correctness（正确率）** — 核心质量信号
```
passed / total
```
通过硬性断言（hard-fail checks）的测试占比。0.68 意味着 68% 的测试用例被正确解决。这是**最重要的指标**，但不是唯一指标。

**② Solve Rate（解决率）** — 正确性 + 速度的复合指标
```
对每个测试：expected_steps / wall_clock_seconds
failed 测试贡献 0
最终分数：所有测试的平均值
```
这是一个"效率修正的正确率"——解决得快且对的模型得分更高。两个模型正确率相同，解决更快的模型 Solve Rate 更高。

**③ Step Ratio（步数比）** — Agent 规划效率
```
total_actual_steps / total_expected_steps
```
值为 1.0 意味着 Agent 用了"预期"的步数。高于 1.0 = 多走了弯路（less efficient）；低于 1.0 = 比预期更高效。这个指标揭示了 Agent 的**规划效率**，而不仅仅是结果正确性。

**④ Tool Call Ratio（工具调用比）** — 工具使用效率
```
同上，但统计的是 individual tool calls 而非 steps
```
值高于 1.0 意味着 Agent 调用了超过必要数量的工具（over-budget），低于 1.0 则是 under-budget。

### 3.2 评测分类：7 类覆盖 Agent 核心能力

Deep Agents 在 7 个维度上评测模型：

| 维度 | 覆盖的能力 |
|------|-----------|
| File Operations | 文件读写、代码修改 |
| Tool Use | 工具调用、参数构造 |
| Retrieval | 信息检索、RAG |
| Conversation | 对话管理、上下文理解 |
| Memory | 记忆读写、状态持久化 |
| Summarization | 内容压缩、摘要生成 |
| Unit Tests | 测试编写、执行验证 |

这 7 个维度覆盖了从"短期反应"（tool use）到"长程规划"（memory）的完整 Agent 能力谱系。

---

## 四、关键数据：Open vs Closed 真实差距

### 4.1 总体结果

| 模型 | Correctness | Passed | Solve Rate | Step Ratio | Tool Call Ratio |
|------|-------------|--------|------------|------------|-----------------|
| Claude Opus 4.6 | **0.68** | 100/138 | 0.38 | 0.99 | 1.02 |
| Gemini 3.1 Pro | 0.65 | 96/138 | 0.26 | 0.99 | 1.01 |
| GPT-5.4 | 0.61 | 91/138 | **0.61** | 1.05 | 1.15 |
| **GLM-5** | **0.64** | 94/138 | **1.17** | 1.02 | 1.06 |
| **MiniMax M2.7** | **0.57** | 85/138 | 0.27 | 1.02 | 1.04 |

### 4.2 分维度正确率

| 模型 | Conversation | File Ops | Memory | Retrieval | Summarization | Tool Use | Unit Test |
|------|-------------|----------|--------|-----------|---------------|----------|-----------|
| Opus 4.6 | **1.0** | 1.0 | 0.67 | 1.0 | 1.0 | 0.87 | 1.0 |
| Gemini 3.1 Pro | 0.24 | 0.92 | 0.62 | 1.0 | 0.8 | 0.79 | 0.92 |
| GPT-5.4 | 0.29 | 1.0 | 0.44 | 1.0 | 0.8 | 0.76 | 1.0 |
| **GLM-5** | 0.38 | **1.0** | 0.44 | 1.0 | 0.6 | **0.82** | **1.0** |
| **MiniMax M2.7** | 0.14 | 0.92 | 0.38 | 0.8 | 0.6 | **0.87** | 0.92 |

### 4.3 数据读法：Open Models 追平了什么，差距在哪里

**File Operations（文件操作）：Open = Closed**
GLM-5（1.0）和 Opus 4.6（1.0）完全持平。MiniMax M2.7（0.92）也接近满分。这是 Open Models 表现最强的维度。

**Tool Use（工具调用）：Open ≈ Closed**
MiniMax M2.7（0.87）和 Opus 4.6（0.87）持平。GLM-5（0.82）略低，但差距不大。对于依赖工具调用的 Agent 系统，这个维度的持平是最重要的信号。

**Unit Tests（单元测试）：Open = Closed**
GLM-5（1.0）和 Opus 4.6（1.0）完全持平。MiniMax M2.7（0.92）也非常接近。这是 Open Models 的第二个强项。

**Conversation（对话）：Closed 显著领先**
Opus 4.6（1.0），而 GLM-5（0.38）、MiniMax M2.7（0.14）。这是差距最大的维度，Open Models 在需要复杂多轮上下文理解和对话状态管理的任务上明显落后。

**Memory（记忆）：Closed 领先**
Opus 4.6（0.67）vs GLM-5（0.44）、MiniMax M2.7（0.38）。差距明显但在可接受范围内。

### 4.4 Solve Rate 的隐藏信息

GLM-5 的 Solve Rate 高达 1.17，远超所有其他模型（次高 GPT-5.4 是 0.61）。这意味着 GLM-5 不仅正确解决了问题，而且解决速度非常快（expected_steps / wall_clock_seconds 的比值远超预期）。

> **工程建议**：在追求"又快又对"的场景，GLM-5 的 Solve Rate 优势值得特别关注。

---

## 五、Harness 层适配：Open Models 的工程可用性

评测结果的工程落地性取决于 Harness 对不同模型的适配能力。Deep Agents SDK 做了三层关键适配：

### 5.1 Model Identity Injection

Open Models 的上下文窗口、工具调用格式、失败模式与闭源模型不同。Deep Agents 在运行时动态修改 system prompt，注入模型身份信息：

```
模型名称 + Provider + 上下文限制 + 支持的模态
```

这样 Agent 知道自己跑在什么模型上，能调整自己的行为预期。

### 5.2 Context Management 自适应

压缩、卸载、摘要的阈值根据模型的实际上下文窗口动态调整——而不是硬编码默认值。

```
4K 上下文的模型 → 更激进的压缩策略
1M 上下文的模型（如 Opus）→ 可以更宽松
```

### 5.3 一行代码切换模型

```python
# GLM-5
from deepagents import create_deep_agent
agent = create_deep_agent(model="baseten:zai-org/GLM-5")

# MiniMax M2.7
from deepagents import create_deep_agent
agent = create_deep_agent(model="openrouter:minimax/minimax-m2.7")
```

Harness 屏蔽了不同模型的接入差异。对于追求"模型中立"的团队，这是核心价值。

---

## 六、Planning/Execution 分离：Open Models 的架构价值

Deep Agents CLI 引入了一个有架构意义的模式：**Runtime Model Swapping**。

### 6.1 中间件实现

ConfigurableModelMiddleware（Deep Agents CLI）允许在会话中途切换模型，无需重启 Agent：

```python
# 模型切换中间件伪代码
class ConfigurableModelMiddleware:
    def __init__(self, planning_model, execution_model):
        self.planning_model = planning_model
        self.execution_model = execution_model
    
    def process(self, turn):
        if turn.requires_planning:
            return self.planning_model.generate(turn)
        else:
            return self.execution_model.generate(turn)
```

### 6.2 Planning/Execution 分离的逻辑

- **Planning**：需要更强的推理能力、更长的上下文 → Frontier Model
- **Execution**：需要可靠的工具调用、文件操作 → Open Model

用一条 `/model` 斜杠命令就能在会话中切换。实测效果：用 Frontier Model 做规划，用 Open Model 执行，达到相近的正确率，同时大幅降低成本。

### 6.3 架构意义

这个模式的本质是**把 Agent 的"思考"和"行动"解耦**——Anthropic 的 Brain/Hands 分离在 Open Models 世界里的等价实现。Planning 用贵的但聪明的模型，Execution 用便宜的但够用的模型。两者通过外部化上下文（Session）连接。

---

## 七、已知局限

### 7.1 Conversation 是最大短板

Open Models 在对话理解上与闭源前沿模型差距显著（MiniMax M2.7: 0.14 vs Opus 4.6: 1.0）。这意味着：

- **对话型 Agent**（客服、销售等）暂不适合用 Open Models
- **工具型/执行型 Agent**（编码、数据处理等）可以大胆迁移

### 7.2 评测集规模有限

138 个测试用例虽然覆盖了 7 个维度，但每个维度的样本量仍然偏小。在 Conversation 维度 0.14 的分数可能受到个别极端用例的影响，不宜过度解读。

### 7.3 OpenRouter / Baseten 的第三方风险

GLM-5 和 MiniMax M2.7 的实测数据来自 OpenRouter 和 Baseten，而非直接自托管。这意味着**性能数字包含了 Provider 侧的优化**，自托管或换 Provider 可能产生差异。

---

## 八、工程决策框架：什么时候选 Open Models

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 工具调用为主的编码 Agent | **GLM-5 / MiniMax M2.7** | Tool Use ≈ Frontier，价格 1/10 |
| 文件操作密集型 Agent | **GLM-5** | File Ops = 1.0，Unit Test = 1.0 |
| 需要快速交互的 Agent | **MiniMax M2.7**（Groq/ Fireworks） | 0.65s 延迟，70 tokens/s |
| 对话密集型 Agent | **Claude Opus 4.6 / GPT-5.4** | Conversation 仍是 Closed 的主场 |
| 长程 Memory 依赖型 Agent | **Claude Opus 4.6** | Memory = 0.67，显著领先 |
| 高频大规模部署 | **MiniMax M2.7** | 20x 成本优势，可覆盖更多请求 |

---

## 九、结论

Open Models 在 Agent 任务上**已经跨越了实用门槛**——但这个门槛的定义需要精确：

- ✅ **已跨越**：File Operations、Tool Use、Unit Tests（Core Agent 执行能力）
- ❌ **尚未跨越**：Conversation（对话理解）、Memory（上下文持久化）

对于以"工具调用 + 文件操作 + 指令遵循"为核心能力的 Agent 系统，Open Models 已经是工程上可行的选择。成本降低 10-20 倍，延迟改善 2-5 倍，而正确率差距在可接受范围内。

**Planning/Execution 分离模式**是这个趋势最有趣的架构衍生：Open Models 不是在所有任务上替代 Frontier Models，而是在 Agent 系统的特定层次上发挥价值。这与 LLM Model Routing（多模型编排）的趋势一脉相承——模型选择是 Agent 架构的一等公民，不是后台的运维决策。

---

## 参考文献

- [LangChain Blog: Open Models have crossed a threshold](https://blog.langchain.com/open-models-have-crossed-a-threshold/) — 评测数据的一手来源
- [Deep Agents GitHub](https://github.com/langchain-ai/deepagents) — 开源 Harness 框架
- [SWE-Rebench](https://swe-rebench.com/) — Open Model Agent 评测基准
- [Terminal Bench 2.0](https://www.tbench.ai/leaderboard/terminal-bench/2.0) — Agent 评测排行榜
- [LangSmith Public Evals](https://smith.langchain.com/public/d4245855-4e15-48dc-a39d-8631780a9aeb/d) — 实时评测运行数据
