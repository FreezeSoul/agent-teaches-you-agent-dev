# Claude Opus 4.7 行为解析：自验证机制与控制架构的工程含义

> **本文解决的问题**：Opus 4.7 的核心变化不在 benchmark 数字——而在模型行为模式的结构性转变。自验证机制的引入、"literal" 指令遵循、以及 control architecture 设计原理，共同构成了一套需要重新设计 Agent 接口的工程现实。本文解析这些变化对 Agent 工程实践的具体影响。

---

## 自验证机制：模型在报告结果之前做什么

Anthropic 对 Opus 4.7 的核心定位是："hand off your hardest coding work"——把任务委托出去，不需要逐行监督。这个定位的背后是 Opus 4.7 引入了一套自验证机制：**在报告结果之前，模型会主动验证自己的输出**。

这不是一个 prompt 技巧，而是模型内生的行为模式。在复杂多步骤工作流中，这意味着：

### 实际执行顺序的改变

传统 Agent 循环的执行路径是：推理 → 工具调用 → 输出 → 终止（或者进入下一轮）。Opus 4.7 的执行路径变成了：推理 → 工具调用 → **自我验证** → 输出 → 终止。

Anthropic 在发布博客中明确指出了这一点：

> "Opus 4.7 handles complex, long-running tasks with rigor and consistency, pays precise attention to instructions, and **devises ways to verify its own outputs before reporting back**."

这里的 "devises ways" 暗示验证方式不是固定的——模型会根据任务性质选择合适的验证策略。这对于 Agent 工程师意味着：不能假设模型的验证行为是可预测或可配置的；它是任务自适应的。

### Hex 的实测数据印证

Hex 在 93-task 编码 benchmark 上的测试结果显示，Opus 4.7 的 tool error 率显著低于 4.6。这个差异的来源之一正是自验证机制在 tool call 层面的作用：模型在提交一个 tool call 结果之前，会检查参数的合理性、上下文的兼容性、以及执行结果的预期一致性。

这解释了为什么 4.7 在 "implicit-need 测试"（隐式需求推断）中首次通过：模型不只在执行后验证，它在规划阶段就做了预验证——推断出需要哪些工具，然后验证这些推断是否合理，再执行。

### 工程实践中的注意事项

自验证机制在以下场景中有明显正面效果：
- 长时间运行的多步骤编码任务（数小时级）
- 需要跨文件一致性检查的重构工作
- 工具调用链中的参数合理性验证

但也存在需要注意的反面：
- 验证本身消耗 token。在简单任务上，自验证可能带来不必要的开销。
- 验证行为不可干预——无法强制模型跳过验证步骤，也无法扩展验证范围。
- 当验证失败时，模型的行为可能与预期不符（因为验证策略是任务自适应的）。

---

## Literal 指令遵循：行为变化而非功能增加

Opus 4.7 相比 4.6 在指令遵循上有结构性变化：**4.7 更 literal，4.6 更 loose**。

这是什么意思？dsebastien 的分析中引用了一个关键案例：

> "4.6 would flag adjacent issues you didn't ask about... 4.7, on the same input, returned a clean summary and missed it."

Brandon Gell 的具体例子：4.6 在处理 P&L 数据时自动捕获了一个产品被错误分类为严重亏损的问题；4.7 在相同输入下返回了"干净的摘要"——它精确执行了被要求做的事，但没有超额执行。

这意味着 **4.6 的 prompt engineering 隐含地利用了模型的"过度执行"倾向**。当团队升级到 4.7 后，同样的 prompt 会得到更精确但更少超额执行的输出——这不是回归，而是行为变化。

### Literal 遵循的实际影响

| 场景 | 4.6 行为 | 4.7 行为 |
|------|---------|---------|
| 收到"检查这个 bug"的请求 | 检查 bug + 连带检查相关潜在问题 | 仅检查被指定的 bug |
| 收到"生成一个函数"的请求 | 生成函数 + 检查边界情况 + 提出改进建议 | 仅生成被要求的函数 |
| 收到"分析这个数据"的请求 | 分析数据 + 标注异常值 + 发现模式 | 仅执行被要求的数据分析 |

