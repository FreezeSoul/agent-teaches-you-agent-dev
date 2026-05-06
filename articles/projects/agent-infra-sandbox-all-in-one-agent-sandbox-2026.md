# AIO Sandbox：让 AI Agent 拥有「完整开发环境」的开源沙箱框架

## TRIP 要素

**Target**：需要为 AI Agent 提供可信赖执行环境的开发者与平台工程师——既包括想快速在本地验证 Agent 行为的个人开发者，也包括需要在生产环境部署隔离 Agent 执行空间的企业团队。

**Result**：30 秒内启动一个包含浏览器、终端、文件系统、VSCode Server、Jupyter 和 MCP 服务的完整沙箱；代码在浏览器中下载后立即可在 Shell 中访问，文件操作跨容器无缝衔接。

**Insight**：传统沙箱方案各司其职（浏览器沙箱、代码执行沙箱、Shell 沙箱），彼此隔离导致文件共享和功能协调极为困难。AIO Sandbox 的核心洞察是：**AI Agent 需要的不是多个隔离的沙箱，而是一个在统一文件系统内运作的多接口执行环境**。

**Proof**：GitHub 2.3k Stars，Docker Hub 120M+ Pulls，涵盖 Python/TypeScript/Go 三种 SDK，服务驻留中国国内可访问的镜像站点。

---

## P-SET 结构

### P - Positioning

**一句话定义**：一个 All-in-One 的 Agent 执行沙箱——把浏览器、终端、文件系统、VSCode、Jupyter、MCP 服务全部装进同一个 Docker 容器，用统一文件系统把它们串联起来。

**场景锚定**：当你需要让 AI Agent 执行「打开网页→下载文件→在终端处理→用 VSCode 审查」这类跨工具工作流时，AIO Sandbox 提供的就是那个「一站式执行空间」。

**差异化标签**：统一文件系统（这是它与所有单点沙箱方案的本质区别）

### S - Sensation

启动 AIO Sandbox 后，你得到的是一个完整的云端开发环境。访问 `http://localhost:8080`，迎面而来的是多个接口选择：VNC 浏览器可以打开网页，VSCode Server 可以编辑代码，Jupyter 可以运行 Python，Terminal 可以执行 Shell 命令。

关键在于**它们共享同一个文件系统**。当你在 VNC 浏览器中下载了一个文件，这个文件立即出现在 Shell 的工作目录和 VSCode 的文件树里。你不需要手动传输、不需要挂载卷，Agent 可以直接在多工具间切换而不会遇到「文件找不到」的问题。

Python SDK 的使用体验：

```python
from agent_sandbox import Sandbox

# 初始化客户端
client = Sandbox(base_url="http://localhost:8080")
home_dir = client.sandbox.get_context().home_dir

# 执行 Shell 命令
result = client.shell.exec_command(command="ls -la")
print(result.data.output)

# 文件操作
content = client.file.read_file(file=f"{home_dir}/.bashrc")

# 浏览器自动化
screenshot = client.browser.screenshot()
```

TypeScript SDK：

```typescript
import { Sandbox } from '@agent-infra/sandbox';

const sandbox = new Sandbox({ baseURL: 'http://localhost:8080' });

// Shell 执行
const result = await sandbox.shell.exec({ command: 'ls -la' });

// 文件读取
const content = await sandbox.file.read({ path: '/home/gem/.bashrc' });

// 浏览器截图
const screenshot = await sandbox.browser.screenshot();
```

**哇时刻**：30 秒 `docker run` 就能启动一个包含 6 种工具的完整环境，而且文件在所有工具间自动共享——这在传统方案里需要配置多个容器+网络+卷挂载才能实现。

### E - Evidence

**技术架构**

AIO Sandbox 将 Browser（VNC + CDP）、Shell（WebSocket Terminal）、File System、MCP Services、VSCode Server、Jupyter Notebook 六种组件运行在同一个 Docker 容器内，通过共享文件系统实现零摩擦的跨工具协作。

统一文件系统的设计逻辑：传统方案中每个工具都有自己的存储空间，数据要跨工具流动必须通过显式的传输机制。AIO Sandbox 将所有工具的根目录指向同一个文件系统，Agent 在工具间切换时不需要考虑「这个文件在上一个工具的哪个目录里」。

