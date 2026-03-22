"""
多 Agent 协作模式示例 — 纯 Python 实现

演示三种协作模式：
1. Sequential（顺序）：一个完成后另一个接替
2. Parallel（并行）：多个 Agent 同时处理不同子任务
3. Hierarchical（层级）：Manager 分配任务给 Workers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class AgentRole(Enum):
    MANAGER = "manager"
    WORKER = "worker"


@dataclass
class Message:
    sender: str
    receiver: str
    content: Any
    type: str = "text"


class BaseAgent(ABC):
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.inbox: list[Message] = []

    @abstractmethod
    def process(self, message: Message) -> Message | None:
        pass

    def receive(self, message: Message):
        self.inbox.append(message)

    def send(self, receiver: "BaseAgent", content: Any, msg_type: str = "text") -> Message:
        msg = Message(sender=self.name, receiver=receiver.name, content=content, type=msg_type)
        receiver.receive(msg)
        return msg


# ========== 顺序协作 ==========

class Researcher(BaseAgent):
    def __init__(self):
        super().__init__("研究员", AgentRole.WORKER)

    def process(self, message: Message) -> Message:
        topic = message.content
        findings = f"【{self.name}】完成了关于 '{topic}' 的研究，结论：技术可行，市场前景广阔"
        return Message(sender=self.name, receiver="作家", content=findings)


class Writer(BaseAgent):
    def __init__(self):
        super().__init__="作家", AgentRole.WORKER)
        super().__init__(self, name

    def process(self, message: Message) -> Message:
        research = message.content
        article = f"【{self.name}】基于研究写成文章：\n{research}\n\n本文由 AI 辅助生成。"
        return Message(sender=self.name, receiver="系统", content=article)


def sequential_workflow(topic: str):
    """顺序执行：研究员 → 作家"""
    researcher = Researcher()
    writer = Writer()

    # 触发工作流
    result = researcher.process(Message(sender="系统", receiver=researcher.name, content=topic))
    final = writer.process(result)
    return final.content


# ========== 并行协作 ==========

class ParallelWorker(BaseAgent):
    def __init__(self, name: str, specialty: str):
        super().__init__(name, AgentRole.WORKER)
        self.specialty = specialty

    def process(self, message: Message) -> Message:
        task = message.content
        result = f"【{self.name}】（专长: {self.specialty}）完成: {task}"
        return Message(sender=self.name, receiver="聚合器", content=result)


class Aggregator(BaseAgent):
    def __init__(self):
        super().__init__("聚合器", AgentRole.MANAGER)

    def process(self, message: Message) -> Message:
        # 收集所有 Worker 结果并聚合
        results = message.content  # list of results
        summary = "【聚合器】汇总结果：\n" + "\n".join(f"  - {r}" for r in results)
        return Message(sender=self.name, receiver="系统", content=summary)


def parallel_workflow(tasks: list[str]) -> str:
    """并行执行：多个 Worker 同时处理，最后聚合"""
    workers = [
        ParallelWorker("Worker-A", "数据分析"),
        ParallelWorker("Worker-B", "竞品调研"),
        ParallelWorker("Worker-C", "用户访谈"),
    ]
    aggregator = Aggregator()

    # 并行处理
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(w.process, Message(sender="系统", receiver=w.name, content=t))
                   for w, t in zip(workers, tasks)]
        results = [f.result().content for f in futures]

    # 聚合
    final = aggregator.process(Message(sender="系统", receiver=aggregator.name, content=results))
    return final.content


# ========== 层级协作 ==========

class Manager(BaseAgent):
    def __init__(self, workers: list[BaseAgent]):
        super().__init__("Manager", AgentRole.MANAGER)
        self.workers = {w.name: w for w in workers}

    def process(self, message: Message) -> Message:
        task = message.content
        assignments = {
            "Worker-X": "子任务 A：架构设计",
            "Worker-Y": "子任务 B：代码实现",
        }
        # 分配任务
        for worker_name, subtask in assignments.items():
            if worker_name in self.workers:
                self.workers[worker_name].receive(
                    Message(sender=self.name, receiver=worker_name, content=subtask)
                )
        # 等待结果（简化版，同步等待）
        worker_results = {}
        for name, worker in self.workers.items():
            if worker.inbox:
                result = worker.process(worker.inbox[-1])
                worker_results[name] = result.content

        summary = f"【Manager】汇总 Worker 结果：{worker_results}"
        return Message(sender=self.name, receiver="系统", content=summary)


def hierarchical_workflow(main_task: str) -> str:
    """层级执行：Manager 分配给 Workers"""
    workers = [
        type('Worker', (), {'name': f'Worker-{c}', 'inbox': [], 'role': AgentRole.WORKER,
                            'receive': lambda s,m: s.inbox.append(m),
                            'process': lambda s,m: Message(s.name, "系统", f"{m.content} 完成")})()
        for c in "XY"
    ]
    manager = Manager(workers)
    result = manager.process(Message(sender="系统", receiver=manager.name, content=main_task))
    return result.content


# ========== 运行示例 ==========

if __name__ == "__main__":
    print("=" * 50)
    print("顺序协作：研究员 → 作家")
    print("=" * 50)
    print(sequential_workflow("AI Agent 发展趋势"))

    print("\n" + "=" * 50)
    print("并行协作：多 Worker 同时处理")
    print("=" * 50)
    print(parallel_workflow(["市场分析", "竞品调研", "用户访谈"]))

    print("\n" + "=" * 50)
    print("层级协作：Manager 分配任务")
    print("=" * 50)
    print(hierarchical_workflow("开发一个 Agent 系统"))
