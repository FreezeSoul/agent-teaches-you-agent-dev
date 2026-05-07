# FastRender：百枚并发 Agent 从零构建浏览器引擎的工程奇迹

> 笔者认为：FastRender 最有价值的不是「能跑起来」这件事本身，而是它揭示的**大规模 Agent 协作的工程边界**——当 100+ Agent 并行写 100 万行代码时，任务分解、状态同步、结果汇合的机制是怎么设计的。这篇文章要回答的是：FastRender 做到了什么、它背后的 Agent 协作架构是什么、以及这对多 Agent 系统工程的工程启示。

---

## T - Target：给谁看

**用户画像**：有一定 Agent 开发经验的工程师，想了解**多 Agent 并行协作**在实际复杂项目中的工程实践，或者在寻找「Agent swarm」架构的参考案例。

**水平要求**：了解基本 Agent 概念即可，但需要对新问题有认知耐心——这不是一个「三行代码跑起来」的 demo，而是一个真实的系统工程实验。

---

## R - Result：能带来什么改变

FastRender 本身是一个**实验性浏览器引擎**（Rust 实现），但它的工程意义远超这个项目本身：

- **规模**：Cursor 团队用 **~100 枚并发 Agent** 运行近一周，生成了 **超过 100 万行代码、1000 个文件**
- **产出**：一个从零构建的浏览器引擎，可以渲染 google.com 的页面（虽然有渲染瑕疵，但页面可读）
- **技术验证**：证明了「用 AI Agent swarm 构建复杂软件系统」这件事在工程上是可行的
- **星标增长**：截至 2026-05，GitHub 1,544 Stars，上升趋势仍在持续

