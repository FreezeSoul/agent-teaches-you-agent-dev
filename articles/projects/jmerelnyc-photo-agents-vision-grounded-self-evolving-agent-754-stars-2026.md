# jmerelnyc/Photo-agents：视觉优先的分层记忆自进化 Agent 运行时

> **TRIP 四要素**：
> - **T**：有 Python 经验的 Agent 开发者，想让 Agent 真正「看得见」屏幕并自主操作计算机；或需要构建多端 Agent（桌面/Web/聊天平台）的团队
> - **R**：754 Stars（2026-05-04 创建，5 天破 754），Python 包，开箱即用，支持 Streamlit Web / PyQt 桌面 / Telegram / Feishu / QQ / WeCom / DingTalk 多端，视觉 grounding + 自写 Skill 双重自进化
> - **I**：perceive → reason → act 三阶段 loop；多层记忆（working/global/SOP/session archive）；Chrome DevTools Protocol 视觉 grounding；自写 Skill 自进化；多 Provider LLM Router（Anthropic/OpenAI 原生）
> - **P**：754 Stars，MIT 许可，官网 photo-agents.com，GitHub + X 双更新通道，2026-05-04 创建仍处 beta

<!--more-->

## 1. 定位破题

Photo-agents 是一个**自进化的视觉 Agent 运行时**。它解决的核心问题是：文本-only Agent（将聊天记录 dump 给模型）无法真正「看见」用户界面，导致操作失误率高、上下文膨胀。

**一句话定义**：让 Agent 能像人一样「看屏幕 → 理解 → 操作」的计算级 Agent 运行时，通过分层记忆和自写 Skill 实现真正的自主进化。

**场景锚定**：当你需要 Agent 操作桌面应用、浏览器、或任何需要视觉上下文的场景时，Photo-agents 提供了一套完整的从感知到执行的 Agent 循环。

