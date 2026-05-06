# SWE-AF × AgentField：自主工程团队的工业化实践

> 本文是 [SWE-AF 架构深度解析](../fundamentals/swe-af-autonomous-engineering-factory-architecture-2026.md) 的配套项目推荐，与该文形成「理论分析 + 工程实证」的闭环。

---

## T - Target

**谁该关注**：有实际生产需求的 Agent 开发者或平台工程师，已完成单 Agent 原型，面临「如何扩展到多 Issue 协作」的问题。至少需要：
- 了解基本的 Agent 概念和 Tool Use 模式
- 有 Python 3.12+ 开发环境
- 有 Claude Code CLI 或等效的 Agent Runtime
- 对「自动化流水线」有实际需求（而非技术兴趣）

**不适合**：刚入门 Agent 的新手（建议先玩单 Agent），或只需要「偶尔跑一个简单脚本」的场景。

---

## R - Result

SWE-AF 的核心价值可以用一句话概括：**一次 API 调用，完整工程团队，交付可合并的代码**。

关键数据（来自官方 PR 案例 #179）：

| 指标 | 数值 |
|------|------|
| 完成的 Issues | 10/10 |
| 通过测试 | 217 |
| 验收标准满足 | 34/34 |
| Agent 调用次数 | 79 |
| 使用模型 | `claude-haiku-4-5` |
| **总成本** | **$19.23** |

> "79 invocations, 2,070 conversation turns. Planning agents scope and decompose; coders work in parallel isolated worktrees; reviewers and QA validate each issue; merger integrates branches."
> — [SWE-AF README](https://github.com/Agent-Field/SWE-AF)

另一个案例：Rust-based Python Compiler benchmark，SWE-AF 驱动的 autonomous engineering team 实现了 **253.8x** 的吞吐量提升（CPython subprocess → RustPython in-process runtime）。

---

## I - Insight

SWE-AF 凭什么做到这些？三个核心设计决策：

### 决策一：三环控制栈替代无限重试

大多数 Agent 框架的失败处理是「重试 × N」。SWE-AF 的失败处理是**诊断 + 策略切换**：

- Inner Loop（单 Issue）：QA/Review 失败 → Coder 根据反馈重试
- Middle Loop（单 Issue 耗尽）：换方法、分拆 Issue、或带债接受
- Outer Loop（剩余 DAG 恶化）：全局重规划

> "Hardness-aware execution — easy issues pass through quickly, while hard issues trigger deeper adaptation and DAG-level replanning instead of blind retries."
> — [SWE-AF README](https://github.com/Agent-Field/SWE-AF)

这意味着 SWE-AF **编码了工程判断**，而不是靠「多试几次碰概率」。

### 决策二：Git Worktree 隔离实现真并行

多 Agent 并行的经典问题是「同时修改同一文件」。SWE-AF 用 Git Worktree 隔离每个 Agent 的工作目录，**文件系统级别保证无冲突**。

```
Worktree-1: Issue-1, Issue-3 (同一分支，串行)
Worktree-2: Issue-2 (独立分支)
Worktree-3: Issue-5, Issue-6 (同一分支，串行)
```

依赖关系在 DAG 层处理，分支隔离在文件系统层处理——**关注点分离**。

### 决策三：按角色分配模型

SWE-AF 不要求所有角色用同一个模型：

```json
{
  "models": {
    "default": "sonnet",
    "coder": "opus",
    "qa": "opus"
  }
}
```

代码生成用 Opus（高精度），架构规划用 Sonnet（性价比）。在 PR #179 案例中，用 `haiku-class` 模型跑完全程，79 次调用仅花 $19.23。

---

## P - Proof

**GitHub 数据**（来自官方 Repo）：

| 指标 | 数值 |
|------|------|
| GitHub Stars | 持续增长中 |
| 架构 | Apache 2.0 |
| Python 版本 | 3.12+ |
| 运行时支持 | Claude Code / OpenCode (OpenRouter/OpenAI/Google) |

**实际案例**：

1. **PR #179: Go SDK DID/VC Registration** — 完全由 SWE-AF 构建（Claude Haiku runtime），零人工代码参与
2. **RustPython Compiler Benchmark** — autonomous team 实现 253.8x 吞吐量提升
3. **AgentField Fleet Deployment** — 支持多个 SWE-AF 节点并行运行，驱动数千次并发 Agent 调用

**社区活跃度**：
- Agent-Field 组织下有多个相关 Repo（AgentField 控制平面、SWE-AF 核心、示例项目）
- 有完整的 Architecture 文档和 Quick Start

---

## P - Threshold（行动引导）

### 快速上手（Railway 部署，5 分钟）

1. 点击 Railway 部署按钮：`https://railway.com/deploy/swe-af`
2. 设置环境变量：
   - `CLAUDE_CODE_OAUTH_TOKEN` — 运行 `claude setup-token`
   - `GH_TOKEN` — GitHub PAT（需要 `repo` scope）
3. 触发第一次构建：

```bash
curl -X POST https://<control-plane>.up.railway.app/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -H "X-API-Key: this-is-a-secret" \
  -d '{"input": {"goal": "Add JWT auth", "repo_url": "https://github.com/user/my-repo"}}'
```

### 本地开发

```bash
# 1. 克隆
git clone https://github.com/Agent-Field/SWE-AF.git
cd SWE-AF

# 2. 创建虚拟环境
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. 启动控制平面 + SWE-AF 节点
af                                          # 控制平面 :8080
python -m swe_af                           # 注册节点

# 4. 触发构建
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d '{"input": {"goal": "Add JWT auth", "repo_url": "https://github.com/user/my-repo"}}'
```

### 适合贡献的场景

- 想学习多 Agent 架构：Architecture 文档写得非常详细
- 想扩展角色能力：角色定义在 `swe_af/roles/` 下，添加新角色只需几十行代码
- 想改进调度算法：核心调度逻辑在 `swe_af/scheduler/` 下

---

## 关联阅读

- [SWE-AF 架构深度解析](../fundamentals/swe-af-autonomous-engineering-factory-architecture-2026.md) — 三环控制栈、Git Worktree 隔离、持续学习的完整分析
- [Cursor 第三时代：人机协作范式转变](../fundamentals/cursor-third-era-cloud-agents-human-role-paradigm-shift-2026.md) — SWE-AF 的理论背景：为什么「工厂思维」是 Agent 发展的下一阶段
- [Anthropic 双组件 Harness](../orchestration/anthropic-managed-agents-brain-hands-decoupling-2026.md) — Initializer + Coding Agent 的双组件设计，与 SWE-AF 的角色分工形成跨框架印证

---

*项目地址：[Agent-Field/SWE-AF](https://github.com/Agent-Field/SWE-AF) | 协议：Apache 2.0*
