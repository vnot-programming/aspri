#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "🐍 Setting up Python Virtual Environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed on this system." >&2
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📁 Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip and install requirements if requirements.txt exists
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "📦 Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Run the python helper script with all passed arguments
echo "🚀 Running deployment script..."
python3 "$SCRIPT_DIR/deploy_helper.py" "$@"

# Deactivate virtual environment
deactivate
echo "✨ Finished!"
