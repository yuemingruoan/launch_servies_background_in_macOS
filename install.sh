#!/bin/bash

# --- Language Detection & Strings ---
LANG_CODE="en"
if [[ $LANG == zh* ]]; then
    LANG_CODE="zh"
fi

# --- Localized Strings ---
if [ "$LANG_CODE" = "zh" ]; then
    # --- Chinese Strings ---
    STR_STARTING_INSTALL="🚀 开始安装 macOS 后台服务管理器..."
    STR_CONFIG_NOT_FOUND="📝 未找到 'config.json'。正在从示例创建..."
    STR_CONFIG_CREATE_ERROR="❌ 错误: 创建 'config.json' 失败。请检查权限。"
    STR_CONFIG_CREATED="✅ 'config.json' 已创建。请根据您的需求进行修改。"
    STR_COMPILING_TRANSLATIONS="🌍 正在编译语言文件..."
    STR_COMPILING_FILE="   - 正在编译 %s 到 %s\n"
    STR_COMPILE_WARN="⚠️ 警告: 编译 %s 失败。工具可能会回退到英文显示。\n"
    STR_NO_LOCALE_DIR="ℹ️  未找到 locales 目录，跳过翻译编译。"
    STR_SETTING_PERMISSIONS="🔧 正在为 manager.py 设置执行权限..."
    STR_PERMISSIONS_ERROR="❌ 错误: 设置执行权限失败。请检查您的用户权限。"
    STR_CREATING_COMMAND="🔗 正在创建命令 '%s' 于 %s..."
    STR_SUDO_PROMPT_1="   此操作需要管理员权限才能写入系统目录。"
    STR_SUDO_PROMPT_2="   按 [Enter] 键继续，系统可能会提示您输入密码..."
    STR_INSTALL_DIR_WARN="⚠️ 警告: 目录 %s 不存在。正在尝试创建...\n"
    STR_INSTALL_DIR_ERROR="❌ 错误: 创建 %s 失败。请手动创建并确保它在您的 PATH 环境变量中。\n"
    STR_SYMLINK_ERROR="❌ 错误: 在 '%s' 中创建符号链接失败。\n   请确保您拥有管理员权限且目录可写。\n"
    STR_COMMAND_CREATED="✅ 命令 '%s' 创建成功。"
    STR_ASK_AUTO_START="🚀 是否要设置服务在登录时自动启动? (Y/n) "
    STR_SKIP_AUTO_START="ℹ️  已跳过自动启动设置。您可以通过 'launch_server start' 手动启动服务。"
    STR_CONFIGURING_AUTO_START="⚙️  正在为自动启动配置和安装 launchd 服务..."
    STR_UNLOADING_EXISTING="   正在卸载已存在的服务..."
    STR_WRITING_PLIST="📝 正在写入最终的 .plist 配置文件..."
    STR_PLIST_ERROR="❌ 错误: 写入最终的 .plist 文件失败。"
    STR_LOADING_SERVICE="🚀 正在使用 launchctl 加载服务..."
    STR_LOAD_ERROR="❌ 错误: 使用 launchctl 加载服务失败。\n   您可以尝试手动运行 'launchctl load %s' 进行调试。\n"
    STR_AUTO_START_CONFIGURED="✅ 自动启动服务已配置并加载。"
    STR_INSTALL_COMPLETE="✅ 安装完成!"
    STR_POST_INSTALL_MSG_1="您现在可以在终端的任何位置使用 'launch_server' 命令了。"
    STR_POST_INSTALL_MSG_2="请尝试运行 'launch_server status' 来检查您的服务状态。"
    STR_POST_INSTALL_MSG_3="如果您设置了自动启动，服务将在下次登录时自动运行。"
