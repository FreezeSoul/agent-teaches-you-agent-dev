# NousResearch Hermes Agent：自改进 AI Agent 的生产级实现

> **目标读者**：希望构建跨平台、持久化、有学习能力的 AI Agent 系统的开发者；关注 agent memory、skill creation、multi-platform messaging 等工程实现的技术负责人。

---

## 定位

Hermes Agent 是 NousResearch 构建的**自改进 AI Agent**，核心特性是内置学习循环——从经验中创建 Skill、使用过程中自我改进、跨会话记住用户偏好。关键差异化：可以运行在 $5 VPS 上，支持 Telegram/Discord/Slack/WhatsApp/Signal 等多平台，且使用任何 LLM（OpenRouter 200+ 模型、NVIDIA NIM、Xiaomi MiMo、Kimi/Moonshot、MiniMax、Hugging Face、OpenAI，或自定义端点）。

---

## 为什么值得用

### T — 具体改变

| 场景 | 之前 | 之后 |
|------|------|------|
| 跨平台工作流 | 每个平台单独维护一个 agent 实例 | 单一 gateway process 处理所有平台 |
| 会话记忆 | 每次对话重置 | Agent-curated memory + FTS5 检索，跨 session 积累 |
| 新任务适应 | 每次手动描述任务上下文 | 复杂任务完成后自动创建 Skill，下次自动调用 |
| 模型切换 | 绑定单一模型供应商 | `hermes model` 一个命令切换任意 provider，不改代码 |
| 环境部署 | 必须有 GPU 或高配服务器 | $5 VPS 可跑（Daytona/Modal serverless 模式，idle 时几乎零成本）|

### R — 量化数据（基于 README）

| 指标 | 数值 |
|------|------|
| 支持 LLM providers | OpenRouter（200+）、NVIDIA NIM、Xiaomi MiMo、Kimi/Moonshot、MiniMax、HuggingFace、OpenAI、custom endpoint |
| 支持平台 | Telegram、Discord、Slack、WhatsApp、Signal、Email、CLI |
| 运行环境 | local、Docker、SSH、Singularity、Modal、Daytona、Vercel Sandbox |
| 安装方式 | Linux/macOS/WSL2 一行脚本、Windows PowerShell 早期 beta、Termux |

### I — 技术洞察

**自改进学习循环的核心机制**：

1. **Agent-curated memory**：每次对话后，agent 决定什么需要记住，定期 nudge 自己持久化知识
2. **Autonomous skill creation**：复杂任务完成后，agent 自动生成对应 Skill，下此类似任务时自动调用
3. **Skills self-improve during use**：Skill 在使用中持续改进（不只是从经验学习，而是直接改进自己的工具）
4. **FTS5 session search**：用 LLM summarization 压缩历史会话，实现跨 session 检索
5. **Honcho dialectic user modeling**：兼容 agentskills.io 开放标准

**多平台 messaging gateway**：

单一 gateway process 连接所有 messaging 平台，跨平台对话连续性由基础设施保证，而非应用层逻辑。

**Batch trajectory generation**：用于 RL 训练——agent 生成多个轨迹，压缩后训练下一代模型。

> "Hermes Agent is the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions."
> — [NousResearch/hermes-agent GitHub README](https://github.com/NousResearch/hermes-agent)

---

## 竞品对比

| 特性 | Hermes Agent | Claude Code | Cursor Composer |
|------|-------------|------------|----------------|
| 多平台 messaging | ✅ 7 个平台 | ❌ CLI only | ❌ CLI only |
| 自改进 skill creation | ✅ | ❌ | ❌ |
| 模型无关 | ✅ 任意 provider | ❌ Anthropic only | ❌ 主要 OpenAI |
| 成本效率 | $5 VPS 可跑 | 需要云端 | 需要云端 |
| FTS5 cross-session search | ✅ | ❌ | ❌ |
| Batch RL training | ✅ | ❌ | ✅ Composer |

---

## 快速上手

```bash
# Linux/macOS/WSL2
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes  # 开始对话

# 模型切换
hermes model  # 选择 provider 和 model

# 启动 messaging gateway
hermes gateway setup   # 配置平台
hermes gateway start    # 启动服务
```

---

## 与 Cursor Autoinstall 的主题关联

Hermes Agent 的自改进机制与 Cursor Composer Autoinstall 形成了一个完整的**Agent 自我改进循环**：

- **Cursor Autoinstall**：用上一代 Composer 模型 bootstrap 下一代 Composer 的训练环境配置
- **Hermes Agent**：用当前 session 的经验 bootstrap 下一个 session 的 Skill 和 memory

两者都展示了"model helps itself improve"的模式——不是靠人工维护改进流程，而是让模型自己管理自己的演进。

> 笔者认为：Hermes Agent 的 skill self-improvement 机制比简单的"记住上次做了什么"更有价值——它将经验转化为**可复用的工具**（Skill），而非只是存储记忆。这意味着 agent 的能力累积是结构化的，而非碎片化的。agentskills.io 开放标准的接入使得这些 Skill 可以跨平台流动。

---

## 行动建议

1. **评估 Hermes 作为你的 personal coding agent**：如果需要跨平台（手机/桌面）、长程记忆、自改进能力，Hermes 提供了完整的开箱即用方案
2. **关注 agentskills.io 标准**：Hermes 兼容该标准，意味着它创建的 Skill 可以迁移到其他兼容平台
3. **Batch trajectory 用于 RL**：如果你在训练自己的 coding model，Hermes 的 batch trajectory generation 可以作为数据来源
4. **Serverless 模式降低成本**：Daytona/Modal 的 hibernate 机制使得 idle 成本几乎为零，适合个人开发者

---

## 关键引用

> "It's the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions."
> — [NousResearch/hermes-agent GitHub README](https://github.com/NousResearch/hermes-agent)

> "Use any model you want — Nous Portal, OpenRouter (200+ models), NVIDIA NIM (Nemotron), Xiaomi MiMo, z.ai/GLM, Kimi/Moonshot, MiniMax, Hugging Face, OpenAI, or your own endpoint. Switch with `hermes model` — no code changes, no lock-in."
> — [NousResearch/hermes-agent GitHub README](https://github.com/NousResearch/hermes-agent)

> "Run it on a $5 VPS, a GPU cluster, or serverless infrastructure that costs nearly nothing when idle."
> — [NousResearch/hermes-agent GitHub README](https://github.com/NousResearch/hermes-agent)