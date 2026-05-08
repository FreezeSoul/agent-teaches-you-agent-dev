# Agent Squad：意图分类驱动的多 Agent 编排框架——从 AWS Labs 到 2FastLabs 的生产级实践

> Agent Squad 是由 2FastLabs（原 AWS Labs）维护的轻量级开源多 Agent 编排框架，提供了从意图分类到团队协作的完整工作流。本文深度解析其架构设计：基于「智能意图分类」的动态路由机制 + 新增的 SupervisorAgent 团队协调模式，以及其与主流框架的差异化定位。

---

## 核心主张

**Agent Squad 的核心价值在于它回答了一个被大多数多 Agent 框架回避的问题**：当一个复杂请求进来时，谁来决定由哪个 Agent 处理？它的答案是「Classifier-first」——先用分类器理解用户意图，再动态路由到最适合的 Agent。这与 LangGraph 的「图驱动编排」或 CrewAI 的「角色驱动协作」有本质区别，是一种「入口智能」优先的架构思路。

---

## 一、Target：谁该关注

| 维度 | 说明 |
|------|------|
| **用户类型** | 后端/全栈工程师，需要快速搭建多 Agent 对话系统的团队 |
| **水平要求** | 熟悉 Python 或 TypeScript，理解 Agent 概念，有对话系统或 Chatbot 开发经验 |
| **场景** | 需要在多个专才 Agent 之间路由的对话类产品，从 Chatbot 到复杂的多域协调系统 |

---

## 二、Result：能带来什么

> GitHub Stars 数据（2026-05）：活跃增长中，从 AWS Labs 迁移到 2FastLabs 后独立运营

基于 GitHub README 的实际用例：

- **6 个专才 Agent 协作演示**：Travel Agent（Amazon Lex）、Weather Agent（Bedrock LLM + 外部 API）、Restaurant Agent（Bedrock Agent）、Math Agent（Bedrock LLM + 数学工具）、Tech Agent（Bedrock LLM）、Health Agent（Bedrock LLM）——一个 Streamlit 应用演示跨域对话的无缝切换
- **意图路由准确性**：Classifier 利用 Agent 特征和对话历史动态选择最合适的 Agent，支持短暂后续输入仍保持上下文连贯
- **并行处理能力**：SupervisorAgent 支持多个 Agent 查询并行执行，团队协调场景下效率倍增

---

## 三、Insight：凭什么做到这些

### 3.1 架构设计：Classifier-First 动态路由

Agent Squad 的核心工作流：

```
用户输入 → Classifier 分析 → 选择最适合的 Agent → Agent 处理输入 
         → 保存对话 → 更新对话历史 → 返回响应给用户
```

**Classifier 的核心输入**：
- Agents' Characteristics（各 Agent 的特征描述）
- Agents' Conversation History（对话历史）

**这意味着 Classifier 不只是做简单的关键词匹配，而是基于上下文语义做决策**——与 Agent 特征描述和历史状态联合判断。

### 3.2 SupervisorAgent：团队协调模式

新增的 SupervisorAgent 实现了「agent-as-tools」架构，允许一个主导 Agent 协调多个专业 Agent 团队并行工作：

> "The SupervisorAgent can be used in two powerful ways: Direct Usage — Call it directly when you need dedicated team coordination for specific tasks; Classifier Integration — Add it as an agent within the classifier to build complex hierarchical systems with multiple specialized teams."

**关键能力**：
- 🤝 **Team Coordination**：协调多个专业 Agent 共同处理复杂任务
- ⚡ **Parallel Processing**：同时执行多个 Agent 查询
- 🧠 **Smart Context Management**：跨所有团队成员维护对话历史
- 🔄 **Dynamic Delegation**：智能分配子任务给合适的团队成员

### 3.3 技术栈中立性

Agent Squad 明确表示兼容所有 Agent 类型（Bedrock、Anthropic、Lex 等），这意味着它不是某个云厂商的专属框架，而是一个**与模型和 Agent 类型解耦的编排中间件**。

> "🤖 Agent Compatibility — Works with all agent types (Bedrock, Anthropic, Lex, etc.)"

---

## 四、Proof：GitHub 热度与社区支撑

| 指标 | 数据 |
|------|------|
| **Stars** | 活跃增长中（原 AWS Labs 项目，迁移后独立运营） |
| **语言** | Python + TypeScript（双语言实现） |
| **部署** | AWS Lambda / 本地 / 任何云平台 |
| **维护** | 2FastLabs（原 AWS Labs 团队） |

