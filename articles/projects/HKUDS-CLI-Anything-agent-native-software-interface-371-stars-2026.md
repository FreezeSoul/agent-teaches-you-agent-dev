# HKUDS/CLI-Anything：让所有软件都变成 Agent-Native 的接口

**一句话亮点**：将任何软件通过一行命令自动转换成 Agent 可用的 CLI 工具，让 AI  Agent 无缝操控 GIMP、Blender、QGIS 等专业软件。

---

**项目信息**

| 项目 | 信息 |
|------|------|
| **GitHub** | [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) |
| **Stars** | 371 (今日) |
| **语言** | Python ≥3.10 |
| **协议** | Apache 2.0 |
| **相关组织** | HKUDS (香港大学数据科学实验室) |

---

## 这个项目解决了什么问题

当前 Agent 面临的核心困境：**模型能思考，但无法有效操控外部软件**。无论是 GIMP 的图像编辑、Blender 的 3D 建模，还是 QGIS 的地理信息系统，Agent 都只能通过笨拙的系统命令或 API 包装来操作这些工具——而这些软件根本没有为 Agent 设计过。

CLI-Anything 的核心价值在于：**自动化生成符合 Agent 使用习惯的 CLI 包装器**，将任何软件的复杂功能转化为结构化、可发现、可组合的工具接口。

> "Today's Software Serves Humans. Tomorrow's Users will be Agents. CLI-Anything: Bridging the Gap Between AI Agents and the World's Software."
> — [CLI-Anything README](https://github.com/HKUDS/CLI-Anything)

---

## 核心机制：七阶段 CLI 生成

CLI-Anything 的 CLI 生成流程分为七个阶段，每个阶段对应一个技术挑战：

| 阶段 | 任务 | 技术要点 |
|------|------|---------|
| 1. 发现 | 识别软件的命令结构 | `--help` 解析、命令行参数提取 |
| 2. 映射 | 建立功能到命令的映射 | 参数语义分析、互斥组识别 |
| 3. 结构化 | 生成标准化 CLI 框架 | Click/argparse 框架生成 |
| 4. 补全 | 补充元数据和描述 | AI 生成的命令说明 |
| 5. 测试 | E2E 测试覆盖 | 2,269 个测试用例，100% 通过率 |
| 6. 发布 | 注册到 CLI-Hub | PyPI/npm 多源发布 |
| 7. SKILL.md | 生成 Agent 可发现的技能定义 | 兼容 Agent Skills 标准 |

---

## Agent 工具箱：已支持的 18+ 应用

当前 CLI-Hub 已收录 18+ 个专业软件的 Agent 工具集：

**媒体创作**：Blender (3D)、Krita (绘画)、MuseScore (乐谱)、VideoCaptioner (视频字幕)、Openscreen (屏幕录制)

**工程设计**：QGIS (地理信息)、FreeCAD (CAD)、Godot (游戏引擎)、RenderDoc (GPU 调试)、Inkscape (矢量图)

**科研工具**：Zotero (文献管理)、UniMol Tools (分子建模)、WireMock (API 测试)

**系统工具**：Obsidian (知识库)、n8n (工作流自动化)、Safari (浏览器自动化)、Exa (AI 搜索)、Dify (工作流)

> "One Command Line: Make any software agent-ready for Pi, OpenClaw, nanobot, Cursor, Claude Code, Codex, and more."
> — [CLI-Anything README](https://github.com/HKUDS/CLI-Anything)

---

## CLI-Hub：Agent 的软件包管理器

CLI-Anything 还发布了一个 **CLI-Hub**（https://hkuds.github.io/CLI-Anything/），让 Agent 能够自主发现和安装新的 CLI 工具集：

```bash
# 一键安装 CLI 工具集
pip install cli-anything-hub
cli-hub install <name>
```

这个模式的意义在于：**将「软件操控能力」变成了一种可分发的资源**，Agent 可以在运行时动态获取新的工具能力，而无需预装所有软件接口。

---

## 竞品对比

| 项目 | 方式 | 覆盖范围 | Agent 兼容性 |
|------|------|---------|-------------|
| **CLI-Anything** | 自动生成 | 18+ 应用/100+ 命令 | Agent Skills 标准 |
| **MCP (Model Context Protocol)** | 协议标准化 | 工具发现层 | 协议层面 |
| **直接 API 包装** | 手动开发 | 单应用 | 定制化 |

CLI-Anything 与 MCP 不是竞争关系，而是互补的：MCP 解决 Agent 与工具之间的「发现和连接」问题，CLI-Anything 解决「如何让软件提供可被发现的工具接口」问题。

---

## 工程价值

CLI-Anything 的工程价值在于：**它将 Agent 工具建设的成本从「为每个软件写一个包装器」降低到「一行命令自动生成」**。

对于 Agent 开发者，这意味着：
- 不需要为每个目标软件手写 API 包装
- Agent 可以动态发现和使用新的工具
- 工具质量由自动生成的测试保证，而非人工维护

对于 Agent 研究者，CLI-Anything 提供了一个研究 **Agent-Software Interaction** 的标准化实验平台。

---

**引用来源**：

- [CLI-Anything GitHub README - Why CLI section](https://github.com/HKUDS/CLI-Anything)
- [CLI-Anything GitHub README - Quick Start](https://github.com/HKUDS/CLI-Anything)
- [CLI-Hub Registry](https://hkuds.github.io/CLI-Anything/)
