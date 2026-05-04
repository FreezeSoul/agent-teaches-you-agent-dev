# Nonstop Agent：让 Claude 跨越多 session 持续工作的 Long-Running Harness

## 一、定位破题（Positioning）

**一句话定义**：基于 Anthropic 2026 工程实践的开源实现——一个让 Claude Code 能够跨多个上下文窗口连续工作数天/数周的 autonomous agent harness。

**场景锚定**：当你需要 Claude 完成一个需要 50+ 小时工作时间的功能时（比如实现一个完整的 SaaS 后台、构建一个嵌入式系统固件），单次对话的上下文窗口根本装不下全部历史。Nonstop Agent 解决了"Agent 在长时间任务中迷路"这个根本问题。

**差异化标签**：最忠实地实现了 Anthropic 官方工程博客中的 two-agent pattern，而非另起炉灶造概念。

---

## 二、体验式介绍（Sensation）

想象这个场景：你在周五下午 5 点给 Claude 一个任务"实现一个完整的电商后台管理系统"，然后下班。周一早上 9 点你回来，Claude 已经完成了 70% 的功能，每个 session 都有清晰的 git commit 和 progress 文件记录。

这个场景在 Nonstop Agent 中是这样运转的：

**Session 1（Initializer Agent）**：
1. 读取 `app_spec.txt`（你写的需求文档）
2. 生成 `feature_list.json` — 把"电商后台"拆解成 200+ 个可验证的功能点，每个初始状态为 `passes: false`
3. 创建项目结构 + 执行初始 git commit
4. 创建 `claude-progress.txt` 用于记录进展

**Session 2, 3, 4...（Coding Agent）**：
1. 读取 git log 和 progress 文件 → 快速了解"上次做到哪了"
2. 从 feature_list.json 选优先级最高且 `passes: false` 的功能
3. **一次只做一个功能** → 避免半成品积累
4. 用 Puppeteer 做端到端验证 → 确保功能真的能用
5. git commit + 更新 progress

> "This project is inspired by and built upon: Anthropic Engineering: Effective Harnesses for Long-Running Agents" 
> — [Nonstop Agent README](https://github.com/seolcoding/nonstop-agent)

---

## 三、拆解验证（Evidence）

### 技术架构：三文件 + 双 Agent + 安全三层

Nonstop Agent 的核心设计浓缩为"状态持久化三文件"：

| 文件 | 职责 | 设计来源 |
|------|------|---------|
| `app_spec.txt` | 原始需求（不可变）| Anthropic 工程博客 |
| `feature_list.json` | 功能清单（只增不改）| Anthropic 工程博客 |
| `claude-progress.txt` + git history | 进展记录 | Anthropic 工程博客 |

**双 Agent 角色分离**：
- Initializer Agent：首次运行，负责搭建项目骨架和功能清单
- Coding Agent：后续每个 session，一次只做一件事，然后验证、提交

**防御性安全三层**：
```
Layer 1: OS-Level Sandbox — 隔离 bash 命令执行
Layer 2: Filesystem Restrictions — 操作限制在项目目录内
Layer 3: Command Allowlist — 只有明确允许的命令才能执行
```

> "Defense-in-Depth Security: Multi-layered security with sandbox, permissions, and command allowlists"
> — [Nonstop Agent README](https://github.com/seolcoding/nonstop-agent)

### 与 Anthropic 官方实现的对应关系

| Nonstop Agent 实现 | Anthropic 原文描述 |
|-------------------|-------------------|
| `uv add nonstop-agent` 或 Claude Code plugin | GitHub: [anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding) |
| `feature_list.json` | "We prompted the initializer agent to write a comprehensive file of feature requirements" |
| 2-Agent Pattern | "Initializer agent that sets up the environment... and a coding agent that is tasked with making incremental progress" |
| git commit after each feature | "Ask the model to commit its progress to git with descriptive commit messages" |

### 部署灵活性

支持两种使用方式：
- **作为 Python 包**：`uv add nonstop-agent`，可在任何 Python 环境中调用
- **作为 Claude Code Plugin**：直接从 marketplace 安装，在 Claude Code 中用自然语言激活

---

## 四、行动引导（Threshold）

### 快速启动（3 步跑起来）

**Step 1：安装**
```bash
# 推荐用 uv
uv add nonstop-agent

# 或作为 Claude Code Plugin
/plugin marketplace add seolcoding/nonstop-agent
/plugin install nonstop-agent@seolcoding/nonstop-agent
```

**Step 2：准备 OAuth Token**
```bash
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN="your-token-here"
```

**Step 3：启动**
```bash
# 新项目
uv run nonstop-agent --project-dir ./my_project

# 恢复之前的 session
uv run nonstop-agent --project-dir ./my_project --resume
```

### 适用边界判断

**✅ 适合的场景**：
- 任务需要跨越多天/多周，复杂到单个 context window 装不下
- 需要可验证的完整性保证（feature_list.json 确保没有功能被遗漏）
- 使用 Claude Code 作为基础模型

**❌ 不适合的场景**：
- 短时任务（< 1 小时）：Nonstop Agent 的初始化开销不划算
- 非 Claude 模型：项目明确针对 Claude Agent SDK 设计
- 需要多 Agent 协作的复杂工作流：当前实现是单 Agent 串行执行

---

## 五、与 Articles 的关联

本文推荐的 Nonstop Agent 直接对应本轮 Articles 的分析主题——**Anthropic 的 two-agent pattern 和 feature_list 机制**。Nonstop Agent 是这一工程实践的开源实现版本，它把 Anthropic 博客中的设计原则转化成了可运行的代码。

Articles 分析了"为什么这套设计能work"（压缩历史无法保证完整性、不可变性防误触），Projects 推荐展示了"如何把这个设计用起来"（Python 包 + Claude Code Plugin 双模式、feature_list.json 格式示例）。

**引用来源**：
- [Nonstop Agent GitHub](https://github.com/seolcoding/nonstop-agent)
- [Anthropic Engineering: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic Claude Quickstarts - Autonomous Coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)