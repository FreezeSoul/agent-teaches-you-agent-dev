# Agent 配置正在让你的 Agent 变笨：为什么「更多规则」等于「更差表现」

> **核心论点**：开发者通过堆叠 AGENTS.md / CLAUDE.md / .cursorrules 来「帮助」AI 编码 Agent，但实际上这些配置正在让 Agent 变笨。ETH Zurich 的研究数据和工程实践均指向同一个结论：**添加上下文文件不仅不能提升任务成功率，反而使其下降，同时推理成本上升超过 20%**。这不是 Agent 的问题，是我们对 Agent 配置认知的根本性错误。

---

## 诊断问题：为什么你的 Agent 一直在忽略你的指令

打开一个经过几个月 AI 辅助开发的项目，你会看到这样的配置「遗迹」：

- `CLAUDE.md`
- `.cursorrules`
- `copilot-instructions.md`
- `AGENTS.md`
- 可能还有一个 `gemini.md`

一个开发者这样描述：「根目录里的彩纸（confetti in the root directory）」。

另一个开发者用符号链接同步五个配置文件，因为它们「几乎相同但略有不同，每个工具技术上都要求有一个」。

第三个人写了一个包含 156 条验证规则、覆盖 28 个类别的 CLI 工具——因为 AI 配置文件现在需要自己的 linter。

这个场景有一个熟悉的名字：**配置蔓延（Configuration Creep）**。

我们见过 webpack 配置。见过 Docker Compose 配置。当这些变坏时，你的构建变慢。

**这次不同的是**：一个糟糕的 Agent 配置让你的 Agent **变笨**。

---

## 研究证据：数据不会说谎

### ETH Zurich 的发现

2026 年 2 月，苏黎世联邦理工学院的研究人员发表了一篇论文（arXiv:2602.11988），评估了 AGENTS.md 文件对多个编码 Agent 和 LLM 的影响。结论直白：

> "Context files reduce task success rates compared to providing no repository context, while increasing inference cost by over 20%."
>
> — ETH Zurich, "Evaluating AGENTS.md Files Across Multiple Coding Agents" (February 2026)

添加上下文文件后，Agent 的任务成功率**低于完全不提供仓库上下文**，同时推理成本增加了超过 20%。

论文作者在 Hacker News 上进一步澄清：即使是人类编写的上下文文件，性能提升也只有约 4%，且这种提升在不同模型间并不一致。在 Sonnet 4.5 上，性能实际上**下降了超过 2%**。

### CodeIF-Bench 的发现

CodeIF-Bench（arXiv:2503.22688）测试了多轮交互式代码生成中的指令遵循能力。其关键发现之一：

> "Additional repository context actively degraded models' ability to follow instructions."
>
> — CodeIF-Bench, "Instruction Following in Interactive Code Generation"

更多上下文，更差的指令遵循。研究人员将上下文管理确定为**关键未解决问题**。

### ConInstruct（AAAI 2026）的发现

ConInstruct（AAAI 2026）进一步测试了模型是否能检测指令中的冲突约束。Claude 4.5 Sonnet 在检测冲突方面得分 87.3% F1。

但问题在于：**即使模型发现了矛盾，也几乎从不会向用户报告**。它只是默默选择一个解释然后继续。

你的配置文件在某处说「使用 tabs」，在另一处说「使用 spaces」。模型注意到了。它不告诉你。它只是选一个。

### PACIFIC 的发现

PACIFIC（arXiv:2512.10713）确认了顺序版本的同一问题。随着代码任务中指令链变长，即使是最先进的模型也会失去跟踪。框架生成难度递增的基准测试，结果一致：**顺序指令越多，失败越多**。

---

## 根本原因：我们不信任 Agent

你有多少条 AGENTS.md 指令？

More rules, worse output. **因为我们不信任 Agent。**

Stack Overflow 2025 年调查显示：84% 的开发者使用或计划使用 AI 工具，但只有 29% 信任它们。比两年前的 40% 有所下降。

当你不信任某样东西时，你会过度指定。你写一份 200 行的 AGENTS.md 解释你的文件夹结构，因为你不相信 Agent 能自己想明白。你添加 linter 已经强制执行的编码风格规则。你粘贴架构文档，Agent 其实可以从仓库本身读取这些。

**肌肉记忆在作祟**。两年前这是合理的。早期的 Agent 确实是盲的。它们看不见你的代码库。你必须解释一切。

但 Agent 变得更好了。上下文引擎变得更好了。工具现在能读取你的代码、依赖、git 历史、文件结构。它们自动推导模式。**开发者仍在为盲版本的 Agent 写指令**。

Tim Sylvester 准确描述了这个沮丧循环：

> "You write down these extensive lists of rules. The agent dutifully ignores them. You call it out. 'You're right to call me out!' it chirps, and apologizes. These are empty apologies it performs by rote. Many of us have been in relationships like this before."