else
    # --- English Strings ---
    STR_STARTING_INSTALL="🚀 Starting installation for macOS Background Service Manager..."
    STR_CONFIG_NOT_FOUND="📝 No 'config.json' found. Creating one from the example..."
    STR_CONFIG_CREATE_ERROR="❌ Error: Failed to create 'config.json'. Please check permissions."
    STR_CONFIG_CREATED="✅ 'config.json' created. Please review and edit it for your needs."
    STR_COMPILING_TRANSLATIONS="🌍 Compiling language files..."
    STR_COMPILING_FILE="   - Compiling %s to %s\n"
    STR_COMPILE_WARN="⚠️ Warning: Failed to compile %s. The tool might fall back to English.\n"
    STR_NO_LOCALE_DIR="ℹ️  No locales directory found, skipping translation compilation."
    STR_SETTING_PERMISSIONS="🔧 Setting execute permissions for manager.py..."
    STR_PERMISSIONS_ERROR="❌ Error: Failed to set execute permissions. Please check your user rights."
    STR_CREATING_COMMAND="🔗 Creating command '%s' in %s..."
    STR_SUDO_PROMPT_1="   This requires administrator privileges to write to a system directory."
    STR_SUDO_PROMPT_2="   Press [Enter] to continue and you may be prompted for your password..."
    STR_INSTALL_DIR_WARN="⚠️ Warning: %s does not exist. Attempting to create it...\n"
    STR_INSTALL_DIR_ERROR="❌ Error: Failed to create %s. Please create it manually and ensure it's in your PATH.\n"
    STR_SYMLINK_ERROR="❌ Error: Failed to create symlink in '%s'.\n   Please ensure you have administrator privileges and that the directory is writable.\n"
    STR_COMMAND_CREATED="✅ Command '%s' created successfully."
    STR_ASK_AUTO_START="🚀 Do you want to set up services to start automatically on login? (Y/n) "
    STR_SKIP_AUTO_START="ℹ️  Skipping auto-start setup. You can start services manually by running 'launch_server start'."
    STR_CONFIGURING_AUTO_START="⚙️  Configuring and installing launchd service for auto-start..."
    STR_UNLOADING_EXISTING="   unloading existing service..."
    STR_WRITING_PLIST="📝 Writing final .plist configuration..."
    STR_PLIST_ERROR="❌ Error: Failed to write the final .plist file."
    STR_LOADING_SERVICE="🚀 Loading service with launchctl..."
    STR_LOAD_ERROR="❌ Error: Failed to load the service with launchctl.\n   You can try running 'launchctl load %s' manually to debug.\n"
    STR_AUTO_START_CONFIGURED="✅ Auto-start service configured and loaded."
    STR_INSTALL_COMPLETE="✅ Installation complete!"
    STR_POST_INSTALL_MSG_1="You can now use the 'launch_server' command globally."
    STR_POST_INSTALL_MSG_2="Try running 'launch_server status' to check your services."
    STR_POST_INSTALL_MSG_3="If you enabled auto-start, services will automatically start on next login."
fi

# --- Helper Functions ---
function compile_translations() {
    echo "$STR_COMPILING_TRANSLATIONS"
    LOCALE_DIR="$SCRIPT_DIR/locales"
    if [ -d "$LOCALE_DIR" ]; then
        for po_file in $(find "$LOCALE_DIR" -name "*.po"); do
            mo_file="${po_file%.po}.mo"
            printf "$STR_COMPILING_FILE" "$po_file" "$mo_file"
            msgfmt -o "$mo_file" "$po_file"
            if [ $? -ne 0 ]; then
                printf "$STR_COMPILE_WARN" "$po_file"
            fi
        done
    else
        echo "$STR_NO_LOCALE_DIR"
    fi
}

# --- Main Logic ---
echo "$STR_STARTING_INSTALL"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PLIST_NAME="com.user.backgroundservices.plist"
SYMLINK_NAME="launch_server"
INSTALL_DIR="/usr/local/bin"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
MANAGER_SCRIPT_PATH="$SCRIPT_DIR/manager.py"
LOG_PATH="$SCRIPT_DIR/logs"
PLIST_TEMPLATE_PATH="$SCRIPT_DIR/$PLIST_NAME"
FINAL_PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
CONFIG_PATH="$SCRIPT_DIR/config.json"
EXAMPLE_CONFIG_PATH="$SCRIPT_DIR/example_config.json"

