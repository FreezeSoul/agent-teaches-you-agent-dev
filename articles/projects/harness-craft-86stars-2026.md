# Harness Craft：YC CEO 背书的可组合 AI Coding Skills/Rules 库

> "Turn agentic coding from a one-off prompt trick into a durable engineering system."
> — [Harness Craft README](https://github.com/YuxiaoWang-520/harness-craft)

## TRIP 四要素

| 要素 | 内容 |
| --- | --- |
| **T - Target** | 有 Python 经验的 Agent 开发新手或团队，想从「prompt tricks」升级到「engineering system」；或者已经遇到长程任务失败（上下文丢失/多 Agent 碰撞/进度不可验证）的团队 |
| **R - Result** | 将 Agent 工作流从「每次会话从零开始」升级为「跨 session 持久化、可验证、可恢复」；GitHub 86 Stars，Created 2026-03-16，Last push 2026-04-08 |
| **I - Insight** | YC CEO Garry Tan 在「Thin Harness, Fat Skills」方法论中指出 100x 效率差距来自 harness 设计而非模型；Harness Craft 将这个原则工程化为 46 个可组合 Skills + 15 条 Rules 的完整系统 |
| **P - Proof** | YC Portfolio 背景（YC CEO 亲自背书），GitHub 86 Stars + 5 Forks，README 746 行详细文档，四大 flagship Skills 都有完整架构文档和脚本 |

## P-SET 骨架

### P - Positioning（定位破题）

**一句话定义**：将 AI Coding Agent 从「prompt 技巧」升级为「工程化持久系统」的技能库和规则集。

**场景锚定**：当你发现 Agent 在长程任务中「失忆」——上次讨论的架构决策在新 session 里消失了；当你需要多个 Agent 协作但文件碰撞和质量退化问题频发；当你无法判断 Agent 说「完成了」是否真的完成了。

**差异化标签**：YC 官方认可 + 四层工程化干预 + Claude/Codex 双平台支持。

### S - Sensation（体验式介绍）

**「哇时刻」**：`repo-bootstrap` Skill 生成的六个持久化文件——`.harness/state.json`、`.harness/memory.md`、`.harness/prompt.md`、`.harness/repowiki.md`、`.harness/plan.md`、`.harness/checklist.md`——这不只是文档模板，而是一套「上下文持久化协议」。

当你从 `repo-bootstrap` 启动一个新 session 时，Agent 自动读取这六个文件，而不需要你重新解释项目背景、已做出的决策、当前进度。这意味着**Agent 的上下文不再依赖于 chat history，而是依赖于显式持久化的 repo 资产**。

`longrun-dev` 的「One feature per session」约束看起来简单，但它是最高杠杆的控制点——它解决了长程任务最常见的失败模式：做太多、范围漂移、「while I'm here」蔓延。

### E - Evidence（拆解验证）

**技术深度**：

四大 flagship Skills 的设计逻辑：

- **`repo-bootstrap`**：将 repo 认知拆分为六个独立职责的文件，每个文件有明确的所有权边界。这种分离防止了「memory.md 和 repowiki.md 混合后变成无结构日记」的问题。
- **`longrun-dev`**：状态驱动而非信心驱动的完成判断。`.longrun/feature_list.json` 的 `passes: false/true` 是机器可读的，而「模型觉得完成了」是主观判断。
- **`agent-team-dev`**：故意维持小型拓扑——Mode A（0-1 子 Agent）、Mode B（2）、Mode C（3-4）。上限是 4，不是「越多越好」。
- **`learn`**：知识累积三层强度模型（weak→medium→strong），而非浮点数置信度（0.47 vs 0.52 没有意义）。

Skills vs Rules 双层架构：Rules 是 Agent 的本能（始终开启），Skills 是 Agent 的 playbook（按需调用）。

**竞品对比**：与 cursor/cookbook（3,675 Stars）不同，cookbook 提供的是 Cursor SDK 的使用示例，而 Harness Craft 提供的是 Agent 工程化系统的完整设计框架。

**YC 背景**：Garry Tan 在「Thin Harness, Fat Skills」中指出 100x 效率差距来自 harness 设计而非模型。Harness Craft 是这个方法论的生产级实现。

### T - Threshold（行动引导）

**快速上手**（3 步以内）：

```bash
# Step 1：一键安装 flagship profile（包含4个核心 Skills + 核心 Rules）
python3 scripts/install.py --assistant claude --profile flagship --with-python-rules

# Step 2：在目标 repo 启动新 session
cd your-project && claude

# Step 3：Agent 自动加载持久化上下文，开始工作
```

**适用场景扩展**：46 个 Skills 覆盖完整开发周期——`repo-bootstrap`（上下文）、`longrun-dev`（长程执行）、`agent-team-dev`（多 Agent 协作）、`learn`（知识累积）、`eval-harness`（评测）、`deep-research`（研究）、`e2e-testing`（端到端测试）等。

**不适合的场景**：一次性代码生成任务（不需要跨 session 持久化）、单 Agent 简单任务（ Skills 的工程化开销不划算）。

## 防重检查

`articles/fundamentals/ai-coding-engineering-paradigm-shift-2026.md`（同轮次）已对本文档形成主题关联：文章解析「Prompt Tricks → Engineering Systems」的范式转移，Projects 提供该范式转移的工程实现。

---

**引用来源**：

1. > "Turn agentic coding from a one-off prompt trick into a durable engineering system."
   > — [Harness Craft README](https://github.com/YuxiaoWang-520/harness-craft)

2. > "The biggest failure mode in agent-driven development is not intelligence — it is **system instability**."
   > — [Harness Craft README](https://github.com/YuxiaoWang-520/harness-craft)

3. > "One feature per session looks simple, but it is one of the highest-leverage control points for agents."
   > — [Harness Craft: longrun-dev](https://github.com/YuxiaoWang-520/harness-craft/blob/main/skills/longrun-dev/SKILL.md)

4. > "The goal is not to add one more clever prompt. The goal is to upgrade agent work into a system that is: Persistent · Verifiable · Collaborative · Recoverable · Learnable."
   > — [Harness Craft README](https://github.com/YuxiaoWang-520/harness-craft)