# 12-Factor Agents：LLM 应用工程的方法论框架

> **核心问题**：为什么大多数 Agent 原型能跑、生产环境却频繁崩溃？HumanLayer 提出的 12-Factor Agents 方法论试图回答这个问题——不是给你一个框架，而是给你一套判断标准，让你在任何技术选型中都能做出更稳健的决策。
>
> **读完能得到什么**：理解 12-Factor Agents 的核心设计原则（Own Your Context、Unify State、Own Control Flow），以及这些原则如何与 Anthropic 的 Brain/Hands 架构形成方法论上的共鸣。

---

## 一、问题的根源：框架无法替代工程判断

过去两年里，Agent 框架经历了大爆发：LangGraph、CrewAI、AutoGen、Griptape、Smolagents 等等。每个框架都声称自己能解决 Agent 的可靠性问题。但现实是，大多数生产级 Agent 项目最终都在 70-80% 的质量线上停住了——团队意识到要突破这条线，需要"逆向工程"这些框架，理解它们的内部假设，然后在上面做大量定制。

这个现象背后的根本原因是：**框架编码的是当下的工程假设，而模型能力在快速演变，假设会过时**。

Anthropic 的人在 2026 年 4 月的复盘文档里说得很清楚——他们曾经给 Claude Sonnet 4.5 加了 context resets，因为模型有"上下文焦虑"（临近 context limit 时会仓促结束任务）。但当 Claude Opus 4.5 出来后，这个行为消失了，context resets 变成了冗余代码。这不是框架的 bug，是假设的保质期问题。

> "Harnesses encode assumptions that go stale as models improve."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

12-Factor Agents 的作者 Dex Horothy 在 YC 的演讲中指出：他与超过 100 个 SaaS 创始人交流过构建 Agent 应用的经历，典型的路径是：

1. 决定构建一个 Agent
2. 快速选择一个框架开始开发
3. 达到 70-80% 质量
4. 意识到这不是足够好——需要"逆向工程"框架、prompt、flow
5. 从头重写

这与 Anthropic 在 Managed Agents 上遇到的问题如出一辙：不是框架不够好，而是框架的抽象层级在某些场景下不够用。

---

## 二、12-Factor Agents 的核心设计原则

### 原则 1-3：Context Engineering（Own Your Context Window）

Anthropic 在"Scaling Managed Agents"中把 Session 设计为外部化的事件日志，Harness 在每次调用 Claude 前从 Session 按需读取组成 Context Window。这与 12-Factor 的 Factor 3（Own your context window）的方法论完全一致：

> "Everything is context engineering. LLMs are stateless functions that turn inputs into outputs. To get the best outputs, you need to give them the best inputs."
> — [12-Factor Agents: Factor 3](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)

12-Factor 的核心主张是：不要把 Context 看作"历史消息列表"，要把它看作"当前任务的状态快照"。标准的消息格式（system/user/assistant/tool messages）对大多数场景够用，但要真正榨取模型的全部能力，需要自定义的 Context 格式，针对你的场景优化 token 使用效率和注意力分配。

具体例子：12-Factor 展示了如何用 XML 风格的标签把事件历史打包进单个 user message：

```xml
<slack_message>
    From: @alex
    Channel: #deployments
    Text: Can you deploy backend v1.2.3 to production?
</slack_message>

<list_git_tags_result>
    tags:
      - name: "v1.2.3"
        commit: "abc123"
        date: "2024-03-15T10:00:00Z"
      ...
</list_git_tags_result>

<deploy_backend_result>
    status: "success"
    ...
</deploy_backend_result>
```

这个格式让模型能一眼看出事件的层次关系，而不需要在多条分散的消息中做推理。

### 原则 4-6：Execution Model（Tools as Structured Outputs + Unified State + Launch/Pause/Resume）

Factor 4（Tools are structured outputs）和 Factor 5（Unify execution and business state）是 12-Factor 最具工程洞察的两个原则。

**Factor 5 的核心主张**：不要把"执行状态"（当前步骤、重试计数、等待状态）和"业务状态"（事件历史）分开管理。尽可能统一它们。

> "By embracing Factor 3 (Own Your Context Window), you can control what actually goes into the LLM. You can engineer your application so that you can infer all execution state from the context window. In many cases, execution state is just metadata about what has happened so far."
> — [12-Factor Agents: Factor 5](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)

