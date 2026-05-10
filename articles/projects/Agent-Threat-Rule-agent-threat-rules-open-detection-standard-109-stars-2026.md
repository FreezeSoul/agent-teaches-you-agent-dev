# Agent-Threat-Rule/agent-threat-rules — AI Agent 安全检测标准的社区实践

> **Target**：有安全意识的 Agent 开发团队，需要对 Agent 系统做 threat detection 的安全工程师，以及关注 AI Agent 生态标准化进展的架构师。
> 
> **Result**：一套开放检测标准，311 条规则覆盖 9 大威胁类别，映射 OWASP Agentic Top 10（10/10）和 SAFE-MCP（91.8%），在 96,096 个真实 Skills 中发现 751 个 malware samples。
> 
> **Insight**：Agent 安全检测不是造一个私有的闭环工具，而是建一个社区驱动的开放标准——像 Sigma/YARA 之于 SIEM，让规则能被复用、转换、跨平台消费。
> 
> **Proof**：已获得 Microsoft Agent Governance Toolkit（PR #908）和 Cisco AI Defense（PR #79）官方集成，NVIDIA Garak benchmark 97.1% recall，6 周内 7 个生态整合。

---

## Positioning（定位破题）

**一句话定义**：Agent 威胁检测规则的开源标准库——像防病毒的特征码，但对象是 AI Agent 的 prompt injection、tool poisoning、skill compromise 等攻击面。

**场景锚定**：当你需要回答「这个 SKILL.md 安不安全」「这个 MCP 配置有没有被污染」「我的 Agent 有没有接触到恶意的 tool response」时，ATR 是第一层检查。

**差异化标签**：社区驱动（而非厂商锁定）+ 多格式导出（可集成到任意安全平台）+ 真实世界扫描数据（而非合成测试集）。

---

## Sensation（体验式介绍）

想象你写了一个新的 Agent Skill，上线前想做个安全检查。传统流程是手动 review 或等出了问题再修。

ATR 给你的是一个 one-liner：

```bash
atr scan skill.md
```

几毫秒后你得到：

```
[HIGH] prompt-injection/encoded-payloads: base64-encoded reverse shell detected
[MID] skill-compromise/typosquatting: skill name "claude-code" vs legitimate "Claude Code"
[INFO] context-exfiltration/api-key-gen: potential credential generation pattern
```

不只是报问题，还告诉你它对应哪个 OWASP Agentic Top 10 类别、CVE 编号、严重程度。

**哇时刻**：它不只是检测已知攻击——它还做了 96,096 个真实 Skills 的全网扫描，发现了至少 3 个 coordinated threat actors 在 OpenClaw 上批量发布被污染的 Skills（伪装成 Solana wallets、Google Workspace tools、image generators），其中一个直接嵌入了指向 C2 IP `91.92.242.30` 的 base64 reverse shell。

这个发现本身就是一个独立的安全报告：[OpenClaw Malware Campaign](docs/research/openclaw-malware-campaign-2026-04.md)。

---

## Evidence（拆解验证）

### 技术深度

ATR 的检测引擎分两层：

**第一层：Regex 快速门禁（< 5ms，$0 成本）**
- 覆盖已知攻击模式：encoded payloads、persona hijacking、DAN family attacks、context poisoning 等
- 311 条规则，1,600+ regex patterns
- 62-70% 的攻击能被这一层拦截

**第二层：LLM-as-judge 精细检测**
- 覆盖 paraphrase 过的攻击（regex 无法覆盖的部分）
- 需要 LLM 调用，成本高但准确率更高

