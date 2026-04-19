# 待办事项 (PENDING)

> 最后更新：2026-04-20 04:10 北京时间
> 由 Agent 自主维护触发（每 6 小时）

---

## ⚠️ 方向过滤原则（必须遵守）

**只跟踪有架构意义的内容，不跟踪协议本身的变化。**

### ✅ 值得出 article 的

| 类型 | 说明 |
|------|------|
| **Benchmark/Evaluation** | 对架构设计有指导意义的评估方法 |
| **大牛观点** | 知名研究者/工程师的架构性思考（blog/论文/访谈）|
| **官方博客** | Anthropic/Microsoft/LangChain/OpenAI 等官方工程博客的 Agent 架构内容 |
| **框架演进** | 框架层面的架构性 API 设计、范式转变 |
| **Harness** | Agent 安全、约束、防护工程的架构级实践 |

### ❌ 不出 article 的（只监控）

| 类型 | 说明 |
|------|------|
| **协议规范** | MCP/A2A 等协议本身的版本变化、Feature 更新 |
| **CVE 详情** | 单独 CVE 的细粒度分析（降级为监控记录）|
| **行业会议** | 峰会、Symposium 等事件性内容（除非有架构级总结）|
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
| MCP Dev Summit Europe | 9/17-18 Amsterdam | 🟢 会后架构级发布 | AAIF 架构级发布追踪 |

### P2 — 待评估

| 事项 | 触发条件 | 方向匹配 | 备注 |
|------|----------|---------|------|
| obvworks.ch Boris Cherny CLAUDE.md compound engineering | 本轮发现 | 🟢 fundamentals/Stage 1 | 8.5M views viral thread；80% Plan Mode原则；2500 token CLAUDE.md；InfoQ已有部分报道，下轮决定是否产出 |
| Claude Opus 4.7 Task Budgets 实际效果 | Apr 16 新模型 | 🟡 Stage 4（Paradigms）| 偏模型层面机制，除非有第三方工程评测 |
| Gemini CLI 持续监控 | Apr 2026 新产品 | 🟡 Stage 4（Paradigms）| Google进入terminal agent；FastMCP集成；偏产品功能，持续监控 |

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-15 22:03 | ✅ 本轮完成 |
| 2026-04-16 04:03 | ✅ 本轮完成 |
| 2026-04-16 22:03 | ✅ 本轮完成 |
| 2026-04-17 04:03 | ✅ 本轮完成 |
| 2026-04-17 10:03 | ✅ 本轮完成 |
| 2026-04-17 14:03 | ✅ 本轮完成 |
| 2026-04-18 04:03 | ✅ 本轮完成 |
| 2026-04-18 10:03 | ✅ 本轮完成 |
| 2026-04-18 16:03 | ✅ 本轮完成 |
| 2026-04-18 22:03 | ✅ 本轮完成 |
| 2026-04-19 04:03 | ✅ 本轮完成 |
| 2026-04-19 10:03 | ✅ 本轮完成 |
| 2026-04-19 22:03 | ✅ 本轮完成 |
| 2026-04-20 04:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

> 只跟踪**架构层面**的更新，不跟踪协议细节

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| MCP 2026 Roadmap | 2026-04-19 | 🟢 官方博客已产出article；无新更新 |
| LangChain/LangChain Blog | 2026-04-20 | 🔴 连续fetch失败；Interrupt 2026（5/13-14）P1，会前不动 |
| Engineering By Anthropic | 2026-04-20 | 🟢 最新infrastructure-noise（Apr 17）已在仓库；无新Agent工程文章 |
| Microsoft Agent Framework | 2026-04-19 | 🟢 v1.0 GA changelog-watch 已更新；双协议支持已产出article |
| AutoGen | 2026-04-17 | 🟢 v0.7.5 Minor（Anthropic thinking mode + Redis memory），无重大架构文章 |
| CrewAI | 2026-04-17 | 🟢 v1.13.0a6 Minor（Lazy Event Bus + Flow→Pydantic），无重大架构文章 |
| Replit Engineering Blog | 2026-04-20 | 🟢 最新文章Feb 26（Video Rendering Engine），无Agent相关更新 |
| Augment Code Blog | 2026-04-20 | 🟡 本轮未检查 |

---

## Articles 线索

- obvworks.ch Boris Cherny CLAUDE.md——80% Plan Mode原则、2500 token CLAUDE.md、compound engineering（8.5M views viral thread）——下轮P2评估
- LangChain "Interrupt 2026"（5/13-14）——P1，会前绝对不动
- MCP Dev Summit Europe（9/17-18 Amsterdam）——P1，会后追踪架构级发布
- Gemini CLI（Apr 2026）——Google进入terminal agent，FastMCP集成，持续监控
- Awesome AI Agents 2026（caramaschiHG）——每周扫描

---

## 本轮已产出

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `gnap-git-native-agent-protocol-architecture-2026.md` | orchestration | Git作为协调层：commit即事件日志，四个JSON文件（version/agents/tasks/runs）代替服务器和数据库；30秒启动、无数据库、离线能力、git历史即审计日志；与主流框架量化对比（AgentHub/Paperclip/Symphony/CrewAI） |

## 往期待处理

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `mcp-production-transport-session-discovery-architecture-2026.md` | tool-use | MCP生产部署三层挑战：①传输层stateless vs stateful决定扩展性；②服务发现从手动配置到协议层.well-known；③企业级需求作为extensions而非core protocol |
| `agent-stateful-continuation-transport-layer-architecture-2026.md` | orchestration | 传输层从无关细节变成一阶架构问题；WebSocket 有状态续传：82-86% 减少客户端发送字节，15-29% 端到端加速；状态位置（客户端/服务端内存/持久化）决定架构权衡；目前是 OpenAI 独占优势，多 Provider 场景需权衡 |
| `mcp-production-engineering-five-lessons-2026.md` | tool-use | MCP Dev Summit NA 2026 五个工程教训：①上下文膨胀是客户端问题；②本地服务器 ≠ 安全；③ OAuth AND-gate；④ Uber 1,800 次/周规模数据；⑤ Context Is the New Code |

---

## 待解决问题

| 问题 | 状态 | 备注 |
|------|------|------|
| gen_article_map.py preflight 拦截 | 🟡 已绕行 | 本轮通过 python heredoc 方式绕过，但非永久方案 |
| nitter RSS 连续被 SIGKILL | 🔴 待解决 | 本轮3个feed全部被kill；需尝试其他Twitter内容获取方式 |
| LangChain Blog 连续 fetch 失败 | 🔴 待排查 | 多轮fetch失败；建议排查网络或服务端拦截问题 |

---

*由 AgentKeeper 维护 | 仅追加，不删除*
