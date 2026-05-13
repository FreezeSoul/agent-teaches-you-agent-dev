# Cursor Bugbot 决策质量经济学：用量计费如何重构代码审查的价值度量

> **核心论点**：Cursor Bugbot 从固定座位收费转向用量计费，不只是定价模式的转变，而是将代码审查的核心价值——"发现多少比例的 bug"——从黑箱承诺变为可量化的质量-成本权衡。默认 effort 保持 80% 解决率，high effort 提升 35% bug 发现量但成本相同，这个数字揭示了 Agent 代码审查产品的关键工程选择。

> **读完能得到什么**：理解 Effort Level 作为质量-成本杠杆的设计原理，以及这对 AI Coding 产品工程实践的启示。

---

## 一、产品背景：为什么定价模式本身就是工程决策

Bugbot 是 Cursor 的 AI 代码审查产品，过去采用 `$40/席位/月` 的固定收费模式。这种模式对供应商的好处是收入可预测，但对用户而言存在一个根本问题：**质量是不可见的**。用户付了月费，得到的是一个黑箱承诺——"我们会在 merge 前发现 bug"——但发现率是多少、是否值得这个价格，用户无从评估。

> "For existing customers, this change will start at your next billing renewal after June 8th, 2026."
> — [Cursor Blog: Updates to Bugbot for Teams and Individuals](https://cursor.com/blog/may-2026-bugbot-changes)

用量计费（usage-based billing）的转变让价格变得透明：`$1.00-$1.50/PR`，取决于 PR 大小和复杂度。但这只是表面。更深的变化是**Effort Level 的引入**——让用户可以主动控制每次审查的质量-成本比率。

---

## 二、Effort Level 设计：质量-成本权衡的具体化

### 2.1 默认 Effort：保持 80% 解决率

Cursor 的内部运行数据显示，默认 effort 下 Bugbot 在 merge 前解决的 bug 比例为 **80%**。这意味着：

- 每发现 5 个 bug，有 1 个会流入生产（平均）
- 这个数字是"默认"水平，用户不需要任何配置

> "Default effort preserves how Bugbot works today: 80% of bugs identified are resolved by merge time."
> — [Cursor Blog: Updates to Bugbot for Teams and Individuals](https://cursor.com/blog/may-2026-bugbot-changes)

**笔者认为**：80% 这个数字的选择值得玩味。不是一个漂亮的整数（如 90%），说明它是实际测量结果而非目标值。这暗示 Cursor 在上线这个功能前，已经有了足够多的内部数据来定义"默认"是什么。

### 2.2 High Effort：35% 更多发现，同等解决率

关键数据在 high effort 模式下：

> "From our internal runs, Bugbot with high effort finds 35% more bugs while resolution rate stays constant at 80%."
> — [Cursor Blog: Updates to Bugbot for Teams and Individuals](https://cursor.com/blog/may-2026-bugbot-changes)

这意味着：
- High effort 发现了更多 bug（+35%）
- 但解决率保持 80% 不变——**发现更多不等于解决更多**

这个区别非常重要。35% 的"发现增量"没有转化为同比例的"修复增量"，说明**发现和修复是两个独立的环节**。可能是：
- 开发者忽略了部分 AI 发现的问题（认为不重要）
- 部分 bug 的修复涉及其他团队/系统，改动成本过高
- High effort 发现的是更深层的 bug，修复路径更长

**这对 Agent 工程意味着什么**：如果你的评测只度量"发现了多少问题"而不度量"解决了多少问题"，你可能会高估系统的实际价值。

### 2.3 动态 Effort：自定义逻辑的可能性

产品设计中还有一个值得注意的细节：

> "Users can configure Bugbot to think for longer and run deeper reviews, or set up custom logic that Cursor uses to dynamically determine review effort."
> — [Cursor Blog: Updates to Bugbot for Teams and Individuals](https://cursor.com/blog/may-2026-bugbot-changes)

"设置自定义逻辑来动态决定 effort"这个能力，暗示 Bugbot 的审查流程本身是 **可编程的**——用户可以根据 PR 类型、代码路径、团队历史等条件，自适应调整审查深度。这是一个比简单的高低两档更灵活的架构。

---

## 三、与 Claude Code Auto Mode 的架构类比

这个 Effort Level 设计与 Anthropic 在 Claude Code Auto Mode 中的分类器设计有异曲同工之处。Auto Mode 使用双层防御：

- **Input Layer**：prompt-injection probe，过滤恶意输入
- **Output Layer**：transcript classifier，决策是否执行工具调用

两者的共同点是**将决策分为"放行"和"阻断"两类**，但粒度和触发条件不同：

| 维度 | Claude Code Auto Mode | Bugbot Effort |
|------|---------------------|---------------|
| 决策对象 | 工具调用（write/delete/execute） | 审查深度（effort level） |
| 决策类型 | 二元阻断（block/allow） | 连续调整（default → high） |
| 驱动方式 | 分类器自动决策 | 用户手动或自定义逻辑 |
| 安全保障 | 防止 agent 越界行动 | 防止 bug 流入生产 |

**笔者认为**：两者都反映了一个趋势——Agent 系统的安全保障正在从"全有或全无"向"可调节的梯度控制"演进。Claude Code Auto Mode 是操作层的安全梯度，Bugbot Effort Level 是审查层的质量梯度。

---

## 四、工程实践启示：Agent 产品的质量度量框架

### 4.1 从黑箱承诺到透明指标

Bugbot 案例给 Agent 产品工程的一个核心启示是：**不要只承诺"发现问题"，要承诺"发现并解决问题的比例"**。两者之间的差距（35% 的发现增量没有转化为同比例的修复增量）恰好是产品持续改进的关键信号。

**实际工程建议**：
- 建立"发现率"和"解决率"的双重度量
- 定期分析 gap 的来源：是 AI 发现不被信任，还是修复成本过高？
- 用这个 gap 来驱动下一代模型的改进方向

### 4.2 Effort Level 作为产品架构原语

Effort Level 的设计暗示了一种可复用的产品架构模式：

```
用户配置 → Effort 参数 → Agent 行为参数（时间/深度/范围）→ 输出质量
```

这个模式可以泛化到任何 Agent 产品：
- **AI Coding**：低 effort = 快速补全，高 effort = 深度重构
- **Deep Research**：低 effort = 快速摘要，高 effort = 多源交叉验证
- **Test Generation**：低 effort = 基础单元测试，高 effort = 属性测试 + 边界条件

**关键设计原则**：Effort 之间的差异应该是**可量化且用户可感知的**，而不是内部的隐藏参数。

### 4.3 用量计费对 Agent 工程的影响

用量计费模式不只是商业模型，它对工程实现有直接影响：

- **每次调用的成本是显式的**：促使 Agent 框架优化 token 消耗
- **审查深度是可配置的**：避免了为简单任务支付高端模型成本的浪费
- **用户获得了控制权**：不再被动接受"供应商认为合适的质量水平"

> 笔者认为：未来的 Agent 产品会普遍采用类似的双重度量 + 用量计费模式。供应商提供基准质量保证（如 80% 默认解决率），用户通过 Effort 参数在基准之上进行精细控制。

---

## 五、结论与启示

Cursor Bugbot 的用量计费转型，本质上是在代码审查这个场景中，首次将 **Agent 审查质量** 从黑箱承诺变成了透明可量化的指标。80% 解决率作为基准，35% high effort 提升作为上限，用户可以在这个范围内动态配置。

这个设计对 Agent 产品工程的启示是：

1. **度量驱动产品演进**：没有 80% 这个基准数字，就不会有 35% 提升的可测量性
2. **发现率和解决率要分开度量**：两者之间的 gap 是改进的关键信号
3. **Effort Level 是一种可泛化的架构模式**：从代码审查到任意 Agent 任务，都可以通过 effort 参数实现质量-成本权衡

> "The average Bugbot run costs $1.00-$1.50, depending on PR size and complexity."
> — [Cursor Blog: Updates to Bugbot for Teams and Individuals](https://cursor.com/blog/may-2026-bugbot-changes)

当平均单次运行成本透明可见时，"AI 代码审查值不值"这个问题就变得可回答了。