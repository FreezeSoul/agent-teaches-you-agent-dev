# Everything Claude Code：AI Agent Harness 的性能优化系统

## 项目背景与解决的问题

AI Agent Harness 是指运行在 AI 模型之上的那层「缰绳」——包括工具定义、prompt 策略、记忆管理、工作流程编排、安全规则等。这层系统的好坏，直接决定了 AI Agent 在真实任务中的表现。

问题是：大多数人对 harness 的优化是凭感觉来的——「加点 system prompt」「加个工具定义」「记忆分段截断」，没有系统化的方法论，也没有可量化的评估标准。更糟糕的是，当你优化了一个维度（比如减少了 token 消耗），往往在另一个维度（任务完成率）引入了新的问题。

**Everything Claude Code（ECC）** 是一个 Anthropic Hackathon 获奖项目，提供了**完整的 harness 性能优化体系**：涵盖技能（Skills）、本能（Instincts）、记忆优化、持续学习、安全扫描和研究优先开发流程。历时超过 10 个月的每日实战打磨，目标是让 harness 的每一次改动都有依据、可验证。

项目规模：140K+ Stars，170K+ Forks，170+ 贡献者，12+ 语言生态，38 个 Agent，156 个技能，72 个传统命令垫片（legacy shims）。

## 核心能力与技术架构

### 核心模块

**1. Skills（技能）系统**

ECC 的技能不是简单的 prompt 模板，而是一套可执行的工作流。覆盖以下领域：

- **Token 优化**：模型选择策略、system prompt 精简、后台进程管理
- **记忆持久化**：Hooks 实现跨会话的上下文自动保存与恢复
- **持续学习**：从每次会话中自动提取模式，沉淀为可复用技能
- **验证循环**：检查点式 vs 持续式评估、grader 类型、pass@k 指标
- **并行化**：Git worktrees、cascade 方法、实例扩展策略
- **子 Agent 编排**：上下文问题、迭代检索模式

**2. Instincts（本能）系统**

Instincts 是 ECC 的自进化机制——让 AI Agent 从实际工作经历中学习，改进行为模式。包含置信度评分、导入/导出、演进机制。

**3. AgentShield 安全体系**

1282 个测试用例，102 条安全规则，覆盖：
- 攻击向量识别
- 沙箱隔离验证
- 输入清洗
- CVE 追踪

`/security-scan` 技能直接集成到 Claude Code 中运行 AgentShield。

**4. 跨 Harness 支持**

ECC 并不绑定 Claude Code，同时支持：
- Claude Code
- OpenAI Codex（CLI + App）
- Cursor
- OpenCode
- Gemini CLI

每个 harness 有对应的安装配置和兼容适配，确保同一套体系在不同工具中的行为一致性。

**5. ECC 2.0 Alpha**

v2.0.0-rc.1 引入了 Rust 实现的控制面原型（`ecc2/`），提供 `dashboard`、`start`、`sessions`、`status`、`stop`、`resume`、`daemon` 等命令。Tkinter 桌面 GUI 提供了主题切换、字体定制和项目 logo 支持。

### 安装架构

ECC 采用了**清单驱动的选择性安装**架构：

- `install-plan.js` + `install-apply.js` 实现精确组件安装
- 状态存储（SQLite）记录已安装内容，支持增量更新
- 不堆叠安装方式（插件路径 + 手动安装混用会导致重复行为）

⚠️ 一个重要警告：Claude Code 插件**无法自动分发 rules**。如果你通过 `/plugin install` 安装了 ECC，需要手动复制 `rules/` 目录到你本地的 `~/.claude/rules/`。ECC 文档对此有详细说明。

## 与同类项目对比

| 维度 | ECC | Cursor Rules / Windsurf Config | Generic Agent Framework |
|------|-----|-------------------------------|----------------------|
| **覆盖范围** | 完整 harness 体系（+安全+并行+记忆） | 单工具配置 | 框架无关 |
| **Token 优化** | 完整方法论 + 工具支持 | 部分 | ❌ |
| **安全扫描** | ✅ AgentShield 集成 | ❌ | 部分 |
| **跨 Harness** | ✅ 6+ 平台 | ❌ | ❌ |
| **Harness 审计** | ✅ `/harness-audit` | ❌ | ❌ |
| **持续学习** | ✅ Instincts 系统 | ❌ | ❌ |
| **社区规模** | 170+ 贡献者，170K Stars | 小 | 中等 |

ECC 和 Superpowers 是互补的：ECC 侧重于 harness 层面（工具、记忆、安全、性能），Superpowers 侧重于开发流程层面（设计、TDD、代码审查）。两者叠加可以构建一个既有工程纪律又有性能优化的 AI 编程环境。

## 适用场景与局限

### 适用场景

- **生产级 AI 编程环境搭建**：当你需要让团队的多个人员使用统一的 harness 配置时，ECC 提供了经过验证的体系
- **Token 成本优化**：在 API 调用量大的场景下，ECC 的 token 优化方法论可以显著降低成本
- **安全敏感的项目**：需要防止 prompt injection、数据泄露等安全问题时，AgentShield 提供了系统化的防护
- **多 harness 迁移**：当你在不同工具之间切换（如从 Claude Code 迁移到 Codex）时，ECC 的跨平台适配能减少迁移成本

### 局限

- **配置复杂度高**：完整安装需要理解多个系统（Skills、Rules、Hooks、Instincts），上手门槛不低
- **Rules 的手动分发**：插件无法自动安装 rules，这是一个已知的架构限制，容易导致新用户困惑
- **版本更新频繁**：项目保持高强度的更新节奏（每月多个版本），需要持续关注变更日志
- **过度优化风险**：当项目不需要极致优化时，ECC 的全套配置可能造成不必要的复杂性

## 一句话推荐

ECC 是目前最完整的 AI Agent Harness 性能优化开源项目，适合那些认真对待 AI 编程工程化的团队和个人——但建议从核心子集开始，逐步引入完整体系。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/affaan-m/everything-claude-code`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：12/15
