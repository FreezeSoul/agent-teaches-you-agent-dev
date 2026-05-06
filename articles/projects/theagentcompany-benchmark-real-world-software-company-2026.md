# TheAgentCompany：真实软件公司场景中的 Agent 能力基准测试

> **推荐理由**：TheAgentCompany 构建了一个包含 175 个真实工作场景的基准测试环境，覆盖 GitLab、Plane、ownCloud、RocketChat 等真实企业工具——Agent 不是在玩具任务上测试，而是在「模拟软件公司」中完成真实工作。这与 Trend 4「Agent 学会在不确定性中主动寻求帮助」形成了完美的测试闭环：基准测试本身就包含了「Agent 何时该问、何时该做」的判断场景。

---

## TRIP 四要素

**T - Target**：构建 Agent 系统的工程师和研究团队，需要量化评估 Agent 在真实企业工作流中的表现，尤其是跨系统协作、长期任务和多步骤决策场景。

**R - Result**：在 Docker 容器中快速部署完整的模拟软件公司环境（GitLab + Plane + ownCloud + RocketChat），然后在 175 个真实工作场景上评估 Agent 表现。零运维成本即可获得量化基准数据。

**I - Insight**：TheAgentCompany 的核心洞察是：**Agent 能力不能只看单任务准确率，必须看跨系统协作和长期上下文维持能力**。真实工作不是「解一道题」，而是「完成一个涉及多个工具和人员的工作流」。

**P - Proof**：GitHub 697 Stars、114 Forks，ICLR 2025/2026 相关论文发表，DeepMind、Google Brain、MIT、Stanford 等机构引用，官方 Leaderboard 追踪主流模型表现。

---

## P-SET 骨架

### P - Positioning

**一句话定义**：在模拟真实软件公司中测试 AI Agent 完成真实工作任务能力的基准测试框架。

**场景锚定**：当你需要回答「这个 Agent 系统在真实企业环境中能做什么？」这个问题时，TheAgentCompany 是目前最接近真实场景的评估方案。

**差异化标签**：真实企业工具链（GitLab/Plane/RocketChat）而非模拟环境，175 个任务覆盖软件公司完整工作流。

---

### S - Sensation

想象这个评估场景：你启动了一个 Docker 环境，里面运行着一家完整的小型软件公司——GitLab 托管着代码仓库、Plane 管理着任务看板、RocketChat 是团队沟通工具、ownCloud 存储着文档和文件。

然后你给 Agent 一个任务指令，比如：

> "在 GitLab 上找到标记为 'bug' 的未完成任务，为每个任务创建一个代码分支，修复相关问题，然后向 code review 负责人发送 RocketChat 消息汇报进度。"

这个任务需要 Agent 自主完成：
1. 跨系统导航（GitLab → Plane → RocketChat）
2. 多步骤执行（搜索 → 创建分支 → 写代码 → 提交 → 发消息）
3. 状态追踪（维护上下文直到所有步骤完成）
4. 错误处理（某个步骤失败后的恢复策略）

这不是单任务测试，这是**工作流完整性测试**。

---

### E - Evidence

**技术架构**：整个环境通过 Docker Compose 在几分钟内启动，每个任务打包为独立 Docker 镜像，包含初始化脚本、评估脚本和预置数据。评估通过 `eval.py` 自动运行，支持 OpenHands 等主流 Agent 框架。

**任务分类**：175 个任务覆盖软件公司多个职能维度：
- **代码任务**：分支管理、代码审查、CI/CD 配置
- **项目管理**：任务创建、状态流转、进度汇报
- **文档协作**：文件上传下载、版本管理、内容编辑
- **沟通协作**：发送消息、@提及、讨论线程

**基准表现**：官方 Leaderboard 显示，当前前沿模型在 TheAgentCompany 上的表现仍有显著提升空间——大多数模型在需要多步骤协作的任务上成功率低于 50%。这说明**真实工作流的复杂度远超单任务基准测试所能揭示的**。

**竞品对比**：

| 基准 | 优势 | 局限 |
|------|------|------|
| **SWE-bench** | 代码修复任务真实，评测客观 | 只测单任务修复，不涉及协作和沟通 |
| **HumanEval** | 评测简单快速 | 不涉及多工具协作 |
| **TheAgentCompany** | 跨系统真实工作流，多角色协作 | 部署复杂度高，评测耗时 |

> "We interact with computers on an everyday basis... many aspects of work can be done entirely with access to a computer and the Internet. But how performant are AI agents at helping to accelerate or even autonomously perform work-related tasks?"
> — [TheAgentCompany README](https://github.com/TheAgentCompany/TheAgentCompany)

---

### T - Threshold

**快速上手**（约 15 分钟）：

```bash
# 1. 安装 Docker 和 Docker Compose（需要 30+ GB 磁盘空间）
# 2. 下载并启动模拟公司环境
sudo chmod 666 /var/run/docker.sock
curl -fsSL https://github.com/TheAgentCompany/the-agent-company-backup-data/releases/download/setup-script-20241208/setup.sh | sh

# 3. 启动 Agent 评估（以 OpenHands 为例）
sudo su
cd evaluation
bash run_eval.sh \
  --agent-llm-config <group1> \
  --env-llm-config <group2> \
  --outputs-path <outputs> \
  --server-hostname <hostname>
```

**适合贡献的场景**：
- 添加新任务到基准测试套件
- 改进评估脚本的判断准确性
- 针对特定 Agent 框架（Claude Code、CrewAI）的集成适配

**持续关注理由**：随着 Agent 系统能力提升，TheAgentCompany 的任务完成率将成为衡量「Agent 是否达到生产级可靠性」的关键指标。
