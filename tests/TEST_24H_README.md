# 🌙 Moon Dev's 24-Hour Trading System Test

Comprehensive 24-hour test van het MT5 trading systeem met real-time AI analysis.

## 📋 Overzicht

Deze test voert het volledige trading systeem uit gedurende 24 uur en test:
- ✅ Multi-asset trading (Forex, Gold, Stocks, Indices)
- ✅ Trading hours filtering (alleen tijdens hoge volatiliteit)
- ✅ Risk management (max 1 positie tegelijk)
- ✅ AI decision making via OpenRouter (DeepSeek V3)
- ✅ Position management en order execution
- ✅ Error handling en recovery

**Alles draait in sandbox mode - GEEN ECHT GELD!**

## 🚀 Quick Start

### Optie 1: Docker (Aanbevolen)

```bash
# Start de 24-uurs test
docker-compose -f docker-compose.test.yml up test-24h

# Met monitoring (in aparte terminal)
docker-compose -f docker-compose.test.yml up test-monitor
```

### Optie 2: Direct Python

```bash
# Activeer conda environment
conda activate tflow

# Installeer dependencies (indien nodig)
pip install -r requirements.txt

# Start test (Windows met MT5)
python tests/test_24h_trading.py --duration 24 --interval 15

# Start test (Mac/Linux zonder MT5)
python tests/test_24h_trading.py --duration 24 --interval 15 --skip-mt5
```

## 📊 Test Parameters

| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `--duration` | 24 | Test duur in uren |
| `--interval` | 15 | Check interval in minuten |
| `--skip-mt5` | False | Skip MT5 initialisatie (voor Mac/Linux) |

### Voorbeelden

```bash
# Korte 1-uur test
python tests/test_24h_trading.py --duration 1 --interval 5

# Snelle 30-minuten test
python tests/test_24h_trading.py --duration 0.5 --interval 2

# Volledige 24-uur test
python tests/test_24h_trading.py --duration 24 --interval 15
```

## 📈 Monitoring

### Real-time Monitoring

Tijdens de test zie je:
- 🔄 Cycle updates (elke 15 minuten)
- 🧠 AI beslissingen
- 💼 Trade executions
- ⏱️  Trading hours status
- ✅/❌ Success/failure status

### Log Bestanden

Alle logs worden opgeslagen in:
- `tests/results/` - JSON resultaten
- `logs/` - Gedetailleerde logs

### Docker Logs

```bash
# Bekijk test logs
docker logs moon-dev-trading-test-24h -f

# Bekijk monitoring logs
docker logs moon-dev-test-monitor -f
```

## 📊 Resultaten Analyseren

### Automatische Analyse

```bash
# Analyseer laatste test
python tests/analyze_results.py --latest

# Analyseer specifiek bestand
python tests/analyze_results.py tests/results/24h_test_FINAL_20250105_120000.json
```

### Analyse Output

De analyzer geeft:
- ✅ Test summary (configuratie, statistieken)
- 🔄 Cycle analysis (success rate, timing)
- 🧠 Decision analysis (beslissingen per cycle)
- 💼 Trade analysis (trade patterns)
- ⚠️  Error analysis (meest voorkomende errors)
- 📈 Performance metrics (uptime, success rate)
- 💡 Recommendations (verbeterpunten)

## 🔧 Configuratie

De test gebruikt configuratie uit `src/config.py`:

```python
# MT5 Configuration
MT5_ENABLED = True
MT5_MAX_POSITIONS = 1  # Max 1 positie!
MT5_MODEL_TYPE = 'openrouter'
MT5_MODEL_NAME = 'deepseek/deepseek-chat-v3-0324'

# Trading Hours
MT5_USE_TRADING_HOURS_FILTER = True
MT5_STRICT_HOURS = True

# Sandbox
SANDBOX_MODE = True
SANDBOX_STARTING_BALANCE = 150000
```

## 📊 Test Data

### Data Bronnen

