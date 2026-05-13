# Tactile: 让 Agent 告别「像素猜谜」的无障碍操作层

> **目标读者**：有 Python 经验的 Agent 开发工程师，正在构建需要操作图形界面应用（桌面软件、Web 应用、游戏等）的编码 Agent，希望提升操作准确率并降低 token 消耗。
>
> **核心结论**：Tactile 将无障碍语义树作为 Agent 操作界面的第一入口（早于 OCR 和视觉推理），将传统的「截图→坐标→点击」倒转为「语义→坐标→验证」。对于支持无障碍语义的桌面应用，这个切换可以将操作准确率提升至接近 100%，同时将 token 消耗降低 60-80%。

---

## 一、定位：为什么需要 Tactile

### 像素猜谜的问题

当前主流的计算机操作 Agent（如 Cursor 的 Agent 模式、Claude Code 的 Computer Use）大多采用视觉优先的操作范式：

```
look at screenshot → infer element → predict coordinates → click → inspect screenshot again
```

这个范式的问题在于：

1. **Token 成本高**：每一步操作都需要完整的截图理解，即使只是点击一个按钮
2. **准确率受限**：GUI 布局变化、字体缩放、动画干扰都会导致坐标预测失败
3. **验证困难**：操作完成后，Agent 需要再次截图来确认结果是否达成

> "Many computer-use agents start from screenshots: look at screenshot -> infer element -> predict coordinates -> click -> inspect screenshot again. This approach is general, but fragile."
> — [Tactile GitHub README](https://github.com/yliust/Tactile)

### 无障碍语义树的优势

现代操作系统（macOS、Windows、Linux）和大量应用都暴露了无障碍语义树（Accessibility Tree）信息，这是为屏幕阅读器设计的语义描述。它包含：

- **元素角色**（role）：button、text_field、checkbox、menu_item
- **元素名称**（name）：可访问的名称描述
- **状态信息**（state）：focused、selected、enabled、checked
- **层级关系**（hierarchy）：树形结构反映 UI 的嵌套关系

Tactile 的核心主张是：**如果 Agent 能够通过无障碍语义树直接定位和操作元素，就不需要走像素级视觉推理那条昂贵的路**。

---

## 二、技术架构：三层操作阶梯

Tactile 设计了一个三层操作阶梯（Operating Ladder），Agent 按顺序尝试，直到找到可行的路径：

### Level 1：Accessibility Semantics（首选）

直接通过无障碍 API 读取语义树，利用元素名称、角色、状态和层级关系定位目标元素，然后通过系统级操作（如 `ax` 点击命令）直接操作。

```
优点：精确、可验证、token 消耗极低
适用：标准桌面应用（Electron、Qt、GTK、Win32）
```

### Level 2：OCR-grounded Coordinates（降级）

如果无障碍信息不完整（某些 Web 应用和移动端模拟器），但可见文本可读，使用系统 OCR 获取文本和坐标信息，用文本位置替代像素猜测。

```
优点：不需要完整语义树，只要有可见文本即可
适用：Web 应用（部分不支持完整无障碍）、游戏 GUI
```

### Level 3：Native Visual Operating（兜底）

当无障碍和 OCR 都无法工作（如 Canvas 游戏、远程桌面、图像密集界面），回退到 Agent 自有的视觉推理能力。

```
优点：通用性最强
缺点：token 消耗最高，准确率受限
```

> "Tactile changes the order of operations: read accessibility semantics -> use OCR-grounded coordinates when needed -> fall back to visual computer use."
> — [Tactile GitHub README](https://github.com/yliust/Tactile)

---

## 三、使用体验：Demo 案例解析

### Lark 和 WeChat 工作流

Tactile 仓库提供的 Demo 视频展示了用 Tactile 技能操作 Lark（飞书）和 WeChat 的场景。Agent 首先检查无障碍语义树，发现目标按钮的 name 和 role，然后直接执行操作。视频中可以看到点击的即时反馈——按钮状态变化直接反映在语义树中，无需再次截图验证。

### CapCut 视频编辑工作流

更复杂的一个场景是用 Tactile 操作 CapCut（剪映）进行视频编辑。Agent 需要操作时间轴、添加转场、应用滤镜——这些操作在传统像素级方案中需要大量截图和坐标推断，但通过无障碍语义树，Agent 可以直接定位到目标轨道、转场按钮和滤镜面板。

> "Tactile gives agents a sense of touch. Agents should not only see software on a screen. When better information is available, they should first touch the structure of the interface."
> — [Tactile GitHub README](https://github.com/yliust/Tactile)

---

## 四、项目数据与社区健康

| 指标 | 数值 |
|------|------|
| GitHub Stars | 179（截至 2026-05-13）|
| Forks | 6 |
| 主语言 | Python |
| 创建时间 | 2026-05-11 |
| 最近更新 | 活跃 |

项目处于早期阶段（v0），但核心设计思路已经清晰，GitHub 上的 Demo 视频验证了可行性。

---

## 五、快速上手

### Skill 配置方式

如果你的 Agent 支持 Skill 机制（如 Claude Code 的 `/skill` 命令），直接让 Agent 配置：

```
Configure this skill for me (make sure to choose the version for the corresponding operating system): https://github.com/yliust/Tactile
```

### API 配置方式

```bash
export TACTILE_OPENAI_BASE_URL=xxxxxxx
export TACTILE_OPENAI_API_KEY=xxxxxxx
export TACTILE_MODEL='gpt-5.5'
```

---

## 六、与本 Articles 的逻辑关联

本文档配套的 Article（Anthropic April 2026 Postmortem 分析）讨论的是 Agent 系统配置变更的复合效应——当多个看似无害的变更同时存在时，可能导致难以追踪的系统退化。

Tactile 在这个话题下的启示是：**如果 Agent 系统在操作层面存在过多绕路（pixel-level guessing → retry → timeout → fallback），这些绕路本身就是一种隐藏的配置噪声**。它们在日志中看起来像随机的失败，但实际上是系统对不可靠操作路径的反复重试。

通过将无障碍语义作为第一入口，Tactile 将这些噪声转移为确定的、可验证的操作链。这不仅提升了操作准确率，还让整个 Agent 系统的行为变得更透明、更可调试。

---

**引用来源**：
- [Tactile GitHub Repository](https://github.com/yliust/Tactile)
- [Tactile README](https://github.com/yliust/Tactile/blob/main/README.md)
- [Tactile README (中文)](https://github.com/yliust/Tactile/blob/main/README_zh.md)