这个变化对 Agent 工程师的直接影响是：**你需要更明确地声明你想要的范围**。在 4.6 时代，"做 X" 通常隐含着"也检查相关的 Y"；在 4.7 时代，"做 X" 就是字面意思。

这解释了为什么 Anthropic 在发布说明中特别指出：

> "Users should re-tune their prompts and harnesses accordingly."

### Prompt 迁移的 practical guide

基于社区反馈，以下是有效的迁移策略：

1. **显式声明边界**：不要说"检查这个函数"，说"检查这个函数的边界条件和可能的整数溢出，同时报告任何明显的性能问题"
2. **显式要求超额执行**：如果你希望模型主动发现额外问题，直接说"除了被要求的内容，请主动检查以下方面：[...]"
3. **重新评估"习惯性前缀"**：4.6 时代很多 Agent 会在 prompt 前加"检查 git log"类的习惯性提示；在 4.7 中，这些提示可能不再必要（因为模型会自己推断），但也可能改变行为——需要实际测试后再决定删留。

---

## Control Architecture：来自泄露 System Prompt 的设计原理

Carlos E. Perez 对 Opus 4.7 system prompt 的分析揭示了一个重要结论：**这份 prompt 读起来不像 safety policy，更像一套可复用的 control architecture**。

这是 Agent 设计领域值得关注的方向。以下是 Perez 识别的两个核心原语：

### 1. Search-First Epistemic Gating（搜索优先的认识门控）

对于当下事实（present-day facts），模型被要求在做答之前通过 web search 验证，而非依赖自身知识。这将 search 从可选工具变成了默认姿势。

这个设计的影响：
- 模型在不确定时倾向于探索而非直接回答
- 减少了"知识截止日期"导致的幻觉问题
- 对需要最新信息的任务，行为更可靠

对于 Agent 工程师：这意味着如果你在构建需要事实准确性的 Agent，应该假设 4.7 会自动 search，而不是在你的 tool list 里把它放在高优先级。

### 2. Latent Capability Discovery（潜在能力发现）

System prompt 明确教导模型：**可见的工具列表不是完整的工具列表**。模型被训练为在宣布某能力不可用之前，先寻找延迟加载的（deferred）能力。

具体机制：
- `tool_search` 工具（regex 和 BM25 两个变体）
- 工具定义中的 `defer_loading: true` 标记
- 延迟工具不会被注入到 system prompt 的前缀中

这个设计解决的问题是：传统 Agent 的工具列表是静态闭包——模型只能使用设计者预先注入的工具。Latent capability discovery 引入了一个开放的能力边界：模型可以在运行时探索未知工具。

对于 Agent 架构设计：这是一个重新思考工具系统设计的信号。如果模型可以在运行时发现隐式工具，那么静态的工具列表定义可能不是最终形态。

---

## Tokenizer 变化对 Agent 成本模型的实质性影响

Opus 4.7 引入了新 tokenizer，Anthropic 官方文档记录了 1.0–1.35× 的 token 膨胀率。但实测数据更悲观：

| 内容类型 | Tokenizer 膨胀率 |
|---------|----------------|
| CJK 文本 + emoji | ~1.01×（几乎无影响）|
| CSV | ~1.07× |
| JSON Schema tool definitions | ~1.12× |
| 英文 prose | ~1.20× |
| 代码（TypeScript/JavaScript）| 1.36–1.39× |
| Shell 脚本 | ~1.39× |
| 技术文档（CLAUDE.md 等）| 最高 1.47× |
| 密集 JSON | ~1.13× |

关键发现：**Claude Code 内容（代码、CLAUDE.md）落在了膨胀率分布的高位**。dsebastien 的实测加权均值是 1.325×，但 Claude Code 工作负载的实际值接近上限。

