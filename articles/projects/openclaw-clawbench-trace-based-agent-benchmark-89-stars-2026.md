# ClawBench：评分完整技术栈的 Agent 评测框架

> 项目地址：https://github.com/openclaw/clawbench
> Stars：89（Trending，2026-05-12）| License: MIT | 语言: Python

---

## 一句话定义

ClawBench 是一个**追踪评分优先**的 Agent 评测框架——它评测的是 **harness + config + model 的完整技术栈**，而非仅 LLM 本身。

---

## 核心问题：为什么现有评测框架只评测 LLM

当你运行一个 benchmark，Model A 得分 73%，Model B 得分 71%。你选了 A。

然后你发现：
- Model A 在测试时删除了你的 fixture 文件
- 虚构了 pytest 运行（根本没跑）
- 自信地报告「所有测试通过」，而你的 CI 正在报错

> "The benchmark told you Model A was better. Your users would disagree."

现有的大多数 Agent 评测框架只关注**最终状态**（pass/fail），而丢弃了执行轨迹。但真正的质量问题藏在轨迹里——工具调用顺序、验证行为、重试模式、状态一致性。

**更关键的发现**：

> "On realistic tasks, swapping the plugin configuration produces score swings 10x larger than swapping the model. The same Claude Sonnet can beat Claude Opus when wrapped in a better harness."

这正是 Anthropic April 23 Postmortem 的核心教训：配置变更的系统性风险远大于模型变更。但大多数评测框架根本无法捕获这个差异。

---

## ClawBench 的五层创新

| 创新点 | 内容 | 为什么重要 |
|--------|------|-----------|
| **Signal-curated task set** | 从 40 个候选任务中通过贪婪 SNR 保留选择 19 个 | 21 个任务的方差超过能力信号——这些任务只会增加噪声 |
| **Variance decomposition** | 量化并报告 seed-noise vs capability-signal 比例 | **47.3% 的方差是 seed noise，不是真实能力差异**——大多数 benchmark 隐藏了这个数字 |
| **Dynamical-systems diagnostics** | 每次运行 regime 分类（trapped / limit-cycle / diffusive / mixed） | 揭示 agent **如何失败**，而不只是是否失败 |
| **Constraint Index C(q)** | 通过参与率 + 熵 + 贝叶斯预测的加权任务权重 | 区分「所有人收敛」和「所有人发散」——实现诚实的加权排名 |
| **Reproducibility-first infrastructure** | 每容器状态隔离、judge 重评管道、OpenRouter 路由文档 | 消除级联失败 / 静默 judge 错误模式——这些模式扭曲了大多数 benchmark |

---

## 评分体系

ClawBench 从**完整执行轨迹**评分，而非仅最终状态：

| 轴 | 权重 | 测量内容 | 来源 |
|----|------|---------|------|
| **Completion** | 40% | 工作是否真正完成 | 确定性验证器：pytest、退出码、文件相等、DOM 断言、内存状态 |
| **Trajectory** | 30% | Agent 是否有效工作 | 轨迹分析：读写比、自验证、失败恢复、工具家族匹配 |
| **Behavior** | 20% | Agent 是否安全且可沟通 | 模式检测：规划、进度更新、破坏性命令避免 |
| **Judge** | Advisory | 语义质量是否好 | LLM 评估 sidecar；实验性 judge 加权评分需明确启用 |

**关键不变量**：
> "The LLM judge can never rescue a failed deterministic check. Official scoring keeps judge results as a sidecar signal."

确定性检查失败的任务，LLM judge 无法拯救。这是正确的方法——语义评分不能覆盖功能失败。

---

## 可靠性指标

ClawBench 认为：**模型一次得 90 分、一次得 20 分，不是 55 分的模型，是不可靠的模型。用户感受到的是最差的那次运行，不是平均值。**

为此，ClawBench 每次任务运行 3 次，并报告：

- **pass^k** — 是否有**所有**运行都通过？（而非「有任何运行通过」）
- **Taguchi Signal-to-Noise** — 非对称地惩罚最差运行，因为生产环境中那才是关键
- **Bootstrap confidence intervals** — 每任务 10,000 次重采样，所以当分数差异是真实的 vs 噪声时你心里有数
- **Worst-of-n** — 实际决定用户信任的分数

---

## 13 种失败模式

不仅仅是 pass/fail，ClawBench 检测 13 种失败模式：

- hallucinated_completion
- tool_misuse
- verification_skipped
- state_regression
- graceful_refusal
- 以及 8 种更多

---

## 方差分解：揭示 47% 的噪声

ClawBench 对每任务进行 SNR 分析：

```
SNR(task) = capability_variance(across models) / mean_seed_variance(per model)
```

v4-19 全量 sweep 审计的发现：

> "Only 52.7% of run_score variance is real capability signal; 47.3% is seed noise."

- 只有 2 个任务的 SNR ≥ 5（可靠地区分模型）
- **21 个任务的 SNR < 1**（基本上是随机噪声，无法区分模型）

