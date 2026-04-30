# Vercel Agent Browser：Rust 原生浏览器自动化 CLI

## 项目概述

**agent-browser** 是 Vercel Labs 出品的浏览器自动化 CLI 工具，使用 Rust 原生实现，提供快速、可靠的浏览器控制能力，专门为 AI Agent 场景设计。

当前 Stars：31,069。

## 核心能力

**安装灵活性**：支持 npm 全局安装、项目本地安装、Homebrew、Cargo 源码编译多种方式。无需 Playwright 或 Node.js 运行时即可运行 daemon。

**命令体系完整**：
- 页面导航与元素交互：`open`、`click`、`fill`、`type`、`hover`、`scroll` 等
- 信息获取：`snapshot`（生成带引用的无障碍树，最适合 AI 理解）、`get text/html/value/attr/title/url/count/box/styles`
- 状态检查：`is visible/enabled/checked`
- 语义化定位：`find role button click --name "Submit"`、`find label "Email" fill`
- 批量执行：`batch` 命令支持多步骤工作流单次调用，JSON stdin 模式避免重复进程启动开销
- 浏览器设置：`viewport`、`device`（设备模拟）、`geo`（地理位置）、`headers`、`credentials`、`media`
- 网络控制：`network route`（请求拦截/mock）、`network requests`（查看追踪请求）、`network har`
- 标签页管理：多标签支持，带 label 的标签页切换
- 剪贴板与鼠标控制
- Cookie 与 Storage 管理
- AI 聊天控制：`agent-browser chat "<instruction>"` 单次指令式，或 `chat` 进入交互 REPL

## 技术亮点

**snapshot 无障碍树**：最值得关注的特性是 `snapshot` 命令，它生成的是一个**带编号引用的无障碍树**（accessibility tree），而不是 DOM 快照。这意味着 AI Agent 可以用 `@e2` 这样的引用来精确定位元素，比 CSS 选择器更稳健（不受页面结构微小变化影响）。

**批量执行模式**：`batch` 命令解决了多次调用 CLI 的进程启动开销问题，特别适合 AI Agent 执行多步骤工作流。

**Chrome for Testing**：默认从 Google 官方 Chrome for Testing 频道下载 Chrome，同时也支持检测已有的 Playwright/Puppeteer/Chrome/Brave 安装。

## 与 Playwright/Puppeteer 的定位差异

| 维度 | agent-browser | Playwright | Puppeteer |
|------|-------------|-----------|-----------|
| **实现语言** | Rust（CLI） | TypeScript | Node.js |
| **AI Agent 友好** | ✅ 原生设计 | 需封装 | 需封装 |
| **snapshot 引用** | ✅ 内置 | ❌ | ❌ |
| **启动速度** | 极快 | 快 | 快 |
| **生态丰富度** | 发展中 | 成熟 | 成熟 |

## 适用场景

- AI Agent 需要执行复杂的多步骤浏览器操作
- 需要原生的无障碍树快照给 AI 理解页面
- 需要快速、轻量的浏览器自动化而非完整测试框架
- 作为 MCP 工具后端控制浏览器

## 一句话推荐

agent-browser 是目前最 AI-native 的浏览器自动化 CLI，Rust 原生实现保证了速度和可靠性，snapshot 引用机制是给 AI 用的设计而非给人类用的，适合集成到 AI Agent 工作流中。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/vercel-labs/agent-browser`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：10/15
