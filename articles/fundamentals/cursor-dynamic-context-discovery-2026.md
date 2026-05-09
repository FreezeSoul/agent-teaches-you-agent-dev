# Cursor 动态上下文发现：编码 Agent 的下一代 Context 工程范式

> **核心论点**：Cursor 提出的「动态上下文发现」代表了一次范式转移——从「把所有上下文塞进 context window」到「让 agent 按需拉取」。这个转变解决的不只是 token 效率问题，更是「context 质量」问题：更少但更精确的信息实际上让 agent 表现更好。

## 1. 旧范式的核心困境：Static Context 的崩溃

传统的 context 工程建立在这样一个假设上：**越多的上下文 = 越好的 agent 表现**。

这个假设在 2024 年还算成立，当时模型能力和 context window 都相对有限。但到了 2026 年，事情发生了变化：

1. **Context window 变大但信息密度没有提升**：模型可以读 200K tokens，但 200K tokens 里的噪音（过时的日志、不相关的文件版本、历史操作的中间产物）同样可以被塞进来
2. **Third-party 工具的 context bloat**：MCP 调用返回的 JSON 可能比你正在编辑的核心代码还大，但 agent 无法区分主次
3. **Summarization 的不可逆损失**：当 context 满了，现有系统只能压缩——但压缩是有损的，关键细节被丢弃导致任务失败

> 官方原文引用：
> "The common approach coding agents take is to truncate long shell commands or MCP results. This can lead to data loss, which could include important information you wanted in the context."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

**Static Context 的根本缺陷**：它假设所有信息在「注入时」就已知其价值，但实际上，信息的价值取决于**当前任务所处的阶段**——同一份测试输出，在「写测试」阶段是核心上下文，在「写业务逻辑」阶段是噪音。

## 2. 动态上下文发现的核心机制

Cursor 的解决方案是**文件系统化**：把工具输出、聊天历史、MCP 工具描述都写成文件，让 agent 自己用 `grep`/`tail`/`read` 按需拉取。

### 2.1 长工具响应的文件化

```
旧模式：tool_call → JSON 200KB 全量塞入 context
新模式：tool_call → write to /tmp/tool_output_xxx.json → agent 用 tail/read 按需读取
```

**效果**：减少不必要的 summarization 触发次数。Cursor 内部测试显示，这个改动让 context 满了之后的 summarization 调用显著减少。

### 2.2 聊天历史的文件化引用

当 context window 满了，Cursor 给 agent 一个「历史文件的引用」，而不是强迫它压缩。Agent 如果发现 summary 里缺了关键细节，可以自己 `grep` 历史文件恢复。

> 官方原文引用：
> "After the context window limit is reached, or the user decides to summarize manually, we give the agent a reference to the history file. If the agent knows that it needs more details that are missing from the summary, it can search through the history to recover them."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

**这个设计背后的洞察**：Summarization 是**系统替 agent 做的主观决策**——系统认为这段历史「不重要」所以压缩掉，但这个判断可能和 agent 当前的任务需求冲突。让 agent 自己决定拉取什么，把决策权还给它。

### 2.3 MCP 工具的动态加载

这是效果最显著的优化：A/B 测试中，使用动态 MCP 加载的 agent 在调用 MCP 工具时**总 token 消耗降低了 46.9%**。

传统模式：MCP server 的所有工具定义 + 描述 → 全量塞入 system prompt
动态模式：只塞工具名称列表 + "需要时用 grep 查找" 的指令

> 官方原文引用：
> "We believe it's the responsibility of the coding agents to reduce context usage. In Cursor, we support dynamic context discovery for MCP by syncing tool descriptions to a folder."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

Cursor 还做了额外的设计：**文件夹结构保持按 server 分组**，而不是扁平索引。这样 agent 看到的是一个 cohesive unit（"这个 server 的所有工具"），而不是散落一地的工具描述。

### 2.4 终端 session 的文件系统化

Cursor 将集成终端的输出同步到本地文件系统，agent 可以直接 `grep` 特定输出，而不需要 copy/paste。

这让 Cursor agent 和 CLI-based agent（Claude Code 等）在上下文来源上变得一致：历史 shell 输出都通过文件系统暴露，只是 CLI agent 是静态注入，Cursor 是动态拉取。

