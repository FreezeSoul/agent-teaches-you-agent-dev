# Ouroboros — Agent OS：规范优先的可验证编码工作流

> Ouroboros 是一个将模糊想法转化为可验证代码的 Agent 运行时层，适用于 Claude Code、Codex CLI、OpenCode 和 Hermes。它通过「访谈→结晶→执行→评估→演化」五阶段循环，将 AI 编码从不确定prompting 变为可回放、可观测的规范驱动工作流。GitHub 3.2K ⭐，MIT License。

---

## T — Target（谁该关注）

- **有 AI Coding 经验**的工程师（已使用过 Claude Code/GitHub Copilot，希望提升输出可靠性）
- **团队 lead**：希望让 AI 编程结果可复现、可审查，而非每次都是黑盒输出
- **追求确定性的开发者**：厌倦了「看起来对但不知道为什么会这样」的 AI 输出

> 如果你每次让 AI 写完代码后还需要大量人工 review 和调试，Ouroboros 正是为你设计的。

---

## R — Result（能带来什么）

| 指标 | 改变 |
|------|------|
| **输入质量** | 从模糊 prompt 变为经过 Socratic 访谈的结构化规范 |
| **架构漂移** | Immutable seed spec 在执行过程中锁定意图，防止中途偏离 |
| **QA 确定性** | 3-stage automated evaluation gate 替代「目测检查」 |
| **可复现性** | Replayable workflow，任何时候都能回放执行过程 |

Ouroboros 官网描述：

> "Turn a vague idea into a verified, working codebase — across Claude Code, Codex CLI, OpenCode, and Hermes."

---

## I — Insight（它凭什么做到）

**核心洞察：Most AI coding fails at the input, not the output.**

| 问题 | 传统做法 | Ouroboros 做法 |
|------|---------|---------------|
| Vague prompts | AI 猜测 → 大量 rework | Socratic 访谈暴露隐藏假设 |
| 无规范 | 架构中途漂移 | Immutable seed spec 执行前锁定意图 |
| Manual QA | "看起来对" ≠ 验证 | 3-stage automated evaluation gate |

### 五阶段循环

```
Interview → Crystallize → Execute → Evaluate → Evolve
```

- **Interview**：用 Socratic 提问暴露用户需求中的隐藏假设和矛盾
- **Crystallize**：将访谈结果凝固为不可变的 seed spec
- **Execute**：AI Agent 按规范执行（Claude Code/Codex CLI 等）
- **Evaluate**：3-stage 自动评估门控
- **Evolve**：根据评估结果迭代优化

README 原文：

> "Ouroboros is an Agent OS for AI coding: a local-first runtime layer that turns non-deterministic agent work into a replayable, observable, policy-bound execution contract. It replaces ad-hoc prompting with a structured specification-first workflow."

### 跨平台支持

README 明确说明支持多个主流 Agent：

> "Works with Claude Code, Codex CLI, OpenCode, and Hermes. The installer detects Claude Code, Codex CLI, and Hermes CLI automatically and registers the MCP server."

---

## P — Proof（凭什么信它）

| 指标 | 数值 |
|------|------|
| **GitHub Stars** | 3,224 ⭐ |
| **Forks** | 314 |
| **License** | MIT |
| **Platform Support** | Claude Code, Codex CLI, OpenCode, Hermes |

### 快速安装

```bash
curl -fsSL https://raw.githubusercontent.com/Q00/ouroboros/main/scripts/install.sh | bash
```

安装后使用：

```
> ooo interview "I want to build a task management CLI"
```

---

## 🎯 为什么 Ouroboros 与 Anthropic Context Engineering 互补

本文 Articles 解读了 [Anthropic Context Engineering 三层技术体系](./anthropic-context-engineering-triple-layer-long-horizon-2026.md)——Compaction（上下文压缩）、Structured Note-taking（结构化笔记）、Sub-agent Architectures（子代理架构）。

Ouroboros 从**输入端**解决同类问题：

| 层次 | Anthropic Context Engineering | Ouroboros |
|------|------------------------------|-----------|
| **输入端** | Just-in-Time Context（减少预加载冗余）| Specification-first（通过访谈减少模糊输入）|
| **过程端** | Compaction（压缩历史 Context）| Evaluation Gate（实时验证防止漂移）|
| **记忆端** | Structured Note-taking（外部持久化）| Replayable workflow（全量回放而非记忆重建）|

> "Stop prompting. Start specifying." — Ouroboros 官网 tagline

两者共同构成了完整的 Agent 可靠性框架：**Ouroboros 从输入端减少上下文污染**（模糊规范 → 结构化 spec），**Anthropic 从过程端管理上下文容量**（Compaction + Note-taking）。

---

## Threshold（行动引导）

### 快速上手

1. **安装**（一键，自动检测 Claude Code / Codex CLI / Hermes）：
```bash
curl -fsSL https://raw.githubusercontent.com/Q00/ouroboros/main/scripts/install.sh | bash
```

2. **启动访谈**：
```bash
ooo interview "我想构建一个任务管理 CLI"
```

3. **跟随 Ouroboros 的 Socratic 访谈**，直到规范被冻结为 seed spec

4. **Execute → Evaluate → Evolve** 循环直到通过 3-stage gate

### 适用边界

- ✅ **大型重构/迁移项目**：规范前置减少中途漂移风险
- ✅ **团队代码审查**：可回放记录让 review 有据可查
- ❌ **小型 quick task**：访谈开销可能大于收益
- ❌ **高度探索性任务**：规范驱动与快速迭代存在内在张力

---

**相关资料**：
- [GitHub: Q00/ouroboros](https://github.com/Q00/ouroboros)
- [Anthropic Context Engineering 三层技术体系](../context-memory/anthropic-context-engineering-triple-layer-long-horizon-2026.md)