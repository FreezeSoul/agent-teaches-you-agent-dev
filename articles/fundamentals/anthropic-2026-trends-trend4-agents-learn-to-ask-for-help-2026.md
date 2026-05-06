# Anthropic 2026 趋势报告解读：Agent 学会在不确定性中主动寻求帮助

> **来源**：Anthropic [2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)
> **原文 Trend 标题**：Trend 4: Agents learn when to ask for help
> **日期**：2026 年第一季度发布
> **分类**：fundamentals
> **关联**：Orchestration · Evaluation · Trustworthy Agents

---

## 核心判断

Anthropic 的 2026 趋势报告中，Trend 4 揭示了一个被长期忽视的 Agent 能力缺陷：**现有的 Agent 默认假设「自己能搞定」，而不是「遇到不确定情况主动问人」。这种盲目自信在低风险场景可以提升效率，但在生产环境中的代价可能是数据泄露、系统故障或安全漏洞。**

**反直觉的核心发现**：

1. **人类目前只将 0-20% 的工作完全委托给 AI** — 不是因为 AI 能力不够，而是因为 AI 不知道什么时候该停下来问
2. **新一代 Agent 系统能主动检测不确定性、标记风险、在关键决策点请求人类输入** — 不是全程自主执行，而是「有判断力地自主」
3. **「请求帮助」的能力需要系统性设计** — 不是靠 Prompt 提示能解决的，而是需要在 Harness 层建立显式的 Uncertainty Flagging 机制

---

## 背景：Agent 为什么「不会」主动寻求帮助

### 传统 Agent 的盲区：Assumption of Competence

现有 Agent 系统的一个隐含假设是：**模型具备完成任务的能力，所以应该自主完成**。这个逻辑在训练阶段是成立的——模型在大量数据上学会了解决各类问题。但在真实生产环境中，模型面对的是：

- 没见过的新技术栈
- 没有测试覆盖的边界条件
- 语义模糊的需求描述
- 缺乏明确正确性标准的开放式问题

在这些情况下，模型不是「能力不足」，而是**无法判断自己给出的答案是否正确**。但由于训练时的奖励信号鼓励「给出答案」而非「承认不确定」，模型倾向于自信地编造（hallucinate）一个答案，而不是说「我不知道」。

