# CLI vs MCP：上下文效率的实战对比

> **本质**：MCP 提供了标准化的工具连接能力，但代价是巨大的上下文开销。在企业级多工具场景下，CLI 工具的 token 效率比 MCP 高出数十倍——这不是理论推算，而是真实的工程Benchmark。

---

## 一、MCP 的上下文税：被忽视的成本

MCP（Model Context Protocol）在工具标准化方面迈出了重要一步，但有一个关键问题很少被讨论：**MCP 是上下文吞噬者**。

一个典型的 MCP 服务器不会只暴露你需要的工具，而是将整个 Schema 注入 Agent 的上下文窗口——工具定义、参数描述、认证流程、状态管理，全部打包。

以 GitHub MCP Server 为例：
- 该服务器包含 **93 个工具**
- 每个工具的 Schema 包含完整的 `inputSchema`
- 总上下文成本：**约 55,000 tokens**

这意味着什么？

在你问出第一个问题之前，GPT-4o 的上下文窗口已经被消耗了一半，或者 Claude 的预算被切掉了一大块。

而这只是 **一个** MCP 服务器。

在企业场景中，一个典型的 Agent 可能需要同时连接：
- GitHub（93 工具，55K tokens）
- Microsoft Graph（Intune/Entra ID，28K tokens）
- 数据库连接器（8K tokens）
- Jira（5K tokens）

**多服务器叠加后，工具定义的上下文开销轻松超过 150,000 tokens。**

---

## 二、Token 数学：改变认知的实测数据

一位从业者在真实客户场景中进行了对比测试：

**任务**：「列出所有不合规的 Intune 设备，并将其详情导出为 CSV。」

### MCP 方案（Microsoft Graph MCP Server）

| 阶段 | Token 消耗 |
|------|-----------|
| 工具 Schema 注入 | ~28,000 tokens |
| Agent 推理 + 工具选择 | ~3,200 tokens |
| MCP 调用：过滤不合规设备 | ~1,800 tokens |
| MCP 响应解析 | ~4,500 tokens |
| MCP 调用：获取每个设备详情（×N） | ~2,100 tokens × N |
| **50 台设备总消耗** | **~145,000 tokens** |

### CLI 方案

| 阶段 | Token 消耗 |
|------|-----------|
| 工具 Schema 注入 | **0 tokens** |
| Agent 推理 + 命令组合 | ~800 tokens |
| Shell 命令执行 | ~150 tokens |
| 输出解析 | ~3,200 tokens |
| **50 台设备总消耗** | **~4,150 tokens** |

**这不是边际差异——这是 35 倍的 token 消耗差距。**

Token 不只是成本指标，它直接决定了 Agent 剩余的推理能力。

---

## 三、真实案例：Intune 合规自动化

### MCP 方案的问题

三个 MCP 服务器加载后的 Agent 上下文分布：

```
Agent 上下文窗口（128K 总计）：
├── 系统提示：~2,000 tokens
├── Graph MCP Schema：~28,000 tokens
├── 合规 MCP Schema：~8,500 tokens
├── 报告 MCP Schema：~5,200 tokens
├── 对话历史：~4,000 tokens
└── 用于推理的可用空间：~82,300 tokens
```

Agent 能工作，但明显变慢。多步骤推理在 3-4 次工具调用后就开始崩溃——因为 MCP 响应的累积上下文将 Agent 推入上下文窗口的末端区域，那里的注意力质量会下降。

最终，开发者不得不将工作流拆分成多个 Agent 会话才能获得可靠结果。

### CLI 方案的优势

同样的任务，给予 Agent mgc（Microsoft Graph CLI）、az CLI 和三个聚焦的 PowerShell 脚本：

```bash
# Agent 自主组合的管道
mgc devices list --filter "complianceState eq 'noncompliant'" \
  --select "id,deviceName,complianceState,userPrincipalName" --output json \
  | ConvertFrom-Json \
  | ForEach-Object {
    $device = $_
    $groups = mgc users list-member-of --user-id $_.userPrincipalName \
      --output json | ConvertFrom-Json
    [PSCustomObject]@{
      DeviceName = $device.deviceName
      User = $device.userPrincipalName
      Compliance = $device.complianceState
      Groups = ($groups.displayName -join "; ")
    }
  } | Export-Csv -Path "compliance-report.csv" -NoTypeInformation
```

