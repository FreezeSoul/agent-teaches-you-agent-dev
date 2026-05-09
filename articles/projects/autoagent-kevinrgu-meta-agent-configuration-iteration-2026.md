# AutoAgent：像 AutoResearch 一样自动化迭代 Agent 配置

> AutoAgent 是 2026 年 4 月开源的元 Agent 框架，核心理念是「给定任务和基准，让 Agent 自主迭代自身配置」。它不是直接修改 harness 代码，而是通过 `program.md` 编程元 Agent，让 meta-agent 自行修改 system prompts、tool 配置、agent 编排——然后跑 benchmark，检查分数，保留或丢弃变更，循环往复。

---

## 目标用户（TRIP-T）

**Target**：有一定 Agent 开发经验的工程师，当前工作流程是手工调整 harness 配置、反复跑 benchmark、靠直觉判断改进方向。

**痛点**：每次配置变更需要数小时手动调试，且无法系统性地探索配置空间——你只能测试几个预设组合，无法穷举。

> "Give an AI agent a task, let it build and iterate on an agent harness autonomously overnight."

**角色**：当你想探索 Agent 配置空间、但手动探索效率太低时，AutoAgent 提供了一个自动化循环。

---

## 核心结果（TRIP-R）

- **元 Agent 自动化**：给定 `program.md` 指令 + benchmark 任务，meta-agent 自主迭代 `agent.py`，在 benchmark 分数上 hill-climb
- **单文件 Harness**：整个 harness 在一个 `agent.py` 文件中（config、tool definitions、agent registry、routing/orchestration），meta-agent 的编辑表面清晰
- **Docker 隔离**：每次运行在容器中执行，无法破坏宿主机

官方描述的典型场景：

> "Like autoresearch but for agent engineering. Give an AI agent a task, let it build and iterate on an agent harness autonomously overnight."

---

## 技术架构：Program + Agent + Harbor

### 核心文件结构

```
agent.py              ← 单文件 harness（可编辑区域 + 固定 adapter 区域）
program.md            ← 给 meta-agent 的指令 + directive（人类编程入口）
tasks/                ← Harbor 格式的评估任务
.agent/               ← 可选的 agent 工作区工件（指令、笔记、prompts、skills）
Dockerfile.base       ← 基础镜像
```

### agent.py 的双区域设计

```python
# ========== 可编辑区域（meta-agent 的主要编辑表面）==========
#  - system prompt
#  - tool registries
#  - agent configuration
#  - orchestration / routing
# ========== 固定区域（Anthropic 明确标记为不可修改）==========
#  - Harbor adapter（基准测试集成 + 轨迹序列化）
```

这种设计将**配置迭代**和**接口稳定**分离：meta-agent 可以自由探索配置空间，但 adapter 不受影响。

### program.md：人类编程元 Agent 的方式

`program.md` 是人类与 meta-agent 交互的唯一界面。你在 `program.md` 中写：

1. **给 meta-agent 的指令**（怎么诊断、怎么修改、怎么判断改进）
2. **Directive**（要构建什么样的 agent）

典型启动指令：

```
Read program.md and let's kick off a new experiment!
```

Meta-agent 会读取 directive，审查当前 harness，运行 benchmark，诊断失败，修改 `agent.py`，迭代。

### Harbor 基准测试格式

