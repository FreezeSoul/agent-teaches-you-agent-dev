# Claude Code 2026 完整架构：为什么大多数团队配置了错误的层

> **来源**：[obvworks.ch - Designing CLAUDE.md correctly: The 2026 architecture](https://www.obviousworks.ch/en/designing-claude-md-right-the-2026-architecture-that-finally-makes-claude-code-work/) | Boris Cherny (Claude Code creator, Staff Engineer @ Anthropic) | 2026-04
> **分类**：Stage 1（Prompt Engineering）+ Stage 5（Context & Memory）
> **评分**：15/20（演进重要性高 + 技术深度中 + 知识缺口明确 + 可落地性强）

---

## 核心论点

大多数开发者觉得 Claude Code 不好用，原因是他们只配置了 4 个层次中的 1 个。他们运行 `/init`，然后抱怨 Claude 幻觉文件结构、推荐错误依赖、忽略代码风格。

Boris Cherny（Claude Code 创作者、Anthropic Staff Engineer）通过 InfoQ 采访和公开分享的工作流揭示了完整架构：**5 层加载作用域 + WHAT/WHY/HOW 框架 + 7 条核心规则 + Hooks/Skills/Multi-session 三阶高级模式**。这不只是一份配置清单，而是一个**自我强化的知识固化系统**——Compound Engineering。

---

## 一、为什么你的 CLAUDE.md 被忽略了

Boris Cherny 对 CLAUDE.md 的定义与大多数人的理解根本不同：

> **「CLAUDE.md 不是给人类阅读的 README，它是给 AI 队友的上岗培训文档——每一条纠错都是一条再也不会发生的 bug。」**

这个定义带来一个直接后果：**每一行都必须有存在的理由。** 根据 2026 年 1 月 InfoQ 采访，Boris 自己使用的 CLAUDE.md 只有约 2,500 个 token（100 行左右），而他的团队已经将 Claude Code ship 到生产环境。

与之对应的是社区的普遍失败模式：

| 失败模式 | 症状 |
|---------|------|
| README 心态 | 写给人类看的项目介绍，不是给 AI 的操作指令 |
| 过度填充 | CLAUDE.md 超过 200 行，Claude 开始忽略重要规则 |
| 模糊规则 | `Write clean code`（被忽略）vs `Use camelCase for variables, PascalCase for React components`（被遵循）|
| 静态文档 | 上传后从不更新，AI 使用过时上下文 |

---

## 二、Claude Code 的 4 个层次（大多数开发者只用了 1 个）

完整架构由 4 个层次组成，层次之间互相依赖：

```
┌─────────────────────────────────────────────────────┐
│  Layer 4: Multi-Session Workflows                    │
│  (Git Worktree + Parallel Sessions)                 │
├─────────────────────────────────────────────────────┤
│  Layer 3: Hooks + Skills                             │
│  (Mandatory Enforcement + On-Demand Context)        │
├─────────────────────────────────────────────────────┤
│  Layer 2: WHAT/WHY/HOW Framework + 7 Rules           │
│  (Structured Instructions)                          │
├─────────────────────────────────────────────────────┤
│  Layer 1: CLAUDE.md + 5 Scopes                       │
│  (Persistent Onboarding)                            │
└─────────────────────────────────────────────────────┘
```

**层次 1**（CLAUDE.md）是大多数开发者配置的全部。**层次 2** 引入了结构化写作方法。**层次 3** 将 advisory 配置（可被忽略）转变为 mandatory 执行。**层次 4** 是 Boris Cherny 本人的实际工作方式：同时运行 10-15 个 Claude Code 会话。

---

## 三、5 层加载作用域：CLAUDE.md 的 cascade 机制

Claude Code 从多个路径加载配置，形成明确的优先级 cascade。理解这个机制是精确控制 AI 行为的前提：

| 作用域 | 路径 | 用途 | 团队共享？ |
|--------|------|------|-----------|
| **Global** | `~/.claude/CLAUDE.md` | 个人默认设置，跨所有项目——代码风格、通用规则 | ❌ |
| **Project** | `./CLAUDE.md` | 项目特定规则，构建命令、规范制度 | ✅ |
| **Local Secret**（2026 新增）| `./CLAUDE.local.md` | 个人笔记和密钥，**必须加入 .gitignore** | ❌ |
| **Folder** | `./src/CLAUDE.md` | 模块级 API/组件覆盖，按需加载，节省 token | ✅ |

**关键规则：Last scope wins on conflicts，most specific prevails。**

这个 cascade 的战略意义是**精确的 token 分配**：通用规则放在根目录，模块特定知识放在子目录，只有 Claude 在对应目录工作时才加载相应的上下文。

`CLAUDE.local.md` 是 2026 年新增的作用域，其价值被严重低估：个人快捷方式、WIP 笔记、敏感路径——永远不需要出现在 Git 历史中。这是 `.gitignore` 的第一个条目。

**工程检查清单**：

```
# 每个项目必须包含的 CLAUDE 家族文件
./CLAUDE.md           # 必选，Git 追踪，团队同步
./CLAUDE.local.md     # 可选，必需 .gitignore
./src/CLAUDE.md       # 仅多模块项目需要
~/.claude/CLAUDE.md   # 仅当有跨项目个人规范时需要
```

---

## 四、WHAT/WHY/HOW 框架：强迫完整，阻止幻觉

大多数 CLAUDE.md 失败于结构不完整——有 WHAT 没有 WHY，有命令没有原则。WHAT/WHY/HOW 框架强制你覆盖所有三个维度：

### WHAT — 给出上下文

没有这个基础，Claude 在黑暗中飞行：

- 项目名称和目标
- **带版本号的**技术栈（不是「React」，而是「React 18.3 + TypeScript 5.4 + Vite 5」）
- 仓库结构图（utils、types、API endpoints 在哪里）
- 关键依赖
- **Monorepo**：每个 app 的职责

### WHY — 设定原则

团队花了数月建立的标准：

- 架构决策及其原因（ADR 编号引用亦可）
- 代码风格和 lint 规则
- 命名规范
- 需要避免的反模式
- 安全约束

### HOW — 定义工作流

每个 session 都需要用到的操作命令：

```markdown
## 工作流
- 每次代码变更后运行 `npm test`
- 每个任务创建新分支，绝不直接 commit 到 main
- 使用 Conventional Commits（feat:、fix:、refactor:、docs:）
- 每次 commit 前运行 `eslint . --fix`
- 工作完成后通过 `gh pr create` 打开 PR
```

**如果缺少任何一个维度，Claude 就会猜测。猜测的结果往往是错的。**

---

## 五、7 条核心规则：从可用到可靠的跃迁

这 7 条规则直接来自 Claude Code 官方文档和 Boris Cherny 公开分享的工作流。它们是将 CLAUDE.md 从「被忽略的文档」变为「可靠的队友指南」的关键：

| # | 规则 | 原因 |
|---|------|------|
| 1 | **先运行 /init** | 让 Claude 从代码库自身 scaffold 基线，再人工 curation。从零开始会遗漏太多。 |
| 2 | **保持在 200 行以内** | 太长 = 被忽略。Claude 可靠遵循约 150 条指令。每行必须有存在的理由。 |
| 3 | **用 Hooks 实现 100% 执行** | CLAUDE.md 是 advisory（约 70% 遵循），Hooks 是 deterministic（exit 0 = 允许，exit 2 = 阻止）。 |
| 4 | **用 @imports 实现模块化**（2026 新增）| 通过 `@docs/git.md` 等引用拆分配置，更干净、可复用、节省 token。 |
| 5 | **/compact 和 Plan Mode 并用**（2026 新增）| `/compact` 清理 50% 上下文；3 步以上任务用 Plan Mode。 |
| 6 | **每月更新一次** | CLAUDE.md 是 Living Document。每次 Claude 犯错 → 新增一条规则。Boris 称这为 Compound Engineering。 |
| 7 | **引用而非复制** | 引用 `package.json` 和 `tsconfig.json` 而非复制内容，使用 `@path/to/file` 语法。 |

---

## 六、精确 vs 模糊：规则质量的工程差异

CLAUDE.md 有效与否的**唯一区别**在于精确度。模糊指令对 Claude 的影响与模糊 ticket 对初级开发者一样——都会导致幻觉解释。

| ❌ 模糊（被忽略）| ✅ 精确（被遵循）|
|---------------|---------------|
| Write clean code | Use camelCase for variables, PascalCase for React components |
| Test everything | `npm test` after every change, min 80% coverage for utils/ |
| Prefer TypeScript | MUST use TypeScript strict mode. MUST NOT use `any` type |
| Be careful with git | Always create a new branch per task. NEVER commit to main directly |

精确度的工程价值在于：它强迫你将团队积累的隐性标准显式化。即使你再也不使用 Claude，这些规则也是一份有价值的团队知识文档。

---

## 七、Compound Engineering：自我强化知识固化的飞轮

Compound Engineering 是 Boris Cherny 工作流的核心创新，也是大多数 CLAUDE.md 文章没有抓住的重点。

**核心原则**：每一次 code review、每一次纠错、每一次错误，都成为 CLAUDE.md 中的一条新规则。

在 Anthropic 的实际工作流中，Boris 在同事的 PR 上使用 `@.claude` tag——Claude 自动将学习内容写入 CLAUDE.md（来源：[Vibe Sparking AI，2026 年 1 月](https://www.vibesparking.com/en/blog/ai/claude-code/2026-01-04-boris-cheny-claude-code-workflow-revealed/)）。三个月后的结果：

- **Claude 永不再犯同样的错误**
- **团队知识被系统性地编码**
- **新成员从第一天起就能访问所有学习成果**

**飞轮效应**：每条新增规则都会减少未来的错误，错误减少意味着更少的规则需要添加——实际上，随着系统成熟，新增规则的速度会自然放缓，因为大部分常见错误已经固化。

**Compound Engineering 的工程门槛**：这要求团队建立「每次错误都是一条规则」的纪律。它不是一次性配置，而是**持续的知识运维流程**。

---

## 八、Advanced Patterns：从 advisory 到 mandatory

### 8.1 Hooks 系统：绕过 30% 忽略率

Hooks 是 `.claude/settings.json` 中的确定性回调。关键指标：**CLAUDE.md advisory 约 70% 遵循率，Hooks 是 deterministic 100% 执行。**

Boris 的 4 个关键 Hook 模式：

```json
// .claude/settings.json - Hooks 配置示例
{
  "hooks": {
    "preToolUse": [
      {
        "name": "RouteRiskyOps",
        "description": "Route git push --force to Opus for approval",
        "when": "tool == 'Bash' && command.includes('git push --force')",
        "action": "pause",
        "requireConfirmation": true
      }
    ],
    "postToolUse": [
      {
        "name": "AutoFormat",
        "description": "Auto-format code after each file edit",
        "when": "tool == 'Edit' || tool == 'Write'",
        "action": "Bash",
        "command": "bun run format"
      }
    ]
  }
}
```

| Hook 类型 | 触发时机 | Boris 的用例 |
|-----------|---------|-------------|
| **PreToolUse** | 工具执行前 | 阻止 `git push --force` 等危险操作 |
| **PostToolUse** | 工具执行后 | 每次文件编辑后自动格式化 |
| **Stop Hook** | Claude 标记「完成」前 | 验证工作质量 |
| **/careful** | Claude 判断需确认时 | 阻止 `rm -rf` 等不可逆操作 |

### 8.2 Skills 系统：按需加载的上下文

Skills 是 `.claude/skills/SKILL.md` 中的 Markdown 指南，在**需要时加载**，而非每次 session 都加载。这是 Skills 与 CLAUDE.md 的决定性区别：

| 特性 | CLAUDE.md | Skills |
|------|-----------|--------|
| 加载时机 | 每个 session | 按需（手动 /skill-name 或自动匹配）|
| Token 消耗 | 每次 session 都要支付 | 仅在使用时支付 |
| 用途 | 项目规范、工作流 | code review 模式、迁移指南、BigQuery 分析 |

Boris 团队在 repo 中维护了一个 BigQuery skill，每天直接在 Claude Code 中使用进行数据分析。Skills 库的存在让 Claude 能够组合使用而非每次从零构建。

---

## 九、Boris Cherny 的 Multi-Session 工作流：10-15 个并行会话

这是 4 层架构中大多数文章都跳过的层次，因为它听起来很疯狂——但这是真实的生产工作流。

Boris Cherny 同时运行 **10-15 个 Claude Code 会话**：
- 5 个在本地 terminal tabs
- 5-10 个在 claude.ai/code
- 还有从早上 iPhone 上启动的会话

**关键技术支撑**：每个会话使用独立的 **Git Worktree**，保证变更不会冲突。

```
# 创建独立 worktree 的会话
git worktree add ../feature-auth feature-auth-branch
cd ../feature-auth
claude  # 独立会话，CLAUDE.md 独立
```

**会话管理协议**：
- `/compact`：上下文用到 50% 时压缩
- `/clear`：切换任务时清理
- **Plan → Execute → Verify**（Tests + Linter + Build，顺序不变）
- **每次错误后**：在 `tasks/lessons.md` 中编码修复

---

## 十、CLAUDE.md vs AGENTS.md：单 agent 与多 agent 的边界

| 维度 | CLAUDE.md | AGENTS.md |
|------|-----------|-----------|
| 适用场景 | 单 agent 工作流，主 Claude Code context | 多 agent 工作流，跨工具协作 |
| 工具兼容性 | Claude Code 专用 | Claude + Cursor + Cline + 其他 AI 编码工具 |
| 配置内容 | 项目规范、工作流规则 | 子 agent 角色定义、交互协议 |
| 标准化 | Claude Code 事实标准 | 兴起的开放标准 |

如果你的工作流编排 sub-agent——例如每个 feature 后运行「Code Simplifier」，或 end-to-end 测试的「Verify App」——配置应放在 AGENTS.md 中。这让你的设置**工具无关且可移植**。

---

## 十一、200 行限制的深层原因

Anthropic 官方建议 CLAUDE.md 保持 150 条指令以内（约 200 行）。这不是武断的数字，而是有机制支撑的：

Claude Code 文档明确指出：**当 CLAUDE.md 文件膨胀时，Claude 会丢失实际重要的指令**。如果你的文件中包含 `YOU MUST` 重复规则但仍然被忽略——这意味着文件已经太长，关键规则淹没在噪声中。

**每行自检**：删除这行会让 Claude 犯错吗？如果否——删除。

超过 200 行的应对方案：**使用 @imports 实现模块化**：

```markdown
# ./CLAUDE.md（根文件，约 50 行）
@docs/architecture.md        # 架构决策
@.claude/git-conventions.md # Git 规范
@.claude/security-rules.md  # 安全约束
```

---

## 十二、已知局限与边界判断

**以下情况 CLAUDE.md 解决不了**：

1. **架构级问题**：如果项目结构本身有缺陷，CLAUDE.md 无法弥补。Claude Code 是执行层优化，不是架构救星。
2. **上下文窗口硬限制**：即使精确配置，Claude 的上下文窗口仍是根本约束。超过 100K token 的项目需要分区策略（module-level CLAUDE.md）。
3. **Compound Engineering 的纪律成本**：需要团队建立「每次错误都要写规则」的流程文化。没有这个纪律，飞轮效应不会启动。

**何时 CLAUDE.md 不是正确答案**：
- 需要动态变化的行为 → 用 Hooks 而非规则更新
- 需要跨工具共享 → 用 AGENTS.md
- 需要 AI 自主判断什么重要 → 用 Claude Code Auto-Memory（Claude 自主更新 MEMORY.md）

---

## 参考文献

1. [Designing CLAUDE.md correctly: The 2026 architecture that finally makes Claude Code work](https://www.obviousworks.ch/en/designing-claude-md-right-the-2026-architecture-that-finally-makes-claude-code-work/) — obvworks.ch，2026，全面架构指南
2. [Building Claude Code with Boris Cherny - YouTube](https://www.youtube.com/watch?v=julbw1JuAz0) — Boris Cherny，Claude Code 创作者访谈，2026
3. [Claude Code creator workflow — InfoQ](https://www.infoq.com/news/2026/01/claude-code-creator-workflow/) — InfoQ 采访，2026 年 1 月，Boris Cherny 工作流首次公开
4. [The Compound Engineering Plugin — LinkedIn](https://www.linkedin.com/pulse/compound-engineering-plugin-why-matters-matthew-hartman-8ksee) — 插件生态分析，2026
5. [Boris Cherny CLAUDE.md workflow — Engr Mejba Ahmed](https://www.mejba.me/blog/boris-cherny-claude-code-workflow) — 6 步工作流详解，2026
6. [How the Creator of Claude Code Actually Uses Claude Code — Substack](https://getpushtoprod.substack.com/p/how-the-creator-of-claude-code-actually) — Compound Engineering 实践分析，2026
7. [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — Anthropic 官方文档
