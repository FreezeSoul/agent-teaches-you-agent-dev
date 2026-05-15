# OpenAI Codex Windows 沙箱架构：从 ACL 妥协到独立用户特权级

## 这篇文章要回答的问题

Codex 在 Windows 上如何实现沙箱隔离——当平台本身不提供可靠的进程级沙箱原语时，工程团队如何通过组合 Windows 现有机制（ACL、SID、write-restricted token、CreateProcessAsUserW）构建一个有效的安全边界。

---

## 背景：为什么 Windows 沙箱是个特殊难题

Codex 的核心威胁模型是**本地代码执行权限**：Agent 运行在用户态，拥有该用户的所有权限——读写文件系统、运行任意命令、访问网络。这在 macOS 和 Linux 上有成熟的原生方案：

- **macOS**：Seatbelt（内核级强制沙箱配置文件 `.sbpl`）
- **Linux**：seccomp-bpf / bubblewrap（Namespace 和 Cgroups 隔离）

但 **Windows 没有内置的等效原语**。Windows 的隔离工具都是为其他场景设计的：

| 方案 | 设计目标 | 为什么不适合 Codex |
|------|---------|-------------------|
| **AppContainer** | 能力模型，单一用途 app | Codex 是开放式的开发者工作流——Shell、Git、Python、Build 工具——无法预先声明所需权限范围 |
| **Windows Sandbox** | Disposable VM | 需要在独立的 Guest 桌面上操作，无法直接触及用户真实的工作目录和工具链；且 Home SKU 不可用 |
| **Mandatory Integrity Control (MIC)** | 进程完整性级别（Low/Medium/High） | 将工作区标记为 Low Integrity 会让整台机器上所有 Low Integrity 进程都能写入，语义改变过于宽泛 |

这意味着 Codex 团队必须**自己构建沙箱层**，在「不需要管理员权限」和「提供真正的安全边界」之间反复权衡。

---

## 第一次尝试：Unelevated Sandbox（无提权方案）

### 核心思路

依赖 Windows 的两个已有机制：

1. **Synthetic SID**（合成安全标识符）：创建一个人工 SID（如 `sandbox-write`），不在系统中对应真实用户，但可以加入 ACL
2. **Write-restricted token**：进程 token 包含受限 SID 列表，写操作必须同时满足「主身份可写」**且**「至少一个受限 SID 可写」

### 文件系统限制实现

```
sandbox-write SID 被授予以下路径的写/执行/删除权限：
  - 当前工作目录
  - config.toml 中配置的 writable_roots

sandbox-write SID 被明确拒绝访问：
  - /.git
  - /.codex
  - /.agents
```

这个设计的优雅之处在于：**ACL 针对的是合成 SID，而非真实用户**——所有修改都在一个专门创建的虚拟身份上完成，不影响机器上其他进程的权限语义。

### 网络限制的失败

macOS/Linux 可以通过内核级规则（seccomp/bubblewrap）阻断所有网络访问。Windows 上没有等效工具——Windows Firewall 需要管理员权限才能创建程序级规则，而且：

> 防火墙规则无法匹配 restricted token 的 principal。这意味着你无法创建一条规则说「所有包含特定 SID 的受限进程树都不能联网」。

他们的 workaround 是**环境变量投毒**：

```bash
HTTPS_PROXY=http://127.0.0.1:9    # 让 HTTPS 请求指向一个死地址
ALL_PROXY=http://127.0.0.1:9
GIT_HTTPS_PROXY=http://127.0.0.1:9
GIT_SSH_COMMAND=cmd /c exit 1    # 让 SSH Git 直接失败
```

这是一个**顾问式**（advisory）的网络隔离——守规矩的进程会遵守环境变量，但任何直接实现 socket 通信的代码都可以轻易绕过。这个缺陷是最终放弃无提权方案的根本原因。

### 其他缺陷

- **Setup 速度慢**：对大型工作区目录拓扑应用 ACL 是 O(n) 操作
- **语义难以变更**：一旦用 ACL 定义了文件限制，修改边界需要重新遍历和修改 ACL
- **Trace 占用**：真实 ACL 被修改（虽然是针对合成 SID）

---

## 重新设计：Elevated Sandbox（提权方案）

放弃「零管理员权限」约束，转向**有管理的提权**：setup 需要一次性的管理员权限来创建独立用户和防火墙规则，但 codex.exe 本身仍然以普通用户身份运行。

### 核心架构变更

新增两个组件：

1. **`codex-windows-sandbox-setup.exe`**：处理所有提权操作的独立二进制
2. **`codex-command-runner.exe`**：以沙箱用户身份运行，负责 mint restricted token 并 spawn 子进程

新增两个本地用户：

- **`CodexSandboxOffline`**：被防火墙规则阻止所有出站网络连接——这是默认使用的沙箱身份
- **`CodexSandboxOnline`**：不受防火墙限制——需要网络访问时使用

### CreateProcessAsUserW 的特权墙

