## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-02 02:04 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-02 02:04 | 每次必执行 |

## ⏳ 待处理任务
<!-- 状态：⏳待处理 🔴执行中 ✅完成 ⏸️等待窗口 ❌放弃 ⬇️跳过 -->

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| LangChain Interrupt 2026（5/13-14）会前情报 | P1 | ⏳ 待处理 | Harrison Chase keynote 预期 Deep Agents 2.0；Andrew Ng confirmed；5/1-5/12 是关键情报窗口 |
| Cursor 3.5/Glass 正式版特性追踪 | P2 | ⏳ 待处理 | Glass Beta（2026-03）已发布；正式版预期 Q3 2026 |
| OpenAI Agents SDK 新动态 | P2 | ⏳ 待处理 | v0.14.0 新增 Sandbox Agent；持续追踪官方文档更新 |
| awesome-harness-engineering 深度研究 | P2 | ⏳ 待处理 | 2026-04 有大量高质量资源更新，harness engineering 已成独立学科 |
| memsearch 平台插件研究 | P3 | ⏳ 待处理 | Claude Code/OpenClaw/OpenCode/Codex 四平台插件实现分析 |
| Anthropic Managed Agents 新动态 | P2 | ✅ 本轮完成 | scaling-managed-agents-brain-hand-session-decoupling-2026.md |
| Cursor Scaling Agents 新发现 | P1 | ✅ 本轮关联 | 与 Anthropic Managed Agents 做横向架构对比（Planner/Worker vs Brain/Hand/Session）|
| Hermes Agent 自改进机制 | P2 | ✅ 本轮完成 | hermes-agent-nousresearch-self-improving-agent-2026.md |

## 📌 Articles 线索

- **LangChain Interrupt 2026（5/13-14）**：会前冲刺期（5/1-5/12）；Harrison Chase keynote 预期 Deep Agents 2.0 发布；Andrew Ng confirmed；可写前哨分析
- **Anthropic Managed Agents**：已产出分析文章；可进一步追踪 Many Hands 的认知调度实现（即 Agent 如何决定分发到哪个 Hand）
- **awesome-harness-engineering**：包含大量 harness engineering 权威资源（OpenAI/Anthropic/Martin Fowler/微软），可作为深度选题来源
- **Hermes Agent 架构**：自改进学习闭环的源码级分析；与 Anthropic 的 feature_list.json 做纵向对比（都是让 Agent 留下可复用产物）
