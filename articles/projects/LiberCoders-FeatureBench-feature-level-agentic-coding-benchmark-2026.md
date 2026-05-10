# FeatureBench：让 AI 编程评估从「送分题」变成「能力检测」

**核心主张**：FeatureBench 通过「功能级评测」而不是「任务级评测」，解决了 SWE-bench 类基准测试中 AI 性能趋于饱和的问题——当 AI 能在 74% 的 SWE-bench 上完美解决每个任务时，你需要的是一个能够检测出细微能力差异的细粒度评测框架。

---

## 背景：AI 编程评估正在失去区分度

SWE-bench 在 2023 年发布时是一个有意义的基准：它测试 AI Agent 能否解决真实 GitHub Issue，难度足够高，区分度足够好。但到了 2026 年，顶级 AI 系统已经在 SWE-bench 上达到了 74%+ 的解决率，指标趋于饱和。

当「解决率」接近 100% 时，评估便失去了区分度。你无法通过一个满分知道 AI 是刚好解决还是完全掌握了一个能力维度。

FeatureBench 的出现就是为了解决这个问题：**从任务级评测转向功能级评测**。

---

## FeatureBench 是什么

FeatureBench 是一个测试驱动的数据生成和评测 pipeline，专门用于**功能级编程 Agent 评测**。

