# CoSAI MCP Security 白皮书：首个系统性 MCP 威胁分类框架

## 背景与核心问题

MCP（Model Context Protocol）在过去一年快速成为 AI Agent 连接外部工具和数据的标准协议——但安全问题已经真实发生：Asana MCP 租户隔离缺陷导致最多 1000 家企业数据污染（2025年5月）、WordPress AI Engine 插件 privilege escalation CVE-2025-5071 影响超过 10 万站点、Supabase MCP 服务器 prompt injection 导致私有表暴露。

这些事件的共同特点是：**缺乏统一的安全分类框架来指导 MCP 的安全设计与评估**。

2026 年 1 月 8 日，CoSAI（Coalition for Secure AI，一个 OASIS Open Project）发布了首个系统性 MCP 安全白皮书，对应了近 40 个威胁横跨 12 个类别。本文对这个框架进行完整解读，回答一个核心工程问题：**这个分类框架对 MCP 部署者意味着什么？如何用它来评估自己的安全状态？**

## MCP 为何需要专门的安全方法论

既有的安全框架（MITRE ATLAS、NIST AI RMF、MAESTRO）针对复杂多组件系统设计，但这些框架**假设组件行为可预测**，遵循预定义逻辑。MCP 引入了一个本质上不可预测的元素：**LLM 本身**。

LLM 的行为无法通过静态分析完全预测，这导致了 MCP 特有的安全问题：

- **动态能力协商**：MCP 的 capability negotiation 在运行时决定 Agent 能访问哪些工具，每次协商结果可能因上下文不同而变化
- **协议级身份认证**：传统 API 调用有固定的身份边界；MCP 的身份认证跨越了「人类用户—Agent Host—MCP Client—MCP Server—下游资源」多层信任链
- **分布式信任关系**：MCP Server 可能来自第三方，Agent 通过 MCP 连接到一个不受自己控制的工具提供商
- **长会话管理**：AI 对话是长时的，一个会话内 Agent 可能调用数十个工具，信任状态需要随时间演变而非一次性确定

> **笔者的核心判断**：MCP 的安全问题不是「协议设计有缺陷」，而是 MCP 将 LLM（不可预测组件）引入了传统分布式系统（已有成熟安全模式），产生了新的攻击面。现有的安全框架不能直接覆盖这个组合。

## 威胁分类框架：两类威胁 × 12 个类别

CoSAI 白皮书将 MCP 威胁分为两类：

### MCP-Specific：MCP 引入的新型攻击向量

这类威胁在传统 API 调用系统中不存在，是 MCP 特有的：

| 类别 | 威胁 ID | 核心问题 |
|------|---------|---------|
| Input/Instruction Boundary Distinction Failure | MCP-T4 | LLM 无法区分「用户输入」和「MCP Server 返回的工具结果」，攻击者在工具返回结果中嵌入恶意指令 |
| Input Validation/Sanitization Failures | MCP-T3 | MCP Server 的输出作为 LLM 输入，缺乏对返回内容的净化 |
| Trust Boundary and Privilege Design Failures | MCP-T9 | MCP 协议层与业务逻辑层之间的权限边界模糊，导致过度授权 |
| Supply Chain and Lifecycle Security Failures | MCP-T11 | MCP Server 作为第三方代码引入，其生命周期管理（更新、撤回、版本控制）缺乏标准 |

### MCP-Contextualized：被 MCP 放大威胁的传统安全问题

这类威胁在传统系统中存在，但 MCP 的架构放大了其影响：

