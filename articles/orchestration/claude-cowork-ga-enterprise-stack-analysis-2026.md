# Claude Cowork GA：企业采购入场券的诞生

> 4月9日，Anthropic 将 Claude Cowork 推至 GA，同时发布六项企业级功能。这不是常规的功能迭代——这是一份企业采购清单的完整交付。

---

## Cowork 是什么：Claude 有手了

Claude Cowork 是 Anthropic 在 2026 年 1 月推出的桌面 AI Agent。与在浏览器窗口中对话不同，Cowork 运行在用户的 macOS 或 Windows 机器上，可以访问本地文件、文件夹和应用程序——在用户的授权下查看屏幕、打开文件、输入文字、点击导航。

典型使用场景：
- 将混乱的 Downloads 文件夹整理为项目目录
- 从桌面一堆 PDF 文件中起草报告
- 根据收据文件夹生成电子表格
- 研究一个主题并将摘要保存到指定位置
- 审阅合同并提取关键条款

1月发布时是 Research Preview，4月9日升 GA，意味着 Anthropic 认为它已经稳定到可用于日常专业工作——企业团队可以带着正式的安全控制清单来评估部署了。

---

## 这不是六个独立功能，而是一套治理体系

官方列出了六项"企业功能"，但如果只是功能清单，就错过了重点：**这六项是一个整体，其存在是为了满足 IT 采购流程中的特定要求，而不是为了提升个人用户的工作效率。**

| 功能 | 解决的采购问题 |
|------|-------------|
| RBAC（基于角色的访问控制）| "我们能控制谁可以用什么功能吗？" |
| 小组消费限额 | "我们能按部门做成本分摊吗？" |
| OpenTelemetry 可观测性 | "CISO 能看到审计日志吗？" |
| 扩展使用分析 | "谁在用？用在哪里？值不值？" |
| Zoom MCP 连接器 | "能和我们的视频会议系统集成吗？" |
| Dispatch + Computer Use | "能从手机远程控制桌面 Agent 吗？" |

前五项是**防守型功能**——它们的存在是为了让企业安全团队、合规团队和财务团队在采购审批表上签字。第六项 Dispatch + Computer Use 是**进攻型功能**——它是真正改变知识工作者工作方式的差异化能力。

---

## 六项功能的实际工程细节

### 1. RBAC：粒度到连接器和工具级别

RBAC 通过 SCIM 协议与身份提供商（Okta、Azure AD 等）集成，管理员可以在组（Group）级别分配自定义角色。

**实际粒度**：
- 可以对营销团队开启 Cowork，但对承包商关闭
- 可以让营销使用 Canva 和 Google Drive 连接器，但将 GitHub 连接器限制为仅工程团队
- 可以对高级用户开启 Computer Use，但对普通用户关闭
- **粒度到单个连接器和单个工具级别**——不是简单的"开/关"，而是"允许读但不允许写"

**当前缺口**：不支持基于时间的访问控制（如仅在工作时间允许使用），也不支持与 Entra ID 的条件访问集成。对于有严格数据residency要求的受监管行业，这些是真实缺口。

### 2. 小组消费限额：优雅降级而非中断

消费限额在组级别设置月度上限。当组接近限额时，成员会收到通知；当组达到限额时，任务不会中途失败，而是**进入队列等待**——这是一个重要的体验细节，说明 Anthropic 考虑到了"不能因为限额导致正在执行的任务损坏数据"。

**重要范围说明**：消费限额仅适用于 Cowork 本身，不适用于用户在浏览器中使用 Claude 的对话。如果团队某人在浏览器里用了好几个小时的 Claude，那不计入 Cowork 组的限额。这个范围界定需要在做预算预测时注意。

### 3. OpenTelemetry：企业级审计的基础

Cowork 现在为以下事件发出 OpenTelemetry 格式的 trace：
- 每次工具和连接器调用
- 每次读取或修改的文件
- 每次使用的 Skill
- 每次 AI 发起的行为是通过手动批准还是自动批准

这些事件可以接入标准 SIEM 管道——Splunk、Cribl、Datadog，或者任何支持 OpenTelemetry 的监控系统。共享的用户账户标识符将 OTel 事件与 Compliance API 记录关联，可以精确重建某个会话中 Claude 访问过的所有内容。