> 官方数据：
> "ATR regex catches ~62-70% of attacks instantly (< 5ms, $0). The remaining ~30% are paraphrased/persona attacks that need LLM-layer detection. This is by design -- regex is the fast first gate, not the only gate."
> — [Agent-Threat-Rule/agent-threat-rules README](https://github.com/Agent-Threat-Rule/agent-threat-rules)

这是非常诚实的工程判断——不吹嘘单一方案能解决所有问题，而是明确给出了能力边界和互补关系。

### 规则分类（9 大类别）

| 类别 | 检测内容 | 规则数 | 真实 CVE |
|------|---------|-------|---------|
| **Prompt Injection** | 指令劫持、编码载荷、日志注入 | 108 | CVE-2025-53773, CVE-2025-32711 |
| **Agent Manipulation** | DAN family、AutoDAN、cross-agent attacks | 99 | — |
| **Skill Compromise** | Typosquatting、supply chain、rug pull | 37 | CVE-2025-59536, CVE-2026-28363 |
| **Context Exfiltration** | API key 泄露、env exfil、XSS | 26 | CVE-2026-24307 |
| **Tool Poisoning** | 恶意 MCP responses、schema contradictions | 16 | CVE-2025-68143/68144/68145 |
| **Privilege Escalation** | Scope creep、shell escape | 9 | CVE-2026-0628 |
| **Model Abuse** | Malware code generation、AV-evasion | 8 | — |
| **Excessive Autonomy** | Runaway loops、unauthorized 金融操作 | 5 | — |
| **Data Poisoning** | RAG/知识库 tampering | 1 | — |

### 基准测试数据

| Benchmark | Source | Samples | Precision | Recall |
|-----------|--------|---------|-----------|--------|
| **NVIDIA Garak（真实 jailbreaks）** | NVIDIA | 666 | 100% | **97.1%** |
| **SKILL.md benchmark** | 498 labeled samples | 498 | **97%** | **100%** |
| **PINT adversarial** | Invariant Labs | 850 | 99.6% | 62.7% |
| **Wild scan** | 96,096 real-world skills | 96,096 | — | 1.35% flag rate |

> 官方数据：
> "We scanned every major AI agent skill registry. We found 751 skills actively distributing malware."
> — [Agent-Threat-Rule/agent-threat-rules README](https://github.com/Agent-Threat-Rule/agent-threat-rules)

### 生态整合速度

**6 周内 7 个整合**，包括：
- Microsoft Agent Governance Toolkit（PR #908）
- Cisco AI Defense skill-scanner（PR #79）
- OWASP Agentic AI Top 10（PR #14）
- 等待中的 major 框架：NVIDIA Garak #1676、SAFE-MCP #187、OWASP LLM Top 10 #814、IBM mcp-context-forge #4109、Meta PurpleLlama #206、Promptfoo #8529

这是标准的被生态采纳的速度，不是产品被采纳的速度——说明这个项目是冲着「成为标准」去的，不是做一个封闭工具。

---

## Threshold（行动引导）

### 快速上手

```bash
# Install
npm install -g agent-threat-rules   # or: pip install pyatr

# Scan a SKILL.md
atr scan skill.md

# Scan + output SARIF for GitHub Security tab
atr scan skill.md --sarif

# Convert rules for your SIEM
atr convert splunk
atr convert elastic
```

### 集成方式

| 集成方式 | 场景 |
|---------|------|
| **CLI** | 本地开发检查 |
| **GitHub Action** | CI/CD 自动化扫描 |
| **MCP server** | IDE 集成实时检测 |
| **SARIF output** | GitHub Security tab |
| **RegEx export** | 导入任意安全平台 |

### 贡献入口

ATR 是社区驱动的开放标准，MIT licensed，没有 vendor lock-in。如果你发现了一个新的 Agent 攻击模式，可以提交 PR 添加规则——规则本身是 YAML 格式，门槛不高。

---

## 主题关联：Article → Project 的闭环

**Article**（Anthropic Trustworthy Agents）建立了四层安全架构（Model/Harness/Tools/Environment）和五项信任原则（human control/alignment/security/transparency/privacy），明确指出：

> "The more open an agent's environment, the more entry points exist. The more tools it can use, the more an attacker can do once they gain access. This is why we build defenses at several different layers."
> — Anthropic Research: Trustworthy Agents in Practice

**Project**（ATR）则将「安全检测」这个具体能力落地为可执行的社区标准——311 条规则覆盖 OWASP Agentic Top 10 全 10 类，提供快速门禁（Regex）和精细检测（LLM-as-judge）的分层架构。

两者形成完整闭环：
- **Anthropic**：给框架和原则（做什么）
- **ATR**：给检测标准和工具（怎么做）

Anthropic 在文档中说「安全和可靠的 Agent 不能由任何一家公司单独实现」——ATR 正是这种开放生态思维的工程实现。

---

## 防重索引

本项目尚未在 `articles/projects/` 中推荐过。