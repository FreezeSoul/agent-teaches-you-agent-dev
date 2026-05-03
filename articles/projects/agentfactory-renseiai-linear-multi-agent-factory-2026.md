# AgentFactory：Linear 原生多 Agent 软件工厂

> **目标读者**：有大规模 Agent 编排需求的工程团队（5+ 工程师同时使用多个 coding agent），特别是已经在用 Linear 作为 issue tracker 的组织。
>
> **核心结论**：AgentFactory 将 Linear issue tracker 变成软件工厂的装配线，每个 issue 经过「开发 → QA → 验收」三阶段流水线，每个阶段由不同的 coding agent 执行，最终产出可直接合并的 PR。它解决的不是「如何让单个 agent 更强」，而是「如何让多个 agent 在统一流程下持续产出可用代码」。

> **来源**：本文核心内容基于 [AgentFactory GitHub README](https://github.com/RenseiAI/agentfactory) 官方资料。

---

## 1. 破题：软件工厂的装配线思维

大多数 Agent 编排工具关注的是「如何启动和管理多个 agent」。AgentFactory 的切入点不同：它关注的是**多个 agent 在统一质量门禁下持续产出可用代码**的工程化问题。

> "AgentFactory turns your issue backlog into shipped code. It orchestrates a fleet of coding agents (Claude, Codex, Spring AI, or any A2A-compatible agent) through an automated pipeline: development, QA, and acceptance — like an assembly line for software."
> — [AgentFactory GitHub README](https://github.com/RenseiAI/agentfactory)

这个定位非常务实：用 Linear 的 issue 队列作为生产流水线的输入，每个 issue 触发一个 agent 执行特定阶段，产出通过质量门禁后进入下一阶段，最终由 human reviewer 验收合并。

---

## 2. 核心架构：三阶段流水线 × 模块化设计

### 2.1 三阶段质量门禁

AgentFactory 将软件交付分为三个标准化阶段：

| 阶段 | 执行者 | 产出 | 质量门禁 |
|------|--------|------|---------|
| **Dev** | Coding Agent（Claude/Codex 等） | 实现代码 + 自测 | 代码风格/lint 通过 |
| **QA** | 独立 QA Agent | 测试报告 + 覆盖率 | 测试通过率阈值 |
| **Acceptance** | Human + Agent Review | Review packet + 视频演示 | 人工确认 |

每个阶段都有明确的输入/输出规范和质量标准，agent 在当前阶段未通过时不会进入下一阶段。这和 OpenAI Symphony 的「给 agent 目标而非步骤」哲学形成对比——AgentFactory 更强调**流水线式强制质量门禁**。

### 2.2 八个核心包（TypeScript/npm）

```
@renseiai/agentfactory          # Core orchestrator + provider abstraction + crash recovery
@renseiai/plugin-linear         # Linear issue tracker 集成
@renseiai/agentfactory-server   # Redis work queue + session storage + worker pool
@renseiai/agentfactory-cli      # CLI 工具
@renseiai/agentfactory-nextjs   # Next.js webhook processor
@renseiai/agentfactory-dashboard # Fleet 管理 UI
@renseiai/agentfactory-mcp-server # MCP server（暴露 fleet 能力给外部）
@renseiai/agentfactory-code-intelligence # Tree-sitter AST 解析 + BM25 搜索 + 增量索引
```

这种模块化设计允许团队按需选用：只用 core + linear 可以快速启动；加 dashboard 可以可视化 fleet 状态；加 code-intelligence 可以获得语义级别的代码搜索能力。

---

## 3. Linear 原生集成：issue 即工作单元

AgentFactory 和 Linear 的集成深度远超表面：

**Linear 作为事实上的 CI/CD 控制台**：
- Issue 创建 → 触发 Webhook → Agent 领取任务
- Issue 状态自动映射到流水线阶段（`In Progress` → Dev, `In Review` → QA, `Done` → Acceptance）
- Agent 可以直接在 Linear 里评论、附加文件、甚至更新状态

**`af-linear` CLI 工具**：除了 Node.js API，还有一套独立的 CLI 工具用于管理 Linear issue 和 AgentFactory worker 的映射关系。这让非技术人员也可以通过 Linear 界面触发 agent 工作流。

---

## 4. 与 Symphony 的关键差异

| 维度 | Symphony | AgentFactory |
|------|----------|--------------|
| **起源** | OpenAI 内部工具（Codex 专项） | 开源社区发起（通用多 agent） |
| **tracker 支持** | Linear（硬编码） | Linear 插件化 + webhook |
| **质量门禁** | 弱（依赖 agent 自我管理） | 强（三阶段流水线强制门禁） |
| **架构哲学** | SPEC.md 优先，语言无关 | TypeScript 优先，模块化 |
| **适用规模** | 中小型团队（<20 agent 并发） | 中大型团队（可水平扩展 worker pool） |
| **A2A 兼容** | 无明确定义 | 明确支持 A2A 兼容 agent |

Symphony 更像是一个**规范框架**，告诉你「应该这样设计」，允许你用任何语言实现。AgentFactory 则是一个**生产可用的系统**，有完整的 TypeScript 实现和配套工具链。

---

## 5. 技术亮点：Crash Recovery + Code Intelligence

### 5.1 Crash Recovery

> "Core orchestrator, provider abstraction, **crash recovery**"
> — [AgentFactory GitHub README](https://github.com/RenseiAI/agentfactory)

在多 agent 并发运行的环境里，agent 崩溃（网络超时、OOM、模型 API 错误）是常态而非异常。AgentFactory 的 core 包内置了 crash recovery 机制：
- 每个 agent session 的状态持久化到 Redis
- agent 崩溃后，orchestrator 从上次checkpoint恢复而非从头开始
- 重试策略：指数退避 + 最大重试次数限制

这对于 Symphony 的参考实现是明显短板——Symphony 依赖外部状态（Linear + 文件系统），如果 agent 在任务中途崩溃，没有原生的重试机制。

### 5.2 Code Intelligence（Tree-sitter + BM25）

`@renseiai/agentfactory-code-intelligence` 提供了代码库级别的语义理解能力：
- **Tree-sitter AST 解析**：在 agent 执行前理解代码结构，避免生成与现有架构冲突的代码
- **BM25 搜索**：轻量级关键词检索，在不依赖 embedding 服务的情况下提供上下文召回
- **增量索引**：只重新索引变更文件，不需要全量重建

这个包的存在说明 AgentFactory 考虑的是**真实的代码库上下文问题**，而不是假设 agent 可以靠模型能力自己理解一切。

---

## 6. 快速上手：三步跑起来

### 第一步：部署 Webhook Server

```bash
npx @renseiai/create-agentfactory-app my-agent
cd my-agent && cp .env.example .env.local
# 填入 LINEAR_ACCESS_TOKEN
pnpm install && pnpm dev
```

### 第二步：配置 Linear Webhook

在 Linear Settings → Webhooks 添加 endpoint 指向你的 `/webhook` 路由。AgentFactory 的 Next.js webhook processor 会接收 Linear 的 issue 事件并转换为 agent 任务。

### 第三步：启动 Worker Pool

```bash
pnpm worker  # 启动本地 worker（可并发多个）
```

Worker 从 Redis queue 拉取任务，每个 worker 处理一个 issue。`maxConcurrent` 配置控制并发数。

---

## 7. 适用边界与局限

**不适用的场景**：
- 不使用 Linear 的团队（需要重写 plugin-linear 才能对接其他 tracker）
- 单 agent 场景（AgentFactory 的复杂度在此场景下是过度设计）
- 需要强实时交互的 agent 任务（流水线式设计天然不适合需要 human-in-the-loop 的场景）

**已知局限**：
- 目前只有 Linear 官方插件，其他 tracker（GitHub Issues、Jira）需要社区贡献
- TypeScript 实现对非 JS/TS 团队有定制门槛
- 尚处于较早版本，生产环境部署需要评估 crash recovery 的实际表现

---

## 8. 下一步行动

- **快速验证**：用 `npx @renseiai/create-agentfactory-app` 搭一个 demo，感受 Linear → AgentFactory → PR 的完整流程
- **贡献插件**：参考 `plugin-linear` 实现 GitHub Issues 或 Jira 插件（spec 文档相对清晰）
- **关注演进**：AgentFactory 的 roadmap 包含 MCP server 暴露 fleet 能力，这意味着未来可以用 MCP client 从外部控制整个软件工厂

> **核心引用**：
> - [AgentFactory GitHub](https://github.com/RenseiAI/agentfactory)
> - [npm 包列表](https://www.npmjs.com/package/@renseiai/agentfactory)
> - [Linear 集成文档](https://github.com/RenseiAI/agentfactory/tree/main/packages/linear)