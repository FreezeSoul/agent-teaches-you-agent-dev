# CUA：计算机使用 Agent 的开源基础设施——全栈沙箱 + 基准测试 + 跨 OS 支持

**Target（目标用户）**：正在构建或评估「计算机使用 Agent」（Computer-Use Agent）的团队——需要跨平台（macOS/Linux/Windows）沙箱能力、标准化基准测试框架、或本地化安全执行环境的企业开发者和研究者。

**Result（成果）**：CUA 提供了一个统一 API 的 Agent 计算机使用平台，今日增长 +359 stars（GitHub Trending），让开发者在「一行代码切换运行平台」的同时，获得与 OSWorld/ScreenSpot 等标准基准的对齐。

**Insight（技术洞察）**：计算机使用 Agent 的核心挑战不是「让 Agent 点击按钮」，而是构建可靠、可量化、可复现的「Agent 与操作系统交互」基础设施——包括沙箱隔离、截图→动作循环、轨迹录制、基准测试。CUA 的创新在于将这四个能力统一到同一个 Python 包中，并支持本地（QEMU）和云端两种运行时。

**Proof（验证）**：GitHub 9,574 Stars，OpenAI/Microsoft/Google 等厂商在 computer-use 方向的投入持续增加，OSWorld 基准论文被引用超过 500 次——computer-use agent 已成独立研究领域。

---

## 一、定位：计算机使用 Agent 的全栈基础设施

CUA 定位于「计算机使用 Agent」的完整工具链层——不是单点工具（如某个截图库或某个沙箱），而是覆盖从开发、测试到部署的全流程：

```python
# 一次编写，任意平台运行
from cua import Sandbox, Image

async with Sandbox.ephemeral(Image.linux()) as sb:
    result = await sb.shell.run("echo hello")
    screenshot = await sb.screenshot()
    await sb.mouse.click(100, 200)
    await sb.keyboard.type("Hello from Cua!")
```

这个 API 设计的关键洞察：**「让 Agent 操作计算机」这个动作，在不同 OS 上的本质是相同的**（截图→分析→决策→执行→验证），抽象层应该屏蔽 OS 差异，而不是让开发者写三套代码。

| 平台 | 云端（cua.ai）| 本地（QEMU） |
|------|--------------|-------------|
| Linux | ✅ | ✅ |
| macOS | ✅ | ✅ |
| Windows | ✅ | ✅ |
| Android | ✅ | ✅ |
| BYOI（自定义镜像）| 即将 | ✅ |

---

## 二、核心能力拆解

### 2.1 CUA Sandboxes：统一 API 的跨平台沙箱

CUA 的沙箱设计支持四种隔离级别：

**云端沙箱**：由 cua.ai 托管，提供网络隔离和按需扩展的算力，适合 CI 集成和大规模并行评测。

**本地 QEMU 虚拟机**：不依赖云端，隐私敏感场景下完全本地运行，数据不出网络边界。

**macOS Virtualization.Framework**：在 Apple Silicon 上利用苹果原生虚拟化框架实现接近原生的性能——这是实现「背景操作」（后台 Agent 点击操作不抢占前台焦点）的技术基础。

**Lume 子系统**：CUA 的 macOS 虚拟化管理 CLI，支持一行命令启动 macOS VM：
```bash
lume run macos-sequoia-vanilla:latest
```

### 2.2 CUA Driver：后台计算机操作的核心能力

> "Drive any native macOS app in the background — agents click, type, and verify without stealing the cursor, focus, or Space, even on non-AX surfaces like Chromium web content and canvas-based tools (Blender, Figma, DAWs, game engines)."

这是 CUA 最独特的技术能力。传统的计算机使用 Agent 在 macOS 上操作时，会抢占用户键盘和鼠标焦点，导致「Agent 工作时人无法用电脑」的困境。CUA Driver 通过 macOS 的辅助功能（Accessibility）API 实现后台操作——Agent 可以在后台点击、输入、验证，而不干扰前台用户操作。

### 2.3 CUA Bench：标准化基准测试框架

> "Evaluate computer-use agents on OSWorld, ScreenSpot, Windows Arena, and custom tasks. Export trajectories for training."

CUA Bench 提供：
- **标准化任务集**：OSWorld（通用计算机操作）、ScreenSpot（GUI 定位）、Windows Arena（Windows 操作）等
- **轨迹导出**：每个评测任务生成完整轨迹（trajectory），可用于训练数据生成或失败案例分析
- **自定义任务**：支持传入自定义 Docker 镜像定义新任务

