# K-Dense-AI/scientific-agent-skills: 135 个科研 Agent Skills，让编码 Agent 变身 AI 科学家

## 目标用户

使用 Claude Code / Codex / Cursor 等编码 Agent，且需要处理**科研、生物学、化学、医学、工程、金融等领域的专业任务**的研究者和工程师。

---

## 能解决什么问题

普通编码 Agent 处理科研任务有两个核心障碍：

1. **不知道用什么工具**：生物信息学有 GATK、单细胞有 Scanpy、分子对接有 AutoDock——Agent 不具备这些领域知识
2. **不知道正确的工作流**：药物发现有 ADMET 筛选流程、基因组分析有标准 pipeline——这些不是通用编程，而是专业规程

Scientific Agent Skills 把 135 个领域的专业工作流编码为 Skills，让 Agent 能像领域专家一样执行多步骤科研任务。

---

## 核心亮点

### 135 个领域 Skills，覆盖 15 个科学大类

| 类别 | 代表 Skills |
|------|-----------|
| 🧬 生物信息学 & 基因组学 | Sequence analysis, single-cell RNA-seq, gene regulatory networks, variant annotation |
| 🧪 化学信息学 & 药物发现 | Molecular property prediction, virtual screening, ADMET analysis, molecular docking |
| 🔬 蛋白质组学 & 质谱 | LC-MS/MS processing, peptide identification, protein quantification |
| 🏥 临床研究 & 精准医学 | Clinical trials, pharmacogenomics, variant interpretation, treatment planning |
| 🧠 医疗 AI & 临床 ML | EHR analysis, physiological signal processing, clinical prediction models |
| 🖼️ 医学影像 & 数字病理 | DICOM processing, whole slide image analysis, radiology workflows |
| 🤖 机器学习 & AI | Deep learning, reinforcement learning, time series, model interpretability |
| 🔮 材料科学 & 化学 | Crystal structure analysis, phase diagrams, metabolic modeling |
| 🌌 物理 & 天文 | Astronomical data analysis, cosmological calculations, symbolic mathematics |
| ⚙️ 工程 & 仿真 | Discrete-event simulation, multi-objective optimization, systems modeling |
| 📊 数据分析与可视化 | Statistical analysis, network analysis, publication-quality figures |
| 🌍 地理空间科学 | Satellite imagery processing, GIS analysis, terrain analysis |
| 🧪 实验室自动化 | Liquid handling protocols, LIMS integration |
| 📚 科学传播 | Literature review, peer review, scientific writing, citation management |
| 🧬 多组学 & 系统生物学 | Multi-modal data integration, pathway analysis, network biology |

### 78+ 公共数据库直连

统一的 `database-lookup` Skill 提供对以下数据库的直接访问：

PubChem, ChEMBL, UniProt, COSMIC, ClinicalTrials.gov, FRED, USPTO, DepMap, Imaging Data Commons, PrimeKG, U.S. Treasury Fiscal Data, Hugging Science 等。

> "A unified database-lookup skill provides direct access to 78 public databases."

### 开放 Agent Skills 标准

> "Same skills, broader compatibility — now works with any AI agent that supports the open Agent Skills standard, not just Claude."
> — [GitHub README](https://github.com/K-Dense-AI/scientific-agent-skills)

基于 [agentskills.io](https://agentskills.io/) 开放标准，支持 Cursor、Claude Code、Codex 等所有兼容该标准的 Agent。

### K-Dense BYOK：本地 AI 科学家

配套项目 [K-Dense BYOK](https://github.com/K-Dense-AI/k-dense-byok) 让用户：

- 带自己的 API key，在桌面运行完整研究工作流
- 从 40+ 模型中选择
- 访问所有 135 个 Skills + 100+ 科学数据库
- 数据留在本地，可选扩展到 Modal 云端

---

## 与同类项目的差异化

| 项目 | 定位 | 差异 |
|------|------|------|
| **huggingface/skills** | 通用 AI/Coding Skills | 通用 vs 科学领域，两者互补 |
| **mattpocock/skills** | 工具类 Skills（git/格式化）| 工具类 vs 专业流程类 |
| **Photo-agents** | 视觉 grounding 自进化 Agent | 视觉/自拍领域 vs 科学研究领域 |
| **obra/superpowers** | 软件工程方法论 Skills | 工程方法论 vs 科学领域知识 |

---

## 快速上手

```bash
# 通过 agentskills.io 安装（以 Claude Code 为例）
# 参考官方文档安装 Agent Skills 标准兼容插件

# 在 Claude Code / Cursor / Codex 中直接使用
# 例如："帮我分析这个分子的 ADMET 性质"
# Agent 自动调用 molecular-property-prediction + ADMET-analysis Skills
```

---

## 引用

> "A comprehensive collection of 135 ready-to-use scientific and research skills for any AI agent that supports the open Agent Skills standard, created by K-Dense."
> — [GitHub README](https://github.com/K-Dense-AI/scientific-agent-skills)

> "Transform your AI coding agent into an 'AI Scientist' on your desktop!"
> — [GitHub README](https://github.com/K-Dense-AI/scientific-agent-skills)