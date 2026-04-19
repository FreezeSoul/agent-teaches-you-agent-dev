# 通用Agent评测的五层架构：从Domain-Specialized到General Agent Evaluation

> **核心问题**：为什么SWE-Agent（4,161行代码）能做到的事，一个131行的通用Agent也能做到90%的程度？Agent评测的碎片化现状掩盖了什么样的架构演进规律？
>
> **读完能得到什么**：一个五层评测架构框架；量化数据说明通用Agent为何在成本/复杂度上优于专用Agent；以及对"Level 5 General Agent Evaluation"这个缺失层的具体定义。

---

## 一、从专用Agent到通用Agent：一次正在重复的历史

2020年的NLP领域经历过一次类似的转变：研究者们从针对每个任务训练独立模型（文本分类、问答、翻译、摘要...各自为政），转向训练一个通用大模型，再通过Prompt或微调适配具体任务。Sutton的"苦涩教训"[^1]精准预言了这一路径：**利用算力的通用方法最终总会超越手工设计的专用方案**。

2026年的AI Agent领域正在重演这一幕。

当前主流的SWE Agent（如SWE-agent、Claude Code）、Research Agent（如OpenAI Deep Research、Perplexity）、Web Agent（如Operator）各自独立开发，却在内部共享几乎相同的组件：ReAct风格的推理循环、记忆子系统、工具调用接口、错误处理与重试机制。[^2]这些组件本质上是通用的，却被打包进了高度专用化的系统里。

ICLR 2026的一篇博客文章[^3]用两组数据揭示了这种"过度工程化"的代价：

| Agent | 规模 | SWE-Bench得分 | 单次成本 | 
|-------|------|--------------|---------|
| SWE-Agent | 4,161行代码 | 67% | ~$2.50 |
| **Mini SWE-Agent** | **131行代码** | **65%** | **~$0.37** |

131行 vs 4,161行，**30倍**的代码量差距，换来2%的性能差距。成本差距约**7倍**。

同样的规律在科学Agent领域重复：

| Agent | 规模 | ASTA得分 | 单次成本 |
|-------|------|---------|---------|
| ASTA-v0（专用） | >13,768行代码 | 53% | $3.40 |
| ReAct（通用基线） | 358行代码 | 44% | $0.31 |

358行代码的ReAct在科学推理任务上达到专用系统72%的性能，成本是**1/11**。

> **工程判断**：这两个案例揭示的不是"通用Agent必然更好"，而是"专用Agent的设计空间被严重过度工程化"。当代码行数成为Agent能力的代理变量，说明组件复用和抽象做得不够——这恰好是框架层应该解决的问题。

---

## 二、Agent评测的五层架构

当前Agent评测方案散落在不同的抽象层次上，缺乏统一的参照框架。ICLR的文章提出了一个五层 Taxonomy，用于描述Agent评测从最具体到最通用的演进路径：

### Level 1：Agentic Skills Evaluation（技能评测）

**特征**：无动态环境，评测模型在文本Prompt上的响应。

这类评测提供一段文字Prompt，要求模型输出文字答案，独立于任何交互循环或自适应环境。评测的是模型**是否具备**某种Agent能力的潜力，而非**能否可靠地**在真实长程任务中部署该能力。

典型代表：
- **GSM8K**：数学推理
- **HotPotQA**：多跳问答  
- **BFCL**：工具调用能力

**局限**：技能存在 ≠ 技能可在长程任务中可靠使用。

### Level 2：Domain-Agent Evaluation（领域Agent评测）

**特征**：引入交互环境（Web浏览器、终端、应用），Agent通过多步交互完成任务，用环境特定指标评估轨迹。

这类评测提供了真实的多步任务，需要Agent在环境内执行操作序列（Agent Trajectory），再用环境定义的指标判断任务是否完成。

典型代表：
- **Tau-Bench**：客服场景
- **AppWorld**：多应用任务
- **WebArena**：浏览器交互
- **TerminalBench**：Linux命令行任务
- **SWE-Bench**：GitHub Issue修复

