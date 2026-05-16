# Anthropic Advanced Tool Use 三项工程突破：从 Schema 到真正的工具协同

> **核心论点**：Anthropic 在 2025 年 11 月发布的 Advanced Tool Use 特性，解决了大型工具库场景下三个根本矛盾——工具发现效率、API 调用成本、Schema 语义缺失。这不是功能迭代，而是工具使用范式的一次根本性转变。

---

## 背景：当工具库变成诅咒

业界普遍将"MCP 协议统一工具生态"视为银弹，但 Anthropic 的一线数据揭示了更严峻的现实：

> *"We've seen tool definitions consume 134K tokens before optimization."*
> — Anthropic Engineering Blog

一个五服务器的典型配置就能产生约 55K token 的工具定义开销，Jira 单个服务器就能消耗 ~17K token。当企业接入 Slack、GitHub、Google Drive、Jira 加上多个 MCP 服务器时，100K+ token 的工具定义开销已成常态——而且这是在模型还没开始处理用户请求之前。

传统方案是"全部加载"，但这在规模面前迅速失效。Claude 的工程数据显示，即使在简单场景下，错误工具选择和错误参数也是最常见的失败模式，尤其是当工具名称高度相似时（如 `notification-send-user` vs. `notification-send-channel`）。

Anthropic 认为这三个问题需要分别从三个不同的工程维度来解决，不是打补丁，而是一套完整的系统性方案。

---

## 突破一：Tool Search Tool——从全部加载到按需发现

### 问题本质

JSON Schema 解决的是结构有效性，不是语义相关性。50 个工具的 Schema 加起来可能语法正确，但模型无法从中判断"当用户要查 Q3 差旅报销时，应该选哪个 API"。

传统方案 A（全部加载）：token 开销巨大，但搜索能力完整。
传统方案 B（手动拆分）：token 节省了，但工具间协作逻辑被打散，跨工具工作流断裂。

### Anthropic 的解法

Anthropic 引入了一个专门的"工具搜索工具"（Tool Search Tool）作为模型的可调用工具之一。工作时序如下：

1. 模型接收用户请求
2. 若需要工具，模型先调用 Tool Search Tool，传入语义搜索词
3. Tool Search Tool 返回匹配的工具引用（而非完整定义）
4. 模型根据引用加载对应工具定义到 context
5. 继续正常调用流程

关键设计：`defer_loading: true` 标记的工具有两种状态——不被搜索时完全不出现在 context 中，被搜索到时才扩展加载。这使得 prompt caching 不受影响，因为 deferred tools 本就不在初始 prompt 中。

### 效果数据

> *"Opus 4 improved from 49% to 74%, and Opus 4.5 improved from 79.5% to 88.1% with Tool Search Tool enabled."*
> — Anthropic Engineering Blog

这是 85% 的 token 降低同时带来的准确率跃升，不是 tradeoff，是架构优化的双重收益。

---

## 突破二：Programmatic Tool Calling——从逐次调用到代码编排

### 问题本质

自然语言工具调用在复杂工作流中有根本性的效率问题：

- 每个工具调用的结果都要经过一次完整的 inference pass 返回给模型 context
- 中间结果堆积在 context 中，无论有用与否
- 循环、条件分支、数据转换这些基本编排逻辑，被隐式地塞进模型的"推理"中，模型需要额外推理来维持对状态的追踪

当工作流涉及 2000+ 行项处理时（比如"谁超出了 Q3 差旅预算"），逐次调用的 context 成本不可接受。

### Anthropic 的解法

Programmatic Tool Calling 让 Claude 将工具调用表达为 Python 代码，由 Code Execution 工具在沙箱环境中执行：

```python
team = await get_team_members("engineering")

# Fetch budgets for each unique level
levels = list(set(m["level"] for m in team))
budget_results = await asyncio.gather(*[
    get_budget_by_level(level) for level in levels
])

budgets = {level: budget for level, budget in zip(levels, budget_results)}

# Fetch all expenses in parallel
expenses = await asyncio.gather(*[
    get_expenses(user_id=m["id"], quarter="Q3") for m in team
])

# 核心逻辑在 code execution 环境中处理
# Claude 只看到最终结果，不看到 2000+ 条 expense 记录
```

