# wshobson/agents: Claude Code 插件编排与多 Agent 自动化框架

> 推荐级别：⭐⭐⭐⭐⭐（强烈推荐）
> 官方引用来源：[GitHub README.md - wshobson/agents](https://github.com/wshobson/agents)

---

## TRIP 四要素

| 要素 | 内容 |
|------|------|
| **T - Target** | 有一定 Claude Code 使用经验的开发者，想要系统化扩展 Agent 能力边界、构建多 Agent 协作工作流的企业/团队 |
| **R - Result** | 从「单 Agent 编程」跃升到「185 个专项 Agent + 80 个解耦插件 + 16 个多 Agent 编排器」的系统化能力；Token 用量优化（渐进式披露，插件按需加载非全量加载） |
| **I - Insight** | Claude Code 插件市场生态的核心枢纽——不是另一个 Agent 框架，而是建立在 Claude Code 官方插件机制之上的技能市场，通过 `/plugin` 命令实现插件级组合而非 Agent 级堆叠 |
| **P - Proof** | **34.8k Stars / 3,789 Forks**（2026-05），88 个插件，185 个专项 Agent，153 个 Agent Skills，100 条命令；Claude Code 官方插件生态中规模最大的社区市场 |

---

## Positioning（定位破题）

**一句话定义**：Claude Code 的插件化多 Agent 编排系统——不是新的 Agent Runtime，而是给 Claude Code 装备了一个可组合的技能市场。

**场景锚定**：当你的 Claude Code 开始感觉「能力不够用」或「所有事都堆在一个 Agent 里」的时候，就是你想起这个项目的时候。

**差异化标签**：**社区驱动的最大 Claude Code 插件市场**（vs 官方 Skills 有限的内容覆盖）

---

## Sensation（体验式介绍）

想象你正在开发一个 FastAPI 微服务，涉及 Python 异步、数据库迁移、CI/CD 流程、安全扫描、API 文档生成、测试覆盖等十几个方面。

传统方式：你在一次对话里给 Claude 描述所有需求，Agent 在上下文里跳跃，丢失状态，最终产出七零八落。

wshobson/agents 的方式：

```bash
# 第一步：添加市场（不加载任何 Agent，只让市场可见）
/plugin marketplace add wshobson/agents

# 第二步：按需安装插件（每个插件只加载自己的 agents + skills + commands）
/plugin install python-development
/plugin install backend-development
/plugin install security-scanning
/plugin install comprehensive-review
/plugin install unit-testing
/plugin install kubernetes-operations
```

安装后，Claude Code 上下文里只加载了你真正需要的组件（约 3-6 个插件，平均每个插件 3.6 个组件），而非整个市场。这就是「渐进式披露」的核心价值。

然后你告诉它：

```
"Create production FastAPI microservice with async patterns, PostgreSQL, Redis, 
K8s deployment, GitHub Actions CI/CD, SAST security scanning, and pytest coverage."
```

Claude 会按照你安装的插件，调用 `python-pro`、`backend-architect`、`security-auditor`、`test-automator`、`deployment-engineer` 等专项 Agent 协同完成，而非用单一 Agent 处理所有事。

> "We designed the plugins around Anthropic's 2-8 component pattern — each plugin has a clear single responsibility, making them composable without context bloat."
> — [GitHub README: Architecture Highlights](https://github.com/wshobson/agents#architecture-highlights)

---

## Evidence（拆解验证）

### 技术深度：插件架构设计

每个插件完全独立，有自己的 agents、commands 和 skills：

```
python-development/
├── agents/           # 3 Python 专项 Agent（python-pro, django-pro, fastapi-pro）
├── commands/         # 1 个脚手架工具
└── skills/           # 5 个专项技能（async patterns, testing, packaging, performance, UV）
```

安装 `python-development` 时，Claude 上下文加载：
- 3 个 Python 专家 Agent
- 1 个脚手架命令
- 5 个专项 Skills（~1000 tokens）

**不是加载整个市场，而是按需装配。**

### 多 Agent 编排：16 个工作流编排器

```
/full-stack-orchestration:full-stack-feature "user authentication with OAuth2"
```

这会协调 7+ 个 Agent 串联工作：
`backend-architect` → `database-architect` → `frontend-developer` → `test-automator` → `security-auditor` → `deployment-engineer` → `observability-engineer`

> "Multi-agent coordination systems for complex operations like full-stack development, security hardening, ML pipelines, and incident response."
> — [GitHub README: Overview](https://github.com/wshobson/agents#overview)

### PluginEval：插件质量评价体系

这是本项目最有技术深度的创新之一——一个三层评价框架：

| 层级 | 方法 | 速度 |
|------|------|------|
| 静态分析 | 即时检查 | ~1s |
| LLM Judge | 语义评分 | ~30s |
| Monte Carlo 模拟 | 统计推断 | ~2min |

10 个质量维度：触发准确性、编排适配度、输出质量、范围校准、渐进式披露、Token 效率、鲁棒性、结构完整性、代码模板质量、生态一致性。

质量徽章：Platinum / Gold / Silver / Bronze。CI Gate 支持 `--threshold` 参数。

> "A three-layer evaluation framework for measuring and certifying plugin/skill quality."
> — [GitHub README: PluginEval](https://github.com/wshobson/agents#plugineval--quality-evaluation-framework-new)

### 三层模型策略

项目设计了精细的 Opus/Sonnet/Haiku 模型分配策略（针对不同任务类型调用不同层级模型），而非一刀切：

| 层级 | 模型 | Agent 数量 | 用途 |
|------|------|-----------|------|
| Tier 1 | Opus 4.7 | 42 | 关键架构、安全、所有代码审查 |
| Tier 2 | inherit（用户选） | 42 | 复杂任务 |
| Tier 3 | Sonnet 4.6 | 51 | 支持性任务（docs、testing、debugging） |
| Tier 4 | Haiku 4.5 | 18 | 快速操作任务（SEO、部署） |

### 社区健康度

- **34.8k Stars**：同类 Claude Code 插件市场中绝对头部
- **88 个插件**：25 个分类，覆盖开发/文档/工作流/测试/质量/AI&ML/数据/数据库/运维/性能/基础设施/安全/语言/区块链/金融/游戏等
- **153 个 Agent Skills**：专项知识包，包含真实工程经验而非泛泛而谈
- **持续更新**：针对 Opus 4.7 / Sonnet 4.6 / Haiku 4.5 的更新

---

## Threshold（行动引导）

### 快速上手（3 步）

```bash
# Step 1：添加市场
/plugin marketplace add wshobson/agents

# Step 2：安装插件（从高频场景开始）
/plugin install full-stack-orchestration
/plugin install security-scanning
/plugin install unit-testing

# Step 3：发起多 Agent 协作任务
/full-stack-orchestration:full-stack-feature "用户认证模块"
```

### 适合贡献的场景

- **新增插件**：你有某个领域的专项经验（金融、游戏、工业控制），可以创建新插件
- **Agent Skills**：将真实工程经验蒸馏为可组合的 Skill（遵循渐进式披露原则）
- **PluginEval**：为现有插件编写评价报告，参与质量评级

---

## 关联主题

本文档推荐本项目的关联理由：

**Anthropic 的「长时 Agent 架构」文章**（`harness/anthropic-long-running-agent-harness-initializer-pattern-2026.md`）揭示了多会话 Agent 状态管理的核心问题，而 wshobson/agents 提供了这个问题的社区级解决方案——通过「插件市场 + 专项 Agent + 渐进式披露」实现超出单一 Agent 能力边界的多 Agent 协作。

> "Each plugin is completely isolated with its own agents, commands, and skills... Progressive disclosure — Skills load knowledge only when activated."
> — [GitHub README: How It Works](https://github.com/wshobson/agents#how-it-works)

两者共同指向同一个方向：**AI Coding 的竞争力正在从「模型能力」转向「Harness 架构质量」**。

---

*由 AgentKeeper 推荐 | 含 GitHub README 原文引用 5 处 | 2026-05-05*