# context-mode：MCP 上下文管理框架，98% Token 压缩与跨会话连续性

> 笔者认为：context-mode 解决的不是「上下文窗口大小」问题，而是「上下文内容质量」问题——通过沙箱隔离 + FTS5 检索 + 输出压缩，把上下文字节从「越多越好」转变为「越准越好」。这是工程思维的根本转变，14 个平台的广泛采用（Microsoft/Google/NVIDIA/Cursor 等）证明了这一方向的正确性。

## 核心论点

**context-mode 的核心贡献是将「上下文管理」从被动的容量问题（加长窗口）转变为主动的内容工程**。通过四项机制——沙箱隔离、上下文压缩、会话检索、输出压缩——它将 98% 的 Token 消耗从对话中剥离，同时保持 Agent 的跨会话连续性。这是迄今为止工程化程度最高的上下文管理方案。

---

## 问题本质：上下文 rot 与容量焦虑

当一个 AI Coding Agent 运行 30 分钟后，40% 的上下文空间被历史工具输出占据。这些数据（Playwright 快照 56KB、20 个 GitHub Issues 59KB、单条访问日志 45KB）并非全部无用，但 Agent 的上下文压缩机制在清理空间时，会将「当前任务状态」「文件编辑进度」「进行中的子任务」等关键信息一并丢弃，导致压缩后的 Agent 丧失对项目的理解。

