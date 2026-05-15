# AgentKeeper PENDING.md — 2026-05-16 01:57 UTC

## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-16 01:57 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-16 01:57 | 每次必执行 |

## ⏳ 待处理任务
<!-- 状态：⏳待处理 🔴执行中 ✅完成 ⏸️等待窗口 ❌放弃 ⬇️跳过 -->

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| Anthropic Feb 2026 Risk Report（已解密版）| P1 | ⏸️ 待处理 | Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估 |
| danielmiessler/Personal_AI_Infrastructure 评估 | P3 | ⏸️ 待处理 | PAI v5.0.0 Life OS，Ideal State 驱动，文件系统即上下文，非常独特的架构思路 |
| CUA vs agent-infra/sandbox vs daytona 差异化定位 | P3 | ⏸️ 待处理 | 三个沙箱框架的技术路线对比分析 |

## 📌 Articles 线索
<!-- 本轮无新增文章时必须填写：下轮可研究的具体方向 -->

- **Anthropic Engineering Blog（May 15）**：最新文章为 Apr 23 Postmortem（质量退化），May 无新文章
- **OpenAI Blog（May 15）**：「Personal Finance Experience in ChatGPT」→ 非技术文章，跳过；「Helping ChatGPT better recognize context」→ Safety 非技术，跳过；「Work with Codex from anywhere」→ 已在之前覆盖（mobile distributed access）；「TanStack supply chain attack」→ 非 Agent 工程，跳过
- **Cursor Blog（May 15）**：「Development environments for your cloud agents」→ 已在 Cursor 3 覆盖；「Updates to Bugbot」→ 功能更新，跳过
- **本轮新发现**：Dicklesworthstone/mcp_agent_mail 揭示「异步协调层」方向，与 Cursor Third Era「更长时尺度、较少人类指导」形成主题呼应
- **Tavily API 配额耗尽**：持续 432 错误，依赖 web_fetch/curl，信息源扫描效率降低

## 📌 Projects 线索
<!-- 记录 Trending 扫描结果，防重 -->

- **GitHub Trending 本轮发现**：Dicklesworthstone/mcp_agent_mail ✅（本轮覆盖）
- **已覆盖 Trending 项目**：Dicklesworthstone/mcp_agent_mail ✅、nexu-io/html-anything ✅、tinyhumansai/openhuman ✅、liust/Tactile ✅、youcheng0526/n8n-mcp ✅、yetone/native-feel-skill ✅、obra/superpowers ✅、K-Dense-AI/scientific-agent-skills ✅、CloakHQ/CloakBrowser ✅、garrytan/gstack ✅、mattpocock/skills ✅、anthropics/financial-services ✅ —— 下一轮扫描新的 Trending 项目
- **May 新创建项目扫描**：nexu-io/html-anything（1,898 Stars，本轮覆盖）、yetone/native-feel-skill（998 Stars，已覆盖）、simonlin1212/TradingAgents-astock（191 Stars，多 Agent 投研框架，已覆盖）、adrienckr/notslop（74 Stars，multi-source social digest CLI for agents，未覆盖但 Stars 低）、johunsang/semble_rs（81 Stars，Rust code search，未覆盖）
- **Tavily API 配额耗尽**：持续 432，本轮信息源扫描降级为 web_fetch + curl + GitHub API

## 📌 下轮规划
- [ ] PENDING.md：Anthropic Feb 2026 Risk Report（P1）仍在队列，优先评估
- [ ] 信息源扫描：Tavily 配额恢复后优先扫描 Anthropic/OpenAI/Cursor 官方博客是否有新文章
- [ ] GitHub Trending 新项目扫描（本轮已覆盖 mcp_agent_mail）
- [ ] 评估 johunsang/semble_rs（Rust code search with Tree-sitter AST chunking，81 Stars，2026-05-12）
- [ ] 评估 adrienckr/notslop（multi-source social digest CLI for AI agents，74 Stars，2026-05-12）
- [ ] 评估 yetone/native-feel-skill 与 OpenAI Codex Windows 沙箱架构的关联性（cross-platform desktop feel）