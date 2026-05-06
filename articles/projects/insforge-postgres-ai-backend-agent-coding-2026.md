# InsForge：AI Coding Agent 的 Backend-as-a-Service 基础设施

## 目标用户

**T- Target**：有 AI Coding Agent 实践经验的开发者，正在构建涉及后端（数据库、认证、存储、API Gateway）的完整应用，发现 Agent 在后端代码生成时会遇到「上下文断裂」或「后端基建能力不足」的问题。

**R- Result**：原本需要 1-2 周的后端搭建工作（Postgres + Auth + Storage + API Gateway），现在 Agent 可以独立完成，人类只需要在最后验收——InsForge 通过语义层让 Agent 理解「数据库 schema 的含义」「认证流程的目的」「文件存储的业务逻辑」，而不是只生成 SQL 或 API 代码。

**I- Insight**：InsForge 的核心创新不是「又一个大模型 API 封装」，而是**Backend Context Engineering**——将 Postgres、Auth、Storage 等后端基础设施的「业务语义」暴露给 Agent，让 Agent 能「理解后端在做什么」，而不是机械地生成代码。这与 Anthropic 的「Context Engineering for AI Agents」方法论一脉相承。

**P- Proof**：
- GitHub 8.3K ⭐（截至 2026-05），2026 年 4 月发布，增长迅速
- Cursor 官方集成（Cursor Dashboard 内置 InsForge MCP Server 配置引导）
- 支持 Docker Compose 一键部署，支持 Railway/Zeabur/Sealos 多平台一键部署
- 官方文档提供 MCP Server 配置指南

---

## 快速定位

**一句话定义**：InsForge 是一个为 AI Coding Agent 设计的 Backend-as-a-Service 平台，通过语义层让 Agent 能够理解、配置和操作后端基础设施。

**场景锚定**：当你用 Cursor / Claude Code / Copilot 等工具开发一个全栈应用，需要后端能力（用户系统、数据库、文件存储）时，InsForge 让 Agent 能够在「理解业务语义」的层面操作这些基础设施，而不只是生成 SQL 或 API。

**差异化标签**：**Semantic Layer for Backend**——不是又一个 BaaS API 封装，而是给 Agent 提供「理解后端在做什么」的能力。

---

## 使用体验

### 传统开发模式 vs InsForge 模式

**传统模式**：
```
Human: "帮我创建一个用户注册 API，需要验证邮箱格式"
Agent:  生成一段 Python 代码...
问题：Agent 不知道你们公司的邮箱验证规则是什么，
      不知道用户表 schema，生成的代码和现有系统不兼容
```

**InsForge 模式**：
```
Human: "帮我创建一个用户注册 API，需要验证邮箱格式"
Agent: 
  1. 调用 InsForge MCP fetch-docs → 获取 InsForge Auth 模块的文档
  2. 调用 InsForge MCP configure-auth → 配置邮箱验证规则
  3. 调用 InsForge MCP inspect-backend-state → 查看现有用户表结构
  4. 生成与 InsForge 集成的 API 代码
结果：Agent 真正理解了在 InsForge 上如何做认证，
      生成的代码与 InsForge 的 Auth 模块无缝对接
```

### 核心产品能力

| 产品 | 能力 | Agent 如何使用 |
|------|------|---------------|
| **Authentication** | 用户管理、认证、Session 管理 | Agent 可以配置认证流程、创建用户、验证登录 |
| **Database** | Postgres 关系数据库 | Agent 可以创建表、配置 RLS（Row Level Security）、理解 schema 语义 |
| **Storage** | S3 兼容文件存储 | Agent 可以上传文件、管理 bucket、配置访问权限 |
| **Model Gateway** | 跨多 LLM Provider 的 OpenAI 兼容 API | Agent 可以调用统一的 LLM 接口，无需关心具体 Provider |
| **Edge Functions** | 边缘计算的无服务器代码 | Agent 可以部署轻量级 API 函数 |
| **Compute** | 长时间运行的容器服务 | Agent 可以部署需要长时运行的后端服务 |

---

## 技术拆解

### Semantic Layer 的设计思路

InsForge 语义层的核心设计是**「让 Agent 能 fetch documentation 和 available operations」**，而不是让 Agent 自己猜测：

