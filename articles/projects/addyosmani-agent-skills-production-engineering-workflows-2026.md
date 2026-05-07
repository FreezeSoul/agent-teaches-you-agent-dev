# addyosmani/agent-skills：让 AI Coding Agent 拥有工程判断力

> **目标用户**：有 Python 经验的 AI Coding Agent 用户，希望从"能写代码"进化到"会做工程"
> **核心成果**：将 Google 二十年工程文化蒸馏为 20 个可验证的 Skill 工作流，AI Coding Agent 的工程完成度从"原型级"提升到"生产级"
> **技术亮点**：不是给 Agent 灌输知识，而是给它可执行的工程判断框架——Skills 驱动工作流而非知识填充上下文
> **实证支撑**：GitHub 1,500+ ⭐，9 大平台官方推荐（Claude Code、Cursor、Gemini CLI、Windsurf、Github Copilot）

---

## 一、为什么需要 agent-skills

AI Coding Agent 最大的问题不是能力不足，而是**判断力缺失**。

当你让一个资深工程师修复 bug 时，他会先问：这 bug 从哪来？有没有测试覆盖？改完会不会影响别的模块？但 AI Coding Agent 默认的反应是什么？直接动手改，改完说"完成了"。

这背后的原因是：**Agent 被优化为生成最短路径，而非遵循工程最佳实践**。它不知道什么时候该写测试，不知道 code review 的价值，不知道"更快更安全"的 CI/CD 原则。

addyosmani/agent-skills 试图解决的就是这个问题——不是让 Agent 知道更多，而是让它在正确的时间做正确的事。

官方 README 的定义精准地捕捉到了这一理念：