**局限**：每个基准各自定义自己的环境设置和Agent接口，导致同一Agent难以跨基准比较。

### Level 3：Agentic Cross-Model Evaluation（跨模型评测）

**特征**：提供统一的评测Harness，实现跨基准的可复现Agent评测。

这一层引入了标准化的评测脚手架，使得同一Agent架构可以更换不同的LLM后端（如GPT-5、Claude Sonnet 4.6、Gemini 2.5），也可以在同一基准上比较不同的Agent架构。

典型代表：
- **HAL**：整合了9个Level 2基准，每个环境有固定Agent设置，用户可以切换骨干模型或添加新的领域Agent。

**局限**：标准化仍然建立在"固定Agent设置"基础上，不支持同一Agent跨环境运行——而这恰恰是General Agent的核心特征。

### Level 4：Protocol-Centric Agent Evaluation（协议中心评测）

**特征**：定义标准化的交互协议（如统一浏览器API或终端接口），任何Agent都必须通过该协议与环境通信。

这打破了"每个环境定义自己的Agent接口"的碎片化，使Agent可以用不同架构但通过同一协议接受评测，从而真正比较不同Agent架构的优劣。

典型代表：
- **BrowserGym**：标准化浏览器交互
- **Harbor**：统一终端协议

**核心矛盾**：协议标准化带来了可比性，却牺牲了灵活性。Harbor通过命令行协议评估Agent，导致基于MCP的Agent（如Claude Code）必须被强制适配到命令行协议才能接受评测——这扭曲了Agent的原生设计，评测结果也因此失真。

> **工程判断**：Level 4的问题揭示了协议层面的根本张力——"用统一协议评测"和"Agent的原生设计"之间的适配成本可能比评测精度更重要。Level 4对专用领域有意义，但对通用Agent（其核心价值恰好在于灵活性）反而可能是一种约束。

### Level 5：General Agent Evaluation（通用Agent评测）—— 缺失的层级

**定义**：一个可以跨环境评估同一Agent的框架，无需强制使用特定通信协议。

Level 5需要解决的是：如何评测一个Agent的"通用性"本身——即它能否在不同类型的环境中迁移并保持性能。

关键维度：
- **环境适应性**：同一Agent在新环境中是否仍能有效运作
- **协议无关的原生性能**：Agent在自己设计的交互模式下表现如何
- **跨任务迁移能力**：在任务A上学到的组件能否迁移到任务B

**目前不存在**符合Level 5定义的评测方案。

---

## 三、三大缺口：为什么Level 5缺失

Level 5的缺失并非因为缺乏关注，而是三个相互关联的技术缺口尚未解决：

### 缺口一：缺乏标准化的Agent接口

当前的Agent接口没有统一规范。每个Agent框架（LangChain、AutoGen、CrewAI、Semantic Kernel）都定义了自己的Agent描述方式。当一个评测框架需要"加载任意Agent并评估其性能"时，首先要解决的是"如何用统一的方式调用任意Agent"。

MCP解决的是Agent与工具之间的接口标准化问题，但Agent自身的接口（即"如何向一个Agent发送任务描述并获取执行轨迹"）尚未有统一方案。

### 缺口二：缺乏标准化的环境接口

Level 2和Level 4的评测基准都依赖各自的环境定义：WebArena有自己的Web服务器和操作接口，TerminalBench有自己的Shell模拟器，SWE-Bench有专门的代码执行容器。这些环境之间的差异不仅是接口不同，还包括任务语义、操作语义和成功标准的根本不同。

从工程角度，这意味着跨环境评测的代价极高——每次引入新环境都需要重新定义评测任务和成功指标。

### 缺口三：缺乏标准化的研究者接口

即便解决了上述两个问题，研究者需要一个统一的"评测配置语言"来描述"我要评测什么Agent、在什么环境、用什么指标"。目前没有这样的规范，导致每次做Agent评测都是重新发明轮子。

---

