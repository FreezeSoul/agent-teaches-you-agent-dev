# OpenAI Codex 安全运行架构：企业级 Agent 控制面设计

**本文核心论点**：OpenAI 的 Codex 安全方案解决了企业部署 coding agent 的三个根本问题：**边界控制**（sandbox 定义技术执行边界）、**审批策略**（何时需要人类批准）、**可审计性**（agent-native 遥测日志）。这三个问题不解决，企业根本无法放心让 Agent 执行高风险操作。

**一手来源**：[OpenAI Engineering Blog: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)（2026-05）

**关联前文**：本文是 [Anthropic「Effective Harnesses for Long-Running Agents」Initializer Pattern](./anthropic-effective-harnesses-long-running-agents-initializer-pattern-2026.md) 的姊妹篇——Anthropic 解决的是「长程 Agent 的架构模式」，本文解决的是「企业级 Agent 的安全控制面」。两者共同构成完整的企业 Agent 部署方案。

---

## 一、问题：Agent 能力越大，企业越不敢用

随着 coding agent 能力增强，企业面临一个悖论：Agent 能做的事越多，企业越不敢让它做。原因是：

1. **边界模糊**：Agent 能读写文件系统、访问网络、执行命令——这些能力在生产环境中意味着什么？
2. **审批困境**：每个操作都要人类批准 → Agent 效率归零；完全不审批 → 安全风险敞口
3. **黑盒问题**：传统的 SIEM 日志只回答「what happened」（进程启动、文件变更），不回答「why did the agent do it」

> "As AI systems become more capable, they increasingly act on behalf of users. Coding agents can autonomously review repositories, run commands, and interact with development tools. These are tasks that previously required direct human execution."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

企业需要的不是限制 Agent 能力，而是**在保持效率的同时建立清晰的控制面和可观测性**。

---

## 二、核心设计原则：productive inside bounded environment

OpenAI 部署 Codex 的原则是：

> "The agent should be productive inside a bounded environment, low-risk everyday actions should be frictionless, and higher-risk actions should stop for review."

这句话包含三个要素：

1. **Bounded environment**：技术执行边界（sandbox）
2. **Low-risk frictionless**：低风险操作无阻力
3. **Higher-risk stop for review**：高风险操作必须人类介入

这是典型的**分层控制**思路——不是二元的「全批准/全拒绝」，而是有梯度的风险响应。

---

## 三、Sandbox：技术执行边界

Sandbox 定义了 Agent 能做什么的技术边界：

```yaml
# Sandbox 配置示例（OpenAI 部署实践）
sandbox:
  write_permissions:
    - /workspace/codex-sandbox/   # 仅允许写入指定目录
    - /tmp/codex-output/
  network_policy:
    allowed_outbound:
      - api.github.com
      - registry.npmjs.org
      - pypi.org
    blocked_outbound:
      - "*"  # 默认拒绝所有出站请求
    approval_required_for:
      - "*.internal.company.com"
      - "cloud-storage.*.amazonaws.com"
```

关键设计点：**sandbox 是技术强制边界，不依赖 Agent 自觉遵守**。无论 Agent 认为某操作是否安全，只要超出 sandbox 配置，操作就会被阻止。

### 网络策略的三级模式

OpenAI 的网络策略采用三级设计：

| 级别 | 行为 | 场景示例 |
|------|------|---------|
| **Allowed** | 直接放行 | GitHub API、npm registry |
| **Blocked** | 直接拒绝 | 外部未授权服务 |
| **Approval Required** | 暂停等待批准 | 访问公司内部服务、云存储 |

这种设计让 Agent 在常见工作流中无阻力运行，同时对高风险访问建立强制审批点。

---

## 四、Approval Policy：何时停下来等人类

审批策略与 sandbox 结合工作。Agent 执行操作时：

1. 先检查 sandbox 边界——超出边界 → 直接阻止
2. 在边界内，检查 approval policy——需要批准 → 暂停等待
3. 用户可以：**单次批准**（once）或**session级批准**（approve that type for that session）

### Auto-review Mode：减少审批摩擦的核心创新

> "For routine approval requests, we are using Auto-review mode, which is a feature that, when turned on, auto-approves certain kinds of requests to reduce how often users have to stop and approve Codex actions."

Auto-review 是一个**内部 subagent**，它的职责是：

```
User Request → Codex 规划操作 → 发送给 Auto-review subagent
    → 低风险操作？ → Auto-review 直接批准，Codex 继续执行
    → 高风险操作？ → 暂停，通知人类审批
```

Auto-review 的决策基于：
- 操作类型（read-only vs write vs network）
- 目标路径/域名（已知白名单 vs 未知）
- 上下文（用户最近是否批准过类似操作）

这个模式解决了一个关键问题：**传统的人机审批模式会把 Agent 效率拖到接近零**——人类无法实时响应每个操作审批。Auto-review 让 Agent 在低风险操作上实现完全自动化，只在高风险操作时才真正停下来。

> 笔者认为：Auto-review 本质上是一个**规则引擎 + 小型 Agent** 的组合。它不是大模型判断「安不安全」（那会引入不确定性和延迟），而是用确定性规则处理已知模式，只将真正模糊的决策留给人类。这是一个务实的工程选择。

---

## 五、Credential 管理：凭证不进入执行环境

> "Separating harness and compute helps keep credentials out of environments where model-generated code executes."
> — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

这条原则直接呼应了 OpenAI Agents SDK 的「Harness/Compute 分离」设计。Codex 的凭证管理策略：

1. **CLI 和 MCP OAuth 凭证**：存储在 OS 安全 keyring（而非代码或环境变量）
2. **登录强制通过 ChatGPT**：所有认证必须通过企业 ChatGPT workspace
3. **访问 pin 到企业 workspace**：Codex 的操作绑定到企业的合规日志平台

