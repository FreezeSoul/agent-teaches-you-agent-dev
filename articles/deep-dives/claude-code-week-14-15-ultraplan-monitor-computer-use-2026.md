# Claude Code Week 14-15 新功能深度分析：Ultraplan、Monitor 与 CLI Computer Use

> **时间**：2026-04-06 至 2026-04-10
> **版本**：v2.1.92 → v2.1.101
> **标签**：#claude-code #ai-coding #tool-use #agent-orchestration

## TL;DR

Claude Code 在 Week 14-15 连续两周发布了多个重要功能更新，涵盖三个核心方向：

1. **Ultraplan（研究预览）**：云端协作规划，终端启动 + Web 端编辑
2. **Monitor Tool（v2.1.98）**：后台事件监视，替代 polling loop
3. **CLI Computer Use（研究预览）**：终端直接控制原生 GUI 应用

这三个功能共同指向一个趋势：**Claude Code 正在从「单点执行工具」向「持续性 Agent 工作流编排平台」演进**。

---

## 1. Ultraplan：云端协作规划模式

### 核心机制

```
终端输入：/ultraplan migrate the auth service from sessions to JWTs
    ↓
Claude Code Cloud Session（Web 端）生成计划
    ↓
用户在 Web 端评论、修订
    ↓
选择：远程执行 or 发送回 CLI 执行
```

### 技术特点

| 维度 | 说明 |
|------|------|
| **启动方式** | 终端直接启动，无需 Web 端预先设置 |
| **协作模式** | 云端起草 → Web 评论 → 终端执行 |
| **首次运行** | v2.1.101 起自动创建默认云环境 |
| **适用场景** | 复杂重构、多步骤迁移、跨文件重架构 |

### 工程价值

Ultraplan 的本质是**规划与执行的解耦**：

- **规划阶段**（消耗 token 少，可快速迭代）：Claude 在云端生成结构化计划，用户可以逐段评论和修订
- **执行阶段**（消耗 token 多，需要精确控制）：用户确认后推送回 CLI 执行

这与 LangGraph 的 `interrupt` 模式有相似之处，但 Ultraplan 的实现更偏向用户体验优化（规划在云端、执，本地），而非技术层面的状态管理。

### 与 KAIROS Daemon Mode 的关系

KAIROS Daemon Mode（上一轮已完成）关注的是**长时间后台运行**的持续性；Ultraplan 关注的是**复杂任务前的规划协作**。两者是互补的：

```
Ultraplan（规划） + KAIROS（执行） = 完整的 Agent 工作流
```

---

## 2. Monitor Tool：事件驱动后台监视

### 核心机制

```text
用户：Tail server.log in the background and tell me the moment a 5xx shows up
Claude：
  1. 启动后台 watcher
  2. 事件流式返回（每条作为独立 transcript message）
  3. Claude 即时反应
  4. 终端保持可用（不阻塞）
```

### 技术特点

| 维度 | 说明 |
|------|------|
| **模式** | 后台 watcher + 事件流 |
| **消息格式** | 每事件作为独立 transcript message |
| **响应方式** | Claude 即时反应，无需轮询 |
| **替代方案** | 传统 `while true; do ... sleep 1; done` polling |

### 与 /loop 的整合

`/loop` 命令现在**自我调度**：

```text
用户：/loop check CI on my PR
Claude：
  - 分析任务类型
  - 自动选择 next tick 间隔
  - 或直接使用 Monitor tool 跳过 polling
```

这意味着 Claude Code 在尝试**消灭显式轮询**，转向事件驱动或智能调度。

### 工程价值

Monitor tool 解决了 Agent **「长时间后台任务」与「即时响应」**的矛盾：

- **传统方式**：Bash sleep loop 阻塞终端 turn，无法同时做其他事
- **Monitor 方式**：后台 watcher 独立运行，事件驱动通知，终端保持可用

---

## 3. CLI Computer Use：终端控制原生 GUI

### 核心机制

```
用户：Open the iOS simulator, tap through onboarding, and screenshot each step
Claude：
  1. 启动 MCP computer-use 工具
  2. 识别屏幕元素
  3. 执行点击/滑动操作
  4. 截图返回
```

