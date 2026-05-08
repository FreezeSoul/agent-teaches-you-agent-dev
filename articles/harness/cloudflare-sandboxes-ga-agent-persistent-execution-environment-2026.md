# Cloudflare Sandboxes GA：Agent 持久化执行环境的企业级解决方案

## 核心论点

> 本文要证明：Cloudflare Sandboxes 通过「持久化隔离计算机」的概念，解决了 AI Agent 从原型到生产的关键缺口——代码执行状态的连续性和安全凭证管理。与 OpenAI Agents SDK 的多提供商沙箱相比，Cloudflare 的差异化在于 **持久化 + 零信任出站代理 + 快照快速恢复** 三层能力的深度整合，这使得它成为企业级 Agent 部署的基础设施选项。

---

## 一、问题：Agent 需要「真正的计算机」，而不是函数

传统的无服务器函数（Serverless Function）模型是为 API 请求设计的：一个函数接收输入、运行、返回输出，状态通常是无状态的。这种模型对于处理用户请求很有效，但对于需要**持续性状态、执行长时间任务、保留工作上下文**的 AI Agent 而言，存在根本性的错配。

Cloudflare 早在八年前就推出了 Workers，但当时的目标用户是 API 和微服务。AI Agent 的出现让这个问题变得更尖锐：

