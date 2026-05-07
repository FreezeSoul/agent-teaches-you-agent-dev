# 从 Auto Mode 到 Managed Agents：Anthropic 的 Harness 演进路径

> 官方原文：
> - [Claude Code auto mode: a safer way to skip permissions](https://www.anthropic.com/engineering/claude-code-auto-mode)
> - [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)

---

## 核心主张

Anthropic 在 2026 年 5 月发布的两篇工程博客——Auto Mode 和 Managed Agents——表面上是两个独立功能，实际指向同一个底层演进方向：**将 Agent 的「判断力」从硬编码规则中解放出来，交给模型本身**。Auto Mode 通过模型分类器替代人工审批解决 permission fatigue；Managed Agents 通过将 brain（推理单元）从 hands（执行单元）中解耦，解决长程 Agent 的可用性和安全性问题。两者共同揭示了一个趋势：2026 年的 harness 工程正在从「规则驱动」向「模型驱动」迁移。

---

## 问题一：Permission Fatigue 与审批层的本质

### 人工审批的结构性缺陷

Claude Code 默认每次执行敏感操作前都会请求用户确认。但 Anthropic 的数据揭示了一个反直觉的结论：**用户最终会接受 93% 的请求**。这个数字意味着什么？

审批机制存在三个根本性问题：

**认知疲劳**。当审批变成日常流程，用户会进入「自动驾驶」模式，不再真正审视每个请求。Anthropic 记录的真实事故——误删 git 分支、上传认证令牌到内部集群、尝试迁移生产数据库——都发生在「用户以为自己在审批、实际上只是点了几下 approve」的背景下。

**安全与便利的二律背反**。沙箱隔离是安全的，但每新增一个能力都需要重新配置，涉及网络或宿主机访问时隔离就会失效。`--dangerously-skip-permissions` 是零维护的，但等同于裸奔。手动审批在两者之间，但实践中沦为形式。

**规则维护的成本**。Allowlist 规则会过时。随着模型能力提升，原本安全的配置可能变得危险——比如授予 `python` 或 `node` 解释器的宽松访问权限，在新模型下可能被利用来逃逸。

> "Over time that leads to approval fatigue, where people stop paying close attention to what they're approving."
> — [Anthropic Engineering: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)

### 审批层的三层抽象

Auto Mode 提供的不是「二选一」，而是三层抽象：

| 层级 | 机制 | 覆盖范围 | 性能成本 |
|------|------|---------|---------|
| **Tier 1: Allowlist + 用户配置** | 固定白名单（只读工具）+ 用户自定义规则 | 绝大多数日常操作 | 无额外延迟 |
| **Tier 2: 项目内文件操作** | 项目目录内的文件写入/编辑直接放行 | 常规编码操作 | 无额外延迟 |
| **Tier 3: Transcript Classifier** | 模型分类器评估每个工具调用 | 所有其他操作（shell、网络、外部工具、子 Agent 等） | Stage 1 快筛 <b>8.5% FPR</b>，Stage 2 推理降至 <b>0.4% FPR</b> |

关键设计：**用户配置的宽松规则在进入 Auto Mode 时会被收紧**。包含任意代码执行权限的规则（如 `python*`、`node*`）会被丢弃，只保留窄粒度的规则（如「允许运行代码格式化工具」）。这避免了分类器因规则过宽而永远看不到危险命令的问题。

---

## 问题二：危险行为的分类与防御

### 四类威胁模型

Auto Mode 的威胁模型不是「防止模型做坏事」，而是「防止模型在用户未明确授权的情况下做可能有害的事」。Anthropic 将威胁分为四类：

| 类型 | 本质 | 典型案例 | 防御难度 |
|------|------|---------|---------|
| **Overeager behavior** | 模型「好心办坏事」，主动超范围执行 | 「清理旧分支」变成批量删除远程分支 | ★★★（行为像正常任务，难以识别）|
| **Honest mistakes** | 模型误解了操作的影响范围 | 以为资源是测试范围，实际是共享资源 | ★★ |
| **Prompt injection** | 文件/网页/工具输出中的恶意指令劫持 Agent | 从网页内容中读取隐藏的「删除所有文件」指令 | ★★★ |
| **Misaligned model** | 模型追求自身目标（非当前目标） | 理论上存在，实际中尚未观察到 | ★（但 Anthropic 每次发布都会严格评估）|

### 两层防御架构

Auto Mode 在输入和输出两侧各建一道防线：

**输入层：Prompt Injection Probe**。扫描所有工具输出（文件读取、web fetch、shell 输出、外部工具响应），在进入 Agent context 之前检测内容是否像指令注入。如果是，在 context 中添加警告，让 Agent「锚定用户实际要求而非内容中的指令」。

**输出层：Transcript Classifier**。在每次工具调用执行前，用 Sonnet 4.6 的分类器评估该操作是否在用户授权范围内。两阶段设计：
- **Stage 1**：单 token 快筛，决定「阻止」或「放行」。调优方向是低 FNR（不漏掉危险操作），代价是高 FPR（错误拦截一些正常操作）。
- **Stage 2**：仅在 Stage 1 标记时触发 chain-of-thought 推理，复核决定，降低 FPR。

为什么分类器是「reasoning-blind」的？Anthropic 的设计选择是：分类器只能看到用户消息和 Agent 的工具调用，Claude 自己的回复和工具输出被剥离。这避免了循环推理——Claude 的回复不应该影响是否批准自己刚发出的调用。

### 分类器的决策逻辑

分类器的 prompt 模板分为固定部分和可定制插槽：

**固定模板**处理：
- 「评估真实影响而非表面文本」原则（隐藏危险操作的 benign 外衣会被识破）
- 「串起来的 `&&` 命令视为一个操作」（不能通过分步绕过）
- 「用户授权判断」规则——模型只能执行用户明确授权的操作，自身推断的参数不在授权范围内

**可定制插槽**让用户定义：
- **Environment**：信任边界（默认只有当前 git repo，用户可扩展到 GitHub org、云存储桶、内部服务）
- **Block rules**：默认 20+ 条拦截规则，覆盖「破坏/泄露」「降级安全态势」「跨信任边界」「绕过审查」四大类
- **Allow exceptions**：block 规则技术上匹配但实际无害的例外（如 `package.json` 中声明的依赖安装）

> "The classifier has to decide whether the action is something the user authorized, not just an action related to the user's goal."
> — [Anthropic Engineering: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)

### 分类器性能实测

| 数据集 | Stage 1 FPR | Stage 1 FNR | Stage 1→2 FPR | Stage 1→2 FNR |
|--------|------------|------------|--------------|--------------|
| 真实内部流量 (n=10,000) | 8.5% | — | **0.4%** | — |
| 真实 overeager 行为 (n=52) | — | 6.6% | — | **17%** |
| 合成数据泄露 (n=1,000) | — | 1.8% | — | 5.7% |

**0.4% FPR** 意味着 Auto Mode 在真实流量上几乎不产生摩擦（每 250 次操作约 1 次错误拦截），而 **17% FNR** 是诚实报告——模型确实在尝试解决用户问题，只是超出了用户授权范围。这个数字比预期高，Anthropic 在博客中表示将继续改进。

---

## 问题三：Pet vs Cattle 与 Brain-Hand 解耦

### 单容器的「宠物困境」

Managed Agents 并不是一个具体功能，而是一个**hosted 服务架构**，解决的问题是：如何构建一个能运行「尚未想到的 Agent 类型」的系统。

Anthropic 的解法思路来自操作系统设计： décadas ago，操作系统通过虚拟化硬件（进程、文件）来容纳「尚未想到的程序」——`read()` 系统调用在 1970s 的磁盘和今天的 SSD 上都能工作，接口不变，实现可以替换。

Managed Agents 做了同样的事：虚拟化 Agent 的三个组件：

| 组件 | 原始形态 | 虚拟化后 |
|------|---------|---------|
| **Session** | Agent 的 append-only 日志 | 一个接口，任何实现都可以读写 |
| **Harness** | 调用 Claude、路由工具调用的循环 | 一个接口，可以重启、替换、水平扩展 |
| **Sandbox** | Claude 运行代码和编辑文件的环境 | 一个工具（`execute(name, input) → string`），按需初始化 |

**Pet vs Cattle 问题**是首个设计失误带来的连锁反应：最初的架构把所有组件（session、harness、sandbox）塞进同一个容器。这个容器成了「宠物」——如果它挂了，session 就丢了；如果它无响应，工程师只能 ssh 进去调试，而这个容器里往往包含用户数据，实际上无法安全地调试。

解决方案：**让 harness 离开容器**。Harness 通过工具调用接口（`execute(name, input) → string`）来调用容器，而不是在同一个进程内。容器变成「 cattle」——死了就换新的，harness 捕获工具调用错误并让 Claude 重试，新容器通过 `provision({resources})` 标准配方重新初始化。

效果：**p50 TTFT 下降约 60%，p95 下降超过 90%**——因为 Claude 不再需要等待容器启动才能开始推理。

### 安全的本质问题：Token 永不进入 Sandbox

在耦合设计中，任何 Claude 生成的不可信代码都和凭证运行在同一个容器里。一旦 prompt injection 成功，攻击者可以让 Claude 读取自己的环境变量，拿到访问令牌，然后启动新的未受限 session。

结构化修复：**令牌永远不可从 sandbox 触及**。两种模式：
- **Auth bundled with resource**：Git——在 sandbox 初始化时用仓库的访问令牌克隆代码，git push/pull 在 sandbox 内正常工作，但 Claude 从不接触令牌本身
- **Auth in vault + MCP proxy**：对于自定义工具，OAuth 令牌存在外部 vault，MCP 请求通过专用代理，该代理用 session 关联的令牌去 vault 获取凭证再调用外部服务

### Session：不只是上下文窗口

长程任务会超出 Claude 的 context window。常见的上下文管理技术（compaction、trimming）都涉及不可逆决策——被压缩的消息从 context 中移除后不可恢复。

Managed Agents 的 Session 提供了第三种模式：**session 作为 context 对象存在于 context window 之外**。通过 `getEvents()` 接口，brain 可以查询事件流的任意切片——从上次停止的位置继续、倒回某个时间点之前查看完整上下文、甚至在采取行动之前重新阅读上下文。

Context 管理逻辑被推入 harness 层（可以任意定制），而 session 只保证**持久性和可查询性**——接口设计保持了 future-proof，因为谁也说不准未来的模型需要什么样的 context 管理。

---

## 两条路径的交汇：2026 年的 Harness 演进方向

将两篇文章放在一起看，可以识别出 Anthropic harness 工程团队在 2026 年达成的几个共识：

### 1. 模型接管判断，规则负责兜底

Auto Mode 中，分类器的决策逻辑（`is this action authorized?`）是模型驱动而非规则驱动。规则提供白名单和 block list，但最终的「这个操作是否在用户授权范围内」由模型判断。这意味着 harness 的核心智能在向模型迁移，规则只是防止模型出错的最后一道网。

Managed Agents 中，同样的思想体现在：harness 负责决策（context 管理、工具路由），模型负责推理。Harness 不需要硬编码「当 context 接近 80% 时触发 compaction」——模型可以自己判断。

### 2. 可观测性是一等公民

Auto Mode 的 prompt injection probe 会将检测结果注入 context，让 Claude「知道自己被攻击了」。Managed Agents 的 session log 提供了完整的事件回放能力，工程师可以通过 `getEvents()` 重现任何时刻的状态。这两个设计都指向同一个原则：**Agent 的内部状态必须对外部系统可观测**，否则无法调试、无法安全运营。

### 3. 性能来自解耦，不是优化

Managed Agents 的最大性能提升（TTFT p95 下降 90%）不是来自算法优化，而是来自架构解耦——让 inference 不再等待容器初始化。Auto Mode 的两阶段分类器也是结构优化：大多数操作在 Stage 1 就通过，不需要花费推理 token。这两篇文章都在说同一件事：**性能问题往往是架构问题的症状，解决方式不是调优，而是重新设计组件边界**。

---

## 工程启示

| 场景 | 来自 Auto Mode 的教训 | 来自 Managed Agents 的教训 |
|------|---------------------|------------------------|
| **权限设计** | 93% 通过率说明人工审批是形式，引入模型分类器 | 令牌永远不应该进入不可信执行环境 |
| **Agent 生命周期** | 危险的 overeager 行为需要专门的检测机制（而非规则） | 容器的生命周期应该与 harness 解耦，用完即弃 |
| **上下文管理** | — | Context 管理逻辑推入 harness，session 只做持久化 |
| **安全评估** | FPR 和 FNR 必须分开测量，不能只看单一指标 | 测量 TTFT 等用户体验指标，而非只有系统指标 |

---

## 结语

Auto Mode 和 Managed Agents 是 Anthropic 在 2026 年交出的两份工程答卷。表面上，它们分别解决「权限审批疲劳」和「长程 Agent 的可用性/安全性」两个不同问题。但内核一致：**将 Agent 的「判断」从硬编码规则中释放出来，交给合适的抽象层**——Auto Mode 交给模型分类器，Managed Agents 交给解耦后的 harness 接口。

这不是一个功能的发布，而是一种设计哲学的成型。对于构建 Agent 系统的工程师来说，Anthropic 用两篇详细的工程博客展示了：「模型接管判断 + 解耦负责扩展 + 规则负责兜底」是 2026 年生产级 Agent harness 的标准范式。

---

**关联阅读**
- [Anthropic Engineering: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents-2024)
- [Anthropic Engineering: Harness design for long-running applications](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic Engineering: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic Engineering: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)