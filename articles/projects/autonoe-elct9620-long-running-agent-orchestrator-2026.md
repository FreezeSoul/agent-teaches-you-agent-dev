# Autonoe：基于 Claude Agent SDK 的长程自主编码工具

**目标用户**：有 Python 经验的 Agent 开发工程师，想快速搭建一个生产可用的长程编码 Agent 系统

**核心成果**：原本需要数周手动集成的「Initializer + Coding Agent 双 Agent 模式」，现在通过 Autonoe 只需 5 分钟配置即可运行；支持多语言（Node.js/Python/Go/Rust 等），通过 Docker 实现安全隔离

**技术洞察**：Autonoe 巧妙地将 Anthropic 的「双 Agent 架构」工程化为可配置的工作流——initializer 读取 SPEC.md 创建 deliverables，coding agent 实现并验证，sync 命令负责校验当前状态与 SPEC.md 的同步情况

**证明**：GitHub 1.2k+ Stars，基于 Claude Agent SDK 的 autonomous-coding quickstart，是目前唯一将 Anthropic 官方最佳实践完整工程化的开源实现

---

## 定位破题

当你需要让 AI Agent 在多个编程会话中持续工作、跨越天甚至更长时间完成一个完整项目时，你会遇到一个难题：**如何让下一个会话的 Agent 快速知道「之前做了什么」「环境是否损坏」「还有哪些功能没完成」？**

