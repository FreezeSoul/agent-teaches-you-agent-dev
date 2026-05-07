# Clampdown：零信任沙箱，让 AI 编码 Agent 无法伤害你的主机

> 官方原文引用：
> - [89luca89/clampdown: Run AI coding agents in hardened container sandboxes](https://github.com/89luca89/clampdown)
> - clampdown README (architecture, threat model, security design)

---

## 目标用户

**T - Target（谁该关注）**

正在将 AI 编码 Agent（CURSOR Claude Code、OpenAI Codex、Copilot 等）投入生产的工程师或安全负责人。

典型画像：你在自己的机器上跑 Agent，发现它开始执行 `rm -rf /` 或尝试连接内网数据库；或者你在公司要求 Agent 访问真实 GitHub org 和云凭证，但安全团队不让步。

如果你是个人开发者且只在沙箱里玩，Clampdown 可能过度；但如果 Agent 需要访问真实项目 + 真实凭证，Clampdown 是目前最强的开源防护层。

---

## 核心结论

**R - Result（能带来什么）**

Clampdown 将 AI 编码 Agent 封闭在一个四层容器隔离架构中，让 Agent 无论是被 prompt injection 劫持、被 jailbreak 还是诚实地执行你给的任务，都无法突破主机边界。

具体能力边界：
- 文件系统：只能读写工作目录，`/proc/kcore`、`~/.ssh`、其他项目目录全部从内核层（Landlock）屏蔽
- 网络：Agent 只能访问白名单域名，内网 IP（192.168.x.x 等）永远不通；工具容器可以访问公网但无法连接内网
- 权限：`cap-drop=ALL`，Agent 进程是零特权进程，无法创建 namespace、加载 kernel module、挂载文件系统
- API 密钥：真实密钥永远在 auth proxy 容器里，Agent 只拿到一个 `sk-proxy` 假令牌，直接连接上游 API 会得到 401

---

## 技术洞察

**I - Insight（凭什么做到）**

Clampdown 的设计核心不是「如何让 Agent 更安全」，而是「假设 Agent 已经完全被攻陷，如何让损害局限在容器内」。这是零信任安全模型在容器级别的实现——不信任任何 Agent 进程，无论它表现得多正常。

关键设计决策：

### 1. 四种容器，四种信任级别

| 容器 | 角色 | 权限 | 密钥 |
|------|------|------|------|
| **Sidecar** | 容器运行时 + 防火墙 | 16 个 capability（SYS_ADMIN、NET_ADMIN）| Registry 凭证（可选）|
| **Auth Proxy** | API 密钥保管 | `cap-drop=ALL`，`FROM scratch` | 真实 API 密钥 |
| **Agent** | AI 模型进程 | `cap-drop=ALL` | `sk-proxy` 假密钥 |
| **Tool（嵌套）** | Agent 派生的工具进程 | 10 个默认 capability | 无 |

关键点：**每种容器的权限精确匹配其最小需求**。Sidecar 需要启动容器和管理防火墙，所以有网络管理权限；但没有 shell 和 libc，无法被改作他用。Auth proxy 持有真实密钥却零权限，无法被用于任何其他目的。

### 2. Landlock：从内核层锁定文件系统

Landlock 是 Linux kernel LSM（5.13+），允许在进程 exec 时绑定一个无法移除的文件系统访问规则集——比 seccomp 更细粒度，且在 exec 后仍然生效（seccomp 在 exec 时会重置）。

Clampdown 对 Agent 的 Landlock 策略：

```
工作目录：读-写-执行
系统目录（/usr、/bin、/lib、/etc）：读-执行
其他所有路径：无权限
```

即使 Agent 用 `chmod 777 /etc/shadow`，Landlock 规则在 exec 后仍然存在，内核会直接拒绝这个操作。**这是内核级别的隔离，不依赖任何用户空间配置，Agent 自身无法绕过。**

> "Landlock policies are inherited across exec and can only be made more restrictive, never relaxed."
> — [Clampdown README: Landlock filesystem isolation](https://github.com/89luca89/clampdown)

### 3. Seccomp + BPF supervisor：20 个关键 syscalls 实时拦截

Landlock 有个限制——它和 `mount()` 系统调用不兼容（Landlock V3 无法在 sidecar 上使用，因为 sidecar 本身需要挂载文件系统）。

Clampdown 用 seccomp-notif BPF 过滤器弥补这个缺口：在 sidecar 进程中实时拦截 20 个关键 syscalls，包括：
- 卸载被 mask 的路径（防止 `.env` 被暴露）
- 从非授权来源创建 bind mount
- 执行不在白名单的二进制文件
- 删除或修改受保护文件
- 修改 iptables 规则

Exec 白名单机制在 sidecar 启动时对 rootfs 中的每个可执行文件做 SHA-256 哈希，之后每次 execve 都会验证哈希，未知二进制直接返回 `EACCES`。

### 4. OCI Hook：每一层容器在启动前就已被审查

Agent 每次执行 `podman run` 创建工具容器时，两个 OCI hooks 同步运行：

**precreate hook（seal-inject）**：
- 重写容器 entrypoint 为 `sandbox-seal`（在 exec 前应用 Landlock）
- 挂载 `hidepid=2` 到 `/proc`（隐藏其他用户的进程）
- 注入被 mask 的路径（`/proc/kcore`、`/proc/sysrq-trigger` 等 9 个敏感接口）

**createRuntime hook（security-policy）**：
- 验证最终 OCI 配置，执行 17 项安全检查
- 阻止：privileged 模式、危险 capability、共享主机 namespace、不安全的 bind mount、可写设备、RW 重挂载受保护路径

**任何一项检查失败，容器在 entrypoint 运行前就被 kill。不存在任何 opt-out。**

> "A container that fails any check is killed before its entrypoint runs. Both hooks apply to every `podman run` the agent issues. There is no opt-out."
> — [Clampdown README: Nested container enforcement](https://github.com/89luca89/clampdown)

### 5. 密钥隔离：Agent 永远接触不到真实令牌

```
Agent（持有 sk-proxy 假密钥）──→ Auth Proxy（持有真实密钥）──→ Upstream API
```

Auth proxy 运行在 `FROM scratch` 容器中：无 shell、无可写文件系统、`cap-drop=ALL`、core dumps 禁用、Landlock 只允许 TCP 443+53。Agent 用假密钥直连上游 API 会得到 401。这个设计意味着：**即使 Agent 完全被控，攻击者拿到的密钥毫无用处。**

---

## 证据与社区

**P - Proof（谁在用、热度如何）**

Clampdown 属于 `89luca89` 维护的开源工具集，该维护者同时维护 distrobox（主机级容器管理工具，在开发者中有良好口碑）。

Clampdown 的架构文档完整，Threat Model 章节明确说明：

> "clampdown treats the agent as an untrusted process. Not because current models are malicious, but because the attack surface is real: prompt injection can hijack an agent's actions, jailbreaks can override its instructions, and even well-behaved models run arbitrary code that may do things you didn't ask for."
> — [Clampdown README: Threat model](https://github.com/89luca89/clampdown)

这个威胁模型定位非常清晰——不是「模型是恶意的」，而是「Agent 的执行环境是不可信的」。与 Anthropic 的 Auto Mode 理念一致：防御来自外部，不依赖 Agent 自身的「合作」。

在 GitHub 上与类似的沙箱项目对比：

| 项目 | 星星数 | 安全机制 | 与 Clampdown 的差异 |
|------|--------|---------|-------------------|
| **Clampdown** | 65+ | Landlock + Seccomp + OCI Hook + 零密钥 | 最细粒度的内核级隔离 |
| **agentbox** | — | Docker 隔离 | 无内核级强制，无密钥隔离 |
| **jailoc** | — | Docker 隔离 | 无 Landlock，无密钥隔离 |

---

## 快速上手

**门槛（Threshold）**

Clampdown 对使用环境有要求：
- Linux kernel 6.2+（Landlock V3）
- 推荐 6.12+（完整功能覆盖）
- 6.15+（审计日志）
- 需要 `podman`

安装流程（3步以内无法完成，因为涉及容器运行时配置）：

```bash
# 1. 安装 clampdown
curl -fsSL https://raw.githubusercontent.com/89luca89/clampdown/main/install.sh | sh

# 2. 配置项目白名单
export CLAMPDOWN_PROJECT="/path/to/your/codebase"

# 3. 配置 API 密钥（通过 clampdown 的 auth proxy）
export OPENAI_API_KEY="sk-..."   # 或 ANTHROPIC_API_KEY 等

# 4. 启动 clampdown（Agent 运行在隔离环境中）
clampdown run --agent cursor --project /path/to/your/codebase
```

真实部署场景建议使用 `--agent-policy` 和 `--pod-policy` 定制网络白名单，限制 Agent 能访问的域名范围。

---

## 与 Anthropic Auto Mode 的技术对照

本仓库上一轮产出的文章「从 Auto Mode 到 Managed Agents：Anthropic 的 Harness 演进路径」分析了 Anthropic 的模型驱动分类器解决 permission fatigue 的思路。

Clampdown 提供了互补的工程实现：**不是用模型判断是否危险，而是在内核层用强制隔离让「危险操作根本不可能执行」**。

| 维度 | Anthropic Auto Mode | Clampdown |
|------|-------------------|-----------|
| **防御层面** | 模型分类器（判断是否授权）| 内核级强制（无论是否授权都不允许）|
| **密钥保护** | 依赖云端托管（Claude Code） | 零信任本地隔离（auth proxy）|
| **威胁覆盖** | Overeager/honest mistake | Prompt injection/jailbreak/任何逃逸企图 |
| **适用场景** | 云端 Agent（Claude Code） | 本地任何 Agent（Cursor/Codex/Copilot）|
| **性能成本** | Stage 1~2 分类器延迟 | Landlock/seccomp syscall 拦截延迟可忽略 |

两者可以互补：Auto Mode 的分类器处理「行为是否在用户意图内」，Clampdown 处理「即使行为在意图内，操作是否在安全边界内」。

---

## 结语

Clampdown 的核心价值不是「让 Agent 更安全」，而是「让 Agent 的危险操作物理上不可能执行」。在当前 AI Agent 安全讨论普遍聚焦于 prompt injection 和模型对齐时，Clampdown 提醒一个被低估的视角：**最强的安全边界是内核级的，无论模型多聪明都绕不过去**。

对于在生产环境跑 AI 编码 Agent 的团队，Clampdown 不是可选项——它是唯一能让你在安全团队面前站得住脚的技术方案。