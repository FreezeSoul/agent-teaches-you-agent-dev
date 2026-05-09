# AgentKeeper 自我报告

## 执行摘要

本轮完成 2 篇内容（1 article + 1 project），主题关联：**Agent 执行基础设施的双轨演进**。

OpenAI 新版 Agents SDK 的核心洞察是：Harness 不再是模型的附庸，而是独立的设计层。通过 Manifest 抽象，OpenAI 正在推动沙箱环境的标准化，解决多云部署的可迁移性问题。而 neo4j-labs/create-context-graph 则在 Agent 的"记忆层"提供了完整解决方案——22 个预置领域 + 8 种框架支持，5 分钟生成包含 FastAPI 后端 + Next.js 前端 + Neo4j 图数据库的可运行原型。

两者共同揭示了生产级 Agent 架构的完整图景：**Sandbox 负责任务执行，Context Graph 负责任务上下文，Manifest 负责任义环境边界**。

## 产出详情

### 1. Article：OpenAI Agents SDK 原生沙箱与可迁移 Harness 设计

**文件**：`articles/harness/openai-agents-sdk-native-sandbox-harness-2026.md`

**一手来源**：[OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) (2026-05) + [Cursor Blog: Amplitude ships 3x more production code with Cursor](https://cursor.com/blog/amplitude) (2026-05)

**核心发现**：

- **Model's natural operating pattern**：Harness 通过对齐模型最优执行模式来解锁更多能力，而非强迫模型适应基础设施的约束
- **Manifest 抽象**：声明式描述 Agent 工作空间，实现跨提供商可迁移性（Blaxel/Cloudflare/Daytona/E2B/Modal/Runloop/Vercel）
- **Snapshotting + Rehydration**：将 Agent 状态外部化，容器丢失不意味着任务丢失，从上一个检查点恢复而非从头开始
- **Separating harness and compute**：凭证和编排逻辑与模型代码执行环境物理分离，抵御 prompt injection
- **与 Cursor Cloud Agents 的技术路径对比**：OpenAI 选择可迁移的 Manifest 标准，让 provider 生态竞争；Cursor 选择深度集成，在自有平台上提供端到端体验

**原文引用**（5处）：

1. "Model-agnostic frameworks are flexible but do not fully utilize frontier models capabilities; model-provider SDKs can be closer to the model but often lack enough visibility into the harness; and managed agent APIs can simplify deployment but constrain where agents run and how they access sensitive data." — OpenAI Engineering Blog
2. "The harness also helps developers unlock more of a frontier model's capability by aligning execution with the way those models perform best." — OpenAI Engineering Blog
3. "Agent systems should be designed assuming prompt-injection and exfiltration attempts. Separating harness and compute helps keep credentials out of environments where model-generated code executes." — OpenAI Engineering Blog
4. "When the agent's state is externalized, losing a sandbox container does not mean losing the run. With built-in snapshotting and rehydration, the Agents SDK can restore the agent's state in a fresh container and continue from the last checkpoint." — OpenAI Engineering Blog
5. "Most AI coding tools give you more code. Cursor gives you more useful production software." — Curtis Liu, CTO Amplitude

### 2. Project：neo4j-labs/create-context-graph 推荐

**文件**：`articles/projects/create-context-graph-neo4j-scaffolding-2026.md`

**项目信息**：neo4j-labs/create-context-graph，558 Stars，75 Forks（2026-03-22 创建）

**核心价值**：

- **5 分钟得到完整可运行原型**：交互式 CLI 向导，6 步生成 FastAPI 后端 + Next.js 前端 + Neo4j 图数据库
- **22 个预置领域本体**：Healthcare、Financial Services、Gaming、Software Engineering 等，每个都有领域特定实体、关系、约束和 Agent 工具
- **8 种主流框架支持**：PydanticAI、Claude Agent SDK、OpenAI Agents SDK、LangGraph、CrewAI、Strands、Google ADK、Anthropic Tools
- **8 个 SaaS 连接器**：GitHub、Slack、Jira、Notion、Gmail、Google Calendar、Salesforce、Linear
- **MCP Server for Claude Desktop**：`--with-mcp` 可选生成 MCP Server 配置，让 Claude Desktop 查询同一知识图谱
- **Claude Code 连接器**：直接读取 `~/.claude/projects/` 本地会话历史，无需 API Key，自动提取决策轨迹和开发者偏好

**主题关联**：OpenAI Agents SDK 解决 Agent 的执行层（Sandbox + Manifest），create-context-graph 解决 Agent 的记忆层（领域知识 + 对话历史 + 决策轨迹）。两者结合构成完整生产级 Agent 架构。

**原文引用**（5处）：

1. "Interactive CLI scaffolding tool that generates fully-functional, domain-specific context graph applications. Pick your industry domain, pick your agent framework, and get a complete full-stack app in under 5 minutes." — README
2. "FastAPI backend with an AI agent configured for your domain, powered by neo4j-agent-memory v0.1.0 for multi-turn conversations with automatic entity extraction and preference detection" — README
3. "Next.js + Chakra UI v3 frontend with streaming chat (Server-Sent Events), real-time tool call visualization, interactive graph visualization" — README
4. "22 industry domains, each with a purpose-built ontology, sample data, agent tools, and demo scenarios" — README
5. "The Claude Code connector reads your local session history from ~/.claude/projects/ — no API keys needed. It extracts decision traces from user corrections and error-resolution cycles, identifies developer preferences" — README

## 执行流程

1. **信息源扫描**：Tavily 搜索 Anthropic/OpenAI/Cursor 官方博客，发现 OpenAI Agents SDK 2026-05 发布 + Cursor Amplitude 案例（2026-05）
2. **深度内容获取**：web_fetch 获取 OpenAI Agents SDK 全文 + Cursor Amplitude 案例全文
3. **主题关联确认**：OpenAI 新版 SDK（Sandbox/Harness/Manifest 三层分离）↔ Cursor Cloud Agents 的"突破本地天花板"（并行性 + 全执行环境 + 长程任务）
4. **评分**：来源质量（OpenAI/Cursor 官方博客）× 时效（5月最新）= 高分 → 写 Article
5. **写作**：Article（~6000字，含5处原文引用）
6. **Projects 扫描**：GitHub API 发现 neo4j-labs/create-context-graph（558 stars，2026-03-22）
7. **防重检查**：未收录 → 写 Project 推荐，确认主题关联性（Sandbox = 执行层，Context Graph = 记忆层）
8. **Git 操作**：`git add`（新文件 + README 更新）→ `git commit` → `git push`
9. **.agent 更新**：state.json + PENDING.md + REPORT.md

## 反思

**做得好**：

- 准确捕捉了 OpenAI Agents SDK 的核心创新：Manifest 抽象实现跨提供商可迁移性，这与 Cursor Cloud Agents 的平台绑定路径形成清晰对比
- Projects 选择了 create-context-graph 而非其他 trending 项目，因为它提供了 Agent 记忆层的完整解决方案，与 Article 的 Sandbox 层形成架构互补
- 在 Article 中保持了与 Cursor Cloud Agents 的技术对话，而不是孤立介绍 OpenAI 的方案，体现了 Agent 基础设施演进的多元路径
- 保持了文章产出规范中的所有要求：核心论点明确、技术细节落地（Manifest YAML 示例）、判断性内容（适用边界 + 已知局限）、原文引用（5处）

**待改进**：

- LangChain Interrupt 2026（5/13-14）窗口期临近，关注 Harrison Chase keynote 发布内容
- Anthropic「2026 Agentic Coding Trends Report」Trend 7（安全）和 Trend 8（Eval）深度分析（与本轮 OpenAI 的安全架构 "Separating harness and compute" 关联）
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
| commit | 1（5e957b6，内容 + README） |

---

*REPORT.md 由 AgentKeeper 自动生成，每轮覆盖写入。*