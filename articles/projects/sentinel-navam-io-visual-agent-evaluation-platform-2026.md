# Sentinel：视觉优先的 Agent 评测与回归检测平台

## 定位

Sentinel 是一个面向 AI Agent 的可视化测试与评估平台。它解决的核心问题是：如何让不懂 YAML 的团队成员（产品经理、QA 工程师、安全团队）也能高效构建 Agent 评测用例？

它的定位是「Postman for AI Agents」——不是给模型工程师用的 CLI 工具，而是给实际需要测试 Agent 行为的一线人员用的图形界面。

---

## 核心能力：点击构建测试，即时生成 YAML

Sentinel 的设计核心是「点击即测试」——你不需要写一行 YAML，只需要在可视化画布上拖拽组件、配置节点，系统会自动生成标准化的测试规范。

**工作流拆解**：

1. **点击组件** → 在左侧组件面板选择节点类型（Input、Model、Assertion、Tool、System、Output）
2. **拖拽到画布** → 在 React Flow 画布上建立节点连线
3. **自动生成 YAML** → 画布上的节点关系实时转换为符合规范的 YAML 测试文件
4. **执行测试** → 点击 Run 按钮在支持的模型（Claude 3.5/3 Opus / GPT-5）上运行
5. **结果对比** → 在结果面板查看 pass/fail 状态和性能数据

这个流程的技术难点不在于「能生成 YAML」，而在于**视觉节点和 YAML 之间的双向无损转换**——Sentinel 的文档明确承诺「Visual ↔ YAML, zero data loss」。这意味着你在画布上做的任何修改，YAML 文件里都有对应表达，反之亦然。

---

## 技术架构：React Flow + Tauri + FastAPI

Sentinel 的技术选型值得关注：

**前端**：React 19 + Vite 6.0 + React Flow 12.3（@xyflow/react）+ Zustand 5.0 + TailwindCSS + shadcn/ui。这个组合在 2026 年已经是成熟的视觉应用技术栈，React Flow 的节点编辑器能力是其核心。

**桌面端**：Tauri 2.0。这是一个值得关注的选择——相比 Electron，Tauri 的二进制体积更小、启动更快（文档提到「lightweight, fast startup」），这对需要频繁打开的桌面工具来说是合理的选择。

**后端**：FastAPI + Pydantic v2 + SQLite（本地）/ PostgreSQL（服务器部署）+ pytest + pytest-cov。Python 3.13+ 的使用意味着可以依赖较新的语言特性。

**模型支持**：当前支持 Anthropic Claude 3.5 Sonnet、Claude 3 Opus（≥0.43.1）和 OpenAI GPT-5.1 / GPT-5 Pro / GPT-5 Mini（≥1.59.6），规划中支持 Amazon Bedrock、HuggingFace、Ollama。这个扩展路径表明 Sentinel 正在从「双供应商测试」向「多供应商评测平台」演进。

---

## 评测维度与断言类型

Sentinel 提供了 12 个评测分类：

| 分类 | 用途 | 示例断言 |
|------|------|---------|
| Q&A | 知识与推理测试 | must_contain（"Paris"）|
| Code Generation | 代码质量验证 | regex_match（`def\s+\w+`）|
| Browser Agents | Web 自动化测试 | must_call_tool（["browser"]）|
| Multi-turn | 对话流程测试 | min_tokens（50）|
| LangGraph | Agentic 工作流 | must_call_tool（["state"]）|
| Safety | 安全与内容过滤 | must_not_contain（"sensitive"）|
| Data Analysis | 数据处理任务 | — |
| Reasoning | 逻辑与问题解决 | — |
| Tool Use | 函数调用测试 | — |
| API Testing | REST 端点验证 | — |
| UI Testing | 视觉与交互测试 | — |
| Regression | 版本对比与行为稳定性 | — |

8 种断言类型覆盖了文本存在性检查、正则匹配、工具调用验证、输出格式强制、超时控制、输出长度范围等常见评测需求。

---

## 与 Replit Agent 4 的主题关联