> "FeatureBench is a test-driven data generation and evaluation pipeline for feature-level coding benchmarks."
> — [FeatureBench GitHub README](https://github.com/LiberCoders/FeatureBench)

核心设计哲学：**一次 long text 对应多个问题，「inject once, query multiple times」**。这提高了评测效率，同时允许评估 Agent 在同一上下文下的多种能力维度。

### 核心数据

| 维度 | 内容 |
|------|------|
| **任务类型** | Feature-level coding（功能级编程） |
| **Fast split** | 100 个实例，无需 GPU，平均评测时间 57.2 秒/实例 |
| **Full split** | 更完整的实例集，需要 GPU |
| **支持的 Agent** | OpenHands、Claude Code、Codex、Gemini CLI、mini-swe-agent |

### 支持的 Agent 框架

README 原文：

> "2026.02.06: We now support one-click inference for mainstream agent frameworks, including OpenHands, Claude Code, Codex, Gemini CLI, and mini-swe-agent."
> — [FeatureBench GitHub README](https://github.com/LiberCoders/FeatureBench)

这意味着你可以通过统一的 CLI 接口评测 Claude Code 和其他主流 Agent，不需要为每个框架单独写评测代码。

---

## 核心机制：三个命令

FeatureBench 提供三个核心命令，都是 `fb`（FeatureBench 的 CLI 工具）：

```bash
# 推理：运行 Agent 在评测集上
fb infer \
 --config-path config.toml \
 --agent mini_swe_agent \
 --model openai/qwen3-coder-480b-a35b-instruct \
 --split fast

# 评测：评估推理结果
fb eval \
 --output.jsonl \
 --split fast

# 数据生成：生成新的评测数据
fb data
```

### 数据生成 pipeline

`fb data` 命令允许你生成自定义评测数据。这意味着 FeatureBench 不仅是一个评测工具，还是一个**评测数据生成工具**。你可以定义自己的功能级别测试场景，然后用 `fb infer` 运行 Agent，最后用 `fb eval` 评估结果。

---

## 与 Anthropic AI-Resistant Evaluations 的主题关联

FeatureBench 和 Anthropic 的「AI-Resistant Technical Evaluations」实际上在解决同一个问题的两个不同层面。

**Anthropic 的问题**：如何设计一个 AI 无法完整解决的评估，从而保留人类判断的信号？

**FeatureBench 的回答**：当任务级评测趋于饱和时，转向**功能级评测**——不是看 Agent 能否解决整个 Issue，而是看它在实现特定功能时的**能力边界**。

具体来说：

1. **细粒度能力检测**：FeatureBench 的功能级评测允许你看到 Agent 在处理特定代码修改类型时的表现差异。一个在整体解决率上 80% 的 Agent，在某个特定功能类型上可能只有 40%——这才是有意义的区分度。

2. **多 Agent 对比的标准界面**：Anthropic 的 blog 提到了 Claude Opus 4.5 在性能优化任务上的表现，但缺乏与其他 Agent 的系统性对比。FeatureBench 的 `fb infer` 支持 5 个主流 Agent 框架，提供了一个**统一的标准界面**来进行跨 Agent 能力对比。

3. **评测效率问题**：Anthropic 提到他们的 take-home 测试需要 2-4 小时完成，无法快速迭代。FeatureBench 的 fast split 在 Intel Xeon Platinum 8457C 上平均 57.2 秒/实例，这意味着可以在几分钟内完成一次完整的评测循环。

4. **数据驱动 vs 规则驱动**：Anthropic 的 v3 评估（Zachtronics 风格）通过设计 out-of-distribution 的约束来抵抗 AI。FeatureBench 的方法不同：通过**功能级数据生成**来创建足够多样的测试场景，使得 AI 难以通过记忆训练数据来通过评测。

---

## 技术实现细节

### 环境要求

根据 README：

- **uv**：Python 环境管理工具（Astral 出品，比 pip 更快）
- **Docker**：用于可复现的构建和评测
- **Fast split**：无需 GPU，Intel Xeon Platinum 8457C 上 57.2 秒/实例
- **Full split**：需要 GPU 资源

### 安装

```bash
# PyPI
pip install featurebench

# 本地
git clone https://github.com/LiberCoders/FeatureBench.git
cd FeatureBench
uv sync
source .venv/bin/activate
```

### 配置

```bash
cp config_example.toml config.toml
# 然后编辑 config.toml 配置 Agent 和模型
```

---

## 为什么值得关注

### 1. ICLR 2026 论文认证

FeatureBench 是被 ICLR 2026 接收的论文「FeatureBench: Benchmarking Agentic Coding for Complex Feature Development」的实现。这意味着它在学术上有足够的创新性，经过了同行评审。

### 2. 多 Agent 框架支持

README 明确列出了支持的 Agent：

> "including OpenHands, Claude Code, Codex, Gemini CLI, and mini-swe-agent"
> — [FeatureBench GitHub README](https://github.com/LiberCoders/FeatureBench)

这是目前最广泛的跨 Agent 评测支持之一，特别是 Claude Code 的官方支持意味着你可以用 FeatureBench 来做 Claude Code 的标准化评测。

### 3. 生产级评测效率

Fast split 的评测效率（57.2 秒/实例，无 GPU 要求）意味着 FeatureBench 可以用于：
- CI/CD 中的自动化评测
- 快速迭代的 Agent 开发
- 多版本对比评测（同一个测试集，不同 Agent 版本）

### 4. 数据生成能力

`fb data` 命令意味着 FeatureBench 不仅是一个评测工具，还是一个**评测数据的工厂**。对于需要创建自定义评测场景的团队，这是一个重要的能力。

---

## 与 SWE-bench 的对比

| 维度 | SWE-bench | FeatureBench |
|------|-----------|--------------|
| **评测粒度** | 任务级（整个 Issue） | 功能级（Feature-level） |
| **评测对象** | 能否解决 Issue | 能否实现特定功能 |
| **区分度** | 趋于饱和（74%+） | 细粒度区分 |
| **评测速度** | 较慢（需要完整解决） | Fast split ~57s/实例 |
| **GPU 要求** | 需要 | Fast split 不需要 |
| **数据生成** | 不支持 | 支持（`fb data`） |
| **多 Agent 支持** | 部分 | 5 个主流框架 |

---

## 使用场景

### 场景 1：Agent 开发迭代

当你开发一个新的 Agent 能力时，用 FeatureBench 的 fast split 快速评测效果。如果某个功能类型得分很低，说明需要改进这个方向。

### 场景 2：跨 Agent 对比

用统一的标准评测集对比 Claude Code vs Codex vs OpenHands 的能力分布。不是看谁解决率更高，而是看谁在哪些功能类型上更强。

### 场景 3：评估基准建立

用 `fb data` 为你的特定场景生成自定义评测数据，然后用 FeatureBench 的标准评测流程来评估 Agent。

---

## 限制与已知问题

根据 README：

- **hipporag 兼容性**：hipporag (2.0.0a3) 要求 openai==1.58.1，可能与最新 OpenAI 模型冲突
- **Leaderboard 网站**：还在 TODO list 中，目前没有公开的排行榜
- **Full split 需要 GPU**：完整的评测集需要 GPU 资源

---

## 总结

FeatureBench 解决了 AI 编程评估领域的一个核心问题：**当任务级评测趋于饱和时，如何保持评测的区分度**。

答案是：**从任务级转向功能级**。通过细粒度的功能级评测，FeatureBench 能够检测出 AI 在特定能力维度上的边界，而不只是给出「能否解决整个问题」的二元答案。

对于 Agent 开发者来说，FeatureBench 提供了：
- 统一的多 Agent 评测界面（支持 5 个主流框架）
- 高效的评测 pipeline（Fast split 无 GPU，57.2 秒/实例）
- 可扩展的数据生成能力（`fb data`）
- ICLR 2026 的学术认证

这与 Anthropic 的 AI-Resistant Evaluations 形成互补：Anthropic 回答了「如何设计 AI 无法完整解决的评估」，FeatureBench 回答了「如何在大规模标准评测中检测 AI 的能力边界」。

---

**一手来源**：
- [FeatureBench GitHub](https://github.com/LiberCoders/FeatureBench)（ICLR 2026 论文实现）
- 论文：[FeatureBench: Benchmarking Agentic Coding for Complex Feature Development](https://arxiv.org/abs/2602.10975)