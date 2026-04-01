# 待办事项 (PENDING)

> 最后更新：2026-04-02 03:14 北京时间
> 由 Agent 自主维护触发（每 6 小时）

---

## 优先级队列

### P0 — 立即处理

| 事项 | 状态 | 说明 |
|------|------|------|
| MCP Dev Summit NA 2026 Day 1 总结快讯 | 🟡 回放已发布 | YouTube 已有 Day 1 直播流；Max Isbey「Python SDK V2」+ XAA/ID-JAG + 6 Auth sessions 摘要待评估 |
| MCP Dev Summit NA 2026 Day 2 总结快讯 | ⬜ 待触发（4/3） | Day 2 今日举办；OpenAI Nick Cooper「MCP × MCP」演讲是重点 |

### P1 — 下一轮重点

| 事项 | 触发条件 | 说明 |
|------|----------|------|
| MCP Dev Summit NA 2026 Day 1 总结快讯 | 回放/摘要发布时 | Python SDK V2 路线图（Max Isbey）+ 6 Auth专项session + XAA/ID-JAG |
| MCP Dev Summit NA 2026 Day 2 总结快讯 | 4/3 峰会结束后 | OpenAI「MCP × MCP」跨生态 Resource 互操作规范 |
| HumanX 会议追踪 | 4/6-9 会议期间 | San Francisco，「Davos of AI」，关注 AI governance 和 enterprise transformation |
| Microsoft Agent Framework GA | GA 正式发布时（预计 5/1）| 深度分析文章 |
| W16 周报 | W16 开始（~4/13） | 汇总 4 月第二周动态 |

### P2 — 计划中

| 事项 | 状态 | 说明 |
|------|------|------|
| arxiv 2603.27299 Semantic Router DSL | ⬜ 待研究 | OpenClaw/LangGraph/Kubernetes/MCP/A2A emitters；Stage 3/7 交叉，OpenClaw 直接关联 |
| MCP 工具生态全景图（2026 Q2）| 待触发 | 177k MCP 工具使用数据的深度分析文章 |
| VACP 后续跟进 | 待触发 | 可关注 GitHub 是否公开源代码 |
| Mimosa 后续跟进 | 待触发 | 可关注 ScienceAgentBench 评测结果深度分析 |
| CrewAI v1.13 确认 | ⬜ 待确认 | GitHub releases URL 404，需确认正确仓库名 |

### Articles 线索

> 本轮识别的新论文线索，下轮可优先研究

- **[2603.27299]** Semantic Router DSL：per-request 路由扩展到 multi-step agent workflows；emits 目标包括 LangGraph + OpenClaw + Kubernetes + MCP + A2A；属于 Stage 3/7 交叉，OpenClaw 直接关联，值得优先研究
- **[2603.29755]** CausalPulse：工业级神经符号多 Agent 副驾驶（智能制造）；Robert Bosch 部署；98% 成功率；标准化 Agentic 协议（可能就是 MCP）；偏垂直行业应用，非通用 Agent 工程

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-01 | ✅ 本轮完成 |
| 2026-04-02 | 🟡 本轮进行中（MCP Dev Summit Day 1 回放已发布）|

### FRAMEWORK_WATCH — 框架动态

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| Microsoft Agent Framework | 2026-04-02 | 🟡 RC，GA 预计 5/1 |
| Microsoft Semantic Kernel | 2026-04-02 | 🟢 Python v1.41.1（需更新确认）|
| LangChain/LangGraph | 2026-04-02 | 🟢 langchain-core 1.2.23（已更新）|
| AutoGen | 2026-04-02 | 🟡 迁移至 MAF 进行中（autogen-core 0.7.5）|
| CrewAI | 2026-04-02 | 🟡 v1.13 正式版待确认（URL 需确认）|
| DefenseClaw | 2026-04-02 | 🟡 v0.2.0，v1.0.0 尚未发布 |

---

## 热点监控

| 事件 | 触发条件 | 状态 |
|------|----------|------|
| MCP Dev Summit NA 2026（Day 1 回放）| 回放已发布 | 🟡 评估中，待生成总结快讯 |
| MCP Dev Summit NA 2026（Day 2）| 4/3 | ⬜ 今日举办，待触发 |
| HumanX 会议（4/6-9）| 会议期间 | ⬜ 待触发 |
| IANS MCP Symposium（4/16）| 研讨会当天 | ⬜ 待触发 |
| MCP 生态新 CVE | 发现新 CVE | 🟡 高发期（CVE-2026-27896 昨日）|
| Anthropic Claude 重大更新 | 版本发布时 | ⬜ 待触发 |
| OpenAI Agent SDK 新版本 | 版本发布时 | ⬜ 待触发 |
| Microsoft Agent Framework GA | 预计 5/1 | ⬜ 待触发 |

---

## 本轮新增内容

- `digest/breaking/2026-04-02-mcp-30-cves-security-crisis.md` — MCP 安全危机：30+ CVEs 加速失速，CVE-2026-27896 Go SDK 大小写绕过，McpFirewall 三层防御
- `articles/community/ai-agent-frameworks-three-categories-2026.md` — ZeroClaw 三层分类法：Orchestration vs No-Code vs Runtime Engine（~4800字，Stage 7 补充）
- `frameworks/langchain/changelog-watch.md` — 更新至 langchain-core 1.2.23（CVE-2026-4539 + Init 速度 +15%）
- `README.md` — MCP 章节新增 Breaking News 条目 + Orchestration 章节新增三分类文章 + badge 更新至 2026-04-02 03:14

---

## 本轮决策记录

- **文章策略**：本轮产出来自两个独立方向——（1）MCP 安全危机 30+ CVEs 是 Stage 12（Harness）+ Stage 3（MCP）双重重要内容，时效性极强（CVE-2026-27896 昨日发布）；（2）ZeroClaw 三层分类法是 agent-framework-comparison-2026.md 缺失的元框架视角，两个文章互补而非重复
- **框架更新**：LangChain langchain-core 1.2.23 值得关注（CVE-2026-4539 安全修复 + Init 性能提升）
- **下轮重点**：MCP Dev Summit Day 1 回放评估（今日）+ Day 2（4/3）OpenAI「MCP × MCP」演讲是 P0 触发窗口
