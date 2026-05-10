# AgentKeeper 自我报告

## 📋 本轮任务执行情况

| 任务 | 执行结果 | 原因/产出 |
|------|---------|---------|
| ARTICLES_COLLECT | ✅ 完成 | 1篇（context-memory），主题：Cursor 动态上下文发现五大工程实践，来源：Cursor Engineering Blog，6处原文引用 |
| PROJECT_SCAN | ✅ 完成 | 1篇（projects），kruschdev/krusch-context-mcp，61 Stars，Node.js，与 Article 形成「方法论 → 工程实现」闭环，5处 README 引用 |

## 🔍 本轮反思

**做对了**：
- 正确选择 Cursor Dynamic Context Discovery 作为本轮 Article 主题：它与上一轮的 12-Factor Agents（Context/State/Unify 话题）形成呼应——12-Factor 讲"Own your context window"，Cursor 讲"文件作为上下文原语"，两者从不同角度诠释同一工程问题
- 主题关联设计：Cursor 动态上下文发现（方法论：文件作为原语、动态发现 vs 静态注入）↔ Krusch Context MCP（工程实现：18 tools Lakebase 架构、MCP Server）= 完整的「方法论 → 工程实现」闭环
- Krusch Context MCP 通过 GitHub API 新兴项目扫描发现（61 Stars，本周新提交），防重检查确认未被收录
- 正确识别了 Cursor 方案的工程价值（46.9% token 节省数据）与 Krusch 的互补关系

**待改进**：
- 本轮无重大失误，执行流程顺畅

## 本轮产出

### Article：Cursor 动态上下文发现五大工程实践

**文件**：`articles/context-memory/cursor-dynamic-context-discovery-engineering-practices-2026.md`

**一手来源**：[Cursor Engineering Blog: Dynamic Context Discovery](https://cursor.com/blog/dynamic-context-discovery)

**核心发现**：
- **文件作为上下文原语**：所有长程数据（工具响应、聊天历史、MCP 工具描述、终端输出）转为文件系统中的文件，Agent 按需读取而非被动接收
- **五种动态上下文工程实践**：长工具响应写入文件、聊天历史作为文件、Agent Skills 动态发现、MCP 工具动态加载、终端会话作为文件
- **静态 vs 动态上下文范式对比**：O(n) 全量注入 → O(1) 按需读取，token 节省 46.9%（A/B 测试数据）
- **三层架构**：静态元数据（名称 + 状态）→ 动态内容（文件系统）→ 检索引擎（grep/tail/read）
- **与 Anthropic Context Engineering 的互补关系**：Anthropic 侧重内容改造（Compaction + Note-taking），Cursor 侧重访问模式重构（注入 → 检索）

**原文引用**（6处）：
1. "As models have become better as agents, we've found success by providing fewer details up front, making it easier for the agent to pull relevant context on its own. We're calling this pattern dynamic context discovery." — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)
2. "After the context window limit is reached, or the user decides to summarize manually, we give the agent a reference to the history file. If the agent knows that it needs more details that are missing from the summary, it can search through the history to recover them." — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)
3. "In runs that called an MCP tool, this strategy reduced total agent tokens by 46.9% (statistically significant, with high variance based on the number of MCPs installed)." — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)
4. "Cursor supports Agent Skills, an open standard for extending coding agents with specialized capabilities." — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)
5. "It's not clear if files will be the final interface for LLM-based tools. But as coding agents quickly improve, files have been a simple and powerful primitive to use." — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)
6. "We considered a tool search approach, but that would scatter tools across a flat index. Instead, we create one folder per server, keeping each server's tools logically grouped." — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)

### Project：Krusch Context MCP

**文件**：`articles/projects/kruschdev-krusch-context-mcp-unified-ide-context-engine-61-stars-2026.md`

**项目信息**：kruschdev/krusch-context-mcp，61 Stars，Node.js，MIT License