**官方文档**：https://2fastlabs.github.io/agent-squad/

**预构建组件**：
- 多种内置 Agent
- 多种 Classifier 实现
- Streamlit 演示应用（AI Movie Production Studio / AI Travel Planner 等）

---

## 五、Threshold：快速上手

### 5.1 安装

```bash
# Python
pip install agent-squad

# Node.js / TypeScript
npm install agent-squad
# 或 yarn add agent-squad
```

### 5.2 快速示例（Python）

```python
from agent_squad import AgentSquad, Agent

# 定义专才 Agent
travel_agent = Agent(
    name="TravelAgent",
    model="bedrock",  # 或 anthropic / any LLM
    instructions="你是旅游规划专家，帮助用户预订航班和酒店"
)

weather_agent = Agent(
    name="WeatherAgent", 
    model="bedrock",
    instructions="你查询天气信息",
    tools=[open_meteo_tool]  # 可选工具
)

# 初始化 Squad
squad = AgentSquad(agents=[travel_agent, weather_agent])

# 用户输入自动路由到最适合的 Agent
response = squad.process("我想去东京，下周二的天气怎么样？")
```

### 5.3 SupervisorAgent 团队协作

```python
from agent_squad import SupervisorAgent, AgentSquad

# 创建 SupervisorAgent
supervisor = SupervisorAgent(
    name="TravelSupervisor",
    agents=[travel_agent, weather_agent, restaurant_agent]
)

# Supervisor 内部并行协调多个 Agent
response = supervisor.process(
    "帮我规划去东京的行程，包括天气、餐厅推荐和景点"
)
```

### 5.4 贡献入口

- 官方 GitHub：https://github.com/2fastlabs/agent-squad
- 文档：https://2fastlabs.github.io/agent-squad/
- 预构建示例涵盖 Customer Support Teams、AI Movie Production Studios、Travel Planning Services 等场景

---

## 六、与同类框架的差异化定位

| 框架 | 核心模式 | 路由机制 | Agent 类型 |
|------|---------|---------|-----------|
| **Agent Squad** | Classifier-first + Supervisor | 意图分类驱动，动态路由 | 模型无关 |
| **LangGraph** | 图驱动 | 预定义图结构，条件边 | LangChain 原生 |
| **CrewAI** | 角色驱动 | 角色协作，任务共享 | 固定角色定义 |
| **AutoGen/AG2** | 对话驱动 | Agent 间自动对话 | 多模型协作 |
| **OpenAI Agents SDK** | Sandbox-first | 内置 harness + sandbox | OpenAI 优先 |

**Agent Squad 的差异化**：是唯一一个将「意图分类」作为核心架构入口的框架——不是预先定义 Agent 协作图，而是让Classifier 根据实时上下文动态决定谁来处理。这在对话式多 Agent 场景下有独特的灵活性优势。

---

## 结语

Agent Squad 提供的是一种「入口智能」优先的多 Agent 编排思路：与其预先设计 Agent 之间的协作拓扑，不如让分类器根据上下文实时决定路由。它的 SupervisorAgent 进一步提供了团队级协调能力，支持并行处理和动态委托。

如果你正在构建需要根据用户意图动态选择处理路径的对话系统，Agent Squad 提供了一个轻量级、模型无关的解决方案——从 AWS Labs 生产验证迁移到独立维护，开源协议友好，上手门槛低。

---

**关联文章**：本文与「Anthropic Managed Agents：大脑与手的解耦」形成互补——后者解决的是 Agent 执行层的架构解耦，前者解决的是多 Agent 入口层的智能路由问题。两者共同构成现代 Agent 系统两大核心挑战（谁来处理 ↔ 执行层如何保证）的一体化回答。

**引用来源**：

> "The Agent Squad is a flexible framework for managing multiple AI agents and handling complex conversations. It intelligently routes queries and maintains context across interactions."
> — [2FastLabs/agent-squad GitHub README](https://github.com/2fastlabs/agent-squad)

> "Introducing SupervisorAgent: The Agent Squad now includes a powerful new SupervisorAgent that enables sophisticated team coordination between multiple specialized agents. This new component implements a 'agent-as-tools' architecture, allowing a lead agent to coordinate a team of specialized agents in parallel, maintaining context and delivering coherent responses."
> — [Agent Squad SupervisorAgent Documentation](https://2fastlabs.github.io/agent-squad/agents/built-in/supervisor-agent)
