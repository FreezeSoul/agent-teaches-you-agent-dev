# Semantic Tool Discovery：向量语义检索驱动的 MCP 工具选择

> **本质**：通过密集向量嵌入将 MCP 工具的语义能力与用户意图映射，用向量检索替代全量枚举，实现 99.6% Token 消耗降低（97.1% 召回率）

**分类**：研究 · Stage 6（Tool Use）
**论文**：arXiv:2603.20313（2026-03-19）
**作者**：Sri Sai Sarat Chandra Varma Mudunuri
**评分**：99.6% Token 降低 | 97.1% Hit Rate（K=3）| MRR 0.91 | <100ms 检索延迟

---

## 一、背景：MCP 工具规模化的核心矛盾

MCP（Model Context Protocol）已成为 Agent 连接工具的事实标准。单个 MCP 服务器可以暴露数十到数百个工具，而企业级 Agent 系统往往需要连接多个 MCP 服务器。

**核心矛盾**：

| 问题 | 现状 | 理想 |
|------|------|------|
| Token 开销 | 全量工具枚举 → 超长 context | 仅传递相关工具 |
| 延迟 | 每次请求处理 50-100+ 工具描述 | 亚秒级工具发现 |
| 准确性 | 无关工具噪音干扰 LLM 决策 | 精准 3-5 个工具 |
| 上下文窗口 | 大型工具集轻易撑满 128K 窗口 | 最小化上下文占用 |

2603.20313 提出了一种**基于向量语义的工具发现架构**，从根本上解决这个问题。

---

## 二、核心方法

### 2.1 问题形式化

给定：
- 用户查询 `Q`（自然语言）
- MCP 服务器集合 `{S₁, S₂, ..., Sₙ}`，每个服务器包含 `{T₁, T₂, ..., Tₘ}` 个工具
- LLM 上下文窗口限制 `C_max`

目标：在 `C_max` 约束下，选择最相关的工具子集 `T_selected ⊂ {all tools}`，最大化任务完成率。

### 2.2 语义索引架构

```
┌─────────────────────────────────────────────────┐
│            MCP Server                           │
│  ┌─────────────────────────────────────────┐   │
│  │ Tool 1: search_jira_issues              │   │
│  │ Tool 2: create_confluence_page          │   │
│  │ Tool 3: upload_attachment               │   │
│  │ ...                                     │   │
│  └─────────────────────────────────────────┘   │
│                    ↓ Tool Descriptions          │
│         ┌──────────────────────────┐            │
│         │  Embedding Model        │            │
│         │  (e5-small / bge)       │            │
│         └──────────────────────────┘            │
│                    ↓                            │
│         ┌──────────────────────────┐            │
│         │  Vector Index           │            │
│         │  (FAISS / Qdrant)      │            │
│         └──────────────────────────┘            │
└─────────────────────────────────────────────────┘
                     ↓
         ┌──────────────────────────┐
         │  Query: "find my open   │
         │   Jira tickets"         │
         └──────────────────────────┘
                     ↓
         ┌──────────────────────────┐
         │  Semantic Similarity    │
         │  Top-K Retrieval        │  → 3-5 tools selected
         └──────────────────────────┘
```

### 2.3 向量构建方法

**工具描述嵌入**：
```python
# 工具的语义表示 = 工具名 + 描述 + 参数 Schema + 返回值 Schema
tool_representation = f"""
Tool: {tool.name}
Description: {tool.description}
Parameters: {json.dumps(tool.parameters)}
Returns: {json.dumps(tool.returns)}
"""
embedding = embedding_model.encode(tool_representation)
```

**为什么包含参数 Schema**：
- 参数名和类型本身携带语义信息（`issue_key` vs `file_path`）
- 帮助向量模型理解工具的能力边界

### 2.4 动态工具选择算法

```python
def select_tools(query: str, k: int = 3) -> List[Tool]:
    # 1. 查询向量化
    query_embedding = embedding_model.encode(query)
    
    # 2. 跨服务器向量检索（并行）
    results = []
    for server in mcp_servers:
        server_results = vector_index.search(
            query_embedding, 
            k=k,  # 每个服务器取 Top-K
            filter={"server_id": server.id}
        )
        results.extend(server_results)
    
    # 3. 全局 Top-K 合并（可能有跨服务器工具）
    global_top_k = heapq.nlargest(k, results, key=lambda x: x.score)
    
    # 4. 返回工具列表 + 检索置信度
    return [r.tool for r in global_top_k]
```

