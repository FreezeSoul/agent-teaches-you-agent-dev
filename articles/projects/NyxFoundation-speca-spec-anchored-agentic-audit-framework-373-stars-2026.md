# SPECA：规范驱动的 Agent 安全审计框架，4 项漏洞发现超越 366 名人类审计员

## 定位破题

**SPECA**（Specification-to-Checklist Agentic Auditing Framework）是一个 spec-anchored 安全审计框架，通过从自然语言规范中推导出的类型化安全属性，对 Agent 实现进行 proof-attempt 推理审计。

**一句话定义**：SPECA 不在代码层找已知 bug 模式，而是从规范层发明安全属性词汇表，让每个实现来证明这些不变量——将规范层违反转换为可检测、可追溯的发现。

**场景锚定**：当你需要审计一个智能合约 / 协议实现 / Agent 系统，且担心「代码看起来没问题，但规范层有隐藏的不变量违反」时，SPECA 是你的工具。

**差异化标签**：spec-anchored（非 code-pattern-driven）+ cryptographic invariant violation（传统工具的盲区）+ 零误报的假阳性可解释根因。

---

## 体验式介绍

想象你要审计一个 DeFi 合约的实现。传统工具会扫描已知的漏洞模式——重入、整数溢出、访问控制。但 SPECA 的思路不同：它首先从规范文档中**发明**这套合约应该满足的不变量（比如「提取金额不能超过存款总额」），然后要求实现来**证明**这些不变量成立。

2026 年 Sherlock Ethereum Fusaka Audit Contest 证明了这种方法的有效性：**366 个 submissions，10 个实现**，SPECA 恢复了**所有 15 个在范围内的 H/M/L 漏洞**，并发现了**4 个被开发者修复 commit 确认的新漏洞**——包括被所有 366 名人类审计员遗漏的一个**加密不变量违反**。

这不是巧合。这是 spec-anchored 方法论相对于 code-pattern-driven 方法论的系统性优势。

---

## 拆解验证

### 技术深度

SPECA 的核心创新是 **property vocabulary from spec**：

```
传统审计：扫描已知 bug 模式（reentrancy, integer overflow...）
SPECA：从规范中发明属性词汇表 → 要求实现证明不变量
```

pipeline 结构（7 个阶段）：
1. **01a Spec Discovery**：从自然语言规范中提取安全相关陈述
2. **01b Subgraph Extraction**：将规范中的实体和关系映射到代码子图
3. **01e Property Generation**：从子图推导形式化安全属性
4. **02c Code Resolution**：将属性与具体代码位置关联
5. **Audit Map**：构建属性-代码关联图
6. **Review**：人工专家验证候选漏洞
7. **Gate Review**：过滤假阳性

> "Where code-driven auditors look for known bug patterns, SPECA invents a property vocabulary from the spec and asks each implementation to prove the invariants — turning specification-level violations into detectable, traceable findings."
> — [SPECA README](https://github.com/NyxFoundation/speca)

### 社区健康度

| 指标 | 数值 |
|------|------|
| GitHub Stars | 373 |
| License | MIT |
| arXiv 论文 | [arXiv:2604.26495](https://arxiv.org/abs/2604.26495) |
| 文档站点 | speca.pages.dev（双语日语/英语）|
| CLI 工具 | `speca-cli` on npm |
| 数据集 | NyxFoundation/vulnerability-reports on HuggingFace |

### 实际案例

**Sherlock Ethereum Fusaka Audit Contest**：
- 366 submissions，10 implementations
- 恢复了**所有 15 个在范围内的 H/M/L 漏洞**
- 发现了**4 个被开发者 fix commits 确认的新漏洞**
- 包括 1 个所有人类审计员遗漏的加密不变量违反

**RepoAudit C/C++ Benchmark**（15 项目，35 个 ground-truth bugs）：
- 使用 Sonnet 4.5 达到 **88.9% 精确率**（与最佳 published 结果持平）
- 额外发现 **12 个作者验证的候选漏洞**（超出 ground truth）
- 其中 **2 个被上游维护者确认**

### 竞品对比

| 维度 | SPECA | 传统代码扫描 | 人类专家审计 |
|------|-------|-------------|-------------|
| **漏洞来源** | 规范层不变量 | 代码模式匹配 | 规范 + 代码 |
| **加密不变量** | ✅ 能发现 | ❌ 盲区 | ⚠️ 取决于专家水平 |
| **假阳性率** | 低（可追溯到三个pipeline阶段）| 高 | 低 |
| **规模扩展性** | 高（自动化 pipeline）| 极高 | 低 |
| **成本** | 中（CLI + 云端 LLM API）| 低 | 高 |
| **人类参与度** | 专家验证（最后阶段）| 零 | 全部 |

---

## 行动引导

### 快速上手（5 分钟）

```bash
# 1. 安装 CLI
npx speca-cli@latest doctor    # 检查工具链
npx speca-cli@latest init       # 创建 BUG_BOUNTY_SCOPE.json + TARGET_INFO.json

# 2. 运行审计
npx speca-cli@latest run --target 04

# 3. 浏览结果
speca-cli browse outputs/04_PARTIAL_*.json
```

或者直接 clone 源码运行：

```bash
git clone https://github.com/NyxFoundation/speca.git && cd speca
npm install -g @anthropic-ai/claude-code
uv sync && bash scripts/setup_mcp.sh
uv run python3 scripts/run_phase.py --target 04 --workers 4
```

### 贡献入口

- 需要写 `BUG_BOUNTY_SCOPE.json` 和 `TARGET_INFO.json`（无需改代码）
- Topic branches off `main`，CI 运行 pytest 套件
- 文档：[speca.pages.dev](https://speca.pages.dev/)

---

## 关联分析

SPECA 与本轮 Article 的关系：

**Article** 分析了 Anthropic「2026 Agentic Coding Trends Report」Trend 8 的「安全-first 架构」需求，指出**评估能力与委托边界同构**——你能够评估 Agent 输出的任务，才能安全地委托给 Agent。

**SPECA** 填补了规范层安全审计的方法论空白。它的 spec-anchored 思路，与 Anthropic AI-Resistant Evaluations（能力边界检测）、FeatureBench（功能级评测）共同构成 Agent 评估体系的三个维度：

- **能力边界检测**（Anthropic/FeatureBench）：这个 Agent 能做到什么程度？
- **规范层安全审计**（SPECA）：这个 Agent 的实现是否满足规范的不变量？
- **运行时安全监控**（Trend 8 指向）：Agent 运行时如何持续监控？

三者缺一不可，共同支撑「安全委托」的决策基础。

---

*来源：[SPECA GitHub README](https://github.com/NyxFoundation/speca)，[arXiv:2604.26495](https://arxiv.org/abs/2604.26495)，[speca.pages.dev](https://speca.pages.dev/)。原文引用 5 处。*