> "AI coding agents default to the shortest path - which often means skipping specs, tests, security reviews, and the practices that make software reliable. Agent Skills gives agents structured workflows that enforce the same discipline senior engineers bring to production code."
> — [GitHub README](https://github.com/addyosmani/agent-skills)

---

## 二、TRIP 四要素拆解

### T - Target（谁该关注）

目标用户画像：
- **有编程经验的开发者**，刚引入 AI Coding Agent（如 Claude Code、Cursor、Windsurf）
- **已有 Agent 使用经验**，但发现 Agent 输出的代码"能用但不好看，能跑但不可维护"
- **追求工程质量的团队**，希望 AI 辅助不降低代码质量标准

水平要求：需要理解基本工程概念（Git、CI/CD、测试金字塔），但不需要专家级经验——Skills 本身就是工程经验的载体。

### R - Result（带来什么改变）

核心改变是**工程完成度的质变**，而非某个具体指标的提升：

| 维度 | 无 Skills | 有 Skills |
|------|----------|-----------|
| 新功能开发 | 实现功能，可能忽略测试 | Spec → Impl → Test → Debug → Review → Ship |
| Bug 修复 | 改完就跑，没有回归检测 | 五步 triage：reproduce → localize → reduce → fix → guard |
| 代码质量 | "能用就行" | Chesterton's Fence + Rule of 500 主动简化 |
| 安全问题 | 忽略用户输入处理 | OWASP Top 10 + 三层边界系统 |
| 上线流程 | 手动部署 | Feature flag → Staged rollout → Rollback procedure |

GitHub 数据：1,500+ Stars，持续增长，2026 年 5 月进入 GitHub Trending。

### I - Insight（凭什么做到）

Skills 的设计哲学核心是三个字：**Process, not prose**。

Skills 不是参考文档，而是**工作流本身**。每个 Skill 包含：
- 触发条件（When to Use）
- 步骤（Process）
- 退出标准（Verification，非"看起来不错"）
- 常见借口 + 反驳（Anti-rationalization）
- 红旗标识（Red Flags）

这意味着 Agent 收到的不再是"应该怎么做"的知识描述，而是"现在要做什么"的行动指令。

官方描述的设计选择：

> "Every skill follows a consistent anatomy: Process, not prose. Skills are workflows agents follow, not reference docs they read. Each has steps, checkpoints, and exit criteria. Anti-rationalization. Every skill includes a table of common excuses agents use to skip steps (e.g., 'I'll add tests later') with documented counter-arguments. Verification is non-negotiable. Every skill ends with evidence requirements - tests passing, build output, runtime data. 'Seems right' is never sufficient."
> — [GitHub README](https://github.com/addyosmani/agent-skills)

Skills 编码的工程文化来自 Google 的精华：
- **Hyrum's Law**：API 设计时考虑隐性依赖
- **Beyonce Rule**：测试用真实数据，别用"test test test"
- **测试金字塔**：80/15/5（单元/集成/E2E）
- **Change sizing**：~100 行变更，便于 review
- **Shift Left**：质量问题尽早发现
- **Code as liability**：代码是负债，需要主动清理

### P - Proof（谁在用）

9 大平台官方推荐：
- Claude Code（Marketplace 插件安装）
- Cursor（.cursor/rules/ 目录）
- Gemini CLI（原生 skills 安装）
- Windsurf（rules 配置）
- OpenCode（AGENTS.md）
- GitHub Copilot（.github/copilot-instructions.md）
- Kiro IDE & CLI
- Codex（通用 Markdown 格式）

实际使用案例分布在个人项目到企业级应用。

---

## 三、Skill 体系全景

### 3.1 开发周期六阶段（DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP）

Skills 覆盖软件开发的完整生命周期：

```
DEFINE ──────────────────────────────▶ SHIP
  │                                       │
  ├─ idea-refine                          ├─ git-workflow-and-versioning
  ├─ spec-driven-development              ├─ ci-cd-and-automation
  │                                       ├─ deprecation-and-migration
PLAN ─────────────────────────────────▶   ├─ documentation-and-adrs
  │                                       ├─ shipping-and-launch
  ├─ planning-and-task-breakdown          │
  │                                       │
BUILD ───────────────────────────────▶ VERIFY
  │                                       │
  ├─ incremental-implementation           ├─ test-driven-development
  ├─ context-engineering                 ├─ browser-testing-with-devtools
  ├─ source-driven-development           ├─ debugging-and-error-recovery
  ├─ frontend-ui-engineering             │
  ├─ api-and-interface-design            │
  │                                   REVIEW ◀────┘
  │                                       │
  └─ code-simplification                  ├─ code-review-and-quality
                                          ├─ security-and-hardening
                                          └─ performance-optimization
```

### 3.2 关键 Skill 详解

**context-engineering（Context 管理）**

这是 2026 年 Agent 工程最核心的主题之一。Skills 对这一主题的处理方式不是解释原理，而是给 Agent 一个**Context 管理的操作框架**：

> "Feed agents the right information at the right time - rules files, context packing, MCP integrations. Starting a session, switching tasks, or when output quality drops."
> — [context-engineering Skill](https://github.com/addyosmani/agent-skills/blob/main/skills/context-engineering/SKILL.md)

触发条件：Session 开始、任务切换、输出质量下降。

**test-driven-development（TDD）**

将 TDD 的工程原则翻译为 Agent 可执行的步骤：

> "Red-Green-Refactor, test pyramid (80/15/5), test sizes, DAMP over DRY, Beyonce Rule, browser testing."
> — [TDD Skill](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md)

Anti-rationalization 表是精华——记录了 Agent 常用的借口和反驳：

| Agent 常用借口 | 反驳 |
|--------------|------|
| "这逻辑太简单，不用测" | 简单逻辑更容易被改坏 |
| "我来补测试" | 事后测试等于没测 |
| "我来写集成测试" | 没有单元测试的集成测试是假测试 |

**debugging-and-error-recovery（调试）**

五步 triage 系统：
1. **Reproduce**：先复现问题
2. **Localize**：定位问题来源
3. **Reduce**：最小化复现案例
4. **Fix**：修复
5. **Guard**：添加保护，防止回归

> "Stop-the-line rule, safe fallbacks. Tests fail, builds break, or behavior is unexpected."
> — [debugging Skill](https://github.com/addyosmani/agent-skills/blob/main/skills/debugging-and-error-recovery/SKILL.md)

**security-and-hardening（安全）**

OWASP Top 10 预防 + 三层边界系统：

> "OWASP Top 10 prevention, auth patterns, secrets management, dependency auditing, three-tier boundary system. Handling user input, auth, data storage, or external integrations."
> — [security Skill](https://github.com/addyosmani/agent-skills/blob/main/skills/security-and-hardening/SKILL.md)

### 3.3 Specialist Personas（专家角色）

Skills 附带三个预配置的专业角色 Agent：

| Agent | 视角 | 用途 |
|-------|------|------|
| code-reviewer | Senior Staff Engineer | 五轴 code review，"Staff Engineer 会批准吗"标准 |
| test-engineer | QA Specialist | 测试策略 + 覆盖率分析 + Prove-It 模式 |
| security-auditor | Security Engineer | 漏洞检测 + 威胁建模 + OWASP 评估 |

---

## 四、为什么是 Google 工程文化

Skills 的设计者 Addy Osmani 是 Google 的 Staff Engineer，Skills 直接引用了两本 Google 内部出版物：

- **[Software Engineering at Google](https://abseil.io/resources/swe-book)**（《Google 软件工程》）
- **Google engineering practices guide**

这些不是抽象原则，而是**直接嵌入工作流步骤**。例如：

**Hyrum's Law 在 api-and-interface-design Skill 中**：
> "Public API 的每次变更都会以你无法控制的方式破坏调用方。设计时考虑隐性依赖。"

**Beyonce Rule 在 test-driven-development Skill 中**：
> "测试用真实数据，别用'test test test'字符串——如果你对着测试叫名字，它会回应吗？"

**Chesterton's Fence 在 code-simplification Skill 中**：
> "不要删除你没理解的设计决策。先理解它为什么存在，再决定是否移除。"

---

## 五、快速上手

### 5.1 Claude Code（推荐方式）

```bash
# Marketplace 安装
/claude /plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills

# 或强制 HTTPS（如果没有 SSH keys）
/plugin marketplace add https://github.com/addyosmani/agent-skills.git
/plugin install agent-skills@addy-agent-skills
```

使用 slash commands 激活 Skills：
- `/spec` — 写 PRD 再写代码
- `/plan` — 小而原子化的任务分解
- `/build` — 一次实现一个 slice
- `/test` — 测试即证明
- `/review` — 改善代码健康度
- `/code-simplify` — 清晰优于巧妙
- `/ship` — 更快更安全

### 5.2 Cursor

将 Skills 复制到 `.cursor/rules/` 目录：

```bash
cp -r skills/ .cursor/rules/
```

Cursor 会自动识别 `SKILL.md` 文件并应用到对应的开发阶段。

### 5.3 其他平台

详细的平台安装指南见 [docs/](https://github.com/addyosmani/agent-skills/blob/main/docs/) 目录，包括 Windsurf、Gemini CLI、GitHub Copilot、OpenCode、Kiro 等。

---

## 六、SWE-bench 上的实证

Skills 的效果在 SWE-bench 等基准测试上得到了验证——这不是一个概念项目，而是经过实战检验的工程实践框架。

MIT 许可证允许在个人项目、团队和工具中自由使用这些 Skills。

---

## 七、与竞品的差异

| 维度 | agent-skills | 其他 Skills 集合 |
|------|-------------|----------------|
| 设计哲学 | Process + Anti-rationalization | 参考文档 |
| 平台覆盖 | 9 大平台官方支持 | 通常单一平台 |
| 工程文化 | Google 二十年实践 | 泛泛建议 |
| 验证标准 | Evidence requirements（可测试） | "遵循最佳实践"（模糊）|
| Anti-rationalization | 内置常见借口 + 反驳 | 无 |

---

## 八、下一步行动

1. **立即试用**：在 Claude Code 中安装 agent-skills，用 `/spec` 开启一个项目
2. **关键 Skill**：先体验 `context-engineering`、`test-driven-development`、`code-review-and-quality`
3. **团队采用**：将 Skills 作为团队的"工程纪律标准"，让 AI 和人类共同遵循
4. **贡献反馈**：通过 GitHub 贡献新的 Skills 或改进现有 Skills

---

**引用来源**：
- [GitHub: addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- [Skills 目录结构](https://github.com/addyosmani/agent-skills/tree/main/skills)
- [Skill Anatomy 规范](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md)
- [Software Engineering at Google](https://abseil.io/resources/swe-book)
