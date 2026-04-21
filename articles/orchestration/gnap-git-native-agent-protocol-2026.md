# GNAP：Git 作为多 Agent 协作的无服务器协调层

> 多个 AI Agent 如何围绕同一个代码库协作？当它们不在同一台机器上、没有共享数据库、也无法访问同一个消息队列时，协作如何实现？GNAP（Git-Native Agent Protocol）给出了一个反直觉的答案：用一个存在了几十年的版本控制系统——Git——作为 Agent 之间共享任务、传递消息、追踪执行历史的协调总线。

## 痛点：多 Agent 协作的基础设施困境

当前多 Agent 协作方案面临一个共同的基础设施门槛：

| 方案 | 必须依赖 |
|------|---------|
| CrewAI / LangGraph | 内存或数据库 |
| Microsoft Agent Framework | 服务端组件（.NET/Python 运行时）|
| AgentScope Distributed | gRPC 服务器 + Service Mesh |
| OpenHands SDK | 数据库 |
| AgentHub / Paperclip | PostgreSQL / SQLite |

这些方案的共同问题是：**协作依赖额外的服务端组件**。在以下场景中，这个门槛就成了障碍：

- **跨时区异步协作**：各 Agent 运行在不同地理位置、不同时间区间
- **异构基础设施**：前端的 Codex、后端的 OpenClaw、本地的 Claude Code，各自运行环境不同
- **离线优先**：CI Worker、临时虚拟机等无法持续连接的场景
- **最小化运维**：不想维护任何服务端，只想专注业务逻辑

GNAP 试图回答的问题是：**能否用已经存在于每个代码仓库里的 Git，作为这个协调层的实现？**

---

## 核心设计：Git 作为协调总线

### 为什么是 Git 而不是消息队列

消息队列（RabbitMQ、Kafka）是典型的「中心辐射型」架构——所有 Agent 必须连接到同一个Broker，一旦 Broker 宕机，整个协作系统崩溃。

Git 的分布式模型天然避免了单点故障。在 GNAP 的设计里：

- **每个 Agent 持有协作空间的完整副本**（.gnap/ 目录）
- **git push/pull 即完成同步**——不需要额外的消息中间件
- **Git 历史天然就是审计日志**——无需单独接入 Prometheus/Grafana

GNAP 的核心断言是：**协作的最小基础设施，就是一个 Git 仓库**。对于已经在使用 Git 管理代码的团队，这意味着零额外运维成本。

### 协议架构

```
┌──────────────────────────────────────────────────┐
│  Application Layer（可选）                        │
│  budgets、dashboards、workflows、governance     │
├──────────────────────────────────────────────────┤
│  GNAP Protocol（协议层）                          │
│  agents · tasks · runs · messages               │
├──────────────────────────────────────────────────┤
│  Git（传输 + 存储层）                             │
│  push/pull · merge · history · distribution     │
└──────────────────────────────────────────────────┘
```

### 四个核心实体

GNAP 协议只定义了四个 JSON 文件类型，作为协调层的数据模型：

#### 1. agents.json —— 谁在团队里

```json
{
  "agents": [
    {
      "id": "carl",
      "name": "Carl",
      "role": "CRO",
      "type": "ai",
      "status": "active",
      "runtime": "openclaw",
      "heartbeat_sec": 300,
      "capabilities": ["billing", "stripe", "api-design"]
    },
    {
      "id": "leo",
      "name": "Leonid",
      "role": "CTO",
      "type": "human",
      "status": "active",
      "contact": { "email": "leo@example.com" }
    }
  ]
}
```

关键字段：
- `type`：ai | human —— **人类和 AI Agent 是一等公民**，没有区别对待
- `status`：active | paused | terminated —— 可以暂停某个 Agent 而不影响协作
- `runtime`：可选，标识 Agent 的运行时类型（openclaw / codex / claude / custom）
- `heartbeat_sec`：轮询间隔，默认 300 秒（5 分钟）

#### 2. tasks/*.json —— 什么需要做

每个任务一个文件，放在 `.gnap/tasks/` 目录下：

```json
{
  "id": "FA-1",
  "title": "Set up Stripe billing",
  "desc": "Create Stripe account and configure webhooks for the billing system",
  "assigned_to": ["carl"],
  "state": "in_progress",
  "priority": 0,
  "created_by": "leo",
  "created_at": "2026-03-12T11:40:00Z",
  "parent": null,
  "blocked": false,
  "reviewer": "leo",
  "tags": ["billing", "urgent"]
}
```

**状态机**（核心机制）：