### 技术演进

| 版本 | 能力 |
|------|------|
| **Opus 4.7** | OSWorld-Verified 78%（桌面操控） |
| **Desktop App** | 上周（Week 13）已支持 |
| **CLI** | 本周（Week 14）新增 |

### 与 Web/Desktop App 的区别

| 维度 | Web Apps | Native Apps |
|------|----------|-------------|
| **验证方式** | API 调用 + 验证循环 | API 有限，需要 GUI 操作 |
| **Computer Use** | 已支持（Web 自动化） | 新增支持（CLI） |
| **适用场景** | Web 表单、点击测试 | iOS/Android Simulator、原生桌面应用 |

### 与 MCP 的关系

CLI Computer Use 通过 MCP 协议实现：

```bash
/mcp → 找到 "computer-use" → toggle on
```

这延续了 Claude Code 将 MCP 作为核心扩展机制的策略。

---

## 4. 综合分析：架构演进方向

### 从「工具」到「平台」

Week 14-15 的更新共同反映了 Claude Code 的架构方向：

```
单点执行工具（v1）
    ↓
持续运行 Agent（KAIROS Daemon Mode）
    ↓
协作规划 + 持续监视 + 跨界面执行（Week 14-15）
    ↓
【正在演进】多 Agent 编排（/team-onboarding, /agents tab）
```

### 核心能力矩阵

| 能力 | 实现方式 | 解决的问题 |
|------|----------|------------|
| **复杂规划** | Ultraplan（云端 + Web） | 减少 token 浪费在错误方向上 |
| **后台监视** | Monitor tool（事件驱动） | 消除 polling 的资源浪费 |
| **GUI 控制** | CLI Computer Use（MCP） | 覆盖无 API 的原生应用 |
| **团队协作** | /team-onboarding, /autofix-pr | 知识传递和 PR 自动化 |

### 与竞品的差异化

| 功能 | Claude Code | Cursor | GitHub Copilot |
|------|-------------|--------|----------------|
| 云端协作规划 | Ultraplan | - | - |
| 后台事件监视 | Monitor tool | - | - |
| CLI Computer Use | ✅ | - | - |
| 多 Agent 并行 | /agents tab | Cursor Agents（tiled layout） | - |
| PR 自动修复 | /autofix-pr | - | Copilot Workspace |

---

## 5. 笔者判断

### 最有价值的功能

1. **Monitor tool**（短期价值最高）
   - 解决了日常开发中的高频痛点（CI 监视、日志监控、服务器状态）
   - 事件驱动替代 polling 是正确方向
   - 预计会成为高频使用的命令

2. **CLI Computer Use**（长期影响最大）
   - 将 Opus 4.7 的 computer-use 能力从桌面扩展到终端
   - 覆盖了「无 API 的原生应用」场景
   - 与 MCP 生态深度整合

3. **Ultraplan**（战略意义明确）
   - 展示了「规划与执行分离」的架构思路
   - 云端规划 + 本地执行的模式有扩展空间

### 对 Agent 工程实践的影响

- **Monitor tool** 可能会催生新的 Agent 设计模式（事件驱动 Agent）
- **CLI Computer Use** 扩展了 Agent 的工具边界（从 API 到 GUI）
- **Ultraplan** 提供了一种「人机协作规划」的新范式

### 值得关注的后续

- Ultraplan 是否会与 KAIROS Daemon Mode 整合？
- Monitor tool 是否会开放自定义事件源？
- CLI Computer Use 是否有计划支持 Linux 桌面环境？

---

## 6. 参考链接

- [Week 15 · April 6–10, 2026](https://code.claude.com/docs/en/whats-new/2026-w15)
- [Week 14 · March 30 – April 3, 2026](https://code.claude.com/docs/en/whats-new/2026-w14)
- [Ultraplan guide](https://code.claude.com/docs/en/ultraplan)
- [Monitor tool reference](https://code.claude.com/docs/en/tools-reference#monitor-tool)
- [Computer use guide](https://code.claude.com/docs/en/computer-use)

---

## CHANGELOG

| 日期 | 内容 |
|------|------|
| 2026-04-26 | 初始版本 |
