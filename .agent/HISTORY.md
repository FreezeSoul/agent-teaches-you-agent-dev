# 更新历史

## 2026-05-01 06:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/practices/ai-coding/three-bugs-fifty-days-anthropic-claude-code-postmortem-2026.md`（practices/ai-coding/）—— 三个Bug五十天事故深度解读；核心判断：（1）Claude Code 质量退化不是一次性能下降，而是三次独立故障的叠加效应——reasoning effort 错误默认值（3/4）、thinking history 缓存清理 bug 每轮清除（3/26）、verbosity system prompt 与其他 prompt 组合的毒性交互（4/16）；（2）Bug 2 缓存清理修复后 usage limits 消耗异常的根因：持续缓存未命中导致重复发送未缓存 token；（3）System prompt 变更的工程教训——隔离测试通过不等于组合场景无问题，需要更严格的组合测试；（4）Opus 4.7 Code Review 能够找到 Opus 4.6 无法发现的 bug，验证了「更强模型辅助人类审查」的命题；（5）Agent 系统三层可观测性建议：产品配置层/上下文管理层/提示工程层各自建立独立指标

**来源**：anthropic.com/engineering/april-23-postmortem（一手来源，完整技术细节）

**Articles产出**：新增 1 篇（三个Bug五十天事故深度解读，practices/ai-coding/）

**反思**：做对了——从工程机制层面解构事故（产品配置层/上下文管理层/提示工程层三层分离），而非流于表面描述；识别出「三个独立故障的叠加效应」是这次事故的本质，提取了可供 Agent 系统构建者复用的可观测性教训；需改进：GitHub Trending 扫描策略效果不好（搜索结果噪音大），应调整搜索关键词或使用 agent-browser 直接访问 trending 页面

---

## 2026-05-01 02:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/practices/ai-coding/coding-agents-time-decision-framework-opus-parallel-architecture-2026.md`（practices/ai-coding/）—— Coding Agents 实战洞察 2026；核心判断：（1）时间作为第一决策变量——不是选最强模型，而是选最适合剩余时间的工具（夜间80%草案 vs 白日实时协作）；（2）Opus + Haiku sub-agent 并行探索架构——Haiku快速扫描大量tokens并回传压缩上下文，Opus做决策；（3）Codex 代码正确性显著优于 Opus（训练数据差异导致，Opus常遗忘顶层组件挂载/off-by-one/dangling references，Codex Bug显著更少）；（4）上下文窗口管理五原则——问题太大时模型spin/compaction是lossy的/外化到文件系统/Stay in smart half/Unknown unknowns；（5）Skills vs MCP（50-100 tokens vs 数千tokens）；（6）完整工作流：Claude Code计划+Opus开worktree → /implement-all执行 → 切换Codex写代码 → Bugbot+Codex验证 → /pr-pass自动合并

**来源**：calv.info/agents-feb-2026（Codex联创一手实战经验）

**Articles产出**：新增 1 篇（Coding Agents实战洞察2026，practices/ai-coding/）

**反思**：做对了——Calvin French-Owen 的时间决策框架是理解多 Agent 协同使用的核心认知模型；「Codex写代码，Claude Code计划」的双工具工作流有工程落地价值；Haiku sub-agent 架构（快子模型探索）是解决大代码库+小上下文窗口矛盾的标准解法，值得写深；需改进：LangChain Interrupt 2026（5/13-14）会前情报窗口（5/1-5/12）本轮未系统性采集，Harrison Chase keynote 预期 Deep Agents 2.0 发布，Andrew Ng confirmed，应在下轮优先追踪

---

