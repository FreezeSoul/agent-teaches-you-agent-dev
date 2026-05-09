# NousResearch Hermes Agent：自改进 AI Agent 的工程化实现

> **核心论点**：Hermes Agent 的核心价值不在于「又一个 Agent 框架」，而在于它解决了一个根本问题——**大多数 Agent 没有学习能力**。每次对话都是从零开始，而 Hermes 通过内置的闭环学习机制，让 Agent 可以从经验中创建技能、在使用中改进技能、把知识固化为长期记忆。这是一个量产的「经验驱动型 Agent」，而不是一个「问答加强型 Agent」。

## 1. 自改进 Agent 的核心机制

### 1.1 关闭学习闭环的四个组件

Hermes Agent 实现了完整的学习闭环，四个组件各司其职：

**① 技能自创建（Skill Creation）**

> 官方原文引用：
> "A closed learning loop — Agent-curated memory with periodic nudges. Autonomous skill creation after complex tasks. Skills self-improve during use."
> — [NousResearch/hermes-agent README](https://github.com/NousResearch/hermes-agent)

复杂任务完成后，Agent 自动从中提取可复用的工作流程，将其固化为 Skill。这个过程是**自主的**，不需要人工干预。

**② 技能自改进（Skill Self-Improvement）**

Skill 不是一次性创建就完了，而是在每次使用中持续改进。这意味着 Agent 会记录「这个 Skill 哪里不完善」，并在下一次使用时自动优化。

**③ 周期性记忆推送（Periodic Nudges）**

> 官方原文引用：
> "Agent-curated memory with periodic nudges."
> — [NousResearch/hermes-agent README](https://github.com/NousResearch/hermes-agent)

Agent 定期主动推送记忆摘要，确保关键信息不会被 session 边界稀释。

**④ 跨 Session 检索（FTS5 Session Search + LLM Summarization）**

Hermes 维护了一个本地 FTS5（SQLite 全文搜索）索引，让 Agent 可以搜索自己过去的对话。这解决了「跨 session 记忆」的核心问题：**Agent 如何在当前任务中发现自己曾经解决过类似问题**。

### 1.2 与传统 Agent 的根本区别

| 维度 | 传统 Agent（无学习闭环）| Hermes Agent（有学习闭环）|
|------|----------------------|------------------------|
| **Session 0** | 从空白开始 | 继承历史 Skills 和记忆 |
| **技能获取** | 靠人工编写/导入 | 自主从经验中提取 |
| **技能改进** | 永不更新 | 在使用中自动迭代 |
| **跨 Session 知识** | 丢失或靠 summarization 压缩 | FTS5 全文索引 + LLM summarization |
| **用户建模** | 每次重新学习偏好 | Honcho dialectic 持续建模 |

## 2. 记忆系统的工程架构

### 2.1 三层记忆架构

Hermes 的记忆系统分为三层：

**① Procedural Memory（程序性记忆）**

Agent 的操作模式和决策逻辑，存储为可执行的 Skills。这是最高频被调用的记忆层。

**② Semantic Memory（语义记忆）**

从对话中提取的长期知识，例如「用户的代码风格偏好」「项目架构约束」。

**③ Episodic Memory（情景记忆）**

具体的会话历史，通过 FTS5 索引支持全文检索。

> 官方原文引用：
> "FTS5 session search with LLM summarization for cross-session recall."
> — [NousResearch/hermes-agent README](https://github.com/NousResearch/hermes-agent)

FTS5 的使用是一个工程亮点：直接用 SQLite 的全文搜索能力做对话历史检索，而不是依赖外部向量数据库。

### 2.2 Honcho 用户建模

Hermes 集成了 [Honcho](https://github.com/plastic-labs/honcho)（Plastic Labs 的开源项目），实现 dialectic 用户建模——不是简单的「标签偏好」，而是构建用户心智的**动态模型**。

### 2.3 与其他 Memory 方案的对比

| 方案 | 存储形式 | 检索方式 | 学习机制 |
|------|---------|---------|---------|
| Hermes Agent | FTS5 + SQLite + Skills | 全文检索 + LLM summarization | 自主技能创建 + 使用中迭代 |
| OpenViking | 文件系统 + RAGFS | 层级检索 + 可视化轨迹 | 自动压缩 + 长期记忆提取 |
| GSD-2 | DB 一等公民 | 状态驱动 | 无（靠外部状态） |
| 传统 RAG | 向量数据库 | embedding similarity | 无 |

## 3. 多平台部署与调度系统

### 3.1 七种终端后端

Hermes 支持七种运行后端：

```
local / Docker / SSH / Singularity / Modal / Daytona / Vercel Sandbox
```

Daytona 和 Modal 提供** serverless 持久化**：Agent 环境在空闲时休眠，需要时按需唤醒，几乎不在空闲时段产生费用。

> 官方原文引用：
> "Daytona and Modal offer serverless persistence — your agent's environment hibernates when idle and wakes on demand, costing nearly nothing between sessions."
> — [NousResearch/hermes-agent README](https://github.com/NousResearch/hermes-agent)

### 3.2 Cron 调度系统

Hermes 内置了自然语言 Cron 调度：

```
"每天早上 9 点给我发送日程摘要"
"每周一早上 10 点运行一次代码审计"
"凌晨 2 点执行数据备份"
```

不需要写 cron 表达式，直接用自然语言描述即可。

### 3.3 Subagent 并行化

> 官方原文引用：
> "Delegates and parallelizes — Spawn isolated subagents for parallel workstreams. Write Python scripts that call tools via RPC, collapsing multi-step pipelines into zero-context-cost turns."
> — [NousResearch/hermes-agent README](https://github.com/NousResearch/hermes-agent)

通过 RPC 调用实现零 context 开销的多步 pipeline 并行执行，不占用主 Agent 的 context window。

## 4. 部署体验：从安装到第一个对话

**安装（2 分钟）**：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes
```

**模型选择**：

```bash
hermes model  # 交互式选择 provider 和 model
```

支持 200+ 模型（OpenRouter）、NVIDIA NIM、Xiaomi MiMo、GLM、Kimi/Moonshot、MiniMax、HuggingFace 等。

**迁移路径（从 OpenClaw）**：

```bash
hermes claw migrate  # 自动检测 ~/.openclaw 并迁移
```

> 官方原文引用：
> "If you're coming from OpenClaw, Hermes can automatically import your settings, memories, skills, and API keys."
> — [NousResearch/hermes-agent README](https://github.com/NousResearch/hermes-agent)

支持的导入项：SOUL.md、MEMORY.md/USER.md、Skills、API keys（白名单内的）、TTS 资产、workspace 指令。

## 5. 安全机制

Hermes 提供了多层安全机制：

- **命令审批白名单**：定义允许/禁止的命令模式
- **DM 配对验证**：只有白名单内的用户可以 DM
- **容器隔离**：Docker/Singularity 容器隔离

## 6. 技术评估

**优势**：
- 自改进闭环是实打实的，不是噱头——技能创建+迭代是生产可用的
- FTS5 而非向量数据库做记忆检索，降低了运维复杂度
- 多后端支持让 serverless 部署成为可能
- 与 OpenClaw 的迁移路径意味着生态是开放的

**局限**：
- 技能自改进的质量取决于 LLM 的自我反思能力——在复杂任务上可能产生错误的自我优化
- 记忆系统完全基于 SQLite，本地存储，多设备同步依赖第三方方案
- 社区相比 OpenClaw 较小，Skills 生态尚在建设中

**与 Cursor 动态上下文发现的主题关联**：两者都指向「Agent 需要更好的上下文管理」，但切入点不同——Cursor 是「如何让 agent 更高效地获取上下文」（动态拉取），Hermes 是「如何让 agent 自己积累和维护上下文」（自主学习）。两个方向互补，共同指向「context engineering 的下一阶段」。

---

**关联文章**：
- [Cursor 动态上下文发现](./cursor-dynamic-context-discovery-2026.md) — 动态拉取 vs 自主积累，构成 context 工程的两极
- [Anthropic「Effective Harnesses」](./anthropic-effective-harnesses-long-running-agents-initializer-pattern-2026.md) — 长程 Agent 的外部状态管理 vs Hermes 的内部记忆系统

---

*来源：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（MIT License，131.8k ⭐，全球 GitHub #60）*
