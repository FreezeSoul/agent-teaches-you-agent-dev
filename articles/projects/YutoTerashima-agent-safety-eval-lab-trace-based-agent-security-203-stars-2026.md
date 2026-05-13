# YutoTerashima/agent-safety-eval-lab — Agent Trace 安全评测框架

> **Target**：有 Python 经验的 Agent 开发者，需要对工具调用安全、trace 质量、风险评估建立量化标准的团队
> **Result**：将 Agent 的安全评估从「单点 prompt 测试」升级为「可复现的轨迹级评测」，支持 Mock/Real 多模式_adapter 架构
> **Insight**：Agent 失败是 workflow 失败，不是单条消息失败——评测必须捕获完整轨迹才能发现工具政策边界越界的累积效应
> **Proof**：203 Stars，50k 样本 V2 benchmark，PKU-Alignment/BeaverTails 50k 评测集成，RTX 5090 GPU 加速实验

---

## Positioning（定位破题）

**一句话定义**：可复现的 Agent trace 级别安全评测框架，评估 LLM Agent 在工具调用过程中的政策边界遵守情况。

**场景锚定**：当你需要回答「这个 Agent 在什么情况下会调用危险工具？它的 trace 是否有 pattern 可以预测风险？」时，你需要这个框架。

**差异化标签**：**轨迹级评测**——不是测单条回复对错，而是测完整工具调用链的累积风险。

---

## Sensation（体验式介绍）

当你用传统的 prompt 注入测试框架测 Agent 时，你只能得到「这条 prompt 有没有骗过模型」的二元答案。

但 Agent-Safety-Eval-Lab 告诉你：**Agent 的失败是 workflow 失败，不是单条消息失败**。

```python
# 核心评测循环
cases=3 passed=2 failed=1 high_risk=1
C-002: fail | tool_policy_violation | blocked_tool=file.delete
```

这个输出揭示了什么？模型在某个中间步骤尝试调用了 `file.delete`，被 policy 拦截了。如果只看最终输出，你可能以为「任务失败了」；但通过 trace，你能看到**失败发生在哪个工具调用上、为什么被拦截**。

这就像调试微服务时看 distributed trace——单点日志不够，需要端到端的调用链。

---

## Evidence（拆解验证）

### 技术深度

**Trace Recorder**：捕获 agent 的完整消息历史、工具调用、policy 判断结果。适配 Mock/LiteLLM/OpenAI 多后端，结果格式统一为 `AgentTrace`。

**Tool Policy Grader**：评估每个工具调用是否越界。关键词规则（rule_safety_keywords）可以达到高安全召回，但在 unsafe recall 上表现差——这是因为简单 blocklist 只能检测已知威胁，无法识别新型攻击模式。

**Safety Rubric Grader**：基于 BeaverTails 真实风险数据训练的风险分类器。V2 实验结果显示：word TF-IDF logistic baseline 是最强分类器，macro-F1 约 0.774，AUROC 约 0.859。

**关键发现**：
- GPU MLP over TF-IDF features 增加 unsafe recall（0.879），但 precision 下降，需要校准才能用于生产
- keyword rule 有高安全召回但漏掉很多 unsafe case——这正是 trace-aware grading 存在的理由

### 架构设计

```
Eval Case → Mock/Model Adapter → Agent Trace Recorder → Tool Policy Grader
                                                      → Safety Rubric Grader
                                                      → Risk Report
```

Adapter 是可插拔的——任何返回 `AgentTrace` 的实现都可以接入评测schema。这让框架可以从 Mock 模式切换到真实模型评估，无需修改评测逻辑。

### 社区健康度

- 203 Stars（2026-05-01 创建，12天）
- 包含完整的 V2 research suite，50k 样本量
- 集成 BeaverTails 50k 评测数据
- GPU 加速实验（RTX 5090）

---

## Threshold（行动引导）

### 快速上手

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e ".[dev]"
python examples/run_mock_eval.py
pytest
```

### 核心命令

```bash
# 运行 demo
python -m agent_safety_eval_lab.cli run-demo

# 回放 trace 并评估
python -m agent_safety_eval_lab.cli replay examples/traces --out reports/replay_results.json

# GPU 加速完整 benchmark
conda run -n Transformers python scripts/run_matrix.py --device cuda --profile full
```

### 适用扩展

如果你想将这个框架集成到自己的 Agent 项目，你需要：
1. 实现一个返回 `AgentTrace` 的 Adapter（对应你的 Agent Runtime）
2. 定义 Tool Policy（哪些工具是危险的、需要拦截的）
3. 选择 Rubric Grader（关键词/TF-IDF/MLP）

---

## 关联闭环

**主题关联**：Cursor Agent Harness 文章揭示「测量驱动的质量迭代」——Cursor 通过 Keep Rate + 用户满意度信号 + 工具错误率监控实现数据驱动的质量改进。

**闭环逻辑**：Cursor 测量的是「功能质量」（代码保留率、用户满意度）；agent-safety-eval-lab 测量的是「安全质量」（工具政策遵守、trace 累积风险）。两者共同构成 Agent 评测的完整坐标：功能对不对 + 安全有没有越界。

> "Agent failures are often workflow failures, not single-message failures. A useful evaluation needs to inspect the trajectory."
> — [YutoTerashima/agent-safety-eval-lab README](https://github.com/YutoTerashima/agent-safety-eval-lab)

---

**引用来源**：
- [GitHub: YutoTerashima/agent-safety-eval-lab](https://github.com/YutoTerashima/agent-safety-eval-lab)
- [README: experiment results and V2 research suite](https://github.com/YutoTerashima/agent-safety-eval-lab/blob/main/reports/agent_safety_v2_research_report.md)
- [Dataset: BeaverTails integration](https://github.com/YutoTerashima/agent-safety-eval-lab/blob/main/datasets/external/beavertails_feature_sample.jsonl)