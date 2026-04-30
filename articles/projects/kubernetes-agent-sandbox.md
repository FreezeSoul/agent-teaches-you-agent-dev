# Kubernetes SIG Apps Agent Sandbox：Kubernetes 原生的 Agent 沙箱 CRD

## 项目概述

**kubernetes-sigs/agent-sandbox** 是 Kubernetes SIG Apps 下的一个项目，它在 Kubernetes 上定义了一个 `Sandbox` CRD（Custom Resource Definition）和控制器，为管理「隔离的、有状态的、单例的工作负载」提供声明式、标准化的 API——这正是 AI Agent 运行时（执行不受信任的 LLM 生成代码）所需要的抽象。

当前 Stars：1,982。

## 解决的问题

Kubernetes 的 Deployment 和 StatefulSet 已经能很好地处理无状态副本应用，但 AI Agent 运行时有几个独特需求：

1. **强隔离**：需要 gVisor 或 Kata Containers 等增强隔离，防止 LLM 生成的恶意代码影响宿主机
2. **持久化状态**：Agent 运行时的状态需要跨重启持久存在
3. **稳定的网络标识**：每个沙箱需要有稳定的主机名和 IP
4. **生命周期管理**：支持休眠、恢复、自动清理

kubernetes-sigs/agent-sandbox 的核心价值就是提供**这四个需求的 Kubernetes 原生解决方案**。

## 核心 CRD

### Sandbox（核心）

声明式管理单个有状态 Pod，具有：
- Stable Identity（稳定主机名）
- Persistent Storage（持久存储）
- Lifecycle Management（创建、定时删除、暂停/恢复）

### Extensions

- **SandboxTemplate**：可复用模板，批量创建同类沙箱
- **SandboxClaim**：从模板实例化沙箱
- **SandboxWarmPool**：预热池管理，快速分配已就绪的沙箱

## 架构特点

遵循 Kubernetes Controller 模式：用户创建 Sandbox 资源，控制器管理底层运行时资源。安装简单，两条 `kubectl apply` 命令即可部署核心组件或扩展组件。

提供了 Python SDK 用于编程方式管理沙箱。

## 局限

- 面向 Kubernetes 直接用户，对于希望「开箱即用」的企业场景，可能需要额外的部署和维护成本
- Stars 较低（不到 2K），社区活跃度需要观察
- AI Agent 运行时支持需要配合具体的 Runtime（如 gVisor）才能实现强隔离

## 一句话推荐

如果你在 Kubernetes 上运行 AI Agent，需要一个标准化的沙箱抽象来管理有状态隔离工作负载，这是目前最符合 Kubernetes 生态的方案——但上手需要一定 K8s 背景。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/kubernetes-sigs/agent-sandbox`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：8.5/15
