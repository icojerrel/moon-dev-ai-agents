# 🔧 Scripts Directory

Utility scripts for Moon Dev AI Agents.

## Available Scripts

### 1. `validate_config.py` - Configuration Validator ✅

Comprehensive validation script that checks your setup before running agents.

### 2. `test_apis.py` - API Connectivity Tester 🔌

Tests all configured API endpoints to verify connectivity and authentication.

**What It Tests:**
- AI Providers: Anthropic, OpenAI, Groq
- Trading APIs: BirdEye, Solana RPC, CoinGecko

**Usage:**
```bash
python scripts/test_apis.py
```

**Exit Codes:** `0` = all working, `1` = some failed

### 3. `check_agents.py` - Agent Health Checker 🏥

Analyzes all agent files for structure, best practices, and potential issues.

**What It Checks:**
- Python syntax validity
- File length (< 800 lines recommended)
- Standalone execution capability
- Error handling
- AI usage patterns
- Documentation quality

**Usage:**
```bash
python scripts/check_agents.py
```

**Output:** Health report for all 31+ agents with status breakdown

---

## `validate_config.py` - Details

### Configuration Validator

#### What It Checks

1. **File Structure** ✅
   - Verifies all required files exist
   - Checks required directories
   - Confirms .env file presence

2. **Python Dependencies** 📦
   - Checks installed packages
   - Identifies missing requirements
   - Distinguishes required vs optional

3. **Environment Variables** 🔐
   - Validates API keys are set
   - Checks for at least one AI provider
   - Lists missing configurations

4. **Configuration Settings** ⚙️
   - Validates config.py values
   - Checks for common mistakes
   - Displays current settings

#### Usage

```bash
# Run validation
python scripts/validate_config.py

# Or make executable and run
chmod +x scripts/validate_config.py
./scripts/validate_config.py
```

#### Example Output

```
============================================================
🌙 Moon Dev Configuration Validator
============================================================

🔍 Checking File Structure...
✅ All required files found

🔍 Checking Python Dependencies...
✅ Core packages installed
⚠️  Some optional packages missing

🔍 Checking Environment Variables...
✅ ANTHROPIC_KEY configured
❌ BIRDEYE_API_KEY missing

🔍 Checking Configuration Settings...
⚠️  MAX_LOSS_USD should be negative
✅ All settings within valid ranges

📊 Current Configuration:
  Position Size: $25
  Max Order Size: $3
  Monitored Tokens: 2
  AI Model: claude-3-haiku-20240307

============================================================
📊 Validation Summary
============================================================
  File Structure: ✅ PASS
  Dependencies: ✅ PASS
  Environment Variables: ⚠️  WARNING
  Configuration: ✅ PASS
============================================================
```

#### When to Use

**Before First Run**: Validate complete setup
```bash
python scripts/validate_config.py
```

**After Configuration Changes**: Verify changes
```bash
# Edit config
vim src/config.py

# Validate
python scripts/validate_config.py
```

**Troubleshooting**: Diagnose issues
```bash
# Having problems?
python scripts/validate_config.py

# Check specific issues in output
```

**CI/CD**: Add to automated testing
```bash
# In GitHub Actions, etc.
python scripts/validate_config.py || exit 1
```

#### Exit Codes

- `0`: All checks passed ✅
- `1`: Some checks failed ❌

Use in scripts:
```bash
if python scripts/validate_config.py; then
    echo "✅ Ready to run"
    python src/main.py
else
    echo "❌ Fix issues first"
    exit 1
fi
```

#### What It Does NOT Check

- API key validity (only checks if they exist)
- Network connectivity
- Actual API rate limits
- Wallet balances
- Token prices

For these, you need to run the actual agents.

## Script Summary

| Script | Purpose | Status |
|--------|---------|--------|
| `validate_config.py` | Validate setup | ✅ Available |
| `test_apis.py` | Test API connectivity | ✅ Available |
| `check_agents.py` | Analyze agent health | ✅ Available |
| `backup_data.py` | Backup agent data | 🔜 Planned |
| `rotate_keys.py` | Rotate API keys | 🔜 Planned |
| `clean_data.py` | Clean old data | 🔜 Planned |

## Recommended Usage Flow

### Before First Run
```bash
# 1. Validate configuration
python scripts/validate_config.py

# 2. Test API connections
python scripts/test_apis.py

# 3. Check agent health
python scripts/check_agents.py

# 4. If all pass, run agents
python src/main.py
```

### Regular Maintenance
```bash
# Weekly: Check agent health
python scripts/check_agents.py

# Monthly: Validate config
python scripts/validate_config.py

# As needed: Test APIs
python scripts/test_apis.py
```

## Future Scripts

### Coming Soon

- `backup_data.py` - Backup agent data and strategies
- `rotate_keys.py` - Safely rotate API keys
- `clean_data.py` - Clean old agent data files
- `benchmark_agents.py` - Performance benchmarking

## Contributing

Want to add a utility script? Follow these guidelines:

1. **Clear Purpose**: One script, one task
2. **Good Documentation**: Add docstrings and comments
3. **Error Handling**: Graceful failures
4. **User Feedback**: Clear progress messages
5. **Exit Codes**: 0 for success, non-zero for failure
6. **Update This README**: Document your script

### Script Template

```python
#!/usr/bin/env python3
"""
🌙 Moon Dev Script Name
Brief description of what this script does
"""

import os
import sys
from pathlib import Path

def main():
    """Main function"""
    try:
        # Your code here
        print("✅ Success")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Usage in SETUP.md

The validation script is referenced in `SETUP.md`:

```markdown
### Test 2: Verify Environment Variables
\`\`\`bash
python scripts/validate_config.py
\`\`\`
```

Users should run this before their first agent execution.

## Usage in CI/CD

Example GitHub Actions workflow:

```yaml
name: Validate Configuration
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate configuration
        run: python scripts/validate_config.py
```

---

🌙 **Built with love by Moon Dev**

*Making AI trading agents accessible to everyone*