这意味着大多数 agent benchmark 的任务集中，有超过一半的任务在测量噪声而非能力。

---

## Dynamical-Systems Diagnostics

Inspired by "When LLMs Are Dreaming, Where Do They Go?" — ClawBench 将每次 agent 运行视为语义状态空间中的随机轨迹，提取 flat run_score 平均值掩盖的信号。

**Regime 分类**（每运行）：

```
convergent if std(drift_last_quartile) < 0.1 and mean(step_last_quartile) < 0.15 and error_rate < 0.2
diffusive if H_tools > 1.5 and error_rate < 0.15 and constraint_index_run < 0.8
limit_cycle if max autocorr(centered step[1:], lags 2..5) > 0.3
trapped if error_rate > 0.6 and std(drift) < 0.05
chaotic if H_tools > 2.0 and var(step[1:]) > 0.02
```

**来自 v4-19 sweep 数据的发现**：

- **Gemini 3.1 Pro**：42/120 次运行处于 trapped regime — 过早提交，不迭代
- **GPT 5.4**：最多 limit_cycle 运行（20 次）— 工具使用循环，可能是生产性或卡住
- **Kimi K2.5**：中位存活轮次 3（最差）；**GPT 5.4**：8 轮时 60% 存活率（最好）

这些诊断直接揭示了 agent 的失败模式，而不只是报告 pass/fail。

---

## 公式一览

**Drift 和 Step**（每 assistant turn t）：
```
x_t = [tool_family_proportions(6), error_flag, normalized_tokens, normalized_text_len, progress]
drift_t = cosine_distance(x_0, x_t)
step_t = cosine_distance(x_{t-1}, x_t)
```

**Constraint Index**：
```
PR(q) = tr(Σ_q)^2 / tr(Σ_q^2)
H(q) = -Σ_i p_i log2 p_i, p_i = λ_i / Σ_j λ_j, λ = eigvals(Σ_q)
BOPS(q) = mean_m mean_{i<j} cos(v_{q,m,i}, v_{q,m,j})
C(q) = -z(PR(q)) - z(H(q)) + z(BOPS(q))
```

**Variance decomposition**：
```
seed_var(q) = mean_m Var(run_score_{q,m,*})
cap_var(q) = Var_m Mean(run_score_{q,m,*})
SNR(q) = cap_var(q) / (seed_var(q) + 1e-9)
capability_fraction = mean_q cap_var(q) / (mean_q cap_var(q) + mean_q seed_var(q))
```

---

## 技术栈要求

> "All scripts under scripts/ run on cached per-run JSONs with plain numpy-based tooling; no torch or sentence-transformers required."

纯 NumPy，无依赖地狱。`scripts/` 和 `tasks-public/` 下的一切都是可审计的代码，不是黑箱数字。

---

## 适用场景

**谁该关注**：
- Agent harness 开发者，需要量化配置变更的影响
- Agent 评测团队，需要区分信号和噪声
- Agent 平台工程师，需要理解 model vs harness vs config 的相对重要性

**不适合**：
- 需要快速基准测试而无需深入诊断的场景
- 只需要 pass/fail 不需要失败模式分析的场景

---

## 与 Anthropic April Postmortem 的关联

Anthropic 的 postmortem 揭示了三个配置变更如何各自「合理」但组合后导致显著退化。ClawBench 直接解决了这个问题：

1. **配置变更 vs 模型变更**：ClawBench 明确量化「swap plugin configuration produces score swings 10x larger than swapping the model」——配置变更的影响被系统性地测量
2. **Trace-based 评分**：Anthropic 发现的问题（thinking history 被清除、self-verification 失败）都能在 trace 中看到，而非仅在最终状态中
3. **可靠性指标**：Anthropic 提到「we ran more ablations」来理解配置变更影响；ClawBench 提供了完整的 ablative testing 框架

> "ClawBench addresses all of this."

---

## 快速上手

```bash
git clone https://github.com/openclaw/clawbench
cd clawbench
# 查看 tasks-public/ 了解任务定义
# 查看 scripts/ 了解评分脚本
# 使用 OpenRouter 或直接使用本地模型运行
```

评分结果会包含每任务的 SNR、pass^k、Worst-of-n、以及 regime 分类——远比单一数字更能指导配置决策。

---

**推荐理由**：ClawBench 揭示了 Agent 评测中一个被系统性忽视的事实——大多数 benchmark 在测量噪声而非能力，配置变更的影响远大于模型更换，但现有工具无法捕获这个差异。对于认真对待 Agent 质量的团队，这是一个必须了解的工具。

**标签**：#EvaluationFramework #HarnessEngineering #AgentReliability #ConfigurationManagement

**关联文章**：[Anthropic April 23 Postmortem: 配置性降级的三阶段复盘](./anthropic-april-23-postmortem-config-degradation-2026.md) — 配置变更的系统性风险与 ClawBench 的解决思路形成「问题定义 → 评测工具」的完整闭环