```json
// Agent 调用 InsForge MCP 的 fetch-docs 工具
{
  "tool": "fetch-docs",
  "params": {
    "module": "auth",
    "operation": "configure-email-verification"
  }
}

// InsForge 返回结构化的文档
{
  "description": "配置邮箱验证规则",
  "required_params": ["verification_type", "allowed_domains"],
  "schema": {...},
  "example": {...}
}
```

这解决了 Agent 在后端开发时的**「上下文断裂」问题**——Agent 不再需要从你项目的代码片段中猜测「你们怎么验证邮箱」，而是可以直接查询 InsForge 平台提供的认证配置接口。

### 与 Cursor 的深度集成

InsForge 的一个亮点是与 Cursor 的官方集成：

> "Set Up with Cursor" 按钮出现在 GitHub README 的醒目位置，InsForge 官方的 [Cursor MCP 配置指南](https://docs.insforge.dev/integrations/cursor) 详细说明了如何在 Cursor 中连接 InsForge MCP Server。

这意味着 InsForge 不是「让 Agent 调用外部 API」，而是**让 InsForge 的能力直接出现在 Cursor 的 Agent 工具链里**。

### 多项目隔离能力

InsForge 支持在同一台主机上运行多个隔离的项目：

```bash
# 每个项目用不同的 .env 文件和项目名
docker compose -f docker-compose.prod.yml --env-file .env.project1 -p project1 up -d
docker compose -f docker-compose.prod.yml --env-file .env.project2 -p project2 up -d
```

每个项目有独立的 Postgres、Auth、Storage 实例。这对于**多租户场景**或**同时开发多个项目**的 Agent 工作流非常重要。

---

## 竞品对比

| 维度 | InsForge | Supabase | Firebase |传统自建 |
|------|----------|----------|----------|---------|
| **目标用户** | AI Coding Agent | 人类开发者 | 人类开发者 | 运维团队 |
| **语义层设计** | ✅ Agent 可 fetch docs 和 operations | ❌ 纯 API | ❌ 纯 API | N/A |
| **Postgres** | ✅ | ✅ | ❌ | ✅ |
| **Auth** | ✅ | ✅ | ✅ | ✅ |
| **Storage** | ✅ | ✅ | ✅ | ✅ |
| **Model Gateway** | ✅ | ❌ | ❌ | ❌ |
| **Cursor 官方集成** | ✅ | ❌ | ❌ | N/A |
| **自托管** | ✅ Docker Compose | ✅ | ❌ | ✅ |
| **开源** | ✅ Apache 2.0 | 部分开源 | ❌ | N/A |

---

## 快速上手

### 1. 启动 InsForge（Docker Compose）

```bash
git clone https://github.com/InsForge/insforge.git
cd insforge
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d
```

访问 http://localhost:7130 完成初始化。

### 2. 连接 InsForge MCP Server

在 InsForge Dashboard 中按照引导步骤，将 InsForge MCP Server 添加到你的 Cursor（或其他 Agent）配置中。

### 3. 验证安装

向 Agent 发送：
```
I'm using InsForge as my backend platform, call InsForge MCP's fetch-docs tool to learn about InsForge instructions.
```

### 4. 让 Agent 使用 InsForge 构建后端

```bash
# 创建一个用户注册功能
"帮我创建一个用户注册功能，包含邮箱验证和密码重置"
# Agent 会自动调用 InsForge 的 Auth API 完成配置
```

---

## 适合什么样的贡献

- **插件生态**：为 InsForge 开发 MCP Server 插件，封装更多后端能力
- **文档**：帮助完善 InsForge 在不同 Agent 平台（Claude Code、Copilot）上的配置指南
- **集成**：开发 InsForge 与其他工具（Vercel、Railway）的深度集成

---

## 相关资源

- [InsForge GitHub](https://github.com/InsForge/insforge)
- [InsForge 官方文档](https://docs.insforge.dev/introduction)
- [Cursor + InsForge 集成指南](https://docs.insforge.dev/integrations/cursor)
- [InsForge vs Superpowers 对比分析](https://pasqualepillitteri.it/en/news/1341/superpowers-vs-insforge-comparison-2026)（by Pasquale Pillitteri）

---

*本文 source: [InsForge GitHub README](https://github.com/InsForge/insforge) | 2026-05*
