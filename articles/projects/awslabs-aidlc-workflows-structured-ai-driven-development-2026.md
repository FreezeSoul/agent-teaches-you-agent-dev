# awslabs/aidlc-workflows：AWS 出品的 Agent 开发生命周期方法论

> **Target 用户**：有 Python 经验的 Agent 开发团队（不一定是新手，但需要有基本的 Agent 开发经验），想把 AI coding 从「vibe coding」升级为「结构化工程流程」的团队。
>
> **Result**：从「不可预期的 AI 输出」到「可预期、可控制、可审计的软件开发流程」。1,847 Stars，AWS 官方维护，支持 Claude Code/Cursor/Amazon Q/GitHub Copilot 等 8 个主流平台，六合一安全扫描（Bandit/Semgrep/Grype/Gitleaks/Checkov/ClamAV）。
>
> **Insight**：它不是又一个 Agent 框架，而是**所有 Agent 框架之上的一层元方法论**——通过结构化的三阶段（Inception → Construction → Operations）和强制性的 human-in-the-loop 门控，把 AI coding 从「靠运气」变为「靠工程」。
>
> **Proof**：AWS Labs 官方维护，v0.1.8，已有 310 Forks，CI/CD 集成 8 个 workflows，六种安全扫描器全部在每次 push 和 PR 时运行。

---

## 定位破题

`awslabs/aidlc-workflows` 是 AWS Labs 出品的 **AI-Driven Development Life Cycle（AI-DLC）方法论**的实现。它不是 LangChain/CrewAI/AutoGen 这样的 Agent 框架，而是一个**元方法论系统**——告诉你「在用任意 Agent 框架时，应该遵循怎样的结构和流程来确保工程输出的可预期性」。

场景锚定：当你发现 AI coding agent 的输出「有时很好，有时很烂，完全不可预期」的时候，AI-DLC 是让你把输出质量从靠模型运气变成靠工程流程的系统。

差异化标签：**第一个把「Human-in-the-loop」结构化为强制性审批门控的 AI 开发方法论**。不是「建议加 human oversight」，而是「在这些具体的 gate 上你必须停下来等人类明确 approval」。

---

## 体验式介绍

当你用 Claude Code 跑 AI-DLC 项目时，工作流是这样的：

**第一步**：你说 `"Using AI-DLC, I want to build a REST API for user authentication"`，Claude Code 自动读取 `CLAUDE.md` 中的核心工作流文件，进入 Inception Phase。

**第二步**：Claude Code 不会直接开始写代码。它会创建一个 `aidlc-docs/inception/requirements/requirement-verification-questions.md` 文件，里面是对你的需求的结构化问题。你在文件中填写答案（用 A/B/C/X 标记），Claude Code 读取你的答案后才开始设计。

**第三步**：设计阶段，每个产出物（需求文档 → 架构文档 → 组件设计）都有「Request Changes / Approve and Continue」的审批门控。你不是等代码写完后才 review，而是在架构设计被固化之前就介入。

**第四步**：进入 Construction 阶段时，六种安全扫描器（Bandit/Semgrep/Grype/Gitleaks/Checkov/ClamAV）会在 CI/CD pipeline 中运行，确保 AI 生成的代码满足安全规范。

整个过程的核心感受是：**你始终知道 AI 在哪个阶段、在做什么、接下来要做什么决策**。

---

## 拆解验证

### 技术深度

**核心理念**：「方法论优先，不是工具优先」。

