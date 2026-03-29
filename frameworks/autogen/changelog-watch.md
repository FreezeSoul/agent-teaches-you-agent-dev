# AutoGen Changelog Watch

> 追踪 AutoGen 版本变化

---

## 2026-03-30｜AutoGen python v0.7.5：Anthropic thinking mode 支持 + 多项修复

**版本**：python-v0.7.5
**性质**：🟡 Minor（功能增强 + Bug 修复）
**来源**：[GitHub Release](https://github.com/microsoft/autogen/releases/tag/v0.7.5)

### 变更要点

| 变更 | 说明 |
|------|------|
| **Anthropic thinking mode** | 新增 `thinking mode support for anthropic client`（PR #7002）|
| **extra args not working** | 修复禁用 thinking 时 extra args 不生效的问题（#7006）|
| **Redis memory** | 支持 Redis 中的 linear memory（#6972）|
| **Bedrock streaming** | 修复 Bedrock streaming 响应处理（tool use + empty argument）（#6979）|
| **Azure AI thinking mode** | Azure AI client streaming thinking mode 修复（#7026）|
| **GraphFlow cycle detection** | 修复 GraphFlow cycle detection 中的递归状态清理问题 |
| **OllamaChatCompletionClient** | 修复 `load_component()` 错误（添加至 WELL_KNOWN_PROVIDERS）|
| **docs** | 修复 dotnet core typo（#6950）|

**评估**：多项 bug 修复和一个重要功能增强（Anthropic thinking mode）。thinking mode 支持对 Anthropic 模型用户有实际价值；GraphFlow 循环检测修复是生产级稳定性改进。

---

## 更新记录

### 2026-03

**新特性**：
- GroupChat 支持动态路由优化
- 人机协同（Human-in-the-loop）体验改善
- 微软内部更多产品采用 AutoGen

**生态**：
- 与 Azure AI Studio 深度集成
- 企业级案例增多

**版本**：
- AutoGen 0.2.x 系列
- Semantic Kernel 集成稳定

---

## 关键版本节点

| 版本 | 日期 | 关键变化 |
|------|------|---------|
| 0.7.5 | 2026-03-30 | Anthropic thinking mode 支持 + GraphFlow 修复 |
| 0.2.x | 2026-Q1 | GroupChat 路由优化 |
| 0.1.x | 2025-Q4 | 稳定版发布 |

---

## 参考来源

- [AutoGen 官方文档](https://microsoft.github.io/autogen/)
- [AutoGen GitHub](https://github.com/microsoft/autogen)

---

*由 AgentKeeper 自动追踪 | 最后更新：2026-03-30*
