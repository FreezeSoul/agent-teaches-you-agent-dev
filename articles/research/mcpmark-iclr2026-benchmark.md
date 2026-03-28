# MCPMark：压力测试真实 MCP 工作流的 ICLR 2026 基准

> **本质**：首个针对 MCP 协议在真实多工具场景下进行系统性压力测试的评测基准（127 任务，5大平台，揭示当前最强模型仍有近半数任务无法完成）

---

## 一、基本信息

| 属性 | 值 |
|------|------|
| **论文** | MCPMark: A Benchmark for Stress-Testing Realistic and Comprehensive MCP Use |
| **会议** | ICLR 2026（Poster，#20592）|
| **作者** | eval-sys |
| **GitHub** | https://github.com/eval-sys/mcpmark |
| **官网** | https://mcpmark.ai |
| **发表** | 2026年1月26日 |
| **修改** | 2026年2月28日 |
| **核心贡献** | 127 个高质量任务，覆盖 5 种 MCP 服务器（Notion/GitHub/Filesystem/PostgreSQL/Playwright），带自动化验证脚本 |

---

## 二、为什么需要 MCPMark

### 现有 MCP 基准的局限性

论文指出现有 MCP 基准存在三大缺陷：

1. **Read-heavy 偏重**：大多数基准偏向读取操作，缺乏完整的 CRUD 压力
2. **交互深度不足**：任务步骤有限，无法模拟真实复杂工作流
3. **平台覆盖窄**：通常只测试 1-2 个 MCP 服务器，缺乏跨平台对比

### MCPMark 的设计目标

MCPMark 填补以下空白：
- 真实初始状态（curated initial state）+ 可编程验证脚本（programmatic verification script）
- 要求多样化 CRUD 操作
- 要求更丰富的环境交互（不仅是读，还有创建、更新、删除）
- 多 MCP 服务器横向对比

---

## 三、任务设计

### 覆盖的 MCP 服务器

| MCP 服务器 | 任务类型 | 代表场景 |
|-----------|---------|---------|
| **Notion** | 页面创建/编辑/查询/归档 | 知识库管理 |
| **GitHub** | Issue/PR/代码/审查 | 开发协作 |
| **Filesystem** | 文件读写/移动/属性 | 本地操作 |
| **PostgreSQL** | SQL 查询/数据操作/事务 | 数据库管理 |
| **Playwright** | 浏览器自动化/GUI 操作 | Web 交互 |

### 任务规模

- **127 个标准任务**（每个 MCP 服务器 20+ 任务）
- 另有 **50 个 easy 任务**（每服务器 10 个，适合小模型快速测试）
- 任务由领域专家和 AI Agent 协作创建

### 评测方式

```bash
# 标准任务（需要外部账号）
python -m pipeline \
  --mcp filesystem \
  --k 1 \
  --models gpt-5 \
  --tasks all

# Easy 任务（无需外部账号，适合 CI）
python -m pipeline --mcp filesystem --tasks all --task-suite easy

# 支持 ReAct agent scaffold
python -m pipeline --mcp notion --tasks all --agent react
```

- **隔离沙箱**：不污染真实账号/数据
- **自动重试**：失败任务自动恢复和续接
- **统一指标**：pass@k, avg@k，自动聚合报告

---

## 四、核心评测结果

### 标准基准（127 任务）

| 模型 | Pass@1 | Pass@4 | 平均 Turn 数 | 平均工具调用数 |
|------|--------|--------|------------|--------------|
| **GPT-5-Medium** | **52.56%** | **33.86%** | 16.2 | 17.4 |
| **Claude Sonnet 4** | <30% | <15% | — | — |
| **o3** | <30% | <15% | — | — |
| Gemini-3-Pro-Preview | 50.6% ± 2.3% | — | — | — |
| GPT-5-High | 51.6% | — | — | — |
| DeepSeek-V3.2-Think | 36.8% | — | — | — |
| DeepSeek-V3.2-Chat | 29.7% | — | — | — |

> **关键洞察**：即使是最强模型 GPT-5-Medium，在标准 127 任务下仍有 **近半数失败**（47.44%）。Pass@4 仅为 33.86%，说明多次尝试并不能稳定解决复杂 MCP 任务。

### Easy 基准（50 任务）

- 专为小模型设计，降低门槛
- GitHub easy 任务已发布

### MCPMark 上各开源模型排名（标准测试）