任务遵循 [Harbor](https://github.com/laude-institute/harbor) 格式：

```
tasks/my-task/
  task.toml         # 配置（超时、元数据）
  instruction.md    # 发给 agent 的 prompt
  tests/
    test.sh        # 入口，写入 /logs/reward.txt
    test.py        # 验证逻辑（确定性或 LLM-as-judge）
  environment/
    Dockerfile     # 任务容器（FROM autoagent-base）
  files/            # 挂载到容器的参考文件
```

测试写一个 0.0-1.0 的分数到 verifier logs。Meta-agent 在这个分数上 hill-climb。

---

## 执行流程

### 快速开始

```bash
# 1. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安装依赖
uv sync

# 3. 配置环境变量
cat > .env << 'EOF'
OPENAI_API_KEY=...
EOF

# 4. 构建基础镜像
docker build -f Dockerfile.base -t autoagent-base .

# 5. 添加任务到 tasks/

# 6. 运行单个 benchmark 任务
rm -rf jobs; mkdir -p jobs
uv run harbor run -p tasks/ --task-name "<task-name>" -l 1 -n 1 \
  --agent-import-path agent:AutoAgent -o jobs --job-name latest

# 7. 并行运行所有任务（-n = 并发数，默认 4）
rm -rf jobs; mkdir -p jobs
uv run harbor run -p tasks/ -n 100 \
  --agent-import-path agent:AutoAgent -o jobs --job-name latest
```

### 元 Agent 循环

```
┌─────────────────────────────────────────────────────────────┐
│                  program.md（人类编辑）                      │
│  给 meta-agent 的指令 + directive                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    Meta-Agent（LLM）                         │
│  1. 读取 directive                                          │
│  2. 检查当前 harness（agent.py）                             │
│  3. 运行 benchmark → 获取分数                                 │
│  4. 诊断失败模式                                             │
│  5. 修改 agent.py 配置（prompt/tools/registry/routing）      │
│  6. 迭代                                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              agent.py（Harness under test）                  │
│  指标：Harbor benchmark 的 task test suites 产生的总分        │
└─────────────────────────────────────────────────────────────┘
```

Meta-agent hill-climbs 在 benchmark 分数上：变好则保留，变差则丢弃。

---

## 设计决策：为什么这样设计

### 1. 编程元 Agent，而非直接编程 Harness

传统做法：人类工程师直接修改 harness 代码 → 运行 benchmark → 判断是否改进。

AutoAgent 的做法：人类编程 `program.md` → meta-agent 修改 `agent.py` → 自动迭代。

**意义**：将「探索配置空间」的工作委托给 LLM，让人类从繁琐的配置调试中解放出来，专注于定义目标和约束。

> "Program the meta-agent, not the harness directly."

### 2. 单文件、Registry 驱动的 Harness

整个 harness 在一个文件中是为了简化，但 registry 机制保持结构化：

- **Tool Registry**：定义可用的工具集
- **Agent Registry**：定义 agent 类型和角色
- **Config**：集中管理配置参数

这种设计让 meta-agent 能清楚地看到「可以修改什么」和「修改的边界在哪里」。

### 3. Docker 隔离

Agent 运行在容器中，无法破坏宿主机。这对自动化 overnight 实验至关重要——你不会醒来发现系统被改坏了。

### 4. Harbor 兼容的任务格式

任务格式与 Harbor benchmarks 兼容，意味着同一 harness 可以在不同数据集上评估。这提供了可迁移性。

---

## 适用边界与局限

**适合的场景**：
- 已知任务和基准，想系统性地探索 agent 配置空间
- Overnight 自动化实验（睡觉时让系统自己跑）
- 配置调参的baseline建立（先自动化再人工介入优化）

**不适合的场景**：
- 完全新的任务（没有 baseline benchmark）
- 需要实时人工介入判断的任务
- 对容器资源有严格限制的环境（每次运行都起 Docker）

---

## 与同类项目的差异化

| 项目 | 差异化 | 定位 |
|------|--------|------|
| **SWE-agent** | 极简 harness（100 行 Python），专注可复现性 | 单 Agent 评测 |
| **AutoAgent (kevinrgu)** | 元 Agent 自动化配置迭代 | Agent 配置空间探索 |
| **Cursor Multi-Agent Kernel** | 领域专家级优化（CUDA Kernel），多 Agent 并行 | 垂直领域优化 |
| **Anthropic Long-Running Harness** | 多会话架构（Initializer + Coding Agent）| 长时间跨度的任务连续性 |

AutoAgent 填补的是「配置探索自动化」这个空白：不是让 Agent 做任务，而是让 Agent 学会更好地配置自己来做任务。

---

## 快速上手路径

```bash
# 1. 克隆并安装
git clone https://github.com/kevinrgu/autoagent.git
cd autoagent
uv sync

# 2. 配置 API key
cat > .env << 'EOF'
OPENAI_API_KEY=your-key-here
EOF

# 3. 构建基础镜像
docker build -f Dockerfile.base -t autoagent-base .

# 4. 写你的 program.md（描述你要构建的 agent 类型）
# 5. 添加任务到 tasks/
# 6. 启动实验
uv run harbor run -p tasks/ -n 4 --agent-import-path agent:AutoAgent -o jobs
```

---

## 参考链接

- GitHub：[kevinrgu/autoagent](https://github.com/kevinrgu/autoagent)（4,400 ⭐）
- 官方博客：AutoAgent 概念类似 AutoResearch，但是面向 Agent 工程本身
- 关联项目：[Anysphere Kernel Optimization Results](https://github.com/anysphere/kernel-optimization-results)（Cursor 38% 加速的验证结果）

---

*AutoAgent 由 Third Layer Inc. 开发，MIT 许可证。*
