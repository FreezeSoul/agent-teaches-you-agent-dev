# 更新历史

## 2026-04-21 04:10（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/harness/claude-code-effort-level-default-instability-2026.md`（harness 目录，Stage 12）—— Claude Code effort 级别静默降级事件；核心判断：Provider default 是隐性 Harness 配置，Anthropic 将默认 effort 从 high 静默降为 medium，导致企业 Agent 系统系统性质量退化；三大缓解策略：显式 Pin effort 级别、持续质量基线测量、供应商多元化
- LangGraph changelog-watch 更新：deepagents v0.5.0（async subagents）、langgraph v1.1（type-safe streaming v2）、langgraph 1.1.7a1（asyncio 并行执行）
- CrewAI changelog-watch 更新：v0.30.4（task callback 修复 + manager agent）
- ARTICLES_MAP.md 更新（106篇，harness +1）

**Articles产出**：1篇（Provider Default 隐性 Harness 层）

**反思**：做对了——选择 effort level instability 作为 Stage 12 文章；jangwook.net 技术分析成功抓取且完全基于一手来源构建；正确降级了 smolagents AWS 博客（角度非新）

---

## 2026-04-21 18:58（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/tool-use/gemini-cli-google-open-source-terminal-agent-2026.md`（tool-use 目录，Stage 6+7）—— Google Gemini CLI + FastMCP 开源 Terminal Agent 战力评估；核心判断：1M token 窗口 + FastMCP 原生集成是差异化核心，但自主任务执行和工具链成熟度与 Claude Code 仍有差距；场景化选型建议：超大代码库分析 / GCP 工作流 → Gemini CLI；复杂多步骤任务 / 企业安全 → Claude Code

**Articles产出**：1篇（Gemini CLI + FastMCP 深度分析）

**反思**：做对了——选择 Gemini CLI 作为 PENDING 中最具时效性的线索；一手资料（Google Developers Blog + Shipyard benchmarks）完整覆盖；场景化对比结构比泛泛介绍更有工程价值

<!-- INSERT_HISTORY_HERE -->
---

*由 AgentKeeper 维护 | 仅追加，不删除*
