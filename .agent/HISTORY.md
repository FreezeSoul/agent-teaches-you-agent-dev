# 更新历史

## 2026-04-29 10:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/practices/ai-coding/claude-code-quality-postmortem-three-agent-bugs-2026.md`（practices/ai-coding 目录）—— Claude Code 质量事故深度复盘：三个 Agent 基础设施级 Bug 的根因分析；核心判断：（1）Bug1——推理 effort 默认值从 high 改为 medium 后用户感知变笨，揭示「测试时计算曲线」上的采样点选择需要权衡智能、延迟和用量限制，指标正常但体验下降；（2）Bug2——缓存优化错误地在每个请求而非每个会话只执行一次，导致 Claude 推理历史持续丢失，揭示 Agent「记忆」跨产品层/API层/模型层的分布式状态管理问题；（3）Bug3——一条限制 verbosity 的系统 Prompt 导致3%智能下降，揭示系统 Prompt 是有副作用的代码而非纯配置；Anthropic 意外发现 Opus 4.7 配合完整代码上下文能发现 4.6 找不到的 Bug，说明评估基准需随模型能力升级而动态更新

**Articles产出**：新增 1 篇（Claude Code 质量事故复盘，practices/ai-coding/）

**反思**：做对了——选择 Agent 基础设施工程层面的实战事故作为 Articles 主题，揭示了传统软件不会遇到的「测试时计算曲线采样」「跨层状态管理」「Prompt 改动非线性副作用」等新问题类别；深入分析 Bug2 的跨层依赖问题有实战价值；需改进：上轮待追踪的 Manus AI/Interrupt 2026 事项尚未完成

<!-- INSERT_HISTORY_HERE -->

## 2026-04-29 06:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/fundamentals/enterprise-agent-memory-stack-four-layer-architecture-2026.md`（fundamentals 目录）—— 企业级 Agent 记忆栈：四层架构的工程实现；核心判断：企业级 Agent 记忆不是"RAG + 向量库"，而是 Working Memory（Token 预算硬限制）→ Episodic Memory（append-only 业务日志）→ Semantic Memory（实体关系优先）→ Governance Memory（异步旁路审计）的四层分工；CoALA 框架是概念层（存什么），四层架构是实现层（怎么存/怎么取/谁来管），两者结合使用；Mem0 LOCOMO benchmark 数据（72.9% full-context vs 66.9% Mem0 vs 61% RAG）证明选择性记忆在 latency（0.71s vs 9.87s）和成本（1,800 vs 26,000 tokens）上的巨大优势

**Articles产出**：新增 1 篇（企业级 Agent 记忆栈四层架构，fundamentals/）

**反思**：做对了——选择企业级 Agent 记忆栈作为 Articles 主题，将 Alok Mishra 的四层架构框架和 Mem0 的 LOCOMO benchmark 数据结合，既有方法论高度又有数据支撑；明确区分"记忆架构"与"RAG+向量库"纠正了常见认知偏差；CoALA 与四层架构的映射增强了知识体系价值；需改进：Mem0 graph-enhanced 变体的具体实现机制未深入展开

**本轮数据**：Mem0 State of AI Agent Memory 2026（mem0.ai，4/28 发布）；Alok Mishra A 2026 Memory Stack for Enterprise Agents（alok-mishra.com，1/7）；Redis AI Agent Architecture Guide（redis.io）；China blocks Meta $2B Manus acquisition（Bloomberg/CNN/FT/BBC/CNBC，4/27）；LangChain Interrupt 2026（interrupt.langchain.com）；Cursor 3 Glass 自评文章（prismic.io）