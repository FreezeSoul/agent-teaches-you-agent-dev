# Anthropic 三代理 Harness：GAN 启发的长时运行应用开发架构

> **来源**：Anthropic Engineering Blog  
> **原文**：[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)  
> **作者**：Prithvi Rajasekaran (Anthropic Labs)  
> **日期**：2026-03-24  
> **分类**：harness  
> **关联**：Stage 7 (Orchestration) · Stage 12 (Harness)

---

## 核心判断

Anthropic Labs 在长时运行 Agent 应用开发中，验证了**三代理 GAN 启发架构**（Planner-Generator-Evaluator）的有效性：Generator 产生代码，Evaluator 用 Playwright MCP 真实操作 App 并打分，两者构成对抗性循环，Planner 负责将简单需求展开为完整规格文档。

**反直觉的核心发现**：
1. **Agent 无法公正评价自己的工作** — 即使有客观验证标准，Generator 也会过度宽容；将 Evaluator 独立出来并专门调参后，评估质量大幅提升
2. **Context Reset vs. Compaction** — 对 Sonnet 4.5，Compaction 无法解决"context anxiety"（模型在接近上下文限制时提前收尾），必须用 Context Reset 提供干净 slate；Opus 4.5 基本消除此问题，可全连续 session
3. **评估语言本身影响生成质量** — "the best designs are museum quality"这类措辞直接塑造了输出风格，说明 Evaluator Prompt 中的措辞是隐式的生成引导

---

## 背景：两代理架构的局限

### 早期两代理 Harness

