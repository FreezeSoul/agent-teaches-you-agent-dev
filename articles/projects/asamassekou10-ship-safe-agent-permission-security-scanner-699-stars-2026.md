# asamassekou10/ship-safe — Agentic 时代的 CLI 安全扫描器

## 一、定位破题

**项目类型**：CLI 安全工具 / Agent 专用扫描器  
**场景锚定**：当你把 Agent 部署到真实开发流程前，需要检查「这个 Agent 的权限配置是否安全」「MCP 工具链有没有注入风险」  
**差异化标签**：首个专门面向 Agentic 工作流的安全扫描器，覆盖 CI/CD 配置、权限风险、工具注入三大维度

> 官方 README 定义：
> "CLI security scanner built for the agentic era. Detects CI/CD misconfigs, agent permission risks, MCP tool injection, hardcoded secrets, and DMCA-flagged AI dependencies."
> — [asamassekou10/ship-safe GitHub README](https://github.com/asamassekou10/ship-safe)

---

## 二、体验式介绍

### 一句话：把 OWASP ASI Top 10 变成自动化检查，在 Agent 伤害生产环境之前拦截它

**解决的真实痛点**：随着 Claude Code、Codex 和 Cursor Agent 进入开发工作流，Agent 拥有了文件写入、网络访问、命令执行等高危权限。但这些权限的配置完全依赖人工审查——没有工具告诉你「这个 Agent 的 MCP 工具链是否被污染」「CI/CD pipeline 中的 Agent 配置是否引入了权限蔓延」。

ship-safe 填补了这个空白。它是一个纯 CLI 工具，安装后用一行命令扫描你的项目：

```bash
npx ship-safe scan .
```

扫描结果包括：
- **Agent 权限风险**：检测 `.claude/`、`AGENTS.md` 等配置中的权限蔓延模式
- **MCP 工具注入**：检测 `mcp.json` 或 `.mcp/` 中是否存在可疑的第三方 MCP 服务器
- **CI/CD 错误配置**：检测 GitHub Actions、GitLab CI 中的 Agent 特权运行器配置
- **硬编码密钥**：检测 Agent 可能在代码中暴露的 API keys 和 tokens
- **DMCA 标志的 AI 依赖**：检测使用了有法律风险的 AI 生成代码库

---

## 三、拆解验证

### 技术深度

ship-safe 的扫描逻辑是规则驱动的，针对 Agentic 工作流的特定风险模式：

| 风险类别 | 典型模式 | ship-safe 检测方式 |
|---------|---------|------------------|
| **MCP 工具注入** | 恶意 MCP 服务器伪装成合法工具，注入到 Agent 工具链 | 检测未知来源的 MCP 服务器配置，检查其权限需求是否异常 |
| **Agent 权限蔓延** | `.claude.json` 中配置了过于宽泛的文件访问权限 | 正则匹配权限配置，检查是否包含 `/` 根路径或生产目录 |
| **CI/CD 特权运行器** | GitHub Actions 中使用 `GITHUB_TOKEN` 的 `write` 权限 | 检测 workflow 文件中的 permissions 配置 |
| **硬编码密钥** | Agent 在代码中生成的 API keys 被 commit | 扫描常见的密钥模式（openai、anthropic、AWS 等） |

> "Detects CI/CD misconfigs, agent permission risks, MCP tool injection, hardcoded secrets, and DMCA-flagged AI dependencies."
> — [asamassekou10/ship-safe README](https://github.com/asamassekou10/ship-safe)

### 社区健康度

- **Stars**：699（截至 2026-05-12）
- **创建时间**：2026 年初
- **定位**：纯 CLI 工具，零运行时依赖，使用 TypeScript 开发
- **安装方式**：`npx ship-safe scan .` 或 `npm install -g ship-safe`

### 与竞品的差异化

| 工具 | 定位 | Agent 特有功能 |
|------|------|---------------|
| **trivy** | 容器镜像扫描 | 无 |
| **Gitleaks** | Git 硬编码密钥扫描 | 无 |
| **Semgrep** | 静态代码分析 | 需要手动写规则 |
| **ship-safe** | Agentic 安全扫描 | MCP 工具注入检测 + Agent 权限配置检查 |

---

## 四、行动引导

### 快速上手（3 步以内）

```bash
# Step 1: 直接运行（npx 方式）
npx ship-safe scan .

# Step 2: 安装为全局 CLI（可选）
npm install -g ship-safe

# Step 3: 集成到 CI/CD
# 在 GitHub Actions 中添加：
- name: Run ship-safe
  run: npx ship-safe scan . --format sarif > ship-safe.sarif
```

### 适用场景

- **Pre-deployment 检查**：Agent 部署到生产环境前，运行 ship-safe 扫描项目配置
- **CI/CD 集成**：在 pull request 中强制运行，发现权限配置问题后阻止合并
- **MCP 生态检查**：引入新的 MCP 服务器前，用 ship-safe 检查其是否有可疑权限需求

### 贡献入口

ship-safe 面向 Agentic 时代的新风险模式，当前覆盖范围仍在扩展中。TypeScript 项目，适合安全工程师和 Agent 开发者贡献检测规则。

---

## 五、主题关联

本文 [Anthropic 四月事后分析](./anthropic-april-2026-postmortem-triple-change-compounding-degradation-2026.md) 揭示了 Agent 系统质量退化的三类根本原因：

| 退化原因 | ship-safe 能做什么 |
|---------|------------------|
| 默认参数错误配置 | 检测 `.claude.json` 等文件中的权限配置模式 |
| 缓存层实现 Bug | 无直接覆盖，但权限配置审计有助于发现异常行为来源 |
| 系统提示词指令的隐蔽影响 | 检测 prompt 文件中的异常指令模式 |

ship-safe 的核心价值是**在 Agent 伤害生产环境之前发现问题**，而不是事后分析。这两个主题形成了「事后分析（Anthropic）+ 事前防御（ship-safe）」的互补闭环。