Agent 上下文分布：

```
Agent 上下文窗口（128K 总计）：
├── 系统提示：~2,000 tokens
├── 工具 Schema：**0 tokens**
├── 对话历史：~1,500 tokens
├── 命令输出：~3,200 tokens
└── 用于推理的可用空间：**~121,300 tokens**
```

Agent 拥有 95% 的上下文窗口用于推理。它在一次交互中组合了整个管道，主动处理边缘情况，单会话完成任务。

---

## 四、AI 模型天生是 CLI 说话者

CLI 工具在 AI Agent 中效果更好的原因远超 token 效率。

**AI 模型在数十亿行终端交互中训练过**——Stack Overflow 答案、GitHub 仓库、文档、教程。当你让 Claude 或 GPT 使用 `git`、`docker`、`az`、`kubectl` 或 `gh` 时，你调用的 是深度学习的模式。

```bash
# CLI：模型已经知道这是什么
docker ps --filter "status=running" --format "{{.Names}}: {{.Status}}"

# MCP：模型需要先解释这个 Schema
{
  "name": "list_containers",
  "inputSchema": {
    "properties": {
      "status_filter": {
        "enum": ["running", "stopped", "all"]
      },
      "format_fields": {
        "type": "array",
        "items": {
          "enum": ["name", "status", "image", "ports"]
        }
      }
    }
  }
}
```

CLI 版本是自文档化的。MCP 版本要求模型将意图映射到一个陌生的抽象层。

---

## 五、CLI 可组合性：Unix 哲学遇上 AI

CLI 工具最强大的优势之一是可组合性——而 AI Agent 在这方面惊人地擅长：

```bash
# Agent 组合的管道：查找高 CPU 虚拟机，
# 获取其 Intune 合规状态
az vm list --query "[?powerState=='VM running']" -o json \
  | jq -r '.[].name' \
  | xargs -I {} mgc devices list \
    --filter "displayName eq '{}'" \
    --select "complianceState" -o json \
    | jq '[.[] | {name: .displayName, compliance: .complianceState}]'
```

在 MCP 中实现这种跨工具工作流，你需要同时加载两个服务器，Agent 需要编排多个结构化调用，管理中间状态，并处理不同的响应格式。

用 CLI，Agent 只需要把文本通过熟悉的工具管道传递。

---

## 六、为什么 MCP 仍然是正确答案

需要明确的是：**MCP 并不是坏的**。

MCP 的价值在以下场景仍然成立：
- **工具发现**：Agent 不知道某个工具存在时，MCP 的标准化 Schema 有助于发现
- **复杂状态管理**：需要维护会话状态的工作流（如多步骤审批流程）
- **工具数量少**：单一工具服务器，Schema 不超过 5-10 个工具
- **安全审计需求**：MCP 的结构化接口更容易做权限控制和安全审计

问题在于：**许多开发者把 MCP 当作所有工具集成问题的默认答案**，而不考虑上下文成本。

---

## 七、实践建议

| 场景 | 推荐方案 |
|------|---------|
| 1-3 个成熟 CLI 工具 | CLI（效率最高）|
| 4+ 工具，Schema < 10K tokens | MCP（可接受）|
| 4+ 工具，Schema > 20K tokens | 考虑 MCP 分片或 CLI 封装 |
| 需要工具发现和自描述 | MCP（标准化优势）|
| 安全审计要求高 | MCP（结构化接口优势）|
| 高频短任务 | CLI（无 Schema 开销）|
| 低频复杂多步骤 | MCP（状态管理优势）|

---

## 八、结论

MCP 和 CLI 不是非此即彼的选择。它们是不同的工具，适用于不同的场景。

关键认知转变是：**从「用 MCP 连接一切」到「根据上下文成本选择正确工具」**。

在资源受限的生产环境中，35 倍的 token 效率差异可能意味着：
- 更低的 API 成本
- 更快的响应时间
- 更好的多步骤推理能力
- 更少的上下文截断问题

CLI 不是倒退——它是在 MCP 时代对工具选择策略的成熟反思。

---

## 参考文献

- [Why CLI Tools Are Beating MCP for AI Agents](https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/) — Jannik Reinhard，2026年2月22日

---

*来源：独立博客 · 工程实践 · Stage 6: Tool Use*
