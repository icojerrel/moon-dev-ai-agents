# System Validation Skill

You are a system validation expert for the Moon Dev AI Trading System. Your job is to perform comprehensive system validation before trading or deployment.

## Your Task

Execute a complete system validation to ensure all components are properly configured, connected, and ready for trading operations.

## Validation Checklist

### 1. File Structure Validation
Check that all critical files and directories exist:
- `src/config.py` - Main configuration
- `src/main.py` - Orchestrator
- `src/nice_funcs.py` - Trading utilities
- `src/agents/` - All agent files (48+)
- `src/models/model_factory.py` - LLM abstraction
- `src/strategies/` - Strategy directory
- `src/data/` - Data directories
- `requirements.txt` - Dependencies
- `.env` file (or `.env_example`)

### 2. Python Syntax Validation
Validate Python syntax for all critical files:
```bash
python -m py_compile src/config.py
python -m py_compile src/main.py
python -m py_compile src/nice_funcs.py
python -m py_compile src/models/model_factory.py
```

For each agent in `src/agents/`:
- Check Python syntax
- Look for common errors (missing imports, syntax issues)
- Count total lines (should be <800 per file)

### 3. Dependency Validation
Check if all required packages are installed:

**Critical Dependencies**:
- anthropic (Claude AI)
- openai (GPT models)
- requests (API calls)
- pandas (data handling)
- numpy (numerical operations)
- termcolor (colored output)
- python-dotenv (environment variables)

**Optional but Recommended**:
- groq (fast inference)
- backtesting (strategy testing)
- pandas_ta (technical indicators)
- talib (alternative indicators)

Run: `pip list` and cross-reference with `requirements.txt`

### 4. Environment Variables Validation
Check `.env` file for required keys:

**Critical**:
- At least ONE AI provider key:
  - `ANTHROPIC_KEY` (Claude)
  - `OPENAI_KEY` (GPT)
  - `DEEPSEEK_KEY` (DeepSeek)
  - `GROQ_API_KEY` (Groq)
  - `OPENROUTER_API_KEY` (OpenRouter)

**Trading APIs**:
- `BIRDEYE_API_KEY` (Solana market data)
- `RPC_ENDPOINT` (Solana blockchain)
- `MOONDEV_API_KEY` (optional, custom API)
- `COINGECKO_API_KEY` (optional, token metadata)

**Trading Wallet** (if live trading):
- `SOLANA_PRIVATE_KEY` (⚠️ WARNING: Needed for real trades)

**Check for**:
- Keys not empty
- Keys don't contain placeholder text
- No keys are exposed in code (security check)

### 5. Configuration Validation
Read `src/config.py` and validate:

**Position Sizing**:
- `usd_size` is reasonable (e.g., $5-$100)
- `max_usd_order_size` > `usd_size`
- `CASH_PERCENTAGE` between 0-100
- `MAX_POSITION_PERCENTAGE` between 0-100

**Risk Management**:
- `MAX_LOSS_USD` should be negative (e.g., -25)
- `MAX_GAIN_USD` should be positive
- `MINIMUM_BALANCE_USD` makes sense for position sizes

**Agent Settings**:
- `SLEEP_BETWEEN_RUNS_MINUTES` is reasonable (5-60 min)
- `AI_MODEL` is a valid model name
- `AI_TEMPERATURE` between 0-2

**Token Lists**:
- `MONITORED_TOKENS` is not empty
- Token addresses are valid Solana addresses (43-44 chars)
- No duplicates between `MONITORED_TOKENS` and `EXCLUDED_TOKENS`

### 6. API Connectivity Tests
Test connectivity to all critical APIs:

**AI Providers**:
- Test Anthropic API (if key present)
- Test OpenAI API (if key present)
- Test configured AI_MODEL works

**Trading APIs**:
- Test BirdEye API endpoint
- Test Solana RPC endpoint
- Test CoinGecko API (if key present)

Use script: `python scripts/test_apis.py` if available

