# 动态上下文发现：Cursor 与 mcp-agent 的 Token 效率工程对比

> **本文核心论点**：上下文管理的范式正在从「预先注入」转向「动态发现」——通过将信息转为文件、按需加载工具、压缩聊天历史，Agent 仅在真正需要时才检索上下文。这种从 Static Context 到 Dynamic Context Discovery 的转变，本质上是用「延迟计算」换取 Token 成本的可控性。Cursor 和 mcp-agent 从两个不同角度验证了这条路的可行性。

---

## 背景：Static Context 的困境

传统 Agent 的上下文管理是**预先加载式**的：系统prompt塞满规则、工具描述、聊天历史，Agent在「充裕」的上下文中工作。这种模式的代价：

- **Token 成本线性增长**：每轮对话都携带完整历史，上下文窗口迟早会满
- **信噪比下降**：大量「可能有用」的信息稀释了真正相关的上下文
- **长尾场景爆炸**：MCP服务器工具描述、终端输出、聊天历史全部涌入context

Anthropic 的 2026 Agentic Coding Trends Report 给出了量化背景：

> "In 2026, agents will be able to work for days at a time, building entire applications and systems with minimal human intervention."
> — [Anthropic: 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)

当任务从「几分钟」扩展到「几天」，Static Context 的不可持续性被放大。一个7小时、12.5M行代码库的任务（如 Rakuten 用 Claude Code 在 vLLM 上实现激活向量提取）不可能把整个过程历史塞进 context window。

---

## 动态上下文发现的核心机制

### 1. 长工具响应 → 文件化

**问题**：Shell 命令和 MCP 调用返回的 JSON 可能很长，直接塞进 context 会导致不必要的截断。

**Cursor 的方案**：

```python
# 工具响应写文件而非直接返回
# Agent 用 tail 检查末尾，按需读取更多
```

这是将**流式输出**转为**随机访问文件**的核心思想。Agent 有了「tail + read」的能力后，不再需要在第一次调用时就获取完整输出——它可以按需索取。

### 2. 聊天历史 → 可检索文件

**问题**：Summarization 是有损压缩，Agent 可能在压缩后丢失关键细节。

**Cursor 的方案**：Summarization 后，Agent 获得聊天历史文件的引用。如果它意识到摘要缺少某些关键信息，可以自己 grep 历史文件来恢复。

> "If the agent knows that it needs more details that are missing from the summary, it can search through the history to recover them."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

这解决了 Summarization 的核心痛点：**信息损失没有倒逼机制**。传统模式下，Agent 被迫「遗忘」，因为压缩不可逆。而文件化+按需检索把压缩变成了可选的优化，而非强制的信息丢弃。

### 3. MCP 工具 → 动态按需加载

**问题**：一个 MCP 服务器可能有几十个工具，每个工具的描述都塞进 system prompt。实际上大多数任务只需要其中1-2个。

**Cursor 的方案**（关键数据）：

> "In an A/B test, we found that in runs that called an MCP tool, this strategy reduced total agent tokens by **46.9%** (statistically significant, with high variance based on the number of MCPs installed)."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

46.9% 的 Token 节省来自一个简单的设计：**工具描述同步到文件系统，Agent 获得小量静态上下文（工具名列表）后，在需要时才 grep 对应工具**。

**mcp-agent 的对应设计**：

mcp-agent 实现了完整的 MCP 生命周期管理，但它的核心理念更激进：

