#!/bin/bash

# --- Configuration ---
PLIST_NAME="com.user.backgroundservices.plist"
SYMLINK_NAME="launch_server"
INSTALL_DIR="/usr/local/bin"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

# --- Main Logic ---
echo "🗑️  Starting uninstallation for macOS Background Service Manager..."

FINAL_PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
SYMLINK_PATH="$INSTALL_DIR/$SYMLINK_NAME"

# 1. Unload the launchd service
if [ -f "$FINAL_PLIST_PATH" ]; then
    echo "🛑 Stopping and unloading launchd service..."
    launchctl unload "$FINAL_PLIST_PATH" > /dev/null 2>&1
    
    # 2. Remove the .plist file
    echo "🗑️  Removing .plist file..."
    rm -f "$FINAL_PLIST_PATH"
    if [ $? -ne 0 ]; then
        echo "⚠️ Warning: Failed to remove .plist file. You may need to remove it manually:"
        echo "   $FINAL_PLIST_PATH"
    fi
else
    echo "ℹ️  launchd service not found, skipping."
fi

# 3. Remove the symlink
if [ -L "$SYMLINK_PATH" ]; then
    echo "🔗 Removing command '$SYMLINK_NAME' from $INSTALL_DIR..."
    echo "   This requires administrator privileges to write to a system directory."
    read -p "   Press [Enter] to continue and you may be prompted for your password..."
    sudo rm -f "$SYMLINK_PATH"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to remove symlink from '$INSTALL_DIR'."
        echo "   Please ensure you have administrator privileges or remove it manually:"
        echo "   $SYMLINK_PATH"
        exit 1
    fi
    echo "✅ Command '$SYMLINK_NAME' removed successfully."
else
    echo "ℹ️  Command '$SYMLINK_NAME' not found, skipping."
fi

echo "✅ Uninstallation complete!"