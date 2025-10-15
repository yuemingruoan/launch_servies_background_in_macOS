#!/bin/bash

# --- Configuration ---
PLIST_NAME="com.user.backgroundservices.plist"
SYMLINK_NAME="launch_server"
INSTALL_DIR="/usr/local/bin"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

# --- Helper Functions ---
function compile_translations() {
    echo "🌍 Compiling language files..."
    LOCALE_DIR="$SCRIPT_DIR/locales"
    if [ -d "$LOCALE_DIR" ]; then
        for po_file in $(find "$LOCALE_DIR" -name "*.po"); do
            mo_file="${po_file%.po}.mo"
            echo "   - Compiling $po_file to $mo_file"
            msgfmt -o "$mo_file" "$po_file"
            if [ $? -ne 0 ]; then
                echo "⚠️ Warning: Failed to compile $po_file. The tool might fall back to English."
            fi
        done
    else
        echo "ℹ️  No locales directory found, skipping translation compilation."
    fi
}

# --- Main Logic ---
echo "🚀 Starting installation for macOS Background Service Manager..."

# Get the absolute path of the directory containing this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MANAGER_SCRIPT_PATH="$SCRIPT_DIR/manager.py"
LOG_PATH="$SCRIPT_DIR/logs"
PLIST_TEMPLATE_PATH="$SCRIPT_DIR/$PLIST_NAME"
FINAL_PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

# 1. Compile translations
compile_translations

# 2. Set execute permission for the manager script
echo "🔧 Setting execute permissions for manager.py..."
chmod +x "$MANAGER_SCRIPT_PATH"
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to set execute permissions. Please check your user rights."
    exit 1
fi

# 2. Create symlink in /usr/local/bin
echo "🔗 Creating command '$SYMLINK_NAME' in $INSTALL_DIR..."
# Check if /usr/local/bin exists and is writable
if [ ! -d "$INSTALL_DIR" ]; then
    echo "⚠️ Warning: $INSTALL_DIR does not exist. Attempting to create it..."
    sudo mkdir -p "$INSTALL_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create $INSTALL_DIR. Please create it manually and ensure it's in your PATH."
        exit 1
    fi
fi

sudo ln -sf "$MANAGER_SCRIPT_PATH" "$INSTALL_DIR/$SYMLINK_NAME"
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create symlink. You may be prompted for your password."
    echo "Please ensure you have sudo privileges."
    exit 1
fi
echo "✅ Command '$SYMLINK_NAME' created successfully."

# 3. Ask user about auto-start
echo
read -p "🚀 Do you want to set up services to start automatically on login? (Y/n) " -n 1 -r
echo # Move to a new line
if [[ $REPLY =~ ^[Nn]$ ]]
then
    echo
    echo "ℹ️  Skipping auto-start setup. You can start services manually by running 'launch_server start'."
else
    # Configure and install the launchd service
    echo
    echo "⚙️  Configuring and installing launchd service for auto-start..."
    # Ensure LaunchAgents directory exists
    mkdir -p "$LAUNCH_AGENTS_DIR"

# Unload any existing service with the same name first
if [ -f "$FINAL_PLIST_PATH" ]; then
    echo " unloading existing service..."
    launchctl unload "$FINAL_PLIST_PATH" > /dev/null 2>&1
fi

# Replace placeholders in the plist template
echo "📝 Writing final .plist configuration..."
sed -e "s|__MANAGER_SCRIPT_PATH__|$MANAGER_SCRIPT_PATH|g" \
    -e "s|__LOG_PATH__|$LOG_PATH|g" \
    "$PLIST_TEMPLATE_PATH" > "$FINAL_PLIST_PATH"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to write the final .plist file."
    exit 1
fi

# 4. Load the new service
    echo "🚀 Loading service with launchctl..."
    launchctl load "$FINAL_PLIST_PATH"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to load the service with launchctl."
        echo "You can try running 'launchctl load $FINAL_PLIST_PATH' manually to debug."
        exit 1
    fi
    echo "✅ Auto-start service configured and loaded."
fi

echo "✅ Installation complete!"
echo "--------------------------------------------------"
echo "You can now use the 'launch_server' command globally."
echo "Try running 'launch_server status' to check your services."
echo "Services will automatically start on next login."