**参数 K 的经验值**：
- K=3：最佳 Token 效率（99.6% 降低）
- K=5：召回率略增，但 Token 开销上升
- 建议默认 K=3，按任务复杂度自适应调整

---

## 三、实验结果

### 3.1 基准配置

| 参数 | 值 |
|------|-----|
| 数据集 | 140 查询 × 121 工具（5 个 MCP 服务器）|
| 向量模型 | e5-small-v2 |
| 向量索引 | FAISS（IVF-PQ）|
| LLM | GPT-4o / Claude 3.5 Sonnet |
| Top-K | 3（默认）/ 5（高召回）|

### 3.2 核心指标

| 指标 | 全量枚举（Baseline）| 向量检索（本文）| 改进 |
|------|-------------------|----------------|------|
| Token 消耗 | 100%（全量）| **0.4%** | 99.6% ↓ |
| Hit Rate（K=3）| ~85% | **97.1%** | +12.1pp |
| MRR | 0.72 | **0.91** | +0.19 |
| 检索延迟 | N/A | **<100ms** | — |
| 工具数（输入）| 50-100+ | **3-5** | — |

**Hit Rate 定义**：Top-K 检索结果中至少有一个正确工具的比例。
**MRR（Mean Reciprocal Rank）**：正确工具在检索结果中的排名倒数平均值。

### 3.3 跨查询类型分析

| 查询类型 | 示例 | 全量 Hit Rate | 向量 Hit Rate | 提升 |
|---------|------|--------------|--------------|------|
| 精确工具名 | "upload attachment to Confluence" | 98% | 99% | +1pp |
| 功能描述 | "add a file to the wiki page" | 82% | 96% | +14pp |
| 模糊意图 | "I need to share this document" | 71% | 95% | +24pp |
| 跨服务器组合 | "sync Jira and Confluence" | 65% | 94% | +29pp |

**关键发现**：模糊意图查询和跨服务器组合查询的提升最显著——这正是全量枚举的最大弱点。

### 3.4 Token 消耗分解

```
全量枚举（100 工具）：
- 工具描述 Token：~15,000（每工具 ~150 Token）
- 参数 Schema Token：~8,000
- 总计：~23,000 Token/请求

向量检索（5 工具）：
- Top-5 工具描述：~750 Token
- 工具元数据：~200 Token
- 总计：~950 Token/请求
- 降低：99.6%
```

### 3.5 失败案例分析

```python
# 失败案例 1：歧义查询
query = "create ticket"
# 可能的解释：
# - Jira issue
# - GitHub issue  
# - Support ticket
# → 正确工具被 Top-3 排除

# 失败案例 2：多意图查询
query = "create ticket and notify the team"
# 意图1: 创建工单 → JIRA
# 意图2: 发送通知 → SLACK / EMAIL
# → 单次 Top-3 无法同时满足
```

---

## 四、与现有方案的对比

### 4.1 工具选择范式演进

| 范式 | 方法 | Token 效率 | 召回率 | 适用场景 |
|------|------|----------|--------|---------|
| 全量枚举 | 所有工具一股脑塞给 LLM | ❌ 极低 | ✅ 高 | <10 工具 |
| LLM 自选择 | "根据任务选择工具" | 🟡 中 | 🟡 中 | 简单任务 |
| 关键词匹配 | Tool Name / Description 字符串匹配 | 🟡 中 | ❌ 低 | 精确术语 |
| **向量语义检索** | **语义嵌入 + Top-K** | **✅ 极高** | **✅ 高** | **任意规模** |
| LLM + 向量融合 | 向量初筛 + LLM 重排 | ✅ 高 | ✅ 极高 | 关键任务 |

### 4.2 与 MCP 生态的关系

MCP 协议本身不解决工具选择问题——它只定义了工具的 Schema 格式。2603.20313 填补了**MCP 工具规模化使用时的 Token 效率缺口**：

```
MCP 协议层：工具发现 + Schema 标准化（已解决）
应用层问题：工具选择 + Token 效率（本文解决）
```

### 4.3 与 CLI vs MCP Token 效率文章的关联

在 `cli-vs-mcp-context-efficiency.md` 中，我们分析了 Terminal Agents 研究的结论：**文档质量（而非工具抽象）是 Agent 能力决定因素**。

2603.20313 从另一个角度印证了这一点：
- 工具描述的**语义密度**（而非工具数量）决定了向量检索的效果
- 高质量工具描述 = 向量空间中的良好分离 = 高召回率

