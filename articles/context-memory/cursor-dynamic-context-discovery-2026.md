# Cursor「动态上下文发现」— 从静态注入到按需拉取的技术解析

> **核心主张**：动态上下文发现将上下文管理从「注入式」转变为「按需拉取式」，让 Agent 能在长程任务中只加载当前所需的信息，避免上下文窗口被无关信息填满。这一设计选择反映了一个重要趋势——随着模型能力的提升，上下文工程的最佳实践正在从「给模型越多信息越好」转向「让模型自己判断需要什么」。

---

## 1. 问题：静态上下文注入的代价

在传统的 Agent 架构中，context engineering 的主流做法是将尽可能多的信息塞进 context window——项目结构、代码规范、历史对话、工具描述、所有 MCP 工具列表。这种「静态注入」模式的逻辑很直接：信息越多，模型决策越准确。

但 Cursor 的工程师观察到了两个反直觉的事实：

1. **Token 效率与信息量并非线性关系**：当 context window 塞满了大量当前任务不需要的信息时，模型需要在更多 token 中做区分，这反而增加了推理成本
2. **上下文膨胀会导致模型质量下降**：当 context 中的低价值信息占据比例过高时，模型更容易被无关内容干扰，做出次优决策

> "As models have become better as agents, we've found success by providing fewer details up front, making it easier for the agent to pull relevant context on its own."
> — [Cursor Engineering Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

这个观察是动态上下文发现范式的起点。其核心思想是：**不预先注入完整上下文，而是让 Agent 在需要时主动发现并加载所需信息**。

---

## 2. 动态上下文发现的核心机制

Cursor 的动态上下文发现在实践中体现为五个具体场景，每个场景都对应一个具体的工程解决方案。

### 2.1 长工具响应转换为文件

当 Agent 调用 shell 命令或 MCP 工具时，返回结果可能很长（例如 `grep -r` 整个代码库的结果），直接注入 context 会造成大量 token 消耗。

**传统做法**：截断（truncation）—— 只保留返回结果的前 N 个 token，但这会导致数据丢失

**Cursor 的做法**：
```
1. 工具响应写入本地文件
2. Agent 获得文件路径引用，而非完整内容
3. Agent 通过 tail/read 按需读取文件
```

这样 Agent 只需读取当前任务相关的部分，而非被迫处理完整输出。Cursor 官方数据显示，这减少了「不必要的上下文压缩」（unnecessary summarizations when reaching context limits）。

### 2.2 摘要后引用历史对话

当 context window 达到上限时，Agent 需要对历史对话做摘要（summarization），这是压缩信息的标准做法。但压缩本身是有损的——Agent 可能会丢失对解决问题至关重要的细节。

**Cursor 的解决方案**：将聊天历史本身作为文件暴露给 Agent。

```
context window 达到上限 → 触发摘要步骤 → Agent 获得历史文件引用
→ 如果 Agent 发现缺失信息 → 主动搜索历史文件恢复细节
```

这是「按需拉取」哲学的典型体现：**不假设 Agent 一定需要什么，而是让 Agent 自己判断缺失了什么并主动检索**。

### 2.3 Agent Skills 的动态加载

Cursor 支持 Agent Skills 开放标准，Skills 定义了 Agent 执行特定领域任务所需的指令和资源。Skills 包含名称和描述，这些信息可以作为静态 context 注入 system prompt。

但关键的设计在于：**Skill 的完整内容（instructions、scripts、resources）并不预先注入，而是让 Agent 在任务需要时动态发现**。

> "The agent can then do dynamic context discovery to pull in relevant skills, using tools like grep and Cursor's semantic search."
> — [Cursor Engineering Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

Agent Skills 的文件结构天然支持这种模式——它们以文件夹形式组织，包含 instructions、scripts、resources，Agent 可以通过 `grep` 或语义搜索找到与当前任务相关的 Skill 内容。

### 2.4 MCP 工具的按需加载

MCP（Model Context Protocol）服务器通常暴露大量工具，每个工具都有长描述。当一个 Agent 连接多个 MCP 服务器时，context window 很快会被工具描述填满——即使大多数工具在该任务中根本不会用到。

**传统做法**：所有 MCP 工具的完整描述始终在 prompt 中

**Cursor 的做法（关键优化）**：

1. 将 MCP 工具描述同步到本地文件夹（每个 server 一个子目录）
2. Agent 获得静态 context：工具名称列表 + 提示「需要时查询工具描述」
3. Agent 通过文件系统操作（grep/rg/jq）按需读取工具描述

Cursor 的 A/B 测试数据：

> "In runs that called an MCP tool, this strategy reduced total agent tokens by **46.9%**"
> — [Cursor Engineering Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

这是一个非常显著的结果，证明了「按需拉取」相比「静态注入」在 token 效率上的巨大优势。

### 2.5 终端会话作为文件系统

Cursor 的集成终端输出不再只是「显示给用户看」，而是同步到本地文件系统。这意味着 Agent 可以像访问代码文件一样访问终端历史。

**工程意义**：用户不需要手动 copy/paste 终端输出给 Agent，Agent 自己可以通过 `grep` 在长日志中定位关键信息。

---

## 3. 文件作为通用接口的设计哲学

贯穿上述所有场景的核心抽象是**文件**——不是数据库、不是 API、不是特殊的中间件，而是操作系统中最通用的文件概念。

为什么选择文件？

Cursor 的工程师在文章结尾给出了一个诚实的回答：

> "It's not clear if files will be the final interface for LLM-based tools. But as coding agents quickly improve, files have been a simple and powerful primitive to use, and a safer choice than yet another abstraction that can't fully account for the future."
> — [Cursor Engineering Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

这个回答体现了一种务实的工程态度：不追求完美的抽象，而是选择**当前最稳健、最不易过时**的方案。文件的几个优势：

1. **普遍性**：所有编程环境都支持文件操作，Agent 的工具调用能力天然匹配
2. **可组合性**：文件可以重组、压缩、索引，与现有的上下文工程工具链兼容
3. **无心智负担**：不需要引入新的抽象概念，工程师和模型都能直观理解

---

## 4. 与静态上下文注入的系统对比

| 维度 | 静态上下文注入 | 动态上下文发现 |
|------|---------------|---------------|
| **Token 使用** | 全部加载，按需处理 | 按需加载，节省 ~47% tokens（MCP 场景）|
| **信息完整性** | 预设完整，但可能包含无关信息 | 需要时才加载，可能遗漏（但 Agent 可主动检索）|
| **上下文窗口利用率** | 低（大量低价值 token 占据空间）| 高（每 token 都与当前任务相关）|
| **实现复杂度** | 低（直接注入）| 中等（需要文件系统同步、引用机制）|
| **适用场景** | 短程任务、信息确定性高 | 长程任务、信息不确定性高 |
| **模型自主性要求** | 低（模型被动接收）| 高（模型主动判断和检索）|

---

## 5. 适用边界与工程决策

动态上下文发现并非银弹。Cursor 明确指出其适用条件：

**适合的场景**：
- 长程任务（long-horizon tasks），上下文压缩频繁发生
- 多 MCP 服务器连接（工具数量 > 5 时收益明显）
- Agent 需要跨session 访问历史状态

**不适用的场景**：
- 短程任务：引入文件系统同步的开销可能大于收益
- 信息确定性高的任务：Agent 已经清楚知道需要什么，直接注入更高效
- 模型自主检索能力不足的场景：动态发现依赖模型主动判断「我需要什么」，如果模型这方面能力弱，可能漏掉关键信息

> 笔者认为：动态上下文发现是模型能力发展到一定阶段后的必然选择。当模型足够强大，能够准确判断「我需要什么」时，预先注入大量信息反而是一种浪费。但对于能力较弱或任务简单的模型，传统静态注入的确定性更强。

---

## 6. 工程落地检查清单

如果你的 Agent 项目正在考虑采用动态上下文发现模式，以下检查清单可供参考：

**架构检查**：
- [ ] 工具响应是否可能超过 1KB？考虑写文件而非直接返回
- [ ] MCP 工具数量是否超过 5 个？考虑动态加载
- [ ] 历史对话是否可能包含 Agent 后续需要的关键细节？考虑暴露历史文件

**Token 成本评估**：
- [ ] 估算当前上下文中的「低价值 token 比例」（理想 < 20%）
- [ ] 如果 MCP 工具列表占据 > 30% 的 context，优先优化

**Agent 能力要求**：
- [ ] 模型是否具备主动检索判断能力？（否则动态发现可能适得其反）
- [ ] 是否有文件系统操作工具支持 Agent 按需读取？

---

## 7. 启示：从「给模型越多越好」到「让模型自己判断」

动态上下文发现代表了 AI Coding Agent 上下文工程的一个范式转变：

**传统思维**：上下文是稀缺资源，应该尽可能把相关信息都塞进去
**新思维**：模型的判断能力提升后，让模型自己决定需要什么，比人类预设更高效

这种转变的前提是模型能力的跃升——当模型能够准确判断「我还需要什么」时，预注入大量信息不仅浪费 token，还可能制造干扰。

对于 Agent 工程师而言，这意味着：
1. **评估模型能力**成为上下文工程设计的第一步
2. **文件作为接口**是一个稳健的选择，值得在工具链设计中采用
3. **按需拉取**模式在长程任务中收益显著，值得在架构中预留支持

---

**引用来源**：
- [Dynamic context discovery - Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)
- [Cursor 3 announcement](https://cursor.com/blog/cursor-3)
- [Training Composer for longer horizons - Cursor Engineering Blog](https://cursor.com/blog/self-summarization)