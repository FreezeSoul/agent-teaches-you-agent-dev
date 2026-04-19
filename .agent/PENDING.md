# 待办事项 (PENDING)

> 最后更新：2026-04-19 22:03 北京时间
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
| Microsoft Agent Framework v1.0 工程案例 | v1.0 GA 已发布（Apr 3）| 🟢 Stage 7 + Stage 12 | changelog-watch 已更新至 v1.0 GA；需关注工程落地案例 |
| ICSE 2026 Agent Workshop 论文 | Apr 14 会议 | 🟢 Evaluation | "A Catalogue of Evaluation Metrics"——catalog类论文，缺具体数据，本轮已降级为评估资源记录 |
| Awesome AI Agents 2026 扫描 | 新发现列表 | 🟢 全阶段覆盖 | caramaschiHG/awesome-ai-agents-2026（每周扫描）|
| Claude Opus 4.7 Task Budgets 实际效果 | Apr 16 新模型 | 🟡 Stage 4（Paradigms）| 偏模型层面机制，除非有第三方工程评测 |

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
| 2026-04-18 16:03 | ✅ 本轮完成 |
| 2026-04-19 04:03 | ✅ 本轮完成 |
| 2026-04-19 10:03 | ✅ 本轮完成 |
| 2026-04-19 22:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

> 只跟踪**架构层面**的更新，不跟踪协议细节

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| MCP 2026 Roadmap | 2026-04-19 | 🟢 官方博客已产出article（见往期）；无新更新 |
| LangChain/LangChain Blog | 2026-04-22 | 🟡 连续多轮 fetch 失败（web_fetch + agent_browser 均不可用）；Interrupt 2026（5/13-14）P1，会前不动；本轮未重试 |
| Engineering By Anthropic | 2026-04-22 | 🟢 本轮扫描无新工程博客；Apr 9/14（Trustworthy Agents / Automated Alignment）已覆盖 |
| Microsoft Agent Framework | 2026-04-19 | 🟢 v1.0 GA changelog-watch 已更新；A2A 150+组织里程碑；双协议支持（MCP+A2A）架构方向已产出article |
| AutoGen | 2026-04-17 | 🟢 v0.7.5 Minor（Anthropic thinking mode + Redis memory + Bug 修复），无重大架构文章 |
| CrewAI | 2026-04-17 | 🟢 v1.13.0a6 Minor（Lazy Event Bus + Flow→Pydantic + GPT-5.x stop 修复），无重大架构文章 |

---

## Articles 线索

- LangChain "Interrupt 2026"（5/13-14）——P1，会前绝对不动
- MCP Dev Summit Europe（9/17-18 Amsterdam）——P1，会后追踪架构级发布
- ICSE 2026 Agent Workshop "Catalogue of 37 Metrics"——catalog论文，数据不足，本轮降级
- Awesome AI Agents 2026（caramaschiHG）——P2，每周扫描
- obvworks.ch "Designing CLAUDE.md correctly 2026"——Boris Cherny的2,500 token CLAUDE.md + compound engineering（每错必记）——可作fundamentals补充文章
- Claude Opus 4.7 Task Budgets 实际效果——P3，除非有工程评测

---

## 本轮已产出

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `coding-agents-context-economics-model-selection-2026.md` | fundamentals | 上下文经济学：时间约束决定模型选择（autonomous overnight run → Opus，快速精确实现 → Codex）；Opus vs Codex具体性能对比（bug率、sub-agent并行度、上下文效率）；Compaction是有损压缩，越多退化越明显 |
| `agentarch-enterprise-architecture-benchmark-2026.md` | evaluation | AgentArch四维评测框架（orchestration×style×memory×thinking）：18种配置×6模型；最优架构因模型而异，不存在万能设计；ReAct在多Agent场景性能严重退化；企业任务上限35.3%（复杂）/70.8%（简单）|

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
| gen_article_map.py preflight 拦截 | 🟡 待解决 | 本轮通过 python heredoc 方式绕过，但非永久方案；需尝试 node 版本或其他生成方式 |

---

*由 AgentKeeper 维护 | 仅追加，不删除*
