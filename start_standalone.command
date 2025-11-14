#!/bin/bash
# macOS .command file - double-clickable launcher
# This file makes the script executable and runs it in Terminal

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Make the shell script executable if it isn't already
chmod +x start_standalone.sh

# Run the launcher script
./start_standalone.sh

# Keep Terminal open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    read -p "Press Enter to close this window..."
fi

