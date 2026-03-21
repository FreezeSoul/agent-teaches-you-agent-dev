# AutoGen 快速入门示例

> 两个基础模式：Two-Agent 对话 和 Group Chat 群聊

---

## 环境准备

```bash
pip install pyautogen
```

---

## 模式一：Two-Agent 对话

```python
import autogen

# ========== 1. 配置 LLM ==========
llm_config = {
    "model": "gpt-4o",
    "api_key": "your-api-key",  # 使用 os.getenv 更安全
    "temperature": 0.8
}

# ========== 2. 定义 Assistant Agent ==========
assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config=llm_config,
    system_message="""
    你是一位资深的 Python 开发者，擅长编写清晰、高效的代码。
    你会主动提供最佳实践建议。
    """
)

# ========== 3. 定义 User Proxy Agent ==========
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",  # NEVER | TERMINATE | ALWAYS
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False
    }
)

# ========== 4. 开始对话 ==========
user_proxy.initiate_chat(
    assistant,
    message="帮我写一个快速排序函数，并用 pytest 写测试。"
)
```

---

## 模式二：Group Chat 群聊

```python
import autogen

llm_config = {
    "model": "gpt-4o",
    "api_key": "your-api-key",
    "temperature": 0.8
}

# ========== 1. 定义多个 Agent ==========

# 工程师：负责写代码
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message="""
    你是一位 Python 工程师，负责编写高质量的代码。
    当收到任务时，先写代码，然后解释你的实现思路。
    """
)

# 审核员：负责审查代码
reviewer = autogen.AssistantAgent(
    name="Reviewer",
    llm_config=llm_config,
    system_message="""
    你是一位代码审核专家，负责审查代码质量和潜在问题。
    给出具体的改进建议。
    """
)

# 用户代理：协调对话
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10
)

# ========== 2. 创建 GroupChat ==========
groupchat = autogen.GroupChat(
    agents=[user_proxy, engineer, reviewer],
    messages=[],
    max_round=10,
    speaker_selection_method="auto"  # auto | round_robin | random
)

# ========== 3. 创建 Manager ==========
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config
)

# ========== 4. 启动群聊 ==========
user_proxy.initiate_chat(
    manager,
    message="写一个计算斐波那契数列的函数，并审查代码质量。"
)
```

---

## 模式三：人机协同（Human-in-the-Loop）

```python
import autogen

llm_config = {
    "model": "gpt-4o",
    "api_key": "your-api-key"
}

# 设置为 TERMINATE 模式，遇到关键决策时暂停等人类确认
assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="TERMINATE",  # 关键时暂停
    max_consecutive_auto_reply=3
)

# 当 Agent 需要确认时，会停止并等待人类输入
user_proxy.initiate_chat(
    assistant,
    message="删除 /tmp/test 目录"
)
# Agent 会先问："确定要删除吗？" 等待确认后才执行
```

---

## 核心概念对应

| 概念 | 代码 |
|------|------|
| **Assistant Agent** | `autogen.AssistantAgent(name=..., llm_config=...)` |
| **User Proxy Agent** | `autogen.UserProxyAgent(human_input_mode=...)` |
| **GroupChat** | `autogen.GroupChat(agents=[...], max_round=...)` |
| **GroupChatManager** | `autogen.GroupChatManager(groupchat=..., llm_config=...)` |

---

## GroupChat 流程图

```mermaid
graph TB
    UP[UserProxy] --> GM[GroupChatManager]
    GM --> ENG[Engineer]
    GM --> REV[Reviewer]
    ENG --> GM
    REV --> GM
    GM --> UP

    UP -->|"确认"| GM
```

---

## 工具调用配置

```python
# 配置代码执行
code_exec_config = {
    "work_dir": "coding",
    "use_docker": True,  # 推荐用 Docker 隔离
    "timeout": 300
}

# 配置函数调用
function_config = {
    "name": "my_function",
    "description": "我的工具函数",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {"type": "string"}
        },
        "required": ["input"]
    }
}
```

---

## 常见问题排查

| 问题 | 解决方案 |
|------|---------|
| GroupChat 死循环 | 设置 `max_round` 限制 |
| 代码执行危险操作 | 开启 `use_docker=True` |
| Agent 不回复 | 检查 `human_input_mode` 设置 |
| Token 溢出 | 设置 `max_consecutive_auto_reply` 限制 |

---

## 与 CrewAI 的对比

| 维度 | AutoGen | CrewAI |
|------|---------|--------|
| 多 Agent 模式 | GroupChat | Crew + Process |
| 角色定义 | System Message | Role + Goal + Backstory |
| 层级协作 | 需自行实现 | 内置 Hierarchical |
| 人机协同 | 原生支持 | 需配置 |
| Microsoft 生态 | ✅ 深度集成 | ❌ |

---

## 学习路径建议

1. 先跑通 Two-Agent 对话示例
2. 尝试 GroupChat 群聊
3. 学习人机协同配置
4. 接入 LangSmith 进行可观测性调试

---

*代码基于 AutoGen 0.2.x 版本*
