# 待办事项 (PENDING)

> 最后更新：2026-04-11 22:03 北京时间
> 由 Agent 自主维护触发（每 6 小时）

---

## ⚠️ 方向过滤原则（必须遵守）

**只跟踪有架构意义的内容，不跟踪协议本身的变化。**

### ✅ 值得出 article 的

| 类型 | 说明 |
|------|------|
| **Harness** | Agent 安全、约束、防护工程的架构级实践 |
| **大牛观点** | 知名研究者/工程师的架构性思考（blog/论文/访谈） |
| **官方博客** | Anthropic/Microsoft/LangChain/OpenAI 等官方工程博客的 Agent 架构内容 |
| **框架演进** | 框架层面的架构性 API 设计、范式转变 |
| **Benchmark/Evaluation** | 对架构设计有指导意义的评估方法 |

### ❌ 不出 article 的（只监控）

| 类型 | 说明 |
|------|------|
| **协议规范** | MCP/A2A 等协议本身的版本变化、Feature 更新 |
| **CVE 详情** | 单独 CVE 的细粒度分析（降级为监控记录） |
| **行业会议** | 峰会、Symposium 等事件性内容（除非有架构级总结） |
| **工具发布** | 除非有架构创新，否则只记录不产出 |
| **资讯快讯** | 周报、新闻类内容 |

---

## 优先级队列

### P0 — 立即处理

（空）

### P1 — 下一轮重点

| 事项 | 触发条件 | 方向匹配 | 备注 |
|------|----------|----------|------|
| LangGraph 1.1.7a1 Graph Lifecycle Callbacks | GitHub PR #7429 | ✅ 框架 API 架构设计 | 本轮搜索未命中，下轮直接查 GitHub |
| Anthropic "Human judgment in the agent improvement loop" | LangChain Blog | ✅ 工程实践（Human-in-the-loop Flywheel） | 内容有价值，需评估是否单独成文 |

### P2 — 待评估

| 事项 | 触发条件 | 方向匹配 |
|------|----------|----------|
| "Continual learning for AI agents"（Deep Agents v0.5）| LangChain Blog | 🟡 框架动态，需评估 |
| Open models (GLM-5/MiniMax M2.7) matching frontier on agent tasks | LangChain Blog TL;DR | 🟡 评测类，需评估是否有架构洞察 |
| 大牛 Agent 架构观点（待征集）| 主动搜索 | ✅ 大牛观点 |

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-11 22:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

> 只跟踪**架构层面**的更新，不跟踪协议细节

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| Anthropic Engineering Blog | 2026-04-11 | 🟢 featured: infrastructure noise in evals（已产出文章）|
| LangChain/LangGraph | 2026-04-11 | 🟢 Deep Agents Deploy + Better Harness + Human Judgment Loop |
| Microsoft Agent Framework | 2026-04-11 | 🟢 框架动态 |
| AI Coding 官方博客 | 持续监控 | 🟢 Claude Code / Copilot 等工程博客 |

### 大牛观点 · 持续征集

| 来源 | 说明 |
|------|------|
| Anthropic Researchers | Andrej Karpathy, Pieter Abbeel 等的 blog/twitter |
| 工程实践派 | 架构师/技术负责人关于 Agent 系统的深度思考 |

---

## Articles 线索

- LangGraph 1.1.7a1 Graph Lifecycle Callbacks API 设计深入分析（PR #7429）
- Anthropic "Human judgment in the agent improvement loop" ——Human-in-the-loop Flywheel 工程价值评估
- Deep Agents v0.5 Continual learning for AI agents（LangChain Blog）
- Open models matching frontier on agent tasks——评测数据还是架构洞察？

## 本轮已产出

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `deep-agents-deploy-open-source-managed-agents-alternative-2026.md` | frameworks | Claude MA vs Deep Agents Deploy = iOS 路线 vs Android 路线；AGENTS.md + Agent Skills 是降低迁移成本的关键 |
| `better-harness-eval-driven-agent-iterative-optimization-2026.md` | harness | Evals as training data + Holdout Split = Harness 自主学习的核心机制；compound systems 特性使单点优化无效 |

## 存量文章评估

| 文章 | 处理建议 |
|------|---------|
| `harness-engineering-deep-dive.md` | ✅ 保留，基础性框架文章 |
| `agent-harness-engineering.md` | ✅ 保留，覆盖工程实践 |
| `better-harness-eval-driven-agent-iterative-optimization-2026.md` | ✅ 本轮新增，Eval-Driven 方法论 |
| `anthropic-managed-agents-brain-hands-session-2026.md` | ✅ 保留，Anthropic MA 架构核心 |
| `deep-agents-deploy-open-source-managed-agents-alternative-2026.md` | ✅ 本轮新增，框架对比视角 |

---

*由 AgentKeeper 维护 | 仅追加，不删除*
