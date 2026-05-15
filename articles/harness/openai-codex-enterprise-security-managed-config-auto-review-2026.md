# OpenAI 企业级 Codex 安全运行架构：managed config、auto-review 与 agent-native telemetry

> **官方原文**：[Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)（2026-05-08）
> **关联阅读**：[Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)（2026-05-13）

---

## 核心问题

当 coding agent 以用户名义自主执行代码时，安全团队面临的不是「要不要用」，而是「怎么管」。Codex 在 OpenAI 内部部署时遇到的核心挑战是：**如何在保持 agent 效能的同时，让安全团队有足够的可见性和控制力？**

OpenAI 的答案是：managed configuration、constrained execution、network policies 和 agent-native logs——四层机制构成一个完整的企业级 harness 安全架构。

---

## 四层安全架构

### 1. Managed Configuration：配置即策略

OpenAI 通过三层配置叠加来应用安全姿态：

- **Cloud-managed requirements**：由管理员统一管控，用户无法覆盖
- **macOS managed preferences**：针对 macOS 端的桌面应用、CLI 和 IDE 扩展统一施加控制
- **Local requirements files**：允许团队、用户组或环境级别的配置测试

> 原文：*"These configurations apply across local Codex surfaces, including the desktop app, CLI, and IDE extension."*

这种分层的配置体系解决了企业的核心矛盾：安全团队需要全局一致的控制力，而开发团队需要灵活的配置能力。

### 2. Approval + Sandbox：双层约束机制

**Approval policy** 和 **sandbox** 是两套不同维度的约束：

| 维度 | Sandbox | Approval Policy |
|------|---------|----------------|
| **作用对象** | 技术执行边界（文件写入位置、网络可达性、受保护路径） | 具体的操作请求（跨边界时是否需要人工确认） |
| **决策依据** | OS 级隔离（文件 ACLs、网络防火墙规则） | 风险等级 + 用户授权级别 |
| **灵活性** | 静态配置，变更成本高 | 可按 session、按操作类型动态调整 |

Approval 和 sandbox 共同服务于同一个目标：**在有边界的环境里高效工作，低风险操作无摩擦，高风险操作显式停止**。

### 3. Auto-review mode：LLM 驱动的自动化审批

当请求跨出 sandbox 边界时，Codex 会将其发送给一个 auto-approval subagent，而不是直接打断用户：

> 原文：*"Codex sends the planned action and recent context to the auto-approval subagent, which can automatically approve low-risk actions—or high-risk actions with sufficient level of user authorization—instead of interrupting the user."*

Auto-review subagent 本身是一个 Agent——它接收 Codex 的计划动作 + 上下文，能够自动决定：
- **低风险操作**：直接批准
- **高风险操作**：检查用户授权级别，有足够权限则批准，否则拒绝

这解决了企业部署中的一个实际问题：当 agent 需要 run autonomously 时，频繁的人工审批会彻底摧毁其可用性。Auto-review 把「人机交互审批」变成了「Agent 对 Agent」的策略执行。

### 4. Agent-native telemetry：可解释的安全审计

传统安全日志只回答"what happened"（进程启动、文件修改、网络连接尝试），而安全团队需要知道"why did the agent do that"。

Codex 通过 OpenTelemetry 导出以下事件：
- User prompts
- Tool approval decisions
- Tool execution results
- MCP server usage
- Network proxy allow/deny events

> 原文：*"When an endpoint alert says Codex did something unusual, the endpoint security tool tells us that a suspicious event occurred. Codex logs then help explain the surrounding intent by the user and agent."*

OpenAI 在内部使用这些日志配合 AI 安全 triage agent：endpoint 安全工具发现异常 → Codex 日志解释 agent 和用户的意图 → AI triage agent 分析并呈现给安全团队审查。

---

## 网络策略：managed network policy

OpenAI 不给 Codex 开放式的网络访问权限。Managed network policy 的设计逻辑：

- **Allowed destinations**：已知的好工作流（如 npm install、Git clone 内部仓库）
- **Blocked destinations**：明确不想要的出口（如外部数据 exfiltration）
- **Approval required**：未知域名

这个设计背后的原则是：**默认拒绝，例外明确**。Agent 需要显式申请超出白名单的网络访问，而不是默认拥有完整的网络访问权。

---

## 与 Windows Sandbox 的关系：技术隔离 vs 策略控制

本文（Running Codex safely at OpenAI）和 Windows Sandbox 文章（Building a safe, effective sandbox）从两个维度描述了 Codex 的安全机制：