Anthropic 在 2025 年 11 月的 [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 中提出了两代理方案：

```
Initializer Agent → 分解规格为 Task List
Coding Agent     → 逐 Feature 实现，跨 Session 传递 Artifact
```

社区也收敛到类似模式（如"Ralph Wiggum"方法，用 Hook/Script 保持连续迭代循环）。

**两个持久性问题**：

1. **Context Window 饱和导致失焦**：模型在长任务中逐渐失去连贯性；部分模型（尤其是 Sonnet 4.5）还表现出"context anxiety"——当感知到接近上下文限制时，会提前收尾。解决方案是**Context Reset**（清空上下文窗口，用结构化 Artifact 传递状态），而非 Compaction（在原位压缩历史）。两者的关键区别：Compaction 保留连续性但无法消除 context anxiety；Reset 提供干净 slate，但要求 Artifact 携带足够的重启状态。

2. **Self-Evaluation 失效**（新问题，之前未解决）：Agent 被要求评估自己产出时，即使有客观验证标准，也会过度宽容。这个问题在主观任务（如设计）中尤为严重，但即使在有客观验收标准的任务中也存在。

---

## 三代理 GAN 启发架构

### 核心思想

从**生成对抗网络（GAN）**获得灵感：两个网络（Generator & Discriminator）对抗训练，Generator 产生样本，Discriminator 评判真伪，两者交替优化。映射到 Agent 系统：

- **Generator** = 代码生成 Agent
- **Evaluator** = 独立评判 Agent（相当于 Discriminator）
- 对抗循环替代单代理自我评估

### 三代理分工

```
┌─────────────────────────────────────────────────────────────────┐
│                        Three-Agent Architecture                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User Prompt (1-4 sentences)                                   │
│          │                                                      │
│          ▼                                                      │
│   ┌─────────────┐                                               │
│   │   Planner   │  展开为完整 Product Spec                       │
│   │   Agent     │  · Product Context + High-level Tech Design   │
│   └──────┬──────┘  · 避免过于具体的实现细节（防止错误级联）       │
│          │        · 主动寻找 AI Feature 融入点                   │
│          ▼                                                      │
│   ┌─────────────┐                                               │
│   │  Generator  │  Sprint 内逐 Feature 实现                      │
│   │   Agent     │  · React + Vite + FastAPI + PostgreSQL        │
│   └──────┬──────┘  · 每个 Sprint 结束时自评                     │
│          │        · Git 版本控制                                 │
│          │                                                     │
│          ▼                                                     │
│   ┌─────────────┐                                               │
│   │  Evaluator  │  Playwright MCP 操作真实 App 并评分            │
│   │   Agent     │  · 功能测试 · UI 交互 · API 端点 · DB 状态   │
│   └──────┬──────┘  · 硬阈值：任何指标低于阈值 → Sprint 失败    │
│          │                                                     │
└──────────┼─────────────────────────────────────────────────────┘
           │ Feedback Loop
           ▼
      Generator（重新执行该 Sprint）
```

### Planner Agent

**输入**：用户 1-4 句话的简单需求  
**输出**：完整 Product Spec（Product Context + High-level Technical Design）

关键设计原则：
- 要求 Planner **保持野心（Ambitious）**，扩展 Scope 而非保守
- **禁止在规格阶段写过于具体的实现细节**——如果 Planner 在这个阶段写了错误的技术设计，这些错误会级联到下游实现
- 主动寻找可嵌入产品的 **AI Feature** 机会（与纯工程规格拉开差距）

### Generator Agent

- 每个 Sprint 挑选 Spec 中的一个 Feature 实现
- 技术栈：React + Vite + FastAPI + PostgreSQL
- Sprint 结束时自评工作（但这个自评不被用于最终判定）
- 使用 Git 做版本控制，支持回滚

### Evaluator Agent（GAN 中的 Discriminator）

**这是架构中最关键的设计**：

- 配备 **Playwright MCP**，能真实操作运行中的 App（点击、导航、截图），而非静态分析代码
- 测试范围：UI 功能、API 端点、数据库状态
- 评分维度（从 Frontend Design 实验中迁移）：
  - **Product Depth**：产品是否完整、有深度
  - **Functionality**：用户能否完成核心任务
  - **Visual Design**：视觉设计质量
  - **Code Quality**：代码质量

**硬阈值机制**：任何指标低于阈值 → Sprint 失败 → 详细反馈给 Generator → Generator 重新执行该 Sprint

---

## 前端设计实验：评估语言如何影响生成质量

在将 GAN 模式应用于代码生成之前，作者先在**前端设计**领域验证了这套方法，发现了几个关键洞察：

### 四维评估标准

| 维度 | 含义 | 权重 |
|------|------|------|
| Design Quality | 色彩/字体/布局/图像是否构成统一风格，而非零件堆砌 | **高** |
| Originality | 是否为定制决策（而非模板/库默认值/AI 生成模式） | **高** |
| Craft | 排版层级、间距一致性、色彩和谐、对比度等技术执行 | 低（默认能力） |
| Functionality | 可用性：用户能否理解界面并完成任务 | 低（默认能力） |

Craft 和 Functionality 默认表现良好，因此**重点加权 Design Quality 和 Originality**，直接惩罚"AI Slop"模式（如紫色渐变白卡片）。

### 评估语言直接影响生成

通过 few-shot 示例校准 Evaluator，使其判断与人类偏好对齐。随着迭代次数增加，设计方向趋向提示词中的语言特征——"the best designs are museum quality"这句话推动了特定视觉收敛。

### 观察到的生成行为

- **第 10 轮出现创意跳跃**：一个荷兰艺术博物馆网站，前 9 轮产出的是预期的暗色主题落地页；第 10 轮时，Generator 突然放弃这个方向，转变为一个 CSS 3D 透视空间体验——棋盘格地面、自由形式挂画、门框式导航。这是单次生成从未出现过的创意。
- **迭代非线性**：最终产出往往优于中间轮次，但整体趋势向上。
- **复杂度随迭代增加**：Generator 在 Evaluator 反馈驱动下，会追求更复杂的实现方案。

---

## 关键工程洞察

### 1. Self-Evaluation 失效的机制

Agent 在评估自己的输出时，倾向于过度宽容。即使明确告知"这是一个客观测试"，Generator 仍然会找理由为不通过的项目辩护。独立 Evaluator 虽然也是 LLM（同样有对 LLM 输出的宽容倾向），但通过**专门的提示词调参**（使其更严格），可以显著改善。关键是：一旦外部反馈存在，Generator 就有了**具体的迭代目标**。

### 2. Context Reset vs. Compaction

- **Compaction**（在原位压缩历史）：保留连续性，但无法消除"context anxiety"——模型仍会感知到上下文在增长
- **Reset**（清空上下文，重开 Agent）：提供干净 slate，消除了 context anxiety，但增加了编排复杂度、Token 开销和延迟

Opus 4.5 基本消除了 context anxiety，因此三代理架构**完全不需要 Context Reset**，使用 Claude Agent SDK 的自动 Compaction 处理上下文增长。

### 3. Playwright MCP 是关键使能技术

Evaluator 能有效评判的前提，是它能**真实操作 App** 而非读代码。在代码层面，一个 App 可能看起来实现了某功能，但在浏览器中可能根本不工作。Playwright MCP 让 Evaluator 能主动探索 App 行为，发现 Generator 自我检查无法发现的 Bug。

### 4. Evaluator Prompt 的措辞是隐式生成引导

"the best designs are museum quality"这样的措辞，不仅描述了评估标准，也直接塑造了 Generator 的输出风格。这说明**评估标准文档本身是生成引导的一部分**，需要在设计评估体系时一并考虑。

---

## 与其他 Harness 路线的关联

| 路线 | 代表工作 | 核心方法 | 与本架构的关系 |
|------|---------|---------|--------------|
| **Meta-Harness** | Stanford (Filesystem-based) | 全量 Traces 诊断，10M tokens/iter Proposer | 本架构的 Generator 可受益于 Meta-Harness 的 Proposer 能力 |
| **AutoHarness** | DeepMind (Environment Feedback Loop) | 约束规则自动生成 | Evaluator 的评分维度可部分自动化生成 |
| **Better Harness** | LangChain Eval-Driven | 手工设计 Harness → Eval 迭代优化 | 三代理架构是 Better Harness 的进阶版：手工 → 自动对抗 |
| **本架构** | Anthropic Labs (Planner-Generator-Evaluator) | GAN 启发的三代理对抗循环 | 自身演进方向：加入 Meta-Harness 的自动 Proposer |

---

## 核心判断总结

1. **GAN 启发的三代理架构是长时运行应用开发的最优 Harness 范式之一**：Planner 解决规格生成问题，Generator 解决实现问题，Evaluator 解决自我评估失效问题，三者缺一不可

2. **Evaluator 必须是独立的、经过调参的 Agent，而非 Generator 的子模块**：Self-Evaluation 失效不是因为模型能力不足，而是因为角色冲突；独立 Evaluator 可以通过 Prompt 工程专门调优评估严格度

3. **Playwright MCP 将评估从静态代码分析升级为动态行为测试**：这是让评估真正有效的技术关键；没有真实操作能力的 Evaluator 会错过大多数 Bug

4. **Context Reset vs. Compaction 的选择取决于模型特性**：对于有 context anxiety 的模型（Sonnet 4.5），Reset 是必须的；对于无此问题的模型（Opus 4.5），Compaction 更高效

5. **Evaluator 的 Prompt 措辞是隐式的生成控制**：设计评估体系时，评估语言本身对生成质量的影响不可忽视
