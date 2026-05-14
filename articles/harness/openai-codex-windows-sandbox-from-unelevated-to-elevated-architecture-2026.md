# OpenAI Codex Windows 沙箱：从无到有的工程演进

> 本文聚焦 OpenAI 2026 年 5 月 13 日发布的工程博客 [Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)，深度解析从「无沙箱」到「unelevated prototype」再到「elevated sandbox」的完整技术路径，以及每个节点的关键设计决策。

---

## 背景：为什么 Windows 沙箱是一个工程难题

Codex 运行在开发者的笔记本电脑上，默认以用户权限执行命令——这意味着它能做任何用户能做的事。在 macOS 和 Linux 上，Codex 可以利用系统原生隔离能力（Seatbelt、seccomp、bubblewrap）实现沙箱，但在 Windows 上，问题变得棘手：

> "Windows doesn't currently provide this type of capability out of the box."
> — [OpenAI Engineering: Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)

Windows 用户面临两个糟糕的选择：
- **Approve 模式**：对每个命令（包括文件读取）都需要人工批准，这使得 Codex 的价值大打折扣
- **Full Access 模式**：完全绕过审批，同时失去了安全防护

Codex 需要在 Windows 上实现与其他平台同等的安全性，同时不能强制要求管理员权限。

---

## 第一阶段：AppContainer、Windows Sandbox、MIC 为什么都不适用

在自研之前，OpenAI 评估了三个 Windows 原生方案：

### AppContainer：强隔离，但形状不对

AppContainer 是 Windows 的原生沙箱模型，基于能力（capability-based）的隔离。但它要求应用预先声明所需的确切资源。

> "Codex is not one tightly scoped app. It drives open-ended developer workflows: shells, Git, Python, package managers, build tools, and whatever other binaries the agent decides it needs."
> — 同上

Codex 的工作流程无法预先界定范围——这是 AppContainer 的设计边界之外的使用形态。

### Windows Sandbox：隔离强，但语义不对

Windows Sandbox 是微软提供的轻量级虚拟机，每次启动都是全新的 Windows 环境，关机后完全消失。

问题在于：Codex 需要直接操作用户的真实代码仓库、工具链和环境，而非一个隔离的「临时桌面」。此外，Windows Sandbox 在 Windows Home SKU 上根本不可用。

### MIC（Mandatory Integrity Control）：语义变更太大

MIC 通过「完整性级别」（Low/Medium/High）来约束进程对对象的写权限。OpenAI 曾设想过让 Codex 以 Low 完整性运行，将 workspace 标记为 Low 可写。

但这个方案的核心问题在于：标记 workspace 为 Low 意味着**所有低完整性进程都能写入该目录**，而不仅仅是 Codex。这是一个系统性的信任模型变更，无法精确控制范围。

---

## 第二阶段：Unelevated Sandbox 原型

在排除所有原生方案后，OpenAI 开始自研。第一个原型要求**零提权**（no elevation），这意味着不能依赖 Windows Firewall 或管理员级工具。

### 核心技术：SIDs + Write-Restricted Tokens

**SID（Security Identifier）** 是 Windows 用来标识身份的安全对象——每个用户、组、甚至登录会话都有一个 SID。Windows 还支持创建**合成 SID**（synthetic SID），不映射到真实用户，但可以出现在 ACL 中。

**Write-Restricted Token** 是一种特殊的进程令牌，写操作需要同时满足两个检查：
1. 令牌 owner（真实用户身份）被允许写
2. 令牌的 restricted SID 列表中至少有一个 SID 被授予写权限

通过结合这两种机制，原型实现了：
- 创建合成 SID `sandbox-write`，授予其对当前工作目录和 `writable_roots` 的写权限
- 显式拒绝 `sandbox-write` 对 `.git`、`.codex`、`.agents` 等只读区域的写权限
- Codex 以包含 `[Everyone, Logon SID, sandbox-write]` 的 write-restricted token 运行

### 网络限制：环境级别的「建议性」防护

由于无法调用 Windows Firewall，原型退而求其次——让子环境中的常见网络工具（HTTPS proxy、GIT_HTTPS_PROXY、Git SSH）指向一个 dead endpoint，使 Git/npm 等工具的请求直接失败。

> "It was still only advisory. A process could ignore the environment, bypass PATH, or just open sockets directly."

这是原型最核心的缺陷：**网络防护是建议性的，无法抵御真正恶意的代码**。

### 原型的问题总结

