# iammm0/execgo — Agent Action Harness：Brain/Hands 架构的工程实现

> GitHub：https://github.com/iammm0/execgo | 8 Stars | Go 1.22+ | MIT License

## 一、Target：谁该关注？

**目标用户**：有 Go 后端开发经验的 Agent 工程团队，需要一个生产级的 Agent 执行内核（execution kernel / action harness）。

- 正在构建上层 Agent 编排层，需要可靠的任务执行与可观测性
- 需要将 Agent 决策映射到具体工具（shell / HTTP / MCP / CLI）
- 对安全和可恢复性有要求（指数退避重试 / DAG 调度 / 状态持久化）

**不适合**：只想用 Python 快速 demo 的场景，或需要完整 Agent 框架（包含 LLM 调用）的一体化方案。

---

## 二、Result：能带来什么？

ExecGo 作为 Agent 的"执行内核"，解决的是：上层 Agent 负责决策，下层系统负责可靠执行。

**具体改善**：
- **故障隔离**：容器崩溃不影响 Brain，harness 可重启恢复
- **DAG 编排**：Kahn 算法环检测 + 并发调度，任务依赖管理从手工变声明式
- **可观测性**：结构化 JSON 日志（slog）+ traceID + `/metrics` 端点
- **安全执行**：shell/file/dns/tcp/http 各工具的参数级控制

> "ExecGo 更适合被理解为一个面向 AI Agent 的执行内核（execution kernel / action harness），而不是一个纯通用工作流引擎。它的职责是把上层 agent 的决策，可靠、安全、可观测地映射到真实工具与运行环境。"
> — [execgo GitHub README](https://github.com/iammm0/execgo)

---

## 三、Insight：它凭什么做到这些？

### 1. 核心模块零第三方依赖

`github.com/iammm0/execgo` 核心仅依赖 Go 标准库，可选能力（SQLite 持久化、Redis 读穿缓存）放在 `contrib/*` 子模块。这意味着：
- 不绑架你的依赖树
- 容易嵌入任何 Go 后端

### 2. Task DSL + DAG 调度

```go
type Task struct {
    ID        string   // 任务唯一标识
    Type      string   // shell / file / http / mcp / cli-skills
    Params    map[string]any  // 类型特定参数
    DependsOn []string // 依赖的任务 ID
    Retry     int      // 指数退避重试次数
    Timeout   int      // ms
}
```

Kahn 算法环检测确保 DAG 有效；semaphore 控制最大并发。

### 3. 三类内置执行器

| 执行器 | 工具集 |
|--------|--------|
| **os** | shell / file / dns / tcp / sleep / noop / http |
| **mcp** | MCP 协议工具 |
| **cli-skills** | CLI Skills 工具 |

扩展方式：实现 `Executor` 接口即可添加自定义执行器。

### 4. 多语言客户端

内置 Go / Java / Python / Node.js 的 HTTP 接入示例，gRPC 接口支持微服务架构。

---

## 四、Proof：项目状态与设计质量

### 架构图

```
AI Agent (secbot)
       POST /tasks ←→ GET /tasks/{id}
              ↓ HTTP/JSON
         API Layer (net/http)
              ↓
         Scheduler (DAG + Kahn)
              ↓
    os / mcp / cli-skills / (extensible)
              ↓
         Store (jsonfile / sqlite / Redis)
              ↓
       Observability (slog + traceID + /metrics)
```

### 生产就绪特性

- **Graceful Shutdown**：信号监听 → HTTP 关闭 → 调度器停止 → 状态持久化
- **幂等提交**：轮询 + 幂等设计，稳定提交与读取结果
- **失败语义**：failed vs skipped，下游自动 skip 而非级联失败
- **CI/CD**：main push 和 PR 执行全量测试，v* tag 自动 release

### 与 Anthropic Brain/Hands 的关联

Anthropic 的 Managed Agents 解耦了 Brain（Harness）与 Hands（Sandbox），ExecGo 提供的是这个模型的**具体工程实现**：

- Anthropic 的 `execute(name, input) → string` 接口 = ExecGo 的 Task DSL
- Anthropic 的 sandbox = ExecGo 的 executors（os / mcp / cli-skills）
- Anthropic 的 session + vault = ExecGo 的 Store + 可选的 SQLite/Redis 持久化

> Anthropic 写道："The harness doesn't know whether the sandbox is a container, a phone, or a Pokémon emulator."
> ExecGo 通过 pluggable executors + `execute(name, input) → string` 接口实现了相同的设计哲学。

---

## 五、Threshold：行动引导

### 快速开始

```bash
# 构建
go build -o execgo ./cmd/execgo

# 运行（默认 :8080）
./execgo

# 提交 DAG 任务
curl -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {"id": "fetch-data", "type": "http", "params": {"url": "https://httpbin.org/json"}, "timeout": 10000},
      {"id": "save-result", "type": "file", "params": {"action": "write", "path": "output.txt", "content": "fetched!"}, "depends_on": ["fetch-data"]}
    ]
  }'
```

### 接入你的 Agent

Python 示例：

```python
import requests

resp = requests.post("http://localhost:8080/tasks", json={
    "tasks": [{
        "id": "scan-ports",
        "type": "shell",
        "params": {"command": "nmap -F 192.168.1.1"},
        "retry": 2,
        "timeout": 30000
    }]
})
task_id = resp.json()["tasks"][0]["id"]
```

### 文档入口

- 中文总入口：[`docs/zh/README.md`](https://github.com/iammm0/execgo/blob/main/docs/zh/README.md)
- HTTP API 入门：[`docs/zh/integration/http-api-getting-started.md`](https://github.com/iammm0/execgo/blob/main/docs/zh/integration/http-api-getting-started.md)
- 英文 FAQ：[`docs/en/faqs.md`](https://github.com/iammm0/execgo/blob/main/docs/en/faqs.md)

---

## 对比：ExecGo vs 其他执行层方案

| 维度 | ExecGo | 通用工作流引擎（Temporal/Airflow） |
|------|--------|----------------------------------|
| **定位** | Agent action harness | 通用业务流程 |
| **依赖** | Go stdlib only（核心） | 通常重量级依赖 |
| **接口** | HTTP/JSON + gRPC | 通常 SDK only |
| **Agent 适配** | ✅ 原生支持 MCP/CLI Skills | ❌ 需要适配 |
| **模型无关** | ✅ 与模型解耦 | ❌ 通常绑定特定框架 |
| **适用场景** | 需要可靠任务执行的 Agent 系统 | 复杂业务流程 |

---

*关联阅读：[Anthropic Managed Agents — Brain/Hands 解耦架构分析](https://github.com/FreezeSoul/agent-engineering-by-openclaw/blob/main/articles/harness/anthropic-scaling-managed-agents-brain-hands-decoupling-2026.md) — Anthropic 的 meta-harness 设计哲学与 ExecGo 的工程实现形成「理论 → 实现」闭环*