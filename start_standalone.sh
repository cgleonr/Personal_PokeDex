#!/bin/bash
# macOS/Linux launcher script for Personal Pokédex Standalone Application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "  Personal Pokédex - Standalone App"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}ERROR: Python is not installed or not in PATH${NC}"
        echo "Please install Python 3.7 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Using Python: $PYTHON_VERSION"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import flask, webview" 2>/dev/null; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install required packages${NC}"
        exit 1
    fi
    echo ""
fi

# Start the standalone application
echo -e "${GREEN}Starting Pokédex standalone application...${NC}"
echo "A window will open automatically."
echo "Close the window to exit."
echo ""

$PYTHON_CMD pokedex_standalone.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Application failed to start${NC}"
    read -p "Press Enter to exit..."
fi

