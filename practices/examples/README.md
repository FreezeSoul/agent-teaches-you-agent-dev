# 可运行代码示例

> 完整的、可直接运行的代码示例，按模式分类。

---

## 基础模式

| 文件 | 描述 |
|------|------|
| [react_agent.py](./react_agent.py) | ReAct 模式：推理与执行交替，纯 Python 无框架依赖 |
| [multi_agent.py](./multi_agent.py) | 多 Agent 协作：顺序 / 并行 / 层级三种模式 |
| [memory_agent.py](./memory_agent.py) | Agent Memory 架构：短期 + 长期 + 人格记忆三层设计 |

---

## 框架示例

| 文件 | 框架 | 描述 |
|------|------|------|
| [langgraph_quickstart.py](../frameworks/langgraph/examples/langgraph_quickstart.py) | LangGraph | ReAct 风格工具调用 Agent，状态机 |
| [crewai_quickstart.py](../frameworks/crewai/examples/crewai_quickstart.py) | CrewAI | 多 Agent 研究团队（研究员+审核员+作家） |
| [autogen_quickstart.py](../frameworks/autogen/examples/autogen_quickstart.py) | AutoGen | Two-Agent 对话、Group Chat、人机协同 |

---

## 使用说明

### 无框架示例（可直接运行）

```bash
# ReAct 模式
python react_agent.py

# 多 Agent 协作
python multi_agent.py

# Memory 架构
python memory_agent.py
```

### 框架示例

```bash
# 进入框架目录
cd ../frameworks/langgraph/examples/
pip install langgraph langchain-openai
export OPENAI_API_KEY=your_key
python langgraph_quickstart.py
```

---

*持续更新中*
