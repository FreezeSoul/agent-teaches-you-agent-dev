# Open Code Review：多评审者对抗式代码审查框架

## 一句话评价

借鉴 GAN 的 Generator-Evaluator 对抗思想，让多个 AI 评审者独立审视代码并通过「辩论」机制相互挑战，形成比单一评审更全面、更深入的代码质量判断——Anthropic 三代理 Harness 架构在 Code Review 场景的开源工程实现。

---

## 为什么关注这个项目

Anthropic 在三代理 Harness 架构中揭示了一个关键洞察：当同一个 Agent 既负责生成代码又负责评价代码时，评价结果会系统性偏向积极——这是「所有权偏好」导致的自我评价失真。解决方案是将「干活」和「评判」彻底分离，让独立的 Evaluator Agent 持有怀疑态度。

Open Code Review 将这个洞察工程化为一个完整的多评审者框架：它让多个独立的 Reviewer Agent 同时审视代码，并通过 Discourse（辩论）机制让评审者之间相互挑战、相互验证，最终产出比任何单一评审更可靠的综合性反馈。

这与 GAN 的训练逻辑高度一致——Generator 生成代码，多个 Discriminator（评审者）独立评分并相互对抗，评分结果反馈给 Generator 改进代码质量。区别在于这里的 GAN 循环发生在 Code Review 阶段而非代码生成阶段。

---

## 核心架构

### 多评审者冗余机制

> "Multi-agent redundancy — Multiple reviewer instances examine your code independently. Different attention patterns catch different issues. What one reviewer misses, another finds."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

与单一 AI 评审不同，OCR 默认启动多个独立评审者实例。每个评审者有不同的关注模式和注意力偏差，这种冗余设计确保没有单一评审者能够覆盖所有问题维度。

### 评审者辩论机制（Discourse）

> "Discourse before synthesis — Reviewers don't just produce findings — they debate them. They challenge assumptions, validate concerns, and surface questions no single reviewer would ask."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

这是 OCR 与其他 AI Code Review 工具最关键的差异点。评审者不只产出发现，还要相互辩论。当评审者 A 提出一个发现后，评审者 B 可以挑战该发现的合理性，要求评审者 A 提供更多证据或修改评估结论。这个辩论过程能够暴露单一评审者视角下的盲区。

### 可配置的评审者团队

> "Fully customizable teams — Pick from 28 reviewer personas (including famous engineers like Martin Fowler, Kent Beck, and Sandi Metz), create your own persistent reviewers, or describe ephemeral one-off reviewers inline."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

OCR 内置了 28 种预设评审者人格，包括 Martin Fowler、Kent Beck、Sandi Metz 等著名工程师的分身。每个评审者人格有不同的审查偏好和关注领域：

- **Martin Fowler**：擅长面向对象设计模式、建筑重构
- **Kent Beck**：擅长测试驱动开发、极限编程实践
- **Sandi Metz**：擅长 Ruby 面向对象设计、 SOLID 原则

用户也可以描述性的方式创建临时评审者（Ephemeral Reviewers），或定义自己持久化的评审者团队。

---

## 核心功能

### 需求感知评审（Requirements-Aware Review）

> "Pass in a spec, proposal, or acceptance criteria. Every reviewer evaluates the code against your stated requirements, not just general best practices."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

OCR 可以接受产品规格说明书、提案或验收标准，每个评审者会针对这些明确的业务需求而非通用最佳实践来评估代码。这解决了 AI 评审常出现的「评分标准与业务目标脱节」问题。

### 项目上下文自动发现

> "OCR discovers your standards from CLAUDE.md, .cursorrules, OpenSpec configs, and other common patterns. Reviewers apply your conventions."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

OCR 自动从项目根目录的规范文件中提取代码规范和团队约定（CLAUDE.md、.cursorrules、OpenSpec 等），确保评审者应用的是团队自己的规范而非通用标准。

### 代码审查地图（Code Review Maps）

> "Navigate large changesets with section-based breakdowns, rendered Mermaid dependency graphs, and file-level progress tracking."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

对于大型代码变更集，OCR 提供可视化的代码审查地图，将变更按模块分解，渲染 Mermaid 依赖图，并追踪每个文件的审查进度。

### GitHub PR 集成

> "Post Team Review — Posts the multi-reviewer synthesis as-is; Generate Human Review — AI rewrites all findings into a single, natural human voice following Google's code review guidelines."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

OCR 支持两种 GitHub PR  posting 模式：
- **Team Review**：直接发布多评审者综合结论
- **Human Review**：将所有发现用符合 Google Code Review 规范的人类语言重写，保持评审意见的专业性和可读性

---

## 技术实现

### 支持的 AI 工具

OCR 支持 15+ 种 AI Coding 助手：

Claude Code、Cursor、Windsurf、OpenAI、GitHub Copilot、JetBrains AI Assistant、Amazon CodeWhisperer、Google Gemini、Tabnine、Replit Agent、Codeium、Cody、Llava、Gemma、Mistral

> "ocr init detects your installed AI tools and configures each one automatically."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

`ocr init` 命令能自动检测项目已安装的 AI 工具并完成自动配置。

### Dashboard + CLI 双界面

> "The dashboard is the recommended way to run reviews, browse results, and manage your workflow from the browser."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

OCR 提供 Browser Dashboard（可视化界面）和 CLI 两种交互方式。Dashboard 是推荐方式，支持实时查看多评审者工作进度、浏览辩论结果、管理工作流。

### 多轮评审（Multi-Round Reviews）

> "Multi-Round Reviews — Reviewers iterate on findings based on feedback and code changes."
> — [Open Code Review README](https://github.com/spencermarx/open-code-review)

评审不是一次性过程，而是支持多轮迭代。评审者可以根据反馈和代码变更更新自己的发现，形成评审结论的持续改进循环。

---

## 与 GAN 三代理架构的关联

OCR 的多评审者辩论机制，本质上是 Anthropic GAN 三代理架构中「Generator-Evaluator 对抗」思想在 Code Review 场景的工程实现：

| GAN 三代理架构 | Open Code Review 对应 |
|----------------|----------------------|
| Generator（生成代码）| Developer（提交代码的开发者）|
| Evaluator（评审代码）| 多评审者团队（Reviewer personas）|
| 对抗反馈循环 | Discourse（辩论）机制 |
| 迭代改进 | Multi-Round Reviews |

关键洞察来自 Anthropic 的发现：

> "Separating the agent doing the work from the agent judging it proves to be a strong lever to address this issue. The key insight is that the model calibrates more skepticism toward an external evaluator than toward its own work."
> — [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

OCR 验证了这个洞察在 Code Review 场景的有效性：多个独立评审者（External Evaluator）比开发者自我评审更能发现真实问题，评审者之间的辩论（Adversarial Feedback）比单一评审者的结论更可靠。

---

## 快速开始

```bash
# 1. 安装 CLI
npm install -g @open-code-review/cli

# 2. 在项目中初始化
cd your-project
ocr init

# 3. 启动 Dashboard 并运行审查
ocr dashboard
```

或直接在 AI 编程助手内调用：

```
/ocr:review  # Claude Code / Cursor
/ocr-review  # Windsurf / 其他工具
```

---

**关联主题**：Generator-Evaluator 分离架构 → 多评审者对抗式代码审查 → Anthropic GAN 三代理 Harness 的工程实现

**关联文章**：
- `articles/harness/anthropic-gan-inspired-three-agent-architecture-long-running-apps-2026.md`

**Stars**: 164（2026-05-08）
**仓库**：[spencermarx/open-code-review](https://github.com/spencermarx/open-code-review)