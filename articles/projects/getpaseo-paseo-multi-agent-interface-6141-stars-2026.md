# Paseo：用一个界面控制所有 AI 编码 Agent，6,141 Stars 的 Agent 编排层

## 这个项目解决了什么问题

你的团队里，有人用 Claude Code，有人用 Codex，有人用 OpenCode。三个工具，三套 CLI，三个不同的交互方式。Paseo 的答案是：**统一这三种 Agent 的控制界面**。

README 开篇明义：

> "One interface for all your Claude Code, Codex and OpenCode agents."

这不是简单地把三个 CLI 包装成一个。Paseo 的架构是**本地 Daemon 模式**：在你的机器上跑一个 daemon（常驻进程），然后通过桌面 App、Mobile App、Web App 或 CLI 客户端连接这个 daemon，由 daemon 统一管理和调度不同的 Agent。

这是一个有意思的架构选择——它把"Agent 运行时"和"Agent 控制界面"彻底解耦了。

---

## Self-hosted + 隐私优先：你的 Agent 跑在你的机器上

Paseo 有一个设计原则贯穿始终：Agent 跑在你自己的机器上，使用你的完整开发环境。README 里说：

> "Self-hosted: Agents run on your machine with your full dev environment. Use your tools, your configs, and your skills."

这句话的潜台词是：没有云端执行，没有第三方数据处理，Agent 用的就是你本地的工具链。Paseo 的另一个承诺是：

> "Paseo doesn't have any telemetry, tracking, or forced log-ins."

对于那些对数据主权有强需求的团队（比如在受监管行业工作、或者单纯不想让代码流经第三方服务），这个定位很有吸引力。

---

## Skills 系统：Agent 编排的技能层

Paseo 不只是"多 Agent UI"，它还内置了一套 Skills 系统，让 Agent 可以互相调用：

> "Skills teach your agent to use Paseo to orchestrate other agents."

具体的 Skill 包括：`/paseo-handoff`（在不同 Agent 之间转移工作）、`/paseo-loop`（让 Agent 按验收标准循环执行）、`/paseo-advisor`（为一个 Agent 配备一个顾问 Agent）、`/paseo-committee`（组建双 Agent 委员会做根因分析）。

笔者认为这个设计很有意思——它把 Multi-Agent 协作从"多个 Agent 在不同终端里各自为战"变成了"用 Skill 协议描述 Agent 之间的协作关系"。虽然目前这套系统的成熟度还有待观察，但方向是对的。

---

## 具体的使用场景

你在 Desktop 上启动 Paseo daemon，用 Claude Code 跑一个"实现用户认证模块"的任务，做到一半发现需要另一个 Agent 帮忙 review 架构设计。你在手机上打开 Paseo App，输入 `/paseo-advisor` 启动一个顾问 Agent，用 OpenCode 作为底层跑安全审计，结论直接回到你与 Claude Code 的对话里。整个过程不需要切换任何应用，不需要 copy/paste 代码。

---

## 为什么值得关注

笔者认为 Paseo 的核心价值是**多 Agent 入口统一**。

现在 Claude Code / Codex / OpenCode 三个工具各有各的 CLI 界面和工作流。长期来看，随着 AI 编码工具越来越多，团队里会出现"工具碎片化"的问题——每个工具都有自己擅长的场景，但开发者需要记住三套不同的交互方式。Paseo 想做的事，是在这之上提供一个统一的控制平面。

如果你已经在同时使用多个 Agent 工具，Paseo 可以减少你的认知负担。如果你只用一个 Agent 工具，Paseo 现在的价值有限。

---

## 所以你可以

如果你同时跑 Claude Code、Codex 和 OpenCode，且需要在它们之间频繁切换或协作，Paseo 的统一界面会显著简化你的工作流。

如果你只专注一个 Agent 生态（比如只用 Claude Code），Paseo 目前提供的额外价值不大——但可以先关注它的 Skills 系统发展，这个方向代表的是多 Agent 协作协议的一种可能。

---

> 📌 GitHub: https://github.com/getpaseo/paseo | Stars: **6,141** | 许可证: AGPL-3.0