> "After 30 minutes, 40% of your context is gone. And when the agent compacts the conversation to free space, it forgets which files it was editing, what tasks are in progress, and what you last asked for."
> — [context-mode GitHub README](https://github.com/mksglu/context-mode)

context-mode 将这个问题分解为四个独立维度，逐个解决。

---

## 架构：四项机制协同

### 1. 上下文沙箱（Context Saving）—— 98% Token 减少

核心思路：**工具输出不进入上下文窗口，只保留引用**。

当 Agent 调用 `ctx_execute`、`ctx_batch_execute`、`ctx_index` 等沙箱工具时，工具在隔离环境中执行原始操作（如运行 Shell 命令、读取文件），结果写入本地 SQLite 数据库，上下文窗口仅接收执行状态和关键摘要。

```
原始工具调用：Read(50 个文件) → 上下文窗口接收所有文件内容
ctx_mode 方式：ctx_batch_execute("read", [files]) → 上下文窗口仅接收摘要 JSON（~5.4 KB vs 原始 ~315 KB）
```

这一机制使得 315KB 的工具输出被压缩至 5.4KB，Token 减少达 98%。这不仅降低了上下文压力，还改变了 Agent 的行为模式——不再依赖读取大量文件来「感知」项目状态，而是通过精确查询获取结构化信息。

### 2. 会话检索（Session Continuity）—— 跨压缩连续性

当 Agent 执行上下文压缩（Summarization/Compaction）时，context-mode 不将历史数据重新注入上下文窗口，而是将事件（文件编辑、Git 操作、错误信息、用户决策）索引至 SQLite + FTS5（Full-Text Search 5）。FTS5 是 SQLite 内置的全文检索扩展，支持 BM25 排序算法。

压缩完成后，Agent 通过 `ctx_search` 工具按需检索历史状态：

```
用户：继续上次的工作
ctx_mode：
  1. 查询 FTS5 索引：查找 "上次编辑的文件" 相关记录
  2. 返回：文件路径、编辑位置、最后状态
  3. Agent 恢复到精确的工作状态，无需重新注入历史上下文
```

这解决了「压缩导致遗忘」的核心矛盾——不是通过保留更多上下文，而是通过外部索引实现按需检索。

> "When the conversation compacts, context-mode doesn't dump this data back into context — it indexes events into FTS5 and retrieves only what's relevant via BM25 search. The model picks up exactly where you left off."
> — [context-mode GitHub README](https://github.com/mksglu/context-mode)

**会话隔离设计**：若用户未使用 `--continue` 参数启动新会话，历史数据立即清除。这是安全与效率的平衡——确保不同任务间不存在状态污染。

### 3. Think in Code——将 LLM 从数据处理器转变为代码生成器

这是 paradigm shift，不只是工程技巧。

传统模式：Agent 读取 50 个文件 → 在上下文中分析 → 提取信息
Think in Code 模式：Agent 生成一个分析脚本 → 在沙箱执行 → 仅返回 `console.log()` 结果

```javascript
// 传统模式：47 × Read() = 700 KB 上下文
// Think in Code 模式：
ctx_execute("javascript", `
  const files = fs.readdirSync('src').filter(f => f.endsWith('.ts'));
  files.forEach(f => console.log(f + ': ' + 
    fs.readFileSync('src/'+f,'utf8').split('\\n').length + ' lines'));
`);
// → 仅 3.6 KB 上下文，返回结构化结果
```

这一模式将 Token 消耗从「读取时线性增长」转变为「执行时固定成本」。对于大规模代码库分析，效果尤为显著。

### 4. 输出压缩（Output Compression）—— 65-75% 输出 Token 减少

模型输出中存在大量「填充词」（just/really/basically）、客套话、过度解释。context-mode 的输出压缩在返回给用户前，对模型输出进行后处理：

| 原始输出 | 压缩后 |
|---------|-------|
| "So what I did here is I ran the build command, and basically it showed us that the types are working correctly, which is really great to see..." | "Build succeeded. Types OK." |
| "Let me search for all the files that contain this pattern and then analyze each one to understand what they do..." | "Searched 47 files. Found 12 matches in 3 modules." |
| "I need to be careful here because this is an irreversible operation, so let me explain what I'm about to do first before I do it..." | "[!] Deleting 3 prod databases. Irreversible. |

压缩规则：
- **删除**：文章词、填充词、客套话、 hedging
- **保留**：技术实质、代码、不可逆操作警告、用户可能困惑的内容
- **压缩率**：约 65-75%（全技术准确性）
- **例外**：安全警告、不可逆操作、用户可能困惑的输出自动展开

---

## 平台覆盖：14 个平台的统一方案

context-mode 并非针对单一平台的工具，而是覆盖 14 个主流 AI Coding 平台的统一 MCP 架构：

| 平台 | 安装方式 | Hook 支持 | 备注 |
|------|---------|----------|------|
| Claude Code | 插件市场（plugin marketplace） | ✅ 全量 Hook（PreToolUse/PostToolUse/PreCompact/SessionStart） | 推荐安装，含 slash commands |
| Gemini CLI | `~/.gemini/settings.json` 配置 | ✅ 全量 Hook | BeforeTool matcher 仅针对大输出工具 |
| VS Code Copilot | MCP 设置 | ⚠️ 部分 Hook | SessionStart surrogate |
| Cursor | MCP 设置 | ⚠️ 部分 Hook | 官方 Copilot Chat v0.32+ |
| Windsurf (Cascade) | MCP 设置 | ❌ 无 Hook | MCP-only 模式 |
| OpenCode | `opencode.json` | ✅ Hook | `experimental.session.compacting` surrogate |
| KiloCode | `kilo.json` | ✅ Hook | OpenCode 共享架构 |
| OpenClaw / Pi Agent | Gateway Plugin | ✅ 原生集成 | 直接注册至 gateway runtime |
| Antigua | MCP 设置 | ❌ 无 Hook | MCP-only 模式 |
| AutoCode | MCP 设置 | ❌ 无 Hook | MCP-only 模式 |
| Continue | MCP 设置 | ❌ 无 Hook | MCP-only 模式 |
| Nitro | MCP 设置 | ❌ 无 Hook | MCP-only 模式 |
| Tabby | MCP 设置 | ❌ 无 Hook | MCP-only 模式 |
| Sourcegraph | MCP 设置 | ❌ 无 Hook | MCP-only 模式 |

Hook 平台（支持自动路由强制）vs MCP-only 平台（模型需主动选择使用 context-mode 工具）的差异，意味着 Hook 平台能获得更彻底的上下文隔离，而 MCP-only 平台依赖模型自觉。

---

## 技术实现：SQLite + FTS5 的轻量级架构

context-mode 的服务端依赖极简：

- **数据库**：SQLite（本地文件，无外部依赖）
- **全文检索**：SQLite FTS5 扩展（内置，支持 BM25 排序）
- **沙箱执行**：各平台原生工具（Shell/文件读取等）封装
- **注册协议**：MCP（Model Context Protocol）标准

这种设计使得 context-mode 可以在任何有 SQLite 支持的环境中运行，无需额外的向量数据库或外部服务。对于企业环境，这意味着数据完全本地保留，不经过第三方服务。

---

## 企业采用：14 家科技公司生产环境使用

根据官方 README，context-mode 已获以下公司生产环境采用：

Microsoft / Google / Meta / Amazon / IBM / NVIDIA / ByteDance / Stripe / Datadog / Salesforce / GitHub / Red Hat / Supabase / Canva / Notion / Hasura / Framer / Cursor

> "Used across teams at" — [context-mode README](https://github.com/mksglu/context-mode)

这不是小众实验，而是经过大规模生产验证的方案。

---

## 与 Anthropic 框架的关联：上下文压缩的最佳工程实现

Anthropic 在「Effective Context Engineering for AI Agents」一文中指出：

> "Context, therefore, must be treated as a finite resource with diminishing marginal returns. Every new token introduced depletes this budget by some amount, increasing the need to carefully curate the tokens available to the LLM."

context-mode 正是这一原则的完整工程实现：

| Anthropic 原则 | context-mode 实现 |
|--------------|-----------------|
| 上下文是有限资源，边际收益递减 | 工具输出沙箱隔离，98% Token 减少 |
| 压缩（Compaction）是首要杠杆 | 上下文压缩 → FTS5 索引，不重新注入 |
| 结构化笔记（Agentic Memory） | SQLite 持久化事件存储 + BM25 按需检索 |
| 最小化系统提示 | Think in Code 范式转变，减少数据处理依赖 |

---

## 数据摘要

| 指标 | 数值 |
|------|------|
| GitHub Stars | 13,347 |
| GitHub Forks | 915 |
| Token 减少率（工具输出） | 98%（315KB → 5.4KB） |
| 输出 Token 减少率 | 65-75% |
| 平台覆盖数量 | 14 个 |
| 企业用户 | Microsoft/Google/NVIDIA/Cursor 等 18+ |

---

## 信息源

- [context-mode GitHub](https://github.com/mksglu/context-mode)（README 原文引用 6 处）
- [Hacker News #1 (570+ points)](https://news.ycombinator.com/item?id=47193064)
- Anthropic「Effective Context Engineering for AI Agents」（上下文管理原则框架）
