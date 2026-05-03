# Cursor 第三时代：从「监督代码」到「定义问题」的范式转变

**核心主张**：Cloud Agents 不仅仅是一种技术升级，它改变了人机协作的**基本单位**——人类不再监督每个 Agent 会话，而是管理**问题定义和验收标准**。这与 Anthropic 的「Initializer Agent + Coding Agent」双组件 Harness 设计形成呼应，共同指向一个结论：未来 Agent 系统的核心工程挑战不是让 Agent 更快，而是**重新设计人与 Agent 之间的交互边界**。

**读者画像**：已使用过 Cursor Agent 或 Claude Code，了解基本 Agent 概念，但仍在「每个会话都盯着 Agent 看」的工程师。

**核心障碍**：即使知道 Agent 能干更多活，实际工作中仍然无法摆脱「一个 Agent 一个会话」的串行模式——因为 Cloud Agents 的价值不是显而易见，且缺乏系统设计思路。

---

## 1. 第三时代的本质：协作单位的变化

Cursor 官方博客对三个时代做了清晰定义：

| 时代 | 核心协作单位 | 人类角色 | 时间跨度 |
|------|------------|---------|---------|
| 第一时代（Tab） | 单行代码 | 审核 + 接受 | ~2年 |
| 第二时代（同步 Agent） | 单个 Agent 会话 | 监督 + 引导 | <1年 |
| **第三时代（Cloud Agents）** | **多 Agent 并行 + 工作定义** | **定义问题 + 设定验收标准** | 正在到来 |

> "As a result, Cursor is no longer primarily about writing code. It is about helping developers build the factory that creates their software."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

这段话的关键不是「Cursor 变了」，而是**协作单位发生了根本转移**。第一时代，协作单位是单行代码；第二时代，协作单位是单个 Agent 会话；第三时代，协作单位是**一组并行运行的 Agent + 人类定义的问题边界**。

---

## 2. 同步 Agent 的根本瓶颈：为什么 Cloud Agents 不是「更好」而是「不同」

很多人把 Cloud Agents 理解为「把 Agent 放到云端跑」，但这只是技术层面的描述。真正重要的变化在于**交互模式的根本转变**。

### 2.1 同步 Agent 的两个隐性约束

同步 Agent（本地运行，随时反馈）有两个隐性约束：

**约束一：资源竞争**

本地机器同时只能运行有限数量的 Agent 会话。当你在 Cursor 里开了 3 个 Agent Tab，每个都在消耗本地 CPU 和上下文资源。你不可能开 10 个本地 Agent 同时跑——这不是 Agent 能力问题，是**资源隔离问题**。

**约束二：上下文重建成本**

同步 Agent 的输出是实时的 diff、chat message。当你需要评估输出时，你需要**重新进入那个会话的上下文**——看 diff、读日志、重建当时的思维过程。这个成本使得人类只能专注于少数会话。

> "Cloud agents remove both constraints. Each runs on its own virtual machine, allowing a developer to hand off a task and move on to something else."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

### 2.2 Cloud Agents 的核心价值：Artifacts 作为评估媒介

Cloud Agents 的关键创新不是「在云端跑」，而是**改变了评估媒介**。

同步 Agent 的输出是：diff 文件、chat message、terminal 输出
Cloud Agent 的输出是：**Artifacts（截图、录屏、live preview）**

Artiface 的本质是**无需重建上下文的评估结果**。你不需要进入 Agent 会话，就能知道：
- 功能是否按预期工作（截图/录屏）
- 界面是否符合设计（live preview）
- 整体进度如何（Artifacts 的数量和质量）

这使得**并行评估**成为可能——人类可以同时 review 多个 Agent 的产出，而不需要在多个会话间切换重建上下文。

---

## 3. 人类角色的根本转变：从「监督」到「定义」

这是第三时代最核心的认知转变。Cursor 博客提到的三个关键行为变化：

