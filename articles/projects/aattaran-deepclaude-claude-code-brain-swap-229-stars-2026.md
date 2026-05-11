# deepclaude：Ai Coding Agent 的「脑身分离」经济 学

> **Target**：在寻找将 Claude Code 成本从 $200/月 降至 ~$20/月 方案、有一定动手能力的开发者；或者对「不同模型在不同任务上有各自优势」有认知、想要灵活切换的 Agent 开发者。
>
> **Result**：日常任务使用 DeepSeek V4 Pro（$0.87/M output tokens vs Claude Opus $15/M），成本降低 75-90%；复杂推理任务秒级切换回 Claude Opus。
>
> **Insight**：Claude Code 的核心价值不在于 Claude 模型本身，而在于它精心调校的 tool loop（Agent Body）——brain 是可以替换的。DeepSeek V4 Pro 在 LiveCodeBench 取得 96.4% 分数，足够cover 80% 的日常任务。
>
> **Proof**：GitHub 229 Stars，2026-05-03 创建，五天内达到 229 Stars。DeepSeek V4 Pro 官方定价 $0.87/M output tokens，自动上下文缓存使 Agent 循环成本降至 $0.004/M（重复turns）。

---

## P - Positioning（定位破题）

Claude Code 是目前最好的自主编码 Agent，但 $200/月的固定费用对于个人开发者和小团队来说是一笔不小的开支。更关键的是：Claude Code 的价值并不只在于 Claude 模型——它真正值钱的是精心调校的 tool loop（文件编辑、bash 执行、子 Agent 生成、多步骤循环）。

**deepclaude 的核心洞察**：把 Claude Code 的 Body（工具循环）当作常数，只换 Brain（模型）。DeepSeek V4 Pro 在 LiveCodeBench 96.4% 的分数意味着它能handle 绝大多数日常编码任务，而只有 20% 的复杂推理场景需要 Claude Opus 出马。

> "Claude Code is the best autonomous coding agent — but it costs $200/month with usage caps. DeepSeek V4 Pro scores 96.4% on LiveCodeBench and costs $0.87/M output tokens. **deepclaude swaps the brain while keeping the body.**"

---

## S - Sensation（体验式介绍）

你现在的日常工作流可能是这样：

```
上午：用 Claude Code 写一个 REST API（$3 token 费用）
中午：用 Claude Code 重构一个工具类（$2 token 费用）
下午：用 Claude Code 调试一个诡异的 race condition（$5 token 费用）
月底：一算，Claude Max $200 刚好用完
```

用了 deepclaude 之后：

```bash
# 日常任务走 DeepSeek，便宜到可以忽略成本
$ deepclaude --backend ds
正在启动 Claude Code + DeepSeek V4 Pro...
# 你的工具循环完全一样，只是模型换成了 DeepSeek

# 遇到硬骨头，1秒切回 Claude Opus（不用重启，不用开新窗口）
deepclaude --switch opus
正在切换至 Claude Opus...
```

你的 terminal 体验完全不变——同样的文件编辑、同样的 bash 执行、同样的 subagent 机制。**唯一变化的是 API 账单上的数字**。

> "Switch between Anthropic and DeepSeek mid-session — from inside Claude Code itself. No restart, no terminal commands. Just type a slash command."

---

## E - Evidence（拆解验证）

### 技术实现原理

deepclaude 通过设置环境变量来实现 brain 替换：

| 环境变量 | 控制什么 |
|---------|---------|
| `ANTHROPIC_BASE_URL` | API 端点（DeepSeek API 而不是 Anthropic API）|
| `ANTHROPIC_AUTH_TOKEN` | API Key |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus 级别任务的模型 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 级别任务的模型 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | 子 Agent 使用的模型 |

deepclaude 在启动时设置这些变量指向 DeepSeek/OpenRouter/Fireworks，Launch Claude Code，然后退出时恢复原设置。**完全不修改 Claude Code 本身**，只是改变了它通信的对象。

### 成本对比

| 使用级别 | Anthropic Max | deepclaude (DeepSeek) | 节省 |
|---------|--------------|----------------------|------|
| 轻度（10天/月）| $200/月 | ~$20/月 | 90% |
| 重度（25天/月）| $200/月 | ~$50/月 | 75% |
| 带自动循环 | $200/月（被 cap）| ~$80/月 | 60% |

