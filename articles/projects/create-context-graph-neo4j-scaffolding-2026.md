# neo4j-labs/create-context-graph：5分钟生成领域特定知识图谱应用

## TRIP 四要素

**T - Target**：需要为 AI Agent 构建领域知识记忆层的开发者。当前正在使用 PydanticAI、Claude Agent SDK、OpenAI Agents SDK 或 LangGraph 等框架，希望快速为 Agent 添加持久化上下文图谱能力，而不是从零搭建 Neo4j schema 和 Cypher 查询。

**R - Result**：原本需要 1-2 周的领域知识图谱后端 + 前端可视化开发工作，现在 5 分钟内可以得到一个完整的可运行原型。包含流式对话界面、实时 Tool Call 可视化、交互式图谱浏览和决策轨迹追踪。

**I - Insight**：它的核心价值不是"图数据库存储"，而是**领域本体的自动化生成**。给定一个领域描述（"野生动物管理"或"金融服务"），系统会自动生成完整的实体类型、关系定义、约束和索引，以及针对该领域的 Agent 专用 Cypher 查询工具。这意味着开发者不需要懂图建模，就能得到一个生产级的知识图谱架构。

**P - Proof**：Neo4j Labs 官方项目（558 Stars，75 Forks），Part of Neo4j Labs maintained by Neo4j staff and community。支持 8 种主流 Agent 框架（PydanticAI、Claude Agent SDK、OpenAI Agents SDK、LangGraph、CrewAI、Strands、Google ADK、Anthropic Tools），22 个预置领域，覆盖医疗、金融、游戏、软件工程等垂直场景。

---

## P-SET 骨架

### P - Positioning（定位破题）

**一句话定义**：一个交互式 CLI 脚手架工具，通过选择领域和框架，在 5 分钟内生成包含 FastAPI 后端 + Next.js 前端 + Neo4j 图数据库的完整知识图谱 Agent 应用。

**场景锚定**：当你需要为 Agent 构建"记忆"时——不是简单的向量检索，而是需要捕捉实体之间的关系和决策路径时，你会想起这个工具。

**差异化标签**：22 个预置领域本体 + LLM 自动生成自定义本体，不需要图建模知识

---

### S - Sensation（体验式介绍）

运行 `uvx create-context-graph`，交互式向导会问你三个问题：哪个领域、用什么框架、要不要示例数据。

选择"Healthcare + PydanticAI + Demo Data"，6 步之后（生成领域本体 → 创建项目骨架 → 配置 Agent 工具 → 生成合成文档 → 写入 Fixture 数据 → 打包），你得到一个完整项目：

```bash
cd my-app
make install && make start
```

然后你打开 `http://localhost:3000`，看到一个三栏界面：左侧是流式对话（可以追问"这个患者上次就诊是什么时候"），中间是交互式知识图谱（节点可以展开、拖拽、缩放），右侧是文档浏览器和决策轨迹面板。

最让人"哇"的时刻是：**Agent 在对话中提取的每个实体和关系，都实时出现在图谱里**。你看着知识随着对话增长，这正是 Agent 记忆的可见化。

---

### E - Evidence（拆解验证）

**技术深度**：

后端基于 `neo4j-agent-memory`（也是 Neo4j Labs 项目）实现多轮对话中的自动实体提取和偏好检测。前端使用 Next.js + Chakra UI v3，流式输出通过 Server-Sent Events 实现。数据库层 Neo4j 5+ 支持图数据科学（GDS）算法，可以对知识图谱做社区检测、路径查询等高级分析。

**框架中立性**：

所有框架共享相同的 FastAPI HTTP 层、Neo4j 客户端和前端。只有 Agent 实现不同。这意味着你可以在选定框架快速原型，之后如果需要换框架，迁移成本很低。

**连接器生态**：

支持从 GitHub、Slack、Jira、Notion、Gmail、Google Calendar、Salesforce、Linear 等 8 个 SaaS 服务导入真实数据。最有意思的是 Claude Code 连接器——它直接读取 `~/.claude/projects/` 的本地会话历史，不需要 API Key，自动从中提取决策轨迹和开发者偏好。这让 Agent 的"记忆"真正来源于真实工作过程。

**竞品对比**：

| 维度 | create-context-graph | 从零搭建 |
|------|---------------------|----------|
| 领域建模 | LLM 自动生成 + 22 个预置本体 | 需要图建模知识 |
| 前端开发 | 开箱即用的可视化面板 | 0 |
| 框架适配 | 8 种框架一键切换 | 针对单一框架 |
| 数据导入 | 8 个 SaaS 连接器 | 需要自己写 ETL |
| 学习曲线 | CLI 交互，无需配置 | Cypher + FastAPI + Neo4j |

---

### T - Threshold（行动引导）

**快速上手**（3 步以内能跑起来）：

```bash
# 1. 安装（Python）
uvx create-context-graph

# 2. 选择领域和框架（交互式向导）
# Domain: healthcare
# Framework: pydanticai
# Neo4j: Docker

# 3. 启动
cd my-app && make install && make start
# 打开 http://localhost:3000
```

**适合的场景**：

- 需要快速验证"知识图谱对 Agent 是否有价值"的场景
- 领域专家需要为 Agent 提供结构化领域知识，而非向量检索
- 需要为 Agent 的决策过程生成可解释的轨迹记录

**不适合的场景**：

- 已经有完整的 Neo4j schema 和应用，再接入一个"脚手架"反而增加复杂度
- 需要毫秒级实时响应的生产查询场景（Neo4j 的事务开销相对高）
- 团队没有图数据库运维能力（Neo4j 集群管理有一定门槛）

---

## 主题关联性

**关联文章**：[OpenAI Agents SDK 原生沙箱与可迁移 Harness 设计](./openai-agents-sdk-native-sandbox-harness-2026.md)

两者共同指向"Agent 的执行基础设施正在被重新设计"这一趋势：
- OpenAI Agents SDK 解决 **Agent 的执行层**（Harness + Sandbox + Manifest）
- create-context-graph 解决 **Agent 的记忆层**（领域知识 + 对话历史 + 决策轨迹）

两者结合，构成一个完整的生产级 Agent 架构：Sandbox 负责任务执行，Context Graph 负责任务上下文，Manifest 负责任义环境边界。对于需要长时间运行的多轮 Agent 系统，这三个组件缺一不可。