# Project: HumanLayer — 把"人类审查"变成 Agent 的可序列化工具

> **一句话评价**：HumanLayer（前身 CodeLayer）是最务实的人机协作 Agent 开发框架——不是把人当作审批流程的外部节点，而是把"请求人类批准"本身设计为一个结构化工具调用，让人类干预变得可恢复、可分叉、可观测。
>
> **Star**: 10,745 | **Language**: TypeScript | **Topics**: `human-in-the-loop`, `claude-code`, `agents`, `llm`

---

## 为什么这个项目值得关注

### 1. 解决的是生产级 Agent 的核心痛点

大多数 Agent 框架在原型阶段表现优异，但一旦进入生产环境，就会遇到一个无法回避的问题：**高风险操作（如发邮件、写数据库、发布内容）需要人工审查，但框架没有提供标准化的人机协作接口**。

HumanLayer 的解法是把"请求人类批准"抽象为一个工具调用（`require_approval`），嵌入到 Agent 的循环中：

```python
class RequestHumanApproval:
    intent: "request_human_approval"
    action_description: str
    stakes: Literal["low", "medium", "high"]

# Agent Loop 中：
if next_step.intent == 'deploy_backend':
    await request_human_approval(next_step)  # 阻塞，等待人工响应
    await db.save_thread(thread)
    break  # 异步等待 — webhook 会回来
```

这与 12-Factor Agents 的 Factor 7 完全一致，也是它能进入 YC 并获得大量关注的原因。

### 2. 从 Context Engineering 到人机协作的完整方法论

HumanLayer 的创始人 Dex Horothy 同时维护了 [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)——一套构建可靠 LLM 应用的原则体系。他的核心洞察是：