工具执行结果通过 `caller` 字段标识来源（`code_execution`），返回给 Code Execution 环境而非模型 context。模型最终只看到代码执行的标准输出。

### 核心价值

笔者认为，Programmatic Tool Calling 的真正价值不在于省 token，而在于**职责分离**：模型负责决策和编排，代码负责执行和数据处理。这是两种不同性质的工作，放在同一个 context 中互相干扰是传统架构的根本缺陷。

---

## 突破三：Tool Use Examples——从 Schema 到使用模式

### 问题本质

JSON Schema 定义了什么是结构上有效的输入，但无法表达：
- 哪些可选参数在这个场景下应该包含
- 参数之间的语义依赖关系
- 业务约定的命名或格式规范

> *"JSON Schema excels at defining structure–types, required fields, allowed enums–but it can't express usage patterns."*
> — Anthropic Engineering Blog

一个 `create_ticket` 工具，Schema 可以说 `labels` 是 string array，但无法告诉模型"创建生产环境 bug 时通常需要加哪些 label"。

### Anthropic 的解法

在工具定义中加入 `input_examples` 字段，直接展示具体的使用样本：

```json
{
  "name": "create_ticket",
  "input_schema": { /* ... */ },
  "input_examples": [
    {
      "title": "Login page returns 500 error",
      "priority": "critical",
      "labels": ["bug", "authentication", "production"],
      "reporter": {"id": "USR-12345", "name": "Jane Smith"}
    }
  ]
}
```

效果数据：

> *"In our own internal testing, tool use examples improved accuracy from 72% to 90% on complex parameter handling."*
> — Anthropic Engineering Blog

18 个百分点的提升，直接来自"告诉模型怎么用"而非"告诉模型可以怎么用"。

---

## 三项特性的协同逻辑

Anthropic 的设计不是三选一，而是分层组合：

| 瓶颈 | 解决方案 | 核心价值 |
|------|---------|---------|
| 工具太多找不到对的 | Tool Search Tool | 动态发现，按需加载 |
| 调用次数多、context 堆积 | Programmatic Tool Calling | 代码编排，结果过滤 |
| Schema 无法表达使用规范 | Tool Use Examples | 示例驱动，语义对齐 |

> *"Tool search matches against names and descriptions, so clear, descriptive definitions improve discovery accuracy."*
> — Anthropic Engineering Blog

Anthropic 给出的实际建议是：**保持 3-5 个最高频工具始终加载，其余全部 deferred**。这平衡了即时可用性和按需扩展。

---

## 工程落地的关键约束

三项特性虽然强大，但 Anthropic 明确指出了各自的适用边界：

**Tool Search Tool** 的 ROI 取决于工具库规模。如果你只有 10 个工具，全部加载的 token 开销可能低于搜索本身的延迟成本。但当你有 50+ 工具时，动态发现的价值迅速超过其成本。

**Programmatic Tool Calling** 需要工具明确声明 `allowed_callers`。这是一个安全设计——不是所有工具都应该被代码执行环境调用，必须由 harness 设计者显式 opt-in。

**Tool Use Examples** 会增加 token 开销，因为每个带示例的工具定义都更大。只有在复杂参数处理场景下（如多字段联动、格式约定），才值得用额外的 token 换取准确率提升。

---

## 笔者的判断

Anthropic 这篇文章最值得关注的不是三项特性本身，而是它们共同揭示的趋势：**工具使用正在从"函数调用"向"工具编排"演进**。

传统函数调用范式假设工具是独立的、调用是原子的、结果是无状态的。但真实的 agent 工作流涉及循环、并发、状态维护和数据变换——这些是代码的工作，不是 prompt 的工作。

Programmatic Tool Calling 代表着一种认识转变：模型擅长决策，代码擅长执行，让各自做擅长的事。这比强迫模型在每次 tool call 结果中"保持状态意识"要工程化得多。

笔者的一个保留意见是：当前 beta header `advanced-tool-use-2025-11-20` 意味着这还不是 stable API。生产环境使用需要承担接口变更风险，建议在非关键的 internal tooling 上先验证。