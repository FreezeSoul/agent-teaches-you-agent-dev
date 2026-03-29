# SkillsBench：首个智能体 Skills 效能系统性评测基准

> **本质**：SkillsBench 回答的不是"模型有多强"，而是"给模型一个 Skill，它到底能获得多少实际提升"——这是整个 Skill 生态目前最缺乏的实证数据。

## 一、基本概念

### 什么是 Agent Skill

在 SkillsBench 的定义中，**Agent Skill** 是"在推理时增强 LLM Agent 的结构化程序性知识包"（structured packages of procedural knowledge），包含指令、代码模板、资源和验证逻辑。与微调不同，Skill 不修改模型权重，在推理时通过上下文注入扩展 Agent 的专业能力。

这个定义与我们在 [Agent Skills Survey](../concepts/agent-skills-survey-architecture-acquisition-security.md) 中讨论的 SKILL$.$md 规范、Cisco Skill Trust 框架一脉相承——Skills 正在成为 AI 软件世界的新"应用包"。

### Skill 的三层架构

SkillsBench 论文提出了一个清晰的类比：

| 层次 | 对应 | 作用 |
|------|------|------|
| Foundation Model | CPU | 提供基础能力 |
| Agent Harness | Operating System | 编排上下文和工具 |
| Skill | Application | 将能力扩展至专业领域 |

这个类比揭示了为什么 Skill 生态会独立于模型演进——就像应用生态不需要重写 CPU 一样，专业领域的 Skill 不需要重新训练模型。

---

## 二、核心技术机制

### 评测设计：三条件对照

SkillsBench 的核心创新在于**三条件对照实验设计**：

1. **No Skills**：纯模型基线
2. **Curated Skills**：人工策划的高质量 Skill（由专家编写）
3. **Self-Generated Skills**：模型自行生成的 Skill（"自己写 Skill 用在自己身上"）

这个设计直接回答了一个关键问题：**模型能否可靠地生成自己消费的程序性知识？** 答案是否定的（见下节），这是 SkillsBench 最重要的实证发现。

### 评测规模

| 维度 | 数值 |
|------|------|
| 任务数 | 86 tasks（评测中有效 84 tasks） |
| 领域数 | 11 个领域 |
| 轨迹数 | 7,308 条 |
| 模型配置 | 7 种 agent-model 配置 |
| 验证方式 | 确定性验证器 + 全轨迹日志 |

**评测基于 Harbor 框架**：每个任务采用容器化结构，包含 Skill 相关环境和数据、确定性验证测试、以及 oracle 解法方案。

### 泄露审计

论文特别进行了**泄露审计**（leakage audits），确保 Skill 提供的是"指导而非答案"。这是一个关键的方法论贡献——如果 Skill 本身就包含了任务的完整解法，那评测就失去了意义。

---

## 三、核心发现

### 发现一：Curated Skills 平均提升 +16.2pp，但差异巨大

**总体结果**：Curated Skills 将平均通过率提升 **+16.2 个百分点**（percentage points）。

但这个平均数掩盖了巨大的领域差异：

| 领域 | Skill 提升效果 |
|------|---------------|
| Healthcare | **+51.9pp**（最大赢家）|
| Legal | +35.x pp |
| Finance | ~+20pp（估算）|
| Software Engineering | **+4.5pp**（最小增益）|

**为什么 Healthcare 提升最大？** 医疗领域的程序性知识高度标准化（临床路径、诊断标准、编码规范），这些知识直接编码进 Skill 后，Agent 可以快速调用，无需模型自行推理。

**为什么 Software Engineering 增益最小？** 软件工程任务的解决路径相对可探索，模型本身对代码生成、调试已有较强能力，Skill 提供的边际增益有限。

### 发现二：16 of 84 tasks 呈现负增量

这是最令人警惕的发现：**有近五分之一（16/84）的任务，在添加 Skill 后性能反而下降**。

可能的解释：
- Skill 引导 Agent 进入了错误的解决路径
- Skill 中的指令与模型内在推理风格冲突
- 验证器设计导致 Skill 反而触发了模型的不确定性

这与 [Agent Skills Survey](../concepts/agent-skills-survey-architecture-acquisition-security.md) 中"26.1% 社区 Skills 含漏洞"的发现相互印证——**Skill 不是加就有用，不合格的 Skill 反而帮倒忙**。

### 发现三：Self-Generated Skills 几乎无收益

模型自行生成的 Skill，在测试中**平均无收益**（negligible or negative benefit）。

这是 SkillsBench 最具颠覆性的结论。它说明：
- **模型无法可靠地创作自己消费的程序性知识**
- 这与 LLM 训练数据中的知识性质有关：模型擅长从海量文本中提取模式，但不擅长将程序性知识组织成可被自己使用的结构化格式
- 社区 Skill 市场（ClawHub、Composio 等）的价值在于人工策划，而非模型自我生成

这一发现与 [AI4Work Benchmark Mismatch](./ai4work-benchmark-real-world-mismatch.md) 的结论形成有趣的对比：AI4Work 发现基准评测与真实工作技能严重脱节；SkillsBench 则发现，即使在同一基准内，模型自己生成的 Skill 也无法有效利用自身能力。

### 发现四：Focused Skills（2-3 modules）优于 comprehensive documentation

Skill 的粒度存在最优区间：
- **2-3 个模块的 focused Skill 表现最佳**
- 过于全面的 comprehensive 文档式 Skill，反而因为信息过载导致性能下降