> 官方原文：
> "Photo Agents is building the next generation of LLM-driven agents that ground in what they actually see on screen. Instead of dumping longer chat transcripts into a model and hoping for the best we treat memory the way biology does."
> — [jmerelnyc/Photo-agents README](https://github.com/jmerelnyc/Photo-agents)

## 2. 体验式介绍

### 2.1 视觉 grounding：你看到什么，Agent 才能操作什么

传统 Agent 基于文件系统路径操作 UI（截图→坐标→点击），问题是：跨分辨率、动态 UI、相对布局都会导致坐标失效。

Photo-agents 的做法是**视觉优先**：通过 Chrome DevTools Protocol 直接读取 DOM 状态和屏幕截图，将「看见什么」作为 Agent 决策的核心输入，而非将文件名和路径作为决策依据。

### 2.2 分层记忆：像人脑一样组织信息

Photo-agents 的记忆系统不是简单的 conversation buffer，而是按生物学原理组织的分层结构：

| 层级 | 类型 | 说明 |
|------|------|------|
| L0 | Working Memory | 当前 session 内的即时上下文 |
| L1 | Global Memory | 跨 session 的长期事实（L2 facts） |
| L2 | SOP Memory | 标准化操作程序（Agent 自己写的 Skills） |
| L3 | Session Archive | 完整 session 历史，用于回顾和学习 |

> 官方原文：
> "Vision in. Bound observations stored in layers. Skills written by the agent itself from real success."
> — [jmerelnyc/Photo-agents README](https://github.com/jmerelnyc/Photo-agents)

### 2.3 自写 Skills：成功经验转化为可复用能力

最有意思的设计是 **L3 → L2 的自进化闭环**：Agent 每次成功解决一个问题，它会把成功的操作流程写成 SOP（Skills），存入 SOP Memory，下次遇到类似场景时直接复用，而非每次都从头探索。

这与 Cursor Composer Autoinstall 的「用上一代模型配置环境」逻辑形成有趣的互补：**Autoinstall 用旧版本模型做环境初始化，Photo-agents 用当前 session 的成功经验写 Skills**。两条路径都在解决同一个问题：如何让 Agent 的能力随时间积累而非每次从零开始。

### 2.4 开箱即用的多端 Agent

Photo-agents 不只是一个人机交互工具，它提供了一套完整的多端 Agent 部署方案：

```bash
# Streamlit Web App（开箱即用）
pythonw -m photoagents.cli.launcher

# PyQt 桌面应用
python -m photoagents.clients.desktop_app

# 桌面伴侣
pythonw -m photoagents.clients.companion_v2

# Telegram Bot
python -m photoagents.clients.telegram_client

# 飞书/企业微信/钉钉/QQ
python -m photoagents.clients.feishu_client
python -m photoagents.clients.wecom_client
python -m photoagents.clients.dingtalk_client
python -m photoagents.clients.qq_client
```

## 3. 技术深度

### 3.1 核心架构：perceive → reason → act

```
输入（屏幕截图 + DOM）→ perceive（视觉解析）→ reason（LLM 推理）→ act（工具调用）
```

关键在于 perceive 阶段不只是「看图」，而是通过 Chrome DevTools Protocol 获取结构化的 DOM 信息，将视觉感知和页面结构信息融合后输入给 LLM。

### 3.2 多 Provider LLM Router

Photo-agents 内置了多 Provider LLM Router，支持：

- **原生支持**：Anthropic Claude、OpenAI GPT
- **Failover 模式**：配置多个 provider，primary 失败时自动切换

这使得 Photo-agents 可以作为低成本方案（DeepSeek 等）结合高性能模型（Claude Opus）的灵活路由层。

### 3.3 API Key Gate

运行时需要 Photo Agents License Key，通过 `https://photo-agents.com/v1/keys/validate` 远程验证。验证结果缓存 24 小时，兼顾安全和性能。

## 4. 竞品对比

| 项目 | 视觉 grounding | 分层记忆 | 自写 Skill | 多端支持 | Stars |
|------|---------------|---------|-----------|---------|-------|
| Photo-agents | ✅ CDP | ✅ 4层 | ✅ | ✅ 8端 | 754 |
| OpenAI Operator | ✅（浏览器）| ❌ | ❌ | ❌ | — |
| Anthropic Computer Use | ✅ | ❌ | ❌ | ❌ | — |
| Browser-use | ✅ | 部分 | ❌ | 部分 | — |

Photo-agents 的差异化在于**三层能力的同时具备**：视觉 grounding + 分层记忆 + 自写 Skill，这三者的结合在开源社区中是独特的。

## 5. 行动引导

### 快速上手

```bash
# 安装
pip install photoagents

# 获取 API Key（免费）
# 访问 https://photo-agents.com/dashboard/keys

# 配置凭证
cp photoagents/config/keys_template.py credentials.py
# 编辑 credentials.py，取消注释一个 Provider 配置

# 交互 REPL
python -m photoagents

# 单次任务模式
python -m photoagents --task my_task --input "List the largest files in this directory."
```

### 适合贡献的场景

- **Skill 生态扩展**：当前 Skills 目录（`photoagents/skills/`）是开放的，欢迎贡献新领域（浏览器自动化、IDE 集成等）的 SOP
- **多端适配**：国内平台（飞书/钉钉/企业微信）的深度集成
- **记忆系统改进**：向量索引检索、SOP 的版本化管理

## 6. 与 Cursor Autoinstall 的关联

本文分析的 [Cursor Bootstrapping Composer Autoinstall](./cursor-bootstrapping-composer-autoinstall-self-bootstrapping-rl-environment-initialization-2026.md)（`articles/practices/`）与 Photo-agents 共享同一个核心洞察：**Agent 的能力需要自我积累而非每次从零开始**。

Autoinstall 的解法是「用旧版本模型初始化新版本的训练环境」，Photo-agents 的解法是「用当前 session 的成功经验写 Skills」。两条路径分别从**训练基础设施**和**运行时能力积累**两个层面解决了同一个问题。

> 官方原文：
> "Skills written by the agent itself from real success."
> — [jmerelnyc/Photo-agents README](https://github.com/jmerelnyc/Photo-agents)

对于 Agent 开发者而言，这意味着：你不需要在每次设计新 Agent 时都从零构建能力层——通过 Bootstrapping（训练期）和 Self-Writing Skills（运行时）两条路径，Agent 的能力可以真正实现时间维度的积累。