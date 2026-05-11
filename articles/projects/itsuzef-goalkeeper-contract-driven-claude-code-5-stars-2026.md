# Goalkeeper: 合约驱动的目标执行，让 Claude Code 学会「真正完成」

> **核心论点**：Goalkeeper 解决了一个根本性问题——**通过测试不等于完成任务**。它通过独立 Judge 子代理对 Definition of Done 的二次验证，填补了「验证器通过」与「真正完成」之间的质量 gap。这与 Augment Code 的「AGENTS.md 是模型升级」研究形成完美互补：AGENTS.md 定义了「做什么」，Goalkeeper 验证「做到什么程度」。

---

## 背景：验证器通过 ≠ 任务完成

OpenAI Codex `/goal` 和 Geoffrey Huntley 的 Ralph loop 都依赖验证器（编译、测试、lint）作为反馈机制。但两者有一个共同的失败模式：

> "A passing validator is not the same as a finished feature. Tests can pass on stubs. Linters can pass on `.todo`s. Codex can declare victory the moment its stop-condition string matches."

Goalkeeper 在验证器之上增加了第二个 gate：独立 Judge 对 Definition of Done 的审查。在验证器通过后，一个具有独立上下文的新子代理——不受执行代理的任何合理化影响——审查 diff 和进度日志，针对明确的完成定义进行判定，并返回结构化修复列表或批准。

---

## 核心机制：两阶段门控

```
┌─────────────────────────────────────────────┐
│  Executor Agent (Claude Code)                │
│  - 在 checkpoints 工作（logged to log.md）   │
│  - 每个 checkpoint 后运行 validator          │
└─────────────────────────────────────────────┘
                        ↓ validator passes
┌─────────────────────────────────────────────┐
│  Judge Agent (独立子代理)                    │
│  - 独立上下文，无执行 Agent 的 rationalization│
│  - 审查 diff + progress log                  │
│  - 对照 Definition of Done 判定              │
│  - ✅ 批准 → 完成                            │
│  - ❌ 拒绝 → 修复列表 → 继续工作             │
└─────────────────────────────────────────────┘
                        ↓ 5 次拒绝后
┌─────────────────────────────────────────────┐
│  Human-in-the-loop                          │
│  - 暂停，等待人类干预                        │
└─────────────────────────────────────────────┘
```

> "After your validator passes, a fresh subagent — independent context, no rationalizations from the executing agent — reviews the diff and the progress log against your written Definition of Done, and either approves or returns a structured fix-list."

---

## 与 Codex `/goal` 和 Ralph Loop 的对比

|  | OpenAI Codex `/goal` | Ralph loop | **Goalkeeper** |
|---|---|---|---|
| 跨多轮次的持久目标 | ✓ | ✓ | ✓ |
| 验证器反压 | 可选 | 核心 | 核心 |
| **独立 Judge gate 对抗显式 Definition of Done** | — | — | **核心** |
| 反占位符规则（stubs / `.todo` / `it.only` 自动拒绝） | — | 非正式 | **强制** |
| 带 Judge-gated handoff 的角色特定目标线性链 | — | — | **`/goal-chain`** |
| N 次连续拒绝后自动暂停 | — | — | **5（可配置）** |
| 每个目标仅附加 checkpoint 日志 | — | 非正式 | **强制** |
| Spec 存在于 | CLI prompt | `PROMPT.md` | `contract.md`（针对 JSON Schema 验证） |
| 区分预存验证器失败和目标导致失败 | — | — | **`validator_baseline_*`** |

---

## Contract 格式：结构化的目标定义

Contract 是 `.claude/goals/<slug>/contract.md` 中的 markdown 文件，包含 YAML frontmatter：

```yaml
---
slug: jest-to-vitest-migration
objective: 将测试套件从 Jest 迁移到 Vitest，无行为回归且测试速度可测量地提升。
non_goals:
  - 不重写测试逻辑
  - 不修改 src/ 下的源代码
definition_of_done:
  - 所有测试文件从 "vitest" 而不是 "@jest/globals" 导入
  - jest.config.* 已删除；vitest.config.ts 存在且覆盖阈值等价
  - "pnpm test" 在 Vitest 下运行完整套件，之前通过的测试 100% 仍然通过
  - 测试运行时间比 Jest 基线至少提升 20%
validator:
  command: pnpm test --run && pnpm exec node scripts/check-no-jest-refs.mjs
  success: exit_zero
  timeout_seconds: 1200
checkpoint_cadence: 每 5 次文件编辑或每 20 分钟
max_rejections: 5
judge_mode: subagent
wakeup_seconds: 270
---
## Context
<表单体 — 文件指针、约束、提示、反占位符提醒>
```

关键字段：
- **definition_of_done**：Judge 评分的依据，必须具体（「正确工作」不是 DoD）
- **non_goals**：明确超出范围的项目，Judge 在 DoD 满足时也会拒绝
- **validator_baseline_***：区分预存验证器失败和目标导致失败

---

## 反占位符保护：阻止「虚假完成」

