# KeWang0622/agent-zero-to-hero：从零构建 Claude-Code 形态的 Agent Harness

> 7 周课程 / 19 章节 / ~4500 行 Python / 42 个测试 / 3 个 LLM Provider / 零框架依赖

---

## 核心定位

**Target**：有一定 Python 基础的 Agent 开发新手，想理解 Claude Code/Cursor/Devin 内部究竟是如何工作的。

**Result**：从第一性原理理解 Agent Harness 的核心要素——Messages API、Tool Loop、Stop Reasons、Skills、MCP——而非停留在「怎么用」的表面。

**Insight**：用 `while True: r = client.messages.create(...); msgs.append(r.content); if r.stop_reason != "tool_use": return r; msgs.append(run_all_tools(r.content))` 这 6 行代码揭示所有编码 Agent 的本质。

**Proof**：GitHub 14 Stars，MIT License，Python 3.10+。

---

## 为什么值得关注

### 「整个 Agent Loop 只要 6 行」

> The model is stateless. The messages array IS the memory. Tools, skills, sessions, MCP — they're how the harness extends the model. They're not the agent. The loop is it.

这个项目用最直接的方式展示了 Agent 的核心架构：Messages array 是唯一的内存，Tools/Skills/MCP 是 Harness 对模型的扩展，而 Loop 才是 Agent 的本质。

### 19 章节的完整学习路径

| Chapter | 内容 | 关键概念 |
|---------|------|---------|
| 00 | Welcome - 30 行实现完整 Agent | Agent Loop 第一印象 |
| 01 | raw_call - 一个 HTTP POST | Messages API，stateless |
| 02 | messages_array - 消息数组即内存 | 上下文外部化 |
| 03 | stop_reasons - Loop 退出的 7 种方式 | end_turn / tool_use |
| 04 | one_tool - 单轮 tool_use → tool_result | 协议本质 |
| 05 | the_loop - 核心循环（枢轴章节） | 6 行代码揭示一切 |
| 06 | parallel_tools - 多 tool_use 并行 | 单 user message 规则 |
| 07 | errors - Tool 错误作为 content | is_error: true |
| 08 | system_prompts | Harness 对模型的引导 |
| ... | ... | Skills / MCP / Session |

### 零框架依赖，只有标准库

不依赖 LangChain、smolagents 或任何封装框架。所有实现都是裸的 Python + httpx，让你看到每个 primitive 的真实样子。

> Not for you if you want a plug-and-play framework. Use LangGraph or smolagents.

### 与 Cursor Autoinstall 的关联

Cursor 的 Bootstrapping Composer 揭示了 RL 训练中环境初始化的重要性，而这个项目从代码层面展示了「一个真正可运行的 Agent Harness 长什么样」。两者形成互补：Autoinstall 告诉你「如何让模型学会设置环境」，这个项目告诉你「Agent Loop 的 6 行核心代码是什么」。

---

## 快速开始

```bash
git clone https://github.com/KeWang0622/agent-zero-to-hero.git
cd agent-zero-to-hero && pip install -e .
pytest tests/  # 42 passed in 0.6s

# 第一个 Agent
export ANTHROPIC_API_KEY=sk-ant-...
python -m chapters.ch00_welcome "what is 17 * 23?"

# 最终挑战
python agent.py "build me Tetris in one HTML file"
```

---

## 架构亮点

```
User --> Msgs[/messages array] --> Model[claude · openai · gemini]
Model --> Stop{stop_reason?}
Stop -- end_turn --> Answer([final answer])
Stop -- tool_use --> Run[run all tools]
Run --> Msgs
```

- **Messages as Memory**：API 无状态，消息数组是唯一记忆
- **Tools as Extensions**：Tools/Skills/MCP 是 Harness 对模型的扩展，不是 Agent 本身
- **Loop as Agent**：6 行 while loop 才是 Agent 的本质

---

## 适合谁

**✅ 适合**：
- 有基本 Python 基础，想理解 Agent 内部原理
- 用过 Claude Code/Cursor 但想深入理解其工作机制
- 想阅读真实 Agent Harness 源码并识别每个 primitive

**❌ 不适合**：
- 想直接用 plug-and-play 框架（用 LangGraph 或 smolagents）
- 不愿意写代码，只想要现成工具

---

## 链接

- GitHub: https://github.com/KeWang0622/agent-zero-to-hero
- Stars: 14
- License: MIT

---

*推荐关联：本文分析的 Cursor Autoinstall 机制 + 该项目的 Harness 从零实现，形成「RL 环境自举 → 工程落地」的完整闭环。*