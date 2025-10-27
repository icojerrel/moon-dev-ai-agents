# 🚀 Moon Dev AI Agents - Deployment Setup Guide

Complete step-by-step guide for setting up and deploying the AI trading agent system.

## 📋 Prerequisites

Before starting, ensure you have:
- Computer with Linux/macOS/Windows (WSL)
- Terminal access
- Git installed
- Internet connection
- Credit card for API subscriptions (most services have free tiers)

## 🔧 Installation Steps

### Step 1: Install Conda (Python Environment Manager)

#### macOS/Linux:
```bash
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install
bash Miniconda3-latest-Linux-x86_64.sh

# Restart terminal or run:
source ~/.bashrc
```

#### Windows:
Download and install from: https://docs.conda.io/en/latest/miniconda.html

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/icojerrel/moon-dev-ai-agents.git
cd moon-dev-ai-agents
```

### Step 3: Create Python Environment

```bash
# Create conda environment with Python 3.10.9
conda create -n tflow python=3.10.9

# Activate environment
conda activate tflow

# Verify Python version
python --version  # Should show Python 3.10.9
```

**Important**: Always activate this environment before running agents:
```bash
conda activate tflow
```

### Step 4: Install System Dependencies

#### TA-Lib (Technical Analysis Library)

**macOS**:
```bash
brew install ta-lib
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ta-lib
```

**Windows**:
Download from: http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip

#### FFmpeg (Video Processing)

**macOS**:
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get install ffmpeg
```

**Windows**:
Download from: https://ffmpeg.org/download.html

### Step 5: Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import anthropic, openai, pandas; print('✅ Core packages installed')"
```

**Known Issue**: Google Gemini is temporarily disabled due to protobuf conflict. See TROUBLESHOOTING.md for details.

### Step 6: Configure Environment Variables

```bash
# Copy example environment file
cp .env_example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

#### Required API Keys

**🔐 Critical (for trading)**:
```bash
# Solana blockchain access
RPC_ENDPOINT=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
SOLANA_PRIVATE_KEY=your_base58_private_key_here

# Trading data
BIRDEYE_API_KEY=your_birdeye_api_key_here
MOONDEV_API_KEY=your_moondev_key_here
```

**🤖 AI Services (choose at least one)**:
```bash
# Anthropic Claude (recommended)
ANTHROPIC_KEY=sk-ant-api03-...

# OpenAI GPT-4
OPENAI_KEY=sk-...

# DeepSeek (cost-effective)
DEEPSEEK_KEY=...

# Groq (fast inference)
GROQ_API_KEY=gsk_...
```

**📊 Optional (for specific agents)**:
```bash
# For sentiment analysis
COINGECKO_API_KEY=...

# For voice features
ELEVENLABS_API_KEY=...

# For YouTube chat agent
YOUTUBE_API_KEY=...
RESTREAM_CLIENT_ID=...
RESTREAM_CLIENT_SECRET=...
RESTREAM_EMBED_TOKEN=...

# For phone agent
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890

# For Twitter agent
TWITTER_USERNAME=...
TWITTER_EMAIL=...
TWITTER_PASSWORD=...

# For Hyperliquid trading
HYPER_LIQUID_ETH_PRIVATE_KEY=...
```

## 🎯 Getting API Keys

### Anthropic Claude (Recommended AI Provider)
1. Visit: https://console.anthropic.com/
2. Sign up for account
3. Navigate to API Keys
4. Create new key
5. Copy to `.env` as `ANTHROPIC_KEY`

**Pricing**: Pay-as-you-go, ~$0.50-$2 per 1000 agent runs

### BirdEye (Solana Market Data)
1. Visit: https://birdeye.so/
2. Request API access
3. Subscribe to plan (free tier available)
4. Copy API key to `.env`

**Pricing**: Free tier available, paid plans from $99/month

### Helius (Solana RPC)
1. Visit: https://helius.dev/
2. Create account
3. Create new project
4. Copy RPC URL to `.env` as `RPC_ENDPOINT`

**Pricing**: Free tier: 100k requests/day

