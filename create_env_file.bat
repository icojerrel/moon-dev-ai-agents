@echo off
REM 🌙 Moon Dev - Create .env file with your MT5 credentials
REM This script creates a .env file with your account details

echo.
echo ============================================================
echo 🌙 Creating .env file for MT5 Trading Bot
echo ============================================================
echo.

REM Check if .env already exists
if exist .env (
    echo ⚠️ .env file already exists!
    echo.
    set /p OVERWRITE="Overwrite existing .env? (y/n): "
    if /i not "%OVERWRITE%"=="y" (
        echo Cancelled. Keeping existing .env file.
        pause
        exit /b 0
    )
)

REM Create .env file
echo Creating .env file...
echo.

(
echo # 🌙 Moon Dev MT5 Trading Bot Configuration
echo # Generated automatically
echo.
echo # ============================================================
echo # MetaTrader 5 Account
echo # ============================================================
echo MT5_LOGIN=5041139909
echo MT5_PASSWORD=m44!YU6XYGXmMjf
echo MT5_SERVER=MetaQuotes-Demo
echo MT5_PATH=C:/Program Files/MetaTrader 5/terminal64.exe
echo.
echo # Alternative password if above doesn't work:
echo # MT5_PASSWORD=qjQYWTzj
echo.
echo # ============================================================
echo # AI Model API Keys ^(Fill in at least ONE^)
echo # ============================================================
echo.
echo # OpenRouter ^(RECOMMENDED - One API for all models^)
echo OPENROUTER_API_KEY=sk-or-v1-your_key_here
echo.
echo # xAI Grok ^(Fast and cheap^)
echo # GROK_API_KEY=xai-your_key_here
echo.
echo # Groq ^(Free tier available^)
echo # GROQ_API_KEY=gsk_your_key_here
echo.
echo # OpenAI GPT-4
echo # OPENAI_KEY=sk-your_key_here
echo.
echo # Anthropic Claude
echo # ANTHROPIC_KEY=sk-ant-your_key_here
echo.
echo # DeepSeek
echo # DEEPSEEK_KEY=your_key_here
echo.
echo # ============================================================
echo # Optional: Solana Trading ^(not needed for MT5 only^)
echo # ============================================================
echo # BIRDEYE_API_KEY=your_key
echo # SOLANA_PRIVATE_KEY=your_key
echo # RPC_ENDPOINT=your_helius_rpc
) > .env

echo ✅ .env file created successfully!
echo.
echo ============================================================
echo ⚠️ IMPORTANT - NEXT STEPS
echo ============================================================
echo.
echo 1. Open .env file in Notepad:
echo    notepad .env
echo.
echo 2. Add your AI API key - replace this line:
echo    GROK_API_KEY=xai-your_key_here
echo.
echo 3. With your actual key:
echo    GROK_API_KEY=xai-abc123youractualkey
echo.
echo 4. Save and close Notepad
echo.
echo 5. Test connection:
echo    python src/agents/mt5_utils.py
echo.
echo 6. Start trading:
echo    start_mt5_trading.bat
echo.
echo ============================================================
echo.

REM Ask to open .env in notepad
set /p EDIT="Open .env in Notepad now? (y/n): "
if /i "%EDIT%"=="y" (
    notepad .env
)

echo.
echo Ready to configure your AI key!
echo.
pause
