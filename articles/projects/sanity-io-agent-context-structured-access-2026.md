# Sanity Agent Context：结构化上下文访问的工程实践

> **核心论点**：Sanity Agent Context 代表了「Context as a Service」的可能——不是把文档向量化后做相似度搜索，而是让 Agent 直接用 GROQ 查询结构化数据。过滤精准度 + 语义搜索发现力，这是向量检索无法同时提供的组合。

## 1. 向量检索的根本局限

当前大多数 RAG 系统的逻辑是：**把所有内容向量化 → 用户提问 → 找最相似的 N 段文字**。

这个模式的局限在哪？

- **精确值查询弱**：当用户问「这款产品的库存是多少」「截止日期是几号」，向量检索只能找到「包含库存文字的相关段落」，而不是「精确的库存数值」
- **结构化关系丢失**：产品 → 品牌 → 品牌的其他产品，这条关系链在向量数据库里无法表达
- **元数据过滤难**：按分类、按价格区间、按发布时间过滤，向量检索要么做不到，要么做到的成本很高

> 官方原文引用：
> "Instead of vectorizing your content into embeddings and hoping similarity search returns the right answer, Agent Context lets agents query your actual data model: filter by fields, traverse references between documents, and combine structured queries with semantic search."
> — [Sanity Agent Context README](https://github.com/sanity-io/agent-context)

## 2. Agent Context 的解决思路

### 2.1 三工具架构

Agent Context 暴露三个 MCP 工具：

| 工具 | 作用 |
|------|------|
| `initial_context` | 返回压缩后的 schema 概览（content types、fields、document counts） |
| `groq_query` | 运行 GROQ 查询，支持可选的语义搜索 |
| `schema_explorer` | 返回指定 content type 的完整 schema |

### 2.2 GROQ 查询的精确 + 发现组合

这是 Agent Context 最精彩的设计——GROQ 查询可以同时写结构化过滤和语义排序：

```groq
*[_type == "product" && category == "shoes"]
  | score(text::semanticSimilarity("lightweight trail runner for rocky terrain"))
  | order(_score desc)
  { _id, title, price, category }[0...5]
```

**结构化过滤**（`category == "shoes"`）保证精准度，**语义排序**（`text::semanticSimilarity()`）提供发现力。一个查询，两种能力。

> 官方原文引用：
> "Embeddings for exploration, structured queries for precision."
> — [Sanity Agent Context README](https://github.com/sanity-io/agent-context)

### 2.3 引用遍历能力

Sanity 的文档模型支持引用（references）——产品引用品牌，品牌引用制造商。Agent Context 的 GROQ 可以遍历这些引用：

```
品牌 → 品牌的所有产品 → 每个产品的分类和库存
```

这个能力在向量数据库里几乎不可能优雅地实现。

## 3. 部署架构

### 3.1 连接模型

```
Your Agent → MCP → Agent Context (Sanity 托管) → Your Content (Sanity Content Lake)
```

Agent Context 是 Sanity 托管的 MCP 端点，你只需要：
1. 在 Sanity Studio 创建 Agent Context 文档
2. 获取生成的 MCP URL + API Token
3. 你的 Agent 通过这个 URL 连接

### 3.2 Skills 集成

> 官方原文引用：
> "If you're using Claude Code, Cursor, or similar, you can install skills that guide your AI assistant through the setup"
> — [Sanity Agent Context README](https://github.com/sanity-io/agent-context)

```bash
npx skills add sanity-io/agent-context --all
```

然后让 Agent 执行 `create-agent-with-sanity-context` skill，它会引导你完成 Studio 配置、MCP 连接和你的技术栈配置（Next.js/SvelteKit/Express/Python 等）。

## 4. Agent Insights：生产级遥测

Agent Context 还提供了内置的遥测能力：

- **自动对话保存**：通过 AI SDK 集成自动保存
- **AI 分类**：success score、sentiment、content gaps
- **Studio Dashboard**：分析和对话浏览

这个能力解决了生产环境的一个实际痛点：你怎么知道 Agent 回答得好不好？Agent Insights 提供了可量化的反馈。

## 5. 使用场景

**Agent Context 适合的场景**：
- 电商产品查询（库存、价格、规格的精确查询）
- 内容驱动的客服 Agent（访问 CMS 结构化内容）
- 知识库问答（精确的元数据 + 语义发现）

**Agent Context 不适合的场景**：
- 纯文档问答（向量检索更合适）
- 实时性要求极高的场景（每次查询都要走 Sanity API）
- 非结构化内容的处理

## 6. 技术评估

**优势**：
- 结构化查询 + 语义搜索的组合是目前 RAG 的最强解
- MCP 协议支持让它可以接入任何 MCP-compatible Agent
- Skills 集成让 Claude Code/Cursor 用户开箱即用
- GROQ 的表达能力远超简单的向量相似度

**局限**：
- 依赖 Sanity 作为 Content Lake——不是通用解，是 Sanity 用户的专有解
- 需要部署 Sanity Studio（v5.1.0+），上手有一定门槛
- MCP 端点由 Sanity 托管，数据要出墙（但 Sanity 是 GDPR 合规的）

**与 Cursor 动态上下文发现的主题关联**：两者都是 context engineering 的工程实践，但解决的问题正交——Cursor 解决的是「Agent 内部 context 的组织方式」（动态拉取 vs 静态注入），Sanity Agent Context 解决的是「外部数据如何高效接入 Agent」（结构化查询 vs 向量检索）。两者是互补关系，不是竞争关系。

---

**关联文章**：
- [Cursor 动态上下文发现](./cursor-dynamic-context-discovery-2026.md) — Agent 内部 context 组织（动态拉取）+ 外部数据接入（结构化查询）= 完整的 context 工程栈
- [Hermes Agent](./hermes-agent-nousresearch-self-improving-agent-2026.md) — 内部记忆系统（Hernes FTS5）+ 外部数据访问（Sanity Agent Context）= Agent 的完整数据层

---

*来源：[Sanity Agent Context](https://github.com/sanity-io/agent-context)（Sanity 官方维护，MIT License）*
