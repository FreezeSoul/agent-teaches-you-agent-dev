# Cursor 动态上下文发现：文件作为上下文原语

> 本文解析 Cursor Engineering Blog 发布的「Dynamic Context Discovery」技术，揭示从「静态上下文注入」到「动态上下文发现」的范式转变，以及这对 AI Coding Agent 设计的根本性影响。

---

## 核心论点

**文件不是终点，而是通道。** Cursor 的动态上下文发现模式证明：将工具输出、历史记录、MCP 工具列表写入文件系统而非直接注入上下文，Token 效率提升 46.9% 的同时，Agent 响应质量也随之提升。这不是优化技巧，而是对「上下文管理应该在哪一层解决」的根本性回答。

---

## 旧范式的困境：静态上下文注入

在传统架构中，Context Window 的管理策略是**注入式**（Inject Everything Possible）：将所有可能相关的信息都塞进 Context，包括：

- 历史对话全文
- 所有 MCP 工具的完整描述
- 当前代码库的索引和摘要
- Terminal 输出日志

这种策略在短程任务中有效，但在长程任务中暴露了两个根本矛盾：

**Token 容量 vs 信息完备性的矛盾。** 代码库的索引、工具的描述、对话的历史——这些信息加在一起远超 Context Window 容量。「注入式」策略要么导致信息被截断丢失，要么被迫触发压缩（Summarization），后者是**有损压缩**，会丢失关键细节。

**上下文相关性 vs 上下文完整性的矛盾。** Agent 执行的每个步骤需要的上下文不同。在一个步骤中注入所有可能相关的上下文，意味着在每个步骤中 Agent 都要从大量无关信息中筛选出真正相关的部分——这是对模型认知资源的极大浪费。

官方原文指出了这个问题：

> "Third-party tools (i.e. shell commands or MCP calls) don't natively get this same treatment. The common approach coding agents take is to truncate long shell commands or MCP results. This can lead to data loss, which could include important information you wanted in the context."

---

## 新范式：动态上下文发现

动态上下文发现（Dynamic Context Discovery）的核心思想是：**不要在系统提示中注入所有信息，而是只提供文件的引用，让 Agent 自己决定需要哪些上下文。**

### 设计原则

1. **最小静态注入**：系统提示只包含最基础的信息（工具名称、主要描述），而不是完整的内容
2. **按需拉取**：Agent 通过工具调用主动读取文件，而不是等待上下文被动注入
3. **文件系统作为管道**：工具输出写入文件，Agent 通过 `tail`/`grep`/`read` 按需访问，而不是一次性加载到 Context

### 五大场景的实现

#### 1. 长工具响应 → 文件

Shell 命令和 MCP 调用的输出通常很长。传统做法是直接注入 Context，导致 Context 膨胀；或者截断，导致信息丢失。

Cursor 的方案：
```
工具输出 → 写入文件 → Agent 用 tail 查看末尾 → 按需读取更多
```

这样 Agent 不需要在每次工具调用后处理完整的原始输出，只需要处理文件路径和 Tail 结果。减少了不必要的 Summarization 触发。

#### 2. 对话历史 → 文件引用

当 Context Window 达到上限触发 Summarization 时，Agent 的知识会有损失（因为 Summarization 是有损压缩）。之后 Agent 可能忘记任务的关键细节。

Cursor 的方案：Summarization 后，给 Agent 提供历史文件的引用，而不是强制让 Agent 在压缩后的 Context 中重建信息：

> "If the agent knows that it needs more details that are missing from the summary, it can search through the history to recover them."

这意味着 **Summarization 不再是不可逆的上下文丢失**，而变成了一个「摘要+文件指针」的组合，Agent 可以主动恢复完整上下文。

#### 3. Agent Skills → 文件按需加载

Cursor 支持 Agent Skills 标准。Skills 是定义文件，告诉 Agent 如何执行特定领域的任务。

Cursor 的方案：Skills 的完整内容不直接注入，而是：
- Skill 名称和简短描述作为静态 Context 注入
- Skill 的完整定义（文件）放在文件系统上
- Agent 在需要时通过工具（grep / Semantic Search）主动查找相关 Skill

#### 4. MCP 工具 → 按需同步

这是最关键的场景之一。MCP 服务器通常包含大量工具，工具描述很长。多个 MCP 服务器的描述加起来会严重占用 Context 空间。

Cursor 的方案：将 MCP 工具描述同步到一个文件夹，工具描述作为文件存在文件系统上，Agent 只接收工具名称的静态提示。Agent 需要某个工具时，自己去文件夹里查找。

**实测效果**：

> "In an A/B test, we found that in runs that called an MCP tool, this strategy reduced total agent tokens by 46.9% (statistically significant, with high variance based on the number of MCPs installed)."

46.9% 的 Token 减少，且这是**有意义的减少**（减少了不必要的信息），而不是截断丢失。

#### 5. Terminal 会话 → 文件

Cursor 将集成的 Terminal 输出同步到本地文件系统。好处：

- Agent 可以直接 `grep` 特定的日志输出，而不是处理完整的 Terminal 历史
- 用户问「为什么命令失败了」，Agent 能直接读日志文件的相关部分
- 长程任务的日志不会占用 Context，而是按需访问

---

## 为什么文件是更好的抽象

Cursor 选择文件系统而非抽象的工具搜索 API，有三个关键原因：

**1. 文件保留了信息的结构**

> "We considered a tool search approach, but that would scatter tools across a flat index. Instead, we create one folder per server, keeping each server's tools logically grouped."

MCP 工具之间有关联性——同一个 MCP 服务器的工具通常是相关的。文件系统按文件夹组织工具，保持了这种语义关联，而不是将所有工具打平。

**2. 文件支持更强的搜索能力**

