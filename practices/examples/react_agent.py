"""
ReAct 模式示例 — 纯 Python 实现，不依赖特定框架

ReAct = Reasoning + Acting
交替进行「思考」和「行动」，每步同时输出推理和决策。
"""

import json
from dataclasses import dataclass
from typing import Literal


@dataclass
class Tool:
    name: str
    description: str
    func: callable


# ========== 内置工具 ==========

def search_web(query: str) -> str:
    """模拟网络搜索"""
    db = {
        "北京人口": "北京市常住人口约 2189 万（2023 年）",
        "Python 优势": "Python 优势：简洁易学、生态丰富、应用广泛",
        "LLM": "LLM = Large Language Model，大语言模型",
    }
    return db.get(query, f"未找到 '{query}' 相关结果")


def calculator(expr: str) -> str:
    """模拟计算器"""
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


def get_weather(city: str) -> str:
    """模拟天气查询"""
    weather_db = {
        "北京": "晴，26°C",
        "上海": "多云，28°C",
        "深圳": "雷阵雨，30°C",
    }
    return weather_db.get(city, f"未找到 {city} 的天气信息")


# ========== ReAct Agent ==========

class ReActAgent:
    def __init__(self, tools: list[Tool], max_iterations: int = 10):
        self.tools = {t.name: t for t in tools}
        self.max_iterations = max_iterations

    def think(self, history: list[dict], query: str) -> dict:
        """模拟 LLM 的思考过程（真实实现需接入 LLM API）"""
        last_obs = history[-1]["observation"] if history else ""
        query_context = f"用户问题: {query}\n历史: {last_obs}"
        available = ", ".join(self.tools.keys())

        # 简化模拟：基于规则判断
        if "天气" in query or "temperature" in query.lower():
            city = query.split()[-1]
            return {"action": "get_weather", "args": {"city": city}}
        elif "计算" in query or any(op in query for op in ["+", "-", "*", "/"]):
            expr = "".join(c for c in query if c in "0123456789+-*/. ")
            return {"action": "calculator", "args": {"expr": expr}}
        elif "人口" in query or "什么是" in query:
            kw = query.replace("什么是", "").replace("北京人口", "北京人口").strip()
            return {"action": "search_web", "args": {"query": kw}}
        else:
            return {"action": "search_web", "args": {"query": query}}

    def run(self, query: str) -> str:
        history = []
        for i in range(self.max_iterations):
            decision = self.think(history, query)
            action = decision["action"]
            args = decision["args"]

            if action not in self.tools:
                return f"未知工具: {action}"

            result = self.tools[action].func(**args)
            history.append({
                "step": i + 1,
                "action": action,
                "args": args,
                "observation": result
            })

            # 简单终止判断
            if len(history) >= 2 and action == "search_web":
                return result

        return "达到最大迭代次数"


# ========== 运行示例 ==========

if __name__ == "__main__":
    tools = [
        Tool("search_web", "搜索网络信息", search_web),
        Tool("calculator", "执行数学计算", calculator),
        Tool("get_weather", "查询城市天气", get_weather),
    ]

    agent = ReActAgent(tools)

    queries = [
        "北京人口是多少？",
        "计算 123 * 456",
        "深圳天气怎么样？",
    ]

    for q in queries:
        print(f"\n问题: {q}")
        print(f"回答: {agent.run(q)}")
