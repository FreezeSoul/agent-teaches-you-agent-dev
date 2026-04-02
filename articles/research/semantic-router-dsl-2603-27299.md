# Semantic Router DSL：从推理路由到 Agent 编排的政策编译 (2603.27299)

> **本质**：用非图灵完备的声明式 DSL（`.sr` 文件）编写路由策略，一次编译，生成 LangGraph 决策节点、OpenClaw 网关策略、Kubernetes 制品、MCP/A2A 协议边界门Gate——全部经过 π-calculus 形式化验证。

## 一、基本概念

### 问题：路由策略的碎片化

在 2026 年的 Agent 系统中，"路由"已经不再是简单的模型选择。它横跨：

- **推理路由**：内容信号（embedding 相似度、PII 检测、越狱评分）→ 选择模型
- **安全路由**：隐私策略执行、合规审计追踪
- **编排路由**：多 Agent 任务分配、工具选择、跨协议上下文传递

现状是每个框架各自为政：LangGraph 用条件边写路由，OpenClaw 用 JSON 配置写策略，Kubernetes 用 NetworkPolicy 写网络策略，MCP/A2A 在协议层各自实现门控。**改一个阈值，要改 N 个文件，N 个地方的行为还不一致。**

### 解法：Single Source of Truth

Semantic Router DSL（论文 2603.27299）提出了一个非图灵完备的 `.sr` 策略语言：

```
# example.sr
PREDICATE jailbreak_score > 0.7 → DENY(reason="jailbreak")
PREDICATE pii_detected == true → MASK_AND_LOG(entity_type)
PREDICATE intent == "code" → MODEL(gpt-5, tier=high)
PREDICATE intent == "闲聊" → MODEL(claude-haiku, tier=low)
```

编译器从这**一个声明式源文件**，同时生成：

| 编译目标 | 产出形式 |
|---------|---------|
| **LangGraph** | 条件边（Strategy A）或 Command-Returning Node（Strategy B）|
| **OpenClaw** | 网关策略 Bundle + Plugin Hook 配置 |
| **Kubernetes** | NetworkPolicy + Sandbox CRD + ConfigMap |
| **MCP 协议** | `tools/call` Gate 拦截器 |
| **A2A 协议** | `tasks/send` Gate 拦截器 |
| **YANG/NETCONF** | 结构化运维配置 |

关键属性：**阈值变更一次编译，全部目标同步更新**。这是人工维护多个目标文件时最难保持一致的属性。

---

## 二、核心技术机制

### 2.1 形式化验证基础：π-calculus

论文使用 π-calculus（进程代数）为 DSL 语义提供形式化基础。具体做法：

- 将 `.sr` 文件中的每条 `PREDICATE → ACTION` 规则建模为**通信进程**
- 验证**冲突自由性**（conflict-free compilation）：即不存在两条规则在相同输入下产生冲突决策
- 概率谓词的冲突检测在编译时完成，而非运行时

这解决了声明式路由策略的一个根本问题：**规则多了之后，规则之间的交互难以预测**。π-calculus 验证确保了 DSL 编译器能捕获规则冲突，而不是等到线上才暴露。

### 2.2 多目标编译架构

编译架构分为三层：

```
┌─────────────────────────────────────────┐
│         DSL Source (.sr file)            │  ← 单一声明式源
└────────────────┬────────────────────────┘
                 │ compiler
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐ ┌──────────┐ ┌──────────────┐
│LangGraph│ │ OpenClaw │ │ Kubernetes   │
│decision │ │ gateway  │ │ artifacts    │
│ nodes   │ │ policy   │ │ + YANG/NETCONF│
└────────┘ └──────────┘ └──────────────┘
```

#### OpenClaw 网关策略编译

对于 OpenClaw（基于网关的平台），DSL 编译器输出：

1. **策略 Bundle**：JSON 格式的路由决策表，包含优先级、阈值、动作类型
2. **Plugin Hook 配置**：声明哪些插件钩子在哪个决策点触发（如安全检查、日志记录、审计追踪）
3. **MCP/A2A Protocol Boundary Gate**：在 OpenClaw 的 MCP 服务器和 A2A 消息边界上插入拦截器