> "Even with state-of-the-art agentic reasoning and prompt routing, LLMs are not sufficiently reliable to be given access to high-stakes functions without human oversight."
> — [HumanLayer README](https://github.com/humanlayer/humanlayer)

这意味着人机协作不是"降低 Agent 能力"的妥协，而是**让 Agent 能真正执行高风险操作的唯一可行路径**。

### 3. CodeLayer IDE：面向团队的 Agent 协作平台

HumanLayer 正在从 SDK 向 IDE 产品演进（CodeLayer），目标用户是团队。核心能力：

- **多 Claude 会话并行**：用 worktree 模式或远程云 worker 并行运行多个 Claude Code 会话
- **高级 Context Engineering**：为团队提供共享的上下文管理，避免"AI 乱改"演变成 chaos
- **Keyboard-first 工作流**：Superhuman 风格的极客键盘操作体验

### 4. 持续迭代，从 SDK 演进到产品

HumanLayer 经历了重要产品转型：

- **SDK 阶段**：HumanLayer SDK 提供 `@require_approval` 等装饰器，让现有代码获得人机协作能力
- **IDE 阶段**：CodeLayer 是独立产品，提供完整的 Agent 协作 UI
- SDK 已被废弃（[PR #646](https://github.com/humanlayer/humanlayer/pull/646)），代码层已合并到 CodeLayer 主仓库

---

## 核心功能

### 工具风险分级体系

HumanLayer 建立了清晰的功能风险分级：

| 风险等级 | 示例 | 处理方式 |
|---------|------|---------|
| **Low** | 搜索 Wikipedia、读公开 API | 直接执行 |
| **Medium** | 读私有数据（邮件/日历）、按模板发消息 | 规则校验后执行 |
| **High** | 代发邮件、代发社交内容、写数据库 | `require_approval` 阻塞，等人类确认 |

### 异步恢复能力

通过 webhook 机制，Agent 可以在等待人类响应的同时释放资源，后续通过 thread ID 恢复：

```python
@app.post('/webhook')
def webhook(req: Request):
    thread = await load_state(req.body.threadId)
    thread.events.append({
        type: 'response_from_human',
        data: req.body
    })
    # 从中断处恢复
    next_step = await determine_next_step(thread_to_prompt(thread))
    result = await handle_next_step(thread, next_step)
```

### Gen 3 Autonomous Agents 架构

HumanLayer 的文档清晰描述了 LLM 应用的演进阶段：

| Generation | 特征 | 人类角色 |
|-----------|------|---------|
| **Gen 1** | Chat — 人类提问，AI 回答 | 请求者 |
| **Gen 2** | Agentic Assistants — 框架驱动 prompt 路由和工具调用 | 单次"批准"节点 |
| **Gen 3** | Autonomous Agents — Agent 自己调度、自己管理成本 | 可被咨询的工具 |

HumanLayer 当前主要覆盖 Gen 2 场景，但架构设计已经为 Gen 3 做好了准备。

---

## 适用场景

### 值得使用 HumanLayer 的场景

- **数据库操作 Agent**：需要 DBA 审批才能执行的 SQL 操作
- **内容发布 Agent**：需要编辑审阅的博客/社交媒体发布流程
- **客户沟通 Agent**：处理客户邮件/工单，需要人工确认后才能发送
- **代码部署 Agent**：生产环境部署需要 SRE 批准

### 不适合的场景

- **纯研究型 Agent**：只做信息收集和总结，没有高风险操作
- **实时性要求极高的 Agent**：不能等待人工响应
- **已有人机协作方案的成熟团队**：可能与现有系统冲突

---

## 工程实践参考

### 与 12-Factor Agents 的配合

HumanLayer 是 12-Factor Agents 原则的工程实现样本：

```python
# 12-Factor: Factor 5 - Unify state
# HumanLayer 实现：
class Thread:
    events: List[Event]  # 执行状态 + 业务状态统一

# 12-Factor: Factor 7 - Contact humans with tool calls
# HumanLayer 实现：
await request_human_approval(next_step)  # 人类是 Agent 的工具

# 12-Factor: Factor 8 - Own control flow
# HumanLayer 实现：
if next_step.intent == 'request_clarification':
    await notify_human(next_step)
    await db.save_thread(thread)
    break  # Agent 自己决定何时暂停
```

### 与 Anthropic Agent Harness 生态的关系

HumanLayer 的架构设计与 Anthropic 在"Scaling Managed Agents"中描述的 Session/Harness 模式形成互补：

- **Anthropic 的方案**：Session（外部化事件日志）+ Harness（无状态编排器）+ Sandbox（cattle）
- **HumanLayer 的方案**：Thread（统一事件流）+ request_approval（人类介入工具）+ webhook（异步恢复）

两者都强调了"状态外部化"和"控制流可干预"的重要性，只是侧重点不同。

---

## 资源链接

| 资源 | 链接 |
|------|------|
| **GitHub** | https://github.com/humanlayer/humanlayer |
| **官网** | https://humanlayer.dev |
| **YC 演讲** | https://humanlayer.dev/youtube（Advanced Context Engineering for Coding Agents）|
| **Discord** | https://humanlayer.dev/discord |
| **12-Factor Agents** | https://github.com/humanlayer/12-factor-agents |

---

## 总结评价

HumanLayer 解决了一个被大多数 Agent 框架忽视的问题：如何让 Agent 真正执行高风险操作，而不陷入"要么全做要么不做"的二元困境。通过把"请求人类批准"设计为结构化工具调用，它实现了：

1. **可序列化的人类干预**：Agent 暂停后可以通过 webhook 恢复，不丢失状态
2. **可分叉的协作流程**：可以在任何检查点 fork 出并行的人类审查路径
3. **可观测的审批历史**：所有人类响应都作为 Thread 事件存储，可审计可回放

对于正在从"AI 原型"向"AI 产品"跨越的团队，HumanLayer 的方法论和工具都是值得深入研究的样本。

> "The best way to get Coding Agents to solve hard problems in complex codebases."
> — HumanLayer Tagline