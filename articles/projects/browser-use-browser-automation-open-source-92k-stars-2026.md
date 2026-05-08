# browser-use：让网站对 AI Agent 可访问的浏览器自动化框架

## 项目概览

| 维度 | 数据 |
|------|------|
| **GitHub** | [browser-use/browser-use](https://github.com/browser-use/browser-use)（92,878 ⭐，10,516 forks） |
| **定位** | AI Agent 的浏览器操作层——让大模型能够自主控制浏览器完成真实世界任务 |
| **技术栈** | Python ≥ 3.11，pip install via `uv init && uv add browser-use` |
| **LLM 支持** | 模型无关（Anthropic Claude / Google Gemini / OpenAI GPT 等均可驱动） |
| **生态** | 开源版 + Cloud 云服务版（stealth 浏览器、代理轮换、1,000+ 集成） |

---

## 核心价值

browser-use 解决的是 AI Agent 与真实世界网站交互的最后一公里问题。当 Agent 需要完成「填写表单」「抓取数据」「验证 UI 变化」「搜索信息」这类任务时，它们不是在调用 API，而是在操作一个真实运行在浏览器里的 Web 应用。browser-use 将这个过程抽象为一个可编程的 Agent 接口。

> "Make websites accessible for AI agents. Automate tasks online with ease."
> — [browser-use GitHub README](https://github.com/browser-use/browser-use)

这个定位听起来简单，但实际工程复杂度很高：反爬虫检测、CAPTCHA 处理、会话状态管理、多标签页协同、文件上传下载——这些都是真实网站交互中的暗礁。browser-use 的方案分为两层：**开源 Agent** 处理通用场景，**Cloud Agent** 处理需要高度隐蔽和规模化的高级场景。

---

## 架构设计：三层抽象

### 3.1 Agent 接口层

```python
from browser_use import Agent, Browser
import asyncio

async def main():
    agent = Agent(
        task="Find the number of stars of the browser-use repo",
        llm=ChatAnthropic(model='claude-sonnet-4-6'),
        browser=Browser(),
    )
    await agent.run()
```

Agent 是核心抽象：接收一个自然语言任务描述 + 一个 LLM 实例 + 一个浏览器对象，然后自主执行。任务描述不需要告诉 Agent「点击哪个按钮」「输入什么内容」——Agent 自己根据任务目标理解网页结构并操作。

### 3.2 LLM-agnostic 设计

browser-use 不绑定特定模型提供商。你可以用 Claude Code 驱动的 Agent，也可以用 Gemini。它们通过统一的 `ChatAgent` 接口接入，Agent 的规划能力和浏览器操作能力完全来自模型本身，browser-use 负责将操作结果反馈给模型进行下一轮决策。

这意味着：**browser-use 是模型能力的放大器，而不是替代品**。一个规划能力强的模型（如 Claude Sonnet 4）配合 browser-use 能够完成复杂的多步骤任务；一个弱模型只能完成简单任务。

### 3.3 Cloud 层的差异化能力

开源版本的能力受限于本地浏览器环境。Cloud 版本（[cloud.browser-use.com](https://cloud.browser-use.com)）提供了企业级能力：

- **Stealth 浏览器**：防止被网站检测为机器人（反爬虫对策）
- **代理轮换**：不同 IP 地址发起请求，避免频率限制
- **CAPTCHA 解决**：自动化处理验证码
- **1,000+ 集成**：Gmail、Slack、Notion 等 SAAS 应用的原生集成
- **持久化文件系统**：跨 session 保留状态
- **持久化记忆**：跨任务记住历史上下文

这些能力对于需要规模化运营的企业来说是关键差异——开源版本适合开发和测试，Cloud 版本适合生产部署。

---

## 基准测试与模型能力对比

browser-use 维护了一个公开的 benchmark 数据集（[browser-use/benchmark](https://github.com/browser-use/benchmark)），包含 100 个真实世界浏览器任务。基准测试结果揭示了一个重要现象：**不同模型在浏览器任务上的表现差异远大于它们在标准 benchmark 上的差异**。

这说明浏览器的操作任务对模型的「具身认知」要求更高——模型需要理解网页的结构逻辑、预期操作后果、处理意外状态。这种能力不完全取决于模型的原始智力，而更多取决于模型在训练中接触到的网页交互数据量。

---

## 与 Cloudflare Sandboxes 的协同关系

在 [Cloudflare Sandboxes GA](./cloudflare-sandboxes-ga-agent-persistent-execution-environment-2026.md) 中我们分析了持久化执行环境对 Agent 的价值：长时间运行的开发服务器、状态持久化、快照恢复。

browser-use 与 Sandboxes 构成了一对**执行 + 操作**的互补关系：

- **Sandboxes**：提供 Agent 的计算环境——有 shell、有文件系统、有后台进程
- **browser-use**：提供 Agent 的操作能力——能够控制真实浏览器与 Web 应用交互

当一个 Agent 在 Sandboxes 中运行时，它可能需要：
1. 打开浏览器访问一个 Web 应用
2. 填写并提交表单
3. 验证返回结果
4. 下载生成的报告

这个「操作真实浏览器」的能力就是 browser-use 提供的。两者组合在一起，Agent 既有持久化的计算环境，又有与真实世界网站交互的操作能力。

---

## 与 Cursor Self-Hosted 的场景关联

Cursor Self-Hosted Cloud Agents 解决的是「代码不出企业边界」的问题。当一个企业开发者使用 Cursor Self-Hosted Agent 处理任务时，Agent 可能需要：

1. 访问内部 GitLab 查看 PR 状态（browser-use）
2. 在测试环境中验证代码变更（browser-use + Sandboxes）
3. 填写 JIRA 工单描述问题（browser-use）
4. 查看 CI/CD 流水线的状态（browser-use）

browser-use 使得 Agent 能够操作那些没有开放 API 的内部工具，将企业内部的 Web 系统纳入 Agent 的工作流。

---

## 适用场景

**适合使用 browser-use 的场景**：
- 需要 AI Agent 完成 Web 表单填写、数据抓取、报告生成
- 需要验证 UI 变更在真实浏览器中的表现（截图 + 视觉验证）
- 需要将内部 Web 系统（没有 API）纳入 Agent 工作流
- 需要大规模自动化 Web 任务（1,000+ 并发需要 Stealth 能力）

**更适合其他方案的场景**：
- 目标系统有完善的 API → 直接调用 API 效率更高
- 纯服务端 HTML 渲染 → 直接抓取 HTML + 解析更高效
- 任务简单且固定 → 写死选择器比让 Agent 理解网页更稳定

---

## 开源生态位置

browser-use 处于 AI Agent 工具链的**操作层**：

```
模型层：Claude / GPT / Gemini
    ↓ 规划与决策
操作层：browser-use（浏览器）/ API 客户端（REST）/ 文件系统（Sandboxes）
    ↓ 执行
目标系统：Web 应用 / 数据库 / Git 仓库 / CI 流水线
```

这个分层意味着 browser-use 的价值在于**让 Agent 能够触达那些只有 Web UI 的系统**。随着 AI Agent 从「写代码」扩展到「操作真实世界系统」，browser-use 这类操作层工具的重要性会持续提升。

---

## 一手引用

> "Want to skip the setup? Use our cloud for faster, scalable, stealth-enabled browser automation!"
> — [browser-use GitHub README](https://github.com/browser-use/browser-use)

> "We benchmark Browser Use across 100 real-world browser tasks. Full benchmark is open source: browser-use/benchmark."
> — [browser-use GitHub README](https://github.com/browser-use/browser-use)

> "1. Direct your favorite coding agent (Cursor, Claude Code, etc) to Agents.md. 2. Prompt away!"
> — [browser-use GitHub README](https://github.com/browser-use/browser-use)

---

## 链接资源

- [GitHub: browser-use/browser-use](https://github.com/browser-use/browser-use)（92,878 ⭐）
- [Benchmark 数据集](https://github.com/browser-use/benchmark)
- [文档：Open Source Introduction](https://docs.browser-use.com/open-source/introduction)
- [文档：Cloud Documentation](https://docs.cloud.browser-use.com)
- [Cloud Service](https://cloud.browser-use.com)