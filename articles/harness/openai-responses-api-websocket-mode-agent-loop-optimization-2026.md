# OpenAI Responses API WebSocket Mode：消除 Agent 循环的 40% 延迟瓶颈

## 来源

- **原始链接**：https://openai.com/index/speeding-up-agentic-workflows-with-websockets/
- **发布时间**：2026 年 3 月
- **官方标题**：Speeding up agentic workflows with WebSockets in the Responses API
- **引用来源**：OpenAI Engineering Blog

---

## 核心问题：API 开销成为 Agent 循环的瓶颈

当 LLM 推理速度从 65 TPS 提升到 1,000+ TPS 时，API 层面的开销不再是能被 GPU 推理时间掩盖的配角——它直接决定了用户体验。OpenAI 在 2026 年初发现，GPT-5.3-Codex-Spark 的 1,000 TPS 推理速度，反而让 Responses API 的延迟问题变得更加突出。

> "As inference gets faster, the cumulative API overhead from an agentic rollout is much more notable... Even with these improvements, Responses API overhead was too large relative to the speed of the model—that is, users had to wait for the CPUs running our API before they could use the GPUs serving the model."

本文深入解析 OpenAI 如何通过 WebSocket Mode 将 Agent 循环的端到端延迟降低 40%，以及这个优化背后的架构决策。

---

## 一、问题根源：HTTP 轮询架构的三大低效

### 1.1 重复的状态重建

在传统的 HTTP/轮询模式下，每个 Follow-up 请求都需要携带完整的对话历史。对于 Codex Agent 的多步骤修复任务，这意味着每次 API 调用都在重复处理相同的状态：

- 完整的对话历史 tokenization
- 历史上下文在每个请求中的验证和处理
- 中间服务（如图像处理）的网络跳转

即使 90% 的对话内容未发生变化，Agent 仍需为完整的对话历史支付处理成本。

### 1.2 连接建立的开销

每个请求都是一个新的 HTTP 连接，需要完整的 TLS 握手。对于有 5-20 次 Tool Call 的中等复杂度 Agent 会话，仅连接建立开销就可能达到数百毫秒。

### 1.3 架构性延迟叠加

```
[用户请求] → [API 服务验证] → [模型推理] → [工具执行] → [返回结果]
                ↑                    ↑
           每次请求都重复      推理之外的瓶颈
```

当推理本身足够快时，API 服务层的累积开销变得不可忽视。

---

## 二、解决方案：持久连接 + 增量状态

### 2.1 设计目标

OpenAI 的设计目标是：**保持开发者熟悉的 API Shape（response.create + previous_response_id），同时实现持久连接的效率**。

这是一个典型的「不改变契约，只改变实现」的设计约束。

### 2.2 WebSocket 原型验证

团队最初设计了一个「Treat tool call as hosted tool」的原型：

```
模型采样 Tool Call → 阻塞推理循环 → 通过 WebSocket 发送 Tool Call 给客户端
                   ↓
客户端执行 Tool → 发送 response.append 事件
                   ↓
推理循环继续 → 一次性完成 Pre-inference + Post-inference
```

这个原型的效果极为显著——它消除了跨 Agent  rollout 的重复 API 工作。但代价是 API Shape 变得陌生且复杂。

### 2.3 最终设计：连接作用域缓存

最终发布的 WebSocket Mode 保留了开发者熟悉的 API Shape：

```python
# 开发者代码不需要改变
response = client.responses.create(
    model="gpt-5.3-codex-spark",
    previous_response_id=prev_response_id,  # 关键：复用连接状态
    input=[{"role": "user", "content": "fix this bug"}]
)
```

在 WebSocket 连接上，服务器维护一个连接作用域的内存缓存，存储：

- 上一个 Response 对象
- 历史 Input/Output items
- Tool definitions 和 namespaces
- 可复用的采样 artifacts（如已渲染的 token）

当请求包含 `previous_response_id` 时，服务器从缓存中获取状态而非重建。

### 2.4 缓存带来的四大优化

| 优化项 | 技术实现 | 效果 |
|--------|----------|------|
| 安全分类器优化 | 只处理新输入，不重复处理完整历史 | 降低每次请求的安全检查开销 |
| Token 缓存 | 追加模式，复用已渲染 token，避免重复 tokenization | 减少 CPU 密集型操作 |
| 模型路由复用 | 跨请求复用成功的模型解析/路由逻辑 | 减少内部服务调用 |
| 重叠非阻塞操作 | Billing 等后处理与后续请求重叠 | 隐藏延迟 |