## 四、Meta-Protocol：一个可能的解决方向

ICLR的文章提出了一个Meta-Protocol概念，作为Level 5的可能路径。核心思路不是再定义一个新的协议，而是定义一个**描述现有协议如何相互映射的元层**：

```
Agent → [原生协议] → 环境
         ↓
    Meta-Protocol层（协议适配）
         ↓
Agent → [目标协议] → 任意环境
```

这个元层不替代具体的Agent-环境交互协议（如MCP），而是提供协议之间的翻译能力。例如，当一个基于MCP的Agent需要被评测在TerminalBench的Shell环境中运行时，Meta-Protocol层负责将MCP的工具调用语义映射到Shell命令。

**工程可行性评估**：
- **优点**：不需要重新发明Agent接口标准，利用现有协议（MCP、A2A）的生态积累
- **挑战**：语义映射的一致性无法保证——MCP的工具调用语义（"搜索数据库"）和Shell命令语义（`grep -r`）之间的映射存在大量边界情况
- **当前状态**：纯研究概念，尚无原型实现

> **工程判断**：Meta-Protocol的方向值得关注，但短期内更实际的做法是Level 4的深化——为MCP等主流协议建立官方的跨环境适配层，而非试图从零建立元层。Microsoft Agent Framework 1.0同时支持MCP和A2A的双协议架构，可能成为这个方向的一个推动力量。

---

## 五、对Agent工程师的实践意义

五层架构对工程实践的直接意义：

### 1. 评测方案选型

| 你的场景 | 推荐评测层级 | 说明 |
|---------|------------|------|
| 评估新LLM的Agent潜力 | Level 1 | GSM8K/BFCL等足够，不需要完整环境 |
| 评测具体领域的Agent效果 | Level 2 | WebArena/SWE-Bench等，需要真实环境 |
| 对比不同LLM作为Agent后端 | Level 3 | HAL等统一Harness |
| 评测Agent架构的跨环境能力 | Level 4（当前）| 受协议约束，选择支持MCP的方案 |
| 评测Agent的真正通用性 | Level 5（缺失）| 目前无法做到 |

### 2. 架构决策参考

数据表明：**专用Agent的工程复杂度往往不能线性转化为性能提升**。当你设计一个新Agent系统时，应该优先考虑：
- 能否用更少的代码行数实现同等能力
- Agent的核心组件是否设计为可复用的通用模块
- 是否需要从Level 4的协议约束中保留足够的灵活性

### 3. 警惕评测的代理变量陷阱

SWE-Bench 67% → 65% = 2%的差距，在工程实践中往往不是关键差异。更值得关注的问题是：
- 这2%的差距在哪些具体任务类型上出现？
- 如果去掉特定的错误处理代码，性能下降多少？
- Agent的可维护性和可调试性，与评测分数的权衡如何量化？

---

## 参考文献

[^1]: Richard Sutton, "The Bitter Lesson", 2019. [http://www.incompleteideas.net/IncIdeas/BitterLesson.html](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) — 70年AI研究的核心教训：通用方法利用算力最终超越专用方案

[^2]: GitHub: bgauryy/open-docs (2026). 汇总了Claude Code、Codex-cli、OpenAI Deep Research、Perplexity等Agent的共同组件模式

[^3]: ICLR Blogposts 2026, "Ready For General Agents? Let's Test It." [https://iclr-blogposts.github.io/2026/blog/2026/general-agent-evaluation/](https://iclr-blogposts.github.io/2026/blog/2026/general-agent-evaluation/) — 五层Agent评测Taxonomy；ReAct vs ASTA-v0和Mini SWE-Agent vs SWE-Agent的Cost/LOC量化对比

[^4]: SWE-agent GitHub: [https://github.com/SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) — SWE-Agent 4,161 LOC，Claude 4 Sonnet，67% SWE-Bench

[^5]: Mini SWE-Agent GitHub: [https://github.com/SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) — 131 LOC，65% SWE-Bench，7x cheaper than SWE-Agent
