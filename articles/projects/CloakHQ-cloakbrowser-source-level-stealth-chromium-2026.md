# CloakBrowser：源码级反检测 Chromium，Agent 浏览器自动化的隐形斗篷

## 一、定位破题

**CloakBrowser** 是一个源码级修改的 Chromium 分支，专门解决 AI Agent 在浏览器自动化场景中被反爬虫系统拦截的核心问题。

它不是通过配置文件修补或 JavaScript 注入来规避检测——而是在 **C++ 源码层面修改浏览器指纹**，让任何检测系统看到的是一个「真实的普通浏览器」。

**场景锚定**：当你的 Agent 需要操作 Web 界面（如社交媒体自动化、数据采集、登录态页面抓取），却频频遭遇 Cloudflare Turnstile、人机验证弹窗或 FingerprintJS 检测时，CloakBrowser 就是答案。

**差异化标签**：**唯一在源码层而非配置层解决浏览器指纹问题的开源方案**。

---

## 二、体验式介绍

### 「三行代码，三十秒」的反检测集成

如果你已经在用 Playwright，迁移到 CloakBrowser 的成本是 **三行代码改动**：

```python
# 之前
from playwright.sync_api import sync_playwright
browser = pw.chromium.launch()

# 之后
from cloakbrowser import launch
browser = launch()
```

**剩余代码完全不变**——你继续使用 `new_page()`、`goto()`、`click()`，但检测系统看到的不再是 `HeadlessChrome`，而是一个带有完整 Canvas 指纹、WebGL 渲染、真实插件列表和人工级鼠标轨迹的标准 Chrome 会话。

### humanize=True：一键开启人类行为模拟

最让笔者印象深刻的功能是 `humanize=True` 参数：

```python
browser = launch(humanize=True)
```

开启后，所有鼠标移动使用 **Bézier 曲线**（而非直线），键盘输入模拟逐字符随机延时，滚动操作带有真实用户的「停顿-加速-减速」模式。

这个功能解决了一个常见困境：Agent 的操作在逻辑上是正确的（点击正确的按钮、填写正确的字段），但在时序模式上暴露了「机器人特征」，被行为分析系统识别。

### 57 个源码级指纹补丁

CloakBrowser 的核心是 **57 个针对 Chromium 源码的 C++ 补丁**，覆盖的检测向量包括：

| 检测维度 | Stock Playwright | CloakBrowser |
|---------|----------------|-------------|
| `navigator.webdriver` | `true` | `false` |
| `navigator.plugins.length` | `0` | `5` (真实插件列表) |
| `window.chrome` | `undefined` | `object` |
| Canvas 指纹 | 统一噪声 | 真实渲染 |
| WebGL 指纹 | 可识别自动化 | 真实硬件报告 |
| reCAPTCHA v3 得分 | 0.1 (bot) | **0.9 (human)** |
| Cloudflare Turnstile | Fail | **Pass** |
| TLS 指纹 | JA3/JA4 不匹配 | 与 Chrome 完全一致 |

---

## 三、拆解验证

### 3.1 技术原理：为什么源码级补丁优于 JS 注入

目前主流的反检测方案有三种技术路线：

| 方案 | 原理 | 优点 | 致命缺陷 |
|------|------|------|---------|
| **配置文件修补** | 修改 Chrome flags | 简单 | Chrome 更新后立即失效 |
| **JS 注入** | `playwright-stealth` 等脚本 | 灵活 | 注入的 JS 本身可被检测；新版 Chrome 不断封堵 |
| **C++ 源码修改** | 直接修改 Chromium 源码并编译 | 底层真实；不被 JS 层检测；自动更新兼容新版 | 需要维护自己的 Chromium 分支 |

CloakBrowser 选择第三条路。这意味着它维护了一个独立的 Chromium 分支，每次 Google 发布安全更新时，CloakBrowser 团队会将所有 57 个补丁 Rebase 到新版。

**这本质上是一个「持续 Rebase」的工程工作**，而非一次性的解决方案。

### 3.2 架构设计：薄包装 + 厚补丁

