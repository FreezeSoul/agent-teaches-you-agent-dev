# GPA: Learning GUI Process Automation from Demonstrations

> **本质**：用单次演示教会 Agent 做 GUI 自动化——基于视觉定位+MCP/CLI 工具集成，比 Gemini CUA 快 10 倍

> **来源**：arXiv:2604.01676（2026/04/02）| Salesforce Research / CMU / Others

---

## 一、基本概念

GUI Process Automation（GPA）是一个**轻量级通用视觉驱动 RPA 框架**，核心卖点是：

> **单次演示 = 一次 replay = 可复用的 GUI 自动化工具**

GPA 解决的是两个极端的各自的缺陷：

| 路径 | 优点 | 致命缺陷 |
|------|------|---------|
| 传统 RPA | 确定性强 | 脆弱（UI 变一下就坏）|
| VLM-based GUI Agent（Gemini CUA 等）| 通用性强 | 不确定（每次执行结果可能不同）、贵、慢 |
| **GPA** | **单次 demo = 稳定 replay** | **通用性比纯 VLM 弱** |

GPA 的定位：**让 VLM Agent 负责 reasoning 和 orchestration，把 GUI 执行交给 GPA**

---

## 二、核心技术/机制

### 2.1 Sequential Monte Carlo（SMC）定位

GPA 的核心创新是**基于 Sequential Monte Carlo 的视觉定位**：

- 给定一次 demo，SMC 在每次 replay 时对 GUI 元素位置进行**概率采样**
- 能处理 UI 缩放、检测不确定性
- 不依赖 DOM 结构，只依赖视觉外观

```python
# GPA 定位逻辑示意（概念层面）
for each frame:
    particles = smc_sample(visual_elements, previous_state)
    best_match = weighted_vote(particles)
    if confidence(best_match) < threshold:
        trigger_readiness_calibration()
```

### 2.2 Readiness Calibration（就绪校准）

这是 GPA 的第二个核心机制：

- **在执行关键操作前**，GPA 会检查 GUI 是否处于「可执行就绪状态」
- 等待动画完成、模态框弹出、页面加载
- 保证 replay 的确定性

### 2.3 隐私保障

- **完全本地执行**：不依赖云端 VLM
- 比 CUA（每次都要调 API）更隐私友好

---

## 三、作为 MCP/CLI 工具：Agent 集成架构

这是 GPA 对 Agent 工程师最关键的部分——GPA 如何作为工具被其他 Agent 调用：

### 3.1 两种集成方式

```
Agent（VLM Reasoning）
    ↓ call GPA（作为 MCP tool 或 CLI）
    ↓
GPA（本地执行 GUI 操作）
    ↓
返回执行结果给 Agent
```

**MCP 集成**：GPA 本身可以作为一个 **MCP Server**，暴露 `execute_gui_action` 等工具
**CLI 集成**：也可以通过命令行调用，适合脚本化场景

### 3.2 关键设计洞察

> **「代理分工」原则**：让专用系统处理执行，让 VLM Agent 只做 reasoning

这与 Agent 设计中的 **Plan-Execute 模式**（Stage 7 Orchestration）高度一致：
- Plan（VLM Agent）→ 决定做什么
- Execute（GPA）→ 执行 GUI 操作

### 3.3 与现有方案的对比

| 维度 | GPA | Gemini CUA |
|------|-----|-----------|
| 执行速度 | **10x 快** | 慢（每次调 API）|
| 确定性 | 高（确定性 replay）| 低（概率性 VLM 输出）|
| 隐私 | 完全本地 | 需要云端 API |
| 通用性 | 中（单次 demo 覆盖同类型任务）| 高（零样本）|
| MCP 工具化 | **原生支持** | 不支持 |

---

## 四、实验结果

### 4.1 核心数据

> **GPA 在长时域 GUI 任务上，成功率高于 Gemini 3 Pro（CUA），执行速度 10 倍快**

具体实验设定：长时域 GUI 任务（多步骤企业工作流）

### 4.2 三个核心优势量化

| 优势 | 描述 | 效果 |
|------|------|------|
| 鲁棒性 | SMC 处理 UI 缩放和检测不确定性 | 适应不同分辨率/DPI |
| 确定性 | Readiness Calibration 保证操作就绪 | replay 一致性 |
| 隐私 | 完全本地执行 | 无云端数据泄露风险 |

---

## 五、与演进路径的关系

### 属于：Stage 6（Tool Use） × Stage 7（Orchestration）

GPA 位于 **工具层** 和 **编排层** 的交叉点：

- **工具层**：GPA 作为可被 Agent 调用的 MCP/CLI 工具
- **编排层**：GPA 体现了 Plan-Execute 的编排分工原则

### 演进链

```
单工具调用（早期 Agent）
    ↓
MCP Server 生态（工具标准化）
    ↓
GPA 类专用执行器（专用工具 × 通用推理分离）
```

---

## 六、局限性

1. **单次 demo 的覆盖边界**：demo 能覆盖的任务类型有限，跨类型任务需要新的 demo
2. **VLM 依赖仍然存在**：demo 录制阶段需要 VLM 辅助（录制时的 GUI 理解）
3. **非视觉 UI 元素**：纯依赖视觉，对某些无图形界面的场景不适用
4. **与 VLM GUI Agent 的关系**：GPA 不是要取代 CUA，而是作为 CUA 的补充

---

## 七、实践指南

### 7.1 何时选 GPA vs CUA

```
选 GPA：
- 企业内部 RPA 场景（重复性高、界面稳定）
- 隐私敏感（金融、医疗）
- 需要确定性执行结果
- 需要 MCP/CLI 工具化

选 CUA（Gemini 等）：
- 零样本新任务（没有 demo）
- 探索性 UI 操作
- 界面变化频繁的场景
```

### 7.2 Agent 集成示例

```python
# Agent 调用 GPA 作为 MCP 工具
class GPATool:
    async def execute(self, demo_id: str, target_ui_state: dict):
        """
        GPA MCP Tool 接口
        - demo_id: 录制好的演示 ID
        - target_ui_state: 目标 UI 状态描述
        返回: 执行结果 + 截图
        """
        result = await smc_localization(demo_id, target_ui_state)
        if not result.ready:
            await readiness_calibration(result.current_state)
        return result.execute()
```

---

## 八、关键引用

> Zirui Zhao et al., "GPA: Learning GUI Process Automation from Demonstrations," arXiv:2604.01676, 2026/04/02.

---

## 九、标签

#tool-use #gui-automation #mcp #cli #enterprise #stage6 #stage7 #rpa #vision-based #plan-execute