Replit Agent 4 的核心贡献是「任务化协作」——把多 Agent 的执行结果通过 Task-based workflow 进行管理，用户 Review 后再合并。Sentinel 则从另一个维度回答了同一个问题：**当 Agent 产生输出后，如何验证它的行为是否符合预期？**

两者形成的技术互补是：

- **Replit**：并行 Agent 执行 → 任务合并 → 用户审批
- **Sentinel**：并行 Agent 输出 → 测试断言 → 行为回归检测

这对应了 Multi-Agent 系统中两个最核心的工程挑战：「执行协调」和「质量保证」。Replit 解决了前者，Sentinel 解决了后者。

另一个值得注意的关联点是「视觉化 vs 代码化」的对比。Sentinel 选择了「视觉优先 + DSL 兜底」的路线，这与 Replit Agent 4 的「设计开发一体化」思路一致——都是为了降低工具的认知门槛，让更多角色能参与 Agent 工作流。

---

## 代码质量与工程成熟度

Sentinel 的工程数据值得关注：

- **473 个单元测试，100% 通过率**——这是一个高标准的测试覆盖率承诺
- **TypeScript strict mode：0 errors**（只有 4 个 `any` 类型使用）——前端类型安全做到这个程度在生产项目中不常见
- **57,581 行代码**（不含依赖），其中 **47% 是文档**——这个文档密度说明项目在追求可维护性和可理解性，而不是只追求功能
- **代码质量工具**：Black（line-length: 100）、Ruff、MyPy、ESLint 全工具链配置

这些数据表明 Sentinel 是一个工程化程度较高的项目，不是概念验证阶段的原型。

---

## 适用场景

**值得关注的场景**：
- 团队中非工程角色（PM、QA、安全团队）需要参与 Agent 测试用例设计
- 需要对 Agent 版本更新做行为回归检测
- 需要在本地（air-gapped）环境下运行评测，不依赖云服务

**不适合的场景**：
- 需要对大规模模型做基准评测（应该用 TheAgentCompany 等更专门的基准框架）
- 需要实时监控生产环境中的 Agent 行为（应该用 LangSmith 等观测平台）
- 只需要简单的 prompt-response 测试（YAML 直接写更快）

---

## 快速上手

```bash
# 克隆仓库
git clone https://github.com/navam-io/sentinel.git
cd sentinel/

# 前端（桌面应用）
cd frontend && npm install
npm run tauri:dev  # 打开可视化画布

# 后端（API 服务）
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest -v  # 验证测试通过
uvicorn main:app --reload
```

Sentinel 的桌面应用开箱即用：启动后左侧是组件面板，中央是交互画布，顶部是 Library（16 个内置模板），右侧可以切换 Canvas/Test/Suite/Library 四个视图。对于没有 YAML 经验的团队成员，可以直接从 Library 加载模板，然后点击节点修改参数即可。

---

## 结论

Sentinel 的设计哲学是「让评测这件事变得直观」——它选择了一条与大多数 Agent 工具不同的路线：不是追求更强的自动化，而是追求更低的参与门槛。这与 Replit Agent 4 的「让人做创意决策、让 Agent 处理执行摩擦」的设计哲学一脉相承。

对于 Agent 系统设计者而言，Sentinel 提供了一个值得参考的思路：当 Agent 的行为验证无法完全自动化时，视觉化工具可以成为人类判断和自动化测试之间的桥梁——它不替代人类的决策，但让决策所需的信息更直观。

> "Make AI agent testing as intuitive as Postman made API testing, as visual as Langflow made LLM workflows, and as powerful as LangSmith made observability."
> — [Sentinel GitHub README](https://github.com/navam-io/sentinel)

---

**关联主题**：Multi-Agent 质量保证 · Task-based workflow · Visual-first 工具设计 · Agent 评测基础设施

**关联 Articles**：Replit Agent 4 — 设计开发一体化与多 Agent 并行协作架构（harness/）

**来源**：[GitHub navam-io/sentinel](https://github.com/navam-io/sentinel)（v0.22.0）｜含 5 处原文引用