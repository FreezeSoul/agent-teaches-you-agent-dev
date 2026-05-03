# SkillClaw：让 Skills 在跨会话、跨 Agent、跨设备间持续演化

> **来源**：[AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw) · GitHub · Stars: 1,148 · Forks: 107
>
> **许可证**：MIT · **语言**：Python · **创建于**：2026-04-10 · **更新于**：2026-05-03
>
> **论文**：[arXiv:2604.08377](https://arxiv.org/abs/2604.08377)

---

## 一句话概括

**SkillClaw 在每个任务完成后运行后台演化循环，从真实交互中自动提取、去重、改进 Skills，让 Agent 的能力随使用不断积累，而非停滞在购买时的状态。**

---

## 核心创新：双循环架构

```
┌─────────────────────────────────────────────────────┐
│         Hermes / Claude Code / OpenClaw              │
│           任务时间循环（Task-time loop）              │
│  user → agent → task → result → (implicit memory)   │
└─────────────────────────────────────────────────────┘
                         ↓  silent post-task signal
┌─────────────────────────────────────────────────────┐
│              SkillClaw 演化循环                      │
│  extract → dedupe → evolve → merge → improved skills │
└─────────────────────────────────────────────────────┘
```

**关键洞察**：大多数 Agent 框架关注「任务执行」，而 SkillClaw 额外关注「任务后的技能积累」。用户的每次会话、每个 Agent、每种设备产生的经验，都被统一汇入 Skills 库并持续改进。

---

## 核心能力

### 1. 零干预演化

用户只需像平常一样与 Agent 对话，演化在后台静默发生：

```bash
skillclaw setup && skillclaw start --daemon
```

无需额外命令，Skills 会在每次任务完成后自动改进。

### 2. 跨平台兼容

| 平台 | 支持状态 |
|------|---------|
| Hermes（NousResearch） | ✅ 原生 |
| Claude Code（Anthropic） | ✅ 原生 |
| OpenClaw | ✅ 原生 |
| Codex（OpenAI） | ✅ 原生 |
| QwenPaw | ✅ |
| IronClaw | ✅ |
| PicoClaw / ZeroClaw | ✅ |
| OpenAI 兼容 API | ✅ |
| 自定义循环 | ✅（通过适配器） |

### 3. 去重与质量提升

多个相似 Skills 自动去重，低质量 Skills 自动改进，避免 Skills 库随时间膨胀为「垃圾堆」。

### 4. 论文支撑

有明确的学术论文（arXiv:2604.08377）支撑设计，有量化指标可验证。

---

## 架构解析

```
Session N ──┐
Session N+1 ─┼──→ SkillClaw Extract ──→ Dedup ──→ Evolve ──→ Merged Skills
Session N+2 ─┘                              ↑
                                         Vector similarity
                                          (auto-merge)
```

---

## 与现有项目的关系

| 项目 | 定位 | 与 SkillClaw 的关系 |
|------|------|-------------------|
| **mattpocock/skills** | 真实工程师 Skills 实践集 | 互补：skills 是「静态集合」，SkillClaw 是「动态演化系统」 |
| **awesome-cursor-skills** | Skills 聚合列表 | 互补：awesome list 解决「发现」，SkillClaw 解决「积累」 |
| **agentic-stack** | 跨 Harness 便携层 | 功能部分重叠：都有 skills/ 目录，但 agentic-stack 侧重 portability，SkillClaw 侧重 evolution |
| **mem0/mem0g** | 记忆系统 | 功能部分重叠：都有记忆积累，但 mem0 侧重上下文检索，SkillClaw 侧重 Skills 质量演化 |

---

## 关键数字

| 指标 | 数值 |
|------|------|
| GitHub Stars | 1,148（2026年4月10日至今，不到一个月） |
| Forks | 107 |
| 支持平台 | 9+ |
| Python 版本 | 3.10+ |
| 论文 | arXiv:2604.08377 |

---

## 适用场景

1. **长期使用的个人 Agent**：不希望每次新会话都从零开始，希望能力随使用不断增长
2. **多设备 / 多用户团队**：同一个 Skill 库被多个设备或用户共享，每次交互都在贡献技能积累
3. **Skills 质量维护**：厌倦了 Skills 库的无序膨胀和重复，期望有自动去重和提升机制

---

## 原文引用

> "Skills evolve from every session, every agent, every context. Solo or team — the loop is the same. Every experience compounds."
> — [README.md](https://github.com/AMAP-ML/SkillClaw)

> "SkillClaw doesn't make Hermes learn more — it makes everything Hermes has learned actually count."

---

## 延伸阅读

- [mattpocock/skills —— 来自真实工程师的 Agent Skills 实践集](articles/projects/mattpocock-skills-engineering-agent-2026.md)
- [agentic-stack —— 跨 Harness 的便携式 Memory + Skills 基础设施](articles/projects/agentic-stack-portable-agent-folder-2026.md)
- [NousResearch/hermes-agent —— 持续自我改进的 Agent 框架](articles/projects/hermes-agent-nousresearch-self-improving-agent-2026.md)
