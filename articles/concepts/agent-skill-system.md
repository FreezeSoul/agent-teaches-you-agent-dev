# Agent Skill：能力的抽象单元

> **本质**：Skill（技能）是 Agent 能力的高度抽象封装——把特定领域的知识、工具、流程打包成可发现、可复用、可组合的独立单元。如果说 Tool 是 Agent 的"手"，Paradigm 是"思维模式"，那么 Skill 就是 Agent 的"专业能力"。

---

## 一、什么是 Agent Skill

### 1.1 定义

**Agent Skill** 是一种将特定领域能力封装为独立模块的技术抽象。一个 Skill 通常包含：

```yaml
Skill: web_scraper
  description: "从任意 URL 提取页面内容"
  capabilities:
    - fetch_html
    - parse_markdown
    - extract_structured_data
  dependencies:
    - browser_automation
    - html_parser
  triggers:
    - "抓取网页"
    - "提取文章"
    - "获取页面内容"
  constraints:
    - max_pages_per_session: 50
    - rate_limit_ms: 1000
```

### 1.2 Skill vs Tool vs Paradigm

| 维度 | Tool（工具）| Skill（技能）| Paradigm（范式）|
|------|------------|-------------|----------------|
| **粒度** | 原子级操作 | 领域级能力包 | 系统级设计模式 |
| **封装** | 单个函数/API | 多工具 + 知识 + 流程 | 完整的思维框架 |
| **复用方式** | 直接调用 | 动态发现 + 组合 | 参照设计 |
| **典型示例** | `ddg-search`, `file_read` | `code_debugger`, `data_analyst` | ReAct, Reflection |
| **抽象层次** | 最底层 | 中间层 | 最顶层 |

**关键区别**：Tool 是执行单元，Paradigm 是组织单元，而 **Skill 是能力单元**。

### 1.3 Skill 的层次结构

```
Paradigm（范式）
    ↓ 封装
Skill（技能）
    ↓ 组合
  Tool（工具）
    ↓ 实现
  API / Function
```

以「代码审查 Skill」为例：
- **Paradigm**：Reflection（自我审视）
- **Skill**：`code_review`（整合了 lint、静态分析、diff 审查等多个工具）
- **Tool**：`run_clang_tidy`, `git_diff`, `llm_annotate`
- **API**：具体的 HTTP 调用或函数

---

## 二、为什么 Skill 是重要的演进阶段

### 2.1 从工具到技能的演进必然性

当 Agent 系统足够复杂时，工具的数量会爆炸：

```
10 个 Agent × 20 个工具 = 200 个管理对象
100 个 Agent × 50 个工具 = 5000 个管理对象
```

**Skill 提供了一层抽象**——把工具按领域能力分组，Agent 只需知道「我要做代码审查」，而不需要知道「先用 clang_tidy，再用 git diff，然后 llm_annotate」。

### 2.2 Skill 是 Multi-Agent 协作的单元

Multi-Agent 系统中，Agent 之间的协作有两种粒度：

1. **消息级协作**：Agent A 发消息给 Agent B（对话/指令）
2. **Skill 级协作**：Agent A 调用 Agent B 的 Skill（能力调用）

Skill 级协作更高效，因为：
- 隐藏了实现细节
- 提供了稳定的接口契约
- 支持权限隔离（A 可以调用 B 的 Skill，但无法访问 B 的内部工具）

> 这也是 **A2A 协议**的核心设计目标之一——让 Agent 之间以 Skill 为单位交互，而非直接调用工具。

---

## 三、Skill 的生命周期

### 3.1 发现（Discovery）

Agent 在运行时动态发现可用的 Skill：

```python
class SkillRegistry:
    def discover(self, query: str) -> List[Skill]:
        """根据用户意图发现匹配的 Skill"""
        # 基于描述的语义搜索
        scored = self.similarity_search(query, all_skills)
        # 返回最相关的 Skill
        return sorted(scored, key=lambda x: x.score)[:3]

    def get_skill(self, name: str) -> Skill:
        """精确获取 Skill"""
        return self.skills[name]
```

**发现机制**：
- **注册中心模式**：集中式 Skill 注册表（如 ClawHub）
- **广播模式**：Skill 在网络中广播自己的能力
- **语义发现**：基于意图理解动态匹配

### 3.2 组合（Composition）

多个 Skill 组合成更复杂的 Skill：

```python
# Skill 组合示例
complex_skill = compose(
    skill("web_search"),      # 第一步：搜索
    skill("content_fetch"),   # 第二步：获取内容
    skill("text_extract"),    # 第三步：提取信息
    skill("summary_generate") # 第四步：生成摘要
)

# 组合后的 Skill 可以像普通 Skill 一样被调用
result = await complex_skill.execute("查找 2026 年 MCP 最新进展")
```

**组合方式**：
- **顺序组合**：A → B → C（流水线）
- **并行组合**：A || B || C（同时执行，结果合并）
- **条件组合**：A ? B : C（根据中间结果选择分支）

### 3.3 链接（Chaining）

Skill 链接是指一个 Skill 的输出直接作为另一个 Skill 的输入：

```python
# Skill 链接
skill_chain = (
    skill("github_search")
    .chain_to(skill("clone_repository"))
    .chain_to(skill("code_analysis"))
    .chain_to(skill("generate_report"))
)
```

### 3.4 共享（Sharing）

