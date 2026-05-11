# google/agents-cli：把任意 Coding Agent 变成 Google Cloud Agent 专家

> 「第三代」云端 Agent 工厂的标准配置工具——让 Claude Code/Codex/Gemini CLI 原生理解 Google Cloud 的 Agent 部署、评估和可观测性。

## 一句话定义

google/agents-cli 是一个 **Google Cloud 原生的 Agent 开发 CLI + Skill 库**，通过模块化的 Skill 体系（6 个核心 Skill）给任意 Coding Agent 赋能，使其能够端到端地构建、评估和部署生产级 Agent 到 Google Cloud，而不需要人类开发者理解每一个 CLI 和服务的细节。

**场景锚定**：当你需要把一个在本地跑通的 Agent（Claude Code / Codex / Gemini CLI）部署到 Google Cloud 并建立完整的评估和可观测性体系时，agents-cli 是那个「让 Agent 自己学会做这件事」的工具。

**差异化标签**：唯一由 Google 官方提供的跨平台 Agent 部署工具（支持 Claude Code / Codex / Gemini CLI），且 Skill 可复用、可组合。

---

## 为什么这值得关注：核心洞察

### 1. Skill 是 Agent 时代的「环境变量」

agents-cli 的架构核心不是 CLI，而是 **Skill**——一种可被任意 Coding Agent 发现和加载的能力模块。每个 Skill 对应 Agent 开发生命周期的一个环节：

| Skill | 功能 | Agent 学会后能做什么 |
|-------|------|---------------------|
| `google-agents-cli-workflow` | 开发生命周期、代码保留规则、模型选择 | 理解 Agent 开发的标准流程 |
| `google-agents-cli-adk-code` | ADK Python API（agents/tools/ored/ callbacks/state） | 理解 Google ADK 框架 |
| `google-agents-cli-scaffold` | 项目脚手架（创建/增强/升级） | 从零生成合规 Agent 项目 |
| `google-agents-cli-eval` | 评估方法论（metrics/evalsets/LLM-as-judge/trajectory scoring） | 建立 Agent 质量评估体系 |
| `google-agents-cli-deploy` | 部署（Agent Runtime/Cloud Run/GKE/CI-CD/secrets） | 一键部署到 Google Cloud |
| `google-agents-cli-publish` | Gemini Enterprise 注册 | 让 Agent 学会「发布」这件事 |
| `google-agents-cli-observability` | 可观测性（Cloud Trace/logging/第三方集成） | 建立 Agent 运行监控 |

这直接对应了 Cursor「第三代」文章的核心预言：**当 Agent 负责大部分工作时，人类需要做的是「装备」Agent，而非「手把手」指导 Agent**。Skill 就是这个装备体系的标准格式。

### 2. 跨 Agent 兼容性：一场标准格式的胜利

agents-cli 官方宣称支持 Claude Code、Codex、Gemini CLI 和「any other coding agent」。这意味着：

- **不是**为每一个 Agent 单独开发部署工具
- **而是**让所有主流 Coding Agent 都能通过 Skill 接口调用同一个部署能力

这个设计背后的逻辑是：Skill 格式（SKILL.md + 执行脚本）已经成了 Agent 工具扩展的事实标准——正如 npm package 之于 Node.js。agents-cli 的 7 个 Skill 相当于 Google Cloud 为 Agent 生态发布了一组「官方 npm packages」，任何实现 Skill 接口的 Agent 都可以无缝使用。

### 3. 「本地优先，部署可选」的设计哲学

agents-cli 文档中明确说明：

> "For local development (create, run, eval), no — you can use an AI Studio API key to run Gemini with ADK locally. For deployment and cloud features, yes."

这意味着 **agents-cli 的 CLI 部分完全可以在本地使用**（不需要 Google Cloud 账号），只有部署和云端功能才需要 GCP 认证。这个设计降低了入门门槛，让 Agent 开发者可以在本地完整测试整个开发-评估流程，然后按需部署到云端。

---

## 技术深度：agents-cli 的架构设计

### 3.1 完整的 Agent 开发生命周期覆盖

从官方文档看，agents-cli 覆盖了 Agent 开发的完整链路：

```
scaffold (创建) → run (本地运行) → eval (评估) → deploy (部署) → publish (发布)
```

每个步骤都有对应的 CLI 命令和 Skill 支持：

```bash
# 从零创建一个合规 Agent 项目
agents-cli scaffold my-agent

# 本地开发和调试
agents-cli run "让 Agent 帮我构建一个客服 Agent"

# 运行评估
agents-cli eval run

# 部署到 Google Cloud
agents-cli deploy

# 增强已有项目（添加部署/CI-CD/RAG）
agents-cli scaffold enhance
```

### 3.2 Skill 的「即插即用」机制

agents-cli 支持两种使用方式：

**方式一：直接安装完整 CLI**
```bash
uvx google-agents-cli setup
```
这会安装 CLI 和所有 Skill 到本地，Agent 通过环境变量发现它们。

