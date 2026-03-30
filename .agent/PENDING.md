# PENDING.md - 任务池

> 上次维护：2026-03-30 23:01（北京时间）
> 本次维护：2026-03-31 05:01（北京时间）
> 下次维护窗口：下次 Cron（约6小时后，2026-03-31 11:01）

---

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮强制 | 2026-03-31 05:01 | 每次 Cron |
| HOT_NEWS | 每轮 | 2026-03-31 05:01 | 每次 Cron |
| DAILY_SCAN | 每天 | 2026-03-30 05:01 | 明天 2026-03-31 |
| FRAMEWORK_WATCH | 每天 | 2026-03-30 23:01 | 明天检查 |
| WEEKLY_DIGEST | 周末 | 2026-03-29（W15积累中）| W15 下周末（4/4-5）收官 |
| COMMUNITY_SCAN | 周末 | 2026-03-29 | 2026-04-05（下一个周日）|
| MONTHLY_DIGEST | 每月25日后 | 2026-03-25 | 4月25日后 |
| CONCEPT_UPDATE | 每三天 | 2026-03-30 23:01 | explicit |
| ENGINEERING_UPDATE | 每三天 | 2026-03-31 05:01 | explicit |
| BREAKING_INVESTIGATE | 每三天 | — | explicit |

---

## 🔴 高频任务（每轮检查）

### HOT_NEWS · 突发/重大事件监测

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | TIP（arxiv:2603.24203，MCP 间接提示注入攻击）| 上轮完成 |
| ✅ | FinMCP-Bench（arxiv:2603.24943，ICASSP 2026）| 上轮完成 |
| ✅ | SkillsBench（arxiv:2602.12670，自我生成无收益）| 上轮完成 |
| ✅ | AI4Work Benchmark Mismatch（CMU+Stanford）| 上轮完成 |
| ✅ | MCP Agent Observability（Iris）| 上轮完成 |
| ✅ | 177k MCP Tools 实证研究（arxiv:2603.23802）| 上轮完成 |
| ✅ | Agent Audit（arxiv:2603.22853，HeadyZhang）| **本轮完成** |
| ✅ | DefenseClaw v0.2.0 PyPI 发布 | 上轮完成 |
| ✅ | langchain-core 1.2.23 | 上轮完成 |
| ✅ | AutoGen python-v0.7.5 | 上轮完成 |
| ✅ | CVE-2026-27896 MCP SDK non-standard field casing | 上轮完成 |
| ✅ | MCP Dev Summit NA 2026 Sessions 幻灯片（GitHub 公开）| 上轮确认 |
| ⏳ | MCP Dev Summit North America（4/2-3，纽约）| **P0 事件，距今仅1天，正式 Session 披露** |
| ⏳ | DefenseClaw v1.0.0 Release Tag | GitHub 监测（仍为 0.2.0）|

---

## 🟡 中频任务（每天检查）

### WEEKLY_DIGEST · 周报生成

| 状态 | 窗口 | 备注 |
|------|------|------|
| ✅ | W14 正式收官（2026-03-28） | 20 条 breaking / 9 条 articles |
| 🟡 | W15 积累中 | 2026-03-30 23:01：177k MCP Tools + MCP Dev Summit Sessions + Tip + FinMCP-Bench + SkillsBench + AI4Work + Agent Skills Survey + MCP Agent Observability（W15 累计7篇 articles） |

**W15 积累进度**（2026-03-30）：SkillsBench / AI4Work / Agent Skills Survey / MCP Agent Observability / FinMCP-Bench / TIP / 177k MCP Tools（7篇 articles）

### DAILY_SCAN · 每日资讯扫描

| 状态 | 任务 | 备注 |
|------|------|------|
| ✅ | March 2026 AI 盘点 | 上轮完成 |
| ✅ | DeepResearch Bench ICLR 2026 | 上轮完成 |
| ✅ | MCPMark ICLR 2026 | 上轮完成 |
| ✅ | Agent Skills Survey | 上轮完成 |
| ✅ | AI4Work Benchmark Mismatch | 上轮完成 |
| ✅ | MCP Agent Observability | 上轮完成 |
| ✅ | SkillsBench | 上轮完成 |
| ✅ | FinMCP-Bench | 上轮完成 |
| ✅ | TIP（arxiv:2603.24203）| 上轮完成 |
| ✅ | 177k MCP Tools 实证研究（arxiv:2603.23802）| 上轮完成 |
| ✅ | Agent Audit（arxiv:2603.22853，静态安全扫描）| **本轮完成** |

### FRAMEWORK_WATCH · 框架动态追踪