Goalkeeper 强制执行反占位符规则，自动拒绝：
- Stubs（未实现的函数体）
- `.todo` 标记
- `it.only`（跳过的测试）
- `MAX_RUNTIME_MS = 9999 // TODO` 之类的 sentinel 占位符

> "Real reject-cycle, 3 minutes wall-clock. Goalkeeper caught a `MAX_RUNTIME_MS = 9999 // TODO` sentinel placeholder in a benchmark test where the validator passed both rounds. Round 1: validator green, judge **reject** on DoD #3 + #7 with a 3-step fix-list. Round 2: real threshold (500ms = 10x measured baseline) with justification, validator green, judge **approve**."

这是验证器无法捕捉的失败模式——测试可以通过占位符，因为断言逻辑本身没有被验证。

---

## Chain 模式：角色边界的门控

当目标跨越多个角色（后端、UI、迁移、测试）时，使用 `/goal-chain`：

```markdown
---
name: stripe-integration
---

1. stripe-api-routes      → Judge gate →
2. stripe-db-migration   → Judge gate →
3. stripe-checkout-ui    → Judge gate →
4. stripe-e2e-tests      → Done
```

每个 slug 有自己的 `contract.md`（聚焦的 DoD + 聚焦的 validator），Judge 在进入下一个角色前必须批准当前角色的完成。

**选择 Pattern A（Chain）当**：角色可序列化，一个角色的工作产出是下一个角色消耗的 artifacts。

**选择 Pattern B（`specialists:` orchestration）当**：专家必须交错在同一文件上，同时工作和同时提交（Goalkeeper v0.2 将支持）。

---

## Mission 模式：超目标迭代编排（v0.2）

Multi-goal 工作，其中每个下一个目标的形状由前一个目标的实际输出决定，Supervisor 原语位于比目标高一级：

```
Goal 完成
    ↓
Judge gate 通过
    ↓
Supervisor 读取 charter + 前一个 goal 的 artifacts
    ↓
决定：
- PROCEED → 起草下一个 goal objective → `/goal-prep` 用户审查
- DONE → Mission 完成条件满足；写入证据
- ESCALATE → 无法决定；向用户呈现具体所需输入
```

> "After a goal completes, `/goalkeeper:goal-supervisor` reads the charter + the prior goal's artifacts and decides: PROCEED / DONE / ESCALATE"

**Missions ≠ Chains**：Chains 承诺预定的线性序列；Missions 自适应——下一个 goal 的形状由前一个 goal 的实际输出决定。

---

## 与 Augment AGENTS.md 研究的关联

Augment 的研究揭示了「好配置 vs 坏配置」的惊人差异（相当于 Haiku → Opus 的质量跃升 vs 下降 30%）。Goalkeeper 的 Contract 格式本质上是一种**结构化的 AGENTS.md**——它将模糊的「做好工作」转化为：

1. **Definition of Done**：可评判的具体标准
2. **Non-goals**：明确的边界
3. **Validator**：可自动化的验证
4. **Judge**：独立的质量 gate

> 笔者认为：Goalkeeper 的真正价值在于「将人类判断封装进可复用的 Artifact」。/goal-prep 交互式地起草 contract，实际上是将人类对「什么是完成」的隐性知识转化为显式的、结构化的文档。这个过程本身就是一个高价值的知识捕获机制。

---

## 与 Cursor Bugbot 的互补

Cursor Bugbot 在 PR 层面捕获 bug（78% 解决率），Goalkeeper 在目标层面确保完成。两者解决不同层面的问题：

| 工具 | 层面 | 机制 | 效果 |
|------|------|------|------|
| Cursor Bugbot | PR review | 自然实验反馈循环 → learned rules | 78% bug 解决率 |
| Goalkeeper | Goal completion | Judge gate 对抗 Definition of Done | 阻止「虚假完成」 |

---

## 安装与使用

```bash
# 添加 marketplace 并安装
/plugin marketplace add itsuzef/goalkeeper
/plugin install goalkeeper@goalkeeper

# 别名命名空间（可选，但推荐）
# 添加到 ~/.claude/settings.json
{
  "aliases": {
    "/goal": "/goalkeeper:goal",
    "/goal-prep": "/goalkeeper:goal-prep",
    "/goal-pause": "/goalkeeper:goal-pause",
    "/goal-resume": "/goalkeeper:goal-resume",
    "/goal-clear": "/goalkeeper:goal-clear",
    "/goal-judge": "/goalkeeper:goal-judge",
    "/goal-chain": "/goalkeeper:goal-chain"
  }
}

# 开始目标
/goal-prep "Migrate the test suite from Jest to Vitest"
```

---

**引用来源**：
- [GitHub: itsuzef/goalkeeper](https://github.com/itsuzef/goalkeeper) — 合约驱动的 Claude Code 目标执行框架
- [OpenAI Codex /goal](https://developers.openai.com/codex/use-cases/follow-goals) — 持久目标执行
- [Geoffrey Huntley: Ralph loop](https://ghuntley.com/ralph/) — 验证器反压循环
- [Augment Code: A good AGENTS.md is a model upgrade](https://www.augmentcode.com/blog/how-to-write-good-agents-dot-md-files) (2026-04-22)