# Cursor 动态上下文发现：五项工程实践如何让 Context Window 翻倍高效

> **本文核心论点**：Cursor 的动态上下文发现不是一项新技术，而是一组工程决策的集合——将长工具输出转为文件、按需加载 MCP 工具、把终端会话文件化，本质上是用「延迟计算」换取「Token 成本可控」。这组实践的共同特点是：工程实现简单，但认知上打破了「上下文越满越好」的直觉。

---

## 背景：Static Context 的崩塌

传统 Agent 的上下文管理是**预先加载式**的：系统 Prompt 塞满规则、工具描述、聊天历史，Agent 在「充裕」的上下文中工作。这种模式的代价：

- **Token 成本线性增长**：每轮对话都携带完整历史，上下文窗口迟早会满
- **信噪比下降**：大量「可能有用」的信息稀释了真正相关的上下文
- **长尾场景爆炸**：MCP 服务器工具描述、终端输出、聊天历史全部涌入 context

Cursor 观察到一个反直觉的结论：

> "As models have become better as agents, we've found success by providing fewer details up front, making it easier for the agent to pull relevant context on its own."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

模型越强，就越不需要被「塞满」。模型自身已经具备「需要什么就去检索什么」的能力。问题只是我们有没有给它提供一个好的检索接口。

---

## 技术一：长工具响应 → 文件化

### 问题

Shell 命令和 MCP 调用返回的 JSON 可能很长。业界常见做法是直接截断（truncation），代价是数据丢失——包括可能很重要的信息。

### Cursor 的解法

不截断，而是**写到文件里，给 Agent 读的能力**。

```
Agent 执行长工具调用 → 响应写入临时文件
                         ↓
                   给予 Agent 文件路径引用
                         ↓
            Agent 用 tail/head 按需读取，而非一次性注入
```

Cursor 强调了一个关键区别：

> "The common approach coding agents take is to truncate long shell commands or MCP results. This can lead to data loss, which could include important information you wanted in the context."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

文件接口比截断更优雅的地方在于：**Agent 自己决定读多少**。Agent 可以 tail 看末尾，也可以 read 看全部，取决于任务需要。这比任何预设的截断策略都更智能。

**工程意义**：这不是 Agent 技巧，而是 Harness 的工程决策——把「截断」改为「写入文件系统」，Agent 的能力不受损，只是换了一种信息传递方式。

---

## 技术二：Summarization 时引用聊天历史

### 问题

当 context window 满时，Cursor 触发 summarization step，给 Agent 一个「压缩版上下文」。但压缩是**有损的**——Agent 可能忘记关键细节（如任务约束、特殊要求）。

### Cursor 的解法

Summarization 之后，不仅给 Agent 压缩后的 summary，还给一个**指向聊天历史的文件引用**。

```
Context Window 满了
       ↓
触发 Summarization → 生成压缩 summary
       ↓
给 Agent 历史文件引用（History file as file）
       ↓
如果 Agent 发现需要的细节在 summary 中缺失
       ↓
Agent 自己去 history file 里 grep 检索
```

这相当于给 Agent 提供了一个**可查询的记忆外部存储**。Summary 是 lossy compression，但 history file 是 lossless 的——Agent 可以按需回溯。

Cursor 点出了这种设计的工程背景：

> "The agent's knowledge can degrade after summarization since it's a lossy compression of the context. The agent might have forgotten crucial details about its task."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

### 与 Anthropic Session 的对比

Anthropic Managed Agents（` Scaling Managed Agents: Decoupling the brain from the hands`）的 session 设计也是「外部化上下文」——`getEvents()` 接口允许 brain 查询 session 日志。Cursor 的 history file 方案与 Anthropic 的 session 设计在精神上是一致的：**上下文是对象，不是窗口**。

---

## 技术三：Agent Skills 按需加载

### 问题

