# Volt — 无损上下文管理：确定性 LCM 架构的工程实现

> Volt 是在 Anthropic Engineering Blog 发布「Effective context engineering for AI agents」后仅数周出现的一个开源项目。它用确定性数据库后端替代了模型驱动的不确定性摘要决策，实现了真正的无损上下文管理。本文解读其核心架构设计。

---

## TRIP 四要素

| 要素 | 内容 |
|------|------|
| **T - Target** | 需要处理长程复杂任务的 Agent 开发者和用户，特别是需要跨天甚至跨周会话的编码 Agent 场景 |
| **R - Result** | 在 OOLONG long-context benchmark 的每个上下文长度（32K-1M tokens）上，使用 Opus 4.6 时得分均高于 Claude Code；异步压缩实现零等待；无限会话持久化 |
| **I - Insight** | 将内存架构的负担从模型移回引擎——确定性控制循环 + Postgres 事务存储 + 双态内存架构（Immutable Store + Active Context）替代模型的随机摘要决策 |
| **P - Proof** | 273 Stars（增长中），开源代码，LCM 技术论文已发布，Voltropy 团队发布 |

---

## P - Positioning（定位破题）

**一句话定义**：终端原生的 AI 编码 Agent，通过 Lossless Context Management（LCM）实现无限时长会话的确定性上下文管理。

**场景锚定**：当你运行一个编码 Agent 超过几小时，发现上下文窗口开始「遗忘」早期决策；或者等待 compaction 压缩时出现不可接受的延迟时，你会想起 Volt。

**差异化标签**：`确定性压缩 > 模型驱动的随机摘要` — 这是 Volt 与所有其他 Agent 框架最本质的区别。

---

## S - Sensation（体验式介绍）

想象你正在做一个跨越数周的大型代码库重构任务。第二周，你发现 Claude Code 开始「忘记」第一周做的架构决策。你开始花大量时间重新解释上下文。

Volt 试图解决这个问题。它没有试图让模型「学会」如何管理记忆，而是把记忆管理的责任从模型转移到确定性引擎。

**核心体验差异**：

- **Anthropic 风格**（Claude Code）：当 token 达到软阈值时，调用模型进行 summarization，模型需要「决定」何时摘要、如何摘要——这是随机的、概率性的
- **Volt 风格**（LCM）：确定性控制循环在模型外部驱动压缩，模型不参与压缩决策——没有等待、没有随机性

> "LCM addresses this by shifting the burden of memory architecture from the model back to the engine. Rather than asking the model to invent a memory strategy, LCM provides a deterministic, database-backed infrastructure."
> — [Volt LCM Technical Paper](https://papers.voltropy.com/LCM)

---

## E - Evidence（拆解验证）

### 核心架构：双态内存 + DAG 摘要

Volt 的 LCM 架构核心是双态内存系统：

- **Immutable Store**：每个用户消息、助手回复和工具结果都以原样持久化，从不修改。这是 Source of Truth。
- **Active Context**：每个回合实际发送到 LLM 的窗口，从最近的原始消息和预计算的摘要节点（Summary Nodes）混合组装。

摘要节点是从旧消息压缩而来的，是缓存，不是真实来源。原始消息被保存用于「无损检索」。

核心数据结构是一个在持久化存储中维护的 DAG（有向无环图），支持事务写入、外键完整性和索引搜索。

### 三级升级协议：保证收敛

当软阈值被超过时，LCM 执行压缩，异步且原子地将生成的摘要交换到上下文之间。如果某个摘要级别未能减少 token 计数，系统自动升级到更激进的策略，通过三级升级协议，最终以确定性回退结束，不需要 LLM 推理。这保证了收敛。

> "This guarantees convergence."
> — [Volt README](https://github.com/Martian-Engineering/volt)

### Dolt 检索遍历：无损指针链

Volt 的检索使用显式谱系指针，使归档记忆可遍历而无需猜测：

- **Pre-response hooks** 注入顶部记忆线索，包含摘要 ID、摘要类型元数据和谱系指针 ID
- 线索可能引用活跃的 **bindle** 或归档的 **archive_stub** 指针
- **lcm_describe** 显示谱系元数据（类型/级别、离上下文状态、指针目标、谱系闭合 ID），让 Agent 可以选择正确的节点进行遍历
- **lcm_expand** 然后沿着谱系追踪（包括归档指针）并展开到底层原始消息

### Operator-Level Recursion：控制流从随机层到确定性层

Volt 引入了 `LLM-Map` 和 `Agentic-Map` 工具，作为模型生成循环的替代方案。不是让模型编写循环，而是调用单个工具调用。引擎（而非概率模型）处理迭代、并发和重试。这将「控制流」逻辑从随机层移到了确定性层。

- **LLM-Map**：将 JSONL 输入文件中的每个项目作为独立 LLM API 调用处理，默认并发 16。适合高吞吐量、无副作用的任务，如分类、实体提取或评分。
- **Agentic-Map**：类似，但为每个项目生成完整的子 Agent 会话，每个子 Agent 可以访问工具（文件读取、网页获取、代码执行）。适合需要工具使用或多步推理的逐项处理。

### 大文件处理：外存引用 + 预计算探索摘要

对于超过 token 阈值的文件，Volt 不将文件加载到活跃上下文中，而是将文件存储在外部并插入紧凑引用：稳定的内容寻址 ID、文件路径和预计算的探索摘要（由类型感知的调度器生成，基于文件类型选择分析策略）。

### 基准验证

Volt with LCM 在 OOLONG long-context benchmark 上，在 32K 到 1M tokens 的每个上下文长度上，使用 Opus 4.6 时得分均高于 Claude Code。

---

## T - Threshold（行动引导）

### 快速上手

```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/Martian-Engineering/volt/dev/install | bash

# 配置 LCM 模式（upward 或 dolt）
export VOLTCODE_LCM_MODE=upward

# 配置 Provider（在 voltcode.json 中）
```

### 两种 LCM 模式

| 模式 | 行为 |
|------|------|
| `upward` | 默认模式，更积极的压缩 |
| `dolt` | 保留更多原始信息，压缩更少 |

### 与 Anthropic 上下文工程的关联

Volt 是 Anthropic Engineering Blog「Effective context engineering for AI agents」中描述的 Compaction 技术的工程实现：

| Anthropic 描述 | Volt 实现 |
|---------------|----------|
| Compaction | LCM 双态架构 + DAG 摘要 |
| 确定性压缩优于随机性 | 三级升级协议保证收敛 |
| Note-taking | Immutable Store + 外部文件引用 |
| Sub-agents | Agentic-Map operator |

---

## 防重索引

已在 `articles/projects/README.md` 中推荐的项目：
-Volt 未在其中，需要添加

---

*推荐阅读：[Volt LCM Technical Paper](https://papers.voltropy.com/LCM) — 确定性上下文管理的完整技术细节*