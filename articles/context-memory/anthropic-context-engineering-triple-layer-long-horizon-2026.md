# Anthropic Context Engineering：三层上下文管理范式与长时任务实战

> 本文深度解读 Anthropic Engineering Blog「Effective context engineering for AI agents」，聚焦三大核心技术：Compaction（上下文压缩）、Structured Note-taking（结构化笔记）、Sub-agent Architectures（子代理架构）。Anthropic 明确指出：Context Engineering 是 Prompt Engineering 的自然演进，是构建可靠 Agent 的必修课。

---

## 核心论点

**Context Engineering 是 Agent 可靠性的分水岭。**

当 Agent 需要跨越多个推理周期完成长时任务时，Context Window 的有限性会成为系统失效的主要矛盾。Anthropic 提出的三层技术体系——Compaction、Structured Note-taking、Sub-agent Architectures——分别从「上下文减肥」、「外部记忆」、「并行分解」三个维度解决了这个问题。

> "Context must be treated as a finite resource with diminishing marginal returns. Like humans, who have limited working memory capacity, LLMs have an 'attention budget' that they draw on when parsing large volumes of context."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 一、为什么 Context Engineering 比 Prompt Engineering 更重要

Prompt Engineering 的核心是「写好一次指令」，而 Context Engineering 的核心是「持续管理上下文状态」。

Anthropic 指出，随着 Agent 越来越自主、运行时间越来越长，工程问题从「如何写好一个 Prompt」演变为「如何在多次推理循环中维护最优的 Token 集合」：

> "Context engineering is the art and science of curating what will go into the limited context window from that constantly evolving universe of possible information."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 1.1 Context Rot：上下文越长的代价

Anthropic 引用了 Needle-in-a-Haystack 研究中的关键发现：**Context Rot**。

> "Studies on needle-in-a-haystack style benchmarking have uncovered the concept of context rot: as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases."

这是 Transformer 架构的内生限制：
- Attention 是 O(n²) 的，每增加一个 Token，与所有历史 Token 的注意力关系都需要被稀释
- 模型在训练数据中短序列占比更高，长上下文是模型的弱项

> "This creates a natural tension between context size and attention focus."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 1.2 三层上下文组件的优先级

Anthropic 将 Context 的组成分为多个组件，并给出工程优先级：

| 组件 | 说明 | Anthropic 建议 |
|------|------|---------------|
| System Prompts | 核心指令层 | 最小化、信息密度最大化、分层结构 |
| Tools | Agent 与环境的交互接口 | 最小可行集合、自包含、错误鲁棒 |
| Examples | Few-shot 示例 | 多样且规范，而非堆砌边缘案例 |
| Message History | 对话历史 | 需要动态压缩（Compaction） |
| External Data | 运行时动态加载 | Just-in-Time 策略优于全量预加载 |

> "Our overall guidance across the different components of context is to be thoughtful and keep your context informative, yet tight."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 二、三层技术体系

### 2.1 Compaction：上下文压缩

**核心机制**：当对话历史接近 Context Window 上限时，将历史压缩为摘要，重新开一个新的 Context Window。

Anthropic 在 Claude Code 中的实现细节：

> "In Claude Code, for example, we implement this by passing the message history to the model to summarize and compress the most critical details. The model preserves architectural decisions, unresolved bugs, and implementation details while discarding redundant tool outputs or messages."

**关键设计决策**：保留什么、丢弃什么？

Anthropic 指出了 Compaction 的艺术所在：

> "The art of compaction lies in the selection of what to keep versus what to discard, as overly aggressive compaction can result in the loss of subtle but critical context whose importance only becomes apparent later."

最小侵入性的 Compaction 形式：**Tool Result Clearing**（工具调用结果清理），这是 Anthropic 在 Claude Developer Platform 上推出的功能：

> "One of the safest lightest touch forms of compaction is tool result clearing — once a tool has been called deep in the message history, why would the agent need to see the raw result again?"
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 2.2 Structured Note-taking：结构化笔记（Agent Memory）

**核心机制**：Agent 主动将关键信息持久化到外部存储（文件系统），在需要时读回 Context。

Anthropic 给出的经典案例是 Claude 玩 Pokémon：

> "Claude playing Pokémon demonstrates how memory transforms agent capabilities in non-coding domains. The agent maintains precise tallies across thousands of game steps — tracking objectives like 'for the last 1,234 steps I've been training my Pokémon in Route 1, Pikachu has gained 8 levels toward the target of 10.' Without any prompting about memory structure, it develops maps of explored regions, remembers which key achievements it has unlocked, and maintains strategic notes of combat strategies that help it learn which attacks work best against different opponents."

