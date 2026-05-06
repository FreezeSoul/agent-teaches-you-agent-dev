# Sandcastle：Git Worktree 隔离的 Claude Code 生产编排工具

> 本文要回答：Sandcastle 是什么、如何实现「零污染 Git 分支 + 隔离沙箱」的 Agent 编排、以及它和 Cursor SDK 的互补关系。
>
> 读完你将得到：掌握 Sandcastle 的 Docker/Podman/Vercel 三层隔离架构、理解 Git Worktree 分支策略的工程原理、并能判断「何时该用 Sandcastle vs Cursor SDK」。

---

## 0. 关联性说明

本文是 [Cursor SDK 分析文章](./cursor-sdk-programmatic-agent-typescript-2026.md) 的配套项目推荐。

两者解决同一个问题的不同层面：

| 工具 | 解决的问题 | 适用场景 |
|------|-----------|---------|
| **Cursor SDK** | 如何用代码调用 Cursor 的 Agent Runtime | 嵌入产品、CI/CD 自动化、内部工具 |
| **Sandcastle** | 如何在隔离环境中可靠地运行 Claude Code | 生产级 Agent 编排、需要 Git 分支隔离 |

Cursor SDK 是「如何使用 Cursor 的 Runtime」，Sandcastle 是「如何让 Claude Code 在隔离生产环境中跑得安全」。

---

## 1. 是什么：一次调用完成沙箱隔离 + Git 分支管理

Sandcastle 是 Matt Pocock（Total TypeScript 创始人）开源的 TypeScript 库，核心能力：