论文 Appendix A.8 给出了具体的 OpenClaw Gateway Policy 输出格式。

### 2.3 内容信号系统

DSL 的输入信号（`jailbreak_score`、`pii_detected`、`intent` 等）来自 embedding 相似度和分类器。vLLM Semantic Router v0.2 Athena（2026 年 3 月发布）提供了完整的信号处理 pipeline：

| 信号类型 | 分类器模型 | 说明 |
|---------|-----------|------|
| Intent | `mmbert32k-intent-classifier` | 多语言意图识别 |
| Jailbreak | `mmbert32k-jailbreak-detector` | 越狱攻击检测 |
| PII | `mmbert32k-pii-detector` | 个人信息识别 |
| Fact-check | `mmbert32k-factcheck-classifier` | 事实性检查 |
| Feedback | `mmbert32k-feedback-detector` | 用户反馈信号 |

这些信号被馈入 DSL 的 `PREDICATE` 条件系统，完成从"信号检测"到"策略执行"的完整链路。

---

## 三、与其他概念的关系（按演进路径）

### Stage 3（MCP）视角

MCP 是这篇论文的核心协议目标之一。论文验证了 DSL 编译产出的 MCP `tools/call` Gate：所有 MCP 工具调用都经过 DSL 策略过滤后才能执行。

**这意味着什么**：如果一个 MCP Server 的某个工具（比如 Shell 工具）存在 CVE 漏洞，传统的修复方式是升级 Server 版本。但如果用 DSL 编写了 `DANGEROUS_TOOL(shell) → APPROVE_WITH_CONSENT()` 规则，这条规则会被编译到 MCP Gate 中，在协议层拦截危险操作，而不是依赖 Server 本身的修复。

这与 **CVE-2026-2256**（ModelScope MS-Agent Shell 工具命令注入）高度相关：该漏洞的核心问题是 Shell 工具缺少输入过滤，而 MCP Gate 形式的协议层策略可以提供额外的防御纵深。

### Stage 7（Orchestration）视角

LangGraph 和 OpenClaw 分别代表两类编排架构：

| 架构类型 | 代表框架 | 路由表达方式 |
|---------|---------|------------|
| **Graph-based** | LangGraph | 条件边 / 专用决策节点 |
| **Gateway-based** | OpenClaw | 配置驱动的绑定表 + 插件钩子 |

论文同时验证了两种架构的编译目标，说明 DSL 路由层可以横跨不同编排范式。这与 vLLM Semantic Router v0.2 Athena 的 ClawOS 方向一致——将语义路由作为多 OpenClaw Worker 系统的大脑。

### 与 Formal Semantics 论文（2603.24747）的关系

2603.24747 用 π-calculus 验证了 MCP 和 A2A 的类型系统（五原则类型系统）。2603.27299 在此基础上**将 π-calculus 验证用于 DSL 编译**：不是验证协议本身，而是验证路由策略的冲突自由性。两者形成互补——前者保证协议安全，后者保证策略安全。

---

## 四、实践指南

### 适用场景

1. **多框架并存的 Agent 系统**：同时使用 OpenClaw（网关路由）和 LangGraph（工作流编排）的团队
2. **需要统一安全策略的 MCP 生态**：MCP Server 数量多，工具调用策略需要集中管理
3. **合规要求严格的部署环境**：需要结构化审计追踪，且策略变更需要可复现验证

### 局限性

1. **DSL 不是图灵完备的**：复杂的跨步骤推理无法用 `.sr` 表达，需要回退到框架原生表达能力
2. **编译目标是快照式的**：策略变更需要重新编译并部署，不能热更新
3. **验证的是冲突自由，不是正确性**：DSL 规则本身写错了，编译器无法发现

---

## 五、参考文献

- [2603.27299] *From Inference Routing to Agent Orchestration: Declarative Policy Compilation with Cross-Layer Verification* — arXiv, 2026-03
- [vLLM Semantic Router v0.2 Athena](https://vllm.ai/blog/v0.2-vllm-sr-athena-release) — ClawOS, Model Refresh, and the System Brain
- [2603.24747] *Formal Semantics of Agentic Tool Protocols: π-calculus Verification of SGD ≃ MCP* — agent-engineering-by-openclaw
