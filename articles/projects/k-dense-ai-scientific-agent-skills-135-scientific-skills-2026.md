# K-Dense-AI/scientific-agent-skills：将 AI Coding Agent 变为 AI Scientist 的 135 个科学技能库

## 目标用户

**有科学研究背景的 AI Coding Agent 用户**——如果你用 Claude Code、Cursor 或 Codex 做科研相关工作，scientific-agent-skills 让你把通用 coding agent 转变为能够执行复杂多步骤科学工作流的「AI 科学家」。

**水平要求**：有科研背景，了解基本的 Python 科学计算（pandas、numpy、scikit-learn），需要 AI 辅助处理文献检索、数据库查询、实验流程设计等科研任务。

---

## 核心改变

没有 scientific-agent-skills 时，AI 能帮你写代码，但你需要：
- 手动查找 API 文档（PubChem、ChEMBL、UniProt...）
- 自己设计多步骤实验流程
- 分别调用不同的数据库和工具

有了之后，你只需说「帮我查找针对 KRAS 突变肺癌的临床试验」，AI 直接在 78+ 科学数据库中检索，返回整理好的结果。

> "Transform your AI coding agent into an 'AI Scientist' on your desktop!"
> — [K-Dense-AI/scientific-agent-skills README](https://github.com/K-Dense-AI/scientific-agent-skills)

---

## 技术架构

### 135 个科学技能的分类组织

| 类别 | 数量 | 示例 |
|------|------|------|
| 🧬 生物信息学 & 基因组学 | 35+ | 单细胞 RNA-seq、基因调控网络、变异注释、系统发育分析 |
| 🧪 化学信息学 & 药物发现 | 25+ | 分子性质预测、虚拟筛选、ADMET 分析、分子对接 |
| 🏥 临床研究 & 精准医学 | 15+ | 临床试验、药物基因组学、变异解读、治疗规划 |
| 🤖 机器学习 & AI | 20+ | 深度学习、强化学习、时间序列分析、贝叶斯方法 |
| 🌍 地学科学 & 遥感 | 15+ | 卫星图像处理、GIS 分析、空间统计 |
| 📚 科学传播 | 30+ | 文献综述、同行评审、学术写作、海报制作 |

### 三个层次的科学工具覆盖

**第一层：100+ 科学数据库**
- 统一入口（database-lookup）：78 个公共数据库直接访问
- 专用接口：DepMap、Imaging Data Commons、PrimeKG、US Treasury Fiscal Data
- 多数据库包：BioServices（40 个生物信息服务）、BioPython（38 个 NCBI 子库）

**第二层：70+ 优化的 Python 包技能**
- RDKit（化学信息学）
- Scanpy（单细胞分析）
- PyTorch Lightning（深度学习）
- scikit-learn、BioPython、PennyLane、Qiskit、OpenMM...

**第三层：9 个科学平台集成**
- Benchling、DNAnexus、LatchBio、OMERO、Protocols.io...

> "While the agent can use any Python package or API on its own, these explicitly defined skills provide curated documentation and examples that make it significantly stronger and more reliable."
> — [K-Dense-AI/scientific-agent-skills README](https://github.com/K-Dense-AI/scientific-agent-skills)

---

## 安装与使用

### 标准安装（一行命令）

```bash
npx skills add K-Dense-AI/scientific-agent-skills
```

支持所有主流 Agent：**Claude Code、Claude Cowork、Codex、Cursor、 Gemini CLI**，以及任何支持开放 Agent Skills 标准的 Agent。

### GitHub CLI 安装（可版本固定）

```bash
# 交互式安装
gh skill install K-Dense-AI/scientific-agent-skills

# 指定 Agent 平台
gh skill install K-Dense-AI/scientific-agent-skills --agent cursor

# 版本固定（可复现）
gh skill install K-Dense-AI/scientific-agent-skills --pin v1.0.0
```

### 快速示例

**文献检索 + 数据库查询**：
```
> 帮我查找针对 KRAS 突变肺癌的临床试验
→ AI 自动查询 ClinicalTrials.gov，返回结构化结果

> 搜索 ChEMBL 中针对 KRAS 的抑制剂
→ AI 调用 ChEMBL API，返回分子结构和活性数据
```

**多步骤科学工作流**：
```
> 帮我分析这个单细胞 RNA-seq 数据：质控→降维→聚类→标记基因识别→富集分析
→ AI 执行完整流程，每个步骤自动选择合适的包和参数
```

---

## 与 Agent Skills 生态的关系

### 开放标准的重要性

scientific-agent-skills 明确标注其基于开放的 [Agent Skills 标准](https://agentskills.io/)——这意味着：
- **非锁定**：不依赖特定 Agent 平台
- **可组合**：可以与其他 Agent Skills 叠加使用
- **社区驱动**：任何人都可以贡献新的 Skills

> "Claude Scientific Skills is now Scientific Agent Skills. Same skills, broader compatibility — now works with any AI agent that supports the open Agent Skills standard."
> — [K-Dense-AI/scientific-agent-skills README](https://github.com/K-Dense-AI/scientific-agent-skills)

### K-Dense BYOK：本地运行的 AI 共同科学家

项目还提供 **K-Dense BYOK**——一个免费、开源的 AI 共同科学家：
- 完全在本地桌面运行，数据不离开你的电脑
- 支持 40+ 模型，支持接入自己的 API key（BYOK）
- 内置 135 个科学技能 + 100+ 科学数据库 + Web 搜索

这解决了科研场景的一个核心顾虑：**数据隐私**。很多临床和基因数据不能上传到云端，本地运行是刚需。

---

## 安全考量

项目在 README 中明确列出了安全风险：

> "Skills can execute code and influence your coding agent's behavior. Review what you install."

项目会定期运行 Cisco AI Defense Skill Scanner 扫描所有技能，但团队资源有限，无法保证每个社区贡献都经过 exhaustive 审查。

**使用建议**：
- 不要一次性安装所有 135 个技能，只安装你实际需要的
- 安装前阅读 SKILL.md，了解技能会调用哪些包和外部服务
- 社区贡献的技能需要额外审查

---

## 社区健康度

| 指标 | 数值 |
|------|------|
| GitHub Stars | 持续增长中 |
| 技能数量 | 135（持续增加）|
| 覆盖科学领域 | 17 个主要领域 |
| 支持 Agent 平台 | 5 个主流平台 |
| 安全扫描 | 每周定期扫描 |

---

## 一句话推荐

如果你在科学研究中使用 AI Coding Agent，scientific-agent-skills 提供了一个经过系统整理的「AI 科学家工具包」——覆盖文献检索、数据库查询、实验流程、多步骤数据分析的完整工作流。本地运行版本（K-Dense BYOK）解决了敏感科研数据不能上云的问题，数据隐私和 AI 辅助研究可以兼得。

---

## 参考链接

- [GitHub: K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
- [Agent Skills 开放标准](https://agentskills.io/)
- [K-Dense BYOK - 本地 AI 科学家](https://github.com/K-Dense-AI/k-dense-byok)
- [Getting Started 视频](https://youtu.be/ZxbnDaD_FVg)