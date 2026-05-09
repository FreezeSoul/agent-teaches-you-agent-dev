# getzep/graphiti：面向 AI Agent 的时态上下文图谱

> **本文解决的问题**：当 AI Agent 在长程任务中处理不断变化的信息时，如何让它的「记忆」既能追踪事实的演变（而非仅仅保留最新状态），又能追溯每个结论的来源？Graphiti 通过时态上下文图谱（Temporal Context Graph）为这个问题提供了开源工程答案。

> **Tags**: `Context Memory` `Knowledge Graph` `Temporal Context` `MCP` `Agent Memory`

---

## 一、定位破题

### 1.1 一句话定义

Graphiti 是一个面向 AI Agent 的**时态上下文图谱引擎**——它不仅存储「什么是真的」，还存储「什么时候变成真的」「什么时候不再是真的」，以及「这个结论来自哪批原始数据」。

### 1.2 场景锚定

当你需要 AI Agent 处理以下场景时，Graphiti 是值得考虑的选项：
- **客户对话系统**：客户的偏好、需求、过往交互历史随时间演变，Agent 需要知道「三个月前的偏好现在还适用吗」
- **金融分析 Agent**：研报数据、公司事件不断更新，Agent 需要追踪「这个事实是什么时候确认的，是否已被新数据推翻」
- **代码审查/开发助手**：代码库的架构决策、依赖关系、设计模式随 PR 演进，Agent 需要理解「这个设计是为什么在什么时候做出的」

### 1.3 差异化标签

