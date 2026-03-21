# CrewAI 快速入门示例

> 一个完整的多 Agent 研究团队示例：研究员 + 审核员 + 作家

---

## 环境准备

```bash
pip install crewai crewai-tools
```

---

## 完整示例：研究团队

```python
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, WebsiteSearchTool

# ========== 1. 定义工具 ==========
search_tool = SerperDevTool(api_key="your-serper-key")  # 或其他搜索工具
web_rag_tool = WebsiteSearchTool()

# ========== 2. 定义 Agents ==========

# 研究员 Agent
researcher = Agent(
    role="研究员",
    goal="收集并分析关于 {topic} 的最新技术动态",
    backstory="""
    你是一位资深科技分析师，专注于 AI 和 Agent 技术领域。
    你有敏锐的信息捕捉能力，能从海量信息中筛选出最有价值的内容。
    """,
    tools=[search_tool, web_rag_tool],
    verbose=True
)

# 审核员 Agent
reviewer = Agent(
    role="审核员",
    goal="确保研究报告的准确性、客观性和深度",
    backstory="""
    你是一位资深的学术审核员，曾在顶级 AI 会议发表多篇论文。
    你对技术细节有严格要求，不接受未经证实的说法。
    """,
    verbose=True
)

# 作家 Agent
writer = Agent(
    role="作家",
    goal="将研究报告转化为易于理解的科普文章",
    backstory="""
    你是一位科技作家，擅长用通俗易懂的语言解释复杂的技术概念。
    你的读者是普通开发者，你总能找出最有意思的角度来呈现内容。
    """,
    verbose=True
)

# ========== 3. 定义 Tasks ==========

research_task = Task(
    description="""
    研究以下主题：{topic}
    1. 搜索最新的技术动态和突破
    2. 整理关键信息和数据
    3. 提供至少 5 个具体例子或案例
    """,
    agent=researcher,
    expected_output="一份详细的研究报告，包含关键发现和数据"
)

review_task = Task(
    description="""
    审核研究员输出的报告：
    1. 核实关键事实和数据
    2. 指出逻辑漏洞或不足之处
    3. 提供具体的改进建议
    """,
    agent=reviewer,
    expected_output="审核意见和改进建议清单"
)

write_task = Task(
    description="""
    根据研究和审核结果，撰写一篇面向开发者的科普文章：
    1. 标题要有吸引力
    2. 内容要有深度但易读
    3. 包含具体的代码示例或实践建议
    """,
    agent=writer,
    expected_output="一篇完整的科普文章"
)

# ========== 4. 组建 Crew ==========

crew = Crew(
    agents=[researcher, reviewer, writer],
    tasks=[research_task, review_task, write_task],
    process="sequential",  # 顺序执行：研究 → 审核 → 写作
    verbose=True
)

# ========== 5. 运行 ==========

if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": "Agent Memory 架构"})
    print(result)
```

---

## 核心概念对应

| 概念 | 代码位置 |
|------|---------|
| **Agent 定义** | `Agent(role=..., goal=..., backstory=...)` |
| **Task 定义** | `Task(description=..., agent=..., expected_output=...)` |
| **Crew 组装** | `Crew(agents=[...], tasks=[...], process=...)` |
| **顺序执行** | `process="sequential"` |
| **层级执行** | `process="hierarchical"`（Manager → Agents） |

---

## 两种执行模式

### Sequential（顺序）

```mermaid
graph LR
    R[研究员] --> REV[审核员]
    REV --> W[作家]
    W --> OUT[输出]
```

### Hierarchical（层级）

```mermaid
graph TB
    M[Manager] --> R[研究员]
    M --> REV[审核员]
    M --> W[作家]
    R --> M
    REV --> M
    W --> M
    M --> OUT
```

---

## 使用 MCP Tools

```python
from crewai import Agent
from mcp import MCPClient

# 连接 MCP Server
mcp_client = MCPClient("http://localhost:8080")

researcher = Agent(
    role="研究员",
    goal="...",
    tools=mcp_client.get_tools()  # 接入 MCP 工具
)
```

---

## 常见问题排查

| 问题 | 解决方案 |
|------|---------|
| Agent 不调用工具 | 检查 `tools` 参数是否正确传入 |
| 任务顺序混乱 | 确认 `process` 设置正确 |
| 输出不完整 | 检查 `expected_output` 是否清晰 |
| Token 溢出 | 减少 Agent 数量或简化 Task 描述 |

---

## 学习路径建议

1. 先跑通上面的快速入门
2. 尝试 `process="hierarchical"` 模式
3. 添加自定义 MCP Tools
4. 学习 Task 之间的依赖设置
5. 接入 LangSmith 进行可观测性调试

---

*代码基于 CrewAI 0.30+ 版本*
