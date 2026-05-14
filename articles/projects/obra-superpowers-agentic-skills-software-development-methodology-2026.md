# obra/superpowers: 让编码 Agent 真正学会软件工程方法论

## 目标用户

有 Claude Code / Codex / Cursor 等编码 Agent 经验，**希望 Agent 不只是写代码，而是遵循工程方法论**（TDD、设计优先、任务分解、人级审查）的开发者。

---

## 能解决什么问题

大多数编码 Agent 的问题是：**拿到任务就开写**。没有 spec、没有设计验证、没有 TDD、没有 review——导致：

- 实现的功能与需求存在理解偏差
- 代码没有测试，后续改动无法验证
- 设计决策没有记录，重构时丢失上下文
- Agent 长时间偏离目标

Superpowers 把软件工程方法论编码为可自动触发的 Skills，让 Agent **在写代码之前先做设计，写代码时遵循 TDD，完成后做 code review**。

---

## 核心亮点

### 1. 设计优先的工作流

Agent 启动时不是立刻写代码，而是：

> "As soon as it sees that you're building something, it doesn't just jump into trying to write code. Instead, it steps back and asks you what you're really trying to do. Once it's teased a spec out of the conversation, it shows it to you in chunks short enough to actually read and digest."

这解决了「Agent 自顾自实现了一个没人要的功能」的根本问题。

### 2. 子代理驱动的开发过程

```
设计批准 → 任务分解 → 每个任务分配给独立子代理
       → 两阶段审查（spec 合规性 + 代码质量）
       → 人类检查点（可选）
```

> "It's not uncommon for Claude to be able to work autonomously for a couple hours at a time without deviating from the plan you put together."

### 3. 强制执行的 TDD

```
RED: 写一个会失败的测试 → 看它失败
GREEN: 写最小代码让它通过 → 看它通过
REFACTOR: 重构 → 确保测试仍然通过
```

Superpowers 的 TDD Skill **强制先写测试**，删除在测试前写的代码，从流程上杜绝「事后补测试」。

### 4. 跨 Agent 平台的插件化

支持 Claude Code / Codex CLI / Codex App / Factory Droid / Gemini CLI / OpenCode / Cursor / GitHub Copilot CLI，通过插件机制接入，**同一套 Skills 在不同 Agent 上生效**。

这意味着 Superpowers 不是绑定某个 Agent 的工具，而是**跨 Agent 的软件工程规范层**。

### 5. 关键 Skill 列表

| Skill | 触发时机 | 作用 |
|-------|---------|------|
| `brainstorming` | 写代码之前 | 通过提问细化需求，分段展示设计供人类确认，保存设计文档 |
| `using-git-worktrees` | 设计批准后 | 在新分支创建隔离 workspace，验证干净测试基线 |
| `writing-plans` | 设计批准后 | 分解为 2-5 分钟粒度的任务，每个任务有精确文件路径和验证步骤 |
| `subagent-driven-development` | 计划就绪 | 每个任务派生子代理 + 两阶段审查 |
| `test-driven-development` | 实现期间 | 强制 RED-GREEN-REFACTOR，删除测试前写的代码 |
| `requesting-code-review` | 任务之间 | 按严重性报告问题，Critical 阻塞进度 |
| `finishing-a-development-branch` | 任务完成 | 验证测试，提供 merge/PR/keep/discard 选项 |

---

## 与同类项目的差异化

| 项目 | 定位 | Superpowers 的差异 |
|------|------|-------------------|
| **mattpocock/skills** | 工具类 Skill 集合（git/代码转换）| 工具 Skill vs 工程方法论，互补 |
| **huggingface/skills** | 多领域 Skill 索引（科学/金融等）| 领域 Skill vs 软件工程 Process Skill |
| **garrytan/gstack** | 多角色虚拟工程团队 | gstack 是「角色分配」，Superpowers 是「流程约束」，可叠加 |
| **YuxiaoWang-520/harness-craft** | 可组合 Skills/Rules 库 | harness-craft 更偏 AI Coding 特定规则，Superpowers 是完整软件工程方法论 |

---

## 实际使用体验

从 README 的描述来看，工作流大致是：

```
你：我要做一个 API 网关
Agent（Superpowers）：先别写代码，你想解决什么问题？有哪些客户端？
   → 你回答问题
   → Agent 分段展示设计（数据模型、路由结构、错误处理）
   → 你批准设计
   → Agent 输出任务计划（每个任务 2-5 分钟，有精确文件路径）
   → 你说"go"
   → Agent 派生子代理执行每个任务，带两阶段 review
   → 你可以长时间不管，Agent 自动保持计划执行
```

这个体验的核心价值：**把人类从「盯着 Agent 写代码」变成「审阅设计 + 中途干预」**，大幅降低人类监控成本。

---

## 快速上手

```bash
# Claude Code
/plugin install superpowers@claude-plugins-official
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# Codex CLI
/plugins
# 搜索 superpowers 安装

# Cursor
/add-plugin superpowers
```

首次使用时告诉 Agent "I want to build [something]"，Superpowers 会自动接管后续流程。

---

## 引用

> "Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them."
> — [GitHub README](https://github.com/obra/superpowers)

> "It's not uncommon for Claude to be able to work autonomously for a couple hours at a time without deviating from the plan you put together."
> — [GitHub README](https://github.com/obra/superpowers)