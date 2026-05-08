# Shell + Skills + Compaction：OpenAI 给出的长程 Agent 三原语框架

> **核心论点**：长程 Agent 从「Demo 可用」到「生产可用」需要三个正交的原语：Skills（可复用指令包）、Shell（持久化容器执行环境）、Compaction（主动上下文压缩）。Anthropic 的解法是渐进式披露（Progressive Disclosure），而 OpenAI 的解法是模块化原语组合——两者并非竞争关系，而是适用不同场景的互补架构。

---

## 1. 为什么长程 Agent 需要新的抽象

当 Agent 的运行时间从几分钟扩展到数小时，任务从单轮对话升级为多阶段工程开发时，传统的「prompt + tool call + context window」模式面临根本性挑战。

这个挑战的核心不是上下文窗口大小的问题，而是**三个正交维度的失效**：

| 维度 | 失效表现 | 根本原因 |
|------|---------|---------|
| **指令** | Agent 自由发挥，工程纪律全无 | 缺乏可复用的工作流抽象 |
| **执行** | 每步重新初始化，状态全部丢失 | 缺乏持久化执行环境 |
| **上下文** | 长对话后期「失忆」，重复劳动 | 缺乏主动压缩机制 |

> "Production agents that run for extended periods need three primitives: reusable skills, persistent shell environments, and proactive compaction."
> — [OpenAI Engineering: Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips)

OpenAI 的解法不是增大上下文窗口，而是**在模型层之下引入三个正交的基础设施原语**，让 Agent 的运行从「模型驱动」变成「模型 + 基础设施联合驱动」。

---

## 2. Skills：版本化的工作流构件

### 2.1 SKILL.md 作为 Manifest

OpenAI 的 Skills 以 `SKILL.md` 为核心——这是一个包含 frontmatter 元数据和执行流程的指令包。与 Anthropic 的 Agent Skills（渐进式披露 + 自动发现）不同，OpenAI 的 Skills 强调：

- **版本化**：每个 Skill 有版本号，可追踪可回滚
- **显式触发**：通过 slash commands 或 API 显式调用，而非依赖模型推断
- **元数据路由**：frontmatter 包含描述、适用场景、不适用场景、预期输出

```yaml
---
name: quarterly-report
version: 2.1.0
description: Generate quarterly sales reports from CRM data
use_when:
  - User asks for sales summaries, pipeline reports, revenue breakdowns
  - Data source is Salesforce or HubSpot
dont_use_when:
  - User wants marketing analytics → use marketing-report skill
  - User asks for individual deal details → use deal-lookup skill
  - Data source is a custom CSV → use data-analysis skill
expected_output:
  - PDF report with charts
  - Raw data CSV export
---
```

### 2.2 负例路由：减少 Skill 误触发的关键

Glean 的生产案例揭示了一个关键洞察：**Skill 描述中的负例（Don't use when）与正例同样重要**。

