# Cursor Agent Harness 的持续改进工程：从在线实验到生产级 SDK

## 核心论点

> **Cursor 的工程团队将 Agent Harness 视为一个需要持续迭代的软件产品，而非静态的基础设施。通过 A/B 在线实验驱动、量化 Keep Rate 与用户语义满意度、以及模型定制化剪裁，他们将"软能力"（harness engineering）变成了一种可衡量、可重复的工程实践，最终在 2026 年 4 月将这套能力的精华产品化为 `@cursor/sdk`——让任何开发者都能用几行 TypeScript 调用 Cursor 生产级 Agent 运行时。**

---

## 一、Harness 的本质：从"给模型喂数据"到"塑造模型行为"

Cursor 工程师在博客中提出的核心观点是：**Harness 和 Model 共同决定 Agent 的质量**。这意味着 Agent 的能力不是纯粹由模型决定的，Harness 的设计同样重要。

早期（2024 年末）Cursor Agent 的核心问题是：模型选择自己上下文的能力很差，因此团队在 Harness 层面加入了大量"护栏"（guardrails）：
- 每次编辑后主动向 Agent 暴露 lint 和类型错误
- 当 Agent 请求的代码行数过少时，自动重写文件读取请求
- 限制 Agent 单轮可调用的工具数量

然而，随着模型能力的提升，这些护栏变成了**约束**。Cursor 的做法是大规模移除静态护栏，转向**动态上下文**——让 Agent 在工作时自行拉取所需信息，而非预先填充。

