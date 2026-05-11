# skelm：TypeScript 原生的安全 Agent 工作流框架

> **Target**：有 TypeScript 开发经验、正在构建生产级 Agent 系统的工程师；或者对「如何让 Agent 工作流既有灵活性又有安全边界」有需求的架构师。
>
> **Result**：用 TypeScript 原生的方式构建 Agent 工作流，默认拒绝所有未声明的权限（工具/MCP/网络/文件系统），实现真正的最小权限原则。
>
> **Insight**：skelm 的核心设计决策是把「安全」从事后添加的防护层变为工作流定义的内置约束——每一个 agent() 调用必须声明自己可以使用什么，未声明的一律拒绝。
>
> **Proof**：GitHub 17 Stars，2026-05-03 创建，TypeScript/Node.js，NPM 包可用（npm install skelm），支持 Opencode/Claude Code/Copilot/Gemini 多后端。

---

## P - Positioning（定位破题）

当前 Agent 框架的问题：大多数 Agent 框架假设「Agent 默认可以做任何事」，安全边界是事后添加的。这意味着要么安全措施过于宽松（Agent 可以访问不该访问的资源），要么安全措施过于严格（限制了 Agent 的实际能力）。

**skelm 的核心洞察**：安全不应该是加上去的护栏，而应该是工作流定义的内在约束。当你用 TypeScript 定义一个 agent 步骤时，同时定义它的权限边界——这不是额外的安全配置，而是工作流声明的一部分。

