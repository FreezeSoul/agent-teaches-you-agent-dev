# Claude Code Memory Setup：Obsidian + Graphify 构建的 Token 优化方案

## 定位破题

**谁该关注**：使用 Claude Code 进行长程开发、有多项目维护需求、对 token 成本敏感、或希望 Claude Code 能跨 Session 保持上下文连续性的开发者。

**场景锚定**：当你发现自己每天都在重新向 Claude Code 解释「项目用什么技术栈、之前做了什么决定、现在在处理什么问题」时——这就是你需要这个项目的时刻。

**差异化标签**：**71.5x Token 节省**——不是压缩模型输出的 token 数量，而是通过结构化知识管理，让 Claude Code 从「重新读取」变成「查询已有上下文」。

---

## 体验式介绍

想象你每天早上打开 Claude Code 开始工作。没有这个项目时，这个过程是这样的：

```
你：我的这个 React 项目上周在处理什么问题？
Claude：不知道，我们之前没见过
你：好吧，我上次用的是 Supabase Auth，现在想加 GitHub 登录...
Claude：[重新读取所有文件，了解项目结构]
Token：~20,000 tokens 用于 Orientation
```

加上这个项目后：

```
你：我的这个 React 项目上周在处理什么问题？
Claude：根据你的 session log，你在处理 Supabase Auth 的刷新 token 问题。
你：现在想加 GitHub 登录
Claude：明白了。根据代码结构，Auth 模块在 src/auth/，现有实现用的是 OAuth2 隐式流。
      建议在 src/auth/providers/github.ts 新增 provider。
Claude：[查询 graph.json 了解代码连接关系]
Token：~280 tokens 用于查询
```

区别在于：**Claude 知道你是谁，项目是什么，之前做了什么**。不是通过记忆（LLM 本身就是健忘的），而是通过外部化的知识管理系统。

---

## 拆解验证

### 技术架构：三层记忆体系

这个项目的架构设计非常清晰，用三个互补的组件解决不同层面的记忆问题：

**第一层：Obsidian Zettelkasten（持久决策记忆）**

解决「项目级上下文」——架构决策、技术选型、进度追踪。Obsidian 作为第二大脑，Claude Code 通过 `/resume` 和 `/save` 命令与 vault 交互。

关键设计决策：

- **单一 Vault 跨所有项目**：不是每个项目一个 vault，而是所有项目的笔记存在同一个 vault 中。这样跨项目的知识（如「Supabase Auth」模式）可以复用，不同项目的笔记在 Obsidian 图谱中自动连接
- **Zettelkasten 方法论**：每条笔记原子化（一个概念一条），密集互联（每条至少两个 wikilinks），带标准化 YAML frontmatter。这不是为了形式主义，而是让笔记可以被 Claude Code 结构化理解和查询

官方原文引用：

