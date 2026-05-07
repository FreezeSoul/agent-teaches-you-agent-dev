# prompt-tower — 上下文打包的工程化实践

> **目标读者**：使用 Claude Code / Cursor / VS Code AI 辅助编程的开发者，频繁需要在大型代码库中让 AI 理解项目上下文
> **核心结论**：prompt-tower 将「选择文件 → 生成结构化上下文 → 复制粘贴」的流程从手动操作升级为可视化一键操作，解决长程任务中的上下文碎片化问题。376 Stars，VS Code Marketplace 1,000+ 用户，5.0 评分。

---

## 1. 定位破题

**一句话定义**：一个 VS Code 插件，将代码库上下文（文件、目录结构、GitHub Issues、PR Diff）打包成 AI 可直接消费的 XML 格式输出。

**场景锚定**：当你需要让 AI 在一个中型/大型代码库中完成复杂任务（重构、多文件修改、bug 排查）时，「如何快速给 AI 完整的项目上下文」是核心痛点。

**差异化标签**：「一键生成」vs 「手动复制粘贴」—— prompt-tower 把上下文打包变成了一个可复用的操作，而非每次都要重新组织。

> "Turn your entire codebase into AI-ready context in seconds"
> — [prompt-tower GitHub README](https://github.com/backnotprop/prompt-tower)

---

## 2. 体验式介绍

**你的工作流可能是这样的**：

1. 在 VS Code 里打开一个 50+ 文件的 Node.js 项目
2. 想让 AI 帮助重构 `src/api/` 目录下的所有文件
3. 传统做法：手动打开文件 → copy → paste 到聊天窗口 → 描述任务
4. 问题：文件太多容易遗漏、token 估算靠感觉、上下文结构不统一

**prompt-tower 解决的是**：

```
1. 安装 VS Code 插件
2. 点击 Activity Bar 的 Tower 图标
3. 勾选需要打包的文件（实时显示 token 数量）
4. 点击「Copy Context to Clipboard」
5. 粘贴到 Claude Code / Cursor / ChatGPT → 描述任务
```

**典型输出格式**：

```xml
src/
├── api/GitHubApiClient.ts (5.2KB)
├── models/FileNode.ts (3.1KB)
└── services/TokenCountingService.ts (2.8KB)

<file path="/src/api/GitHubApiClient.ts">
export class GitHubApiClient {
  // Your actual code
}
</file>
```

从用户体验角度看：这不是一个「编程框架」，而是一个「开发者工具」——它的价值在于减少手工操作、提升上下文一致性。

---

## 3. 技术拆解与验证

### 技术架构

prompt-tower 的架构非常简洁：

1. **Visual File Selection**：VS Code UI 层，通过 TreeView 展示项目结构，checkbox 选择文件
2. **Smart Context Packaging**：将选中的文件打包成 XML 格式，包含目录结构和文件内容
3. **Token Intelligence**：实时 token 计数，防止超出模型上下文限制
4. **`.towerignore`**：类 .gitignore 语法，排除 test fixtures / generated files / docs

### 核心能力

| 能力 | 说明 |
|------|------|
| **多文件选择** | 通过 UI 勾选，不依赖命令行或文件路径 |
| **实时 token 计数** | 每选中一个文件，UI 显示当前上下文总 token 数 |
| **结构化输出** | XML 格式的目录树 + 文件内容，适合 AI 解析 |
| **GitHub 集成** | 直接导入 Issue 和 Comments，让 AI 理解「为什么改」|
| **模型无关** | 输出格式通用，支持 Claude Code、Cursor、ChatGPT、Gemini |

### GitHub Issues 集成

> "Import issues and comments directly. AI understands your problems, not just your code."

这是一个有意思的设计——将「问题背景」也纳入上下文，而不只是「代码内容」。这对于 AI 理解「这次重构要解决什么问题」很有帮助。

### `.towerignore` 机制

类似 .gitignore 的排除规则：

```gitignore
tests/fixtures/
dist/
*.test.js
data/
```

确保打包的上下文只包含与任务相关的文件，避免低价值 token 浪费 context window。

---

## 4. 与动态上下文发现的关系

**这篇文章的主题**是 Cursor 的「动态上下文发现」（Agent 按需拉取上下文），而 prompt-tower 代表了另一种思路——**在发送给 Agent 之前预先结构化打包上下文**。

| 维度 | Cursor 动态上下文发现 | prompt-tower |
|------|----------------------|--------------|
| **触发时机** | Agent 运行时动态发现 | Agent 运行前预先打包 |
| **上下文来源** | 文件系统、MCP 工具、历史记录 | 开发者手动选择 |
| **Token 效率** | 按需加载，47% 节省（MCP 场景）| 开发者控制，依赖选择质量 |
| **实现复杂度** | 高（需要文件系统同步、引用机制）| 低（VS Code 插件 + XML 模板）|
| **适用场景** | 长程任务、多工具、多 MCP | 中型代码库、单次复杂任务 |

> 两者不是替代关系，而是不同场景下的互补选择：
> - **prompt-tower**：需要人类决策「哪些文件重要」的短中期任务
> - **动态上下文发现**：Agent 自主判断「我还需要什么」的长程任务

---

## 5. 快速上手

### 安装

在 VS Code 中搜索 "Prompt Tower" 或直接访问 [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=backnotprop.prompt-tower)。

### 基础使用

1. 在 VS Code Activity Bar 点击 Tower 图标
2. 浏览项目文件树，勾选需要打包的文件
3. 观察右下角实时 token 计数
4. 点击「Copy Context to Clipboard」
5. 粘贴到任意 AI 编程工具

### 配置 .towerignore

在项目根目录创建 `.towerignore` 文件：

```gitignore
# 排除测试固件和生成文件
tests/mocks/
dist/
*.min.js

# 排除文档和配置
docs/
config/local/
```

### GitHub Issues 集成

在 Tower 侧边栏选择「GitHub Issues」标签页，浏览并选择需要导入的 Issue，AI 就能看到问题的完整讨论上下文。

---

## 6. 局限性

| 局限 | 说明 |
|------|------|
| **人类决策依赖** | 文件选择完全依赖人类判断，无法自动化 |
| **不适合超大代码库** | 当代码库包含 1000+ 文件时，手动选择仍然费时 |
| **VS Code 强依赖** | 无法在 CLI 环境（Claude Code TUI）直接使用 |
| **不支持增量更新** | 每次任务都需要重新选择和打包，无法利用上次选择的上下文 |

---

## 7. 什么时候选择 prompt-tower

**适合的场景**：
- 代码库规模：50 - 500 个文件的中型项目
- 任务类型：需要跨多个模块的复杂修改、重构、bug 排查
- 工具偏好：主要在 VS Code / Cursor 界面中工作
- 上下文特征：开发者能清晰判断「哪些文件与任务相关」

**不适合的场景**：
- 超大代码库（1000+ 文件）：手动选择仍然繁琐
- CLI 优先工作流（Claude Code TUI）：无 VS Code 界面可用
- Agent 需要自主探索的场景：动态上下文发现更合适

---

**引用来源**：
- [prompt-tower GitHub](https://github.com/backnotprop/prompt-tower)
- [VS Code Marketplace 页面](https://marketplace.visualstudio.com/items?itemName=backnotprop.prompt-tower)
- [Cursor Engineering Blog: Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)