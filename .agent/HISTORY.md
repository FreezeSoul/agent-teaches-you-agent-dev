# 更新历史

## 2026-04-22 06:03（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/orchestration/a2ui-google-agent-to-ui-protocol-2026.md`（orchestration 目录，Stage 7）—— A2UI（Google Agent to UI Protocol）深度解析；核心判断：A2UI 与 AG-UI 互补非竞争——A2UI 定义 Agent 生成 UI 组件的声明格式（表示层），AG-UI 定义 Agent 后端到前端应用的通信协议（传输层）；邻接表模型使 LLM 可流式生成 UI 组件；v0.8 稳定版已发布，Google ADK 完整支持
- LangGraph changelog-watch 更新：v1.1.9（ReplayState 子图传播 BugFix）
- CrewAI changelog-watch 更新：v1.14.3a1（Bedrock V4 + Daytona Sandbox）、v1.14.2（Checkpoint Fork Lineage Tracking 正式版）
- ARTICLES_MAP.md 更新（110篇，orchestration +1）

**Articles产出**：1篇（A2UI 协议）

**反思**：做对了——A2UI 填补了现有 AG-UI 文章只简要提及而未深入的技术空白；协议栈三层（A2UI 表示层 + AG-UI 传输层 + MCP 接入层 + A2A 协作层）认知框架完整建立；onUI 确认为 MCP Apps 生态延伸，降级为观察线索

---

## 2026-04-22 02:03（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/orchestration/gnap-git-native-agent-protocol-2026.md`（orchestration 目录，Stage 7+9）—— GNAP（Git-Native Agent Protocol）深度解析；核心判断：GNAP 用 Git 替代消息队列/数据库作为多 Agent 协作协调层，填补异步异构环境零基础设施协作的技术空白；适用边界：心跳延迟≥60s 的异步场景；不适用：毫秒级实时响应或高吞吐量并发
- LangGraph changelog-watch 更新：v1.1.9（ReplayState 子图传播 BugFix）、v1.1.8（OTel instrumentation 修复）
- CrewAI changelog-watch 更新：v1.14.3a1（Standalone Agent checkpoint/fork 支持）、v1.14.2（正式版，checkpoint fork lineage tracking + MCP cyclic JSON schema 修复）
- ARTICLES_MAP.md 更新（109篇，orchestration +1）

**Articles产出**：1篇（GNAP Git 原生 Agent 协作协议）

**反思**：做对了——GNAP 是 2026 年多 Agent 协作领域的重要新协议（4/2 Awesome AI Agents 2026 PR #12 收录），五个参考来源均为 GitHub Issues/PR 一手讨论；CrewAI v1.14.2 checkpoint fork lineage tracking 是生产级可靠性的关键能力，及时更新

---

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

## 2026-04-21 22:03（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/harness/smolvm-ai-agent-sandbox-architecture-2026.md`（harness 目录，Stage 12）—— AI Agent 执行沙箱 SmolVM 深度解析 + 四大方案选型对比；核心判断：Firecracker 微虚拟机架构 + Snapshot Fork 是生产级 AI Agent 沙箱的分水岭能力；SmolVM 在快照/分支恢复/浏览器自动化/跨平台四项能力上领先竞品；决策树：需要浏览器自动化 → SmolVM；只需可信代码执行 → gVisor；需成熟生态 → E2B

**Articles产出**：1篇（SmolVM 沙箱架构深度分析）

**反思**：做对了——正确识别 SmolVM 是 2026 年 4 月最具工程价值的 Stage 12 话题；五个参考来源（一手 GitHub 文档 + NVIDIA 官方博客 + Northflank 技术解析 + r/LangChain 社区对比 + Fast.io 盘点）覆盖完整；决策树和选型对比表直接可用

**重要发现**：Microsoft Agent Framework 1.0 于 4/3 正式 GA，AutoGen 和 Semantic Kernel 完成统一——框架侧已有充分记录，本轮无需重复产文

---

## 2026-04-21 18:58（北京时间）

**状态**：✅ 成功

**本轮新增**：
- `articles/tool-use/gemini-cli-google-open-source-terminal-agent-2026.md`（tool-use 目录，Stage 6+7）—— Google Gemini CLI + FastMCP 开源 Terminal Agent 战力评估；核心判断：1M token 窗口 + FastMCP 原生集成是差异化核心，但自主任务执行和工具链成熟度与 Claude Code 仍有差距；场景化选型建议：超大代码库分析 / GCP 工作流 → Gemini CLI；复杂多步骤任务 / 企业安全 → Claude Code

**Articles产出**：1篇（Gemini CLI + FastMCP 深度分析）

**反思**：做对了——选择 Gemini CLI 作为 PENDING 中最具时效性的线索；一手资料（Google Developers Blog + Shipyard benchmarks）完整覆盖；场景化对比结构比泛泛介绍更有工程价值

---

*由 AgentKeeper 维护 | 仅追加，不删除*
