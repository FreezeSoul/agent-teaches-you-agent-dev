# context-evaluator：你的 AGENTS.md 文件健康体检报告

> **核心问题**：556:1 的复制者/贡献者比例告诉我们，整个行业都在堆叠 AI 配置文件，却没有人真正审核它们。context-evaluator 是第一个专门解决这个问题的工具——用 17 个评估器诊断你的 AGENTS.md / CLAUDE.md，告诉你在哪里出了问题，以及如何修复。

---

## 定位：给 AI 配置文件做「体检」

**目标用户**：已经意识到 AGENTS.md/CLAUDE.md 没有预期效果，但不知道哪里出了问题的开发者和 AI 团队负责人。

**一句话定义**：一个 AI Agent 配置文件的质量分析器 + 自动修复工具。

**场景锚定**：你刚刚从网上复制了一份「完美 AGENTS.md 模板」，或者你手动写了 200 行配置，但你的 Agent 仍然在忽略它们。context-evaluator 告诉你哪里出了问题。

**差异化标签**：业界第一个针对 AI Agent 配置文件的系统性诊断工具。

---

## 体验：5 分钟内拿到体检报告

### 安装

```bash
# 下载对应平台的可执行文件
./context-evaluator-<platform> api   # 启动 Web UI
# 或
./context-evaluator-<platform> cli evaluate --path /path/to/project
```

### 使用

输入你的仓库 URL 或本地路径，1-3 分钟后拿到完整的评估报告。

评估结果分为两类：
- **Errors（13 个）**：现有内容的问题，需要修复
- **Suggestions（4 个）**：基于代码库分析建议新增的内容

每个问题包含：
- **严重级别**（Critical / High / Medium / Low）
- **具体位置**
- **问题描述**
- **修复建议**

### 自动修复

在 Web UI 中选中问题，选择目标 Agent 格式（AGENTS.md / Claude Code / GitHub Copilot / Cursor），点击执行。它会运行一个 4 阶段 pipeline：

1. 计划错误修复
2. 执行错误修复
3. 计划建议添加
4. 执行建议添加

然后你可以逐文件审查 diff，下载 `.patch` 文件手动应用。

---

## 拆解：17 个评估器覆盖了哪些维度

| # | 评估器 | 类型 | 说明 |
|---|--------|------|------|
| 01 | Content Quality | Error | 检测人类导向、无关或模糊的内容 |
| 02 | Structure & Formatting | Error | 识别组织混乱和格式不一致 |
| 03 | Command Completeness | Error | 发现不完整的命令和缺失的前置条件 |
| 04 | Testing Guidance | Error | 检测缺失或不清晰的测试指导 |
| 05 | Code Style Clarity | Error | 识别缺失或冲突的代码风格指南 |
| 06 | Language Clarity | Error | 查找歧义语言和未定义的术语 |
| 07 | Workflow Integration | Error | 检测缺失的 git/CI 工作流文档 |
| 08 | Project Structure | Error | 识别缺失的代码库组织说明 |
| 09 | Security Awareness | Error | 发现暴露的凭据和安全风险 |
| 10 | Completeness & Balance | Error | 检测骨架化或过度详细的内容 |
| 11 | Subdirectory Coverage | Suggestion | 建议为子目录单独创建 AGENTS.md |
| 12 | (Suggestion) | Suggestion | 建议类型 |
| 13 | (Suggestion) | Suggestion | 建议类型 |
| 14 | (Suggestion) | Suggestion | 建议类型 |

> 这是第一个系统性地将「配置文件质量」分解为可量化维度的工具。之前的行业现状是：复制模板 → 堆叠文件 → 抱怨不生效，没有人知道为什么。

---

## 技术实现：如何做到自动化诊断

### 评估流程

```
Input (Git URL or Local Path)
  ↓
Clone Repository (if remote)
  ↓
Analyze Codebase (languages, frameworks, patterns)
  ↓
Find Documentation (AGENTS.md, CLAUDE.md, linked files)
  ↓
Run 17 Evaluators via AI
  ↓
Rank by Impact
  ↓
Calculate Score & Grade
  ↓
Return Results
```

### 输出格式映射

context-evaluator 会根据目标 Agent 格式决定输出文件的结构和位置：

| 目标 | 主文件 | Rules / Instructions | Skills |
|------|--------|----------------------|--------|
| AGENTS.md | AGENTS.md | .agents/rules/ | .agents/skills/ |
| Claude Code | CLAUDE.md | .claude/rules/ | .claude/skills/ |
| GitHub Copilot | .github/copilot-instructions.md | .github/instructions/ | .github/skills/ |
| Cursor | .cursor/rules/*.mdc | (integrated) | .cursor/skills/ |

**关键设计决策**：Rule（短期声明性约束，始终加载）和 Skill（按需加载的流程性工作流）的区分，直接对应了 Anthropic Agent Skills 的设计理念。

---

## 为什么现在出现是合理的

context-evaluator 的出现不是偶然的。它是三个趋势交汇的产物：

### 1. 配置蔓延到临界点

如 Augment Code 博客所描述的：556:1 的复制者/贡献者比例意味着整个行业在传播没人审核的配置文件。这个问题足够普遍、足够痛，才会产生专门的工具。

### 2. ETH Zurich 研究提供了数据基础

研究证明了「上下文文件降低任务成功率」这一反直觉事实。现在有了数据，才能量化「什么让配置文件变坏」。

### 3. Agent Skills 提供了分层思路

Anthropic 的 Skills vs Rules 区分（始终加载 vs 按需加载）为「什么应该进 AGENTS.md，什么应该进 Skill」提供了判断框架。context-evaluator 将这个框架操作化为具体的评估维度。

---

## 使用建议

**适合的场景**：
- 你的团队有 3+ 个 AI 配置文件，不确定它们是否有效
- 你从网上复制了 AGENTS.md 模板，但 Agent 表现没有改善
- 你想对团队的 AI 配置质量做一次系统性审计

**不适合的场景**：
- 你的项目还没有任何 AI 配置文件（先用起来，从简单开始）
- 你已经知道问题在哪（直接手动修复更快）

**行动路径**：
1. 运行一次 `context-evaluator` 获取体检报告
2. 关注 Critical 和 High 级别的问题，这些是最影响 Agent 表现的因素
3. 使用 AI 自动修复前先审查 diff，确认改动符合预期
4. 修复后再次运行评估，对比 Before/After 分数

---

> **引用来源**：
> - [PackmindHub/context-evaluator GitHub](https://github.com/PackmindHub/context-evaluator)
> - [Augment Code Blog: Your agent's context is a junk drawer](https://www.augmentcode.com/blog/your-agents-context-is-a-junk-drawer)（配置文件蔓延的行业背景）
> - [ETH Zurich: Evaluating AGENTS.md Files](https://arxiv.org/abs/2602.11988)（配置文件有效性的研究数据）