```
backlog → ready → in_progress → review → done
   ↑         │
   │         └───────────────┘（reviewer 拒绝）
   │
blocked → ready（解除阻塞）
   │
   ↓
cancelled
```

关键理解：
- 一个任务可以有多次执行尝试（runs），但任务本身不因单次失败而终结
- `blocked` 字段让任务可以被显式暂停（等待依赖项完成）
- `reviewer` 字段支持人机协同审批流程

#### 3. runs/*.json —— 一次执行尝试

```json
{
  "id": "FA-1-1",
  "task": "FA-1",
  "agent": "carl",
  "state": "completed",
  "attempt": 1,
  "started_at": "2026-03-12T12:30:00Z",
  "finished_at": "2026-03-12T12:35:00Z",
  "tokens": { "input": 12400, "output": 3200 },
  "cost_usd": 0.08,
  "result": "Stripe account created, test mode live",
  "commits": ["a1b2c3d", "e4f5g6h"],
  "artifacts": ["stripe-config.json", "webhook-handler.py"]
}
```

**runs 的核心价值**：

| 能力 | 说明 |
|------|------|
| **成本追踪** | 每个任务的累计 cost_usd → 预算控制的基础 |
| **重试历史** | 失败后其他 Agent 可以开新 run，不丢失历史 |
| **性能基准** | 对比不同 Agent 的 speed / cost / success rate |
| **审计日志** | git commit SHA 直接关联到具体任务的执行 |

#### 4. messages/*.json —— Agent 间通信

```json
{
  "id": "1",
  "from": "leo",
  "to": ["carl"],
  "at": "2026-03-12T09:30:00Z",
  "type": "directive",
  "text": "Focus on billing first. Everything else can wait."
}
```

`type` 可以是 `directive`（指令）、`query`（询问）、`response`（响应）、`notification`（通知）。

### Agent 的心跳循环

每个 GNAP Agent 持续运行以下循环：

```
1. git pull                    # 拉取最新协作状态
2. Read agents.json           # 确认自己是否 active
3. Read tasks/                # 有没有分配给我的任务？
4. Read messages/              # 有没有发给我的消息？
5. Do the work                # 执行任务 → 写 runs/ → commit
6. git push                   # 推送结果
7. Sleep(heartbeat_sec)       # 等待下一轮
```

这个模型的关键特性：
- **完全无状态**：Agent 自身不需要存储任何协作状态，所有状态都在 .gnap/ 目录里
- **任意实现**：只要能执行 git push/pull，就能接入 GNAP 网络
- **离线安全**：Agent 可以断开网络连接工作，联网后 sync 即可

---

## 与现有方案的系统对比

| 维度 | AgentScope RPC | GNAP | CrewAI / LangGraph |
|------|---------------|------|---------------------|
| **基础设施** | gRPC 服务器 + Service Mesh | git init（零服务器）| 内存/In-memory |
| **数据库** | 无（RPC 直连）| 无（git 历史）| 无 |
| **审计日志** | 需要单独接入 | Git 历史自动提供 | 需要单独接入 |
| **人机协同** | 复杂（需额外接口）| 原生支持（human = 一等公民）| 困难 |
| **离线能力** | 无 | 完全支持 | 无 |
| **延迟** | 毫秒级 | 秒~分钟级（心跳间隔）| 取决于具体实现 |
| **适用场景** | 高吞吐实时系统 | 异步协作、长时任务 | 单进程内的 Agent 编排 |

**关键结论**：

GNAP 不是要替代 AgentScope 或 CrewAI，而是在它们的适用场景之外提供一个正交的选择。当任务的完成时间以分钟或小时计、Agent 运行环境异构、且需要完整的人类参与节点时，GNAP 的无服务器模型提供了最低的协作门槛。

---

## 工程接入：如何在现有项目中启用 GNAP

### 最小初始化

```bash
cd your-project
mkdir -p .gnap
cd .gnap

# 初始化协议版本
echo "4" > version

# 初始化团队
cat > agents.json << 'EOF'
{
  "agents": [
    {
      "id": "my-agent",
      "name": "My Agent",
      "role": "developer",
      "type": "ai",
      "status": "active",
      "runtime": "openclaw",
      "heartbeat_sec": 60
    }
  ]
}
EOF

mkdir -p tasks runs messages

git add .gnap
git commit -m "chore: initialize GNAP coordination layer"
```

### Agent SDK 接入（伪代码示例）