这展示了 Structured Note-taking 的核心价值：**跨 Context Window 的状态连续性**。

> "After context resets, the agent reads its own notes and continues multi-hour training sequences or dungeon explorations. This coherence across summarization steps enables long-horizon strategies that would be impossible when keeping all the information in the LLM's context window alone."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

Anthropic 还发布了 Memory Tool（Beta）支持文件持久化：

> "As part of our Sonnet 4.5 launch, we released a memory tool in public beta on the Claude Developer Platform that makes it easier to store and consult information outside the context window through a file-based system."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 2.3 Sub-agent Architectures：子代理架构

**核心机制**：将长时任务分解为多个专业子代理，每个子代理在干净的 Context 中运行。

Anthropic 的设计理念：

> "Rather than one agent attempting to maintain state across an entire project, specialized sub-agents can handle focused tasks with clean context windows. The main agent coordinates with a high-level plan and delegates to specialized sub-agents."

这与 Orchestration 层（Planner/Worker 模式）形成互补。Planner/Worker 解决的是「任务分配」，Sub-agent Architectures 解决的是「上下文隔离」。

---

## 三、Just-in-Time Context 策略 vs Pre-inference 策略

Anthropic 描述了范式转换：

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **Pre-inference Retrieval** | 推理前预加载所有相关数据到 Context | 静态领域（法律/金融文档） |
| **Just-in-Time Context** | 运行时通过工具动态加载（保留轻量引用/路径） | 动态环境（代码库、实时数据） |

Claude Code 的混合模型：

> "Claude Code is an agent that employs this hybrid model: CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time, effectively bypassing the issues of stale indexing and complex syntax trees."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**元数据作为上下文信号**：文件夹层次结构、命名约定、时间戳——Agent 在文件系统导航时，这些元数据提供了丰富的上下文线索，无需将整个数据体加载到 Context。

---

## 四、与 Agent Skills 的关联

Anthropic 的 Context Engineering 体系与 [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) 形成了互补关系：

- **Agent Skills** 解决的是「Agent 如何获取新的专业能力」（Skill 的三级渐进披露机制）
- **Context Engineering** 解决的是「Agent 在长时任务中如何维持上下文完整性」

两者共同构成了 Anthropic 的 Agent 工程框架：Skills 是能力的扩展，Context Engineering 是能力的持续性保障。

---

## 五、工程实践建议

### 5.1 Compaction 工程检查清单

1. **先宽后紧**：先用最大化的 recall 压缩 prompt，捕获所有可能相关内容
2. **迭代优化**：逐步提高 precision，剔除边际价值的内容
3. **安全删除顺序**：Tool Call Results → 低价值对话回合 → 边缘案例描述
4. **验证**：在复杂 agent traces 上测试，确保关键上下文没有丢失

### 5.2 Structured Note-taking 设计模式

```python
# 笔记持久化示例（伪代码）
def save_progress(agent, task_state, notes_file="NOTES.md"):
    """长时任务中定期保存关键状态"""
    notes = f"""
## Task: {task_state['goal']}
## Progress: {task_state['progress']}
## Pending: {task_state['pending']}
## Key Context: {task_state['critical_context']}
"""
    agent.write_file(notes_file, notes)

def restore_context(agent, notes_file="NOTES.md"):
    """Context 压缩后恢复关键上下文"""
    notes = agent.read_file(notes_file)
    return notes
```

### 5.3 工具集最小化原则

> "One of the most common failure modes we see is bloated tool sets that cover too much functionality or lead to ambiguous decision points about which tool to use. If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."
> — [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 六、结论

Context Engineering 是 Prompt Engineering 的下一阶段。Anthropic 提出的三层技术体系（Compaction / Structured Note-taking / Sub-agent Architectures）分别解决了长时任务的三个核心问题：**历史累积的上下文膨胀**、**跨会话的状态连续性**、**复杂任务的上下文隔离**。

 Ouroboros（本文 Projects 推荐项目）从另一个角度呼应了这些挑战——它的「规范优先」（Specification-first）工作流通过在执行前锁定意图，减少了上下文污染的概率，与 Anthropic 的 Context Engineering 形成互补：一个从输入端减少冗余，一个从过程端管理容量。

---

**关联项目**：
- [Ouroboros — Agent OS：规范驱动的可验证编码工作流](./projects/ouroboros-agent-os-replayable-specification-first-2026.md)（与本文 Context Engineering 形成互补：前者减少输入端冗余，后者管理过程端容量）