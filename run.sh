#!/bin/bash
echo "🎮 Starting Bolamiga Game Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
echo "Starting game server on port 5030..."
python app.py