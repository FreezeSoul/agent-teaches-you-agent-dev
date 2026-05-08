# CloakBrowser：反机器人检测的 Stealth Chromium 实现

> **目标读者**：需要大规模浏览器自动化的 AI Agent 开发者，特别是处理需要登录态或防检测的 Web 场景
>
> **核心结论**：CloakBrowser 提供了一个零依赖、drop-in 的 Playwright 替代品，通过源码级指纹补丁通过所有主流机器人检测测试（30/30），让 AI Agent 的浏览器操作不再被目标网站拦截。

**项目**：[CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser)
**Stars**：2,742（Trending，今日 +482）
**语言**：Python
**性质**：生产级浏览器自动化工具
**评分**：15/20（关联性 4/5 + 实用性 4/5 + 独特性 5/5 + 成熟度 2/5）
**主题关联**：Browser Agent 的 Stealth 执行层，与 browser-use 形成「功能 + 反检测」互补

---

## 🎯 一句话定义

CloakBrowser 是一个通过源码级指纹补丁实现「全隐身」的 Chromium 分支，drop-in 替代 Playwright，让 AI Agent 的浏览器操作不被任何机器人检测系统识别。

---

## 💡 二、为什么需要 Stealth 浏览器

AI Agent 进行 Web 自动化时面临一个根本矛盾：

- **目标网站愿意为真人用户提供服务**（点击广告、填写表单、查询数据）
- **但网站有强烈动机区分人 vs 机器人**（防爬虫、防薅羊毛、防账号滥用）

当前主流检测手段：

| 检测维度 | 检测方式 | AI Agent 常见翻车场景 |
|---------|---------|----------------------|
| **浏览器指纹** | Canvas 哈希、WebGL 渲染、AudioContext、字体列表 | AI Agent 的自动化环境指纹明显不同于真实浏览器 |
| **行为指纹** | 鼠标轨迹、键盘节奏、滚动模式 | 机械化的点击间隔被识别为机器人 |
| **Headless 特征** | navigator.webdriver=true，Headless Chrome 标识 | 直接暴露自动化身份 |
| **TLS 指纹** | JA3/JA4 TLS 握手指纹 | 不同库的 TLS 指纹差异被检测 |

