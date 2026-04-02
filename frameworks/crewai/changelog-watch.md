# CrewAI Changelog Watch

> 追踪 CrewAI 版本变化与生态动态

---

## 更新记录

### 2026-04-01 · v1.13.0a6 ⭐（最新预发布）

**来源**：[GitHub Release v1.13.0a6](https://github.com/crewaiinc/crewai/releases/tag/v1.13.0a6) | 仓库名已确认为 `crewaiinc/crewai`（非 crewAIInc/crewAI）

| 变更类型 | 变更内容 |
|---------|---------|
| **性能** | **Lazy Event Bus**：实现惰性事件总线，禁用 tracing 时跳过跟踪，显著降低框架开销 |
| **文档** | RBAC 权限级别修复（与实际 UI 选项对齐）|
| **贡献者** | @alex-clawd、@joaomdmoura、@lucasgomide |

**值得关注的 v1.13.0 演进线索**（从 a3 ~ a6 累积）：
- **GPT-5.x stop 参数处理**：修复 GPT-5.x 模型不支持 `stop` API 参数的问题（v1.13.0a3）
- **Token Usage 事件化**：`LLMCallCompletedEvent` 新增 token 使用量数据（v1.13.0a3）
- **Flow → Pydantic BaseModel**：将 Flow 转换为 Pydantic BaseModel（v1.13.0a3，结构性变更）
- **SSO 配置指南**：新增完整 SSO 配置指南（v1.13.0a3）
- **Agent Capabilities 文档**：新增 Agent Capabilities 概述和改进 Skills 文档（v1.13.0a3）

**为什么重要**：
- Lazy Event Bus 是性能优化方向——CrewAI 在 v1.13 中开始关注框架自身开销，而非仅增加功能
- GPT-5.x stop 参数修复表明主流框架正在适应 GPT-5 的 API 差异
- Flow → Pydantic 转换是CrewAI 内部架构升级，可能影响自定义 Flow 的编写方式

### 2026-04-01（v1.13.0a5）

**2026-03-31 · v1.13.0a3** ⭐
- **Token Usage 数据事件化**：LLMCallCompletedEvent 新增 token 使用量数据，AMP（Agent Memory Protocol）可提取和发布工具元数据
- **GPT-5.x stop 参数修复**：修复 GPT-5.x 模型不支持 `stop` API 参数的问题
- Agent capabilities 文档多语言修复

**2026-03-26 · v1.12.2**
- 保留 `@human_feedback` 方法返回值作为 flow 输出（emit 模式）
- 安全策略和报告说明修订

**2026-03-26 · v1.12.1** ⭐
- HumanFeedbackRequestedEvent 新增 request_id
- **Qdrant Edge 存储后端**：CrewAI Memory System 新增 Qdrant Edge 支持，针对边缘部署场景的向量数据库选择
- docs-check 命令：自动分析变更并生成带翻译的文档
- 阿拉伯语支持（文档全面翻译）

**2026-03-26 · v1.12.0** ⭐
- Qdrant Edge 存储后端正式版
- 多语言文档（阿拉伯语等）
- 企业级发布流程改进

**2026-03-25（v1.11.1）补丁更新**

**2026-03-23 · v1.11.1 正式版**
- 继 v1.11.0 之后的小版本补丁
- 包含 bug 修复和稳定性改进
- CrewAI 文档更新，预计近期将有重大文档重构

> 来源：[GitHub Release 1.11.1](https://github.com/crewAIInc/crewAI/releases/tag/1.11.1)

### 2026-03-24（v1.11.x）补丁更新

**2026-03-24 · 最新补丁版本**
- **ContextVars 传播修复**：修复 ContextVars 上下文在并行工具调用线程间的传播问题，提升多线程/并行执行场景的稳定性和数据一致性
- 工具集成可靠性改进

### 2026-03（v1.10.1 → v1.11.0）

**2026-03-18 · v1.11.0 正式版**
- 稳定版本，v1.11.0rc2 直接转正
- 主要变更继承 rc2：Bug 修复、安全依赖升级（authlib、PyJWT、snowflake-connector-python）、pip install unsafe mode 修复（`os.system` → `subprocess.run`）
- MCP 文档更新

**2026-03-17 · v1.11.0rc2**
- 修复 LLM 响应处理与序列化
- 安全依赖升级（authlib、PyJWT、snowflake-connector-python）
- pip install unsafe mode 修复：`os.system` → `subprocess.run`
- MCP 文档更新、Exa Search Tool 文档改进、OTEL collectors 文档更新

**2026-03-15 · v1.11.0rc1** ⭐
- **A2A Plus API token 认证**：Agent-to-Agent 通信增加标准化 Token 认证，企业协作场景安全性提升
- **Plan-Execute 模式**：实现规划与分步执行的显式分离，增强复杂任务稳定性与可观测性
- **代码解释器沙盒逃逸修复**：修复可能导致容器/进程逃逸的严重漏洞

**2026-03-14 · v1.10.2rc2**
- 移除只读存储操作的排他锁

**2026-03-13 · v1.10.2rc1**
- 新增 release 命令，触发 PyPI 自动发布
- 修复跨进程/线程安全的锁机制
- ContextVars 跨所有线程和执行器边界传播
- 异步任务线程中的 ContextVars 传播

**2026-03-11 · v1.10.2a1** ⭐
- **Anthropic 工具搜索**：支持在执行时动态搜索、保存 token 并注入合适工具
- 新增更多 Brave Search 工具
- 代码解释器沙盒逃逸修复
- MCP 工具解析修复，消除所有共享可变连接
- gitpython 升级至 ≥3.1.41，修复 CVE path traversal 漏洞
- 内存类重构为可序列化

**2026-03-04 · v1.10.1**
- Gemini GenAI 升级
- 多项 Bug 修复（executor listener 递归问题、Gemini 并行函数响应分组、human_feedback LLM 参数处理）
- MCP 和 platform tools 加载逻辑修复
- A2A 支持 Jupyter 环境 event loop
- PyPDF 升级 4.x → 6.7.4（Dependabot alerts）
- 关键和高危 Dependabot 安全告警修复

---

## 关键版本节点

| 版本 | 日期 | 关键变化 |
|------|------|---------|
| **v1.11.0** | 2026-03-18 | A2A Plus Token Auth、Plan-Execute 模式、沙盒安全修复 |
| **v1.10.2a1** | 2026-03-11 | Anthropic 工具搜索、MCP 解析改进、gitpython CVE 修复 |
| **v1.10.1** | 2026-03-04 | Gemini 升级、安全补丁批量修复 |
| **v1.10.0** | 2026-Q1 | A2A 协议公告、MCP 工具集成 |
| **v1.0+** | 2025-Q4 | Hierarchical Agent 模式、多 Agent 协作成熟 |
| **v0.30+** | 2025-Q1 | MCP 集成、A2A 协议概念引入 |
| **v0.20+** | 2025-Q4 | Hierarchical 模式稳定 |
| **v0.10+** | 2025-Q2 | 初始生产版本 |

---

## 版本趋势观察

### v1.x 时代的关键演进方向

1. **A2A 协议深度集成**：从 v1.10.0 引入到 v1.11.0 的 Plus Auth，A2A 已从实验性功能走向企业级标准
2. **安全成熟度提升**：沙盒逃逸修复、CVE 依赖升级、Token 认证——CrewAI 在快速迭代中持续加固安全
3. **Plan-Execute 模式**：明确将规划与执行分离，反映多 Agent 系统的工程化趋势
4. **MCP 生态整合**：从 v0.30 的 MCP 工具集成到 v1.10 的 MCP 解析全面改进

---

## 参考来源

- [CrewAI Changelog](https://docs.crewai.com/en/changelog)
- [CrewAI GitHub Releases](https://github.com/crewAIInc/crewAI/releases)
- [CrewAI Blog](https://crewai.com/blog)

---

*由 AgentKeeper 自动追踪 | 最后更新：2026-03-23*
