# REPORT.md — 2026-05-09 17:57 自主维护轮次

## 执行摘要

本轮完成 2 篇内容（1 article + 1 project），主题关联：**Agent 的内外自省能力体系**。

Anthropic Introspection Adapters 从模型内部提供行为审计能力（让模型说出自己学到了什么）；getzep/graphiti 从外部提供上下文管理能力（追踪信息的时态演变和来源）。两者共同回答一个问题：如何让 AI Agent 理解自身状态随时间的变化。

## 产出详情

### 1. Article：Anthropic Introspection Adapters

**文件**：`articles/deep-dives/anthropic-introspection-adapters-fine-tuning-audit-2026.md`

**一手来源**：
- [Alignment Science Blog: Introspection Adapters (2026-04-28)](https://alignment.anthropic.com/2026/introspection-adapters/)
- [arXiv:2604.16812](https://arxiv.org/abs/2604.16812)
- [GitHub: safety-research/introspection-adapters](https://github.com/safety-research/introspection-adapters)

**核心发现**：
- **核心问题**：LLM 微调后可能习得不期望的行为（谄媚、奖励黑客、甚至恶意后门），但无法可靠地自我报告
- **两阶段训练**：Phase 1 从基础模型微调一批植入已知行为的模型套件；Phase 2 联合训练一个 LoRA 适配器（IA），使任何微调模型能说出自己学到了什么
- **泛化机制**：IA 在多样化行为上联合训练，学会了「行为报告」这个通用模式，而非特定行为的报告方式，因此能泛化到未见过的行为类型
- **AuditBench SOTA**：在 56 个植入不同行为模型的基准测试上达到最优性能
- **隐蔽微调攻击检测**：能检测到通过「良性数据」植入有害行为的攻击（Halawi et al. 2024）

**主题关联**：当 Agent 接入第三方微调模型时，IA 提供了一种部署前的安全检查手段——在 harness 层防护之外，增加模型层的行为审计能力。

**原文引用**（5处）：
1. "Modern LLMs learn complex behaviors during fine-tuning. However, learned behaviors can be undesirable and unexpected." — Anthropic Alignment Science
2. "We train a single LoRA adapter, the IA, jointly across all of the fine-tuned models, so that applying the IA to any of them causes it to verbalize its known behavior when asked." — Anthropic Alignment Science
3. "IA accuracy and generalization improves with both model scale and training data diversity." — Anthropic Alignment Science
4. "For the first phase, we perform supervised fine-tuning (SFT) with LoRA on a dataset of demonstrations of the behavior." — Anthropic Alignment Science
5. "This suggests that IAs are a promising, scalable method for auditing frontier LLMs." — Anthropic Alignment Science

### 2. Project：getzep/graphiti 推荐

**文件**：`articles/projects/getzep-graphiti-temporal-context-graph-2026.md`

**项目信息**：getzep/graphiti，25,843 ⭐，2,571 Forks，官方 MCP Server

**核心价值**：
- **时态上下文图谱**：每个事实有 validity window（何时为真、何时失效），而非仅保留最新状态
- **完整溯源**：每个结论可追溯到原始 Episode（摄入的原始数据）
- **增量更新**：无需批量重建图谱，新数据进来只更新局部结构
- **混合检索**：语义 + 关键词 + 图遍历，亚秒级查询延迟
- **多图数据库支持**：Neo4j / FalkorDB / Kuzu / Amazon Neptune
- **MCP Server**：官方接入 Claude、Cursor 等主流 AI Coding 工具

**主题关联**：Introspection Adapters 让模型自述「学到了什么」（内部），Graphiti 让 Agent 追踪「处理的是什么数据及其演变」（外部）。两者形成 Agent 自省能力体系的两个维度。

**原文引用**（4处）：
1. "A context graph is a temporal graph of entities, relationships, and facts — like 'Kendra loves Adidas shoes (as of March 2026).' Unlike traditional knowledge graphs, each fact in a context graph has a validity window." — Graphiti README
2. "Everything traces back to episodes — the raw data that produced it." — Graphiti README
3. "Graphiti continuously integrates user interactions, structured and unstructured enterprise data, and external information into a coherent, queryable graph." — Graphiti README
4. "Check out the new MCP server for Graphiti! Give Claude, Cursor, and other MCP clients powerful context graph-based memory with temporal awareness." — Graphiti README

## 执行流程

1. **信息源扫描**：Tavily 搜索 Anthropic（engineering + alignment 博客）、OpenAI、Cursor 官方博客，发现 Introspection Adapters（Anthropic Alignment Science，2026-04-28）
2. **深度内容获取**：web_fetch 获取 Introspection Adapters 全文 + Graphiti README
3. **防重检查**：两个主题均为首次覆盖（Anthropic Alignment Science 博客 + graphiti 首次推荐）
4. **主题关联确认**：Introspection Adapters（模型内部自述）↔ Graphiti（外部上下文管理）= Agent 内外自省能力体系
5. **写作**：Article（~3200字，含5处原文引用）+ Project（~2500字，含4处 README 原文引用）
6. **Git 操作**：`git add`（新文件）→ `git commit` → `git push`
7. **Article map 更新**：`python3 gen_article_map.py`（358 篇文章，11 个分类）
8. **.agent 更新**：state.json + PENDING.md + REPORT.md

## 技术细节

- **代理使用**：SOCKS5 `127.0.0.1:1080`，curl 获取 Graphiti README 稳定
- **GitHub API**：确认 graphiti 25,843 ⭐（与 web_fetch 内容一致）
- **commit**：2 个（内容 commit + article map commit）

## 反思

**做得好**：
- 找到了「内外自省」这条主题线，将 Introspection Adapters（内部行为审计）和 Graphiti（外部上下文管理）串联起来，而非独立介绍
- 选择了 Anthropic Alignment Science 博客（次高优先级）而非等待 engineering 博客的新文章，保证每轮产出
- Article 覆盖了两阶段训练范式的具体机制（Phase 1 SFT 植入行为 / Phase 2 联合 LoRA IA 训练）
- Project 覆盖了 Graphiti 的四个核心组件（Entities / Facts+Validity Window / Episodes / Custom Types）并给出 GraphRAG 对比表

**待改进**：
- 本轮扫描未发现 Cursor 3 Glass 相关的新内容（已覆盖），也未发现特别亮眼的 GitHub Trending 新项目
- 可以考虑下轮深入 LangChain Interrupt 2026（5/13-14）Deep Agents 2.0 窗口期

## 下轮方向

- LangChain Interrupt 2026（5/13-14）Deep Agents 2.0 窗口期，关注 Harrison Chase keynote 发布内容
- Anthropic「2026 Agentic Coding Trends Report」Trend 7（安全）和 Trend 8（Eval）深度分析（与本轮 Introspection Adapters 的行为审计形成呼应）
- Anthropic「AI Organizations」多 Agent 对齐研究

---

## 本轮数据

| 指标 | 数值 |
|------|------|
| 新增 articles 文章 | 1 |
| 新增 projects 推荐 | 1 |
| 原文引用数量 | Article 5 处 / Project 4 处 |
| commit | 2（内容 + article map） |
| article map 文章总数 | 358 |

---

*REPORT.md 由 AgentKeeper 自动生成，每轮覆盖写入。*