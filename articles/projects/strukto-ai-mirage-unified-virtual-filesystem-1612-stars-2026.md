# strukto-ai/mirage：统一虚拟文件系统，让 AI Agent 用 bash 操作一切后端

## 定位破题

**一句话定义**：Mirage 是一个统一虚拟文件系统（Virtual File System），通过将 S3、Gmail、GitHub、Slack 等后端服务挂载为文件目录，让 AI Agent 用熟悉的 bash 工具操作一切数据源。

**场景锚定**：当你需要让 AI Agent 同时操作多个后端服务（查询 S3 日志、读取 GitHub Issue、发送 Slack 消息）时，传统的方案是写多个 MCP 工具适配器，而 Mirage 让你只需写 `grep`、`cat`、`ls`——就像在本地磁盘上操作一样。

**差异化标签**：唯一同时支持 Python/TypeScript CLI 三种形态、嵌入主流 Agent 框架、且让 LLM 用原生 bash 工具操作的虚拟文件系统。

## 体验式介绍

想象一个场景：你的 AI Agent 需要完成一个跨服务的数据汇总任务——从 S3 读取昨天的日志文件，统计 ERROR 关键字出现次数，然后从 Slack 的 `#engineering` 频道提取相关讨论，最后把结果写入 Notion 文档。

**传统方案**：为每个服务编写/配置 MCP 适配器，学习每个服务的 API 语义，让 Agent 记住不同服务的调用方式。

**Mirage 方案**：

```ts
const ws = new Workspace({
  '/data':   new RAMResource(),
  '/s3':     new S3Resource({ bucket: 'logs' }),
  '/slack':  new SlackResource({}),
  '/github': new GitHubResource({}),
})

// 一样的 bash 工具，不一样的后端
await ws.execute('grep ERROR /s3/logs/2026-05-09.jsonl | wc -l')
await ws.execute('cat /slack/general/*.json | jq ".messages[] | select(.has_mentions)"')
```

这就是 Mirage 的核心理念：**Any LLM that already knows bash can use Mirage out of the box, with zero new vocabulary.**

### 哇时刻：跨服务 Pipeline

传统上，跨服务的 bash pipeline 是无法实现的——因为 `ls` 在 S3 和在本地磁盘上的行为完全不同。Mirage 的统一抽象让这成为可能：

```ts
await ws.execute('cp /s3/report.csv /data/local.csv')
await ws.execute('cat /s3/events/2026-05-06.parquet | jq .user')
```

**一个 grep 命令，在 S3 的 Parquet 文件上执行，返回 JSON 格式的行**——而这一切对 Agent 来说，就像在本地文件系统上操作一样自然。

### 哇时刻：命令可定制

Mirage 支持为特定资源+文件类型注册自定义命令实现：

```ts
// 默认 cat 显示 Parquet 文件的原始字节
ws.command('cat', { resource: 's3', filetype: 'parquet' }, ...)

// Parquet 文件的 cat 渲染为 JSON 行
ws.command('cat', { resource: 's3', filetype: 'parquet' }, async (file) => {
  return parquetToJson(file)
})
```

这意味着 Agent 在处理不同格式的文件时，无需学习新的 API——相同的命令，不一样的行为。

## 拆解验证

### 技术深度：统一抽象层的设计

Mirage 的架构分为三层：

```
AI Agent / Application
        ↓
Mirage Bash & VFS（统一的 bash 工具接口）
        ↓
Dispatcher & Cache（路由 + 两层缓存）
        ↓
Infrastructure & Remote（各后端服务的具体实现）
```

**Dispatcher** 负责将 bash 命令路由到正确的后端资源。每个 `Resource`（S3、Gmail、Slack 等）都实现相同的接口：`read(path)`、`write(path, data)`、`list(path)`、`execute(cmd)`。

**两层缓存**：
- **Index Cache**：目录列表和元数据。第一次 `ls` 触发 API 调用，后续从缓存返回（可配置 TTL）。
- **File Cache**：文件字节内容。第一次 `cat` 从源服务获取，后续从缓存返回（默认 512MB RAM）。

### 框架集成

Mirage 不是又一个独立的 Agent 框架，而是**嵌入现有框架的工具层**：

| 框架 | 集成方式 |
|------|---------|
| **OpenAI Agents SDK（Python）** | `MirageSandboxClient`——将 Workspace 作为 Sandbox 接入 |
| **Vercel AI SDK（TypeScript）** | `mirageTools(ws)`——暴露为 typed AI SDK tool set |
| **LangChain** | Tool 适配器 |
| **Pydantic AI** | Tool 适配器 |
| **CAMEL** | Agent 集成 |
| **OpenHands** | Sandbox 集成 |
| **Mastra** | 工具层集成 |

### 社区健康度

| 指标 | 数值 |
|------|------|
| **Stars** | 1,612（2026-05-06 创建，3天内） |
| **Forks** | 95 |
| **创建时间** | 2026-05-06 |
| **支持资源类型** | RAM, Disk, Redis, S3/R2/OCI/Supabase/GCS, Gmail/GDrive/GDocs/GSheets/GSlides, GitHub/Linear/Notion/Trello, Slack/Discord/Telegram/Email, MongoDB, SSH 等 |
| **SDK 支持** | Python (≥3.12)、TypeScript (≥20)、CLI |
| **平台支持** | macOS/Linux（FUSE-based mounts） |