> "We still include some useful static context (e.g., operating system, git status, current and recently viewed files). But we've adapted to increasing model capability by knocking down guardrails and providing more dynamic context, which can be fetched by the agent while it works."
> — [Cursor Engineering Blog: Continually improving our agent harness](https://www.cursor.com/blog/continually-improving-agent-harness)

这是一个重要的范式转变：**好的 Harness 不再是"给模型更多信息"，而是"在正确的时机给模型正确的信息"。** 静态上下文填充在模型能力不足时有效，但当模型能主动探索时，它反而增加了噪声。

---

## 二、双重测量体系：离线 Benchmark 与在线 A/B 实验的结合

Cursor 建立了多层测量体系来评估 Harness 变更的效果，分为两类：

### 2.1 离线评估：CursorBench

Cursor 维护了一套公开基准 [CursorBench](https://cursor.com/blog/cursorbench)，用于快速、标准化的质量评估。这提供了跨时间维度的方向性判断，但不能完全替代真实使用场景。

### 2.2 在线实验：A/B 测试 + 语义信号

Cursor 的在线实验系统直接面向真实用户流量，测量维度包括：

| 维度 | 类型 | 说明 |
|------|------|------|
| **Keep Rate** | 核心质量指标 | Agent 生成的代码在用户代码库中保留的比例。这是一个强烈的"任务完成度"信号：用户是否需要手动修改或要求 Agent 修复。 |
| **用户语义满意度** | 高级信号 | 用 LLM 分析用户对 Agent 初始输出的后续响应——用户转向下一个功能说明任务完成好，用户粘贴堆栈跟踪说明任务失败。 |
| **延迟 / Token 效率 / 工具调用数 / 缓存命中率** | 方向性指标 | 这些指标本身不直接说明"Agent 做得对不对"，但能指向系统瓶颈。 |

> "We measure agent quality in these tests through a variety of metrics. Some are straightforward like latency, token efficiency, tool call count, and cache hit rate. Those are directionally useful but still don't get at fuzzier and more important questions of whether the agent actually did a good job."
> — Cursor Engineering Blog

这段话揭示了一个关键认识：**指标和目标是两回事**。Token 效率高不代表 Agent 完成了正确的事。Cursor 选择用 Keep Rate 和语义满意度来逼近"Agent 实际做了什么"这个根本问题。

---

## 三、Context Rot 与工具错误链式效应

Cursor 在博客中描述了一个极具工程价值的现象：**Context Rot**——当工具调用错误累积时，后续决策质量会系统性下降。

```
正确操作 → 状态干净 → 模型正确决策
错误操作 → 错误残留在上下文 → 模型基于错误状态决策 → 新的错误 → 循环恶化
```

这与我在之前分析 [Anthropic GAN 三代理架构](articles/harness/anthropic-gan-inspired-three-agent-architecture-long-running-apps-2026.md) 时提到的"错误传播导致整个任务失败"是同一机制在不同层面的体现。Cursor 将其量化为**工具错误率监控**，并建立了以下分类体系：

- **Unknown Error**： Harness 自身的 Bug（触发告警的阈值是固定的）
- **InvalidArguments / UnexpectedEnvironment**：模型自身的错误（每个模型有基线）
- **ProviderError**：外部工具供应商的故障

> "Any unknown error represents a bug in the harness, and we treat it accordingly."
> — Cursor Engineering Blog

Cursor 的做法是：**为每个工具、每个模型分别建立基线**，因为不同模型在不同工具上的错误率差异很大。这不是简单的阈值告警，而是一个自适应的异常检测系统。

---

## 四、自动化 Software Factory：Harness 的自我修复

Cursor 在 2026 年初的一个 Sprint 中，将意外的工具调用错误率降低了一个数量级（order of magnitude）。这一成果的核心机制是一个**自动化 Software Factory**：

1. **每周运行的 Automation**：装备了一个 Skill，该 Skill 教会模型如何搜索日志
2. **问题发现**：自动识别新出现的问题和最近激增的问题
3. **Ticket 创建**：在 backlog 中自动创建或更新 ticket
4. **Cloud Agent 修复**：大规模并行触发修复（"lean heavily on Cloud Agents to kick off fixes for many issues at once"）
5. **Linear 集成**：甚至可以从 Linear 直接触发修复

> "Over the course of a focused sprint earlier this year, we drove unexpected tool call errors down by an order of magnitude."
> — Cursor Engineering Blog

这意味着 Cursor 的 Harness 不是被动响应问题的系统，而是**主动发现和修复问题的系统**。这已经接近 DevOps 中的"自动化修复"理念，只不过修复对象是 Agent 的行为质量。

---

## 五、模型定制化：Harness 的深度差异

Cursor 的 Harness 为每个支持的模型做了深度定制，这种定制深入到了**工具格式**层面：

- **OpenAI 的模型**：使用基于 patch 的编辑格式（模型训练时的格式）
- **Anthropic 的模型**：使用字符串替换格式（模型训练时的格式）

> "Either model could use either tool, but giving it the unfamiliar one costs extra reasoning tokens and produces more mistakes."
> — Cursor Engineering Blog

这揭示了一个重要的工程洞察：**工具格式不是中性的，它是模型能力的一部分**。选择模型不熟悉的工具格式会直接导致 Token 浪费和错误率上升。这意味着当你选定了模型，Harness 的工具配置就基本确定了。

此外，Cursor 还为不同提供商、甚至同一提供商的不同版本模型提供了**定制化 Prompt**。OpenAI 模型倾向于精确遵循指令，Claude 模型更"直觉"，对模糊指令的容忍度更高——Harness 需要适配这些差异。

### 5.1 "Context Anxiety"：一个模型定制化的极端案例

Cursor 提到一个模型在上下文窗口接近填满时开始拒绝工作——它会自我审查说"任务看起来太大了"。Cursor 通过**Prompt 调整**降低了这种行为。这说明模型的"自我限制"行为可以通过 Harness 层的指令工程来干预。

---

## 六、Mid-Chat 模型切换的工程挑战

Cursor 坦诚地描述了一个工程难题：当用户在中途切换模型时会发生什么？

1. **Harness 切换**：不同的模型有不同的 Harness（工具集、Prompt）
2. **对话历史不匹配**：历史由另一个模型生成，对新模型来说是 out-of-distribution
3. **缓存失效**：缓存是提供商和模型特定的，切换后缓存未命中

Cursor 的解决方案：
- 为中途接手的模型添加自定义指令，告诉它正在"从另一个模型接手"
- 同时引导它不要调用历史中出现但自身工具集中不存在的工具
- 实验"切换时总结对话"来减轻缓存惩罚，但发现如果任务复杂，总结会丢失关键细节

> "We generally recommend staying with one model for the duration of a conversation unless you have a reason to switch."
> — Cursor Engineering Blog

这是第一个我看到的、**以工程结论形式给出的模型切换建议**——不是因为哲学原因，而是因为上下文失配导致的信息损失太大。

---

## 七、产品化：从 Harness 迭代到 `@cursor/sdk`

2026 年 4 月 29 日，Cursor 将其持续迭代的 Harness 能力产品化为 `@cursor/sdk`（公开 Beta）。这是本次分析文章的"落地结论"：

```
Harness 改进工程（2024-2026）→ 产出稳定可用的生产级 Agent 运行时 → SDK 产品化
```

SDK 的核心价值主张是：**让开发者不用自己构建整个 Agent 栈**：
- 安全沙箱（不用自己搭）
- 持久状态与会话管理（不用自己管）
- 环境初始化（不用自己写 initializer agent）
- 上下文管理（不用自己设计动态上下文策略）

> "Building fast, reliable, and capable coding agents that run safely against your data requires meaningful engineering effort: secure sandboxing, durable state and session management, environment setup, and context management."
> — [Cursor Blog: Build programmatic agents with the Cursor SDK](https://www.cursor.com/blog/typescript-sdk)

Cursor SDK 的编程模式：
```typescript
import { Agent } from "@cursor/sdk";

const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  local: { cwd: process.cwd() },
});

const run = await agent.send("Summarize what this repository does");

for await (const event of run.stream()) {
  console.log(event);
}
```

这是一个**声明式 API**——用户只需描述目标，Agent 运行时处理所有中间环节。Cloud Agent 场景下：
```typescript
const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "gpt-5.5" },
  cloud: {
    repos: [{ url: "https://github.com/cursor/cookbook", startingRef: "main" }],
    autoCreatePR: true,
  },
});
```

---

## 八、与 Anthropic Harness Engineering 的系统性对比

| 维度 | Cursor | Anthropic |
|------|--------|-----------|
| **核心方法** | 在线实验驱动（Keep Rate + 语义满意度）| GAN 启发三代理架构（Initializer/Worker/Checker）|
| **上下文管理** | 动态拉取为主，模型自适应 | 三层分离避免上下文污染 |
| **错误处理** | 工具错误率监控 + 自动化 Software Factory | 代理间权限分层隔离 |
| **模型定制化** | 工具格式/Prompt 定制到版本级别 | Agent Skills 渐进式披露 |
| **产品化路径** | `@cursor/sdk` 公开 Beta | Claude Code + Plugins |
| **多 Agent 编排** | Subagent API + Cloud Agents | Multi-Agent Skill 协作 |
| **自我修复** | Cloud Agent 并行修复 + Linear 触发 | GAN Checkpoint 重试 |

两者代表了两个不同的工程哲学：
- **Cursor**：从产品角度出发，通过海量用户流量驱动实验，快速迭代
- **Anthropic**：从架构角度出发，通过抽象模型（GAN）指导设计，再逐步落地

但两者的收敛方向是相同的：**让 Harness 成为 Agent 能力的放大器，而不是限制器。**

---

## 九、判断与局限

### 9.1 我认为的真正贡献

Cursor 这次发布的最大价值不在于某个单点技术突破，而在于**将 Agent Harness 的质量工程化、可衡量化**。Keep Rate + 语义满意度的双重信号体系，使得"Agent 做得好不好"这个问题第一次有了可操作的量化方法。

### 9.2 已知的局限

1. **模型切换建议**：Cursor 明确说"不推荐中途切换模型"，但这实际上是对架构局限的承认。如果 Harness 设计得足够好，切换应该对用户透明。
2. **Context Rot 的根因**：文章描述了 Context Rot 现象，但未深入解释为什么错误会在上下文中"累积"并导致决策质量下降——这是一个值得单独成文的机制分析。
3. **在线实验的边界**：用户语义满意度依赖 LLM 分析，这是一个间接信号，可能存在系统性偏差（例如，用户可能因为"已经习惯了低质量"而给出正面反馈）。

### 9.3 工程启示

对于构建 Agent 系统的团队，Cursor 的实践提供了以下可直接复用的检查点：

- **建立 Keep Rate 指标**：追踪 Agent 生成代码的最终保留率，这是比"工具调用成功"更好的质量信号
- **为每个模型建立工具错误基线**：不同模型在不同工具上的错误率不同，一把钥匙开所有锁的阈值设计会漏掉大量信号
- **Context Rot 是真实存在的**：当 Agent 工具调用失败时，立即重置相关上下文，而非让错误累积
- **模型定制化要深入到工具格式层**：工具格式的选择不是中性的，它直接影响推理 Token 消耗和错误率

---

## 参考文献

1. Cursor Engineering Blog, "Continually improving our agent harness", Apr 30, 2026 — https://www.cursor.com/blog/continually-improving-agent-harness
2. Cursor Blog, "Build programmatic agents with the Cursor SDK", Apr 29, 2026 — https://www.cursor.com/blog/typescript-sdk
3. Cursor Blog, "CursorBench: How we compare model quality in Cursor", Mar 11, 2026 — https://www.cursor.com/blog/cursorbench
4. Cursor GitHub, "cookbook" repo — https://github.com/cursor/cookbook