**方式二：仅安装 Skill（让 Agent 处理其余部分）**
```bash
npx skills add google/agents-cli
```
这会下载 Skill 定义文件，Agent 启动时自动加载。

### 3.3 与 Google ADK 的关系

agents-cli 不是 Google ADK（Agent Development Kit）的替代品，而是 ADK 的「Agent 友好包装」：

> "ADK is an agent framework. agents-cli gives your coding agent the skills and tools to build, evaluate, and deploy ADK agents end-to-end."

这意味着：
- ADK 是给人类开发者用的 Python 框架
- agents-cli 是给 Coding Agent 用的「部署和评估工具包」

两者互补，共同构成了 Google Cloud 的 Agent 开发体验。

---

## 社区健康度与竞品对比

### GitHub 数据（截至 2026-05-11）

| 指标 | 数值 |
|------|------|
| Stars | **2,272** |
| 官方支持 | ✅ Google 官方 |
| 维护活跃度 | 持续更新（Pre-GA） |
| 文档完整性 | 完整文档 + YouTube 教程 |

### 竞品对比

| 项目 | 类型 | 支持的 Agent | 部署目标 | Stars |
|------|------|-------------|----------|-------|
| **google/agents-cli** | 官方 CLI + Skills | Claude Code / Codex / Gemini CLI / any | Google Cloud (ADK/Cloud Run/GKE) | 2,272 |
| Cursor Cloud Agents | 闭源 SaaS | Cursor 专用 | Cursor 云 | N/A |
| Anthropic Managed Agents | 托管服务 | Claude 专用 | Anthropic 云 | N/A |
| stainlu/openclaw-managed-agents | 开源替代 | 任意模型 | 任意云 | 406 |

**差异化**：
- agents-cli 是唯一一个**官方、跨平台、支持多 Agent**的部署工具链
- 2,272 stars 远超同类开源替代（openclaw-managed-agents 406 stars）

---

## 快速上手：3 步跑起来

### 前置要求
- Python 3.11+
- uv（Astral 的 Python 包管理器）
- Node.js

### Step 1：安装（一条命令）
```bash
uvx google-agents-cli setup
```

### Step 2：启动 Agent，让它学会使用 agents-cli
```bash
# 启动你偏好的 Agent
claude  # 或 codex / gemini

# 问它：
> "Use agents-cli to build a caveman-style agent that compresses 
   verbose text into terse, technical grunts"
```

### Step 3：部署到 Google Cloud
```bash
agents-cli login
agents-cli scaffold my-agent
agents-cli eval run
agents-cli deploy
```

---

## 适合谁：TRIP 定位

**Target（目标用户）**：
- 有一定 Agent 开发经验，想把 Agent 部署到生产环境的开发者
- 需要在 Google Cloud 上建立 Agent 评估和可观测性体系的企业团队
- 想让 Claude Code/Codex 原生理解 Google Cloud 部署细节的工程师

**不适合**：
- 只需要本地原型开发的 Agent（直接用 ADK 就够了）
- 目标是 AWS/Azure 的 Agent 部署（需要对应的云工具）
- 完全不想接触云端、只需要本地运行的场景

---

## 为什么这与「第三代」文章完美互补

Cursor 的「第三代」文章描述了**云端 Agent 工厂范式**的兴起——Agent 在云端 VM 并行运行，交付 Artifacts 而非 Diffs，人类从「每步指导」变成「定义问题和验收标准」。

**agents-cli 正是这个工厂范式的具体实现工具**：

| 第三代的核心特征 | agents-cli 的对应实现 |
|----------------|---------------------|
| Cloud VM 执行环境 | 部署到 Cloud Run/GKE/Agent Runtime |
| 并行多 Agent | agents-cli scaffold + eval run 可批量处理 |
| 长程异步任务 | deploy 支持完整的 CI/CD 流程 |
| Artifact 交付 | eval 输出结构化评估报告（metrics/trajectory） |
| 质量门禁 | agents-cli eval 提供的 LLM-as-judge 评估体系 |
| 装备 Agent 而非手把手 | 7 个 Skill = 给 Agent 的装备库 |

换句话说：**Cursor 告诉你第三代是什么，agents-cli 告诉你怎么在 Google Cloud 上实现第三代**。

---

## 参考来源

> "agents-cli gives your coding agent the skills and commands to build, scale, govern, and optimize enterprise-grade agents — so you don't have to learn every CLI and service yourself." — [google/agents-cli README](https://github.com/google/agents-cli), Google, 2026

> "Works seamlessly with: Gemini CLI • Claude Code • Codex • Antigravity • and any other coding agent." — [google/agents-cli README](https://github.com/google/agents-cli), Google, 2026

> "agents-cli is a tool for coding agents, not a coding agent itself. It provides the CLI commands and skills that make your coding agent better at building, evaluating, and deploying ADK agents on end-to-end." — [google/agents-cli FAQ](https://github.com/google/agents-cli), Google, 2026

> "For local development (create, run, eval), no — you can use an AI Studio API key to run Gemini with ADK locally. For deployment and cloud features, yes." — [google/agents-cli README](https://github.com/google/agents-cli), Google, 2026