> "The goal was to get as close as possible to the minimal-overhead prototype but with an API shape developers already understood and built around."

---

## 三、性能数据与生态采用

### 3.1 核心数据

| 指标 | 数值 |
|------|------|
| 端到端延迟降低 | **40%** |
| GPT-5.3-Codex-Spark 推理速度 | 1,000+ TPS（峰值 4,000 TPS）|
| Alpha 用户反馈 | Up to 40% improvement |
| Vercel AI SDK | Latency decrease up to 40% |
| Cline 多文件工作流 | **39% faster** |
| Cursor（OpenAI 模型）| Up to **30% faster** |

### 3.2 生态快速采用

WebSocket Mode 在发布后迅速被主流工具采用：

- **Codex**：大多数流量已迁移到 WebSocket Mode
- **Vercel AI SDK**：官方集成
- **Cline**：多文件 Agent 工作流 39% 加速
- **Cursor**：OpenAI 模型推理 30% 加速

> "WebSocket mode is one of the most significant new capabilities in the Responses API since its launch in March 2025."

---

## 四、与 Anthropic 的 Brain-Hand 分离的架构对比

值得注意的是，OpenAI 的 WebSocket Mode 与 Anthropic 的 Managed Agents 在架构上有相似的设计哲学——**将 Agent 的状态管理与执行层分离**：

| 维度 | OpenAI WebSocket Mode | Anthropic Managed Agents |
|------|----------------------|---------------------------|
| **分离对象** | 连接状态（缓存）vs 执行（客户端） | Session（Brains）vs Sandbox（Hands） |
| **接口形式** | `previous_response_id` 引用缓存 | `getEvents()` + `emitEvent()` |
| **失效恢复** | 新连接重建缓存 | 新 Harness 从 Session 恢复 |
| **扩展方向** | 增量输入 + 状态复用 | 多 Brain + 多 Hand 的灵活连接 |

两者都在解决「如何让 Agent 系统在长时间运行中保持高效且可恢复」的问题，但侧重点不同：OpenAI 侧重**单次会话内的延迟优化**，Anthropic 侧重**跨会话的状态持久性与弹性**。

---

## 五、已知局限与未解决问题

### 5.1 连接状态丢失

WebSocket 连接断开后，缓存状态丢失。客户端需要重新建立 HTTP 连接并携带完整历史，这与 WebSocket 的效率优势相悖。

### 5.2 多客户端并发

当同一个 Agent 被多个客户端并发访问时，连接作用域的缓存无法跨客户端共享，可能导致状态不一致。

### 5.3 客户端实现复杂度

虽然服务器端对开发者透明，但客户端需要支持 WebSocket 的持久连接管理、心跳、以及断线重连逻辑。

---

## 六、工程启示

### 6.1 推理加速后的基础设施瓶颈

当模型推理变得足够快时，系统中的其他环节（网络、序列化、状态管理）会成为新的瓶颈。这要求 Agent 系统的设计者从「模型优先」转向「全链路优化」。

### 6.2 API 兼容性 vs 性能的正交性

OpenAI 的设计表明，可以在不破坏 API 兼容性的前提下实现显著的性能优化。关键是找到「抽象层」与「实现层」的边界——让开发者继续在抽象层工作，优化在实现层发生。

### 6.3 工具调用的本地化趋势

WebSocket Mode 将工具调用从「远程服务调用」转变为「本地消息传递」，这一模式与 Anthropic 的「execute(name, input) → string」接口设计思路一致——**工具调用越接近本地，Agent 循环延迟越低**。

---

## 七、检查清单：评估你的 Agent 系统是否需要 WebSocket 优化

- [ ] 你的 Agent 单次会话中有多于 5 次的工具调用？
- [ ] 你的 LLM 推理速度超过 500 TPS？
- [ ] 你的用户对延迟敏感（交互式 Agent vs 批量任务）？
- [ ] 你的 Agent 会话长度经常超过 20 轮对话？
- [ ] 你的基础设施是 OpenAI Responses API 或兼容实现？

如果满足 3 个以上，WebSocket Mode 或类似的持久连接优化值得评估。

---

**引用来源**：

> "The goal was to get as close as possible to the minimal-overhead prototype but with an API shape developers already understood and built around."
> — [OpenAI Engineering: Speeding up agentic workflows with WebSockets](https://openai.com/index/speeding-up-agentic-workflows-with-websockets/)

> "As inference gets faster, the services and systems that surround inference also need to speed up to transfer these gains to users."
> — [OpenAI Engineering: Speeding up agentic workflows with WebSockets](https://openai.com/index/speeding-up-agentic-workflows-with-websockets/)