```python
import json
import subprocess
import time
from pathlib import Path

class GNAPAgent:
    def __init__(self, agent_id, repo_path=".gnap"):
        self.agent_id = agent_id
        self.repo = Path(repo_path)
    
    def heartbeat(self):
        # 1. sync
        subprocess.run(["git", "pull", "--rebase"], cwd=self.repo.parent)
        
        # 2. 读取分配给自己的任务
        tasks_dir = self.repo / "tasks"
        for task_file in tasks_dir.glob("*.json"):
            task = json.loads(task_file.read_text())
            if (self.agent_id in task.get("assigned_to", []) 
                    and task["state"] == "ready"):
                self._execute_task(task)
        
        # 3. 处理消息
        msgs_dir = self.repo / "messages"
        for msg_file in msgs_dir.glob("*.json"):
            msg = json.loads(msg_file.read_text())
            if self.agent_id in msg.get("to", []):
                self._handle_message(msg)
        
        # 4. push 结果
        subprocess.run(["git", "add", "."], cwd=self.repo.parent)
        subprocess.run(["git", "commit", "-m", 
                        f"chore: {self.agent_id} heartbeat"], 
                       cwd=self.repo.parent)
        subprocess.run(["git", "push"], cwd=self.repo.parent)
    
    def _execute_task(self, task):
        # 更新状态
        task["state"] = "in_progress"
        # ... 执行任务 ...
        task["state"] = "review"
        task["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        # 写回任务文件 + 创建 run 记录
```

---

## 适用边界与已知局限

### 应该用 GNAP 的场景

- **异步多 Agent 协作**，Agent 运行在不同机器、不同运行时
- **需要人类介入** 的工作流（review、approval）
- **最小化运维**，不想维护任何服务端组件
- **离线优先**，Agent 可能在无网络环境下工作一段时间
- **审计合规**，需要 git 级别的操作审计轨迹

### 不应该用 GNAP 的场景

- **毫秒级实时响应**：GNAP 的心跳模型（最短 60s，通常 300s）决定了它的延迟下限
- **高吞吐量并发**：大量同时进行的短任务，用 RPC 框架更合适
- **需要事务性**：Git 的 merge 模型无法提供 ACID 级别的一致性保证
- **无 Git 管理的基础设施**：纯无服务器环境（如某些 SaaS 平台）

### 当前已知局限

1. **冲突处理未标准化**：两个 Agent 同时修改同一个任务文件时，当前的解决方案是「后提交者负责 resolve」，没有自动冲突合并逻辑
2. **心跳开销**：大量 Agent 的高频心跳会产生 git push/pull 流量
3. **协议版本演进**：当前是 draft v4，没有版本协商机制（Agent 发现 version 不匹配时只能拒绝运行）
4. **安全模型不完善**：.gnap/ 目录包含任务和消息数据，没有细粒度的权限控制文档

---

## 工程判断：什么时候选 GNAP

GNAP 的出现填补了一个具体的技术空白：**当你的多 Agent 系统需要跨越异构运行时、在没有共享数据库的环境中协作时，GNAP 是目前唯一零基础设施的解决方案**。

它的核心价值主张不是「更好」，而是「更简单」——用 Git 替代消息队列 + 数据库 + 监控系统的组合，在合适的场景下能将协调层的搭建成本从数天降低到数十分钟。

> **工程建议**：如果你正在构建一个需要人类审批节点的多 Agent 软件开发工作流（如自动化的 PR review → 修改 → merge），GNAP 的 task/review 状态机和 human-as-agent 设计是当前框架中最低摩擦的选择。在更通用的异步任务场景中，它值得与 AgentScope 的 RPC 方案做一次针对具体业务的对比评估。

---

## 参考资料

- [GNAP — Git-Native Agent Protocol（GitHub 官方仓库）](https://github.com/farol-team/gnap) — 协议规范一手来源，包含完整 JSON Schema
- [Superpowers 项目中 GNAP 的应用场景](https://github.com/obra/superpowers/issues/736) — Architect Agent → Frontend/Backend/Test Agent 分发任务的协作模式实例
- [AgentScope 分布式部署的 GNAP 后端提案](https://github.com/agentscope-ai/agentscope/issues/1329) — AgentScope 团队对 GNAP 的技术评估与对比分析
- [Microsoft Agent Framework Issue #4715](https://github.com/microsoft/agent-framework/issues/4715) — 微软框架对 GNAP 作为跨语言 Agent 协调层的讨论
- [OpenHands 多 Agent 任务协调方案讨论](https://github.com/OpenHands/OpenHands/issues/13416) — OpenHands SDK 对 GNAP 的评估
