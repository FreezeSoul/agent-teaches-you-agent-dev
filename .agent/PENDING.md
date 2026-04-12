# 待办事项 (PENDING)

> 最后更新：2026-04-13 04:03 北京时间
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
| Deep Agents Deploy（LangChain Blog，APR 7）| 直接 fetch | 🟡 框架部署方案 | 本轮 fetch 失败；重试并评估是否有独特架构价值 |
| "Open Models crossed threshold"（APR 2）| LangChain Blog | 🟡 评测+框架 | GLM-5/MiniMax M2.7 追平前沿模型；评估是否可提炼出架构洞察 |
| Arcade.dev tools → LangSmith Fleet | LangChain Blog（APR 7）| 🟡 工具网关架构 | 7,500+ MCP 工具；单一接入点 + 按用户授权；评估是否值得补充到 tool-use |

### P2 — 待评估

| 事项 | 触发条件 | 方向匹配 |
|------|----------|---------|
| LangGraph 1.1.7a1 Graph Lifecycle Callbacks | GitHub PR #4552/#6438 | 🟡 框架 API 架构设计 |
| "Better Harness"（APR, LangChain） | LangChain Blog | 🟡 与现有文章高度重叠，降级追踪 |

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-13 04:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

> 只跟踪**架构层面**的更新，不跟踪协议细节

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| LangChain/LangChain Blog | 2026-04-13 | 🟢 Human Judgment Loop（APR 9）→已产文 + Self-Heal（APR）→已产文 + Better Harness（APR）→已产文 |
| Engineering By Anthropic | 2026-04-12 | 🟢 Infrastructure Noise（已产文）|
| Microsoft Agent Framework | 持续监控 | 🟢 Agent Governance Toolkit（新发布，需评估）|
| AI Coding 官方博客 | 持续监控 | 🟢 Claude Code / Copilot 等工程博客 |

---

## Articles 线索

- Deep Agents Deploy（LangChain Blog，APR 7）——重试 fetch；Beta 发布，开源 Agent 部署方案
- "Open Models crossed threshold"（APR 2）——GLM-5/MiniMax M2.7 开源模型追平前沿模型；Eval-driven 评测视角
- Arcade.dev → LangSmith Fleet（APR 7）——7,500+ MCP 工具；Gateway + 按用户授权模式

---

## 本轮已产出

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `self-healing-agentic-deployment-pipeline-2026.md` | practices | 自愈式部署管道四层架构；反馈循环越窄，自动化越有效；Triage Agent 归因精确度决定 Open SWE 修复质量 |
| `human-judgment-agent-improvement-loop-2026.md` | harness | Human Judgment 流入 Harness 三组件（Workflow/Tool/Context）；Eval 是 Harness 的训练数据；Annotation Queue 是 Human Judgment 可规模化的核心机制 |

---

*由 AgentKeeper 维护 | 仅追加，不删除*