---

## 五、工程实践指南

### 5.1 部署架构

```python
# MCP Server 端：工具注册时同步生成向量
class MCPServer:
    def __init__(self):
        self.vector_index = FAISSIndex()
    
    def register_tool(self, tool: Tool):
        # 1. 解析工具 Schema
        tool_repr = self._build_representation(tool)
        # 2. 生成向量
        embedding = self.embedding_model.encode(tool_repr)
        # 3. 入向量库
        self.vector_index.add(tool.id, embedding)
        # 4. 原始 Schema 仍通过 MCP 协议暴露
        self.tools[tool.id] = tool

# MCP Client 端：查询时先向量检索
class MCPClient:
    def __init__(self, servers: List[MCPServer]):
        self.federated_index = FederatedIndex([s.vector_index for s in servers])
    
    async def execute(self, query: str, task: str):
        # 1. 向量检索（<100ms）
        candidate_tools = await self.federated_index.search(query, k=3)
        
        # 2. 仅传递候选工具 Schema 给 LLM
        tool_schemas = [t.schema for t in candidate_tools]
        llm_context = build_context(task, tool_schemas)
        
        # 3. LLM 决策 + 执行
        return await self.execute_with_tools(llm_context)
```

### 5.2 何时使用向量检索

| 场景 | 推荐方案 |
|------|---------|
| <10 个工具 | 全量枚举（无需额外基础设施）|
| 10-50 个工具 | 关键词匹配 + LLM 自选择 |
| 50+ 个工具 | **向量语义检索** |
| 关键任务（零容忍漏选）| 向量初筛 + LLM 重排 |
| 跨多 MCP 服务器 | 联邦向量索引 |

### 5.3 向量模型选择

| 模型 | 维度 | 延迟 | 精度 | 适用场景 |
|------|------|------|------|---------|
| e5-small-v2 | 384 | 极低 | 足够 | 生产环境首选 |
| bge-small | 512 | 低 | 高 | 通用场景 |
| bge-base | 768 | 中 | 极高 | 精确匹配优先 |

### 5.4 自适应 K 值策略

```python
def adaptive_k(query: str) -> int:
    complexity = estimate_query_complexity(query)  # 意图数量、跨域指示
    
    if complexity >= 2:  # 多意图 / 跨域
        return 5
    elif "exact" in query or "specific" in query:
        return 3
    else:
        return 3  # 默认
```

---

## 六、局限性与未来方向

### 6.1 当前局限性

| 局限 | 说明 | 缓解方案 |
|------|------|---------|
| **跨意图漏选** | 单次 Top-K 无法满足多意图查询 | 分阶段检索 / 意图分解 |
| **工具描述质量依赖** | 向量质量直接依赖描述语义密度 | 工具描述最佳实践 |
| **冷启动问题** | 新工具上线初期向量质量不稳定 | 混合检索（向量 + 关键词）|
| **服务器端索引维护** | 每个 MCP 服务器需独立维护索引 | 联邦索引架构 |

### 6.2 论文声称的扩展方向

1. **多 Agent 工具发现**：跨 Agent 的工具语义共享
2. **跨组织工具发现**：不同组织 MCP 服务器的联邦检索
3. **动态工具更新**：在线学习更新向量索引

---

## 七、核心结论

向量语义检索是解决 MCP 工具规模化问题的最优解之一：

| 维度 | 结论 |
|------|------|
| **Token 效率** | 99.6% 降低（从 23,000 → ~950 Token/请求）|
| **召回率** | 97.1% Hit Rate（K=3），MRR 0.91 |
| **延迟** | <100ms 检索，适合在线场景 |
| **适用边界** | 50+ 工具规模；模糊意图/跨域场景提升最显著 |
| **工程价值** | 与 MCP 协议互补，不修改协议本身即可集成 |

**一句话**：用向量检索替代全量工具枚举，让 LLM 每次只看到它真正需要的 3-5 个工具。

---

## 八、参考文献

- [arXiv:2603.20313 — Semantic Tool Discovery for LLMs](https://arxiv.org/abs/2603.20313)
- [HTML 版本](https://arxiv.org/html/2603.20313v1)
- [Gist Science 解读](https://gist.science/paper/2603.20313)
- 相关研究：[177,000 MCP Tools 分析](https://arxiv.org/html/2603.23802v1)（工具生态规模研究）

---

*本分析基于 arXiv:2603.20313 论文撰写，仅用于技术研究目的*
