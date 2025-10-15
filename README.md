# macOS 后台服务管理器 (launch_server)

## 概览

本项目提供了一个专业的命令行工具 `launch_server`，用于在 macOS 上轻松管理后台服务。它通过 macOS 原生的 `launchd` 服务框架，确保你的程序在用户登录后自动、静默地启动，并提供了一套完整的命令来实时控制这些服务。

## 功能特性

- **全局命令**: 安装后，可在终端任何位置使用 `launch_server` 命令。
- **自动化安装/卸载**: 提供 `install.sh` 和 `uninstall.sh` 脚本，一键完成所有配置。
- **国际化 (i18n)**: 自动检测系统语言，目前支持**简体中文**和英文。
- **后台静默运行**: 所有服务都在后台运行，没有任何终端窗口。
- **集中化配置**: 通过一个简单的 `config.json` 文件即可管理所有服务。
- **独立环境变量**: 为每个服务单独配置环境变量，避免冲突。
- **日志与进程管理**: 自动记录日志并管理进程 PID。

## 安装

1.  **克隆或下载项目**:
    将本项目文件放置在你希望永久保留的位置。

2.  **运行安装脚本**:
    打开终端，进入项目目录，然后运行 `install.sh`。

    ```bash
    cd /path/to/launch_servies_background_in_macOS
    bash install.sh
    ```
    安装脚本会引导你完成整个过程。你可能会被要求输入密码，因为脚本需要在 `/usr/local/bin` 中创建 `launch_server` 全局命令。

    **开机自启动选项**: 在安装过程中，脚本会询问你是否希望将服务设置为在用户登录时自动启动。
    - 如果你选择 **是 (Y)**，脚本会自动配置 `launchd` 服务。
    - 如果你选择 **否 (n)**，将跳过自动启动的设置。你之后仍然可以随时通过 `launch_server start` 命令手动启动所有服务。

## 如何使用 `launch_server`

安装成功后，你就可以在终端的任何位置使用 `launch_server` 命令了。

### **可用命令:**

- **`launch_server start`**
  启动配置文件中所有 `enabled: true` 的服务。`launchd` 在登录时会自动执行此命令。

- **`launch_server status`**
  显示所有已配置服务的状态（是否启用，是否正在运行）。

- **`launch_server stop <服务名>`**
  **临时停止**一个正在运行的服务。这**不会**修改配置文件。
  ```bash
  launch_server stop "Simple Python Web Server"
  ```

- **`launch_server restart <服务名>`**
  重启一个服务。
  ```bash
  launch_server restart "Simple Python Web Server"
  ```

- **`launch_server disable <服务名>`**
  **永久禁用**一个服务。此命令会停止服务并修改 `config.json`，将 `"enabled"` 设为 `false`。
  ```bash
  launch_server disable "Continuous Ping Test"
  ```

- **`launch_server enable <服务名>`**
  重新启用一个已被禁用的服务，此命令会将 `"enabled"` 修改为 `true`。
  ```bash
  launch_server enable "Continuous Ping Test"
  ```

## 如何配置 `config.json`

`config.json` 是一个 JSON 数组，每个对象代表一个服务。

| 字段名 | 类型 | 描述 |
|---|---|---|
| `name` | string | 服务的**唯一**可读名称，用于命令行操作。 |
| `command` | string | 要执行的程序或脚本的**绝对路径**。 |
| `args` | array | 传递给程序的命令行参数列表。 |
| `env` | object | 为该服务设置的特定环境变量。 |
| `log_path` | string | 存储该服务日志的**绝对路径**。 |
| `enabled` | boolean | `true` 表示该服务将在 `start` 命令时启动。 |

## 卸载

如果你想完全移除本工具，只需运行 `uninstall.sh` 脚本：

```bash
cd /path/to/launch_servies_background_in_macOS
bash uninstall.sh
```
该脚本会自动停止服务、移除 `launchd` 配置和 `launch_server` 命令。

## 权限说明

- **安装时的管理员权限 (`sudo`)**:
  安装脚本在向 `/usr/local/bin` 目录写入 `launch_server` 命令时，会请求管理员密码。这是在 macOS 上安装全局命令行工具的标准做法，是安全且必要的操作。

- **运行时的用户权限**:
  本工具被设计为**用户级别**的服务 (`LaunchAgent`)，这意味着所有后台服务都将以**当前登录用户的身份**运行。这样做更安全，能防止后台服务意外修改系统关键文件。

- **重要限制**:
  由于服务是以普通用户权限运行，它们无法执行需要 `root` 权限的操作，例如绑定到 1024 以下的网络端口（如 80, 443）。如果你的服务需要此类权限，你需要探索以 `LaunchDaemon` 方式运行，但这会增加复杂性和安全风险，已超出本工具的设计范围。

## 国际化 (i18n)

本工具支持多语言。它会自动检测你的系统语言环境 (`LANG` 环境变量)，并显示相应的语言。

- **目前支持**: 简体中文 (`zh_CN`) 和英文 (默认)。
- **贡献翻译**: 我们欢迎你贡献新的语言翻译！只需复制 `locales/zh_CN` 目录，将其重命名为你的语言代码 (如 `fr_FR`)，然后翻译 `messages.po` 文件中的字符串即可。

## 文件结构详解

- **`manager.py`**: 工具的核心逻辑，一个可执行的 Python 脚本。
- **`config.json`**: 你的服务配置文件。
- **`install.sh` / `uninstall.sh`**: 自动化安装和卸载脚本。
- **`com.user.backgroundservices.plist`**: `launchd` 服务的模板文件。
- **`locales/`**: 存放语言包的目录。
- **`logs/` / `pids/`**: (自动创建) 分别用于存放日志和进程 ID 文件。
