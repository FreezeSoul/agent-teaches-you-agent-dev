## 项目名称：open-multi-agent

## 核心问题：当你的 Node.js 后端需要一个多 Agent 团队时，如何用最小的依赖代价实现「输入目标，输出结果」？

## 为什么存在（项目背景）

Multi-Agent 框架（LangGraph、CrewAI、AutoGen）在生产环境中往往带来巨大的依赖树和学习曲线。JackChen-me/open-multi-agent 提出了一个不同的思路：**如果你的系统已经是一个 Node.js 后端，Multi-Agent 能力应该是这个后端的一个库，而不是一个新平台**。

> "open-multi-agent is the `npm install` you drop into an existing Node.js backend when you need a team of agents to work on a goal together."
> — [open-multi-agent GitHub README](https://github.com/JackChen-me/open-multi-agent)

## 核心能力与技术架构

### 关键特性 1：零平台绑定，单文件引入
整个框架只有 3 个运行时依赖。无需 Docker、无需独立的编排服务、无需消息队列。一个 `npm install` 即可在任意 Node.js 项目中注入 Multi-Agent 能力。

### 关键特性 2：目标驱动的自动任务分解
`runTeam()` 接口将自然语言目标作为输入，内部自动将目标分解为可并行的子任务：

```typescript
import { openMultiAgent } from 'open-multi-agent';

const result = await openMultiAgent.runTeam(
  team,
  'Build a REST API with authentication'
);
```

### 关键特性 3：Multi-Model 多模型协同
支持任意 LLM Provider（OpenAI、Anthropic、本地 Ollama）。可以在同一个任务中让不同能力的模型处理不同子任务。

### 关键特性 4：并行执行与结果聚合
任务分解后自动并行执行，结果在团队层面聚合为统一输出。

> "Auto task decomposition, parallel execution."
> — [open-multi-agent GitHub README](https://github.com/JackChen-me/open-multi-agent)

## 与同类项目对比

| 维度 | open-multi-agent | LangGraph | CrewAI | AutoGen |
|------|-----------------|-----------|--------|---------|
| 运行时依赖 | 3 个 | 数十个 | 数十个 | 数十个 |
| 部署复杂度 | 单进程 | 需要图运行时 | 多 Agent 服务 | 分布式 |
| 任务分解 | 自动 | 需显式定义 | 角色定义 | 需显式定义 |
| 适用场景 | 后端集成 | 复杂工作流 | 角色扮演 | 通用研究 |
| 学习曲线 | 低 | 高 | 中 | 中 |

> 官方原文："one runTeam() call from goal to result."
> — [open-multi-agent GitHub README](https://github.com/JackChen-me/open-multi-agent)

## 适用场景与局限

**适用场景**：
- 已有 Node.js 后端服务，需要引入 Multi-Agent 能力（如客服 Agent 团队、文档处理流水线）
- 轻量级场景，不需要 LangGraph 级别的复杂状态机
- 需要在单个进程内快速集成多模型协同能力

**局限**：
- 无内置持久化机制（Session 状态由调用方管理）
- 无内置安全沙箱（不适用于执行不可信代码）
- 无 Handoff 原生支持（Agent 间显式交接需要自行实现）

## 一句话推荐

当你的系统已经是 Node.js，希望以最小代价获得 Multi-Agent 并行任务分解能力时，open-multi-agent 是目前生产级依赖最少的方案——3 个依赖替换几十个，适合不想引入完整 Agent 平台开销的场景。

## 防重索引记录

- GitHub URL: https://github.com/JackChen-me/open-multi-agent
- 推荐日期: 2026-05-02
- 推荐者: ArchBot
- 关联文章: `metamorph-multi-agent-file-lock-parallel-2026.md`（Multi-Agent 并行协调机制）
