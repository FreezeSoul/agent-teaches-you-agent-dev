# agent-sandbox/agent-sandbox：E2B 兼容的企业级 AI Agent 沙箱

## 项目概述

**agent-sandbox/agent-sandbox** 是一个企业级、云原生、高性能的 AI Agent 运行时环境，结合 Kubernetes 和容器隔离，允许 Agent 安全执行不受信任的 LLM 生成代码、浏览器操作、计算机控制、Shell 命令等，同时支持有状态、长生命周期、多会话和多租户场景。

与 [kubernetes-sigs/agent-sandbox](#kubernetes-agent-sandbox) 名称相近但定位不同：该项目提供的是**可直接使用的完整沙箱服务**，而 K8s SIG 的项目提供的是底层 CRD 构建块。

当前 Stars：116（项目较新）。

## 核心特点

### E2B 完全兼容

完全兼容 E2B 协议和 SDK，现有的基于 E2B 的 AI Agent 工具可以无缝迁移。

### MCP 原生支持

内置 MCP（Model Context Protocol）Server，Agent 可以通过 MCP 自动管理沙箱的完整生命周期：创建→访问→删除，无需人工干预。

### 多类型沙箱支持

- Code Sandbox（代码执行）
- Browser Sandbox（浏览器自动化）
- Computer Sandbox（计算机控制）
- Customized Sandbox（自定义）

### RESTful API

同时提供 RESTful API 和 MCP 两种接口，灵活适配不同集成需求。

### UI 管理界面

内置 Web UI，支持沙箱管理、池管理、模板管理和文件、日志、终端访问。

## 架构

基于 Kubernetes 构建，提供 Agent 到沙箱的单跳路由。Agent 创建沙箱时，系统自动处理底层容器编排和资源分配。

## 局限

- Stars 较低（116），项目成熟度和社区规模有待验证
- 文档相对简洁，完整企业级使用需要一定二次开发
- 与 kubernetes-sigs/agent-sandbox 名称易混淆，两者定位不同需要注意区分

## 一句话推荐

如果你需要 E2B 兼容的企业级沙箱环境且希望有国产开源方案，agent-sandbox/agent-sandbox 值得关注——但建议先在测试环境充分验证其稳定性和安全性。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/agent-sandbox/agent-sandbox`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：9.5/15
