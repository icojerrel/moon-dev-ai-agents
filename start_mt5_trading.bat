@echo off
REM 🌙 Moon Dev MT5 Trading Bot Startup Script
REM Quick start script for Windows

echo.
echo ============================================================
echo 🌙 Moon Dev MT5 AI Trading Bot
echo ============================================================
echo.

REM Check if conda is available
conda --version >nul 2>&1
if errorlevel 1 (
    echo Using system Python...
    set USE_CONDA=0
) else (
    echo Using conda environment: tflow
    call conda activate tflow
    set USE_CONDA=1
)

echo.
echo ============================================================
echo 🔍 Pre-flight Checks
echo ============================================================
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo ❌ Python not found!
    pause
    exit /b 1
)

REM Check MT5 library
python -c "import MetaTrader5 as mt5; print(f'✅ MT5 library v{mt5.__version__}')" 2>nul
if errorlevel 1 (
    echo ⚠️ MetaTrader5 library not found!
    echo Installing...
    pip install MetaTrader5
)

REM Check if .env exists
if not exist .env (
    echo.
    echo ⚠️ WARNING: .env file not found!
    echo Please create .env from .env_example and add your MT5 credentials:
    echo.
    echo MT5_LOGIN=your_account_number
    echo MT5_PASSWORD=your_password
    echo MT5_SERVER=MetaQuotes-Demo
    echo GROK_API_KEY=xai-your_key
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🚀 Starting MT5 Trading Bot
echo ============================================================
echo.
echo Make sure:
echo   ✅ MetaTrader 5 terminal is RUNNING
echo   ✅ You are logged into your demo account
echo   ✅ Market Watch shows symbols (Ctrl+M)
echo.
echo Press any key to start trading...
pause >nul

REM Start the bot
python src/agents/mt5_trading_agent.py

echo.
echo ============================================================
echo 👋 Trading Bot Stopped
echo ============================================================
echo.
pause
