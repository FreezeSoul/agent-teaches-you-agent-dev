# Claude Code Game Studios：把一个 AI 变成游戏开发工作室

## 项目概述

**Claude Code Game Studios** 是一个 Claude Code 模板项目，通过 49 个专用 Agent、72 个 Skills、12 个 Hooks 和 11 个 Rules，将单个 Claude Code 会话转变为完整的游戏开发工作室——有导演、美术总监、QA、发行经理，每个角色各司其职。

当前 Stars：16,679。

## 解决的问题

「用 AI 编程一个游戏」和「用 AI 管理一个游戏项目」是两件完全不同的事。单独使用 Claude Code 做游戏时，没有人会阻止你硬编码魔法数字、跳过设计文档、写意大利面条式代码。没有 QA 环节，没有设计评审，没有人问「这个改动是否真正符合游戏愿景」。

Claude Code Game Studios 通过**真实的游戏工作室组织架构**解决此问题：不是给 AI 增加几个工具，而是给它一整套组织结构和质量门禁。

## 工作室层级

**Tier 1 — 导演（Director）**：Creative Director、Technical Director、Producer

**Tier 2 — 部门负责人（Lead）**：Game Designer、Lead Programmer、Art Director、Audio Director、Narrative Director、QA Lead、Release Manager、Localization Lead

**Tier 3 — 专家（Specialist）**：Gameplay Programmer、Engine Programmer、AI Programmer、Network Programmer、UI Programmer、UX Designer、QA Tester、Performance Analyst 等

同时包含**三大引擎专项 Agent 集**：Godot 4、Unity（带 DOTS/ECS）、Unreal Engine 5。

## 核心机制

**协作而非自主**：每个 Agent 遵循严格协作协议——提问→展示选项→用户决策→草稿展示→审批确认。用户始终控制方向，Agent 提供结构和专业能力。

**自动化安全**：12 个 Hooks 在关键节点自动运行，包括 commit 验证（硬编码检测）、push 警告、资产命名规范、会话启动方向引导、缺失设计文档检测、子 Agent 审计追踪等。

**路径作用域规则**：不同目录下的代码自动应用不同的编码标准（`src/gameplay/` 强制数据驱动，`src/core/` 强制零分配热路径，`src/networking/` 强制服务器权威等）。

## 局限

- **上手门槛**：需要理解整个工作室结构才能有效使用，对于只想快速写个小游戏的新手来说过于复杂
- **Agent 数量多意味着管理复杂度高**：49 个 Agent 的协作有时可能超出 Claude 的上下文处理能力
- **专注游戏开发**：对于非游戏项目没有使用价值，不是一个通用 AI 编程框架

## 一句话推荐

如果你认真用 AI 做游戏开发，并且需要工作室级别的工程纪律来保证质量，Claude Code Game Studios 提供了目前最完整的 AI 游戏开发组织方案——但建议先从 `/start` 工作流开始逐步适应。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/Donchitos/Claude-Code-Game-Studios`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：8.5/15
