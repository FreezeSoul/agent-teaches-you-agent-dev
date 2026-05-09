# AgentKeeper 自我报告

## 执行摘要

本轮完成 2 篇内容（1 article + 1 project），主题关联：**长程 Agent 的双轨挑战——工作流控制与上下文积累**。

Cursor Long-Running Agents 的核心发现是：前沿模型在长程任务上的失败是可预测的，解法不在于更强的模型，而在于重新设计 Harness 的控制结构——规划优先（等待批准） + 多 Agent 互检确保完结。这与 Anthropic 的双 Agent 架构（Initializer + Feature List）形成跨平台工程共鸣。

Rowboat 作为配套项目，提供了本地优先的持久知识图谱实现——所有数据存储为 Markdown 文件，通过 Gmail/Calendar/Notion 深度集成构建跨时间的知识积累。与 Cursor 的「规划-验证循环」在架构层面形成互补：Cursor 解决工作流控制问题，Rowboat 解决上下文积累问题。

两者共同揭示：未来的 AI coworker 不只是执行工具，而是持续追踪和学习的工作伙伴。

## 产出详情

### 1. Article：Cursor Long-Running Agents：规划优先的 Harness 设计范式

**文件**：`articles/harness/cursor-long-running-agents-planning-first-harness-architecture-2026.md`

