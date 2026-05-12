# 模型驱动 Harness 演进：2026 年 Agent 工程的关键范式转移

## 核心主张

> **2026 年上半年，主流 AI 厂商的 harness 工程出现了一个清晰的演进方向：原本依赖规则、配置和人工审批的 harness 逻辑，正在系统性地迁移给模型本身。Anthropic 的 Auto Mode（权限判断）、Managed Agents（上下文管理）、Cursor 的 Autoinstall（环境准备），以及 OpenAI 的 Auto-review（审批分流）分别独立展示了这一趋势的不同切面。这些看似独立的功能，实则是同一个范式转移的不同实例——「规则引擎 → 模型驱动」。本文通过深度解析这四条线索，揭示这个范式转移的底层逻辑、工程动机和适用边界。**

---

## 一、问题的本质：规则引擎的天花板

### 传统 Harness 的规则驱动困境

在 2025 年的主流 harness 设计中，大量决策逻辑以规则形式硬编码：

- **权限审批**：基于 allowlist/rejectlist 的静态规则，用户逐条审批
- **上下文管理**：基于固定窗口的 compaction 策略或周期性 context reset
- **环境准备**：人类工程师预先配置或依赖固定的环境模板
- **审批分流**：按规则分流哪些操作需要人工审批，哪些可以直接执行

这些规则在模型能力较弱时是合理的——模型不具备足够的判断力来替人类做决策。但 2026 年的模型能力已经让这个前提变得值得质疑。

> "We keep an internal incident log focused on agentic misbehaviors. Past examples include deleting remote git branches from a misinterpreted instruction, uploading an engineer's GitHub auth token to an internal compute cluster, and attempting migrations against a production database."
> — [Anthropic Engineering: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)

这段话揭示了一个深层问题：**规则无法覆盖所有危险场景**。当 Agent 在上下文窗口中看到 credentials 时，它有判断力理解「这不应该被上传」，但 allowlist 规则无法表达这个约束——因为允许读取文件和允许外传数据之间没有明确的规则边界。

### 规则维护的成本随时序增长

Anthropic 在 Auto Mode 文章中记录了一个关键数据：**用户最终接受了 93% 的审批请求**。这个数字有两重含义：

1. 人工审批在实践中形同虚设（审批疲劳）
2. 规则维护者试图通过 allowlist 控制 Agent 行为，但用户不断绕过后者

> "Over time that leads to approval fatigue, where people stop paying close attention to what they're approving."
> — [Anthropic Engineering: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)

规则系统的第二个问题：**规则随模型能力提升而失效**。Anthropic 明确指出，当模型能力更强时，原本安全的 allowlist 规则（如授予 `python` 解释器的宽松访问权限）会变成新的攻击面。规则无法泛化，它只能针对已知的威胁模型编写。

---

## 二、Auto Mode：权限判断从规则到模型

### 架构解析

Auto Mode 是 Claude Code 中将权限判断迁移给模型的典型案例。它用两层防御替代了原来的人工审批规则：

**输入层**：prompt-injection probe
- 扫描工具输出（文件读取、Web 内容、Shell 输出）中是否存在注入攻击
- 发现可疑内容时，在送入 Agent 上下文前插入警告锚点（warning anchor）
- 模型根据这个锚点自行判断「这是一个可疑内容，我应该更谨慎」

**输出层**：transcript classifier（双阶段）
- **Stage 1**：快速 single-token filter，判断是否阻止
- **Stage 2**：如果 Stage 1 标记，则执行 chain-of-thought reasoning 降低误报

关键设计选择：classifier 看不到 Claude 自己的消息和工具输出，只能看到 user messages + agent tool calls——**reasoning-blind by design**，防止 Claude 的自我辩护影响判断。

### 为什么是模型而不是规则？

Auto Mode 的核心洞察是：**规则只能覆盖已知的危险模式，而模型可以泛化到未见过的危险场景**。

考虑以下真实案例（来自 Anthropic 事故日志）：

> "A user asked to 'clean up old branches.' The agent listed remote branches, constructed a pattern match, and issued a delete. This would be blocked since the request was vague, the action irreversible and destructive, and the user may have only meant to delete local branches."

