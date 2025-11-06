# 🚀 SETUP NU - Account 5041139909

Je MT5 account is klaar! Volg deze stappen om **nu** te starten.

---

## ✅ JE HEBT AL

- MT5 Desktop geïnstalleerd ✅
- Demo Account: **5041139909** ✅
- Password: **qjQYWTzj** ✅
- Server: **MetaQuotes-Demo** ✅

---

## 📝 STAP 1: Maak .env Bestand (1 minuut)

**Optie A: Automatisch Script (MAKKELIJKST) ✅**

1. Dubbelklik of run:
   ```bash
   create_env_file.bat
   ```

2. Script maakt automatisch `.env` met je MT5 credentials!

3. Notepad opent automatisch

4. **Vul alleen je AI API key in:**
   ```bash
   GROK_API_KEY=xai-jouw_echte_key_hier
   ```

5. Save (Ctrl+S) en sluit Notepad

**Klaar!** ✅

---

**Optie B: Handmatig (als script niet werkt)**

1. Maak nieuw bestand: `.env` (let op: begint met punt!)

2. Kopieer dit erin:
   ```bash
   MT5_LOGIN=5041139909
   MT5_PASSWORD=m44!YU6XYGXmMjf
   MT5_SERVER=MetaQuotes-Demo

   GROK_API_KEY=xai-jouw_key_hier
   ```

3. Vervang `xai-jouw_key_hier` met je echte API key

**Note:** Als password niet werkt, probeer: `qjQYWTzj`

---

## 🔍 STAP 2: Test Verbinding (30 seconden)

```bash
python src/agents/mt5_utils.py
```

**Verwacht:**
```
✅ Connected to MT5 account: 5041139909
💰 Balance: $10000.00
📈 EURUSD: Bid: 1.04567
```

**Als error:**
- Check of MT5 Desktop **draait** (applicatie moet open zijn!)
- Check of je AI key hebt ingevuld in `.env`

---

## 🚀 STAP 3: START TRADEN! (Nu!)

```bash
start_mt5_trading.bat
```

**Eerste trade komt binnen 15-30 minuten!**

---

## 📊 MONITOR

**MT5 Desktop:**
- Ctrl+T → Terminal
- Tab "Trade" = live posities

**Console:**
- Zie elke AI beslissing
- Real-time reasoning

**Logs:**
```
src\data\mt5_trading_agent\trades_20250206.csv
```

---

## ⚙️ VEILIGE SETTINGS (Al Geconfigureerd)

```
Lot Size: 0.01 (micro lot)
Max Posities: 3
Stop Loss: 50 pips
Take Profit: 100 pips
Interval: Elke 15 minuten
```

**Max risico per trade: ~$50**
**Max totaal risico: ~$150** (3 posities)

Zeer veilig voor $10k account!

---

## 🎯 VERWACHTINGEN DAG 1

- ✅ 2-5 trades
- ✅ Mix BUY/SELL
- ✅ Veel "NOTHING" (AI is selectief - goed!)
- ✅ Eerste trade binnen 30 min mogelijk

---

## 🆘 HULP NODIG?

**"Failed to login"**
→ MT5 Desktop moet **draaien**!

**"No AI key"**
→ Vul GROK_API_KEY in `.env`

**"Symbol not found"**
→ MT5: Ctrl+M → Right-click → Show All

---

## ✅ CHECKLIST

- [ ] MT5 Desktop draait
- [ ] Ingelogd met 5041139909
- [ ] `.env` bestand aangemaakt
- [ ] AI API key toegevoegd
- [ ] Test: `python src/agents/mt5_utils.py` ✅
- [ ] Start: `start_mt5_trading.bat` 🚀

---

**KLAAR? RUN DIT:**

```bash
start_mt5_trading.bat
```

**En je trades beginnen! 💰📈🚀**