> "A TypeScript library for orchestrating AI coding agents in isolated sandboxes: You invoke agents with a single `sandcastle.run()`. Sandcastle handles sandboxing the agent with a configurable branch strategy. The commits made on the branches get merged back."
> — [GitHub: mattpocock/sandcastle README](https://github.com/mattpocock/sandcastle)

三件事一次解决：
1. **沙箱隔离**：在 Docker / Podman / Vercel 中运行 Agent
2. **分支策略**：Agent 在独立的 Git Worktree 上工作，不污染主分支
3. **合并回溯**：工作完成后，Worktree 的提交自动合并回主干

---

## 2. 核心设计：SandboxProvider 体系

Sandcastle 的核心抽象是 `SandboxProvider`——一个插件式接口，定义了「如何在隔离环境中运行 Agent」。

### 2.1 三种内置 Provider

| Provider | 隔离类型 | Import | 适用场景 |
|----------|---------|--------|---------|
| **Docker** | Bind-mount | `@ai-hero/sandcastle/sandboxes/docker` | 最常见的本地开发 |
| **Podman** | Bind-mount | `@ai-hero/sandcastle/sandboxes/podman` | 无 root 需求的场景 |
| **Vercel** | Firecracker MicroVM | `@ai-hero/sandcastle/sandboxes/vercel` | 云端隔离、快速扩缩 |

官方原文：

> "Sandcastle is provider-agnostic — it ships with built-in providers for Docker, Podman, and Vercel, and you can create your own using `createBindMountSandboxProvider` or `createIsolatedSandboxProvider`."
> — [GitHub README](https://github.com/mattpocock/sandcastle)

### 2.2 自定义 Provider

如果内置 Provider 不满足需求，可以自己实现：

```typescript
import { createBindMountSandboxProvider, createIsolatedSandboxProvider } from "@ai-hero/sandcastle";

// Bind-mount：性能优先，适合需要访问宿主机资源的场景
const myProvider = createBindMountSandboxProvider({
  imageName: "my-custom-agent-image",
  // ...
});

// Isolated：安全优先，完全隔离的 MicroVM
const secureProvider = createIsolatedSandboxProvider({
  // ...
});
```

### 2.3 Worktree：Git 分支隔离的关键

Sandcastle 使用 Git Worktree 而非普通 Git Clone 来实现分支隔离。这意味着：

- Agent 在独立的文件系统快照上工作，不会意外修改主分支
- 可以同时在多个分支上运行不同的 Agent
- 工作完成后，通过 `createMergeRequest()` 将变更合并回主干

> 笔者认为：Worktree 的设计是整个系统的精髓——它解决了「让 Agent 自由写代码」和「不让 Agent 污染主干」之间的根本矛盾。传统的方案是在 CI pipeline 中手动创建分支，流程重、反馈慢；Sandcastle 让这个过程自动化，而且可以本地和云端统一使用。

---

## 3. 典型使用场景

### 3.1 CI/CD 中的 AFK Agent

> "Great for parallelizing multiple AFK agents, creating review pipelines, or even just orchestrating your own agents."
> — [GitHub README](https://github.com/mattpocock/sandcastle)

```typescript
import { run, claudeCode } from "@ai-hero/sandcastle";
import { docker } from "@ai-hero/sandcastle/sandboxes/docker";

const result = await run({
  agent: claudeCode("claude-opus-4-6"),
  sandbox: docker(),
  promptFile: ".sandcastle/prompt.md",
});

console.log(result.commits); // [{ sha: "..." }, ...]
```

Agent 可以在后台运行（"AFK" = Away From Keyboard），不占用本地终端，系统自动完成分支创建→Agent 执行→提交→合并的完整流程。

### 3.2 跨仓库的并行 Agent 执行

通过 `cwd` 参数指定不同仓库：

```typescript
await run({
  agent: claudeCode("claude-opus-4-6"),
  sandbox: docker(),
  cwd: "../other-repo",  // 指向另一个仓库
  branchStrategy: { type: "branch", branch: "agent/fix-42" },
  prompt: "Fix issue #42 in this repo",
});
```

多个 Agent 可以同时在不同的仓库/分支上工作，互不干扰。

### 3.3 生命周期钩子

Sandcastle 提供了细粒度的生命周期钩子：

```typescript
hooks: {
  host: {
    onWorktreeReady: [{ command: "cp .env.example .env" }],
    onSandboxReady: [{ command: "echo setup done" }],
  },
  sandbox: {
    onSandboxReady: [{ command: "npm install" }],
  },
},
```

> 典型场景：在 Agent 运行前，先在沙箱里安装依赖（`npm install`）、复制环境变量文件（`cp .env.example .env`），确保 Agent 进入时环境已就绪。

---

## 4. 技术规格

| 维度 | 规格 |
|------|------|
| **语言** | TypeScript（需要 Node.js 环境）|
| **npm 包** | `@ai-hero/sandcastle` |
| **依赖要求** | Git + Docker/Podman/Vercel 其一 |
| **Agent 支持** | Claude Code（通过 `claudeCode()` 工厂函数）|
| **模型选择** | 支持传入模型字符串（如 `"claude-opus-4-6"`）+ effort level |
| **npm 安装量** | `npm install --save-dev @ai-hero/sandcastle` |
| **开源协议** | MIT |

---

## 5. 与 Cursor SDK 的互补分析

Cursor SDK 和 Sandcastle 解决的是「如何把 Agent 变成可编程基础设施」这个共同问题，但路径不同：

| 维度 | Cursor SDK | Sandcastle |
|------|-----------|------------|
| **底层 Runtime** | Cursor 自有 Runtime（Cloud VM 或本地）| Claude Code（你提供 API key）|
| **隔离方式** | 云端 Dedicated VM / 本地 | Docker / Podman / Vercel 容器 |
| **Git 分支管理** | 不涉及（Cloud Agent 直接对 repo 操作）| 原生 Worktree 分支策略 |
| **多 Agent 并行** | SDK 本身支持，但需要自己处理并发 | 内置 `wt.run()` 的并行 Worktree 模式 |
| **适用语言** | TypeScript | TypeScript |
| **目标用户** | 想用 Cursor 基础设施的团队 | 想在自己的基础设施上跑 Claude Code 的团队 |

> 笔者的判断：两者是互补关系，不是竞争关系。如果你的团队已经在用 Cursor IDE 并想扩展其 Agent 能力，Cursor SDK 是最短路径。如果你想在 Claude Code 基础上构建自己的 Agent 平台（需要隔离、分支管理、并行执行），Sandcastle 是更好的选择。

---

## 6. 快速起步

```bash
# 1. 安装
npm install --save-dev @ai-hero/sandcastle

# 2. 初始化项目结构
npx sandcastle init

# 3. 配置环境变量
cp .sandcastle/.env.example .sandcastle/.env
# 编辑 .env，填入 ANTHROPIC_API_KEY

# 4. 编写 prompt 文件
echo "Fix the authentication bug in this repository" > .sandcastle/prompt.md

# 5. 运行
npx tsx .sandcastle/main.ts
```

---

## 引用来源

- [GitHub: mattpocock/sandcastle](https://github.com/mattpocock/sandcastle)
- [GitHub: cursor/cookbook](https://github.com/cursor/cookbook)（关联：Cursor SDK 的 DAG Task Runner 示例展示了类似的多 Agent 并行模式）