# GNAP：Git原生Agent协调协议——无服务器的编排新范式

> **核心判断**：MCP 和 A2A 解决的是协议层问题，但都需要服务器、数据库或专用的协调基础设施。GNAP（Git-Native Agent Protocol）的起点完全不同——用 git 本身作为协调层，让所有主流 Agent（OpenClaw、Codex、Claude Code 或自定义 Agent）通过四个 JSON 文件和标准 git 操作即可组成团队。本文拆解 GNAP 的架构设计决策，评估它与现有协调协议的取舍。

---

## 传统多Agent协调的隐性成本

当前主流的多Agent协调方案——无论是 MCP 的工具调用、A2A 的 Agent 间通信，还是 CrewAI/LangGraph 的工作流引擎——都隐含着一个共同假设：**需要一个中心化的协调层**。

这个协调层可能是：
- 一个长期运行的 WebSocket 服务（处理状态续传）
- 一个消息队列或数据库（存储任务队列和执行记录）
- 一个 API 网关（管理 Agent 注册和服务发现）

每增加一个基础设施组件，就引入一组新的运维问题：服务可用性、数据一致性、访问授权、部署复杂度。对于需要在隔离环境中运行多个 Agent 团队的企业团队来说，这个隐性成本往往在 POC 阶段被低估，在生产阶段才暴露。

GNAP 提出的核心问题是：**如果把 git 本身作为协调层，这些问题能否被消除？**

---

## GNAP 的设计：用commit作为协调事件

GNAP（Git-Native Agent Protocol）是一个 RFC 草稿阶段的协调协议，其核心洞察是：**git 的 commit 天然是一个分布式、版本化、可审计的事件日志**。

### 四个文件，一个协议

GNAP 只需要在项目根目录添加一个 `.gnap/` 子目录，包含四个文件：

```
.gnap/
├── version          # 协议版本号（如 "4"）
├── agents.json      # 团队成员（人 + AI Agent）
├── tasks/           # 任务队列（FA-1.json, FA-2.json, ...）
└── runs/            # 执行记录（FA-1-1.json, FA-1-2.json, ...）
```

每个文件都有明确定义的语义：

**agents.json** — 团队注册表，记录每个 Agent 的身份、能力和状态：
```json
{
  "agents": [
    {
      "id": "researcher-1",
      "type": "ai",
      "capabilities": ["web-search", "document-read"],
      "active": true
    },
    {
      "id": "alice",
      "type": "human",
      "role": "reviewer"
    }
  ]
}
```