### 7. Model Factory Validation
Verify ModelFactory is properly configured:
- Check `src/models/model_factory.py` exists
- Verify supported providers list
- Test that configured AI_MODEL can be instantiated
- Check for proper error handling

### 8. Agent Integrity Check
For all agents in `src/agents/`:
- Count total agents
- Check if they use ModelFactory (grep for `model_factory.get_model`)
- Look for direct API client usage (anti-pattern)
- Check for proper error handling
- Verify they can run standalone

### 9. Performance Infrastructure Check
Validate performance optimization tools:
- Check if `src/utils/cache_manager.py` exists
- Check if `src/utils/error_handling.py` exists
- Verify cache system is importable
- Check if agents use caching decorators
- Verify retry decorators are available

### 10. Trading Functionality Validation
Check core trading functions in `nice_funcs.py`:
- `token_overview()` - Get token data
- `token_price()` - Get price
- `get_position()` - Check positions
- `market_buy()` - Execute buy
- `market_sell()` - Execute sell
- `get_ohlcv_data()` - Historical data

Don't execute trades, just verify functions exist and are importable.

## Expected Output Format

```markdown
# Moon Dev System Validation Report
Date: [Current Date/Time]

## Summary
✅ Passed: XX/10 checks
⚠️  Warnings: XX issues
❌ Failed: XX critical issues

**System Status**: READY / NEEDS ATTENTION / NOT READY

---

## 1. File Structure ✅/❌
✅ All critical files found
⚠️  Missing: [list any missing files]

## 2. Python Syntax ✅/❌
✅ All XX agents validated
❌ Errors in: [list files with syntax errors]

[show error details]

## 3. Dependencies ✅/❌
✅ Installed: [list critical packages]
❌ Missing: [list missing packages]

Install command:
```bash
pip install [missing packages]
```

## 4. Environment Variables ✅/❌
✅ AI Provider: [Anthropic/OpenAI/DeepSeek/etc.]
✅ Trading APIs: BirdEye ✅, RPC ✅
⚠️  Optional missing: [list]

## 5. Configuration ✅/❌
✅ Position sizing: $XX per trade
✅ Risk limits: Loss $XX, Gain $XX
⚠️  Issues found: [list any config issues]

## 6. API Connectivity ✅/❌
✅ Anthropic API: Connected
✅ BirdEye API: Connected
❌ RPC Endpoint: Failed - [error message]

## 7. Model Factory ✅/❌
✅ Configured model: [model name]
✅ Provider: [provider name]

## 8. Agent Integrity ✅/❌
✅ Total agents: XX
✅ Using ModelFactory: XX/XX
⚠️  Direct API usage: [list agents]
⚠️  Over 800 lines: [list large agents]

## 9. Performance Infrastructure ✅/❌
✅ Cache manager: Available
✅ Error handling: Available
⚠️  Agents using caching: XX/XX (XX%)

## 10. Trading Functions ✅/❌
✅ All core functions available
✅ nice_funcs.py: importable

---

## Critical Issues to Fix
1. [Issue 1 with specific fix]
2. [Issue 2 with specific fix]

## Warnings to Address
1. [Warning 1 with recommendation]
2. [Warning 2 with recommendation]

## System Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Next Steps
If READY:
```bash
# Run main orchestrator
python src/main.py

# Or run specific agent
python src/agents/trading_agent.py
```

If NEEDS ATTENTION:
1. [Fix critical issue 1]
2. [Fix critical issue 2]
3. Re-run validation

If NOT READY:
⚠️  System cannot run. Fix all critical issues first.
```

## Tools You Should Use

- Use `Read` to check file contents
- Use `Glob` to find files
- Use `Grep` to search for patterns
- Use `Bash` to run validation commands (py_compile, test_apis.py)
- DO NOT use Task tool - perform validation directly

## Success Criteria

System is READY when:
- All critical files exist and are valid Python
- At least one AI provider is configured and working
- Trading APIs are accessible
- Configuration values are reasonable
- No critical issues blocking execution
- Performance utilities are available (warnings OK)

Begin system validation now!