> "If even a fraction of the world's knowledge workers each run a few agents in parallel, you need compute capacity for tens of millions of simultaneous sessions. The one-app-serves-many-users model the cloud was built on doesn't work for that."
> — [Cloudflare Agents Week 2026 Review](https://blog.cloudflare.com/agents-week-in-review/)

Cloudflare Sandboxes 的核心设计目标是为每个 Agent session 提供**一台持久化的隔离计算机**——不是容器，不是函数，而是一台有 shell、文件系统、后台进程的真实计算环境，按需启动、状态持久、自动休眠。

---

## 二、核心能力解析

### 2.1 持久化与按需启动

传统容器方案的一个核心问题是：Agent 工作在长时间任务中，关闭后再次打开需要重新初始化（clone 仓库、npm install、配置环境）。Sandboxes 通过**快照（Snapshot）机制**解决这一问题：

> "A snapshot preserves a container's full disk state, OS config, installed dependencies, modified files, data files and more. Then it lets you quickly restore it later."
> — [Cloudflare Sandboxes GA](https://blog.cloudflare.com/sandbox-ga/)

用户可以通过配置自动快照：

```javascript
class AgentDevEnvironment extends Sandbox {
  sleepAfter = "5m";
  persistAcrossSessions = {type: "disk"};
}
```

这解决了 Burstiness（突发性）和 Quick state restoration（快速恢复）两个核心问题：Sandbox 空闲时自动休眠（不占用计算资源），唤醒时从快照快速恢复（而不是从头启动）。

### 2.2 零信任出站代理：安全凭证注入

企业级 Agent 的一个关键挑战是：**Agent 需要访问私有服务，但不能拥有原始凭证**。传统方案是将凭证直接注入环境变量，但这意味着如果 Agent 被攻破，攻击者可以获取所有凭证。

Cloudflare Sandboxes 提出了**网络层注入**的方案：

```javascript
class OpenCodeInABox extends Sandbox {
  static outboundByHost = {
    "my-internal-vcs.dev": (request, env, ctx) => {
      const headersWithAuth = new Headers(request.headers);
      headersWithAuth.set("x-auth-token", env.SECRET);
      return fetch(request, { headers: headersWithAuth });
    }
  }
}
```

Agent 代码永远看不到 `SECRET`，所有认证在出站代理层完成。这与 Cursor Self-Hosted Cloud Agents 的设计哲学高度一致——**代码不出网络，但工作结果可以返回**。两个系统都把「代码不见凭证」作为核心安全约束。

### 2.3 持久化代码解释器（Code Interpreter）

Sandboxes 还提供了比 PTY 更高层的抽象——持久化代码上下文：

```javascript
const ctx = await sandbox.createCodeContext({ language: "python" });
await sandbox.runCode(`import pandas as pd`, { context: ctx });
// 第二次调用时，pd 已经导入，状态保留
const result = await sandbox.runCode(`df.groupby('region')['margin'].mean()`);
```

这与 Jupyter Notebook 的语义相同——状态在多次调用间保持。对于数据分析和探索性工作流，这种持久化上下文比每次重新初始化要高效得多。

### 2.4 PTY 支持与实时终端

Sandboxes 支持通过 WebSocket 提供完整的 PTY 会话，兼容 xterm.js：

```javascript
return sandbox.terminal(request, { cols: 80, rows: 24 });
```

这让 Agent 能够：
- 实时流式输出命令执行结果
- 支持 Ctrl+C 中断长时间运行的命令
- 断线重连后回放历史输出

Agent 获得的不是「命令→输出」的事后查询，而是与真实终端相同的交互体验。

### 2.5 文件系统监听与自动化反馈

`sandbox.watch()` 返回基于 Linux inotify 的 SSE 流，支持实时响应文件变更：

```javascript
const stream = await sandbox.watch('/workspace/src', { recursive: true, include: ['*.ts', '*.tsx'] });
for await (const event of parseSSEStream(stream)) {
  if (event.type === 'modify') {
    await sandbox.exec('npx tsc --noEmit', { cwd: '/workspace' });
  }
}
```

这是一个典型的「让 Agent 接入人类开发反馈循环」的机制——Save a file → rerun the build → see the result。这是现代 IDE 的核心体验，Sandboxes 将其延伸到 Agent 执行层。

---

## 三、架构定位：与 OpenAI Agents SDK 的对比

Cloudflare Sandboxes 与 OpenAI Agents SDK 都提供沙箱执行能力，但设计哲学不同：

| 维度 | Cloudflare Sandboxes | OpenAI Agents SDK |
|------|---------------------|-------------------|
| **执行模型** | 持久化计算机（有 shell/文件系统/后台进程） | 轻量级隔离环境 + Manifest 抽象 |
| **状态持久化** | 快照恢复，磁盘级保存 | Sandbox 生命周期内保持，跨请求有限支持 |
| **凭证安全** | 网络层注入，Agent 永远不接触原始凭证 | 凭证由开发者管理，Sandbox 隔离 |
| **网络控制** | Outbound-only Workers 零信任代理 | 多提供商（Blaxel/Cloudflare/Daytona/E2B/Modal/Vercel） |
| **定价模型** | Active CPU Pricing（按实际使用付费） | 由提供商决定 |
| **生态系统** | Cloudflare 平台（KV/Durable Objects/Mesh） | OpenAI 官方 + 14+ 提供商集成 |
| **适用场景** | 长时间复杂任务、需要完整开发环境 | 快速任务、跨提供商切换 |

Cloudflare Sandboxes 的差异化在于**深度整合 Cloudflare 平台能力**（KV 存储、Durable Objects 数据库、AI Gateway 路由、Mesh 零信任网络）。如果你的 Agent 基础设施已经构建在 Cloudflare 上，Sandboxes 提供的是无缝集成。如果你是多云或厂商中立方案，OpenAI Agents SDK 的抽象层更合适。

---

## 四、与 Cursor Self-Hosted 的架构关联

在 [Cursor Self-Hosted Cloud Agents](./cursor-self-hosted-cloud-agents-kubernetes-enterprise-deployment-2026.md) 中我们分析了「代码不出企业边界」的 Outbound-only Worker 架构。Cloudflare Sandboxes 提供了另一种企业级隔离方案，但场景不同：

**Cursor Self-Hosted**：解决企业**不信任云端 Agent 处理代码**的问题，通过 Outbound-only Worker 让企业基础设施主动建立出站 HTTPS 连接，不需要开放入站端口。

**Cloudflare Sandboxes**：解决企业**需要给 Agent 一个安全的长时间工作环境**的问题，核心能力是持久化 + 凭证不见 + 快照恢复，适用于需要运行完整开发服务器、进行数据分析、执行长时间任务的 Agent。

两者是互补关系：一个负责「代码在哪里运行」（Self-Hosted 边界），一个负责「运行的计算机有什么能力」（Sandbox 执行环境）。

---

## 五、生产案例：Figma Make

Cloudflare Sandboxes 的生产级用户是 Figma Make：

> "Figma Make is built to help builders and makers of all backgrounds go from idea to production, faster. To deliver on that goal, we needed an infrastructure solution that could provide reliable, highly-scalable sandboxes where we could run untrusted agent- and user-authored code. Cloudflare Containers is that solution."
> — Alex Mullans, AI and Developer Platforms at Figma

这个案例的关键信息是**「运行不受信任的 Agent 和用户代码」**——Figma Make 需要执行用户通过 AI Agent 或直接提交的代码片段，这在传统模型中是一个高风险操作。Cloudflare Sandboxes 通过隔离环境确保即使恶意代码也无法突破沙箱边界。

---

## 六、技术规格与限制

根据 Cloudflare 官方文档，Sandboxes 提供以下核心能力：

- **持久化**：每个 Sandbox 实例有独立文件系统，关闭后可通过 ID 恢复
- **快照**：自动休眠时保存完整状态，支持快速恢复
- **Background processes**：支持在 Sandbox 中启动开发服务器并暴露预览 URL
- **Port exposure**：将内部端口映射为公开 URL，方便 Agent 与外部系统交互
- **PTY**：通过 WebSocket 提供完整终端体验，兼容 xterm.js
- **Secure credential injection**：通过 outbound proxy 实现网络层认证，Agent 代码不可见凭证
- **代码解释器**：Python/JavaScript/TypeScript 持久化上下文

当前限制：
- 快照功能正在推出（rollout 进行中）
- Active CPU Pricing 意味着需要关注实际 CPU 使用时间
- 需要 Cloudflare 账号和 Containers 产品支持

---

## 七、Agent 执行环境的设计启示

Cloudflare Sandboxes 的发布揭示了 AI Agent 基础设施的一个重要趋势：**从函数式执行到机器级执行**。

传统 FaaS（Function as a Service）的核心抽象是「一个函数接收请求，返回响应」。但 AI Agent 的工作模式更接近人类开发者：打开电脑 → 克隆仓库 → 配置环境 → 写代码 → 测试 → 提交 PR → 保持会话以继续工作。

Sandboxes 正是对这种工作模式的云端映射。它不只是一个隔离环境，更是一台**为 Agent 优化的持久化虚拟机**。快照机制解决的是「关闭后如何继续」的问题；零信任代理解决的是「如何安全访问内部服务」的问题；PTY 和文件系统监听解决的是「如何接入人类的开发反馈循环」的问题。

这与 OpenAI 的 Manifest abstraction（将代码生成结果与执行环境解耦）代表了两种不同的抽象层级：OpenAI 选择让环境变得可描述（Manifest），Cloudflare 选择让环境变得更强大（持久化机器）。两者并不冲突，未来可能出现整合两个优点的混合方案。

---

## 总结：Cloudflare Sandboxes 在 Agent 工程化版图中的位置

| 能力 | 解决的问题 | 对应 Harness 组件 |
|------|-----------|------------------|
| 持久化隔离计算机 | 代码执行状态的连续性 | Execution Runtime |
| 快照快速恢复 | 长时间任务的断点续传 | State Management |
| 零信任出站代理 | 凭证安全管理 | Security Layer |
| PTY + 文件监听 | Agent 接入人类反馈循环 | Human-in-the-loop |
| Preview URLs | Agent 产出的即时验证 | Artifact Verification |

Cloudflare Sandboxes 补全了企业级 Agent 基础设施的关键一块——**执行环境本身的可信赖性和持续性**。它与 Cursor Self-Hosted 的网络边界控制、OpenAI Agents SDK 的多提供商抽象，共同构成了 2026 年 Agent 生产部署的三大基础设施范式。

---

## 引用来源

- [Agents Week 2026 Review — Cloudflare](https://blog.cloudflare.com/agents-week-in-review/)
- [Agents have their own computers with Sandboxes GA — Cloudflare](https://blog.cloudflare.com/sandbox-ga/)
- [Cloudflare Sandboxes SDK — GitHub](https://github.com/cloudflare/sandbox-sdk)
- [Dynamic, identity-aware, and secure: egress controls for Sandboxes](https://blog.cloudflare.com/sandbox-auth/)
- [OpenAI Agents SDK — GitHub](https://github.com/openai/openai-agents-python)