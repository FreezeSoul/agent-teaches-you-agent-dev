# 今日推荐项目：react-doctor — AI 生成的 React 代码质量检测

**关联主题**：本次 Anthropic April 2026 Postmortem 揭示了 Agent 系统的一个核心风险——「状态在跨层交互中被错误传播」。react-doctor 从另一个角度解决同一个根本问题：**AI 生成的代码可能在语义上看起来正确，但在质量和最佳实践层面存在缺陷**。两者共同指向一个结论：Agent 系统的输出质量不能仅依赖模型本身的智能，需要额外的监控层。

**读者画像**：关注 AI 编程工具质量的工程师，想了解如何检测 AI 生成代码中的常见反模式。

**核心主张**：react-doctor 是一个"AI 代码质量守门人"——它不评价代码逻辑是否正确，而是检测 AI 在生成 React 代码时系统性地犯哪些错误，帮助团队建立针对性的 lint 规则和最佳实践基线。

---

## 1. 项目概述

**GitHub**: [millionco/react-doctor](https://github.com/millionco/react-doctor) ⭐ 9,100+

**一句话描述**："Your agent writes bad React. This catches it"——专门检测 AI 生成的 React 代码中的质量问题。

### 解决的问题

AI 编程工具（Cursor、Claude Code、GitHub Copilot）生成的 React 代码有可识别的系统性问题：

- **Missing key props in lists**：AI 经常忘记在 `.map()` 中添加 `key`
- **Inline object styles**：倾向于内联 style 对象而非 CSS class
- **Inline function definitions in JSX**：`.map((item, index) => <div onClick={() => handleClick(item)} ...>` 每次渲染创建新函数
- **Incorrectref usage**：对 `ref` 的误用（如将 `ref` 当作 state）
- **Inefficient state management**：过度使用 `useState`，不会用 `useReducer` 或 Zustand

react-doctor 的核心假设：如果这些错误可以被系统性地检测出来，它们就不是「偶发的模型错误」，而是「AI 编程工具的结构性倾向」——后者可以通过 lint 配置、prompt 工程或 harness 层干预来解决。

---

## 2. 技术实现

### 2.1 工作原理

react-doctor 是一个 ESLint 插件，通过静态分析检测 AI 生成的 React 代码中的特定模式。

```bash
npm install react-doctor
```

配置方式：
```javascript
// eslint.config.mjs
import reactDoctor from 'react-doctor'

export default [
  reactDoctor(),
  // ... other configs
]
```

### 2.2 核心规则

| 规则 ID | 检测目标 | 描述 |
|---------|---------|------|
| `ai/no-inline-function-in-jsx` | JSX 内联函数 | `.map(item => <div onClick={() => fn(item)}>)` 每次渲染创建新函数引用 |
| `ai/no-missing-key` | 列表缺少 key | `.map(item => <Component />)` 缺少稳定的 key prop |
| `ai/no-boolean-in-jsx` | JSX 渲染布尔值 | `{flag && <Component />}` 未显式处理 |
| `ai/no-new-scripts-in-production` | 生产环境 new Script() | 动态加载脚本的潜在 XSS 风险 |
| `ai/no-mutable-global` | 可变全局状态 | 直接修改 `window.globalState` 类型的不安全模式 |
| `ai/no-direct-mutation-of-props` | Props 直接修改 | `props.items.push(...)` 违反 React 数据流 |

---

## 3. 为什么推荐这个项目

### 3.1 与本仓库主题的关联性

Anthropic April 2026 Postmortem 的核心教训之一：**Agent 系统的质量缺陷往往不在「智能不足」，而在「正确组件的错误组合」**。react-doctor 提供了一个补充视角：

- Postmortem 关注 **Agent 系统本身的缺陷检测**（跨层交互 bug）
- react-doctor 关注 **Agent 输出的代码的质量监控**（结构性的 AI 编程错误模式）

两者共同构建了一个完整的「Agent 质量保障体系」：既监控 Agent 系统本身的运行时行为，也监控 Agent 生成内容的静态质量。

### 3.2 开源夏洛克（Open Source Sherlock）

项目维护者在博客中提到，react-doctor 的开发过程使用了"AI 来研究 AI 生成的代码"的工作流：

1. 收集 Cursor、Claude Code 等工具生成的 React 代码样本
2. 运行 react-doctor 检测错误模式
3. 根据检测结果迭代更新规则

这本身就是一个「测量驱动改进」的案例——与 Anthropic 的 eval-driven development 一脉相承。

### 3.3 实际适用性

对于使用 Cursor、Claude Code 等工具的团队：
- **直接价值**：在 CI 中集成 react-doctor，自动拦截有问题的 AI 生成代码
- **间接价值**：通过错误分布了解当前 AI 工具的结构性弱点，用于调整 prompt 或选择更适合的模型

---

## 4. 与 Cursor Composer 的对比

react-doctor 与 Cursor 2026年5月6日发布的「Context Usage Breakdown」功能形成有趣的对比：

| 维度 | react-doctor | Cursor Context Usage Breakdown |
|------|-------------|---------|
| 层面 | 静态代码分析 | 运行时 context 消耗监控 |
| 检测目标 | 代码最佳实践违反 | context window 使用效率 |
| 触发时机 | CI 阶段（代码提交后）| 开发阶段（实时）|
| 问题类型 | 质量问题（代码风格/性能）| 效率问题（token 浪费）|

两者互补：react-doctor 保证输出质量，Context Usage Breakdown 保证输入效率。

---

## 5. 快速开始

```bash
# 安装
npm install react-doctor

# 在项目中运行
npx react-doctor ./src

# ESLint 配置中启用
# eslint.config.mjs
import reactDoctor from 'react-doctor'
export default [reactDoctor()]
```

---

**相关引用**：
- [GitHub: millionco/react-doctor](https://github.com/millionco/react-doctor)
- 项目 README 中提到的「AI 研究 AI」工作流体现了测量驱动的开发理念，与本仓库多篇文章的主题一致