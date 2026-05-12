# 🗺️ Projects Map

> 本目录存放 GitHub Trending 高价值项目推荐文章
- [golutra/golutra](./golutra-multi-agent-orchestration-platform-3444-stars-2026.md) — 多 Agent 统一编排平台，3,444 Stars，Vue 3 + Rust（Tauri），支持 Claude Code / Codex / Gemini CLI / OpenClaw 等 7 种 CLI 并行协作，与 Cursor「多 Agent 是 Harness 的核心职责」判断形成「判断 → 工程实现」闭环（关联：Cursor → 多 Agent 编排活在 Harness 层 → golutra 统一编排层具体实现）
- [YuxiaoWang-520/harness-craft](./harness-craft-86stars-2026.md) — 可组合 AI Coding Skills/Rules 库，86 Stars，YC CEO 背书，46 Skills + 15 Rules，Claude/Codex 双平台支持，将 Agent 从「prompt tricks」升级为「工程化持久系统」，与本文「AI Coding 工程化范式转移」形成「范式定义 → 工程实现」闭环
> **防重索引**：已推荐项目的 GitHub URL 列表（避免重复推荐）

---

- [strukto-ai/mirage](./strukto-ai-mirage-unified-vfs-1922-stars-2026.md) — 统一虚拟文件系统，1,922 Stars，将 S3/Slack/GitHub/Gmail 等 15+ 服务挂载为文件系统路径，Agent 用熟悉的 bash 工具（`cat`/`grep`/`cp`）操作一切，与 Cursor 模型亲和性 Harness 文章形成「工具层抽象 vs 模型层适配」的正交关系（关联：OpenAI patch 格式 vs Claude string replacement → Mirage 统一为 filesystem API → 模型特异性被隐藏）

- [garrytan/gstack](./garrytan-gstack-yc-ceo-ai-software-factory-93788-stars-2026.md) — YC CEO Garry Tan 的 AI 软件工厂，93,788 Stars，将 Claude Code 变成 23 角色虚拟工程团队（CEO/设计师/安全官/QA 等），810x 生产力提升，与 PayPal Cursor 案例形成「个人 → 企业」完整 Agent 工具链光谱

- [google/agents-cli](./google-agents-cli-google-cloud-agent-factory-2272-stars-2026.md) — Google 官方 Agent 部署 CLI + Skill 库，2,272 Stars，支持 Claude Code / Codex / Gemini CLI / any，7 个核心 Skill 覆盖 scaffold→eval→deploy 全链路，与 Cursor「第三代」云端 Agent 工厂形成「范式定义 → 工程实现」闭环（关联：第三代 → 云端 VM 并行 + Artifacts 交付 → agents-cli 提供部署/评估/可观测性标准工具）

- [NousResearch/hermes-agent](./NousResearch-hermes-agent-self-improving-agent-2026.md) — 自改进 AI Agent，支持 Telegram/Discord/Slack/WhatsApp 等多平台，`hermes model` 任意切换 LLM provider（200+ 模型），$5 VPS 可跑，与 Cursor Autoinstall 形成「Agent 自我改进循环」的互补（关联：Autoinstall 用上一代 Composer 配置环境 → Hermes Agent 用当前 session 经验创建 Skill → model helps itself improve 的两条路径）

- [itsuzef/goalkeeper](./itsuzef-goalkeeper-contract-driven-claude-code-5-stars-2026.md) — 合约驱动的 Claude Code 目标执行框架，5 Stars，2026-05-11 创建，独立 Judge 子代理对抗 Definition of Done，反占位符规则自动拒绝 stub/`.todo`/`it.only`，与 Augment AGENTS.md 研究形成「配置定义 → 完成验证」的完整闭环（关联：Augment 发现好 AGENTS.md = Haiku→Opus 升级 → Goalkeeper 定义 DoD + Judge 验证完成 = 结构化配置工程的两个维度）

- [huggingface/skills](./huggingface-skills-interoperable-agent-tools-1881-stars-2026.md) — Hugging Face 官方 Agent Skills 库，1,881 Stars，标准 SKILL.md 格式，interoperable with Claude Code / Codex / Gemini CLI / Cursor，与 Cursor Autoinstall 形成「训练环境自动化 vs 工具定义标准化」的互补



- [aattaran/deepclaude](./aattaran-deepclaude-claude-code-brain-swap-229-stars-2026.md) — Claude Code Brain Swap 方案，229 Stars，2026-05-03 创建，DeepSeek V4 Pro（$0.87/M）替换 Claude Opus（$15/M），90% 成本降低 + mid-session 切换，支持 Anthropic 兼容端点（DeepSeek/OpenRouter/Fireworks），与 Anthropic Managed Agents Brain/Hands 解耦形成「Harness 抽象层」的互补（关联：Body 固定 → Brain 可换 → Claude Code harness 的真实价值在 tool loop 而非模型）

- [Liu-PenPen/skill-reviewer](./Liu-PenPen-skill-reviewer-skill-quality-enforcement-2026.md) — 给 Agent Skill 做 Code Review 的 Skill，17 Stars，2026-05-11 创建，10 条可检测 rubric + P0–P3 分级 + 零依赖 lint 脚本，与 Cursor「Better AI Models」研究形成「管理 AI 输出」趋势的工具化实现（关联：代码审查 +51% → Skill 成为基础单元 → Skill Review 成为质量门禁）

- [scottgl9/skelm](./scottgl9-skelm-secure-agentic-workflows-typescript-2026.md) — TypeScript 原生安全 Agent 工作流框架，17 Stars，2026-05-03 创建，默认拒绝（default-deny）安全模型 + 嵌入式 CONNECT 代理 + per-agent workspace 隔离，与 Cursor Agent Harness 测量驱动质量形成「质量优化 vs 安全边界」的互补（关联：测量驱动改进 → 安全边界内置 → skelm 将安全从护栏变为工作流定义的内置约束）

