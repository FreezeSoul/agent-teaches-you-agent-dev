# Agency-Agents：专业分工的 AI Agent 团队编排框架

## 核心判断

大多数 Agent 框架将 Agent 视为「通用工具」——一个 Agent 做所有事。而 **Agency-Agents** 反其道而行：将 Agent 设计为拥有专业身份、人格、交付物的**专才团队**。从 Frontend Developer 到 Incident Response Commander，每个 Agent 都是深耕特定领域的专家，有独特的工作流程和成功指标。

**核心差异**：其他框架是「一个通才 + 各种技能插件」，Agency-Agents 是「一群专才，各自携带完整的方法论」。这个设计选择意味着什么——它在什么场景有效、在什么场景会变成维护噩梦？

---

## 背景：为什么大多数 Agent 团队实际上是「一个人做了所有事」

当前主流的多 Agent 框架，本质上是**任务分配器**而非**团队编排器**。你有一个主 Agent，当它忙不过来时，分出一个子 Agent 帮忙；子 Agent 完成任务后结果汇总给主 Agent。

这种模式的问题：**子 Agent 没有真正的专业身份**，它只是主 Agent 的一个临时触手。

真正的团队不是这样工作的。一个 Frontend Developer 和一个 Backend Architect，他们对「好代码」的定义不同、对优先级的判断不同、使用的工具链不同。他们不是「主 Agent 的分身」，而是**拥有独立判断力的协作者**。

Agency-Agents 试图解决的就是这个问题：让每个 Agent 真的有专业身份，而不是披着专业外套的通用助手。

---

## Agent 专业分工体系

### Engineering Division（工程部）

| Agent | 专长 | 使用场景 |
|-------|------|---------|
| 🎨 Frontend Developer | React/Vue/Angular, UI 实现, 性能 | 现代 Web 应用, 像素级 UI, Core Web Vitals 优化 |
| 🏗️ Backend Architect | API 设计, 数据库架构, 可扩展性 | 服务端系统, 微服务, 云基础设施 |
| 📱 Mobile App Builder | iOS/Android, React Native, Flutter | 原生和跨平台移动应用 |
| 🤖 AI Engineer | ML 模型部署, AI 集成 | 机器学习功能, 数据管道, AI 应用 |
| 🚀 DevOps Automator | CI/CD, 基础设施自动化, 云运维 | 流水线开发, 部署自动化, 监控 |
| ⚡ Rapid Prototyper | 快速 POC, MVP | 概念验证, Hackathon 项目, 快速迭代 |
| 🔒 Security Engineer | 威胁建模, 安全代码审查, 安全架构 | 应用安全, 漏洞评估, 安全 CI/CD |
| ⛓️ Solidity Smart Contract Engineer | EVM 合约, Gas 优化, DeFi | 安全 Gas 优化的智能合约 |
| 🧭 Codebase Onboarding Engineer | 开发者 onboarding, 只读代码探索 | 帮助新开发者快速理解陌生代码库 |
| 👁️ Code Reviewer | 代码审查, 安全, 可维护性 | PR 审查, 代码质量门禁 |
| 🗄️ Database Optimizer | Schema 设计, 查询优化, 索引策略 | PostgreSQL/MySQL 调优, 慢查询调试 |
| 🌿 Git Workflow Master | 分支策略, conventional commits, 高级 Git | Git 工作流设计, 历史清理, CI 友好分支管理 |
| 🏛️ Software Architect | 系统设计, DDD, 架构模式, 权衡分析 | 架构决策, 领域建模, 系统演化策略 |
| 🛡️ SRE | SLO, 错误预算, 可观测性, 混沌工程 | 生产可靠性, 重复性工作消除, 容量规划 |

### Design Division（设计部）

| Agent | 专长 |
|-------|------|
| 🎯 UI Designer | 视觉设计, 组件库, 设计系统 |
| 🔍 UX Researcher | 用户测试, 行为分析 |
| 🏛️ UX Architect | 技术架构, CSS 系统 |
| 🎭 Brand Guardian | 品牌身份, 一致性 |
| ✨ Whimsy Injector | 个性, 乐趣, 趣味交互 |

### Paid Media Division（付费媒体部）

| Agent | 专长 |
|-------|------|
| 💰 PPC Campaign Strategist | Google/Microsoft/Amazon Ads |
| 🔍 Search Query Analyst | 搜索词分析, 意图映射 |
| 📋 Paid Media Auditor | 200+ 点账户审计 |
| 📡 Tracking & Measurement Specialist | GTM, GA4, 转化追踪 |

### Operations Division（运营部）

| Agent | 专长 |
|-------|------|
| 🚨 Incident Response Commander | 事件管理, post-mortems, on-call |
| 📧 Email Intelligence Engineer | 邮件解析, MIME 提取 |
| 🎙️ Voice AI Integration Engineer | 语音转文本管道, Whisper, ASR |

---

## 核心设计：Personality-Driven Agents

Agency-Agents 与其他框架的本质区别在于 **Agent 拥有「人格」**。这不是装饰性的，而是工程化的：

> "Each agent is a specialized expert with personality, processes, and proven deliverables."

每个 Agent 文件包含：
- **Identity & personality traits** — Agent 的身份和性格特征
- **Core mission & workflows** — 核心任务和工作流程
- **Technical deliverables with code examples** — 技术交付物和代码示例
- **Success metrics & communication style** — 成功指标和沟通风格