### 2.4 CUA Bot：零配置 Agent 沙箱

```bash
cuabot claude   # Claude Code 沙箱运行
cuabot openclaw  # OpenClaw 沙箱运行
cuabot chromium  # 任意 GUI 工作流沙箱
```

CUA Bot 的设计理念：**让任何编码 Agent（Claude Code、Cursor、OpenClaw 等）一键进入沙箱环境**，无需手动配置 Docker 或 VM。

---

## 三、技术架构：跨层解耦设计

CUA 的架构与 Anthropic 的 Brain-Hands 解耦思路一致：

| CUA 层 | Anthropic 等效概念 | 说明 |
|--------|-------------------|------|
| **CUA Driver** | Hands（执行层）| 直接操作 macOS 应用的后台进程 |
| **CUA Sandbox** | Hands（隔离层）| QEMU/云端 VM，提供文件系统和网络隔离 |
| **CUA Agent SDK** | Brain（Harness 层）| 编排决策循环，调用沙箱执行操作 |
| **Session/Trajectory** | Externalized Session Log | 持久化操作历史，供分析和回放 |

CUA Bot 的 OpenClaw 集成说明：
> "Built-in support for `agent-browser` and `agent-device` (iOS, Android) out of the box."

这意味着 CUA 将 OpenClaw 的 browser 能力作为「视觉输入」，与自己的沙箱操作能力结合——这是典型的「感知 + 执行」双通道架构。

---

## 四、与 Cursor Cloud Agent 开发环境的关联

**关联主题**：企业级 Agent 需要可靠的开发/执行环境，而不仅仅是「能运行代码的容器」。

**互补点**：
- **Cursor 环境**：解决「多代码库环境配置」问题——让 Agent 获得正确的代码上下文
- **CUA 沙箱**：解决「安全执行」问题——让 Agent 的操作不破坏主机、不泄露数据
- **结合后的状态**：Cursor Cloud Agent 配置多代码库环境 → Agent 在 CUA 沙箱中执行代码 → 全流程隔离、可审计、可回滚

Cursor 的文章提到：
> "An agent that can write code but can't run tests, query services, or reach APIs cannot close the loop on its work."

CUA 正是这个「闭环」缺失的那一环——可靠的、与平台无关的、安全的代码执行环境。

---

## 五、快速上手

```bash
# 安装 cua（Python 3.11+）
pip install cua

# 运行第一个沙箱（Linux Docker）
python3 -c "
from cua import Sandbox, Image
import asyncio

async def main():
    async with Sandbox.ephemeral(Image.linux()) as sb:
        result = await sb.shell.run('echo hello cua')
        print(result.stdout)

asyncio.run(main())
"
```

对于评测任务：
```bash
# 安装 cua-bench
cd cua-bench && uv tool install -e . 

# 创建基准镜像
cb image create linux-docker

# 运行基准测试
cb run dataset datasets/cua-bench-basic --agent cua-agent --max-parallel 4
```

---

## 六、适合与不适合的场景

**适合**：
- ✅ 评估计算机使用 Agent 能力（OSWorld/ScreenSpot 基准对齐）
- ✅ 需要 macOS 背景操作能力（不抢占前台焦点）
- ✅ 隐私敏感场景（数据不出网络，完全本地 QEMU 运行）
- ✅ 跨平台 Agent 评测（Linux/macOS/Windows/Android 统一 API）

**不适合**：
- ❌ 只需要简单 HTTP API 调用（用 LangChain 等更轻量的框架）
- ❌ Windows 原生 GUI 操作（目前本地 QEMU 模式支持有限）
- ❌ 毫秒级延迟敏感的操作（沙箱层引入额外延迟）

---

**引用来源**：
> "Drive any native macOS app in the background — agents click, type, and verify without stealing the cursor, focus, or Space, even on non-AX surfaces like Chromium web content and canvas-based tools."
> — [CUA GitHub: cua-driver](https://github.com/trycua/cua)

> "Build agents that see screens, click buttons, and complete tasks autonomously. One API for any VM or container image — cloud or local."
> — [CUA GitHub](https://github.com/trycua/cua)

> "Evaluate computer-use agents on OSWorld, ScreenSpot, Windows Arena, and custom tasks. Export trajectories for training."
> — [CUA GitHub](https://github.com/trycua/cua)

> "Built-in support for `agent-browser` and `agent-device` (iOS, Android) out of the box."
> — [CUA GitHub](https://github.com/trycua/cua)