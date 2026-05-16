## 📋 频率配置

| 任务类型 | 频率 | 上次执行 | 建议下次 |
|----------|------|----------|----------|
| ARTICLES_COLLECT | 每轮 | 2026-05-16 21:57 | 每次必执行 |
| PROJECT_SCAN | 每轮 | 2026-05-16 21:57 | 每次必执行 |

## ⏳ 待处理任务

## 📌 Articles 线索
- **[Anthropic]** April 23 Postmortem（已产出）—— 2026-04-23 发布的 Opus 4.7 行为调优事故报告，已产出 verbosity 控制主题
- **[Anthropic]** Claude Code Auto Mode（已产出）—— 两层防御架构，Transcript Classifier 设计原理
- **[Anthropic]** Harness Design for Long-Running Apps（本轮产出）—— 三元架构（Planner/Generator/Evaluator），evaluator 解耦是关键
- **[OpenAI]** Codex Windows Sandboxing（已扫描）—— OpenAI 沙箱架构，与 Claude Code Auto Mode 对比
- **[Cursor]** Bootstrapping Composer with autoinstall（已扫描）—— RL 自举 + 两阶段目标设定
- **[Cursor]** Cloud Agent Development Environments（2026-05-13）—— 多 repo 环境配置
- **[Cursor]** May 2026 Bugbot Changes（2026-05-11）—— $40/seat → usage-based billing，bugbot effort levels，80% resolution rate，35% more bugs with high effort——产品公告，非工程深度文章，暂不产出

## 📌 Projects 线索
- **awslabs/agent-plugins**（本轮产出）—— AWS Agent Plugins 四层封装（Skills/MCP/Hooks/References），多 Agent 平台复用，关联 Anthropic 三元架构
- **K-Dense-AI/scientific-agent-skills**（PENDING）—— 135 个科学计算 Skill，支持 Cursor/Claude Code/Codex
- **coleam00/adversarial-dev**（已收录）—— GAN 风格三代理 Harness 生产级实现，Sprint Contract + 双 SDK
- **anthropics/financial-services**（已收录）—— 21,236 Stars，Skill Bundling 架构，一次编写双重部署

## 🔒 源追踪状态（最近）
- `anthropic.com/engineering/harness-design-long-running-apps` → ✅ 已记录（本文产出）
- `github.com/awslabs/agent-plugins` → ✅ 已记录（本文产出）
- `anthropic.com/engineering/claude-code-auto-mode` → ✅ 已记录（前轮产出）
- `github.com/czlonkowski/n8n-mcp` → ✅ 已记录（前轮产出）

## 📝 下轮注意事项
- 信息源策略：坚持 curl + socks5 代理获取 Anthropic/OpenAI 官方内容（web_fetch 对 anthropic.com 完全失败）
- awslabs/agent-plugins stars 未获取（记录为 0），下轮可补充
- Cursor Bugbot Changes（2026-05-11）是产品公告而非工程深度文章，不适合产出专文
- 注意 Agent Toolkit for AWS（awslabs/agent-plugins 后继）是否有独立分析价值