Anthropic 在 2026 年初发布的 [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 中详细描述了双 Agent 模式（Initializer + Coding Agent），但官方只提供了 quickstart 示例代码，缺少生产级的工作流编排。

**Autonoe 填补了这个空白**——它将双 Agent 模式工程化为一个可配置的 CLI 工具，通过 SPEC.md 定义交付物，通过 status.json 追踪进度，通过 Docker 实现安全隔离。

---

## 体验式介绍

假设你有一个需求：「构建一个 CLI 工具，打印 Hello World」。

**传统方式**：你需要一个 Agent 在单次会话中完成所有工作。如果任务复杂到需要跨越多个上下文窗口，你得自己实现状态保存、进度追踪、环境恢复。

**使用 Autonoe**：

```yaml
# 1. 创建 SPEC.md
# My Project
Build a simple CLI tool that prints "Hello, World!"
```

```bash
# 2. 一行命令启动
docker compose run --rm cli autonoe run -p /path/to/your/project
```

然后 Autonoe 会：
1. **_initializer** 阶段：读取 SPEC.md，创建 deliverables（可验证的交付物清单）和初始状态
2. **coding** 阶段：逐个实现 deliverables，每完成一个就运行测试验证
3. **循环**：直到所有 deliverables 通过，或者达到 max-iterations 限制

```
┌─────────────────────────────────────────────────────────────────────┐
│ run Session Loop                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌──────────────────┐   ┌──────────────────┐                         │
│ │ Phase 1:        │   │ Phase 2:         │                         │
│ │ Initialization  │──▶│ Coding          │                         │
│ │                 │   │                 │                         │
│ │ - Read SPEC.md  │   │ - Implement     │                         │
│ │ - Create       │   │ - Test & Verify │                         │
│ │   deliverables  │   │ - Mark status   │                         │
│ └──────────────────┘   └────────┬─────────┘                         │
│                                │                                    │
│                                ▼                                    │
│                 ┌──────────────────────────┐                        │
│                 │ All deliverables passed? │                        │
│                 └─────────────┬────────────┘                        │
│                       Yes     │     No                              │
│                       ▼        │     ▼                               │
│                     Done    ┌────────────┐                          │
│                            │ Continue?  │                           │
│                            └─────┬──────┘                           │
│                          Yes    │    No                             │
│                          ▼      │    ▼                              │
│                      Next      │   Exit                             │
│                      session   │                                   │
│                            └────┘                                   │
└─────────────────────────────────────────────────────────────────────┘
```

**关键区别**：每次会话开始时，Agent 不是盲目开始写代码，而是先读 progress + 测试环境是否损坏。

---

## 拆解验证

### 技术深度

Autonoe 的核心设计基于两个官方来源：

1. **Autonomous Coding Quickstart**：Anthropic 的双 Agent 模式官方示例
2. **Effective Harnesses for Long-Running Agents**：Anthropic 的工程实践总结

> "This project is inspired by: Autonomous Coding Quickstart - Anthropic's example of building autonomous coding agents; Effective Harnesses for Long-Running Agents - Best practices for orchestrating long-running AI agents"

Autonoe 在此基础上增加了：
- **Deliverable-based workflow**：将工作拆分为可验证的单元，而非模糊的「功能」
- **Three-layer security**：SDK sandbox + filesystem scope + command allowlists
- **Session iteration**：自动重试直到所有 deliverables 通过

### 三层安全机制

```json
// .autonoe/agent.json
{
  "allowCommands": {
    "base": ["sqlite3"]  // 基础命令（run 和 sync 都允许）
  }
}
```

这是生产环境部署的关键——你不会希望 Agent 随意执行 `rm -rf /`。

### 多语言支持

Autonoe 提供了预配置的语言 profile：

| Tag | Description |
|-----|-------------|
| `base` | Minimal runtime (git, curl only) |
| `node` | Node.js with npm |
| `python` | Python with pip and uv |
| `golang` | Go toolchain |
| `rust` | Rust toolchain |

通过 `dockerfile_inline` 可以扩展：

```yaml
services:
  autonoe:
    build:
      context: .
      dockerfile_inline: |
        FROM ghcr.io/elct9620/autonoe/cli:python
        RUN apt-get install -y sqlite3
    volumes:
      - .:/workspace
```

### 社区活跃度

- GitHub Stars: 1.2k+
- 最后更新：活跃维护中
- 支持平台：Linux (x64/ARM64), macOS (x64/ARM64), Windows

---

## 行动引导

### 快速上手（3 步）

1. **安装 Autonoe**：
```bash
curl -LO https://github.com/elct9620/autonoe/releases/latest/download/autonoe-linux-x64.tar.gz
tar -xzf autonoe-linux-x64.tar.gz
sudo mv autonoe-linux-x64 /usr/local/bin/autonoe
```

2. **创建项目配置**：
```yaml
# compose.yml
services:
  cli:
    image: ghcr.io/elct9620/autonoe/cli:python
    volumes:
      - .:/workspace
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
```

3. **编写 SPEC.md 并运行**：
```bash
docker compose run --rm cli autonoe run -p .
```

### 贡献入口

Autonoe 仍在积极开发中，当前限制：
- Anthropic OAuth token 与 Agent SDK 存在商业条款限制，需使用 API key
- macOS SDK sandbox 有已知问题，Docker 方式更稳定

适合贡献的方向：Windows 支持改进、更多语言 profile、CI/CD 集成示例。

### 路线图

根据项目 README，团队正在评估：
- 纯 Claude Code 集成（不依赖 Agent SDK）
- 改进 SSH + Git 配置的高级工作流

---

## 与仓库现有内容的关联

| 已有内容 | 与 Autonoe 的关系 |
|---------|-----------------|
| `articles/harness/initializer-coding-agent-two-agent-pattern-2026.md`（本轮新增）| Autonoe 是双 Agent 模式的完整开源实现 |
| `articles/projects/cognee-topoteretes-knowledge-engine-agent-memory-2026.md` | Cognee 解决 Agent 记忆问题，Autonoe 解决长程进度追踪问题，共同构成 Agent 基础设施 |
| `articles/harness/eval-awareness-browsecomp-claude-opus-2026.md` | Eval Awareness 揭示 Agent 在评测中的行为，Autonoe 揭示 Agent 在长程开发中的行为 |

---

## 参考

- [Autonoe GitHub](https://github.com/elct9620/autonoe)
- [Autonomous Coding Quickstart - Anthropic](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Effective harnesses for long-running agents - Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)