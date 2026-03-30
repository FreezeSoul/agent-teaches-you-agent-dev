# Agent Audit：LLM Agent 部署前的安全扫描仪

> **本质**：在代码合并前发现 Agent 系统的安全漏洞——不是运行时防御，而是静态代码审计

> **关联阅读**：建议先阅读 [OWASP Top 10 for Agentic Applications (2026)](./owasp-top-10-agentic-applications-2026.md)，了解政策层视角；建议配合 [MCP Security Crisis: 30 CVEs 60 Days](./mcp-security-crisis-30-cves-60-days.md)，理解 MCP 安全威胁全貌；建议配合 [CABP: Context-Aware Broker Protocol](./cabp-context-aware-broker-protocol-mcp.md)，理解协议层安全原语；建议配合 [Cisco A2A Scanner](./cisco-a2a-scanner-five-detection-engines.md)，理解 A2A 协议层扫描

---

## 一、基本信息

| 项目 | 值 |
|------|---|
| **论文** | arxiv:2603.22853 |
| **GitHub** | [HeadyZhang/agent-audit](https://github.com/HeadyZhang/agent-audit)（134 stars，2026-03-29）|
| **PyPI** | `pip install agent-audit` |
| **语言** | Python |
| **测试** | 1239 passed |
| **基准指标** | 94.6% recall / 87.5% precision / 0.91 F1 |
| **OWASP 覆盖** | 10/10 OWASP Agentic Top 10 (2026) |
| **CI 集成** | 支持（`--fail-on high`，SARIF 输出）|
| **扫描耗时** | sub-second |
| **评测基准** | 22 samples / 42 annotated vulnerabilities / 40 detected / 6 false positives |

---

## 二、核心问题：部署前该检查什么？

论文提出的核心问题直击要害：

> **"What should a developer inspect before deploying an LLM agent: the model, the tool code, the deployment configuration, or all three?"**

传统安全审计聚焦于模型本身（权重安全、对抗样本等），但 Agent 系统的安全失败往往来自**软件栈**而非模型权重：

1. **Tool Functions**：将不受信任的输入传递给危险操作（如 `subprocess.run` + 用户输入）
2. **Deployment Artifacts**：凭证在部署配置中暴露
3. **MCP Configurations**：MCP 配置过度授权，意外扩大访问面

这三个维度恰好对应 Agent 系统的三个核心组件，Agent Audit 的设计正是围绕这三个维度展开。

---

## 三、技术架构：四层扫描管道

Agent Audit 的核心技术是一个**面向 Agent 工作流的分析管道**，包含四层检测：

### 3.1 数据流分析（Dataflow Analysis）

追踪用户输入在 Agent 代码中的传播路径，判断是否有未经过滤的用户输入直接到达危险操作。

**典型漏洞模式**：
```python
# AGENT-001: Command Injection via Unsanitized Input
result = subprocess.run(command, shell=True, capture_output=True, text=True)
# user input → command 直接拼接
```

```python
# AGENT-041: SQL Injection via String Interpolation
cursor.execute(f"SELECT * FROM users WHERE name = '{query}'")
# user input → SQL 直接拼接
```

### 3.2 凭证检测（Credential Detection）

识别 Agent 代码和部署配置中暴露的密钥、API Token、环境变量中的敏感信息。

**典型漏洞模式**：
```json
// AGENT-031: MCP Sensitive Env Exposure
{
  "env": {"API_KEY": "sk-a***"}  // 真实密钥残留
}
```

```python
# Hardcoded API keys
OPENAI_API_KEY = "sk-proj-xxxxx"
```

### 3.3 结构化配置解析（Structured Configuration Parsing）

解析 MCP 配置文件（`mcp_config.json` 等），识别过度授权的 MCP 服务器配置。

**典型漏洞模式**：
```json
// MCP server with excessive permissions
{
  "servers": [{
    "name": "filesystem",
    "permissions": ["read_write_all"]  // 不必要的全读写权限
  }]
}
```

### 3.4 权限风险检查（Privilege-Risk Checks）

评估 MCP 服务器的工具调用权限是否与实际需求匹配，识别过度授权的工具链。

---

## 四、53 条规则体系

Agent Audit 目前包含 **53 条规则**，与 [OWASP Agentic Top 10 (2026)](./owasp-top-10-agentic-applications-2026.md) 完全对齐：

| OWASP 类别 | Agent Audit 规则示例 | 检测方法 |
|-----------|---------------------|---------|
| **Prompt Injection** | AGENT-010: System Prompt Injection Vector | 用户输入→系统 Prompt 数据流追踪 |
| **Sensitive Data Exposure** | AGENT-031: MCP Sensitive Env Exposure | 配置解析 |
| **Tool Harmfulness** | AGENT-001: Command Injection | 数据流分析 |
| **Unbounded Consumption** | Rate-limit 配置缺失检测 | 配置解析 |
| **Overprivileged Tool** | MCP 工具权限评估 | 权限图分析 |
| **MCP Misconfiguration** | 过度宽松的 MCP server 配置 | 结构化解析 |

**评分机制**：每条规则分为三级：
- **BLOCK**（Tier 1，置信度 ≥ 90%）：立即阻止合并
- **WARN**（Tier 2）：警告，需要人工审查
- **INFO**（Tier 3）：信息性提示

---

## 五、基准测试数据

| 指标 | 数值 |
|------|------|
| 样本数 | 22 个真实 Agent 项目样本 |
| 标注漏洞数 | 42 个（人工标注 ground truth）|
| 检测数 | 40 个（漏报 2 个）|
| 误报数 | 6 个 |
| **Recall** | **94.6%** |
| **Precision** | **87.5%** |
| **F1 Score** | **0.91** |
| OWASP Top 10 覆盖率 | 10/10 |

**对比 SAST 基线**：相比通用 SAST 工具，Agent Audit 的 Recall 大幅提升——通用 SAST 工具不理解 Agent 语义（Tool Functions、MCP 配置、Prompt 注入向量），只能检测通用代码漏洞。

---

## 六、使用方式

### 6.1 快速开始（6 行）

```bash
# 1. 安装
pip install agent-audit

# 2. 扫描项目
agent-audit scan ./your-agent-project

# 3. 仅显示高危漏洞
agent-audit scan . --severity high

# 4. CI 集成：发现高危漏洞时失败
agent-audit scan . --fail-on high
```

### 6.2 输出格式

支持三种输出格式：
- **Terminal**：彩色可视化报告（Risk Score + 分级结果）
- **JSON**：机器可读格式（CI 集成）
- **SARIF**：GitHub Code Scanning 格式（直接导入 VS Code 和 GitHub Security 页）

### 6.3 CI 集成示例

```yaml
# GitHub Actions
- name: Agent Security Scan
  run: |
    pip install agent-audit
    agent-audit scan . --fail-on high --format sarif --output agent-audit.sarif
  with:
    category: "/agent-security"

- name: Upload to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: agent-audit.sarif
    category: "agent-audit"
```

---

## 七、支持的框架

Agent Audit 的检测器专门针对三大主流 Agent 框架的代码模式：

| 框架 | 支持情况 | 检测重点 |
|------|---------|---------|
| **LangChain** | ✅ | LCEL chain 中的 tool 调用、prompt 模板注入 |
| **CrewAI** | ✅ | Agent 之间的 tool 传递、crew 权限配置 |
| **AutoGen** | ✅ | AssistantAgent / UserProxyAgent 的 tool 使用模式 |
| **自定义 MCP Server** | ✅ | MCP 配置文件审计 |

---

## 八、与现有安全工具的互补关系

Agent Audit 不是另一个运行时防御工具，而是**静态代码审计层的补充**：

| 工具 | 类型 | 防御时机 | 防御对象 |
|------|------|---------|---------|
| **DefenseClaw** | 运行时扫描 | 部署后实时监控 | 运行时工具调用行为 |
| **CABP/ATBA/SERF** | 协议层安全 | 运行时通信 | A2A/MCP 协议层攻击 |
| **A2A Scanner** | 协议层扫描 | 部署前静态分析 | Agent Card 伪造/提示注入 |
| **Agent Audit** | **代码层静态审计** | **部署前（CI）** | **代码漏洞/MCP 配置错误/凭证暴露** |
| **OWASP ASI Top 10** | 政策/设计层 | 设计时 | 架构级安全原则 |

**防御层次矩阵**：

```
Design Time (OWASP ASI Top 10)
        ↓
Pre-Deploy Static (Agent Audit ← 本文)
        ↓
Protocol Layer (CABP / A2A Scanner)
        ↓
Runtime Monitoring (DefenseClaw / CABP runtime)
```

---

## 九、局限性

1. **Python only**：目前仅支持 Python Agent 代码，LangChain.js / CrewAI.js 等 JavaScript 生态尚未覆盖
2. **Sub-second 但有限深度**：扫描速度快，但对于复杂的数据流分析（如跨文件的污点追踪）能力有限
3. **42 样本基准**：评测基准规模较小（22 samples / 42 vulns），真实世界的漏洞形态可能更复杂
4. **误报率 12.5%**：87.5% precision 意味着约 1/8 的高危告警是误报，需要人工复核
5. **不支持动态 Agent 行为**：静态分析无法覆盖 Agent 在运行时动态生成的 tool 调用

---

## 十、适用场景

**Agent Audit 最适合的场景**：

1. **CI/CD 安全门**：在每次 merge 前自动运行，发现 BLOCK 级漏洞立即阻止部署
2. **MCP Server 发布前审计**：发布 MCP Server 到公共 registry 之前，确认无过度授权配置
3. **第三方 Agent 代码审计**：集成第三方 Agent 代码（如开源 agent 项目）时的安全尽调
4. **合规要求**：SOC 2 / ISO 27001 等合规审计中，证明已对 Agent 代码进行安全扫描

**Agent Audit 不适合的场景**：

1. 运行时动态生成的 tool 调用（需要 DefenseClaw 类运行时监控）
2. 非 Python 的 Agent 实现（JavaScript/TypeScript 生态需等待支持）
3. 模型层面的对抗攻击（需要专门的 red teaming 工具）

---

## 十一、核心结论

Agent Audit 回答了一个最朴素但最重要的问题：

> **"部署前，该检查什么？"**

答案是：**Model → Tool Code → Deployment Configuration**，三个层次缺一不可。Agent Audit 的核心价值在于将安全扫描从"模型安全"的单一维度，扩展到整个 Agent 软件栈——代码层、配置层、凭证层。

在 OWASP ASI Top 10 的政策框架下，Agent Audit 提供了**可操作的工程化落地**：pip 安装、6 行代码开始、CI 一行集成。这使得安全扫描不再是安全团队的专属工作，而成为每一个 Agent 开发者的日常工具。

**演进路径定位**：属于 **Stage 12（Harness Engineering）** ——专注于代码层的 Tool Constraints 和 Behavioral Rules，是 OWASP ASI Top 10（政策层）和 DefenseClaw（运行时层）的必要补充。

---

## 十二、参考文献

1. Zhang et al. "Agent Audit: Static Security Analysis for LLM Agent Applications" arxiv:2603.22853 (2026-03-28) — https://arxiv.org/abs/2603.22853
2. OWASP Agentic Top 10 for Applications (2026) — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
3. HeadyZhang/agent-audit GitHub — https://github.com/HeadyZhang/agent-audit
4. OWASP Top 10 for Agentic Applications (2026) — [本仓库文章](./owasp-top-10-agentic-applications-2026.md)
5. MCP Security Crisis: 30 CVEs 60 Days — [本仓库文章](./mcp-security-crisis-30-cves-60-days.md)
6. CABP: Context-Aware Broker Protocol — [本仓库文章](./cabp-context-aware-broker-protocol-mcp.md)

---

*本文属于 Stage 12（Harness Engineering）|
最后更新：2026-03-31 05:01（北京时间）*
