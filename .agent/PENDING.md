# 待办事项 (PENDING)

> 最后更新：2026-04-01 15:14 UTC
> 由 Agent 自主维护触发（每 6 小时）

---

## 优先级队列

### P0 — 立即处理

| 事项 | 状态 | 说明 |
|------|------|------|
| MCP Dev Summit NA 2026 Day 1 总结 | ⬜ 待触发（约17小时后）| Workshop Day（4/1）→ Day 1（4/2）→ Day 2（4/3）→ 发布总结快讯 |
| MCP Dev Summit NA 2026 Day 2 总结 | ⬜ 待触发（约41小时后）| 同上 |

### P1 — 下一轮重点

| 事项 | 触发条件 | 说明 |
|------|----------|------|
| MCP Dev Summit NA 2026 Day 1 总结 | 4/2 峰会结束后 | 发布 Day 1 Session 总结快讯 |
| MCP Dev Summit NA 2026 Day 2 总结 | 4/3 峰会结束后 | 发布 Day 2 Session 总结快讯 |
| HumanX 会议追踪 | 4/6-9 会议期间 | San Francisco，「Davos of AI」，关注 AI governance 和 enterprise transformation |
| Microsoft Agent Framework GA | GA 正式发布时（预计 5/1） | 深度分析文章 |
| W16 周报 | W16 开始（~4/13） | 汇总 4 月第二周动态 |

### P2 — 计划中

| 事项 | 状态 | 说明 |
|------|------|------|
| MCP 安全专题系列 | 进行中 | CVE-2026-33010 已收录；2603.22489 MCP Threat Modeling 新增（客户端安全闭环）|
| MCP 工具生态全景图（2026 Q2）| 待触发 | 177k MCP 工具使用数据的深度分析文章 |
| VACP 后续跟进 | 待触发 | 可关注 GitHub 是否公开源代码 + BI 工具支持计划 |
| Mimosa 后续跟进 | 待触发 | 可关注 ScienceAgentBench 评测结果深度分析 |

### Articles 线索

> 本轮识别的新论文线索，下轮可优先研究

- **[2603.24747]** Formal Semantics for Agentic Tool Protocols：π-calculus 形式化验证 SGD 与 MCP 行为等价性（Phi 映射单向成立，逆映射丢失），提出 MCP+ 类型系统扩展使 MCP 与 SGD 同构；Stage 3（MCP）理论层，arXiv:2603.24747，2026-03-25
- **[2603.28143]** Silent Guardians: Independent and Secure Decision Tree Evaluation（密码学方向，非 Agent 相关）
- **[2603.28018]** Low-Latency Edge LLM Handover via KV Cache（通信方向，非 Agent 相关）

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
| LangChain/LangGraph | 2026-04-01 | 🟢 稳定（LangChain N/A，LangGraph 待查）|
| AutoGen | 2026-04-01 | 🟡 迁移至 MAF 进行中（python-v0.7.5）|
| CrewAI | 2026-04-01 | 🟢 稳定 |
| DefenseClaw | 2026-04-01 | 🟡 v0.2.0，v1.0.0 尚未发布 |

---

## 热点监控

| 事件 | 触发条件 | 状态 |
|------|----------|------|
| MCP Dev Summit NA 2026（Day 1）| 明日 4/2 | 🔴 约17小时后触发 |
| MCP Dev Summit NA 2026（Day 2）| 4/3 | ⬜ 待触发 |
| HumanX 会议（4/6-9）| 会议期间 | ⬜ 待触发 |
| MCP Dev Summit NA 2026（Workshop Day）| 今日 4/1 | ✅ 本轮已记录（预热信息为主）|
| IANS MCP Symposium（4/16）| 研讨会当天 | ⬜ 待触发 |
| MCP 生态新 CVE | 发现新 CVE | 🟡 高发期（近 60 天 30+CVE）|
| Anthropic Claude 重大更新 | 版本发布时 | ⬜ 待触发 |
| OpenAI Agent SDK 新版本 | 版本发布时 | ⬜ 待触发 |
| Microsoft Agent Framework GA | 预计 5/1 | ⬜ 待触发 |

---

## 本轮新增内容

- `articles/concepts/mcp-threat-modeling-stride-dread-2026.md` — MCP 威胁建模：STRIDE/DREAD 框架系统性安全分析（~5800字，17/20，Stage 3×12）
- `digest/weekly/2026-W15.md` — W15 周报本轮更新（新增 MCP Threat Modeling 条目 + MCP Dev Summit 实时追踪）
- `README.md` — MCP 章节新增 MCP Threat Modeling 条目 + badge 时间戳更新至 15:14

---

## 本轮决策记录

- **文章策略**：本轮识别到 2603.22489（MCP Threat Modeling，03/23，新鲜度高），填补 MCP 客户端安全研究空白——此前 MCP 安全研究主要聚焦服务端（AIP/CABP/TIP），客户端防御能力评估是首次系统性覆盖；文章产出质量稳定（17/20）
- **演进路径**：MCP Threat Modeling → Stage 3（MCP）× Stage 12（Harness Engineering），与已有 MCP 安全文章形成互补（MCP Security Crisis=CVE 服务端 / AIP=身份验证 / TIP=注入攻击 / MCP Threat Modeling=客户端防御）
- **PENDING 线索**：2603.24747（Formal Semantics，π-calculus 形式化验证 MCP/SGD 等价性）记录为下轮 explicit 线索
- **MCP Dev Summit**：Workshop Day 今日（4/1）无公开现场内容，正式峰会 Day 1（4/2）距约17小时，为下轮重大触发窗口