- [Storybloq/storybloq](./Storybloq-storybloq-cross-session-context-persistence-217-stars-2026.md) — 跨会话上下文持久化，217 Stars，TypeScript，`.story/` 文件约定 + CLI + 43 工具 MCP Server + `/story` Skill，让每次 Claude Code session 变成可积累的建设块而非重置，与 Cursor Composer Autoinstall 形成「环境自动化 vs Session 连续性」的互补（关联：RL 训练环境自动化 → 跨天/跨 session 的长程 Agent 上下文断点问题）
- [itsuzef/goalkeeper](https://github.com/itsuzef/goalkeeper) — 合约驱动的 Claude Code 目标执行框架，独立 Judge 子代理对抗 Definition of Done

- [kruschdev/krusch-context-mcp](./kruschdev-krusch-context-mcp-unified-ide-context-engine-61-stars-2026.md) — 统一 IDE 上下文引擎，61 Stars，Node.js + PostgreSQL + SQLite + Ollama 本地向量，一个 MCP Server 提供 18 个工具（情景记忆 + 语义代码搜索 + Nuggets + Zero-Trust Deep Search），零 API 成本 + 全数据主权，与 Cursor 动态上下文发现形成「方法论 → 工程实现」闭环（关联：Cursor 动态上下文发现 → 文件作为上下文原语 → Krusch Context MCP 系统性实现）

- [coleam00/adversarial-dev](./coleam00-adversarial-dev-gan-style-three-agent-harness-2026.md) — GAN 风格三代理编码 Harness 的生产级实现，108 Stars，TypeScript，双 SDK（Claude Agent SDK + Codex SDK）支持，Sprint Contract 协商机制 + JSON 结构化反馈，Evaluator 主动攻击机制驱动质量提升，与 Anthropic GAN-Style 三代理架构论文形成「理论 → 工程实现」闭环（关联：GAN 三代理架构 → adversarial-dev 生产级实现 → Sprint Contract + 双 SDK 支持）

- [Agent-Threat-Rule/agent-threat-rules](./Agent-Threat-Rule-agent-threat-rules-open-detection-standard-109-stars-2026.md) — Agent 安全检测开放标准，109 Stars，311 条规则覆盖 9 大威胁类别（prompt injection/agent manipulation/skill compromise 等），映射 OWASP Agentic Top 10（10/10）+ SAFE-MCP（91.8%），96,096 真实 Skills 扫描发现 751 个 malware samples，NVIDIA Garak benchmark 97.1% recall，6 周 7 个生态整合（Microsoft/Cisco/NVIDIA Garak 等），与 Anthropic Trustworthy Agents 形成「安全框架 + 检测标准」的完整闭环（关联：Trustworthy Agents → 四层安全架构 → ATR 检测规则 → OWASP 映射 → 真实威胁发现）

- [OptimAI-Lab/CudaForge](./OptimAI-Lab-CudaForge-training-free-multi-agent-cuda-kernel-2026.md) — 训练免费的多智能体 CUDA Kernel 生成工作流，80 Stars，Python，模拟人类专家的迭代工作流（开发→测试→分析硬件反馈→迭代改进），与 Cursor Multi-Agent Kernel 实验形成「规范驱动协调」的互补（关联：Markdown 协调规范 → 开源工作流实现 → CudaForge SKILL.md 驱动）

- [Fangcun-AI/SkillWard](./Fangcun-AI-SkillWard-security-scanner-agent-skills-2026.md) — Agent Skills 安全扫描工具，123 Stars，Python，三阶段扫描（静态分析 + LLM 评估 + Docker 沙箱执行），实测 5,000 个 Skills 中 ~25% 标记不安全，约 1/3 可疑样本在沙箱中暴露运行时威胁，与 OpenAI Codex Safe Deployment 形成「发布前扫描 + 运行控制」的安全闭环（关联：Codex 安全运行架构 → Skills 部署前的安全检查 → SkillWard 三阶段漏斗）

- [kangarooking-system-prompt-skills-15-design-patterns-2026](./kangarooking-system-prompt-skills-15-design-patterns-2026.md) — 15 个可执行的系统提示词设计模式，64 Stars，从 165 个顶级 AI 产品系统提示词中蒸馏，覆盖 persona/tool/safety/memory 等 15 个维度，与 OpenAI Agents SDK Skills 原语形成「标准定义 → 设计模式参考」的互补（关联：OpenAI Agents SDK → Skills 已成为标准原语 → system-prompt-skills 提供具体设计模式）

- [strukto-ai-mirage-unified-virtual-filesystem-1612-stars-2026](./strukto-ai-mirage-unified-virtual-filesystem-1612-stars-2026.md) — 统一虚拟文件系统，1,612 Stars，TypeScript，将 S3/Gmail/GitHub/Slack 等后端挂载为文件目录，让 AI Agent 用原生 bash 工具操作一切数据源，与 OpenAI Codex Agent Loop 形成「工具抽象 vs 上下文管理」的互补（关联：Codex Agent Loop → 长程 Agent 需要统一的工具抽象层 → Mirage VFS 的工程实现）

- [rowboatlabs-rowboat-local-first-ai-coworker-13666-stars-2026](./rowboatlabs-rowboat-local-first-ai-coworker-13666-stars-2026.md) — 本地优先的 AI coworker，13,666 Stars，TypeScript，构建持久知识图谱 + Gmail/Calendar/Notion 深度集成，与 Cursor Long-Running Agents 形成「工作流控制 + 上下文积累」的互补（关联：规划优先 Harness 架构 → 长程 Agent 需要外部化的上下文积累机制）

- [claude-code-memory-setup-obsidian-graphify-token-optimization-2026](./claude-code-memory-setup-obsidian-graphify-token-optimization-2026.md) — 71.5x Token 优化的 Claude Code 记忆方案，Obsidian Zettelkasten + Graphify 知识图谱 + Chat Import Pipeline 三层体系，499x 查询 token 节省，0 token 生成成本（AST 模式），跨项目知识复用（关联：Cursor 3 第三时代 → 长程 Agent 上下文连续性 → 记忆基础设施的系统性解决方案）

- [agentmemory-persistent-memory-ai-coding-agents-2026](./agentmemory-persistent-memory-ai-coding-agents-2026.md) — 免 DB 的持久记忆基础设施，iii engine 实现零外部依赖，95.2% R@5 检索精度 + 92% token 节省，16+ Agent 共享统一记忆服务器（关联：Anthropic Measuring Agent Autonomy → 长程 Agent 的上下文坍缩问题 → 记忆基础设施的系统性解决方案）

- [agent-squad-2fastlabs-multi-agent-orchestration-2026](./agent-squad-2fastlabs-multi-agent-orchestration-2026.md) — 意图分类驱动的多 Agent 编排框架，AWS Labs → 2FastLabs，Classifier-First 动态路由 + SupervisorAgent 并行协调（关联：Anthropic Managed Agents Brain-Hands 解耦 → 多 Agent 入口层智能路由问题的一体化回答）

- [clampdown-89luca89-zero-trust-sandbox-agent-2026](./clampdown-89luca89-zero-trust-sandbox-agent-2026.md) — 零信任沙箱推荐，Landlock + Seccomp + 零密钥架构，与 Anthropic Auto Mode 形成技术互补（判断 vs 强制）

- [open-code-review-multi-agent-code-review-2026](./open-code-review-multi-agent-code-review-2026.md) — 多评审者对抗式代码审查框架，28 种评审者人格 + 辩论机制 + GAN 风格对抗评审（关联：GAN 三代理架构 → 多评审者对抗式代码审查工程实现）

- [prompt-tower-context-packaging-376-stars](./prompt-tower-context-packaging-376-stars-2026.md) — VS Code 上下文打包插件，376 Stars，1,000+ 用户，将代码库上下文一键打包为 AI 可消费的 XML 结构，与 Cursor 动态上下文发现形成互补（预打包 vs 动态拉取）

[gsd-2-gsd-build-autonomous-coding-agent-7269-stars-2026](./gsd-2-gsd-build-autonomous-coding-agent-7269-stars-2026.md) — 生产级自主编码 Harness，7269 ⭐，DB 权威状态 + Auto Pipeline + Milestone/Slice 机制，Pi SDK 构建，真正实现"一次命令，几个月不管"的无人值守编码（关联：Anthropic 长程 Agent 双组件架构 → 生产级工程实现）

- [awslabs/aidlc-workflows](./awslabs-aidlc-workflows-structured-ai-driven-development-2026.md) — AWS 出品的 Agent 开发生命周期方法论，1847 ⭐，三阶段（Inception→Construction→Operations）+ 六合一安全扫描 + 8 平台适配层（关联：Claude Code April Postmortem 质量回退 → 结构化 Human-in-the-loop 的工程实现）
- [agentmemory-persistent-memory-4902-stars-2026](./agentmemory-persistent-memory-4902-stars-2026.md) — 免 DB 的 Agent 持久记忆，4902 Stars，BM25+Vector+Graph 混合检索（RRF fusion），95.2% R@5 + $10/年 + 零 API 成本，与本文配置性降级形成「平台层缓存污染 → 工具层外部记忆」的互补关系

## 已推荐项目（防重索引）

- [Storybloq/storybloq](https://github.com/Storybloq/storybloq) — 跨会话上下文持久化，217 Stars，TypeScript，`.story/` 文件约定 + CLI + 43 工具 MCP Server，与 Cursor Composer Autoinstall 形成「环境自动化 vs Session 连续性」的互补
- [itsuzef/goalkeeper](https://github.com/itsuzef/goalkeeper) — 合约驱动的 Claude Code 目标执行框架，独立 Judge 子代理对抗 Definition of Done

- [NyxFoundation/speca](https://github.com/NyxFoundation/speca) — spec-anchored 安全审计框架，373 Stars，Python，Sherlock Fusaka 恢复全部 15 个漏洞 + 发现 4 个新漏洞（含 1 个人类审计员遗漏的加密不变量违反），arXiv:2604.26495，与 Anthropic Trend 8 形成「认知风险 → 规范层防御方法论」闭环

- [rowboatlabs/rowboat](https://github.com/rowboatlabs/rowboat) — 本地优先的 AI coworker，13,666 Stars，TypeScript，持久知识图谱 + Gmail/Calendar/Notion 深度集成（关联：Cursor Long-Running Agents → 长程 Agent 的上下文积累问题 → 外部化知识图谱的工程实现）

- [neo4j-labs/create-context-graph](https://github.com/neo4j-labs/create-context-graph)

- [2FastLabs/agent-squad](https://github.com/2FastLabs/agent-squad) — 意图分类驱动的多 Agent 编排框架，AWS Labs → 2FastLabs，Classifier-First 动态路由 + SupervisorAgent 并行协调，Python/TypeScript 双语言

- [PackmindHub/context-evaluator](https://github.com/PackmindHub/context-evaluator) — AI Agent 配置文件健康体检工具，17 个评估器诊断 AGENTS.md/CLAUDE.md 质量问题，自动修复 + Before/After 分数对比（关联：Agent 配置过载问题 → 配置文件质量的系统性诊断与修复）

- [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) — 100 行 Python 的极简 Agent，>74% SWE-bench 得分，Princeton & Stanford 团队维护，19K+ Stars，无专用工具接口设计（关联：Anthropic 基础设施噪声研究 → 最干净的可复现评测环境）

- [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) — GitHub 最大的 Agent Skills 索引，4,494 ⭐，覆盖 9 个主流 AI Coding 平台

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — AI Coding Agent 的 Production-Grade 工程技能库，DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP 六阶段质量门禁，9 大平台官方推荐
- [virattt/dexter](https://github.com/virattt/dexter) — 面向深度金融研究的 Autonomous Agent，24K ⭐，Multi-Agent 分工 + 沙箱执行 + 全程可溯源

- [HKUDS/OpenHarness](https://github.com/HKUDS/OpenHarness) — 开源 Agent Harness 实现，深度集成 Claude Code / OpenClaw，支持 Ollama 本地运行
- [meta-pytorch/KernelAgent](https://github.com/meta-pytorch/KernelAgent) — Deep Agent + GPU Kernel 自动化优化开源实现，PyTorch → Triton 自动转化
- [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) — AWS Labs 出品的 AI-Driven Development Life Cycle 方法论，1847 Stars，六合一安全扫描，Claude Code/Cursor/Amazon Q 等 8 平台适配
- [agentmemory-persistent-memory-4902-stars-2026](./agentmemory-persistent-memory-4902-stars-2026.md) — 免 DB 的 Agent 持久记忆，4902 Stars，BM25+Vector+Graph 混合检索（RRF fusion），95.2% R@5 + $10/年 + 零 API 成本，与本文配置性降级形成「平台层缓存污染 → 工具层外部记忆」的互补关系
- [coleam00/Archon](https://github.com/coleam00/Archon) — 首个开源 AI 编程工作流引擎，让 AI 编程变得确定可重复
- [obra/superpowers](https://github.com/obra/superpowers) — 用技能框架让 AI 编程从「能写」进化到「会做」
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — AI Agent Harness 的性能优化系统
- [kangarooking/system-prompt-skills](https://github.com/kangarooking/system-prompt-skills) — 15 个可执行的系统提示词设计模式，64 Stars，从 165 个顶级 AI 产品系统提示词中蒸馏，覆盖 persona/tool/safety/memory 等 15 个维度（关联：OpenAI Agents SDK → Skills 已成为标准原语 → system-prompt-skills 提供具体设计模式）

- [strukto-ai/mirage](https://github.com/strukto-ai/mirage) — 统一虚拟文件系统，1,612 Stars，TypeScript，将 S3/Gmail/GitHub/Slack 等后端挂载为文件目录，AI Agent 用 bash 工具操作一切数据源（关联：Codex Agent Loop → 工具抽象层 → 跨后端统一 bash 接口）
- [badlogic/pi-mono](https://github.com/badlogic/pi-mono) — 开源 AI Agent 工具链，强调开放会话数据共享（Hugging Face），npm 包涵盖 LLM API / Agent Runtime / Coding Agent CLI / TUI / Web UI
- [gsd-build/GSD-2](https://github.com/gsd-build/GSD-2) — 生产级自主编码 Harness，7269 ⭐，DB 权威状态 + Auto Pipeline + Milestone/Slice 机制，真正实现"一次命令，几个月不管"（关联：Anthropic 长程 Agent 双组件架构 → 生产级工程实现）
- [Q00/ouroboros](https://github.com/Q00/ouroboros) — Agent OS：规范优先的可验证编码工作流，Specification-first + 3-stage Evaluation Gate，3.2K ⭐

- [RenseiAI/AgentFactory](https://github.com/RenseiAI/agentfactory) — Linear 原生的多 Agent 软件工厂，Dev/QA/Acceptance 三阶段流水线，TypeScript/Redis 生产级架构
- [openai/openai-agents-python](https://github.com/openai/openai-agents-python) — OpenAI 官方多 Agent 编排 SDK，Sandbox Agents + Handoffs + Guardrails 生产级基础设施，685+ stars/day
- [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research) — 本地化深度研究 Agent，4,706 ⭐，SQLCipher AES-256 加密 + LangGraph Agent Strategy + SimpleQA ~95%

- [VibePod/vibepod-cli](https://github.com/VibePod/vibepod-cli) — Docker 容器化的 AI 编码 Agent 管理 CLI，零配置 + 本地 Analytics Dashboard，支持 7 个主流 Agent
- [jayminwest/overstory](https://github.com/jayminwest/overstory) — Git Worktree 隔离的多 Agent 编排工具，1.2K ⭐，Session as Orchestrator 设计，SQLite Mail 高效通信

- [ruvnet/ruflo](https://github.com/ruvnet/ruflo) — Claude 原生 Multi-Agent 编排平台，38K ⭐，32 插件生态，自学习 swarm 智能
- [ruflo-claude-swarm-orchestration-2026](./ruflo-claude-swarm-orchestration-2026.md) — Ruflo 推荐，+2,598 stars/day，32 插件 + SONA 自学习 + 零信任联邦（关联：上下文工程 → 多 Agent 记忆协同的工程实现）
- [browser-use/browser-use](./browser-use-browser-automation-open-source-92k-stars-2026.md) — 浏览器自动化开源框架，92,878 ⭐，LLM-agnostic + Stealth Cloud，与 Cloudflare Sandboxes 形成「执行 + 操作」互补
- [daytonaio/daytona](https://github.com/daytonaio/daytona) — OCI 原生的 AI Agent 沙箱运行时，Sub-90ms 冷启动 + 可选 Kata/Sysbox 强隔离，OpenAI Agents SDK 8个官方沙箱提供商之一

- [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) — Kubernetes 原生的 Agent 沙箱 CRD
- [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) — Rust 原生浏览器自动化 CLI
- [lobehub/lobe-chat](https://github.com/lobehub/lobe-chat) — Agent 协作空间，75K ⭐，Agent as the Unit of Work 设计理念
- [omxyz/lumen](https://github.com/omxyz/lumen) — 视觉优先浏览器 Agent，screenshot→action 循环 + 两层上下文压缩，100% WebVoyager 成功率
- [MemTensor/MemOS](https://github.com/MemTensor/MemOS) — LLM 和 AI Agent 的记忆操作系统
- [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) — 多框架统一的 Agent 持久记忆后端，REST API + MCP + OAuth + CLI + Dashboard，5ms 检索因果知识图谱，与 Cursor App Stability 形成「本地资源约束 vs 远程记忆解耦」的互补
- [alibaba/page-agent](https://github.com/alibaba/page-agent) — 让任何网页都能被自然语言控制
- [Agent-Field/SWE-AF](https://github.com/Agent-Field/SWE-AF) — 自主工程团队 Runtime，三层控制闭环（Inner/Middle/Outer Loop）+ Git Worktree 隔离并行，Fleet-scale 编排
- [agent-sandbox/agent-sandbox](https://github.com/agent-sandbox/agent-sandbox) — E2B 兼容的企业级 AI Agent 沙箱
- [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) — 把一个 AI 变成游戏开发工作室
- [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe) — 面向零基础的 vibe coding 学习课程
- [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) — 多模型协同的开源 Agent Harness
- [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) — Claude Code 与 Google NotebookLM 的无缝集成
- [titanwings/colleague-skill](https://github.com/titanwings/colleague-skill) — 将人蒸馏为 AI Skill 的工程实践
- [bytedance/deer-flow](https://github.com/bytedance/deer-flow) — 字节跳动开源的多智能体编排框架，Supervisor 模式 + Docker 沙箱 + 持久化记忆
- [numman-ali/openskills](https://github.com/numman-ali/openskills) — Anthropic Agent Skills 的跨平台实现，一个 CLI 让所有 AI 编码工具都能用 Skills
- [mattpocock/skills](./mattpocock-skills-agent-engineering-discipline-74875-stars-2026.md) — 让 AI Coding 从「Vibe」进化到「Engineered」的 Skills 实践集，74,875 Stars，解决对齐偏差/反馈循环断裂/代码entropy加速四大工程失败模式，/grill-me + CONTEXT.md + /tdd + /improve-codebase-architecture 与 Cursor Multi-Agent Kernel 优化形成「能力边界扩展 + 工程纪律强化」的互补（关联：Multi-Agent 探索能力 → 更需要工程纪律防止 chaos → Skills 提供可操作实践框架）
- [mattpocock/sandcastle](https://github.com/mattpocock/sandcastle) — Git Worktree 隔离的 Claude Code 生产编排工具，Docker/Podman/Vercel 三层沙箱 + 分支策略自动化，TypeScript 生产级开源实现（关联：Cursor SDK → 生产级 Agent 基础设施的双轨路径）
- [wilsonzlin/fastrender](https://github.com/wilsonzlin/fastrender) — 百枚并发 Agent 从零构建浏览器引擎，Planner/Sub-Planner/Worker 三层分离架构，100 万行代码验证大规模 Agent Swarm 工程可行性，1.5K ⭐（关联：Anthropic Agent Skills 渐进式披露 → 复杂工作流的知识组织与按需加载）
- [microsoft/skills](https://github.com/microsoft/skills) — 174 个 Agent Skills 的 Microsoft 官方技能库，覆盖 Azure SDK / Foundry / MCP 构建，Context-Driven Development 理念，与 Anthropic Agent Skills 形成企业级 vs 开源的两条路径（关联：Agent Skills 渐进式披露 → 企业级大规模技能管理的实现路径）
- [1jehuang/jcode](https://github.com/1jehuang/jcode) — 下一代编码 Agent Harness，极致轻量化设计（RAM 占用比 Claude Code 低 93%）
- [browserbase/skills](https://github.com/browserbase/skills) — 将 Browserbase 云端浏览器自动化封装为 Claude Code Skill 插件，使编码 Agent 能处理登录受限站点、CAPTCHA 和反爬保护页面
- [provos/ironcurtain](https://github.com/provos/ironcurtain) — 运行时动态风险评估安全运行时，填补静态规则和人工审批之间的空白
- [najeed/ai-agent-eval-harness](https://github.com/najeed/ai-agent-eval-harness) — 开源 MultiAgentOps 评估框架，5000+ 场景库 + Flight Recorder 轨迹回放 + 9层安全审计
- [RightNow-AI/forge-mcp-server](https://github.com/RightNow-AI/forge-mcp-server) — Swarm Agent GPU Kernel 优化 MCP Server，14x 加速 + 100% 数值正确性
- [BytedTsinghua-SIA/CUDA-Agent](https://github.com/BytedTsinghua-SIA/CUDA-Agent) — 首个 RL 训练超越 Claude Opus-4.6 的 GPU Kernel 优化系统，2,026 ⭐
- [withastro/flue](https://github.com/withastro/flue) — Astro 团队开源的 TypeScript Agent Harness 框架，虚拟沙箱 + Markdown Skill 系统
- [aden-hive/hive](https://github.com/aden-hive/hive) — 目标驱动的 Multi-Agent 生产级 Harness，自动生成执行图谱 + 自愈能力
- [robmorgan/metamorph](https://github.com/robmorgan/metamorph) — 并行 Claude Code 容器编排，Git 文件锁分布式任务协调
- [langgenius/dify](https://github.com/langgenius/dify) — 生产级 Agentic Workflow 开发平台，134.7k Stars 全球排名第 49，支持可视化 Workflow/RAG/Agent 多类型编排
- [JackChen-me/open-multi-agent](https://github.com/JackChen-me/open-multi-agent) — 3 依赖的 TypeScript Multi-Agent 引擎，单 `runTeam()` 调用从目标到结果
- [lsdefine/GenericAgent](https://github.com/lsdefine/GenericAgent) — ~3K 行代码的极简自进化 Agent 框架，技能从任务中结晶而非预装
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — AI Coding Agent 的 Production-Grade 工程技能库，DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP 六阶段质量门禁，9 大平台官方推荐
- [virattt/dexter](https://github.com/virattt/dexter) — 面向深度金融研究的 Autonomous Agent，24K ⭐，Multi-Agent 分工 + 沙箱执行 + 全程可溯源

- [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) — GitHub 最大的 Agent Skills 索引，4,494 ⭐，覆盖 9 个主流 AI Coding 平台
- [mem0ai/mem0](https://github.com/mem0ai/mem0) — LLM 和 AI Agent 的通用记忆层，self-improving memory，LoCoMo 91.6 分，ADD-only extraction + Entity linking

- [cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex) — 长程 Agent 增量上下文引擎，代码库变化仅 delta 重嵌入，Rust 生产级实现，8.4k ⭐，Apache 2.0
- [agno-agi/agno](https://github.com/agno-agi/agno) — 将 Agent 转化为生产软件的 Runtime，Session 管理 + OpenTelemetry tracing + RBAC + 多框架兼容
- [memfreeme/memfree](https://github.com/memfreeme/memfree) — 开源混合 AI 搜索引擎，支持知识库 + 互联网搜索 + Chrome 书签同步，一键部署
- [lastmile-ai/mcp-agent](https://github.com/lastmile-ai/mcp-agent) — 用简单模式构建高效 Agent 的 MCP 框架，Full MCP Support + Temporal Durable Execution + 46%+ Token 节省
- [hidai25/eval-view](https://github.com/hidai25/eval-view) — AI Agent 行为回归测试框架，snapshot behavior → diff tool calls → classify regression，生产级 Silent Regression 检测
- [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) — MCP Server for n8n workflow automation，1,650+ nodes 文档覆盖，Claude Code/VS Code/Cursor 多 IDE 支持
- [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) — Multi-Agent 金融交易框架，角色分层（分析师/研究员/交易员/风控），真实金融机构运作逻辑的开源实现
- [kyegomez/swarms](https://github.com/kyegomez/swarms) — 企业级 Multi-Agent 编排框架，6,620 ⭐，七种预构建编排模式（MCP/x402/Skills 协议兼容）

- [opensearch-project/agent-health](https://github.com/opensearch-project/agent-health) — OpenSearch 官方的 Agent 评估与观测框架，Golden Path Trajectory 对比 + OpenTelemetry Traces + LLM Judge，15 ⭐
- [elct9620/autonoe](https://github.com/elct9620/autonoe) — 基于 Claude Agent SDK 的长程自主编码工具，1.2k ⭐，Anthropic 双 Agent 模式的完整开源实现
- [sunnweiwei/FoldAgent](https://github.com/sunnweiwei/FoldAgent) — Context-Folding 强化学习框架开源实现，AAAI 2026 论文，让 Agent 学会主动上下文管理

- [cloveric/cc-telegram-bridge](https://github.com/cloveric/cc-telegram-bridge) — Claude Code / Codex CLI 的 Telegram bridge，161 ⭐，session resume + 隔离多 Bot 实例 + Agent Bus 编排（关联：OpenAI Agents SDK 沙箱执行 → CLI harness 桥接模式扩展）
- [Apra-Labs/apra-fleet](https://github.com/Apra-Labs/apra-fleet) — MCP 原生多机 Agent 协作框架，Doer-Reviewer 双角色循环，SSH 跨机器编排（35 ⭐，Apache 2.0）

- [TheAgentCompany/TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) — 在模拟真实软件公司中测试 AI Agent 能力的基准测试框架，175 个真实工作场景，GitLab/Plane/RocketChat 全工具链覆盖，697 ⭐（关联：Anthropic Trend 4 — Agent 学会在不确定性中主动寻求帮助的测试基准）
- [InsForge/InsForge](https://github.com/InsForge/insforge) — AI Coding Agent 的 Backend-as-a-Service 平台，Postgres + Auth + Storage + Model Gateway + Edge Functions，语义层让 Agent 理解「后端在做什么」而非机械生成代码，8.3K ⭐（关联：Anthropic Initializer Agent + Coding Agent 双组件架构 → 后端基础设施的语义化封装）

---

- [89luca89/clampdown](https://github.com/89luca89/clampdown) — 零信任 AI 编码 Agent 沙箱，Landlock + Seccomp + OCI Hook 三层内核级隔离，零密钥泄露架构
- [navam-io/sentinel](https://github.com/navam-io/sentinel) — 视觉优先 Agent 评测平台，React Flow 画布 + YAML 即时生成 + 12 分类断言系统，Postman for AI Agents 定位
- [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) — 专业分工的 AI Agent 团队编排框架，30+ 专才 Agent（Frontend/Backend/SRE/Security 等），人格驱动的 Agent 定义格式标准

## 推荐文章索引

- [Martian-Engineering/Volt](./Martian-Engineering-volt-lossless-context-management-2026.md) — 无损上下文管理，273 Stars，LCM 双态架构（Immutable Store + Active Context）+ 三级升级协议保证收敛，在 OOLONG benchmark 32K-1M tokens 所有长度上超过 Claude Code，与 Anthropic 上下文工程形成「理论框架 → 工程实现」的完整闭环（关联：上下文压缩 → 确定性压缩引擎 → Volt LCM）

- [LiberCoders-FeatureBench-feature-level-agentic-coding-benchmark-2026](./LiberCoders-FeatureBench-feature-level-agentic-coding-benchmark-2026.md) — ICLR 2026 功能级编程 Agent 评测框架，Fast split 57.2 秒/实例，支持 Claude Code/Codex/OpenHands 等 5 个主流 Agent 框架，与 Anthropic AI-Resistant Evaluations 形成「能力边界检测 vs AI 抗性设计」的互补（关联：AI-Resistant Evaluations → 细粒度能力评测趋势 → FeatureBench 功能级评测框架）

- [context-evaluator-packmindhub-ai-agent-config-health-2026](./context-evaluator-packmindhub-ai-agent-config-health-2026.md) — AI Agent 配置文件健康体检工具，17 个评估器诊断 AGENTS.md 质量问题，自动修复 + Before/After 对比（关联：Agent 配置过载 → 配置文件质量的系统性诊断）
- [cursor-cookbook-sdk-examples-2026](./cursor-cookbook-sdk-examples-2026.md) — cursor/cookbook 推荐，3,675 ⭐，5 个生产级 Sample，DAG Task Runner + Cloud Agent 自动化 PR（关联：Cursor Harness 持续改进工程 → SDK 产品化 → 开发者接入生产级 Agent 运行时的代码级入口）

- [openharness-hKUDS-agent-harness-open-source-2026](./openharness-hKUDS-agent-harness-open-source-2026.md) — 香港大学开源 Agent Harness，深度集成 Claude Code / OpenClaw
- [kernelagent-meta-multi-agent-gpu-optimization](./kernelagent-meta-multi-agent-gpu-optimization.md) — Deep Agent + GPU Kernel 自动化优化开源实现
- [archon-open-source-harness-builder](./archon-open-source-harness-builder.md) — 让 AI 编程变得确定可重复的开源工作流引擎
- [superpowers-llm-feature-flags](./superpowers-llm-feature-flags.md) — 用技能框架让 AI 编程从「能写」进化到「会做」
- [everything-claude-code](./everything-claude-code.md) — AI Agent Harness 的性能优化系统
- [pi-mono-langchain-alternative](./pi-mono-langchain-alternative.md) — 轻量级 AI Agent 工具链的另一种选择
- [kubernetes-agent-sandbox](./kubernetes-agent-sandbox.md) — Kubernetes 原生的 Agent 沙箱 CRD
- [vercel-agent-browser](./vercel-agent-browser.md) — Rust 原生浏览器自动化 CLI
- [memos-memory-os](./memos-memory-os.md) — LLM 和 AI Agent 的记忆操作系统
- [alibaba-page-agent](./alibaba-page-agent.md) — 让任何网页都能被自然语言控制
- [agent-sandbox-framework](./agent-sandbox-framework.md) — E2B 兼容的企业级 AI Agent 沙箱
- [claude-code-game-studios](./claude-code-game-studios.md) — 把一个 AI 变成游戏开发工作室
- [easy-vibe-ai-tooling](./easy-vibe-ai-tooling.md) — 面向零基础的 vibe coding 学习课程
- [oh-my-openagent-agent-framework](./oh-my-openagent-agent-framework.md) — 多模型协同的开源 Agent Harness
- [notebooklm-skill-google-ai](./notebooklm-skill-google-ai.md) — Claude Code 与 Google NotebookLM 的无缝集成
- [colleague-skill-ai-agent](./colleague-skill-ai-agent.md) — 将人蒸馏为 AI Skill 的工程实践
- [deer-flow-2-bytedance-super-agent-harness](./deer-flow-2-bytedance-super-agent-harness-2026.md) — 字节跳动开源的多智能体编排框架，Supervisor 模式 + Docker 沙箱 + 持久化记忆
- [claude-context-zilliz-semantic-code-search](./claude-context-zilliz-semantic-code-search-2026.md) — 语义代码搜索 MCP server，让编码 Agent 在 50k+ 行代码库中即时检索相关上下文
- [openskills-universal-skills-loader](./openskills-universal-skills-loader-2026.md) — Anthropic Agent Skills 的跨平台实现
- [mattpocock-skills-engineering-agent-2026](./mattpocock-skills-engineering-agent-2026.md) — 来自真实工程师的 Agent Skills 实践集
- [sandcastle-mattpocock-claude-code-sandbox-orchestration-2026](./sandcastle-mattpocock-claude-code-sandbox-orchestration-2026.md) — Git Worktree 隔离的 Claude Code 生产编排工具，Docker/Podman/Vercel 三层沙箱（关联：Cursor SDK → 生产级 Agent 基础设施的双轨路径）
- [openai-agents-sdk-multi-agent-framework](./openai-agents-sdk-multi-agent-framework.md) — OpenAI 官方多 Agent 编排框架
- [openfang-rust-agent-operating-system](./openfang-rust-agent-operating-system.md) — Rust 编写的开源 Agent 操作系统
- [memsearch-cross-platform-agent-memory-2026](./memsearch-cross-platform-agent-memory-2026.md) — 跨平台统一的 AI Agent 持久记忆层
- [RightNow-AI/openfang](https://github.com/RightNow-AI/openfang) — Rust 编写的开源 Agent 操作系统，Hands 概念实现真正的自主执行
- [zilliztech/claude-context](https://github.com/zilliztech/claude-context) — 语义代码搜索 MCP server，让编码 Agent 在 50k+ 行代码库中即时检索相关上下文
- [zilliztech/memsearch](./memsearch-cross-platform-agent-memory-2026.md) — 跨平台统一的 AI Agent 持久记忆层，Markdown 即真理、Milvus 影子索引
- [jcode-next-generation-coding-agent-harness](./jcode-next-generation-coding-agent-harness.md) — 极致轻量化的下一代编码 Agent Harness（RAM 比 Claude Code 低 93%）
- [planner-worker-multi-agent-autonomous-coding-architecture-2026](../orchestration/planner-worker-multi-agent-autonomous-coding-architecture-2026.md) — Planner/Worker 架构深度分析（Cursor Scaling Agents + Anthropic C Compiler 双案例实证）
- [hermes-agent-nousresearch-self-improving-agent-2026](./hermes-agent-nousresearch-self-improving-agent-2026.md) — Nous Research 自改进 AI Agent，131.8k ⭐，内置学习闭环 + FTS5 跨 Session 检索 + 多平台部署（关联：Cursor 动态上下文发现 → context 工程的两极：动态拉取 vs 自主积累）

- [sanity-io/agent-context](./sanity-io-agent-context-structured-access-2026.md) — Sanity 官方的 Agent Context 工具库，结构化访问 CMS 内容，MCP 集成 + Skills 系统（关联：Context 工程的下一阶段 → 结构化上下文访问）
- [ruflo-ruvnet-claude-native-multi-agent-orchestration-2026](./ruflo-ruvnet-claude-native-multi-agent-orchestration-2026.md) — Claude 原生 Multi-Agent 编排平台，38K ⭐，32 插件生态，自学习 swarm 智能（关联：Context Engineering 外部化记忆设计）
- [ironcurtain-secure-runtime-autonomous-ai-2026](./ironcurtain-secure-runtime-autonomous-ai-2026.md) — 运行时动态风险评估安全运行时，与 Claude Code Auto Mode 双层防御形成技术对照
- [forge-mcp-server-rightnow-2026](./forge-mcp-server-rightnow-2026.md) — 让 AI 编程 Agent 拥有 GPU Kernel 优化能力的 MCP Server，14x 加速
- [autonoe-elct9620-long-running-agent-orchestrator-2026](./autonoe-elct9620-long-running-agent-orchestrator-2026.md) — 基于 Claude Agent SDK 的长程自主编码工具，1.2k ⭐，Anthropic 双 Agent 模式的完整开源实现
- [multiagenteval-open-source-agent-eval-harness-2026](./multiagenteval-open-source-agent-eval-harness-2026.md) — 填补 Agentic Reliability Gap 的开源评估框架，5000+ 场景 + Zero-Touch Core Architecture
- [flue-astro-agent-harness-framework-2026](./flue-astro-agent-harness-framework-2026.md) — Astro 团队开源的 TypeScript Agent Harness，虚拟沙箱 + Markdown Skill 系统
- [hive-openhive-multi-agent-harness-2026](./hive-openhive-multi-agent-harness-2026.md) — 目标驱动的 Multi-Agent 生产级 Harness，YC 背景 + 自愈图谱演化
- [anysphere-kernel-optimization-results](./anysphere-kernel-optimization-results-2026.md) — Cursor + NVIDIA 235 个 CUDA Kernel 38% 加速的开源验证结果
- [metamorph-multi-agent-file-lock-parallel-2026](../orchestration/metamorph-multi-agent-file-lock-parallel-2026.md) — Git 文件锁分布式协调机制，Anthropic 100K 行 C 编译器的工程验证
- [open-multi-agent-typescript-multi-agent-2026](./open-multi-agent-typescript-multi-agent-2026.md) — 3 依赖的 TypeScript Multi-Agent 引擎，从目标到结果单调用
- [brain-hands-decoupled-agent-architecture-2026](../orchestration/brain-hands-decoupled-agent-architecture-2026.md) — Anthropic / OpenAI / Cursor 三家 Brain-Hands 解耦架构对比分析
- [getzep/graphiti](https://github.com/getzep/graphiti) — 面向 AI Agent 的时态上下文图谱，25.8k ⭐，实体/关系/事实四组件 + validity window + episode 溯源，MCP Server 接入 Claude/Cursor
- [browserbase-skills-claude-code-cloud-browser-automation-2026](./browserbase-skills-claude-code-cloud-browser-automation-2026.md) — Browserbase Skills 云端浏览器自动化，突破编码 Agent 处理受保护站点的能力瓶颈
- [genericagent-self-evolving-agent-framework-3k-lines-2026](./genericagent-self-evolving-agent-framework-3k-lines-2026.md) — ~3K 行极简自进化 Agent 框架，技能从任务中结晶而非预装，<30K context window
- [awesome-agent-skills-agent-skill-index-4494-stars-2026](./awesome-agent-skills-agent-skill-index-4494-stars-2026.md) — GitHub 最大的 Agent Skills 索引，4,494 ⭐，覆盖 9 个主流 AI Coding 平台
- [cursor-multi-agent-cuda-kernel-optimizer-38-percent-2026](../orchestration/cursor-multi-agent-cuda-kernel-optimizer-38-percent-2026.md) — Cursor 多智能体系统 3 周 38% 加速，235 个 CUDA Kernel 优化工程方法论解析（Planner/Worker 架构 + Self-Benchmarking 闭环）
- [cuda-agent-byted-tsinghua-rl-kernel-optimization-2026](./cuda-agent-byted-tsinghua-rl-kernel-optimization-2026.md) — 字节跳动 × 清华 RL 训练 GPU Kernel 优化系统，首个超越 Claude Opus-4.6 的开源实现
- [gastown-multi-agent-workspace-manager-2026](./gastown-multi-agent-workspace-manager-2026.md) — 多 Agent 工作空间编排系统，14,914 ⭐，Git Worktree 隔离 + Beads 账本 + Witness/Deacon 三层监控（关联：Cursor 第三时代多 Agent Fleet 范式）
- [lobehub-agent-collaboration-platform-2026](./lobehub-agent-collaboration-platform-2026.md) — Agent 协作空间平台，75K ⭐，Agent as the Unit of Work + Create/Collaborate/Evolve 三层协作模式（关联：Anthropic 四层组件模型 → 多 Agent 协作场景下的人类控制设计）
- [mem0-universal-memory-layer-agent-2026](./mem0-universal-memory-layer-agent-2026.md) — LLM 和 AI Agent 的通用记忆层，self-improving memory，LoCoMo 91.6 分（关联：Anthropic Context Engineering → Memory Management 实践验证）
- [tradingagents-multi-agent-trading-framework-2026](./tradingagents-multi-agent-trading-framework-2026.md) — Multi-Agent 金融交易框架，角色分层（分析师/研究员/交易员/风控），真实金融机构运作逻辑的开源实现（关联：Anthropic Agent Skills → 多 Agent 专业角色编排）
- [evalview-ai-agent-behavior-regression-gate-2026](./evalview-ai-agent-behavior-regression-gate-2026.md) — AI Agent 行为回归门卫，snapshot behavior → diff tool calls → classify regression，与 Anthropic Long-Running Agent Harness 互补（前者保实现可维护性，后者保行为一致性）
- [nonstop-agent-claude-long-running-harness-2026](./nonstop-agent-claude-long-running-harness-2026.md) — Claude 长时连续工作 harness，feature_list.json + 双 Agent Pattern，Anthropic 官方工程实践的开源实现（关联：Anthropic Initializer + Coding Agent 双组件架构）
- [ouroboros-agent-os-replayable-specification-first-2026](./ouroboros-agent-os-replayable-specification-first-2026.md) — Agent OS：规范优先的可验证编码工作流，Specification-first + 3-stage Evaluation Gate，与 Anthropic Context Engineering 形成互补（前者减少输入端冗余，后者管理过程端容量）
- [daytona-open-source-ai-agent-sandbox-oci-containers-2026](./daytona-open-source-ai-agent-sandbox-oci-containers-2026.md) — OCI 原生的 AI Agent 沙箱运行时，Sub-90ms 冷启动 + 可选 Kata/Sysbox 强隔离（关联：Anthropic April Postmortem → 沙箱隔离是防止跨层缺陷演变为安全事件的最后防线）

- [getzep/graphiti](./getzep-graphiti-temporal-context-graph-2026.md) — 面向 AI Agent 的时态上下文图谱，25.8k ⭐，MCP Server + 多图数据库支持，与 Anthropic Introspection Adapters 形成「外部上下文管理 vs 内部行为审计」的互补
- [local-deep-research-encrypted-agentic-research-2026](./local-deep-research-encrypted-agentic-research-2026.md) — 本地化深度研究 Agent，4,706 ⭐，SQLCipher AES-256 加密 + LangGraph Agent Strategy + SimpleQA ~95%（关联：Cursor Composer Self-Summarization → 信息管理问题的互补视角：压缩 vs 扩展）
- [vibepod-cli-docker-agent-container-2026](./vibepod-cli-docker-agent-container-2026.md) — Docker 容器化的 AI 编码 Agent 管理 CLI，零配置 + 本地 Analytics Dashboard，支持 7 个主流 Agent（关联：OpenAI Agents SDK Native Sandbox → 本地 vs 云端的不同隔离路径）
- [overstory-multi-agent-orchestration-git-worktree-2026](./overstory-multi-agent-orchestration-git-worktree-2026.md) — Git Worktree 隔离的多 Agent 编排工具，让单个 Claude Code Session 变身多 Agent 团队（关联：Cursor 第三代软件开发 → Agent Fleet 架构的第三种路线：本地化隔离 + 实时干预）
- [mcp-agent-lastmile-ai-mcp-framework-2026](./mcp-agent-lastmile-ai-mcp-framework-2026.md) — 用简单模式构建高效 Agent 的 MCP 框架，Full MCP Support + Temporal Durable Execution（关联：动态上下文发现 → Token 效率工程）
- [opensearch-agent-health-opensearch-eval-harness-2026](./opensearch-agent-health-opensearch-eval-harness-2026.md) — OpenSearch 官方的 Agent 评估框架，Golden Path Trajectory 对比 + OpenTelemetry + LLM Judge（关联：Cursor Harness 持续改进 → 测量驱动改进的工程实现）
- [lumen-omxyz-vision-first-browser-agent-context-compression-2026](./lumen-omxyz-vision-first-browser-agent-context-compression-2026.md) — 视觉优先浏览器 Agent，screenshot→action 循环 + 两层上下文压缩（80% threshold），与 Cursor Self-Summarization 形成训练侧×工程侧的互补（关联：Context Engineering → 注意力预算管理与压缩触发机制工程实现）
- [swarms-kyegomez-enterprise-multi-agent-orchestration-2026](./swarms-kyegomez-enterprise-multi-agent-orchestration-2026.md) — 企业级 Multi-Agent 编排框架，6,620 ⭐，七种预构建编排模式（MCP/x402/Skills 协议兼容）（关联：Anthropic Multi-Agent 四种协调范式 + Swarms 工程实现）
- [wshobson-agents-claude-code-plugins-34800-stars-2026](./wshobson-agents-claude-code-plugins-34800-stars-2026.md) — Claude Code 最大插件市场，34,800 ⭐，185 个专项 Agent + 80 个解耦插件 + 渐进式披露架构（关联：Anthropic Initializer+Coding Agent 双组件模式 → 插件市场级多 Agent 协作解决方案）
- [cc-telegram-bridge-claude-code-telegram-harness-2026](./cc-telegram-bridge-claude-code-telegram-harness-2026.md) — Claude Code / Codex CLI 的 Telegram bridge，161 ⭐，session resume + 隔离多 Bot 实例 + Agent Bus 编排（关联：OpenAI Agents SDK 沙箱执行 → CLI harness 桥接模式扩展）
- [apra-fleet-apra-labs-mcp-multi-agent-coordination-2026](./apra-fleet-apra-labs-mcp-multi-agent-coordination-2026.md) — MCP 原生多机 Agent 协作框架，Doer-Reviewer 双角色循环，SSH 跨机器编排（关联：Cursor 第三时代工厂思维 → 多机 Agent 协作的开源实现路径）

- [claude-agent-teams-ui-777genius-multi-agent-kanban-2026](./claude-agent-teams-ui-777genius-multi-agent-kanban-2026.md) — 多 Agent 团队编排桌面应用，855 ⭐，Kanban 看板 + Hunk 级 Review + 零配置启动，Electron 桌面端读取本地 Claude/Codex Session（关联：Cursor 3 统一多 Agent 工作空间 → 开源生态的等效实现）
- [foldagent-context-folding-reinforcement-learning-2026](./foldagent-context-folding-reinforcement-learning-2026.md) — Context-Folding 强化学习框架开源实现，AAAI 2026 论文，让 Agent 学会主动上下文管理（关联：Anthropic「注意力预算」+ Cursor「Self-Summarization」→ Learned Context Compression 方向实证）
- [swe-af-autonomous-engineering-factory-agentfield-2026](./swe-af-autonomous-engineering-factory-agentfield-2026.md) — 自主工程团队 Runtime，三层控制闭环（Inner/Middle/Outer Loop）+ Git Worktree 隔离并行，Fleet-scale 编排（关联：Cursor 第三时代「工厂思维」→ 自主工程工厂的开源实现）

- [cocoindex-incremental-context-for-long-horizon-agents-2026](./cocoindex-incremental-context-for-long-horizon-agents-2026.md) — 长程 Agent 增量上下文引擎，代码库变化 delta-only 重嵌入，Rust 生产级实现，8.4k ⭐（关联：OpenAI Codex Agent Loop 上下文膨胀问题 → 增量引擎从数据源侧解决新鲜度）
- [memory-benchmarks-eval-suite-2026](./memory-benchmarks-eval-suite-2026.md) — Mem0 开源的 Agent 内存系统评估套件，LoCoMo / LongMemEval / BEAM 三个基准，3000+ 评测题，Cloud + OSS 双模式（关联：Anthropic AI-Resistant Evaluations → 可量化基准测试是持续改进的前提）

- [deepseek-tui-terminal-native-coding-agent-2026](./deepseek-tui-terminal-native-coding-agent-2026.md) — Terminal 原生 AI 编码 Agent，DeepSeek V4 + 1M context + Auto mode，+1,274 stars trending（关联：OpenAI 企业 AI 战略 → Codex vs DeepSeek-TUI 的终端工具双轨竞争）
- [agency-agents-msitarzewski-multi-agent-professional-team-2026](./agency-agents-msitarzewski-multi-agent-professional-team-2026.md) — 专业分工的 AI Agent 团队编排框架，30+ 专才 Agent 人格驱动定义（关联：Anthropic 三代理 GAN 启发架构 → Planner-Generator-Evaluator vs. Agency-Agents 静态专才分工的两种协作范式）
- [context-mode-mksglu-98-percent-context-reduction-2026](./context-mode-mksglu-98-percent-context-reduction-2026.md) — MCP 上下文管理框架，98% Token 压缩 + SQLite FTS5 BM25 检索 + 14 平台覆盖（Microsoft/Google/NVIDIA/Cursor 等），Anthropic Context Engineering 原则的完整工程实现（关联：Anthropic「上下文压缩」+「注意力预算」框架 → 98% 压缩率的工业级验证）

- [agent-infra-sandbox-all-in-one-agent-sandbox-2026](./agent-infra-sandbox-all-in-one-agent-sandbox-2026.md) — All-in-One Agent 沙箱框架，Browser+Shell+File+VSCode+Jupyter+MCP 同容器统一文件系统，2.3k ⭐（关联：Cursor Automations → 本地化执行环境替代方案，与 Cursor Self-Hosted 形成完整闭环）

- [future-agi/future-agi](https://github.com/future-agi/future-agi) — 开源端到端 Agent 评估与优化平台，Simulate→Evaluate→Protect→Monitor→Optimize 单闭环，Go 网关 ~29k req/s，836 ⭐

- [agent-infra/sandbox](https://github.com/agent-infra/sandbox) — All-in-One Agent 沙箱框架，Browser+Shell+File+VSCode+Jupyter+MCP 同容器统一文件系统，2.3k ⭐

- [Hmbown/DeepSeek-TUI](https://github.com/Hmbown/DeepSeek-TUI) — Terminal 原生 AI 编码 Agent，DeepSeek V4 + 1M context + Auto mode 自动选择模型思考级别，+1,274 stars trending（关联：OpenAI Codex → 终端原生 AI 工具的双轨竞争格局）

- [skyflo-ai/skyflo](https://github.com/skyflo-ai/skyflo) — Kubernetes 原生的 Self-Hosted AI Agent，Approval-Gated + 确定性控制循环，TypeScript，108 ⭐

- [777genius/claude_agent_teams_ui](https://github.com/777genius/claude_agent_teams_ui) — 多 Agent 团队编排桌面应用，Kanban 看板 + Hunk 级 Review，855 ⭐，Electron + React + TypeScript