### Moon Dev API
1. Join Discord: http://moondev.com
2. Request API access
3. Copy key to `.env`

**Pricing**: Check Discord for details

### OpenAI (Optional)
1. Visit: https://platform.openai.com/
2. Create account
3. Add payment method
4. Generate API key

**Pricing**: GPT-4: $0.03-$0.12 per 1K tokens

### DeepSeek (Cost-Effective)
1. Visit: https://platform.deepseek.com/
2. Create account
3. Generate API key

**Pricing**: Much cheaper than GPT-4, good for backtesting

## ⚙️ Configuration

### Step 1: Configure Trading Parameters

Edit `src/config.py`:

```python
# Tokens to monitor
MONITORED_TOKENS = [
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "So11111111111111111111111111111111111111112",   # SOL
    # Add your tokens here
]

# Position sizing
usd_size = 10  # Start small!
max_usd_order_size = 100

# Risk limits
MAX_LOSS_USD = -50
MAX_GAIN_USD = 200
MINIMUM_BALANCE_USD = 100

# Agent timing
SLEEP_BETWEEN_RUNS_MINUTES = 15
```

### Step 2: Enable Agents

Edit `src/main.py`:

```python
ACTIVE_AGENTS = {
    'risk': True,       # ✅ START WITH THIS
    'trading': False,   # Enable after testing
    'strategy': False,  # Enable after creating strategies
    'copybot': False,   # Enable if using copybot
    'sentiment': False, # Enable for sentiment analysis
}
```

**⚠️ IMPORTANT**: Start with only `risk` agent enabled to verify setup!

## 🧪 Testing Your Setup

### Test 1: Verify Dependencies
```bash
python -c "
import anthropic
import openai
import pandas
import numpy
from termcolor import cprint
print('✅ All core dependencies working')
"
```

### Test 2: Verify Environment Variables
```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
assert os.getenv('ANTHROPIC_KEY'), 'Missing ANTHROPIC_KEY'
assert os.getenv('BIRDEYE_API_KEY'), 'Missing BIRDEYE_API_KEY'
assert os.getenv('RPC_ENDPOINT'), 'Missing RPC_ENDPOINT'
print('✅ Environment variables configured')
"
```

### Test 3: Test Individual Agent
```bash
# Test risk agent (safest to start)
python src/agents/risk_agent.py
```

### Test 4: Test Model Factory
```bash
python -c "
from src.models.model_factory import ModelFactory
model = ModelFactory.create_model('anthropic')
response = model.generate_response(
    'You are a test',
    'Say OK if you can read this',
    temperature=0.7,
    max_tokens=10
)
print(f'✅ AI Model working: {response}')
"
```

## 🚀 Running the System

### Option 1: Run Main Orchestrator (Multiple Agents)
```bash
# Activate environment
conda activate tflow

# Run main system
python src/main.py
```

Press `Ctrl+C` to stop gracefully.

### Option 2: Run Individual Agents
```bash
# Run specific agents standalone
python src/agents/risk_agent.py
python src/agents/sentiment_agent.py
python src/agents/whale_agent.py
python src/agents/rbi_agent.py
```

### Option 3: Run in Background (Linux/macOS)
```bash
# Run with nohup
nohup python src/main.py > agent.log 2>&1 &

# Check logs
tail -f agent.log

# Stop
pkill -f "python src/main.py"
```

## 📊 Monitoring

### Check Logs
The system outputs color-coded logs:
- 🔵 Cyan: Agent activity
- 🟢 Green: Success
- 🟡 Yellow: Warnings
- 🔴 Red: Errors

### Check Agent Outputs
```bash
# View agent data
ls -la src/data/

# View specific agent output
cat src/data/risk_agent/risk_analysis.csv
cat src/data/sentiment_agent/sentiment_results.json
```

### Monitor Positions
```bash
# Check positions via Python
python -c "
from src.nice_funcs import get_position
position = get_position('YOUR_TOKEN_ADDRESS')
print(position)
"
```

## 🛡️ Safety Guidelines

