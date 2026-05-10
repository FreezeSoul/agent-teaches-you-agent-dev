# 上下文工程的范式转移：从提示词优化到注意力预算管理

> 本文基于 Anthropic Engineering Blog「Effective context engineering for AI agents」（2026年），深度解读从 Prompt Engineering 到 Context Engineering 的范式转移，以及三个核心技术支柱：上下文压缩（Compaction）、结构化笔记（Structured Note-taking）、多 Agent 架构（Sub-agent Architectures）。

---

## 核心论点

**上下文工程是提示词工程的自然演进，而非替代**。当 Agent 需要在多个推理轮次和更长时间跨度内运行时，管理整个上下文状态（系统指令、工具、MCP、外部数据、消息历史）的策略变得与编写有效提示词同等重要。

> "Context engineering is the art and science of curating what will go into the limited context window from that constantly evolving universe of possible information."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**笔者认为**：上下文工程的核心洞察是「注意力是有限资源」——LLM 的上下文窗口不是硬盘，而是一个有边际效应递减的注意力预算。工程问题从「如何填满上下文」转变为「如何在有限预算内最大化信号密度」。

---

## 为什么上下文工程对构建有能力 Agent 至关重要

### 注意力预算的物理约束

LLM 基于 Transformer 架构，每个 token 可以attend到上下文中的所有其他 token，形成 O(n²) 的成对关系。随着上下文长度增加，模型捕获这些成对关系的能力被摊薄，在上下文大小和注意力焦点之间产生天然张力。

> "Every new token introduced depletes this budget by some amount, increasing the need to carefully curate the tokens available to the LLM."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

