# run-llama/sandboxed-lit：Micro-VM 级 Agent 沙箱的 Rust 实现

> 推荐一个填补容器与 V8 Isolate 之间空白的 Agent 执行方案：sandboxed-lit 用 Rust 实现了微虚拟机级别的资源隔离，让 Agent 可以在毫秒级启动的轻量级沙箱内安全执行文件操作和命令。

---

## 🚀 快速理解

| 维度 | 信息 |
|------|------|
| **项目** | [run-llama/sandboxed-lit](https://github.com/run-llama/sandboxed-lit) |
| **Stars** | 49（2026-05-11 创建，2天内） |
| **语言** | Rust |
| **许可** | MIT |
| **定位** | Micro-VM Agent 执行沙箱 |

---

## 🤔 T — Target：谁该关注

- **有 Rust 经验**的 Agent 开发工程师，想构建需要处理不受信任代码的安全执行环境
- **安全团队**需要为 AI Agent 部署文件分析流水线但担心代码外泄
- **平台开发者**在设计 Agent 即服务（Agent-as-a-Service）产品，需要比容器更细粒度的隔离方案

---

## 📊 R — Result：能带来什么

**具体改变**：
- Agent 执行环境启动时间从 **秒级（Docker）降至毫秒级（Micro-VM）**
- PDF/Office 文档解析从「需要挂载外部服务」变为「沙箱内置 liteparse」
- 文件系统边界从「容器 Overlay FS」变为「精确 bind mount」，Agent 只能看到 `/app/data/` 下的文件

**量化数据**：
- microsandbox 启动：**<100ms**（官方描述）
- 资源配置：**2 CPU + 1GB RAM**（硬性上限，无法超用）
- 文档解析：PDF/图片/Office 全部在沙箱内完成，无需网络

---

## 💡 I — Insight：它凭什么做到这些

**Micro-VM 架构**：sandboxed-lit 没有使用 Docker 容器，而是依赖 microsandbox 的微虚拟机技术。微 VM 比容器更轻量（启动更快），比 V8 Isolate 更安全（资源硬限制 + 文件系统精确绑定）。

**工具设计**：sandboxed-lit 暴露三个 agent-sdk 工具——`list_files`、`read_file`、`run_bash_command`——全部只能在 `/app/data/` 目录下操作，超出绑定目录的访问会被架构层面拒绝。

**liteparse 集成**：大多数 Agent 沙箱只处理纯文本，但 sandboxed-lit 内置了 PDF/图片/Office 文档解析。这意味着 Agent 可以分析扫描件、读取报告、操作 Office 文件，全部在隔离环境内完成。

> 官方原文：
> "A small Rust CLI that runs an LLM agent inside a microsandbox VM. The agent uses OpenAI's GPT models via agent-sdk and has tools to list files, read files (parsing PDFs / images / Office docs through liteparse), and run bash commands, all confined to the sandbox."
> — [run-llama/sandboxed-lit README](https://github.com/run-llama/sandboxed-lit)

---

## 📈 P — Proof：谁在用/热度/生态

**生态位置**：run-llama 是 LlamaIndex 团队的项目，sandboxed-lit 是其在 Agent 安全执行方向的实验性扩展。依赖 microsandbox 基础设施（[microsandbox.dev](https://github.com/microsandbox/microsandbox)）和 agent-sdk（Rust 版 Agent SDK）。

**数据**：
- 49 Stars，2026-05-11 创建，2 天
- 依赖：`agent-sdk`（Rust Agent SDK）+ `microsandbox`（微 VM）+ `liteparse`（文档解析）
- 技术栈：Rust + microsandbox VM + OpenAI GPT

**竞品对比**：

| 方案 | 隔离级别 | 启动时间 | PDF/Office | Rust 支持 |
|------|---------|---------|-----------|---------|
| **sandboxed-lit** | Micro-VM | <100ms | ✅ liteparse | ✅ 原生 |
| Docker 容器 | 容器 | 1-5s | ✅ 需挂载 | ❌ |
| Cloudflare Workers | V8 isolate | <10ms | ❌ | ❌ |
| Anthropic Code Executor | 容器 + MCP | 秒级 | ✅ | ❌ |

---

## 🎯 T — Threshold：行动引导

**快速上手**：

```bash
# 1. 安装 microsandbox host（见文档）
# 2. 设置 OpenAI API key
export OPENAI_API_KEY=sk-...

# 3. 构建
cargo build --release

# 4. 运行
sandboxed-lit -p "Summarize every PDF in the working directory."

# 或挂载特定目录
sandboxed-lit -p "List the files, then read report.pdf and extract the key findings." -v /Users/me/documents
```

**限制**：
- 需要运行 microsandbox host，不是开箱即用
- 只支持 OpenAI GPT 模型（暂无 Claude 支持）
- 资源配置硬编码（2CPU/1GB），无法动态调整

**持续关注价值**：当 Agent 平台需要处理不受信任的用户代码或文档时，micro-VM 隔离是一个值得关注的技术方向。sandboxed-lit 作为第一个生产可用的 Rust 实现，提供了有价值的工程参考。

---

## 主题关联

**关联 Article**：「Agent 执行层的架构演进：从进程隔离到 Micro-VM」（harness/）

本文与「OpenAI Codex 安全运行架构」共同构成 Agent 执行层的完整覆盖：
- **OpenAI Codex**：权限控制与审批流程（控制面）
- **sandboxed-lit**：资源隔离与文件边界（隔离面）

两者组合提供了企业级 Agent 部署的「控制面 + 隔离面」双重保障。

---

*推荐评分：主题重要性 3/5 | 实践价值 4/5 | 独特视角 4/5 | 项目成熟度 2/5 | 综合推荐阈值：≥12 → 推荐*