# macOS 后台服务管理器 (launch_server)

## 概览

本项目提供了一个专业的命令行工具 `launch_server`，用于在 macOS 上轻松管理后台服务。它通过 macOS 原生的 `launchd` 服务框架，确保你的程序在用户登录后自动、静默地启动，并提供了一套完整的命令来实时控制这些服务。

其核心特性是**自动化的日志管理**：你只需指定一个日志根目录，工具便会自动为每个服务创建独立的子目录，并以时间戳命名日志文件，极大地简化了配置和后续的问题排查。

## 功能特性

- **自动化日志管理**: 只需配置一次日志根目录，即可自动为服务创建带时间戳的日志文件。
- **全局命令**: 安装后，可在终端任何位置使用 `launch_server` 命令。
- **自动化安装/卸载**: 提供 `install.sh` 和 `uninstall.sh` 脚本，一键完成所有配置。
- **国际化 (i18n)**: 自动检测系统语言，目前支持**简体中文**和英文。
- **后台静默运行**: 所有服务都在后台运行，没有任何终端窗口。
- **集中化配置**: 通过一个简单的 `config.json` 文件即可管理所有服务。

## 安装

1.  **克隆或下载项目**:
    将本项目文件放置在你希望永久保留的位置。

2.  **运行安装脚本**:
    打开终端，进入项目目录，然后运行 `install.sh`。

    ```bash
    cd /path/to/launch_servies_background_in_macOS
    bash install.sh
    ```
    安装脚本会自动处理所有事情：
    - 如果 `config.json` 不存在，它会从 `example_config.json` 创建一个。
    - 编译语言包。
    - 创建 `launch_server` 全局命令（可能会请求管理员密码）。
    - 询问你是否要设置开机自启动。

## 配置文件 (`config.json`)

这是你定义所有后台服务的地方。`config.json` 包含两个主要部分：`settings` 和 `services`。

- **`settings`**: 用于全局设置。目前只有一个选项：
  - `log_directory`: **必须指定**。所有服务日志的根目录。推荐使用 `~/Library/Logs/launch_server`。工具会自动处理 `~`。

- **`services`**: 一个服务对象的数组。每个对象定义一个后台服务。

### 配置服务 (`services` 数组详解)

请参考 `example_config.json` 获取完整的示例。

| 字段名 | 类型 | 描述 |
|---|---|---|
| `name` | string | 服务的**唯一**可读名称，用于命令行和日志子目录。|
| `command` | string | 要执行的程序或脚本的**绝对路径**。 |
| `args` | array | 传递给程序的命令行参数列表。 |
| `env` | object | 为该服务设置的特定环境变量。 |
| `enabled`| boolean| `true` 表示该服务将在 `start` 命令时启动。 |

## 日志结构

日志会自动生成在 `log_directory` 中，结构如下：

```
~/Library/Logs/launch_server/
├── error/
│   └── 2023-10-27_12-05-00.log  (致命错误报告)
├── launch_server/
│   ├── 2023-10-27_12-00-00.log  (launch_server 工具自身的操作日志)
│   └── launchd_bootstrap.log    (launchd 服务的引导日志)
└── Service Name A/
    └── 2023-10-27_10-30-00.log  (服务 A 的日志)
```

- **服务日志**: 每个服务的输出都会被重定向到其名称对应的子目录下。
- **工具日志 (`launch_server/`)**: 记录 `launch_server` 命令的**所有正常操作**，并采用结构化格式。
- **致命错误报告 (`error/`)**:
  - 当 `launch_server` 遇到**严重**的、**无法恢复**的错误时（例如，`config.json` 损坏），它会在这里生成一份详细的调试报告。
  - 这份报告包含完整的错误堆栈、环境信息和上下文，是进行问题排查的最重要依据。即使在 `config.json` 无法读取的情况下，备用错误报告也会被尝试写入项目根目录下的 `logs/error/` 文件夹中，以保持结构一致性。

## 如何使用 `launch_server`

安装成功后，你就可以在终端的任何位置使用 `launch_server` 命令了。

**可用命令:**

- **`launch_server check`**:
  检查 `config.json` 文件是否存在语法和结构错误。在修改配置文件后，推荐使用此命令进行验证。

- **`launch_server start`**:
  启动所有已启用的服务。**注意**: 此命令会自动先进行配置检查。如果 `config.json` 仍处于未修改的模板状态，它会给出一个友好的提示。

- **`launch_server status`**:
  显示所有服务的状态。如果 `config.json` 仍处于未修改的模板状态，它会给出一个友好的提示。

- **`launch_server stop <服务名>`**:
  临时停止一个服务。

- **`launch_server restart <服务名>`**:
  重启一个服务。

- **`launch_server disable <服务名>`**:
  永久禁用一个服务（修改配置文件）。

- **`launch_server enable <服务名>`**:
  重新启用一个服务（修改配置文件）。

## 卸载

运行 `uninstall.sh` 脚本即可干净地移除所有组件。

```bash
cd /path/to/launch_servies_background_in_macOS
bash uninstall.sh
```

## 权限说明

- **安装时的管理员权限 (`sudo`)**:
  安装脚本在向 `/usr/local/bin` 目录写入 `launch_server` 命令时，会请求管理员密码。这是在 macOS 上安装全局命令行工具的标准做法。

- **运行时的用户权限**:
  本工具被设计为**用户级别**的服务 (`LaunchAgent`)，所有后台服务都将以**当前登录用户的身份**运行，这更加安全。

## 国际化 (i18n)

本工具支持多语言，会自动检测你的系统语言环境。

- **目前支持**: 简体中文 (`zh_CN`) 和英文 (默认)。
- **贡献翻译**: 欢迎在 `locales/` 目录下贡献新的语言翻译。
