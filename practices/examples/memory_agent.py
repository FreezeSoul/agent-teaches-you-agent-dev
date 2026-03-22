"""
Agent Memory 架构示例 — 三种记忆层次实现

短期记忆（Short-Term）：对话历史，窗口内滚动
长期记忆（Long-Term）：向量检索，支持跨会话
人格记忆（Personality）：持久化角色设定
"""

from dataclasses import dataclass, field
from typing import TypedDict
from datetime import datetime
import time


# ========== 1. 短期记忆 — 滚动窗口 ==========

class ShortTermMemory:
    """
    固定大小的对话历史窗口，新消息顶掉旧消息
    适用于单会话内的上下文维护
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.messages: list[dict] = []

    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "ts": datetime.now().isoformat()
        })
        # 滚动窗口
        if len(self.messages) > self.window_size:
            self.messages.pop(0)

    def get_context(self) -> list[dict]:
        return self.messages[-self.window_size:]

    def clear(self):
        self.messages.clear()

    def __len__(self):
        return len(self.messages)


# ========== 2. 长期记忆 — 向量语义检索（简化版） ==========

@dataclass
class MemoryEntry:
    content: str
    embedding: list[float]  # 简化：用随机向量代替真实 embedding
    ts: str
    importance: int = 1  # 1-5 分

    def relevance_score(self, query_embedding: list[float]) -> float:
        """余弦相似度（简化版）"""
        import math
        dot = sum(a * b for a, b in zip(self.embedding, query_embedding))
        norm_a = math.sqrt(sum(a * a for a in self.embedding))
        norm_b = math.sqrt(sum(b * b for b in query_embedding))
        return dot / (norm_a * norm_b) if norm_a * norm_b > 0 else 0


class LongTermMemory:
    """
    基于语义相似度的长期记忆
    真实实现需要接入向量数据库（如 ChromaDB、Milvus）
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.entries: list[MemoryEntry] = []

    def add(self, content: str, importance: int = 3):
        """存入记忆，自动生成 embedding（简化版）"""
        import hashlib
        # 用内容 hash 生成伪 embedding（真实场景用 LLM embedding）
        h = hashlib.md5(content.encode()).digest()
        embedding = [b / 255.0 for b in h[:8]]  # 8 维向量
        self.entries.append(MemoryEntry(
            content=content,
            embedding=embedding,
            ts=datetime.now().isoformat(),
            importance=importance
        ))

    def retrieve(self, query: str, query_embedding: list[float] | None = None) -> list[MemoryEntry]:
        """检索最相关的记忆"""
        if query_embedding is None:
            import hashlib
            h = hashlib.md5(query.encode()).digest()
            query_embedding = [b / 255.0 for b in h[:8]]

        scored = [(e, e.relevance_score(query_embedding)) for e in self.entries]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [e for e, _ in scored[:self.top_k]]

    def forget_old(self, days: int = 30):
        """遗忘超过 N 天的记忆"""
        # 简化实现
        pass


# ========== 3. 人格记忆 — 持久化角色设定 ==========

@dataclass
class PersonalityMemory:
    """持久化的 Agent 人格、价值观、行为约束"""
    name: str
    role: str
    goals: list[str]
    constraints: list[str]
    backstory: str = ""

    def system_prompt(self) -> str:
        parts = [
            f"# Role: {self.name}",
            f"# Goal: {', '.join(self.goals)}",
            f"# Backstory: {self.backstory}",
            "",
            "## 行为约束",
        ]
        for c in self.constraints:
            parts.append(f"- {c}")
        return "\n".join(parts)

    @classmethod
    def from_dict(cls, data: dict) -> "PersonalityMemory":
        return cls(**data)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "goals": self.goals,
            "constraints": self.constraints,
            "backstory": self.backstory,
        }


# ========== 4. 统一记忆系统 ==========

class UnifiedMemory:
    """
    整合三种记忆，对 LLM 输出完整上下文
    """

    def __init__(self, personality: PersonalityMemory, stm_window: int = 10, ltm_top_k: int = 5):
        self.personality = PersonalityMemory(**personality) if isinstance(personality, dict) else personality
        self.stm = ShortTermMemory(window_size=stm_window)
        self.ltm = LongTermMemory(top_k=ltm_top_k)

    def add_user_message(self, content: str):
        self.stm.add("user", content)

    def add_agent_message(self, content: str):
        self.stm.add("assistant", content)

    def store_important(self, content: str, importance: int = 4):
        """重要信息存入长期记忆"""
        self.ltm.add(content, importance)

    def get_full_context(self, query: str = "") -> str:
        """生成完整上下文给 LLM"""
        parts = [
            "## System Profile",
            self.personality.system_prompt(),
            "",
            "## Conversation History (Recent)",
        ]
        for msg in self.stm.get_context():
            parts.append(f"- [{msg['role']}]: {msg['content']}")

        if query:
            relevant = self.ltm.retrieve(query)
            if relevant:
                parts.append("")
                parts.append("## Relevant Past Experience")
                for e in relevant:
                    parts.append(f"- {e.content}")

        return "\n".join(parts)


# ========== 运行示例 ==========

if __name__ == "__main__":
    # 定义 Agent 人格
    persona = PersonalityMemory(
        name="TechAnalyst",
        role="AI 技术分析师",
        goals=[
            "跟踪最新 AI Agent 技术动态",
            "提供深度技术分析和见解",
        ],
        constraints=[
            "不臆测未经证实的技术",
            "引用必须标注来源",
        ],
        backstory="5 年 AI 技术研究经验，专注 Agent 和 LLM 应用"
    )

    # 创建统一记忆
    memory = UnifiedMemory(persona=persona.to_dict())

    # 对话
    memory.add_user_message("介绍一下 MCP 协议")
    memory.add_agent_message("MCP（Model Context Protocol）是 Anthropic 提出的...")

    # 重要信息存入长期记忆
    memory.store_important("MCP = Model Context Protocol，Anthropic 提出", importance=5)
    memory.store_important("MCP 生态：Claude Desktop、Cursor、Cline 支持", importance=4)

    # 查询时检索相关记忆
    context = memory.get_full_context("MCP 是什么，支持哪些工具")
    print(context)