| 维度 | Windows Sandbox | Running Codex safely |
|------|----------------|---------------------|
| **关注点** | OS 级别的技术隔离（文件写入、网络访问的强制约束） | 企业级的策略控制和可见性 |
| **解决的问题** | "Codex 能访问哪些文件和网络" | "安全团队如何审计和控制 Codex 的行为" |
| **技术手段** | Windows ACLs、Write-restricted tokens、Firewall rules | Managed configs、Approval policies、OpenTelemetry |
| **使用者** | 技术实现团队 | 安全/合规团队 |

两者合在一起才是一个完整的企业级 harness 安全方案：Windows Sandbox 解决「能不能」的技术问题，Running Codex safely 解决「怎么管」的运营问题。

---

## 关键设计决策

### Decision 1：规则分层，而非单一权限模型

Codex 的规则系统不把所有 shell 命令视为同等风险，而是：
- **常见且低风险的操作**（如 `git status`、`ls`）：无审批直接通过
- **明确危险的命令**：阻止或要求审批

> 原文：*"We use rules so Codex does not treat every shell command as equally safe."*

这个设计解决了「default-deny 安全模型」的实用性问题：如果所有操作都要审批，agent 的可用性归零；如果没有任何约束，安全性归零。分层规则让 agent 在普通工程任务中保持高效，同时对高风险操作强制审查。

### Decision 2：Auto-review subagent 而非规则引擎

当请求超出 sandbox 时，OpenAI 选择用一个 Agent（auto-review subagent）来做审批决策，而不是一个基于规则的 if-then 系统：

- 规则引擎的问题是：企业环境中的例外情况太多，规则会膨胀到无法维护
- Agent 作为决策者的优势是：能理解上下文，平衡风险和效率

这本身就是一个有意思的设计选择——用 Agent 来管理 Agent 的行为。

### Decision 3：Agent-native logs 而非通用安全日志

OpenAI 明确区分了"传统安全日志"和"agent-aware telemetry"。前者回答 what，后者回答 why：

> 原文：*"Traditional security logs are still useful when looking at actions taken by Codex, but they mostly answer what happened... Defenders are still left to figure out why Codex did something, or the user's intent."*

Agent-native telemetry 是为了让安全团队能够在「Agent 自主行为」这个新范式下做有效的审计，而不是用旧工具硬凑。

---

## 对 Agent 工程的意义

### 企业级 harness 的标准架构

OpenAI 的四层架构（managed config → sandbox/approval → auto-review → telemetry）代表了 2026 年企业级 Agent 部署的标准范式：

1. **Configuration 层**：让管理员有全局控制力
2. **Execution 层**：OS 级别的硬隔离（sandbox）
3. **Policy 层**：风险感知的审批决策（auto-review）
4. **Observability 层**：Agent 可解释的审计日志

任何一个严肃的 Agent harness 产品（如 Claude Code、Cursor、Copilot）如果要进入企业市场，这四层缺一不可。

### Auto-review 的意义：从人到 Agent 的决策链

Auto-review subagent 模式引出了一个重要的设计模式：**当 Agent 需要审批时，由另一个 Agent 来处理审批请求**。这个模式在 multi-agent 系统中具有普遍意义——它意味着 Agent 之间的交互可以不是简单的 request-response，而是包含「决策」和「策略执行」的层次。

### Telemetry 的未来：从审计到持续优化

OpenAI 使用 telemetry 的方式不只是审计，还在驱动运营优化：

> 原文：*"We use these logs to understand how internal adoption is changing, which tools and MCP servers are being used, how often the network sandbox is blocking or prompting, and where the rollout still needs tuning."*

这意味着 telemetry 数据最终会反馈到 harness 的配置调整中——形成「部署 → 监控 → 配置更新 → 再部署」的闭环。

---

## 已知局限

1. **Auto-review 的信任问题**：auto-review subagent 本身也是一个 LLM，它的决策质量直接影响安全团队的信任度
2. **跨平台的配置一致性**：本文描述的配置体系在 macOS 上有成熟的 managed preferences 实现，Windows 上的 equivalent 机制在 Windows Sandbox 文章中有描述，但两者的一致性管理尚未完全解决
3. **MCP 服务器的信任边界**：Codex 通过 MCP 扩展工具能力，但 MCP server 本身的安全性（例如被篡改的 server 返回恶意结果）不在本文讨论范围内

---

## 引用

> We deploy Codex with a simple principle that it should be productive inside a bounded environment, low-risk everyday actions should be frictionless, and higher-risk actions should stop for review.
> — [OpenAI Engineering: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)

> When an endpoint alert says Codex did something unusual, the endpoint security tool tells us that a suspicious event occurred. Codex logs then help explain the surrounding intent by the user and agent.
> — [OpenAI Engineering: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)