# 1. Create config.json from example if it doesn't exist
if [ ! -f "$CONFIG_PATH" ]; then
    echo "$STR_CONFIG_NOT_FOUND"
    cp "$EXAMPLE_CONFIG_PATH" "$CONFIG_PATH"
    if [ $? -ne 0 ]; then
        echo "$STR_CONFIG_CREATE_ERROR"
        exit 1
    fi
    echo "$STR_CONFIG_CREATED"
    echo
fi

# 2. Compile translations
compile_translations

# 3. Set execute permission for the manager script
echo "$STR_SETTING_PERMISSIONS"
chmod +x "$MANAGER_SCRIPT_PATH"
if [ $? -ne 0 ]; then
    echo "$STR_PERMISSIONS_ERROR"
    exit 1
fi

# 4. Create symlink in /usr/local/bin
printf "$STR_CREATING_COMMAND\n" "$SYMLINK_NAME" "$INSTALL_DIR"
echo "$STR_SUDO_PROMPT_1"
read -p "$STR_SUDO_PROMPT_2"

if [ ! -d "$INSTALL_DIR" ]; then
    printf "$STR_INSTALL_DIR_WARN" "$INSTALL_DIR"
    sudo mkdir -p "$INSTALL_DIR"
    if [ $? -ne 0 ]; then
        printf "$STR_INSTALL_DIR_ERROR" "$INSTALL_DIR"
        exit 1
    fi
fi

sudo ln -sf "$MANAGER_SCRIPT_PATH" "$INSTALL_DIR/$SYMLINK_NAME"
if [ $? -ne 0 ]; then
    printf "$STR_SYMLINK_ERROR" "$INSTALL_DIR"
    exit 1
fi
printf "$STR_COMMAND_CREATED\n" "$SYMLINK_NAME"

# 5. Ask user about auto-start
echo
read -p "$STR_ASK_AUTO_START" -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]
then
    echo
    echo "$STR_SKIP_AUTO_START"
else
    echo
    echo "$STR_CONFIGURING_AUTO_START"
    mkdir -p "$LAUNCH_AGENTS_DIR"

    if [ -f "$FINAL_PLIST_PATH" ]; then
        echo "$STR_UNLOADING_EXISTING"
        launchctl unload "$FINAL_PLIST_PATH" > /dev/null 2>&1
    fi

    echo "$STR_WRITING_PLIST"
    
    # Read log_directory from config.json to set launchd log path
    # NOTE: This is a simple parser. It won't handle complex JSON structures.
    LOG_DIR_RAW=$(grep '"log_directory"' "$CONFIG_PATH" | cut -d'"' -f 4)
    if [ -z "$LOG_DIR_RAW" ]; then
        echo "❌ Error: Could not read 'log_directory' from config.json."
        exit 1
    fi
    
    # Manually expand ~ since we are in a script
    LOG_DIR="${LOG_DIR_RAW/#\~/$HOME}"
    LAUNCHD_LOG_PATH="$LOG_DIR/launch_server/launchd_bootstrap.log"
    
    # Ensure the directory for the launchd log exists
    mkdir -p "$(dirname "$LAUNCHD_LOG_PATH")"

    sed -e "s|__MANAGER_SCRIPT_PATH__|$MANAGER_SCRIPT_PATH|g" \
        -e "s|__LAUNCHD_LOG_PATH__|$LAUNCHD_LOG_PATH|g" \
        "$PLIST_TEMPLATE_PATH" > "$FINAL_PLIST_PATH"

    if [ $? -ne 0 ]; then
        echo "$STR_PLIST_ERROR"
        exit 1
    fi

    echo "$STR_LOADING_SERVICE"
    launchctl load "$FINAL_PLIST_PATH"
    if [ $? -ne 0 ]; then
        printf "$STR_LOAD_ERROR" "$FINAL_PLIST_PATH"
        exit 1
    fi
    echo "$STR_AUTO_START_CONFIGURED"
fi

echo
echo "$STR_INSTALL_COMPLETE"
echo "--------------------------------------------------"
echo "$STR_POST_INSTALL_MSG_1"
echo "$STR_POST_INSTALL_MSG_2"
echo "$STR_POST_INSTALL_MSG_3"