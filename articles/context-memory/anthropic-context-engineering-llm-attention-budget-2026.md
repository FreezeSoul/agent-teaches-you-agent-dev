# Context Engineering：超越 Prompt Engineering 的 Agent 上下文管理之道

> **本文解决的问题**：为什么传统的 prompt engineering 技巧在长周期 Agent 任务中失效？Context Engineering 作为 Prompt Engineering 的自然演进，如何重新定义 Agent 构建者对「上下文」的理解？

> **读者将获得的能力**：理解 LLM 注意力约束的本质、掌握有效上下文的组成原则、能够判断何时使用「预加载」策略 vs 「运行时动态检索」策略。

---

## 引言：从 Prompt Engineering 到 Context Engineering

过去几年，prompt engineering 是应用 AI 的核心关注点——人们关注的是如何为 prompts 找到正确的词汇和短语组合，以获得最佳输出。然而，当我们构建更强大的 Agent（这些 Agent 在多轮推理中运行，跨越更长的时间跨度）时，仅靠写好 prompt 已经不够了。

**Context Engineering** 是指在 LLM 推理时，对所有进入上下文窗口的 tokens（信息）进行策略性 curation 的集合——包括 system prompts、tools、Model Context Protocol（MCP）配置、外部数据、message history 等。这是一个迭代的过程，每次决定向模型传递什么时，curation 阶段就会发生。

> "Context engineering is the natural progression of prompt engineering."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

两者的核心区别在于：**Prompt engineering 是离散的一次性任务；Context engineering 是迭代的、持续的过程**。

---

## 注意力预算：上下文工程的基础约束

为什么 context engineering 如此重要？答案在于 LLM 的架构本质。

LLM 基于 Transformer 架构，每个 token 可以 attend 到上下文中的所有其他 token。对于 n 个 tokens，存在 n² 个成对的注意力关系。随着上下文长度增加，模型捕捉这些成对关系的能力被「拉薄」了。

> "As its context length increases, a model's ability to capture these pairwise relationships gets stretched thin, creating a natural tension between context size and attention focus."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

此外，模型从训练数据分布中发展注意力模式，而较短序列通常比较长序列更常见。这意味着模型对上下文级依赖关系的处理经验较少，专门的参数也较少。

Context 的这种稀缺性意味着它必须被视为**有限资源，具有边际收益递减**的特性——就像人类有有限的工作记忆容量一样，LLM 也有一个「注意力预算」，每引入一个新 token 都会消耗一部分预算。

> "LLMs have an 'attention budget' that they draw on when parsing large volumes of context. Every new token introduced depletes this budget by some amount, increasing the need to carefully curate the tokens available to the LLM."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**工程启示**：在构建长周期 Agent 时，必须将 context 视为需要优化的资源，而非越多越好。有效的 context engineering 意味着找到**最小的高信号 token 集合**，以最大化实现预期结果的概率。

---

## 有效上下文的组成原则

Anthropic 将上下文分解为多个组件，每个组件都有特定的 curation 原则：

### System Prompts：清晰而非冗长

System prompts 应该极度清晰，使用简单直接的语言，在「正确的抽象层级」上呈现 ideas。

这个正确的抽象层级是「Goldilocks zone」，处于两个常见失败模式之间：
- **过度复杂**：工程师硬编码复杂的、脆弱的逻辑来引出精确的 Agent 行为——这创造脆弱性，增加维护复杂度
- **过度笼统**：工程师有时提供模糊的、高层次的指导，未能给 LLM 提供期望输出的具体信号，或错误地假设存在共享上下文

> "At one end of the spectrum, we see brittle if-else hardcoded prompts, and at the other end we see prompts that are overly general or falsely assume shared context."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**推荐实践**：将 prompts 组织成不同部分（如 `<background_information>`, `<instructions>`, `## Tool guidance`, `## Output description` 等），并使用 XML tags 或 Markdown headers 来区分这些部分。最终目标是找到**最小信息集**，完整描述期望行为——注意「最小」不一定意味着「短」。

### Tools：最小可行集

Tools 定义了 Agent 与其信息/行动空间之间的契约，因此 tool 返回的信息必须 token 高效，并促进高效的 Agent 行为。

最常见的失败模式之一是**肿大的 tool sets**，涵盖太多功能或导致关于使用哪个 tool 的模糊决策点。如果人类工程师无法明确说出在给定情况下应该使用哪个 tool，就不能指望 AI Agent 做得更好。

> "If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

 curation 一个最小可行的 tool 集也会带来更可靠的长周期交互维护和 context 精简。

### Few-Shot Examples：多样化而非穷举

Few-shot prompting是一种持续推荐的最佳实践，但团队经常在 prompt 中塞入大量边缘案例，试图表达 LLM 应该在特定任务中遵循的每一条规则。

**不推荐的做法**：列出所有可能的规则。
**推荐的做法**： curation 一组多样的、典型的例子，有效地描绘 Agent 的期望行为。

> "For an LLM, examples are the 'pictures' worth a thousand words."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 上下文检索的两种策略：「预加载」vs「运行时动态加载」