**Browser 控制的三层接口**

AIO Sandbox 提供三种浏览器控制方式：

- **VNC**：通过远程桌面进行可视化交互，适合人类协作场景
- **CDP（Chrome DevTools Protocol）**：程序化控制，用于截图、DOM 操作、Network 监听
- **MCP**：高级浏览器自动化工具，通过 MCP 协议暴露浏览器能力给 AI Agent

> "All components run in the same container with a shared filesystem, enabling seamless workflows."
> — [agent-infra/sandbox README](https://github.com/agent-infra/sandbox)

**与 Cursor Automations 的互补关系**

Cursor Automations 运行在 Cursor 的云端沙箱，为 Agent 提供「规则清晰但执行枯燥」的自动化能力。AIO Sandbox 则提供了更底层的基础设施：**让 Agent 拥有一个完整的开发执行空间**。如果你想在 Cursor 外部构建类似的自动化能力，AIO Sandbox 是一个可直接集成的执行环境。

**MCP 兼容性**

AIO Sandbox 预配置了多个 MCP Servers，开箱即用。这意味着 AI Agent（无论用 Claude Code、Cursor 还是其他框架）都可以通过 MCP 协议调用 AIO Sandbox 的各项能力。

> "Zero Configuration - Pre-configured MCP servers and development tools ready to use"
> — [agent-infra/sandbox README](https://github.com/agent-infra/sandbox)

### T - Threshold

**快速上手（3 步）**

```bash
# Step 1: 启动容器
docker run --security-opt seccomp=unconfined --rm -it -p 8080:8080 ghcr.io/agent-infra/sandbox:latest

# Step 2: 访问 Web 接口
# http://localhost:8080/v1/docs     — 文档
# http://localhost:8080/vnc/        — VNC 浏览器
# http://localhost:8080/code-server/ — VSCode Server
# http://localhost:8080/mcp        — MCP 服务端点

# Step 3: 用 SDK 集成（Python 示例）
from agent_sandbox import Sandbox
client = Sandbox(base_url="http://localhost:8080")
result = client.shell.exec_command(command="echo 'hello'")
```

**国内加速**

中国区用户可以直接使用字节跳动提供的国内镜像，无需配置代理：

```bash
docker run --security-opt seccomp=unconfined --rm -it -p 8080:8080 \
  enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest
```

**适合贡献的场景**

- MCP Server 开发：为特定工具编写 MCP 协议封装
- 浏览器自动化工具：基于 CDP 接口开发更高级的自动化能力
- 文件系统集成：在共享文件系统上构建跨工具的数据处理管道

**路线图关注点**

AIO Sandbox 的定位是「基础设施层」，其路线图主要取决于 Agent 框架的发展方向。如果多 Agent 协作成为主流，对统一沙箱环境的需求会显著增加。建议关注其 GitHub Releases 的版本更新，尤其是 MCP 协议版本兼容性的变化。

---

## 差异化验证

如果把 AIO Sandbox 换成「Docker + VNC + 手动挂载卷」，差异在哪里？

AIO Sandbox 的核心差异化是**统一文件系统 + 多接口预集成**。手动方案需要：
1. 配置多个容器（browser / shell / vscode）
2. 设置网络通信
3. 配置共享存储卷
4. 逐个安装和配置 MCP Servers
5. 处理各容器间的文件同步

AIO Sandbox 把这一切打包成一个 `docker run` 命令，而且全部预配置好了 MCP 服务。对于需要快速验证 Agent 行为或快速搭建测试环境的场景，这个差异化非常显著。

---

**关联文章**

- [Cursor Automations：面向软件工厂的常驻 Agent 执行引擎](./cursor-automations-always-on-agent-software-factory-2026.md) — Automations 的 Cloud Sandbox 执行模式，AIO Sandbox 可作为其本地化替代方案
- [Cursor Self-Hosted Cloud Agents：企业级 Kubernetes 部署架构](./cursor-self-hosted-cloud-agents-kubernetes-enterprise-deployment-2026.md) — 企业级 Agent 部署，与 AIO Sandbox 的本地快速验证场景形成互补

---

*推荐来源：GitHub Trending + agent-browser 工具生态*