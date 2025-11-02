#!/bin/bash
# OptiFIRE Run Script

cd "$(dirname "$0")"

echo "=============================="
echo "OptiFIRE Startup"
echo "=============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q -U pip
pip install -q -r requirements.txt

# Check if secrets.env exists
if [ ! -f "secrets.env" ]; then
    echo ""
    echo "WARNING: secrets.env not found!"
    echo "Please create secrets.env with your API keys."
    echo "See secrets.template.env for reference."
    echo ""
    exit 1
fi

# Run the application
echo ""
echo "Starting OptiFIRE..."
echo "Dashboard will be available at: http://localhost:8000"
echo ""

python main.py
