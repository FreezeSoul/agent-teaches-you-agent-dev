# mattpocock/skills：让 AI Coding 从"Vibe"进化到"Engineered"

## 核心问题：如何解决 AI Agent 的四大工程失败模式

当 AI Agent 被广泛应用于软件开发时，常见的失败模式不是技术问题，而是**工程纪律缺失**：对齐偏差、反馈循环断裂、代码entropy加速。而大多数 AI 编程工作流（GSD、BMAD、Spec-Kit）通过剥夺工程师的控制权来「解决」这些问题，反而让问题更深。

Matt Pocock（TypeScript 专家，Total TypeScript 创始人）将二十年软件工程经验蒸馏为可组合的 Skills，让 AI 编程从「vibe coding」进化到「disciplined engineering」。

---

## 为什么存在（项目背景）

> "Developing real applications is hard. Approaches like GSD, BMAD, and Spec-Kit try to help by owning the process. But while doing so, they take away your control and make bugs in the process hard to resolve."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

**核心问题**：当前 Agent 编程失败的根本原因是**对齐偏差**——开发者以为 Agent 理解了需求，而 Agent 构建出的却完全不是预期。传统方法通过流程化开发来「解决」这个问题，但代价是剥夺工程师的控制权，让 debug 变得几乎不可能。

**Matt Pocock 的方案**：不是替代工程师的判断，而是**强化工程师对 Agent 的引导能力**。Skills 提供小型、易适配、可组合的工程实践工具，适用于任何模型。

---

## 核心能力：四大失败模式的对应对策

### 对策 1：[/grill-me](/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) — 对齐偏差的预防针

**问题**：Agent 开始编码前，开发者没有真正澄清需求，导致返工。

**方案**：强制 Agent 在开始前进行「批判性访谈」，挑战计划的每个分支。

> "The most common failure mode in software development is misalignment. You think the dev knows what you want. Then you see what they've built - and you realize it didn't understand you at all."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

[/grill-with-docs](/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) 是进阶版，额外更新 CONTEXT.md（共享语言文档）和 ADR（架构决策记录）。

---

### 对策 2：CONTEXT.md — 统一语言的构建工具

**问题**：开发者和 Agent 对同一概念使用不同术语，导致 Agent 用 20 个词表达 1 个概念。

**方案**：建立项目级「共享语言」文档，帮助 Agent 解码项目术语。

**效果**：
- 变量、函数、文件命名一致
- 代码库更易导航
- Agent 消耗更少 tokens 在思考上

> "A shared language has many other benefits than reducing verbosity: Variables, functions and files are named consistently... the codebase is easier to navigate for the agent... the agent also spends fewer tokens on thinking"
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

---

### 对策 3：[/tdd](/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md) — 反馈循环的重构

**问题**：Agent 写完代码后不知道自己写的是否正确，缺乏持续反馈。

**方案**：将 TDD 红-绿-重构循环注入 Agent 工作流：先写失败的测试 → 写代码修复测试 → 重构。

> "Without feedback on how the code it produces actually runs, the agent will be flying blind."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

[/diagnose](/mattpocock/skills/blob/main/skills/engineering/diagnose/SKILL.md) 是 debug 技能，将最佳调试实践封装为简单循环。

---

### 对策 4：[/improve-codebase-architecture](/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md) — 代码entropy的防火墙

**问题**：Agent 加速开发同时加速了软件 entropy，代码库以史无前例的速率变得更复杂。

**方案**：定期扫描代码库，识别模块深化机会，结合领域语言和 ADR 推动代码库持续改进。

> "Most apps built with agents are complex and hard to change. Because agents can radically speed up coding, they also accelerate software entropy."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

---

## 技术架构：渐进式披露 + 可组合性

### Skill 结构

每个 Skill 遵循**渐进式披露（Progressive Disclosure）**原则：

```
SKILL.md          # 只展示立即需要的指令
├── docs/         # 文档（按需加载）
├── templates/    # 模板（按需加载）
└── scripts/      # 脚本（按需加载）
```

这避免 Agent 被过多上下文淹没，同时保持完整信息可用性。

### 可组合性

Skills 设计为**可组合**：开发者可以根据项目需求混用不同 Skills，而不是使用一个包含一切的 monolithic workflow。

### 跨模型兼容

> "These skills are designed to be small, easy to adapt, and composable. They work with any model."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

不绑定特定 Agent（Claude Code / Codex / Cursor），适用于任何支持 Skill 机制的模型。

---

## 安装与使用

**30 秒快速开始**：

```bash
# 1. 运行 skills.sh 安装器
npx skills@latest add mattpocock/skills

# 2. 选择要安装的 Skills 和目标 Agent
# 确保选择 /setup-matt-pocock-skills

# 3. 在 Agent 中运行 /setup-matt-pocock-skills
# 它会询问：issue tracker、labels、文档保存位置

# 4. 开始使用
/grill-me      # 开始前对齐
/tdd           # 测试驱动开发
/diagnose      # 调试循环
```

**已发布的 Skills 清单**：

| Category | Skills |
|----------|--------|
| Engineering | diagnose, grill-with-docs, tdd, to-prd, zoom-out, improve-codebase-architecture |
| Productivity | grill-me |

---

## 数据与社区

| 指标 | 数值 |
|------|------|
| GitHub Stars | **74,875** |
| Newsletter 订阅者 | **~60,000** |
| 活跃 Repo 启用 Learning | **110,000+** |
| 生成 Learned Rules | **44,000+** |

> "If you want to keep up with changes to these skills, and any new ones I create, you can join ~60,000 other devs on my newsletter."
> — [mattpocock/skills README](https://github.com/mattpocock/skills)

---

## 与 Cursor Multi-Agent Kernel 优化的关联

在 Cursor 的 Multi-Agent CUDA Kernel 优化实验中，我们看到 Multi-Agent 系统在开放域问题上的能力边界被不断突破。但**能力边界扩展的同时，工程纪律的重要性也随之增加**。

mattpocock/skills 正是这个方向的工程实践：

- **Planner-Worker 协调** ≈ grill-me 的批判性访谈——在开始前对齐
- **Benchmark-driven 迭代** ≈ TDD 红绿重构——持续的反馈循环
- **代码架构持续优化** ≈ improve-codebase-architecture——防止 entropy 积累

无论 Agent 多么强大，**工程纪律是释放其全部潜力的必要条件**。mattpocock/skills 提供了一套可操作的工程实践，让 AI Coding 从「vibe」进化到「engineered」。

---

*来源：[mattpocock/skills README](https://github.com/mattpocock/skills)（2026-05）*