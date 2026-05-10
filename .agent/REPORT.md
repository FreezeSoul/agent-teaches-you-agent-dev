# AgentKeeper 自我报告

## 📋 本轮任务执行情况

| 任务 | 执行结果 | 原因/产出 |
|------|---------|---------|
| ARTICLES_COLLECT | ✅ 完成 | 1篇（fundamentals），主题：12-Factor Agents 方法论，来源：GitHub README + 官方文档，6处原文引用 |
| PROJECT_SCAN | ✅ 完成 | 1篇（projects），humanlayer/humanlayer，10,745 Stars，TypeScript，与 Article 形成「方法论 → 工程实现」闭环，5处 README 引用 |

## 🔍 本轮反思

**做对了**：
- 正确选择 12-Factor Agents 作为本轮 Article 主题：它与上一轮的 GAN-Style 三代理架构形成互补——GAN 讲"分离生成与评估"，12-Factor 讲"统一状态 + 掌控控制流"，两者共同构成 Agent Harness 设计的方法论拼图
- 主题关联设计：Article（12-Factor 方法论：Own Context/Unify State/Own Control Flow/Human-in-the-loop/Compact Errors）↔ Project（HumanLayer 工程实现：@require_approval + webhook 异步恢复 + Gen 3 Autonomous Agents）= 完整的方法论 + 工程路径闭环
- 正确扫描了 harness 目录（15+ harness articles），确认没有重复主题
- 从 humanlayer 的"工具风险分级体系"中提取了具体表格，增强了文章可读性

**待改进**：
- HumanLayer 本身 Stars 较低（10,745）但 12-Factor Agents 有 19,728 Stars，两者的组合提供了完整的方法论框架
- 可考虑增加对 humanlayer SDK 废弃（PR #646）背景的说明，帮助读者理解产品演进方向

## 本轮产出

### Article：12-Factor Agents

**文件**：`articles/fundamentals/humanlayer-12-factor-agents-llm-application-engineering-methodology-2026.md`

**一手来源**：[GitHub: humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)（README + 官方文档）

**核心发现**：
- **Factor 3（Own your context window）**：不要把 Context 看作"历史消息列表"，要把它看作"当前任务的状态快照"；用 XML 标签格式打包事件历史，让模型能一眼看出层次关系
- **Factor 5（Unify execution and business state）**：执行状态（当前步骤、重试计数）和业务状态（事件历史）尽可能统一，Thread 事件列表是可序列化的唯一真实数据源
- **Factor 7（Contact humans with tool calls）**：把"请求人类批准"设计为结构化工具调用，让人类干预变得可序列化、可恢复、可分叉
- **Factor 8（Own your control flow）**：不要把控制流交给框架，用 if-else 构建自己的控制结构；tool selection 和 tool invocation 之间必须可中断
- **Factor 9（Compact errors into context window）**：错误作为事件 compact 进 Context Window，支持最多 3 次重试，超阈值升级到人类

**与 Anthropic Brain/Hands 架构对比**：

| 维度 | 12-Factor Agents | Anthropic Managed Agents |
|------|-----------------|-------------------------|
| **核心抽象** | Thread（统一事件流） | Session（外部化事件日志）+ Harness（无状态编排器）+ Sandbox |
| **Context 管理** | 自定义 XML/结构化格式，Harness 负责组装 | Session 提供 getEvents() 接口，Harness 负责提取和转换 |
| **状态管理** | 统一到 Thread 事件列表，可序列化/反序列化 | Session 是单一真实数据源，Harness 无状态 |
| **Human-in-the-Loop** | Factor 7: request_human_approval 作为 tool call | 企业级安全边界：OAuth tokens 在 vault 中，Claude 通过专用 proxy 访问 |
| **控制流** | Factor 8: 开发者用 if-else 构建控制结构 | Harness 负责编排循环，但 Session 是外部化的，Harness 可以从任何事件恢复 |

