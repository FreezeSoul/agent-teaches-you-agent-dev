# dagger/container-use：用 Docker 容器重新定义 AI Coding Agent 的开发环境隔离

**这篇文章要回答的问题是**：当你在本地同时运行多个 AI Coding Agent 时，如何让它们在互不干扰的独立环境中工作，同时又能让你随时介入查看状态甚至接管控制？

---

## 背景：Cloud Agent 开发环境的工程挑战

Cursor 3.4 changelog 揭示了一个核心工程命题：要完成端到端的工程任务，AI Agent 需要与本地开发机器一样的环境配置——克隆的代码库、安装的依赖、内部工具链的凭据，以及对构建系统的访问权限。

Cursor 的解法是通过 Dockerfile 配置云端开发环境。而 `dagger/container-use` 提供了另一种思路：**用 Docker 容器作为 Agent 的工作空间，每个 Agent 在独立的容器中运行，通过 Git 分支隔离工作成果，实现真正的并行与隔离**。

笔者认为这种方式比纯 VM 或纯进程隔离更灵活，比直接在宿主机上运行 Agent 更安全——一个失控的 Agent 最多只能影响它自己的容器。

---

## container-use 的核心设计

根据 README，container-use 的核心特性：

> *"Container Use lets coding agents do their work in parallel environments without getting in your way. Go from babysitting one agent at a time to enabling multiple agents to work safely and independently with your preferred stack."*

关键设计：

1. **容器级隔离**：每个 Agent 工作在独立的 Docker 容器中，失败直接丢弃，不影响主机环境
2. **Git 分支工作流**：每个 Agent 的工作在独立 Git 分支上，通过 `git checkout <branch_name>` 随时审查、合并或丢弃
3. **实时可见性**：提供完整的命令历史和日志，不只是 Agent「声称」做了什么，而是能看到实际执行了什么操作
4. **直接干预能力**：可以随时进入任何一个 Agent 的终端查看状态并在需要时接管控制
5. **MCP 协议兼容**：作为 MCP Server 工作，支持 Claude Code、Cursor 以及其他 MCP 兼容的 Agent

---

## 竞品对比

| 维度 | container-use | Cursor Cloud Environments | 本地进程隔离 |
|------|--------------|---------------------------|--------------|
| 隔离粒度 | Docker 容器 | 云端 VM（远程） | 进程级别 |
| 并行能力 | 多 Agent 并行，天然隔离 | 需要云端 Fleet 配置 | 受本地资源限制 |
| 干预能力 | 实时进入 Agent 终端 | 远程连接 | 终止进程 |
| 配置方式 | Dockerfile + MCP Server | Web UI 配置 | N/A |
| 依赖 | Dagger | Cursor Cloud | 无 |
| 适用场景 | 私有代码库、混合团队 | 企业级云端管理 | 个人简单任务 |

---

## 使用方式

作为 MCP Server 安装：

```bash
# macOS
brew install dagger/tap/container-use

# 其他平台
curl -fsSL https://raw.githubusercontent.com/dagger/container-use/main/install.sh | bash

# 添加到 Claude Code
cd /path/to/repository
claude mcp add container-use -- container-use stdio
```

添加 Agent 规则（可选）：
```bash
curl https://raw.githubusercontent.com/dagger/container-use/main/rules/agent.md >> CLAUDE.md
```

---

## 笔者的判断

container-use 的最大价值在于**将「开发环境即代码」的理念引入到 AI Agent 领域**。传统 Docker 用于服务部署，container-use 将其变成 Agent 的「工作台」——每个任务一个容器，每个成果一个分支，每次实验无后顾之忧。

但笔者也注意到它不是银弹：对于需要访问本地 GPU 或特定硬件外设的场景，Docker 容器的网络和硬件穿透会带来额外复杂度；另外早期版本（README 标注 "early development"）的生产稳定性需要实际验证。

**适用场景**：私有代码库的多 Agent 并行开发、需要严格环境隔离的敏感项目、追求本地控制权但又想要容器化隔离的团队。

**不适用**：依赖特殊硬件或需要本地 GPU 的任务、企业级云端 Fleet 统一管理场景。

---

**关联文章**：[Cursor Cloud Development Environments (2026-05-13)](https://cursor.com/changelog/05-13-26) — 同期发布的 Cursor 云端开发环境方案，与 container-use 的本地方案形成对照

---

> 本文原文来自 [dagger/container-use](https://github.com/dagger/container-use)，使用 MCP 协议实现开发环境隔离，2026-05-15 最后更新，3,779 Stars。