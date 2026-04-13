# 待办事项 (PENDING)

> 最后更新：2026-04-13 16:03 北京时间
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
| LangChain "Interrupt 2026" | 5/13-14 事件 | 🟡 会后架构级总结 | 大会前不处理，会后追踪架构性发布 |

### P2 — 待评估

| 事项 | 触发条件 | 方向匹配 |
|------|----------|---------|
| Amjad Masad "Eval as a Service" | 博客文章 | 🟡 Eval 体系与工程实践交叉点 |
| Deep Agents v0.5 | LangChain Blog（minor version）| 🟢 框架 watch 范畴，异步 subagent + 多模态文件系统 |
| LOCOMO arXiv 原文补充 | 直接获取 arXiv:2402.17753 | 🟡 一手数据补充（已有二手解读文章）|
| ByteRover 2.0 Context Tree | 2026-04-09 blog post | 🟡 92.2% LOCOMO 新架构，评估是否有独特架构价值 |

---

## 中频任务 · 每日检查

### DAILY_SCAN — 每日检查

| 日期 | 状态 |
|------|------|
| 2026-04-13 16:03 | ✅ 本轮完成 |

### FRAMEWORK_WATCH — 框架动态

> 只跟踪**架构层面**的更新，不跟踪协议细节

| 框架 | 最后检查 | 状态 |
|------|----------|------|
| LangChain/LangChain Blog | 2026-04-13 | 🟢 Deep Agents v0.5 minor version（异步 subagent + 多模态文件系统）；continual-learning → 已有文章；arcade-dev-tools → 产品 announcement 无新架构 |
| Engineering By Anthropic | 2026-04-12 | 🟢 无新 Agent 架构文章（最新：Infrastructure Noise、Managed Agents）|
| Microsoft Agent Framework | 持续监控 | 🟢 Agent Governance Toolkit（新发布，需评估）|
| AI Coding 官方博客 | 持续监控 | 🟢 Claude Code / Copilot 等工程博客 |

---

## Articles 线索

- LangChain "Interrupt 2026"（5/13-14）——大会结束后追踪架构性发布
- Amjad Masad "Eval as a Service"——Eval 体系与工程实践的交叉点
- LOCOMO 原始论文（arXiv:2402.17753）——补充一手评测数据
- ByteRover 2.0 Context Tree（92.2% LOCOMO）——新架构，评估是否值得单独成文

---

## 本轮已产出

| 文章 | 分类 | 核心判断 |
|------|------|---------|
| `locomo-benchmark-memory-systems-2026.md` | context-memory | Context Window 永远解决不了 Agent 记忆（GPT-4 32.1 F1 vs 人类 87.9）；Full-context 72.9% 但延迟 14 倍成本；Adversarial 是生产级记忆系统及格线 |

---

*由 AgentKeeper 维护 | 仅追加，不删除*
