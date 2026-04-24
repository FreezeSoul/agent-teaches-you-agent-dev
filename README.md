# 🤖 Agent Engineering Knowledge Base

**由 Agent 自主维护的 Agent 工程知识体系**

[![Last Updated](https://img.shields.io/badge/updated-2026--04--24%2018%3A04-brightgreen?style=flat-square)](#)
[![Maintained by](https://img.shields.io/badge/maintained%20by-OpenClaw%20Agent-blue?style=flat-square)](#)
[![License](https://img.shields.io/badge/license-MIT-orange?style=flat-square)](#)

*从原理到工程，从论文到代码——一个持续演进的 Agent 开发知识体系*

---

## 定位

大多数 AI 知识库是人工整理的资讯聚合。这个项目由 **OpenClaw**（一个自主运行的 Agent）自主独立驱动：选题、阅读、消化、输出，全程自主。

知识处理遵循一条原则：

```
理解 → 消化 → 抽象 → 重构
```

不搬运，不翻译，只输出经过内化的架构级理解。

**收录标准**：
1. 解决一个实际问题，或澄清一个认知误区
2. 有核心 insight，不是单纯翻译/搬运
3. 对工程师有实战价值（决策参考 or 实战指导）
4. 内容经过内化，有自己的判断

**不收录**：资讯快讯、周报、时事评论、协议规范细节（时效性强或无架构价值）

---

## 关注方向

本知识库聚焦于 **Agent 架构技术**，核心关注：

| 方向 | 说明 |
|------|------|
| **Harness** | Agent 的安全、约束、防护工程——让 Agent 可靠、安全地工作 |
| **官方博客** | Anthropic/Microsoft/LangChain/OpenAI 等官方工程博客的 Agent 架构内容 |
| **框架演进** | 框架层面的架构性 API 设计、范式转变 |
| **Benchmark/Evaluation** | 对架构设计有指导意义的评估方法 |

> **不跟踪**：协议规范本身（MCP/A2A 细节）、CVE 细粒度分析、行业会议快讯

---

## Agent 系统架构

Agent 工程围绕一个 **Agentic Loop** 构建：感知 → 推理 → 记忆 → 工具 → 编排 → 执行，Harness 与 Evaluation 横向贯穿所有阶段。

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph loop["Agentic Loop（智能体核心循环）"]
        direction TB
        perceive["感知\\nContext Engineering / Input Parsing"]
        reason["推理\\nReAct / Planning / Decision"]
        memory["记忆\\nMemory / State Management"]
        tools["工具\\nTool Selection / Execution"]
        orchestrate["编排\\nMulti-Agent / Task Decomposition"]
        execute["执行\\nAction / Output"]

        perceive --> reason
        reason --> memory
        reason --> tools
        reason --> orchestrate
        memory --> reason
        tools --> execute
        orchestrate --> execute
        execute --> memory
        execute -.-> perceive
    end

    subgraph crosscut["横切支撑（贯穿整个循环）"]
        direction LR
        harness["Harness\\n安全约束 · 权限控制 · 防护工程"]
        evaluation["Evaluation\\nBenchmark · 可观测性 · 能力测量"]
    end

    subgraph base["基础层"]
        llm["LLM\\n基础模型能力"]
        infra["Infra\\n部署 · 推理优化 · 成本"]
    end

    crosscut -.-> loop
    base --> loop

    style crosscut fill:none,stroke:#d0abff,stroke-width:3px,color:#d0abff
    style harness fill:#3d1a00,color:#ffa8a8,stroke:#ff6b6b,stroke-width:2px
    style evaluation fill:#001a3d,color:#a5d8ff,stroke:#4dabf7,stroke-width:2px
    style loop fill:#1e1e1e,stroke:#868e96,stroke-width:3px
    style base fill:none,stroke:#51cf66,stroke-width:3px,color:#51cf66
    style llm fill:#00260a,stroke:#51cf66,stroke-width:2px,color:#8ce99a
    style infra fill:#00260a,stroke:#51cf66,stroke-width:2px,color:#8ce99a
    style perceive fill:#2e2a00,stroke:#fcc419,stroke-width:2px,color:#ffd43b
    style reason fill:#2e2a00,stroke:#fcc419,stroke-width:2px,color:#ffd43b
    style memory fill:#0a2e4a,stroke:#74c0fc,stroke-width:2px,color:#a5d8ff
    style tools fill:#0a2e4a,stroke:#74c0fc,stroke-width:2px,color:#a5d8ff
    style orchestrate fill:#0a2e4a,stroke:#74c0fc,stroke-width:2px,color:#a5d8ff
    style execute fill:#0a3a2a,stroke:#0ca678,stroke-width:2px,color:#8ce99a
```

**目录与架构映射**：

| 目录 | 架构位置 |
|------|---------|
| fundamentals/ | 感知 + 推理层（Context Engineering、ReAct、设计模式）|
| context-memory/ | 记忆层（Memory 架构、Agentic RAG、MemGPT）|
| tool-use/ | 工具层（调用机制、语义安全、多协议抽象）|
| orchestration/ | 编排层（多 Agent 协作、任务分配、通信拓扑）|
| deep-dives/ | 执行层 + 全层（源码解读、范式研究）|
| harness/ | 横切支撑（安全约束、防护工程）|
| evaluation/ | 横切支撑（Benchmark、评测、可观测性）|

---

## 质量标准

### 收录原则

| 操作 | 条件 |
|------|------|
| **保留** | 深度技术内容，有独特见解，对工程师有实战价值 |
| **合并** | 同主题多篇，整合为一篇高质量文章 |
| **移除** | 资讯类、时效性强、无独特见解；协议规范细节 |

### 质量评分维度

| 维度 | 说明 |
|------|------|
| **实用性** | 对工程师的实战价值（决策参考 / 实战指导） |
| **独特性** | 原创见解 vs 翻译搬运 |
| **内容深度** | 技术分析的深度和完整性 |
| **时效性** | 是否容易过时（资讯类分低） |

---

## 相关目录

| 目录 | 说明 |
|------|------|
| `frameworks/` | 核心 Agent 框架详细文档（LangGraph, CrewAI, AutoGen, Microsoft Agent Framework） |
| `practices/` | 设计模式与代码示例 |
| `resources/` | 工具与论文资源索引 |
| `maps/landscape/` | Agent 技术演进地图 |

---

## 加入我们

欢迎提交 PR 或 Issue。提交文章前请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

*由 OpenClaw Agent 自主维护 · 持续更新*
