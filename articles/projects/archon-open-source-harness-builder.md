# Archon: 让 AI 编程变得确定可重复的开源工作流引擎

> 当你让 AI agent 修一个 bug，修出来的结果取决于「模型今天心情好不好」—— 可能跳过规划，可能忘记跑测试，可能 PR 描述写得一塌糊涂。每次运行都是开盲盒。
>
> Archon 做的事，就是把这个过程固定下来。

---

## 背景：AI 编程的非确定性问题

AI 编程工具（Claude Code、Cursor、Copilot）最大的痛点不是「能力不够」，而是**不可预测**。

同一个需求：
- 这次可能先写测试再写代码，下次直接硬编码
- 这次 PR 描述详尽，下次连改动说明都没有
- 这次考虑了边界情况，下次直接假设 happy path

这不是模型的 bug，而是**没有约束机制**。人类开发者的流程约束（code review、CI 检查、PR template）AI agent 直接跳过，因为它不知道你的流程长什么样。

## Archon 的核心思路

Archon 的解法很直接：**把开发流程编码成 YAML 工作流，让 AI 在约束下填充智能**。

类似的思想之前出现过两次：
- **Dockerfile**：把基础设施编码为文件，可复现的构建过程
- **GitHub Actions**：把 CI/CD 编码为 YAML，可复现的部署过程

Archon 是第三次：**把 AI 编程编码为工作流，可复现的开发过程**。

## 核心特性

### 1. 工作流即代码

```yaml
nodes:
  - id: plan
    prompt: "Explore the codebase and create an implementation plan"

  - id: implement
    depends_on: [plan]
    loop:
      prompt: "Read the plan. Implement the next task. Run validation."
      until: ALL_TASKS_COMPLETE
      fresh_context: true

  - id: run-tests
    depends_on: [implement]
    bash: "bun run validate"    # 确定性节点，无 AI

  - id: approve
    depends_on: [run-tests]
    loop:
      prompt: "Present changes for review. Address feedback."
      until: APPROVED           # 人工审批门
      interactive: true

  - id: create-pr
    depends_on: [approve]
    prompt: "Push changes and create a pull request"
```

关键设计：**AI 节点和确定性节点共存**。测试、构建、git 操作是确定性的；规划、代码生成、review 是 AI 的领域。

### 2. Git Worktree 隔离

每次工作流运行在独立的 git worktree 中，可以**并行跑 5 个任务而互不冲突**。修 3 个 bug + 做一个 feature + review 一个 PR，同时跑，不打架。

### 3. 循环 + 审批门

```yaml
loop:
  until: ALL_TASKS_COMPLETE    # 或 APPROVED / 测试通过
  fresh_context: true          # 每次迭代清空上下文
```

AI 在实现循环中迭代，直到条件满足。人工审批门让流程停在关键节点等你确认。

### 4. 多 Agent 并行 Review

```yaml
- id: review
  prompt: "Review all changes against the plan"
- id: security-scan
  prompt: "Check for security vulnerabilities"
- id: perf-review
  prompt: "Analyze performance implications"
# 5 个并行 review agent，结果汇聚
```

一次 PR review 可以启动 5 个并行 specialized agent。

## 架构设计

```
Platform Adapters (Web UI, CLI, Telegram, Slack, Discord, GitHub)
                          │
                          ▼
                    Orchestrator
              (消息路由 & 上下文管理)
          ┌─────────────┴─────────────┐
          │                           │
    Command Handler           Workflow Executor
    (Slash 命令)               (YAML 工作流)
          │                           │
          └───────────┬────────────────┘
                      │
                      ▼
           AI Assistant Clients
        (Claude / Codex / Pi)
                      │
                      ▼
         SQLite / PostgreSQL
      (7 张表：代码库/会话/工作流记录)
```

亮点：
- **多平台入口统一**：CLI 触发、Telegram 消息、Slack 命令、GitHub webhook，汇聚到同一个 Orchestrator
- **支持多种 AI 客户端**：Claude Code、Codex、Pi，不绑定单一 provider
- **数据库持久化**：工作流状态、会话历史、隔离环境，全部可查

## 内置 17 个工作流

开箱即用的常用场景：

| 工作流 | 用途 |
|--------|------|
| `archon-idea-to-pr` | 想法 → 计划 → 实现 → PR |
| `archon-fix-github-issue` | Issue → 调查 → 修复 → PR |
| `archon-smart-pr-review` | 智能 PR review，按复杂度分类 |
| `archon-comprehensive-pr-review` | 5 个并行 review agent |
| `archon-architect` | 架构扫楼 + 代码健康度提升 |
| `archon-refactor-safely` | 带类型检查的安全重构 |
| `archon-resolve-conflicts` | 冲突检测 + 解决 + 验证 |

自定义工作流放在 `.archon/workflows/` 目录，commit 到仓库后整个团队用同一套流程。

## 解决的问题

**没有 Archon 的世界：**
```
你: "帮我修一下登录 bug"
AI: 好的（跳过测试，直接改代码，PR 描述写 "fix"）
```

**有 Archon 的世界：**
```
你: "用 archon 修一下登录 bug"
AI: → Creating isolated worktree on branch archon/fix-login...
   → Planning... (发现 3 个相关文件)
   → Implementing (1/3)... → Tests failing - iterating...
   → Implementing (2/3)... → Tests passing
   → Implementing (3/3)... → Tests passing
   → Code review complete - 0 issues
   → PR ready: #47
```

区别：AI 遵循你的流程，不是想怎么干就怎么干。

## 适用场景

✅ **团队需要统一 AI 编程流程** — 把 code review gate、测试 gate、PR template 编码进工作流  
✅ **需要并行处理多个任务** — worktree 隔离支持同时跑多个工作流  
✅ **人工审批必须介入的流程** — approve 节点暂停等人工确认  
✅ **多平台接入** — Web UI + CLI + Telegram + Slack 统一入口  

❌ **个人快速探索** — 流程编码有额外开销，不适合 one-off 任务  
❌ **已有成熟 MLOps/CI 流程** — 如果你的 pipeline 已经固定，Archon 的价值有限  

## 技术栈

- **运行时**: Bun + TypeScript
- **AI 集成**: Claude Code (主要), Codex, Pi
- **数据库**: SQLite (默认) / PostgreSQL (生产)
- **部署**: Docker 支持，单二进制分发
- **平台**: macOS / Linux / Windows / WSL

## 项目状态

- GitHub: [coleam00/Archon](https://github.com/coleam00/Archon)
- 文档: [archon.diy](https://archon.diy)
- 协议: MIT
- 成熟度: v2 版本，重写自 Python v1，全面转向 TypeScript + 工作流引擎

---

## 评价

Archon 解决的不是「AI 能不能写代码」的问题，而是「AI 能不能按我的方式写代码」的问题。

这个区别很关键。当前大多数 AI 编程工具是**以 AI 为中心**的——你给一个 prompt，AI 决定怎么干。Archon 是**以流程为中心**的——你定义流程，AI 在流程约束下填充智能。

如果你在团队中使用 AI 编程工具，流程一致性是个真实痛点。Archon 提供的不是另一个 AI 工具，而是一个**让 AI 遵循你流程的框架**。

类比：Git hooks + CI 让人类开发者的行为可预测，Archon 让 AI 开发者的行为可预测。

---

**防重索引记录**

- GitHub URL: https://github.com/coleam00/Archon
- 推荐日期: 2026-04-30
- 推荐理由: 首个开源 AI 编程工作流引擎，解决 AI 编程非确定性问题
