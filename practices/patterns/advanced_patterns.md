"""
Agent 设计模式 — 进阶篇

在 basic patterns 基础上，补充生产级高频模式。
"""

# ========== 1. Tool Mesh（工具网格）模式 ==========
"""
多个 Agent 共享同一工具池，通过路由分发任务。
避免重复定义工具，每个工具可被多个 Agent 调用。
"""

class ToolMeshRouter:
    def __init__(self, agents: list, tools: dict):
        self.agents = {a.name: a for a in agents}
        self.tools = tools  # name -> tool_func

    def route(self, task: str, target_agent: str):
        agent = self.agents.get(target_agent)
        if not agent:
            return f"Unknown agent: {target_agent}"
        return agent.execute(task, available_tools=self.tools)


# ========== 2. Handoff（交接）模式 ==========
"""
Agent 之间转移控制权，接手方完全继承上下文。
CrewAI hierarchical 模式的基础实现。
"""

class Handoff:
    def __init__(self, from_agent: str, to_agent: str, reason: str, context: dict):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.reason = reason
        self.context = context  # 完整上下文传递


class Agent:
    def __init__(self, name: str, fallback_agent: str = None):
        self.name = name
        self.fallback = fallback_agent

    def can_handle(self, task: str) -> bool:
        """判断是否能处理该任务"""
        return True  # 简化

    def handoff_to(self, task: str, context: dict) -> any:
        """交接给下一个 Agent"""
        if self.fallback:
            handoff = Handoff(self.name, self.fallback, "capability_limit", context)
            print(f"{self.name} → 交接给 {self.fallback}，原因: {handoff.reason}")
            from_agent = self._get_agent(self.fallback)
            return from_agent.execute(task, handoff.context)
        return "无可用 Agent"

    def execute(self, task: str, context: dict = None):
        return f"{self.name} 处理: {task}"


# ========== 3. Guardrail（护栏）模式 ==========
"""
在 Agent 执行前/后插入检查层，防止危险操作。
类似 AutoGen 的 human_input_mode 但更通用。
"""

from enum import Enum

class RiskLevel(Enum):
    SAFE = "safe"
    WARN = "warn"
    BLOCK = "block"

class Guardrail:
    def __init__(self, rules: list):
        # rules: [(pattern, risk_level, message), ...]
        self.rules = rules

    def check(self, action: str) -> tuple[RiskLevel, str]:
        for pattern, level, msg in self.rules:
            if pattern in action:
                return level, msg
        return RiskLevel.SAFE, "OK"


class GuardedAgent:
    def __init__(self, agent: Agent, guardrail: Guardrail):
        self.agent = agent
        self.guardrail = guardrail

    def execute(self, task: str):
        level, msg = self.guardrail.check(task)
        if level == RiskLevel.BLOCK:
            return f"⛔ 阻止: {msg}"
        elif level == RiskLevel.WARN:
            print(f"⚠️ 警告: {msg}")
        return self.agent.execute(task)


# ========== 4. Observability（可观测性）模式 ==========
"""
结构化日志 + trace_id 串联请求全链路。
生产环境调试必备。
"""

import uuid
from datetime import datetime
from typing import Optional

class TraceContext:
    def __init__(self, trace_id: str = None, parent_id: str = None):
        self.trace_id = trace_id or str(uuid.uuid4())[:8]
        self.parent_id = parent_id
        self.span_id = str(uuid.uuid4())[:8]

    def log(self, event: str, data: any = None):
        print(f"[{self.trace_id}] {datetime.now().isoformat()} | {event} | data={data}")


class ObservableAgent:
    def __init__(self, name: str):
        self.name = name

    def execute(self, task: str, ctx: Optional[TraceContext] = None) -> str:
        ctx = ctx or TraceContext()
        ctx.log("agent_start", {"task": task, "agent": self.name})

        # 模拟执行
        result = f"{self.name} 完成: {task}"

        ctx.log("agent_end", {"result": result[:50]})
        return result


class ToolWithTracing:
    def __init__(self, name: str, func: callable):
        self.name = name
        self.func = func

    def call(self, args: dict, ctx: TraceContext) -> any:
        ctx.log("tool_start", {"tool": self.name, "args": args})
        result = self.func(**args)
        ctx.log("tool_end", {"tool": self.name, "result": str(result)[:50]})
        return result


# ========== 运行示例 ==========

if __name__ == "__main__":
    # 1. Tool Mesh
    print("=== Tool Mesh ===")
    router = ToolMeshRouter(agents=[Agent("Researcher"), Agent("Writer")],
                            tools={"search": lambda q: f"结果: {q}"})
    print(router.route("AI 最新进展", "Researcher"))

    # 2. Handoff
    print("\n=== Handoff ===")
    senior = Agent("Senior Dev")
    junior = Agent("Junior Dev", fallback_agent="Senior Dev")
    junior.handoff_to("写一个操作系统", {})

    # 3. Guardrail
    print("\n=== Guardrail ===")
    rules = [
        ("rm -rf", RiskLevel.BLOCK, "危险命令禁止执行"),
        ("drop table", RiskLevel.BLOCK, "数据库删除操作禁止"),
        ("format", RiskLevel.WARN, "格式化操作请确认"),
    ]
    guarded = GuardedAgent(Agent("Helper"), Guardrail(rules))
    print(guarded.execute("帮我格式化磁盘"))
    print(guarded.execute("帮我查天气"))

    # 4. Observability
    print("\n=== Observability ===")
    ctx = TraceContext()
    agent = ObservableAgent("Coder")
    agent.execute("写一个快速排序", ctx)