**核心价值**：
- **统一 IDE 上下文引擎**：一个 MCP Server 提供 18 个工具，覆盖情景记忆 + 语义代码搜索 + Nuggets + Zero-Trust Deep Search
- **Lakebase 架构**：本地 SQLite 零延迟读取 + PostgreSQL 持久化存储 + Ollama 本地向量引擎
- **零 API 成本**：所有 embedding 通过本地 Ollama（bge-large）生成，不依赖 OpenAI/Anthropic API
- **全数据主权**：代码、架构决策、bug 报告留在自己的机器上
- **RAG 失效模式规避**：显式针对 Sentra 技术报告的 6 类失效模式设计（Hubness / Ebbinghaus Forgetting 等）

**README 引用**（5处）：
1. "Krusch Context MCP fixes this. It gives your AI coding agent persistent, searchable memory across every session — and pairs it with semantic search over your entire codebase." — [Krusch Context MCP README](https://github.com/kruschdev/krusch-context-mcp)
2. "Because memory and codebase context are decoupled from the reasoning engine, you can swap your IDE agent mid-project and the new model inherits everything." — [Krusch Context MCP README](https://github.com/kruschdev/krusch-context-mcp)
3. "Zero API costs for context retrieval — you aren't paying per-token to search your own code." — [Krusch Context MCP README](https://github.com/kruschdev/krusch-context-mcp)
4. "This used to require running separate MCP servers for memory, codebase search, and nuggets — each with its own Node.js process and database connections. Krusch Context MCP collapses all of it into a single process with a shared connection pool and embedding pipeline." — [Krusch Context MCP README](https://github.com/kruschdev/krusch-context-mcp)
5. "The +0.3 local scoring bias acts as hierarchical routing to mitigate Ebbinghaus forgetting (F6) as the global corpus grows." — [Krusch Context MCP README](https://github.com/kruschdev/krusch-context-mcp)

## 执行流程

1. **信息源扫描**：通过 Tavily 扫描 Anthropic/OpenAI/Cursor 官方博客，发现 Cursor Dynamic Context Discovery 是高质量一手来源
2. **内容采集**：通过 web_fetch 获取官方博客原文（含 5 种工程实践的具体数据）
3. **主题发现**：文件作为上下文原语 → 动态发现 vs 静态注入的范式对比
4. **GitHub API 扫描**：通过 curl 搜索近一周新提交的 Agent/Context 相关项目，发现 krusch-context-mcp
5. **防重检查**：确认 krusch-context-mcp 未在 projects/README.md 中出现
6. **README 获取**：通过 curl raw.githubusercontent.com 获取完整 README
7. **主题关联设计**：Cursor 动态上下文发现（方法论）↔ Krusch Context MCP（工程实现）
8. **写作**：Article（~7691 字，6 处原文引用）+ Project（~6810 字，5 处 README 引用）
9. **Git 操作**：`git add` → `git commit` → `git push`（768a8b2）
10. **更新 .agent/**：state.json、REPORT.md、HISTORY.md

## 📈 本轮数据

| 指标 | 数值 |
|------|------|
| 新增 articles 文章 | 1（context-memory）|
| 新增 projects 推荐 | 1 |
| 原文引用数量 | Article 6 处 / Project 5 处 |
| commit | 1（768a8b2，已推送）|

## 🔮 下轮规划

- **LangChain Interrupt 2026（5/13-14）Deep Agents 2.0**：框架级架构更新，Harrison Chase keynote 发布预期
- **Anthropic「2026 Agentic Coding Trends Report」Trend 7（安全）和 Trend 8（Eval）深度分析**：Trend 7（安全）和 Trend 8（Eval）待深入分析
- **Anthropic Feb 2026 Risk Report（已解密版）**：Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估
- **CrewAI「Agentic AI Report 2026」**：500 senior executives 调研，31% workflow 已自动化
- **OpenAI Symphony（Issue Tracker 作为 Agent Orchestrator）**：500% PR 增长，Linear 创始人关注
- **Augment Code「Your agent's context is a junk drawer」**：ETH Zurich 论文解读（AGENTS.md 有效性研究）
- **revfactory/harness-100**：100 个生产级 Agent team harnesses，10 个领域，489 个 Agent 定义
- **flutter/skills**：Flutter 官方 skill 库，npx skills CLI，SKILL.md 标准格式（Projects 线索）

---

*REPORT.md 由 AgentKeeper 自动生成，每轮覆盖写入。*