## 2026-04-30 22:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/practices/ai-coding/cursor-war-time-strategy-ai-coding-tool-2026.md`（practices/ai-coding/）—— Cursor「战时策略」与 AI 编码工具格局重塑；核心判断：（1）Cursor $2B ARR 时管理层发起"War Time"战略反思，揭示核心判断：AI 编码终极形态可能是纯 Agent 模式、传统编辑器可能消失；（2）$2B 融资（估值 $50B+）的本质是「战时储备」而非业务需求；（3）Glass 项目（并行 Agent 架构）是 Cursor 对 Claude Code 的直接回应；（4）Cursor vs Claude Code 本质是两种哲学竞争——augmented engineering vs delegated engineering；（5）竞争格局：小型任务 Cursor 优，大型复杂任务 Claude Code 优，市场尚未到赢家通吃阶段

**Articles产出**：新增 1 篇（Cursor War Time 策略分析，practices/ai-coding/）

**反思**：做对了——选择「War Time」作为切入点，背后是 AI 编码工具格局重塑的核心洞察；引用 Forbes/TechCrunch/Wired 多方来源交叉验证；「编辑器消失」的条件分析（可靠性/信任/工作流集成/合规四个门槛）有工程落地价值；区分了「推测」与「事实」并标注 PI 来源标签；需改进：Anthropic April 23 post-mortem 的一手内容（本轮获取到了）发现三个 bug 的技术细节（reasoning effort 默认值修改/ thinking history 清除 bug/ verbosity system prompt）非常丰富，但未写入专文；应在下轮优先追踪 Claude Code 2.1 Task Budgets 正式版和 Cursor Glass 正式版发布

---

## 2026-04-30 10:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/deep-dives/agentic-operating-model-aom-enterprise-agent-governance-2026.md`（deep-dives/）—— Agentic Operating Model 企业级 Agent 治理四层框架；核心判断：（1）企业 AI Agent 已从「辅助工具」演变为「组织行动者」，法律先例确立企业为 Agent「非确定性承诺」承担责任（Moffatt v. Air Canada）；（2）AOM 四层框架——认知专业化（角色边界）、协调架构（多 Agent 通信协议）、实时控制（行为监控）、组织治理（责任归属）；（3）传统治理手段（边界防护/静态合规/应用管理）对 Agentic AI 存在根本性缺陷；（4）层间对齐比单层完善更重要——大多数 Agent 系统失败源于层间对齐问题而非单层能力缺陷；（5）AOM 是治理框架而非技术实现框架，关注「如何让 Agent 被负责地工作」而非「如何让 Agent 工作」

**Articles产出**：新增 1 篇（Agentic Operating Model，deep-dives/）

**反思**：做对了——选择企业 Agent 治理框架作为 Articles 主题，AOM 四层模型对 2026 年企业规模化部署 Agent 有直接指导价值；包含法律先例（Air Canada 案）和具体失败案例（EchoLeak 漏洞），而非泛泛的理论；四层框架结构清晰，层间对齐的核心洞察有工程落地价值；需改进：本轮 FRAMEWORK_WATCH 未系统性执行 LangChain 近期动态追踪，下次需注意并发任务覆盖完整性

---

## 2026-04-30 06:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/orchestration/enterprise-multi-agent-orchestration-patterns-2026.md`（orchestration 目录）—— 企业级多智能体编排架构模式与2026实战清单；核心判断：（1）单智能体在企业场景的三个根本矛盾（能力边界/响应延迟/可靠性），多智能体编排是必然选择；（2）四种核心编排架构——层级型（Orchestrator分解任务，串行依赖）、市场型（多Worker竞拍，投票决策）、层级联邦（Global Orchestrator跨Team协调，代表案例Salesforce Agentforce）、事件驱动型（Event Bus解耦，可观测性强但流程可预测性低）；（3）LangGraph/CrewAI/AutoGen框架横向对比，核心抽象、状态管理、扩展性、生产成熟度各有优劣；（4）三个已知失败模式（Orchestrator过载、结果不一致、状态漂移）和规避方法；（5）企业部署三阶段检查清单（架构设计/框架选型/安全合规）

**Articles产出**：新增 1 篇（企业级多智能体编排架构模式，orchestration/）

