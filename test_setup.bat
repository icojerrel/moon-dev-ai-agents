@echo off
REM 🌙 Moon Dev's Setup Tester for Windows
REM Run this to verify everything is configured correctly

echo.
echo ============================================================
echo 🌙 Moon Dev MT5 Setup Tester
echo ============================================================
echo.
echo This will test your complete setup WITHOUT actually trading.
echo.
pause

REM Activate conda if available
conda --version >nul 2>&1
if not errorlevel 1 (
    echo Activating conda environment: tflow
    call conda activate tflow
)

REM Run the test script
python test_mt5_setup.py

echo.
echo ============================================================
echo Test complete! Check results above.
echo ============================================================
echo.
pause