研究表明 [Context Rot](https://research.trychroma.com/context-rot) 现象：随着上下文窗口中 token 数量的增加，模型准确回忆信息的能力下降。这不是某个模型的缺陷，而是所有基于 Transformer 的模型的共同特征。

> "Context, therefore, must be treated as a finite resource with diminishing marginal returns. Like humans, who have limited working memory capacity, LLMs have an 'attention budget'."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 上下文污染的现实问题

即使是目前最大的上下文窗口（1M+ tokens），对于跨越数天到数周的 Agent 会话仍然不够。在这样的会话中，工具调用、文件内容和中间推理的量可以超过任何生产 LLM 的上下文限制。这个问题被「Context Rot」加剧——模型性能在达到标称限制之前就会退化。

> "Even models with 1M+ token windows are insufficient for multi-day agentic sessions, where the volume of tool calls, file contents, and intermediate reasoning can exceed the context limit of any production LLM."
> — [Martian-Engineering/volt LCM Technical Paper](https://papers.voltropy.com/LCM)

---

## 有效上下文的组成

### 系统提示词：找到正确的「粒度高度」

系统提示词应使用简单、直接的语言，在正确的粒度高度上呈现想法。正确的粒度是两个常见失败模式之间的「黄金区域」：

- **过度工程化**：工程师在提示词中硬编码复杂的脆弱逻辑，以引发精确的 Agent 行为。这会产生脆弱性并增加维护复杂性。
- **过于模糊**：工程师有时提供模糊的、高层次的指导，未能给 LLM 提供期望输出的具体信号，或错误地假设共享上下文。

> "At one end of the spectrum, we see brittle if-else hardcoded prompts, and at the other end we see prompts that are overly general or falsely assume shared context."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**优化建议**：按主题组织提示词为不同部分（如 `<background_information>`、`<instructions>`、`## Tool guidance`、`## Output description` 等），使用 XML 标签或 Markdown 标题来划分这些部分。应努力追求完整概述预期行为的最小信息集。

### 工具设计：最小可行集合

工具定义 Agent 与其信息/行动空间之间的契约，因此工具必须促进效率——既返回token高效的信息，也鼓励高效的 Agent 行为。

> "One of the most common failure modes we see is bloated tool sets that cover too much functionality or lead to ambiguous decision points about which tool to use. If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

工具应具有自包含性、错误稳健性，并对其预期用途极其清晰。

### Few-shot 示例：多样化且规范

不应在提示词中塞入一长串边缘情况，而应策展一组多样化、规范的示例，有效描绘 Agent 的预期行为。对 LLM 来说，示例是「一图抵千言」。

---

## 上下文检索：从预推理到即时获取

### 预推理检索 vs 即时检索

今天，许多 AI 原生应用采用某种形式的基于嵌入的预推理时间检索，在 Agent 推理之前提前获取重要上下文。随着领域转向更多 Agent 化方法，团队越来越多地用「即时」（just-in-time）上下文策略来增强这些检索系统。

**预推理检索**：在 Agent 运行前预先处理所有相关数据
**即时检索**：维护轻量级标识符（文件路径、存储查询、网页链接等），在运行时使用工具动态加载数据到上下文

> "Rather than pre-processing all relevant data up front, agents built with the 'just in time' approach maintain lightweight identifiers and use these references to dynamically load data into context at runtime using tools."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### Claude Code 的混合模型

Anthropic 的 Agent 编码解决方案 Claude Code 使用这种即时方法对大型数据库执行复杂数据分析。模型可以编写针对性查询、存储结果，并利用 Bash 命令（如 `head` 和 `tail`）分析大量数据，而无需将完整数据对象加载到上下文中。

> "This approach mirrors human cognition: we generally don't memorize entire corpuses of information, but rather introduce external organization and indexing systems like file systems, inboxes, and bookmarks to retrieve relevant information on demand."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 混合策略

在某些设置中，最有效的 Agent 可能采用混合策略——为速度预先检索一些数据，并在其判断需要时追求进一步的自主探索。

> "Claude Code is an agent that employs this hybrid model: CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 长程任务的上下文工程

### Compaction（压缩）：无丢失的上下文摘要

Compaction 是将接近上下文窗口限制的对话内容进行摘要，并在新的上下文窗口中重新开始的实践。Compaction 通常作为上下文工程中推动更好长期内聚力的第一杠杆。

**Claude Code 的 Compaction 实现**：将消息历史传递给模型进行摘要和压缩，保留最关键细节（架构决策、未解决的 bug、实现细节），同时丢弃冗余的工具输出或消息。然后 Agent 可以继续使用此压缩上下文加上最近访问的 5 个文件。

> "The art of compaction lies in the selection of what to keep versus what to discard, as overly aggressive compaction can result in the loss of subtle but critical context."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Volt 的 LCM 架构**：确定性压缩避免模型决定何时摘要的随机性

Volt（Martian-Engineering/volt）采用了不同的方法——通过软和硬 token 阈值驱动的确定性控制循环，而不是依赖模型决定何时摘要。

> "LCM addresses this by shifting the burden of memory architecture from the model back to the engine. Rather than asking the model to invent a memory strategy, LCM provides a deterministic, database-backed infrastructure."
> — [Volt LCM Technical Paper](https://papers.voltropy.com/LCM)

Volt 的双态内存架构：
- **不可变存储（Immutable Store）**：每个用户消息、助手回复和工具结果都以原样持久化，从不修改
- **活跃上下文（Active Context）**：每个回合实际发送到 LLM 的窗口，从最近的原始消息和预计算的摘要节点混合组装

### Structured Note-taking（结构化笔记）：Agent 记忆外部化

结构化笔记是一种 Agent 定期将笔记写入持久化到内存（上下文窗口之外）的技术。这些笔记在后续时间被重新拉入上下文窗口。

> "Claude playing Pokémon demonstrates how memory transforms agent capabilities. The agent maintains precise tallies across thousands of game steps—tracking objectives like 'for the last 1,234 steps I've been training my Pokémon in Route 1.'"
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

这种策略提供最小开销的持久记忆。就像 Claude Code 创建待办列表，或自定义 Agent 维护 NOTES.md 文件，这个简单模式允许 Agent 跨复杂任务跟踪进度，维护关键上下文和依赖关系，否则这些将在数十次工具调用中丢失。

### Sub-agent Architectures（多 Agent 架构）：专业化分工

Sub-agent 架构提供了另一种绕过上下文限制的方法。不是让一个 Agent 尝试跨整个项目维护状态，而是让专业化的子 Agent 处理专注的任务，保持干净的上下文窗口。主 Agent 协调子 Agent 的工作。

> "Rather than one agent attempting to maintain state across an entire project, specialized sub-agents can handle focused tasks with clean context windows."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 工程实践建议

### 1. 最小化上下文，最大化信号

始终寻求在最小信息集中完整概述预期行为。最小化不一定意味着短——你仍然需要给 Agent 足够的信息以确保其坚持预期行为。

### 2. 工具集合最小化

如果人类工程师无法明确说出一个工具在给定情况下应该使用，AI Agent 也不能期望做得更好。策展最小可行工具集也可以带来更可靠的长期维护和上下文修剪。

### 3. 混合策略是常态，而非例外

「预推理 + 即时探索」的混合策略是大多数复杂任务的正确答案。模型能力越强，Agent 化设计越倾向于让智能模型智能行动，减少人工策展。

> "Given the rapid pace of progress in the field, 'do the simplest thing that works' will likely remain our best advice for teams building agents on top of Claude."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 4. 压缩提示词的调试建议

对于实现压缩系统的工程师，建议在复杂 Agent 追踪上仔细调整压缩提示。先最大化召回以确保压缩提示从追踪中捕获每个相关信息，然后迭代改进精度以消除多余内容。

---

## 与上下文工程的关联主题

| 主题 | 关联点 |
|------|--------|
| [Volt — Lossless Context Management](https://github.com/Martian-Engineering/volt) | 确定性压缩引擎，Immutability + Active Context 双态架构，3级升级协议 |
| [Claude Code Memory Setup (Obsidian Zettelkasten)](./claude-code-memory-setup-obsidian-graphify-token-optimization-2026.md) | 结构化笔记的工程实现，跨会话持久化 |
| [agentmemory — 免 DB 持久记忆基础设施](./agentmemory-persistent-memory-ai-coding-agents-2026.md) | 记忆基础设施的系统性解决方案 |
| [Anthropic Measuring Agent Autonomy](./anthropic-measuring-agent-autonomy-long-running-agents-2026.md) | 长程 Agent 的上下文坍缩问题 |

---

## 结论

上下文工程代表了从「如何写好提示词」到「如何在有限注意力预算内最大化信号密度」的根本性视角转变。这个范式转移的关键洞察是：

1. **上下文是有限资源**，不是硬盘——需要精心策展
2. **Compaction + Note-taking + Sub-agents** 是三大工程支柱
3. **确定性优于随机性**——Volt 的 LCM 架构用数据库后端替代模型的随机摘要决策
4. **混合策略是常态**——预检索 + 即时探索的组合优于单一策略

> "Context engineering is the natural progression of prompt engineering."
> — [Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**笔者认为**：随着模型能力持续提升，Agent 化设计将越来越倾向于让智能模型智能行动，越来越多的人工策展工作将被替换。但在当下，最佳实践仍然是「do the simplest thing that works」——在注意力预算约束下寻求信号密度的最大化，而非盲目追求上下文的最大化。

---

*来源：[Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)（2026年）*