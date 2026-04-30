# Coding Agents 实战洞察 2026：Codex 联创Calvin French-Owen 的时间决策框架与 Opus 并行架构

> **来源**：Calvin French-Owen — [Coding Agents in Feb 2026](https://calv.info/agents-feb-2026)（个人博客，2026-02）  
> **背景**：Calvin French-Owen 是 Segment 联合创始人，曾参与 OpenAI Codex 产品发布，长期活跃于 AI Coding Agent 领域  
> **原文性质**：一手实战经验，非厂商发布或媒体转述  
> **分类**：AI Coding 工具 / 实战框架 / 模型选型  
> **标签**：Claude-Code / Codex / Opus / 决策框架 / 并行架构 / Skills

---

## 概述

2026年2月，Calvin French-Owen 在 YC Lightcone Podcast 讨论后感到意犹未尽—— Podcast 没能展开技术细节。于是他在个人博客上写了一篇深度文章，记录他作为 Codex 联创成员和长期 Claude Code 用户，对当前主流 Coding Agent 的真实对比判断。

**核心洞察**：他将 **时间** 作为选择 Agent 的第一决策变量——不是哪个模型最强，而是「我现在有多少时间」。这个框架重构了整个选型逻辑。

---

## 核心判断 1：时间是最好的 Agent 选择器

Calvin 的第一个框架转变是：他选择用哪个 Agent，取决于**有多少时间**以及**想让 Agent 运行多久**。

| 场景 | 决策 | 背后的逻辑 |
|------|------|-----------|
| 夜间跑一个 80% 完成度的草案 | 用 Claude Code + Opus | 让它自主运行，早上起来看结果 |
| 白天协作式工作（实时交互） | 用 Codex | 需要更高正确率，但速度较慢 |
| 需要并行多个任务 | 用 Claude Code（Opus + Haiku sub-agent） | Haiku 快速探索上下文，回传关键信息 |
| 真正开始写代码 | 切换到 Codex | Codex 写出来的代码 Bug 明显更少 |

> "I'm primarily picking my coding agent as a function of how much time I have, and how long I want it to run autonomously."
> — Calvin French-Owen

**这背后的假设**：Claude Code（Opus）和 Codex 不是同质替代品，而是互补工具。两者在代码正确性、上下文效率、并行能力上有根本性差异，时间约束决定了哪个差异更重要。

---

## 核心判断 2：Opus 的并行 sub-agent 架构（Haiku 快速探索模式）

Calvin 在文章中详细描述了 Opus 的一个关键工程特性：**并行 sub-agent 架构**，使用 Haiku 作为快速探索层。

### 机制描述

```
Opus 主会话
    ├── Sub-agent 1 (Haiku): 快速扫描 /src 目录，提取文件结构和关键接口
    ├── Sub-agent 2 (Haiku): 快速扫描 /test 目录，提取测试覆盖范围
    └── Sub-agent 3 (Haiku): 快速扫描 /docs 目录，提取架构文档

各 Sub-agent 完成 → 回传压缩后的上下文给 Opus
Opus 主会话 整合 → 做出决策或生成方案
```

### 为什么用 Haiku 而不是 Opus

Haiku 的特点是**速度极快、处理大量 token 效率高**，但推理深度有限。它的任务是「快速扫完一大段代码，把有用的部分提取回来」，而不是做复杂推理。

这解决了一个核心矛盾：
- **上下文窗口有限**：不能把整个代码库都塞进去
- **但代码库很大**：需要知道结构才能做出正确决策
- **解决方案**：用 Haiku 并行扫描多个区域，然后回传压缩后的上下文

Calvin 原话："The explore tool uses Haiku so it is very fast at processing a lot of tokens, and handing the relevant context back to Opus."

### 这个架构的工程启示

| 维度 | 启示 |
|------|------|
| **模型分级使用** | 不是所有任务都需要最强模型；用 Haiku 做 bulk scanning，用 Opus 做决策 |
| **上下文压缩是 lossy 的** | 在决定压缩什么的时候，模型可能做出错误选择，导致遗漏关键信息 |
| **Sub-agent 应该有独立上下文窗口** | Claude Code 的 `context: fork` 可以让 skill 在新上下文窗口运行，避免主会话被撑爆 |
| **并行 vs 串行的权衡** | 并行启动多个 sub-agent 提升了吞吐量，但增加了复杂度（结果汇总、冲突处理） |

---

## 核心判断 3：Codex 代码正确性显著优于 Opus

这是文章中最有力的工程对比结论。Calvin 运行了多次 A/B 测试，对比 Claude Code 和 Codex 在相同任务上的代码输出质量，然后用 Cursor Bugbot 和自动化 Code Review 做验证。

### 发现的问题模式

Opus 常见的问题（Codex 明显更少）：

- **遗忘顶层组件挂载**：写了 React 组件，通过单元测试，但忘了加到 `<App>` 根组件
- **Off-by-one 错误**：循环边界、条件判断的细微偏差
- **Dangling references**：引用了已删除或未定义的变量
- **Race conditions**：并发场景下的同步问题，不容易在简单测试中捕获

### 代码

```python
# 验证方法：Claude Code vs Codex A/B test
# 1. checkout a branch
# 2. run /code-review in Claude Code → record bugs
# 3. run /review in Codex → record bugs
# 4. 对比两个输出

# Calvin 的结论：
# Codex 输出的 bug 显著更少
# 如果预算受限，选 Codex
```

### 为什么训练数据差异导致这个差距

Calvin 明确指出这是**训练数据差异**导致的，而非工程实现（harness）差异：

- **Opus（Claude）**：训练更多面向「通用智能」和「工具使用」，代码正确性是副产品
- **Codex（OpenAI）**：专门针对编程任务优化，在代码补全、代码修复任务上的 RL 强度更高

> "Both models have different strengths and weaknesses related to their training mix."

这意味着这不是可以通过 prompt engineering 弥补的差距，而是模型本身能力边界的体现。

---

## 核心判断 4：上下文窗口管理是决定性工程问题

Calvin 用了一整节讲上下文窗口的重要性，并称之为 "guiding principles"。

### 五条核心原则

**1. 问题太大时模型会 spin 然后给出糟糕结果**

当一个任务超出上下文窗口容量时，模型会做大量的 token 压缩（compaction），这个过程是 lossy 的——模型决定保留什么、丢弃什么，这个决策本身就可能出错。

**2. Compaction 是 lossy 技术**

当上下文快要满时，模型需要「摘要化」之前的内容。这个过程不可逆地丢失信息。更多的 compaction → 更大的性能 degradation。

**3. 外化上下文到文件系统**

把计划、进度、结构化文档放在文件系统而非对话历史中，Agent 可以选择性读取，不需要全部塞进上下文。

```python
# 外化上下文的目录结构示例
plans/
    ├── 00034-add-user-auth.md
    ├── 00035-fix-session-bug.md
    └── ...

# Agent 读取时只需要读对应文件
# 而不是在对话中保留所有历史 context
```

**4. 保持在上下文窗口的「聪明区」（Stay in the smart half）**

短上下文数据比长上下文数据更容易训练。模型在上下文窗口填充较少时表现更好。Dex Horthy 称之为 ["dumb zone"](https://www.youtube.com/watch?v=rmvDxxNubIg&t=355s)。

**5. 你不知道你不知道的（Unknown unknowns）**

如果 Agent 遗漏了一个关键文件或 package，它可能走向完全错误的方向。因为这个信息不在上下文中，Agent 也没有办法知道自己不知道。

### 上下文窗口管理的工程建议

| 做法 | 说明 |
|------|------|
| 保持上下文窗口低于 50% | 留出「聪明区」，模型表现更好 |
| 用文件系统外化计划 | 不要把所有中间状态放在对话历史里 |
| 分 chunk 做任务 | 大任务拆成小阶段，每个阶段在上下文窗口内 |
| 用 `context: fork` 分离 sub-agent | sub-agent 在独立上下文运行，不污染主会话 |
| 定期开新会话而非累积历史 | 旧会话历史积累导致每个新 turn 成本更高 |

---

## 核心判断 5：Skills 是比 MCP 更高效的上下文机制

Calvin 在文章中对比了 Skills 和 MCP，发现：

- **MCP 调用**：每次调用消耗数千 token
- **Skill 调用**：通常只消耗 50-100 token

### 为什么 Skills 更高效

Skills 本质上是**预定义的 prompt 片段**，在调用时注入，而非实时从外部工具获取数据。当工作流是固定的、可预期的，Skills 比 MCP 的灵活性更有价值。

### Skills 的两个核心用途

**用途 1：工作流自动化**

```
/commit     → 提交并推送
/worktree   → 创建新 worktree（分支）
/implement  → 执行计划的下一步，然后 /commit
/implement-all → 执行所有计划阶段
/address-bugs → 读取 GitHub API，查找 Cursor + Codex 的 bug 报告，尝试修复
/pr-pass   → 推送 → 等 CI 通过 → /address-bugs → 循环直到通过
```

**用途 2：拆分上下文窗口**

Claude Code 的 `context: fork` 允许在**新上下文窗口**中调用 skill，而不是在当前会话中。这意味着：

- 主会话（Orchestrator）：维护整体计划和状态
- Sub-agent sessions：并行执行子任务，输出结果后关闭
- 不污染主会话的上下文窗口

```yaml
# skill 定义中的 context: fork 示例
name: implement
description: Execute the next stage of the plan
context: fork  # 在新上下文窗口运行
prompt: |
  Read the current plan file ...
  Execute the next unchecked stage ...
```

---

## 实战工作流：Calvin 的完整 Agent 使用栈

### 日常开发配置

- **终端**：Ghostty（Mitchellh 的终端，native，快）
- **Monorepo**：Turborepo + Bun（fast installs）
- **分支策略**：用 Git worktrees 做并行开发，不用传统分支
- **部署**：每个 branch 有独立的 Preview deploy（Vercel Web + Cloudflare Durable Objects API）

### 工作流循环

```
1. 用 Claude Code + Opus 做计划
   - 创建 plans/00034-xxx.md
   - 描述目标、阶段划分

2. 用 Claude Code 开 worktree
   - /worktree skill：创建新 worktree，分支名 = plan 编号

3. 用 Claude Code 的 /implement-all 执行计划
   - 自动分阶段执行
   - 每个阶段后 /commit

4. 阶段完成 → 切换到 Codex 写代码
   - Codex 代码正确性更高
   - 用 Codex 的 /review 做 code review

5. CI 运行 → Cursor Bugbot + Codex 检查 bug
   - /address-bugs skill：自动读取 GitHub API bug 报告

6. PR 通过 → /pr-pass 自动合并
```

### 关键洞察：这个工作流不是设计出来的，是演化出来的

> "Importantly, I don't think I would've had any success trying to start with this process. But by building it over time and noticing little areas where I could automate, it's significantly improved my workflow."

Skills 的积累是渐进式的：先手动做，发现规律后 skill 化，然后发现 skill 可以组合，最终形成 /pr-pass 这样的元 skill。

---

## 给厂商的产品建议

### 给 Anthropic 的建议

| 建议 | 理由 |
|------|------|
| **"Opus Strict" 模式** | 用户需要 RL 强化训练后的代码正确性版 Opus；当下来说，Opus 创意强但代码 bug 多 |
| **采用 Agent Skills 标准**（agentskills.io） | 不需要每个工具维护自己一套 skills 目录，跨 CLI 工具共享 |
| **发布 --stream-json 的输出格式规范** | 第三方需要稳定格式来构建 sandbox 环境；当前格式可能会变 |

### 给 OpenAI 的建议

| 建议 | 理由 |
|------|------|
| **#1 优先级：上下文窗口拆分和 sub-agent 委托** | 这是 Codex 和 Claude Code 最大的体验差距；Haiku parallel sub-agent 架构值得借鉴 |
| **简化 sandbox 审批流程** | Codex 的模型「Determined」特性导致频繁要求用户审批，用户不敢开 --yolo |
| **支持 context: fork** | 让 sub-agent 在独立上下文运行，避免主会话被撑爆 |
| **把 /review 做成动态可调用的 skill** | 当前是打包命令形式，不够灵活 |

---

## 工程启示总结

### 认知框架层面

1. **时间是最优的 Agent 选择变量**：不是选最强的模型，而是选最适合剩余时间的工具
2. **上下文窗口是稀缺资源**：所有架构设计都围绕如何高效利用上下文窗口
3. **代码正确性 vs 创意能力是可以分开的**：Opus 和 Codex 的训练目标不同，导致能力分化；未来可能出现「Opus Strict」这样的专项优化版本

### 架构设计层面

1. **并行 sub-agent + 快子模型（Haiku）做探索层**：这是解决「大代码库 + 小上下文窗口」矛盾的标准解法
2. **Skills 是比 MCP 更轻量的工作流复用机制**：50-100 tokens vs 数千 tokens
3. **外化上下文到文件系统**：让 Agent 主动读取，而非塞满对话历史
4. **Worktree 做并行开发**：每个 worktree 是独立的上下文空间，不污染主开发分支

### 工程实践层面

1. **Claude Code + Codex 组合使用**：用 Claude Code 计划/探索，用 Codex 实现/验证
2. **自动化你的工作流**：先手动做，规律出现后 skill 化，然后组合
3. **保持上下文窗口低于 50%**：留出「聪明区」，模型推理质量更高
4. **A/B 测试不同 Agent 的输出质量**：Calvin 的方法——用 Cursor Bugbot + Codex 做自动化验证对比

---

## 关联阅读

- [Coding Agents in Feb 2026](https://calv.info/agents-feb-2026)（原文）
- [YC Lightcone Podcast](https://www.youtube.com/watch?v=qwmmWzPnhog)（Calvin 参与的 Podcast 讨论）
- [Claude Code Sub-agents 文档](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Dex Horthy - "Stay out of the dumb zone"](https://www.youtube.com/watch?v=rmvDxxNubIg&t=355s)