| 问题 | 严重性 | 描述 |
|------|--------|------|
| ACL 变更成本高 | 中 | 修改 workspace ACL 的开销与目录拓扑相关，大型仓库代价昂贵 |
| 系统语义变更 | 中 | 依赖真实 ACL，即使变更范围有限，仍会修改主机的安全模型 |
| 网络防护薄弱 | **高** | 进程可绕过环境变量，直接打开 socket，无法抵御恶意代码 |

---

## 第三阶段：Elevated Sandbox——以提权换取真正的网络隔离

原型的前三个问题都与「不依赖提权」这一约束相关。当 OpenAI 需要真正阻断网络流量时，发现唯一有效的工具是 Windows Firewall，而这要求**以独立 Windows 用户作为 principal 运行沙箱进程**，而非以真实用户身份运行。

这就是 elevated sandbox 的核心设计转变。

### 架构设计

```
真实 Windows 用户
       │
       ▼
Codex harness 生成两个本地用户：
  ├── CodexSandboxOffline（目标为防火墙规则，适用于需要网络隔离的命令）
  └── CodexSandboxOnline（不受防火墙限制，适用于需要网络的命令）
       │
       ▼
子进程以对应用户的 write-restricted token 运行
       │
       ▼
CodexSandboxOffline 受 Windows Firewall 规则约束—— outbound traffic 被完全阻断
```

在进程层面，elevated sandbox 和 unelevated prototype 看起来类似：都使用 write-restricted token，都包含相同的 restricted SID 列表。**但 principal 的身份发生了根本性变化**——不再是真实用户，而是一个专用的沙箱用户。

### 提权的边界

需要注意：提权仅在**setup 时**需要。日常运行时，Codex 以非管理员身份运行，但以专用沙箱用户的身份执行命令。Setup 时需要管理员权限来创建 `CodexSandboxOffline` 和 `CodexSandboxOnline` 两个本地用户，以及写入 Windows Firewall 规则。

---

## 设计决策的工程权衡

从整个演进路径来看，OpenAI 的选择遵循一个清晰的优先级：

| 阶段 | 核心约束 | 选型 | 代价 |
|------|---------|------|------|
| 评估 | 不依赖提权 | AppContainer/MIC/Windows Sandbox | 均无法满足「开放工作流 + 操作真实文件系统」需求 |
| 原型 | 无提权 + 文件写控制 | SIDs + write-restricted token | 网络防护薄弱、ACL 语义变更 |
| 生产版 | 真正的网络隔离 | 专用 Windows 用户 + Firewall | setup 时需要管理员权限 |

### 从 Agent 工程的角度看

这个案例揭示了一个关键工程原则：**沙箱安全性与系统复杂度之间存在不可避免的权衡**。Unix/macOS 的进程级沙箱机制（seccomp/Seatbelt）所以有效，是因为它们是内核级的一等公民，不需要在用户态做大量修补。Windows 作为面向桌面用户的操作系统，其安全模型更侧重于「用户能信任什么」，而非「进程能隔离什么」。

OpenAI 最终选择接受「setup 需要提权」这一约束，换取「生产运行时真正的网络隔离」——这是一个务实的工程决策，而非技术理想主义。

---

## 延伸：沙箱设计的多平台共性

虽然 Windows 没有原生沙箱工具，但 OpenAI 在这个案例中使用的技术（SIDs、ACL、restricted tokens）揭示了所有沙箱实现都需要回答的核心问题：

1. **文件访问边界**：在哪里画线，哪些路径可写，哪些必须只读
2. **网络访问控制**：如何阻止数据外泄，同时不破坏正常工作流
3. **进程树隔离**：沙箱约束是否向子进程传递
4. **提权边界**：setup 时需要的权限是否与 runtime 安全目标冲突

这些问题在任何平台的沙箱实现中都是共通的，只是各平台提供的原语不同。

---

## 结论

OpenAI 在 Windows 上实现 Codex 沙箱的完整路径（评估 → 原型 → 生产版）是一份高质量的工程案例研究。它展示了一个核心矛盾：**Agent 的能力（能做任何用户能做的事）与安全约束（不能让 Agent 做任何用户能做的事）之间的张力**，在不同平台上以不同的形式出现。

Windows 的案例特别有价值，因为它迫使工程师从平台原生工具箱中走出来，**从第一性原理构建隔离机制**，而这也正是 AI Agent 工程在 2026 年面临的核心挑战——当 Agent 的能力边界扩展到文件系统、网络、多进程协作时，每个操作系统原生的安全模型都需要重新评估。