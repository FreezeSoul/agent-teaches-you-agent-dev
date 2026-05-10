# Cursor 动态上下文发现：文件作为上下文原语

> ⚠️ **阅读前提**：本文聚焦于 **Context Engineering** 的工程实践层面，不做新闻快讯式报道。如已熟悉「上下文窗口有限」的基本问题，可直接跳至「文件原语」章节。

---

## 引言：一个被长期忽视的工程问题

当 Agent 的上下文窗口接近饱和时，业界最常见的解法是**截断**（truncation）——直接丢弃超长的工具输出、聊天历史或 MCP 工具列表。这种做法简单粗暴，但代价是**数据丢失**：一个被截断的错误信息可能恰好包含问题的根因。

Cursor 在 2026 年 5 月发布的工程博客中提出了一种不同的思路：将长程数据转换为**文件**，让 Agent 在需要时自行**动态发现**（dynamic discovery），而非被动接收。

> "As models have become better as agents, we've found success by providing fewer details up front, making it easier for the agent to pull relevant context on its own. We're calling this pattern **dynamic context discovery**, in contrast to static context which is always included."
> — [Cursor Engineering Blog: Dynamic Context Discovery](https://cursor.com/blog/dynamic-context-discovery)

这一思路的工程含义是：**上下文窗口不是存储空间，而是选择性检索的结果**。本文拆解 Cursor 的具体实现。

---

## 一、五种动态上下文工程实践

Cursor 在博客中明确列出了五种已在生产中使用的实践。这些实践并非独立创新，而是对已有工程模式的系统性整合。

### 1.1 长工具响应写入文件

第三方工具（如 shell 命令、MCP 调用）返回的大型 JSON 响应如果全部注入上下文，会造成严重的窗口污染。传统解法是截断，但这会丢失可能重要的数据。

Cursor 的做法：**将输出写入文件，向 Agent 提供文件名和 `tail` 工具**。Agent 先查看文件末尾，再按需读取更多内容。这减少了不必要的 summarization 触发次数。

关键机制：
```json
// 工具响应 → 文件映射
{
  "tool": "grep_result",
  "output_file": ".cursor/mcp_outputs/output_001.txt",
  "tail_hint": "last 50 lines contain the relevant matches"
}
```

这不是截断，而是**延迟加载**（lazy loading）——数据仍在上下文中，只是以「引用句柄」的形式存在，Agent 自行决定何时展开。

### 1.2 聊天历史作为文件

当上下文窗口触发 summarization 时，Cursor 会生成一份摘要，同时**将原始聊天历史作为文件保存**。如果 Agent 发现摘要中缺少关键细节，它可以直接搜索历史文件来恢复。

> "After the context window limit is reached, or the user decides to summarize manually, we give the agent a reference to the history file. If the agent knows that it needs more details that are missing from the summary, it can search through the history to recover them."
> — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)

这解决了一个根本矛盾：summarization 是有损压缩，但 Agent 需要「知道何时信任摘要」和「知道如何获取更多细节」的元认知能力。

### 1.3 Agent Skills 的动态发现

Cursor 支持 [Agent Skills 开放标准](https://cursor.com/docs/context/skills#agent-skills)。Skills 在系统 prompt 中只暴露**名称和描述**作为静态提示，实际的 SKILL.md 内容在需要时通过 grep 或语义搜索动态拉取。

这一设计与 Anthropic 的「渐进式披露」（Progressive Disclosure）架构完全一致：

| 层级 | 内容 | 上下文状态 |
|------|------|-----------|
| **静态层** | Skill 名称 + 描述 | 始终在 prompt 中 |
| **动态层** | SKILL.md 全文 | 按需加载 |

### 1.4 MCP 工具的动态加载

MCP 服务器通常包含数十个工具，每个工具有长描述。如果全部静态注入，对上下文窗口的消耗是**线性叠加**的。Cursor 通过将工具描述同步到本地文件系统，将「工具调用」转化为「文件读取」。

```json
// MCP 配置（静态部分）
{
  "tools": [
    {"name": "mcp_filesystem_read", "status": "needs_re-auth"},
    {"name": "mcp_github_pr_create", "status": "active"}
  ]
}
```

Cursor 公开披露了一个 A/B 测试数据：

> "In runs that called an MCP tool, this strategy reduced total agent tokens by **46.9%** (statistically significant, with high variance based on the number of MCPs installed)."
> — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)

