# OWASP Agentic Skills Top 10：AI Agent 技能层安全风险地图

> **核心论点**：当行业聚焦于 LLM 安全和 MCP 协议层安全时，一个更脆弱的中介层正在被大规模引入生产系统——AI Agent Skills。作为连接模型决策与真实世界执行的关键行为抽象层，Skills 缺乏任何成熟生态应有的安全基线。OWASP AST10 是首个系统填补这一空白的权威框架。
>
> **本文要回答**：AST10 覆盖哪些风险？它们与现有 OWASP LLM Top 10 的关系是什么？为什么 Skills 安全是 2026 年 Agent 落地的最大盲区？

**来源**：[OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/)（OWASP Foundation，Q1 2026）
**关联项目**：Agentic Skills Top 10 — [kenhuangus/agentic-skills-top-10](https://github.com/kenhuangus/agentic-skills-top-10)
**性质**：安全风险标准（OWASP 官方项目）
**评分**：18/20
**演进阶段**：Stage 12（⚡ Harness Engineering）+ Stage 10（Skill）
**主题关联**：本文是 `agent-skills-survey-architecture-acquisition-security-2026.md` 的安全续篇——前者讨论 Skills 架构与演进，后者聚焦 Skills 安全风险全景

---

## 一、为什么 Skills 安全是一个独立的工程问题

### 1.1 定位：MCP = 如何通信，AST10 = 如何行动

理解 AST10 的前提是厘清其在 Agent 架构中的位置：

| 架构层次 | 负责问题 | 已有标准 |
|---------|---------|---------|
| **LLM 层** | 模型输出质量与对齐 | RLHF、SFT、安全评测基准 |
| **MCP 层** | Agent 如何调用外部工具（协议层）| Model Context Protocol（Linux Foundation）|
| **Skills 层** | Agent 如何编排行为完成任务（行为层）| **空白**——AST10 要填补的位置 |
| **执行层** | 代码实际运行的系统环境 | 传统安全：容器/SAST/DAST |

> "While significant attention has been devoted to securing large language models (LLMs) and the Model Context Protocol (MCP) tool layer, the intermediate behavior layer—embodied in agentic skills—has emerged as a particularly vulnerable and under-protected component of the AI agent ecosystem."
> — [OWASP AST10 Overview](https://owasp.org/www-project-agentic-skills-top-10/)

这意味着：即便 LLM 安全且 MCP 协议无懈可击，Skills 层的漏洞仍能导致完整的系统沦陷。

### 1.2 Skills 的「 lethal trifecta」：为什么它比协议层更危险

OWASP 提出了一个关键概念——**Lethal Trifecta**（Simon Willison / Palo Alto Networks，2026）：

当一个 Skill 同时具备三个特性时，它就是最高风险等级：

1. **访问私密数据**：SSH keys、API credentials、钱包文件、浏览器数据
2. **接触不可信内容**：Skill 指令本身、memory 文件、email、Slack 消息
3. **具备外部通信能力**：网络出口、webhook 调用、curl 执行

> "Most production agent deployments today satisfy all three conditions."

这意味着**大多数生产级 Agent 部署天然处于 Lethal Trifecta 状态**——而 Skills 层是打穿这三层防线的最短路径。

### 1.3 数据：危机已经在发生

| 指标 | 数值 | 来源 |
|------|------|------|
| Skills 扫描总量 | 3,984 | Snyk ToxicSkills（2026/02）|
| 含安全缺陷的 Skills | 1,467（36.82%）| Snyk ToxicSkills |
| 含严重问题的 Skills | 534（13.4%）| Snyk ToxicSkills |
| 确认的恶意 Payload | 76+ | Snyk ToxicSkills |
| ClawHavoc 恶意技能 | 1,184 个 | Antiy CERT（2026/02）|
| OpenClaw 公网暴露实例 | 135,000+ | SecurityScorecard（2026/03）|
| 独立 CVE（仅 OpenClaw）| 9（3 个有公开利用）| Endor Labs |

> "The ClawHub registry—the primary marketplace for OpenClaw skills—became the first AI agent registry to be systematically poisoned at scale."
> — [OWASP AST10](https://owasp.org/www-project-agentic-skills-top-10/)

---

## 二、AST10 十类风险详解

### AST01 — Malicious Skills（恶意 Skills）

**严重性**：Critical | **受影响平台**：全部

**攻击机制**：攻击者在 Skills 市场发布看似合法的技能包，实际嵌入了隐藏的恶意 Payload——凭据窃取器、反向 shell、后门，或社交工程指令。

**为什么独特于 Skills**：传统恶意包只利用代码层，Malicious Skills 同时利用**代码层**（shell 脚本、Python 调用）和**自然语言指令层**（Markdown 文本指示 Agent 执行窃取操作）。Snyk 确认：100% 的恶意 Skills 同时结合了两种攻击向量。

**真实案例**：
- ClawHavoc 活动（2026/01）：1,184 个恶意 Skills，全部共享 C2 IP 91.92.242[.]30，投递 AMOS（Atomic Stealer）窃取 macOS 加密钱包、SSH keys、浏览器凭据
- 仅需 SKILL.md 中的三行 Markdown 即可指示 Agent 读取 SSH key 并外传（Snyk，2026/02）

**关键缓解**：ed25519 密码签名、发布时行为分析、不可信 Skills 的隔离执行

---

### AST02 — Supply Chain Compromise（供应链攻陷）

**严重性**：Critical | **受影响平台**：全部

**攻击机制**：Skills 注册表和分发渠道缺乏成熟生态（如 npm/PyPI/Cargo）已有的 provenance 控制。攻击者通过注册为开发者发布恶意包，或对已有流行 Skills 进行供应链注入。

**真实案例**：
- ClawHavoc：12 个 publisher 账户发布了 1,184 个恶意 Skills
- CVE-2025-59536（CVSS 8.7）：Claude Code 仓库级配置文件可在项目打开时静默执行任意 shell 命令并外传 API keys，patch 已在数月前发布但 disclosure 于 2026/02/25 才公开

---

### AST03 — Over-Privileged Skills（权限过载 Skills）

**严重性**：High | **受影响平台**：全部

**攻击机制**：Skills 声明了超出其功能所需的系统权限，导致即使是无意恶意的 Skill 也能造成大规模凭据泄露。

**真实案例**：
- Snyk（2026/02）发现 280+ 个" leaky Skills"——权限过度扩张导致 API keys 和 PII 大规模暴露
- 问题根因：Skills 缺少最小权限 Manifest Schema 定义

**关键缓解**：Least-privilege manifests + schema validation

---

### AST04 — Insecure Metadata（不安全元数据）

**严重性**：High | **受影响平台**：全部

**攻击机制**：Skill 的元数据（名称、描述、版本号）可被攻击者操控，用于 typosquatting（相似名称伪造）和 fake brand impersonation（品牌仿冒）。

**真实案例**：
- ClawHub 上的「Google」「Solana wallet tracker」「YouTube Summarize Pro」「Polymarket Trader」——全部为品牌仿冒，匹配高搜索量关键词

---

### AST05 — Unsafe Deserialization（不安全反序列化）

**严重性**：High | **受影响平台**：全部

**攻击机制**：Skills 依赖 YAML/JSON 反序列化传递配置和脚本引用，攻击者可在这些文件中注入 Payload，利用不安全的反序列化触发代码执行。

**关键缓解**：Safe parsers + sandboxed loading

---

### AST06 — Weak Isolation（弱隔离）

**严重性**：High | **受影响平台**：全部

**攻击机制**：Skills 执行时缺乏强隔离，恶意或半恶意 Skills 可突破容器边界访问宿主机资源。

**真实案例**：
- OpenClaw host-mode 执行 + 135,000+ 公网暴露实例
- Microsoft Defender 安全团队 advisory（2026/02）："Because of these characteristics, OpenClaw should be treated as untrusted code execution with persistent credentials. It is not appropriate to run on a standard personal or enterprise workstation."

**关键缓解**：Containerization + Docker sandboxing

---

### AST07 — Update Drift（更新漂移）

**严重性**：Medium | **受影响平台**：全部

**攻击机制**：已安装的 Skills 在作者发布更新后自动接收更新，但缺乏 hash 验证机制——攻击者可推送恶意更新版本，覆盖原本审查通过的版本。

**真实案例**：
- ClawJacked（CVE-2026-28363，CVSS 9.9）：恶意网站可暴力破解 localhost WebSocket 连接（无 rate limiting），静默劫持本地 OpenClaw 实例、注册新设备、穿过已有集成的数据防线

**关键缓解**：Immutable pinning + hash verification

---

### AST08 — Poor Scanning（劣质扫描）

**严重性**：Medium | **受影响平台**：全部

**攻击机制**：现有的 Skill 安全扫描工具依赖模式匹配（pattern matching），无法检测利用自然语言指令操控的威胁——这类攻击不包含任何代码特征。

> "Why Your Skill Scanner Is Just False Security (and Maybe Malware)" — Snyk（2026/02）：演示 pattern-matcher 如何被自然语言指令注入绕过

**正确方法**：语义分析 + 行为分析的多工具 Pipeline，而非单纯代码签名匹配

---

### AST09 — No Governance（无治理）

**严重性**：Medium | **受影响平台**：全部

**攻击机制**：企业缺乏 Skills 清单（inventory）和 Agent 身份控制机制，导致影子 AI Agent 部署蔓延，安全团队毫无感知。

**真实案例**：
- 53,000+ OpenClaw 实例关联至先前入侵活动，企业 SOC 无可见性
- 员工在企业设备上部署 OpenClaw 且无任何安全扫描

---

### AST10 — Cross-Platform Reuse（跨平台复用）

**严重性**：Medium | **受影响平台**：全部

**攻击机制**：恶意 Skills 可低成本移植到不同平台的 Skills 注册表——ClawHub、skills.sh 等——复用同一套攻击手法。

**关键缓解**：Universal YAML format + cross-registry scanning

---

## 三、平台对照：Skills 格式与风险文件

| 平台 | Skill 格式 | 主要风险文件 |
|------|-----------|------------|
| OpenClaw | SKILL.md（YAML frontmatter + Markdown）| SKILL.md、SOUL.md、MEMORY.md |
| Claude Code | skill.json / YAML + scripts/ | .claude/settings.json、hooks config |
| Cursor / Codex | manifest.json + handler scripts | manifest.json、tool configs |
| VS Code | package.json + extensions | package.json、extension.ts |

---

## 四、与现有 OWASP 标准的关系

| 标准 | 覆盖范围 | 与 AST10 的关系 |
|------|---------|----------------|
| OWASP LLM Top 10 | LLM 本身的安全风险（Prompt injection、数据泄露）| AST10 是互补而非覆盖——Skills 层可绕过 LLM 对齐机制 |
| OWASP Top 10 for Agentic Applications 2026 | Agent 系统的整体风险 | AST10 聚焦 Skills 行为层，是后者的细粒度深化 |
| MCP 安全研究 | MCP 协议层 | MCP = 如何通信，AST10 = 如何行动——分层互补 |

> "Mental Model: MCP = how the model talks to tools; AST10 = what those tools actually do."

---

## 五、工程实践建议：Skills 安全检查清单

### 部署前（Pre-deployment）

| 检查项 | 标准 |
|--------|------|
| Skill 签名验证 | 强制要求 ed25519 签名，拒绝无签名安装 |
| 权限最小化验证 | 检查 Skill 申请的权限是否与其功能声明匹配 |
| 行为沙箱测试 | 在隔离环境中运行 Skill，观察其实际行为（网络请求、文件系统访问）|
| 元数据完整性 | 验证 publisher 身份、install count、scan status |
| 依赖反序列化安全 | 使用安全的 YAML/JSON 解析器，禁止 unsafe loading |

### 运行时（Runtime）

| 检查项 | 标准 |
|--------|------|
| 隔离执行 | Docker 容器化执行，禁止 host-mode |
| 网络出口控制 | Skills 只允许访问其功能声明范围内的端点 |
| 凭据隔离 | Skills 不可访问超出其需求的 API keys 或 secrets |
| 更新验证 | 已安装 Skills hash-pinned，任何修改触发告警 |
| 监控与告警 | 监控 Skills 的异常行为模式（异常网络流量、敏感文件访问）|

### 治理层面（Governance）

| 检查项 | 标准 |
|--------|------|
| Skills 清单 | 企业维护所有已部署 Skills 的完整清单 |
| 注册表扫描 | 在发布时和安装时均进行行为扫描（不仅是 pattern matching）|
| 信任等级制度 | 按 publisher 信誉分配不同的自动执行权限 |
| 应急响应预案 | 预设 Skills 相关安全事件的响应流程 |

---

## 六、判断框架：什么时候该担心 Skills 安全

| 场景 | Skills 安全风险等级 | 说明 |
|------|-------------------|------|
| 个人开发桌面使用 | 中等 | 本地数据为主，隔离有限但攻击面小 |
| 团队共享开发环境 | 高 | 多 Skills 来源，凭据共享，协作风险上升 |
| 企业生产部署 | 极高 | Lethal Trifecta 全中：私密数据 + 不可信内容 + 外部通信 |
| 多租户 SaaS | 极高 | 恶意 Skills 可横向移动影响其他租户 |

> 笔者的工程判断：2026 年任何将 AI Agent 接入生产系统的企业，都必须将 Skills 安全纳入安全评审流程。没有 SKILL.md 的安全审计流程，就相当于没有供应链安全审计就上线 npm 私有化部署。

---

## 七、关键引用

> "The AI agent skill ecosystem is under active attack as of Q1 2026. This is not a theoretical future risk."
> — [OWASP AST10](https://owasp.org/www-project-agentic-skills-top-10/)

> "Skills define not just what resources agents can access, but how they orchestrate multi-step workflows autonomously."
> — [OWASP AST10](https://owasp.org/www-project-agentic-skills-top-10/)

> "Because of these characteristics, OpenClaw should be treated as untrusted code execution with persistent credentials. It is not appropriate to run on a standard personal or enterprise workstation."
> — Microsoft Defender Security Research Team（2026/02）

---

## 关联文章

- [Agent Skills 全面综述：架构、获取、安全与演进路径](./agent-skills-survey-architecture-acquisition-security.md) — Skills 基础架构与演进（上篇）
- [Anthropic Agent Skills 渐进式披露架构](../tool-use/anthropic-agent-skills-progressive-disclosure-architecture-2026.md) — SKILL.md 三层渐进式披露实现细节
- [Cursor 动态上下文发现：文件作为上下文原语](../harness/cursor-dynamic-context-discovery-file-as-context-primitive-2026.md) — 文件作为 Skill/Context 的最小抽象单元
- [OWASP Top 10 for Agentic Applications 2026](./owasp-top-10-agentic-applications-2026.md) — Agent 系统整体安全风险
