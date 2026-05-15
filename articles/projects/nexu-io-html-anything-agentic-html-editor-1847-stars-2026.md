# nexu-io/html-anything：让 AI Agent 直接产出消费级 HTML 的编辑器

**推荐核心论点**：当你不再自己敲代码，当你的 Agent 成为主要的内容产出者，「Markdown 作为中间态」的旧范式就应该被淘汰了。HTML Anything 解决了一个实际问题：**如何让 AI Agent 的 HTML 输出直接达到可发布标准，而不需要人类做第二次排版**。它的 Zero API Key 设计（复用本地 coding agent session）和一键多平台分发（WeChat/X/Zhihu）让这个目标变得真正可用。

---

## 这个项目解决了一个长期让人头疼的问题

AI coding agent 写代码很强，但写「让人阅读的内容」产出物往往是 Markdown——你需要手动转换、手动排版、手动适配各个平台。尤其是当你需要把同一份内容发布到微信、X、小红书时，每个平台都要重新排版。

HTML Anything 的核心思路是：**Markdown 是人类写作者友好的格式，HTML 才是读者真正消费的格式**。当 Agent 成为生产者，格式转换的成本应该由工具承担，而不是由人类承担。

---

## 亮点：Zero API Key + 75 Skill Templates + 一键多平台分发

**最聪明的设计：Zero API Key**

它不要求你输入任何 API Key。它在启动时扫描你本地已经登录的 coding agent CLI——Claude Code、Cursor Agent、Codex、Gemini CLI、Copilot CLI、OpenCode、Qwen Coder、Aider——然后直接复用你已有的订阅 session。**边际成本 = $0**。如果你已经订阅了某个 coding agent，用 HTML Anything 不需要额外付费。

> "Markdown is the draft. HTML is what humans read. Your local agent writes it."
> — [HTML Anything README](https://github.com/nexu-io/html-anything)

**75 个 Skill Templates 覆盖 9 种交付形态**

不是给你一堆配置让你自己调，而是给你预定义好的格式约束：

- **prototype**: web / SaaS landing / dashboard / data report
- **deck**: 20 个演示文稿技能（Swiss International、Guizang Editorial、XHS Pastel、Hermes Cyber……）
- **frame**: 10 个视频帧脚本（liquid hero、NYT data chart、glitch title、cinema light-leak……）
- **social**: X / Xiaohongshu / Spotify / Reddit cards
- **office**: PM spec、eng runbook、finance report、HR onboarding、invoice、OKRs
- **doc**: Kami warm-parchment editorial（温暖的羊皮纸质感长文）
- **mockup**: 3D device frame
- **vfx**: text-cursor VFX 效果
- **video**: Hyperframes 6-10 个 1920×1080 序列帧 + 过渡脚本，可直送 Remotion 渲染

每个 skill 都有硬约束：CJK-first 字体栈、8px 基准网格、对比度 ≥ 4.5、必须使用真实数据（anti-AI-slop）。

**一键导出到 WeChat/X/Zhihu**

这是最有价值的能力。不同的平台需要不同的格式：
- **WeChat**: juice-inlined CSS，直接粘贴，不用手动调格式
- **X/Zhihu/Xiaohongshu**: modern-screenshot → 2× PNG → ClipboardItem，直达 tweet composer
- **Standalone**: .html 下载 / .png 高分辨率下载

> "One-click export — juice inlines CSS → WeChat paste with zero re-formatting · modern-screenshot renders the iframe to a 2× PNG → ClipboardItem → drop straight into the tweet composer"
> — [HTML Anything README](https://github.com/nexu-io/html-anything)

---

## 技术原理：五层架构

```
Layer 1: Agent Detection
├─ 自动扫描 PATH 上的 8 个 coding agent CLI
├─ 包括 GUI 进程通常遗漏的路径（~/.local/bin、~/.bun/bin 等）
└─ 检测登录状态，复用已有 session

Layer 2: Skill Picker
├─ 75 个 skill 模板，9 种交付形态
└─ 每个 skill 有硬约束保证产出质量

Layer 3: Streaming SSE
├─ Agent stdout JSON-line → SSE → iframe srcdoc 实时更新
└─ 用户看着页面一行一行渲染，可随时中断重 prompt

Layer 4: Sandboxed Preview
├─ <iframe sandbox="allow-scripts allow-same-origin">
├─ 用户产出的 HTML 在隔离 origin 运行
└─ Cookie/LocalStorage 与主机隔离，Tailwind CDN/Google Fonts 可用

Layer 5: One-Click Export
├─ WeChat: juice-inlined CSS
├─ X/Zhihu/Xiaohongshu: modern-screenshot → 2× PNG
└─ Standalone: .html / .png 下载
```

---

## 竞品对比

| | HTML Anything | 传统 Markdown + 手动转换 | 专业设计工具（Figma/Sketch）|
|---|---|---|---|
| **产出速度** | Agent 生成，一键导出 | Agent 生成 → 手动转换 | 纯手动，AI 辅助有限 |
| **多平台适配** | 一键 9 种形态 | 每个平台手动重排 | 需要导出后重新调整 |
| **API 成本** | $0（复用已有 session）| 每个 agent 单独付费 | 不适用 |
| **设计质量** | Skill 约束保证下限 | 依赖 prompt 质量 | 专业级，但慢 |
| **适用场景** | Agent 产出内容的快速分发 | 简单文档 | 高端品牌物料 |

---

## 适用边界

**适合**：技术博主/内容创作者（一次生成多平台分发）、需要保持设计一致性的系列文档、AI coding agent 用户（想让输出直接达到可发布标准）

**不适合**：需要后端集成的复杂 Web 应用、高度交互的 Web 原型、对格式有独特品牌要求的企业客户

---

## 上手建议

1. **安装**：克隆仓库，`pnpm dev` 本地运行，或者 Vercel 部署 web 层（Agent 始终运行在你本地机器）
2. **选择 Agent**：启动时自动检测 PATH 上的 coding agent CLI，从顶部栏选择一个
3. **选 Skill**：输入 Markdown/CSV/JSON/SQL 等原始内容，选择 skill template（deck/prototype/social 等）
4. **看 Agent 渲染**：SSE 流式渲染，实时看着页面生成，随时中断重新 prompt
5. **一键导出**：选目标平台（WeChat/X/Zhihu），直接粘贴或下载

---

**一手来源**：
- [GitHub: nexu-io/html-anything](https://github.com/nexu-io/html-anything)（1,847 Stars，Apache-2.0 License）
- [nexu-io/open-design](https://github.com/nexu-io/open-design)（上游设计系统，40k Stars，200+ contributors）
- [Anthropic Claude Code 团队停止使用 Markdown 的声明](https://x.com/trq212/status/2052809885763747935)（核心产品理念的官方确认）

---

*关联文章*：[「AI Agent 时代的 HTML 优先编辑新范式」](../practices/ai-coding/nexu-io-html-anything-agent-era-html-first-editor-2026.md)（深度分析同一主题）