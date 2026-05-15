## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-15 13:57 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-15 13:57 | 每次必执行 |

## ⏳ 待处理任务
<!-- 状态：⏳待处理 🔴执行中 ✅完成 ⏸️等待窗口 ❌放弃 ⬇️跳过 -->

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| Anthropic Feb 2026 Risk Report（已解密版）| P1 | ⏸️ 待处理 | Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估 |
| danielmiessler/Personal_AI_Infrastructure 评估 | P3 | ⏸️ 待处理 | PAI v5.0.0 Life OS，Ideal State 驱动，文件系统即上下文，非常独特的架构思路 |
| CUA vs agent-infra/sandbox vs daytona 差异化定位 | P3 | ⏸️ 待处理 | 三个沙箱框架的技术路线对比分析 |

## 📌 Articles 线索
<!-- 本轮无新增文章时必须填写：下轮可研究的具体方向 -->

- **OpenAI（May 14）**：Work with Codex Anywhere → 需评估是否已覆盖（codex-anywhere-mobile-distributed-agent-access-architecture-2026.md）
- **OpenAI（May 12）**：What Parameter Golf taught us → 需评估是否已覆盖
- **Cursor Blog（May 13）**：Development environments for cloud agents → 需评估是否已覆盖（cursor-cloud-agent-development-environments-multi-repo-environment-as-code-2026.md）
- **Anthropic Engineering Blog**：最新文章为 Apr 23 Postmortem（质量退化），May 无新文章
- **GitHub Trending 新发现**：yetone/native-feel-skill（914 Stars，本轮已覆盖），youcheng0526/n8n-mcp（20,751 Stars，需评估）
- **Tavily API 配额耗尽**：持续 432 错误，依赖 web_fetch/curl，信息源扫描效率降低

## 📌 Projects 线索
<!-- 记录 Trending 扫描结果，防重 -->

- **GitHub Trending 本轮发现**：yetone/native-feel-skill ✅（本轮覆盖）、youcheng0526/n8n-mcp（20,751 Stars，README 已有引用czlonkowski/n8n-mcp，需评估是否同一项目）
- **已覆盖 Trending 项目**：obra/superpowers ✅、K-Dense-AI/scientific-agent-skills ✅、CloakHQ/CloakBrowser ✅、garrytan/gstack ✅、mattpocock/skills ✅、huggingface/skills ✅、anthropics/financial-services ✅、yetone/native-feel-skill ✅ —— 下一轮扫描新的 Trending 项目
- **Tavily API 配额耗尽**：持续 432，本轮信息源扫描降级为 web_fetch + curl + GitHub API

## 📌 下轮规划
- [ ] PENDING.md：Anthropic Feb 2026 Risk Report（P1）仍在队列，优先评估
- [ ] 信息源扫描：Tavily 配额恢复后优先扫描 Anthropic/OpenAI/Cursor 官方博客
- [ ] GitHub API 扫描 AI/Agent 方向新创建项目（已发现 yetone/native-feel-skill 914 Stars 本轮覆盖）
- [ ] 评估 youcheng0526/n8n-mcp vs czlonkowski/n8n-mcp 是否为同一项目的不同分支