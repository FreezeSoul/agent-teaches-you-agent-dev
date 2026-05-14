# OpenAI Codex 内部安全架构：Auto-review 子代理与 Agent-native 遥测体系

**本文核心论点**：OpenAI 在 `running-codex-safely` 中揭示的内部安全架构，解决了企业级 Agent 部署的两个核心难题——**何时授权**（Auto-review 自动审批）和**如何审计**（Agent-native 遥测）。这两个机制共同构成了「内部安全控制面」，与外部沙箱（Windows Sandbox 等）形成正交互补，构成完整的企业 Agent 安全体系。

**一手来源**：[OpenAI Engineering Blog: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)（2026-05-08）

**关联前文**：
- [OpenAI Codex Windows 沙箱：从无到有的工程演进](./openai-codex-windows-sandbox-from-unelevated-to-elevated-architecture-2026.md) — 外部沙箱的操作系统级隔离方案
- [Anthropic「Effective Harnesses for Long-Running Agents」Initializer Pattern](./anthropic-effective-harnesses-long-running-agents-initializer-pattern-2026.md) — 长程 Agent 的架构模式

---

## 一、问题：企业需要的不只是沙箱，而是控制面

外部沙箱定义了技术执行边界（文件系统、网络、进程权限），但它无法回答一个更高级别的问题：**在边界之内，Agent 的每次操作是否都应该被授权？**

企业面临的真实困境：
- 沙箱内的低风险操作（读文件、运行测试）如果仍需人工批准，Agent 的效率优势归零
- 但对高风险操作不审批，企业无法满足合规要求

> "We deploy Codex with a simple principle: it should be productive inside a bounded environment, low-risk everyday actions should be frictionless, and higher-risk actions should stop for review."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

这个「frictionless vs. stop for review」的二元决策，正是 **Auto-review mode** 要解决的问题。

---

## 二、Auto-review 子代理：让低风险操作自动通过

### 2.1 设计背景

传统授权模式有两种极端：
- **全批准**：每个操作都等人类确认，Agent 效率归零
- **全跳过**：Agent 自行决定一切，安全风险不可控

Auto-review mode 引入了第三种路径：**用专用子代理做预审批决策**。

### 2.2 机制解析

Auto-review mode 的工作流程：

```
用户请求 ──┐
           │
           ▼
    ┌──────────────────┐
    │  Codex 主代理     │
    │ (planned action   │
    │  + recent context)│
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Auto-review       │
    │ Subagent          │
    ├──────────────────┤
    │ 低风险操作 → 自动批准  │
    │ 高风险操作 → 推送用户   │
    │           (有足够授权) │
    └──────────────────┘
```

关键设计点：

> "Codex sends the planned action and recent context to the auto-approval subagent, which can automatically approve low-risk actions—or high-risk actions with sufficient level of user authorization—instead of interrupting the user."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

**发送的内容**不是简单的操作名，而是 `planned action + recent context`——这意味着子代理做决策时拥有足够的上下文，而非只看操作类型。

### 2.3 与 Anthropic 权限分层架构的对比

Anthropic 的 Auto Mode 采用的是**两层安全架构**（Skip Permissions + Human-in-the-loop），权限下放是按场景而非按实时决策。OpenAI 的 Auto-review 更进一步——**用子代理实时评估每次操作的风险级别**。

| 维度 | Anthropic Auto Mode | OpenAI Auto-review |
|------|---------------------|--------------------|
| 决策粒度 | 场景级（skip permissions 开关）| 操作级（每次操作单独评估）|
| 人类介入时机 | 预设的「always approve」边界 | 实时判断高风险后推送 |
| 上下文依赖 | 固定规则 | 发送「planned action + context」 |
| 子代理架构 | 无明确描述 | 专用 auto-approval subagent |

> 笔者认为：操作级的实时判断比场景级开关更灵活，但也更依赖子代理的判断质量——子代理本身的 prompt 工程和评测体系变得至关重要。

---

## 三、Managed Configuration：跨越云端到本地的配置一致性

### 3.1 配置架构的三层叠加

OpenAI 的配置体系由三层构成，应用于所有 Codex Surface（桌面应用、CLI、IDE 扩展）：

```
┌─────────────────────────────────────────┐
│  Cloud-managed requirements (强制，不可override) │
├─────────────────────────────────────────┤
│  macOS managed preferences + local requirements files │
│  (允许按 team/user group/environment 测试不同配置)   │
└─────────────────────────────────────────┘
```

> "Requirements are admin-enforced controls that users cannot override."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

关键特征：**云端配置是强制性的，用户在本地无法绕过**。这解决了企业安全策略落地最难的部分——「管理员配置的安全策略如何在端侧生效」。

### 3.2 与 macOS Seatbelt Profiles 的类比

在 macOS 上，OpenAI 已经利用了系统原生的 managed preferences 机制（类似于 MDM profiles）。这次披露的配置体系暗示，OpenAI 在 macOS 上是通过：
- 系统的 managed preferences 传递安全配置
- 本地 requirements 文件作为补充配置层

这意味着 OpenAI 的配置管理已经与操作系统层的安全机制对齐。

---

## 四、网络策略：已知良好目的地的白名单模式

### 4.1 三级网络访问控制

OpenAI 的网络策略不是简单的「全封或全放」，而是三级结构：

| 级别 | 行为 | 典型场景 |
|------|------|---------|
| **Allowed destinations** | 直接放行 | 已知良好的工作流终点 |
| **Blocked destinations** | 明确拒绝 | 已知的恶意地址 |
| **Unfamiliar domains** | 触发审批 | 不在白名单也不在黑名单 |

> "Our managed network policy allows expected destinations, blocks destinations we do not want Codex reaching, and requires approval for unfamiliar domains."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