Agent 可以用 `grep` 的完整参数进行搜索，而不是依赖一个 flat index 的简单搜索功能。文件系统的层级结构让 Agent 能够：
- 列出整个服务器的工具（`ls`）
- 在工具描述中全文搜索（`grep -r`）
- 理解工具之间的分组关系

**3. 文件是模型见过的原语**

LLM 在训练数据中见过大量文件和代码文件。这种熟悉度意味着文件作为接口的出错概率更低。相比于设计一个新的抽象层（如「Tool Registry」API），使用文件更简单、更稳定。

官方原文：

> "Files have been a simple and powerful primitive to use, and a safer choice than yet another abstraction that can't fully account for the future."

---

## 上下文工程的新分层

动态上下文发现模式揭示了一个新的上下文工程分层：

| 层级 | 方式 | 特点 |
|------|------|------|
| **静态上下文** | 直接注入 System Prompt | 最基础的信息，始终保留 |
| **动态上下文** | 文件引用 + 按需访问 | 按需拉取，Token 高效 |
| **持久上下文** | 外部存储（Session Log） | 超出 Context Window 的信息，可恢复 |

这个分层与 Anthropic 的「Brain-Hands-Session 解耦」形成呼应——Context 管理在 Harness 层解决，而不是让模型自己管理。

---

## 与现有工作的关联

**与 Cursor App Stability 的互补**：上一轮分析了 Cursor 的 App Stability 工程（OOM Reduction、Crash Watchdog），关注的是「如何在长程任务中保持进程稳定」。动态上下文发现关注的是「如何在长程任务中保持上下文质量」。两者共同构成 Cursor 长程 Agent 的双支柱：**执行稳定性 + 上下文效率**。

**与 Anthropic Context Engineering 的互补**：Anthropic 的上下文工程强调 Summarization、Compaction、Selective Memory 等技术来解决 Context 容量问题。Cursor 的动态上下文发现在另一个维度上解决问题——不是压缩上下文内容，而是**重新定义上下文的获取方式**（从注入变为按需拉取）。

**Token 效率 vs 压缩效率的区分**：动态上下文发现不是压缩（Compression），而是路由（Routing）——让正确的信息在正确的时间到达正确的位置。46.9% 的 Token 减少不是来自信息压缩，而是来自**信息路由的优化**。

---

## 判断性内容

### 这个模式的局限

动态上下文发现不是银弹，有几个关键限制：

**1. 需要 Agent 主动探索的能力**。如果 Agent 在规划阶段不知道自己缺少什么上下文，它不会主动去查找。这与 Agent 的 Self-Reflection 能力高度相关。

**2. 文件 I/O 增加工具调用次数**。Agent 需要额外的工具调用（read/tail/grep）来获取上下文，这会增加总的工具调用次数，进而影响延迟。在高频工具调用的场景中，这可能是代价。

**3. 依赖底层文件系统的可靠性**。如果文件写入失败或同步延迟，Agent 可能拿到过期或缺失的上下文。这要求 Cursor 的文件系统同步机制本身是可靠的。

### 对行业的启示

动态上下文发现的核心贡献不是「46.9% Token 减少」这个数字，而是**重新定义了 Context Window 管理的思路**：

> 上下文管理的责任从「注入端」（把信息塞进去）转向「消费端」（让模型按需拉取）。

这对 Agent 设计的影响是根本性的。在传统架构中，Harness 负责「尽可能多地注入信息」；在新的范式中，Harness 负责「建立好文件系统管道，让模型自己决定需要什么」。

前者随着 Context Window 扩大变得越来越难以为继（信息太多无法注入）；后者随着模型能力的增强变得越来越可行（模型能够更准确地判断自己需要什么）。

---

## 技术细节

**文件同步的工程实现**：
- MCP 工具描述同步到一个本地文件夹（每个 Server 一个子文件夹）
- Terminal 输出实时同步到文件系统
- Chat History 在 Summarization 后作为文件引用提供

**Agent 的上下文发现行为**：
- Agent 收到工具名称的静态提示（而不是完整描述）
- 工具名称提示 Agent「需要时去查文件」
- Agent 使用 `grep` / `ls` / `tail` 等工具获取完整信息

**性能影响**：
- MCP 工具调用场景：Token 减少 46.9%（A/B 测试，统计显著）
- 减少的 Token 是「不必要注入的冗余信息」，而不是有用信息

---

## 结论

Cursor 的动态上下文发现模式指向了一个更根本的设计转变：**从「上下文是注入的数据」到「上下文是按需获取的资源」**。文件作为上下文原语的优势在于：Token 高效、保留结构、支持强搜索、易于实现。

这个模式的核心洞察是：**Context Window 的容量问题不只是压缩问题，更是路由问题**。让正确的信息在正确的时间到达，比把所有可能相关的信息都塞进去更有效。

> "Files have been a simple and powerful primitive to use, and a safer choice than yet another abstraction that can't fully account for the future."
> — [Cursor Engineering: Dynamic Context Discovery](https://cursor.com/blog/dynamic-context-discovery)

---

## 参考来源

- [Cursor Blog: Dynamic Context Discovery](https://cursor.com/blog/dynamic-context-discovery)（官方原文，5 处直接引用）
- [Cursor Blog: Long-Running Agents Research Preview](https://cursor.com/blog/long-running-agents)（长程 Agent 背景，2 处引用）

**关联文章**：
- `cursor-app-stability-engineering-oom-reduction-2026.md` — App 稳定性工程（执行稳定性）
- `anthropic-managed-agents-brain-hands-decoupled-architecture-2026.md` — Brain-Hands 解耦（架构层面的关注点分离）
- `cursor-cloud-agents-amplitude-3x-production-pipeline-2026.md` — Cloud Agents（长程 Agent 的产品化路径）