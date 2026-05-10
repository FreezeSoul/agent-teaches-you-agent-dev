## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-11 05:57 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-11 05:57 | 每次必执行 |

## ⏳ 待处理任务
<!-- 状态：⏳待处理 🔴执行中 ✅完成 ⏸️等待窗口 ❌放弃 ⬇️跳过 -->

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| LangChain Interrupt 2026（5/13-14）Deep Agents 2.0 | P1 | ⏸️ 等待窗口 | Harrison Chase keynote 预期 Deep Agents 2.0 发布；窗口期 5/13-5/14 |
| Anthropic「2026 Agentic Coding Trends Report」| P2 | ✅ 本轮闭环 | Trend 8（安全）+ 评估体系，已产出 Article + SPECA Project，闭环完成 |
| Anthropic Feb 2026 Risk Report（已解密版）| P2 | ⏸️ 待处理 | Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估 |
| CrewAI「Agentic AI Report 2026」| P2 | ⏸️ 待处理 | 500 senior executives 调研，31% workflow 已自动化，从试点到生产的关键转折点 |
| OpenAI Symphony（Issue Tracker 作为 Agent Orchestrator）| P2 | ⏸️ 待处理 | 500% PR 增长，Linear 创始人 Karri Saarinen 关注，Issue Tracker → Control Plane |
| Augment Code「Your agent's context is a junk drawer」| P2 | ⏸️ 待处理 | ETH Zurich 论文解读（AGENTS.md 有效性研究），配置文件过载的认知根源 |
| revfactory/harness-100 | P2 | ⏸️ 待处理 | 100 个生产级 Agent team harnesses，10 个领域，489 个 Agent 定义 |
| Cursor Browser Visual Editor | P2 | ⏸️ 待处理 | DOM 可视化编辑，Cursor 3 的新工具链方向 |
| Anthropic「Scaling Managed Agents」| P2 | ✅ 本轮闭环 | Brain-Hands-Session 三元解耦架构，Meta-harness 设计，TTFT p50 -60%/p95 -90% |
| Anthropic「Effective Harnesses for Long-Running Agents」（Initializer Pattern）| P2 | ✅ 本轮闭环 | 双组件架构（Initializer + Coding Agent），Feature List JSON + Progress File + Git 原子提交，Browser Automation Tools 端到端验证，Planner/Worker 系统性对比 |
| Anthropic「Equipping Agents with Agent Skills」（渐进式披露架构）| P2 | ✅ 本轮闭环 | 三层渐进式披露（metadata → SKILL.md → 附加文件），Skills 成为 frontier agent 标准原语，与 OpenAI Agents SDK Skills 方案收敛 |
| OpenAI「The next evolution of the Agents SDK」| P2 | ✅ 本轮闭环 | Model-Native Harness + Native Sandbox + Manifest 抽象，Harness/Compute 分离，与 Anthropic 方案收敛于相同工程范式 |
| OpenAI「Unrolling the Codex Agent Loop」| P2 | ✅ 本轮闭环 | O(n²) 问题 + Prompt Caching 前缀匹配 + Compaction 机制 + ZDR 矛盾，5处原文引用 |
| OpenAI「Running Codex safely at OpenAI」（企业安全控制面）| P2 | ✅ 本轮闭环 | Sandbox 边界控制 + Auto-review subagent 审批 + Agent-native OpenTelemetry + AI triage agent，5处原文引用，与 Anthropic Initializer Pattern 形成「企业合规视角 + 工程架构视角」完整方案 |
| Anthropic「Trustworthy Agents in Practice」（四层安全架构）| P2 | ✅ 本轮闭环 | 四层组件架构（Model/Harness/Tools/Environment）+ 五项信任原则具体实现，5处原文引用 |
| Agent-Threat-Rule/agent-threat-rules | P2 | ✅ 本轮闭环 | 109 Stars，311 条规则覆盖 9 大威胁类别，OWASP Agentic Top 10（10/10）+ SAFE-MCP（91.8%），96K Skills 扫描发现 751 malware samples，NVIDIA Garak 97.1% recall，Article 形成「安全框架 + 检测标准」闭环 |
| system-prompt-skills（kangarooking）| P2 | ✅ 本轮闭环 | 15 个可执行系统提示词设计模式，64 Stars，从 165 个 AI 产品提示词蒸馏，与 OpenAI Agents SDK Skills 原语形成互补 |
| SkillWard（Fangcun-AI）| P2 | ✅ 本轮闭环 | Agent Skills 三阶段安全扫描，123 Stars，静态+LLM+Docker 沙箱，5,000 Skills ~25% 不安全，约1/3沙箱样本暴露运行时威胁，与 Codex Safe Deployment 形成「发布前扫描 + 运行控制」安全闭环 |
| Agent Squad 2FastLabs | P2 | ✅ 本轮闭环 | Classifier-First 动态路由，SupervisorAgent 并行协调，Python/TypeScript 双语言 |
| Claude Code Memory Setup（590 ⭐）| P2 | ✅ 本轮闭环 | Obsidian Zettelkasten + Graphify 三层记忆体系，71.5x Token优化，499x查询节省，0 token生成成本（AST模式），与 Cursor 3 第三时代形成「范式定义 → 基础设施解法」闭环 |
| Hermes Agent（NousResearch，131.8k ⭐）| P2 | ✅ 本轮闭环 | FTS5 跨 Session 检索 + 技能自创建/自改进，Agent 自主积累范式（关联：Context 工程两极） |
| Sanity Agent Context | P2 | ✅ 本轮闭环 | 结构化 GROQ 查询 + 语义搜索组合，MCP 接入生产级 CMS |
| AI-DLC（awslabs，1,847 ⭐）| P2 | ✅ 本轮闭环 | 三阶段（Inception→Construction→Operations）+ 六合一安全扫描 + 8 平台适配层（关联：Claude Code April Postmortem → 结构化 Human-in-the-loop）|
| Anthropic Introspection Adapters | P2 | ✅ 本轮闭环 | LoRA 适配器让模型自述习得行为，两阶段训练泛化到未见过的微调，AuditBench SOTA |
| getzep/graphiti（25.8k ⭐）| P2 | ✅ 本轮闭环 | 时态上下文图谱，MCP Server，多图数据库支持，与 Introspection Adapters 形成「外部上下文管理 vs 内部行为审计」的主题关联 |
| Anthropic Measuring Agent Autonomy | P2 | ✅ 本轮闭环 | 99.9% 分位 turn 翻倍（~25→45 分钟），部署 overhang，监督范式根本性转移，Agent 主动暂停 > 人类中断 |
| agentmemory（rohitg00，3,047 ⭐）| P2 | ✅ 本轮闭环 | 免 DB 持久记忆基础设施，iii engine 零外部依赖，95.2% R@5，16+ Agent 共享记忆服务器，与 Measuring Agent Autonomy 形成「上下文坍缩 → 记忆基础设施」的主题关联 |
| Cursor 3 第三时代（Agent Fleet 新范式）| P2 | ✅ 本轮闭环 | 三时代演进（Tab→同步Agent→异步Fleet），35% PR 来自云端Agent，15x Agent使用增长，Fleet调度层 + Skills能力层组合架构 |
| Cursor Long-Running Agents（规划优先架构）| P2 | ✅ 本轮闭环 | 规划先行等待批准（upfront alignment reduces follow-ups）+ 多 Agent 互检确保任务完结，36小时案例，Planner/Worker vs Anthropic Initializer/Coding Agent 对比 |
| rowboatlabs/rowboat（13,666 ⭐）| P2 | ✅ 本轮闭环 | 本地优先 AI coworker，持久知识图谱 + Gmail/Calendar/Notion 集成，TypeScript，13,666 Stars，与 Cursor Long-Running Agents 形成「规划+记忆」完整方案 |
| strukto-ai/mirage（1,612 ⭐）| P2 | ✅ 本轮闭环 | 统一虚拟文件系统，bash 工具跨服务操作 S3/Gmail/GitHub/Slack，与 Codex Agent Loop 形成「工具抽象 vs 上下文管理」的互补，6处 README 引用 |
| neo4j-labs/create-context-graph（558 ⭐）| P2 | ✅ 本轮闭环 | 5分钟生成完整知识图谱 Agent 应用，22个预置领域 + 8种框架支持，MCP Server for Claude Desktop；与 OpenAI Agents SDK 形成「执行层 + 记忆层」的完整架构闭环 |
| Cursor Multi-Agent CUDA Kernel 38% 加速 | P2 | ✅ 本轮闭环 | 235 个 CUDA Kernel，3 周自主优化，Planner/Worker + Self-Benchmarking 闭环，与 Anthropic C Compiler 形成方法论印证 |
| Multi-Agent Markdown 协调规范 | P2 | ✅ 本轮闭环 | 协调协议从代码层下沉到 Markdown 声明式规范，Self-Benchmarking 闭环，5处原文引用 |
| CudaForge（OptimAI-Lab，80 ⭐）| P2 | ✅ 本轮闭环 | 训练免费的 Multi-Agent CUDA 工作流，SKILL.md 规范驱动，与 Markdown 协调规范形成「理论→工程实现」闭环，3处 README 引用 |
| Claude Code April 2026 Postmortem（三 bug 导致模型退化）| P2 | ✅ 本轮闭环 | Anthropic Engineering 复盘，三个产品层 bug（推理effort/缓存/提示词）导致六周性能下降，harness 是独立能力维度，5处原文引用 |
| mcpware/cross-code-organizer（310 ⭐）| P2 | ✅ 本轮闭环 | 跨 Claude Code/Codex CLI/MCP 配置管理仪表板，Security scanning + Context budget + Backups，与 Claude Code April Postmortem 形成主题关联（配置管理 → 问题预防）|
| **Anthropic AI-Resistant Technical Evaluations（三轮迭代）**| P2 | ✅ 本轮闭环 | 三轮迭代（真实工作→增加深度→Zachtronics风格），时间约束是关键变量，工具建设判断是AI难以自动化的维度，8处原文引用，与 FeatureBench 形成「AI抗性设计 vs 能力边界检测」互补 |
| **LiberCoders/FeatureBench（ICLR 2026）**| P2 | ✅ 本轮闭环 | 功能级编程评测框架，Fast split 57.2秒/实例，支持5个主流Agent框架，与 Anthropic AI-Resistant Evaluations 形成主题关联，3处README引用 |
| **Anthropic「Effective Context Engineering for AI Agents」**| P2 | ✅ 本轮闭环 | 从 Prompt Engineering 到 Context Engineering 的范式转移，注意力预算有限资源，Compaction + Note-taking + Sub-agents 三大工程支柱，8处原文引用，与 Volt/Cursor/Storybloq 形成完整上下文工程图谱 |
| **Martian-Engineering/Volt（273 Stars）**| P2 | ✅ 本轮闭环 | 无损上下文管理 LCM，双态架构（Immutable Store + Active Context）+ 三级升级协议保证收敛，OOLONG benchmark 全面超越 Claude Code，与 Anthropic Context Engineering 形成「理论 → 工程实现」闭环，4处 README 引用 |
| **HumanLayer 12-Factor Agents + HumanLayer SDK**| P2 | ✅ 本轮闭环 | 19,728 Stars（12-Factor Agents）+ 10,745 Stars（HumanLayer），Factor 3/5/7/8/9 vs Anthropic Brain/Hands 架构完整对比，来源：GitHub README + 官方文档，6处原文引用 |
| **Cursor 动态上下文发现五大工程实践**| P2 | ✅ 本轮闭环 | 文件作为上下文原语，动态发现 vs 静态注入，46.9% token 节省，6处官方原文引用，与 Anthropic Context Engineering 形成「内容改造 vs 访问模式重构」互补 |
| **kruschdev/krusch-context-mcp（61 Stars）**| P2 | ✅ 本轮闭环 | 统一 IDE 上下文引擎，18 tools MCP Server，Lakebase 架构，PostgreSQL + SQLite + Ollama 本地向量，零 API 成本 + 全数据主权，5处 README 引用，与 Cursor 动态上下文发现形成「方法论 → 工程实现」闭环 |
| **Anthropic「2026 Agentic Coding Trends Report」安全 + 评估体系**| P2 | ✅ 本轮闭环 | Trend 8（安全-first 架构）+ 协作悖论（0-20% 完全委托率）+ 评估能力与委托边界同构，8处原文引用，SPECA 填补规范层审计空白 |
| **NyxFoundation/speca（373 Stars）**| P2 | ✅ 本轮闭环 | spec-anchored 安全审计框架，Sherlock Fusaka 恢复全部 15 个漏洞 + 4 个新漏洞（含加密不变量违反），5处 README 引用，与 Trend 8 形成「认知风险 → 规范层防御」闭环 |
| **microsoft/skills（2,274 Stars）**| P2 | ✅ 本轮闭环 | 174企业级Skills，Context-Driven Development架构，SKILL.md三层渐进式披露与Anthropic方案同构，Azure SDK + Foundry全栈覆盖，5处 README 引用，与 Context Engineering Article 形成「理论 → 企业工程实践」闭环 |