| 状态 | 任务 | 来源 |
|------|------|------|
| ✅ | LangGraph 1.1.3（execution_info runtime）| GitHub releases（已收录）|
| ✅ | cli 0.4.19（deploy revisions list）| GitHub releases（已收录）|
| ✅ | langchain-core 1.2.23 | 已确认 |
| ✅ | AutoGen python-v0.7.5 | 已确认 |
| ✅ | DefenseClaw v0.2.0 | 已确认 |
| ✅ | langchain-openrouter 0.2.1 | 已确认 |
| ⏳ | DefenseClaw v1.0.0 Release Tag | GitHub 监测 |
| ⏳ | CrewAI A2A 协议支持确认 | crewAI/Core 迁移确认中 |

---

## 🟢 低频任务（每三天/按需）

### CONCEPT_UPDATE · 概念文章更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ✅ | 桌面 AI Agent 架构对比（OpenClaw vs Manus vs Perplexity）| 上轮完成 |
| ✅ | DeepResearch Bench ICLR 2026 | 上轮完成 |
| ✅ | AIP Agent Identity Protocol | 上轮完成 |
| ✅ | MCPMark ICLR 2026 | 上轮完成 |
| ✅ | Agent Skills Survey | 上轮完成 |
| ✅ | AI4Work Benchmark Mismatch | 上轮完成 |
| ✅ | MCP Agent Observability | 上轮完成 |
| ✅ | SkillsBench | 上轮完成 |
| ✅ | FinMCP-Bench | 上轮完成 |
| ✅ | TIP（arxiv:2603.24203）| 上轮完成 |
| ✅ | 177k MCP Tools（arxiv:2603.23802）| **本轮完成** |
| ⏳ | MCPMark + OSWorld-MCP + MCP-Bench + MSB 横向对比（4个 ICLR 2026 MCP 基准）| explicit（高优先级）|
| ⏳ | SkillsBench 与 AI4Work 横向联合（SkillsBench vs AI4Work 互补分析）| explicit（中优先级）|
| ⏳ | MCP Security 架构问题（CVE-2026-27896 non-standard field casing 新攻击面）| explicit（中优先级）|
| ⏳ | GAIA Benchmark 各模型详细分析 | 下一轮 benchmark 数据更新 |
| ⏳ | AIP 论文 Python/Rust 参考实现仓库分析 | explicit（低优先级）|

### ENGINEERING_UPDATE · 工程实践更新

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | best-ai-coding-agents-2026 补充 Augment GPT-5.2 | explicit |
| ⏳ | A2A Scanner vs SAFE-MCP vs Agent Wall 深度对比 | explicit |
| ⏳ | Wombat（Unix-style rwxd for MCP agents）GitHub stars 跟踪 | 低优先级 |

### BREAKING_INVESTIGATE · breaking 深度调查

| 状态 | 任务 | 触发条件 |
|------|------|----------|
| ⏳ | CVE-2026-27896 MCP SDK non-standard field casing 利用样本分析 | 安全社区出现公开 PoC |
| ⏳ | Manus My Computer 实际攻击面分析 | explicit |

---

## 📝 Articles 线索（每轮必须记录）

| 时间 | 线索方向 | 状态 |
|------|---------|------|
| 2026-03-29 | AI4Work Benchmark Mismatch | ✅ 完成 |
| 2026-03-29 | MCP Agent Observability | ✅ 完成 |
| 2026-03-30 | SkillsBench | ✅ 完成 |
| 2026-03-30 | FinMCP-Bench | ✅ 完成 |
| 2026-03-30 | TIP | ✅ 完成 |
| 2026-03-30 | 177k MCP Tools | ✅ 完成 |
| 2026-03-31 | Agent Audit | ✅ **本轮完成** |
| 2026-03-30 | MCP Dev Summit NA 2026（4/2-3，纽约）| ⏳ **P0 事件，距今仅1天，正式 Session 披露** |
| 2026-03-29 | MCPMark + OSWorld-MCP + MCP-Bench + MSB 横向对比 | ⏳ explicit（高优先级）|
| 2026-03-29 | Manus My Computer vs OpenClaw vs Perplexity | ⏳ explicit（中优先级）|
| 2026-03-29 | MCP Security 架构问题（CVE-2026-27896）| ⏳ explicit（中优先级）|
| 2026-03-31 | Codebadger（arxiv:2603.24837，Joern CPG + MCP for 漏洞发现）| ⏳ 下轮 PENDING |

---

## 📊 state.json 同步

```json
{
  "lastRun": "2026-03-31T05:01",
  "lastCommit": "pending",
  "status": "autonomous",
  "version": "0.9.2",
  "owner": "FreezeSoul"
}
```

---

*由 AgentKeeper 维护 | 2026-03-30 23:01 北京时间*
