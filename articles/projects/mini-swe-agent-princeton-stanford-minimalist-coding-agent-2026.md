# mini-SWE-agent：极简主义的胜利

> 当所有人都在构建复杂的 Agent 框架时，Princeton 和 Stanford 的研究团队问了一个更根本的问题：如果我们的 Agent 只需要 100 行代码，而且依然能在 SWE-bench 上拿下 74%——那过去一年我们到底在卷什么？

---

## 定位破题

**Target（谁该关注）**：想在 SWE-bench 上快速 baseline 任何模型能力的评测开发者 / 研究 Agent 极简可行性的架构师 / 需要 hackable 工具而非黑箱框架的一线工程师

**Result（带来了什么）**：100 行 Python 的 Agent，>74% SWE-bench verified 得分；冷启动速度远快于 Claude Code；任何模型只需替换 litellm 模型配置即可参与评测

**Insight（凭什么）**：用 bash 替代全部专用工具，让语言模型自己决定何时该用何种工具——2026 年的 LMs 已经足够强大，不需要人工设计工具接口

**Proof（谁来用）**：Meta、NVIDIA、Essential AI、IBM、Nebius、Anyscale、Princeton University、Stanford University；GitHub >19K Stars；SWE-bench 官方团队维护

> "In 2024, we built SWE-bench & SWE-agent and helped kickstart the coding agent revolution. We now ask: What if our agent was 100x simpler, and still worked nearly as well?"
> — [SWE-agent GitHub: mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)

---

## 体验式介绍

想象你需要快速测试一个新模型在真实代码修复任务上的能力。

**传统方案**：搭建 Claude Code 环境 → 配置 API key → 运行 → 等 3 分钟初始化

**mini-SWE-agent 方案**：
```bash
pip install mini-swe-agent
python -m minisweagent.run.hello_world --model gpt-4o --github-url https://github.com/org/repo --issue-number 123
```

你得到的是一个没有任何" Agent 框架包袱"的简单脚本。模型直接面对 bash shell，自己决定何时执行命令。没有特殊工具、没有状态机、没有工作流编排——只有模型、bash、和一个问题。

**这和 2024 年的 SWE-agent 完全不同**。那时的设计哲学是"模型不够强，需要专门设计的工具接口来弥补"：文件搜索工具、代码编辑工具、grep 工具、Git 操作工具……每个工具都是精心设计的 API。

但 2026 年的语言模型已经能自主完成这些操作——**专用工具变成了过度设计的负担，而非能力提升的来源**。

