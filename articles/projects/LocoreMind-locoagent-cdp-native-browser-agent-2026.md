# LocoreMind/locoagent：CDP 原生浏览器 Agent 的工程范本

> **这篇文章解决的问题**：当大多数浏览器 Agent 还在用 Playwright/Selenium 的高级 API 模拟用户操作时，locoagent 选择了直接走 CDP（Chrome DevTools Protocol）——这条路为什么是正确的，以及这对 Browser Agent 架构设计意味着什么。

GitHub 上一个 136 Stars 的项目，[LocoreMind/locoagent](https://github.com/LocoreMind/locoagent)。它做的事情一句话概括：**用 CDP 协议直接控制浏览器的 Agent 框架**。

---

## 为什么这不是又一个 Playwright Wrapper

大多数现有的浏览器自动化框架——Playwright、Puppeteer、WebDriver——在 API 设计上都是「模拟人操作」：点击一个按钮、填写一个表单、等待元素出现。这些 API 对于自动化测试是合理的，但它们对于 Agent 来说有一个根本性的问题：**语义层太厚**。

Agent 需要的不是「模拟点击」，Agent 需要的是**精确控制 + 完整观测**。

CDP 协议直接暴露的是浏览器的内部状态：DOM 树、网络请求、JavaScript 执行上下文、渲染层信息。Playwright 在 CDP 之上包装了一层「人类友好的」API，这层包装让普通人容易上手，但也让 Agent 失去了一些关键能力：

- 无法直接观测网络请求的详细结构
- 无法直接操控 JavaScript 执行上下文
- 无法精确控制哪些交互事件被触发

locoagent 的设计选择了 CDP 路线，这意味着 Agent 拿到的是**完整的浏览器控制能力**，而不是被抽象层过滤过的子集。

---

## 实际场景里的差异

举一个具体例子：当 Agent 需要抓取一个单页应用（SPA）里的动态内容时，用 Playwright 的典型做法是「等元素出现」。但「等多久」是个经验值——设短了内容还没加载，设长了浪费时间。

用 CDP 的做法是：Agent 可以直接查询「当前 DOM 里的网络请求状态」，精确知道数据什么时候到达，然后才触发下一步操作。这不是微小的改进，这是**观测精度**的质变。

---

## 对 Browser Agent 架构设计的启示

locoagent 的存在实际上在说明一件事：**浏览器 Agent 的最终形态会收敛到 CDP 层**。就像操作系统的发展路径最终会让虚拟化方案收敛到硬件虚拟化支持一样，浏览器 Agent 的架构演进也在往「协议层直接控制」收敛。

这不是说 Playwright 会被淘汰——它对于人类使用者仍然是最友好的 API。但对于 Agent 系统，CDP 是更精确的控制平面。这也是为什么 OpenAI 的 Codex 和 Anthropic 的 Claude Code 在云端浏览器执行时，都在往底层协议方向优化。

---

## 笔者的判断

locoagent 目前的 Stars 不高（136），这说明它还处于早期阶段，社区还没充分注意到。但从架构选择上看，这是一个值得关注的路线验证：**CDP 原生路线在 Browser Agent 领域，可能是比 Playwright 封装路线更接近终态的选择**。

如果你在构建需要精确控制浏览器的 Agent 系统，建议关注这个方向。

---

> **引用来源**
> - [LocoreMind/locoagent GitHub README](https://github.com/LocoreMind/locoagent)
> - [Chrome DevTools Protocol 官方文档](https://chromedevtools.github.io/devtools-protocol/)