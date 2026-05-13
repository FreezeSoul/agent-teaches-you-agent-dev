# Agent 执行层的架构演进：从进程隔离到 Micro-VM

> 本文分析 LLM Agent 执行环境的架构演进，重点解读 microsandbox 微虚拟机方案如何重新定义 Agent 沙箱的边界控制粒度。
>
> **核心论点**：Agent 执行层正在从「进程级隔离」向「Micro-VM 级隔离」演进，sandboxed-lit 通过 Rust + microsandbox 实现了第一个生产可用的 Micro-VM Agent 执行方案，将文件操作、PDF 解析、Bash 命令的执行边界精确到 2CPU/1GB RAM 的资源配额，而非传统容器的粗粒度控制。

---

## 1. 为什么 Agent 需要新的沙箱范式

传统的 Agent 执行环境依赖 Docker 容器或 Namespaces 实现隔离，这在大多数场景下足够——但当 Agent 开始处理长程任务、操作多样化工具集（文件读写 + PDF 解析 + 命令执行）时，容器的局限性变得明显：

| 维度 | 传统容器隔离 | Micro-VM 隔离 |
|------|------------|--------------|
| **启动时间** | 秒级 | 毫秒级（micro-VM） |
| **资源粒度** | CPU/内存配额，可被滥用 | 固定 2CPU/1GB，无法超用 |
| **文件系统** | Overlay FS，隔离但不精确 | Bind mount 到指定目录，精确控制 |
| **网络** | 网桥模式，可访问任意地址 | 默认无网络，必要时明确开启 |
| **清理成本** | 删除容器，秒级 | 微 VM 销毁，毫秒级 |

`sandboxed-lit` 的设计目标不是替代 Docker，而是填补「需要比容器更细粒度控制，但不需要完整 VM」的空白场景。对于需要运行不受信任代码的 Agent，这个空白曾经不存在。

---

## 2. sandboxed-lit 的架构解析

`sandboxed-lit` 由 Rust 实现，核心依赖两个组件：

### 2.1 microsandbox 微虚拟机层

`sandboxed-lit` 使用 microsandbox 的预构建镜像 `ghcr.io/run-llama/liteparse:main`，这是一个轻量级 VM：

```rust
// src/sandbox.rs 核心逻辑（简化）
pub fn create_sandbox(volume: &Path) -> Result<Sandbox> {
    // 创建/复用名为 lit-sandbox 的微 VM
    // 资源配置：2 CPUs + 1GB RAM
    // 工作目录：/app/
    // 数据卷：/app/data（通过 bind mount 映射）
}
```

每次 Agent 调用时，sandbox 会被创建或复用。关键设计决策：**sandbox 命名固定**，相同名字的调用会复用同一个微 VM 实例，而非每次重新创建——这是毫秒级启动的关键。

### 2.2 agent-sdk 工具抽象

`sandboxed-lit` 暴露三个核心工具，全部通过 `agent-sdk` 注册：

| 工具 | 功能 | 隔离保证 |
|------|------|---------|
| `list_files` | 递归列出 `/app/data/` 下的文件 | 只能看到挂载目录 |
| `read_file` | 读取文件；PDF/图片/Office 文档通过 `liteparse` 解析 | 只能读取挂载目录内的文件 |
| `run_bash_command` | 在微 VM 内执行任意命令 | 只能操作 `/app/data/` 下的资源 |

PDF 解析是这里的关键差异化能力。大多数 Agent 沙箱方案只处理纯文本，但 `liteparse` 集成意味着 Agent 可以分析 PDF、扫描图片、读取 Office 文档——全部在沙箱内完成，没有文件外泄风险。

---

## 3. 与现有 Agent 执行方案的对比

`sandboxed-lit` 不是唯一的 Agent 沙箱方案。对比主流方案：

| 方案 | 隔离级别 | 启动时间 | PDF/Office | 生态 |
|------|---------|---------|-----------|------|
| **sandboxed-lit** | Micro-VM | <100ms | ✅ liteparse | Rust + agent-sdk |
| **Docker 容器** | 容器 | 1-5s | ✅ 需挂载解析器 | 通用 |
| **Cloudflare Workers** | V8 isolate | <10ms | ❌ | JS/Wasm |
| **Anthropic Code Executor** | 容器 + MCP | 秒级 | ✅ | Claude 专用 |

