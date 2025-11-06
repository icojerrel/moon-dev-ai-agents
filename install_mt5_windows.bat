@echo off
REM 🌙 Moon Dev's MT5 Setup Script for Windows
REM Run this on your Windows machine to install MT5 dependencies

echo.
echo ============================================================
echo 🌙 Moon Dev's MT5 Trading Bot Setup (Windows)
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if conda is available
conda --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Conda not found. Using pip for installation.
    set USE_CONDA=0
) else (
    echo ✅ Conda found
    conda --version
    set USE_CONDA=1
)

echo.
echo ============================================================
echo 📦 Installing MetaTrader5 Library
echo ============================================================
echo.

if %USE_CONDA%==1 (
    echo Using conda environment: tflow
    call conda activate tflow
    if errorlevel 1 (
        echo ⚠️ Failed to activate tflow environment
        echo Creating new environment...
        call conda create -n tflow python=3.11 -y
        call conda activate tflow
    )
)

REM Install MetaTrader5
echo Installing MetaTrader5...
pip install MetaTrader5
if errorlevel 1 (
    echo ❌ Failed to install MetaTrader5
    pause
    exit /b 1
)

echo ✅ MetaTrader5 installed successfully
echo.

REM Install other dependencies
echo ============================================================
echo 📦 Installing other dependencies
echo ============================================================
echo.

pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️ Some dependencies failed to install, continuing anyway...
)

echo.
echo ============================================================
echo ✅ Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo.
echo 1. Make sure MetaTrader 5 is installed on your system
echo    Download from: https://www.metatrader5.com/en/download
echo.
echo 2. Create a demo account in MT5:
echo    File -^> Open an Account -^> MetaQuotes-Demo
echo.
echo 3. Configure your .env file with MT5 credentials:
echo    MT5_LOGIN=your_account_number
echo    MT5_PASSWORD=your_password
echo    MT5_SERVER=MetaQuotes-Demo
echo.
echo 4. Test the connection:
echo    python src/agents/mt5_utils.py
echo.
echo 5. Run the trading bot:
echo    python src/agents/mt5_trading_agent.py
echo.
echo 📖 Full setup guide: src/agents/MT5_SETUP_GUIDE.md
echo.
echo 🌙 Built by Moon Dev - Happy Trading!
echo.
pause