Skill 的核心价值之一是**跨 Agent 复用**：

```python
# Skill 市场示例
class SkillMarket:
    async def publish(self, skill: Skill, author: Agent):
        """将 Skill 发布到市场"""
        # 验证 Skill 质量
        await self.verify(skill)
        # 注册到全局索引
        await self.registry.add(skill)

    async def install(self, skill_name: str, agent: Agent):
        """Agent 从市场安装 Skill"""
        skill = await self.registry.get(skill_name)
        await agent.install_skill(skill)
```

---

## 四、Skill 生态系统

### 4.1 主要 Skill 框架

| 平台 | 定位 | Skill 数量 | 特点 |
|------|------|-----------|------|
| **OpenClaw ClawHub** | Agent Skill 市场 | 大量 | 完整的 Skill 生命周期管理 |
| **Composio** | Claude Code Skill 集成 | 100+ | 聚焦编码场景，即装即用 |
| **MCP** | 工具/技能协议 | 快速增长 | 标准化 Skill 接口 |
| **LangChain Agents** | LLM Agent 框架 | 内置多种 | Skill 作为 Tool 的上层封装 |
| **PraisonAI** | 轻量 Multi-Agent | Self-Reflection | Skill 级的 Multi-Agent |

### 4.2 ClawHub：OpenClaw 的 Skill 市场

ClawHub 是 OpenClaw 官方的 Skill 分发平台：

```bash
# 安装 Skill
openclaw skills install clawhub:<package_name>

# 搜索 Skill
openclaw skills search "<keyword>"

# 更新 Skill
openclaw skills update <package_name>
```

**Skill 的安装过程**：
1. 从 ClawHub 下载 Skill 包（含 SKILL.md + 脚本 + 配置）
2. 验证签名和权限声明
3. 安装到 `~/.openclaw/workspace/skills/`
4. 注册到 Skill 注册表

### 4.3 Composio：Claude Code 的 Skill 生态

Composio 聚焦于**编码 Agent 的 Skill 集成**：

> 详见：[Top 10 Claude Code Skills](articles/community/top-claude-code-skills-composio.md)

**核心价值**：
- 每个 Skill 都是一个完整的编码能力（如 GitHub 集成、File 操作、Shell 执行）
- Agent 无需知道具体 API 调用，只需调用 Skill
- Skill 之间相互独立，版本可控

---

## 五、Skill 与 MCP 的关系

MCP 是 Skill 系统的底层协议——MCP Server 暴露的工具，本质上是一个 Skill 的底层实现。

```
┌─────────────────────────────────────┐
│  Skill: code_review                 │
│  ├── Tool: run_clang_tidy (MCP)    │
│  ├── Tool: git_diff (MCP)          │
│  └── Tool: llm_annotate (MCP)     │
└─────────────────────────────────────┘
```

**MCP 提供了 Skill 的标准化传输协议**，而 Skill 则定义了**何时调用什么工具的领域知识**。

---

## 六、Skill 的工程挑战

### 6.1 Skill 依赖地狱

Skill 之间可能有复杂的依赖关系：

```yaml
skill_A:
  depends_on: [skill_B, skill_C]
skill_B:
  depends_on: [skill_D]
skill_C:
  depends_on: [skill_D]
skill_D:
  depends_on: []
```

**解决方案**：依赖解析器 + 版本锁定

### 6.2 Skill 版本管理

当 Skill 升级时，使用它的 Agent 可能受影响：

- **热更新**：Skill 升级后自动生效（仅当接口兼容时）
- **版本锁定**：Agent 可以锁定 Skill 版本
- **接口契约**：Skill 必须声明其接口版本

### 6.3 Skill 安全

安装未知来源的 Skill 存在安全风险：

| 风险 | 描述 | 防御手段 |
|------|------|---------|
| **恶意 Skill** | Skill 包含恶意代码 | 签名验证、沙箱执行 |
| **依赖注入** | Skill 依赖被篡改 | 依赖锁定、来源验证 |
| **权限升级** | Skill 申请超出需要的权限 | 最小权限审查 |
| **数据泄露** | Skill 收集敏感数据 | 运行时监控 |

> 详见：[NVIDIA Sandbox Security Guide](articles/community/nvidia-sandbox-security-guide.md)

---

## 七、演进路径中的位置

```
Multi-Agent（多智能体协作）
    ↓ Skill 成为协作单元
Skill（技能抽象）
    ↓ Skill + Harness
Harness Engineering（工程约束）
    ↓
Deep Agent（深度自主 Agent）← Skill 是其能力边界
```

**Skill 与其他阶段的关系**：
- **Prompt Engineering**：Skill 的触发条件由 Prompt 定义
- **RAG**：Skill 可以内置 RAG 能力作为知识检索
- **MCP**：MCP 是 Skill 的底层传输协议
- **Paradigms**：Skill 是 Paradigm 的实现载体（Reflection Skill、Planning Skill）
- **Multi-Agent**：Agent 之间通过 Skill 接口交互，而非直接调用工具
- **Deep Agent**：Deep Agent 的能力边界由其 Skill 集合决定

---

## 参考文献

- Composio：https://composio.dev
- ClawHub：https://clawhub.com
- MCP 规范：modelcontextprotocol.io
- [Top 10 Claude Code Skills](articles/community/top-claude-code-skills-composio.md)
- [A2A Protocol](articles/community/a2a-protocol-http-for-ai-agents.md)
