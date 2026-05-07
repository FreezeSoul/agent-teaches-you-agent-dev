# Gizele1/harness-init：OpenAI Harness Engineering 的工程化实现

## 一句话评价

将 OpenAI 的 Harness Engineering 方法论转化为可执行的 8 阶段脚手架——让任何代码仓库在 5 分钟内变成 Agent-ready 环境，适用于 Claude Code / Codex / Cursor。

## 为什么这个项目值得关注

2026 年 2 月，OpenAI 发布了"Harness Engineering"方法论，核心观点是"工程师变成环境设计者，而非代码实现者"。但方法论需要落地工具——`harness-init` 正是这个缺口。

它将 OpenAI 五个月实证经验压缩为一个可执行的初始化流程：检测栈 → 构建 AGENTS.md → 建立 docs/ 知识库 → 架构边界测试 → Linting → CI → 垃圾回收 → Hooks。8 个阶段，循序渐进。

## 核心设计理念（来自项目 README）

### 1. "给 Agent 地图，而非百科全书"

> "Give agents a map, not an encyclopedia — AGENTS.md ~100 lines, progressive disclosure"
> — [harness-init README](https://github.com/Gizele1/harness-init)

OpenAI 在实战中发现，把所有规则塞进 AGENTS.md 会导致上下文拥挤，Agent 反而找不到重点。正确的做法是让 AGENTS.md 作为目录（约 100 行），指向 docs/ 中的深层文档。

harness-init 将这个原则工程化：AGENTS.md 作为入口索引，docs/ 作为系统知识记录。

### 2. "如果 Agent 看不到，它就不存在"

> "If agents can't see it, it doesn't exist — all knowledge machine-readable in repo"
> — [harness-init README](https://github.com/Gizele1/harness-init)

这是 OpenAI 最深刻的教训之一：在 Agent 的执行上下文中，只有 repo 内可发现的内容才算存在。Google Docs、Slack 讨论、工程师的脑中知识——对 Agent 来说都是不可见的。

harness-init 将这个原则转化为具体的目录结构要求：
```
docs/
├── architecture/LAYERS.md      # 权威的依赖层次定义
├── golden-principles/           # DO/DON'T 模式，30-60 行每个
├── SECURITY.md                 # 认证、密钥、威胁模型
├── guides/                     # 安装、测试、部署指南
└── exec-plans/                 # 执行计划生命周期
```

### 3. "机械性执行架构，而非用 Markdown 文档"

> "Enforce architecture mechanically, not via markdown — linters and tests, not prose"
> — [harness-init README](https://github.com/Gizele1/harness-init)

架构约束如果只是文档，Agent 会忽略它们。harness-init 要求用 Linter 和测试来机械性执行层间依赖方向。错误消息被设计为向 Agent 注入修复指令——不是告诉它"你违反了规则"，而是告诉它"如何修复"。

### 4. "无聊的技术胜出"

> "Boring technology wins — composable, stable, well-trained-on APIs"
> — [harness-init README](https://github.com/Gizele1/harness-init)

OpenAI 在五个月实验中发现：Agent 更擅长处理组合性好、API 稳定、训练数据充足的技术。这种技术选择原则不是为了"安全"，而是为了让 Agent 能更准确地建模和操作。

### 5. "Entropy management 就是垃圾回收"

> "Entropy management is garbage collection — periodic scans catch drift"
> — [harness-init README](https://github.com/Gizele1/harness-init)

完全由 Agent 生成的代码会复制已有的模式，包括不均匀或次优的模式。harness-init 将 OpenAI 的 Entropy Management 具象化为定期扫描脚本和每周 CI 任务。

## 8 阶段执行流程

| 阶段 | 内容 | 产物 |
|------|------|------|
| Phase 0 | Discovery — 检测栈、映射架构、识别层次、注入动态上下文 | 堆栈分析报告 |
| Phase 1 | AGENTS.md — ~100 行方向地图（索引，非百科全书） | AGENTS.md |
| Phase 2 | docs/ — 系统记录：architecture/LAYERS.md + golden-principles/ + SECURITY.md + guides/ | 知识库目录 |
| Phase 3 | Testing — 带棘轮机制的架构边界测试 | boundary.test.* |
| Phase 4 | Linting — 带修复指令的导入限制规则 | lint 规则 |
| Phase 5 | CI — 并行 lint + typecheck + test + build pipeline | ci.yml |
| Phase 6 | GC — 垃圾回收脚本 + 每周计划扫描 | gc.yml |
| Phase 7 | Hooks — Pre-commit 强制执行 | pre-commit hooks |

## 文件结构（harness-init 的目标状态）

```
project-root/
├── AGENTS.md                    # ~100 行，方向地图 [必须]
├── ARCHITECTURE.md              # 顶级域地图 [必须]
├── docs/
│   ├── architecture/
│   │   └── LAYERS.md            # 权威层次定义，机械执行 [必须]
│   ├── golden-principles/       # DO/DON'T 模式 [必须]
│   ├── SECURITY.md              # 认证和威胁模型 [必须]
│   ├── guides/                  # 设置/测试/部署指南 [推荐]
│   ├── exec-plans/
│   │   ├── active/              # 活跃计划
│   │   ├── completed/           # 完成计划
│   │   └── tech-debt-tracker.md
│   ├── design-docs/
│   │   ├── index.md
│   │   ├── core-beliefs.md      # 不可违反的核心信念
│   │   └── {NNNN-title}.md      # ADR 格式
│   └── references/             # LLM 用的外部文档
├── scripts/gc/                  # 垃圾回收脚本
├── tests/architecture/
│   └── boundary.test.*          # 机械性层强制测试
└── .github/workflows/
    ├── ci.yml                   # lint + typecheck + test + build
    └── gc.yml                   # 每周 entropy 扫描
```

## 与 OpenAI 原始文章的对照

| OpenAI 原始 | harness-init 改进 | 原因 |
|-------------|------------------|------|
| FRONTEND.md | docs/STACK.md | 栈无关命名，适用于后端、移动端等 |
| .agent/PLANS.md | docs/exec-plans/ | 目录生命周期支持多功能项目 |
| 扁平 docs/ | 分层 docs/ 带优先级 | Agent 知道什么是核心什么是可选 |
| 无 ADR | docs/design-docs/ ADR 格式 | 捕获 Architectural Decision Records |
| 无安全文档 | docs/SECURITY.md 作为必须项 | 安全上下文对 Agent 安全不可选 |

## 使用方式

### Claude Code
```bash
claude plugin marketplace add https://github.com/Gizele1/harness-init.git
claude plugin install harness-init@harness-init
# 然后：/harness-init full
```

### 手动执行
```bash
git clone --depth 1 https://github.com/Gizele1/harness-init.git /tmp/harness-init
mkdir -p .claude/skills/harness-init/references
cp /tmp/harness-init/skills/harness-init/SKILL.md .claude/skills/harness-init/
cp /tmp/harness-init/skills/harness-init/references/*.md .claude/skills/harness-init/references/
```

### 在 Claude Code 中
```
/harness-init           # 交互式——询问要设置什么
/harness-init full      # 完整设置，所有阶段
/harness-init 2         # 仅特定阶段
/harness-init 3-4       # 阶段范围
```

或者简单地说：
- "harness init this repo"
- "make this repo agent-ready"
- "set up architecture boundaries"

## 适用场景

harness-init 是一个**仓库初始化工具**，适合以下场景：

1. **新项目启动**：开始一个新项目时，快速建立 Agent-ready 的基础架构
2. **遗留代码库改造**：将现有项目转化为 Agent 友好的环境（Phase 0 Discovery 会检测实际堆栈）
3. **团队标准化**：在团队中建立统一的 Agent 工作环境规范

它不涵盖的内容（项目已明确定义边界）：
- 运行时可读性（启动应用、浏览器/CDP 验证）
- 可观测性集成（Agent 可查询的日志/指标/traces）
- Agent review loops（Agent-to-Agent PR review）
- 自动回归验证
- PR 反馈迭代循环

## 关联知识

- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/) — 原始方法论
- [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) — Feedforward + Feedback 框架分析
- [OpenAI Cookbook: Using PLANS.md](https://developers.openai.com/cookbook/articles/codex_exec_plans) — 多小时问题解决的执行计划

## 基础信息

| 项目 | 信息 |
|------|------|
| GitHub | [Gizele1/harness-init](https://github.com/Gizele1/harness-init) |
| 许可证 | MIT |
| 适用工具 | Claude Code, Codex, Cursor |
| 方法论来源 | OpenAI Harness Engineering (Feb 2026) |