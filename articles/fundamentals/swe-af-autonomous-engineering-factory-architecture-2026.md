# SWE-AF：自主工程团队的架构解析

**核心主张**：SWE-AF（Software Engineering Autonomous Factory）将多角色 Agent 协作从「多个单 Agent 串行调用」升级为「三层控制闭环的工厂架构」——Planner/Worker/Governance 不是简单的 Prompt 分离，而是编码了真实工程策略的控制栈。这与 Cursor 第三时代的「工厂思维」形成闭环：Cursor 定义了人机交互的新范式，SWE-AF 提供了该范式的开源工程实现。

**读者画像**：有 Agent 开发经验，了解基本的多 Agent 编排概念，但尚未深入理解「工厂级 Agent 编排」与「单 Agent Wrapper」的本质差异。

**核心障碍**：市面上的 Agent 框架大多是「单 Agent 循环包装」，将多 Agent 协作简化为「轮流调用」。当面对需要真实工程策略（优先级排序、依赖解析、适应性重规划）的复杂任务时，这类框架无法提供可预测的输出。

---

## 1. 背景：为什么需要「工厂级」Agent 编排

### 1.1 单 Agent Wrapper 的根本局限

大多数 Agent 框架的工作模式是：给定一个目标 → 调用单 Agent 循环 → 返回结果。这种模式在简单任务上有效，但存在三个根本问题：

**问题一：任务难度与重试次数成正比**

当任务失败时，单 Agent Wrapper 的策略是「用同样的方法重试更多次」或「接受失败」。它无法识别任务失败是因为「方法错误」还是「任务本身太难」。

**问题二：任务之间无依赖建模**

当一个目标需要拆解为多个子任务时，单 Agent Wrapper 无法建模：
- 哪些子任务可以并行
- 哪些子任务必须串行
- 一个子任务失败时，哪些其他子任务需要取消或重新规划

**问题三：无法区分「实现」与「验收」**

单 Agent 同时处理代码编写和测试验证，两种行为在同一个上下文中竞争资源，导致两者都无法做好。

