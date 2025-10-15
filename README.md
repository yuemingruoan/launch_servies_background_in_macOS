# macOS 后台服务管理器 (launch_server)

## 概览

本项目提供了一个专业的命令行工具 `launch_server`，用于在 macOS 上轻松管理后台服务。它通过 macOS 原生的 `launchd` 服务框架，确保你的程序在用户登录后自动、静默地启动，并提供了一套完整的命令来实时控制这些服务。

其核心特性是**自动化的日志管理**和对**复杂启动场景**的支持。你可以安全地直接运行程序，也可以在需要时（如设置 `ulimit`）使用 shell 来执行命令。

## 功能特性

- **支持 Shell 命令**: 通过 `shell_command` 选项，可以运行需要 `ulimit`, `&&`, `|` 等 shell 特性的复杂命令。
- **自动化日志管理**: 只需配置一次日志根目录，即可自动为服务创建带时间戳的日志文件。
- **全局命令**: 安装后，可在终端任何位置使用 `launch_server` 命令。
- **自动化安装/卸载**: 提供 `install.sh` 和 `uninstall.sh` 脚本，一键完成所有配置。
- **国际化 (i18n)**: 自动检测系统语言，目前支持**简体中文**和英文。

## 安装

1.  **克隆或下载项目**:
    将本项目文件放置在你希望永久保留的位置。

2.  **运行安装脚本**:
    打开终端，进入项目目录，然后运行 `install.sh`。

    ```bash
    cd /path/to/launch_servies_background_in_macOS
    bash install.sh
    ```
    安装脚本会自动处理所有事情，包括编译语言包、创建全局命令、并询问你是否要设置开机自启动。

## 配置文件 (`config.json`)

这是你定义所有后台服务的地方。`config.json` 包含 `settings` 和 `services` 两个部分。

- **`settings`**: 用于全局设置。
  - `log_directory`: **必须指定**。所有服务日志的根目录。

- **`services`**: 一个服务对象的数组。

### 配置服务 (`services` 数组详解)

每个服务对象**必须且只能**包含 `command` 或 `shell_command` 之一。

- **`command` (推荐)**: 用于直接、安全地执行一个程序。
- **`shell_command`**: 用于需要 shell 特性的场景。**注意**: 使用此选项时，请确保命令是安全的，因为它会由 shell 直接解释。

| 字段名 | 类型 | 描述 |
|---|---|---|
| `name` | string | 服务的**唯一**可读名称。 |
| `command` | string | 要执行的程序或脚本的**绝对路径**。 |
| `args` | array | 传递给 `command` 的参数列表 (与 `shell_command` 不兼容)。 |
| `shell_command` | string | 要在 shell 中执行的完整命令字符串。 |
| `env` | object | 为该服务设置的特定环境变量。 |
| `enabled`| boolean| `true` 表示该服务将在 `start` 命令时启动。 |

### 示例:

**使用 `command` (标准方式):**
```json
{
  "name": "Simple Python Web Server",
  "command": "/usr/bin/python3",
  "args": ["-m", "http.server", "8080"],
  "env": {},
  "enabled": true
}
```

**使用 `shell_command` (高级场景):**
```json
{
  "name": "Qdrant Server",
  "shell_command": "ulimit -n 99999 && /path/to/your/qdrant --config-path /path/to/config.yaml",
  "env": {},
  "enabled": true
}
```

## 日志结构

日志会自动生成在 `log_directory` 中，并按服务名和时间戳进行归档。

## 如何使用 `launch_server`

安装成功后，你就可以在终端的任何位置使用 `launch_server` 命令了。

**可用命令:** `check`, `start`, `status`, `stop <服务名>`, `restart <服务名>`, `disable <服务名>`, `enable <服务名>`。

## 卸载

运行 `uninstall.sh` 脚本即可干净地移除所有组件。
