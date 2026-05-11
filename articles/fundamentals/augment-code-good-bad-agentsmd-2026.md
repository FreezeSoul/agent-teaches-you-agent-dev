# AGENTS.md 是模型升级：好的配置让编码 Agent 表现跃升，坏配置比没有更糟糕

> **核心论点**：Augment Code 的实证研究表明，配置良好的 AGENTS.md 文件可以让编码 Agent 的质量提升幅度相当于「从 Haiku 升级到 Opus」；但配置错误的 AGENTS.md 会让输出比没有配置更差。这一发现揭示了 Agent 配置工程学的核心原理：渐进式披露 > 全面覆盖，流程性工作流 > 架构性概述，决策表 > 约束清单。

---

## 背景：AGENTS.md 质量差异的惊人幅度

Augment Code 从其 monorepo 中抽取数十个 AGENTS.md 文件，测量它们对代码生成质量的影响。结果发现：

- **最好的 AGENTS.md**：在常规 bug fix 任务上，质量提升相当于从 Haiku 升级到 Opus（25% 提升）
- **最差的 AGENTS.md**：在复杂 feature 任务上，完整性下降 30%（比没有配置更差）

> "The best ones gave our coding agent a quality jump equivalent to upgrading from Haiku to Opus. The worst ones made the output worse than having no AGENTS.md at all."
> — [Augment Code Blog: A good AGENTS.md is a model upgrade](https://www.augmentcode.com/blog/how-to-write-good-agents-dot-md-files)

关键发现：**同一个 AGENTS.md 文件，在不同任务上可能产生完全相反的效果**。同一个决策表在 bug fix 任务上让 Agent 选对了数据获取模式（+25% best_practices），但在 feature 任务上让 Agent 陷入「参考文档旋涡」，打开了数十个 markdown 文件试图验证方案，最终产生了不完整的解决方案。

---

## 七大有效模式

### 1. 渐进式披露优于全面覆盖

最有效的 AGENTS.md 文件采用「技能式」结构：

- 主文件 100-150 行，覆盖高频场景和工作流
- 参考文档负责细节，按需加载

> "The 100–150 line AGENTS.md files with a handful of focused reference documents were the top performers... Once the main file got longer than that, the gains started reversing."

这一发现与 Anthropic 的「渐进式披露」（Progressive Disclosure）架构原则一致：不是把所有信息一次性塞进上下文窗口，而是让 Agent 在需要时主动拉取。

**工程建议**：主 AGENTS.md 文件不超过 150 行，每个参考文档有清晰的边界，Agent 知道何时该加载、何时该跳过。

### 2. 流程性工作流让 Agent 从失败到完成

将任务描述为「编号的多步骤流程」是测量到最有效的模式之一。一个六步 deploy 工作流示例：

1. 运行测试套件确保零回归
2. 更新 Changelog
3. 构建 Docker 镜像
4. 推送到 ECR
5. 更新 Lambda 函数版本
6. 发送 Slack 通知

> "A well-written workflow can move the agent from unable to complete a task to producing a correct solution on the first try."

实测数据：PR 中 missing wiring files 的比例从 40% 降到 10%，正确性 +25%，完整性 +20%。

**关键机制**：流程性描述解决了 Agent 的「任务边界模糊」问题——当 Agent 知道每一步做什么、什么时候完成，就不需要在「是否已经完成」这个问题上反复试探。

### 3. 决策表在写代码前解决歧义

当代码库有两种或三种合理方案时（如 React Query vs Zustand），决策表强制 Agent 在写代码前做出选择：

```
问题 → React Query → Zustand
服务器是唯一数据源？→ ✅
多个代码路径同时修改这个状态？→ ✅
需要乐观更新混合本地状态？→ ✅
```

> "PRs in this area scored 25% higher on best_practices. The table resolved the ambiguity before the agent wrote a single line of code."

这一模式解决了「架构选择拖延症」——Agent 不会在实现过程中反复切换技术栈，因为决策已经在写代码前做出。

### 4. 真实代码示例提升复用

3-10 行的生产代码片段比架构描述更有效：

- 真实的代码示例让 Agent 理解「代码风格」而非「规则描述」
- 示例数量控制在少数最相关的，避免 Agent 开始「模式匹配到错误的东西」

### 5. 领域特定规则仍然重要，但需要可执行

这是大多数开发者对 AGENTS.md 的直觉认知：「不要用 X，因为 Y」。但关键约束：

> "This works when the rule is specific and enforceable. It stops working when you stack dozens of them."

规则需要满足：具体 + 可执行。`Don't use X` 的效果不如 `Use X instead`。

### 6. 每条「不要」必须配对一条「要做」

纯警告式文档持续表现不佳：

| 写法 | 效果 |
|------|------|
| `Don't instantiate HTTP clients directly` | Agent 变得谨慎、试探性、减少工作量 |
| `Don't use X. Use the shared apiClient from lib/http with retry middleware.` | Agent 知道该做什么，然后继续推进 |

含有 15+ 连续「不要」且没有对应「要做」的文件导致 Agent **过度探索**——Agent 读取每条指令，试图判断是否适用于当前任务，然后开始根据每条警告验证解决方案，消耗大量上下文。

### 7. AGENTS.md 与周围文档环境共同决定效果

最差表现的 AGENTS.md 文件不是内容本身有问题，而是周围的文档环境太重：

- 一个 module 有 37 个相关文档，总计约 500K 字符
- 另一个有 226 个文档，总计超过 2MB

> "If your AGENTS.md is good but your module has 500K of specs around it, the specs are what the agent is reading."

**关键洞察**：即使 AGENTS.md 配置良好，如果周围有大量架构文档和 spec 文件，Agent 仍会找到并阅读它们。解决的不是入口点，而是周围的文档环境。

---

## 过度探索陷阱：最常见的失败模式

过度探索（Over-exploration）是 Agent 配置失败的最常见形态，两种模式导致它：

### 模式 A：过多的架构概述

Agent 被拉入阅读文档文件（有时数十个），试图「更好地理解架构」。它加载了 tens 或 hundreds of thousands 的 token 上下文，然后输出变得更差。

### 模式 B：过多的警告

大量「不要」但没有对应的「要做」产生特定失败：Agent 读取每条指令，尝试判断是否适用于当前任务，然后开始根据每条警告验证解决方案——30-50 条警告意味着即使任务完全不相关，Agent 也会读取 migration scripts、检查 API 版本兼容性、探索 auth middleware 代码。

---

## 文档发现机制：AGENTS.md 是唯一可靠的发现路径

Augment 追踪了数百个 session 中的文档发现率：

| 文档位置 | 发现率 |
|---------|--------|
| 工作目录下任意位置的 AGENTS.md | **100%（自动发现）** |
| AGENTS.md 中直接引用的文档 | **>90%（按需加载）** |
| 目录级 README.md（非自动加载） | **~80%（Agent 在该目录工作时）** |
| 嵌套 README（子目录） | **~40%** |
| `_docs/` 中的孤立文档 | **<10%** |

> "AGENTS.md is the only documentation location with reliable discovery. If something needs to be seen, it either lives there or is directly referenced from there."

**工程含义**：如果某个文档必须被看到，它要么直接放在 AGENTS.md 中，要么从 AGENTS.md 直接引用。间接引用的文档可靠性骤降。

Agent 也通过 grep 和语义搜索找到参考材料——约一半的搜索结果来自这些工具而非 AGENTS.md 引用。**维护 legacy 文档时，确保文档包含相关代码示例和描述性文本（可被搜索）是关键**。

---

## 模式选择决策表

根据目标选择模式：

| 如果想改善... | 使用这个模式 |
|--------------|-------------|
| 现有代码复用 | 来自 prod 代码的清晰相关示例 |
| 遵循代码库既定实践 | 组件和库的决策表 |
| 正确 wiring 大型功能 | 流程性 AGENTS.md |
| 处理 gotchas | 「不要」配对「要做」 |
| 防止上下文坍缩 | 通过参考文档的渐进式信息泄露 |
| 防止上下文坍缩 | 清晰的逻辑分隔，AGENTS.md 中说明每个参考文档的内容，但不展开 |
| 防止上下文坍缩 | 明显的建议，但 AGENTS.md 应只包含与周围代码相关的指导 |

---

## 新模式破坏旧文档

一个关键警告：当引入代码库中尚不存在的新模式时，AGENTS.md 可能主动将 Agent 引向错误方向。

Agent 会在写代码前对照 AGENTS.md 验证方案。如果新模式不在 AGENTS.md 中，Agent 可能用旧模式实现新功能。如果 AGENTS.md 描述了一个还不存在的模式，Agent 会将其理解为「应该这样做」但代码库中没有任何证据。

**这揭示了 AGENTS.md 的根本限制**：AGENTS.md 是对现有实践的编码，不是对目标状态的描述。当实践本身变化时，AGENTS.md 既是加速器也是惯性源。

---

## 对比：AGENTS.md 与 Anthropic 的 Context Engineering

Augment 的研究实际上是对 Anthropic Context Engineering 原则的实证验证：

| Augment 发现 | Anthropic 原则 |
|-------------|---------------|
| 渐进式披露（主文件 100-150 行） | Progressive Disclosure |
| 流程性工作流比架构概述更有效 | Section 3: How Claude uses context |
| 参考文档按需加载 > 全面注入 | Note-taking / Compaction |
| 过度探索是最大失败模式 | Attention Budget / Context Rot |

> "A good AGENTS.md is a model upgrade. A bad one is worse than no docs at all."

这句话本质上是对 Anthropic「Attention as Limited Resource」原则的重述：当 Agent 的注意力被低价值信息消耗时，输出质量下降。

---

## 结论：配置即 harness

Augment 的研究最终揭示了一个关键认知：**AGENTS.md 本质上是一种轻量级 harness**。它不是描述 Agent 应该做什么，而是约束 Agent 在特定上下文中的行为空间。

好的 AGENTS.md：
- 减少 Agent 的决策负担（决策表在写代码前解决歧义）
- 提供结构化的工作流程（流程性工作流）
- 管理信息流（渐进式披露）

坏的 AGENTS.md：
- 增加 Agent 的决策负担（过多的架构概述）
- 限制 Agent 的行动空间（过多的「不要」没有「要做」配对）
- 消耗注意力预算（过度探索陷阱）

> 笔者认为：AGENTS.md 的研究还揭示了一个更深层的模式——**文档质量与 Agent 性能的关系，本质上是「人类对系统行为的预期与 Agent 实际行为之间的 gap」**。好的 AGENTS.md 弥合了这个 gap；坏的 AGENTS.md 扩大了这个 gap。

---

**引用来源**：
- [Augment Code: A good AGENTS.md is a model upgrade. A bad one is worse than no docs at all.](https://www.augmentcode.com/blog/how-to-write-good-agents-dot-md-files) (2026-04-22)
- [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29)