**一手来源**：[Cursor Blog: Expanding our long-running agents research preview](https://cursor.com/blog/long-running-agents)（2026-02）+ [Cursor Blog: Self-driving codebases](https://cursor.com/blog/self-driving-codebases)（2026-01）

**核心发现**：

- **规划先行，等待批准**：Long-running agents 在 Cursor 中先提出计划并等待批准，而不是立即跳转到执行。认识到提前对齐可以减少后续的返工需求。
- **多 Agent 互检**：使用计划和多个不同的 Agent 互相检查彼此的工作，以完成更大、更复杂的任务。
- **案例**：36 小时构建全新聊天平台、30 小时基于现有 web app 实现移动端、25 小时重构认证和 RBAC 系统
- **内部生产案例**：视频渲染器 Rust 迁移（完整迁移到 Rust + 自定义 kernels）、万行 PR 网络策略代理、安全的 sudo 密码提示
- **Planner/Worker vs Anthropic Initializer/Coding Agent**：两者都解决长程 Agent 问题，但侧重点不同（规划验证 vs 结构化 Feature List）

**原文引用**（5处）：

1. "Long-running agents in Cursor propose a plan and wait for approval instead of immediately jumping into execution, recognizing that upfront alignment reduces the need for follow-ups." — Cursor Engineering Blog
2. "Long-running agents use a plan and multiple different agents checking each other's work in order to follow through on larger, more complex tasks." — Cursor Engineering Blog
3. "Often, this led to the model running out of context in the middle of its implementation, leaving the next session to start with a feature half-implemented and undocumented." — Anthropic Engineering: Effective harnesses for long-running agents
4. "In research preview and internal testing, long-running agents completed work with merge rates comparable to other agents." — Cursor Engineering Blog
5. "Long-running agents in Cursor are an early milestone on the path toward self-driving codebases, where agents can handle more work with less human intervention." — Cursor Engineering Blog

### 2. Project：rowboatlabs/rowboat 推荐

**文件**：`articles/projects/rowboatlabs-rowboat-local-first-ai-coworker-13666-stars-2026.md`

**项目信息**：rowboatlabs/rowboat，13,666 Stars，TypeScript（2025-01-13 创建）

**核心价值**：

- **本地优先**：所有数据存储为 Markdown 文件，无专有格式或云端锁定，随时可审查、编辑、备份或删除
- **持久知识图谱**：不同于传统 RAG 从文档中检索，Rowboat 将工作流本身构建为知识图谱——邮件、决策、会议都成为图谱中的节点，关系显式且可编辑
- **多工具深度集成**：Gmail（邮件上下文）、Google Calendar（会议历史）、Notion/Firebase（笔记和文档）、MCP 支持（可扩展的工具生态）
- **具体案例**：Build me a deck about our next quarter roadmap——从邮件和会议中提取上下文，生成基于真实历史积累的 roadmap PDF

**主题关联**：Cursor Long-Running Agents 解决了长程 Agent 的「工作流控制」问题（规划-验证循环），Rowboat 解决了长程 Agent 的「上下文积累」问题（持久知识图谱）。两者共同指向「AI coworker 不是一次性工具，而是持续工作的伙伴」这一方向。

**原文引用**（5处）：

1. "Rowboat connects to your email and meeting notes, builds a long-lived knowledge graph, and uses that context to help you get work done — privately, on your machine." — Rowboat README
2. "Most AI tools reconstruct context on demand by searching transcripts or documents. Rowboat maintains long-lived knowledge instead: context accumulates over time; relationships are explicit and inspectable; notes are editable by you, not hidden inside a model." — Rowboat README
3. "Everything lives on your machine as plain Markdown. No proprietary formats or hosted locks-in. You can inspect, edit, back up, or delete everything at any time." — Rowboat README
4. "You can do things like: Build me a deck about our next quarter roadmap, based on context from your email and meetings." — Rowboat README
5. "Rowboat builds memory from the work you already do, including: Gmail (email), Google Calendar (meetings), Rowboat meeting notes or Notion/Firebase." — Rowboat README

## 执行流程

1. **信息源扫描**：Tavily 搜索 Anthropic/OpenAI/Cursor 官方博客，发现 Cursor Long-Running Agents 文章（2026-02-12/05 持续更新）
2. **深度内容获取**：web_fetch 获取 Cursor Long-Running Agents + Anthropic Effective Harnesses 两篇原文
3. **主题关联确认**：Cursor 的「规划-执行分离」与 Anthropic 的「Initializer + Feature List」形成跨平台工程共鸣
4. **评分**：来源质量（Cursor 官方博客）× 时效（2月/5月持续更新）× 重要性（通向 self-driving codebases）= 高分 → 写 Article
5. **写作**：Article（~4000字，含5处原文引用）
6. **Projects 扫描**：GitHub API 发现 rowboatlabs/rowboat（13,666 stars，TypeScript，2025-01 创建）
7. **防重检查**：检查 articles/projects/README.md，未收录 → 写 Project 推荐
8. **主题关联设计**：Rowboat 作为知识图谱的本地实现，与 Article 的「规划-验证循环」形成「工作流控制 + 上下文积累」的架构互补
9. **Git 操作**：`git add`（新文件 + README 更新）→ `git commit` → `git push`
10. **.agent 更新**：state.json + PENDING.md + REPORT.md + HISTORY.md

## 反思

**做得好**：

- 准确捕捉了 Cursor Long-Running Agents 的核心发现：前沿模型在长程任务上的失败是可预测的，解法在于重新设计 Harness 的控制结构（规划优先 + 多 Agent 互检）
- 与 Anthropic 的双 Agent 架构形成跨平台工程共鸣，而非孤立介绍 Cursor 的方案
- Projects 选择了 rowboatlabs/rowboat，因为它提供了本地优先的持久知识图谱，与 Article 的「规划-验证循环」在架构层面形成互补（工作流控制 + 上下文积累）
- Rowboat 的「显式关系」设计哲学与 Cursor 的「规划优先」模式异曲同工——都不是依赖模型自己记住，而是通过外部结构让记忆变得可审查和可控
- 保持了文章产出规范中的所有要求：核心论点明确、技术细节落地（架构图 + 案例数据）、判断性内容（Anthropic vs Cursor 对比）、原文引用（5处）

**待改进**：

- LangChain Interrupt 2026（5/13-14）窗口期临近，关注 Harrison Chase keynote 发布内容
- Anthropic「2026 Agentic Coding Trends Report」Trend 7（安全）和 Trend 8（Eval）深度分析（与 Cursor 的安全关键任务案例关联）
- OpenAI Symphony（Issue Tracker 作为 Agent Orchestrator）500% PR 增长数据待跟进

## 下轮方向

- **LangChain Interrupt 2026（5/13-14）Deep Agents 2.0**：关注框架级架构更新，预期 Harrison Chase keynote 发布
- **Anthropic「2026 Agentic Coding Trends Report」Trend 7（安全）和 Trend 8（Eval）深度分析**
- **OpenAI Symphony（Issue Tracker 作为 Agent Orchestrator）**：500% PR 增长，Linear 创始人关注

---

## 本轮数据

| 指标 | 数值 |
|------|------|
| 新增 articles 文章 | 1（harness）|
| 新增 projects 推荐 | 1 |
| 原文引用数量 | Article 5 处 / Project 5 处 |
| commit | 2（6609937 内容 + 499a53a HISTORY.md） |

---

*REPORT.md 由 AgentKeeper 自动生成，每轮覆盖写入。*