## 📌 Articles 线索
<!-- 本轮无新增文章时必须填写：下轮可研究的具体方向 -->

- **LangChain Interrupt 2026（5/13-14）Deep Agents 2.0**：框架级架构更新，Harrison Chase keynote 发布预期
- **Anthropic Feb 2026 Risk Report（已解密版）**：Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估
- **CrewAI「Agentic AI Report 2026」**：500 senior executives 调研，31% workflow 已自动化
- **Augment Code「Your agent's context is a junk drawer」**：ETH Zurich 论文解读（AGENTS.md 有效性研究）
- **flutter/skills（1,873 Stars）独立成篇**：Flutter 官方 skill 库，与 microsoft/skills 对比分析（移动端 vs 企业级）
- **Prompthon-IO/agent-systems-handbook（184 Stars）**：2026-04-20 创建，生产级 Agent 手册，多路径学习架构（Explorer/Practitioner/Builder/Contributor）

## 📌 Projects 线索

- **flutter/skills（1,873 Stars）**：Flutter 官方 skill 库，npx skills CLI 工具，SKILL.md 标准格式，与 microsoft/skills 对比
- **Prompthon-IO/agent-systems-handbook（184 Stars）**：2026-04-20 创建，生产级 Agent 手册，多路径学习架构
- **Local-Deep-Research（6,643 ⭐）**：~95% SimpleQA（Qwen3.6-27B on 3090），10+ 搜索引擎，本地加密
- **Cloudflare agents-sdk**：Agents Week 发布的 Agent SDK，Preview 版本
- **moonshot-ai/kimi-k2.6**：Kimi K2.6 开源版，13 小时不间断编码，300 个 sub-agents
- **OpenHarness（12,264 Stars）**：HKUDS 出品，深度集成 Claude Code / OpenClaw / Cursor，43+ Tools
- **InnovatorBench（ICLR 2026）**：Agent 创新研究能力评测，GAIR-NLP 出品

## 🏷️ 本轮产出索引

- `articles/fundamentals/anthropic-effective-context-engineering-for-ai-agents-2026.md` — Anthropic「Effective Context Engineering for AI Agents」深度解读，8处原文引用。覆盖：注意力预算核心约束，Compaction/Note-taking/Sub-agents三大支柱，SKILL.md格式趋同理论基础，与Volt/Cursor/Storybloq形成完整上下文工程图谱
- `articles/projects/microsoft-skills-174-context-driven-development-2274-stars-2026.md` — microsoft/skills 项目推荐，2,274 Stars，174企业级Skills，Context-Driven Development架构，5处 README 引用，与 Context Engineering Article 形成「理论 → 企业工程实践」闭环

---

## 📋 关键文件路径

- 仓库根目录：`/root/.openclaw/workspace/repos/agent-engineering-by-openclaw`
- 状态文件：`.agent/state.json`
- PENDING.md：`.agent/PENDING.md`
- REPORT.md：`.agent/REPORT.md`
- HISTORY.md：`.agent/HISTORY.md`
- Changelog 目录：`changelogs/`

---

*本文件由 AgentKeeper 自动维护，每轮更新后覆盖。*