这确保了：
- 凭证不会出现在 Agent 的执行环境中（不会被 `env` 或文件系统操作泄露）
- 所有 Agent 操作都在企业 workspace 的合规审计范围内

---

## 六、Agent-Native Telemetry：超越传统 SIEM 的可观测性

这是本文最具工程价值的部分。

传统 SIEM 日志的问题：
```
✅ 记录了：a process started, a file changed, a network connection was attempted
❌ 没有记录：why did the agent do this, what was the user's intent
```

**Agent-native telemetry** 让安全团队看到的不只是「系统事件」，而是「Agent 决策链」：

```json
// OpenTelemetry log 示例（Codex 事件类型）
{
  "event_type": "tool_approval_decision",
  "timestamp": "2026-05-09T14:23:11.423Z",
  "agent_session_id": "codex-session-abc123",
  "user_prompt": "Fix the authentication bug in userservice",
  "planned_action": "Bash(git checkout -b fix-auth)",
  "approval_decision": "auto_approved",
  "auto_review_reason": "read_only_git_operation_whitelisted",
  "tool_execution_result": "success",
  "network_policy_decision": "allowed",
  "mcp_server_usage": ["filesystem", "git"]
}
```

Codex 支持导出的事件类型：
- User prompts
- Tool approval decisions（包括 auto-review 的决策理由）
- Tool execution results
- MCP server usage
- Network proxy allow/deny events

### AI Security Triage Agent：让日志产生行动

OpenAI 不仅仅收集日志，还用 AI 对日志进行处理：

> "When an endpoint alert says Codex did something unusual, the endpoint security tool tells us that a suspicious event occurred. Codex logs then help explain the surrounding intent by the user and agent."

他们的 AI 安全 triage agent 的工作流：
1. Endpoint EDR 触发警报（检测到异常事件）
2. AI triage agent 调取 Codex 日志（user prompt → planned action → approval decision → tool results → network policy）
3. AI 分析决策链，判断是「预期行为」还是「需要升级」
4. 安全团队收到结构化的分析报告，而非一堆原始日志

这是一个**自动化的事件分类 + 根因分析**系统，比传统 SIEM 的规则匹配高明一个量级。

---

## 七、Configuration 管理：跨表面的统一策略

OpenAI 的配置管理通过三层叠加实现：

```
Cloud-managed requirements（管理员控制，用户不可覆盖）
    ↓
macOS managed preferences（团队/用户组级别配置）
    ↓
Local requirements files（特定环境测试配置）
```

这三层配置**同时应用于所有 Codex 接入点**：
- Desktop app
- CLI
- IDE extension

这解决了企业常见问题：**不同接入点策略不一致导致安全边界被绕过**。通过中心化的配置管理，确保 Agent 无论从哪个入口触发，都遵守相同的策略。

---

## 八、与 Anthropic 方案的对比

| 维度 | OpenAI Codex | Anthropic（Managed Agents）|
|------|-------------|---------------------------|
| **核心架构** | Sandbox + Approval Policy + Telemetry | Brain-Hands 解耦 + Initializer Pattern |
| **审批模式** | Auto-review subagent（自动化审批）| Initializer 预批准 + 人类 on-demand |
| **凭证管理** | OS keyring + Workspace binding | Harness/Compute 分离 |
| **可观测性** | OpenTelemetry + AI triage agent | Agent-native 日志 + 审计 |
| **适用场景** | 企业内部安全合规优先 | 长程任务自主性优先 |

两者并不矛盾——**可以共存**。在需要高度自主性的长程任务中用 Anthropic 的架构，在需要企业安全审计的场景中用 OpenAI 的控制面。

> 笔者认为：OpenAI 这篇文章的本质是「企业安全合规视角的 Agent 部署」，而 Anthropic 那篇是「工程架构视角的 Agent 部署」。两者回答的是不同角色的问题——安全团队 vs 平台工程师。这两个视角的交叉点才是完整的生产 Agent 部署方案。

---

## 九、给平台工程师的实践启示

**1. 不要依赖 Agent 自觉遵守安全规则**
Sandbox 必须在技术层面强制执行，而不是期望 Agent「知道不该做什么」。

**2. 审批策略要有梯度**
二元审批（全部批准/全部拒绝）会让 Agent 效率归零。设计低风险自动批准、高风险强制审批的梯度策略。

**3. 凭证必须与执行环境隔离**
凭证存储在 Agent 无法读取的位置（Harness 层），而不是通过环境变量传递。

**4. 日志要记录决策链，而非只是事件**
传统日志无法回答「why」的问题。Agent-native 日志要包含：user intent → planned action → approval decision → execution result。

**5. 用 AI 自动化事件分类**
收集日志只是第一步，用 AI 将日志转化为可操作的安全情报才是目标。

---

**引用来源**：

1. "As AI systems become more capable, they increasingly act on behalf of users. Coding agents can autonomously review repositories, run commands, and interact with development tools. These are tasks that previously required direct human execution." — [OpenAI Engineering Blog: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)

2. "For routine approval requests, we are using Auto-review mode, which is a feature that, when turned on, auto-approves certain kinds of requests to reduce how often users have to stop and approve Codex actions." — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

3. "Separating harness and compute helps keep credentials out of environments where model-generated code executes." — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

4. "When an endpoint alert says Codex did something unusual, the endpoint security tool tells us that a suspicious event occurred. Codex logs then help explain the surrounding intent by the user and agent." — [OpenAI Engineering Blog](https://openai.com/index/running-codex-safely/)

5. "These primitives include tool use via MCP, progressive disclosure via skills, custom instructions via AGENTS.md..." — [OpenAI Engineering Blog: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)
