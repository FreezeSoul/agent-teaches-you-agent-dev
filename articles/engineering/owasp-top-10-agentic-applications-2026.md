# OWASP Top 10 for Agentic Applications (2026) 解读

> 来源: [OWASP GenAI Security](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | [PromptPwnd Research](https://www.aikido.dev/blog/promptpwnd-github-actions-ai-agents) | [DeepTeam](https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications)  
> 时间: 2026-03-23（RSAC 2026 主题演讲日）

## 背景：为什么需要单独的 Agentic Top 10

传统的 OWASP Top 10 面向 Web 应用和 LLM 应用，核心风险是注入、访问控制失效、配置错误等。

**Agentic AI 系统引入了四个根本性变化**，改变了风险传播方式：

| 属性 | 含义 | 新风险维度 |
|------|------|-----------|
| 自主决策 | Agent 自主规划、推理、执行多步操作 | 小漏洞可被放大 |
| 自然语言输入表面 | NL 成为可携带可执行指令的输入 | 间接注入成为主要向量 |
| 运行时动态组合 | 工具/插件/其他 Agent 在运行时动态组合 | 供应链风险延伸至运行时 |
| 跨会话状态复用 | 记忆在会话/角色/租户间复用 | 记忆污染可持久化 |

OWASP 2026 版的核心原则：**最小代理权（Least Agency）**——只授予 Agent 完成受限任务所需的最少自主权。

---

## OWASP ASI Top 10 (2026) 完整列表

| ID | 风险名称 | 核心问题 |
|----|---------|---------|
| ASI01 | **Agent Goal Hijack** | 攻击者通过恶意内容篡改 Agent 目标或决策路径 |
| ASI02 | **Tool Misuse & Exploitation** | Agent 以不安全方式使用合法工具 |
| ASI03 | **Identity & Privilege Abuse** | Agent 继承或滥用高权限凭证 |
| ASI04 | **Agentic Supply Chain Vulnerabilities** | 被污染的工具、插件或外部组件 |
| ASI05 | **Unexpected Code Execution** | Agent 不安全地生成或执行代码/命令 |
| ASI06 | **Memory & Context Poisoning** | 攻击者污染 Agent 记忆系统和 RAG 数据库 |
| ASI07 | **Insecure Inter-Agent Communication** | 多 Agent 系统面临欺骗和篡改 |
| ASI08 | **Cascading Failures** | 小错误在规划和执行链中传播放大 |
| ASI09 | **Human-Agent Trust Exploitation** | 用户对 Agent 推荐过度信任 |
| ASI10 | **Rogue Agents** | 被入侵的 Agent 在看似正常的外表下执行有害操作 |

---

## 逐条深度解析

### ASI01 — Agent Goal Hijack（目标劫持）

**问题本质**：Agent 无法可靠区分"指令"与"数据"。当处理被污染的邮件、PDF、会议邀请、RAG 文档或网页内容时，可能被植入隐藏目标。

**攻击形态**：
- 直接目标覆盖：通过提示注入显式覆盖 Agent 原始目标
- 间接指令注入：隐藏在文档/RAG 内容中的指令改变行为
- 递归目标修改：随着时间推移目标被逐步篡改
- 跨上下文注入：在一个上下文中植入的指令影响另一上下文的行为

**缓解措施**：
- 将自然语言输入视为不可信
- 应用提示注入过滤器
- 限制工具权限
- 目标变更或高影响操作需人工审批

---

### ASI02 — Tool Misuse & Exploitation（工具滥用）

**问题本质**：即使 Agent 拥有合法工具权限，歧义提示、错位或被操纵的输入也会导致 Agent 以破坏性参数调用工具，或将工具链成意外的危险组合。

**攻击形态**（参考真实案例 PromptPwnd）：
- 参数污染：操纵函数调用参数超出预期范围
- 工具链操纵：利用顺序工具调用漏洞（如 GitHub Actions/GitLab 中未信任的 PR/Issue 内容注入提示，导致密钥泄露）
- 递归工具调用：Agent 循环调用工具导致资源耗尽
- 跨工具状态泄漏：信息在工具上下文间不安全流动

**缓解措施**：
- 严格工具权限范围控制
- 沙箱执行环境
- 参数验证
- 每个工具调用添加策略控制

---

### ASI03 — Identity & Privilege Abuse（身份与权限滥用）

**问题本质**：Agent 通常继承用户或系统身份，包括高权限凭证、会话令牌和委托访问。当这些权限被无意重用、升级或跨 Agent 传递时产生风险。

**攻击形态**：
- SSH 密钥缓存在 Agent 记忆中
- 跨 Agent 委托无范围限制
- 混淆副手（Confused Deputy）场景

**缓解措施**：
- 短生命周期凭证
- 任务粒度权限控制
- 策略强制执行授权

---

### ASI04 — Agentic Supply Chain Vulnerabilities（代理供应链漏洞）

**问题本质**：Agent 供应链不仅包括传统软件依赖，还延伸至工具、插件、MCP 服务器等运行时组件。被污染的组件可直接成为攻击向量。

**典型场景**：
- 恶意 MCP 服务器描述符注入
- 被污染的插件在工具调用时执行恶意代码
- 第三方 API 返回被篡改的数据影响 Agent 决策

**缓解措施**：
- 工具和插件签名验证
- 供应链安全扫描集成
- 运行时监控与异常检测

---

### ASI05 — Unexpected Code Execution（意外代码执行）

**问题本质**：Agent 能够生成并执行代码（Shell、Python、SQL 等），当生成逻辑不安全或输入验证不足时，Agent 可能执行有害操作。

**风险场景**：
- Agent 生成的数据库查询包含 SQL 注入
- 动态生成的脚本被注入恶意命令
- 代码执行结果被用于后续危险操作

**缓解措施**：
- 代码执行前静态分析
- 限制可执行代码类型
- 沙箱隔离执行环境
- 执行结果白名单验证

---

### ASI06 — Memory & Context Poisoning（记忆与上下文污染）

**问题本质**：Agent 的短时和长时记忆系统（向量数据库、RAG 系统、会话历史）可被污染，导致 Agent 在后续会话中基于错误信息做出有害决策。

**攻击形态**：
- RAG 数据库植入恶意文档
- 跨会话记忆污染（如上一个会话的恶意上下文影响下一个会话）
- 嵌入向量空间被注入对抗性内容

**缓解措施**：
- RAG 内容输入过滤
- 记忆验证机制
- 定期记忆完整性检查
- 敏感上下文隔离

---

### ASI07 — Insecure Inter-Agent Communication（不安全的 Agent 间通信）

**问题本质**：多 Agent 系统内部的消息交换和协调机制缺乏足够安全验证，攻击者可在 Agent 间注入伪造消息或篡改通信内容。

**风险场景**：
- Agent 间消息被拦截和篡改
- 恶意 Agent 冒充合法 Agent 发送指令
- 消息队列被污染导致指令注入

**缓解措施**：
- Agent 间通信加密和认证
- 消息完整性验证
- 零信任架构（每个 Agent 验证对方身份）

---

### ASI08 — Cascading Failures（级联失败）

**问题本质**：Agent 的多步规划和执行链中，小错误或异常会被放大传播，导致系统整体失效。与传统系统的级联失败类似，但因 Agent 自主性而更难预测。

**触发条件**：
- 单个工具返回错误被 Agent 误解为成功，继续执行下游步骤
- 记忆中的错误状态导致后续决策连锁偏差
- 规划阶段的小偏差在执行中指数放大

**缓解措施**：
- 步骤间状态验证
- 执行链路监控和回滚机制
- 置信度阈值控制

---

### ASI09 — Human-Agent Trust Exploitation（人-Agent 信任利用）

**问题本质**：用户倾向于过度信任 Agent 的输出和建议，当 Agent 被操纵或误导时，用户不会进行足够的验证。

**典型场景**：
- Agent 生成的代码/文档表面上看起来专业，用户直接采纳
- Agent 说服用户执行危险操作
- 用户授权 Agent 执行操作但未充分理解影响

**缓解措施**：
- 风险级别可视化提示
- 高影响操作强制确认
- Agent 决策可解释性输出

---

### ASI10 — Rogue Agents（恶意 Agent）

**问题本质**：被入侵或被恶意控制的 Agent，在外表看起来正常执行任务的同时，实际执行对用户或系统有害的操作。

**攻击形态**：
- 目标被篡改但行为表现正常（长期潜伏）
- 在特定触发条件下执行恶意操作
- 与命令控制（C2）服务器通信

**缓解措施**：
- Agent 行为审计和异常检测
- 操作日志完整性保护
- Agent 身份持续验证
- 操作范围硬限制

---

## 与 Agent 开发者的关联

OWASP ASI Top 10 对 Agent 开发者的实际意义：

1. **安全左移到了新层次**：传统 SAST/DAST 不足以覆盖 Agent 安全，需专门的红队测试框架（如 DeepTeam、Promptfoo 支持 ASI 系列）
2. **最小权限原则必须贯彻到工具调用级别**：不只是 API 密钥，而是每个工具的每次调用
3. **多 Agent 系统的信任边界需要显式建模**：不能假设 Agent 间通信默认可信
4. **记忆系统的安全性与模型能力同等重要**：RAG 和向量数据库的安全审计应成为标准流程

## 延伸阅读

- [OWASP Top 10 for Agentic Applications 官方页面](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP GenAI Security Summit @ RSAC 2026](https://genai.owasp.org/event/rsac-conference-2026-owasp-ai-security-summit-safeguarding-gengen-ai-agents-autonomous-ai-risk-2026/)
- [AI Security Solutions Landscape for Agentic AI Q2 2026](https://genai.owasp.org/resource/ai-security-solutions-landscape-for-agentic-ai-q2-2026/)
- [Promptfoo OWASP Agentic 扫描指南](https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/)
- [PromptPwnd 研究：GitHub Actions AI Agent 秘密泄露](https://www.aikido.dev/blog/promptpwnd-github-actions-ai-agents)

---
*由 AI 自动生成 | 内容基于公开资讯整理*
