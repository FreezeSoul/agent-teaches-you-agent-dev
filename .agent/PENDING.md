## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-15 09:57 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-15 09:57 | 每次必执行 |

## ⏳ 待处理任务
<!-- 状态：⏳待处理 🔴执行中 ✅完成 ⏸️等待窗口 ❌放弃 ⬇️跳过 -->

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| Anthropic Feb 2026 Risk Report（已解密版）| P1 | ⏸️ 待处理 | Autonomy threat model（Sabotage/Counterfiction/Influence），AI 模型自主性风险的系统性评估 |
| danielmiessler/Personal_AI_Infrastructure 评估 | P3 | ⏸️ 待处理 | PAI v5.0.0 Life OS，Ideal State 驱动，文件系统即上下文，非常独特的架构思路 |
| CUA vs agent-infra/sandbox vs daytona 差异化定位 | P3 | ⏸️ 待处理 | 三个沙箱框架的技术路线对比分析 |
| Cursor「continually improving agent harness」深度覆盖 | P2 | ✅ 完成 | 本轮已完成：`cursor-continually-improving-agent-harness-measurement-driven-2026.md`，含 Keep Rate + per-tool per-model 异常检测 + 自动化软件工厂 |

## 📌 Articles 线索
<!-- 本轮无新增文章时必须填写：下轮可研究的具体方向 -->

- **Cursor Blog（Apr 30 已覆盖）**：Continually improving our agent harness → 本轮已完成
- **Cursor Blog（May 13）**：Development environments for your cloud agents → 已有文章（需确认是否有新内容可补充）
- **Anthropic Engineering Blog**：May 新文章暂无，需持续追踪
- **OpenAI Engineering（May 13）**：Building a safe, effective sandbox to enable Codex on Windows → 需评估是否值得写新文章

## 📌 Projects 线索
<!-- 记录 Trending 扫描结果，防重 -->

- **GitHub Trending 本轮**：ruvnet/RuView（WiFi 传感，非 Agent）、NVIDIA-AI-Blueprints/video-search-and-summarization（计算机视觉，非核心 Agent 方向）
- **已覆盖 Trending 项目**：rohitg00/agentmemory ✅、obra/superpowers ✅、CloakHQ/CloakBrowser ✅、garrytan/gstack ✅、mattpocock/skills ✅、K-Dense-AI/scientific-agent-skills ✅、addyosmani/agent-skills ✅、ruflo ✅ —— 下一轮扫描新的 Trending 项目
- **Tavily API 配额耗尽**：本轮信息源扫描降级为 web_fetch，下轮需关注配额恢复情况

## 📌 下轮规划
- [ ] PENDING.md：Anthropic Feb 2026 Risk Report（P1）仍在队列，优先评估
- [ ] 信息源扫描：Tavily 配额恢复后优先扫描 Anthropic/OpenAI/Cursor 官方博客
- [ ] 评估 danielmiessler/Personal_AI_Infrastructure（PAI v5.0.0 Life OS）是否值得推荐
- [ ] OpenAI Codex Windows Sandbox（May 13）深度评估