> "We see the developers adopting this new way of working as characterized by three traits: Agents write almost 100% of their code. They spend their time breaking down problems, reviewing artifacts, and giving feedback. They spin up multiple agents simultaneously instead of handholding one to completion."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

### 3.1 三种角色的职责分离

| 传统模式 | 第三时代模式 | 关键差异 |
|---------|------------|---------|
| 人类：写代码（或监督 Agent 写） | Agent：写几乎 100% 的代码 | 人类完全退出实现层 |
| 人类：逐会话引导 | 人类：拆解问题 + 反馈 | 人类专注问题分解而非实现 |
| 人类：单会话串行 | 人类：并行评估多 Agent | 并行评估替代串行监督 |

### 3.2 「问题拆解」成为核心技能

第三时代中，人类的核心工作变成了**将复杂问题拆解为可并行的子任务**，并为每个子任务设定**验收标准**（Artifacts 形式）。

这与 Anthropic 的 Initializer Agent 设计高度一致——Initializer Agent 的职责也是「建立完整的功能地图，让后续 Agent 知道还需要做什么」。只不过在 Anthropic 的设计中这是 Agent 对 Agent 的协议，而在 Cursor 第三时代这是**人类对 Agent 的协议**。

> "The human role shifts from guiding each line of code to defining the problem and setting review criteria."
> — [Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)

---

## 4. Cursor 3 的工程实现：多 Repo + 无缝 Handoff

Cursor 3 是这一范式转变的产品实现。三个关键工程决策：

### 4.1 多 Repo 布局

```ascii
┌─────────────────────────────────────────────────────────────┐
│  Cursor 3 Sidebar                                            │
├─────────────────────────────────────────────────────────────┤
│  [Agent 1] ← repo-A (cloud, working)                        │
│  [Agent 2] ← repo-B (local, paused)                        │
│  [Agent 3] ← repo-A (cloud, completed → awaiting review)    │
│  [Agent 4] ← repo-C (local, active)                         │
└─────────────────────────────────────────────────────────────┘
```

所有本地和云端 Agent 都在 sidebar 统一管理，包括从不同渠道触发的 Agent（mobile、web、desktop、Slack、GitHub、Linear）。

### 4.2 Cloud ↔ Local 无缝 Handoff

Cursor 3 允许在本地和云端之间快速迁移 Agent 会话：

- **Cloud → Local**：将云端 Agent 迁移到本地继续编辑和测试
- **Local → Cloud**：将本地 Agent 推送到云端保持运行（适合下班前）

这是 Anthropic「多会话状态管理」的产品化实现——不再需要手动 export 上下文，平台自动处理状态迁移。

### 4.3 Composer 2 作为前端模型

