# 🚀 Production Deployment Guide

Complete guide for deploying Moon Dev AI Trading System to production.

## 📋 Prerequisites

### System Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB disk space
- Ubuntu 20.04+ or similar Linux distribution

**Recommended:**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD storage
- Ubuntu 22.04 LTS
- Dedicated VPS/server with good network connectivity

### Software Requirements

- Docker & Docker Compose (for containerized deployment)
- OR Python 3.10.9 + Conda (for native deployment)
- Git
- systemd (for service management)

## 🐳 Option 1: Docker Deployment (Recommended)

### 1. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin
```

Logout and login again for group changes to take effect.

### 2. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/yourusername/moon-dev-ai-agents.git
cd moon-dev-ai-agents
sudo chown -R $USER:$USER .
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env_example .env

# Edit with your credentials
nano .env
```

**Required variables:**
```bash
# Trading APIs
BIRDEYE_API_KEY=your_key_here
RPC_ENDPOINT=your_helius_rpc_here
SOLANA_PRIVATE_KEY=your_private_key_here

# AI Services (at least one)
ANTHROPIC_KEY=your_claude_key_here
OPENAI_KEY=your_openai_key_here
DEEPSEEK_KEY=your_deepseek_key_here

# Alerting (highly recommended)
TELEGRAM_ALERTS_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# MT5 (if using forex trading)
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

### 4. Configure Trading Settings

Edit `src/config.py`:

```python
# Enable/disable agents
MT5_ENABLED = True  # Set to True if using MT5

# Position sizing
usd_size = 25  # Adjust based on your capital
max_usd_order_size = 3

# Risk management
CASH_PERCENTAGE = 20
MAX_POSITION_PERCENTAGE = 30
MAX_LOSS_USD = 25
MAX_GAIN_USD = 25
```

### 5. Build and Run

```bash
# Build images
docker-compose build

# Start main trading system
docker-compose up -d trading-system

# Start MT5 agent (if enabled)
docker-compose --profile mt5 up -d mt5-agent

# Start health monitoring
docker-compose --profile monitoring up -d health-monitor

# View logs
docker-compose logs -f trading-system
```

### 6. Manage Containers

```bash
# View running containers
docker-compose ps

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart trading-system

# View logs
docker-compose logs -f

# Check resource usage
docker stats
```

## 💻 Option 2: Native Deployment

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools
sudo apt install -y build-essential git wget curl

# Install TA-Lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

### 2. Install Miniconda

```bash
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install
bash Miniconda3-latest-Linux-x86_64.sh

# Reload shell
source ~/.bashrc
```

### 3. Setup Python Environment

```bash
# Clone repository
cd ~
git clone https://github.com/yourusername/moon-dev-ai-agents.git
cd moon-dev-ai-agents

# Create conda environment
conda create -n tflow python=3.10.9 -y
conda activate tflow

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy and edit .env
cp .env_example .env
nano .env
```

### 5. Install as Systemd Service

```bash
# Edit service file with your paths
nano moondev-trading.service

# Install service
sudo cp moondev-trading.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable moondev-trading
sudo systemctl start moondev-trading

# Check status
sudo systemctl status moondev-trading

# View logs
sudo journalctl -u moondev-trading -f
```

## 🔐 Security Best Practices

### 1. Secrets Management

**Never commit secrets to git:**
```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

**Use environment-specific files:**
```bash
.env.production  # Production credentials
.env.staging     # Staging credentials
.env.dev         # Development credentials
```

### 2. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Apply
sudo ufw reload
```

### 3. SSH Hardening

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config

# Set:
PasswordAuthentication no
PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd
```

### 4. API Key Rotation

- Rotate API keys every 90 days
- Use separate keys for prod/staging/dev
- Monitor API usage for anomalies

## 📊 Monitoring & Alerts

### 1. Setup Telegram Alerts

**Create Telegram Bot:**
1. Message @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Save the bot token

**Get Chat ID:**
1. Message your bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find your chat ID in the response

**Configure:**
```bash
# In .env
TELEGRAM_ALERTS_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
MIN_ALERT_LEVEL=WARNING
```

### 2. Setup Discord Alerts (Optional)

1. Create Discord server
2. Server Settings → Integrations → Webhooks → New Webhook
3. Copy webhook URL

