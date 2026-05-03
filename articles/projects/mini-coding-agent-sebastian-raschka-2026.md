# mini-coding-agent：精简至极的 Coding Agent 入门级 Harness 实现

> **来源**：[rasbt/mini-coding-agent](https://github.com/rasbt/mini-coding-agent) · GitHub · Stars: 793 · Forks: 151
>
> **许可证**：MIT · **语言**：Python · **创建于**：2026-04-02 · **更新于**：2026-05-03
>
> **作者**：Sebastian Raschka（[Lightning AI](https://lightning.ai/) Research Scientist）
>
> **配套文章**：[Components of a Coding Agent](https://magazine.sebastianraschka.com/p/components-of-a-coding-agent)（[Sebastian Raschka's AI Newsletter](https://magazine.sebastianraschka.com/)）

---

## 一句话概括

**一份约 500 行代码的极简 Python 实现，展示 Coding Agent 的 6 个核心构建块：Repo Context、Prompt Cache、Structured Tools、Context Reduction、Memory/Transcript、Delegation —— 适合作为理解生产级 Harness 工程原理的教学级参考。**

---

## 核心定位

mini-coding-agent **不是**生产级框架，而是**教学级参考实现**。

作者 Sebastian Raschka（Lightning AI 研究科学家，AI 教育者）明确指出：

> "Minimal and readable coding agent harness implementation in Python to explain the core components of coding agents."

目标是**拆解核心组件，帮助理解原理**，而非提供生产级功能。

---

## 六大核心组件

### 1. Live Repo Context（实时仓库上下文）

```
Agent 启动时 → 收集 repo layout、instructions、git state
               → 作为稳定的 prompt 前缀
```

### 2. Prompt Cache（Prompt 缓存）

将 prompt 分为三个部分，只有动态部分（transcript、memory）每次变化，静态部分（system prefix）可缓存复用：

```
┌────────────────────┐
│ Stable System Prep │  ← 可缓存
├────────────────────┤
│ Changing Transcript│  ← 动态
├────────────────────┤
│ Working Memory      │  ← 动态
└────────────────────┘
```

### 3. Structured Tools（结构化工具）

不依赖自由形式的工具调用，而是通过**命名工具 + 输入校验 + 路径验证 + 审批门**来约束 Agent 行为。

### 4. Context Reduction（上下文缩减）

长输出自动裁剪、重复读取去重、旧 transcript 条目压缩，确保 prompt 长度可控。

### 5. Transcript + Memory（会话记录 + 记忆）

运行时维护两个持久化存储：
- **Full Transcript**：完整会话记录，支持回放
- **Working Memory**：精简后的工作记忆，支持会话恢复

### 6. Bounded Delegation（有界委托）

子任务委托给辅助 Agent，继承足够上下文，但在限定范围内运行，防止无限循环。

---

## 架构图

```
┌──────────────────────────────────────────────────┐
│           mini-coding-agent 运行时                 │
│                                                  │
│  ┌────────────┐    ┌────────────┐                │
│  │ Repo       │───▶│ Prompt     │                │
│  │ Context    │    │ Constructor│                │
│  └────────────┘    └────────────┘                │
│                          ↓                        │
│  ┌────────────┐    ┌────────────┐    ┌─────────┐ │
│  │ Ollama     │◀───│ Tool       │───▶│ Approval│ │
│  │ Backend    │    │ Executor   │    │ Gate    │ │
│  └────────────┘    └────────────┘    └─────────┘ │
│                          ↓                        │
│  ┌────────────┐    ┌────────────┐                │
│  │ Transcript │    │ Context    │                │
│  │ Logger     │    │ Reducer    │                │
│  └────────────┘    └────────────┘                │
└──────────────────────────────────────────────────┘
```

---

## 与其他项目的关系

| 项目 | 定位 | 与 mini-coding-agent 的关系 |
|------|------|---------------------------|
| **Claude Code** | 生产级 Harness | 参考 mini-coding-agent 理解底层原理 |
| **agentic-stack** | 便携式 Harness 基础设施 | 互补：mini-coding-agent 是原理教学，agentic-stack 是生产可用实现 |
| **Everything Claude Code** | Claude Code 全方位分析 | 互补：mini-coding-agent 解释「为什么这样设计」，Everything Claude Code 展示「生产系统如何实现」 |

---

## 关键数字

| 指标 | 数值 |
|------|------|
| GitHub Stars | 793 |
| Forks | 151 |
| 代码行数 | ~500 行（教学级精简） |
| Python 版本 | 3.10+ |
| 模型后端 | Ollama（本地） |
| 依赖 | 标准库（无 heavy dependency） |

---

## 适用场景

1. **学习 Agent 架构**：想从底层理解 Coding Agent 的 6 个核心组件如何协作
2. **教学或内部培训**：作为 Agent 开发入门材料，而非直接用于生产
3. **baseline 实现**：基于此代码进行二次开发或对比实验

---

## 原文引用

> "A minimal local agent loop with: workspace snapshot collection, stable prompt plus turn state, structured tools, approval handling for risky tools, transcript and memory persistence, bounded delegation."
> — [README.md](https://github.com/rasbt/mini-coding-agent)

---

## 延伸阅读

- [Claude Code 质量回退事件深度复盘：三次变更如何瓦解一个生产级 Agent](articles/harness/claude-code-april-2026-postmortem-three-changes-2026.md)
- [agentic-stack —— 跨 Harness 的便携式 Memory + Skills 基础设施](articles/projects/agentic-stack-portable-agent-folder-2026.md)
- [Anthropic Agent Skills —— 让通用 Agent 获得专业能力的架构设计](articles/fundamentals/anthropic-agent-skills-architecture-deep-dive-2026.md)
