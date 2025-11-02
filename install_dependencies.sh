#!/bin/bash
# Install all dependencies needed for 75 plugins

echo "Installing Python dependencies for OptiFIRE plugins..."

# Core dependencies (already installed, but listing for completeness)
apt-get update -qq
apt-get install -y -qq python3-numpy python3-pandas python3-scipy python3-sklearn 2>&1 | grep -v "already"

# Additional dependencies for plugins
apt-get install -y -qq \
  python3-statsmodels \
  python3-matplotlib \
  python3-seaborn \
  2>&1 | grep -v "already"

# Pip-only dependencies (if pip is available, otherwise skip)
if command -v pip3 &> /dev/null; then
  pip3 install --quiet --no-warn-script-location \
    pykalman \
    pywavelets \
    antropy \
    dtaidistance \
    optuna \
    sentence-transformers \
    evidently \
    pandera \
    duckdb \
    APScheduler \
    fastapi-cache2 \
    2>&1 | grep -E "Successfully|already"
else
  echo "pip3 not available, skipping pip dependencies"
fi

echo "✓ Dependencies installation complete"
