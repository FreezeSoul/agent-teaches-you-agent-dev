# Cursor Composer 自举技术：RL 训练环境中环境自动化的新范式

## 核心论点

> **Cursor 的工程团队将 RL 训练中的环境配置问题转化为一个双代理协作任务——一个代理设定目标，另一个代理尝试实现。通过这种"目标定义 + 目标实现"的解耦设计，Composer 能够从任意未配置的代码仓库自动生成可运行的训练环境，将环境准备的失败率从不可控降低到可量化评估的水平，同时通过前代模型引导后继模型的训练改进，形成了一套可积累的自举飞轮。**

---

## 一、问题的本质：环境配置是 RL 训练的第一个瓶颈

在 RL 训练中，如果环境在起点就是坏的，模型会浪费大量 tokens 去调试配置，而不是学习解决问题。在最坏的情况下，一个坏的环境可以让一个问题变得根本无法解决，导致计算资源消耗却得不到任何奖励信号。

这在生产级 Agent 开发中同样成立。Cursor 自己在博客中提到：

> "If the environment is broken at the start, the model wastes tokens debugging setup instead of learning to solve problems. In the worst cases, a bad environment can make a problem unsolvable entirely, which ends up burning compute for no reward signal."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

传统的解法是让人类工程师预先配置好所有环境，但这有几个根本性问题：

1. **不可扩展**：每换一个代码仓库都需要重新配置，无法泛化
2. **配置本身可能出错**：人类配置也会引入错误
3. **无法适应 RL 的动态需求**：RL 训练需要大量多样化的环境，预先配置的成本太高

Cursor 的解法是将环境配置本身变成一个 Agent 可以完成的任务——通过前代模型（Composer 1.5）来自动完成 Composer 2 训练环境的设计。

---

## 二、双阶段设计：目标定义与目标实现的解耦

Cursor 的 autoinstall 系统将环境配置分解为两个阶段，形成了一个精巧的解耦设计：

### 阶段一：目标设定（Goal Setting Agent）

第一个 Composer 代理接收一个固定的代码仓库 checkout，然后被要求**提出 10 条命令和一个高级别描述**，说明如果环境正确设置，这些命令应该产生什么输出。

这个代理会主动探索：
- README 或 Makefile（了解项目的标准构建流程）
- 语言特定的包管理器（如 Python 的 uv、Go 的 go mod、Rust 的 cargo）
- 测试命令和启动命令

> "The agent will explore any readme or makefiles for the environment, as well as try typical language-specific commands such as project managers like uv or linters like clippy. The agent's work will typically consist of setup commands, tests if they are available, and launch commands for executables."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

### 阶段二：目标实现（Implementation Agent）

第二个独立的 Composer 代理被给予：
- 环境的初始状态
- 从第一阶段筛选出的 3 条目标命令

然后这个代理会探索代码仓库、调用工具，尽可能让这三条命令运行成功。如果测试失败，重试这个阶段。整个过程最多重复 5 次——如果 5 次后环境仍然不能令人满意，就丢弃这个环境。

> "We provide a separate Composer agent with the initial state of the environment as well as three target commands selected from the proposed 10. The agent will then explore the codebase, calling tool calls to get the environment set up so that the commands can run. Afterward, we test that all three commands run and that the output matches the target description from the first agent. If not, we restart the second phase again."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

### 这种设计的核心价值

**它将"环境是否正确设置"这个问题从一个人类判断变成了一个可量化的 Agent 判断**。第一阶段定义成功标准，第二阶段执行并验证。如果验证失败，Agent 可以自主调整并重试。这本质上是一个自动化的单元测试循环，只不过测试的对象是环境配置本身。

---

## 三、目标定义代理的智能：mock 和补充缺失资源

一个值得注意的细节是，当真实环境缺少必要资源时，Composer 会主动 mock 缺失的部分。

Cursor 博客记录了一个典型场景：

> "To achieve that, it will mock missing files, create placeholder images, or even create fake database tables. Some projects require installing additional components that are needed to run tests, such as S3 folders or missing sidecar containers. Composer often mocks these as well, creating MinIO configs or Docker containers to get these to work."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

这揭示了一个重要的设计哲学：**环境配置的终点不是"真实"，而是"可用"**。对于 RL 训练来说，环境的目的是提供有效的训练信号，而不是忠实地复制生产环境。因此，mock 只要能产生有效的训练信号，就是合理的。

更进一步，Composer 被允许创建启动脚本来启动长进程（如需要运行的后台服务）：