### Start Small
1. ✅ Enable only `risk_agent` first
2. ✅ Use small position sizes (`usd_size = 10`)
3. ✅ Set tight risk limits (`MAX_LOSS_USD = -50`)
4. ✅ Test with paper trading first if possible

### Before Live Trading
- [ ] Tested all agents individually
- [ ] Verified API keys work
- [ ] Understood risk management settings
- [ ] Read all documentation
- [ ] Started with minimal capital
- [ ] Set up alerts/monitoring
- [ ] Have stop-loss strategy

### Security Checklist
- [ ] `.env` file is in `.gitignore` (✅ already configured)
- [ ] Never share API keys
- [ ] Never commit `.env` file
- [ ] Use separate keys for testing
- [ ] Rotate keys if exposed
- [ ] Keep private keys secure
- [ ] Use hardware wallet for large amounts

## 📈 Strategy Development

### Create Your First Strategy

1. Create new file in `src/strategies/`:
```python
# src/strategies/my_strategy.py
class MyStrategy:
    name = "my_simple_strategy"
    description = "My first trading strategy"

    def generate_signals(self, token_address, market_data):
        # Your logic here
        return {
            "action": "NOTHING",  # or "BUY" or "SELL"
            "confidence": 0,
            "reasoning": "Waiting for good setup"
        }
```

2. Test backtest with RBI agent:
```bash
python src/agents/rbi_agent.py
# Provide YouTube video or PDF with strategy idea
```

3. Enable strategy agent in `src/main.py`:
```python
ACTIVE_AGENTS = {
    'risk': True,
    'strategy': True,  # ✅ Enable
}
```

## 🔍 Troubleshooting

See `TROUBLESHOOTING.md` for common issues and solutions.

### Quick Fixes

**Import errors**:
```bash
pip install -r requirements.txt --upgrade
```

**TA-Lib errors**:
```bash
# Install system library first, then:
pip install ta-lib --upgrade
```

**Environment variable errors**:
```bash
# Verify .env file exists
ls -la .env

# Check it's being loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('ANTHROPIC_KEY')[:20])"
```

**API errors**:
- Check API key is correct
- Verify account has credits
- Check API rate limits

## 📚 Next Steps

1. ✅ Complete this setup guide
2. 📖 Read `CLAUDE.md` for development patterns
3. 📖 Read `README.md` for project overview
4. 🎥 Watch tutorial videos: https://youtube.com/moondevai
5. 💬 Join Discord: http://moondev.com
6. 🧪 Test individual agents
7. 📊 Create your first strategy
8. 🚀 Start with paper trading

## ⚠️ Important Disclaimers

**This is an experimental research project, NOT a guaranteed profitable trading system.**

- No AI agent can guarantee profitable trading
- You must develop and validate your own strategies
- Trading involves substantial risk of loss
- Start small and test thoroughly
- Past performance does not indicate future results
- You are responsible for all trading decisions

## 🆘 Getting Help

- 📖 Documentation: `CLAUDE.md`, `README.md`, `TROUBLESHOOTING.md`
- 💬 Discord: http://moondev.com
- 🎥 YouTube: https://youtube.com/moondevai
- 📧 Email: moon@algotradecamp.com
- 🐛 Issues: GitHub Issues

## 📝 Checklist

Copy this checklist and track your progress:

```markdown
## Setup Checklist
- [ ] Conda installed
- [ ] Repository cloned
- [ ] Python 3.10.9 environment created
- [ ] TA-Lib installed
- [ ] FFmpeg installed
- [ ] Python dependencies installed
- [ ] .env file created and configured
- [ ] At least one AI API key added
- [ ] Trading API keys added
- [ ] RPC endpoint configured
- [ ] config.py reviewed and customized
- [ ] Dependencies verified
- [ ] Environment variables verified
- [ ] Individual agent tested
- [ ] Model factory tested
- [ ] Risk limits configured
- [ ] Position sizes set (small!)
- [ ] Documentation read
- [ ] Safety guidelines understood
- [ ] Ready to start testing!
```

---

🌙 **Built with love by Moon Dev**

*Remember: This is for educational purposes. Trade responsibly.*
