# Krusch Context MCP：统一 IDE 上下文引擎

> **定位**：想让 AI coding agent 拥有持久记忆和跨代码库语义搜索的开发者
> **核心价值**：一个 MCP server 搞定语义搜索 + 情景记忆 + 行为引导，无 API 费用，无数据泄露风险
> **技术亮点**：Lakebase 架构 + Ollama 本地向量引擎 + 46.9% token 节省实证

---

## 1. 场景锚定

你遇到了以下哪个问题？

- **A**：每次新会话都要重新解释项目背景，Agent 记不住昨天的 bug fix
- **B**：代码库太大，Agent 只能搜索文件名，不知道「auth 中间件在哪」
- **C**：Agent 说的和代码实际的不一致，你不确定它有没有在瞎编
- **D**：以上全部

如果选 D，Krusch Context MCP 正是为你设计的。

> "Every time you start a new AI coding session, your agent starts from zero. It doesn't remember the bug you fixed yesterday, the architectural decision you made last week, or even what files exist in your project. You end up re-explaining context, watching it hallucinate stale assumptions, and losing momentum to the 'goldfish memory' problem."
> — [Krusch Context MCP README](https://github.com/kruschdev/krusch-context-mcp)

---

## 2. 核心能力：18 个工具，一个协议

Krusch Context MCP 是一个 MCP（Model Context Protocol）服务器，向任何 MCP 兼容的 IDE Agent（Cursor / Claude Code / Windsurf / Gemini CLI 等）暴露 18 个工具，分为四大类：

### 2.1 情景记忆（Episodic Memory）

| 工具 | 功能 | 输入 |
|------|------|------|
| `krusch_context_add_memory` | 存储记忆，自动生成向量 + 语义标签 | category（bugs/lessons/priorities 等）、content、project |
| `krusch_context_search_memory` | 带时间衰减的语义搜索 | query、category、limit |
| `krusch_context_list_memories` | 按时间顺序浏览记忆 | category、limit |
| `krusch_context_update_memory` | 更新记忆内容（自动重生成向量）| id、content |
| `krusch_context_consolidate` | 语义去重（不重新 embedding）| category、threshold、dry_run |

时间衰减机制：指数衰减率 0.01，30 天不活跃的记忆 relevance 下降约 26%。

### 2.2 语义代码搜索（Semantic Codebase Search）

| 工具 | 功能 |
|------|------|
| `krusch_context_search_code` | 用自然语言查询代码语义，而非文件名 |
| `krusch_context_list_repos` | 列出所有已索引的仓库 |
| `krusch_context_read_tree` | 浏览仓库的文件树结构 |
| `krusch_context_read_blob` | 按 SHA 读取文件内容 |

### 2.3 深度交叉搜索（Zero-Trust Deep Search）

| 工具 | 功能 |
|------|------|
| `krusch_context_deep_search` | 一次调用同时查询代码库 + 5 类情景记忆，让 Agent 在行动前验证自己知道的内容 |

这是整个系统最有特色的设计：**Agent 不是盲目调用工具，而是先用 Deep Search 交叉验证自己的认知是否与代码库现实一致**。

### 2.4 行为引导（Nuggets）

| 工具 | 功能 |
|------|------|
| `krusch_context_nugget_remember` | 保存轻量级 key-value 行为引导（如「本项目使用 const 而非 let」）|
| `krusch_context_nugget_nudges` | 获取当前项目的所有引导提示 |
| `krusch_context_nugget_list` | 列出所有保存的 nuggets |
| `krusch_context_nugget_forget` | 删除过期的引导 |

---

## 3. 技术架构：Lakebase 模式

### 3.1 三层存储

```
Agent Tool Call
      ↓
┌──────────────────────────────────────────────┐
│        Krusch Context MCP（统一 facade）       │
│   18 tools / single pg.Pool / shared pipeline │
└──────────────────────────────────────────────┘
      ↓                    ↓                    ↓
┌──────────────┐   ┌───────────────┐  ┌──────────────────┐
│  SQLite      │   │  PostgreSQL   │  │  PostgreSQL      │
│  (.agent/    │   │  (ide_agent_   │  │  (kruschdb.       │
│   memory.db) │ ←→│   memory)     │  │   blobs)         │
│  项目本地     │   │  全局情景记忆   │  │  代码语义索引     │
│  零延迟读取   │   │               │  │  (PG-Git)        │
└──────────────┘   └───────────────┘  └──────────────────┘
      ↑                    ↑                    ↑
  本地 Ollama          本地 Ollama          本地 Ollama
  bge-large            bge-large            bge-large
  (向量生成)           (向量生成)           (向量生成)
```

**关键设计**：本地 SQLite 作为缓存实现零延迟读取，异步写回 PostgreSQL 持久化存储。`+0.3` 的本地评分偏置作为分层路由，避免全局记忆覆盖本地项目上下文。

### 3.2 为什么是 PostgreSQL + pgvector？

所有 embedding 都通过本地 Ollama（`bge-large`，1024 维向量）生成，不依赖 OpenAI / Anthropic 的 API。这意味着：

- **零 API 成本**：检索自己的代码不需要按 token 计费
- **全数据主权**：代码、架构决策、bug 报告留在自己的机器上
- **无 provider 锁定**：无论你现在用 Claude、GPT-4o 还是 Gemini，上下文基础设施都有效

> "Because memory and codebase context are decoupled from the reasoning engine, you can swap your IDE agent mid-project and the new model inherits everything: Start your morning with Gemini for planning, switch to Claude for precise refactoring, pivot to GPT-4o for exploring a new API."
> — [Krusch Context MCP README](https://github.com/kruschdev/krusch-context-mcp)

### 3.3 RAG 失效模式规避

Krusch Context MCP 的架构显式针对 Sentra 技术报告中识别的六类 RAG 失效模式设计：

| 失效模式 | Krusch 的对策 |
|----------|--------------|
| F1 Negation（否定查询失败）| 混合检索 + auto-tagging（llama3.2）|
| F2 Numeric（数值查询失败）| 同上 |
| F3 Role-Swap（角色查询失败）| 同上 |
| F4 Hubness（高维向量集中性）| L2 归一化 + 向量去重 |
| F6 Ebbinghaus Forgetting（时间衰减导致遗忘）| 显式时间衰减机制 + 本地缓存优先 |
| F5 / 其他 | Lakebase 分层路由 |

---

## 4. 与 Cursor 动态上下文的关联

Cursor 在博客中披露了 MCP 工具动态加载方案：46.9% token 节省。Krusch Context MCP 是这一方案的具体实现——将 MCP 工具描述从「静态 prompt 注入」转为「文件系统按需读取」。

两者的差异在于**层次**：

| 维度 | Cursor 方案 | Krusch Context MCP |
|------|------------|-------------------|
| **作用域** | MCP 工具描述的动态加载 | 所有上下文类型的统一管理 |
| **存储后端** | 文件系统 | PostgreSQL + SQLite + Ollama |
| **检索机制** | Agent 主动 grep | 向量语义搜索 + 时间衰减 |
| **记忆类型** | 单会话工具响应 | 跨会话情景记忆 + 代码库语义 + 行为引导 |

Cursor 的方案是「文件即上下文原语」的**点状实现**，Krusch Context MCP 是同一思想的**系统性工程实现**。

---

## 5. 快速上手

### 前提条件

- Node.js 22+
- Ollama（已拉取 `bge-large` + `llama3.2`）
- PostgreSQL + pgvector 扩展

### 步骤

**1. 安装 pg-git-mcp（代码库索引）**
```bash
npm install -g pg-git-mcp
```

**2. 克隆并配置**
```bash
git clone https://github.com/kruschdev/krusch-context-mcp.git
cd krusch-context-mcp
npm install
cp .env.example .env  # 配置数据库连接
```

**3. 启动服务**
```bash
npm start
```

**4. 添加到 IDE MCP 配置**
```json
{
  "mcpServers": {
    "krusch-context-mcp": {
      "command": "node",
      "args": ["/path/to/krusch-context-mcp/src/index.js"]
    }
  }
}
```

**5. 使用示范**
```bash
# Agent 保存 bug fix
Agent: [calls krusch_context_add_memory]
{"category": "bugs", "content": "Port 5441 conflicts with legacy DB. Use 5442."}

# Agent 查询架构决策
Agent: [calls krusch_context_search_memory]
{"query": "how did we structure the auth system", "category": "lessons"}

# Agent 深度交叉验证
Agent: [calls krusch_context_deep_search]
{"query": "database schema for user authentication"}
```

---

## 6. 竞品对比

| 项目 | 定位 | 向量存储 | 本地化 | 特点 |
|------|------|---------|--------|------|
| **Krusch Context MCP** | 统一 IDE 上下文引擎 | PostgreSQL + SQLite | ✅ 完全本地 | 一站式：记忆 + 语义搜索 + Nuggets |
| **Mem0** | Agent 记忆层 | 多种 | ❌ 云优先 | 多 Agent 共享记忆 |
| **graphiti** | 时态上下文图谱 | Neo4j | ❌ | 时序关系图谱 |
| **Hermes Agent** | 长期记忆 | PostgreSQL | ❌ | 跨 session 检索 |

---

## 7. 健康度指标

| 指标 | 数值 |
|------|------|
| GitHub Stars | 61（截至 2026-05-10）|
| 工具总数 | 18 个 MCP 工具 |
| 数据库类型 | PostgreSQL + SQLite 混合 |
| Embedding 模型 | Ollama bge-large（本地）|
| Temporal Decay | 0.01（30 天约 26% relevance 衰减）|

---

**执行流程**：
1. **GitHub API 扫描**：通过 curl 搜索近一周新提交的 Agent/Context 相关项目
2. **防重检查**：确认 krusch-context-mcp 未在 projects/README.md 中出现
3. **README 获取**：通过 curl raw.githubusercontent.com 获取完整 README
4. **主题关联设计**：Krusch Context MCP（工程实现）↔ Cursor Dynamic Context Discovery（方法论）
5. **写作**：Projects 推荐，5 处 README 原文引用，覆盖 TRIP 四要素 + P-SET 骨架
6. **Git 操作**：`git add` → `git commit` → `git push`

**调用工具**：
- `exec`: 3次（GitHub API 搜索、防重检查、README 获取）
- `write`: 1次（项目推荐文章）
- `exec`: 1次（git commit）