## 3. 为什么这个转变有效：信息论视角

Dynamic context discovery 有效的根本原因是：**好的 context 不是「多」的 context，而是「信噪比高」的 context**。

当 agent 的 context window 装的是「所有可能相关的信息」时，它面临的是**信息检索负担**——它需要自己从大量噪音中筛选出真正相关的信息。而当 context window 装的是「当前任务直接相关的信息」时，agent 的推理资源可以全部用于任务本身。

**认知负荷理论**也支持这个结论：给模型更少的干扰项实际上提升了它处理核心问题的能力——这和人类专家在「整洁桌面」上工作效率更高的现象是一致的。

## 4. 适用边界与局限

**动态上下文发现不适合什么场景**：
1. **第一次冷启动**：Agent 还没建立足够的问题模型，不知道该拉取什么时，动态发现反而增加无效搜索
2. **实时性要求极高的任务**：例如监控告警、实时交互，grep 文件的 IO 开销可能不可接受
3. **上下文之间有隐藏依赖**：如果文件 A 和文件 B 的关系是「知道 A 才能理解 B」，但 agent 先看到 B，动态发现可能会让它走入死胡同

**文件抽象的局限性**：
> 官方原文引用：
> "It's not clear if files will be the final interface for LLM-based tools."
> — [Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

Cursor 自己也承认，文件只是一个「目前足够简单且足够强大的原语」，不一定是最终形态。例如，structured search（比如向量检索）可能比 grep 更适合语义相关的上下文拉取。

## 5. 工程实践建议

### 如何在你的 Agent 中实现动态上下文发现

**最小化可行实现（3步）**：

```
Step 1: 工具响应文件化
- 所有 >10KB 的工具响应写入 /tmp/context/{uuid}.json
- Agent system prompt 中添加：">10KB tool outputs are stored in /tmp/context/ — use tail/read to access"

Step 2: 聊天历史摘要引用
- 每次 summarization 时保留完整 history file path
- Agent 可用 grep 恢复 summary 中缺失的关键细节

Step 3: MCP 工具按需加载
- 只在 system prompt 中放工具名列表
- 提供 "lookup_mcp_tools(query)" 工具，agent 主动查找需要的工具
```

**检测动态上下文是否生效的指标**：
- Summarization 调用频率（应该下降）
- 任务完成率（跨 session 任务应该提升）
- Agent 的 grep/read 调用分布（应该集中在你预期的工作流上）

## 6. 与其他方案的对比

| 方案 | 上下文组织方式 | 优点 | 缺点 |
|------|--------------|------|------|
| Static Context（传统）| 全部塞入 context window | 简单，agent 无需主动搜索 | 200K tokens 限制，信噪比低 |
| Dynamic Context Discovery（Cursor）| 文件按需拉取 | 46.9% token 降低，agent 自主决策 | 需要工具层改造，IO 开销 |
| Hierarchical Memory（LangChain）| 层级压缩 + 检索 | 系统控制质量，可解释 | 压缩损失不可避免，检索质量依赖嵌入模型 |
| Context Caching（OpenAI）| KV Cache 复用 | 相同前缀只计算一次 | 只适合「共享前缀」场景，不适合动态内容 |

> 笔者的判断：动态上下文发现代表了 context 工程从「系统为中心」到「agent 为中心」的转变。未来的主流架构很可能是**混合的**：静态注入「元上下文」（agent 的目标、约束、可用工具），动态拉取「任务上下文」（历史操作、中间结果、相关文件）。

---

**关联主题**：
- 关联 Project：[GS-2](./gsd-2-gsd-build-autonomous-coding-agent-7269-stars-2026.md) — 其 DB 权威状态实际上也是一种「动态上下文」：agent 的状态不靠 summarization 压缩保留，而是靠外部 DB 按需恢复
- 关联 Article：[Anthropic「Effective Harnesses」](./anthropic-effective-harnesses-long-running-agents-initializer-pattern-2026.md) — Anthropic 的方案是「双组件架构」，Cursor 的方案是「动态拉取」，两者都指向同一个结论：**跨 session 的状态不能靠 summarization，必须靠外部存储**

---

*来源：[Cursor Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)（2026 年 5 月）*
