# OpenClaw AWD Arena：多 Agent 攻防演练平台

> 本文推荐 LYiHub/OpenClaw-AWD-Arena，一个 71 Stars 的多 Agent 自动化攻防平台，用 Docker 容器隔离 + FastAPI 裁判引擎 + React 观战前端，让多个 LLM Agent 在防御期和交战期中进行实时对抗。

## 核心定位

**T - Target（谁该关注）**

- 对多 Agent 协作有兴趣的开发者，特别是想理解「Agent 在竞争环境下如何决策」的工程师
- 安全研究领域对 Agent 对抗感兴趣的研究者
- 想在自己的 Agent 项目中引入「红蓝对抗」测试的开发团队

**R - Result（能带来什么）**

- 将抽象的 Multi-Agent 协作问题具象化为可观测的攻防游戏
- 72 小时内部署一套完整的多 Agent 对抗环境，包含前后端 + Docker 容器编排
- 通过实时排行榜和日志回放，快速理解不同模型/策略在对抗中的表现差异

**I - Insight（凭什么做到）**

- **容器级隔离**：每个 Agent 运行在独立 Docker 容器中（Agent Gateway），防止相互干扰
- **两阶段赛制**：防御期（Agent 加固靶机）+ 交战期（Agent 互相攻击夺 Flag），模拟真实 AWD 场景
- **轮次编排器**：动态创建/销毁容器实例，根据配置自动管理比赛生命周期
- **FastAPI 裁判引擎**：接收前端配置、管控比赛流程、计算分数、监听 Agent 状态

**P - Proof（谁来用、热度如何）**

- 71 Stars，17 Forks，2026-05-09 创建
- 基于 OpenClaw（Alpine Linux + OpenClaw Agent）
- Docker + Docker Compose 部署，最少 4核 CPU + 8GB 内存

---

## 场景锚定

想象这样一个场景：你想测试 Claude Code 和 Codex 在「被攻击时」谁更能保护自己。

传统的测试方法是模拟各种攻击场景，但这种测试很难量化。**OpenClaw AWD Arena 提供了另一种思路：让 Agent 真正进入竞争环境，通过攻击他人和防守自己的行为来判断「哪个 Agent 更健壮」。**

---

## 技术架构

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                      观战前端 (React)                        │
│         配置大厅 | 模板管理 | 实时大屏观战 | 历史记录          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   裁判引擎 (FastAPI)                        │
│  - 接收前端配置                                              │
│  - 管控比赛流程 (创建/销毁容器实例)                          │
│  - 计算分数                                                  │
│  - 监听 Agent 状态                                          │
│  - 轮次编排器 (Round Orchestrator)                           │
└─────────────────────────────────────────────────────────────┘
              │                                    │
              ▼                                    ▼
   ┌──────────────────┐                ┌──────────────────┐
   │  Agent Gateway    │   ... ...      │  Agent Gateway   │
   │  (Docker容器)     │                │  (Docker容器)     │
   │  alpine/openclaw  │                │  alpine/openclaw  │
   └──────────────────┘                └──────────────────┘
              │                                    │
              ▼                                    ▼
   ┌──────────────────┐                ┌──────────────────┐
   │   靶机容器        │                │   靶机容器        │
   │ openclaw/ctf-target │            │ openclaw/ctf-target │
   └──────────────────┘                └──────────────────┘
```

### 关键设计决策

**决策一：Docker-in-Docker 的容器编排**

裁判引擎容器挂载了宿主机的 `/var/run/docker.sock`，使其能够在容器内部创建和管理其他 Docker 容器：

```yaml
# docker-compose.yml 关键配置
referee-engine:
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock  # 容器内管理 Docker
    - referee_data:/app/data
  environment:
    - OPENCLAW_DB_PATH=/app/data/openclaw.db
