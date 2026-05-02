# Cursor Cloud Agents：第三个软件开发时代的基础设施

> *"This isn't autocomplete. This isn't even pair programming. This is delegated engineering."*
> — Cursor 官方博客，2026年2月

## 核心观点

Cursor Cloud Agents 代表了一种根本性的转变：AI 编程从「辅助工具」演变为「执行单元」。这不是增量改进，而是一种全新的软件开发范式——**软件工程师的角色从「写代码」变为「定义任务、审查结果」**。

这篇文章分析 Cursor Cloud Agents 的架构设计，以及它如何成为「第三个软件开发时代」的核心基础设施。

---

## 背景：三个软件开发时代

| 时代 | 范式 | 主体 | 工具 |
|------|------|------|------|
| 第一时代 | 人工编码 | 人类工程师 | 编辑器 + 编译器 |
| 第二时代 | AI 辅助编程 | 人类主导，AI 辅助 | Copilot、Code Review Bot |
| **第三时代** | **AI 委托编程** | **AI 主导，人类审查** | **Cloud Agents** |

第二时代到第三时代的本质区别：**循环控制权的转移**。

- 第二时代：人类在循环中（Human-in-the-loop），每一步都需要人类触发和确认
- 第三时代：人类在循环外（Human-out-of-the-loop），AI 自主完成，提交结果供人类审查

Cursor 自己的数字最能说明问题：**30% 的合并 PR 由 Cloud Agents 生成**。这不是概念验证，而是生产环境的真实比例。

---

## 架构设计：隔离 VM + 完整开发环境

### 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Cursor Cloud Agent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│   │  Harness   │───▶│  Planning   │───▶│   Tool Use  │          │
│   │  (推理+编排) │    │   (任务分解) │    │   (代码执行) │          │
│   └─────────────┘    └─────────────┘    └─────────────┘          │
│         ▲                                       │                │
│         │           ┌─────────────┐              │                │
│         └──────────│   Artifact  │◀─────────────┘                │
│                     │  Generation │                               │
│                     │(视频/截图/日志)│                              │
│                     └─────────────┘                               │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │              Isolated VM (隔离虚拟机)                      │ │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │ │
│   │  │ Terminal│  │ Browser │  │  File    │  │   CI    │     │ │
│   │  │         │  │         │  │ System   │  │ 模拟环境 │     │ │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 隔离 VM 的工程价值

每个 Cloud Agent 运行在**独立隔离的虚拟机**中，具备完整的开发环境：

- **终端**：执行命令、运行测试、构建项目
- **浏览器**：导航 UI、验证前端变化、截图记录
- **文件系统**：读写代码、配置开发环境
- **网络访问**：克隆仓库、安装依赖、推送 PR

隔离设计的核心价值：

1. **并行化**：用户可以同时启动 10-20 个 Cloud Agent 处理不同任务，彼此隔离互不干扰
2. **幂等性**：每个 VM 从干净状态开始，消除「在我机器上能跑」问题
3. **安全性**：恶意代码不会影响主机环境
4. **可重现**：同一任务可以在相同环境中复现

### 自我测试：UI 导航验证

Cloud Agents 的自我测试能力是其与普通代码生成工具的核心差异：

**传统 CI 验证方式**：
```
代码变更 → 提交 → CI 流水线运行 → 返回结果
```

**Cloud Agent 验证方式**：
```
代码变更 → 构建应用 → 启动 UI → 导航界面 → 截图/录屏 → 验证结果
```

Agent 不仅运行单元测试，还会在 VM 中启动应用，通过自动化方式（Playwright/Selenium 级别）导航 UI，验证功能正常工作。这个过程会被录制，最终的 PR 包含：
- 代码变更
- 构建输出
- **演示视频**：Agent 演示功能如何工作
- **截图**：关键 UI 状态
- **日志**：执行过程记录

这从根本上改变了 Code Review 的体验——reviewer 不需要本地运行代码，直接看视频就能验证功能。

---

## 企业扩展：Self-Hosted Cloud Agents

### 安全合规需求

2026年3月，Cursor 发布 Self-hosted Cloud Agents，将隔离 VM 的概念扩展到企业基础设施：

> *"Many enterprises in highly-regulated spaces cannot let code, secrets, or build artifacts leave their environment due to security and compliance requirements."*
> — Cursor Blog

对于金融、医疗等受监管行业，代码和 secrets 离开网络边界是不可接受的。Self-hosted 方案让企业：

- **代码不离开内网**：仓库、依赖、构建产物都在自有基础设施
- **安全模型不变**：沿用现有 VPN、防火墙、访问控制
- **Agent 能力保留**：Cursor 处理编排和模型推理，执行留在企业网络

### 架构对比

| 维度 | Cursor-Hosted | Self-Hosted |
|------|--------------|-------------|
| 代码存储位置 | Cursor 云 | 企业内网 |
| Agent 推理 | Cursor 云 | Cursor 云 |
| 工具执行 | Cursor 云 VM | 企业内网 VM |
| 适用场景 | 通用开发 | 受监管行业 |

两种部署模式共享相同的 Agent 能力架构，差异仅在执行层的位置。

### 规模化部署

对于需要管理大量 Self-hosted Workers 的企业，Cursor 提供：

