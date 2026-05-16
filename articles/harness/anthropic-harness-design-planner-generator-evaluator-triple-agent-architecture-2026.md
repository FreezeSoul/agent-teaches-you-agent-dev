# 三元组合架构：Anthropic 的长时 Agent Harness 设计方法论

> **来源**：[Anthropic Engineering Blog — Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（2026-03-24，Prithvi Rajasekaran）
>
> **核心论点**：长时 Agent 任务的核心瓶颈不是模型能力不足，而是**缺乏独立的 QA 机制**。通过引入 Evaluator 代理并与 Generator 解耦，可以将应用质量从「功能演示」提升到「生产可用」。当模型升级时，Harness 需要同步降级——找最简单的解决方式，不到必要时不增加复杂度。

---

## 1. 问题：为什么 Agent 自己评不好自己的工作

在长时间自主编码任务中，存在两个持续失败的模式：

**第一，上下文焦虑（Context Anxiety）**。模型在接近「自认为的上下文上限」时会提前收尾，导致任务草草完成。Anthropic 的实验发现：Claude Sonnet 4.5 对上下文窗口的焦虑足够强烈，单纯的压缩（compaction）不足以支撑长任务性能，因此 context reset（清空上下文 + 结构化交接）成为必要设计。但 reset 带来了编排复杂度、token 开销和延迟。

**第二，自我评价偏差（Self-Evaluation Bias）**。这是关键发现：

> "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."

尤其是主观任务（如设计），没有二进制测试能验证「这个布局是否足够精致」。Agent 倾向于对自己生成的内容给出偏高的评价。

但即便在有可验证结果的任务上，Agent 的判断力依然不够稳定。关键是：**把做事的 Agent 和评判的 Agent 分离开来**，效果远超让同一个 Agent 自我批评。

---

## 2. 方案：三代理架构（Planner / Generator / Evaluator）

Anthropic 构建了一个三层代理结构：

```
Planner（规划代理）
  └─ 将一句话需求扩展为完整的功能规格说明书（Spec）
      并为 Generator 提供 frontend-design skill

Generator（生成代理）
  └─ 负责实现，用代码构建功能

Evaluator（评估代理）
  └─ 使用 Playwright MCP 与运行中的应用交互
     逐条验证 Sprint Contract 中的测试条件
     写详细的缺陷报告，反馈给 Generator 进入下一轮
```

每个 Sprint 开始前，Generator 和 Evaluator 会协商一份 **Sprint Contract**——明确「完成」的定义和可测试的验收条件。这解决了产品规格过于高层、无法直接验证的问题。

Generator 提出自己的实现计划和验证方式，Evaluator 审核确认后开始编码。两者迭代直到达成一致。

### Solo Harness vs Full Harness 的关键对比

Anthropic 在同一篇文章中做了对照实验：同样的「一句话需求（Build a platform game）」，Solo Harness 直接开工，Full Harness 使用三层架构。

| 维度 | Solo Harness | Full Harness（+ Planner + Evaluator） |
|------|-------------|---------------------------------------|
| 实现结果 | 核心功能不可用（玩家无法移动） | 完整可玩，包含 sprite 编辑器、AI 生成关卡、导出分享 |
| 规划 | 无结构，直接写代码 | 16 个功能点，分布在 10 个 Sprint 中 |
| 视觉设计 | 不一致，组件堆砌 | 统一的视觉语言，设计方向贯穿始终 |
| AI 集成 | 无 | 内置 Claude 集成，通过 prompting 驱动游戏生成 |
| 质量验证 | 无 | 每 Sprint 有 27 个具体验收条件，Evaluator 逐条测试 |
| 成本 | 低 | 高（但随模型升级可降级）|

---

## 3. 核心机制：Sprint Contract 与 Evaluator 的调优

### Sprint Contract 的运作方式

Contract 不是单向文档，而是 Generator 和 Evaluator 之间的实时协商产物。例如 Sprint 3 单独有 27 个验收条件，以下是 Evaluator 发现的实际缺陷：

| Contract 条件 | Evaluator 发现 |
|--------------|----------------|
| 矩形填充工具支持拖拽填充区域 | **FAIL** — 工具只在拖拽起止点放置单块瓦片，`fillRectangle` 函数存在但未在 `mouseUp` 时正确触发 |
| 用户可选择并删除已放置的实体出生点 | **FAIL** — Delete 键处理器在 `LevelEditor.tsx:892` 要求同时有 `selection` 和 `selectedEntityId`，但点击实体只设置了 `selectedEntityId`，条件应改为 `selection \|\| (selectedEntityId && activeLayer === 'entity')` |
| 用户可通过 API 重新排序动画帧 | **FAIL** — `PUT /frames/reorder` 路由定义在 `/{frame_id}` 路由之后，FastAPI 将 `reorder` 匹配为 `frame_id` 整数导致 422 |

这些都是**真实的工程缺陷**，不是概念问题——而且是 Generator 自己漏掉的。

### Evaluator 的调优过程

> "Out of the box, Claude is a poor QA agent. In early runs, I watched it identify legitimate issues, then talk itself into deciding they weren't a big deal and approve the work anyway. It also tended to test superficially, rather than probing edge cases."

Evaluator 的 prompt 需要通过**调优循环**逐步优化：
1. 读 Evaluator 的日志
2. 找到判断与人类预期不符的例子
3. 更新 QA prompt 来修正这些问题
4. 多轮迭代后，Evaluator 的评分开始合理

即便如此，输出结果依然展示了模型 QA 能力的边界：小的布局问题、不够直观的交互、深层功能中未被发现的 bug。Anthropic 的判断是「仍有明显的验证提升空间」，但相比 Solo Run「核心功能完全不可用」，收益是显著的。

---

## 4. 迭代与降级：Harness 随模型升级而简化

这是文章中最有工程价值的方法论之一：**Harness 的复杂度应该跟随模型能力动态调整**。

Anthropic 的设计原则引用了官方博文《Building Effective Agents》：

> "Find the simplest solution possible, and only increase complexity when needed."

### 从 V1 降级到 V2 的具体路径

**第一步：移除 Sprint 构造**

Opus 4.6 带来的关键改进：
- 规划更仔细，能在更大的代码库中可靠运行
- 更好的代码审查和调试能力，能发现自己的错误
- 显著改善的长上下文检索能力

这些正是 V1 Harness 被构建来补充的能力。随着 4.6 到来，Planner 依然有价值（去掉它会导致 Generator 产出功能不够丰富的应用），但 **Sprint 分解不再必要**——模型原生就能处理连贯的长时任务。

同时，Evaluator 的角色也变了：它不再是每个 Sprint 后的强制关卡，而是「当任务超出当前模型可靠独立完成的边界时」才值得付出的成本。简单说：**任务越接近模型能力边界，Evaluator 越有价值**。

**第二步：多轮迭代的结果（DAW 示例）**

用「Build a fully featured DAW in the browser using the Web Audio API」这句话测试 V2 Harness：

| Agent & Phase | Duration | Cost |
|---------------|----------|------|
| Planner | 4.7 min | $0.46 |
| Build (Round 1) | 2 hr 7 min | $71.08 |
| QA (Round 1) | 8.8 min | $3.24 |
| Build (Round 2) | 1 hr 2 min | $36.89 |
| QA (Round 2) | 6.8 min | $3.09 |
| Build (Round 3) | 10.9 min | $5.88 |
| QA (Round 3) | 9.6 min | $4.06 |
| **Total V2 Harness** | **3 hr 50 min** | **$124.70** |

第一轮 QA 反馈揭示了典型的「AI 生成应用」问题：

> "This is a strong app with excellent design fidelity, solid AI agent, and good backend. The main failure point is Feature Completeness — while the app looks impressive and the AI integration works well, several core DAW features are display-only without interactive depth: clips can't be dragged/moved on the timeline, there are no instrument UI panels (synth knobs, drum pads), and no visual effect editors (EQ curves, compressor meters)."

第二轮 QA 继续发现：

> "Remaining gaps: Audio recording is still stub-only (button toggles but no mic capture); Clip resize by edge drag and clip split not implemented; Effect visualizations are numeric sliders, not graphical (no EQ curve)."

Generator 依然会漏掉细节或 stub 化功能，QA 在最后一公里持续贡献价值。

---

## 5. 方法论提炼：Harness 设计者的核心认知

### 认知一：每个组件都在编码你对模型能力的假设

> "Every component in a harness encodes an assumption about what the model can't do on its own, and those assumptions are worth stress testing, both because they may be incorrect, and because they can quickly go stale as models improve."

当模型升级时，第一反应应该是**重新审视现有组件**：
- 移除不再起作用的约束
- 加入之前无法实现的新能力

### 认知二：Evaluator 不是二元开关，而是连续值

> "The practical implication is that the evaluator is not a fixed yes-or-no decision. It is worth the cost when the task sits beyond what the current model does reliably solo."

任务在模型能力边界内？Evaluator 是浪费。任务超出边界？Evaluator 是核心杠杆。这个判断需要基于具体的任务特征和模型版本。

### 认知三：好设计标准要能对抗「AI 味」

Anthropic 给 Generator/Evaluator 的四个评分标准中，设计质量（Design Quality）和原创性（Originality）权重最高：

- **Originality 明确惩罚**：AI 生成的典型模式（如白色卡片上的紫色渐变）直接导致低分
- **Craft 权重低**：因为 Claude 默认就能做好，不需要额外鞭策

这与社区普遍认知相反——通常人们会把「代码能跑」当作质量信号，但 Anthropic 认为「精致感」才是更难达到的维度。

### 认知四：Criteria 的措辞直接塑造输出风格

> "Including phrases like 'the best designs are museum quality' pushed designs toward a particular visual convergence, suggesting that the prompting associated with the criteria directly shaped the character of the output."

Evaluator 的 system prompt 不仅是评分规则，更是**方向引导**。选择什么样的描述词，决定了模型收敛到什么样的输出分布。

---

## 6. 对 Agent 工程实践的启示

### 何时用三元架构

三层架构（Planner/Generator/Evaluator）适合：
- 任务周期超过 1 小时
- 有明确的可验证验收条件（功能测试、UI 交互）
- 应用质量要求生产级（不只是 demo）
- 愿意投入前期调优成本换取稳定产出

不适合：
- 快速探索性任务（原型、一次性脚本）
- 任务边界本身不清晰，无法写 Contract
- 评测成本远超任务价值的小任务

### 降级策略

随着模型能力提升，Harness 的自然演化路径是：

```
V1: Planner + Generator(多Sprint) + Evaluator(每Sprint后)
    ↓ 模型能力提升
V2: Planner + Generator(无Sprint) + Evaluator(仅在超出边界时)
    ↓ 模型继续提升
V3: 单一 Generator + 按需调用 Evaluator
    ↓ 最终
V0: 裸模型
```

但这不是线性递减——当模型能可靠完成更多任务时，**Harness 的边界会外扩**，可以尝试之前无法实现的更复杂目标。

### 关键工程指标

从 DAW 示例提炼的实际数字：
- **成本**：$124.70 / 完整 DAW（3h50min）
- **轮次**：3 轮 Build+QA（每轮 2~3 小时）
- **效率**：大部分时间（$71+$37=$108）用于 Build，QA 只占 ~$14
- **缺陷发现**：每轮 QA 都发现「stub 功能」问题（音频录制、拖拽、EQ 可视化）

---

## 结语

这篇文章的本质不是「Claude 代码能力测试」，而是** Harness 工程的方法论输出**。

Anthropic 验证的核心命题：

1. **解耦是关键**：Generator 和 Evaluator 不分离，QA 质量就无法达标
2. **假设需要压力测试**：每个 harness 组件都编码了对模型能力的假设，模型升级时必须重新审视
3. **简单性优先**：不要在模型能做到的事情上浪费 harness 复杂度
4. **模型改进不等于 harness 简化**：模型变强后，Harness 可以尝试更复杂的目标，而不是变得更简单

> "The space of interesting harness combinations doesn't shrink as models improve. Instead, it moves, and the interesting work for AI engineers is to keep finding the next novel combination."

---

**引用来源**

- [Harness design for long-running application development — Anthropic Engineering Blog](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Building Effective Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [Effective harnesses for long-running agents — Anthropic Engineering Blog](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)