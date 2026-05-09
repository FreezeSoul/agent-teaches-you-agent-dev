# kangarooking/system-prompt-skills：15 个可执行的系统提示词设计模式

> **T - Target**：想让 AI 产品从 Chat 升级为 Agent 的开发者，或需要设计稳定 system prompt 的 AI 产品团队，或希望理解 OpenAI/Anthropic/Google 等厂商提示词工程共性模式的工程师。
> 
> **R - Result**：用 15 个原子化 skill 替代 165 份散乱的系统提示词，将"如何设计身份/工具/安全/记忆"等工程决策从经验变成可组合的方法论。
> 
> **I - Insight**：不是泄露 prompt 模板，而是从真实产品提示词中蒸馏设计模式——把"答案"变成"可迁移的方法论"。
> 
> **P - Proof**：2026-05-04 创建，5 天 64 Stars，17 Forks，MIT 协议，asgeirtj/system_prompts_leaks 165 个产品语料。

---

## P - Positioning（定位破题）

**一句话定义**：从 165 个顶级 AI 产品系统提示词中蒸馏出的 15 个可执行 Agent skill 工具包。

**场景锚定**：当你需要回答"一个稳定的 Agent system prompt 应该包含哪些部分"、"工具权限该如何定义"、"怎么防御 prompt injection"这些问题时，这套 skills 提供了经过验证的设计模式，而非需要自己从头摸索的经验。

**差异化标签**：方法论 > 模板，组合 > 堆砌。

---

## S - Sensation（体验式介绍）

打开 `INDEX.md`，你会看到一张 15 个 skill 的全景图，按"核心架构层 / 交互控制层 / 工程支撑层 / 场景适配层"四层组织。

每个 skill 目录下有一个 `SKILL.md`，包含触发条件、执行步骤和边界条件。比如 `injection-defense` 目录下的 SKILL.md，会告诉你：

- 什么情况下触发防御（用户输入包含可疑模式）
- 如何分级处理（完全拒绝 / 脱敏后放行 / 警告后放行）
- 边界在哪里（防御过度导致正常功能失效怎么办）

这套方法论来自对 165 个真实 AI 产品的系统提示词分析——不是凭空设计，而是从真实产品中归纳。覆盖厂商包括 Anthropic、Google、OpenAI、xAI、Perplexity、Meta、Mistral、Notion、Warp、Brave 等。

---

## E - Evidence（拆解验证）

### 技术深度

15 个 skills 按四层组织，层层递进：

**核心架构层**：persona-design / personality-system / tool-specification / safety-guardrails / memory-system — 这是任何 AI 产品 system prompt 的地基。

**交互控制层**：output-formatting / conversation-flow / search-integration / citation-system — 控制 Agent 如何与用户交互、如何处理外部知识。

**工程支撑层**：context-management / agent-delegation / injection-defense — 解决 Token 预算、子代理分工、安全防御等工程问题。

**场景适配层**：voice-optimization / mobile-adaptation / code-engineering — 针对语音端、移动端、代码代理的专门设计模式。

### 生成方法论

> "cangjie-skill 基于 RIA-TV++ 方法论，将原始材料中的方法论、框架、原则提取为原子化 skill，可被 AI agent 在真实场景中直接调用。"

这不是简单的 prompt 收集，而是经过方法论抽象的过程——从具体产品的提示词文本中提取"为什么这样设计"，而非只保留"这样设计的文本"。

### 与 OpenAI Agents SDK 的关联

在[上篇文章](openai-agents-sdk-next-evolution-model-native-harness-2026.md)中，我们分析了 OpenAI 将 Skills 视为 frontier agent primitives 的标准化集成：

> "These primitives include tool use via MCP, progressive disclosure via skills, custom instructions via AGENTS.md..."

Skills 被明确定义为 Agent 系统的标准组件。而 `system-prompt-skills` 提供了具体的设计模式实现——如果你在设计一个 Agent 系统，可以从这 15 个 skills 中选择适合你的组合。

### 与 Anthropic Agent Skills 的互补

Anthropic 的 Agent Skills（如 [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)）强调的是**渐进式披露**（metadata → SKILL.md → 附加文件）让 Agent 按需加载知识。

`system-prompt-skills` 的价值在于，它提供了"在设计 SKILL.md 时应该包含哪些内容"的参考模式——相当于告诉你"一份好的 SKILL.md 长什么样"。

---

## T - Threshold（行动引导）

### 快速上手

1. 浏览 [INDEX.md](https://github.com/kangarooking/system-prompt-skills/blob/main/INDEX.md) 了解 15 个 skill 的全景图
2. 根据你的产品形态选择组合路径：
   - 从零设计 AI 产品 → 从 `persona-design`、`safety-guardrails`、`output-formatting` 开始
   - 构建 Agent → 组合 `tool-specification`、`conversation-flow`、`agent-delegation`、`injection-defense`
3. 将相关 SKILL.md 的触发条件、执行步骤和边界条件接入你的 agent 框架

### 贡献入口

如果你有其他高价值文本想要蒸馏成可执行的 Agent skills，可以使用 [cangjie-skill](https://github.com/kangarooking/cangjie-skill) 工具链自己生成。

---

## 关联主题

**本篇关联**：OpenAI Agents SDK 新增 Skills 作为标准原语，与 Anthropic Agent Skills 方案收敛。`system-prompt-skills` 提供了具体的设计模式实现——当你需要构建 Skills 系统时，这 15 个模式是可直接参考的工程样本。

**主题关联图**：
```
Anthropic Agent Skills（渐进式披露架构）
        ↕ 技术路径不同但目标相同
OpenAI Agents SDK（Skills 作为 primitives）
        ↓
Skills 已成为 frontier agent 的标准组件
        ↓
system-prompt-skills 提供 15 个设计模式参考实现
```

---

## 链接

- GitHub: [kangarooking/system-prompt-skills](https://github.com/kangarooking/system-prompt-skills)
- 生成工具: [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill)
- 语料来源: [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks)

---

*本推荐属于"AI Coding 工具链"系列。主题关联：OpenAI Agents SDK 进化 → Skills 作为标准原语 → system-prompt-skills 提供 15 个设计模式参考。*