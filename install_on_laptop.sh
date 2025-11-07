#!/bin/bash
# Install OptiFIRE on laptop after migration

set -e

echo "=========================================="
echo "OptiFIRE Laptop Installation"
echo "=========================================="

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    OS="unknown"
fi

echo "Detected OS: $OS"

# Check Python version
echo ""
echo "Checking Python version..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PY_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PY_VERSION < 3.11" | bc) -eq 1 ]]; then
        echo "⚠ WARNING: Python 3.11+ recommended (you have $PY_VERSION)"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "✗ Python 3 not found!"
    echo ""
    if [[ "$OS" == "linux" ]]; then
        echo "Install with: sudo apt install python3.11 python3.11-venv"
    elif [[ "$OS" == "macos" ]]; then
        echo "Install with: brew install python@3.11"
    fi
    exit 1
fi

echo "✓ Using: $PYTHON_CMD ($(${PYTHON_CMD} --version))"

# Extract archive if in current directory
if [ -f "optifire_migration.tar.gz" ]; then
    echo ""
    echo "Extracting archive..."
    tar -xzf optifire_migration.tar.gz
    cd optifire_export
    echo "✓ Extracted"
fi

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    echo "✗ Error: main.py or requirements.txt not found!"
    echo "Please run this script from the optifire directory."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
rm -rf venv
$PYTHON_CMD -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies (this may take 5-10 minutes)..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Create data directory
echo ""
echo "Setting up directories..."
mkdir -p data/backups
mkdir -p logs
mkdir -p optifire/api/static
mkdir -p optifire/api/templates
echo "✓ Directories created"

# Check secrets.env
echo ""
if [ -f "secrets.env" ]; then
    echo "✓ secrets.env found (API keys present)"
    # Verify Alpaca keys
    if grep -q "ALPACA_API_KEY=" secrets.env && grep -q "ALPACA_API_SECRET=" secrets.env; then
        echo "✓ Alpaca API keys present"
    else
        echo "⚠ WARNING: Alpaca API keys missing in secrets.env!"
    fi
else
    echo "⚠ WARNING: secrets.env not found!"
    echo "Creating template..."
    cat > secrets.env <<EOF
# Alpaca API (Paper or Live)
ALPACA_API_KEY=YOUR_KEY_HERE
ALPACA_API_SECRET=YOUR_SECRET_HERE
ALPACA_PAPER=true

# Auto-Trading
AUTO_TRADING_ENABLED=true

# Authentication
JWT_SECRET=$(openssl rand -hex 16)
ADMIN_USER=admin
ADMIN_PASS=YOUR_PASSWORD_HERE

# OpenAI (optional)
OPENAI_API_KEY=YOUR_OPENAI_KEY_HERE
EOF
    echo "✓ Template created: secrets.env"
    echo "⚠ IMPORTANT: Edit secrets.env and add your API keys!"
fi

# Check database
echo ""
if [ -f "data/optifire.db" ]; then
    DB_SIZE=$(du -h data/optifire.db | cut -f1)
    echo "✓ Database migrated (size: $DB_SIZE)"
else
    echo "⚠ No database found (will create fresh on first run)"
fi

# Test installation
echo ""
echo "Testing installation..."
python -c "
import sys
import fastapi
import uvicorn
import pandas
import numpy
print('✓ All core dependencies working')
sys.exit(0)
" || {
    echo "✗ Dependency test failed!"
    exit 1
}

# Create startup script
echo ""
echo "Creating startup scripts..."
cat > start.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOF
chmod +x start.sh

cat > restart.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
pkill -f "python main.py" || true
sleep 2
bash start.sh
EOF
chmod +x restart.sh

echo "✓ Startup scripts created (start.sh, restart.sh)"

# OS-specific instructions
echo ""
echo "=========================================="
echo "✓ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit secrets.env (if needed):"
echo "   nano secrets.env"
echo ""
echo "2. Start OptiFIRE:"
echo "   bash start.sh"
echo ""
echo "3. Open dashboard:"
echo "   http://localhost:8000"
echo ""
echo "4. Setup auto-start (optional):"
if [[ "$OS" == "linux" ]]; then
    echo "   bash setup_laptop_service.sh"
elif [[ "$OS" == "macos" ]]; then
    echo "   bash setup_laptop_service.sh"
elif [[ "$OS" == "windows" ]]; then
    echo "   Use Task Scheduler (see MIGRATION_GUIDE.md)"
fi
echo ""
echo "5. Prevent laptop sleep:"
if [[ "$OS" == "linux" ]]; then
    echo "   Settings → Power → Never sleep"
elif [[ "$OS" == "macos" ]]; then
    echo "   System Preferences → Energy Saver → Never sleep"
elif [[ "$OS" == "windows" ]]; then
    echo "   Settings → System → Power & Sleep → Never"
fi
echo ""
echo "For troubleshooting, see: MIGRATION_GUIDE.md"
echo "=========================================="
