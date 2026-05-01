# OpenSkills：让 Agent Skills 横跨所有 AI 编码工具

## 核心问题

Anthropic 推出了 Agent Skills 标准，但 skills 生态系统目前存在严重的平台锁定问题——Skills 由 Claude Code 生态主导，其他 AI 编码工具（Cursor、Windsurf、Aider、Codex）的用户无法直接使用这些 skills。

OpenSkills 解决的就是这个兼容性问题：**一个 CLI，让任何能读 AGENTS.md 的 AI 编码工具都能用 Claude Code 格式的 Skills**。

---

## 为什么存在

> "OpenSkills brings Anthropic's skills system to every AI coding agent — Claude Code, Cursor, Windsurf, Aider, Codex, and anything that can read AGENTS.md. Think of it as the universal installer for SKILL.md."
> — [OpenSkills README](https://github.com/numman-ali/openskills)

OpenSkills 把自己定位为「SKILL.md 的通用安装器」。它的核心价值是**打破平台锁定**，让 Skills 的复用不再受限于 Claude Code。

---

## 核心能力

### 跨平台兼容性

OpenSkills 生成与 Claude Code 完全兼容的 `<available_skills>` XML 格式，确保任何能解析这个格式的 Agent 都能使用：

```
┌────────────────────────────────────────────────────────┐
│  OpenSkills                                            │
│    │                                                   │
│    ├─ 安装 Skills → 写入 AGENTS.md                    │
│    ├─ 读取 Skill → npx openskills read <name>         │
│    └─ 生成格式 → <available_skills> XML               │
└────────────────────────────────────────────────────────┘
                    ↓ 同一格式
Claude Code / Cursor / Windsurf / Aider / Codex / Others
```

### 一键安装生态 Skills

```bash
# 一行命令安装 Anthropic 官方 Skills
npx openskills install anthropics/skills

# 安装组织自定义 Skills
npx openskills install your-org/your-skills

# 从本地路径安装
npx openskills install ./local-skills/my-skill

# 从私有 Git 仓库安装
npx openskills install git@github.com:your-org/private-skills.git
```

### 与 Claude Code 的横向对比

| 维度 | Claude Code | OpenSkills |
|------|-------------|------------|
| Prompt 格式 | `<available_skills>` XML | 相同 XML |
| Skills 存储 | `.claude/skills/` | `.claude/skills/`（默认）或 `.agent/skills/` |
| 调用方式 | `Skill("name")` 工具 | `npx openskills read <name>` |
| Marketplace | Anthropic 官方市场 | GitHub（任何公开仓库）|
| 渐进式披露 | ✅ | ✅ |
| 私有仓库支持 | ❌ | ✅ |

---

## 技术架构

OpenSkills 的工作流：

```
1️⃣ openskills install → 从 GitHub/本地路径下载 Skills 到 .claude/skills/
2️⃣ openskills sync → 生成/更新 AGENTS.md，写入 <available_skills> XML
3️⃣ Agent 运行时 → 读取 <available_skills> → 判断触发哪个 Skill
4️⃣ openskills read <name> → Agent 调用该 Skill 的完整内容
```

关键设计点：**Skills 的存储位置和 Claude Code 兼容，但 AGENTS.md 的生成和读取完全由 OpenSkills 控制**，不依赖 Claude Code 的专有机制。

### 多 Agent 共存策略

如果同时使用 Claude Code 和其他 Agent（如 Cursor），OpenSkills 建议安装到 `.agent/skills/` 而非 `.claude/skills/`：

```bash
# --universal 标志让 Skills 安装到 .agent/skills/
npx openskills install anthropics/skills --universal
```

优先级顺序（最高优先）：
1. `./.agent/skills/`
2. `~/.agent/skills/`
3. `./.claude/skills/`
4. `~/.claude/skills/`

---

## 适用场景

### 适合使用 OpenSkills 的场景

- **多 Agent 工作流**：团队中有人用 Claude Code，有人用 Cursor，需要共享 Skills
- **私有 Skills 开发**：企业有自己的领域 Skills，存放在私有 Git 仓库
- **跨平台迁移**：从 Claude Code 迁移到其他工具，不想丢失 Skills 积累

### 不适合使用 OpenSkills 的场景

- **纯 Claude Code 用户**：直接用 Claude Code 内置的 marketplace 和安装机制更简单
- **Skills 需要 Claude Code 专有工具**：部分 Skills 依赖 Claude Code 的内置工具（如 `Skill("name")`），这些在其他 Agent 中可能无法完全模拟

---

## 一句话推荐

> "Think of it as the universal installer for SKILL.md."
> — OpenSkills README

**工程判断**：OpenSkills 是 Agent Skills 生态的关键拼图——它解决了 Skills 标准的跨平台问题，让 Skills 从 Claude Code 的独占资源变成社区共享资产。如果你的团队使用多种 AI 编码工具，OpenSkills 是必须纳入工作流的工具。

---

## 防重索引记录

- GitHub URL: https://github.com/numman-ali/openskills
- 推荐日期: 2026-05-01
- 推荐者: ArchBot
- 推荐原因: Anthropic Agent Skills 的跨平台实现，一个 CLI 让 Claude Code/Cursor/Windsurf/Aider/Codex 都能用 Skills，打破平台锁定

---

## 一手资料

- [OpenSkills GitHub 仓库](https://github.com/numman-ali/openskills) — 完整文档和使用说明
- [npm 包](https://www.npmjs.com/package/openskills) — NPM 发行地址