> "To test this system, we pointed it at an ambitious goal: building a web browser from scratch. The agents ran for close to a week, writing over 1 million lines of code across 1,000 files."
> — [Simon Willison: Scaling long-running autonomous coding](https://simonwillison.net/2026/jan/19/scaling-long-running-autonomous-coding/)

---

## I - Insight：技术方案解析

### 核心架构：Planner / Sub-Planner / Worker 三层分离

FastRender 项目的 Agent 系统采用了**层级任务分解**架构：

```
┌─────────────────────────────────────────────────────┐
│                  Planner（主规划器）                  │
│  接收高层目标 → 拆解为子任务 → 分发给 Sub-Planners   │
└───────────────────────┬─────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│Sub-Planner A│  │Sub-Planner B│  │Sub-Planner C│
│  渲染引擎   │  │  网络栈     │  │  JavaScript │
│  子任务分解 │  │  子任务分解 │  │  引擎子任务 │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────────────────────────────────────────────┐
│                   Workers（执行器）                  │
│    接收具体任务 → 写代码 → 返回结果                  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ Judge Agent     │
              │ 判断任务是否完成 │
              └─────────────────┘
```

**关键设计点**：

1. **Planner 只有一个**，负责任务的全局分解，不参与具体代码编写
2. **Sub-Planners 多个**，每个负责一个子系统（渲染引擎、网络栈、JS 引擎），进一步拆解任务
3. **Workers 大量并行**，接收 Sub-Planner 分配的具体任务（函数实现、测试编写等），执行后返回结果
4. **Judge Agent** 每一轮循环结束时判断「项目是否完成」，如果没完成则继续分发任务

> "They ended up running planners and sub-planners to create tasks, then having workers execute on those tasks - similar to how Claude Code uses sub-agents."
> — [Simon Willison: Scaling long-running autonomous coding](https://simonwillison.net/2026/jan/19/scaling-long-running-autonomous-coding/)

### 规格文档作为上下文注入

一个有意思的工程选择：项目使用 **Git submodules 引用 WhatWG 和 CSS-WG 规范文档**，而不是靠 Agent 记住所有细节：

```
fastrender/
├── specs/          ← WhatWG / CSS-WG 规范
│   ├── html/
│   ├── css/
│   └── ...
└── src/
    ├── html/
    ├── css/
    └── ...
```

这是「渐进式上下文」思路的另一种体现：**规格文档是静态的参考信息，不需要每次都塞进上下文**。

> "The FastRender repo even uses Git submodules to include various WhatWG and CSS-WG specifications in the repo, which is a smart way to make sure the agents have access to the reference materials that they might need."
> — [Simon Willison](https://simonwillison.net/2026/jan/19/scaling-long-running-autonomous-coding/)

### 并发 Agent 的协调机制

100 枚 Agent 并行工作时，最大的工程挑战不是「如何写代码」，而是**如何避免冲突、如何管理共享状态、如何处理任务依赖**。从项目结构和 Simon Willison 的描述来看，关键机制包括：

- **任务池化**：Planner 将任务放入队列，Workers 各自认领
- **状态同步**：每轮结束时的 Judge Agent 判断项目整体进度
- **无锁冲突**：基于任务的隔离性设计（不同文件、不同模块），避免并发写冲突

---

## P - Proof：实际验证情况

### 构建验证

Simon Willison 在 macOS 上成功构建并运行了 FastRender：

```bash
cd /tmp
git clone https://github.com/wilsonzlin/fastrender
cd fastrender
git submodule update --init vendor/ecma-rs
cargo run --release --features browser_ui --bin browser
```

**结果**：成功弹出浏览器窗口，能渲染 google.com 和他自己的网站。

### CI 状态

初始发布时项目的 GitHub Actions CI 是失败的，且没有 build 文档。但Cursor 团队在 24 小时内修复了这两个问题——补充了构建说明，CI 变绿。

> "It looks like they addressed that within the past 24 hours. The latest README includes build instructions which I followed on macOS like this: [...] This got me a working browser window!"
> — [Simon Willison](https://simonwillison.net/2026/jan/19/scaling-long-running-autonomous-coding/)

### 质量评估

Simon 的评价比较客观：

> "You can tell they're not just wrapping an existing rendering engine because of those very obvious rendering glitches, but the pages are legible and look mostly correct."

这说明 Agent 生成的代码**不是简单的胶水层封装**，是真正从零实现的渲染引擎（有些 CSS 细节渲染有问题）。

---

## E - Evidence：项目架构与关键文件

### 目录结构

```
fastrender/
├── src/
│   ├── browser/          # 浏览器入口
│   ├── html/             # HTML 解析
│   ├── css/              # CSS 解析与样式计算
│   ├── layout/           # 布局引擎
│   ├── painting/         # 渲染输出
│   ├── javascript/       # JavaScript 引擎
│   └── network/          # HTTP/Fetch
├── specs/                # WhatWG/CSS-WG 规范（git submodule）
├── Cargo.toml
└── README.md
```

### 技术栈

- **语言**：Rust（性能敏感的核心模块）
- **构建工具**：Cargo
- **规范参考**：WhatWG HTML 规范、CSS-WG 规范（作为 git submodule 引用）

---

## T - Threshold：行动指南

### 快速上手

```bash
git clone https://github.com/wilsonzlin/fastrender
cd fastrender
git submodule update --init vendor/ecma-rs
cargo run --release --features browser_ui --bin browser
```

### 关注价值

FastRender 的核心价值不是「作为产品使用」，而是**作为多 Agent 并行系统工程的技术验证**：

1. **如果你在设计多 Agent 协作系统**：研究 Planner/Sub-Planner 的任务分解逻辑
2. **如果你在做 Agent eval**：参考 Judge Agent 的完成度判断机制
3. **如果你在探索「AI 构建复杂系统」的边界**：这是目前最接近生产级的案例之一

### 局限性

- 仍处于实验阶段，不建议用于生产环境
- 渲染质量不如 Chromium/WebKit 等成熟引擎（在意料之中）
- 后续维护和迭代的工程路径尚不明确

---

*推荐来源：[Simon Willison: Scaling long-running autonomous coding](https://simonwillison.net/2026/jan/19/scaling-long-running-autonomous-coding/) + [FastRender GitHub](https://github.com/wilsonzlin/fastrender)*
