@echo off
REM 🌙 Moon Dev Complete Trading System (with MT5 + other agents)
REM Runs main.py orchestrator with MT5 agent enabled

echo.
echo ============================================================
echo 🌙 Moon Dev AI Trading System (Full Orchestrator + MT5)
echo ============================================================
echo.

REM Activate conda if available
conda --version >nul 2>&1
if not errorlevel 1 (
    echo Activating conda environment: tflow
    call conda activate tflow
)

REM Check .env
if not exist .env (
    echo ❌ .env file not found! Create from .env_example first.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🚀 Starting Full Trading System
echo ============================================================
echo.
echo Active agents will be shown on startup...
echo.
echo Make sure MetaTrader 5 is RUNNING before starting!
echo.
pause

REM Run main orchestrator
python src/main.py

pause