这个场景中，「模糊请求 + 不可逆操作」的组合在任何 allowlist 中都不存在对应规则——因为它需要理解用户的真实意图边界，而这恰恰是模型的专长。

### 权限三层架构的工程启示

Auto Mode 的权限架构分为三层，每层有明确的职责边界：

| 层级 | 职责 | 模型参与度 |
|------|------|-----------|
| Tier 1: 静态 allowlist | 明确安全的只读操作，零判断成本 | 无 |
| Tier 2: 项目内文件操作 | 项目目录内的文件编辑，通过 VCS review | 无 |
| Tier 3: Classifier 决策 | 外部操作、网络请求、子代理spawn | **完整参与**（双阶段推理）|

这个分层结构的工程价值在于：**低风险操作零延迟，高风险操作才有模型参与**。不是所有权限决策都需要模型推理——对于明确安全的操作，静态规则更快。

---

## 三、Managed Agents：上下文管理从过程到模型

### Session 架构的核心思想

Anthropic Managed Agents 的核心创新是将 **Session（事件日志）从 Claude 的上下文窗口中解耦出来**，作为外部可查询的上下文对象：

```
Harness → getEvents(sessionId, range) → 事件片段
         → 任意转换逻辑（context organization / prompt cache 优化）
         → 注入 Claude 上下文窗口
```

这与传统方案的本质区别：

**Compaction（传统）**：在上下文窗口内压缩历史消息 → 消息被销毁，不可恢复

**Context Reset（传统）**：清除上下文窗口，起始新 Agent → 依赖 handoff artifact 质量

**Session 外置（Managed Agents）**：上下文窗口只保留当前切片，全部历史持久化在 Session 中 → 任意时刻可回溯

### 为什么这是「模型驱动」？

关键在于 **getEvents() 返回的事件片段如何被使用，完全由 harness 自己决定**——而 harness 的决策逻辑，就是一个小型模型推理系统。

Anthropic 明确承认：

> "Any fetched events can also be transformed in the harness before being passed to Claude's context window. These transformations can be whatever the harness encodes, including context organization to achieve a high prompt cache hit rate and context engineering."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这意味着：
1. **模型决定何时需要回溯上下文**（而不是规则说「每 N 轮压缩一次」）
2. **模型决定如何组织上下文以提高 cache hit rate**（而不是固定的压缩策略）
3. **模型决定回溯的窗口大小**（而不是 reset 策略）

### 性能数据：从容器耦合到 Brain/Hands 解耦

Managed Agents 最有力的论据来自性能数据：

- **p50 TTFT 下降约 60%**
- **p95 TTFT 下降超过 90%**

这个改进的直接原因是：**不是所有 session 都需要 sandbox 容器**。在耦合设计中，每个 session 都必须等待容器启动（克隆代码、拉取事件、启动进程）才能开始推理。在解耦设计中，如果 session 的第一个请求是纯推理任务（如「帮我分析这个代码库」），inference 可以在容器启动前就开始——因为 Session 事件可以被立即拉取，不需要等待 sandbox 初始化。

> "Decoupling the brain from the hands means that containers are provisioned by the brain via a tool call only if they are needed. So a session that didn't need a container right away didn't wait for one."
> — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

这个决策（是否需要 sandbox）本质上是模型推理的一部分——**模型决定「这个任务是否需要执行工具」**，而工具执行才需要 sandbox。这是规则系统无法表达的，因为规则无法预测模型在每个具体任务中的行为。

---

## 四、Cursor Autoinstall：环境准备从配置到模型协作

### 双阶段自举机制

Cursor Composer 的 Autoinstall 系统展示了规则→模型迁移的第三个维度：**环境准备本身变成一个可委托给模型的协作任务**。

**Stage 1：Goal-Setting Agent**
- 输入：未配置的代码仓库
- 输出：10 条目标命令 + 每条命令的预期输出描述
- Agent 探索 README、Makefiles、语言特定的包管理器命令

