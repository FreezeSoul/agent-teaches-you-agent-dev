# OpenAI Codex Windows 沙箱架构：从无特权到提权的工程演进

## 核心主张

OpenAI 在 Codex Windows 沙箱的实现上经历了一次重要的架构迭代：初期用 SIDs + write-restricted tokens 构建「无提权沙箱」，解决了非管理员用户的环境约束问题；但随着需求深化，这套方案在网络隔离和 git 写保护上暴露了根本性缺陷，最终不得不走向「提权沙箱」路线。这段演进揭示了一个关键工程教训：**当安全机制依赖系统薄弱的原生原语时，渐进式修补会累积出比直接设计更高代价的复杂度**。

---

## 问题背景：Windows 欠缺的沙箱原语

Codex 运行在用户开发者笔记本上，默认持有用户身份的全部权限。沙箱的目标是：允许读几乎所有文件、只允许写工作区目录、禁止网络访问——在用户不干预的情况下自动约束。

Linux 有 seccomp、macOS 有 Seatbelt，都是 OS 级别的进程约束机制。Windows 呢？

> "Windows doesn't currently provide this type of capability out of the box."
> — [Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)

OpenAI 评估了三条现有路径，逐一放弃：

| 方案 | 优势 | 致命缺陷 |
|------|------|---------|
| **AppContainer** | OS 级真隔离 | 面向「需求固定的单应用」，Codex 是开放性开发者工作流，需求无法预先界定 |
| **Windows Sandbox** | 强 VM 边界 | 隔离在独立 VM 内，无法操作用户真实 checkout；Windows Home SKU 不可用 |
| **MIC (Mandatory Integrity Control)** | OS 级机制 | 将 workspace 标记为 low integrity 会让整个主机上所有 low-integrity 进程都能写，语义变更无法收回 |

这三条路都走不通，核心原因是：**Windows 的安全原语是面向静态权限分配的，而 Codex 需要动态的、基于上下文的权限边界**。

---

## 第一阶段：Unelevated Sandbox（无提权方案）

### 核心设计：Synthetic SIDs + Write-Restricted Tokens

既然没有 OS 级进程约束，OpenAI 在 ACL 层面构建了等效约束。核心两个原语：

**Synthetic SID（合成安全标识符）**

Windows 的 SID（Security Identifier）是权限系统的原子单位。每个用户、组、会话都有一个 SID，但 Windows 也允许创建不对应真实用户的「合成 SID」，可用于 ACL 但不影响其他系统组件。

OpenAI 创建了一个专用合成 SID：`sandbox-write`，专门用于沙箱写权限控制。

**Write-Restricted Token（写受限令牌）**

Windows 进程令牌中的 Restricted SID list 与正常访问检查双重验证：一次基于 owner，一次基于 restricted SID list。只有当两个检查都通过时，写操作才被允许。

```
写入检查通过条件：
1. token owner 有写权限
2. token 的 restricted SID list 中至少有一个 SID 被授予写权限
```

这意味着：即使当前用户是管理员，只要 restricted SID list 包含 `sandbox-write` 而 workspace ACL 又恰好只给 `sandbox-write` 写权限，写入就会被阻止。

### Unelevated Sandbox 的工作流程

```
初始设置：
├─ 创建合成 SID：sandbox-write
├─ 授予 sandbox-write 对以下路径的写/执行/删除权限：
│   ├─ 当前工作目录
│   └─ config.toml 中配置的额外可写根目录
├─ 对只读区域显式拒绝 sandbox-write：
│   ├─ /.git
│   ├─ /.codex
│   └─ /.agents
└─ 为 Codex 子进程创建 write-restricted token
    └─ restricted SID list = [Everyone, 当前会话 SID, sandbox-write]

运行时：
Codex 执行命令 → 在 write-restricted token 下运行 → 写操作触发双重检查
```

这套机制在文件写入控制上有效：**对工作区的写被允许，对 `/.git` 等敏感区域的写被阻止**。

### Unelevated 的根本缺陷：网络隔离

但文件写入控制只是沙箱的一半。另一半是网络隔离——防止恶意代码外传数据。

问题在于：**Windows Firewall 需要管理员权限才能配置**，而 OpenAI 的硬约束是「不能要求用户提权」。

OpenAI 的应对方案是「fail-closed」——让常见开发工具的网络请求在沙箱内默认失败，而不是依赖 OS 级阻断：

> "We tried to make the child environment fail-closed for the kinds of networked tools developers actually use, so that Git commands, package installers, etc., would fail in the sandbox and the user would have to approve any internet-facing operations."
> — [Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)

