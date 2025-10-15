#!/bin/bash

# --- Language Detection & Strings ---
LANG_CODE="en"
if [[ $LANG == zh* ]]; then
    LANG_CODE="zh"
fi

if [ "$LANG_CODE" = "zh" ]; then
    # --- Chinese Strings ---
    STR_STARTING_UNINSTALL="🗑️  开始卸载 macOS 后台服务管理器..."
    STR_STOPPING_SERVICE="🛑 正在停止并卸载 launchd 服务..."
    STR_REMOVING_PLIST="🗑️  正在移除 .plist 文件..."
    STR_PLIST_WARN="⚠️ 警告: 移除 .plist 文件失败。您可能需要手动删除:\n   %s\n"
    STR_SERVICE_NOT_FOUND="ℹ️  未找到 launchd 服务，跳过。"
    STR_REMOVING_COMMAND="🔗 正在从 %s 移除命令 '%s'..."
    STR_SUDO_PROMPT_1="   此操作需要管理员权限才能写入系统目录。"
    STR_SUDO_PROMPT_2="   按 [Enter] 键继续，系统可能会提示您输入密码..."
    STR_SYMLINK_ERROR="❌ 错误: 移除符号链接失败。\n   请确保您拥有管理员权限或手动删除:\n   %s\n"
    STR_COMMAND_REMOVED="✅ 命令 '%s' 移除成功。"
    STR_COMMAND_NOT_FOUND="ℹ️  未找到命令 '%s'，跳过。"
    STR_UNINSTALL_COMPLETE="✅ 卸载完成!"
else
    # --- English Strings ---
    STR_STARTING_UNINSTALL="🗑️  Starting uninstallation for macOS Background Service Manager..."
    STR_STOPPING_SERVICE="🛑 Stopping and unloading launchd service..."
    STR_REMOVING_PLIST="🗑️  Removing .plist file..."
    STR_PLIST_WARN="⚠️ Warning: Failed to remove .plist file. You may need to remove it manually:\n   %s\n"
    STR_SERVICE_NOT_FOUND="ℹ️  launchd service not found, skipping."
    STR_REMOVING_COMMAND="🔗 Removing command '%s' from %s..."
    STR_SUDO_PROMPT_1="   This requires administrator privileges to write to a system directory."
    STR_SUDO_PROMPT_2="   Press [Enter] to continue and you may be prompted for your password..."
    STR_SYMLINK_ERROR="❌ Error: Failed to remove symlink.\n   Please ensure you have sudo privileges or remove it manually:\n   %s\n"
    STR_COMMAND_REMOVED="✅ Command '%s' removed successfully."
    STR_COMMAND_NOT_FOUND="ℹ️  Command '%s' not found, skipping."
    STR_UNINSTALL_COMPLETE="✅ Uninstallation complete!"
fi

# --- Main Logic ---
echo "$STR_STARTING_UNINSTALL"

PLIST_NAME="com.user.backgroundservices.plist"
SYMLINK_NAME="launch_server"
INSTALL_DIR="/usr/local/bin"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
FINAL_PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
SYMLINK_PATH="$INSTALL_DIR/$SYMLINK_NAME"

# 1. Unload the launchd service
if [ -f "$FINAL_PLIST_PATH" ]; then
    echo "$STR_STOPPING_SERVICE"
    launchctl unload "$FINAL_PLIST_PATH" > /dev/null 2>&1
    
    echo "$STR_REMOVING_PLIST"
    rm -f "$FINAL_PLIST_PATH"
    if [ $? -ne 0 ]; then
        printf "$STR_PLIST_WARN" "$FINAL_PLIST_PATH"
    fi
else
    echo "$STR_SERVICE_NOT_FOUND"
fi

# 2. Remove the symlink
if [ -L "$SYMLINK_PATH" ]; then
    printf "$STR_REMOVING_COMMAND\n" "$SYMLINK_NAME" "$INSTALL_DIR"
    echo "$STR_SUDO_PROMPT_1"
    read -p "$STR_SUDO_PROMPT_2"
    sudo rm -f "$SYMLINK_PATH"
    if [ $? -ne 0 ]; then
        printf "$STR_SYMLINK_ERROR" "$SYMLINK_PATH"
        exit 1
    fi
    printf "$STR_COMMAND_REMOVED\n" "$SYMLINK_NAME"
else
    printf "$STR_COMMAND_NOT_FOUND\n" "$SYMLINK_NAME"
fi

echo "$STR_UNINSTALL_COMPLETE"