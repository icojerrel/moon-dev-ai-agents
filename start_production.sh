#!/bin/bash
# Moon Dev Production Startup Script
# ===================================
# Safely starts the trading system with all safety checks

set -e  # Exit on error

echo ""
echo "================================================================================"
echo "🌙 Moon Dev AI Trading System - Production Startup"
echo "================================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if emergency stop is active
if [ -f "src/EMERGENCY_STOP_ACTIVE" ]; then
    echo -e "${RED}❌ EMERGENCY STOP IS ACTIVE${NC}"
    echo ""
    echo "Cannot start system while emergency stop is active."
    echo "To restart:"
    echo "  1. Remove: src/EMERGENCY_STOP_ACTIVE"
    echo "  2. Run pre-flight check: python src/scripts/pre_flight_check.py"
    echo "  3. Then re-run this script"
    echo ""
    exit 1
fi

# Step 1: Environment check
echo -e "${CYAN}[1/6] Checking environment...${NC}"
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda not found${NC}"
    echo "Please install Miniconda or Anaconda"
    exit 1
fi

# Check if tflow environment exists
if ! conda env list | grep -q "^tflow "; then
    echo -e "${RED}❌ Conda environment 'tflow' not found${NC}"
    echo "Create it with: conda create -n tflow python=3.11"
    exit 1
fi

echo -e "${GREEN}  ✅ Environment ready${NC}"

# Step 2: Activate conda environment
echo ""
echo -e "${CYAN}[2/6] Activating conda environment...${NC}"
eval "$(conda shell.bash hook)"
conda activate tflow
echo -e "${GREEN}  ✅ Environment activated: tflow${NC}"

# Step 3: Safety checks
echo ""
echo -e "${CYAN}[3/6] Running pre-flight safety checks...${NC}"
echo ""

python src/scripts/pre_flight_check.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ Safety check failed. Cannot start production.${NC}"
    echo "Fix all issues and re-run this script."
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Safety checks passed${NC}"

# Step 4: Create logs directory
echo ""
echo -e "${CYAN}[4/6] Setting up logging...${NC}"
mkdir -p logs
mkdir -p src/data/orchestrator
mkdir -p src/data/deepseek_director
echo -e "${GREEN}  ✅ Log directories ready${NC}"

# Step 5: Final confirmation
echo ""
echo -e "${YELLOW}[5/6] Final confirmation before starting production...${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT WARNINGS:${NC}"
echo "  • This is an EXPERIMENTAL AI trading system"
echo "  • There is SUBSTANTIAL RISK of loss"
echo "  • Only use capital you can afford to LOSE"
echo "  • Monitor the system CONTINUOUSLY for first 24-48 hours"
echo "  • Have emergency stop ready: python src/scripts/emergency_stop.py"
echo ""

read -p "Do you understand the risks and want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo ""
    echo -e "${YELLOW}❌ Startup cancelled by user${NC}"
    echo ""
    exit 0
fi

# Step 6: Start system
echo ""
echo -e "${CYAN}[6/6] Starting trading system...${NC}"
echo ""
echo "================================================================================"
echo -e "${GREEN}🚀 PRODUCTION SYSTEM STARTING${NC}"
echo "================================================================================"
echo ""
echo "System will start in 5 seconds..."
echo "Press Ctrl+C now to cancel"
echo ""

sleep 5

# Create timestamped log file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/production_$TIMESTAMP.log"

echo "📝 Logging to: $LOG_FILE"
echo ""
echo "To monitor in real-time:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To stop system:"
echo "  Press Ctrl+C (graceful shutdown)"
echo "  OR run: python src/scripts/emergency_stop.py (emergency halt)"
echo ""
echo "================================================================================"
echo ""

# Start main system with logging
python src/main.py 2>&1 | tee "$LOG_FILE"

# Cleanup on exit
EXIT_CODE=$?

echo ""
echo "================================================================================"
echo "System shutdown"
echo "================================================================================"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ System exited gracefully${NC}"
else
    echo -e "${YELLOW}⚠️  System exited with code: $EXIT_CODE${NC}"
    echo "Review logs for details: $LOG_FILE"
fi

echo ""
echo "Final state exported to: src/data/orchestrator/"
echo "Logs saved to: $LOG_FILE"
echo ""
echo "To restart system:"
echo "  1. Review logs and fix any issues"
echo "  2. Run: ./start_production.sh"
echo ""