随着工程师们设计 Agent 上下文的思维方式转变，我们看到了两种策略的分化：

### 预推理时间检索（Pre-inference Time Retrieval）

在推理前预处理所有相关数据，将其全部加载到上下文中。许多 AI 原生应用采用这种方式进行基于 embedding 的检索，在 Agent 推理之前就向其呈现重要上下文。

**优点**：快速，无需额外的工具调用开销
**缺点**：context 可能变得过时；复杂语法树难以准确索引；信息过载风险

### 「Just-in-Time」上下文策略

维护轻量级标识符（文件路径、存储查询、网页链接等），并使用 tools 在运行时动态将数据加载到上下文中。

Anthropic 的 Agent 编码解决方案 Claude Code 使用这种方法来执行对大型数据库的复杂数据分析。模型可以编写目标查询、存储结果、使用 Bash 命令如 `head` 和 `tail` 来分析大量数据，而无需将完整数据对象加载到上下文中。

> "This approach mirrors human cognition: we generally don't memorize entire corpuses of information, but rather introduce external organization and indexing systems like file systems, inboxes, and bookmarks to retrieve relevant information on demand."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**优点**：避免 context 膨胀；支持渐进式发现；元数据（如文件路径、层级结构）提供有用的行为信号
**缺点**：运行时探索比预计算数据慢；需要正确的 tools 和启发式方法才能有效导航

### 元数据的价值

Anthropic 特别强调了元数据的作用：对于在文件系统中操作的 Agent，`tests/` 文件夹中的 `test_utils.py` 与 `src/core_logic/` 中同名文件暗示了不同的目的。文件夹层级、命名约定、时间戳都提供了重要的信号，帮助 Agent 和人类理解如何以及何时利用信息。

> "Folder hierarchies, naming conventions, and timestamps all provide important signals that help both humans and agents understand how and when to utilize information."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### Claude Code 的混合策略

Claude Code 采用混合模型：`CLAUDE.md` 文件被盲目地提前放入上下文，而 `glob` 和 `grep` 等原语允许 Agent 按需导航环境并检索文件，从而有效地规避了过时索引和复杂语法树的问题。

> "Claude Code is an agent that employs this hybrid model: CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 选择正确策略的判断框架

| 场景 | 推荐策略 | 原因 |
|------|---------|------|
| 动态内容多的场景（如编码、文件操作） | Just-in-Time 动态检索 | 避免 context 膨胀，支持渐进式发现 |
| 变化较少的场景（如法律、金融） | 混合策略或预加载 | 速度优先，内容相对稳定 |
| 模型能力提升时 | 倾向 Just-in-Time | 给智能模型更多自主权，减少人工 curation |

> "The hybrid strategy might be better suited for contexts with less dynamic content, such as legal or finance work. As model capabilities improve, agentic design will trend towards letting intelligent models act intelligently, with progressively less human curation."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 工程实践检查清单

基于 Anthropic 的上下文工程原则，Agent 构建者应定期检查：

**System Prompt 层面**
- [ ] Prompt 是否在「正确抽象层级」——足够具体以引导行为，又足够灵活以提供强 heuristics？
- [ ] 是否存在硬编码的 if-else 逻辑？考虑用原则性描述替代
- [ ] 是否组织了 distinct sections 并使用清晰的格式分隔？

**Tools 层面**
- [ ] 是否是「最小可行集」——人类工程师能明确说出每个 tool 的使用场景？
- [ ] 每个 tool 的返回信息是否 token 高效？
- [ ] 是否存在功能重叠的 tool？考虑合并或删除

**Examples 层面**
- [ ] 示例是否多样化且 canonical，而非穷举边缘案例？
- [ ] 每个示例是否有效描绘了期望的 Agent 行为？

**检索策略层面**
- [ ] 对于当前场景，是否选择了合适的检索策略（预加载 vs Just-in-Time）？
- [ ] 是否建立了元数据系统来支持动态检索？
- [ ] 是否有机制处理 Just-in-Time 探索的慢速问题（如缓存、预热）？

---

## 总结与启示

Context Engineering 的核心洞察是：**上下文是一个有限的、昂贵的资源，需要像工程系统一样被精心设计**。

> "Given that LLMs are constrained by a finite attention budget, good context engineering means finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

随着模型能力的提升，Agent 构建将趋向于让智能模型更自主地行动，减少人工 curation。但在那之前，「do the simplest thing that works」仍然是最佳建议。

**下一步行动**：
1. 检查你当前的 Agent prompts——是否陷入了「过度复杂」或「过度笼统」的陷阱？
2. 审计你的 tool set——是否真的需要所有这些 tools？
3. 评估你的检索策略——对于长周期任务，Just-in-Time 策略是否更合适？

---

## 关联阅读

- [Anthropic: Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) — Agent vs LLM-based workflows 的定义边界
- [Anthropic: Writing tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Tool 设计最佳实践
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — 长周期 Agent 的 Harness 设计（Initializer Agent + Feature List JSON）