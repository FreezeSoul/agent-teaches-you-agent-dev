# addyosmani/agent-skills：让 AI Agent 获得工程师级工作流的 Production-Grade 技能库

## TRIP 四要素

- **T（Target）**：有 Python/JS 经验的 Agent 开发者在生产环境使用 AI Coding 工具（Claude Code/Cursor/GitHub Copilot），但受困于 Agent 输出的代码缺乏工程纪律（无测试、PR 无 review、直接 push 到 main）
- **R（Result）**：通过加载 `DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP` 六阶段工作流，让 Agent 的输出从「能跑」进化到「可合并」——每次 commit 都带测试，每次 PR 都经过 quality gate
- **I（Insight）**：不是教 Agent 新技能，而是**把资深工程师的开发纪律编码成可触发的工作流**——技能通过 slash commands 自动激活（`/spec` 触发 spec-driven-development，`/test` 触发 TDD），而不是靠 Agent 自由发挥
- **P（Proof）**：Addy Osmani（Google Chrome 团队工程总监）亲自维护；被 Cursor/C Claude Code/Gemini CLI/Windsurf/OpenCode/GitHub Copilot 等所有主流 AI Coding 平台官方推荐；README 显示 20 个精炼技能，覆盖完整开发周期

---

## P-SET 骨架

### P - Positioning（定位破题）

**一句话定义**：将软件工程的质量门禁（spec review、test pyramid、code review、security hardening）编码为 AI Agent 可执行的自动化工作流。

**场景锚定**：当你对 Claude Code 说 `/build` 写一个用户认证模块，结果 Agent 直接写完代码写进 main 分支，没有任何测试，没有任何 PR review——这正是 agent-skills 要解决的问题。

**差异化标签**：**唯一被所有主流 AI Coding 平台官方集成的第三方技能库**（Cursor Marketplace、Claude Code Plugin、Gemini CLI native skills）

### S - Sensation（体验式介绍）

当你用 Claude Code 写代码时，现在可以这样操作：

```
/spec 实现一个 JWT 刷新 token 机制
→ Agent 加载 spec-driven-development skill
→ Agent 生成包含：Objectives / Commands / Structure / Code Style / Testing / Boundaries 的 PRD
→ PRD 通过后才进入下一阶段
```

```
/test 用户认证模块
→ Agent 加载 test-driven-development skill
→ Agent 先写 test（RED），再写实现（GREEN），最后重构（REFACTOR）
→ 测试金字塔：80% 单元测试 / 15% 集成测试 / 5% E2E
```

```
/review
→ Agent 加载 code-review-and-quality skill
→ Agent 对 PR 做五轴 review：Correctness / Safety / Performance / Maintainability / Security
→ NIT / Optional / FYI / Must-Fix severity分级
```

这就是 agent-skills 的核心价值——**把开发流程从「自由发挥」变成「强制执行的质量门禁序列**。

### E - Evidence（拆解验证）

**技能体系**：20 个技能，分为 6 个阶段 + 5 个专项：

| 阶段 | 技能 | 核心内容 |
|------|------|---------|
| DEFINE | idea-refine | 结构化发散/收敛思维，把模糊想法变成具体提案 |
| DEFINE | spec-driven-development | PRD 覆盖：Objectives/Commands/Structure/Code Style/Testing/Boundaries |
| PLAN | planning-and-task-breakdown | 任务分解为可验证的小单元，含 acceptance criteria |
| BUILD | incremental-implementation | Thin vertical slice，feature flag，safe rollback |
| BUILD | test-driven-development | Red-Green-Refactor，80/15/5 测试金字塔 |
| BUILD | context-engineering | 规则文件、context packing、MCP 集成 |
| BUILD | frontend-ui-engineering | 组件架构、设计系统、WCAG 2.1 AA |
| BUILD | api-and-interface-design | 契约优先设计、Hyrum's Law、One-Version Rule |
| BUILD | source-driven-development | 框架决策基于官方文档，引用溯源 |
| VERIFY | browser-testing-with-devtools | Chrome DevTools MCP，DOM 检查、日志、网络追踪 |
| VERIFY | debugging-and-error-recovery | 五步 triage：reproduce/localize/reduce/fix/guard |
| REVIEW | code-review-and-quality | 五轴 review，~100 行/changeset，severity 分级 |
| REVIEW | code-simplification | Chesterton's Fence，Rule of 500 |
| REVIEW | security-and-hardening | 自动安全扫描、CVE 检测 |
| SHIP | deployment-and-environment-setup | 生产部署、环境隔离 |
| SHIP | monitoring-and-observability | 日志、追踪、指标 |

**跨平台支持**：README 列出 9 个平台的安装方式，这是 agent-skills 与其他技能库的核心差异——它不是一个特定 Agent 的插件，而是一个**跨平台技能格式标准**。

> "Claude Code (recommended) / Cursor / Gemini CLI / Windsurf / OpenCode / GitHub Copilot / Kiro IDE & CLI / Codex / Other Agents"

### T - Threshold（行动引导）

**快速上手**（Claude Code）：
```bash
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

然后使用 `/spec`、`/plan`、`/build`、`/test`、`/review`、`/ship` 任一命令激活对应技能。

**如果你想自己开发技能**：参考 `skills/` 目录下的现有 SKILL.md 格式，关键约束：
1. YAML frontmatter 必须包含 `name` 和 `description`（这是 L1 层索引）
2. 技能主体是 Markdown，包含具体步骤和验证条件
3. 可以引用同目录下的其他文件（L3 层，按需加载）

---

## 主题关联性说明

本文与同期发布的 [Anthropic Agent Skills 渐进式披露架构分析](../../fundamentals/anthropic-agent-skills-progressive-disclosure-architecture-2026.md) 共同探讨「技能系统」的工程实现：

- **Anthropic Agent Skills**：协议层设计（渐进式披露的上下文分层架构）
- **addyosmani/agent-skills**：实现层设计（生产级工作流的技能内容库）

两者关系：**Anthropic 解决了「如何让 Agent 高效加载技能」的问题，addyosmani 解决了「技能本身应该包含什么内容」的问题**。前者是架构规范，后者是内容实现——组合起来才构成完整的 Agent Skills 生态。

---

*推荐基于 [addyosmani/agent-skills README](https://github.com/addyosmani/agent-skills) 和 Anthropic Agent Skills 官方文档*