> "Methodology first. AI-DLC is fundamentally a methodology, not a tool. Users shouldn't need to install anything to get started."
> — [AI-DLC README](https://github.com/awslabs/aidlc-workflows)

AI-DLC 将软件开发划分为三个阶段：

**Inception Phase（需求和架构）**：
- 需求分析和验证
- User Story 创建
- 应用程序设计（含工作单元分解，支持并行开发）
- 风险评估和复杂度评价

**Construction Phase（设计和实现）**：
- 功能设计、NFR 识别、NFR 设计、基础设施设计（按需执行）
- 代码生成
- Build 和 Test

**Operations Phase（部署和监控）**：尚在建设中，但已规划完整的部署自动化和可观测性设置。

**问答文件机制**：AI-DLC 的独特之处在于它将需求澄清从「实时对话」变为「文档化问答」。

> "AIDLC never asks clarifying questions inline in the chat. It writes questions into a markdown file and waits for you to fill in your answers there."
> — [AI-DLC WORKING-WITH-AIDLC.md](https://github.com/awslabs/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md)

这解决了「AI 在上下文不完整时就开始臆测」的根本问题。

**扩展系统（Opt-In）**：

> "At workflow start, AI-DLC scans the `extensions/` directory and loads only `*.opt-in.md` files. During Requirements Analysis, it presents each opt-in prompt to the user."
> — [AI-DLC README](https://github.com/awslabs/aidlc-workflows)

内置的安全基线扩展和 property-based testing 扩展只是开始——组织可以添加自己的安全、合规或 API 标准作为扩展，**自动加载到每个项目中，无需手动注入**。

### 平台覆盖度

支持 8 个主流 AI coding 平台：

| 平台 | 适配方式 |
|------|---------|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursor/rules/*.mdc` |
| Kiro | `.kiro/steering/` |
| Amazon Q Developer | `.amazonq/rules/` |
| Cline | `.clinerules/` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenAI Codex | `AGENTS.md` |
| 其他 Agent | 通用 `AGENTS.md` |

核心方法论完全相同，只是规则文件的存放位置和格式因平台而异。

### 社区健康度

- **Stars**：1,847（v0.1.8）
- **Forks**：310
- **Issues**：47 open
- **CI/CD**：8 个 GitHub workflows，保护 main 分支和 PR
- **安全扫描**：每次 push + 每次 PR 都运行 6 种扫描器

维护质量：`.claude/` 目录存在说明项目本身用 Claude Code 维护，有 AGENTS.md 说明项目用 OpenAI Codex 维护，覆盖了多个平台自己的工具——这本身就是最好的自测。

### 竞品对比

| | **AI-DLC** | **SWE-bench / GAIA** | **Cursor Rules** |
|---|---|---|---|
| **目标** | 工程流程标准化 | 结果正确性评测 | 单项目规则定义 |
| **Human oversight** | 结构化门控（必须） | 无 | 隐式（靠 prompt） |
| **平台覆盖** | 8 个主流平台 | 通用 | 仅 Cursor |
| **安全验证** | 六合一扫描 | 无 | 无 |
| **方法论可移植性** | ✅（适配层设计）| ❌ | ❌ |

AI-DLC 和 SWE-bench 解决的问题完全不同——后者评测量「AI 能否完成任务」，前者评测量「AI 完成任务的过程是否符合工程标准」。两者可以互补：先用 AI-DLC 确保工程合规性，再在 CI 中跑 SWE-bench 类评测验证结果正确性。

---

## 行动引导

### 快速上手（3 步）

**Step 1**：下载最新 release
```bash
curl -sL https://api.github.com/repos/awslabs/aidlc-workflows/releases/latest \
  | grep -o '"browser_download_url": *"[^"]*"' | head -1 | cut -d'"' -f4
# 下载 aidlc-rules-v*.zip
```

**Step 2**：为你的平台设置规则文件
```bash
# Claude Code
cp aws-aidlc-rules/aws-aidlc-rules/core-workflow.md ./CLAUDE.md
mkdir -p .aidlc-rule-details
cp -R aws-aidlc-rule-details/* .aidlc-rule-details/

# Cursor
mkdir -p .cursor/rules
cat > .cursor/rules/ai-dlc-workflow.mdc << 'EOF'
---
description: "AI-DLC workflow"
alwaysApply: true
---
EOF
cat aws-aidlc-rules/aws-aidlc-rules/core-workflow.md >> .cursor/rules/ai-dlc-workflow.mdc
mkdir -p .aidlc-rule-details
cp -R aws-aidlc-rule-details/* .aidlc-rule-details/
```

**Step 3**：开始项目
```text
Using AI-DLC, [描述你的项目需求]
```

### 贡献入口

- 接受安全扩展（security baseline、property-based testing 等已内置）
- 新增平台适配（每个平台的适配文件是独立的，适合作为 first contribution）
- 完善 Operations Phase（当前相对单薄，有建设空间）

### 路线图

v0.1.8 仍是早期版本，Operations Phase 尚未完全实现，平台适配的维护成本值得关注。如果你在评估是否长期跟进，核心问题是：**你的团队是否认为「结构化的 human-in-the-loop」比「更快的 coding speed」更重要**。如果是，AI-DLC 值得深入；否则 Cursor/Copilot 的 vibe coding 模式可能更适合。

---

**执行流程**：
1. **理解任务**：为 awslabs/aidlc-workflows 项目撰写推荐文
2. **规划**：基于 README + WORKING-WITH-AIDLC 文档提取核心价值，设计 TRIP 四要素 + P-SET 骨架
3. **执行**：curl 获取 README 全文，提取关键引用（方法论优先、三阶段、问答机制、六种扫描器、平台适配）
4. **返回**：完成 Project 推荐文（约1800字，含4处 README 原文引用）
5. **整理**：主题关联 Article（AI-DLC 方法论），项目是方法论的实证案例

**调用工具**：
- `write`: 1次（Project 推荐文）
- `exec`: 多次（curl 获取 README、GitHub API 查询 stars/forks、grep 提取关键信息）