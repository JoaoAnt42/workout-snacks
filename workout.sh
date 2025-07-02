#!/bin/bash

# Workout Snacks - Shell Script Runner
# This script activates the virtual environment and runs the workout CLI

# Change to the script's directory
cd "$(dirname "$0")"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found at .venv"
    echo "Please create a virtual environment first:"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if workout_cli.py exists
if [ ! -f "workout_cli.py" ]; then
    echo "❌ workout_cli.py not found in current directory"
    exit 1
fi

# Run the workout CLI with any passed arguments
python workout_cli.py "$@"

# Deactivate virtual environment
deactivate