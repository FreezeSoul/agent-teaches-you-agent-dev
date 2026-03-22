# Agent 设计模式

收录经典 Agent 设计模式，附带代码示例。

---

## 目录

### 基础模式（[README.md](./README.md)）

- [ReAct 模式](./README.md#react-模式) — 推理与执行分离
- [Plan-Execute 模式](./README.md#plan-execute-模式) — 规划与执行分离
- [Reflection 模式](./README.md#reflection-模式) — 自我反思与改进

### 进阶模式（[advanced_patterns.md](./advanced_patterns.md)）

- [Tool Mesh](./advanced_patterns.md#1-tool-mesh工具网格模式) — 工具共享与路由分发
- [Handoff](./advanced_patterns.md#2-handoff交接模式) — Agent 间控制权转移
- [Guardrail](./advanced_patterns.md#3-guardrail护栏模式) — 执行前后安全检查
- [Observability](./advanced_patterns.md#4-observability可观测性模式) — 全链路追踪与日志

---

## 模式对比速查

| 模式 | 核心思想 | 迭代 | 工具调用 | 适用场景 |
|------|---------|------|---------|---------|
| ReAct | 推理-执行交替 | 多轮 | ✅ | 搜索/问答 |
| Plan-Execute | 规划-执行分离 | 2阶段 | ✅ | 复杂任务 |
| Reflection | 自我反思 | 多轮 | ❌ | 内容生成 |
| Tool Mesh | 工具共享路由 | 灵活 | ✅ | 多 Agent 协作 |
| Handoff | 控制权转移 | 按需 | ✅ | 层级协作 |
| Guardrail | 安全检查 | 每步前后 | 均可 | 企业应用 |

---

*持续更新中*
