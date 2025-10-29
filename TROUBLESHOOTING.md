# 🔧 Troubleshooting Guide

Common issues and solutions for Moon Dev AI Agents.

## 📑 Table of Contents
- [Installation Issues](#installation-issues)
- [Dependency Errors](#dependency-errors)
- [API Errors](#api-errors)
- [Trading Errors](#trading-errors)
- [Agent-Specific Issues](#agent-specific-issues)
- [Performance Issues](#performance-issues)
- [Git Issues](#git-issues)

---

## Installation Issues

### Conda Command Not Found

**Problem**:
```bash
conda: command not found
```

**Solution**:
```bash
# Restart terminal or run:
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS with zsh

# Or re-install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### Python Version Mismatch

**Problem**:
```
Python 3.11.14 instead of recommended 3.10.9
```

**Solution**:
```bash
# Create new environment with correct version
conda create -n tflow python=3.10.9
conda activate tflow

# Verify
python --version  # Should show 3.10.9
```

### Cannot Create Conda Environment

**Problem**:
```
CondaHTTPError or PackageNotFound
```

**Solution**:
```bash
# Update conda
conda update -n base conda

# Try creating environment again
conda create -n tflow python=3.10.9

# If still fails, specify channel
conda create -n tflow python=3.10.9 -c conda-forge
```

---

## Dependency Errors

### TA-Lib Installation Failed

**Problem**:
```
ERROR: Could not find a version that satisfies the requirement ta-lib
```

**Root Cause**: TA-Lib requires system-level library installation first.

**Solution**:

**macOS**:
```bash
# Install via Homebrew
brew install ta-lib

# Then install Python wrapper
pip install ta-lib
```

**Ubuntu/Debian**:
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install build-essential
sudo apt-get install ta-lib

# Then install Python wrapper
pip install ta-lib
```

**Manual Build** (if above fails):
```bash
# Download source
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/

# Build and install
./configure --prefix=/usr
make
sudo make install

# Install Python wrapper
pip install ta-lib
```

**Windows**:
```bash
# Download pre-built wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

# Install wheel
pip install TA_Lib‑0.4.24‑cp310‑cp310‑win_amd64.whl
```

### Google Gemini / Protobuf Conflict

**Problem**:
```
ERROR: Cannot install google-generativeai due to protobuf version conflict
```

**Current Status**: Temporarily disabled in `requirements.txt`

**Workaround**:
```bash
# Option 1: Skip Gemini (recommended)
# Already done - line is commented out in requirements.txt

# Option 2: Try specific versions (experimental)
pip install google-generativeai==0.8.3 protobuf==4.25.1 proto-plus==1.25.0

# Option 3: Use other AI providers
# Use Anthropic, OpenAI, DeepSeek, or Groq instead
```

**Fix**: Use `ModelFactory` to switch to different provider:
```python
from src.models.model_factory import ModelFactory

# Instead of Gemini, use:
model = ModelFactory.create_model('anthropic')  # or 'openai', 'deepseek'
```

### FFmpeg Not Found

**Problem**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution**:

**macOS**:
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows**:
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**Verify**:
```bash
ffmpeg -version
```

### NumPy/Pandas Version Conflicts

**Problem**:
```
ImportError: numpy.core.multiarray failed to import
```

**Solution**:
```bash
# Uninstall and reinstall
pip uninstall numpy pandas
pip install numpy>=1.24.0 pandas>=2.0.0

# Or upgrade all
pip install -r requirements.txt --upgrade
```

### OpenCV Import Error

**Problem**:
```
ImportError: libGL.so.1: cannot open shared object file
```

**Solution** (Linux):
```bash
sudo apt-get update
sudo apt-get install libgl1-mesa-glx
```

---

## API Errors

### Anthropic API Key Invalid

**Problem**:
```
anthropic.AuthenticationError: Invalid API key
```

**Diagnosis**:
```bash
# Check key is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_KEY')[:20])"
```

**Solutions**:
1. **Verify key in .env**:
   ```bash
   # Key should start with sk-ant-api03-
   cat .env | grep ANTHROPIC_KEY
   ```

2. **Check for extra spaces**:
   ```bash
   # Remove any whitespace
   # .env should be:
   ANTHROPIC_KEY=sk-ant-api03-...
   # Not:
   ANTHROPIC_KEY = sk-ant-api03-...
   ```

3. **Regenerate key**:
   - Go to https://console.anthropic.com/
   - Create new API key
   - Update `.env`

4. **Check API credits**:
   - Visit console to ensure account has credits

### Rate Limit Exceeded

**Problem**:
```
Rate limit exceeded. Please try again later.
```

**Solutions**:
1. **Increase sleep time**:
   ```python
   # In config.py
   SLEEP_BETWEEN_RUNS_MINUTES = 30  # Increase from 15
   ```

2. **Reduce agent frequency**:
   ```python
   # Disable some agents
   ACTIVE_AGENTS = {
       'risk': True,
       'trading': False,  # Disable to reduce API calls
   }
   ```

3. **Upgrade API tier**:
   - Check provider's rate limits
   - Upgrade to higher tier if needed

### BirdEye API Errors

**Problem**:
```
403 Forbidden or 401 Unauthorized from BirdEye API
```

**Solutions**:
1. **Verify API key**:
   ```bash
   curl -H "X-API-KEY: YOUR_KEY" https://public-api.birdeye.so/public/tokenlist
   ```

2. **Check subscription status**:
   - Login to BirdEye dashboard
   - Verify subscription is active
   - Check API limits

3. **Rate limiting**:
   - Reduce request frequency
   - Implement caching

### RPC Endpoint Errors

**Problem**:
```
Failed to connect to RPC endpoint
```

**Solutions**:
1. **Test endpoint**:
   ```bash
   curl YOUR_RPC_ENDPOINT -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'
   ```

2. **Check Helius dashboard**:
   - Verify API key is active
   - Check request limits
   - Ensure credits available

3. **Try different endpoint**:
   ```bash
   # Public endpoints (rate limited)
   RPC_ENDPOINT=https://api.mainnet-beta.solana.com
   ```

### OpenAI API Errors

**Problem**:
```
openai.error.RateLimitError: You exceeded your current quota
```

**Solutions**:
1. **Check billing**:
   - Go to https://platform.openai.com/account/billing
   - Add payment method
   - Check usage limits

2. **Switch to cheaper model**:
   ```python
   # Use GPT-3.5 instead of GPT-4
   model = ModelFactory.create_model('openai')
   # Specify model in config
   ```

3. **Use alternative provider**:
   ```python
   # DeepSeek is much cheaper
   model = ModelFactory.create_model('deepseek')
   ```

---

## Trading Errors

### Insufficient Balance

**Problem**:
```
Error: Insufficient balance for trade
```

**Solutions**:
1. **Check balance**:
   ```python
   python -c "from src.nice_funcs import get_balance; print(get_balance())"
   ```

2. **Reduce position size**:
   ```python
   # In config.py
   usd_size = 5  # Reduce from 10
   ```

3. **Fund wallet**:
   - Send SOL to wallet address
   - Ensure enough for gas fees

### Transaction Failed

**Problem**:
```
Transaction simulation failed
```

**Solutions**:
1. **Check RPC connection**:
   ```bash
   # Test RPC
   curl $RPC_ENDPOINT -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'
   ```

2. **Increase slippage**:
   ```python
   # In trading code
   slippage = 0.05  # 5% instead of 1%
   ```

3. **Check token liquidity**:
   - Verify pool has enough liquidity
   - Avoid low-liquidity tokens

### Private Key Error

**Problem**:
```
Invalid private key format
```

**Solutions**:
1. **Verify format**:
   ```bash
   # Should be base58 encoded
   # Example: 5KQwr...
   cat .env | grep SOLANA_PRIVATE_KEY
   ```

2. **Export from wallet**:
   - Phantom: Settings → Export Private Key
   - Copy exactly (no spaces)

3. **Test key**:
   ```python
   python -c "
   from solders.keypair import Keypair
   import base58
   key = 'YOUR_KEY'
   kp = Keypair.from_bytes(base58.b58decode(key))
   print(f'Address: {kp.pubkey()}')
   "
   ```

### Position Not Found

**Problem**:
```
No position found for token
```

**Possible Causes**:
1. Position was closed
2. Using wrong wallet address
3. Token address incorrect

**Debug**:
```python
python -c "
from src.nice_funcs import get_position
position = get_position('TOKEN_ADDRESS')
print(position)
"
```

---

## Agent-Specific Issues

### Risk Agent: Circuit Breaker Triggered

**Problem**:
```
🚨 CIRCUIT BREAKER: Max loss reached
```

**This is working as intended!** Risk agent is protecting you.

**To Resume**:
1. Review why losses occurred
2. Adjust strategy
3. Restart system if you want to continue

**To Adjust Limits**:
```python
# In config.py
MAX_LOSS_USD = -100  # Increase if needed (negative number)
```

### RBI Agent: Can't Parse Strategy

**Problem**:
```
Failed to extract strategy from video
```

**Solutions**:
1. **Use clearer source**:
   - Choose videos with explicit strategy explanations
   - PDFs often work better than videos

2. **Provide more context**:
   ```python
   # When prompted, give detailed description
   "Moving average crossover: Buy when 20 MA crosses above 50 MA, sell opposite"
   ```

3. **Check DeepSeek credits**:
   - Verify DeepSeek API key has credits

### Sentiment Agent: No Twitter Data

**Problem**:
```
Failed to fetch Twitter sentiment
```

**Solutions**:
1. **Check Twitter API keys**:
   ```bash
   cat .env | grep TWITTER
   ```

2. **Rate limiting**:
   - Twitter API has strict limits
   - Increase sleep time between requests

3. **Use alternative sentiment sources**:
   - CoinGecko sentiment
   - Reddit sentiment

### Chat Agent: YouTube Connection Failed

**Problem**:
```
Cannot connect to YouTube live chat
```

**Solutions**:
1. **Verify stream is live**:
   - Chat agent only works on live streams
   - Check stream URL is correct

2. **Check Restream credentials**:
   ```bash
   cat .env | grep RESTREAM
   ```

3. **API token expired**:
   - Regenerate token in Restream dashboard

### Clips Agent: FFmpeg Error

**Problem**:
```
FFmpeg processing failed
```

**Solutions**:
1. **Verify FFmpeg installed**:
   ```bash
   ffmpeg -version
   ```

2. **Check video file path**:
   - Ensure source video exists
   - Check file permissions

3. **Check disk space**:
   ```bash
   df -h  # Ensure enough space for output
   ```

---

## Performance Issues

### Agents Running Slow

**Symptoms**: Agents take >5 minutes per cycle

**Solutions**:
1. **Reduce LLM token usage**:
   ```python
   # In config.py
   AI_MAX_TOKENS = 500  # Reduce from 1000
   ```

2. **Use faster AI model**:
   ```python
   # Switch to Haiku or Groq
   model = ModelFactory.create_model('groq')  # Very fast
   ```

3. **Reduce data fetching**:
   ```python
   # Fetch less historical data
   days_back = 1  # Instead of 7
   ```

4. **Disable heavy agents**:
   ```python
   ACTIVE_AGENTS = {
       'sentiment': False,  # Can be slow
       'whale': False,      # Lots of data processing
   }
   ```

### High Memory Usage

**Symptoms**: System using >4GB RAM

**Solutions**:
1. **Clear agent cache**:
   ```bash
   # Clear old data files
   find src/data -name "*.csv" -mtime +7 -delete
   ```

2. **Reduce batch sizes**:
   ```python
   # Process fewer tokens at once
   ```

3. **Restart agents periodically**:
   ```bash
   # Add to crontab for daily restart
   0 0 * * * pkill -f "python src/main.py" && cd /path/to/repo && python src/main.py
   ```

### API Quota Exhausted

**Symptoms**: Unexpected API bills

**Solutions**:
1. **Monitor usage**:
   - Check AI provider dashboards daily
   - Set up billing alerts

2. **Reduce API calls**:
   ```python
   # Increase sleep time
   SLEEP_BETWEEN_RUNS_MINUTES = 60  # From 15
   ```

3. **Use cheaper models**:
   - Claude Haiku instead of Sonnet
   - DeepSeek instead of GPT-4
   - Local Ollama for some tasks

---

## Git Issues

### Stale Remote Branch

**Problem**:
```
Your branch is based on 'origin/X', but the upstream is gone
```

**Solution**:
```bash
# Clean up stale references
git remote prune origin

# Re-push if needed
git push -u origin YOUR_BRANCH
```

### Push Rejected (403)

**Problem**:
```
fatal: unable to access: HTTP 403
```

**Solution**:
```bash
# For claude/* branches, ensure session ID matches
# Branch must start with 'claude/' and end with session ID

# Check current branch
git branch --show-current

# If needed, create correct branch name
git checkout -b claude/YOUR_SESSION_ID
```

### Merge Conflicts

**Problem**:
```
CONFLICT (content): Merge conflict in FILE
```

**Solution**:
```bash
# See conflicting files
git status

# Edit files to resolve conflicts (remove <<<, ===, >>> markers)
# Then:
git add .
git commit -m "Resolve merge conflicts"
```

---

## Environment Issues

### .env File Not Loaded

**Problem**:
```
None returned for API keys
```

**Diagnosis**:
```bash
# Check file exists
ls -la .env

# Check it's being loaded
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('ANTHROPIC_KEY:', os.getenv('ANTHROPIC_KEY')[:20] if os.getenv('ANTHROPIC_KEY') else 'NOT FOUND')
"
```

**Solutions**:
1. **Verify file location**:
   ```bash
   # .env should be in project root
   # Same directory as main.py parent
   ls -la .env
   ```

2. **Check file format**:
   ```bash
   # No spaces around =
   # Correct: KEY=value
   # Wrong: KEY = value
   cat .env
   ```

3. **Explicit path**:
   ```python
   # In your script
   from dotenv import load_dotenv
   load_dotenv('/full/path/to/.env')
   ```

### Import Errors

**Problem**:
```
ModuleNotFoundError: No module named 'src'
```

**Solution**:
```bash
# Run from project root
cd /path/to/moon-dev-ai-agents

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/moon-dev-ai-agents"

# Or in script:
import sys
sys.path.append('/path/to/moon-dev-ai-agents')
```

---

## Emergency Procedures

### Kill All Running Agents

```bash
# Linux/macOS
pkill -f "python src/main.py"
pkill -f "python src/agents"

# Or find and kill
ps aux | grep "python src"
kill PID
```

### Reset Everything

```bash
# Stop all agents
pkill -f "python src"

# Clear conda environment
conda deactivate
conda env remove -n tflow

# Start fresh
conda create -n tflow python=3.10.9
conda activate tflow
pip install -r requirements.txt
```

### Backup Important Data

```bash
# Backup .env
cp .env .env.backup

# Backup agent data
tar -czf agent_data_backup.tar.gz src/data/

# Backup strategies
tar -czf strategies_backup.tar.gz src/strategies/
```

---

## Getting Help

If you can't resolve your issue:

1. **Check logs carefully** - error messages are usually descriptive
2. **Search GitHub Issues** - someone may have had the same problem
3. **Ask in Discord** - http://moondev.com
4. **Check YouTube** - https://youtube.com/moondevai
5. **Review documentation** - CLAUDE.md, README.md, SETUP.md

### When Asking for Help

Include:
- Error message (full traceback)
- What you were trying to do
- What you've tried already
- Environment info:
  ```bash
  python --version
  pip list | grep anthropic
  cat .env | grep -v KEY  # Don't share keys!
  ```

---

## Prevention Best Practices

### Regular Maintenance

```bash
# Weekly:
- Review API usage and costs
- Check agent performance logs
- Update dependencies
- Backup important data
- Review trading results

# Monthly:
- Update Python packages
- Rotate API keys
- Review and optimize strategies
- Clean old data files
```

### Monitoring Checklist

```markdown
- [ ] API usage within budget
- [ ] No error spikes in logs
- [ ] Agents completing in reasonable time
- [ ] Risk limits appropriate
- [ ] Balances sufficient
- [ ] No rate limiting issues
- [ ] Git backups up to date
```

---

🌙 **Need more help? Join the Discord: http://moondev.com**