| 排名 | 模型 | Pass@1 | 备注 |
|------|------|--------|------|
| 🥇 | **Qwen-3-Coder-Plus** | 最高开源 | 最佳开源代码模型 |
| 🥈 | DeepSeek-V3.2 | 36.8% (think) / 29.7% (chat) | 思维链版本明显更强 |
| — | GPT-5 系列 | 51-52% | 闭源模型领先 |

### 关键数字

- **16.2 turns**：平均每个任务需要的对话轮数
- **17.4 tool calls**：平均每个任务的工具调用次数
- **127 tasks**：标准测试集规模
- **5 platforms**：覆盖的 MCP 服务器数量

---

## 五、与 GAIA/OSWorld 的关系

MCPMark 与本库已有的 GAIA/OSWorld 基准文章形成互补，定位不同：

| 维度 | GAIA | OSWorld | **MCPMark** |
|------|------|---------|------------|
| **核心焦点** | 通用 AI 助手 | 计算机操作 Agent | **MCP 协议工具调用** |
| **协议** | 自由工具选择 | 任意工具 | **MCP 标准化接口** |
| **任务类型** | 多领域知识问答 | OS 级 GUI 操作 | **Notion/GitHub/DB 等 CRUD** |
| **评测对象** | 模型+工具系统 | 模型+OS+浏览器 | **模型+MCP 服务器** |
| **验证方式** | 最终答案可验证 | 截图对比 | **自动化脚本验证** |
| **最新成绩** | GPT-5/o3 达 90.37% | 多种模型对比 | **GPT-5-Medium 52.56%** |

**核心区别**：GAIA 评测 Agent 的"整体能力"（可自由选择工具），MCPMark 专门评测 **MCP 协议接口的完整性和鲁棒性**——即 Agent 与标准化 MCP 服务器交互时的实际表现。

---

## 六、ReAct Agent 支持

MCPMark v13（2025年10月）新增了 ReAct agent scaffold：

```bash
python -m pipeline \
  --mcp filesystem \
  --tasks all \
  --agent react \
  --models MODEL
```

PR 欢迎添加新的 agent scaffold，形成框架无关的评测对比。

---

## 七、局限性与未来方向

### 当前局限

1. **GPT-5-Medium 仅 52.56%**：即使最强模型也无法完成近半数任务，说明 MCP 工作流复杂度远超单步工具调用
2. **仅 5 个 MCP 服务器**：Notion/GitHub/Filesystem/PostgreSQL/Playwright，尚未覆盖 Search/Memory/其他 MCP
3. **账号依赖**：标准任务需要 Notion/GitHub 等外部服务账号，easy 任务可无账号运行
4. **版本控制挑战**：MCP 服务器版本更新可能导致基准不一致（已固定版本：GitHub MCP v0.15.0，Notion MCP @1.9.1）

### 未来方向

- 更多 MCP 服务器覆盖（Slack/MCP、Database MCP 等）
- 更大规模任务集（目标 500+ 任务）
- 攻击安全性评测（结合 MSB MCP Security Benchmark）

---

## 八、相关研究

| 论文 | 会议 | 核心贡献 |
|------|------|---------|
| **MCPMark**（本文）| ICLR 2026 | MCP 压力测试基准 |
| **OSWorld-MCP** | ICLR 2026 | 计算机使用 Agent MCP 工具调用评测 |
| **MCP-Bench** | ICLR 2026 | 多步真实世界任务 MCP 评测 |
| **MSB**（MCP Security Benchmark）| ICLR 2026 | MCP 安全攻击评测（攻击防御）|
| **GAIA** | — | 通用 AI 助手评测（本库已有）|
| **OSWorld** | — | 计算机操作 Agent 评测（本库已有）|

---

## 九、参考资料

- 论文：https://openreview.net/forum?id=uobROwBsJm
- GitHub：https://github.com/eval-sys/mcpmark
- 官网：https://mcpmark.ai
- MCPMark Leaderboard：https://mcpmark.ai/leaderboard

---

## 十、一句话总结

> MCPMark 揭示了当前最强模型在真实 MCP 工作流下仍有近半数任务失败——GPT-5-Medium 仅 52.56% Pass@1，平均每任务 16.2 轮对话、17.4 次工具调用，MCPMark 成为评估 Agent 与 MCP 服务器交互能力的关键基准。

---

*相关演进阶段：Stage 6 (Tool Use) → Stage 8 (Deep Research) | 属于 Deep Research 评测体系*