> "skelm is a TypeScript framework for authoring, running, and operating workflows — typed orchestrations that mix deterministic code, LLM inference, and full agent loops behind a single, secure, default-deny execution model."
> — [GitHub: scottgl9/skelm](https://github.com/scottgl9/skelm)

---

## S - Sensation（体验式介绍）

假设你正在构建一个自动化代码审查 Agent 工作流：

```
步骤 1：code() - 拉取 PR 变更
步骤 2：agent() - 让 Agent 分析代码问题
步骤 3：code() - 将审查结果写入 Comment
```

在 skelm 里，这个工作流看起来像这样（安全声明是内置的）：

```typescript
export const reviewWorkflow = workflow({
  name: 'code-review',
  steps: [
    code({
      run: async (ctx) => {
        const pr = await ctx.github.getPR(ctx.input.prNumber);
        return { diff: pr.diff };
      },
      allowedSecrets: ['GITHUB_TOKEN'],  // 明确声明需要的 secret
    }),
    agent({
      system: 'You are a security-focused code reviewer.',
      allowedTools: ['Read', 'Grep', 'Comment'],  // 只允许这些工具
      allowedMCP: ['github'],  // 只允许 GitHub MCP
      allowedNetwork: ['api.github.com'],  // 只允许访问 GitHub API
      allowedFilesystem: ['/tmp/review-workspace'],  // 只允许这个目录
    }),
    code({
      run: async (ctx) => {
        await ctx.github.postComment(ctx.input.prNumber, ctx.state.review);
      },
      allowedSecrets: ['GITHUB_TOKEN'],
    }),
  ],
});
```

关键是：任何一个步骤尝试使用未声明的权限，会在运行时被拒绝，而不是事后才发现安全问题。

---

## E - Evidence（拆解验证）

### 技术深度：默认拒绝的安全模型

skelm 的安全模型基于三个核心机制：

**1. 声明式权限**

每个 step（code/llm/agent）必须声明它需要的权限：
- `allowedSecrets`：可以读取的 secret 名称
- `allowedTools`：Agent 可以调用的工具列表
- `allowedMCP`：允许连接的 MCP 服务器
- `allowedNetwork`：允许访问的网络主机
- `allowedFilesystem`：允许访问的文件系统路径（每个 agent 有自己的 workspace root）

> "Every agent step declares the tools, MCP servers, network hosts, and filesystem roots it may use. Anything undeclared is denied at step start."
> — [GitHub: scottgl9/skelm](https://github.com/scottgl9/skelm)

**2. 嵌入式 CONNECT 代理**

skelm 的 gateway 内置了一个 CONNECT 代理（默认端口 14739）。Agent 子进程的 HTTP_PROXY/HTTPS_PROXY 自动指向这个代理，所有出站连接在离开机器之前被代理拦截和检查：

> "Real network egress enforcement. The gateway runs an embedded CONNECT proxy (default port 14739). Agent subprocesses receive HTTP_PROXY/HTTPS_PROXY automatically — outbound connections to undeclared hosts are blocked at the proxy before they leave the machine."
> — [GitHub: scottgl9/skelm](https://github.com/scottgl9/skelm)

**3. Per-agent 工作空间**

每个 agent 步骤获得自己的文件系统 root——可以是持久化的或临时性的，与其他步骤隔离：

> "Per-agent workspaces. Each agent step gets its own filesystem root — persistent or ephemeral — locked against cross-step corruption."
> — [GitHub: scottgl9/skelm](https://github.com/scottgl9/skelm)

### 架构设计：TypeScript 原生的工作流定义

skelm 选择 TypeScript 而非 JSON/YAML DSL，意味着：
- 工作流是真正的代码：可以 refactor/type-check/test/version
- 控制流是原生的：parallel/forEach/branch/loop/wait/invoke 都是 TypeScript 的控制结构，不是配置
- 类型安全：步骤之间的数据传递是类型化的

```typescript
// 嵌套 pipeline 是原生支持的功能，不是 add-on
const pipeline = pipeline({
  steps: [
    code({ run: async () => { /* ... */ } }),
    parallel([  // 并行执行多个步骤
      agent({ ... }),
      agent({ ... }),
    ]),
    branch([  // 条件分支
      { when: (ctx) => ctx.result.needsMoreReview, steps: [...] },
      { when: () => true, steps: [...] },  // 默认分支
    ]),
  ],
});
```

### 多后端支持

skelm 支持多种 Agent 后端，通过统一的 provider SPI：

> "Multi-backend agents. Opencode, ACP (Copilot, Claude Code, Gemini), OpenAI, Anthropic, Pi — plus a provider SPI for custom backends."
> — [GitHub: scottgl9/skelm](https://github.com/scottgl9/skelm)

这意味着你可以用同一个工作流定义，在不同后端之间切换——Claude Code 用于复杂推理，Gemini 用于快速任务。

### 社区健康度

- 当前状态：早期开发（Status: early development）
- API 在 v1 之前不稳定
- 鼓励通过 issue 反馈

这是一个典型的新兴项目——功能完整但生态还在建设期。适合愿意深入参与并影响项目方向的技术团队。

---

## T - Threshold（行动引导）

### 快速上手

```bash
# 1. 安装 CLI
npm install -g skelm

# 2. 初始化项目
skelm init my-agent-workflow && cd my-agent-workflow && npm install

# 3. 运行第一个 workflow
skelm run workflows/hello.workflow.ts --input '{"name":"world"}'
```

### 与 Cursor SDK 的对比

| 维度 | skelm | Cursor SDK |
|------|-------|------------|
| **定位** | 工作流框架（orchestration） | Agent 运行时 SDK |
| **安全模型** | 内置 default-deny | 基于云端隔离 |
| **语言** | TypeScript 原生 | TypeScript/Node.js |
| **后端** | 多后端（Opencode/Claude/Gemini） | Cursor 云端 |
| **适用场景** | 企业内部安全合规场景 | 快速接入 Cursor 云 Agent |

### 贡献入口

skelm 是早期项目，API 不稳定但这也是贡献的最佳时机：
- 功能 PR：实现新的 provider 或 step 类型
- 安全审计：发现 default-deny 模型的潜在绕过
- 文档：补充各后端的接入指南

---

## 主题关联

本文与 **Cursor Agent Harness 持续改进工程：测量驱动的 Agent 质量优化**（deep-dives/）形成完整的「质量 + 安全」双视角：

- **Cursor 文章**：如何测量 Agent 质量（Keep Rate + 语义评分），让数据驱动改进
- **skelm**：如何在工作流层建立安全边界，让默认拒绝成为架构约束

两者共同指向 Agent 工程的核心挑战：当 Agent 能力越来越强时，如何让它在正确的边界内运行——既有足够的自主性完成复杂任务，又不会超出安全边界。

---

*推荐指数：★★★☆☆（TypeScript 原生安全 Agent 工作流，适合安全敏感的企业场景，但早期项目需要谨慎评估稳定性）*