> "To support long-running processes, we allowed autoinstall to create a start script to launch these at the beginning of the RL usage."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

---

## 四、实战案例：从 Celo-monorepo 看真实场景的复杂性

Cursor 记录了一个真实的实验案例：使用 autoinstall 来设置 Celo（一个大型区块链项目）的环境。

### 第一阶段观察

目标设定代理在探索阶段做了以下事情：
- 阅读项目的文档和代码，找到关键的安装命令
- 发现项目自带的文档相对稀疏，于是使用 web 搜索来查找额外的设置命令
- 识别出的命令主要是安装或测试命令，还包括一个来自文档的基础最小化应用程序

### 第二阶段观察

目标实现代理在尝试运行这些命令时遇到了问题：
- 它发现需要额外安装 Foundry（一个相关仓库）
- 使用 web 搜索阅读了这个依赖项目的文档
- 第一次迭代没有成功运行测试应用程序，但在第二次迭代中找到了解法：创建一个 mock 用户来本地启动应用程序

> "On the first iteration of this stage, it failed to get this test application running, but on a second iteration it found that it could create a mock user to start the application locally and satisfy the requirement."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

这个案例说明了几个关键点：

1. **探索的必要性**：代理需要使用 web 搜索来补充缺失的文档信息，这说明静态的文档是不够的
2. **迭代的价值**：第一次失败不意味着环境无法配置，代理有能力自我调整
3. **Mock 的合理性**：创建 mock 用户来启动应用，而不是配置一个完整的认证系统——这正是"可用性优先于真实性"的设计哲学

---

## 五、自举飞轮：Terminal-Bench 上的可量化成果

Cursor 报告了一个明确的数据：

> "Composer 2 now scores significantly higher on Terminal-Bench (61.7% versus 47.9% for Composer 1.5), a benchmark that includes tests of a model's ability to set up developer environments."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

Terminal-Bench 是一个测试模型环境配置能力的 benchmark，Composer 2（使用 Composer 1.5 的 autoinstall 生成训练环境）相比 Composer 1.5 提升了近 14 个百分点（从 47.9% 到 61.7%）。

这个结果揭示了几个重要的结论：

**第一，训练环境的质量直接影响模型在 benchmark 上的表现。** 好的环境让模型学习到正确的行为模式，坏的环境让模型学到错误的或不完整的技能。

**第二，自举是有效的。** Composer 1.5 设计的训练环境，训练出的 Composer 2 在环境配置能力上超越了 Composer 1.5 本身——这证明了两代模型之间的知识传递是成功的。

**第三，这个飞轮会继续加速。** Cursor 明确表示：

> "We anticipate in future runs, previous Composer instances will play a large role in many other aspects of the training process, including run management, data preprocessing, and architecture tuning."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

---

## 六、与生产级 Agent 环境的关联：Cloud Agents 的影子

Cursor 明确指出，autoinstall 的设计灵感来自于生产环境：