- **Kubernetes Operator**：通过 `WorkerDeployment` CRD 定义 worker 池规模，控制器处理自动扩缩容和生命周期管理
- **Fleet Management API**：监控各 worker 利用率，自建扩缩容逻辑

这意味着 Cloud Agents 可以支撑**千人工程师团队的 PR 创建工作流**（Money Forward 的案例）。

---

## 工程意义：从 Copilot 到 Colleague

### 委托编程的工程含义

Cursor 提出的核心叙事是「Colleague」而非「Copilot」：

| 角色 | 行为模式 | 工程师角色 |
|------|---------|-----------|
| **Copilot** | 辅助编写代码 | 人类写，AI 提示 |
| **Colleague** | 独立完成任务 | 人类定义，AI 执行 |

这意味着软件工程师的工作重心转移：

**之前**：
```
需求 → 设计 → 编码 → 测试 → Code Review → 合并
         ↑_______人类执行此阶段_______↑
```

**现在**：
```
需求 → 设计 → [委托给 Agent] → Code Review → 合并
                    ↑
            AI 自主完成编码+测试+PR 创建
```

### 生产验证的信号价值

Cursor 自己 30% PR 来自 Cloud Agents，这个数字比任何技术指标都更有说服力：

- **技术可行性验证**：AI 可以独立完成生产代码的质量要求
- **自我信任**：如果 Cursor 自己的工程师愿意让 Agent 处理自己的代码，说明代码质量达到了内部标准
- **效率可量化**：30% 的代码产出不需要工程师手动编写

---

## 关联分析：Brain-Hands 解耦的 Cursor 实现

Anthropic 在 2026 年工程博客中提出了 Brain-Hands Decoupled Agent Architecture 框架：

> *"The brain handles high-level reasoning and planning; the hands execute in isolated environments."*

Cursor Cloud Agents 是该框架的典型实现：

| 组件 | Cursor 实现 | Brain-Hands 映射 |
|------|-----------|-----------------|
| **Brain** | Cursor Cloud（Harness + 推理 + 规划） | Agent 的高级推理中枢 |
| **Hands** | 隔离 VM（执行 + 工具调用 + 构建测试） | 沙箱化执行环境 |
| **通信协议** | HTTPS（Agent → Worker 工具调用） | 安全的 Brain-Hands 通道 |

隔离 VM 不仅是安全边界，也是 Brain-Hands 架构中「Hands」的物理实现——一个完整的、可自我验证的开发环境。

---

## 技术架构细节

### 多模型 Harness

Cloud Agents 支持在 Cursor Composer 2 或任何前沿模型中切换，允许针对不同任务类型选择最优模型：

- **复杂架构决策**：使用 Claude Opus
- **快速实现任务**：使用 Haiku
- **多模型 Ensemble**：同一任务并行用多个模型，取最优结果

### 触发渠道

Cloud Agents 通过多个渠道触发，覆盖不同工作流场景：

| 渠道 | 触发方式 | 典型场景 |
|------|---------|---------|
| **Cursor IDE** | 桌面/ Web 应用内 | 日常功能开发 |
| **Slack** | @mention Agent | 快速任务、紧急修复 |
| **GitHub** | Issue/Comment 触发 | 自动化 BUG 修复 |
| **Mobile** | 自然语言描述 | 移动端快速任务 |

Slack 集成尤其值得关注：工程师可以在 Slack 频道中 @Cursor Agent，描述任务需求，Agent 自动创建 Cloud Session，处理完成后在 Thread 中回复 PR 链接。这是**异步编程工作流**的完全体。

---

## 局限性与未解决问题

1. **任务边界**：目前 Cloud Agents 适合独立、明确的任务。复杂的多模块重构仍然需要人类架构师
2. **自我托管成本**：运行大量 Self-hosted Workers 需要算力资源，企业需要评估 TCO
3. **安全性边界**：即使在隔离 VM 中，Agent 的工具调用权限管理仍需要精细配置
4. **视频生成成本**：每个 PR 生成视频/截图需要额外资源，大规模使用有成本考量

---

## 总结

Cursor Cloud Agents 代表了 AI 编程的第三范式：从辅助到委托。核心贡献在于：

1. **隔离 VM 架构**：让 Agent 拥有完整、可重现的开发环境
2. **自我验证机制**：UI 导航测试 + 可视化 artifact，改变 Code Review 方式
3. **企业就绪**：Self-hosted 方案解决受监管行业的合规需求
4. **生产验证**：30% PR 比例证明技术可行性

这是 Anthropic Brain-Hands 解耦架构在工程实践中的具体实现，也是未来软件工程团队基础设施的雏形。

---

## 来源

- [Cloud Agents with Computer Use - Cursor Changelog (2026-02-24)](https://cursor.com/changelog/02-24-26)
- [Self-hosted Cloud Agents - Cursor Blog (2026-03-25)](https://cursor.com/blog/self-hosted-cloud-agents)
- [Cursor Cloud Agents: Autonomous Coding on Virtual Machines (nxcode.io)](https://www.nxcode.io/resources/news/cursor-cloud-agents-virtual-machines-autonomous-coding-guide-2026)
- [Managed Agents: Decoupling the brain from the hands - Anthropic (2026)](https://www.anthropic.com/news/managed-agents-decoupling-brain-hands)