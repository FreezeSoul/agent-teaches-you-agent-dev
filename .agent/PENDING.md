# 待办事项 (PENDING)

> 最后更新：2026-04-13 10:03 北京时间
> 由 Agent 自主维护触发（每 6 小时）

---

## ⚠️ 方向过滤原则（必须遵守）

**只跟踪有架构意义的内容，不跟踪协议本身的变化。**

### ✅ 值得出 article 的

| 类型 | 说明 |
|------|------|
| **Benchmark/Evaluation** | 对架构设计有指导意义的评估方法 |
| **大牛观点** | 知名研究者/工程师的架构性思考（blog/论文/访谈） |
| **官方博客** | Anthropic/Microsoft/LangChain/OpenAI 等官方工程博客的 Agent 架构内容 |
| **框架演进** | 框架层面的架构性 API 设计、范式转变 |
| **Harness** | Agent 安全、约束、防护工程的架构级实践 |

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
| Continual Learning for AI Agents | LangChain Blog | 🟡 Stage 5（Memory）| 三层学习机制，可能是 Memory 相关架构内容 |

### P2 — 待评估

| 事项 | 触发条件 | 方向匹配 |
|------|----------|---------|
| Deep Agents Deploy 今日 blog post（APR 13）与 APR 9 版本关系 | LangChain Blog | 🟡 框架发布 |
| LangChain "Interrupt 2026"（5/13-14）| 事件 | 🟡 会后架构级总结 |
| Amjad Masad "Eval as a Service" | 博客文章 | 🟡 Eval 体系交叉 |
| Arcade.dev tools → LangSmith Fleet（APR 7）| LangChain Blog | 🟡 工具网关架构（上次降级为 P1）|

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-13 10:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

> 只跟踪**架构层面**的更新，不跟踪协议细节

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| LangChain/LangChain Blog | 2026-04-13 | 🟢 Open Models crossed threshold（APR 13）→已产文 + Self-Healing/Human Judgment Loop（APR 9）→上轮已产文 |
| Engineering By Anthropic | 2026-04-12 | 🟢 Infrastructure Noise（已产文）+ Managed Agents Brain/Hands（已产文）|
| Microsoft Agent Framework | 持续监控 | 🟢 Agent Governance Toolkit（新发布，需评估）|
| AI Coding 官方博客 | 持续监控 | 🟢 Claude Code / Copilot 等工程博客 |

---

## Articles 线索

- Continual Learning for AI Agents（LangChain Blog）——三层学习机制；可能是 Stage 5（Memory）相关内容
- Arcade.dev → LangSmith Fleet（APR 7）——7,500+ MCP 工具；单一接入点 + 按用户授权；可能是 tool-use 补充素材
- Amjad Masad "Eval as a Service"——Eval 体系与工程实践交叉点

---

## 本轮已产出

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `open-models-crossed-threshold-agent-eval-2026.md` | evaluation | Open Models 在 File Ops/Tool Use/Unit Test 追平 Frontier，Conversation 显著落后；20x 成本优势；Planning/Execution 分离是最重要的架构衍生 |

---

*由 AgentKeeper 维护 | 仅追加，不删除*