具体做法：设置死路由、污染 Git HTTP(S) 传输层。这个方案是**尽力而为**的，因为：

- 它依赖每个网络工具显式尊重系统代理设置
- 恶意代码可以通过自定义 DNS / 非常见端口绕过
- 无法防御 TCP/UDP 直接连接

这不是真正的网络隔离，只是「普通开发场景下的大部分情况有效」。

---

## 第二阶段：向 Elevated Sandbox 的演进

Unelevated 方案的文件写入控制是严密的，但网络隔离是软肋。OpenAI 在 2026 年 5 月 13 日的文章中实际上透露了完整的沙箱设计思路，其中「managed configuration + constrained execution + network policies + telemetry」是完整的四层安全体系。

这意味着**无提权沙箱只是过渡方案**，真正的生产部署需要某种形式的提权：

> "Our managed network policy allows expected destinations, blocks destinations we do not want Codex reaching, and requires approval for unfamiliar domains."
> — [Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)

managed network policy 的实现很可能是借助 Windows 防火墙规则或其他需要管理员权限的机制。

---

## 为什么这个演进值得记录

### 教训 1：平台安全原语决定架构上限

Codex 的 Windows 沙箱问题，本质是「在缺乏 OS 级进程约束原语的平台上构建进程约束」的工程挑战。当平台不提供你需要的安全能力，你面临两个选择：

1. **用应用层原语模拟**（unelevated sandbox）→ 复杂度高、覆盖窄
2. **要求环境具备能力**（elevated sandbox）→ 门槛高、覆盖全

OpenAI 最终走了第二条路。这不是失败，而是对平台局限的诚实承认。

### 教训 2：「无提权」是产品约束，不是安全约束

「不要求用户提权」是 Codex 的 UX 设计决策，而非安全架构的必然。把这两件事分开很有必要：可以在启动时请求一次性提权（设置防火墙规则），之后用户仍以普通权限运行，但沙箱边界由 OS 强制执行。

### 教训 3：复合攻击面需要系统性方案

单纯的文件写入控制 + 尽力而为的网络隔离，在面对真实攻击者时存在攻击链：

```
文件写入控制 → 写入恶意脚本到 startup 目录
尽力而为网络隔离 → 脚本通过非常见协议外传数据
```

OpenAI 的最终方案（见 `running-codex-safely`）采用了多层防御：Auto-review 子代理 + Managed Configuration + OpenTelemetry 审计。这比单纯依赖沙箱边界更符合真实生产环境的需求。

---

## 架构对比：Unelevated vs Elevated

| 维度 | Unelevated Sandbox | Elevated Sandbox |
|------|-------------------|------------------|
| **提权需求** | 无（用户无需 admin）| 一次性设置时需要 admin |
| **文件写入控制** | 强（ACL + write-restricted token）| 强（OS 级别进程约束）|
| **网络隔离** | 尽力而为（fail-close 污染）| 强制（Windows Firewall）|
| **Git 写保护** | ACL 显式拒绝 `sandbox-write` | OS 进程级只读挂载 |
| **兼容性** | Windows Home SKU 可用 | 需要 Pro/Enterprise |
| **安全等级** | 中（应用层模拟）| 高（OS 原语强制）|

---

## 工程实践建议

**如果你在类似 Windows 平台上构建 Agent 沙箱：**

1. **先评估平台安全原语**：确认 OS 是否提供进程级约束（seccomp/Lockdown Mode/AppArmor 等），再决定是用应用层模拟还是要求环境能力
2. **把 UX 约束和安全约束分开设计**：无提权是 UX 选择，不是安全边界；可以要求一次性提权建立沙箱，之后普通权限运行
3. **网络隔离不能靠污染**：fail-close 是尽力而为，真实网络隔离需要 OS 级防火墙规则
4. **记录架构决策的演进**：OpenAI 从 unelevated 到 elevated 的演进不是失败，而是对平台约束认识深化的结果——这个过程本身是工程方法的体现

---

## 引用

> "Windows doesn't currently provide this type of capability out of the box. To make Codex just as safe and delightful to use on Windows as it already is everywhere else, we needed to implement our own sandbox."
> — [Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)

> "We tried to make the child environment fail-closed for the kinds of networked tools developers actually use, so that Git commands, package installers, etc., would fail in the sandbox and the user would have to approve any internet-facing operations."
> — [Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)

> "As coding agents like Codex become integrated into development workflows, security teams need tools specifically designed for managing this shift."
> — [Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)