# Flue：The Agent Harness Framework

## 核心问题：如何构建一个与 Claude Code 行为一致、但完全可编程且可部署到任何环境的 Agent Harness？

## 为什么存在（项目背景）

Astro 团队（知名 Web 框架厂商）在 2025-2026 年间观察到 AI Agent 在生产环境中的核心矛盾：**Claude Code 拥有出色的交互体验，但其设计隐含了「需要人类在终端前操作」的前提**。当工程师想把同样的 Agent 能力嵌入到自动化流水线、CICD、API 服务时，现有的框架要么过于复杂、要么过于玩具化，无法提供 Claude Code 级别的可靠性。

> 官方原文："Flue is a TypeScript framework for building the next generation of agents, designed around a built-in agent harness. It's like Claude Code, but 100% headless and programmable. There's no baked-in assumption like requiring a human operator to function."

Flue 的目标是填补 Claude Code 的「交互式终端体验」与生产环境部署之间的架构鸿沟——不是重新发明 Agent 能力，而是将 Claude Code 的行为模式提取为可复用的 Harness 运行时。

## 核心能力与技术架构

### 关键特性 1：Virtual Sandbox（虚拟沙箱）

Flue 默认使用 `just-bash` 作为虚拟沙箱，而非为每个 Agent 启动完整容器。这个设计直接对应 Anthropic 提出的 Brain-Hands 解耦中的 **按需扩展** 原则：

> "Unless you opt-in to initializing a full container sandbox, Flue will default to a virtual sandbox for every agent, powered by [just-bash](https://github.com/vercel-labs/just-bash). A virtual sandbox is going to be dramatically faster, cheaper, and more scalable than running a full container for every agent, which makes it perfect for building high-traffic/high-scale agents."

虚拟沙箱的特点：
- **无容器开销**：启动时间从秒级降至毫秒级
- **可扩展性**：高频 Agent 调用场景（API Webhook）不再需要排队等容器
- **Cloudflare R2 集成**：文件系统和知识库直接挂载为 Agent 的虚拟文件系统

### 关键特性 2：三层解耦架构（SDK / CLI / Connectors）

Flue 将框架拆分为三个独立包，每个包有明确的职责边界：

| 包 | 职责 |
|----|------|
| `@flue/sdk` | Core SDK：Build System、Sessions、Tools |
| `@flue/cli` | CLI：构建和运行 Agent |
| `@flue/connectors` | 第三方连接器：Sandbox（Daytona 等）|

这个分层直接对应了 Agent 系统的 **Harness-Sandbox 解耦**：SDK 是 Brain 层，Connectors 是 Hands 层。

### 关键特性 3：Skills 和 AGENTS.md 作为一等公民

Flue 将「逻辑外置」的思想发挥到极致——大多数业务逻辑存在于 Markdown 文件中，而非 TypeScript 代码：

```typescript
// Agent 发现 skills 和 context 的方式
// 与 Claude Code 完全一致：从当前工作目录向上查找 AGENTS.md
// Skills 定义在 .agents/skills/ 目录下
const result = await session.skill('triage', {
  args: { issueNumber: payload.issueNumber },
  commands: [gh, npm], // 命令级权限控制
  result: v.object({ ... }) // Schema 验证的返回类型
});
```

> 官方原文："Most of the 'logic' lives in Markdown: skills, context, and AGENTS.md."

这个设计与 Claude Code 的 skill 机制完全对齐，使 Claude Code 的 prompt 资产可以直接迁移到 Flue 环境。

### 关键特性 4：Sandbox-as-a-Tool 的按需连接

Flue 的 `defineCommand()` 设计允许在调用级别授予/限制命令权限，而非全局暴露：

```typescript
// 敏感命令（GH_TOKEN）仅在特定 skill 调用中可见
// Agent 永远不会在自己的上下文中看到 token
const gh = defineCommand('gh', { env: { GH_TOKEN: process.env.GH_TOKEN } });

await session.skill('triage', {
  commands: [gh, npm],  // 仅这个 skill 有 gh 权限
});
```

这与 Anthropic 的 Vault 模式异曲同工：**最小权限暴露**，而非全量授权。

### 关键特性 5：多部署目标支持

> "Write once, build, and deploy your agents anywhere (Node.js, Cloudflare, GitHub Actions, GitLab CI/CD, etc.)"

这是 Harness 运行时无关性的体现——相同的 Agent 代码，可以部署到：
- Node.js HTTP Server
- Cloudflare Workers（边缘计算）
- CI/CD Pipeline（无服务触发）
- GitHub/GitLab Actions

### 关键特性 6：Task（子 Agent）的并行委托

```typescript
const research = await session.task('Research the auth flow and summarize the key files.', {
  cwd: '/workspace/project',
  role: 'researcher',
});

const answer = await session.prompt(
  `Use this research to draft the implementation plan:\n\n${research.text}`,
);
```

`session.task()` 在同一个 Sandbox 内启动一个独立的子 Agent，有自己的消息历史和工作目录。这是 **Many Hands, One Brain** 的具体实现。

## 与同类项目对比

| 维度 | Flue | Claude Code | AgentScope Runtime | OpenAI Codex CLI |
|------|------|------------|-------------------|-----------------|
| **语言** | TypeScript | Node.js | Python | Rust |
| **沙箱模型** | Virtual (just-bash) + Daytona 容器 | 完整容器 | Docker/gVisor/BoxLite | 原生沙箱（实验性）|
| **部署目标** | Node.js / Cloudflare / CI | 本地CLI | K8s / Serverless | 本地CLI + 云端 |
| **权限模型** | defineCommand (per-call) | 交互确认 | 沙箱隔离 | 沙箱边界 |
| **Skill 系统** | Markdown 文件（Claude Code 兼容）| Markdown 文件 | Python Toolkit | 内置工具 |
| **多 Agent** | Task API（子 Agent）| - | 多 Agent 协作 | 多 Provider |

## 适用场景与局限

### 适用场景

- **高并发 API Agent**：Webhook 驱动的 Agent 服务，虚拟沙箱提供毫秒级启动
- **CI/CD 自动化**：GitHub Issue Triage、Bug 复现、自动修复 PR
- **多租户 Agent 服务**：每个租户独立 Session，Cloudflare Durable Objects 持久化
- **Claude Code 能力迁移**：现有 AGENTS.md 和 skills 无缝复用

### 局限

- **虚拟沙箱的能力边界**：仅支持 Bash 操作，不支持完整的 Linux 环境（需要 Daytona 容器）
- **TypeScript-first**：非 JS/TS 项目集成成本较高
- **生态成熟度**：v0.0.x 阶段，API 尚未稳定，生产环境采用需谨慎
- **多 Agent 协作**：目前只有 Task API（父子关系），没有 A2A 协议级别的多 Brain 协调

## 一句话推荐

**Flue 是 Brain-Hands 解耦架构的 TypeScript 实现**：如果你需要一个像 Claude Code 一样可靠、但能部署在任何环境（而非必须有人操作终端）的 Agent Harness，Flue 提供了目前最干净的抽象层——Virtual Sandbox 的按需扩展、Markdown 逻辑外置、per-call 权限控制，三者共同构成了生产级 Agent 运行的最小化基础设施。

---

## 防重索引记录

- GitHub URL: https://github.com/withastro/flue
- 推荐日期: 2026-05-02
- 推荐者: ArchBot
- 关联文章: `brain-hands-decoupled-agent-architecture-2026.md`（orchestration/）
- 主题关联: Agent Harness + Brain-Hands 解耦 + 虚拟沙箱 + 按需扩展