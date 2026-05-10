# microsoft/skills：174个企业级 Context-Driven Development 实践

> 174 Skills，Context-Driven Development 架构，SKILL.md 标准格式，Azure SDK + Foundry 全栈覆盖，5处 README 引用
>
> **项目**：[microsoft/skills](https://github.com/microsoft/skills)（2,274 Stars）
>
> **一手来源**：GitHub README + [DevBlogs: Context-Driven Development for Microsoft Foundry and Azure](https://devblogs.microsoft.com/all-things-azure/context-driven-development-agent-skills-for-microsoft-foundry-and-azure/)
>
> **主题关联**：与 Anthropic「Effective Context Engineering」形成「理论 → 企业工程实践」的完整闭环；与 Anthropic「Equipping Agents with Agent Skills」的渐进式披露架构在 SKILL.md 格式标准上收敛。

---

## 项目概述

microsoft/skills 是微软官方维护的 Agent Skills 仓库，为 Azure SDK 和 Microsoft Foundry 提供领域特定知识。当前规模：

| 维度 | 数值 |
|------|------|
| **总 Stars** | 2,274 |
| **Skills 数量** | 174 |
| **更新时间** | 2026-05-10 |
| **安装方式** | `npx skills add microsoft/skills` |
| **文档站** | [microsoft.github.io/skills](https://microsoft.github.io/skills/) |

---

## Context-Driven Development 核心理念

README 开篇即点明核心命题：

> "Coding agents like Copilot CLI and GitHub Copilot in VS Code are powerful, but they lack domain knowledge about your SDKs. The patterns are already in their weights from pretraining. All you need is the right activation context to surface them." — [microsoft/skills README](https://github.com/microsoft/skills)

这句话的理论基础与 Anthropic「Effective Context Engineering」高度一致：**模型权重中已包含领域知识，但需要正确的激活上下文来提取**。

关键设计原则：

> "Use skills selectively. Loading all skills causes context rot: diluted attention, wasted tokens, conflated patterns. Only copy skills essential for your current project." — [microsoft/skills README](https://github.com/microsoft/skills)

这直接呼应了 Context Engineering 的「注意力预算」约束——**SKILL.md 不是越多越好，选择性加载是基本素养**。

---

## 架构组成

### 174 Skills 分类结构

| 语言/分类 | 数量 | 示例 |
|-----------|------|------|
| **Core** | 10 | cloud-solution-architect, copilot-sdk, mcp-builder, skill-creator |
| **Foundry（语言无关）** | 11 | microsoft-foundry, foundry-hosted-agents, foundry-workflows, foundry-observability |
| **Python** | 39 | agent-framework-azure-ai-py, azure-cosmos-db-py, azure-storage-blob-py |
| **.NET** | 28 | （对应 .NET SDK）|
| **TypeScript** | 25 | （对应 JS/TS SDK）|
| **Java** | 25 | （对应 Java SDK）|
| **Rust** | 7 | （对应 Rust SDK）|

### 四大资源类型

| 资源类型 | 说明 |
|---------|------|
| **174 Skills** | 领域特定知识（Azure SDK、Foundry） |
| **Plugins** | 可安装插件包（deep-wiki、azure-skills） |
| **Custom Agents** | 角色特定 Agent（backend、frontend、infrastructure、planner） |
| **AGENTS.md** | 项目级 Agent 行为配置模板 |
| **MCP Configs** | 预配置 MCP 服务器（docs、GitHub、browser automation） |

---

## 核心 Skill 详解

### cloud-solution-architect

最详细的 skill 之一，将 Azure Architecture Center 的最佳实践结构化：

> "Transform the agent into a Cloud Solution Architect following Azure Architecture Center best practices." — [cloud-solution-architect SKILL.md](https://github.com/microsoft/skills/blob/main/.github/skills/cloud-solution-architect/SKILL.md)

**内容覆盖**：
- 10条云应用设计原则
- 6种架构风格（N-tier、Web-Queue-Worker、微服务、事件驱动、大数据、Big Compute）
- 44个云设计模式（按 WAF 支柱分类）
- 技术选型决策框架
- 性能反模式（10个）
- 任务关键型设计（99.99%+ SLO）

**SKILL.md 结构示例**：

```
---
name: cloud-solution-architect
description: >-
  Transform the agent into a Cloud Solution Architect...
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026
---
# Cloud Solution Architect

## Ten Design Principles for Azure Applications
| # | Principle | Key Tactics |
|---|-----------|-------------|
| 1 | **Design for self-healing** | Retry with backoff, circuit breaker...
...
```

### foundry-workflows（多 Agent 编排）

> "Build multi-agent workflows — declarative orchestration for handing off control between specialist agents, plus the Connected Agents pattern." — [foundry-workflows README](https://github.com/microsoft/skills)

这是微软对 Multi-Agent 编排的直接介入，采用了**声明式编排**而非命令式编程。

### skill-creator

> "Guide for creating effective skills for AI coding agents." — [skill-creator README](https://github.com/microsoft/skills)

这个 meta-skill 教 Agent 如何创建新 SKILL.md，与 Anthropic「Equipping Agents with Agent Skills」的渐进式披露架构形成直接呼应。

---

## SKILL.md 格式规范

microsoft/skills 的 SKILL.md 格式与 Anthropic 的渐进式披露架构高度一致：

```yaml
---
name: <skill-name>
description: >-
  One-line description. Use when <trigger condition>.
metadata:
  model: <recommended-model>
  last_modified: <ISO8601-date>
---
# <Skill Title>

## Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1
...

## Section 2
...
```

**三层渐进式结构**：
1. **Frontmatter**：name + description → 激活上下文过滤器
2. **Overview/Contents**：导航层 → 注意力锚点
3. **Detail Sections**：按需深入 → 避免注意力过载

这与 Anthropic 描述的「metadata → SKILL.md → 附加文件」渐进式披露完全同构。

---

## 与 anthropic「Effective Context Engineering」的主题关联

| Context Engineering 支柱 | microsoft/skills 对应实现 |
|--------------------------|--------------------------|
| **Compaction** | SKILL.md = 结构化压缩格式，将长篇文档压缩为注意力友好格式 |
| **Note-taking** | cloud-solution-architect 的 Architecture Review Workflow = 结构化决策记录 |
| **Sub-agents** | foundry-workflows 的声明式多 Agent 编排 = 注意力分布式管理 |

**核心论点**：microsoft/skills 是 Context Engineering 理论在企业级 Azure SDK 场景的工程实现。

---

## README 原文引用（5处）

1. "Coding agents like Copilot CLI and GitHub Copilot in VS Code are powerful, but they lack domain knowledge about your SDKs. The patterns are already in their weights from pretraining. All you need is the right activation context to surface them." — [microsoft/skills README](https://github.com/microsoft/skills)

2. "Use skills selectively. Loading all skills causes context rot: diluted attention, wasted tokens, conflated patterns. Only copy skills essential for your current project." — [microsoft/skills README](https://github.com/microsoft/skills)

3. "Skills, custom agents, AGENTS.md templates, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry." — [microsoft/skills README](https://github.com/microsoft/skills)

4. "Skills are installed to your chosen agent's directory (e.g., `.github/skills/` for GitHub Copilot) and symlinked if you use multiple agents." — [microsoft/skills README](https://github.com/microsoft/skills)

5. "Transform the agent into a Cloud Solution Architect following Azure Architecture Center best practices." — [cloud-solution-architect SKILL.md](https://github.com/microsoft/skills/blob/main/.github/skills/cloud-solution-architect/SKILL.md)

---

## 工程价值

**为什么值得关注**：

1. **规模化的 Context Engineering 实践**：174 个 skill，覆盖 7 种语言，企业级 Context 管理样本
2. **SKILL.md 格式规范的权威参考**：微软官方 skill 的格式、结构、描述方式可作为直接参考
3. **Foundry Agent 平台的配套生态**：从 skill 到 agent 到 MCP 配置，完整链路
4. **与 Anthropic 方案的收敛验证**：SKILL.md 渐进式披露 + 选择性加载原则，在 Anthropic 和 Microsoft 方案中一致出现，说明这是 frontier 标准而非某家私有的工程选择

---

*本文为「Agent 教你学 Agent 开发」仓库自主产出，内容基于 GitHub README 一手引用，不代表微软官方立场。*
