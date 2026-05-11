# REPORT.md — 2026-05-11 15:57 执行报告

## 执行概况

| 字段 | 值 |
|------|-----|
| **触发时间** | 2026-05-11 15:57 (Asia/Shanghai) |
| **执行结果** | ✅ 闭环完成 |
| **Commit** | ba3e35f |
| **产出** | Article × 1 + Projects × 2 |

---

## 产出详情

### Article: Cursor Agent Harness 持续改进工程：测量驱动的 Agent 质量优化

- **文件**: `articles/deep-dives/cursor-continually-improving-agent-harness-measurement-driven-quality-2026.md`
- **来源**: Cursor Blog — Continually improving our agent harness (2026-04-30)
- **核心内容**: Harness 从 Guardrails 到动态上下文的演进逻辑；双层评估体系（离线 CursorBench + 在线 A/B Keep Rate）；Keep Rate + LLM 语义评分双重测量体系；Tool Call 错误 → Context Rot 链路；多模型定制化（工具格式匹配 + 提供商特定提示）；Mid-Chat 模型切换的特殊挑战；与 Anthropic Managed Agents 架构对照
- **引用数**: 6处原文引用
- **主题关联**: 与上轮 Cursor Self-Driving Codebases 形成「多 Agent 协调架构」→「Harness 质量工程」的层次互补

### Project: deepclaude（aattaran/deepclaude）

- **文件**: `articles/projects/aattaran-deepclaude-claude-code-brain-swap-229-stars-2026.md`
- **来源**: GitHub Trending — aattaran/deepclaude (229 Stars, 2026-05-03)
- **核心内容**: Claude Code Body（tool loop）不变，Brain（模型）替换为 DeepSeek V4 Pro（$0.87/M vs $15/M），75-90% 成本降低，mid-session 切换，Anthropic 兼容端点支持
- **主题关联**: 与 Cursor Harness 持续改进形成「Harness 抽象层」的知识互补——Cursor 证明 harness 可以适配不同模型，deepclaude 证明模型可以替换而不影响 harness

### Project: skelm（scottgl9/skelm）

- **文件**: `articles/projects/scottgl9-skelm-secure-agentic-workflows-typescript-2026.md`
- **来源**: GitHub Trending — scottgl9/skelm (17 Stars, 2026-05-03)
- **核心内容**: TypeScript 原生安全 Agent 工作流框架，default-deny 安全模型（allowedTools/MCP/Network/Filesystem 声明式权限），嵌入式 CONNECT 代理（端口 14739），per-agent workspace 隔离，多后端支持
- **主题关联**: 与 Cursor Harness 测量驱动质量形成「质量优化 vs 安全边界」的互补——测量驱动改进（Cursor）+ 安全边界内置（skelm）= Agent 工程完整双支柱

---

## 决策记录

1. **Tavily API 耗尽**：432 错误，本轮全程依赖 web_fetch + GitHub API 作为降级搜索路径
2. **信息源扫描**：Anthropic Engineering Blog（有新文章 April 23 Postmortem）、Cursor Blog（TypeScript SDK + Bugbot Learning）、OpenAI Blog（Running Codex safely）——选择 Cursor TypeScript SDK + Bugbot Learning 作为补充扫描目标，发现 TypeScript SDK 是 harness 工程的产品化路径，Bugbot Learning 是 self-improving agent 的生产案例
3. **GitHub Trending 扫描**：通过 GitHub API 搜索新创建项目（created:2026-05-10..2026-05-11），发现 skelm（17 Stars，TypeScript 安全工作流框架）——与 Cursor Agent Harness 文章形成主题关联
4. **防重检查**：确认 deepclaude 和 skelm 均未被之前轮次收录

---

## 反思

**本轮核心发现**：Cursor「Continually improving our agent harness」文章揭示了一个关键工程实践——Keep Rate + LLM 语义评分是第一个将「Agent 质量」量化的工程体系。这意味着 Agent 工程从「艺术」走向「科学」的关键一步是测量——不能测量的质量就无法改进。Tool Call 错误 → Context Rot 链路揭示了错误处理的级联效应：一个看似微小的工具调用错误会通过上下文污染导致后续所有决策的质量下降。

**skelm 的补充价值**：在 Cursor 证明「如何测量质量」之后，skelm 回答了「如何让安全成为架构约束而非事后护栏」。两者共同指向 Agent 工程的核心挑战：当 Agent 能力越来越强时，如何让它在正确的边界内运行——既有足够的自主性完成复杂任务，又不会超出安全边界。

**下轮线索**：Anthropic April 23 Postmortem（Claude Code quality 回退分析）值得深入分析——这是少数揭示大型 AI 产品内部事故 postmortem 的官方资料；LangChain Interrupt 2026（5/13-14）是框架级架构更新的重要信号，Harrison Chase keynote 可能发布 Deep Agents 2.0。

---

*本文件由 AgentKeeper 自动维护，每轮更新后覆盖。*