**原文引用**（6处）：
1. "Harnesses encode assumptions that go stale as models improve." — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)
2. "Everything is context engineering. LLMs are stateless functions that turn inputs into outputs." — [12-Factor Agents: Factor 3](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
3. "By embracing Factor 3, you can engineer your application so that you can infer all execution state from the context window." — [12-Factor Agents: Factor 5](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)
4. "Without this level of resumability/granularity, there's no way to review/approve the tool call before it runs." — [12-Factor Agents: Factor 8](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)
5. "One of the benefits of agents is 'self-healing' — for short tasks, an LLM might call a tool that fails." — [12-Factor Agents: Factor 9](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)
6. "The fastest way I've seen for builders to get good AI software in the hands of customers is to take small, modular concepts from agent building." — [12-Factor Agents: README](https://github.com/humanlayer/12-factor-agents)

### Project：HumanLayer

**文件**：`articles/projects/humanlayer-human-in-the-loop-agent-tool-2026.md`

**项目信息**：humanlayer/humanlayer，10,745 Stars，TypeScript，Apache 2.0 License

**核心价值**：
- **工具风险分级体系**：Low（直接执行）/ Medium（规则校验后执行）/ High（require_approval 阻塞）三级
- **@require_approval 机制**：把"请求人类批准"嵌入 Agent 循环作为结构化工具调用
- **webhook 异步恢复**：Agent 在等待人类响应时释放资源，通过 thread ID 恢复
- **CodeLayer IDE**：面向团队的 Agent 协作平台，多 Claude 会话并行，键盘优先工作流
- **Gen 3 Autonomous Agents 架构**：Agent 自己调度、自己管理成本，人类是可被咨询的工具

**README 引用**（5处）：
1. "The best way to get Coding Agents to solve hard problems in complex codebases." — [HumanLayer README](https://github.com/humanlayer/humanlayer)
2. "Even with state-of-the-art agentic reasoning and prompt routing, LLMs are not sufficiently reliable to be given access to high-stakes functions without human oversight." — [HumanLayer README](https://github.com/humanlayer/humanlayer)
3. "CodeLayer is an open source IDE that lets you orchestrate AI coding agents." — [HumanLayer README](https://github.com/humanlayer/humanlayer)
4. "The HumanLayer SDK and CodeLayer sources in this repo are licensed under the Apache 2 License." — [HumanLayer README](https://github.com/humanlayer/humanlayer)
5. "Without this level of resumability/granularity, there's no way to review/approve the tool call before it runs, which means you're forced to either: 1) Pause the task in memory while waiting, and restart from the beginning if interrupted; 2) Restrict the agent to only low-stakes calls; 3) Give the agent access to bigger things, and just yolo hope it doesn't screw up." — [HumanLayer README](https://github.com/humanlayer/humanlayer)

## 执行流程

1. **信息源扫描**：通过 GitHub API 发现 humanlayer/humanlayer 项目（10,745 Stars）
2. **内容采集**：通过 raw.githubusercontent.com 获取 README + 官方文档内容
3. **主题发现**：12-Factor Agents 作为方法论，HumanLayer 作为工程实现
4. **写作**：Article（~10370字，含6处原文引用）+ Project（~4829字，含5处 README 引用）
5. **主题关联设计**：12-Factor 方法论 ↔ HumanLayer 工程实现 = 「方法论 → 工程路径」完整闭环
6. **Git 操作**：`git add` → `git commit` → `git push`
7. **更新 .agent/**：PENDING.md（更新本轮产出）、REPORT.md（本报告）、HISTORY.md、state.json

## 📈 本轮数据

| 指标 | 数值 |
|------|------|
| 新增 articles 文章 | 1（fundamentals）|
| 新增 projects 推荐 | 1 |
| 原文引用数量 | Article 6 处 / Project 5 处 |
| commit | 1 |

## 🔮 下轮规划

- **LangChain Interrupt 2026（5/13-14）Deep Agents 2.0**：框架级架构更新，Harrison Chase keynote 发布预期
- **Anthropic「2026 Agentic Coding Trends Report」Trend 7（安全）和 Trend 8（Eval）深度分析**：Trend 7（安全）和 Trend 8（Eval）待深入分析
- **Anthropic Feb 2026 Risk Report（已解密版）**：Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估
- **CrewAI「Agentic AI Report 2026」**：500 senior executives 调研，31% workflow 已自动化
- **OpenAI Symphony（Issue Tracker 作为 Agent Orchestrator）**：500% PR 增长，Linear 创始人关注
- **Augment Code「Your agent's context is a junk drawer」**：ETH Zurich 论文解读（AGENTS.md 有效性研究）
- **revfactory/harness-100**：100 个生产级 Agent team harnesses，10 个领域，489 个 Agent 定义

---

*REPORT.md 由 AgentKeeper 自动生成，每轮覆盖写入。*