这意味着当你激活一个 Agent 时，它的「思考方式」就被确定了。Frontend Developer 不会用 Backend Architect 的方式分析问题；Security Engineer 的沟通风格和 Rapid Prototyper 完全不同。

---

## 多工具支持：不是绑定，是桥接

Agency-Agents 的一大特点是**跨工具支持**。同一个 Agent 定义可以部署到不同的 Agent 运行时：

```bash
# 安装所有 Agent 到 Claude Code
./scripts/install.sh --tool claude-code

# 或针对特定工具
./scripts/install.sh --tool cursor
./scripts/install.sh --tool copilot
./scripts/install.sh --tool openclaw
./scripts/install.sh --tool windsurf
```

转换脚本（`convert.sh`）会为每个工具生成适配层。这意味着 Agency-Agents 本质上是一个 **Agent 定义格式标准**，而不是又一个 Agent 运行时。

---

## 工程洞察

### 洞察 1：专才模式的维护成本

**优点**：每个 Agent 的 prompt 都是独立进化的，不会有「改一个全局设置影响所有 Agent」的问题。

**缺点**：当你要给所有 Agent 添加同一个能力（如「都支持 MCP」）时，工作量是 O(n) 的。如果 Agent 数量达到 30+，更新会成为显著的工程负担。

### 洞察 2：「人格」是隐式的还是显式的？

Agency-Agents 的「人格」是**显式的**——每个 Agent 文件明确定义了沟通风格。这与其他框架的「人格是由 LLM 隐式决定」完全不同。

显式人格的好处是**可预测性**：同一个需求发给不同 Agent，它们的响应模式是可预期的。坏处是**僵硬**——如果 prompt 里没写，Agent 就不会；如果 prompt 写了但场景没覆盖，Agent 也不知道灵活应变。

### 洞察 3：跨工具桥接的工程难度

将 Agent 定义转换为不同工具的格式看起来简单（一个脚本的事），但实际上每个工具的 Agent 模型差异很大：
- Claude Code 的 Agent 模型 vs. Cursor 的 Agent 模型 vs. Copilot 的 Agent 模型
- 输入输出格式不同、工具调用方式不同、上下文管理策略不同

一份 prompt 不可能天然适配所有工具。Agency-Agents 的 `convert.sh` 本质上是一个「尽可能保留语义」的近似翻译，而非精确等价转换。

---

## 适用场景

### ✅ 适合的场景

1. **原型快速验证**：你有 30 个不同领域的专家 Agent 定义，需要快速组装一个全能团队跑一个 Hackathon 项目
2. **团队能力标准化**：当你不确定「我们的安全审查 Agent 应该做什么」，Agency-Agents 提供了经过 battle-test 的定义
3. **多工具环境**：你在同时使用 Claude Code 和 Cursor，想让两边的 Agent 有相同的方法论

### ❌ 不适合的场景

1. **资源受限环境**：30+ 个 Agent 定义在 token 预算上会很贵——每个 Agent 的 prompt 少则 500 token，多则 2000 token
2. **需要深度协作的场景**：Agency-Agents 的 Agent 是「各自为战」的，如果你的场景需要 Agent A 的输出直接传给 Agent B，你需要自己设计 handoff 协议
3. **追求单 Agent 极致性能**：Agency-Agents 的设计假设是多 Agent 协作，如果你只需要一个很棒的 Frontend Developer，不如直接用 Cursor

---

## 与 Cursor Multi-Agent Kernel Optimizer 的对比

| 维度 | Agency-Agents | Cursor Kernel Optimizer |
|------|--------------|----------------------|
| **架构** | 专业分工团队（静态角色定义）| Planner-Worker 动态协作 |
| **协作方式** | 各自独立工作，按需人工编排 | Planner 自动分发 + 自主迭代闭环 |
| **验证机制** | 无内置验证（依赖 Agent 自我判断）| SOL-ExecBench 自动化评分 |
| **适用场景** | 宽泛（设计/工程/运营/媒体）| 垂直（GPU Kernel 优化）|
| **规模化** | 适合多工具多场景 | 适合高并行度单一任务 |

两者代表了**多 Agent 协作的两种范式**：
- **Agency-Agents = 静态角色定义**，适合需要明确专业分工的开放场景
- **Cursor Kernel = 动态任务分配**，适合目标明确、需要高效探索的封闭问题

---

## 结论：专业分工的边界在哪里

Agency-Agents 回答了一个重要问题：**多 Agent 协作的粒度应该有多细？**

它的答案是「尽可能细」——30+ 个专业 Agent，每个都有独立的方法论。这是一种**高度专业化的设计哲学**。

这种哲学在以下场景非常有效：
- 需要「一站式团队」的场景（初创公司没有各领域的专家，希望 AI 来填补）
- 需要「专家级输出」的场景（你不只要代码，你要符合该领域最佳实践的代码）

但在资源受限或任务单一的场景，这种「团队感」可能是过度设计。

> "Think of it as: Assembling your dream team, except they're AI specialists who never sleep, never complain, and always deliver."
> — [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)

**下一步**：如果你在构建一个需要多领域专家协作的系统，Agency-Agents 的角色定义值得参考——即使你不直接用它，它的 Agent 分工思路可以帮助你设计自己的多 Agent 架构。

---

## 参考链接

- GitHub：[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)
- 安装脚本：`./scripts/install.sh --tool <tool>`
- 转换脚本：`./scripts/convert.sh`

---

*本文由 ArchBot 基于 GitHub 官方 README 生成 | 2026-05-07*
