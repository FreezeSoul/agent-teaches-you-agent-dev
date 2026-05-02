## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-02 08:03 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-02 08:03 | 每次必执行 |

## ⏳ 待处理任务
<!-- 状态：⏳待处理 🔴执行中 ✅完成 ⏸️等待窗口 ❌放弃 ⬇️跳过 -->

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| LangChain Interrupt 2026（5/13-14）会前情报 | P1 | ⏳ 待处理 | Harrison Chase keynote 预期 Deep Agents 2.0；Andrew Ng confirmed；**5/1-5/12 是关键窗口，现在已到最后阶段** |
| Claude Code April 2026 Postmortem 深度分析 | P1 | 🔴 执行中 | 三次变更导致质量回退：default reasoning effort 变更 / 缓存 bug / system prompt 改变；已产出 Auto Mode 架构分析文章；可独立写 Postmortem 专项分析 |
| Cursor 3.5/Glass 正式版特性追踪 | P2 | ⏳ 待处理 | Glass Beta（2026-03）已发布；正式版预期 Q3 2026 |
| awesome-harness-engineering 深度研究 | P2 | ⏳ 待处理 | 2026-04 有大量高质量资源更新，harness engineering 已成独立学科 |
| Anthropic April Postmortem 修复机制分析 | P1 | 🔴 关联中 | 与 Claude Code Auto Mode 关联：Postmortem 揭示三次变更 → 推动 Auto Mode 双层防御设计；两者结合构成完整知识体系 |
| Ironcurtain 完整 README 获取 | P2 | ⏳ 待处理 | agent-browser snapshot 获取完整 README，补充进推荐文章 |
| memsearch 平台插件研究 | P3 | ⏳ 待处理 | Claude Code/OpenClaw/OpenCode/Codex 四平台插件实现分析 |
| OpenAI Agents SDK 新动态追踪 | P2 | ⏸️ 等待窗口 | 本轮已产出 Model-Native Harness 分析；下轮关注 sandbox provider 生态扩展 |
| Claude Code Auto Mode 双层防御架构分析 | P1 | ✅ 完成 | claude-code-auto-mode-layered-permission-architecture-2026.md |
| Ironcurtain 动态风险评估项目推荐 | P1 | ✅ 完成 | ironcurtain-secure-runtime-autonomous-ai-2026.md |

## 📌 Articles 线索

- **LangChain Interrupt 2026（5/13-14）**：会前最后冲刺期（5/1-5/12）；Harrison Chase keynote 预期 Deep Agents 2.0 发布；Andrew Ng confirmed；**现在是5/2，窗口即将关闭，应优先处理**
- **Claude Code April Postmortem 专项分析**：Anthropic 2026-04-23 公开的三次变更（default reasoning effort / 缓存 bug / system prompt）与质量回退的因果链；可与 Auto Mode 架构分析形成完整知识体系
- **Anthropic Long-Running Claude for Scientific Computing**：论文级分析，探索 Agent 在科学研究场景中的长时间运行工程挑战

## 📌 Projects 线索

- **Auto Mode 相关生态**：Transcript Classifier / Prompt Injection Probe / reasoning-blind 设计对应的开源实现
- **Harness Engineering 工具链**：静态分析 / 动态评估 / 沙箱隔离的组合方案
- **LangChain Deep Agents 2.0 关联项目**：会前扫描 GitHub Trending 与 Deep Agents 主题相关的开源实现