#!/bin/bash
# ============================================================================
# TPU Setup Script
# Run this after cloning the repository on TPU
# Usage: ./setup_tpu.sh
# ============================================================================

set -e  # Exit on any error

echo "=========================================="
echo "Setting up MLE-Bench environment on TPU"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Create virtual environment
echo ""
echo "[1/5] Creating virtual environment..."
if [ -d "aide_env" ]; then
    echo "  aide_env already exists, skipping creation"
else
    python3 -m venv aide_env
    echo "  Created aide_env"
fi

# 2. Activate virtual environment
echo ""
echo "[2/5] Activating virtual environment..."
source aide_env/bin/activate
echo "  Activated: $(which python)"

# 3. Upgrade pip
echo ""
echo "[3/5] Upgrading pip..."
pip install --upgrade pip

# 4. Install mlebench in editable mode
echo ""
echo "[4/5] Installing mlebench..."
cd mle-bench
pip install -e .
cd ..

# 5. Install additional dependencies
echo ""
echo "[5/5] Installing additional dependencies..."
pip install kaggle

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the environment:"
echo "   source aide_env/bin/activate"
echo ""
echo "2. Set up your API keys:"
echo "   export OPENAI_API_KEY='your-key-here'"
echo "   # or for Anthropic:"
echo "   export ANTHROPIC_API_KEY='your-key-here'"
echo ""
echo "3. Set up Kaggle credentials:"
echo "   mkdir -p ~/.kaggle"
echo "   echo '{\"username\":\"YOUR_USERNAME\",\"key\":\"YOUR_KEY\"}' > ~/.kaggle/kaggle.json"
echo "   chmod 600 ~/.kaggle/kaggle.json"
echo ""
echo "4. Prepare competition data:"
echo "   cd mle-bench"
echo "   mlebench prepare -c playground-series-s5e8 --skip-verification"
echo ""
echo "5. Run experiments:"
echo "   python run_agent.py --agent-id aide --competition-set experiments/splits/your_competitions.txt"
echo ""
