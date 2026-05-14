# oh-my-agent：跨 IDE 的便携式多 Agent 编排框架

> 本文推荐 [first-fluke/oh-my-agent](https://github.com/first-fluke/oh-my-agent)，944 ⭐，一个将 Agent 编排从单一 IDE 解锁并泛化的多 Agent 工作流框架。与 Codex Windows 沙箱的文章主题（harness 工程的平台差异与设计权衡）形成呼应——当沙箱解决「隔离」问题时，oh-my-agent 解决的是「编排」问题。

---

## 一、项目定位：Agent 团队，而非单个 Agent

oh-my-agent 的核心洞察是：**单个 Agent 容易在中途混淆，尤其是任务复杂度上升时**。

> "Instead of one AI doing everything (and getting confused halfway through), oh-my-agent splits work across **specialized agents** — frontend, backend, architecture, QA, PM, DB, mobile, infra, debug, design, and more."
> — [oh-my-agent README](https://github.com/first-fluke/oh-my-agent)

项目将 Agent 重新定义为「角色团队」：每个角色（oma-frontend、oma-backend、oma-db 等）有自己独立的工具集、检查清单和职责边界。PM 先规划，后端构建 API，QA 审查——这与 OpenAI 在 Codex Windows 沙箱中展示的分层设计（harness 层 → 执行层 → 隔离层）有相似的结构化思维。

---

## 二、技术架构：.agents/ SSOT + 双层分发

### .agents/ SSOT（单一真实来源）

项目以 `.agents/` 目录作为所有技能、工作流和配置的单一真实来源：

```
.agents/
├── oma-config.yaml          # 全局配置
├── skills/                   # 各角色的 skill 定义
│   ├── oma-frontend/
│   ├── oma-backend/
│   ├── oma-db/
│   └── ...
└── workflows/               # 预定义工作流
```

这个设计的优势在于：**.agents/ 目录是可移植的**——它随项目移动，不绑定在任何单一 IDE 的配置系统中。Codex、Windows沙箱中的 harness 配置与项目紧耦合，但 oh-my-agent 通过将配置抽离为可移植单元，实现了 harness 的跨项目复用。

### 双层模型分发

```
Layer 1: Same-vendor native dispatch
  → .claude/agents/, .codex/agents/, .gemini/agents/ 中的 vendor 原生定义

Layer 2: Cross-vendor or fallback CLI dispatch
  → .agents/skills/oma-orchestrator/config/cli-config.yaml 中的 vendor 默认配置
```

这意味着可以在同一个团队中让 oma-frontend 使用 Claude，oma-backend 使用 GPT-5.5，oma-architecture 使用 Gemini——每个角色选择最合适的模型，而非强制整个团队使用同一模型。

> "Mix Gemini, Claude, Codex, and Qwen per agent type"
> — 同上 README

---

## 三、核心工作流设计

### Slash Commands（6 个核心阶段）

| 阶段 | Command | 功能 |
|------|---------|------|
| 0 | `/deepinit` | 引导现有代码库（AGENTS.md, ARCHITECTURE.md, docs/） |
| 1 | `/brainstorm` | 自由形式头脑风暴 |
| 2 | `/architecture` | 软件架构评审（ADR/ATAM/CBAM 风格分析） |
| 2 | `/plan` | PM 分解任务为子任务，定义 API 契约 |
| 3 | `/work` | 逐步执行多 Agent |
| 3 | `/orchestrate` | 自动并行 Agent 生成 |
| 3 | `/ultrawork` | 5 阶段质量工作流，11 个评审门控 |
| 4 | `/review` | 安全 + 性能 + 可访问性审计 |
| 5 | `/debug` | 结构化根因调试 |

**质量门控设计**值得特别注意：`/ultrawork` 内置了 11 个评审门控，每次代码变更都需要经过同行评审才能进入下一阶段。这与 Codex Windows 沙箱的「分层提权」设计有相似的工程思维——**不是在终点做一次检查，而是将检查点分布到整个执行路径中**。

### Auto-Detection：无 slash 命令也能工作

项目支持通过自然语言关键词（11 种语言）自动激活对应工作流：

```
"帮我架构一下这个系统" → 自动触发 /architecture
"有个 bug 需要调查" → 自动触发 /debug
"review 这段代码" → 自动触发 /review
```

这降低了团队的学习成本——不需要记住精确的命令格式。

---

## 四、Agent 角色矩阵

| Agent | 职责 | 关键能力 |
|-------|------|---------|
| **oma-architecture** | 架构权衡分析 | ADR/ATAM/CBAM 感知 |
| **oma-backend** | API 开发 | Python, Node.js, Rust |
| **oma-frontend** | React/Next.js 前端 | TypeScript, Tailwind CSS v4, shadcn/ui |
| **oma-db** | Schema 设计 | migrations, indexing, vector DB |
| **oma-pm** | 任务规划 | 需求分解，API 契约定义 |
| **oma-qa** | 安全+性能+可访问性审查 | OWASP 标准 |
| **oma-debug** | 根因分析 | 回归测试，修复验证 |
| **oma-deepsec** | Agent 驱动的漏洞扫描 | PR gate + 自定义 matcher |
| **oma-scm** | Git 工作流 | branching, merges, worktrees, Conventional Commits |
| **oma-orchestrator** | 并行执行 | CLI 驱动的多 Agent 协调 |

---

## 五、与 Codex Windows 沙箱的关联性

为什么一个讲「沙箱隔离」的文章，要推荐一个「多 Agent 编排」的项目？因为两者解决的是同一个问题的不同维度：

| 问题维度 | Codex Windows 沙箱 | oh-my-agent |
|---------|-------------------|-------------|
| **隔离** | 如何让单个 Agent 的文件/网络访问受限 | 如何让多个 Agent 各司其职、互不越界 |
| **编排** | Harness 层如何分发命令到受控进程 | Orchestrator 层如何分发任务到专业角色 |
| **平台差异** | Windows 原生机制不足，需要从第一性原理构建 | 多 IDE（Claude Code/Cursor/Codex/Gemini CLI）原生机制各异，需要统一抽象层 |
| **设计原则** | 接受「setup 提权」换取「runtime 安全」 | 接受「角色边界清晰」换取「大规模协作效率」 |

两者都在回答一个问题：**当 Agent 的能力边界扩大时，如何设计 harness/framework 来维持可控性**。

---

## 六、快速上手

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/first-fluke/oh-my-agent/main/cli/install.sh | bash

# Windows (PowerShell)
irm https://raw.githubusercontent.com/first-fluke/oh-my-agent/main/cli/install.ps1 | iex

# 或使用 bunx
bunx oh-my-agent@latest
```

```bash
# 选择预设
oma setup --preset fullstack   # architecture + frontend + backend + db + pm + qa + debug + brainstorm + scm

# 开始工作
oma plan "Build a TODO app with user auth"  # PM 分解任务
oma orchestrate                            # 并行启动各角色 Agent
oma review                                 # QA + 安全审计
```

---

## 七、项目健康度

| 指标 | 数值 | 说明 |
|------|------|------|
| GitHub Stars | 944 | 中等规模，但增长稳健 |
| License | MIT | 完全开源 |
| 多语言支持 | 11 种语言 | README 有完整翻译 |
| 包管理器 | npm（oh-my-agent）| 一键安装 |
| 文档 | 完整（韩/中/葡/日/法/西/荷/波/俄/德/越/泰）| 国际化程度高 |
| CI/CD 集成 | Daytona（沙箱）+ GitHub Actions | 可观测性内置 |

---

## 结论

oh-my-agent 是一个**专注于解决 Agent 规模化协作问题**的框架。当大多数工具在讨论「如何让单个 Agent 更快更强」时，它选择了一个更有结构性价值的路径：**将 Agent 从业者转变为团队角色**。

对于需要管理复杂多角色协作的开发团队，这是一个值得关注的工具——尤其是它与平台无关的设计（Claude Code/Cursor/Codex/Gemini CLI 均可使用），能够在保持 harness 一致性的同时利用各平台的最强模型。

> 项目地址：https://github.com/first-fluke/oh-my-agent