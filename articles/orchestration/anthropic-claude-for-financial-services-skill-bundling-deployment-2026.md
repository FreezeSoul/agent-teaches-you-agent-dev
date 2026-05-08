# Anthropic Claude for Financial Services：Skill Bundling 与双重部署架构

> 本文深入分析 [anthropics/financial-services](https://github.com/anthropics/financial-services) 仓库的架构设计，揭示 Anthropic 如何通过 Skill Bundling 机制实现「一次编写，双重部署」——既作为 Claude Cowork 插件安装，也可通过 Claude Managed Agents API 部署。文章聚焦 skill 同步机制、vertical-agent 的 source-of-truth 设计，以及 managed-agent cookbook 的 subagent 编排方式。

## 背景：从 Skill 到可部署的 Agent

Anthropic 官方博客 [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) 提出了 progressive disclosure 架构（Level 1 metadata → Level 2 SKILL.md → Level 3 additional files），解决了「如何标准化 agent 技能」的问题。但还有一个关键问题没有回答：**Skill 编写完成后，如何与具体的 Agent 实例绑定并部署？**

`anthropics/financial-services` 仓库是这个问题的官方答案。

## 仓库整体架构

```
plugins/
  agent-plugins/        # Named agents — self-contained plugins
  vertical-plugins/     # Skills + commands + MCP connectors (source of truth)
  partner-built/         # Partner-authored plugins (LSEG, S&P Global)
managed-agent-cookbooks/ # Claude Managed Agent templates
claude-for-msft-365-install/ # Microsoft 365 add-in admin tooling
scripts/                # deploy-managed-agent.sh, sync-agent-skills.py, orchestrate.py
```

两层插件系统分离了「技能定义」与「技能使用」：

| 层级 | 位置 | 角色 | 可编辑性 |
|------|------|------|----------|
| **Vertical Plugin** | `plugins/vertical-plugins/<vertical>/` | Skills 的 source of truth | 维护者编辑 |
| **Agent Plugin** | `plugins/agent-plugins/<slug>/` | 打包特定 agent 所需的 skills 子集 | 自动同步 |

## Skill Bundling 机制：垂直源 → 代理副本

核心机制由 `scripts/sync-agent-skills.py` 实现：

```python
# index every skill name -> source dir in verticals
src_by_name: dict[str, Path] = {}
for sk in VERTICALS.glob("*/skills/*"):
    if sk.is_dir():
        src_by_name[sk.name] = sk

for bundled in sorted(AGENTS.glob("*/skills/*")):
    src = src_by_name.get(bundled.name)
    shutil.rmtree(bundled)
    shutil.copytree(src, bundled)  # 每次同步都 full replace
```

这个脚本的语义非常明确：**`vertical-plugins/` 是唯一真相源，`agent-plugins/` 下的 skills 目录是 vendored copy**。每次运行 sync，bundled skills 会被完整替换为最新版本。

这解决了企业场景中的两个实际问题：

1. **Skill 统一维护**：多个 agent 共享的技能（如 `comps-analysis`、`dcf-model`）只需在一处更新
2. **Agent 隔离**：每个 agent 插件 bundles 它实际需要的 skill 子集，不多不少

## Pitch Agent 实例：端到端 skill 编排

以 [Pitch Agent](./plugins/agent-plugins/pitch-agent) 为例，看 skill 如何被实际调用：

### Agent 定义（agents/pitch-agent.md）

```markdown
---
name: pitch-agent
description: End-to-end investment banking pitch agent.
tools: Read, Write, Edit, mcp__capiq__*
---

You are the Pitch Agent — a senior investment banking associate...

## Workflow

1. Invoke `sector-overview` skill → draft company snapshot
2. Use CapIQ MCP → pull trading multiples and filings
3. Invoke `comps-analysis` skill → lay out trading comps
4. Invoke `lbo-model` skill → sponsor case LBO
5. Invoke `dcf-model` + `3-statement-model` skills
6. Invoke `pitch-deck` skill → generate branded deck
7. Invoke `ib-check-deck` skill → deck QC
```

Pitch Agent 依赖的 skills 清单：

```
sector-overview · comps-analysis · lbo-model · dcf-model · 
3-statement-model · audit-xls · pitch-deck · ib-check-deck · deck-refresh
```

这些 skill 全部来自 `vertical-plugins/financial-analysis/skills/`，由 sync 脚本同步到 agent bundle。

### Subagent 拆解（researcher subagent）

Pitch Agent 的 `managed-agent-cookbooks/pitch-agent/subagents/researcher.yaml` 展示了一个 leaf subagent 的定义：

```yaml
name: pitch-researcher
model: claude-opus-4-7

system:
  text: |
    You research comps and precedent transactions for a target.
    Pull trading multiples from CapIQ/Daloopa, return a structured table.
    Read-only — you do not write files.

skills: []   # leaf agent，无 bundled skills

output_schema:
  type: object
  required: [target, comps]
  properties:
    target: { type: string, maxLength: 64 }
    comps:
      type: array
      maxItems: 30
      items:
        type: object
        properties:
          ticker: { type: string, maxLength: 12, pattern: "^[A-Z.]+$" }
          metric: { type: string }
          value:  { type: number }
    precedents:
      type: array
      maxItems: 30
      items:
        type: object
        properties:
          target:   { type: string }
          acquirer: { type: string }
          ev:       { type: number }
          multiple: { type: number }
```

注意 leaf subagent 的 `skills: []` — 这是 **「thin leaf」设计**：subagent 不需要 bundled skills，因为它们通过 `callable_agents` 机制接收上游 agent 的任务分配。

## 双重部署：同一 source，两种路径

这是 `claude-for-financial-services` 最关键的设计决策：**相同的 agent 目录，同时适配 Cowork 插件和 Managed Agent API 两种部署方式**。

### 部署路径对比

| | **Claude Cowork** | **Claude Managed Agent API** |
|---|---|---|
| **安装方式** | Settings → Plugins → Add plugin（URL 或 zip） | `scripts/deploy-managed-agent.sh` → POST `/v1/agents` |
| **Agent 定义来源** | `agents/<slug>.md` system prompt | `agent.yaml` + `subagents/` 目录 |
| **工具配置** | YAML front matter（`tools:`） | `agent.yaml` 中的 `tools:` 列表 |
| **Subagent 编排** | 不支持（单一 agent） | `callable_agents` + `manifest:` 引用 |
| **MCP 连接** | `.mcp.json` connector | `agent.yaml` 中的 `mcp_servers:` |

### Managed Agent Cookbook 结构

每个 agent 的 cookbook 目录（如 `managed-agent-cookbooks/pitch-agent/`）结构：

```
pitch-agent/
  agent.yaml              # 顶层 agent 配置（model、tools、skills、subagents）
  subagents/
    researcher.yaml       # Leaf subagent 1（数据研究）
    modeler.yaml          # Leaf subagent 2（财务建模）
    deck-writer.yaml      # Leaf subagent 3（PPT 生成，仅此 agent 有 Write 权限）
```

### agent.yaml 的关键字段

```yaml
name: pitch-agent
model: claude-opus-4-7

system:
  file: ../../plugins/agent-plugins/pitch-agent/agents/pitch-agent.md
  append: "You are running headless. Produce files in ./out/..."

tools:
  - type: agent_toolset_20260401
    default_config: { enabled: false }
    configs:
      - { name: read,  enabled: true }
      - { name: grep,  enabled: true }
      - { name: glob,  enabled: true }
  - { type: mcp_toolset, mcp_server_name: capiq,   default_config: { enabled: true } }
  - { type: mcp_toolset, mcp_server_name: daloopa, default_config: { enabled: true } }

mcp_servers:
  - { type: url, name: capiq,   url: "${CAPIQ_MCP_URL}" }
  - { type: url, name: daloopa, url: "${DALOOPA_MCP_URL}" }

skills:
  - { from_plugin: ../../plugins/agent-plugins/pitch-agent }

callable_agents:
  - { manifest: ./subagents/researcher.yaml }
  - { manifest: ./subagents/modeler.yaml }
  - { manifest: ./subagents/deck-writer.yaml }
```

关键字段解读：

- **`system.file` + `system.append`**：Cowork 插件的 system prompt 直接复用文件引用，Managed Agent 部署时通过 `file:` 字段加载
- **`from_plugin` in skills**：引用 agent plugin 目录（即 bundles 了同步后的 skills）
- **`callable_agents`**：Managed Agent 独有字段，定义可调用的 subagent 列表

## vertical-plugin 的 Skill 组织方式

`plugins/vertical-plugins/financial-analysis/` 展示了按领域垂直组织 skills 的最佳实践：

```
financial-analysis/
  skills/
    comps-analysis/     # 可比公司分析
    dcf-model/          # DCF 建模
    lbo-model/         # LBO 建模
    3-statement-model/ # 三张报表模型
    audit-xls/          # Excel 审计规范
    pitch-deck/         # Pitch Deck 生成
    ib-check-deck/      # 投行 Deck 检查清单
  commands/
    /comps              # Slash 命令
    /dcf
    /earnings
  .mcp.json             # MCP servers 连接配置
```

Skills 被多个 agent 共享（如 `comps-analysis` 同时被 Pitch Agent 和 Market Researcher 使用），通过 sync 脚本各自同步到需要的 agent bundle 中。

## 与 Anthropic 官方 Agent Skills 架构的对应关系

| Progressive Disclosure Level | 在 financial-services 中的实现 |
|-----------------------------|-------------------------------|
| **L1: Metadata（名称、描述、触发条件）** | `SKILL.md` 中的 `name`、`description`、`trigger` front matter |
| **L2: SKILL.md（详细指令、步骤、约定）** | `skills/<name>/SKILL.md` — 领域专业知识、步骤序列、格式规范 |
| **L3: Additional Files（参考数据、模板、工具）** | 垂直插件中的 `.mcp.json`（MCP server 连接）、`commands/`（slash commands） |

## 架构价值：为什么这个设计重要

### 1. Skill 作为可组合单元

Skills 摆脱了「紧耦合在单个 agent」的限制。同一个 `comps-analysis` skill 可以被：
- Pitch Agent 用来做交易估值
- Market Researcher 用来做行业概览
- Valuation Reviewer 用来做 LP 报告

### 2. 开发与部署分离

Agent 开发者编写 skill 时只需关注「做什么」，部署时选择「谁来执行」：
- Cowork：单一 agent 执行，技能直接内置
- Managed Agent：通过 `callable_agents` 分发给多个 specialized subagents

### 3. 安全边界通过架构天然隔离

Leaf subagents 如 `pitch-researcher` 明确定义 `skills: []` 和 `Read-only` 约束，任何文件写入操作只能在顶层 agent 进行。这比运行时权限检查更可靠——**安全边界在结构上就被定义**。

## 结论

`anthropics/financial-services` 是 Agent Skills 架构理念的完整生产级实现。它展示了：

1. **Vertical plugins 作为 skill 的 source of truth**，通过 `sync-agent-skills.py` 同步到各 agent bundles
2. **同一套 skill 定义支持双重部署**：Cowork 插件 vs. Managed Agent API
3. **Managed Agent 通过 `callable_agents` 实现 hierarchy**：顶层 agent 编排多个 specialized leaf subagents
4. **Leaf subagents 的「thin by design」原则**：不bundles skills，仅通过 schema 化的 output 与上游通信

这个架构为「企业级 Agent 技能库」提供了可复用的范式：**skill 应该是可发现、可同步、可组合、可版本化的独立单元，而不是硬编码在 agent 系统提示里的知识**。

> 信息来源：[anthropics/financial-services](https://github.com/anthropics/financial-services) GitHub 仓库，14,871 ⭐，最后更新 2026-05-08。原文引用均来自仓库内 `agents/pitch-agent.md`、`managed-agent-cookbooks/` 配置文件及 `scripts/sync-agent-skills.py` 脚本。