> "A context graph is a temporal graph of entities, relationships, and facts — like 'Kendra loves Adidas shoes (as of March 2026).' Unlike traditional knowledge graphs, each fact in a context graph has a validity window: when it became true, and when (if ever) it was superseded."
> — [GitHub: getzep/graphiti](https://github.com/getzep/graphiti)

**核心差异化**：其他 Context/RAG 方案关注「如何检索正确信息」，Graphiti 关注「如何管理信息的生命周期」——包括它的诞生、演变和失效。

---

## 二、体验式介绍

### 2.1 从「文档块」到「时态事实」

传统的 RAG 系统将文档切成块（chunks），当文档更新时，要么重新索引整个文档库，要么保留新旧两套碎片让 Agent 自己判断用哪个。

Graphiti 的做法完全不同：它从原始数据中提取**实体-关系-事实三元组**，每个三元组带有一个**有效期窗口**。

```
实体: Kendra
关系: loves
目标实体: Adidas shoes
有效期: [2026-03-01, 2026-05-01)  ← 这个时间段内为真
来源: Episode(id=e123, source="Mar 2026 conversation")
```

当新数据来了（例如 Kendra 在五月说她现在更喜欢 Nike），Graphiti 不会删除旧记录，而是：
1. 将旧记录的 validity window 截止到 2026-05-01
2. 创建一个新记录，有效期从 2026-05-01 开始

这意味着 Agent 可以问「2026 年 4 月的时候，Kendra 的鞋子偏好是什么？」——并且得到准确的答案。

### 2.2 追溯根源：每个结论都有 episode

> "Everything traces back to **episodes** — the raw data that produced it."
> — [GitHub: getzep/graphiti](https://github.com/getzep/graphiti)

当 Graphiti 告诉你「Kendra 喜欢 Adidas 鞋子」，你可以追问「你怎么知道的？」——它会告诉你这个结论来自某次客户对话（episode），你可以回溯到原始数据。

这种 provenance（溯源）能力对 Agent 工程至关重要：当 Agent 给出了错误建议时，开发者需要能够追溯到是哪个 source data 导致了错误结论。

### 2.3 增量更新，无需批量重建

> "Graphiti continuously integrates user interactions, structured and unstructured enterprise data, and external information into a coherent, queryable graph. The framework supports incremental data updates, efficient retrieval, and precise historical queries without requiring complete graph recomputation."
> — [GitHub: getzep/graphiti](https://github.com/getzep/graphiti)

传统的 GraphRAG 在数据更新时往往需要重新计算整个图谱（batch-oriented），Graphiti 支持增量更新——新数据进来时，只有相关的局部图谱需要更新，大幅降低维护成本。

---

## 三、拆解验证

### 3.1 架构设计

Graphiti 的上下文图谱包含四个核心组件：

| 组件 | 存储内容 | 说明 |
|------|---------|------|
| **Entities** | 实体节点 | 人、产品、策略、概念——带随时间演变的摘要 |
| **Facts/Relationships** | 带时态窗口的边 | 三元组（实体→关系→实体），每个事实有时态有效期 |
| **Episodes** | 原始数据流 | 摄入的原始数据——每个派生事实都可以追溯到这里 |
| **Custom Types** | 本体定义 | 通过 Pydantic 模型定义自定义实体和边类型 |

### 3.2 与竞品对比

| 维度 | GraphRAG | Graphiti |
|------|---------|---------|
| 适用场景 | 静态文档摘要 | Agent 的动态上下文 |
| 数据处理 | 批量处理 | 持续增量更新 |
| 知识结构 | 实体簇+社区摘要 | 时态上下文图——实体、有效期事实、episode |
| 检索方式 | 顺序 LLM 摘要 | 混合语义+关键词+图遍历 |
| 适应性 | 低 | 高 |
| 时态处理 | 基本时间戳跟踪 | 双向时态跟踪+自动事实失效 |
| 矛盾处理 | LLM 判断摘要 | 自动事实失效+保留历史 |
| 查询延迟 | 秒到数十秒 | 通常亚秒级 |
| 自定义实体类型 | 否 | 是，通过 Pydantic 模型 |

> 表格来源：Graphiti README 官方对比表

### 3.3 MCP Server：给 Agent 配备图谱记忆

> "Check out the new MCP server for Graphiti! Give Claude, Cursor, and other MCP clients powerful context graph-based memory with temporal awareness."
> — [GitHub: getzep/graphiti](https://github.com/getzep/graphiti)

Graphiti 提供了官方 MCP Server，这意味着它可以无缝接入 Claude Code、Cursor 等主流 AI Coding 工具。

支持的图数据库后端：
- Neo4j 5.26
- FalkorDB 1.1.2
- Kuzu 0.11.2
- Amazon Neptune Database / Neptune Analytics
- Amazon OpenSearch Serverless（全文搜索后端）

### 3.4 学术基础

> "Using Graphiti, we've demonstrated Zep is the State of the Art in Agent Memory."
> — [GitHub: getzep/graphiti](https://github.com/getzep/graphiti)

Graphiti 是 Zep 平台的开源核心，Zep 在论文 [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956) 中证明了其 SOTA 性能。

### 3.5 GitHub 热度

- ⭐ **25,843** Stars
- Fork **2,571**
- 趋势：被 Trendshift 标记为活跃仓库

---

## 四、行动引导

### 4.1 快速上手（3 步）

1. **安装**：`pip install graphiti-core`
2. **配置后端**：选择支持的图数据库（推荐 Neo4j）
3. **构建图谱**：定义 Episode → 提取事实 → 查询上下文

### 4.2 与 Anthropic Introspection Adapters 的互补

有趣的主题关联：Anthropic Introspection Adapters 让**模型**能够自述它学到了什么行为；Graphiti 让**Agent**能够追踪它在处理什么数据以及数据的演变。

两者都在解决「AI 系统需要理解自身状态随时间的变化」这个问题，只是角度不同：
- IA：从模型内部审计角度
- Graphiti：从外部上下文管理角度

### 4.3 适合的使用者

- **需要长程记忆的 Agent 开发者**：Context 窗口不够用，需要结构化记忆系统
- **多 Agent 协作场景**：不同 Agent 需要共享对「事实演变」的共同理解
- **金融/法律/医疗等合规场景**：需要完整的决策溯源能力

### 4.4 不适合的使用者

- 简单的 FAQ 问答机器人（传统 RAG 足够）
- 数据完全不更新的静态知识库
- 没有图数据库运维能力的团队

---

**一手来源**：
- [GitHub: getzep/graphiti](https://github.com/getzep/graphiti) (25.8k ⭐)
- [MCP Server for Graphiti](https://github.com/getzep/graphiti/blob/main/mcp_server/README.md)
- [arXiv:2501.13956 - Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956)
- [Zep Blog: State of the Art in Agent Memory](https://blog.getzep.com/state-of-the-art-agent-memory/)