# beenuar/AiSOC：开源 AI SOC 的决策 Ledger 与公开评测 Harness

> **这篇文章推荐什么**：AiSOC 是一个 MIT 许可、自托管的 AI 安全运营中心，其核心差异化在于**每一步决策都有可回放的操作日志**，且**评测 Harness 在 CI 中对所有 PR 生效**。791 Stars（2026-05-02 创建，11 天），Python，LangGraph 多 Agent 编排，MITRE ATT&CK 推理。

---

## TRIP 四要素

| 要素 | 内容 |
|------|------|
| **T - Target** | 安全工程师 / SOC 分析师 / 企业安全团队，评估 AI SOC 产品或需要开源可审计的安全 Agent 基础设施 |
| **R - Result** | 791 Stars（11 天），v7.1.0（2026-05-10），55 种攻击模板，14 种日志源，≥50:1 告警-事件比率（CI 验证） |
| **I - Insight** | 将 Agent 的每次工具调用、每次推理、每次决策都写入 **Investigation Ledger**，而非黑箱 API 调用——可重放、可审计、可修复 |
| **P - Proof** | MIT 许可，完全自托管，公开的 CI-gated 评测 Harness，每次 PR 都跑 200 事件合成数据集，无 API key 可复现结果 |

---

## P - Positioning（定位破题）

### 一句话定义

**开源 AI SOC 平台**：用 LangGraph 多 Agent 推理安全事件，每步决策写入可重放 Ledger，MIT 许可，自托管。

### 场景锚定

什么情况下你会想起它：
- 评估 AI SOC 产品时，想知道"供应商的 Agent 到底做了什么"但供应商不给你看
- 需要一个生产级 SOC 基础设施，但不想把数据交给云厂商
- 想在 IDE 里（Claude/Cursor/Cody）直接查询 SOC 告警和调查进度
- 想用公开的评测 Harness 验证你的 Agent SOC 实现是否达标

### 差异化标签

**最透明**：没有哪家闭源 AI SOC 厂商会给你看每一步推理。Investigation Ledger 把这个黑箱打开了。

---

## S - Sensation（体验式介绍）

### 核心体验：从黑箱到透明

用 AiSOC 的典型场景：

1. **告警来了** → AiSOC 的 Fusion 引擎对告警打分、关联、衰减风险点
2. **Agent 开始调查** → 它调用工具、推理、决策，每一步都写入 Investigation Ledger
3. **你随时回放** → 打开 `/cases/INC-XXX?tab=ledger`，看 Agent 第一分钟做了什么、第三分钟做了什么决策、为什么拒绝某个 action
4. **发现错误** → 一键反馈 `false_positive` / `true_positive`，闭环修正

**哇时刻**：当你看到 AI 在第三步"认为这是一个 credential exploration 攻击，block"，然后在 Ledger 里清楚地看到它搜索了哪些环境变量、找到了什么、为什么判断这不是正常业务行为——这种透明性在闭源产品里根本不可能看到。

### 多端集成

AiSOC 的 MCP server 让分析师在 IDE 里就能操作：

```bash
npx -y @aisoc/mcp install --host claude \
  --aisoc-url https://aisoc.your-company.com \
  --api-key aisoc_pat_xxxxxxxxxxxx
```

然后可以在 Claude/Cursor 里调用 `aisoc_list_alerts`、`aisoc_run_investigation`、`aisoc_replay_decision`。这是**把 SOC 的能力集成到开发者日常工具**的工程实现。

---

## E - Evidence（拆解验证）

### 技术深度：LangGraph orchestrator 的工程实现

