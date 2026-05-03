# awesome-agent-skills：GitHub 最大的 Agent Skills 索引，4,494 ⭐ 的生态地图

> **Target**：想用好 Agent Skills 的开发者 / 想让 AI 编码工具变得更专业的团队
> **Result**：通过这个索引找到正确的 Skill，让 Claude/Copilot/Codex 在特定领域从「通用」变「专业」；比自己在论坛里大海捞针快 10 倍
> **Insight**：Skills 不是 Claude 专属特性，而是跨平台互操作标准——awesome-agent-skills 证明了 Skills 生态已从「单厂商锁定」演变为「多平台共识」
> **Proof**：4,494 ⭐、多语言维护（6 种语言）、覆盖 9 个主流 AI Coding 平台、社区 Skills 分类完整

---

## 一、定位破题：Skills 生态的「黄页」

> 官方原文：
> "Never heard of 'agent skills' before? You're in the right place. This is a community-curated list of simple text files that teach AI assistants (like Claude, Copilot, or Codex) how to do new things on demand, without retraining."
> — [awesome-agent-skills README](https://github.com/heilcheng/awesome-agent-skills)

awesome-agent-skills 的定位非常清晰：**Skills 生态的「黄页」**——不是给你一个 Skill，而是告诉你「有哪些 Skill、在哪里找、怎么用」。

它解决的是这个痛点：当你想让 Claude 处理 PDF，却不知道该用什么 Skill；当你想让 Copilot 帮你调 Terraform，却不知道社区有没有现成的——awesome-agent-skills 就是答案。

---

## 二、Sensation：30 秒入门 Skills

**Step 1：选一个 Skill**（从目录或 agent-skill.co 浏览）

**Step 2：加载到你的 AI**：
```bash
# Claude Code
/claude skills add https://github.com/anthropics/skills/tree/main/pdf

# Claude.ai
# 粘贴 raw SKILL.md URL 到对话

# Codex / Copilot
# 参照各平台文档（README 中有链接）
```

**Step 3：直接用自然语言描述任务**。AI 会自动识别并加载需要的 Skill。

> 官方原文：
> "That's it. No installation. No configuration. No coding required."
> — [awesome-agent-skills README](https://github.com/heilcheng/awesome-agent-skills)

---

## 三、Evidence：生态有多完整

### 3.1 覆盖 9 个主流 AI Coding 平台

| Agent | Documentation |
|-------|---------------|
| Claude Code | code.claude.com/docs/en/skills |
| Claude.ai | support.claude.com |
| Codex (OpenAI) | developers.openai.com/codex/skills |
| GitHub Copilot | docs.github.com/copilot/concepts/agents/about-agent-skills |
| VS Code Agent | code.visualstudio.com/docs/copilot/customization/agent-skills |
| Antigravity (Google) | antigravity.google/docs/skills |
| Kiro | kiro.dev/docs/skills/ |
| Gemini CLI | geminicli.com/docs/cli/skills/ |
| Junie | junie.jetbrains.com/docs/agent-skills.html |

**这不是 Claude 的独占生态，而是整个 AI Coding 领域的共识**。

### 3.2 三大生态枢纽

| 平台 | URL | 用途 |
|------|-----|------|
| **SkillsMP Marketplace** | skillsmp.com | 自动索引 GitHub 所有 Skill，按分类/更新时间/stars 排序 |
| **skills.sh Leaderboard** | skills.sh | Vercel 运营，最流行 Skills 仓库排行榜 |
| **agent-skill.co** | agent-skill.co | awesome-agent-skills 的 live 目录 |

### 3.3 官方 Skill 目录（按厂商）

- **Anthropic**：docx/pptx/xlsx/pdf/algorithmic-art/canvas-design/frontend-design/mcp-builder 等 16 个官方 Skills
- **OpenAI (Codex)**：cloudflare-deploy/develop-web-game/gh-address-comments/gh-fix-ci/figma-implement-design 等 18 个 Skills
- **Google Gemini**：gemini-api-dev/vertex-ai-api-dev/gemini-live-api-dev/gemini-interactions-api
- **Hugging Face**：hf-cli/hugging-face-datasets/hugging-face-model-trainer/transformers.js
- **Cloudflare**：agents-sdk/building-mcp-server-on-cloudflare/durable-objects/wrangler 等 6 个 Skills
- **Microsoft (Azure)**：132 个 Skills 覆盖 Azure 全家桶（python/dotnet/typescript/java/rust 各语言变体）

### 3.4 社区 Skills 分类

- Vector Databases（向量数据库专项）
- Marketing（营销工作流）
- Productivity and Collaboration（效率工具）
- Development and Testing（开发测试）
- Context Engineering（上下文工程）

---

## 四、Threshold：快速上手

### 找 Skill 的路径

```
1. 直接访问 agent-skill.co → 搜索关键词
2. 或者访问 skillsmp.com → 按分类浏览
3. 找到后 → 复制 GitHub URL → `/skills add <url>` → 搞定
```

### 创建自己的 Skill

如果社区没有现成的，参考：
- Anthropic 官方模板：[anthropics/skills/template](https://agent-skill.co/anthropics/skills/template)
- Anthropic Skill 创建指南：[How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- Claude Code Skills 文档：[code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)

### Skill 文件结构

```
skill-name/
├── SKILL.md          # 必需：YAML frontmatter + 指令
├── scripts/          # 可选：辅助脚本（Claude 执行）
├── templates/        # 可选：文档模板
└── resources/        # 可选：参考文件
```

---

## 五、为什么现在重要：Skills 正在成为新的 Plugin 生态

> 官方原文（2026 Trends）：
> "Modern agents move past simple 'prompt-response' models. They break down broad objectives into multi-step strategic plans... Organizations are moving from general-purpose prompting to highly specialized skills for each platform and workflow — reducing hallucinations and improving reliability in production deployments."
> — [awesome-agent-skills README - Trends & Capabilities 2026](https://github.com/heilcheng/awesome-agent-skills)

Skills 的价值主张：
- **比 Fine-tuning 轻量**：无需重新训练，更新只是更新文件
- **比 System Prompt 高效**：不需要把所有知识塞进 context window
- **比 MCP 可组合**：MCP 是「连接层」，Skills 是「应用层」，两者互补

---

## 六、与同类项目的差异

awesome-agent-skills 不是「一个 Skill 集合」，而是「所有 Skill 仓库的索引」。它的价值在于：

1. **完整性**：覆盖所有主流平台的 Skills 生态
2. **可发现性**：SkillsMP + agent-skill.co 提供搜索和分类
3. **社区验证**：所有收录的 Skills 都有 GitHub 仓库背书（stars/活动/维护状态）
4. **多语言支持**：README 有 6 种语言（英/繁中/简中/日/韩/西班牙），生态国际化

同类对比：
- mattpocock/skills：单个维护者的技能集，偏 TypeScript/前端方向
- microsoft/skills：Azure 特定领域，深度够但范围窄
- **awesome-agent-skills**：全栈地图，宽广且持续更新

---

## 七、数据验证

| 指标 | 数值 |
|------|------|
| GitHub Stars | 4,494 ⭐ |
| Forks | 424 |
| 最后更新 | 2026-05-03 |
| 多语言 | 6 种（EN/繁中/简中/日/韩/西班牙）|
| 覆盖平台 | 9 个主流 AI Coding 工具 |

---

## 八、下一步行动

1. **立即试用**：访问 [agent-skill.co](https://agent-skill.co)，搜索你当前项目的技术栈
2. **如果找不到合适的 Skill**：参考 [skill-creator](https://agent-skill.co/anthropics/skills/skill-creator) 创建自己的 Skill 并贡献给社区
3. **关注生态**：订阅 awesome-agent-skills 的更新，Skills 生态在 2026 年正在快速扩张

---

**引用来源**：
- [awesome-agent-skills - GitHub](https://github.com/heilcheng/awesome-agent-skills)（4,494 ⭐，Hailey Cheng 维护）
- [agent-skill.co](https://agent-skill.co)（Live directory）
- [SkillsMP Marketplace](https://skillsmp.com)（自动索引）
- [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)