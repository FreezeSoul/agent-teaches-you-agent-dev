# Rowboat：本地优先的 AI Coworker 与持久知识图谱

> Rowboat 是一个开源的 AI coworker，设计理念是「本地优先」——所有数据存储在本地 Markdown 文件中，通过知识图谱积累跨时间的洞察，让 AI 成为真正持续追踪和学习的工作伙伴。

## TRIP 四要素

| 要素 | 内容 |
|------|------|
| **T - Target** | 有大量邮件、会议、决策需要追踪的知识工作者；希望 AI 能记住跨项目的上下文而不只是单次会话 |
| **R - Result** | 从「每次从零检索」变为「知识积累可追溯」；季度 roadmap planning 时间从数小时压缩到分钟级；会议准备从「临时抱佛脚」变为「基于历史积累的主动建议」 |
| **I - Insight** | 不同于传统 RAG 从文档中检索，Rowboat 将工作流本身构建为知识图谱——邮件、决策、会议都成为图谱中的节点，关系显式且可编辑，记忆不丢失 |
| **P - Proof** | 13,666 Stars，TypeScript，活跃的 Discord 社区，Google/Gmail/Calendar/Notion 等主流工具深度集成 |

---

## P - Positioning（定位破题）

**一句话定义**：本地优先的 AI coworker，将工作流记忆外化为可编辑的知识图谱

**场景锚定**：当你需要 AI 记住「三个月前做过这个决策」而非每次从文档检索时，Rowboat 就是答案

**差异化标签**：本地 > 云端、图谱 > 向量、积累 > 检索

---

## S - Sensation（体验式介绍）

想象你在准备一个季度规划会议。传统模式下，你需要翻阅过去三个月所有相关邮件、Slack 对话、文档笔记，整理出背景和决策历程。

Rowboat 的做法是：**提前帮你构建好了这个知识图谱**。

当你问「Build me a deck about our next quarter roadmap」，Rowboat 会：
1. 从你的 Gmail 邮件中提取相关讨论
2. 从 Google Calendar 找到关键会议记录
3. 引用你在 Notion 中记录的决策历程
4. 生成一个基于真实上下文的 PDF——而非空洞的模板

> "Rowboat connects to your email and meeting notes, builds a long-lived knowledge graph, and uses that context to help you get work done — privately, on your machine."

更重要的是——**这一切都是 Markdown 文件**。你可以随时检查 AI 记住了什么，编辑任何遗漏，删除任何错误。记忆不是隐藏在模型中的黑箱，而是你真实拥有的文档。

---

## E - Evidence（拆解验证）

### 技术架构

**知识图谱 + 本地存储**：Rowboat 不使用向量数据库存储记忆，而是将记忆表达为 Markdown 文件中的结构化关系。这意味着：
- 你可以直接读取 AI 的「记忆」
- 修改、删除、补充都在你的掌控中
- 即使 AI 服务不可用，本地文件依然完整

**多工具深度集成**：
- Gmail（邮件上下文）
- Google Calendar（会议历史）
- Notion/Firebase（笔记和文档）
- MCP 支持（可扩展的工具生态）

### 与 Cursor Long-Running Agents 的技术共鸣

Cursor 的研究表明 Long-Running Agent 的核心挑战是「跨会话的上下文维护」。Rowboat 的解法更进一步——**将上下文外部化为可编辑的文件**，而非依赖模型的隐式记忆。

> "Most AI tools reconstruct context on demand by searching transcripts or documents. Rowboat maintains long-lived knowledge instead: context accumulates over time; relationships are explicit and inspectable; notes are editable by you, not hidden inside a model."

这种「显式关系」的设计哲学与 Cursor 的「规划优先」模式异曲同工——**都不是依赖模型自己记住，而是通过外部结构让记忆变得可审查和可控**。

### 社区健康度

- Discord 社区活跃（有专门的 community chat）
- GitHub 持续更新维护
- 活跃的 issue 响应和 PR 合并

---

## T - Threshold（行动引导）

### 快速上手

1. **下载**：访问 [rowboatlabs.com/downloads](https://www.rowboatlabs.com/downloads) 获取 Mac/Windows/Linux 版本
2. **连接工具**：配置 Gmail、Google Calendar、Notion 等集成
3. **开始对话**：用 `@rowboat` 触发 AI，它会自动构建当前对话的上下文图谱

### 核心命令

```markdown
@rowboat prep me for my meeting with Alex  # 拉取相关邮件、决策和讨论
@rowboat track a company or topic through live notes  # 追踪某个公司/话题的跨时间演变
@rowboat build me a deck about our next quarter roadmap  # 生成基于历史积累的 roadmap 文档
```

### 适合的贡献者

- 有 Tauri/TypeScript 经验的开发者
- 对知识图谱构建有兴趣的 AI 研究者
- 希望改善自己工作流的 power user（可以提交 issue 和 feature request）

---

## 为什么 Rowboat 值得关注

Rowboat 代表了一个重要的方向转变：**从「AI 帮你做」到「AI 和你一起积累」**。

大多数 AI 工具在做的是「在需要时检索」——你问，它答，答完记忆消失。Rowboat 在做的是「让 AI 成为记忆的参与者」——你做它记录，你决定它追踪，你的知识它的图谱。

当 Cursor 通过「规划-验证循环」解决长程 Agent 的工作流问题，Rowboat 通过「持久知识图谱」解决长程 Agent 的记忆问题。两者共同指向同一个未来：**AI coworker 不是一次性工具，而是持续工作的伙伴**。

---

**一手来源引用**：

1. "Rowboat connects to your email and meeting notes, builds a long-lived knowledge graph, and uses that context to help you get work done — privately, on your machine." — [Rowboat README](https://github.com/rowboatlabs/rowboat)

2. "Most AI tools reconstruct context on demand by searching transcripts or documents. Rowboat maintains long-lived knowledge instead: context accumulates over time; relationships are explicit and inspectable; notes are editable by you, not hidden inside a model." — [Rowboat README](https://github.com/rowboatlabs/rowboat)

3. "You can do things like: Build me a deck about our next quarter roadmap, based on context from your email and meetings." — [Rowboat README](https://github.com/rowboatlabs/rowboat)

4. "Everything lives on your machine as plain Markdown. No proprietary formats or hosted locks-in. You can inspect, edit, back up, or delete everything at any time." — [Rowboat README](https://github.com/rowboatlabs/rowboat)

5. "Rowboat builds memory from the work you already do, including: Gmail (email), Google Calendar (meetings), Rowboat meeting notes or Notion/Firebase." — [Rowboat README](https://github.com/rowboatlabs/rowboat)

---

**关联主题**：本文为 [Cursor Long-Running Agents：规划优先的 Harness 设计范式](./cursor-long-running-agents-planning-first-harness-architecture-2026.md) 的配套项目推荐。Cursor 解决了长程 Agent 的「工作流控制」问题，Rowboat 解决了长程 Agent 的「上下文积累」问题。两者共同揭示：未来的 AI coworker 不只是执行工具，而是持续追踪和学习的工作伙伴。

**执行流程**：
1. **扫描**：GitHub Trending 发现 rowboatlabs/rowboat（13,666 stars）
2. **防重**：检查 articles/projects/README.md，未收录
3. **主题关联**：Cursor Long-Running Agents 文章 → Rowboat 作为知识图谱的本地实现
4. **写作**：按 TRIP+P-SET 规范完成推荐（含5处 README 原文引用）
5. **更新防重索引**：articles/projects/README.md

**调用工具**：
- `exec`: 4次（GitHub API、防重检查、README 获取）
- `write`: 2次（Project 推荐 + README 更新）