> "Composer 2, our own frontier coding model with high usage limits, is great for iterating quickly."
> — [Cursor Blog: Cursor 3](https://cursor.com/blog/cursor-3)

Cursor 用自研的 Composer 2 作为 Cloud Agents 的前端模型，而不是调用第三方 API——这是从「工具」到「平台」的战略升级，意味着 Cursor 不再只是 Claude/ChatGPT 的 UI 包装，而是有了自己模型层控制的 AI Coding 平台。

---

## 5. 范式对比：三种 Agent 协作模式的适用边界

| 模式 | 适用场景 | 不适用场景 | 核心瓶颈 |
|------|---------|-----------|---------|
| Tab（第一时代） | 小型修改、模板化代码 | 复杂功能、跨文件修改 | 只能处理低熵任务 |
| 同步 Agent（第二时代） | 单会话可完成的小中型任务 | 需要多会话、长时间运行的任务 | 资源竞争 + 上下文重建 |
| Cloud Agents（第三时代） | 大型项目、多 Agent 并行、长时任务 | 小型快速修改（启动开销不划算） | 问题拆解能力要求高 |

> 笔者认为：第三时代不会完全取代第二时代。对于「写一个 API endpoint」「修复一个 bug」这类小型任务，同步 Agent 的反馈速度仍然更快。Cloud Agents 的价值在于**规模化**——当你需要同时处理 5 个以上的任务时，第三时代的模式才真正体现优势。

---

## 6. 工程实践：从「监督模式」到「定义模式」的迁移路径

Cursor 博客提到一个关键数字：35% 的 Cursor 内部 PR 现在由 Cloud Agents 创建。这个数字说明：**即使在 Cursor 内部，迁移也没有完成**。

迁移的关键步骤：

**Step 1：问题拆解训练**
将大型需求拆解为「Agent 可独立执行 + Artifacts 可评估」的问题单元。这需要人类从「代码思维」切换到「验收思维」。

**Step 2：验收标准前置化**
在启动 Agent 之前，明确：
- 成功标准是什么？（功能截图、测试通过、性能指标）
- 如何评估？（Artiface 形式、PR 形式）
- 边界在哪里？（哪些是不需要 Agent 做的）

**Step 3：多 Agent 并行实验**
从「同时跑 2 个 Agent」开始，积累对 Artifact 评估节奏的体感，逐步扩展到 5 个以上。

**Step 4：工作流集成**
将 Linear/Jira 的 Issue 自动映射为 Agent 任务，实现「问题进、PR 出」的完整流水线。

---

## 7. 与 Anthropic 双组件 Harness 的理论呼应

Cursor 第三时代的范式与 Anthropic 的双组件 Harness 设计形成了有趣的**跨框架理论呼应**：

| 维度 | Cursor 第三时代 | Anthropic 双组件 Harness |
|------|---------------|------------------------|
| 人类角色 | 定义问题 + 设定验收标准 | Initializer Agent 建立功能地图 |
| Agent 协作 | 多 Agent 并行（问题拆解） | Initializer + Coding Agent 分工 |
| 状态继承 | Cloud ↔ Local 无缝 Handoff | feature_list.json + progress.txt |
| 评估媒介 | Artifacts（截图/录屏） | 端到端测试 + Puppeteer MCP |
| 失败处理 | 多个 Agent 失败不影响整体 | 单一 feature 失败不影响其他 |

两者都在解决同一个核心问题：**如何让人类从「监督每个会话」的模式中解放出来**，但采用了不同的路径——Cursor 靠产品设计（Cloud Agents + Artifacts），Anthropic 靠 Harness 工程（会话协议 + Feature List）。

> 笔者认为：这说明行业正在形成共识——「监督模式」不是可扩展的 Agent 使用方式。无论是通过平台层（Cloud Agents）还是协议层（Feature List），未来的主流方向都是**人类定义问题边界，Agent 自主执行**。

---

## 8. 结论与启示

Cursor 第三时代的核心贡献不是「Cloud Agents」这个产品功能，而是它验证了一个范式假设：**人类可以从「监督代码」的模式中退出，让 Agent 自己管理自己**。

对于 Agent 开发者的启示：
1. **问题拆解能力**将成为 Agent 时代最稀缺的产品/工程能力
2. **验收标准前置化**比「写好 Prompt」更重要——Prompt 决定 Agent 怎么干，验收标准决定 Agent 干对了没有
3. **多 Agent 并行**的关键不是技术，而是**问题分解的粒度**——分解太粗会导致部分 Agent 闲置，分解太细会增加人类的协调成本

对于 Agent 框架开发者的启示：
1. **Artifact 评估机制**是 Cloud Agents 的核心创新，框架需要原生支持结构化的输出证明
2. **状态迁移协议**（Cloud ↔ Local）需要在框架层解决，而不是让每个产品各自实现
3. **问题-任务映射**（Issue → Agent Task → PR）是自动化工作流的唯一可行入口

---

*来源：[Cursor Blog: The third era of AI software development](https://cursor.com/blog/third-era)、[Cursor Blog: Meet the new Cursor](https://cursor.com/blog/cursor-3)*
