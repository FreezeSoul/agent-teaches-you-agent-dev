# agentmemory：免数据库的 Agent 持久记忆基础设施

> 628 stars/day · 95.2% R@5 · 16+ Agent 共享 · $10/年 · **5,530 Stars（2026-05-12）**

---

## 目标用户

有跨会话记忆需求的 AI Coding Agent 用户——无论你用 Claude Code、Cursor、Windsurf 还是 Gemini CLI，只要你的 Agent 在每次新 session 都要重新学习项目架构和之前讨论过的决策，agentmemory 就是为你设计的。

**水平要求**：有 AI Coding 经验，知道什么是"每次都要重新解释项目结构"的痛苦。

---

## 核心改变

你 explain the same architecture every session. You re-discover the same bugs. You re-teach the same preferences.

Built-in memory（CLAUDE.md / .cursorrules）上限 200 行且会过时。agentmemory 静默记录 Agent 的行为，将内容压缩为可检索的记忆，并在下次 session 启动时注入正确上下文。**一个命令，跨所有 Agent 生效。**

> "You explain the same architecture every session. You re-discover the same bugs. You re-teach the same preferences. Built-in memory (CLAUDE.md, .cursorrules) caps out at 200 lines and goes stale. agentmemory fixes this."
> — [agentmemory README](https://github.com/rohitg00/agentmemory)

**使用前 vs 使用后对比**：

| 场景 | 无 agentmemory | 有 agentmemory |
|------|--------------|----------------|
| Session 1 | 设置 JWT auth（jose middleware） | 完成 ✓ |
| Session 2 | 问 rate limiting | Agent 已知道 auth 用 `jose` 在 `src/middleware/auth.ts`，测试覆盖 token 验证，选择 jose 是因为 Edge 兼容性 |
| Session 3 | 问缓存策略 | Agent 知道之前讨论过 Redis 作为缓存，不是因为你告诉它，而是因为它记得 |

---

## 为什么能做到

### 架构选择：iii engine 驱动的零依赖设计

agentmemory 的核心依赖只有两个：SQLite + iii-engine，**无外部向量数据库依赖**。

这与竞品形成鲜明对比：

| 项目 | 依赖 |
|------|------|
| agentmemory | SQLite + iii-engine（内置）|
| mem0 | Qdrant / pgvector（外部依赖）|
| Letta / MemGPT | Postgres + vector DB（外部依赖）|

> "External deps: None (SQLite + iii-engine) vs Qdrant / pgvector vs Postgres + vector DB"
> — [agentmemory README: vs Competitors](https://github.com/rohitg00/agentmemory#vs-competitors)

iii-engine 提供了 BM25 + Vector + Graph 的混合检索（RRF fusion），all-MiniLM-L6-v2 嵌入模型运行在本地（无 API key，无成本）。

### 检索精度：95.2% R@5

在 ICLR 2025 LongMemEval-S（500 题）上的评测数据：

| 系统 | R@5 | R@10 | MRR |
|------|-----|------|-----|
| agentmemory | **95.2%** | **98.6%** | **88.2%** |
| BM25-only fallback | 86.2% | 94.6% | 71.5% |

> "LongMemEval-S (ICLR 2025, 500 questions): agentmemory 95.2% R@5, 98.6% R@10, 88.2% MRR"
> — [agentmemory README: Benchmarks](https://github.com/rohitg00/agentmemory#retrieval-accuracy)

对比竞品检索精度（来源：[benchmark/COMPARISON.md](https://github.com/rohitg00/agentmemory/blob/main/benchmark/COMPARISON.md)）：

| 系统 | R@5 |
|------|-----|
| agentmemory | **95.2%** |
| Letta / MemGPT（LoCoMo）| 83.2% |
| mem0（LoCoMo）| 68.5% |
| Built-in（grep）| N/A |

### Token 效率：$10/年 vs 无法处理的 19.5M tokens

| 方案 | Tokens/年 | 成本/年 |
|------|----------|-------|
| 粘贴完整上下文 | 19.5M+ | 不可能（超出窗口）|
| LLM 摘要 | ~650K | ~$500 |
| agentmemory | ~170K | ~$10 |
| agentmemory + 本地嵌入 | ~170K | $0（免费）|

> "Embedding model: all-MiniLM-L6-v2 (local, free, no API key)"
> — [agentmemory README](https://github.com/rohitg00/agentmemory)

### 多 Agent 共享：16+ Agent 通过 MCP + REST 互联

agentmemory 的设计哲学：**一个服务器，记忆在所有 Agent 间共享**。

支持的 Agent：

> "Claude Code (12 hooks + MCP + skills) / Cursor (MCP server) / Gemini CLI / Codex CLI / Cline / OpenCode / Goose / Kilo Code / Aider / Claude Desktop / Windsurf / Roo Code / Claude SDK / OpenClaw / Hermes"
> — [agentmemory README](https://github.com/rohitg00/agentmemory#works-with-every-agent)

跨 Agent 协调机制：MCP + REST + leases + signals，与其他竞品的 API-only 无协调方案形成对比。

### 记忆生命周期：4-tier consolidation + auto-forget

> "Memory lifecycle: 4-tier consolidation + decay + auto-forget" vs mem0 的 Passive extraction / Letta 的 Agent-managed / Built-in 的 Manual pruning

---

## 快速上手

**Step 1：启动记忆服务器**
```bash
npx @agentmemory/agentmemory
```

**Step 2：在你的 Agent 中添加 MCP Server**

MCP 配置在所有主流 Agent 中完全相同：
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"],
      "env": { "AGENTMEMORY_URL": "http://localhost:3111" }
    }
  }
}
```

支持的配置文件路径：Cursor (`~/.cursor/mcp.json`) / Claude Desktop / Cline / Windsurf / Gemini CLI / OpenClaw / Codex CLI / OpenCode。

**Step 3：验证**
```bash
curl http://localhost:3111/agentmemory/health
# 打开 http://localhost:3113 查看实时 viewer
```

**导入已有的 Claude Code 历史记录**：
```bash
npx @agentmemory/agentmemory import-jsonl ~/.claude/projects/-my-project/abc123.jsonl
```

> "Import everything under the default ~/.claude/projects: npx @agentmemory/agentmemory import-jsonl" — [agentmemory README: Import](https://github.com/rohitg00/agentmemory#import-jsonl)

---

## 技术深度

### 基础：Karpathy 的 LLM Wiki 模式的增强实现

agentmemory 建立在 Karpathy 的 LLM Wiki 模式之上，但增加了四个关键增强：

> "The gist extends Karpathy's LLM Wiki pattern with confidence scoring, lifecycle, knowledge graphs, and hybrid search."
> — [agentmemory README](https://github.com/rohitg00/agentmemory)

这四个增强解决了原版 LLM Wiki 模式的三个问题：
1. **confidence scoring**：解决"哪些记忆是可靠的"问题，避免低置信度记忆被注入导致误导
2. **lifecycle + auto-forget**：解决记忆过期问题，不再需要手动清理 CLAUDE.md
3. **knowledge graphs**：解决关系型记忆的检索问题，不只是匹配内容，还理解实体关系
4. **hybrid search**：解决单一检索模式的局限，BM25 + vector + graph 互补覆盖

### v0.9.0 的关键更新（2026-04-18）

> "v0.9.0 — Landing site at agent-memory.dev, filesystem connector (@agentmemory/fs-watcher), standalone MCP now proxies to the running server so hooks and the viewer agree, audit policy codified across every delete path, health stops flagging memory_critical on tiny Node processes"
> — [agentmemory README: Changelog](https://github.com/rohitg00/agentmemory/blob/main/CHANGELOG.md#090--2026-04-18)

filesystem connector 的引入意味着 agentmemory 不再只记录 Agent 的对话历史，还能监听文件系统变化，将代码变更纳入记忆。

---

## 与本轮 Article 的关联

本轮 Article 分析了 Anthropic 2026 年 4 月质量事件中的缓存污染 Bug：会话 idle 超过 1 小时后，thinking 历史在每个后续请求上都被清除，导致 Agent 在残缺上下文中继续运行，表现出"遗忘、重复和奇怪的工具选择"。

agentmemory 解决的是这个问题的**工具层方案**：当 Agent 的上下文无法依赖平台层的缓存机制时，外部化的记忆基础设施提供了一个独立于平台缓存策略的记忆层，确保跨会话的项目知识不会因为平台配置变更而丢失。

> "Agent memory architecture: context state cannot depend on a single caching layer. When cache fails, there must be an explicit degradation path, not让 Agent 在残缺的上下文中继续运行并产出看似合理但实际无根据的结果。" — 来自本轮 Article

---

## 适合谁 / 不适合谁

**适合**：
- 长时间运行的 Agent 项目，项目上下文复杂
- 多个人共用同一个 Agent，项目知识需要跨用户积累
- 跨 session 的决策追踪（如架构选型、安全考虑、技术债务）

**不适合**：
- 单次性任务，不需要跨会话记忆
- 对外部数据库依赖有严格审查要求的场景（但 iii-engine 的 SQLite 本身已足够轻量）
- 需要在 200 行以内解决所有上下文的简单项目（直接写 CLAUDE.md 可能更简单）

---

**关联 Article**：[Anthropic April 2026 Postmortem：AI 系统的配置性降级](./anthropic-april-2026-postmortem-configuration-degradation-2026.md) — 配置变更导致的上下文污染与 agentmemory 的工具层解决方案