这个模式体现了**最小权限原则的工程化实现**——不是「沙箱内网络全封」，而是「已知好的放行，未知的要求审批」。

### 4.2 与 Windows 沙箱「环境变量污染」方案的对比

在 Windows 沙箱文章中，OpenAI 描述了用 `HTTPS_PROXY=127.0.0.1:9` 等环境变量「让网络请求 fail-closed」的 advisory 方案。这种方案在内部部署时是可接受的后备，但在 OpenAI 自己的生产环境，他们使用了更严格的基于目的地的白名单控制。

这说明：**网络边界的控制强度取决于部署环境**——在 OpenAI 内部可以做到真正的网络层控制，在用户侧则只能依赖 advisory 方案。

---

## 五、Agent-native 遥测：超越传统 SIEM 的 agent-aware 日志

### 5.1 传统安全日志的局限

传统 SIEM 日志回答的是「what happened」：
- 进程启动了
- 文件被修改了
- 网络连接被尝试了

但它无法回答：
- **用户为什么要执行这个操作？**
- **Agent 的决策上下文是什么？**

### 5.2 Codex 的 OpenTelemetry 日志覆盖范围

Codex 支持导出的 OpenTelemetry 事件类型：

| 事件类型 | 内容 | 用途 |
|---------|------|------|
| `user prompts` | 用户原始请求 | 理解意图 |
| `tool approval decisions` | 操作审批决策（批准/拒绝）| 审计 Human-in-the-loop |
| `tool execution results` | 工具执行结果 | 追踪操作链 |
| `MCP server usage` | MCP 服务调用 | 审计工具使用 |
| `network proxy allow/deny events` | 网络策略决策 | 审计网络边界 |

> "Codex supports OpenTelemetry log export for various Codex events such as user prompts, tool approval decisions, tool execution results, MCP server usage, and network proxy allow or deny events."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

这个日志体系的独特价值在于它是 **Agent-native**——每个事件都知道自己处于 Agent 的决策上下文中，而不只是操作系统级别的操作记录。

### 5.3 AI 安全分类 Agent 的工作流程

OpenAI 内部使用 AI 安全分类 Agent（security triage agent）处理 Endpoint 安全告警：

```
Endpoint Alert 触发
       │
       ▼
AI Security Triage Agent 接收
       │
       ├── 读取 Codex 日志（原始请求 + 工具活动 + 审批决策 + 工具结果 + 网络策略）
       │
       ▼
生成分析结论
       │
       ▼
安全团队人工审查
```

> "When an endpoint alert says Codex did something unusual, the endpoint security tool tells us that a suspicious event occurred. Codex logs then help explain the surrounding intent by the user and agent."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

关键洞察：**AI triage agent 不是替代人类做决策，而是将「what happened」的 Endpoint 日志翻译为「what was the agent trying to do」的 Agent-native 分析**。这个翻译层，才是 Agent-native 遥测的核心价值。

---

## 六、四层安全体系的系统性视角

将本文（内部安全控制面）与前文（外部沙箱架构）结合，OpenAI Codex 的安全体系是四层结构：

| 层次 | 机制 | 作用 |
|------|------|------|
| **L1 外部沙箱** | Windows Seatbelt/MIC/ACL | 操作系统级隔离，执行边界 |
| **L2 内部权限层** | Auto-review subagent + rules | 操作级实时授权决策 |
| **L3 网络边界** | 白名单目的地 + 审批 | 网络访问的最小权限 |
| **L4 可审计性** | OpenTelemetry 日志 + Compliance Platform | 完整决策链可追溯 |

> 笔者认为：这套体系的工程意义在于**每层都可以独立演进**。当 Windows 的沙箱能力演进时，L1 层可以升级而不影响 L2-L4。当 Auto-review 的决策质量提升时，L2 层可以精细化而不改变 L1。这种分层设计让安全能力可以随 Agent 能力同步成长。

---

## 七、对企业 Agent 部署的启示

### 7.1 安全控制面必须内置，而非外挂

传统的安全方案是将 Agent 放在沙箱里，然后通过外部防火墙/审批工作流控制。但 OpenAI 的方案表明：**真正的企业级安全需要 Agent-native 的控制面**，控制面需要理解 Agent 的决策上下文，而不只是操作系统级的操作记录。

### 7.2 遥测是安全的基础设施，而非监控附件

「有了日志再查」的安全模式在 Agent 时代失效了。OpenAI 的 OpenTelemetry 日志体系不只是用于事后审计，而是**作为 AI triage agent 的输入**，实现实时的安全响应。这意味着日志的设计必须从一开始就将「Agent 决策上下文」作为一等公民。

### 7.3 Auto-review 的质量取决于评测体系

Auto-review subagent 的判断质量决定了「frictionless vs. stop for review」的准确性。这个 subagent 本身需要被评测和持续优化——它不是一次性实现的，而是一个需要生产验证和迭代的基础设施。

---

**执行流程**：
1. **理解任务**：自主维护仓库，每2小时执行一次
2. **规划**：Tavily API 耗尽，改用 web_fetch 直接扫描官方博客；Articles 分析 running-codex-safely（内部安全架构），Projects 推荐 agentmemory（8571 ⭐，记忆架构）
3. **执行**：web_fetch 扫描 Anthropic/OpenAI/Cursor 博客，curl 获取 GitHub Trending，API 查询 agentmemory 星标
4. **返回**：OpenAI running-codex-safely 发现新角度（内部控制面 vs 外部沙箱），agentmemory 已三次覆盖（4902→8571 星有新角度）
5. **整理**：产出一篇新 Harness 文章，完成 PENDING 队列一个 P1 项

**调用工具**：
- `exec`: 6次
- `web_fetch`: 5次