**tasks/*.json** — 工作项，每个任务包含描述、分配者和状态：
```json
{
  "id": "FA-3",
  "title": "Analyze competitor pricing",
  "assignee": "researcher-1",
  "status": "open",
  "created": "2026-04-19T10:00:00Z"
}
```

**runs/*.json** — 每次执行尝试的记录，包括输入、输出和结果：
```json
{
  "id": "FA-3-1",
  "task": "FA-3",
  "agent": "researcher-1",
  "started": "2026-04-19T10:05:00Z",
  "completed": "2026-04-19T10:12:00Z",
  "result": "success",
  "output": { "summary": "Price analysis complete" }
}
```

### Agent的心跳循环

每个 Agent 运行一个极简的心跳循环：

```
1. git pull
2. 读取 agents.json → 确认自己是否处于活跃状态
3. 读取 tasks/ → 发现分配给自己的任务
4. 读取 messages/ → 是否有发给自己的消息
5. 执行工作 → git add → git commit → git push
6. sleep(N秒) → 重复
```

整个协调过程不需要任何专用服务。Agent 可以是 Claude Code、OpenAI Codex、OpenClaw 或任何能执行 git push 的自定义程序。

### 为什么git适合做协调层

GNAP 选择 git 并非为了蹭热点，而是因为 git 的几个核心特性恰好解决了分布式协调的经典问题：

**分布式一致性**：git 的 push/pull 机制提供了端到端的一致性保证。一个 commit 要么被所有节点看到，要么没有——不存在"部分同步"的状态。

**审计日志即状态历史**：git log 是完整的执行历史。每次任务分配、执行尝试和结果提交都被永久记录，无需额外的数据库或日志服务。

**无单点故障**：每个克隆都是完整副本。服务器宕机不影响 Agent 继续工作——它们只是暂时无法 push，等恢复后自动同步。

**离线能力**：Agent 可以在完全隔离的环境中工作，push/pull 等网络恢复后自动同步。这对于安全隔离环境或网络不稳定场景是关键优势。

---

## 架构分层：Git作为传输+存储

GNAP 的架构文档明确描述了三个层次：

```
┌──────────────────────────────────────────────────┐
│ Application Layer（可选）                         │
│ 预算追踪 · 仪表板 · 工作流 · 治理规则              │
├──────────────────────────────────────────────────┤
│ GNAP Protocol（协议规范）                         │
│ agents · tasks · runs · messages                 │
├──────────────────────────────────────────────────┤
│ Git（传输层 + 存储层）                             │
│ push/pull · merge · history · distribution        │
└──────────────────────────────────────────────────┘
```

关键设计决策：**应用层不在协议范围内**。GNAP 只定义四个核心实体（Agent、Task、Run、Message），所有业务逻辑（预算控制、优先级、审批流）都在应用层实现。这保持了协议的简洁性，同时允许不同场景按需扩展。

---

## 与主流框架的量化对比

GNAP 官方提供了一个对比表，直接将自己与当前主流的多Agent平台比较：

| 维度 | GNAP | AgentHub | Paperclip | Symphony | CrewAI/LangGraph |
|------|------|----------|-----------|----------|------------------|
| 需要服务器 | ❌ 无 | ✅ Go服务 | ✅ Node.js | ✅ | ✅ Python |
| 数据库 | ❌ 无（git） | ✅ SQLite | ✅ PostgreSQL | ✅ In-memory | ✅ In-memory |
| 供应商锁定 | ❌ 无 | ❌ 无 | ❌ 无 | ⚠️ Linear+Codex | ⚠️ LangChain/OpenAI |
| 启动时间 | **30秒** | 5分钟 | 30分钟 | 30分钟 | 15分钟 |
| 任务追踪 | ✅ 内置 | ❌ 无 | ✅ 有 | ⚠️ 依赖Linear | ❌ 无 |
| 成本追踪 | ✅ 有（runs） | ❌ 无 | ✅ 有 | ✅ 有 | ❌ 无 |
| Agent间消息 | ✅ 有 | ✅ channels | ⚠️ 有限 | ❌ 无 | ❌ 无 |
| 人类+AI混合 | ✅ 有 | ✅ 有 | ✅ 有 | ❌ 无 | ❌ 无 |
| **离线工作** | ✅ 有 | ❌ 无 | ❌ 无 | ❌ 无 | ❌ 无 |

这个对比有几个值得关注的维度：

**离线能力是GNAP独有的**。没有其他框架能在网络中断期间继续工作并在恢复后自动同步。这个特性在安全隔离环境、开发中频繁切换网络场景、以及需要跨多个独立网络运行的团队中有实际价值。

**零基础设施是真实承诺，不是噱头**。不需要数据库意味着没有 SQL 迁移、没有连接池、没有备份策略要维护。这在 GNAP 的对比表里是与其他框架最本质的差异。

**任务追踪是内置的**。CrewAI 和 LangGraph 的任务追踪依赖外部系统（Linear、Jira），而 GNAP 把任务状态直接放在 git 里，不需要额外服务。

---

## 局限性：没有魔法

GNAP 的设计选择带来了明显的权衡，不是所有场景都适合。

**实时性受限于心跳频率**。心跳循环的间隔决定了任务被发现的延迟。如果设置为 30 秒，Agent 最多需要 30 秒才能发现自己被分配了新任务。这对需要亚秒级响应的场景（如交互式编程助手）是硬伤。

**冲突解决依赖 git merge，不是共识协议**。如果两个 Agent 同时修改同一个任务文件，git 会产生冲突，需要手动解决或依赖应用层的冲突策略。相比之下，使用数据库的方案可以通过事务或乐观锁避免这类问题。

**Git历史不是为高吞吐量设计的**。当任务数量达到数万、执行记录达到数十万条时，git 仓库会变得臃肿。虽然这可以通过定期归档或克隆新仓库解决，但引入了额外的运维负担。

**RFC草稿阶段，生产环境自担风险**。GNAP 目前是 draft 状态，协议本身可能发生变化。生产系统采用需要自行承担兼容性风险。

**没有原生的streaming或callback机制**。传统的 Agent 通信协议（如 A2A）支持实时的 streaming 响应，而 GNAP 的 pull 模式天然不支持。如果需要实时看到 Agent 的中间输出，GNAP 不适合。

---

## 适用场景判断

GNAP 不是银弹，但在特定场景下提供了真实的基础设施节省：

**✅ 适合 GNAP 的场景**：
- 快速组建多 Agent 团队的临时项目，不需要部署服务
- 需要完整审计追踪的合规场景（git log = 审计日志）
- 隔离/气隙环境，无法访问外部消息服务
- 小型团队（<10 Agent），任务复杂度适中

**❌ 不适合 GNAP 的场景**：
- 需要亚秒级实时响应的交互式场景
- 高吞吐量（每秒数百任务分配/完成）
- 需要复杂业务逻辑（权限审批、条件触发）的场景
- 对协议稳定性有要求的生产系统

---

## 演进价值评估

GNAP 代表了一种有别于 MCP/A2A 的协调思路：**不需要基础设施的协调协议**。这在概念上与 Web 的静态网站（无需服务器）和区块链的共识机制有相似之处——用底层系统的保证（git 的一致性）代替中间件的复杂性。

从 Agent 演进路径看，GNAP 对应 Stage 7（Orchestration）和 Stage 9（Multi-Agent）的特定子场景：需要人在回路、需要完整审计、不需要实时性的多 Agent 协作团队。

值得关注的是，OpenHands（一个开源软件 Agent SDK）和 AWS Agent Squad 都已在 issues 中引用 GNAP 作为协调基板的候选方案。如果这些项目推进 GNAP 的生产实现，GNAP 的成熟度会快速提升。

---

## 一手来源

- [GNAP GitHub Repo - farol-team](https://github.com/farol-team/gnap)：协议规范和实现，含与主流框架的对比表
- [OpenHands#13416 - GNAP as task coordination substrate](https://github.com/OpenHands/OpenHands/issues/13416)：OpenHands SDK 对 GNAP 的评估
- [Agent Squad#447 - GNAP for multi-agent coordination](https://github.com/awslabs/agent-squad/issues/447)：AWS 对 GNAP 的引用

---

*分类：orchestration | 演进阶段：Stage 7 🎬 Orchestration / Stage 9 🤖 Multi-Agent | 产出时间：2026-04-20*