> **工程意义**：OpenTelemetry 支持是 Cowork 与其他桌面 AI Agent 的根本性差异。对于受监管行业（医疗、金融、政府），CISO 要求"查看 AI Agent 上季度访问的所有内容的审计跟踪"，现在答案是"可以"。这改变了采购对话的走向。

**套餐限制**：OpenTelemetry 支持仅在 Team 和 Enterprise 计划中可用，Pro 计划不支持。

### 4. 使用分析：回答"谁在用"，但无法回答"产生了什么价值"

分析数据在两个地方可用：
- **管理员仪表板**：面向人类阅读的报表，支持按日期范围查看会话数和活跃用户数——对追踪采用率有用
- **Analytics API**：程序化访问，支持按用户维度的 Cowork 活动、Skill 调用次数、连接器使用量，以及日/周/月活跃用户指标，与现有的 Chat 和 Claude Code 数据并行

**当前缺口**：可以回答"有人在用吗""谁在用""用了哪些集成"。无法轻松回答"产生了什么成果""哪些任务 Claude 完成得好，哪些完成得差"。Anthropic 将 Outcomes API 列为研究预览阶段，在它 GA 之前，你只能衡量活动，无法衡量影响。

### 5. Zoom MCP 连接器：会议后工作流的自动化

Zoom 官方发布了原生 MCP 连接器，可以将会议相关内容直接接入 Cowork 工作流。

测试过的工作流示例：Cowork 从定期的周一站会拉取 Zoom 转录文本，格式化为项目更新条目，起草每周状态邮件。连接器处理身份验证和数据获取，Claude 处理格式化和综合。整个配置大约需要四分钟，之后无需干预。

**当前限制**：只能访问转录文本，不支持会议录制访问、不支持视频分析、不支持 Cowork 加入和参与实时会议。这些都是合理的路线图项目，但目前不存在。

### 6. Dispatch + Computer Use：改变 ROI 计算的那一项

Dispatch 允许用户从手机向桌面 Cowork 分配任务。在 GA 之前，Dispatch 只能处理文件操作和终端命令。GA 版本中，Dispatch 新增了 Computer Use 支持——你可以从手机发送任务，桌面的 Cowork 将自主打开应用程序、导航 UI、完成多步骤工作流。

这使得 Dispatch 从"有用的小工具"变成了"真正的远程助手"。非技术工作流的示例：
- "处理我邮件里的费用报告"
- "用这周的数据更新团队电子表格"

> 笔者认为：Dispatch + Computer Use 是 Cowork GA 最重要的功能。它的意义不在于任何单一功能的强大，而在于它真正实现了"手机是遥控器，桌面是执行器"的 Agent 工作形态。这是 Copilot 和 Gemini 在 2026 年都没有做到的。

---

## 被忽视的关键数据：用户是谁

Anthropic 自己的数据显示，Cowork 在早期企业采用者中的**主要用户群体不是工程师团队**，而是运营、营销、财务、法务——用于项目更新、研究冲刺、协作演示文稿制作。不是代码。

这个数据彻底改变了治理要求的性质：如果你管理的是十个开发者，你治理的是一个技术团队；如果你管理的是成百上千的知识工作者，你治理的是一个完全不同的风险面——这些人对安全边界的理解参差不齐，访问的文件可能包含机密财务数据或客户隐私信息。

这就是为什么六项企业功能不是"锦上添花"，而是"必须交付"。

---

## 企业竞品对比：不是功能对比，是生态对比

