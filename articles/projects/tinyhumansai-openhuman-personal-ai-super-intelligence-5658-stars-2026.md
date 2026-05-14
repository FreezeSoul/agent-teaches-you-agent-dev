# tinyhumansai/openhuman: Personal AI Super Intelligence，5,658 Stars，Rust + TypeScript 双技术栈

> OpenHuman 是一个开源的个人 AI super intelligence 助手，核心设计理念是「让 Agent 在几分钟内了解你，而非几周」。它通过 Memory Tree + Obsidian Vault + 118+ OAuth 集成 + Auto-fetch 机制，将个人数据源压缩为 AI 可理解的上下文，实现真正的「个人化 Agent」。与 Anthropic Claude Code April Postmortem 形成「Harness 变更 → 用户感知质量」的完整闭环：Anthropic 发现三次变更导致质量下降，OpenHuman 提供了「数据驱动的上下文积累」作为解决方案——让 Agent 拥有持久记忆，而非每次都从零开始。

---

## TRIP 四要素

### T - Target（目标用户）

**个人用户或小型团队**：想要一个开箱即用、无需配置的「个人 AI 助手」，具备完整的记忆能力和跨平台集成。需要 Agent 在几分钟内就了解用户的完整上下文，而非需要几周的数据积累期。

**不适合**：需要深度定制、对数据主权有严格监管要求（已在本地但需要高级安全控制）、或者只需要单一功能（纯编码/纯搜索）的用户。

### R - Result（核心成果）

- **启动时间**：从安装到「Agent 了解你的完整上下文」仅需几分钟（vs 其他 Agent 需要数周的训练期）
- **Token 压缩**：TokenJuice 技术可将工具调用、爬取结果、邮件正文和搜索负载压缩至多 80% 的 token 消耗
- **Auto-fetch**：每 20 分钟自动同步所有已连接的数据源到 Memory Tree，无需手动触发
- **118+ OAuth 集成**：Gmail/Notion/GitHub/Slack/日历/Drive/Linear/Jira 等，开箱即用

### I - Insight（技术亮点）

**Memory Tree + Obsidian Vault 双层架构**：
- 所有数据 canonicalized 为 ≤3k-token Markdown chunks，评分后存入 SQLite 的分层摘要树
- 同时以 `.md` 文件形式存入 Obsidian 兼容的 vault，用户可以直接浏览和编辑
- 灵感来自 Karpathy 的 obsidian-wiki workflow，实现「本地优先 + Agent 可读」的双重目标

**Model Routing 内置**：
- 每个任务自动路由到合适的 LLM（reasoning/fast/vision）
- 支持 Ollama 本地模型，用于设备上的工作负载
- 一个订阅覆盖所有模型，无「API 碎片化」问题

**Rust + TypeScript 双技术栈**：
- 核心 runtime（Rust）：高性能、低内存占用、桌面级稳定性
- Web UI（TypeScript）：跨平台一致的用户体验
- Tauri/CEF 作为桌面 Shell，兼顾安全性和功能性

### P - Proof（数据支撑）

- **GitHub**: 5,658 Stars，TrendsShift top 1%
- **技术栈**: Rust (core) + TypeScript (UI) + Tauri (desktop shell)
- **平台支持**: macOS/Linux/Windows，通过 `curl | bash` 或 PowerShell 一键安装
- **文档**: 完整的 GitBook 文档，Architecture/Getting Started/Cloud Deploy 均有覆盖
- **社区**: Discord + Reddit + X，贡献者 Hall of Fame 机制

---

## P-SET 骨架

### P - Positioning（定位破题）

**一句话定义**：Personal AI super intelligence 运行时，让 AI Agent 在几分钟内通过数据积累了解你的完整上下文，而非需要数周的训练期。

**场景锚定**：当你觉得 Claude Code/Coworker 或其他 Agent「需要花很长时间才能了解我」，或者每次新 session 都要重新解释上下文时，OpenHuman 是解决这个问题的工程级方案。

**差异化标签**：Rust 性能 + Memory Tree 持久化 + Obsidian Vault 可读性 + 118 OAuth 自动同步

---

### S - Sensation（体验式介绍）

当你首次打开 OpenHuman，桌面 Mascot 会出现。连接 Gmail/Notion/GitHub 后，20 分钟内 Auto-fetch 将所有数据拉取到本地，压缩为 Memory Tree 中的层级摘要。同时，Obsidian vault 中生成了对应的 `.md` 文件——你打开 Obsidian 时可以看到 Agent「眼中的你」。

这不是传统的「聊天历史回顾」——而是结构化的知识图谱，每个节点都是从真实活动中提取的语义摘要。

---

### E - Evidence（拆解验证）

**技术深度**：
- Memory Tree：hierarchical summary trees，SQLite 存储，本地优先
- TokenJuice：压缩层，HTML→Markdown，长 URL 缩短，非 ASCII 字符移除，可降低 80% token 消耗
- Auto-fetch：每 20 分钟对每个活跃连接拉取最新数据，零人工干预

**与 Claude Code 对比**：

| 维度 | Claude Code | OpenHuman |
|------|-------------|-----------|
| 记忆范围 | 当前 session + 插件传递 | 全量历史数据 + Memory Tree |
| 启动时间 | 每次从零 | 几分钟（通过已有数据）|
| 上下文获取 | 手动 prompt | Auto-fetch + Memory Tree |
| 工具层 | 代码专用工具 | 代码 + 搜索 + 爬取 + 语音 |
| 模型 | 单一模型 | 自动路由到合适的 LLM |

**社区健康度**：
- 持续活跃开发（Early Beta 状态）
- 完整的 CONTRIBUTING.md + Architecture 文档
- `pnpm dev` / `cargo check` 等标准化开发流程

---

### T - Threshold（行动引导）

**快速上手**：
```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash

# Windows
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex

# 从源码构建
git clone https://github.com/tinyhumansai/openhuman
cd openhuman
git submodule update --init --recursive
pnpm install
pnpm dev
```

**适合贡献的场景**：
- Rust 开发者：core runtime、memory tree、model routing
- TypeScript 开发者：UI、integration OAuth flows
- 文档：GitBook 文档完善

---

## 关联分析

### 与本文的关联

**Anthropic April 2026 Postmortem** 发现：三个独立的 Harness 变更（默认推理努力度、缓存清除 Bug、系统提示词长度限制）各自在不同时间影响不同的流量切片，造成「广泛且不一致」的感知质量下降。

**OpenHuman** 提供的解决方案核心逻辑：**如果 Agent 有持久化的 Memory Tree，每次变更的影响会被压缩到最小**——因为 Agent 不再依赖单次 session 的上下文，而是有跨 session 的结构化知识积累。这形成了一个「Harness 变更 → 用户感知质量下降 → 持久记忆作为缓冲」的完整闭环。

### 适用边界

- **适合**：需要「时刻了解我」的长期 Agent、跨 session 的上下文连续性、多数据源的个人用户
- **不适合**：需要完全离线/高安全要求的场景（虽然数据在本地，但默认开启云端同步）、只需要单次编码 session 的场景

---

*来源：[OpenHuman GitHub README](https://github.com/tinyhumansai/openhuman) | [Docs](https://tinyhumans.gitbook.io/openhuman/) | [Install](https://tinyhumans.ai/openhuman)*