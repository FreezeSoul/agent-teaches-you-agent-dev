## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-15 23:57 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-15 23:57 | 每次必执行 |

## ⏳ 待处理任务
<!-- 状态：⏳待处理 🔴执行中 ✅完成 ⏸️等待窗口 ❌放弃 ⬇️跳过 -->

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| Anthropic Feb 2026 Risk Report（已解密版）| P1 | ⏸️ 待处理 | Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估 |
| danielmiessler/Personal_AI_Infrastructure 评估 | P3 | ⏸️ 待处理 | PAI v5.0.0 Life OS，Ideal State 驱动，文件系统即上下文，非常独特的架构思路 |
| CUA vs agent-infra/sandbox vs daytona 差异化定位 | P3 | ⏸️ 待处理 | 三个沙箱框架的技术路线对比分析 |

## 📌 Articles 线索
<!-- 本轮无新增文章时必须填写：下轮可研究的具体方向 -->

- **OpenAI（May 14）**：「Work with Codex Anywhere」→ 已在 `openai-codex-anywhere-mobile-distributed-agent-access-architecture-2026.md` 覆盖
- **OpenAI（May 12）**：「What Parameter Golf taught us」→ 已在 `openai-parameter-golf-ai-coding-agents-competition-insights-2026.md` 覆盖
- **Cursor Blog（May 13）**：「Development environments for your cloud agents」→ 已在 `cursor-cloud-agent-development-environments-multi-repo-environment-as-code-2026.md` 覆盖
- **Cursor Blog（May 13）**：「Development environments for your cloud agents」→ 本轮深度分析 HTML Anything 项目的「HTML 优先于 Markdown」范式转移作为 AI Coding 方向的补充（Claude Code 团队停止使用 Markdown 官方声明 + HTML Anything 实证）
- **Anthropic Engineering Blog**：最新文章为 Apr 23 Postmortem（质量退化），May 无新文章
- **GitHub Trending 新发现**：nexu-io/html-anything（1,847 Stars，本轮覆盖），zhanex/legax（Mobile-first remote control for coding agents，7 Stars，需评估）
- **Tavily API 配额耗尽**：持续 432 错误，依赖 web_fetch/curl，信息源扫描效率降低

## 📌 Projects 线索
<!-- 记录 Trending 扫描结果，防重 -->

- **GitHub Trending 本轮发现**：nexu-io/html-anything ✅（本轮覆盖）、zhanex/legax（Mobile-first remote control for coding agents，7 Stars，self-hosted relay + Telegram support + local-first privacy，需评估）
- **已覆盖 Trending 项目**：nexu-io/html-anything ✅、tinyhumansai/openhuman ✅、liust/Tactile ✅、youcheng0526/n8n-mcp ✅、yetone/native-feel-skill ✅、obra/superpowers ✅、K-Dense-AI/scientific-agent-skills ✅、CloakHQ/CloakBrowser ✅、garrytan/gstack ✅、mattpocock/skills ✅、huggingface/skills ✅、anthropics/financial-services ✅ —— 下一轮扫描新的 Trending 项目
- **Tavily API 配额耗尽**：持续 432，本轮信息源扫描降级为 web_fetch + curl + GitHub API
- **youcheng0526/n8n-mcp（20,751 Stars）**：需确认与 README 中已有的 czlonkowski/n8n-mcp 是否为同一项目的不同分支/版本（可能一个是 fork，一个是独立实现）

## 📌 下轮规划
- [ ] PENDING.md：Anthropic Feb 2026 Risk Report（P1）仍在队列，优先评估
- [ ] 信息源扫描：Tavily 配额恢复后优先扫描 Anthropic/OpenAI/Cursor 官方博客是否有新文章
- [ ] GitHub API 扫描 AI/Agent 方向新创建项目（已发现 zhanex/legax 7 Stars 本轮待评估）
- [ ] 评估 zhanex/legax（Mobile-first remote control for coding agents）与 OpenAI「Work with Codex Anywhere」的关联性（两者都解决「分布式 Agent 控制」问题）
- [ ] 评估 youcheng0526/n8n-mcp（20,751 Stars）与 czlonkowski/n8n-mcp 是否为同一项目的不同分支