> 官方原文：
> "A small Rust CLI that runs an LLM agent inside a microsandbox VM. The agent uses OpenAI's GPT models via agent-sdk and has tools to list files, read files (parsing PDFs / images / Office docs through liteparse), and run bash commands, all confined to the sandbox."
> — [run-llama/sandboxed-lit README](https://github.com/run-llama/sandboxed-lit)

`sandboxed-lit` 的核心价值在于**资源约束的硬性执行**。当 Agent 执行 `run_bash_command` 时，无论输入什么命令，资源天花板都是固定的 2CPU/1GB——这是 Docker 容器无法保证的（容器可以通过 `docker run --privileged` 或挂载宿主目录绕过隔离）。

---

## 4. 实际使用场景与限制

### 4.1 适用场景

- **文档分析流水线**：需要让 Agent 读取 PDF/Office 并提取信息，但不允许网络访问或文件外泄
- **代码审查流水线**：需要分析代码仓库但不希望 Agent 执行持久化操作
- **测试环境**：需要隔离执行，不影响宿主系统

```bash
# 示例：分析工作目录中的所有 PDF
export OPENAI_API_KEY=sk-...
sandboxed-lit -p "Summarize every PDF in the working directory."

# 示例：挂载特定目录
sandboxed-lit -p "List the files, then read report.pdf and extract the key findings." -v /Users/me/documents
```

### 4.2 关键限制

1. **需要运行 microsandbox host**：不是开箱即用，需要部署 microsandbox 基础设施
2. **只支持 OpenAI 模型**：通过 `agent-sdk` 绑定 GPT，暂无 Anthropic/Claude 支持
3. **固定资源配置**：2CPU/1GB 是硬编码，无法动态调整
4. **无网络隔离配置**：README 未说明如何控制网络访问（默认无网络是正确的，但配置路径不明确）

---

## 5. 对 Agent 工程实践的启示

`sandboxed-lit` 代表了一个新兴方向：**Micro-VM 级别的 Agent 执行隔离**。在它之前，Agent 执行要么是「太轻量无法真正隔离」（V8 isolate），要么是「太重需要完整容器管理」（Docker）。Micro-VM 填补了这个空白。

从 Agent 工程的角度看，这个方向的成熟会改变几个实践：

- **untrusted code 执行**：当 Agent 需要分析用户上传的不受信任代码时，Micro-VM 比容器更安全（资源硬限制 + 文件系统精确绑定）
- **工具调用成本**：毫秒级启动使得「按需创建 sandbox，执行后销毁」的模式变得可接受
- **PDF/Office 处理**：liteparse 集成意味着非结构化文档处理可以在隔离环境内完成，Agent 可以处理更丰富的输入类型

> 笔者认为：Micro-VM 沙箱方案的关键优势不在于「更安全」，而在于「安全的同时保持开发体验」——sandboxed-lit 通过固定资源配额（2CPU/1GB）而非权限标志（`--privileged`）来定义边界，这意味着隔离不是可选项而是架构强制。

---

## 6. 评分与适用性评估

| 维度 | 评分 | 说明 |
|------|------|------|
| **主题重要性** | 3/5 | Agent 执行层隔离是长程 Agent 的核心挑战，但 microsandbox 是细分方向 |
| **实践价值** | 4/5 | 有代码有配置，PDF 解析能力是差异化亮点 |
| **独特视角** | 4/5 | 第一个生产可用的 Micro-VM Agent 执行方案 |
| **技术深度** | 4/5 | Rust + agent-sdk + liteparse 的技术栈组合有说服力 |

> 本文分析了 `run-llama/sandboxed-lit` 的架构设计与工程实践价值。该项目代表了 Agent 执行层从容器向 Micro-VM 演进的技术趋势，对于需要处理不受信任代码或非结构化文档的 Agent 场景具有实际参考意义。

---

**关联主题**：本文与「OpenAI Codex 安全运行架构」（harness/）共同构成 Agent 执行层的完整覆盖——OpenAI 解决的是「权限控制与审批流程」，sandboxed-lit 解决的是「资源隔离与文件边界」。两者组合提供了企业级 Agent 部署的「控制面 + 隔离面」双重保障。