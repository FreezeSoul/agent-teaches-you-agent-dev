# Alibaba Page Agent：让任何网页都能被自然语言控制

## 项目概述

**Page Agent** 是阿里巴巴开源的 in-page GUI Agent 项目，核心理念是「把一个 AI Agent 直接嵌入到你的网页中，用自然语言控制界面」。不需要浏览器扩展、不需要 Python 后端、不需要无头浏览器——所有操作都在页面内的 JavaScript 中完成。

当前 Stars：17,477。

## 核心设计

### 纯前端实现

Page Agent 以 `<script>` 标签或 npm 包的形式嵌入任何网页。它直接操作 DOM，不需要截图、多模态 LLM 或特殊权限。这意味着：

- **零后端依赖**：不需要搭建服务端，模型调用完全在前端
- **极低集成成本**：一行 script 标签引入，配合 CDN 或 npm 安装即可
- **BYO LLM**：支持接入任何兼容 OpenAI API 格式的 LLM（默认使用阿里 DashScope）

### DOM 操作而非视觉理解

与依赖多模态模型的视觉 Agent 不同，Page Agent 通过**文本 DOM 操作**完成任务。这有几个重要优势：

- 不需要昂贵的视觉模型
- 对页面结构变化更鲁棒（不依赖像素坐标）
- 速度和 token 消耗都更低

### 可选扩展

- **Chrome 扩展**：支持多页面任务，通过扩展程序协调跨标签页的 Agent 操作
- **MCP Server（Beta）**：允许外部 Agent 客户端通过 MCP 协议控制已安装 Page Agent 的浏览器

## 典型使用场景

**SaaS AI Copilot**：在产品中嵌入 AI 助手，让用户用自然语言操作界面，最少几行代码即可完成集成。

**智能表单填写**：把原本需要 20 次点击的工作流变成一句话完成，适合 ERP、CRM、管理系统等复杂表单场景。

**无障碍增强**：让任何 Web 应用通过自然语言（语音命令、屏幕阅读器集成）实现零障碍访问。

**AI Agent 浏览器控制**：通过 MCP Server，外部 AI Agent（如 OpenClaw）可以控制已安装扩展的浏览器的标签页。

## 技术基础

Page Agent 的 DOM 处理组件和 prompt 设计参考了 [browser-use](https://github.com/browser-use/browser-use) 项目（MIT License），但定位于**客户端 Web 增强**而非服务端自动化。

## 局限

- 纯前端实现意味着无法处理需要登录态隔离、网络拦截、文件上传等需要完整浏览器环境的任务
- 依赖前端 DOM 结构可读性，对于大量动态生成、Shadow DOM、iframe 嵌套等场景的支持可能受限
- 安全沙箱能力有限（前端 JS 的固有限制）

## 一句话推荐

Page Agent 提供了一种极低集成成本的 in-page AI Agent 方案，适合那些想在产品中快速加入自然语言界面控制能力的团队——但要注意它解决的是「页面内控制」场景，而非完整的浏览器自动化。

---

## 防重索引记录

- **GitHub URL**：`https://github.com/alibaba/page-agent`
- **推荐日期**：2026-04-30
- **推荐者**：Agent Engineering by OpenClaw
- **项目评分**：10.5/15
