# LangChain / LangGraph / LangSmith Changelog Watch

> 本文件追踪 LangChain 生态的重大更新。每日检查 GitHub Releases 和官方博客，有重大版本更新时追加。

---

## 2026-04-01｜langchain-core 1.2.23：安全补丁 + 性能优化

**版本**：langchain-core 1.2.23
**性质**：🟢 Patch（安全 + 性能）
**来源**：[GitHub Release](https://github.com/langchain-ai/langchain/releases/tag/langchain-core%401.2.23)

### 变更要点

| 类别 | 变更 |
|------|------|
| **CVE-2026-4539** | 通过升级 pygments>=2.20.0 修复安全漏洞 |
| **性能** | Init 速度提升 15% |
| **Async TodoList** | TodoList 中间件新增 async 实现 |
| **Bug 修复** | Revert "trace invocation params in metadata"（regression 回退）|
| **依赖更新** | requests 2.32.5 → 2.33.0；cryptography 46.0.5 → 46.0.6 |

**为什么重要**：CVE-2026-4539 是跨依赖包的安全漏洞修复；Init 速度提升 15% 对大型 Chain 应用有感知价值；revert 说明该版本的 trace 相关改动引入了回归。

**版本判断**：Patch（安全修复 + 性能优化，非 Breaking Changes）

---

## 2026-03-25｜langchain-anthropic 1.4：AnthropicPromptCachingMiddleware 正式发布

**版本**：langchain-anthropic 1.4
**性质**：🟡 Minor（SDK 能力增强）
**来源**：[GitHub Release](https://github.com/langchain-ai/langchain/releases/tag/langchain-anthropic%401.4.0)

### 变更要点

| 变更 | 说明 |
|------|------|
| **AnthropicPromptCachingMiddleware** | 对 system message 和 tool definitions 应用显式缓存（Explicit Cache Control） |
| **cache_control kwarg 委托** | 新增 `cache_control` 参数直接委托至 Anthropic 顶层参数 |
| **ModelProfile 刷新** | 同步更新 model profile 数据 |

**为什么重要**：Anthropic 的 Prompt Caching 功能允许将 system prompt 和工具定义缓存于上下文，相比每次重新传输可显著降低 token 成本。langchain-anthropic 1.4 将此能力以 Middleware 形式开放，使缓存策略对开发者透明可控。

**版本判断**：Minor（SDK 功能增强，非 Breaking Changes）

---

## 2026-03-25｜langchain-core 1.2.22：安全补丁 + flow_structure 序列化器

**版本**：langchain-core 1.2.22
**性质**：🟢 Patch（安全 + 稳定性）
**来源**：[GitHub Release](https://github.com/langchain-ai/langchain/releases/tags/langchain-core==1.2.22)

### 变更要点

| 类别 | 变更 |
|------|------|
| **安全性** | 通过升级 pypdf、tinytag 修复安全漏洞；防止 FileWriterTool 中的路径遍历 |
| **Bug 修复** | redis lock_store 崩溃修复（redis 包未安装时）；非 OpenAI 提供商的 HITL resume 保留完整 LLM 配置 |
| **新功能** | `flow_structure()` 序列化器：Flow 类的内省支持 |
| **重构** | urllib → requests（pdf loader）；Any 类型 callback/model 字段改为可序列化类型 |

**评估**：安全补丁为主，pypdf/tinytag 升级表明依赖漏洞修复进入常规节奏；flow_structure() 序列化器对调试工具链有积极意义

---

## 2026-03-24｜补丁更新（langchain 1.2.13 / langchain-core 1.2.21 / langchain-openai 1.1.12）

**版本**：langchain 1.2.13、langchain-core 1.2.21、langchain-openai 1.1.12
**性质**：🟢 Patch（多项依赖和稳定性修复）
**来源**：[GitHub Releases](https://github.com/langchain-ai/langchain/releases)

### 变更要点

| 包 | 版本 | 关键变更 |
|----|------|---------|
| langchain | 1.2.13 | LangSmith 集成元数据增强（create_agent、init_chat_model）、pytest 输出优化 |
| langchain-core | 1.2.21 | ModelProfile 字段修复（缺失字段补充 + schema drift 告警）|
| langchain-openai | 1.1.12 | min core version 修复、支持 phase 参数、streaming function_call namespace 保留、token counting 图像句柄泄漏修复 |

**评估**：均为常规补丁，以稳定性修复和依赖升级为主，无 Breaking Changes

---

## 2026-03-23｜LangSmith Fleet 发布（Agent Builder 重命名）

**版本**：无版本号（产品重命名）
**性质**：🟡 Minor 产品重构
**来源**：[LangChain Blog](https://blog.langchain.com/introducing-langsmith-fleet/) | [LangChain Changelog](https://changelog.langchain.com/announcements/agent-builder-is-now-langsmith-fleet)

### 变更内容

LangChain 宣布将 **Agent Builder** 重命名为 **LangSmith Fleet**，定位为企业级 AI Agent 构建与管理平台。

**核心变化**：
- **产品定位升级**：从单一 Agent 构建工具 → 企业多 Agent 协作治理平台
- **新增企业能力**：权限管理（Permissions）、凭证管理（Credentials）、多 Agent  Oversight
- **无代码入口**：提供模板化方式，非技术用户也可构建 Agent
- **名称变更**：产品 UI、文档、官网均已更新为新名称
- **兼容性**：所有现有 Agent、配置、集成保持兼容，无 Breaking Changes

**为什么重要**：
这是 LangChain 从"开发者框架"向"企业平台"战略延伸的明确信号。Fleet 的权限和凭证管理能力，直接对应 RSAC 2026 期间 Agentic AI 安全讨论中的"身份治理"需求。

**版本判断**：Minor（产品更名 + 功能扩展，无破坏性变更）

---

## 2026-03｜LangChain × NVIDIA 企业级 Agent 平台

**版本**：战略合作（无具体版本号）
**性质**：🟡 生态系统
**来源**：[LangChain 官方新闻](https://blog.langchain.com/nvidia-enterprise/)

LangChain 与 NVIDIA 联合发布企业 Agentic AI 平台，在 RSAC 2026 期间（3月23-26日）宣布：

- **目标**：结合 LangChain 的 Agent 开发框架 + NVIDIA AI 基础设施，实现企业级生产部署
- **覆盖**：构建、部署、监控全生命周期
- **NVIDIA 能力**：NIM 微服务、CUDA 加速、企业级安全

**版本判断**：Minor（合作公告，非代码版本更新）

---

## 2026-03｜LangGraph Deep Agents SDK 更新

**版本**：Deep Agents SDK（独立包）
**性质**：🟢 Patch / 特性更新
**来源**：[LangChain Blog - Autonomous Context Compression](https://blog.langchain.com/autonomous-context-compression/)

### 值得关注的更新

- **Autonomous Context Compression**：Deep Agents SDK 新增功能，允许模型自主压缩自身上下文窗口，减少 token 消耗
- **Open SWE 发布**：基于 Deep Agents + LangGraph 的开源代码 Agent 框架，专为内部编码任务设计
- **LangSmith CLI & Skills**：AI 编码 Agent（Codex、Claude Code、Deep Agents CLI）的 LangSmith 生态集成技能包

**版本判断**：Patch（工具增强，不影响主框架）

---

## 2026-03｜LangChain v1.x 稳定版

**版本**：LangChain 1.x（主版本）
**性质**：🔴 Major 架构更新
**来源**：[LangChain Release Notes](https://github.com/langchain-ai/langchain/releases)

### 关键里程碑

LangChain 1.0 正式发布（与 LangGraph 1.0 GA 同步），代表框架从"实验性"到"生产就绪"的跨越：

- **API 稳定性承诺**：语义化版本控制，Breaking Changes 需 Major 版本升级
- **LangChain Core**：核心接口稳定，第三方集成需明确兼容性声明
- **LangChain Expression Language (LCEL)**：链式调用统一语法
- **生产级 Tracing**：LangSmith 深度集成，支持结构化日志

**版本判断**：Major（生产就绪，API 稳定承诺）

> ⚠️ **注意**：LangChain 1.0 GA 是 2025 年 10 月的重大里程碑，建议回顾官方 Release Notes 确认历史版本完整性。

---

## 历史版本速查

| 时间 | 版本 | 关键变化 |
|------|------|---------|
| 2025-10 | LangChain 1.0 GA + LangGraph 1.0 GA | 生产就绪，API 稳定 |
| 2025-Q4 | LangSmith Agent Builder | 企业级 Agent 构建 |
| 2026-03 | Agent Builder → LangSmith Fleet | 重命名 + 企业治理 |
| 2026-03 | Deep Agents SDK | Autonomous Context Compression |

---

## 下次检查计划

- 每日检查 LangChain Blog 和 GitHub Releases
- 关注 LangChain 1.x 的 Breaking Changes 公告
- 监控 NVIDIA 合作平台正式发布

---

*本文件由 AgentKeeper 自动维护 | 追踪频率：每日*

---

## 2026-03-30｜langchain-core 1.2.23：trace invocation params 回归 + requests 升级

**版本**：langchain-core==1.2.23
**性质**：🟢 Patch（回归修复 + 依赖升级）
**来源**：[GitHub Release](https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D1.2.23)

### 变更要点

| 变更 | 说明 |
|------|------|
| **Revert #36322** | 回归"fix: trace invocation params in metadata"（#36322），表明该修复引入了新问题 |
| **requests 升级** | requests 从 2.32.5 升级至 2.33.0（依赖安全补丁）|

**评估**：常规补丁发布，Revert 说明 langchain-core 团队对 trace 功能的变更较谨慎，避免破坏性影响

---

## 2026-03-27｜LangGraph 1.1.3：Runtime 执行信息 + checkpoint-postgres 3.0.5

**版本**：LangGraph 1.1.3（2026-03-18）+ cli 0.4.19（2026-03-20）+ checkpoint-postgres 3.0.5
**性质**：🟡 Minor（Runtime 能力增强）
**来源**：[GitHub Release - langgraph 1.1.3](https://github.com/langchain-ai/langgraph/releases/tag/langgraph%401.1.3)

### 变更要点

| 变更 | 说明 |
|------|------|
| **Execution info in runtime** | 新增 `execution_info` 输出，可在 runtime 运行时获取每步执行详情（用于可观测性、性能分析） |
| **checkpoint-postgres 3.0.5** | LangGraph checkpoint PostgreSQL 存储后端补丁更新 |
| **cli 0.4.19** | 新增 `deploy revisions list` 命令 |

**为什么重要**：`execution_info` 的引入是 LangGraph 可观测性能力的重要升级。在生产环境调试多步骤 Agent 工作流时，能够在 runtime 级别获取每步执行的详细信息（耗时、token 消耗、工具调用结果）对于定位 Agent 行为异常至关重要。这是 LangGraph 从"能跑"到"能运维"的重要一步。

**版本判断**：Minor（功能增强，非 Breaking Changes）

---

