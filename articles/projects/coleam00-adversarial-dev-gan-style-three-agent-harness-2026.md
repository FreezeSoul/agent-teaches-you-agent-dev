# adversarial-dev：GAN 风格三代理编码 Harness 的生产级实现

> **目标用户**：有 Claude Code/Codex 使用经验的 Agent 开发工程师，想将 GAN 风格三代理架构从概念验证迁移到生产级工作流
>
> **核心价值**：把 Anthropic 2026 年 3 月工程博客中的 GAN 风格三代理架构实现为双 SDK（Claude Agent SDK + Codex SDK）可运行的工具链，让对抗反馈循环驱动每个 Sprint 的质量提升

---

## 定位破题

**一句话定义**：基于 Anthropic GAN 风格论文的生产级多代理编码 Harness，同时支持 Claude 和 Codex 双 SDK

**场景锚定**：当你需要构建完整应用（而非脚本），且对输出质量有明确要求（通过质量门控而非人工终检）时，你会想起它

**差异化标签**：`Claude SDK + Codex SDK 双支持` | `Sprint Contract 协商机制` | `JSON 结构化反馈 + 文件式通信`

---

## 体验式介绍

### GAN 架构的工程实现

adversarial-dev 的核心逻辑来自 Anthropic Labs 的 Prithvi Rajasekaran——它将生成与评估分离，让对抗压力驱动质量：

```
User Prompt (1-4 sentences)
         |
         v
   +-----------+
   |  PLANNER  |  --> writes spec.md (features, sprints, design language)
   +-----------+
         |
         v  (for each sprint)
   +---------------------+
   | CONTRACT NEGOTIATION |  Generator proposes criteria,
   | Generator <-> Eval   |  Evaluator tightens the screws,
   +---------------------+  both lock in "done"
         |
         v
   +-----------+     fail + feedback     +------------+
   | GENERATOR | <---------------------- | EVALUATOR  |
   | (build)   | ----------------------> | (attack)   |
   +-----------+     implementation      +------------+
         |                                      |
         v              pass                    |
    Next Sprint <-------------------------------+
```

每个 Sprint 有硬性通过阈值（7/10），任何维度不达标就返回 Generator 重新构建，最多 3 轮重试。

### 关键机制：Sprint Contract

在写任何代码之前，Generator 和 Evaluator 协商「完成标准」——用 JSON 定义每个维度的具体测试方式，而非模糊的「功能正常」：

```json
{
  "criterion": "PUT /frames/reorder returns 200",
  "test": "returns 200 and reorders frames in the database",
  "threshold": 7
}
```

Anthropic 在原论文中发现 **JSON contracts 优于 Markdown**，因为模型更难篡改结构化数据。这个项目直接实现了这一发现。

### 双 SDK 支持

同一个架构跑在两个 SDK 上：
- **Claude Harness**：使用 Claude Agent SDK 的 `query()` async generators
- **Codex Harness**：使用 Codex SDK 的 threads

两者共享相同的 prompts、types 和 orchestration flow，区别仅在于 SDK 特定的 agent 实现。这让架构对比变得可工程化。

---

## 拆解验证

### 技术深度

**文件式通信架构**：通过文件系统而非共享对话历史传递状态——
- `spec.md`：Planner 输出的产品规格
- `contracts/sprint-{n}.json`：每个 Sprint 的完成标准
- `feedback/sprint-{n}-round-{m}.json`：Evaluator 的详细反馈（含文件路径和行号）
- `progress.json`：Harness 状态追踪

这种设计让每个 Agent 的 context 保持专注，不会被其他 Agent 的历史污染。

**对抗压力机制**：
> "The evaluator doesn't just review code -- it's an adversary. It runs the application, probes for failures, tests edge cases the generator didn't think of, and scores each criterion on a 1-10 scale with a hard pass threshold."

Evaluator 被明确设定为「攻击者」——不是评审代码，而是主动寻找能打破 Generator 输出的方式。

**硬阈值设计**：7/10 分通过门控，每个 Criterion 独立计分，任何一项低于阈值 Sprint 即失败。这避免了「平均分过关」的模糊性。

### 社区健康度

| 指标 | 数值 |
|------|------|
| Stars | 108 |
| Language | TypeScript |
| 基础依赖 | Bun runtime |
| 认证要求 | Claude CLI + Codex CLI |

108 Stars 说明还处于早期，但架构完整度较高——不是玩具项目，是认真实现。

### 与原论文的对应

| Anthropic 论文要点 | adversarial-dev 实现 |
|-------------------|---------------------|
| 三代理（Planner/Generator/Evaluator） | ✅ 三代理独立模块 |
| Generator-evaluator 对抗反馈循环 | ✅ Evaluator 主动攻击 |
| Sprint Contract 协商 | ✅ JSON 结构化 Contract |
| 主观质量标准（Design/Originality/Craft/Functionality） | ✅ 1-10 评分 + 硬阈值 |
| Playwright MCP 端到端测试 | ⏸️ 项目未明确提及 |
| 双 SDK（Claude + Codex）| ✅ 同期实现 |

---

## 行动引导

### 快速上手

```bash
git clone https://github.com/coleam00/adversarial-dev.git
cd adversarial-dev
bun install

# Claude Harness
bun run claude-harness/index.ts "Build a personal task manager with REST API"

# 或从文件读取
bun run claude-harness/index.ts --file prompt.md
```

### 关键配置（`shared/config.ts`）

```typescript
{
  maxSprints: 10,           // 最大 Sprint 数
  maxRetriesPerSprint: 3,   // 每 Sprint 最大重试次数
  passThreshold: 7,         // 通过阈值（1-10）
  CLAUDE_MODEL: "claude-sonnet-4-6",
  CODEX_MODEL: "gpt-5.4"
}
```

### 贡献入口

适合 TypeScript 开发者，对 Agent 架构有兴趣；当前 Stars 较低，适合想参与早期项目演进的贡献者。

---

## 主题关联闭环

**Anthropic GAN-Style 三代理架构**（Article：理论/原理层）
↔
**adversarial-dev**（Project：生产级工程实现）

两者形成完美的「理论 → 工程验证」闭环：

- **Article** 解析了为什么 Generator 不能可靠评估自己（认知偏见 + 上下文污染）、为什么对抗反馈有效（外部压力逼迫走出局部最优）
- **Project** 把这个原理实现为可运行的工具链，包含完整的通信协议、配置阈值和双 SDK 支持

这一关联让读者理解「不只是知道 GAN Harness 是什么，更能看到它如何变成可用的代码」。

---

**README 原文引用**：

> "The evaluator doesn't just review code -- it's an adversary. It runs the application, probes for failures, tests edge cases the generator didn't think of, and scores each criterion on a 1-10 scale with a hard pass threshold. If any criterion fails, the sprint goes back to the generator with detailed, unforgiving feedback."
> — [coleam00/adversarial-dev README](https://github.com/coleam00/adversarial-dev)

> "This architecture is inspired by Generative Adversarial Networks (GANs), where a generator creates outputs and a discriminator tries to reject them, iterating until quality emerges from the tension between the two."
> — [coleam00/adversarial-dev README](https://github.com/coleam00/adversarial-dev)

> "As models improve, harnesses simplify. When Opus 4.5 shipped, Anthropic removed context resets from their harness because the model could maintain coherence natively."
> — [coleam00/adversarial-dev README](https://github.com/coleam00/adversarial-dev)