> "Agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."
> — [Anthropic Engineering: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

这个现象在代码生成场景尤为严重：Agent 生成的代码可能通过语法检查、逻辑上看起来合理，但实际运行时会出现边界条件失败、安全漏洞或与系统其他部分不兼容。人类开发者会感到「哪里不对劲」，但 Agent 本身无法感知这种模糊的可靠性警告。

### 两种失败模式的根源

Anthropic 在实验中将 Agent 的过度自信失败分为两类：

| 失败模式 | 表现 | 根因 |
|---------|------|------|
| **Self-praise bias** | Agent 评价自己的代码时倾向于打高分，即使有明显缺陷 | 训练时正向反馈过度，缺少「自我批评」的训练信号 |
| **Context anxiety** | Agent 在接近 context 限制时提前结束任务或跳过不确定步骤 | 模型将「完成感」与「任务完成」混淆 |

这两种失败模式的共同特点是：**Agent 缺乏对自身不确定性的元认知能力**。它们不知道自己不知道什么。

---

## 核心解法：不确定性感知架构

### 1. 解耦 Generator 与 Evaluator

Anthropic 在他们的 GAN 启发的三 Agent 架构中，核心洞察是将「生成代码的 Agent」与「评价代码的 Agent」分离：

```
┌─────────────────────────────────────────────────────┐
│                   Generator Agent                     │
│  负责实现功能，追求完成度                             │
└──────────────────────────┬──────────────────────────┘
                           │ 产出（代码/设计）
                           ▼
┌─────────────────────────────────────────────────────┐
│                   Evaluator Agent                    │
│  负责评价质量，能够调用独立判断标准                    │
│  （Playwright MCP、测试套件、设计准则）               │
└──────────────────────────┬──────────────────────────┘
                           │ 评价结果 + 改进建议
                           ▼
              Generator 重新迭代 / 标记需要人工介入
```

关键洞察：**Generator 不知道自己的产出质量，需要一个独立的评估机制**。这不仅仅是技术问题，而是一个架构设计决策——你的 Harness 是假设 Agent 能搞定一切，还是内置了「不确定性触发器」？

### 2. 不确定性 Flagging 的工程实现

Anthropic 的报告指出了工程层面实现不确定性检测的三个维度：

**维度一：内部置信度信号**

模型在给出答案时，其内部激活状态包含了关于「这个答案有多大把握」的信息。一些前沿 Agent 系统通过以下方式提取这种信号：

- 检查模型在关键推理节点的选择分布（选择分布的熵越高，不确定性越大）
- 监控 Tool Call 的拒绝行为——当 Agent 反复拒绝调用某个工具时，可能意味着它无法确定正确的工具
- 追踪连续失败后的重试次数——超过阈值自动触发人工介入标记

**维度二：外部验证信号**

独立于模型输出，通过外部系统进行正确性验证：

- 静态分析工具（linter、类型检查）验证代码语法和基本正确性
- Playwright 等浏览器自动化工具在真实环境中验证 UI 行为
- 单元测试和集成测试套件提供可量化的通过/失败信号

**维度三：人类在环的触发点设计**

不是全程人工监督，而是在关键决策点设置「人工介入触发器」：

| 触发条件 | 预期人类行为 |
|---------|------------|
| 安全相关操作（删除文件、访问凭据、修改系统配置）| 显式审批 |
| 首次接触新代码库 / 新技术栈 | 初始上下文确认 |
| 连续 N 次尝试后仍然失败 | 诊断性人工介入 |
| 涉及外部 API 调用或支付逻辑 | 业务逻辑确认 |

> "Agents are also increasingly used to review AI-generated code for security issues, consistency, and defects at a scale humans cannot match. The effect is more selective human review focused on judgment-heavy calls."
> — [Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)

### 3. Ask-vs-Assume 框架

加州大学 Berkeley 的研究团队提出了一个更系统化的框架：Ask-vs-Assume。

核心思想是：**Agent 在面对不确定性时，应该有一个明确的决策框架来判断「该问还是该猜」**。

```
                      ┌──────────────────────────┐
                      │   不确定性场景触发        │
                      │  (新API/模糊需求/边界条件) │
                      └───────────┬──────────────┘
                                  │
               ┌──────────────────┴──────────────────┐
               ▼                                       ▼
    ┌───────────────────────┐            ┌───────────────────────┐
    │  ASK（主动请求人类澄清）  │            │  ASSUME（基于推理继续执行） │
    ├───────────────────────┤            ├───────────────────────┤
    │  触发条件：             │            │  触发条件：             │
    │  - 需求语义模糊，无法   │            │  - 有足够上下文支持     │
    │    确定唯一正确方案     │            │    合理推断            │
    │  - 涉及安全/隐私/财务   │            │  - 失败后果可恢复      │
    │  - 关键路径依赖链断裂   │            │  - 有测试覆盖          │
    └───────────────────────┘            └───────────────────────┘
```

这个框架的核心价值在于：**它让不确定性不再是 Agent 的「弱点」，而是一个可设计、可测量、可干预的系统特性**。

---

## 工程实践：如何构建不确定性感知的 Agent 系统

### 第一步：在 Harness 层埋入检测点

传统的 Harness 是纯执行循环——调用模型、执行工具、返回结果。要支持不确定性检测，需要在 Harness 中增加「元循环」：

```
Harness Loop:
  1. 调用 Agent
  2. 检测不确定性信号（置信度 / 验证结果 / 连续失败）
  3. 如果不确定性超阈值 → 触发 Human-in-the-Loop
  4. 否则 → 继续执行
```

这不是修改 Agent 的行为（那是模型层面的问题），而是在 Harness 层建立「安全阀」。

### 第二步：建立明确的 Escalation 协议

当 Agent 决定「需要问人」时，它不能只是停在那里等。它需要一个结构化的请求格式：

```json
{
  "type": "human_escalation",
  "uncertainty_area": "接口设计选择",
  "options_considered": [
    "REST API with explicit versioning",
    "GraphQL with nullable fields"
  ],
  "recommendation": "REST with explicit versioning",
  "confidence": 0.35,
  "reasoning": "当前系统已有 REST 约定，新接口保持一致更安全",
  "waiting_on": "架构决策：是否需要支持灰度发布？"
}
```

这个结构让人类介入时能够直接针对问题核心给出判断，而不是重新理解上下文。

### 第三步：将「知道何时不问」纳入评估体系

如果 Agent 评估时不包含「何时该求助」的能力指标，模型就没有动力学习这个行为。Anthropic 的研究发现：

> "In production environments, we observed a 3.2x reduction in error rates when using structured outputs compared to free-form generation."
> — [Anthropic Engineering Blog](https://www.anthropic.com/engineering)

这说明**结构化的输出格式本身就是一种不确定性约束**——当 Agent 被迫在有限选项中做选择时，它的置信度分布更可解释，更容易被 Harness 检测。

---

## 判断性内容：局限性尚未解决

尽管「主动寻求帮助」已经成为 Agent 设计的重要方向，但以下问题尚未被系统性地解决：

**问题一：延迟 vs. 质量的权衡没有标准答案**

Ask-vs-Assume 框架的核心矛盾是：每多问一次人，系统吞吐量就下降一次。对于时间敏感的工作流（如高频交易、实时系统），过多的人工介入可能比 AI 错误本身代价更高。

**问题二：缺乏跨任务的不确定性度量标准**

当前的不确定性检测是任务相关的——代码生成的置信度信号与 UI 测试的置信度信号完全不同。这使得构建通用的「不确定性分数」非常困难。

**问题三：模型仍在被训练「给出答案」**

主流 LLM 的 RLHF 训练仍然以「答案质量」为主要奖励信号。这与「在适当时机说不知道」的目标存在结构性冲突。在模型层面真正解决这个问题，可能需要新的训练范式。

---

## 结论：不确定性是 Agent 可靠性的关键缺口

Trend 4 的核心启示是：**生产级 Agent 系统的核心挑战不是让 Agent 更聪明，而是让 Agent 更知道自己什么时候不够聪明**。

这个转变将影响三个层面：

- **模型层**：需要新的训练目标来鼓励「主动承认不确定性」
- **Harness 层**：需要结构化的不确定性检测机制和 Escalation 协议
- **评估层**：需要将「知道何时求助」纳入 Agent 能力的核心评估指标

 Anthropic 的预测是：随着这些能力成熟，Agent 能够完成 20+ 步自主操作后再需要人工介入（较六个月前的数据翻倍）。但这个目标实现的前提，是行业能够系统性解决上述三个未解决问题。