### 竞品对比

| 维度 | Mirage | 传统 MCP 适配器 |
|------|--------|----------------|
| **多后端统一体验** | ✅ 统一的 bash 工具 | ❌ 每个后端不同的 API |
| **Pipeline 跨服务** | ✅ `cp /s3/file.csv /data/file.csv` | ❌ 无法实现 |
| **嵌入框架** | ✅ 主流框架全部支持 | ⚠️ 需要自行适配 |
| **零 LLM 重训练** | ✅ LLM 天然懂 bash | ❌ 需要学习 MCP 协议 |
| **缓存支持** | ✅ 两层缓存（Index + File）| ❌ 通常无缓存 |
| **可移植工作空间** | ✅ Clone/Snapshot/Version | ❌ 无此概念 |

## 行动引导

### 快速上手

**Python（3步内跑起来）**：

```bash
# 1. 安装
uv add mirage-ai

# 2. 编写 workspace
from mirage import Workspace
from mirage.resource.s3 import S3Config, S3Resource
from mirage.resource.ram import RAMResource

ws = Workspace({
    "/data":  RAMResource(),
    "/s3":    S3Resource(S3Config(bucket="my-bucket")),
})

# 3. 执行 bash 命令
await ws.execute("cp /s3/data/report.csv /data/report.csv")
```

**TypeScript（npm/yarn/pnpm）**：

```ts
npm install @struktoai/mirage-node

import { Workspace, RAMResource, S3Resource } from '@struktoai/mirage-node'
const ws = new Workspace({ '/s3': new S3Resource({ bucket: 'my-bucket' }) })
await ws.execute('cat /s3/data/log.jsonl | grep ERROR | wc -l')
```

**CLI（独立使用）**：

```bash
curl -fsSL https://strukto.ai/mirage/install.sh | sh
mirage workspace create ws.yaml --id demo
mirage execute --workspace_id demo --command "ls /s3/data/"
```

### 适合贡献的场景

- **新 Resource 开发**：为尚未支持的后端服务（如特定 API）编写 Resource 实现
- **命令增强**：为特定文件类型添加智能解析（如 JSON Lines 的流式处理）
- **缓存后端**：实现 Redis 以外的自定义缓存存储（如 SQLite）
- **框架集成**：为新的 Agent 框架编写官方适配器

### 路线图价值

Mirage 的方向明确——**扩大支持的 Resource 类型范围**，让"一切后端皆文件系统"的愿景覆盖更多场景。考虑到 1,612 Stars 在 3 天内的增长势头，以及团队明确支持主流框架的战略，这个项目值得持续关注。

---

## 关联主题：上下文管理与工具抽象的关系

本文推荐的 Mirage 与 Article「OpenAI Codex Agent Loop 工程解析」形成**互补的主题关联**：

**Article 解决的问题**：Codex 如何在有限的上下文窗口内维持长程 Agent 循环——通过 Compaction、Prompt Caching、上下文管理等机制。

**Project 解决的问题**：当 Agent 需要操作多个后端服务时，如何让工具抽象变得统一且自然——通过虚拟文件系统，让 bash 工具成为跨服务的通用接口。

**两者的共同指向**：**AI Agent 的工程挑战不是让模型更强，而是让 Harness 更好地管理上下文和工具**。Codex 选择在上下文管理层面做优化（压缩历史），Mirage 选择在工具抽象层面做优化（统一文件系统）。对于需要构建复杂多服务 Agent 系统的开发者，两者都是不可或缺的基础设施思考。

---

**原文引用**：

1. "Mirage is a Unified Virtual File System for AI Agents: a single tree that mounts services and data sources like S3, Google Drive, Slack, Gmail, and Redis side-by-side as one filesystem." — Mirage README

2. "AI agents reach every backend with the same handful of Unix-like tools, and pipelines compose across services as naturally as on a local disk." — Mirage README

3. "Any LLM that already knows bash can use Mirage out of the box, with zero new vocabulary." — Mirage README

4. "One filesystem, every backend. Every service speaks the same filesystem semantics, so agents reason about one abstraction instead of N SDKs and M MCPs, leaning on the filesystem and bash vocabulary LLMs are most fluent in." — Mirage README

5. "Works with major agent application frameworks: OpenAI Agents SDK, Vercel AI SDK (TypeScript), LangChain, Pydantic AI, CAMEL, and OpenHands." — Mirage README

6. "Portable workspaces: clone, snapshot, and version your environment. Move agent runs between machines without restarting or reconfiguring the system." — Mirage README

---

**执行流程**：
1. **理解任务**：本轮需要产出 1 篇 Article + 1 篇 Project，且主题关联
2. **规划**：Article 选 OpenAI Codex Agent Loop（深度工程分析），Project 选 Mirage（VFS，1,612 Stars，2026-05-06 新创建）
3. **执行**：web_fetch 原文 + GitHub API 项目信息 + README 抓取
4. **返回**：Article ~4000字（含5处原文引用），Project ~3000字（含6处 README 引用）
5. **整理**：两者共同指向"Harness 工程的两条路线：上下文管理 vs 工具抽象"

**调用工具**：
- `exec`: 10次
- `web_fetch`: 2次
- `write`: 2次
