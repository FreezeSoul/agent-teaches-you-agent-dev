# "Thin Harness, Fat Skills" 架构——YC Garry Tan 的 Agent 工程实践

> 本文解读 YC President & CEO Garry Tan 在 YC Spring 2026 公开的「Thin Harness, Fat Skills」方法论，基于其 GitHub 开源项目 gbrain 的核心文档，结合 BestBlogs Issue #92 中提到的 YC 内部实践经验，探讨为什么 100x 效率差距来自 harness 设计而非模型本身。

---

## 核心论点

**大多数人在错误的地方寻找瓶颈。**

当人们听说有人用 AI coding agent 达到 100x 效率提升时，第一反应是：更好的模型、更大的参数、更贵的 API。但 Garry Tan 的断言是：

> "The 2x people and the 100x people are using the same models. The difference isn't intelligence. The difference is five concepts that fit on an index card."
> — Garry Tan, YC Spring 2026

同样版本的 Claude Code，在不同人手里产生 50 倍的产出差距——不是模型不同，是 **harness**（包裹模型的工程基础设施）的设计质量不同。这个结论在 2026 年 3 月 Anthropic 意外泄漏的 Claude Code 512,000 行源码中得到了工程层面的印证。

---

## 第一性原理：harness 的本质是什么

Garry Tan 给出了最简洁的定义：

> "The harness is the program that runs the LLM. It does four things: runs the model in a loop, reads and writes your files, manages context, and enforces safety."

这四件事——**循环执行、文件读写、上下文管理、安全防护**——就是 harness 的全部职责。任何超出这个范围的逻辑，都是放错位置的东西。

对应的反面 anti-pattern 是：

> "The anti-pattern is a fat harness with thin skills: 40+ tool definitions eating half the context window. God tools with 2 to 5 second MCP round-trips."

当一个 harness 塞入 40 多个工具定义、复杂的 MCP 封装、冗长的 REST API 包装器时，它做了两件致命的事：
1. 吃掉模型宝贵的 context window tokens
2. 把延迟和失败率同时放大了 3 倍

---

## Fat Skills 的真正含义

**Skill 文件是一个可复用的 markdown procedure，它教会模型「如何做某件事」，而不是「具体做什么」。**

这是理解「Thin Harness, Fat Skills」的核心跳板。大多数人对「prompt」的理解是往模型里塞指令，但这不是 skill。Skill 是**过程抽象**——它定义的是判断流程和决策步骤，具体参数由调用者注入。

Garry Tan 在 gbrain 文档中给了一个具体例子：

```
左侧是一个名为 /investigate 的 skill，七个步骤：
1. scope the dataset
2. build a timeline
3. diarize every document
4. synthesize
5. argue both sides
6. cite sources

它接受三个参数：TARGET, QUESTION, DATASET
```

同一个 skill，用在同一批 discovery emails 上可以是「医学研究分析师」，用在 FEC filings 上可以是「竞选资金调查员」。**skill 描述的是判断流程，调用者提供的是具体世界。**

> "This is the key insight most people miss: a skill file works like a method call. It takes parameters. You invoke it with different arguments. The same procedure produces radically different capabilities depending on what you pass in. This is not prompt engineering. This is software design, using markdown as the programming language and human judgment as the runtime."

Markdown 在这里不是文档，是**代码**。Skill 文件用模型思考的同一种语言来编码过程、判断和上下文，其封装能力远超僵化的源代码。

---

## Resolver：上下文路由的第三层

在 harness 和 skill 之外，Garry Tan 引入了第三个概念——**resolver**，上下文的路由表。

> "A resolver is a routing table for context. When task type X appears, load document Y first."

Skill 负责 HOW，resolver 负责 WHAT TO LOAD WHEN。

一个具体场景：开发者改了一个 prompt，提交时没有意识到有 eval suite 存在。没有 resolver，模型直接跑。有 resolver，模型在跑之前先读 `docs/EVALS.md`，其中写道「跑 eval suite，对比分数，如果准确率下降超过 2%，回滚并调查」。开发者不知道 eval suite 存在，resolver 在关键时刻把它加载进来了。

> "Skills say HOW. Resolvers say WHAT to load WHEN."

Claude Code 本身有一个内置的 resolver：每个 skill 的 description 字段就是隐式的 resolver，模型通过匹配用户意图和 skill 描述自动选择调用哪个 skill——「它像 Clippy，但真的能用」。

---

## 三层架构的完整图景

Garry Tan 给出的三层架构：

| 层级 | 名称 | 职责 | 代码量 |
|------|------|------|--------|
| **Top** | Fat Skills | 过程抽象、判断逻辑、领域知识 | 90% 价值所在 |
| **Middle** | Thin CLI Harness | 模型循环、JSON 输入输出、只读优先 | ~200 行 |
| **Bottom** | 你的应用 | QueryDB、ReadDoc、Search、Timeline | 确定性基础 |

对应的反模式（大厂常见问题）：

| 层级 | Anti-pattern | 结果 |
|------|-------------|------|
| **Top** | Thin Skills（只有几个通用 prompt） | 模型缺乏领域知识，输出泛泛 |
| **Middle** | Fat Harness（40+ 工具定义） | Context window 浪费 50%，延迟 3x |
| **Bottom** | 缺失或不可靠的基础工具 | 模型无法有效执行，频繁幻觉 |

