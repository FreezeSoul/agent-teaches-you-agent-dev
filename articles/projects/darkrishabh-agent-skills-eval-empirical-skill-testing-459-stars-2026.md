# darkrishabh/agent-skills-eval：让 Agent Skills 的有效性可以被实证测量

## 定位破题

**一句话定义**：一个 Skill 的测试运行器——给一个 `SKILL.md` 文件加上一套评测，就能用数据回答「这个 Skill 真的让模型在这项任务上变强了吗」。

**场景锚定**：当你（或你的团队）写了一个 Agent Skill，假设它有效——但你无法证明。这时候想起这个工具。

**差异化标签**：不是在「定义」Skill 好不好，而是在「测量」它好不好。

---

## 体验式介绍

用法简单到难以置信：

```bash
npx agent-skills-eval ./skills \
  --target gpt-4o-mini \
  --judge gpt-4o-mini \
  --baseline \
  --strict
```

你指向一个技能文件夹，给它一个目标模型和一个评判模型，它会：
1. **带 Skill 运行**你的评测
2. **不带 Skill 运行**同样的评测（baseline）
3. **用 judge 模型**给两轮输出打分
4. **生成一份 HTML 报告**：side-by-side 对比，pass/fail，带引用论据

> "If the skill doesn't make a measurable difference, you'll see it. If it does, you have receipts."
> — [agent-skills-eval README](https://github.com/darkrishabh/agent-skills-eval)

这就是「有数据支撑的工程决策」——不是「感觉这个 Skill 有用」，而是「对比数据证明这个 Skill 有/无效」。

---

## 拆解验证

### 技术深度：与 agentskills.io 规范的深度耦合

这个工具不只是「运行测试」——它完整实现了 [agentskills.io specification](https://agentskills.io/specification) 的规范要求：

- `SKILL.md` 验证：检查你的 Skill 文件格式是否合规
- `evals/evals.json`：标准评测描述格式
- `iteration-N/`：标准迭代产物布局

这意味着你的 Skill 一旦通过这个框架验证，就**天然兼容 agentskills.io 生态的任何工具**。这是一个规范驱动的工程选择——不是自己做生态，而是融入已有的生态。

### 工具调用断言：不只是文本生成质量

大多数评测框架只检查「模型说了什么」。这个工具支持**工具调用断言**（tool-call assertions），能检测「Agent 是否调用了正确的工具」，而不仅仅是生成了正确的文本。

这对于技能评测至关重要——很多 Skill 的价值不在于「模型说出了什么」，而在于「模型是否做了正确的动作」。

### OpenAI 兼容：开箱即用

> "Works out of the box with OpenAI, Together, Groq, Anthropic via OpenAI-compat layers, Anthropic via OpenAI-compat layers, local Llama servers — anything that speaks the OpenAI chat API."
> — [agent-skills-eval README](https://github.com/darkrishabh/agent-skills-eval)

### TypeScript + MIT：生产级工程实现

- 完整 TypeScript 类型定义
- 标准化 CI/CD 工作流
- MIT 许可，无商业限制

---

## 数据指标

| 指标 | 数值 |
|------|------|
| Stars | 459（2026-05-06 创建，7天） |
| Language | TypeScript |
| License | MIT |
| npm 周下载 | 增长中 |
| 规范兼容 | agentskills.io spec 完整实现 |

---

## 行动引导

### 快速上手

```bash
npm install agent-skills-eval
npx agent-skills-eval ./your-skills --target gpt-4o-mini --judge gpt-4o-mini --baseline
```

1. 写一个 `SKILL.md`
2. 写一个 `evals/evals.json`
3. 运行命令
4. 看报告，决定是否保留这个 Skill

### 适合的场景

- 新 Skill 上线前的有效性验证
- Skill 迭代过程中的 A/B 对比
- Skill 质量门禁（CI/CD 集成）
- Skill 贡献者提交时的自动化验证

---

## 主题关联

本文与 Parameter Golf 文章形成「AI 时代实证验证」的双视角：

- **Parameter Golf**：用 Codex triage bot 做「提交预审」，回答「这个提交是否合规、是否值得人工审查」——AI 辅助评审
- **agent-skills-eval**：用对比评测做「Skill 有效性实证」，回答「这个 Skill 是否真的让模型变强」——AI 输出质量量化

两者共同指向同一个工程需求：**当 Agent 的输出越来越复杂时，如何系统性地验证其质量**。Parameter Golf 从「竞赛评审」角度揭示了这个需求，agent-skills-eval 从「Skill 评测」角度提供了具体工具。

---

## 参考链接

- [GitHub: darkrishabh/agent-skills-eval](https://github.com/darkrishabh/agent-skills-eval)
- [agentskills.io 规范](https://agentskills.io/specification)
- [Documentation](https://darkrishabh.github.io/agent-skills-eval/)