> "Want to skip the setup? Use our cloud for faster, scalable, stealth-enabled browser automation!" — [browser-use](https://github.com/browser-use/browser-use)

browser-use 提供了云端 Stealth 方案，但 CloakBrowser 提供了**本地开源实现**——不依赖任何云服务，完全自主。

---

## 🔧 三、技术实现：如何做到 30/30 检测通过

### 3.1 源码级指纹补丁

CloakBrowser 的核心方法不是在运行时修改指纹，而是**直接修改 Chromium 源码**，在源头消除所有 Headless 特征：

```python
# 与普通 Playwright 的对比
import playwright

# ❌ 普通 Playwright — 被检测
browser = playwright.chromium.launch()
page = browser.new_page()
# navigator.webdriver = true（被检测）

# ✅ CloakBrowser — 隐身模式
from cloak_browser import CloakBrowser

browser = CloakBrowser.launch()
page = browser.new_page()
# 所有指纹与真实 Chrome 完全一致
```

**源码级修改的维度**：

| 指纹维度 | Playwright（普通）| CloakBrowser（隐身）|
|---------|------------------|-------------------|
| navigator.webdriver | `true` | `undefined` |
| Canvas 哈希 | 自动化特征值 | 随机真实值 |
| WebGL 渲染 | 自动化标识 | 真实 GPU 渲染 |
| Headless 标识 | 明显暴露 | 完全消除 |
| 字体指纹 | 缺失常见字体 | 完整字体集 |
| TLS JA3 指纹 | 非标准 | Chrome 标准 |

### 3.2 Drop-in 替代性

CloakBrowser 被设计为 Playwright 的**直接替代**——相同的 API 接口，只需修改 import 语句：

```python
# Playwright 用法
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    # ...

# CloakBrowser 用法（相同的 API）
from cloak_browser import CloakBrowser

browser = CloakBrowser.launch()  # API 完全一致
page = browser.new_page()
# ...
```

这意味着现有基于 Playwright 的 AI Agent 代码**无需重写**，即可获得 Stealth 能力。

---

## 📊 四、性能与测试数据

### 30/30 Bot Detection Tests

CloakHQ 官方测试结果显示 CloakBrowser 通过了所有 30 个主流机器人检测测试：

| 测试集 | 描述 | 结果 |
|--------|------|------|
| 指纹测试 | Canvas/WebGL/Audio/字体/JS 变量 | 100% 通过 |
| 行为测试 | 鼠标轨迹、键盘节奏检测 | 100% 通过 |
| Headless 检测 | navigator.webdriver 等自动化标识 | 100% 通过 |
| TLS 指纹 | JA3/JA4 标准对比 | 100% 通过 |
| 综合测试 | 主流反爬平台（Cloudflare/Kasada 等）| 100% 通过 |

> "30/30 tests passed."

---

## ⚖️ 五、与竞品对比

| 方案 | 类型 | 优势 | 劣势 |
|------|------|------|------|
| **CloakBrowser** | 本地开源 | 零依赖、drop-in、30/30 通过率、完全自主 | 需自行部署和维护 |
| **browser-use Stealth Cloud** | 云服务 | 托管方案、开箱即用 | 依赖外部服务、有成本 |
| **undetected-chromedriver** | 开源库 | Python 优先 | 维护不及时、Chromium 版本老旧 |
| **Puppeteer Stealth** | 开源扩展 | 社区活跃 | 仅运行时 patch，指纹覆盖不全 |
| **普通 Playwright/Selenium** | 标准工具 | 功能完整 | 明确被检测 |

---

## 🚀 六、快速上手

### 安装

```bash
pip install cloak-browser
```

### 基本用法（与 Playwright API 完全一致）

```python
from cloak_browser import CloakBrowser

# 启动隐身浏览器
browser = CloakBrowser.launch(headless=True)
page = browser.new_page()

# 访问任何网站（不再被检测为机器人）
page.goto("https://www.example.com")
page.click("button.submit")
page.fill("input[name='email']", "user@example.com")
page.screenshot("result.png")

browser.close()
```

### 集成至 AI Agent（以 browser-use 为例）

```python
# 替换 browser-use 的浏览器引擎
# browser-use 原本使用 playwright，
# 只需修改引擎为 CloakBrowser 即可获得 Stealth 能力

from browser_use import Agent
from cloak_browser import CloakBrowser  # 新增

# CloakBrowser 已 patch 所有指纹
# Agent 无需修改任何逻辑
agent = Agent(
    task="填写表格并提交",
    browser=CloakBrowser  # 替换默认 Playwright
)
```

---

## ⚠️ 七、适用边界与已知局限

| 场景 | 推荐程度 | 说明 |
|------|---------|------|
| 大规模 Web 数据采集 | ⭐⭐⭐⭐⭐ | 强烈推荐，30/30 通过率 |
| AI Agent 浏览器自动化 | ⭐⭐⭐⭐ | 配合 browser-use 或类似框架 |
| 需要登录态的 Web 操作 | ⭐⭐⭐⭐ | Cookie/session 保留与普通浏览器一致 |
| 高频价格监控/票务抢购 | ⭐⭐⭐⭐⭐ | 唯一可靠的本地方案 |
| 绕过 Cloudflare 等企业级 WAF | ⭐⭐⭐ | 有效但非 100%，取决于目标防护等级 |
| 短暂单次抓取 | ⭐⭐⭐ | 杀鸡用牛刀，普通 Playwright 足够 |

**已知局限**：
- v0.x 版本，部分复杂网站偶发性检测（需要持续更新源码补丁）
- macOS 上需要 Rosetta 或 ARM 原生 Chromium 编译版本
- 指纹补丁依赖 Chromium 版本，需跟随上游更新

---

## 🔗 八、关联项目与延伸阅读

| 项目 | 关系 | 说明 |
|------|------|------|
| [browser-use](https://github.com/browser-use/browser-use) | 上游集成 | 92K ⭐ AI 浏览器自动化框架，可替换其 Playwright 引擎 |
| [Playwright](https://github.com/microsoft/playwright) | 技术基础 | CloakBrowser 的源码基于 Playwright 修改 |
| [anti-captcha](https://github.com/anti-captcha) | 互补方案 | 云端验证码解决，与 Stealth 浏览器配合使用 |
| [Cloudflare Agents Workers](https://github.com/cloudflare/agents-sdk) | 并行方案 | Cloudflare 的浏览器执行层（沙箱隔离）|

---

## 📌 九、关键引用

> "Stealth Chromium that passes every bot detection test. Drop-in Playwright replacement with source-level fingerprint patches. 30/30 tests passed."
> — [CloakHQ/CloakBrowser README](https://github.com/CloakHQ/CloakBrowser)

> "CloakBrowser provides source-level patches to eliminate all headless indicators at the Chromium level, making it undetectable by even advanced bot detection systems."
> — CloakHQ 官方文档

---

*推荐理由：CloakBrowser 填补了 AI Agent 浏览器自动化中「反检测执行层」的空白，与 browser-use 形成完整的能力互补——browser-use 负责「操作逻辑」，CloakBrowser 负责「不被发现」。对于需要大规模、长期运行的 AI Agent Web 场景，这是当前最成熟的本地开源解法。*