CloakBrowser 的架构非常清晰：

```
┌─────────────────────────────────────┐
│  Python / JavaScript 包装层          │
│  (launch() / launch_context() 等)   │
├─────────────────────────────────────┤
│  Playwright / Puppeteer API          │
│  (标准接口，完全兼容)                │
├─────────────────────────────────────┤
│  CloakBrowser Chromium Binary       │
│  (57 个 C++ 指纹补丁 + 人类行为模拟) │
└─────────────────────────────────────┘
```

用户接触的是标准 Playwright API，但底层运行的是修改过的 Chromium。二进制文件在首次运行时自动下载（约 200MB），带有 SHA-256 校验和验证。

### 3.3 竞品对比

| 特性 | Playwright | playwright-stealth | undetected-chromedriver | Camoufox | CloakBrowser |
|------|-----------|-------------------|------------------------|---------|-------------|
| reCAPTCHA v3 得分 | 0.1 | 0.3-0.5 | 0.3-0.7 | 0.7-0.9 | **0.9** |
| Cloudflare Turnstile | Fail | Sometimes | Sometimes | Pass | **Pass** |
| 补丁层级 | None | JS 注入 | Config | C++ (Firefox) | **C++ (Chromium)** |
| Chrome 更新兼容性 | N/A | 频繁失效 | 频繁失效 | 一般 | **Active 维护** |
| Playwright API 兼容 | Native | Native | No | No | **Native** |

---

## 四、行动引导

### 快速上手（3 步内可跑起来）

**Step 1：安装**
```bash
pip install cloakbrowser
# 或
npm install cloakbrowser playwright-core
```

**Step 2：替换导入**
```python
from cloakbrowser import launch
browser = launch()
page = browser.new_page()
page.goto("https://protected-site.com")
```

**Step 3：（可选）开启人类行为模拟**
```python
browser = launch(humanize=True, human_preset="careful")
```

### 代理集成

CloakBrowser 原生支持 SOCKS5 代理，且可配合 GeoIP 自动从代理出口 IP 检测时区和语言设置：

```python
browser = launch(
    proxy="socks5://user:pass@proxy:1080",
    geoip=True  # 自动从代理 IP 设置时区和 locale
)
```

### 持久化会话

如果需要保持登录态跨会话运行：

```python
from cloakbrowser import launch_persistent_context

ctx = launch_persistent_context("./my-profile")
page = ctx.new_page()
page.goto("https://example.com")
ctx.close()  # cookies 和 localStorage 自动保存
```

### 贡献与路线图

CloakBrowser 是一个活跃维护的开源项目，在 GitHub 上持续更新。有意贡献者可关注其 [CHANGELOG.md](https://github.com/CloakHQ/CloakBrowser/blob/main/CHANGELOG.md) 了解当前状态。赞助可通过 [Ko-fi](https://ko-fi.com/cloakhq) 支持。

---

## 关联主题：与 Cursor Cloud Agent 开发环境的互补

Cursor 发布的「Cloud Agent 开发环境」文章中提到：

> "An agent that can write code but can't run tests, query services, or reach APIs cannot close the loop on its work."

Browser-based Agent 面临同样的困境：**Agent 能够执行 Web 操作，但如果操作被反爬虫系统拦截，就无法闭环工作**。

CloakBrowser 解决的是这个「Browser Agent 能力闭环」问题——它让 Agent 能够真正与目标网站交互，而非被挡在第一层验证之外。

配合 Cursor 的云端开发环境和 Docker 配置能力，CloakBrowser 可以构建一个**完整的浏览器自动化 Agent 运行时**，覆盖代码执行、Web 操作和结果验证的全链路。

---

> **项目信息**
> - GitHub: [CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser)
> - 语言：Python + JavaScript/TypeScript
> - 核心依赖：Chromium（自维护分支）
> - 许可证：MIT（开源）
> - PyPI：`pip install cloakbrowser`
> - NPM：`npm install cloakbrowser`
> - Docker：`docker run --rm cloakhq/cloakbrowser cloaktest`