> "mcp-agent's vision is that _MCP is all you need to build agents, and that simple patterns are more robust than complex architectures for shipping high-quality agents_."
> — [GitHub: lastmile-ai/mcp-agent](https://github.com/lastmile-ai/mcp-agent)

mcp-agent 的 MCP 动态加载体现在其架构设计中：**MCPApp 管理 MCP 服务器连接生命周期，Agent 可以动态 attach/detach 服务器**，而非在启动时全部加载。

### 4. Agent Skills → 描述即入口，文件即实现

**Cursor 对 Agent Skills 的动态发现设计**：

Skills 的 name/description 作为静态上下文进入 system prompt（因为简短，适合预加载）。而 Skills 本身的内容（定义文件、可执行脚本）以文件形式存在于文件系统，Agent 在需要时通过 grep/semantic search 找到它。

> "Skills can also bundle executables or scripts relevant to the task. Since they're just files, the agent can easily find what's relevant to a particular skill."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

### 5. 终端会话 → 文件化历史

Cursor 将集成终端的输出同步到本地文件系统。Agent 可以 grep 日志、定位失败原因，而不需要在 context 中维护一个持续增长的终端历史 buffer。

---

## 技术演进：从「记住一切」到「知道在哪找」

动态上下文发现背后有一个认知层面的转变：

| 维度 | Static Context | Dynamic Context Discovery |
|------|---------------|---------------------------|
| 信息访问 | 预加载，用空间换时间 | 按需加载，用时间换空间 |
| 上下文增长 | O(n)，每轮线性累积 | O(1)，常数空间 |
| Agent 能力假设 | 需要完整的当前状态 | 只需要「如何找到信息」 |
| 信息损失 | 无（全部保留） | 有（压缩/丢弃），但有检索路径 |
| 适用场景 | 短任务、确定性上下文 | 长时任务、不确定上下文 |

Anthropic 的 Trends Report 在这个方向上提供了宏观背景：

> "Teams maintain quality and velocity simultaneously by building intelligent systems that handle routine verification while escalating genuinely novel situations, boundary cases, and strategic decisions for human input."
> — [Anthropic: 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)

这里的「intelligent systems」部分包括了**上下文管理**——Agent 需要知道什么时候该检索、什么时候该压缩、什么时候该请求人工介入。

---

## 两种实现路径的对比

### Cursor：文件作为文件系统级的抽象

Cursor 的动态上下文发现核心依赖**文件系统作为存储层**。工具响应、聊天历史、终端输出都以文件形式存在于本地。Agent 通过标准的文件系统操作（grep、tail、read）按需访问。

优点：
- 透明，Agent 可以用已有的工具访问
- 不需要额外的协议或基础设施
- 与本地开发环境天然整合

局限：
- 依赖本地文件系统，云端/远程场景需要额外同步
- 文件内容的语义索引需要 Agent 自己的推理能力

### mcp-agent：MCP 协议作为编排层

mcp-agent 的方案是**MCP 服务器按需连接**：MCPApp 管理多个 MCP 服务器的连接生命周期，Agent 在需要时动态 attach。这种模式更适合云端部署和分布式场景。

优点：
- 云端部署原生支持（mcp-agent cloud deploy）
- 标准化协议，不依赖本地文件系统
- 与 Temporal 结合，支持长时任务的 pause/resume

局限：
- 需要 MCP 服务器支持动态工具发现协议
- 依赖 MCP 协议生态的成熟度

---

## 共同的设计哲学：简单原语 > 复杂抽象

Cursor 团队在文末点出了核心原则：

> "It's not clear if files will be the final interface for LLM-based tools. But as coding agents quickly improve, files have been a simple and powerful primitive to use, and a safer choice than yet another abstraction that can't fully account for the future."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

mcp-agent 的设计哲学也呼应这一点：

> "simple patterns are more robust than complex architectures for shipping high-quality agents"
> — [GitHub: lastmile-ai/mcp-agent](https://github.com/lastmile-ai/mcp-agent)

两个项目都选择了**简单原语**（文件/MCP）而非**复杂抽象**（自定义协议/图结构），因为在 Agent 能力快速演进的阶段，过于复杂的抽象会很快过时。

---

## 启示：Context Engineering 的下一站

从 Anthropic 的 Context Engineering（压缩时机选择）到 Cursor 的 Dynamic Context Discovery（按需发现），再到 mcp-agent 的 MCP 原生 Agent 框架，这条线索指向同一个结论：

**Context 的问题不是「塞多少」，而是「何时取」**。

动态上下文发现将这个问题从「上下文管理策略」变成了「信息检索问题」。当 Agent 需要什么时，它去取；当它不需要时，信息保持在存储层而非活跃context中。

Token 效率只是副产品——真正的收益是**Agent 的上下文空间变成了可伸缩的**，不再受限于固定 context window 大小。

---

## 结论

动态上下文发现代表了 Agent 上下文管理的范式转移：从「预加载 + summarization」到「文件化 + 按需检索」。Cursor 验证了这条路在 IDE 场景下的可行性（46.9% Token 节省），mcp-agent 则将其扩展为生产级框架。

对于 Agent 工程师而言，这意味着：
- 设计 Harness 时，应该假设 Agent **知道在哪找**，而非**已经记住**
- 上下文管理的核心指标从「上下文窗口利用率」变成「信息检索命中率」
- MCP 的价值不仅是「连接工具」，更是「按需加载工具」的能力

> "Stay tuned for lots more exciting work to share in this space."
> — Cursor Blog (closing line)

这个空间刚刚开始。

---

**引用来源**：
1. [Anthropic: 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)
2. [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)
3. [GitHub: lastmile-ai/mcp-agent](https://github.com/lastmile-ai/mcp-agent)