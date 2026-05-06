# Apra Fleet：MCP 原生的多 Agent 协作编排框架

> **关联主题**：Cursor 第三时代工厂思维 → 多机 Agent 协作的实际工程路径

## TRIP 要素

**Target**：在使用 Claude Code 时遇到「单机器瓶颈」的开发者——当你需要并行跑多个 Agent、跨机器协调任务、或实现 Doer-Reviewer 双角色协作时，Apra Fleet 填补了这个缺口。

**Result**：将 Claude Code 的单会话扩展为跨多台机器的 Agent 团队，每个成员通过 SSH 连接，一个对话界面统一指挥；解决了 Anthropic 自身在 GitHub Issue #28300 中承认的「跨机器多 Agent 协作」需求。

**Insight**：传统方案用独立 Dashboard 或 YAML 配置管理多 Agent，Apra Fleet 的核心洞察是**让多机协调回归对话本身**——你只需告诉 Fleet「让 doer 机写代码，reviewer 机审查」，它自动完成注册、连接、任务分发和状态同步。

**Proof**：GitHub 35 Stars，Apache 2.0 开源许可，TypeScript 实现，macOS/Linux/Windows 全平台支持，MCP 官方兼容标识。

---

## P-SET 结构

### P - Positioning

**一句话定义**：基于 MCP 协议的多机 Agent 协作编排工具——将多个 Claude Code/Gemini/Codex 实例注册为 Fleet Members，通过 SSH 跨机器协调，实现 Doer-Reviewer 协作工作流。

**场景锚定**：当你想要「在一个对话里指挥多台机器的 Agent」时；当你需要「一个写代码、另一个审查」的自动化协作流程时；当你想在本地开发的同时让云端 VM 跑测试或编译时。

**差异化标签**：MCP 原生 + 对话式编排（用自然语言指挥跨机器 Agent 团队，而非配置 YAML）

### S - Sensation

安装 Apra Fleet 后，你的 Claude Code 会多出一个 `/mcp` 入口。注册成员的方式非常自然：

```
你：「注册一个叫 doer 的本地成员，工作目录 ~/projects/myapp」
你：「再注册一个叫 reviewer 的本地成员」
你：「让 doer 构建 auth 模块，reviewer 进行审查」
```

Fleet 会自动：
1. 在后台启动两个独立的 Agent 会话
2. 让 doer 先执行，完成后暂停在 checkpoint
3. 将产物交给 reviewer 评估
4. 根据评估结果决定是否返工或通过

跨机器协作同样简单——只需提供 SSH 连接信息：

```
你：「注册 192.168.1.10 为 build-server，用户名 akhil，工作目录 /home/akhil/projects」
你：「在 build-server 上运行测试套件，修复任何失败」
```

Fleet 通过 SSH 在远程机器上执行命令，结果返回到你的本地对话。

**Provider 混搭**是另一个亮点：Planner/PM 建议用 Claude Opus/Sonnet（强推理），Doer 可以用任何模型（ Sonnet/Flash/Codex/Copilot），Reviewer 建议用高端模型（捕捉细微问题）。这与 Anthropic 的三 Agent 架构（Planner-Generator-Evaluator）形成对应。

### E - Evidence

**技术架构**：

Apra Fleet 是一个 MCP Server，它管理一个「成员注册表」：

| 组件 | 职责 |
|------|------|
| **Member Registry** | 跟踪所有注册的机器/工作区（本地或 SSH 远程） |
| **Fleet Server** | MCP Server 核心，接收指令并分发到各成员 |
| **PM Skill** | 可选的 Project Manager Skill，提供结构化工作流（Planning → Doer-Reviewer → Checkpoint → Progress） |
| **Beads (bd CLI)** | 本地 Issue Tracker，PM 自动创建 Epic/Task，状态跨会话持久化 |

**Doer-Reviewer 工作流的技术实现**：

```
User Prompt → PM Skill 分解任务 → Doer Agent 执行 → Checkpoint 暂停 
→ Reviewer Agent 评估 → 通过则结束 / 失败则返工
```

