# Harness Engineering: Martin Fowler 的深度解读

> 来源：Martin Fowler（Thoughtworks）
> 评分：4.5/5（实践 4 / 独特 5 / 质量 5）
> 关联 FSIO 文章： Harness Engineering：构建让 AI Agent 可靠工作的系统工程

## 核心观点

### OpenAI 的 Harness 三组件

OpenAI 团队用"no manually typed code at all"作为驱动力，构建了维护大型应用的 harness，包含三个核心组件：

1. **Context Engineering**
   - 持续增强的知识库
   - 动态上下文访问（可观测性数据、浏览器导航）

2. **Architectural Constraints**
   - LLM Agent + 确定性 linter + 结构化测试双重监控
   - 不是单纯依赖 Agent，而是有规则约束

3. **Garbage Collection**
   - 定期运行的 Agent，清理文档不一致性和架构约束违规
   - 对抗熵增和衰退

### 关键洞察：迭代式改进

> "When the agent struggles, we treat it as a signal: identify what is missing — tools, guardrails, documentation — and feed it back into the repository, always by having Codex itself write the fix."

### Martin Fowler 的三个反思

1. **Harnesses 会成为新的 Service Templates？**
   - 企业通常只有 2-3 个主要技术栈
   - 未来团队可能从预设的 harnesses 中选择，像现在的 service templates 一样
   - 但也面临同样的 fork 和同步挑战

2. **运行时必须被约束才能获得更多 AI 自主性？**
   - 早期 AI 编程假设 LLM 给我们无限的灵活性
   - 但要获得可维护的、AI 生成的代码，必须约束解决方案空间
   - 特定的架构模式、强制边界、标准化结构

3. **两种未来：Pre-AI vs Post-AI 应用维护？**
   - 老代码库 retrofit harness 是否值得？
   - 很多非标准化、充满熵的应用可能不值得

## 一句话总结

> Martin Fowler 评注 OpenAI Harness Engineering：工具+规则+定期清理的三层约束是 AI 长期可维护性的关键，而不是单纯依赖 Agent 本身。

## 原文

https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html

## 标签

#community #HarnessEngineering #MartinFowler #OpenAI #system-design