> "The orchestrator is a ~600-line LangGraph in `services/agents/`. It is small enough to read end-to-end, swap models in, and patch."
> — [AiSOC GitHub README](https://github.com/beenuar/AiSOC)

600 行代码的 LangGraph，这个规模是精心设计的——足够复杂到能处理真实 SOC 场景，又足够简单到能完全理解和修改。这是真正符合"生产级可维护"原则的实现。

**三层 Agent Memory 架构**：
- Session（进程内 LRU）
- Working（Redis 后备，24h TTL）
- Institutional（PostgreSQL + pgvector，永久）

### 公开评测 Harness：每个数字可复现

> "We don't have to take our word for it. From a fresh clone: `python3 scripts/run_evals.py` — no Docker, no API key, no GPU, no LLM."
> — [AiSOC Benchmark Page](https://github.com/beenuar/AiSOC/blob/main/apps/docs/docs/benchmark.md)

AiSOC 的评测体系是整个项目的工程亮点：

| Suite | Metric | Per-case | Per-template macro | Target |
|-------|--------|----------|-------------------|--------|
| Alert reduction ratio | reduction | 75.3% | _n/a_ | ≥70% |
| MITRE ATT&CK tactic accuracy | accuracy | 97.0% | 96.4% (n=55) | ≥80% |
| Investigation completeness | mean keyword coverage | 94.2% | 94.3% (n=55) | ≥85% |
| Response-plan quality | mean rubric score | 1.000 | 1.000 (n=55) | ≥0.80 |
| Playbook completion rate | completion rate | 50.5% | 100% H/C | ≥50% |

**Per-template macro** 是关键设计：200 个事件从 55 个模板生成，单个模板的回归只会移动 ~0.5% 的 per-case 均值，但移动 ~1.8% 的 per-template macro。这是防止"数据稀释"的统计设计。

### 社区健康度

- **Stars**：791（2026-05-02 创建，11 天）
- **License**：MIT（完全开放）
- **版本**：v7.1.0（2026-05-10），说明活跃维护
- **v7.0 发布**：16 个 workstreams，包括 Slack ChatOps、PDF 报告、MSSP 控制台、WCAG AA 无障碍

---

## T - Threshold（行动引导）

### 快速上手（3 步）

**方式一：60 秒 demo（无需 Docker）**
```bash
curl -fsSL https://raw.githubusercontent.com/beenuar/AiSOC/main/install.sh | bash
```
覆盖 Ubuntu/Debian/Fedora/Arch/Alpine/macOS/Windows。

**方式二：Docker Compose（本地，3.5 分钟）**
```bash
git clone https://github.com/beenuar/AiSOC.git && cd AiSOC && pnpm aisoc:demo
```

**方式三：Render 一键部署**
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/beenuar/AiSOC)

### 适合的场景

- 需要**可审计的 AI 安全决策**：金融、医疗、合规敏感行业
- 想**对比评估 AI SOC 产品**：用 AiSOC 的 harness 作为基准
- 需要**自托管**（不能数据外传的合规要求）

### 不适合的场景

- 想要开箱即用的纯 SaaS体验（AiSOC 需要自运维）
- 只需要简单告警，不需要 Agent 调查能力

---

## 与 Articles 主题的关联

本文推荐 AiSOC，与上一轮 Articles（Anthropic April Postmortem 复合效应分析）形成以下互补关系：

| Articles 洞察 | AiSOC 实证 |
|-------------|-----------|
| 配置变更的复合效应难以追踪 | **Investigation Ledger** 将 Agent 每步决策显式化，追踪"哪个推理步骤出了问题" |
| "足够好"的环境是 RL 训练的前提 | SOC 场景中**可验证的环境**（已知攻击模板 + backing telemetry）是 Agent 推理的前提 |
| Harness 是系统可靠性的保障 | **公开 CI-gated eval harness** 是 SOC Agent 的质量门禁 |

> 笔者的判断：Anthropic 的 April Postmortem 揭示了"复合效应导致难以追踪的质量退化"，而 AiSOC 的 Investigation Ledger 是这个问题在 SOC 场景下的具体解决方案——**不是减少变更，而是让变更的影响可追踪**。这个思路对任何构建 Agent 系统的工程师都有参考价值。