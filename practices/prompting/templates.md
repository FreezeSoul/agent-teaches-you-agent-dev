# Prompt 模板与技巧

> 好的 Prompt 是 Agent 效果的地基。本目录收录可直接复用的模板。

---

## 模板分类

| 类别 | 文件 | 说明 |
|------|------|------|
| [Agent 系统模板](./templates.md#1-agent-system-prompt-模板) | `templates.md` | 角色、目标、约束设定 |
| [工具调用模板](./templates.md#2-tool-use-prompt) | `templates.md` | 教会 LLM 调用外部工具 |
| [ReAct 模板](./templates.md#3-react-prompt-模板) | `templates.md` | 推理-执行交替格式 |
| [Few-shot 模板](./templates.md#4-few-shot-示例模板) | `templates.md` | 通过示例澄清任务 |
| [思维链模板](./templates.md#5-chain-of-thought) | `templates.md` | 分步推理引导 |
| [安全边界模板](./templates.md#6-安全边界模板) | `templates.md` | 约束有害或敏感操作 |
| [多角色辩论模板](./templates.md#7-多角色辩论模板) | `templates.md` | 多个 Agent 立场对立 |

---

## 1. Agent System Prompt 模板

```markdown
# Role: {role_name}
# Goal: {specific_goal}
# Backstory: {background_and_context}

## 核心能力
- 能力 1：{具体描述}
- 能力 2：{具体描述}

## 行为约束
- 不做 X
- 不说 Y
- 始终做 Z

## 输出格式
{expected_output_format}

## 上下文范围
{context_scope}
```

### 变体：带温度/风格控制

```markdown
# Role: 专业 {domain} 分析师

## 沟通风格
- 语气：专业、简洁
- 输出长度：每点不超过 2 句话
- 必须使用中文，术语保留英文

## 专业边界
- 只讨论 {domain} 领域
- 超出范围说"这个话题超出我的专业范围"
```

---

## 2. Tool Use Prompt

```markdown
你可以通过以下工具完成任务：

## 可用工具

### search_web(query: str) → str
- 用途：搜索网络获取最新信息
- 参数：query 是搜索关键词

### get_weather(city: str) → str
- 用途：查询城市天气
- 参数：city 是城市名（中文）

### calculator(expr: str) → str
- 用途：执行数学计算
- 参数：expr 是数学表达式

## 调用规则

1. 先判断用户问题是否需要工具
2. 如果需要，选择最合适的工具
3. 调用后基于结果回答
4. 如果工具返回空结果，说"未找到相关信息"
```

---

## 3. ReAct Prompt 模板

```markdown
针对问题：{user_question}

请按以下格式交替进行推理和行动：

Thought: {你的思考过程}
Action: {工具名称}({"参数"})
Observation: {工具返回结果}

... (重复直到得到答案)

Thought: 现在我有足够信息，可以回答了
Final Answer: {最终回答}
```

### ReAct 示例

```
问题：北京今天天气如何？

Thought: 用户问天气，需要调用天气工具
Action: get_weather({"city": "北京"})
Observation: 晴，26°C

Thought: 工具返回了天气信息，可以回答了
Final Answer: 北京今天天气晴朗，气温26°C。
```

---

## 4. Few-shot 示例模板

```markdown
通过示例帮助模型理解任务：

## 示例 1

输入: {example_input_1}
输出: {example_output_1}

## 示例 2

输入: {example_input_2}
输出: {example_output_2}

## 示例 3

输入: {example_input_3}
输出: {example_output_3}

---

现在回答：
输入: {actual_input}
输出:
```

---

## 5. Chain of Thought

```markdown
回答这个问题时，请分步骤思考：

Step 1: {明确问题本质}
Step 2: {拆解关键要素}
Step 3: {逐一分析}
Step 4: {综合得出结论}

---

问题：{user_question}

回答：
```

### Zero-shot CoT 变体

```
请仔细思考这个问题：{question}

（模型自动生成推理步骤）
```

---

## 6. 安全边界模板

```markdown
## 安全约束

### 绝对禁止
- 提供医疗诊断建议
- 提供法律意见
- 透露他人个人信息
- 执行未经确认的危险操作

### 条件限制
- 如果不确定 → 说"我不确定，建议咨询专业人士"
- 如果涉及隐私 → 说"这个问题涉及隐私，无法回答"
- 如果超出知识范围 → 说"这个问题我不确定，建议核实"

### 敏感性判断
如果用户请求涉及以下内容，直接拒绝：
- 违法操作指导
- 伤害他人
- 绕过安全机制
```

---

## 7. 多角色辩论模板

```markdown
## 辩论场景

你是 {Role A}，立场是 {position_A}。
对方是 {Role B}，立场是 {position_B}。

## 规则
1. 各自阐述观点（不超过 3 句话）
2. 针对对方观点提出质疑
3. 对方反驳后，补充论据
4. 轮流发言，共 3 轮
5. 最后由主持人总结

## 议题
{topic}

---

现在开始第一轮。

{Role A}：
```

---

## 技巧汇总

| 技巧 | 适用场景 | 效果 |
|------|---------|------|
| 角色设定 | 需要领域专业知识 | ⭐⭐⭐⭐⭐ |
| 输出格式约束 | 需要结构化输出 | ⭐⭐⭐⭐⭐ |
| Chain of Thought | 复杂推理任务 | ⭐⭐⭐⭐⭐ |
| Few-shot | 任务不明确或边界模糊 | ⭐⭐⭐⭐ |
| 安全边界 | 避免有害输出 | ⭐⭐⭐⭐⭐ |
| 示例+约束组合 | 精准控制输出风格 | ⭐⭐⭐⭐⭐ |

---

## 避坑指南

1. **不要过度约束**：Prompt 太长会让模型忽略关键指令（一般不超过 2000 tokens）
2. **不要模糊指令**：每个指令应该明确可执行
3. **不要矛盾**：约束之间不能相互冲突
4. **及时更新**：模型版本变化可能导致 Prompt 效果改变
5. **测试边界**：在正式使用前测试各种边界 case

---

*持续更新中*
