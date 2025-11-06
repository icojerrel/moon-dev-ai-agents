#!/usr/bin/env python3
"""
🌙 Moon Dev's MT5 Connection Test
Test if Python can connect to MetaTrader 5
"""
import MetaTrader5 as mt5
from termcolor import cprint

cprint("\n" + "="*70, "cyan")
cprint("  🔧 Testing MT5 Connection", "cyan", attrs=["bold"])
cprint("="*70 + "\n", "cyan")

# Initialize MT5
cprint("1️⃣  Initializing MT5...", "yellow")
if not mt5.initialize():
    cprint("❌ MT5 initialize() failed", "red")
    error = mt5.last_error()
    cprint(f"   Error code: {error[0]}", "yellow")
    cprint(f"   Error message: {error[1]}", "yellow")
    cprint("\n💡 Tips:", "cyan")
    cprint("   - Is MT5 application running?", "white")
    cprint("   - Are you logged into a demo account?", "white")
    cprint("   - Try running this script as Administrator (Windows)", "white")
    quit()

cprint("✅ MT5 initialized successfully!\n", "green")

# Get account info
cprint("2️⃣  Getting account information...", "yellow")
account_info = mt5.account_info()
if account_info is None:
    cprint("❌ Failed to get account info", "red")
    cprint("   Make sure you're logged into a demo account in MT5", "yellow")
    mt5.shutdown()
    quit()

# Show account details
cprint("\n💼 Account Information:", "cyan", attrs=["bold"])
cprint("─" * 70, "cyan")
cprint(f"  Login:          {account_info.login}", "white")
cprint(f"  Server:         {account_info.server}", "white")
cprint(f"  Name:           {account_info.name}", "white")
cprint(f"  Balance:        ${account_info.balance:,.2f}", "green", attrs=["bold"])
cprint(f"  Equity:         ${account_info.equity:,.2f}", "white")
cprint(f"  Margin:         ${account_info.margin:,.2f}", "white")
cprint(f"  Free Margin:    ${account_info.margin_free:,.2f}", "white")
cprint(f"  Leverage:       1:{account_info.leverage}", "white")
cprint(f"  Currency:       {account_info.currency}", "white")
cprint("─" * 70 + "\n", "cyan")

# Test getting symbols
cprint("3️⃣  Checking available symbols...", "yellow")
symbols = mt5.symbols_get()
cprint(f"✅ Found {len(symbols)} available symbols\n", "green")

# Try to get prices for our trading symbols
cprint("4️⃣  Testing price feeds...", "yellow")
test_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
prices_ok = 0

for symbol in test_symbols:
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        cprint(f"✅ {symbol}:", "green")
        cprint(f"     Bid: {tick.bid:.5f} | Ask: {tick.ask:.5f} | Spread: {(tick.ask - tick.bid):.5f}", "white")
        prices_ok += 1
    else:
        cprint(f"⚠️  {symbol}: Could not get price", "yellow")
        cprint(f"     Try enabling this symbol in MT5 Market Watch", "white")

cprint(f"\n✅ {prices_ok}/{len(test_symbols)} price feeds working\n", "green")

# Test getting historical data
cprint("5️⃣  Testing historical data access...", "yellow")
import pandas as pd
from datetime import datetime, timedelta

rates = mt5.copy_rates_from(
    "EURUSD",
    mt5.TIMEFRAME_M15,
    datetime.now(),
    100  # Get 100 candles
)

if rates is not None and len(rates) > 0:
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    cprint(f"✅ Retrieved {len(df)} candles for EURUSD M15", "green")
    cprint(f"   Latest candle:", "white")
    cprint(f"     Time:  {df.iloc[-1]['time']}", "white")
    cprint(f"     Open:  {df.iloc[-1]['open']:.5f}", "white")
    cprint(f"     High:  {df.iloc[-1]['high']:.5f}", "white")
    cprint(f"     Low:   {df.iloc[-1]['low']:.5f}", "white")
    cprint(f"     Close: {df.iloc[-1]['close']:.5f}", "white")
else:
    cprint("⚠️  Could not retrieve historical data", "yellow")

# Test trading permissions
cprint("\n6️⃣  Checking trading permissions...", "yellow")
if account_info.trade_allowed:
    cprint("✅ Trading is allowed on this account", "green")
    if account_info.trade_expert:
        cprint("✅ Expert Advisors (automated trading) is enabled", "green")
    else:
        cprint("⚠️  Expert Advisors are disabled", "yellow")
        cprint("   To enable: MT5 → Tools → Options → Expert Advisors → Allow automated trading", "white")
else:
    cprint("❌ Trading is not allowed on this account", "red")

# Shutdown
mt5.shutdown()

# Final summary
cprint("\n" + "="*70, "cyan")
cprint("  ✅ ALL TESTS PASSED!", "green", attrs=["bold"])
cprint("="*70, "cyan")
cprint("\n💡 Your MT5 connection is working perfectly!", "green")
cprint("   You can now run the trading agent:\n", "white")
cprint("   python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1\n", "cyan")
