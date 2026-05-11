# gstack：YC CEO 的 AI 软件工厂——93,788 Stars 的工程力作

> **核心结论**：gstack 将 Claude Code 变成了一个虚拟工程团队——CEO、设计师、工程经理、QA 负责人、安全官等 23 个专家角色，全部通过 Slash 命令调用。93,788 Stars 验证了"单人ceo × AI = 团队"这个命题的现实性，与 PayPal 3,000 应用改造案例形成「个人 → 企业」的完整 Agent 工具链光谱。

---

## T - Target：谁该关注

**目标用户画像**：
- 有技术背景的创始人/CEO——特别是那些仍然想亲自下场的产品人
- 首次接触 Claude Code 的开发者——有结构的角色指导而不是空白提示
- Tech Lead 和 Staff Engineer——每个 PR 上的严格审查、QA 和发布自动化

> 适用水平：已入门 Claude Code，想从「个人助手」升级到「AI 团队」的用户。不适合完全没用过 Claude Code 的新手。

---

## R - Result：能带来什么具体改变

Garry Tan（Y Combinator CEO）自己的数据，官方原文：

> "In the last 60 days: 3 production services, 40+ shipped features, part-time, while running YC full-time."
> — [garrytan/gstack README](https://github.com/garrytan/gstack)

关键对比数据：

| 指标 | 2013（Bookface） | 2026（gstack） | 提升倍数 |
|------|-----------------|---------------|---------|
| GitHub 贡献 | 772 次 | 1,237 次（至今） | ~1.6x |
| 代码产出速率 | 14 logical lines/day | 11,417 logical lines/day | **~810x** |
| 年产出（到4月18日）| — | 240x 整个 2013 年 | — |

> 官方原文：
> "On logical code change — not raw LOC, which AI inflates — my 2026 run rate is **~810× my 2013 pace** (11,417 vs 14 logical lines/day)."
> — [garrytan/gstack README](https://github.com/garrytan/gstack)

---

## I - Insight：它凭什么做到这些

gstack 的核心设计不是另一个 AI 编程工具，而是一个**角色扮演框架**。

Garry Tan 在 README 中解释：

> "It turns Claude Code into a virtual engineering team — a CEO who rethinks the product, an eng manager who locks architecture, a designer who catches AI slop, a reviewer who finds production bugs, a QA lead who opens a real browser, a security officer who runs OWASP + STRIDE audits, and a release engineer who ships the PR."
> — [README](https://github.com/garrytan/gstack)

**23 个专家角色**：

| 角色 | Slash 命令 | 功能 |
|------|-----------|------|
| CEO | `/plan-ceo-review` | 产品战略审查 |
| 工程经理 | `/plan-eng-review` | 架构锁定审查 |
| 设计师 | `/design-consultation` | 设计评审 |
| 安全官 | `/cso` | OWASP + STRIDE 安全审计 |
| QA 负责人 | `/qa` | 打开真实浏览器测试 |
| 发布工程师 | `/ship` | PR 合并和部署 |
| 调查员 | `/investigate` | 根因调试方法论 |
| 回顾 | `/retro` | 周工程回顾 |
| ... | ... | ... (共 23 个) |

**8 个 Power Tools**：覆盖计划、审查、QA、部署、安全等全链路。

---

## E - Evidence：技术深度与社区健康度

### 安装：30 秒完成

官方原文：

> "Open Claude Code and paste this. Claude does the rest.
> Install gstack: run `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`"
> — [README](https://github.com/garrytan/gstack)

**Team Mode**：团队共享，自动化更新，无版本漂移：

> "No vendored files in your repo, no version drift, no manual upgrades. Every Claude Code session starts with a fast auto-update check (throttled to once/hour, network-failure-safe, completely silent)."
> — [README](https://github.com/garrytan/gstack)

### 与 OpenClaw 的深度集成

gstack 明确支持 OpenClaw：

> "OpenClaw spawns Claude Code sessions via ACP, so every gstack skill just works when Claude Code has gstack installed."
> — [README](https://github.com/garrytan/gstack)

Dispatch 路由表：

| 你说 | 发生什么 |
|------|---------|
| "Fix the typo in README" | 简单任务，Claude Code session，不需要 gstack |
| "Run a security audit on this repo" | 用 `/cso` 生成 Claude Code session |
| "Build me a notifications feature" | 用 `/autoplan` → implement → `/ship` |
| "Help me plan the v2 API redesign" | 用 `/office-hours` → `/autoplan`，保存计划但不实现 |

### GitHub 数据

| 指标 | 数值 |
|------|------|
| Stars | **93,788** |
| Forks | — |
| 创建时间 | 2026-03-11 |
| 最后更新 | 2026-05-11 |
| License | MIT |

> 数据来源：[GitHub API - garrytan/gstack](https://github.com/garrytan/gstack)

### 与 gbrain 的关系

Garry Tan 的另一个项目 [garrytan/gbrain](https://github.com/garrytan/gbrain)（13,599 Stars）是 gstack 的"大脑"——提供知识图谱自布线和 34 个 skills。gstack 是前台界面，gbrain 是后台能力。这是「Thin Harness Fat Skills」理念的完整工程实现。

---

## P - Threshold：行动引导

### 快速开始（5 步）

1. **安装**：在 Claude Code 中粘贴安装命令
2. **描述需求**：运行 `/office-hours`——描述你在构建什么
3. **计划审查**：在任何功能想法上运行 `/plan-ceo-review`
4. **代码审查**：在任何分支上运行 `/review`
5. **QA 测试**：在你的 staging URL 上运行 `/qa`

> "Stop there. You'll know if this is for you."
> — [README](https://github.com/garrytan/gstack)

### OpenClaw 用户

```
clawhub install gstack-openclaw-office-hours gstack-openclaw-ceo-review gstack-openclaw-investigate gstack-openclaw-retro
```

这四个 skill 让 OpenClaw agent 直接运行 gstack 方法论，不需要 Claude Code session。

---

## 与 PayPal 案例的主题关联

**gstack**（个人工具）和 **PayPal Cursor 案例**（企业规模）构成了完整的 AI 编程工具光谱：

| 维度 | gstack（个人） | PayPal Cursor（企业） |
|------|--------------|---------------------|
| 规模 | 单人 × AI = 虚拟团队 | 8,000 开发者，3,000 应用 |
| 角色 | 23 个 Slash 专家角色 | 角色边界模糊，全员 AI 协作 |
| 产出 | 810x 生产力提升 | 2 个月完成 8-12 个月的 Java 升级 |
| 核心洞察 | 单人可以像团队一样运作 | 团队整体产出 40% 增长 |

两者共同指向：**AI 编程工具的本质不是提升个人效率，而是重新定义「一个人能做什么」**。

---

## 引用来源

- [garrytan/gstack - GitHub](https://github.com/garrytan/gstack)（官方 README，第一手来源，MIT License）
- [Cursor Blog: Beyond efficiency: PayPal expands what's possible to build with AI](https://cursor.com/blog/paypal)（关联案例）