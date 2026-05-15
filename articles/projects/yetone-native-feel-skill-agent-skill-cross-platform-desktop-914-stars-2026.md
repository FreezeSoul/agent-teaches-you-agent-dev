# yetone/native-feel-skill：一个 Skill 定义如何让 Agent 输出「像本地原生应用」

## 这个项目解决了一个长期让人头疼的问题

当 Agent 生成跨平台桌面应用时，最大的噩梦不是「跑不起来」，而是「跑起来了，但感觉哪里不对劲」——按钮位置不符合平台惯例、滚动行为像 Web 而不是原生、快捷键和系统菜单完全不工作。**native-feel-skill** 是一个专注于让 AI 生成的应用「看起来像本地人写的」的 Agent Skill，核心价值在于它把「什么让应用感觉原生」这个隐性知识变成了一套可执行的审计清单和架构约束。

---

## 为什么这个方向值得单独推荐

### 现有的 Agent 生成代码的最大盲区

当前 AI Coding 工具在生成 UI 代码时，主要优化目标是**功能正确性**和**视觉外观**，但忽视了一个关键维度：**平台交互范式**。一个 Windows 原生应用应该有标准的窗口 decorations、系统菜单、和 Windows 95 就确立的交互惯例；macOS 应用应该遵守 Human Interface Guidelines，有真正的原生控件而不是仿制的。

Agent 生成的代码倾向于「用 Web 技术栈实现看起来像原生的外观」，而忽略了：

- 窗口管理行为（最小化/最大化/关闭的预期行为）
- 原生控件映射（不是 `<div>` 模拟的按钮，而是真正的 NSButton / Win32 Button）
- 滚动行为和惯性滚动
- 菜单栏和系统托盘集成
- 快捷键的系统级处理

### 这个项目的核心贡献：八条架构原则 + 75 项交付审计

作者从 Raycast Beta.app 的逆向工程和 2.0 deep-dive 中提炼出**八个架构原则**，指导 Agent 如何生成真正原生的跨平台应用：

1. **每个平台有且仅有一个窗口装饰系统**：Agent 不能混用窗口框架
2. **WebView 是逃生舱，不是默认渲染目标**：WebView 只用于复杂内容，原生控件负责 shell
3. **平台快捷键必须使用平台 API 注册**：不是 `keydown` 事件监听，是 `RegisterHotKey()` / `MASShortcut`
4. **滚动必须使用原生滚动行为**：不能自己实现 inertia scroll
5. **平台菜单栏优先于自定义 UI**：macOS 的 Menu Bar 和 Windows 的 Ribbon/Command Bar 是第一公民
6. **窗口状态必须持久化到本地**：Agent 生成的代码经常忘记记住窗口位置和大小
7. **无障碍（Accessibility）是架构约束，不是附加功能**：原生控件天然支持，Web 模拟控件需要额外工作
8. **测试必须覆盖真实平台行为，不是视觉截图**：截图测试无法验证滚动、焦点、快捷键

75 项 Ship Audit 则是一套可执行的交付标准清单——相当于一个「这个应用感觉像本地人写的」的检查清单。

---

## 与本轮 Articles 的关联

本轮 Articles 分析了 [OpenAI Codex Windows 沙箱架构](./openai-codex-windows-sandbox-architecture-acl-limits-independent-user-2026.md)，其中提到 Codex 的核心挑战是**在 Windows 缺乏原生沙箱原语的情况下构建有效安全边界**。这个难题的根源之一是：Windows 的平台隔离能力远远落后于 macOS/Linux，而应用需要通过大量非标准手段（ACL、合成 SID、受限 token）来补偿。

**native-feel-skill 揭示了同一个平台能力缺口的另一个维度**：不仅安全边界需要人工构建，连「如何让生成的应用感觉原生」也需要 Agent 有明确的架构约束来弥补平台差异。

两者共同指向一个结论：**在桌面应用开发领域，平台的抽象能力远未成熟**，无论是安全隔离还是 UI 范式，Agent 都需要比在 Web 开发中更明确地依赖平台特定知识。

---

## 技术实现亮点

### WebKit/WebView2 生存指南

项目包含了对 WebView 在跨平台场景中行为的深度分析：

> "WebView is a survival guide, not a rendering target." 

核心原则：当 WebView 作为内容渲染容器时，Agent 必须明确知道：
- macOS WebView2（WKWebView）和 Windows WebView2 的 API 差异
- 两者与平台快捷键系统的集成方式完全不同
- WebView 滚动与原生滚动的性能边界

### 四层架构

```
┌─────────────────────────────────────────────┐
│  Layer 1: Window Shell (原生窗口框架)         │
│  - macOS: NSWindow + NSWindowController    │
│  - Windows: Win32 API / WinUI 3            │
├─────────────────────────────────────────────┤
│  Layer 2: Navigation & Shortcuts (导航+快捷键)│
│  - 平台快捷键注册系统                        │
│  - 菜单栏集成                               │
├─────────────────────────────────────────────┤
│  Layer 3: Content Rendering (内容渲染)       │
│  - WebView (复杂内容) / 原生控件 (简单内容)   │
├─────────────────────────────────────────────┤
│  Layer 4: Platform Integration (平台集成)     │
│  - 系统通知、拖放、剪贴板                    │
│  - 原生文件对话框、颜色选择器                │
└─────────────────────────────────────────────┘
```

这个分层的好处是：**每层都可以独立替换**，不需要用 Web 技术栈替换整个应用。

---

## 适合谁来用

**有 Python 基础、使用 Agent 生成桌面应用、但生成的 app「总觉得哪里不对」的开发者。**

这个 Skill 不是教你「如何用 Electron 打包 Web 应用」，而是教你「在 Agent 生成代码时，如何通过架构约束让输出天然接近平台原生行为」。

对于正在用 Claude Code / Cursor / Codex 构建桌面工具的团队，这个 Skill 提供了一套**预防性架构约束**——与其让 Agent 生成后再花大量时间改「感觉不对」的地方，不如在 Skill 层面就约束好生成方向。

---

## 竞品对比

| 项目 | 方向 | 特点 |
|------|------|------|
| **native-feel-skill** | 架构约束 + 交付审计 | 从平台交互范式出发，75项清单覆盖感知质量 |
| **anthropics/skills** | Skill 格式标准化 | SKILL.md 极简格式，定义做什么，不定义怎么做 |
| **Cursor Bootstrapping** | 框架自举 | 用现有技能系统让 Composer 自我安装 |

---

## 引用

> "Eight architectural tenets, four-layer architecture, WebKit/WebView2 survival guide, 75-item ship audit."
> — [yetone/native-feel-skill README](https://github.com/yetone/native-feel-skill)

> "An Agent Skill for designing cross-platform desktop apps that feel native — distilled from Raycast's 2.0 deep-dive and reverse engineering of Raycast Beta.app."
> — 同上

---

## 下一步

1. 安装 Skill：`claude skill install https://github.com/yetone/native-feel-skill`
2. 在生成桌面应用前先加载 Skill，让 Agent 知道「原生感」的具体约束
3. 用 75 项 Ship Audit 检查生成结果，识别架构层面的偏差

---

*标签：agent-skill、desktop-development、cross-platform、architecture*
*来源：[GitHub - yetone/native-feel-skill (914 stars)](https://github.com/yetone/native-feel-skill)*
*关联文章：[OpenAI Codex Windows 沙箱架构](./openai-codex-windows-sandbox-architecture-acl-limits-independent-user-2026.md)*