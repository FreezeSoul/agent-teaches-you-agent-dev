# agentmemory：让 AI Coding Agent 拥有持久记忆

> **项目地址**：[rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)  
> **Stars**：Trending（2026-05-13）  
> **标签**：#Memory #ContextManagement #CodingAgents #MCP  

---

## 一句话描述

agentmemory 是一个**为零长上下文窗口外的 AI coding agent 提供持久记忆**的基础设施项目。支持 Claude Code、Cursor、Codex、pi、OpenCode 等所有主流 Agent，通过 Hook/MCP/REST 三种方式接入。

---

## 核心能力

### 95.2% Recall@5 + 92% Token 节省

agentmemory 在知识检索上的基准数据：

| 指标 | 数值 | 含义 |
|------|------|------|
| **Recall@5** | **95.2%** | 检索 top-5 结果中包含正确答案的概率 |
| **Token 节省** | **92%** | 相比将所有历史塞入上下文，节省的 token 量 |
| **MCP Tools** | **51 个** | 通过 Model Context Protocol 暴露的工具数 |
| **Auto Hooks** | **12 个** | 自动触发记忆读写的钩子数 |

### 全 Agent 覆盖

支持：Claude Code、Cursor、Codex CLI、pi、OpenCode、OpenClaw、Hermes、 Gemini CLI，以及任意 MCP 客户端。

### 零外部数据库依赖

agentmemory 本身不需要额外的数据库服务（虽然支持外部 DB 接入），这降低了部署复杂度。

### 实时记忆查看器

提供 iii Console 和实时查看器，可以在 Agent 运行时直接观察其记忆状态。

---

## 技术架构

基于 [iii engine](https://github.com/iii-hq/iii)，实现了：

1. **混合检索**（Hybrid Search）：向量 + 关键词混合
2. **置信度评分**（Confidence Scoring）：每个记忆条目带置信度，过期/低置信记忆自动淘汰
3. **生命周期管理**：记忆有明确的创建→活跃→衰减→删除周期
4. **知识图谱**（Knowledge Graph）：记忆条目之间的关系建模

---

## 与 Anthropic Long-Running Agent 方案的对比

Anthropic 在《Effective Harnesses for Long-Running Agents》中提出的方案是通过**外部化工件**（feature list JSON + claude-progress.txt + git history）来桥接多会话：

| 维度 | Anthropic 方案 | agentmemory |
|------|--------------|-------------|
| **记忆载体** | 文本文件（feature_list.json, progress.txt） | 结构化数据库（iii engine） |
| **检索方式** | Agent 读取文件后自行解析 | 向量+关键词混合检索 |
| **上下文节省** | 依赖文件大小和 Agent 读取策略 | 精确检索，只召回相关内容 |
| **跨 Agent 共享** | 通过文件系统共享（需同步机制） | 通过共享记忆服务器天然共享 |
| **记忆质量度量** | 无 | 置信度评分 + 生命周期管理 |
| **实现复杂度** | 低（纯文本文件） | 中（需接入 Hook/MCP） |

两者解决的是同一个根本问题：**上下文窗口外的工作记忆消失**。Anthropic 选择了"让 Agent 自己写文件记录状态"的方案，agentmemory 则提供了"专业的记忆基础设施"方案。

---

## 适用场景

✅ **适合使用 agentmemory 的场景**：

- 多会话、长周期的大型项目（功能开发周期跨越数天）
- 需要 Agent 之间共享上下文（团队协作场景）
- 希望减少 token 消耗同时保持记忆质量
- 希望对 Agent 的记忆状态有可视化观察能力

⚠️ **可能不需要的场景**：

- 单会话、短周期任务（上下文窗口内能完成）
- 偏好极简方案（纯文本文件方案足够）
- 部署环境不允许额外依赖

---

## Quick Start

```bash
# npm 安装
npm install @agentmemory/agentmemory

# 或 npx 直接运行
npx @agentmemory/agentmemory
```

接入后，Agent 每次会话开始时会自动从记忆服务器恢复相关历史，无需重复解释项目背景。

---

## 与本仓库文章的关联主题

- **Long-Running Agent**：Anthropic 的 initializer pattern 解决的是"如何让 Agent 跨会话不丢上下文"——agentmemory 提供了更系统化的记忆基础设施
- **Context Management**：本仓库有多篇关于上下文压缩、上下文工程的文章，agentmemory 是另一种"上下文外溢出"的解决方案
- **Harness Design**：记忆是 Harness 设计的一级组件，agentmemory 可以作为 memory 模块的专业实现

---

> 项目地址：[rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)  
> Star History Gist：[设计文档 - 1200+ stars](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)