[Agent Skills](https://cursor.com/docs/context/skills#agent-skills) 是一个开放标准，允许向 Agent 注入领域特定能力。Skills 包含描述（供 static context 使用）和可执行文件/脚本（供运行时调用）。

当 Skill 数量增加时，每个 Skill 的描述都会进入 context window。即使 Agent 只会用到其中 2-3 个。

### Cursor 的解法

Skills 的描述写入文件系统（而不是直接塞进 system prompt）。Agent 收到的不再是完整的 Skill 描述列表，而是一个** Skills 名称和简介的索引**。

```
Skills 描述 → 文件系统（每个 Skill 一个文件夹）
                    ↓
      Agent 收到：Skill 名称 + 简介（静态 context）
                    ↓
        当任务需要时，Agent 自己 grep 检索相关 Skill
                    ↓
                 动态加载
```

这与 MCP 工具的动态加载逻辑相同——**把「静态注入」改为「按需发现」**。

---

## 技术四：MCP 工具按需加载（Token 减少 46.9%）

### 问题

MCP 服务器通常包含很多工具，每个工具有长描述。当用户装了多个 MCP 服务器时，所有工具的描述都被塞进 context window——即使 Agent 一轮会话只用到其中 1-2 个。

### Cursor 的解法

把 MCP 工具描述同步到文件夹，Agent 收到的不再是完整工具列表，而是一个**工具名 + 简介的索引**。

```bash
# MCP 工具描述 → 本地文件夹
mcp_tools/
├── server-a/     # Folder per MCP server
│   ├── tool-1.md
│   └── tool-2.md
└── server-b/
    ├── tool-1.md
    └── tool-2.md
```

Agent 只有在**真正需要某个工具时**，才去对应文件夹读取工具描述。

**关键数据**：Cursor 的 A/B 测试结果：

> "In runs that called an MCP tool, this strategy reduced total agent tokens by 46.9% (statistically significant, with high variance based on the number of MCPs installed)."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

46.9% 的 Token 节省是**可量化的收益**，而且是「在保证等效检索质量的前提下」实现的。

### 为什么是文件夹而非搜索索引

Cursor 选择文件夹而非扁平搜索索引，有两个工程理由：

1. **按服务器分组**：保持同一服务器工具的逻辑连贯性，Agent 可以理解「这些工具属于同一个服务」
2. **支持强大搜索**：Agent 可以用 `rg` 参数甚至 `jq` 过滤工具描述，而非只做关键词匹配

---

## 技术五：终端会话作为文件

### 问题

在集成终端（integrated terminal）执行命令后，输出在终端里，但 Agent 的输入是 context window。如果 Agent 需要引用「为什么这条命令失败了」，用户需要 copy/paste 终端输出到 Agent 输入。

### Cursor 的解法

把集成终端的输出**同步到本地文件系统**，Agent 可以直接 grep 相关输出。

```
终端执行命令 → 输出写入 ~/.cursor/terminal_history/
                              ↓
                     Agent 通过文件系统引用
                              ↓
                 "grep relevant output from terminal"
```

这让 CLI Agent 和 Web-based Agent 在终端输出处理上**体验一致**——都在 context 里看到了历史输出，只是通过的是动态发现而非静态注入。

---

## 统一模式：文件系统作为信息交换层

五项技术有一个共同的结构：

| 技术 | 传统方式 | Cursor 方式 |
|------|----------|-------------|
| 长工具响应 | 截断 → 数据丢失 | 写文件 → Agent 按需读 |
| Summarization 后历史 | 丢失 | 文件引用 → 可回溯 |
| Skills/MCP 工具 | 全部塞进 context | 文件夹索引 → 动态发现 |
| 终端输出 | copy/paste | 同步到文件系统 → grep |

**共同模式**：用文件系统作为信息交换的中间层，把「静态注入」改为「动态发现」。

Cursor 在博客结尾留下了一个值得思考的注释：

> "It's not clear if files will be the final interface for LLM-based tools. But as coding agents quickly improve, files have been a simple and powerful primitive to use."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

文件不是最终接口，但是**当下最好的接口**——因为文件系统有三个不可替代的特性：
1. **原子性**：文件内容完整，不会像 context 一样被截断
2. **可查询性**：Agent 可以用 grep/find 按需检索
3. **延迟计算**：信息在被需要时才被读取，而不是一开始就注入

---

## 工程启示：Harness 设计的新思维

### 从「注入越多越好」到「注入越准越好」

Dynamic Context Discovery 打破了 Agent 开发中的一个常见误解：「给 Agent 越多上下文，Agent 表现越好」。

实际上，当模型能力足够强时，**给 Agent 太少上下文 + 给 Agent 好的检索能力**，比**给 Agent 太多上下文**更高效。

### 三个工程原则

**1. 延迟计算优于预先加载**

信息在被需要时才传递，而不是一开始就塞进 context。这降低了 Token 成本，也提高了信息质量（Agent 读到的是完整信息，而非截断后的片段）。

**2. 文件系统是 Agent 记忆的外部存储**

当 Agent 需要持久化但不适合写进 context 的信息时，文件系统是一个比 KV store 更简单、更通用的接口。Agent 天然会用文件——这是它们熟悉的工具。

**3. 索引与内容分离**

索引（如工具名称列表）进入 static context，详细内容（如工具描述）放在文件系统按需读取。Index 是信息「入口」，而非信息「本体」。

---

## 结论

Cursor 的动态上下文发现是一组**工程决策的集合**，每个决策都指向同一个目标：让 Agent 自己决定需要什么信息，而不是由 Harness 替 Agent 做决定。

这组实践的工程意义大于算法意义——它们不需要新模型，不需要新训练，只需要在 Harness 层做文件系统和信息加载策略的调整，就能带来 46.9% 的 Token 节省和更高的信息完整性。

> "Stay tuned for lots more exciting work to share in this space."
> — Cursor Engineering Team

下一代 Context Engineering 的方向已经明确：**不是把 Context Window 变大，而是让 Context 管理变得更智能**。