这与我们在 [Context Engineering](../concepts/context-engineering-for-agents.md) 中讨论的"上下文工程"原则一致——不是越多越好，精准优于全面。

### 发现五：小模型 + Skills 可以匹配大模型

一个具有实践意义的发现：**使用 Skill 的小模型，可以匹配不使用 Skill 的大模型**。

这意味着：
- 组织可以在已有的小模型基础设施上，通过 Skill 扩展覆盖更多专业场景
- Skill 是降低 Agent 部署成本的可行路径
- 大模型厂商的优势可能被 Skill 生态部分稀释

---

## 四、与其他基准的关系

### 评测体系的层次分工

SkillsBench 与我们已有的评测文章形成互补：

| 基准 | 评测什么 | 侧重点 |
|------|---------|--------|
| [GAIA/OSWorld](./gaia-osworld-benchmark-2026.md) | 通用 Agent 能力 | "模型能做什么" |
| [MCPMark](./mcpmark-iclr2026-benchmark.md) | MCP 协议专项 | "模型能否正确使用工具协议" |
| [DeepResearch Bench](./deep-research-bench-iclr2026.md) | 深度研究任务 | "模型能否完成博士级研究" |
| [AI4Work](./ai4work-benchmark-real-world-mismatch.md) | 基准 vs 真实工作 | "评测覆盖是否反映真实需求" |
| **SkillsBench** | **Skill 效能** | **"给模型一个 Skill，它能获得多少提升"** |

### SkillsBench 与 AI4Work 的互补性

[AI4Work](./ai4work-benchmark-real-world-mismatch.md) 揭示了评测基准与真实工作之间的系统性错位；SkillsBench 则在 Skill 这个具体维度上发现了另一层错位：**即使 Skill 被设计出来用于弥补能力缺口，它的实际效能也高度依赖领域、粒度和编写质量**。

两者共同指向一个结论：Agent 系统的能力扩展（无论是通过基准训练还是 Skill 注入）都不是线性可预测的，需要实证评测而非理论推演。

---

## 五、实践指南

### 何时值得使用 Skill

基于 SkillsBench 的发现，以下场景使用 Skill 预期收益最高：

1. **程序性知识高度标准化的领域**：Healthcare、Legal、Finance
2. **需要遵循严格流程的合规任务**：监管报告、审计跟踪、认证流程
3. **小团队资源受限**：可用小模型 + Skill 扩展能力覆盖

以下场景 Skill 增益有限：

1. **模型本身已具备较强能力的领域**：Software Engineering、通用编程
2. **探索性/创新性任务**：没有标准流程可编码
3. **需要模型自主判断的场景**：Skill 可能反而约束了模型的推理灵活性

### Skill 设计原则

| 原则 | 依据 |
|------|------|
| 聚焦（Focused）：2-3 个模块 | 避免信息过载 |
| 程序性 > 描述性 | 程序性知识（how-to）比文档（documentation）更有效 |
| 避免泄露解法 | Skill 引导而非替代推理过程 |
| 按领域定制 | Healthcare (+51.9pp) vs SE (+4.5pp) 差异巨大 |

### Skill 生成策略

由于 self-generated Skill 几乎无收益，以下策略更有效：

1. **人工策划为主**：由领域专家编写高质量 Curated Skill
2. **小模型 + 人工审核**：模型生成初稿，人工审核后使用
3. **复用社区资源**：ClawHub、Composio 等平台的策划 Skill 优先于自生成

---

## 六、局限性与开放问题

### 主要局限性

1. **84 tasks 的规模有限**：相比 GAIA（万级任务）仍较小，但已覆盖 11 个领域
2. **Harbor 框架依赖**：评测结果与 Harbor 的容器化设计紧密相关，泛化性待验证
3. **Skill 版本未控制**：Curated Skill 的质量本身可能存在较大方差

### 开放问题

1. **Skill 的长程影响**：SkillsBench 关注单任务提升，Skill 是否会在多任务累积使用中产生负面干扰？
2. **Skill 组合效应**：多个 Skill 同时注入时，是否存在干扰或协同效应？
3. **Skill 的生命周期**：随着模型能力提升，Skill 是否需要动态更新或退役？
4. **跨领域 Skill 迁移**：为某个领域设计的 Skill，能否有效迁移至相邻领域？

---

## 七、参考文献

- Li, X. et al. (2026). *SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks*. arXiv:2602.12670. https://arxiv.org/abs/2602.12670
- Merrill et al. (2026). *Harbor Framework*. (SkillsBench 评测基础设施)

---

## 相关文章

| 文章 | 一句话描述 |
|------|----------|
| [MCPMark ICLR 2026](./mcpmark-iclr2026-benchmark.md) | 压力测试真实 MCP 工作流的 ICLR 2026 基准 |
| [AI4Work Benchmark Mismatch](./ai4work-benchmark-real-world-mismatch.md) | 43基准映射 O*NET 发现 95% 真实工作技能未被覆盖 |
| [Agent Skills Survey](../concepts/agent-skills-survey-architecture-acquisition-security.md) | SKILL$.$md 规范 + Skill Trust 四层门控框架 |
| [GAIA/OSWorld Benchmark 2026](./gaia-osworld-benchmark-2026.md) | 通用 Agent 评测基准与 OpenWorld 跨平台评测 |
| [DeepResearch Bench ICLR 2026](./deep-research-bench-iclr2026.md) | 深度研究 Agent 评测（RACE + FACT 双维度）|