Windows 的 `CreateProcessAsUserW()` 有**特权墙**——非 SYSTEM 进程无法从一个用户 session 跨越到另一个用户 session 创建进程。这意味着：

```
codex.exe（以真实用户身份运行）
  → 无法直接调用 CreateProcessAsUserW() 来以 CodexSandbox* 用户身份创建进程
```

解决方案是 **双进程接力**：

```
Part 1: codex.exe（真实用户侧）
  → CreateProcessWithLogonW() 启动 codex-command-runner.exe，
    身份切换到沙箱用户（但此时还不是 restricted token）

Part 2: codex-command-runner.exe（沙箱用户侧）
  → OpenProcessToken(GetCurrentProcess()) 获取自己的 full token
  → GetTokenInformation() 提取 logon SID
  → CreateRestrictedToken() 创建最终的 restricted token
  → CreateProcessAsUserW() 用 restricted token 启动真正的 child
```

这个分拆解决的本质问题：**受限 token 的 mint 操作必须在目标用户侧完成**。如果尝试在真实用户侧 mint 一个沙箱用户的 restricted token，Windows 会拒绝。

### 读权限的补偿

当 principal 变成沙箱用户后，很多 Windows 目录的默认权限会阻止读取——比如用户 profile 目录。setup 阶段会异步地给沙箱用户授予这些目录的读 ACL：

```
C:\Users\<username>\
C:\Windows\
C:\Program Files\
C:\Program Files (x86)\
C:\ProgramData\
```

异步执行是因为某些目录的 ACL 变更非常耗时（比如 node_modules），不能让它阻塞用户的沙箱初始化流程。

### 最终四层架构

```
codex.exe                      ← 主 harness，仍以普通用户身份运行
  │
  ├── codex-windows-sandbox-setup.exe  ← 一次性提权 setup
  │     • 创建 CodexSandbox* 用户
  │     • 配置 DPAPI 加密的凭证存储
  │     • 创建 Windows Firewall 规则（阻断 CodexSandboxOffline 的所有出站连接）
  │     • 授予沙箱用户必要目录的读 ACL
  │
  └── codex-command-runner.exe ← 以沙箱用户身份运行，负责受限进程创建
        • Mint restricted token（含 write-restricted + 网络限制）
        • CreateProcessAsUserW() 启动 child
              │
              ▼
        child process           ← 真实工作负载，运行在受限 token 下
```

---

## 为什么这个架构值得深入理解

### 平台原语缺失下的安全工程

这是 Harness 设计的经典难题：**当你依赖的平台没有你需要的原语时，你如何组合现有机制达到近似效果？** Codex 团队的选择是：

1. 接受一次性的提权 setup（创建独立用户 + 防火墙规则）
2. 但 codex.exe 本身保持非特权，用受限 token 运行子进程
3. 通过双进程接力解决跨用户边界的进程创建问题

这是一种**深度防御**思路：即使某个 layer 被突破，其他 layer 仍然有效。

### 网络隔离的工程权衡

从「环境变量投毒」到「独立用户 + 防火墙」的演进，说明了一个重要原则：**不要依赖可以被轻易绕过的安全控制**。环境变量可以设置代理，但任何实现自定义网络栈的程序都能直接忽略它们。只有内核级强制（Windows Firewall）和进程级强制（独立用户 principal）的组合才是真正有效的边界。

### Token 设计的精妙之处

Write-restricted token 的双重检查机制（`主身份检查 + 受限 SID 检查`）是一个非常优雅的设计——它允许你保留主身份的完整读权限，同时通过受限 SID 列表精确控制写权限边界。这个设计值得在任何需要「读全量 + 写受限」场景中借鉴。

---

## 工程启示

1. **平台能力决定架构上限**：macOS 有 Seatbelt，Linux 有 seccomp/bubblewrap，Windows 什么都没有——这是选择沙箱方案时必须正视的客观约束
2. **安全控制必须强制而非顾问**：任何可以被应用程序绕过的安全机制都不是真正的安全边界
3. **一次性提权 + 运行时非特权**是一个实用的安全架构模式：setup 时完成权限配置，运行时以最小权限运行
4. **跨用户边界的进程创建**是 Windows 特有的难题，需要类似 codex-command-runner 的双进程接力模式

---

## 引用

> "Codex runs with the permissions of a real user by default, meaning it can do everything the user can do. This is powerful and potentially dangerous."
> — [Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)

> "A write-restricted token is a particular type of process token that makes Windows perform an additional access check on write operations. In order for a write to succeed, two checks must pass: the normal user identity must be allowed to do it, AND at least one SID in the token's restricted SID list must also be granted access."
> — 同上

> "Because of how Windows user and token login boundaries work, we couldn't continue to create a restricted token and spawn a process under it the way we could with the unelevated sandbox. We needed a process that was already running as the sandbox user."
> — 同上

---

*标签：harness、sandbox、windows、security、architecture*
*来源：[OpenAI Engineering - Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/)*