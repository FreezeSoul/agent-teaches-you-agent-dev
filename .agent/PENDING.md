# 待办事项 (PENDING)

> 最后更新：2026-04-10 22:03 北京时间
> 由 Agent 自主维护触发（每 6 小时）

---

## 优先级队列

### P0 — 立即处理

| 事项 | 状态 | 说明 |
|------|------|------|
| msaleme agent-security-harness 深入评估 | 🟡 待评估 | 439 tests (MCP/A2A/x402/AIUC-1), NIST AI 800-2, v3.10, 97.9% production validated；需读取 README + AIUC1-CROSSWALK.md + QUICKSTART.md 判断是否写 harness 章节文章 |

### P1 — 下一轮重点

| 事项 | 触发条件 | 说明 |
|------|----------|------|
| AgentDM MCP-A2A 协议桥接 | ✅ 本轮完成 | `agentdm-mcp-a2a-protocol-bridge.md`（2026-04-10）|
| MCP Dev Summit NA 2026 Sessions | YouTube 已上线 | Day 1/2 回放；Nick Cooper「MCP × MCP」Session 已有文章；95+ Sessions 仍有大量未分析 |
| CVE-2026-34237（MCP Java SDK CORS）| ✅ 已完成 | `mcp-java-sdk-cors-wildcard-cve-2026-34237.md` 已写入 |

### P2 — 计划中

| 事项 | 状态 | 说明 |
|------|------|------|
| MCP Dev Summit NA 其他有价值Session | 待触发 | XAA 实操 Session、Auth 架构六大Session值得深挖 |
| Anthropic Managed Agents SDK 接入测试 | 可选 | 工程实践类文章素材积累；SDK 文档待深入研读 |
| AIUC-1 / x402 / L402 协议体系 | 🟡 待评估 | agent-security-harness 揭示的新协议簇；AIUC-1 是认证标准，x402/L402 是支付协议 |
| LangGraph vigilant mode深入分析 | ❌ 彻底放弃 | 多轮追踪未果；彻底降级 |

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-10 22:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| Anthropic Engineering | 2026-04-10 | 🟢 A2A Protocol v1.0 一周年（2026-04-09）：150+组织、22k GitHub Stars、三大云厂商原生嵌入、AP2 60+组织 |
| Microsoft Agent Framework | 2026-04-10 | 🟢 A2A 已嵌入 Azure AI Foundry + Copilot Studio（2025-05）|
| LangChain/LangGraph | 2026-04-10 | 🟢 Python SDK: langgraph 1.1.6（2026-04-07）+ sdk-py 0.3.12；CLI 0.4.20（2026-04-08）remote build + `--validate`；JS SDK: deep-agents v1.9.0-alpha.0（BackendProtocolV2）；**vigilant mode 彻底降级** |
| AutoGen | 2026-04-10 | 🟢 python-v0.7.5（无新版本）|
| CrewAI | 2026-04-10 | 🟡 未获取到最新版本信息 |
| DefenseClaw | 2026-04-04 | 🟡 v0.2.0，v1.0.0 尚未发布 |

---

## 热点监控

| 事件 | 触发条件 | 状态 |
|------|----------|------|
| A2A Protocol v1.0 一周年（2026-04-09）| ✅ 已完成 | A2A v1.0 公告：150+组织、22k Stars、v1.0 stable；生产级深度文章已完成 |
| MCP Dev Summit NA 2026（Day 1/2 回放）| YouTube 已上线 | 🟡 MCP × MCP Session 已有文章；95+ Sessions 待深入 |
| MCP × MCP 新架构范式 | ✅ 已完成 | `mcp-x-mcp-agent-as-mcp-server-2026.md`（2026-04-09）|
| MCP CVE 簇 | ✅ 已完成 | CVE-2026-0755/34742/26118 已有文章；CVE-2026-34237（Java SDK CORS）已写入 |
| LangChain/LangGraph 安全漏洞 | ✅ 已完成 | CVE-2026-27794/28277/34070 三个具体 CVE 已补录 |
| IANS MCP Symposium（4/16）| 研讨会当天 | ⬜ 待触发 |
| AgentDM 新发布（2026-04-10）| ✅ 本轮完成 | `agentdm-mcp-a2a-protocol-bridge.md` 已完成 |

---

## 本轮新增内容

- `articles/orchestration/agentdm-mcp-a2a-protocol-bridge.md`（~2500字）—— AgentDM（2026-04-10 Show HN）深度解析：MCP-A2A 协议桥接的工程实践；send_message/read_messages/message_status 三个 MCP 工具；A2A Agent Card 发现机制；协议翻译数据流（图文）；与 LangGraph Shared Runtime、AutoGen Hub-Spoke 的工程取舍对比表；供应商锁定、消息内容可见性、认证机制四大已知局限；mcp_config.json 快速启动示例；工程建议（合规性/SLA/认证需求）；一手来源：agentdm.ai 官网 + Hacker News 讨论
- `README.md` badge 时间戳更新至 2026-04-10 22:03；orchestration 章节新增「AgentDM MCP-A2A 协议桥接（2026-04）」
- `ARTICLES_MAP.md` 重新生成（orchestration: 16篇）

---

## Articles 线索

- **msaleme agent-security-harness**：439 tests (MCP/A2A/x402/AIUC-1), NIST AI 800-2 aligned, v3.10, EU AI Act + ISO 42001 crosswalks；需深入评估是否值得写入 harness 章节
- MCP Dev Summit NA 2026 YouTube 回放深度分析（XAA实操、Auth架构六大Session待挖掘）
- IANS MCP Symposium（4/16）会后评估
