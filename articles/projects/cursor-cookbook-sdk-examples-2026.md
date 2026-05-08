# cursor/cookbook: Cursor SDK 官方示例库——将生产级 Agent 运行时装进口袋

## 定位

> **谁该关注**：想在 Cursor 生态外调用 Cursor Agent 运行时的开发者；正在构建内部 Agent 平台、需要"开箱即用的生产级 Harness"的团队；希望将 AI Agent 能力嵌入自己产品的产品工程师。

---

## 核心价值

cursor/cookbook 是 `@cursor/sdk` 的官方示例库，发布于 2026 年 4 月 27 日（距今约 11 天），截至今日已收获 **3,675 Stars、417 Forks**。这不是一个普通的"hello world"示例集合——它的每一个 Sample 都是一个**完整的生产场景**，可以直接 fork 并根据自身需求改造。

> "This repo contains small examples for building with Cursor. The Cursor SDK is the TypeScript API for running Cursor's coding agent from your own apps, scripts, and workflows."
> — [cursor/cookbook GitHub README](https://github.com/cursor/cookbook)

### Target — 目标用户

**用户画像**：有 TypeScript 经验的开发者或工程团队，正在或计划在以下场景使用 AI Coding Agent：
- CI/CD 流水线中的自动化代码审查与修复
- 内部工具中的嵌入式 AI 助手
- 产品中的 AI-driven 工作流自动化
- 快速原型验证（不需要自己搭 Harness）

**水平要求**：熟悉 Node.js / TypeScript 生态，了解 Agent 基本概念（有编程经验即可，不要求 Agent 系统背景）。

---

## 为什么值得用

### T — 具体改变

| 场景 | 之前 | 之后 |
|------|------|------|
| CI/CD 中的代码审查 | 人工 Review 或购买 ESLint/JSHound 等规则引擎 | `Agent.send()` 发起 Cloud Agent，自动审查 + PR 更新 |
| 内部工具嵌入 AI | 自己搭 Agent 运行时（沙箱/状态管理/上下文）| 几行 TypeScript 调用 Cursor Cloud Agent |
| Bug 修复流程 | 开发者手动定位 + 修复 | Cloud Agent 克隆仓库 → 定位根因 → 打开 PR（自动） |
| 新项目初始化 | 手动创建骨架代码 | 沙箱 Cloud Agent 自动 scaffold + 迭代改进 |

根据 Cursor 官方博客的描述，"多家企业在 CI/CD 流水线中直接调用 Agent 来总结变更、定位失败根因、更新 PR 修复内容"——cookbook 就是这个场景的代码级实现。

### R — 量化数据

| 指标 | 数值 |
|------|------|
| Stars | 3,675（11 天，新诞生的 repo）|
| Forks | 417 |
| 仓库创建时间 | 2026-04-27 |
| 最新推送 | 2026-05-07 |
| 覆盖 Sample 数量 | 5 个（含 Quickstart / Kanban / Coding Agent CLI / DAG Task Runner / Prototyping Tool）|

### I — 技术洞察

cookbook 的技术深度在于它展示了**Cursor Agent 运行时与外部代码的集成边界**。以 Quickstart 为例：

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

这看起来简单，但背后是：
- **会话持久化**：流式事件可以断开重连，Agent 不会因为你的 laptop 睡眠而中断
- **模型路由**：一个字段切换 `composer-2` 和 `gpt-5.5`，不用改任何集成代码
- **Cloud Agent 的完整生命周期管理**：`run.id` 可以跨进程查询结果状态

**DAG Task Runner** 是最深度的 Sample——它展示了一个完整的多 Agent 编排模式：
- 将任务分解为 JSON DAG（有向无环图）
- Fan-out 到多个本地 Subagent 并行执行
- 流式状态实时推送到 Cursor Canvas（热重载）
- 同时产出一个可复用的 Cursor Skill（`.cursor/skills/dag-task-runner`）

> "Decompose a task into a JSON DAG, fan it out across local subagents, and stream live status into a Cursor Canvas that hot-reloads on every state change."
> — [cursor/cookbook README](https://github.com/cursor/cookbook)

这是第一个我看到的、将 **Subagent 并行执行 + 可视化状态推送 + 可复用 Skill** 三者串联的完整工程示例。

### P — 证明

- **GitHub trending**：2026 年 4 月底-5 月初的 AI Agent 领域热门仓库
- **Cursor 官方维护**：`cursor/` 组织官方仓库，不是个人项目
- **真实用户采用**：Cursor 官方博客明确提到 Faire/Rippling/Notion/C3 AI 在使用 Cursor SDK
- **持续活跃**：最近一次 push 是 2026-05-07（4 天前），PR #21 添加 code-reviewer SDK example

---

## 体感式介绍

假设你在构建一个内部工具，需要 AI Coding Agent 来自动审查 PR。现在你有两条路：

**路线 A（自己搭）**：
- 搭沙箱环境（安全隔离）
- 处理 Agent 状态持久化（断开重连）
- 管理上下文窗口（不要让 Agent 上下文溢出）
- 集成代码解析工具（AST/grep/语义搜索）
- 处理 Agent → 代码库的写权限问题
- ……（你还有 3 个 sprint 的时间吗？）

**路线 B（用 Cursor SDK）**：
```typescript
const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  cloud: { repos: [{ url: repoUrl }], autoCreatePR: true },
});

const result = await (await Agent.getRun(run.id, { runtime: "cloud" })).wait();
console.log(result.git?.branches[0]?.prUrl);
```

cookbook 就是这条路线 B 的**代码级路线图**——它把 Cursor 内部使用的生产级 Harness 包装成了任何人调用几行 TypeScript 就能用的服务。

---

## 与其他方案的对比

| 方案 | 优势 | 局限 |
|------|------|------|
| **cursor/cookbook + @cursor/sdk** | Cursor 自家 Harness（持续迭代）、Cloud Agent 免运维、Composer 2 成本优化 | 依赖 Cursor 生态（不是所有场景都适合把控制权交给 Cursor）|
| **OpenAI Agents SDK** | OpenAI 官方、工具生态丰富 | 生产级功能需要额外工程投入 |
| **从头自建** | 完全可控 | 搭生产级 Harness 需要 3-6 个月（参考 Cursor 自身的迭代周期）|

cookbook 的定位是：**让你不用从头造 Cursor 轮子，但保留全部定制灵活性**。你用的是同一个运行时，但调用方式是你自己控制的。

---

## 快速上手

```bash
# 1. 安装 SDK
npm install @cursor/sdk

# 2. 获取 API Key（Cursor integrations dashboard）
# https://cursor.com/dashboard/integrations

# 3. 克隆 cookbook
git clone https://github.com/cursor/cookbook
cd cookbook

# 4. 运行 Quickstart
CURSOR_API_KEY=your_key node quickstart/index.ts
```

cookbook 的 5 个 Sample 覆盖了从"最简单的一次性调用"到"复杂多 Agent 编排"的完整谱系——无论你是验证可行性还是构建生产系统，都能在里面找到接近的参考。

---

## 关联知识

**本文是 [Cursor Agent Harness 持续改进工程](./cursor-continually-improving-agent-harness-2026.md) 的配套 Projects 推荐**：

- **Articles** 讲述 Cursor 如何通过在线实验、Keep Rate 指标和模型定制化将 Harness 打造成可衡量的工程实践
- **Projects** 展示这套工程实践的产品化结晶——`@cursor/sdk` 和它的 cookbook 示例库

两者的主题关联是：**从"实验驱动改进"到"SDK 产品化"**——前者是方法论，后者是载体。

---

## References

- GitHub: https://github.com/cursor/cookbook（3,675 ⭐, 417 forks, TypeScript, created 2026-04-27）
- Cursor SDK Docs: https://cursor.com/docs/sdk/typescript
- Cursor Blog: "Build programmatic agents with the Cursor SDK", Apr 29, 2026 — https://www.cursor.com/blog/typescript-sdk
- Cursor Engineering Blog: "Continually improving our agent harness", Apr 30, 2026 — https://www.cursor.com/blog/continually-improving-agent-harness