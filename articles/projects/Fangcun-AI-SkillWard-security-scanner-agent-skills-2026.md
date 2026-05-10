# SkillWard：Agent Skills 的生产级安全扫描仪

**推荐目标**：有 Python 经验的 Agent 开发平台工程师，想在发布/部署 Skills 前做安全把关

**核心结论**：SkillWard 用「三阶段扫描」（静态分析 + LLM 评估 + Docker 沙箱执行）解决 Skills 安全检测的「高误报、低覆盖」问题——实测 5,000 个真实 Skills 中 ~25% 被标记，~38% 可疑样本进入沙箱后约 1/3 暴露了纯静态分析无法发现的运行时威胁。

**主题关联**：本文是 [OpenAI Codex 安全运行架构](./openai-codex-safe-deployment-security-control-plane-2026.md) 的配套——Codex 解决的是「Agent 执行时的控制面」，SkillWard 解决的是「Skills 部署前的安全检查」。两者构成完整的「发布前扫描 + 运行控制」安全闭环。

---

## 定位破题（Positioning）

**一句话定义**：Agent Skills 的生产级安全扫描工具，专注解决 Skills 市场「只管能用，不管安全」的问题。

**场景锚定**：当你从 ClawHub 或其他 Skills 市场拉取一个 Skill，准备集成到生产 Agent 时——SkillWard 告诉你它到底会做什么。

**差异化标签**：唯一同时用「静态分析 + LLM 语义推理 + Docker 沙箱实际运行」三种手段检测 Skills 威胁的工具。

---

## 体验式介绍（Sensation）

假设你从网上拉了一个 Skills，准备这样用：

```bash
# 安装并运行一个未信任的 Skill
npx skill install company-internal-tool
# Skill 声明：我只会读取代码，不会外传数据
```

你的顾虑是什么？这个 Skill 真的只读取代码吗？它会不会在你不知情的情况下把 secrets 外泄？

**SkillWard 的工作流**：

1. **提交 Skill**：单个或批量上传
2. **选择扫描模式**：Quick Scan（< 1 分钟）/ Sandbox Scan（需沙箱）/ Deep Trace（完整行为追踪）
3. **获取报告**：威胁等级 + 证据 + 修复建议

```python
# 示例：通过 Python API 调用 SkillWard
from skillward import Scanner

scanner = Scanner(
    llm_provider="openai",  # 或 "anthropic"
    docker_enabled=True    # 启用沙箱执行
)

result = scanner.scan_skill("./my-skill/")
print(f"威胁等级: {result.threat_level}")  # HIGH / MEDIUM / LOW / SAFE
print(f"发现: {result.findings}")          # 三阶段详情
```

---

## 拆解验证（Evidence）

### 技术架构：三阶段漏斗

```
Stage A：静态分析（秒级）
├── YARA 规则：匹配已知恶意模式（凭证窃取、代码注入）
├── Regex：检测可疑编码/隐蔽文件/prompt poisoning
└── 权限行为对比：Skill 声明的权限 vs 实际代码行为

         ↓ 可疑样本进入

Stage B：LLM 语义评估（快速）
├── 目的推理：Skill 的真实意图是什么
├── 置信度判断：能否自信地分类为安全/不安全
└── 不确定的样本 → Stage C

         ↓ 仍可疑的样本进入

Stage C：沙箱执行（深度）
├── Docker 容器隔离环境
├── In-container Agent 自动安装依赖、驱动 Skill 端到端运行
├── Guard 监控：网络访问、文件写入、凭证访问
└── 蜜罐诱饵：植入假凭证检验是否外泄
```

**关键数字**（README 数据）：
- 扫描 5,000 真实世界 Skills：~25% 被标记为不安全
- ~38% 可疑样本进入 Stage C 沙箱后，约 1/3 暴露了运行时威胁（静态分析无法发现）
- 99% 部署成功率（自动修复依赖问题）

### 竞品对比

| 维度 | SkillWard | 纯静态扫描工具 | 纯 LLM 评估 |
|------|---------|--------------|-------------|
| **速度** | 快（静态部分秒级）| 最快 | 中等 |
| **误报率** | 低（三阶段置信度高）| 高 | 中 |
| **检测覆盖率** | 高（含运行时）| 中（仅已知模式）| 低（依赖 LLM 能力）|
| **实际运行验证** | ✅ | ❌ | ❌ |

### 引用自 README

> "Five scanners on 238,180 Skills showed highly inconsistent results, only 0.12% were flagged by all five, with individual flag rates ranging from 3.79% to 41.93%."
> — Holzbauer et al., *Malicious Or Not: Adding Repository Context to Agent Skill Classification*, 2026

> "SkillWard enables security review of AI Agent Skills before they are published or deployed, reducing the potential risks of Agent usage. Beyond static analysis and LLM evaluation, it executes suspicious Skills in isolated Docker sandboxes, replacing uncertain warnings with runtime evidence."
> — [SkillWard README](https://github.com/Fangcun-AI/SkillWard)

---

## 行动引导（Threshold）

### 快速上手（3 步）

```bash
# 1. 安装
pip install skillward

# 2. 启动 Web UI（可选）
skillward ui

# 3. 扫描一个 Skill
skillward scan ./my-skill/ --mode quick
```

### Web 在线体验

> [skillward.fangcunleap.com](https://skillward.fangcunleap.com/) — 无需安装，直接在线体验

### 适用场景

- **平台团队**：在 Skills 市场发布前强制扫描
- **安全团队**：审计已引入的 Skills 是否有隐蔽威胁
- **开发者**：集成第三方 Skills 前做尽职调查

### 不适用场景

- 实时拦截（当前是离线的批量扫描，不是 IDS）
- 非 Python Skills（当前主要支持 Python-based Skills）
