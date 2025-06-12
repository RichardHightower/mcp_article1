#!/bin/bash
# MCP Server Runner for Claude Desktop

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Activate the virtual environment and run the server
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    python src/main.py
else
    # Fallback to poetry if venv doesn't exist
    poetry run python src/main.py
fi