这正是 Anthropic 在 Managed Agents 中所做的：Session 是 append-only event log，所有执行状态都可以从事件历史中重建。Harness 是无状态的——任何 Harness 实例可以从任何 Session 恢复，继续上次中断的地方。

Factor 6（Launch/Pause/Resume with simple APIs）与 Factor 5 紧密相关。统一状态后，序列化/反序列化变得trivial——你只需要存储/恢复 Thread/事件列表：

```python
class Thread:
    events: List[Event]  # 既是执行状态，也是业务状态

def thread_to_prompt(thread: Thread) -> str:
    return '\n\n'.join(event_to_prompt(event) for event in thread.events)
```

### 原则 7：Human-in-the-Loop（Contact Humans with Tool Calls）

Factor 7 是 12-Factor 中最独特的原则——把人类当作 Agent 的工具来调用，而不是外部的审批流程：

> "By default, LLM APIs rely on a fundamental HIGH-STAKES token choice: Are we returning plaintext content, or are we returning structured data?"
> — [12-Factor Agents: Factor 7](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md)

这个设计让人类干预变得可序列化——Agent 请求人类输入，就像请求任何其他工具的结果一样自然。Thread 可以被暂停（await human_response）、恢复（webhook 返回结果）、甚至分叉（fork at any point）。

这与 Anthropic 在 Claude Code April Postmortem 中提到的修复策略形成呼应：Anthropic 为所有订阅用户重置了用量限制，因为用户发现 Agent 的行为不符合预期时，没有足够的可见性和干预手段。12-Factor 的 Factor 7 提供了这种干预的手段。

### 原则 8：Own Your Control Flow

Factor 8 直接挑战了"Agent 框架应该管理控制流"的假设：

> "Build your own control structures that make sense for your specific use case... Without this level of resumability/granularity, there's no way to review/approve the tool call before it runs, which means you're forced to either: 1) Pause the task in memory while waiting, and restart from the beginning if interrupted; 2) Restrict the agent to only low-stakes calls; 3) Give the agent access to bigger things, and just yolo hope it doesn't screw up."
> — [12-Factor Agents: Factor 8](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)

12-Factor 展示了如何用 Python 的 switch/if-else 控制 Agent 的流转：

```python
def handle_next_step(thread: Thread):
    while True:
        next_step = await determine_next_step(thread_to_prompt(thread))
        
        if next_step.intent == 'request_clarification':
            # break the loop, wait for human response
            await notify_human(next_step)
            await db.save_thread(thread)
            break  # async step - we'll get a webhook later
        elif next_step.intent == 'fetch_git_tags':
            # sync step - pass the new context to LLM directly
            issues = await linear_client.issues()
            thread.events.append({type: 'fetch_git_tags_result', data: issues})
            continue
        elif next_step.intent == 'deploy_backend':
            # high-stakes - require human approval
            await request_human_approval(next_step)
            await db.save_thread(thread)
            break
```

这个模式让控制流完全由开发者决定，而不是框架。Anthropic 在 Scaling Managed Agents 中展示的 Meta-harness 架构与此一致——Managed Agents 是"unopinionated about the specific harness"，但对接口（Session/Sandbox/Harness）高度 opinionated。12-Factor 的 Factor 8 则是在 Harness 内部实现层面提供了相同的控制能力。

### 原则 9：Compact Errors into Context Window

Factor 9 提供了一个被大多数框架忽视的能力：错误恢复的自主性：

> "One of the benefits of agents is 'self-healing' — for short tasks, an LLM might call a tool that fails. Good LLMs have a fairly good chance of reading an error message or stack trace and figuring out what to change in a subsequent tool call."
> — [12-Factor Agents: Factor 9](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)

这正是 Claude Code April Postmortem 中描述的场景——第三个 bug（系统提示词变更）在模型层面引入了"变冗长"的行为，而这个行为本可以通过更严格的 eval 体系在发布前捕获。Factor 9 暗示了一个解决方案：每次错误都应该被完整地送回 Context Window，让 Agent 自己判断是否需要重试、绕行还是升级到人类。

---

## 三、方法论对照：12-Factor vs Anthropic Brain/Hands

