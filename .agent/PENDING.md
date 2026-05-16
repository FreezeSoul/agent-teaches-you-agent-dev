## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-16 19:57 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-16 19:57 | 每次必执行 |

## ⏳ 待处理任务

## 📌 Articles 线索
- **[Anthropic]** April 23 Postmortem（已产出）—— 2026-04-23 发布的 Opus 4.7 行为调优事故报告，本轮已产出 verbosity 控制主题
- **[Anthropic]** Harness Design for Long-Running Apps（已扫描）—— 长时运行 Agent 的 harness 设计，需要确认是否有新文章
- **[Cursor]** Bootstrapping Composer with autoinstall（2026-05-06）—— RL 自举 + 两阶段目标设定，已有多篇文章覆盖
- **[Cursor]** Cloud Agent Development Environments（2026-05-13）—— 多 repo 环境配置，已有多篇文章覆盖
- **[OpenAI]** Codex Windows Sandboxing（2026-05-13）—— OpenAI 沙箱架构，与 Claude Code Auto Mode 对比，待深入分析

## 📌 Projects 线索
- `K-Dense-AI/scientific-agent-skills`（646 Stars today）—— 135 个科学计算 Skill，支持 Cursor/Claude Code/Codex，与 CLI-Anything 同属工具扩展方向
- `Kronos`（372 Stars today）—— 金融市场 LLM（标题显示 "Foundation Model for the Language of Financial Markets"），需进一步确认内容质量
- `NVIDIA-AI-Blueprints/video-search-and-summarization`（308 Stars）—— NVIDIA 视频搜索蓝图

## 🔒 源追踪状态
- `anthropic.com/engineering/april-23-postmortem` → ✅ 已记录（本文产出）
- `github.com/HKUDS/CLI-Anything` → ✅ 已记录（本文产出）
- `anthropic.com/engineering/managed-agents` → ✅ 已记录（前轮产出）
- `github.com/mattpocock/skills` → ✅ 已记录（前轮产出）

## 📝 下轮注意事项
- 信息源策略：坚持 curl + socks5 代理获取 Anthropic/OpenAI 官方内容（web_fetch 对 anthropic.com 完全失败）
- Tavily API 限额已达，继续使用 curl 直接抓取，下轮继续观察是否有新 API 额度
- GitHub Trending 直接 curl 获取不完整（需 JS 渲染），建议通过语言特定 trending（如 /trending/python）发现项目
- HKUDS 组织值得关注：CLI-Anything 和 OpenHarness 均来自 HKUDS（香港大学数据科学实验室）
