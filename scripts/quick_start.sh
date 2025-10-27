#!/usr/bin/env bash
# 🌙 Moon Dev AI Trading System - Quick Start Script
# One-command setup and deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}🌙 Moon Dev AI Trading System Setup${NC}"
echo -e "${CYAN}============================================${NC}\n"

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Check Python version
print_info "Checking Python version..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        print_status 0 "Python $PYTHON_VERSION (>= 3.10 required)"
    else
        print_status 1 "Python $PYTHON_VERSION found, but >= 3.10 required"
    fi
else
    print_status 1 "Python 3 not found. Please install Python 3.10+"
fi

# Step 2: Check for conda/venv
print_info "Checking Python environment..."
if command_exists conda; then
    print_status 0 "Conda found"

    # Check if tflow environment exists
    if conda env list | grep -q "^tflow "; then
        print_info "Using existing 'tflow' environment"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate tflow
    else
        print_warning "'tflow' environment not found"
        read -p "Create new conda environment 'moon-trading'? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            conda create -n moon-trading python=3.10 -y
            conda activate moon-trading
            print_status 0 "Created and activated 'moon-trading' environment"
        fi
    fi
else
    print_warning "Conda not found - using system Python"
fi

# Step 3: Install Python dependencies
print_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_status $? "Python dependencies installed"
else
    print_status 1 "requirements.txt not found"
fi

# Step 4: Check for .env file
print_info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found"

    if [ -f ".env_example" ]; then
        cp .env_example .env
        print_info "Created .env from .env_example"
        print_warning "Please edit .env with your API keys!"
        echo -e "${YELLOW}Required API keys:${NC}"
        echo "  - ANTHROPIC_KEY (Claude)"
        echo "  - BIRDEYE_API_KEY (Solana data)"
        echo "  - SOLANA_PRIVATE_KEY (Trading wallet)"
        echo ""
        read -p "Press Enter to open .env in nano editor (or Ctrl+C to exit)..."
        nano .env || vi .env || echo "Please edit .env manually"
    else
        print_status 1 ".env_example not found"
    fi
else
    print_status 0 ".env file exists"
fi

# Step 5: Validate API keys
print_info "Validating API keys..."
source .env

MISSING_KEYS=0

if [ -z "$ANTHROPIC_KEY" ]; then
    print_warning "ANTHROPIC_KEY not set"
    MISSING_KEYS=1
else
    print_status 0 "ANTHROPIC_KEY configured (${ANTHROPIC_KEY:0:10}...)"
fi

if [ -z "$BIRDEYE_API_KEY" ]; then
    print_warning "BIRDEYE_API_KEY not set (optional but recommended)"
else
    print_status 0 "BIRDEYE_API_KEY configured"
fi

if [ -z "$SOLANA_PRIVATE_KEY" ]; then
    print_warning "SOLANA_PRIVATE_KEY not set (required for trading)"
    MISSING_KEYS=1
else
    print_status 0 "SOLANA_PRIVATE_KEY configured"
fi

if [ $MISSING_KEYS -eq 1 ]; then
    print_warning "Some required API keys are missing"
    echo "You can still run in demo mode, but trading will not work."
fi

# Step 6: Check for Rust (optional)
print_info "Checking for Rust (optional for maximum performance)..."
if command_exists rustc; then
    RUST_VERSION=$(rustc --version | cut -d ' ' -f 2)
    print_status 0 "Rust $RUST_VERSION installed"

    # Ask if user wants to build Rust core
    read -p "Build Rust core for 450x performance boost? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Building Rust core..."

        # Install maturin if needed
        if ! command_exists maturin; then
            pip install maturin
        fi

        cd rust_core
        maturin develop --release
        cd ..

        # Test Rust import
        python3 -c "import moon_rust_core; print('Rust version:', moon_rust_core.version())" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_status 0 "Rust core built and working!"
        else
            print_warning "Rust core build completed but import failed"
        fi
    fi
else
    print_warning "Rust not found - system will use Python fallback (slower)"
    echo "Install Rust from: https://rustup.rs"
fi

# Step 7: Create necessary directories
print_info "Creating data directories..."
mkdir -p src/data/{trading_agent,risk_agent,sentiment_agent,swarm_agent}
mkdir -p logs
mkdir -p benchmarks
print_status 0 "Directories created"

# Step 8: Test imports
print_info "Testing Python imports..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from src.agents.async_orchestrator import AsyncOrchestrator
    print("✅ Async orchestrator import OK")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

try:
    from src.services.realtime_price_feed import RealtimePriceFeed
    print("✅ Real-time price feed import OK")
except ImportError as e:
    print(f"⚠️  Real-time feed not available: {e}")

try:
    from src.agents.swarm_agent import SwarmAgent
    print("✅ Swarm agent import OK")
except ImportError as e:
    print(f"⚠️  Swarm agent not available: {e}")
EOF

print_status $? "Import tests completed"

# Step 9: Configuration check
print_info "Checking configuration..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from src import config

print(f"✅ Monitored tokens: {getattr(config, 'MONITORED_TOKENS', ['SOL'])}")
print(f"✅ Max loss: ${getattr(config, 'MAX_LOSS_USD', 1000)}")
print(f"✅ Sleep interval: {getattr(config, 'SLEEP_BETWEEN_RUNS_MINUTES', 1)} min")
EOF

# Step 10: Run quick test
print_info "Running quick system test..."
python3 << 'EOF'
import sys
import asyncio
sys.path.insert(0, '.')

from src.nice_funcs import token_price

# Test price fetch
try:
    price = token_price('SOL')
    if price:
        print(f"✅ Price fetch test: SOL = ${price:.2f}")
    else:
        print("⚠️  Price fetch returned None (check API keys)")
except Exception as e:
    print(f"⚠️  Price fetch failed: {e}")
EOF

# Final summary
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${CYAN}============================================${NC}\n"

echo -e "${CYAN}Next steps:${NC}\n"
echo "1. Review configuration in src/config.py"
echo "2. Test the system:"
echo -e "   ${GREEN}python src/agents/async_orchestrator.py${NC}"
echo ""
echo "3. Run benchmarks:"
echo -e "   ${GREEN}python scripts/benchmark_performance.py${NC}"
echo ""
echo "4. Deploy to production:"
echo -e "   ${GREEN}See DEPLOYMENT_GUIDE.md${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "  - Always test with small amounts first"
echo "  - Monitor the system closely"
echo "  - Review logs regularly"
echo ""
echo -e "${CYAN}Documentation:${NC}"
echo "  - DEPLOYMENT_GUIDE.md - Production deployment"
echo "  - HYBRID_ARCHITECTURE_PLAN.md - Architecture overview"
echo "  - IMPLEMENTATION_SUMMARY.md - Complete feature list"
echo ""
echo -e "${GREEN}Happy trading! 🚀${NC}\n"