| 维度 | 12-Factor Agents | Anthropic Managed Agents |
|------|-----------------|-------------------------|
| **核心抽象** | Thread（统一事件流） | Session（外部化事件日志）+ Harness（无状态编排器）+ Sandbox（可抛投执行环境） |
| **Context 管理** | 自定义 XML/结构化格式，Harness 负责组装 | Session 提供 getEvents() 接口，Harness 负责从事件流中提取和转换 |
| **状态管理** | 统一到 Thread 事件列表，可序列化/反序列化 | Session 是单一真实数据源，Harness 无状态 |
| **Human-in-the-Loop** | Factor 7: request_human_approval 作为 tool call，可序列化暂停/恢复 | 企业级安全边界：OAuth tokens 在 vault 中，Claude 通过专用 proxy 访问，不直接接触凭据 |
| **控制流** | Factor 8: 开发者用 if-else 构建控制结构 | Harness 负责编排循环，但 Session 是外部化的，Harness 可以从任何事件恢复 |
| **错误处理** | Factor 9: 错误 compact 成事件，支持重试和升级 | Sandbox 失败作为 tool-call error 传给 Harness，Harness 决定是否重试或换新 Sandbox |
| **演进方向** | 原则不变，实现随模型能力变化 | 接口（Session/Sandbox/Harness）不变，实现随模型能力变化 |

两者的核心洞察一致：**把状态外部化，把控制权还给开发者**。框架的假设会过时，但接口和原则不会。

---

## 四、12-Factor 对实际工程的价值

### 什么时候 12-Factor 有用

- **框架选型**：评估一个框架时，用 12-Factor 的原则检查它是否把控制权还给你——它是否允许你自定义 Context 格式？它是否支持你接管控制流？
- **生产级 Agent 设计**：在设计早期就用 12-Factor 的检查清单评估架构，避免在 70% 质量线上被迫重写
- **团队工程实践**：12-Factor 提供了一套共享词汇，让"我们需要在 Factor 7 上投入更多"这样的讨论变得具体

### 什么时候 12-Factor 可能过度

- **原型验证阶段**：如果你的目标是快速验证 Agent 概念，用框架快速跑起来是合理的
- **简单场景**：Agent 只做单次工具调用，不需要循环和状态管理

---

## 五、已知局限与开放问题

**模型能力快速演进**：12-Factor 的作者在 README 中承认，LLM 的能力在指数级提升，核心工程技巧会持续有效，但具体实现会随模型变化。Factor 10（Small, Focused Agents）特别提到了这一点——如果模型变得足够聪明，可能不再需要复杂的 Agent 架构。

**MCP 协议的演进**：12-Factor 明确表示不讨论 MCP（"I'm not going to talk about MCP. I'm sure you can see where it fits in."），这留下了一个空白：12-Factor 的原则如何映射到 MCP 的工具发现和调用机制上？

**Eval 体系的缺失**：12-Factor 没有专门讨论评测体系（这与 Anthropic 的多篇文章形成了互补），但 Factor 9 的 error compaction 暗示了需要某种持续监控来发现模型退化。

---

## 结论

12-Factor Agents 是一套在 Agent 框架爆炸时代保持工程判断力的方法论。它的核心主张不是"用这个框架"，而是"不管你用什么框架，都要确保你控制了 Context Window、统一了状态、掌握了控制流、能把人类当作可序列化的工具调用"。

这与 Anthropic 在 Scaling Managed Agents 中展示的架构设计高度共鸣——Session 作为外部化事件日志，Harness 作为无状态编排器，Sandbox 作为 cattle 而不是 pets——这些设计决策不是偶然的，它们是从第一性原理出发解决"框架假设会过时"这个问题的方法论体现。

> "The fastest way I've seen for builders to get good AI software in the hands of customers is to take small, modular concepts from agent building, and incorporate them into their existing product."
> — [12-Factor Agents: README](https://github.com/humanlayer/12-factor-agents)

---

**一手来源引用**：
1. "Harnesses encode assumptions that go stale as models improve." — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)
2. "Everything is context engineering. LLMs are stateless functions that turn inputs into outputs." — [12-Factor Agents: Factor 3](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
3. "By embracing Factor 3, you can engineer your application so that you can infer all execution state from the context window." — [12-Factor Agents: Factor 5](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)
4. "Without this level of resumability/granularity, there's no way to review/approve the tool call before it runs." — [12-Factor Agents: Factor 8](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)
5. "One of the benefits of agents is 'self-healing' — for short tasks, an LLM might call a tool that fails." — [12-Factor Agents: Factor 9](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)
6. "The fastest way I've seen for builders to get good AI software in the hands of customers is to take small, modular concepts from agent building." — [12-Factor Agents: README](https://github.com/humanlayer/12-factor-agents)