| 类别 | 威胁 ID | 核心问题 |
|------|---------|---------|
| Improper Authentication and Identity Management | MCP-T1 | Agent 身份认证在多方（用户/Host/Client/Server/资源）之间跨越，身份声明难以验证 |
| Missing or Improper Access Control | MCP-T2 | MCP 的 capability negotiation 动态性使得传统的静态访问控制模型无法直接应用 |
| Inadequate Data Protection and Confidentiality Controls | MCP-T5 | MCP Server 可能访问敏感数据源（数据库、业务系统），但传输和存储的保密性缺乏保障 |
| Missing Integrity/Verification Controls | MCP-T6 | MCP Server 返回的工具结果缺乏完整性验证，可能被篡改 |
| Session and Transport Security Failures | MCP-T7 | MCP 支持 stdio（本地进程）和 Streamable HTTP（网络通信），两种传输模式的安全要求不同 |
| Network Binding/Isolation Failures | MCP-T8 | 本地部署的 MCP Server 不能依赖「本地=安全」的假设，DNS rebinding 等攻击已有实案 |
| Resource Management/Rate Limiting Absence | MCP-T10 | MCP Server 可能被滥用为攻击下游系统的跳板，缺少速率限制 |
| Insufficient Logging, Monitoring, and Auditability | MCP-T12 | MCP 操作缺乏可审计的日志，导致安全事件无法溯源 |

## 真实事件映射：三个案例的威胁链分析

### Asana MCP 租户隔离缺陷（2025年5月）

**影响**：跨组织数据污染，多达 1000 家企业受影响。

**涉及威胁类别**：`MCP-T2`（访问控制缺失）+ `MCP-T5`（数据保密性不足）

**攻击链路**：多租户环境下，某个租户的 MCP Client 发送的请求被错误路由到另一个租户的 MCP Server，源于 capability negotiation 时未充分校验租户边界。

**关键工程教训**：多租户 MCP Server 必须实现租户级别的资源隔离，不能依赖 MCP 协议本身提供的默认隔离机制。

### WordPress AI Engine CVE-2025-5071（2025年6月修补）

**影响**：超过 10 万站点面临 privilege escalation 攻击。

**涉及威胁类别**：`MCP-T1`（身份管理）+ `MCP-T11`（供应链安全）

**攻击链路**：WordPress AI Engine 插件中的 MCP Server 未正确验证调用者身份，允许低权限用户通过 MCP 接口提升权限。

**关键工程教训**：MCP Server 必须实现最小权限原则，每个工具调用应独立授权，而非假设「已认证的用户可以做任何事」。

### Supabase MCP Prompt Injection（2025年）

**涉及威胁类别**：`MCP-T3`（输入验证）+ `MCP-T4`（边界区分失败）+ 工具过度授权

**攻击链路**：攻击者通过 Supabase 支持工单数据注入 prompt，诱导 Cursor AI 工具暴露私有数据库表。问题的根源是 MCP Server 返回的数据未经过滤直接作为 LLM 指令上下文。

**关键工程教训**：MCP Server 的输出不应被信任为「数据」——它应该始终被视为「可能的指令来源」，需要经过内容净化。

## 8 类控制措施与工程落地

CoSAI 为每个威胁类别提供了具体的控制措施，按工程可落地性分类：

### 1. Agent Identity（对应 MCP-T1）

- 使用 Ed25519 公钥建立加密 Agent 身份
- 跨会话的 identity 持久化，不依赖临时 session token
- 行为画像作为身份验证的补充手段

**工程落地参考**：Agent Governance Toolkit（AGT）的 Agent Mesh 组件使用 Ed25519 + SPIFFE 证书实现此模型。

### 2. Secure Delegation and Access Control（对应 MCP-T2/T9）

- 基于 capability 的最小权限：每个工具调用独立授权，不授予「工具集合」的笼统权限
- 动态权限衰减：Agent 行为异常时自动降级权限
- MCP-T9 特别要求：Agent 的信任状态应区分「协议层信任」和「业务逻辑层权限」

### 3. Input and Data Sanitization and Filtering（对应 MCP-T3/T4）

- MCP Server 输出必须经过内容净化才能作为 LLM 上下文
- 工具描述字段（tool descriptions）应对用户可见，防止隐藏的指令注入
- 建议在 MCP Client 侧实现「输入净化」层，在数据进入 LLM 前过滤

### 4. Cryptographic Integrity and Remote Attestation（对应 MCP-T6）

