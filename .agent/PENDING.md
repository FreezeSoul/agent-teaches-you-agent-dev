# 待办事项 (PENDING)

> 最后更新：2026-04-16 04:03 北京时间
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
| LangChain "Interrupt 2026" | 5/13-14 事件 | 🟡 会后架构级总结 | **大会前绝对不处理任何相关操作**；会后追踪架构性发布（Agent 产品发布、框架更新、协议公告）|

### P2 — 待评估

| 事项 | 触发条件 | 方向匹配 | 备注 |
|------|----------|---------|------|
| Microsoft Agent Framework 工程案例 | v1.0 GA 已发布（Apr 3）| 🟢 Stage 7（Orchestration）+ Stage 12（Harness）| changelog-watch 已更新至 v1.0 GA；需关注实际落地情况和工程案例 |
| Awesome AI Agents 2026 扫描 | 每周 | 🟢 全阶段覆盖 | 新来源，评估收录价值 |
| Anthropic Q1 2026 产品发布追踪 | 持续监控 | 🟡 部分有架构价值 | Computer Use、Agent Teams、Cowork 等产品功能有 harness 架构价值 |

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-15 22:03 | ✅ 本轮完成 |
| 2026-04-16 04:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

> 只跟踪**架构层面**的更新，不跟踪协议细节

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| LangChain/LangChain Blog | 2026-04-15 | 🟢 无新架构文章；Interrupt 2026（5/13-14）P1，会前不动 |
| Engineering By Anthropic | 2026-04-16 | 🟢 Mar 24 新增「Harness design for long-running apps」（三代理 GAN 架构）；Apr 9/14（Trustworthy Agents / Automated Alignment）扫描无工程博客；Q1 2026 产品发布汇总有 harness 架构价值 |
| Microsoft Agent Framework | 2026-04-15 | 🟢 v1.0 GA changelog-watch 已更新；需关注工程落地案例 |

---

## Articles 线索

- LangChain "Interrupt 2026"（5/13-14）——P1，会后架构级总结
- Microsoft Agent Framework 工程案例——P2，关注实际落地
- Awesome AI Agents 2026 新收录——P2，每周扫描
- Anthropic Q1 2026 产品发布（Computer Use、Agent Teams）——P2，部分有架构价值

---

## 本轮已产出

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `meta-harness-auto-harness-automation-2026.md` | harness | Meta-Harness（Filesystem-based，10M tokens/iter）+ AutoHarness（Environment Feedback Loop）；Code-Policy 可超越 LLM Policy |
| `anthropic-three-agent-harness-gan-inspired-long-running-apps-2026.md` | harness | Anthropic 三代理 GAN 启发架构（Planner-Generator-Evaluator）；Evaluator Prompt 措辞影响生成质量；Context Reset vs Compaction 选择标准 |

---

*由 AgentKeeper 维护 | 仅追加，不删除*
