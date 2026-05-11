# Liu-PenPen/skill-review：给 Agent Skill 做 Code Review 的 Skill

**来源**：[GitHub — Liu-PenPen/skill-review](https://github.com/Liu-PenPen/skill-review)（17 Stars，2026-05-11 创建）

**主题关联**：[Cursor「Better AI Models」研究](./cursor-better-models-ambitious-work-jevons-effect-2026.md) 揭示了当 AI 提升代码生成能力后，开发者的核心工作转向**管理 AI 输出**（文档 +62%、代码审查 +51%）。Skill Reviewer 正是这个趋势的工具化实现——用 AI Agent 标准化人类与 AI 协作的核心工件（Skill）。

---

## 定位破题

Skill Reviewer 解决了一个被忽视的问题：**当 Skill 成为 Agent 系统的基础单元时，谁来保证 Skill 本身的质量？**

它是：
- **一个 Skill**，用于审查其他 Skill 的质量
- **一套 10 条可检测的工程规范**，而非模糊的「写得好不好」
- **一个零依赖的 lint 脚本**，可在 CI 中独立运行

> "用 **10 条 rubric + 1 个零依赖 lint 脚本** 检测一个 Skill 是否符合高质量规范，按 **P0–P3 分级** 输出报告"

这与 Cursor Bugbot 的思路一脉相承——当 AI 能够生成代码时，**Review 和标准化**成为瓶颈，而标准化需要可测量的规则而非主观判断。

---

## 核心机制：10 条 Rubric + 分级体系

### Rubric 维度（可检测的工程规范）

Skill Reviewer 不检查「文字写得好不好」，而是检查**可验证的工程属性**：

| 规则 | 检查内容 |
|------|---------|
| R1 | 渐进式加载（lazy loading） |
| R2 | Description 关键词密度 |
| R3 | 工作流 checklist 完整性 |
| R4 | 确认节点（Confirmation points） |
| R5 | 脚本封装（Scripts wrapped） |
| R6 | 参数系统（Parameters system） |
| R7 | References 组织 |
| R8 | Pre-Delivery 自检 |
| R9 | CLI + Skill 双模式 |
| R10 | 反 Slop（Anti-slop measures） |

> 这是关键洞见——**Skill 质量可以被结构化检测**，就像代码质量可以被 lint 规则检测一样。

### P0–P3 分级

检测结果按严重性分级：

- **P0**：阻断性问题，Skill 无法正常工作
- **P1**：严重功能缺陷
- **P2**：最佳实践偏离
- **P3**：建议改进

> 笔者认为，P0–P3 分级的意义在于将 Skill 质量从「主观感受」变为「可量化的质量指标」。这为 Skill 生态的演进提供了必要的数据基础——你可以说「我们的 Skill 库 P0 缺陷减少了 50%」，而不仅仅是「Skill 质量提高了」。

---

## 使用模式

### 三种使用方式

**1. 斜杠命令（最常用）**
```
/skill-reviewer <path>
```
在 Cursor 聊天框中直接触发，输出分级报告。

**2. 自然语言触发**

Description 中有关键词网，以下说法都能触发：
- "帮我 review 一下 `.cursor/skills/superdesign`"
- "审查这个 skill 写得怎么样"
- "看看这个 skill 是不是 slop"

**3. 命令行 lint（CI/Git Hook）**
```bash
node scripts/lint-skill.mjs .cursor/skills/my-skill --json
```

### Template 模式

Skill Reviewer 还能**生成符合规范的新 Skill 骨架**：

```bash
/skill-reviewer --template code-reviewer
```

会自动：
1. 收集 Skill 意图（名称、用途、触发短语）
2. 生成标准目录结构（`SKILL.md` + `scripts/` + `references/`）
3. 运行 lint 验证骨架本身合格

> 这解决了 Skill 生态的先有鸡还是先有蛋问题——**创建 Skill 的工具本身必须符合它要检查的规范**。官方文档指出："这个 Skill 必须遵守它自己要检查的每一条规则——不然就是用 Slop 检测 Slop。"

---

## 技术实现

### 零依赖 lint 脚本

核心是 `scripts/lint-skill.mjs`，一个纯 Node.js 脚本：
- 无外部依赖（Python/其他 runtime 不需要）
- 可以在任何 CI 系统中运行
- 支持 `--json` 输出机器可读结果
- 支持 `--quick` 跳过软评，只跑硬指标

### 渐进式披露设计

Review 工作流设计遵循**渐进式披露**原则：

```text
Step 0  Confirm mode & target       ⚠️ REQUIRED
Step 1  Run lint-skill.mjs          (hard facts)
Step 2  Soft review per rubric      (per-step reference load)
Step 3  Aggregate findings by P0–P3
Step 4  Ask user how to proceed     ⚠️ REQUIRED
Step 5  Deliver report / apply fixes
Step 6  Pre-delivery self-check
```

> 注意到 Step 0 和 Step 4 的 `⚠️ REQUIRED` 标记——这是防止 Skill 在没有确认目标的情况下自动执行大量检查，造成 Token 浪费。这与 Anthropic 的渐进式披露架构（Agent Skills with progressive disclosure）在工程实践层面形成呼应。

---

## 与 Cursor「Better AI Models」研究的关联

Cursor 研究揭示了一个关键趋势：**随着 AI 提升代码生成能力，代码审查的需求同步增长（+51%）**。Skill Reviewer 将这个逻辑延伸到 Skill 层面：

> "As AI improves at code generation, the developer's job shifts to managing that output."
> — [Cursor Blog](https://cursor.com/blog/better-models-ambitious-work)

当 Skill 成为 Agent 系统的「代码」，Skill Review 就成为必要的**质量门禁**。

两个核心关联：

1. **研究 → 工具**：研究观察到的「管理 AI 输出」趋势（代码审查 +51%）→ Skill Reviewer 提供系统化的 Skill 质量审查机制

2. **工具 → 生态**：Skill Reviewer 的 rubric 体系（10 条可检测规则）为 Skill 生态提供了质量标准，为 Skill Marketplace/Registry 提供了数据基础

---

## 快速上手

```bash
# 一行安装
npx skills add Liu-PenPen/skill-review

# 常用选项
npx skills add Liu-PenPen/skill-review -a cursor  # 只装到 Cursor
npx skills add Liu-PenPen/skill-review -g        # 安装到用户目录

# CLI lint（在 CI 中使用）
node .cursor/skills/skill-reviewer/scripts/lint-skill.mjs <path> --json
```

---

## 项目元数据

| 字段 | 值 |
|------|-----|
| **Stars** | 17（2026-05-11 创建） |
| **Language** | JavaScript |
| **License** | 未声明 |
| **依赖** | 零外部依赖（lint 脚本） |
| **安装方式** | `npx skills add Liu-PenPen/skill-review` |

---

## 引用

> "它检查的不是「文字写得好不好」，而是 10 条**可检测的工程规范**：渐进式加载、description 关键词密度、工作流 checklist、确认节点、脚本封装、参数系统、references 组织、Pre-Delivery、CLI+Skill 模式、反 Slop。"
> — [GitHub README](https://github.com/Liu-PenPen/skill-review)

> "这个 Skill 必须遵守它自己要检查的每一条规则——不然就是用 Slop 检测 Slop。"
> — [GitHub README](https://github.com/Liu-PenPen/skill-review)