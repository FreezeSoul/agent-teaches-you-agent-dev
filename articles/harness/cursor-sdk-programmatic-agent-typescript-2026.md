# Cursor SDK：把 IDE 的 Agent Runtime 变成你的代码基础设施

> 本文要回答：Cursor SDK 是什么、它解决了什么问题、以及为什么它的设计哲学代表了 2026 年 Agent 基础设施的主流方向。
>
> 读完你将得到：理解 Cursor SDK 的三层抽象（Agent / Runtime / Model）、掌握 programmatic agent 的典型调用模式、并能判断「何时该用 SDK vs 自建 Harness」。

---

## 1. 背景：编程 Agent 从工具到基础设施的演变

Cursor 在 2026 年 4 月 29 日发布了 Cursor SDK，一个 TypeScript 包（`@cursor/sdk`），让开发者可以在自己的应用、脚本和工作流中调用 Cursor 的 Agent 能力。

官方原文说：

> "Coding agents are evolving from interactive tools for individual developers to programmatic infrastructure for organizations. The Cursor SDK lets you deploy agents without the overhead of building and maintaining the entire agent stack."
> — [Cursor Blog: Build programmatic agents with the Cursor SDK](https://cursor.com/blog/typescript-sdk)

这句话点出了 2026 年的核心趋势：**编程 Agent 不再只是给人用的 IDE 插件，而是变成了可以被程序驱动的后端基础设施**。这是一个根本性的角色转变。

---

## 2. 核心设计：三层抽象

Cursor SDK 的设计围绕三个核心概念展开：

### 2.1 Agent — 任务执行单位

```typescript
import { Agent } from "@cursor/sdk";

const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  local: { cwd: process.cwd() },
});

const run = await agent.send("Summarize what this repository does");

for await (const event of run.stream()) {
  console.log(event);
}
```

`Agent.create()` 创建的是一个**会话级别的执行单元**，它绑定到特定的工作目录、模型和 API key。`agent.send()` 发起任务，`run.stream()` 支持流式输出。

官方原文：

> "The agents that run in the Cursor desktop app, CLI, and web app are now accessible with a few lines of TypeScript. Run it on your machine or on Cursor's cloud against a dedicated VM, with any frontier model."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

### 2.2 Runtime — 执行环境的选择

这是 Cursor SDK 最关键的设计决策：**同一个 Agent API 可以切换不同的执行环境**：

```typescript
// 本地执行
const agentLocal = await Agent.create({
  local: { cwd: process.cwd() },
});

// 云端执行（Dedicated VM）
const agentCloud = await Agent.create({
  cloud: {
    repos: [{ url: "https://github.com/cursor/cookbook", startingRef: "main" }],
    autoCreatePR: true,
  },
});
```

官方原文说明了这种设计的目的：

> "Cloud sessions initiated from the SDK run on the same optimized runtime we use for Cloud Agents. Each agent gets its own dedicated VM with strong sandboxing, a clone of the repo, and a fully configured development environment."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

本地 vs 云端的选择意味着：快速迭代用本地，长时任务或需要隔离的执行用云端。Cursor 通过同一个 API 抽象了两种场景。

### 2.3 Model — 模型路由

SDK 支持 Cursor 支持的所有模型：

> "Route agents to the best model for the task at hand, with your desired balance of cost and capability, with a single field change."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

```typescript
// 省钱用 composer-2
model: { id: "composer-2" }

// 旗舰能力用 opus
model: { id: "claude-opus-4-6" }

// OpenAI 也可以
model: { id: "gpt-5.5" }
```

---

## 3. SDK 的 Harness 能力

Cursor SDK 继承了 Cursor IDE 的完整 Harness 体系，官方原文：

> "Agents launched through the SDK benefit from the same harness that powers Cursor across our desktop app, CLI, and web app: Intelligent context management, MCP servers, Skills, Hooks, Subagents."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

具体来说，SDK 可用的 Harness 能力包括：

| Harness 组件 | SDK 支持 | 说明 |
|-------------|---------|------|
| Context Management | ✅ | 代码库索引、语义搜索、即时 grep |
| MCP Servers | ✅ | 通过 `mcp.json` 配置或内联传递 |
| Skills | ✅ | 自动从 `.cursor/skills/` 目录加载 |
| Hooks | ✅ | `.cursor/hooks.json` 控制 Agent 循环 |
| Subagents | ✅ | 通过 `Agent` tool 生成命名子 Agent |

这意味着：**用 SDK 写的 agent，享有和 IDE 里的 Agent 一样的上下文工程能力**，而不只是「发送 prompt 获得回复」的单轮交互。

---

## 4. 典型使用场景

Cursor 官方博客中列出了几个真实案例：

> "Teams are using the Cursor SDK to ship custom agents faster. For example, programmatic agents that are kicked off directly from CI/CD to summarize changes, identify root causes for CI failures, and update PRs with fixes. Others are building custom agent platforms like internal applications that let GTM teams query product data without writing code."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

几个典型的生产场景：

### 4.1 CI/CD 驱动的质量门禁

```typescript
// CI failure 后自动调用 Agent 分析根因并更新 PR
const agent = await Agent.create({
  cloud: { repos: [{ url: repoUrl }] },
  model: { id: "composer-2" },
});

const run = await agent.send(
  `Analyze the CI failure at commit ${commitHash}. Find root cause and update the PR with a fix.`
);

const result = await (await Agent.getRun(run.id, { runtime: "cloud", agentId: run.agentId })).wait();
console.log(result.git?.branches[0]?.prUrl);
```

### 4.2 内部平台嵌入

> "Some customers are even embedding Cursor directly into customer-facing products, where end users now get an agent experience without leaving the host application."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

这是把 Agent 能力变成 SaaS 产品的模式——不需要自己训练模型，只要接入 SDK 就能给用户提供 AI 编程能力。

### 4.3 长时任务的云端保持

```typescript
// 本地机器可能休眠，但云端 Agent 继续跑
const run = await agent.send("Refactor this monolith into microservices — this will take hours");

// 可以断连，之后从任何地方恢复
const result = await (
  await Agent.getRun(run.id, { runtime: "cloud", agentId: run.agentId })
).wait();
```

官方原文：

> "Agents keep going when your laptop sleeps or network drops. You can stream the conversation and reconnect later."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

---

## 5. 订阅模式与定价

Cursor SDK 的定价采用标准 token 消耗模式，没有额外的平台费用：

> "The Cursor SDK is available to all users and is billed based on standard, token-based consumption pricing."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

这意味着：
- Local 模式：不消耗 Cursor 平台的 token（只在本地跑），但仍需要 `CURSOR_API_KEY` 做认证
- Cloud 模式：消耗 token，但获得专用 VM + 完整 sandbox + repo clone

> 笔者认为：Cloud 模式的成本结构对于企业级用例是合理的——每个 Task 一个独立 VM 的隔离级别，在传统方式下需要运维一整套 Kubernetes Pod 管理，成本远高于 token 费用。

---

## 6. 示例项目：cookbook

Cursor 提供了 `cursor/cookbook` 公共仓库作为起步参考：

> "We've added a few starter projects to a public GitHub repo that you can fork and extend for your own use cases: Quickstart, Prototyping tool, Kanban board, Coding agent CLI."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

其中最值得注意的示例是 **DAG Task Runner**：

> "Decompose a task into a JSON DAG, fan it out across local subagents, and stream live status into a Cursor Canvas that hot-reloads on every state change. Ships as both a runnable example and a copyable Cursor skill."
> — [GitHub cursor/cookbook README](https://github.com/cursor/cookbook)

这是 SDK 能力的最深度展示——多 subagent 并行执行，带实时状态可视化。

---

## 7. 技术判断：SDK vs 自建 Harness

Cursor SDK 的发布让 Agent 开发多了一个选择：**用 SDK 还是自己搭 harness**？

| 维度 | Cursor SDK | 自建 Harness |
|------|-----------|-------------|
| 开发成本 | 极低（几行代码启动）| 高（需要理解 agent loop、context 管理、MCP 集成）|
| 定制化 | 受限于 Cursor Runtime 的能力边界 | 完全自由 |
| 运行成本 | Token 消耗（云端）+ 本地算力（本地）| 基础设施成本（VM/容器）|
| 适用场景 | 非核心业务、 rapid prototyping、企业内部工具 | 核心业务、需要差异化竞争、有安全合规要求 |
| 数据控制 | 云端执行意味着数据经过 Cursor 服务器 | 可以完全私有化 |

> 笔者认为：Cursor SDK 适合的场景是「不需要 Agent 作为竞争核心」的用例——比如内部工具、CI/CD 自动化、平台功能增强。在这个层次，自建 harness 的成本远超收益。但如果你在做一个需要差异化 Agent 能力的产品（比如竞品 Cursor 的 IDE 产品），SDK 的封闭性会成为限制。

---

## 8. 与 OpenAI Agents SDK 的横向对比

Cursor SDK 发布的时间点（2026 年 4 月）正好在 OpenAI Agents SDK 已经开源一段时间之后。两者的设计哲学有显著差异：

| 维度 | Cursor SDK | OpenAI Agents SDK |
|------|-----------|-------------------|
| 沙箱 | 专用 VM（Cloud）+ 本地执行 | 内置 Sandbox 抽象，支持多 provider |
| 生态 | 强依赖 Cursor 自有生态（Skills/Hooks/MCP）| 更开放，跨模型 |
| 多 Agent | 通过 subagent tool 支持 | 原生 handoffs 机制 |
| 语言 | TypeScript | Python |

> 笔者的判断：Cursor SDK 的价值在于「能把 Cursor 积累的工程能力（Context 管理、Skill 系统、Hook 体系）」快速变现为企业级 Agent 基础设施。如果你的团队已经在使用 Cursor IDE，SDK 是最低迁移成本的选项。但如果你需要跨 IDE 的 Agent 编排能力，OpenAI Agents SDK 的 Python 生态和跨模型支持更占优势。

---

## 9. 下一步

Cursor SDK 还在快速迭代中：

> "We are continuing to invest in the Cursor SDK, with a focus on making it even easier for teams to build programmatic agents across more languages, workflows, and deployment patterns."
> — [Cursor Blog](https://cursor.com/blog/typescript-sdk)

已知方向：更多语言支持（目前只有 TypeScript）、更多部署模式。

如果你想快速上手：

```bash
npm install @cursor/sdk
# 然后用 Cursor 的 /sdk skill 获取内置指导
```

---

## 引用来源

- [Cursor Blog: Build programmatic agents with the Cursor SDK](https://cursor.com/blog/typescript-sdk)
- [GitHub: cursor/cookbook](https://github.com/cursor/cookbook)
- [Cursor Changelog: SDK Release](https://cursor.com/changelog/sdk-release)
- [Cursor Docs: SDK TypeScript](https://cursor.com/docs/sdk/typescript)