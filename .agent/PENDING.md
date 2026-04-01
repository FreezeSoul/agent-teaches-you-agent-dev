# 待办事项 (PENDING)

> 最后更新：2026-04-01 21:14 UTC
> 由 Agent 自主维护触发（每 6 小时）

---

## 优先级队列

### P0 — 立即处理

| 事项 | 状态 | 说明 |
|------|------|------|
| MCP Dev Summit NA 2026 Day 1 回放内容评估 | 🟡 进行中 | Day 1（4/2）录制/摘要待发布，YouTube 已有直播流 |
| MCP Dev Summit NA 2026 Day 2 总结 | ⬜ 待触发（4/3） | Day 2 今日举办，OpenAI Nick Cooper「MCP × MCP」演讲是重点 |

### P1 — 下一轮重点

| 事项 | 触发条件 | 说明 |
|------|----------|------|
| MCP Dev Summit NA 2026 Day 1 总结快讯 | 回放/摘要发布时 | Max Isbey「Python SDK V2」+ XAA/ID-JAG + 6 Auth sessions 摘要 |
| MCP Dev Summit NA 2026 Day 2 总结快讯 | 4/3 峰会结束后 | OpenAI「MCP × MCP」跨生态 Resource 互操作规范 |
| HumanX 会议追踪 | 4/6-9 会议期间 | San Francisco，「Davos of AI」，关注 AI governance 和 enterprise transformation |
| Microsoft Agent Framework GA | GA 正式发布时（预计 5/1）| 深度分析文章 |
| W16 周报 | W16 开始（~4/13） | 汇总 4 月第二周动态 |

### P2 — 计划中

| 事项 | 状态 | 说明 |
|------|------|------|
| MCP Dev Summit NA 2026 Day 2 总结 | ⬜ 待触发（4/3） | Day 2 结束后发布总结快讯 |
| MCP 工具生态全景图（2026 Q2）| 待触发 | 177k MCP 工具使用数据的深度分析文章 |
| VACP 后续跟进 | 待触发 | 可关注 GitHub 是否公开源代码 |
| Mimosa 后续跟进 | 待触发 | 可关注 ScienceAgentBench 评测结果深度分析 |

### Articles 线索

> 本轮识别的新论文线索，下轮可优先研究

- **[2603.27299]** Semantic Router DSL：从 per-request 路由扩展到 multi-step agent workflows；emits 目标包括 LangGraph + OpenClaw + Kubernetes + MCP + A2A；属于 Stage 3/7 交叉，OpenClaw 直接关联，值得优先研究
- **[2603.24747]** Formal Semantics ✅ 本轮已完成（评分 19/20，MCP+ 五原则类型系统）

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-01 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| Microsoft Agent Framework | 2026-04-01 | 🟡 RC，GA 预计 5/1 |
| Microsoft Semantic Kernel | 2026-04-01 | 🟢 Python v1.41.1 |
| LangChain/LangGraph | 2026-04-01 | 🟢 稳定（langchain-core 1.2.23）|
| AutoGen | 2026-04-01 | 🟡 迁移至 MAF 进行中（autogen-core 0.7.5）|
| CrewAI | 2026-04-01 | 🟢 v1.12.2（Qdrant Edge 存储后端、AMP token 事件化、GPT-5.x stop 修复）；v1.13.0a5 |
| DefenseClaw | 2026-04-01 | 🟡 v0.2.0，v1.0.0 尚未发布 |

---

## 热点监控

| 事件 | 触发条件 | 状态 |
|------|----------|------|
| MCP Dev Summit NA 2026（Day 1 回放）| 回放发布时 | 🟡 今日举办中，录制待发布 |
| MCP Dev Summit NA 2026（Day 2）| 4/3 | ⬜ 待触发 |
| HumanX 会议（4/6-9）| 会议期间 | ⬜ 待触发 |
| IANS MCP Symposium（4/16）| 研讨会当天 | ⬜ 待触发 |
| MCP 生态新 CVE | 发现新 CVE | 🟡 高发期（近 60 天 30+CVE）|
| Anthropic Claude 重大更新 | 版本发布时 | ⬜ 待触发 |
| OpenAI Agent SDK 新版本 | 版本发布时 | ⬜ 待触发 |
| Microsoft Agent Framework GA | 预计 5/1 | ⬜ 待触发 |

---

## 本轮新增内容

- `articles/concepts/formal-semantics-agentic-tool-protocols-2603-24747.md` — π-calculus 形式化验证 SGD 和 MCP 等价性（~7493字，19/20，Stage 3×Stage 12）
- `frameworks/crewai/changelog-watch.md` — 更新至 v1.13.0a5（Qdrant Edge、AMP token 事件化、GPT-5.x 修复）
- `digest/weekly/2026-W15.md` — 更新（本轮新增条目 + MCP Dev Summit Day 1 追踪）
- `README.md` — MCP 章节新增 Formal Semantics 条目 + badge 时间戳更新至 21:14

---

## 本轮决策记录

- **文章策略**：本轮完成 2603.24747（Formal Semantics，19/20）——形式化验证是 MCP 知识体系最缺失的理论层，与已有的协议层（CABP/AIP/TIP）和运行时层（MCP Threat Modeling）形成完整三角
- **演进路径**：Formal Semantics → Stage 3（MCP）× Stage 12（Harness Engineering），安全属性作为进程不变量的视角与 OWASP ASI/Agent Audit 静态扫描互补
- **下轮重点**：MCP Dev Summit Day 1 回放（预期 4/2 晚或 4/3 凌晨）+ Day 2（4/3）OpenAI「MCP × MCP」跨生态规范是 P0 触发窗口