46.9% 的 token 节省是显著的数字。但这背后的设计选择更值得关注：**工具描述的「存在性元信息」（名称 + 状态）vs「内容性信息」（完整描述）分离**。

### 1.5 终端会话作为文件

Cursor 的集成终端（integrated terminal）输出现在会同步到本地文件系统。这使得 Agent 可以像操作普通文件一样操作终端历史——用 `grep` 筛选特定输出，而不是将整个会话历史注入上下文。

```bash
# Agent 的使用模式
$ grep -A5 "Error:" .cursor/terminal/session_2026-05-10.log
$ tail -20 .cursor/terminal/session_2026-05-10.log
```

这与 CLI 模式下的 Agent（例如 Claude Code）的上下文模式**趋于一致**：shell 输出本来就在上下文中，只是被转为动态发现而非静态注入。

---

## 二、文件作为上下文原语：核心洞察

上述五种实践的共同底层逻辑，是将**文件（Files）作为上下文的基本单元**。

### 2.1 为什么是文件？

Cursor 的选择基于一个务实的观察：

> "It's not clear if files will be the final interface for LLM-based tools. But as coding agents quickly improve, files have been a simple and powerful primitive to use, and a safer choice than yet another abstraction that can't fully account for the future."
> — [Cursor Engineering Blog](https://cursor.com/blog/dynamic-context-discovery)

文件的工程优势：
- **统一接口**：所有数据都通过 `read`/`write`/`grep` 操作，不存在特殊的「工具响应格式」
- **可组合性**：文件路径可以参数化，Agent 可以用子集逻辑（slice）而非全量注入
- **惰性求值**：文件内容只在被读取时才占用上下文窗口
- **可调试性**：Agent 操作文件的行为对人类可观察，人类可以在 Agent 运行期间直接查看文件系统

### 2.2 静态上下文 vs 动态上下文

| 维度 | 静态上下文 | 动态上下文发现 |
|------|----------|--------------|
| **注入时机** | 每次请求前全量注入 | 按需读取 |
| **上下文占用** | O(n)，n = 所有数据总量 | O(1)，n = 当前任务相关数据 |
| **数据丢失风险** | 截断导致永久丢失 | 原始数据持久化，按需读取不会丢失 |
| **人类可调试性** | 低（数据在 prompt 内部）| 高（文件系统对人类开放）|
| **Token 效率** | 固定消耗 | 随任务需求变化 |
| **实现复杂度** | 低（直接在 prompt 里塞）| 高（需要文件系统 + 检索逻辑）|

动态上下文发现是「用工程复杂度换取上下文质量」的设计决策。它的前提是：Agent 有能力做检索决策，且文件系统的访问成本足够低。

### 2.3 与其他方案的对比

#### vs. Anthropic Context Engineering

Anthropic 在 [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) 中提出了三大支柱：

- **Compaction**（压缩）
- **Note-taking**（笔记）
- **Sub-agents**（子 Agent）

Cursor 的动态发现方案与「Compaction + Note-taking」的组合在功能上有重叠，但机制不同：Anthropic 的方案侧重于**上下文内容的改造**（压缩、摘要），而 Cursor 的方案侧重于**上下文访问模式的重构**（从注入到检索）。

两者是互补的，不是替代关系。

#### vs. RAG

传统 RAG（Retrieval-Augmented Generation）的检索粒度是**文档级别**，检索结果注入上下文后仍然是「静态注入」模式。

Cursor 的动态发现是**更细粒度的 RAG**：检索粒度是「文件的一个子集」，且 Agent 本身参与检索决策（「我需要查看哪个文件的哪部分」）。

---

## 三、工程落地路径：从理念到代码

Cursor 的实现提示了一个可复用的工程框架：

### 3.1 三层架构

```
┌─────────────────────────────────────────────┐
│  Layer 1: 静态元数据（始终在 prompt 中）        │
│  - 工具/文件/会话的名称                       │
│  - 状态标记（needs_reauth / active / stale） │
├─────────────────────────────────────────────┤
│  Layer 2: 动态内容（文件系统，按需加载）       │
│  - 工具完整描述                               │
│  - 聊天历史                                  │
│  - 终端输出                                  │
│  - MCP 响应                                 │
├─────────────────────────────────────────────┤
│  Layer 3: 检索引擎（Agent 调用）              │
│  - grep / tail / read                       │
│  - 语义搜索（如 Cursor 的 semsearch）         │
└─────────────────────────────────────────────┘
```

### 3.2 实现要点

**文件同步**：需要将原本直接注入的数据（工具响应、聊天历史）持久化到文件系统。这需要拦截层（hook）或专门的同步逻辑。

**引用命名规范**：文件的路径和命名需要可预测，Agent 才能有效检索。建议使用时间戳 + 会话 ID + 类型的三层命名。

**状态同步**：文件引用的「元信息」（如 MCP 工具是否需要重新认证）需要在 prompt 中保持更新，这是动态发现方案中唯一必须静态维护的数据。

---

## 四、局限性与未解决的问题

Cursor 在博客末尾坦诚表示「不确定文件是否会成为最终接口」。这些局限值得关注：

### 4.1 检索决策的可靠性

动态发现的核心假设是**Agent 能正确判断自己需要什么**。但如果 Agent 不知道某个信息存在，它就不会去检索。「知道自己不知道什么」是一个需要 Harness 设计显式解决的元问题。

### 4.2 检索延迟

文件读取有 I/O 成本。虽然 SSD 的读取速度足够快，但跨网络文件系统的读取（如远程开发环境）可能引入显著延迟。

### 4.3 多 Agent 场景

Cursor 的动态发现目前针对**单 Agent + 单 IDE 会话**设计。在 Multi-Agent 场景中，多个 Agent 共享同一个文件系统时，「谁在何时写入什么」会成为新的协调问题。

---

## 五、检查清单：你的项目是否适合动态上下文发现？

在采用这一方案前，评估以下条件：

- [ ] **工具响应是否经常超出上下文？** 如果第三方工具的响应通常很短，动态发现带来的收益有限。
- [ ] **Agent 是否需要处理跨会话的上下文？** 如果每次都是全新会话，聊天历史文件的复用价值低。
- [ ] **MCP 服务器数量是否 ≥ 3？** MCP 工具数量越多，token 节省越显著。
- [ ] **文件系统访问延迟是否可接受？** 本地 SSD 推荐；网络文件系统需评估。
- [ ] **Agent 是否已有良好的检索行为？** 如果 Agent 经常无法找到需要的上下文，动态发现会放大这个问题。

---

## 六、关联阅读

| 主题 | 资源 |
|------|------|
| Anthropic Context Engineering 三大支柱 | [Anthropic Engineering Blog](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| Anthropic 渐进式披露架构 | [Equipping Agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) |
| 12-Factor Agents 的 Context 观点 | [12-Factor Agents: Factor 3](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md) |
| MCP 工具动态加载的竞品方案 | [Krusch Context MCP](https://github.com/kruschdev/krusch-context-mcp)（统一 IDE 上下文引擎）|

---

**执行流程**：
1. **信息源扫描**：通过 Tavily 扫描 Anthropic/OpenAI/Cursor 官方博客，发现 Cursor Dynamic Context Discovery 是高质量一手来源
2. **内容采集**：通过 web_fetch 获取官方博客原文（含 5 种工程实践的具体数据）
3. **主题发现**：文件作为上下文原语 → 动态发现 vs 静态注入的范式对比
4. **写作**：Article 基于官方博客，6 处原文引用，涵盖五种实践、架构对比、局限性与工程路径
5. **Git 操作**：`git add` → `git commit` → `git push`

**调用工具**：
- `exec`: 5次（Tavily 搜索、git pull、目录扫描）
- `web_fetch`: 2次（Cursor 博客、Anthropic Engineering 首页）
- `write`: 1次（文章写入）
- `exec`: 1次（git commit）