> "Having one vault per project fragments knowledge. With a single vault, a note about 'Supabase Auth' links to both project A and B. The graph view reveals cross-project connections you didn't expect."
> — [lucasrosati/claude-code-memory-setup README](https://github.com/lucasrosati/claude-code-memory-setup)

**第二层：Graphify（代码结构知识图谱）**

解决「代码库上下文」——文件关系、模块边界、函数调用链。当 Claude Code 需要理解代码结构时，查询 graph.json 而非重新读取所有文件。

关键数据：

| 指标 | 值 |
|------|---|
| Token 节省（查询时）| **499x**（~280 vs ~140,000 tokens）|
| Token 生成成本 | **0 tokens**（纯 tree-sitter AST 模式）|
| 支持语言数 | 20+（Python/JavaScript/TypeScript/Go/Rust/Java/C/C++/Ruby/C# 等）|
| 重处理触发 | SHA256 缓存，只处理变更文件 |

官方原文引用：

> "Graphify transforms your codebase into a queryable knowledge graph. Instead of Claude Code re-reading every file, it queries the graph — which is persistent across sessions and costs a fraction of the tokens."
> — [lucasrosati/claude-code-memory-setup README](https://github.com/lucasrosati/claude-code-memory-setup)

**第三层：Chat Import Pipeline（对话历史外部化）**

解决「对话上下文」——每次 Claude Code 对话中产生的洞察和决策，通过定时 cron job 自动导入 vault。避免对话历史的丢失，同时让历史对话内容可以被检索和复用。

### Token 优化的量化数据

项目在真实项目上测试的数据：

| 测试场景 | React + Supabase 项目（126 TypeScript 文件）|
|---------|------------------------------------------|
| Graph 节点数 | 332 |
| 边数（连接数）| 258 |
| 图谱大小 | 172 KB |
| Obsidian 生成笔记 | 456 条 |
| Token 节省倍数（查询）| **499x** |
| LLM 调用成本（生成）| **0 tokens**（AST 模式）|

### 竞品对比：与其他记忆方案的定位差异

| 方案 | 解决的问题 | Token 影响 | 维护成本 |
|------|-----------|-----------|---------|
| **本项目（Obsidian + Graphify）** | 决策记忆 + 代码结构 + 对话历史 | 查询 499x 节省 | 中等（需要维护 vault 和 graphify）|
| **mem0** | 通用 Agent 记忆层 | 取决于使用频率 | 低（自动记忆）|
| **graphiti** | 对话上下文追踪 | 中等 | 中等（MCP Server 接入）|
| **agentmemory** | 跨 Agent 共享记忆 | 取决于场景 | 中等（需要 iii engine）|

本项目的差异化在于：**Token 优化是通过减少「重新读取」实现的，而非压缩上下文本身**。这是更根本的解法，因为无论上下文窗口多大，重新读取都是浪费。

### 社区健康度

- **Stars**：590（2026-04-12 创建，不到一个月）
- **GitHub 增长**：稳定增长，作为 Claude Code 配套工具链的一部分
- **文档完整性**：README 极其详细，包含完整架构图、工作流说明、故障排除指南
- **主题匹配度**：直接服务于第三时代长程 Agent 的核心痛点（上下文管理）

---

## 行动引导

### 快速上手（3 步）

**1. 创建 Obsidian Vault**

```bash
# 下载 Obsidian，创建 vault
# 建立标准文件夹结构
cd ~/vault
mkdir -p permanent inbox fleeting templates logs references
```

**2. 安装 Graphify**

```bash
pip install graphifyy
graphify install

# 生成项目图谱
cd ~/my-project
graphify . --obsidian --obsidian-dir ~/vault/graphify/my-project
```

**3. 配置 Claude Code 指令**

在 Vault 根目录创建 `CLAUDE.md`，写入 Context Navigation 规则；Claude Code 读取 vault 中的上下文，查询 graph.json 而非重新读取文件。

### 进阶配置

- **Chat Import Pipeline**：安装 `claude-conversation-extractor`，配置 cron job 自动导入对话历史
- **Git Hook**：自动在每次 commit 后重建图谱

```bash
graphify hook install
```

- **多项目管理**：新项目只需运行 `graphify` 命令，笔记自动出现在 Obsidian 图谱中

### 持续关注

- 项目活跃度高（2026-04-12 创建，不到一个月）
- 适合与 Cursor 3 Agent Fleet 工作流配合使用——当 Agent 在云端长时间运行时，Obsidian vault 作为持久上下文提供者

---

## 主题关联

本项目与本轮 Articles 主题「Cursor 3 与第三次软件工程时代」形成紧密关联：

**关联逻辑**：Cursor 3 揭示了第三时代的核心特征——Agent Fleet 在更长的时间尺度上自主运行。长程 Agent 面临的核心问题是**上下文跨 Session 的连续性**。Claude Code Memory Setup 通过三层记忆体系（Obsidian + Graphify + Chat Pipeline）在基础设施层面解决了这个问题。

两者的关联体现在：

- **共同的技术趋势**：都在解决「Agent 长时间运行」带来的上下文管理问题
- **互补的解决方案**：Cursor 3 提供了 Agent 调度的界面层，Claude Code Memory Setup 提供了 Agent 的记忆基础设施
- **共同的优化目标**：减少 token 浪费（前者通过 Artifact 预览，后者通过结构化知识查询）

---

**原文引用**：

1. "71.5x fewer tokens per session with Graphify and permanent memory across sessions with Obsidian Zettelkasten." — [lucasrosati/claude-code-memory-setup README](https://github.com/lucasrosati/claude-code-memory-setup)
2. "Having one vault per project fragments knowledge. With a single vault, a note about 'Supabase Auth' links to both project A and B. The graph view reveals cross-project connections you didn't expect." — [lucasrosati/claude-code-memory-setup README](https://github.com/lucasrosati/claude-code-memory-setup)
3. "Graphify transforms your codebase into a queryable knowledge graph. Instead of Claude Code re-reading every file, it queries the graph — which is persistent across sessions and costs a fraction of the tokens." — [lucasrosati/claude-code-memory-setup README](https://github.com/lucasrosati/claude-code-memory-setup)
4. "Code: processed 100% locally via tree-sitter AST. No code content leaves your machine." — [lucasrosati/claude-code-memory-setup README](https://github.com/lucasrosati/claude-code-memory-setup)
5. "Token reduction per query: 499x" — [lucasrosati/claude-code-memory-setup README](https://github.com/lucasrosati/claude-code-memory-setup)
