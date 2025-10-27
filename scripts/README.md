# 🔧 Scripts Directory

Utility scripts for Moon Dev AI Agents.

## Available Scripts

### `validate_config.py` - Configuration Validator

Comprehensive validation script that checks your setup before running agents.

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

## Future Scripts

### Coming Soon

- `check_health.py` - Live system health monitoring
- `backup_data.py` - Backup agent data and strategies
- `rotate_keys.py` - Safely rotate API keys
- `test_apis.py` - Test API connectivity
- `clean_data.py` - Clean old agent data files

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