1. **MT5 Real-Time Data**
   - Live prijzen van MetaQuotes demo server
   - OHLCV data voor technische analyse
   - Bid/Ask spreads

2. **OpenRouter AI**
   - DeepSeek V3 voor primary analysis
   - Claude Sonnet 4.5 als fallback
   - Real-time market sentiment

3. **Trading Hours Filter**
   - Detecteert huidige markt sessie
   - Filtert op optimale trading tijden
   - Amsterdam/CET timezone display

### Output Bestanden

Elke test cycle genereert:

**Intermediate Results** (elke 15 min):
```
tests/results/24h_test_INTERMEDIATE_[timestamp].json
```

**Final Results** (na 24 uur):
```
tests/results/24h_test_FINAL_[timestamp].json
```

## 🎯 Success Criteria

De test is succesvol als:
- ✅ System uptime > 95%
- ✅ Success rate > 80%
- ✅ Max 1 positie gerespecteerd
- ✅ Trading hours filter werkt correct
- ✅ Error rate < 10%
- ✅ Alle AI calls succesvol

## ⚠️  Troubleshooting

### OpenRouter API Errors

```bash
# Check API key
echo $OPENROUTER_API_KEY

# Check credits
# Ga naar: https://openrouter.ai/credits

# Test connectivity
python tests/test_openrouter_basic.py
```

### MT5 Connection Issues

```bash
# Windows: Check MT5 is running
tasklist | findstr terminal64

# Test MT5 connection
python -c "import MetaTrader5 as mt5; print(mt5.initialize())"
```

### Docker Issues

```bash
# Rebuild image
docker-compose -f docker-compose.test.yml build test-24h

# Check logs
docker logs moon-dev-trading-test-24h --tail 100

# Clean restart
docker-compose -f docker-compose.test.yml down
docker-compose -f docker-compose.test.yml up test-24h
```

## 📝 Test Checklist

Voor de test:
- [ ] `.env` file geconfigureerd met alle keys
- [ ] OpenRouter credits beschikbaar
- [ ] MT5 demo account actief (Windows)
- [ ] Sandbox mode enabled in `config.py`
- [ ] `conda activate tflow` uitgevoerd

Tijdens de test:
- [ ] Monitor logs voor errors
- [ ] Check intermediate results elke uur
- [ ] Verify trading hours filter werkt
- [ ] Confirm max 1 position rule

Na de test:
- [ ] Run `analyze_results.py --latest`
- [ ] Review recommendations
- [ ] Check error patterns
- [ ] Document findings

## 🎉 Expected Results

Na 24 uur verwacht je:
- **~96 cycles** (elke 15 minuten)
- **Multiple AI decisions** per cycle
- **0-10 trades** (afhankelijk van markt condities en trading hours)
- **<5% error rate**
- **>95% uptime**

Weinig/geen trades is normaal als:
- Trading hours filter veel tijden blokkeert
- AI geen geschikte opportuniteiten ziet
- Market condities niet voldoen aan criteria

## 🚀 Volgende Stappen

Na succesvolle test:
1. Review analysis report
2. Optimize parameters indien nodig
3. Test met kortere intervals (bijv. 5 min)
4. Deploy naar Windows VPS voor 24/7 trading
5. Setup Telegram alerts voor notifications

## 💡 Tips

- **First time**: Start met 1-hour test om systeem te valideren
- **Monitoring**: Open aparte terminal voor real-time monitoring
- **Debugging**: Gebruik `--skip-mt5` op Mac/Linux voor code testing
- **Performance**: Docker test draait in sandbox, real MT5 requires Windows
- **Costs**: OpenRouter API calls ~$0.01-0.05 per cycle

## 📞 Support

Vragen of problemen?
- Check logs eerst: `docker logs moon-dev-trading-test-24h`
- Review analysis: `python tests/analyze_results.py --latest`
- Debug mode: Set `LOG_LEVEL=DEBUG` in docker-compose.test.yml