DeepSeek 的自动上下文缓存是关键——首次请求后，系统提示和文件上下文被缓存，重复 turns 成本降至 $0.004/M。这使得 Agent 循环的边际成本几乎为零。

### 能力边界

> "Routine tasks (80% of work): DeepSeek V4 Pro is comparable to Claude Opus"
> "Complex reasoning (20%): Claude Opus is stronger — switch with `--backend anthropic`"

| 功能 | 状态 | 原因 |
|------|------|------|
| 文件读写编辑 | ✅ | DeepSeek 完全支持 |
| Bash/PowerShell 执行 | ✅ | Claude Code CLI 本身处理 |
| 多步骤自主循环 | ✅ | Agent loop 在 CLI 层，不在 API 层 |
| 子 Agent 生成 | ✅ | 同上 |
| 图像/视觉输入 | ❌ | DeepSeek Anthropic endpoint 不支持图像 |
| MCP Server 工具 | ❌ | 兼容层不支持 |
| 并行工具使用 | ⚠️ | DeepSeek 支持 128/ call，但 Claude Code 默认串行发送 |
| 提示缓存 | ⚠️ | DeepSeek 有自己的缓存机制（自动），但忽略 Anthropic `cache_control` |

### 与 Cursor/Anthropic 的架构关联

这个"brain-swappable"的思路和 Cursor 的 multi-model harness 定制化以及 Anthropic 的 Managed Agents Brain/Hands 解耦形成了有趣的呼应：

- **Anthropic**：明确提出 Brain/Hands 分离，Brain 是推理引擎，Hands 是执行环境
- **Cursor**：为每个模型定制 tool format（patch vs string replacement），但 harness 本身是模型无关的
- **deepclaude**：把模型选择变成了 runtime 配置，证明了 tool loop（Body）的可移植性

deepclaude 的存在本身就是一个实证：Claude Code 的 harness 价值（tool loop）确实独立于它内置的 Brain（Claude 模型）。当你想要换 Brain 时，Body 完全可以继续工作。

---

## T - Threshold（行动引导）

### 快速上手

```bash
# 1. 获取 DeepSeek API key（$5 足够用很久）
# 2. 安装
chmod +x deepclaude.sh
sudo ln -s "$(pwd)/deepclaude.sh" /usr/local/bin/deepclaude

# 3. 设置 key
export DEEPSEEK_API_KEY="sk-your-key-here"

# 4. 启动
deepclaude

# 5. 遇到复杂推理问题时
deepclaude --switch anthropic
```

### 适合人群

- **有成本意识的个人开发者**：不需要为 80% 的日常任务付 Claude Opus 的价格
- **需要灵活切换模型的 Agent 开发者**：理解不同模型在不同任务上的优势
- **想测试不同模型在实际编码任务上表现的开发者**：同样的 tool loop，不同的 brain，方便做对照实验

### 不适合人群

- 需要视觉输入的编码任务（DeepSeek endpoint 不支持图像）
- 依赖 MCP Server 的工作流
- 需要在单个会话内混合使用不同模型处理同一任务（deepclaude 是会话级切换，不是 turn 级）

---

## 关联主题

本文与以下文章形成「Harness 抽象层」的知识互补：

- **Anthropic Managed Agents（Brain/Hands/Session 三元组）**：Session 是外部化记忆，Brain 是推理引擎——deepclaude 用环境变量实现了类似的概念解耦，把 Brain（模型）从 CLI 层抽象出去
- **Cursor Harness 持续改进工程**：Cursor 为每个模型定制 tool format，deepclaude 则把模型选择变成了 runtime 开关——两种思路都在回答"如何让 harness 适配不同模型"
- **Prompt Tower（上下文打包）**：两者都在解决"上下文管理"问题，但角度不同——Prompt Tower 解决的是输入端上下文的组织和压缩，deepclaude 解决的是推理引擎的灵活选择

---

## 参考文献

- [deepclaude GitHub](https://github.com/aattaran/deepclaude) — 项目首页，README 原文引用
- [DeepSeek Platform Pricing](https://platform.deepseek.com) — DeepSeek API 官方定价
- [LiveCodeBench](https://livecodebench.github.io) — DeepSeek V4 Pro 96.4% 评测来源