**核心原则**：

> "Push intelligence UP into skills. Push execution DOWN into deterministic tooling. Keep the harness THIN."

---

## 实践案例：YC 6,000 个创始人申请评审

YC 面临的实际问题：Chase Center，2026 年 7 月，6,000 个创始人申请，每人有结构化申请表、1:1 顾问对话记录、公共信号（X 帖子、GitHub commits、Claude Code 产出记录）。

传统方案：15 人团队读申请、凭直觉判断、更新表格。200 个创始人勉强可以，6,000 个完全崩溃。

AI 方案的核心不是「更聪明的模型」，而是**正确的架构**：

- 模型读取50份文档，产生1页结构化判断
- 这个任务无法用 SQL 查询替代，无法用 RAG 管道替代
- 模型必须真正阅读、持有矛盾、注意到变化、写出结构化情报

这对应了 Garry Tan 的另一个核心区分：

> "Latent space is where intelligence lives. The model reads, interprets, decides. Judgment. Synthesis. Pattern recognition.
> Deterministic is where trust lives. Same input, same output. Every time."

当一个任务需要「对 6,000 个候选人的材料形成结构化判断」时，这是 latent space 的问题，强制塞入确定性系统注定失败。

---

## Garry Tan 的 CLAUDE.md 教训

> "A confession: my CLAUDE.md was 20,000 lines. Every single thing I ran across went in there. Every quirk, every pattern, every lesson. Completely ridiculous. The model's attention degraded. Claude Code literally told me to cut it back. The fix: about 200 lines. Just pointers to documents."

这个教训的价值：当你把一切信息都塞入 context，模型会失去对重要信息的注意力。正确的方式是**用 resolver 做路由**，让模型在需要某个特定 context 时才加载它，而不是一开始就全部塞进去。

---

## BestBlogs 的行业印证

BestBlogs Issue #92 提供了更多行业佐证。Garry Tan 在 YC 的实践：

> "GStack is my implementation of the thin harness fat skills approach. It's an open source repo that I built that turns Claude Code into an AI engineering team — with skills for office hours, design, code review, QA, and browser testing."

对应 GitHub 数据：`garrytan/gbrain` 目前 13,599 Stars、1,735 Forks，是 2026 年 Q2 AI Coding 工具链方向最炙手可热的新兴项目之一。

此外，BestBlogs 提到的另一个印证来自 Anthropic：

> "YC's Garry Tan wrote GStack in three weeks and already has more GitHub stars than Ruby on Rails — a 'thin harness, fat skills' approach that turns Claude Code into a full engineering team: Office Hours, adversarial review, Playwright browser testing, all reusable skills. He's written more code this year than in all of 2013."

---

## 工程实践建议

### 1. 检查你的 harness 复杂度

数一下你的 agent 项目定义了有多少个工具/工具定义。如果超过 20 个，你需要问自己：这些逻辑真的应该放在 harness 里吗？

### 2. Skill 文件从 5 步开始

从一个具体的 5-7 步 skill 入手（如 /investigate、/review_code、/write_test），用 markdown 写清楚每个步骤的判断条件，不要用代码。

### 3. 加入 resolver 路由

如果模型在执行任务时经常「不知道该读什么文档」，这意味着你需要 resolver。简单的实现：每个 skill 配一个 description，模型自动匹配。

### 4. 把执行下推到确定性工具

对比数据：
- Chrome MCP 做 screenshot + find + click + wait + read：15 秒
- Playwright CLI 做 screenshot + assert：200 毫秒

**75 倍的延迟差距不是 MCP 的问题，是选择了错误的抽象层级的问题。**

---

## 与现有架构的对比

| 维度 | 传统 Agent 架构 | Thin Harness, Fat Skills |
|------|----------------|-------------------------|
| 工具数量 | 20-50+（fat harness）| <10（thin harness）|
| 上下文策略 | 全部塞入 context | resolver 按需加载 |
| 技能组织 | prompt 模板散落 | markdown skill 过程抽象 |
| 执行层级 | LLM 负责判断+执行混在一起 | 判断在 skill，执行在确定性工具 |
| 扩展方式 | 修改 harness 代码 | 增加 skill 文件 |

---

## 结论

「Thin Harness, Fat Skills」不是一组新的 API 或框架，是一组**架构决策原则**——哪些逻辑应该放在 harness 里，哪些应该抽到 skill 文件里，哪些应该下推到确定性工具里。

这个框架的价值在于它解决了一个根本性问题：**在 context window 有限的情况下，如何让模型专注于正确的事。** 答案不是更大的 context window，是更聪明的上下文路由——把正确的信息在正确的时机加载进来，而不是一开始就把所有东西都塞进去。

对于正在构建 Agent 系统的工程师，Garry Tan 的建议是：

> "Build exactly what you need. Software doesn't have to be precious anymore."

---

**引用来源**：
- Garry Tan, "Thin Harness, Fat Skills", YC Spring 2026, https://github.com/garrytan/gbrain
- Y Combinator, "Inside Garry Tan's AI Coding Setup", YC Startup Library, https://www.ycombinator.com/library/OW-inside-garry-tan-s-ai-coding-setup
- BestBlogs.dev Issue #92, https://www.bestblogs.dev/newsletter/issue92