---

## 正确认知：上下文分层

### Agent 能看到的

- 你的代码
- 你的文件结构
- 你的依赖
- 你的 git 历史

一个好的上下文引擎能读取所有这些。你不需要在 markdown 文件中重述。这就像给一个已经克隆了仓库的同事写 README。

### Agent 看不到的

- 如何部署
- 如何运行测试
- 存在于人们头脑中而非 linter 配置中的团队约定
- 你的 staging 环境是什么样的
- 为什么三个月前你做出了那个奇怪的架构决策

### 正确做法

大多数人用第二类（Agent 看不到）的工具解决第一类（Agent 能看到）的问题。他们写描述代码结构的 AGENTS.md 文件。他们添加解释 API 模式的规则，而这些模式在代码中已经可见。**Agent 知道。你在添加噪声。**

一个好的上下文引擎读取你的代码库，所以你不必解释它。**你告诉 Agent 它已经能看到的东西越少，留给真正看不到的东西的注意力预算就越多**。

---

## Vercel 的反直觉实验

Vercel 在 Next.js 16 API 上比较了两种方法：

- **Skills**（按需检索）：Agent 可以访问文档，但从未查看。**零改进**。
- **AGENTS.md**（被动上下文）：他们将整个文档索引压缩成一个 **8KB 的 AGENTS.md 文件**。不是完整文档，只是一个指向可检索文件的索引。

结果：**100% 通过率**，涵盖 build、lint 和 test。

40KB 压缩到 8KB。满分。「笨」方法赢了。

> "We compressed our entire docs index into an 8KB AGENTS.md file. Not the full documentation. Just an index pointing to retrievable files. 100% pass rate."
>
> — Vercel Engineering Blog

---

## Anthropic 的警告

Anthropic 自己的文档明确警告：

> "Bloated CLAUDE.md files cause Claude to ignore your actual instructions."
>
> — Anthropic Engineering, "Effective Context Engineering for AI Agents"

Karpathy 更直白：

> "Too much or too irrelevant and the LLM costs might go up and performance might come down."
>
> — Andrej Karpathy

Martin Fowler 站点上的 Birgitta Böckeler 写道：

> "An agent's effectiveness goes down when it gets too much context, and too much context is a cost factor as well."

---

## 实践建议：给你的配置减肥

### 立即行动

1. **审核现有的配置数量**：如果你有超过 3 个 AI 配置文件，这是个信号
2. **问自己这个关键问题**：这条规则，Agent 能从代码库本身推导出来吗？如果能，删掉
3. **优先保留的工具类信息**：部署命令、测试运行方式、团队约定——这些 Agent 确实看不到

### 配置优先级

| 类型 | 例子 | 保留？ |
|------|------|--------|
| 代码结构 | 文件组织、模块关系 | ❌ Agent 能看见 |
| 编码风格 | tabs vs spaces、命名规范 | ❌ linter 已强制 |
| 架构决策 | 为什么这样设计 | ✅ Agent 看不到 |
| 团队约定 | 部署流程、测试方式 | ✅ Agent 看不到 |
| 外部依赖 | API 密钥、配置 | ✅ Agent 看不到 |

### 更好的配置策略

与其写详细的规则，不如：

1. **保持简短**：你的 AGENTS.md 应该像一个 8KB 的索引，而不是 40KB 的完整文档
2. **索引而非内容**：指向可检索文件的路径，而不是把所有内容直接写进去
3. **信任你的 Agent**：如果上下文引擎足够好，它会自己找到需要的信息

---

## 结论

我们正处于一个集体认知失调的时刻：工具已经变得更好，但我们的配置实践仍然停留在两年前。

556:1 的比例——每个贡献者对应 556 个复制者——告诉我们整个行业正在做什么：复制、分发、堆叠，没有人真正审核。

> "The difference this time: a bad webpack config made your build slow. A bad agent config makes your agent dumber."

给你的 Agent 指令减肥。不是因为它们不听话。是因为你给的信息太多了。

**Agent 配置的正确目标**：不是告诉 Agent 它已经能看到的一切，而是告诉它它真正看不到的东西。

---

> **引用来源**：
> - ETH Zurich (2026), "Evaluating AGENTS.md Files Across Multiple Coding Agents", arXiv:2602.11988
> - CodeIF-Bench (2025), "Instruction Following in Interactive Code Generation", arXiv:2503.22688
> - ConInstruct (2026), AAAI 2026, arXiv:2511.14342
> - PACIFIC (2025), arXiv:2512.10713
> - Anthropic Engineering, "Effective Context Engineering for AI Agents"
> - Vercel Engineering Blog, "Agents.md outperforms Skills in our agent evals"
> - Augment Code Blog, "Your agent's context is a junk drawer" (2026)