> "As LMs have become more capable, a lot of this is not needed at all to build a useful agent!"
> — [mini-SWE-agent README](https://github.com/SWE-agent/mini-swe-agent)

---

## 拆解验证

### 技术深度

mini-SWE-agent 的核心架构极度精简：

**Agent Class（约 100 行 Python）**：
```python
# 没有工具定义，没有状态机，没有特殊接口
class Agent:
    def run(self, messages, env):
        # 每一步：让 LM 决定执行什么 bash 命令
        # 执行命令，将 stdout/stderr 加入 messages
        # 重复直到任务完成或达到 max_steps
        return final_messages
```

**没有工具接口意味着**：不需要实现 `tool_call` 格式，不需要定义工具 schema，不需要解析工具返回结果。模型自己通过 bash 输出推断下一步行动。

**Linear History 设计**：每个 step 的 trajectory 和 messages 完全等价，没有隐式状态。这给调试和 fine-tuning 带来了根本性的便利：

> "Great for debugging & fine-tuning."
> — [mini-SWE-agent README](https://github.com/SWE-agent/mini-swe-agent)

**Stateless Shell Session**：每个 action 通过 `subprocess.run` 完全独立执行，不保持有状态的 shell 会话。这意味着：
- 切换沙箱环境只需把 `subprocess.run` 换成 `docker exec`
- 水平扩展只需并行运行独立进程
- 不会有 shell 状态泄漏导致的跨任务污染

> "This makes it trivial to execute the actions in sandboxes (literally just switch out subprocess.run with docker exec) and to scale up effortlessly."
> — [mini-SWE-agent README](https://github.com/SWE-agent/mini-swe-agent)

### 性能数据

| 模型 | SWE-bench Verified 得分 |
|------|----------------------|
| Gemini 3 Pro | >74% |
| Claude 3.7 | SOTA（结合 SWE-agent 1.0）|
| Mini（100 行）| >65%（基准版本）|

**关键洞察**：即使是最简版本（100 行，无特殊工具），也能让顶级模型在 SWE-bench 上发挥出接近完整的潜能。工具接口的缺失并没有显著拖累能力——这本身就是一个重要的研究结论。

### 竞品对比

| 项目 | 定位 | 代码量 | 工具设计 | 适用场景 |
|------|------|--------|----------|----------|
| **mini-SWE-agent** | 极简基线 | ~100 行 | 无（纯 bash）| 快速 baseline / 研究 / fine-tuning |
| **SWE-agent** | 全功能框架 | 中等 | 专用工具接口 | 需要完整工具能力的生产评测 |
| **Claude Code** | Production harness | 大型 | 完整工具生态 | 真实编码任务 |
| **Cursor Composer** | 编程辅助 | 大型 | 多工具集成 | IDE 集成 |

**差异化标签**：极简基线，hackable，无包袱

### 社区健康度

- **Stars**：>19K（2026）
- **维护者**：Princeton & Stanford SWE-bench 团队
- **用户**：Meta、NVIDIA、Essential AI、IBM、Nebius、Anyscale 等顶级研究机构和公司
- **文档**：完整 FAQ + 多个模型接入指南 + Codespaces 一键试用

---

## 行动引导

### 快速上手（3 步）

1. **安装**：`pip install mini-swe-agent`
2. **配置模型**：编辑 `~/.minisweagent/config.yaml` 或通过 `--model` 参数指定（支持 litellm/openrouter/portkey）
3. **运行**：
```bash
# 在 GitHub Issue 上测试模型
python -m minisweagent.run.hello_world --github-url https://github.com/org/repo --issue-number 123

# 本地 Docker 环境
python -m minisweagent.run.hello_world --github-url ... --environment docker
```

### 参与贡献

项目代码极度精简（100 行核心），非常适合：
- 研究极简 Agent 架构的可行性边界
- 尝试新的模型/提示词组合
- Fork 并添加自定义工具（当需要时）

### 持续关注

SWE-bench 团队已经将主要开发精力转移到 mini-SWE-agent 上。官方明确表示：

> "Our general recommendation is to use mini-SWE-agent instead of SWE-agent going forward."
> — [SWE-agent README](https://github.com/SWE-agent/swe-agent)

这意味着 mini-SWE-agent 将成为 SWE-bench 生态的核心工具，值得持续关注。

---

## 与文章的关联：极简主义对评测基础设施的启示

mini-SWE-agent 的极简哲学和本文"重新理解 Agent 评测"的主题形成了深层共鸣：

**Agent 评测的信噪比问题**：Anthropic 的研究指出，基础设施配置能造成 6 个百分点的分数差异。mini-SWE-agent 的线性历史和 stateless 执行提供了最干净的可复现评测环境——没有状态机、没有复杂 harness、没有隐藏状态，只有模型+bash+资源。

**工具复杂度的边界**：SWE-agent 2024 版的精心设计工具接口，在 2026 年的模型能力下变成了过度设计。这说明 Agent 架构复杂度不是越高越好——复杂度只有在模型能力不足时才必要。

**评测的本质**：mini-SWE-agent 证明了一个重要观点：在足够强的模型面前，Agent 架构可以极度精简，精简到只剩"把模型和 bash 连起来"。这与 Anthropic 的研究共同指向一个结论：**Agent 能力的主体是模型本身，框架只是载体**。

---

## 防重索引

- 已推荐项目 GitHub URL：`https://github.com/SWE-agent/mini-swe-agent`

---

*推荐来源：[mini-SWE-agent GitHub](https://github.com/SWE-agent/mini-swe-agent) | [官网](https://mini-swe-agent.com/latest/) | SWE-bench 官方团队*