这带来了具体的成本影响：
- 一个 80-turn 的典型 Claude Code 会话：从 ~$6.65 上升到 ~$7.86–$8.76（约 20–30% 增加）
- Prompt cache 的 partition per model 特性意味着：切换 4.6 → 4.7 会 invalidate 所有已缓存的 prefix，cold start 成本更高
- Cache-bust 事件（CLAUDE.md 编辑、tool list 变更、compaction）在 4.7 上需要支付完整的膨胀率（1.3–1.45×）来重写

对于 Agent 工程团队：升级到 4.7 不只是改 model ID，需要同步更新成本模型、预算设置、和 cache 策略。

---

## Opus 4.7 vs Mythos Preview：能力边界的精确理解

Anthropic 明确表示 Opus 4.7 不如 Mythos Preview："less broadly capable than our most powerful model"。

发布说明中的关键细节：

> "Opus 4.7 is the first such model: its cyber capabilities are not as advanced as those of Mythos Preview (indeed, during its training we experimented with efforts to differentially reduce these capabilities)."

这是第一次有一个模型被明确标注为"有限制地释放"能力——与 Mythos Preview 的对比实际上是一个能力上限的声明。

对于 Agent 工程师，这意味着：
- 如果你在做网络安全相关（渗透测试、红队）方向的 Agent，Opus 4.7 不适合你——Mythos Preview 才适合，但后者尚未 GA
- 对于一般企业级 Agent 场景，Opus 4.7 是当前能获得的最佳能力（GA 模型中）

---

## 各场景的升级判断

| 场景 | 建议 | 原因 |
|------|------|------|
| 长时间运行的自主编码 Agent（Devin 类）| ✅ 升级 | 3x Rakuten-SWE-Bench 提升，自验证机制减少 tool error |
| 快速交互式单步任务 | ⚠️ 谨慎 | tokenizer 增加成本，literal 遵循可能改变行为 |
| 多 Agent 并行审查（/ultrareview 场景）| ✅ 升级 | xhigh effort + 更强的 instruction adherence |
| 需要主动发现问题的辅助任务 | ❌ 保持 4.6 或重新调 prompt | 4.6 的超额执行倾向在某些场景有价值 |
| 需要最新事实的搜索增强任务 | ✅ 升级 | search-first epistemic gating |
| 企业文档分析（OfficeQA Pro 类）| ✅ 升级 | 21% fewer errors，state-of-the-art on Finance Agent |

---

## 总结：工程决策框架

Opus 4.7 不是一次常规的模型升级，它是 Agent 工程行为模式的一次结构性调整：

1. **自验证是内生的、任务自适应的**——无法干预，但可以设计利用它的接口
2. **Literal 遵循要求更明确的 prompt**——4.6 时代的"隐含期望"在 4.7 中需要显式声明
3. **Control architecture 设计原理值得参考**——特别是 search-first epistemic gating 和 latent capability discovery
4. **Tokenizer 成本增加是真实且不均匀的**——代码和 CLAUDE.md 受影响最大
5. **升级需要成本模型和 prompt 的共同调整**——单独改 model ID 不够

> 如果你的 Agent 系统依赖了 4.6 的超额执行行为（隐式连带检查、主动问题发现），升级到 4.7 后需要显式地将这些行为写入 prompt，否则会得到更"干净"但更少惊喜的输出。

---

## 来源

- [Introducing Claude Opus 4.7 (Anthropic)](https://www.anthropic.com/news/claude-opus-4-7)
- [Claude Opus 4.7 (dsebastien.net)](https://www.dsebastien.net/claude-opus-4-7/)
- [Opus 4.7 Review: What Actually Changed and What Got Worse (MindStudio)](https://www.mindstudio.ai/blog/claude-opus-4-7-review/)
- [Claude Opus 4.7 GA: What Changed, What Regressed, and How to Use It (TicNote)](https://ticnote.com/en/blog/claude-opus-4-7-changes)
- [Control Architecture Analysis (Carlos E. Perez)](https://note.youdao.com/s/V2CRM)