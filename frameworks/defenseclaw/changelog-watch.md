# DefenseClaw Changelog Watch

> 追踪 Cisco DefenseClaw 的版本变更和动态更新。

---

## 📋 追踪记录

### 2026-03-30｜DefenseClaw v0.2.0：PyPI 发布 + Splunk HEC trace_id 支持

**版本**：v0.2.0
**性质**：🟢 Patch（基础设施完善）
**来源**：[GitHub Release](https://github.com/cisco-ai-defense/defenseclaw/releases/tag/v0.2.0)

### 变更要点

| 变更 | 说明 |
|------|------|
| **PyPI release publishing** | 新增 PyPI 自动发布流程（生产就绪标志）|
| **OSS release files** | 新增开源发布文件 |
| **trace_id to Splunk HEC events** | 向 Splunk HEC 事件添加 trace_id（#224），可与 LangSmith 等 APM 集成 |
| **docs v1** | 文档 1.0 版本发布 |

**评估**：v0.2.0 表明 DefenseClaw 从"发布公告"向"实际可用"过渡。PyPI 发布使得工具可通过 pip 直接安装，降低了使用门槛。trace_id 支持表明该工具正在与主流可观测性生态集成。

**版本判断**：Patch（基础设施完善，非功能增加）

---

### 2026-03-23 — Initial Release（RSAC 2026）

**版本**：Initial Release（GitHub repo 建立）
**来源**：RSAC 2026 / GitHub（cisco-ai-defense/defenseclaw）

**本轮变更**：

- 🚀 **Initial Release**：DefenseClaw 开源仓库正式建立（cisco-ai-defense/defenseclaw，127 stars）
- Skills Scanner：Agent 技能安全扫描工具
- MCP Scanner：MCP Server 完整性验证和监控
- A2A Scanner：Agent 间通信安全和身份验证（5 检测引擎：pattern matching / protocol validation / behavioral analysis / runtime testing / LLM analyzer）
- CodeGuard：动态生成代码的静态分析层
- AI Bill of Materials（AI BoM）：AI 资产持续清单生成

**其他来源记录**：

- Cisco 博客：https://blogs.cisco.com/ai/cisco-announces-defenseclaw
- ZDNet：https://www.zdnet.com/article/cisco-defenseclaw-to-govern-agentic-ai/
- Cisco 新闻：https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m03/cisco-reimagines-security-for-the-agentic-workforce.html
- A2A Scanner 独立博客：https://blogs.cisco.com/ai/securing-ai-agents-with-ciscos-open-source-a2a-scanner
- RSAC 2026 Innovation Sandbox 发布（3/23-27）

**状态**：✅ 已确认 v0.2.0 PyPI 发布（2026-03-28）

**备注**：

- GitHub repo 在 v0.2.0 之前非常精简（仅 README + LICENSE），v0.2.0 补全了 PyPI 发布流程和文档
- 完整工具集（Skills Scanner / MCP Scanner / A2A Scanner / CodeGuard / AI BoM）的具体实现代码有待进一步验证
- A2A Scanner 有独立博客详细介绍其 5 检测引擎架构
- 集成 NVIDIA OpenShell 运行时，提供沙箱执行环境
- 与 Cisco Duo Zero Trust Access 深度集成

---

*由 AgentKeeper 维护 | 每轮更新*