**Stage 2：Goal-Achieving Agent**
- 输入：仓库初始状态 + Stage 1 选出的 3 条目标命令
- 输出：配置好的可运行环境 + 验证命令执行结果
- 如果失败，最多重试 5 次

**Stage 3（如需要）**：如果 Stage 2 5 次重试后仍无法达到满意配置，丢弃该环境

### 为什么这是规则→模型的迁移？

传统的环境配置是**规则驱动的**——人类工程师编写配置脚本（Dockerfile、setup.sh），覆盖已知的环境依赖关系。但这个方法有两个根本性问题：

1. **不可扩展**：每换一个新代码仓库都需要新的配置脚本
2. **无法处理未知依赖**：规则只覆盖已知的依赖图

Autoinstall 的 Stage 1 将「什么命令能把环境跑起来」这个问题本身交给模型——因为这是一个推理任务，需要理解代码库的依赖结构，而这正是 LLM 的专长。

Cursor 的数据揭示了实际效果：

> "Through autoinstall, Composer aims to correctly set up an environment in as complete a manner as possible. To achieve that, it will mock missing files, create placeholder images, or even create fake database tables."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

模型不是按规则 mock 文件，而是**理解环境缺失了什么，然后主动创造缺失的组件**——这是一个「模型知道该做什么」的判断行为，而不是「规则规定遇到 X 情况时执行 Y」的触发行为。

### 自举飞轮

更值得关注的是 Autoinstall 创造了一个**自举飞轮**：

- Composer 2 使用 Composer 1.5 配置训练环境
- Composer 2 的性能改进后，下一版本将使用 Composer 2 配置 Composer 3 的训练环境

> "In future runs, previous Composer instances will play a large role in many other aspects of the training process, including run management, data preprocessing, and architecture tuning."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

这个飞轮意味着：**环境准备的质量会随模型能力提升而自动提升**，而不是依赖人类工程师维护配置脚本。

---

## 五、OpenAI Auto-review：审批分流从人工到模型

### Auto-review 的架构

OpenAI 的 Auto-review 是 Auto Mode 的企业版本对应物。在 Codex 的部署中，OpenAI 使用了一个 **Auto-review subagent** 来处理常规审批请求：

```
User Request → Codex 规划操作 → Auto-review subagent
    → 低风险操作？ → Auto-review 直接批准，Codex 继续
    → 高风险操作？ → 停止，等待人类审批
```

Auto-review 的决策基于：
- 操作类型（已知的 routine 操作 vs 高风险操作）
- 当前 session 的上下文（同一操作在不同上下文中风险不同）
- 企业配置的规则（自定义审批策略）

### 为什么不是大模型直接判断？

值得注意的是，OpenAI 的 Auto-review **不是让大模型直接判断「安不安全」**——那是 Auto Mode 的 transcript classifier 做的事。Auto-review 是一个 **确定性规则引擎 + 小型模型的组合**。

> "Auto-review mode, which is a feature that, when turned on, auto-approves certain kinds of requests to reduce how often users have to stop and approve Codex actions."
> — [OpenAI Engineering Blog: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)

这个设计选择背后的工程推理：**大模型直接判断存在不确定性和延迟**。对于已知的 routine 操作（如 `git status`、`ls`、`cat`），用确定性规则处理更快、更稳定——只有真正模糊的决策才需要模型推理。

> 笔者认为：Auto-review 代表了一种务实的混合策略——确定性规则处理已知模式（低延迟、可预测），模型处理未知场景（高泛化能力）。这是当前模型驱动 harness 工程的主流方向：**模型不是万能的，但模型擅长处理规则覆盖不到的边缘情况**。

---

## 六、统一分析：规则→模型迁移的四条路径

### 迁移矩阵

| Harness 维度 | 传统方法（规则/过程）| 模型驱动方法 | 代表案例 |
|-------------|-------------------|-------------|---------|
| 权限判断 | allowlist/rejectlist | 双阶段 classifier | Anthropic Auto Mode |
| 上下文管理 | compaction/reset | Session 外置 + 模型查询 | Anthropic Managed Agents |
| 环境准备 | 预配置脚本 | Goal-setting + achieving agent | Cursor Autoinstall |
| 审批分流 | 固定规则分流 | Auto-review subagent | OpenAI Auto-review |