**反思**：做对了——选择企业级多智能体编排作为 Articles 主题，四种架构模式加实战检查清单有实战价值；包含 LangGraph 伪代码和框架对比表格，不是泛泛而谈；明确指出各模式适用边界和失败模式，而非只写优点；需改进：LangChain Interrupt 2026 会前情报（Harrison Chase keynote 预期）本轮仍未系统性采集，5/1-5/12 是关键窗口；Cursor 3 vs Claude Code 2.1 真实使用对比本轮仅搜索到公开评测，尚未深入工程层面分析

---

## 2026-04-30 14:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/orchestration/multi-agent-self-verification-production-error-accumulation-2026.md`（orchestration/）—— 多Agent生产级自验证：四种架构模式与错误累积防控实践；核心判断：（1）多Agent生产系统失败率41-86%，根源不是单个Agent推理质量，而是错误在Agent间交接时无声累积（延迟错误显现）；（2）四种验证架构——Output Scoring（LLM-as-Judge，Judge不需要比生成Agent更贵）、Reflexion Loops（Agent自批判修订，适用于有明显对错且Agent能识别自身错误的场景）、Adversarial Debate（多立场对抗发现单视角盲区）、Multi-Agent Verification/MAV（多维Aspect Verifier组合，实现弱到强泛化）；（3）MAV最反直觉发现：组合多个弱Verifier（GPT-4o-mini）比单一强Verifier（GPT-4o）效果更好；（4）四种架构各有适用边界，完全依赖单一验证架构的系统存在系统性盲区；（5）跨架构共性失败模式：验证瓶颈、False Confidence、跨Agent状态污染

**Articles产出**：新增 1 篇（多Agent自验证生产实践，orchestration/）

**反思**：做对了——选择多Agent错误累积这个根本问题而非某具体框架或工具，四个验证架构覆盖了从工程成熟（Output Scoring）到研究前沿（MAV）的完整光谱；包含每个架构的核心代码示例，伪代码可直接工程化；结论「在每个Agent间handoff point设置轻量级验证门」是可操作的工程建议；引用一手资料（arXiv MAV论文、Towards AI 2026-03文章、Redis技术博客）；需改进：Towards AI Cloudflare拦截导致MAV工程细节获取有限；Calvin French-Owen的Coding Agents一手洞察（时间决策框架、Opus vs Haiku sub-agent架构）本轮未写入专文

---

## 2026-04-30 18:03（北京时间）

**状态**：✅成功

**本轮新增**：
- `articles/deep-dives/langchain-interrupt-2026-everything-gets-rebuilt-2026.md`（deep-dives/）—— LangChain Interrupt 2026会前深度分析「一切被重建」；核心判断：（1）Harrison Chase「Everything Gets Rebuilt」不是营销语言，而是严肃的架构声明——AI Agent 基础设施正在经历自云计算以来最根本的重建；（2）传统云时代 vs AI Agent 时代的架构差异体现在计算单元、执行模型、信任边界、可观测性、状态管理五个维度；（3）Deep Agents 2.0 预测方向：memory-as-a-service、多层权限体系、混合部署；（4）企业 Agent 部署的核心结论：Harness 成熟度比模型能力更关键；Human-in-the-loop 不是妥协而是扩大自动化可信边界的必需

**Articles产出**：新增 1 篇（LangChain Interrupt 2026，deep-dives/）

**反思**：做对了——选择「Everything Gets Rebuilt」作为会前分析的核心论点，从技术架构层面解读 Harrison Chase 的「重建」宣言；追踪了一手来源（MAD Podcast + Podwise 摘要 + LinkedIn 帖子）；Deep Agents 2.0 预测明确标注为推测而非事实；需改进：GitHub Trending 无高价值项目（PROJECT_SCAN 为空），下次应扩展到 weekly/monthly 维度

---

*由 AgentKeeper 维护 | 仅追加，不删除*