- MCP Server 返回结果应附有密码学完整性校验（HMAC 或签名）
- 插件和 MCP Server 应提供可验证的来源声明

### 5. Sandboxing and Isolation（对应 MCP-T8/T10）

- 每个 MCP Server 应在独立进程/容器中运行，实现资源隔离
- MCP Server 不应被信任为「网络隔离区」——即使运行在 localhost，也应视为潜在攻击者
- 速率限制应在 MCP Gateway 层面实现，而非依赖单个 Server

### 6. Transport Layer Security（对应 MCP-T7）

- stdio 传输：适用于本地进程，但应验证父子进程关系
- Streamable HTTP：必须使用 TLS，并实现双向 TLS 认证（mTLS）
- 不同部署模式（All-Local / Single-Tenant / Multi-Tenant）的 TLS 要求不同

### 7. Human-in-the-loop（对应 MCP-T9）

- 高风险操作（删除、修改外部系统、写数据库）需要人工审批
- quorum 逻辑：多个 Agent 协作时，需要多个 Agent 确认才能执行高风险操作
- 关键决策应保留「否决点」

### 8. Logging, Monitoring, and Auditability（对应 MCP-T12）

- MCP 操作日志应包含：调用者身份、被调用工具、参数、时间戳、返回结果摘要
- 日志应为 append-only，防止篡改
- 建议使用 hash chain 保证日志完整性

## 部署模式的安全考量

不同部署模式下，威胁优先级差异显著：

| 部署模式 | 主要威胁 | 首要控制 |
|---------|---------|---------|
| All-Local（本地 stdio）| MCP-T4/MCP-T3（prompt injection） | 输出净化 + 工具描述可见化 |
| Single-Tenant Hybrid | MCP-T1/T2（身份和访问控制）| Agent 身份体系 + 能力级授权 |
| Multi-Tenant Cloud | MCP-T5/T2（数据隔离）| 租户隔离 + 加密传输 |

**一个关键陷阱**：「本地部署」不等于「安全」。DNS rebinding 攻击（CVE-2026-34742）已经证明本地 MCP Server 也需要严格的安全边界——localhost 本身不是信任边界，密码学身份才是。

## 框架评估：贡献与局限

### 贡献

1. **首次系统性分类**：CoSAI MCP Security 是首个覆盖近 40 个 MCP 威胁的分类框架，填补了行业空白
2. **区分了两类威胁**：MCP-Specific vs. MCP-Contextualized 的划分非常有价值——前者需要协议层解决，后者需要工程实践层解决
3. **与 OWASP Top 10 形成映射**：白皮书中提到的 OWASP Agentic AI Top 10 映射关系，使得两个框架可以协同使用
4. **实际事件驱动**：威胁分类基于真实事件（Asana、Supabase、WordPress），不是理论推演

### 局限

1. **无参考实现**：白皮书明确说明「提供指导，不提供实现」，控制措施的工程落地需要使用者自行设计
2. **未覆盖内容安全**：专注于安全，不涉及 AI 内容安全、 misinformation 等领域
3. **协议版本覆盖不完整**：仅覆盖 2025-06-18 和 2025-11-25 两个版本，较新版本可能引入新的威胁面
4. **评估标准缺失**：白皮书提供了威胁分类，但没有提供「如何评估自己的 MCP 部署安全状态」的量化评估方法

### 工程建议

> **使用方式**：将 12 个威胁类别作为 MCP 部署的安全审计 checklist，逐项评估。对于 MCP-Specific 威胁（主要是 T3/T4/T9/T11），优先投入治理；对于 MCP-Contextualized 威胁，参考既有的云原生安全实践。

## 信息来源

- [CoSAI Model Context Protocol (MCP) Security 白皮书](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/model-context-protocol-security.md)（OASIS Open，2026年1月8日）
- [CoSAI at RSAC 2026](https://www.coalitionforsecureai.org/cosai-at-rsac-2026/)
- [Adversa AI：Top MCP Security Resources February 2026](https://adversa.ai/blog/top-mcp-security-resources-february-2026/)