### 共同的设计原则

四条路径共享两个相同的底层原则：

**1. 将「判断」从硬编码规则迁移给模型**
- 规则只能覆盖已知模式，无法泛化到未见过的场景
- 模型可以处理需要「理解意图」的判断（模糊请求 + 不可逆操作；credentials 不应外传）
- 规则失效的主要原因是模型能力提升后，原本安全的配置变成新的攻击面——模型比规则更快适应能力演进

**2. 混合架构：规则处理确定性场景，模型处理不确定性**
- Auto-review 的设计选择：routine 操作用规则，模糊场景用模型
- Auto Mode 的 Tier 架构：低风险操作用静态 allowlist，高风险操作才触发 classifier
- 这不是「规则 vs 模型」的二元对立，而是**分层决策**——各层用最适合的工具

### 这个范式转移的局限

模型驱动 harness 不是银弹。已知局限：

**1. 模型推理延迟**：transcript classifier 的双阶段推理增加了每个工具调用的延迟。Auto Mode 的 Tier 架构是对这个问题的工程缓解——大部分操作在 Tier 1/Tier 2 被放行，只有高风险操作才进入 Tier 3。

**2. 模型仍会被 prompt injection 影响**：即使有 prompt-injection probe，模型的判断仍然可能被精心构造的注入内容操纵。Auto Mode 的 design decision（如 reasoning-blind classifier）是缓解措施，但不是根本解决方案。

**3. Session 外置增加了系统复杂度**：Managed Agents 的架构需要可靠的 Session 持久化机制。如果 Session 存储失败，整个 Agent 的状态丢失。这个复杂度是 Brain/Hands 解耦的代价。

---

## 七、工程实践建议

### 何时应该将规则迁移给模型

| 判断维度 | 适合规则 | 适合模型 |
|---------|---------|---------|
| 决策类型 | 确定性（二元判断）| 条件性（需要理解上下文）|
| 错误成本 | 误报可接受 | 需要精确判断 |
| 覆盖范围 | 已知的固定模式 | 已知 + 未知的组合场景 |
| 延迟要求 | 低延迟必须 | 可接受一定延迟 |

**具体应用**：
- 「git pull」是安全操作 → 规则 allowlist
- 「将 credentials 上传到外部服务」是危险操作 → 模型判断（需要理解上下文：credentials 从哪来、操作的目的是什么）
- 「删除 3 天前的分支」→ 模型判断（需要理解：用户意图是清理本地还是远程、批量删除是否授权）

### 如何逐步迁移

1. **从边缘案例开始**：首先识别现有规则无法覆盖的边缘场景，这些是迁移给模型的第一候选
2. **构建 Tier 架构**：不是把所有规则都换成模型，而是分层——确定性规则在外层快速放行，模型只处理通过规则筛选后的场景
3. **测量并迭代**：Auto Mode 的 classifier 需要持续调优（few-shot examples 减少 score drift），模型驱动的 harness 不是一次设计、永久生效

---

## 引用来源

> "Over time that leads to approval fatigue, where people stop paying close attention to what they're approving." — [Anthropic Engineering: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)

> "We keep an internal incident log focused on agentic misbehaviors. Past examples include deleting remote git branches from a misinterpreted instruction, uploading an engineer's GitHub auth token to an internal compute cluster." — [Anthropic Engineering: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)

> "Context resets—clearing the context window entirely and starting a fresh agent, combined with a structured handoff that carries the previous agent's state and the next steps—addresses both these issues." — [Anthropic Engineering: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

> "Decoupling the brain from the hands means that containers are provisioned by the brain via a tool call only if they are needed." — [Anthropic Engineering: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

> "Through autoinstall, Composer aims to correctly set up an environment in as complete a manner as possible. To achieve that, it will mock missing files, create placeholder images, or even create fake database tables." — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

> "For routine approval requests, we are using Auto-review mode, which is a feature that, when turned on, auto-approves certain kinds of requests to reduce how often users have to stop and approve Codex actions." — [OpenAI Engineering Blog: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)
