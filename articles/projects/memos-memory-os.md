# MemOS：LLM 和 AI Agent 的记忆操作系统

## 项目概述

**MemOS**（Memory Operating System）是 MemTensor 团队开源的 LLM 记忆操作系统，目标是为 LLM 和 AI Agent 提供统一的记忆管理能力——**存储、检索、管理一体化**，实现跨任务的上下文感知和个性化交互。

当前 Stars：8,813。已有配套论文发表在 ArXiv（arXiv:2507.03724）。

当前与 OpenClaw（moltbot、clawdbot、openclaw）有官方集成插件。

## 核心设计

### 统一记忆 API

一套 API 完成记忆的添加、检索、编辑、删除——底层以图结构存储，可检视和编辑，不是黑盒式的向量存储。

### 多模态记忆

原生支持文本、图片、工具调用轨迹（tool traces）、人格（personas），在统一记忆系统中共同检索和推理。

### Multi-Cube 知识库管理

将多个知识库作为可组合的「记忆立方体」（Memory Cube）管理，支持用户级、项目级、Agent 级的隔离和受控共享。

### MemScheduler

异步调度系统，基于 Redis Streams 提供毫秒级延迟的内存操作，支持生产环境高并发下的稳定性。

### 记忆反馈与修正

用自然语言反馈精化记忆——修正、补充或替换已有记忆内容，而非只能追加。

## 部署方式

- **云服务**：通过 [MemOS Dashboard](https://memos-dashboard.openmem.net/) 获取 API Key，支持 OpenAI、Azure OpenAI、Qwen、DashScope、DeepSeek、MiniMax、Ollama、HuggingFace、vLLM 等后端
- **自托管**：Docker 一键部署，依赖 Neo4j（图数据库）和 Qdrant（向量数据库）

## 与 OpenClaw 的集成

MemOS 提供了完整的 OpenClaw 插件：
- **云插件**：72% token 节省，多 Agent 记忆共享
- **本地插件**：SQLite 存储，FTS5 + 向量搜索，任务自动摘要，技能演进

## 局限

- 部署依赖 Neo4j + Qdrant，自托管运维有一定复杂度
- 图数据库设计在超大规模记忆场景下的性能表现需要验证
- 记忆的质量和检索效果高度依赖嵌入模型的选择

## 一句话推荐

MemOS 为 AI Agent 的长期记忆问题提供了一个系统化的解决方案，其图结构记忆模型和统一 API 设计值得在 Agent 架构中认真考虑——特别适合需要多 Agent 共享记忆和企业级知识管理的场景。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/MemTensor/MemOS`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：8/15