每个变更在合并前都经过独立审查——这直接呼应了 Anthropic 的发现：**「Agent 无法公正评价自己的工作，将 Evaluator 独立出来后评估质量大幅提升」**。

**跨机器 SSH 连接**：

```bash
# 注册远程成员
Fleet.register_member(
    name="build-server",
    host="192.168.1.10",
    username="akhil",
    auth="password",  # 或 "key"
    work_folder="/home/akhil/projects/myapp"
)

# 在远程执行
Fleet.execute_prompt(
    member="build-server",
    prompt="运行测试套件，修复任何失败"
)
```

**平台支持**：

| 平台 | 安装方式 |
|------|---------|
| macOS (Apple Silicon) | `apra-fleet-installer-darwin-arm64` |
| Linux (x64) | `apra-fleet-installer-linux-x64` |
| Windows (x64) | `apra-fleet-installer-win-x64.exe` |

一键安装后自动配置 MCP Server、Shell Hooks、Status Bar 图标和 Skill 文档。

### T - Threshold

**快速上手（3 步）**：

1. **安装**（一键）：
   ```bash
   curl -fsSL https://github.com/Apra-Labs/apra-fleet/releases/latest/download/apra-fleet-installer-linux-x64 -o apra-fleet-installer && chmod +x apra-fleet-installer && ./apra-fleet-installer install
   ```

2. **在 Claude Code 加载 MCP**：
   ```
   /mcp
   ```

3. **注册并使用**：
   ```
   「注册一个本地成员叫 doer」
   「注册另一个叫 reviewer」
   「让 doer 构建 auth 模块，reviewer 审查」
   ```

**不适合场景**：
- 需要复杂 DAG 编排（非对话式）的任务
- Windows 远程 + 复杂 SSH 密钥管理
- 完全离线环境（GitHub 下载受限）

**开源贡献**：
- GitHub: `Apra-Labs/apra-fleet`
- License: Apache 2.0
- 欢迎 Issue/PR，尤其是多模态 Provider 集成

---

## 关联分析

**为什么这个项目重要？**

Anthropic 的 Claude Code 团队在 GitHub Issue #28300 中明确承认：
> "We hit this exact wall and ended up building Apra Fleet as an open-source MCP server"

这意味着 Apra Fleet 解决的是一个**被官方认可的工程缺口**：Claude Code 擅长单 Agent 单机器任务，但当需要「跨机器协作」时，社区必须自己搭方案。

**与 Cursor 第三时代的关联**：

Cursor 3 提出的「第三时代」核心是「Factory of Agents」——多 Agent 舰队协同工作。Apra Fleet 提供了这种协作模式的开源实现路径：
- Cursor 3 的 Sidebar 多 Agent 管理 → Apra Fleet 的 Member Registry
- Cursor 3 的 Cloud Agents → Apra Fleet 的 SSH 远程成员
- Cursor 3 的 Agent Review 机制 → Apra Fleet 的 Doer-Reviewer 循环

**与 Anthropic 三 Agent 架构的对应**：

| Anthropic 三 Agent | Apra Fleet 实现 |
|---------------------|-----------------|
| Planner Agent | PM Skill（Planning 阶段） |
| Generator Agent | Doer Agent（执行阶段） |
| Evaluator Agent | Reviewer Agent（审查阶段） |

---

## 引用来源

> "Apra Fleet is an open-source MCP server that pairs AI coding agents into doer-reviewer loops for higher quality code, and orchestrates them across machines via SSH when you need distributed power."
> — [Apra Fleet GitHub README](https://github.com/Apra-Labs/apra-fleet)

> "An Agent-to-Agent protocol built on top of MCP, enabling: Shared Workspace / Channel: Multiple Claude Code instances join a shared collaboration channel (via MCP server or similar)."
> — [Anthropic Claude Code GitHub Issue #28300](https://github.com/anthropic/claude-code/issues/28300)