```bash
# In .env
DISCORD_ALERTS_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 3. Log Monitoring

```bash
# Tail main logs
tail -f logs/moondev_agents.log

# Watch errors only
tail -f logs/moondev_errors.log

# Monitor trades
tail -f logs/trades.log

# With Docker
docker-compose logs -f trading-system
```

### 4. Resource Monitoring

```bash
# System resources
htop

# Docker stats
docker stats

# Disk usage
df -h

# Memory
free -h
```

## 🔄 Maintenance

### Updating Code

**Docker:**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

**Native:**
```bash
# Pull latest code
git pull origin main

# Update dependencies
conda activate tflow
pip install -r requirements.txt

# Restart service
sudo systemctl restart moondev-trading
```

### Backup Procedures

**Automated backup script:**
```bash
#!/bin/bash
# /opt/moondev-backup.sh

BACKUP_DIR="/backup/moondev"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup logs
tar -czf $BACKUP_DIR/logs_$TIMESTAMP.tar.gz logs/

# Backup data
tar -czf $BACKUP_DIR/data_$TIMESTAMP.tar.gz src/data/

# Backup config
cp src/config.py $BACKUP_DIR/config_$TIMESTAMP.py
cp .env $BACKUP_DIR/env_$TIMESTAMP

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
```

**Add to crontab:**
```bash
# Run daily at 2 AM
0 2 * * * /opt/moondev-backup.sh >> /var/log/moondev-backup.log 2>&1
```

### Log Rotation

Logs are automatically rotated by the logging system (10MB max, 5 backups).

**Manual cleanup:**
```bash
# Remove old logs
find logs/ -name "*.log.*" -mtime +30 -delete
```

## 🧪 Testing Production Setup

### 1. Pre-deployment Checklist

- [ ] All API keys configured and tested
- [ ] Risk limits set appropriately
- [ ] Position sizes reviewed
- [ ] Alerts configured and tested
- [ ] Backup system in place
- [ ] Monitoring dashboard accessible
- [ ] Emergency shutdown procedure documented

### 2. Test with Demo Account

**Before live trading:**
1. Use demo/testnet accounts
2. Run for minimum 1 week
3. Monitor all trades
4. Verify alerts working
5. Test emergency shutdown

### 3. Gradual Rollout

**Phase 1: Paper Trading**
- Run with demo accounts
- Monitor for 1-2 weeks

**Phase 2: Micro Positions**
- Start with minimum position sizes
- Monitor for 1 week

**Phase 3: Scale Up**
- Gradually increase position sizes
- Never exceed risk tolerance

## 🆘 Troubleshooting

### System Won't Start

```bash
# Check logs
sudo journalctl -u moondev-trading -n 50

# With Docker
docker-compose logs trading-system

# Test manually
conda activate tflow
python src/main.py
```

### High CPU Usage

```bash
# Check process
top -p $(pgrep -f main.py)

# Reduce check frequency in config.py
SLEEP_BETWEEN_RUNS_MINUTES = 30  # Increase from 15
```

### Out of Memory

```bash
# Check memory
free -h

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### API Connection Errors

```bash
# Test API connectivity
curl -H "X-API-KEY: $BIRDEYE_API_KEY" \
  https://public-api.birdeye.so/public/tokenlist

# Check DNS
ping api.birdeye.so

# Check firewall
sudo ufw status
```

## 📞 Support

**Issues:**
- GitHub Issues: [Repository Issues](https://github.com/youruser/moon-dev-ai-agents/issues)
- Discord: Join via [moondev.com](https://moondev.com)

**Emergency Shutdown:**
```bash
# Docker
docker-compose down

# Native
sudo systemctl stop moondev-trading

# Force kill (last resort)
pkill -f "python src/main.py"
```

## ⚖️ Legal & Compliance

**Before Production:**
- [ ] Understand local trading regulations
- [ ] Verify broker allows automated trading
- [ ] Review tax implications
- [ ] Ensure compliance with securities laws
- [ ] Consider consulting legal/financial advisor

**Risk Disclaimer:**
- This software is experimental
- No guarantee of profitability
- Substantial risk of loss
- Only trade with risk capital
- Past performance ≠ future results

---

**Built with ❤️ by Moon Dev 🌙**

For video tutorials, visit the [YouTube playlist](https://youtube.com/playlist?list=PLXrNVMjRZUJg4M4uz52iGd1LhXXGVbIFz)