```

这种设计的优势是裁判引擎可以完全控制容器的生命周期，劣势是容器逃逸风险较高。README 中提到生产环境需要配置 `REFEREE_API_KEY` 进行接口鉴权。

**决策二：两阶段攻防赛制**

比赛分为两个阶段：

| 阶段 | Agent 行为 | 目标 |
|------|-----------|------|
| 防御期 | 加固靶机（打补丁、修配置） | 减少被攻击面 |
| 交战期 | 攻击其他 Agent + 防守自己 | 夺取 Flag + 保护 Flag |

两阶段赛制将「安全性」和「攻击性」分开评估，可以更清晰地看出不同 Agent 在攻守两端的策略差异。

**决策三：容器隔离的多 Agent 模型**

每个参赛 Agent 运行在独立容器中，通过 Alpine Linux + OpenClaw Agent 镜像提供一致的运行环境。这意味着可以同时运行 Claude Code、Codex、Gemini 等不同 Agent 在同一环境中对抗。

---

## 实测体验

### 部署流程（3 步）

```bash
# Step 1: 克隆代码
git clone https://github.com/LYiHub/OpenClaw-AWD-Arena.git
cd OpenClaw-AWD-Arena

# Step 2: 构建靶机镜像
cd target-image/ctf
docker build -t openclaw/ctf-target:v1 .
cd ../..

# Step 3: 一键启动
docker-compose up -d --build
```

启动后访问 `http://localhost:8000` 即可进入配置大厅。

### 比赛配置

```json
{
  "match_config": {
    "total_duration": 60,      // 比赛总时长（分钟）
    "defense_duration": 15,    // 防御期时长（分钟）
  },
  "llm_config": {
    "provider": "anthropic",   // 或 openai
    "api_key": "sk-...",
    "base_url": "https://api.anthropic.com"
  },
  "players": [
    {"id": 1, "model": "claude-3-opus-20240229"},
    {"id": 2, "model": "gpt-5.2"},
    {"id": 3, "model": "claude-3-sonnet-20240229"},
    {"id": 4, "model": "gpt-5.1"}
  ]
}
```

### 观战大屏

比赛开始后自动进入实时观战大屏，可以监控：
- 各选手得分排行榜
- Flag 被攻陷的实时播报
- 容器资源（CPU/内存）使用状态

---

## 与文章的关联

**本文推荐的项目与 Article「Cursor Self-Driving Codebases」形成互补关系**：

| 维度 | Cursor Self-Driving Codebases | OpenClaw AWD Arena |
|------|------------------------------|-------------------|
| 核心问题 | 多 Agent 如何协作完成任务 | 多 Agent 如何在竞争中决策 |
| 协调方式 | Planner-Executor-Worker 角色分层 | 防御期 + 交战期 两阶段赛制 |
| 失败场景 | 锁竞争导致吞吐量坍缩 | 攻击方夺 Flag，守方丢分 |
| 观察重点 | 任务完成率、执行效率 | 攻击/防御策略、安全性 |
| 适用场景 | 协同开发、长程任务 | 安全评测、红蓝对抗 |

> 笔者认为：两者共同揭示了一个核心洞察——**多 Agent 系统的问题不只是「如何完成任务」，还有「如何在资源竞争/外部压力下做出正确决策」**。Cursor 研究的是协作问题，OpenClaw AWD Arena 研究的是对抗问题，两者结合才能完整理解多 Agent 系统的复杂性。

---

## 快速开始

```bash
# 验证裁判引擎健康状态
curl http://localhost:8000/health
# 预期: {"status": "ok"}

# 查看容器运行状态
docker-compose ps

# 查看编排器日志（如果比赛启动失败）
docker logs openclaw-referee
```

---

## 局限性

1. **安全风险**：裁判引擎挂载了宿主机 Docker socket，容器逃逸可能性存在
2. **模型配置复杂度**：需要手动配置每个 Agent 的 API Key 和 Base URL
3. **靶机复杂度**：当前靶机是 CTF 风格漏洞服务，如何扩展到「代码仓库」场景需要进一步研究

---

## 引用来源

> "裁判引擎（Referee Engine）是系统的后端核心（FastAPI 实现），负责接收前端配置，管控比赛流程、计算分数，以及监听所有 Agent 的状态。"
> — [LYiHub/OpenClaw-AWD-Arena README](https://github.com/LYiHub/OpenClaw-AWD-Arena)

> "选手/Agent 镜像即参赛的 AI Agent（默认为 alpine/openclaw:latest），在比赛时以独立 Docker 容器（Agent Gateway）运行。"
> — [LYiHub/OpenClaw-AWD-Arena README](https://github.com/LYiHub/OpenClaw-AWD-Arena)

> "防御期 Agent 负责加固靶机，交战期开始进行互相攻击并夺取 Flag。"
> — [LYiHub/OpenClaw-AWD-Arena README](https://github.com/LYiHub/OpenClaw-AWD-Arena)