> "Most agent frameworks wrap a single coder loop. SWE-AF is a coordinated engineering factory — planning, execution, and governance agents run as a control stack that adapts in real time."
> — [SWE-AF README](https://github.com/Agent-Field/SWE-AF)

---

## 2. 工厂架构：三环控制栈

SWE-AF 的核心架构是**三层嵌套控制闭环**，每一层有不同的触发条件和响应策略。

### 2.1 三层控制环

| 层级 | 作用域 | 触发条件 | 响应策略 |
|------|--------|---------|---------|
| Inner Loop | 单个 Issue | QA/Review 失败 | Coder 根据反馈重试 |
| Middle Loop | 单个 Issue | Inner Loop 耗尽 | `run_issue_advisor` 换方法、分拆或带债接受 |
| Outer Loop | 剩余 DAG | 升级失败 | `run_replanner` 重构剩余问题和依赖关系 |

三层控制环的本质是将「工程判断」编码为 Agent 行为，而不是依赖 Prompt 工程的偶然成功。

### 2.2 控制栈的工程逻辑

```
┌─────────────────────────────────────────────────────────────┐
│  Outer Loop: run_replanner                                  │
│  ─────────────────────────────────────────────────────     │
│  当 Inner + Middle 循环都无法解决时触发                       │
│  行为：重构剩余 DAG，修改依赖关系，可能回滚已完成的工作       │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Middle Loop: run_issue_advisor                        │  │
│  │  ─────────────────────────────────────────────────    │  │
│  │  当 Inner 循环耗尽仍失败时触发                          │  │
│  │  行为：换方法、分拆 Issue、接受 Debt 并记录类型和严重度  │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Inner Loop: Coder + QA + Review                 │  │  │
│  │  │  ───────────────────────────────────────────    │  │  │
│  │  │  触发：QA/Review 失败                            │  │  │
│  │  │  行为：Coder 根据反馈重试                        │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

这种设计的工程含义：
- **不是无限重试**：每层有明确的退出条件，避免在错误路径上浪费资源
- **Debt 可追踪**：当选择「带债接受」时，Debt 被分类（类型+严重度）并传播
- **Outer Loop 保护**：当剩余 DAG 的依赖被破坏时，触发全局重规划而非局部修复

### 2.3 单 Agent Wrapper vs 三环控制栈

| 维度 | 单 Agent Wrapper | SWE-AF 三环控制栈 |
|------|-----------------|------------------|
| 失败处理 | 重试（等概率成功） | 诊断 + 换方法/分拆/带债 |
| 任务依赖 | 无建模 | DAG 建模 + 并行调度 |
| 资源分配 | 平均分配 | 按难度自适应 |
| 进度透明度 | 黑盒 | Checkpoint + 可 resume |
| 规模行为 | 退化（任务越多越慢） | 线性扩展（Agent 并行） |

---

## 3. 角色分工：PM + Architect + Coder + QA + Merger

SWE-AF 不是「一个全能的 Coding Agent」，而是**多个专业角色的组合**。每个角色有明确的输入/输出规范和决策边界。

### 3.1 角色配置示例

```json
{
  "config": {
    "runtime": "claude_code",
    "models": {
      "default": "sonnet",
      "coder": "opus",
      "qa": "opus",
      "architect": "sonnet"
    }
  }
}
```

关键设计：**不同角色可以使用不同模型**。代码生成用 Opus（强推理），架构规划用 Sonnet（性价比），QA 验证用 Opus（高精度）。

### 3.2 角色职责矩阵

| 角色 | 输入 | 输出 | 决策边界 |
|------|------|------|---------|
| PM | Goal + PRD | Issue List + 优先级 | 范围划分、优先级排序 |
| Architect | Issue + 上下文 | 技术方案 + 依赖图 | 技术选型、接口设计 |
| Coder | Issue + 方案 | 代码变更 + 自测结果 | 实现细节、代码风格 |
| QA | 代码变更 + 测试目标 | 测试结果 + 回归分析 | 测试覆盖度、失败分类 |
| Reviewer | 代码变更 | Review 意见 + Approval | 代码质量门禁 |
| Merger | 多个 Approval | 合并 PR | 合并策略、冲突解决 |

### 3.3 Multi-Model 的实际价值

SWE-AF 的文档中提到一个案例：用 `claude-haiku-4-5` 运行完整流程，79 次 Agent 调用，总成本 $19.23。

> "79 invocations, 2,070 conversation turns. Planning agents scope and decompose; coders work in parallel isolated worktrees; reviewers and QA validate each issue; merger integrates branches; verifier checks acceptance criteria against the PRD."
> — [SWE-AF README: PR #179 Case Study](https://github.com/Agent-Field/SWE-AF)

这说明**模型选择是工程决策**，不是「越贵越好」：
- 简单任务用 Haiku（成本 ~$0.1/1K tokens）
- 复杂任务用 Opus（成本 ~$15/1M tokens）
- 按角色分配模型，整体成本可降低 10x 而不牺牲质量

---

## 4. 关键工程实现：Git Worktree 隔离并行

### 4.1 为什么需要 Worktree 隔离

多 Agent 并行编程的经典问题是**分支冲突**：多个 Agent 同时修改同一个文件的不同部分，导致合并时出现大量冲突。

传统解决方案：
- 串行执行（慢）
- 粗粒度文件锁（粒度太大）
- 人工协调（贵）

SWE-AF 的方案：**Git Worktree 隔离**。每个 Agent 在独立的 Git Worktree 中工作，文件系统级别隔离，无冲突。

### 4.2 Worktree + DAG 调度的协同

```
Issue DAG:
  Issue-1 ──┬── Issue-3 ── Issue-5
  Issue-2 ──┘       └────── Issue-6

Worktree 分配：
  Worktree-1: Issue-1, Issue-3 (串行，同一分支)
  Worktree-2: Issue-2 (独立分支)
  Worktree-3: Issue-5, Issue-6 (串行，同一分支)
```

依赖关系在 DAG 层处理，分支隔离在文件系统层处理，两层关注点分离。

### 4.3 合并策略

当多个 Worktree 完成时，Merger Agent 负责：
1. 按依赖顺序依次合并（Issue-1/2 → Issue-3 → Issue-5/6）
2. 解决合并冲突（通常发生在 Issue-3 和 Issue-5 修改了同一文件的相邻区域）
3. 验证合并后的 CI

---

## 5. 持续学习：enable_learning=true

SWE-AF 的 `enable_learning=true` 配置开启了**跨任务的经验积累**。

### 5.1 学习什么

| 学习内容 | 来源 | 注入目标 |
|---------|------|---------|
| 代码规范 | Code Review 拒绝原因 | 新 Issue 的 Coder Prompt |
| 失败模式 | Middle Loop 决策记录 | Issue Advisor 的决策树 |
| 依赖经验 | Outer Loop 重规划记录 | DAG 优先级排序 |
| 工具偏好 | Agent 调用日志 | 工具选择策略 |

### 5.2 学习机制

```
每次 Issue 完成 → 提取经验 → 更新知识库 → 下次 Issue 注入
```

不是「记住答案」，而是**记住决策模式**——当类似的上下文再次出现时，Agent 知道优先尝试什么方法。

> "With `enable_learning=true`, conventions and failure patterns discovered early are injected into downstream issues."
> — [SWE-AF README](https://github.com/Agent-Field/SWE-AF)

### 5.3 学习的边界

SWE-AF 的学习机制有明确的边界：
- **不学习业务逻辑**：业务逻辑必须来自 PRD，不来自历史经验
- **不学习个人信息**：不存储密码、密钥、个人数据
- **可审计**：所有学习内容可追溯到原始决策记录

---

## 6. 与 Cursor 第三时代的理论呼应

Cursor 第三时代定义了「工厂思维」：**人类定义问题边界，Agent 自主执行**。SWE-AF 是该范式的工程实现：

| 维度 | Cursor 第三时代 | SWE-AF 工厂架构 |
|------|---------------|----------------|
| 人类角色 | 定义问题 + 验收标准 | PM 定义 Scope + Architect 建模 |
| Agent 协作 | 多 Agent 并行 | 多角色 Worktree 并行 |
| 评估媒介 | Artifacts（截图/录屏） | QA 测试 + Acceptance Criteria |
| 失败处理 | 多 Agent 不互相阻塞 | Inner→Middle→Outer 三环处理 |
| 状态管理 | Cloud ↔ Local 无缝 Handoff | Checkpoint + resume_build |
| 规模化 | 35% PR 由 Cloud Agents 创建 | Fleet-scale 并行（AgentField）|

两者共同指向的方向：**软件工程的生产力瓶颈从「代码生成速度」转移到「问题分解质量」**。

---

## 7. 适用边界与已知局限

### 7.1 SWE-AF 的适用场景

| 场景 | 适用度 | 原因 |
|------|--------|------|
| 复杂多 Issue PR | ★★★★★ | DAG 建模 + 多角色分工 |
| 需要跨 Repo 修改 | ★★★★☆ | Multi-Repo 模式原生支持 |
| 快速原型验证 | ★★☆☆☆ | 启动开销较高 |
| Bug 修复 | ★★☆☆☆ | 粒度太小，工厂开销不划算 |
| 绿色字段项目 | ★★★★☆ | PM + Architect 角色充分发挥 |

### 7.2 已知局限

**局限一：PM 角色依赖 PRD 质量**

SWE-AF 的输出质量高度依赖输入的 PRD（Product Requirements Document）。如果 PRD 模糊或不完整，PM 的 Issue 分解会反映这些问题。

**局限二：Outer Loop 重规划成本高**

当 Outer Loop 触发时，意味着整个剩余 DAG 需要重构。这可能导致：
- 已完成的部分 Issue 需要回滚
- 新的 Issue 依赖关系可能推翻之前的决策
- 整体进度可能倒退

**局限三：模型成本可预期但总量不可预期**

每个 Issue 的 Agent 调用次数取决于难度。复杂 Issue 可能触发 Middle Loop 甚至 Outer Loop，导致单个 Issue 的成本可能是预期的 3-5 倍。

> 笔者认为：SWE-AF 的定位是「工程团队增强」而非「替代工程师」。它的价值在于处理「大量中等复杂度的 Issue」——当你有 50 个 Feature Request 需要实现时，SWE-AF 可以把人从「逐一实现」的负担中解放出来，专注于「定义做什么」和「验证做得对不对」。

---

## 8. 结论与启示

SWE-AF 的三层控制闭环揭示了一个关键洞察：**多 Agent 编排的本质不是「调用更多 Agent」，而是「为不同难度的任务配置不同的控制策略」**。

对于 Agent 开发者的启示：
1. **任务分解先于 Agent 调用**：在调用 Agent 之前，先建模任务的难度分布和依赖关系
2. **控制策略是工程问题**：重试次数、退出条件、Debt 策略都需要显式设计
3. **按角色分配模型是成本优化的关键**：不是所有任务都需要 Opus

对于 Agent 框架开发者的启示：
1. **单 Agent Wrapper 是原型阶段的妥协**：生产级系统需要控制栈
2. **学习机制需要边界**：不是所有经验都值得积累
3. **Git Worktree 隔离是并行 Agent 的工程基础**：没有文件系统隔离，任何「并行」都是伪并行

---

*来源：[SWE-AF GitHub README](https://github.com/Agent-Field/SWE-AF)、[AgentField Platform](https://github.com/Agent-Field)*