> "Routing accuracy dropped 20% initially without negative examples, then recovered after adding edge case coverage."
> — [OpenAI Engineering](https://developers.openai.com/blog/skills-shell-tips)

没有负例时，模型会在边界情况下误触发 Skill。例如「销售报告生成」Skill 可能被误触发去回答「这个月的营销活动效果如何」——负例的存在让模型能够区分「这是 sales-report skill 的领地」和「这是 marketing-report skill 的领地」。

### 2.3 隐式路由 vs 显式触发

| 模式 | 适用场景 | 特点 |
|------|---------|------|
| **隐式路由**（模型决定调用哪个 Skill） | 探索性对话、灵活任务 | 灵活但不确定 |
| **显式触发**（API 指定 `/quarterly-report`） | 生产流水线、确定性工作流 | 精确但需要人工编排 |

> "The difference between a chatbot and a workflow engine is explicit triggering."
> — [OpenAI Engineering](https://developers.openai.com/blog/skills-shell-tips)

这个区分非常重要：OpenAI 的 Skills 更接近**工作流引擎的原子步骤**，而非对话式助手的技能菜单。

---

## 3. Shell：持久化容器执行环境

### 3.1 一次性执行 vs 状态ful 执行

传统的代码执行沙箱（如 AWS Lambda、Fugue）假设每次执行都是独立的。但 Agent 的代码执行是**状态ful 的**：

- **多步骤**：单个任务可能涉及数十甚至数百个代码步骤
- **状态累积风险**：早期步骤的损坏或畸形状态会影响后续所有步骤
- **代码不可预测**：模型在运行时决定执行什么，无法提前白名单

> "Standard sandbox infrastructure is designed around one-shot execution. Agent workloads break that assumption in ways that matter at the infrastructure level."
> — [Northflank: Code Execution Environment for Autonomous Agents](https://northflank.com/blog/code-execution-environment-for-autonomous-agents)

### 3.2 容器复用模式

OpenAI Hosted Shell 的核心设计是**跨步骤复用同一个容器**：

```
Step 1: pip install pandas matplotlib  →  容器状态保存（依赖已安装）
Step 2: Load data, generate charts   →  复用已安装的依赖，上一步的输出
Step 3: Write report to /mnt/data    →  访问 Step 2 的输出文件
```

通过 `previous_response_id` 实现跨请求的容器状态延续。这避免了每次步骤重新冷启动的开销（依赖安装、环境初始化），同时允许 Agent 在中间结果上继续构建。

**何时用新容器 vs 复用容器**：

| 场景 | 推荐策略 |
|------|---------|
| 步骤之间有依赖，需要访问中间输出 | 复用同一容器 |
| 步骤相互独立，需要可重现性保证 | 用新容器 |
| 前一步破坏了环境状态 | 用新容器 |

### 3.3 Install → Fetch → Artifact：确定性交付模式

OpenAI 提出的三阶段模式为长程 Agent 的代码执行提供了清晰的故障隔离：

```
Phase 1: Install  →  设置环境，安装依赖
           ↓ 如果 Install 失败，不浪费 token 做 Fetch
Phase 2: Fetch    →  拉取外部数据，读文件，查询 API
           ↓ 如果 Fetch 失败，不生成坏 Artifact
Phase 3: Artifact →  将具体交付物写入磁盘
```

每个阶段有明确的失败模式和边界。Artifact 阶段总是产出可供审查的交付物（报告、清洗后的数据集、生成的代码）。

### 3.4 隔离模型：容器的真实成本

> "If you are running agent workloads in standard containers today, your containers aren't as isolated as you think: containers share the host kernel."
> — [Northflank](https://northflank.com/blog/code-execution-environment-for-autonomous-agents)

| 隔离方案 | 适用场景 | 风险/成本 |
|---------|---------|----------|
| **加固容器 + seccomp** | 内部 Agent，低风险任务 | 共享内核，内核逃逸风险存在 |
| **gVisor** | 中等信任，中等隔离需求 | Syscall 拦截延迟，内核特性兼容性缺口 |
| **MicroVM (Firecracker/Kata)** | 多租户生产环境，LLM 生成代码执行 | 每个 Session 有独立 guest 内核，Hypervisor 仍有攻击面 |

> "A guest kernel compromise does not directly expose the host kernel [with MicroVMs], but the hypervisor remains part of the attack surface."
> — [Northflank](https://northflank.com/blog/code-execution-environment-for-autonomous-agents)

---

## 4. Compaction：主动上下文管理

### 4.1 反应式 vs 主动式压缩

大多数团队只在**上下文溢出时**才触发压缩（反应式）。OpenAI 倡导的是主动式压缩——无论上下文是否即将溢出，都按计划压缩对话历史。

> "Without proactive compaction, agents exhibit restart behavior. They lose track of earlier steps, re-read files they already processed, and repeat work."
> — [OpenAI Engineering](https://developers.openai.com/blog/skills-shell-tips)

主动式压缩维持了一个干净的工作状态，使 Agent 在数十次 tool call 后仍能保持线程连贯性。

### 4.2 与 Anthropic/Cursor 压缩方案的关系

Anthropic 的压缩方案（Cursor Self-Summarization、Claude Composer）强调的是** learned compression**（模型学会识别高价值信息）；OpenAI 的 Compaction 更强调**规则驱动的上下文摘要**，作为 Server-Side 的自动机制。

两者并不冲突——OpenAI 的 Compaction 是在协议/基础设施层的实现，Anthropic 的 learned compression 是在模型层的实现。生产系统可以同时使用两者。

---

## 5. 三原语组合决策框架

OpenAI 给出的决策框架：

| 场景 | Skills | Shell | Compaction |
|------|--------|-------|------------|
| 快速 Q&A | 可选 | ❌ | ❌ |
| 数据分析任务 | ✅ | ✅ | ❌ |
| 多步骤工作流（10+ 步骤）| ✅ | ✅（复用容器）| ✅ |
| 长研究会话 | 可选 | 可选 | ✅（主动）|
| **生产流水线** | **✅（显式触发）** | **✅** | **✅** |

> "For production workflows with clear contracts, bypass implicit routing entirely: 'Use the quarterly-report skill with Q4 2025 data.'"
> — [OpenAI Engineering](https://developers.openai.com/blog/skills-shell-tips)

---

## 6. 安全：双层 Allowlist 架构

当 Agent 具有网络访问能力时，OpenAI 推荐**双层网络约束**：

```
Org-level allowlist  →  最大批准目标（小型、稳定）
Request-level subset →  本次任务需要的具体域名（更小型）
```

> "Never combine skills with open network access. This creates a data exfiltration path."
> — [OpenAI Engineering](https://developers.openai.com/blog/skills-shell-tips)

对于需要认证 Header 的允许域名，使用 Sidecar 注入真实凭证——模型永远看不到原始凭证。

---

## 7. 与 Anthropic 架构的对比

| 维度 | Anthropic Agent Skills | OpenAI Skills + Shell + Compaction |
|------|----------------------|----------------------------------|
| **核心抽象** | 渐进式披露（Progressive Disclosure）| 模块化原语组合 |
| **Skill 发现** | 自动发现 + 上下文路由 | 显式触发 + 元数据路由 |
| **执行环境** | 依赖外部 Harness 设计 | Hosted Shell 原生支持 |
| **上下文管理** | 模型层 learned compression | 基础设施层主动压缩 |
| **适用场景** | 复杂长程任务，需要动态上下文 | 生产流水线，需要确定性工作流 |
| **代表实现** | Claude Code Managed Agents | OpenAI Responses API + Codex CLI |

两者并非竞争关系——Anthropic 的渐进式披露解决的是「模型如何在上下文中找到正确信息」的问题；OpenAI 的三原语解决的是「如何在基础设施层保证长程 Agent 的可靠性」的问题。

---

## 8. 判断性总结

### 什么情况下选 OpenAI 三原语路线

- 需要**确定性工作流**：生产流水线的每个步骤都必须可预测、可重现
- 需要**显式编排**：通过 API 精确控制哪个 Skill 在哪个上下文中执行
- 需要**多租户隔离**：Agent 在共享基础设施上为不同用户执行代码
- 已有**深厚的工程纪律积累**：Skills 本质上是把 SOP 数字化，需要有值得编码的最佳实践

### 什么情况下选 Anthropic 渐进式路线

- 任务边界不清晰，需要 Agent 自主探索
- 上下文管理复杂度高，依赖模型的判断决定上下文取舍
- 多 Agent 协作场景，需要动态的上下文分配

### 当前局限

1. **Skill 生态尚未成熟**：Skills 的价值依赖于行业积累足够多的高质量 Skill。目前 Addy Osmani 的 agent-skills 是最完整的工程技能库（33k Stars），但覆盖范围仍限于开发阶段
2. **容器状态管理复杂度**：容器复用带来的状态累积风险需要严格的快照和回滚机制
3. **多租户网络安全**：双层 Allowlist 是好的起点，但在复杂的生产环境中网络策略管理本身就是一个挑战

---

## 参考文献

- [OpenAI Engineering: Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips)
- [Understanding Data: Long-Running Agent Patterns](https://understandingdata.com/posts/long-running-agent-patterns/)
- [Northflank: Code Execution Environment for Autonomous Agents](https://northflank.com/blog/code-execution-environment-for-autonomous-agents)
- [Anthropic Engineering: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents-2024)
- [Anthropic Engineering: Equipping Agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