> "Like many aspects of our model development, autoinstall is inspired by production Cursor systems. In Cursor cloud agents, we have a feature that automates the setup of cloud environments for users, to allow their agents to work on projects in a mock environment."
> — [Cursor Engineering Blog: Bootstrapping Composer with autoinstall](https://cursor.com/blog/bootstrapping-composer-with-autoinstall)

这说明了一个重要的现象：**Cursor 的 RL 训练基础设施和它的产品基础设施是同构的**。Cloud agents 用于为真实用户自动配置云端开发环境，autoinstall 用于为 RL 训练自动配置模拟环境。两者都面临同一个核心问题：从零开始，让一个陌生的代码仓库变成可运行的状态。

这与 OpenAI 的「Shell + Skills + Compaction」三原语框架中的 Shell primitive 有直接的关联——Shell 的核心功能是创建一个持久的、执行环境，让 Agent 可以在其中工作。autoinstall 解决的问题是如何在 RL 训练开始前准备好这样的环境。

从更广泛的角度看，这涉及到的是**Agent 的环境 provisioning 问题**。无论是 RL 训练还是生产部署，Agent 都需要一个可运行的环境，而这个环境不能总是由人类预先准备好。autoinstall 提供了一种通用的自动化方案。

---

## 七、工程启示：目标-实现解耦的价值

Cursor 的 autoinstall 设计提供了一种可复用的工程模式：**将"定义正确的结果"和"实现正确的结果"解耦为两个独立的 Agent 任务**。

这种设计有几个关键优势：

1. **可验证性**：第一阶段明确定义了"成功"的标准（命令输出匹配预期），使得验证成为可能
2. **可迭代性**：第二阶段的失败可以自动触发重试，不需要人类介入
3. **可扩展性**：两阶段的划分使得系统可以独立升级——改进目标设定算法或改进目标实现算法
4. **可测量性**：5 次重试上限和丢弃机制提供了一个明确的失败边界，使得整体成功率可以被测量

这个模式在 RL 训练之外也有应用价值。例如，在 CI/CD 系统中，可以用一个 Agent 定义"构建成功"的标准，用另一个 Agent 尝试满足这个标准。在测试系统中，可以用一个 Agent 定义"功能正确"的条件，用另一个 Agent 尝试达到这个条件。

---

## 八、局限性与未解决的问题

Cursor 的 autoinstall 也揭示了一些重要的问题：

**5 次重试上限是否足够？** 对于简单的项目，5 次重试可能足够；但对于复杂的生产级项目（如包含区块链、多语言 monorepo 等），可能需要更多次的迭代。这意味着环境配置的难度可能比预期高得多。

**Mock 的边界在哪里？** Composer 被允许 mock 文件系统、数据库甚至认证系统，但 mock 到什么程度会损害训练的有效性？这是一个没有被明确回答的问题。

**目标设定的质量如何保证？** 如果第一阶段的"目标设定"代理本身能力不足，它提出的 10 条命令和预期输出可能本身就是错误的。如何验证目标设定代理的质量？

这些问题指向了一个更深层的方向：**当我们将"环境配置"交给 Agent 自动完成时，我们实际上创建了一个新的、复杂的系统，其行为需要被单独验证**。这与 Agent 的可观测性问题有直接的关联。

---

## 九、与现有 Agent 工程框架的互补关系

autoinstall 的核心思想——将"定义目标"和"实现目标"解耦——与多个现有的 Agent 工程框架形成了互补：

| 框架 | 与 autoinstall 的关系 |
|------|---------------------|
| **OpenAI Shell + Skills + Compaction** | Shell primitive 提供持久的执行环境，autoinstall 解决的是"如何自动准备这样的环境" |
| **Anthropic Agent Skills（渐进式披露）** | Skills 定义了 Agent 的能力边界，autoinstall 解决的是"如何从零开始让这些能力可被验证" |
| **Cursor Cloud Agents** | Cloud agents 是生产级的环境自动化实现，autoinstall 是其 RL 训练版本 |
| **HumanLayer 的 12-Factor Agents** | Factor 5（Environment 属性）涉及环境配置，autoinstall 提供了一种自动化的实现路径 |

从方法论的角度看，autoinstall 解决的是"在训练或执行开始前，确保环境处于正确状态"这个问题，这是所有 Agent 系统都需要面对的前提条件。

---

## 十、核心结论与行动建议

### 核心结论

**环境配置是 Agent 系统的一个核心工程问题，而不是一个可以忽略的前提条件。** Cursor 通过双阶段代理设计（目标设定 + 目标实现）将这个问题自动化，并且验证了这套方法在 Terminal-Bench 上带来了 14 个百分点的提升。这证明了一个重要的工程原则：**好的训练环境不是预先设计出来的，而是通过自动化方法生成出来的**。

### 行动建议

**对于 Agent 系统设计者：**
- 不要假设环境是正确配置的；在 Agent 执行前加入环境验证和自动修复机制
- 将"定义成功标准"和"实现成功"解耦为独立的子任务
- 为环境配置失败设计明确的回退机制（重试上限、丢弃机制）

**对于 RL 训练工程师：**
- 投资建设环境自动化能力；这是提升训练效率的关键杠杆
- 使用前代模型来引导后代模型的环境配置是一个有效的自举路径
- 建立 Terminal-Bench 这样的专门评估环境配置能力的 benchmark

**对于平台工程师：**
- Cloud agents 和类似的自动化环境 provisioning 系统是 Agent 平台的基础能力
- 将环境配置从"人类操作"变为"Agent 自动完成"是降低 Agent 使用门槛的关键

---

## 参考文献

1. Cursor Engineering Blog: "Bootstrapping Composer with autoinstall" (2026-05-06) — https://cursor.com/blog/bootstrapping-composer-with-autoinstall
2. Cursor Blog: "Composer 2" — https://cursor.com/blog/composer-2
3. Terminal-Bench (tbench.ai) — https://www.tbench.ai/

---

*本文属于 fundamentals/ 目录，关联主题：RL训练环境自动化 · 双代理解耦设计 · 自举飞轮 · Terminal-Bench*