| 维度 | Claude Cowork Enterprise | Microsoft 365 Copilot | Google Gemini Enterprise |
|------|------------------------|----------------------|------------------------|
| 桌面 Agent | ✅ macOS + Windows | ⚠️ 仅 Windows | ❌ 纯浏览器 |
| 本地文件访问 | ✅ 完整本地文件系统 | ⚠️ 仅 SharePoint/OneDrive | ⚠️ 仅 Drive 连接器 |
| Computer Use | ✅ Pro/Max 计划 | ⚠️ 有限（Copilot Studio） | ❌ 不可用 |
| OpenTelemetry 审计 | ✅ 操作级别事件 | ⚠️ Microsoft Purview | ⚠️ Workspace 审计（粒度较低）|
| 消费控制 | ✅ 组级别硬上限 | ⚠️ 仅许可证级别 | ⚠️ 账单警报（非硬上限）|
| 上下文窗口 | 1M token（Opus 4.6 beta）| 128K token | 2M token（Gemini 3.1 Pro）|
| 套件独立性 | ✅ 任意技术栈 | ❌ 必须 Microsoft 365 | ❌ 必须 Google Workspace |
| 价格 | Enterprise 定制 / Pro $20/月 | ~$30/用户/月 | $30/用户/月（AI Ultra $250/月）|

**Cowork 的绝对优势**：本地文件访问和 Computer Use。Copilot 和 Gemini 是云优先架构——它们只处理存在于各自云存储中的文件。Cowork 在桌面运行，可以与机器上的任何内容交互。对于处理敏感文档（从不存放在云端的法律文件、HR 数据）的团队，这一点至关重要。

**Cowork 的当前短板**：生态深度。Microsoft 的 Purview 集成为受监管行业（医疗、金融、政府）提供了 Cowork 目前无法匹配的政策执行水平。如果你的安全团队已经建立了 Purview 工作流，Copilot 的合规故事目前确实更强。

**决策树**：
- 公司使用 Microsoft 365 → Copilot 是阻力最小的路径
- 公司使用 Google Workspace → Gemini 是自然选择
- **没有套件包袱 + 主要工作是研究密集型/长上下文任务 + 需要本地文件访问** → Cowork 是明确选择

---

## 谁现在应该部署

**立即部署**：
- 非 Microsoft/Google 生态的团队，有受监管数据（法律、医疗、HR）
- 需要本地文件访问且数据不能上云的组织
- 有 OpenTelemetry/SIEM 基础设施的安全团队，需要完整审计跟踪

**等待更适合的时机**：
- 在受监管行业，需要 Purview 级别的合规策略执行
- 需要 Outcomes API 来衡量 AI 投资回报（目前仍在研究预览）
- 需要时间让 RBAC 的细粒度控制（尤其是 Per-Tool Connector Controls）变得更加稳定和一致

---

## 企业 AI Agent 的分层战略

Anthropic 在 Cowork GA 博客中透露了其企业产品的分层战略：

| 层级 | 产品 | 目标用户 |
|------|------|---------|
| L1 | Claude Code | 开发者 |
| L2 | Cowork | 知识工作者 |
| L3 | Managed Agents | 产品构建者 |
| L4 | Mythos（即将到来）| 所有三层 |

这个分层战略意味着：Anthropic 不仅仅在构建"一个 AI 助手"，而是在构建一套覆盖技术栈所有层面的 Agent 基础设施。Cowork 是这整套战略中面向非技术人员的入口。

---

## 参考来源

- [Making Claude Cowork Ready for Enterprise — Anthropic Blog](https://claude.com/blog/cowork-for-enterprise)
- [Claude Cowork GA Enterprise Guide — FindSkill.ai](https://findskill.ai/blog/claude-cowork-ga-enterprise-guide/)
- [Claude Cowork Enterprise Features: The Complete Guide — PrimeAIcenter](https://primeaicenter.com/claude-cowork-enterprise-features/)
- [Claude Cowork GA Launch — Testing Catalog](https://www.testingcatalog.com/anthropic-launches-claude-cowork-in-general-availability/)
- [Claude Cowork RBAC and MCP Permissions — Digital Today](https://www.digitaltoday.co.kr/en/view/46883/anthropic-launches-claude-cowork-with-role-based-access-control-and-mcp-permissions-management)
- [Claude Cowork Enterprise Rollout — Blockchain News](https://blockchain.news/news/anthropic-claude-cowork-enterprise-rollout-april-2026)
- [Securing Claude Cowork — Harmonic Security](https://www.harmonic.security/resources/securing-claude-cowork-a-security-practitioners-guide)
- [Set up role-based permissions on Enterprise plans — Claude Help Center](https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans)
