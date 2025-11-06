#!/usr/bin/env python3
"""
🌙 Moon Dev's Trade Analysis Script
Analyze paper trading performance
"""
import json
import pandas as pd
from termcolor import cprint
from pathlib import Path

trade_file = Path("src/data/mt5_paper/paper_trades.json")

cprint("\n" + "="*70, "cyan")
cprint("  📊 Trade Performance Analysis", "cyan", attrs=["bold"])
cprint("="*70 + "\n", "cyan")

# Check if file exists
if not trade_file.exists():
    cprint("❌ No trade history found!", "red")
    cprint(f"   Looking for: {trade_file}", "yellow")
    cprint("\n💡 Run the agent first to generate trades:", "cyan")
    cprint("   python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1\n", "white")
    exit(1)

# Load data
with open(trade_file) as f:
    data = json.load(f)

initial = data['initial_balance']
current = data['current_balance']
trades = pd.DataFrame(data['trade_history'])

# Account Summary
cprint("💼 ACCOUNT SUMMARY", "cyan", attrs=["bold"])
cprint("─" * 70, "cyan")
cprint(f"  Initial Balance:  ${initial:,.2f}", "white")
cprint(f"  Current Balance:  ${current:,.2f}", "green" if current >= initial else "red", attrs=["bold"])
cprint(f"  Total P/L:        ${current - initial:+,.2f}", "green" if current >= initial else "red")
cprint(f"  Return:           {((current / initial) - 1) * 100:+.2f}%", "green" if current >= initial else "red")
cprint("─" * 70 + "\n", "cyan")

if len(trades) == 0:
    cprint("📭 No trades yet", "yellow")
    cprint("   Agent is waiting for high-confidence SMC setups\n", "white")
    exit(0)

# Separate open and closed
open_trades = trades[trades['status'] == 'OPEN']
closed_trades = trades[trades['status'] == 'CLOSED']

# Open Positions
if len(open_trades) > 0:
    cprint(f"🔄 OPEN POSITIONS ({len(open_trades)})", "yellow", attrs=["bold"])
    cprint("─" * 70, "yellow")
    for _, trade in open_trades.iterrows():
        cprint(f"  #{trade['ticket']} {trade['symbol']} {trade['type']}", "white")
        cprint(f"    Entry:  {trade['open_price']:.5f} @ {trade['open_time']}", "white")
        cprint(f"    Volume: {trade['volume']} lots", "white")
        cprint(f"    SL:     {trade['sl']:.5f} | TP: {trade['tp']:.5f}", "white")
        cprint(f"    P/L:    ${trade.get('profit', 0):+,.2f}", "green" if trade.get('profit', 0) > 0 else "red")
        cprint(f"    Note:   {trade['comment']}", "cyan")
        cprint("")
    cprint("─" * 70 + "\n", "yellow")

# Closed Trades Statistics
if len(closed_trades) > 0:
    cprint(f"📈 CLOSED TRADES STATISTICS ({len(closed_trades)} trades)", "cyan", attrs=["bold"])
    cprint("─" * 70, "cyan")

    # Win/Loss
    winners = closed_trades[closed_trades['profit'] > 0]
    losers = closed_trades[closed_trades['profit'] < 0]
    breakeven = closed_trades[closed_trades['profit'] == 0]

    win_rate = (len(winners) / len(closed_trades)) * 100 if len(closed_trades) > 0 else 0

    cprint(f"  Total Trades:     {len(closed_trades)}", "white")
    cprint(f"  Winners:          {len(winners)} ({len(winners)/len(closed_trades)*100:.1f}%)", "green")
    cprint(f"  Losers:           {len(losers)} ({len(losers)/len(closed_trades)*100:.1f}%)", "red")
    if len(breakeven) > 0:
        cprint(f"  Breakeven:        {len(breakeven)}", "yellow")

    cprint(f"\n  Win Rate:         {win_rate:.1f}%", "green" if win_rate >= 50 else "yellow")

    # P/L Stats
    if len(winners) > 0:
        avg_win = winners['profit'].mean()
        max_win = winners['profit'].max()
        cprint(f"\n  Average Win:      ${avg_win:,.2f}", "green")
        cprint(f"  Largest Win:      ${max_win:,.2f}", "green")

    if len(losers) > 0:
        avg_loss = losers['profit'].mean()
        max_loss = losers['profit'].min()
        cprint(f"\n  Average Loss:     ${avg_loss:,.2f}", "red")
        cprint(f"  Largest Loss:     ${max_loss:,.2f}", "red")

    # Profit Factor
    if len(winners) > 0 and len(losers) > 0:
        gross_profit = winners['profit'].sum()
        gross_loss = abs(losers['profit'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        cprint(f"\n  Gross Profit:     ${gross_profit:,.2f}", "green")
        cprint(f"  Gross Loss:       ${gross_loss:,.2f}", "red")
        cprint(f"  Profit Factor:    {profit_factor:.2f}", "green" if profit_factor >= 1.5 else "yellow")

    # Symbol breakdown
    cprint("\n  Trades by Symbol:", "white")
    symbol_stats = closed_trades.groupby('symbol').agg({
        'profit': ['count', 'sum', 'mean']
    }).round(2)

    for symbol in symbol_stats.index:
        count = int(symbol_stats.loc[symbol, ('profit', 'count')])
        total = symbol_stats.loc[symbol, ('profit', 'sum')]
        avg = symbol_stats.loc[symbol, ('profit', 'mean')]
        cprint(f"    {symbol}:  {count} trades, ${total:+,.2f} total, ${avg:+,.2f} avg",
               "green" if total > 0 else "red")

    cprint("─" * 70 + "\n", "cyan")

    # Recent trades
    cprint("📜 RECENT TRADES (Last 5)", "cyan", attrs=["bold"])
    cprint("─" * 70, "cyan")
    recent = closed_trades.tail(5)
    for _, trade in recent.iterrows():
        color = "green" if trade['profit'] > 0 else "red"
        cprint(f"  {trade['close_time']}  {trade['symbol']} {trade['type']}", "white")
        cprint(f"    ${trade['profit']:+,.2f}  |  {trade['comment']}", color)
    cprint("─" * 70 + "\n", "cyan")

else:
    cprint("📭 No closed trades yet", "yellow")
    cprint(f"   {len(open_trades)} position(s) currently open\n", "white")

# Performance Rating
cprint("🎯 PERFORMANCE RATING", "cyan", attrs=["bold"])
cprint("─" * 70, "cyan")

if len(closed_trades) >= 10:
    rating = []

    if win_rate >= 60:
        rating.append("⭐⭐⭐ Excellent win rate!")
    elif win_rate >= 50:
        rating.append("⭐⭐ Good win rate")
    else:
        rating.append("⭐ Win rate needs improvement")

    if len(winners) > 0 and len(losers) > 0:
        profit_factor = winners['profit'].sum() / abs(losers['profit'].sum())
        if profit_factor >= 2.0:
            rating.append("⭐⭐⭐ Excellent profit factor!")
        elif profit_factor >= 1.5:
            rating.append("⭐⭐ Good profit factor")
        else:
            rating.append("⭐ Profit factor needs improvement")

    return_pct = ((current / initial) - 1) * 100
    if return_pct >= 20:
        rating.append("⭐⭐⭐ Outstanding returns!")
    elif return_pct >= 10:
        rating.append("⭐⭐ Good returns")
    elif return_pct >= 0:
        rating.append("⭐ Positive returns")
    else:
        rating.append("❌ Negative returns")

    for r in rating:
        cprint(f"  {r}", "white")

else:
    cprint("  ⏳ Need at least 10 closed trades for rating", "yellow")

cprint("─" * 70 + "\n", "cyan")

# Recommendations
cprint("💡 RECOMMENDATIONS", "cyan", attrs=["bold"])
cprint("─" * 70, "cyan")

if len(closed_trades) < 20:
    cprint("  • Continue paper trading to gather more data (target: 50+ trades)", "white")

if len(closed_trades) >= 20:
    if win_rate >= 55:
        cprint("  • ✅ Win rate is solid! Consider live trading with small positions", "green")
    else:
        cprint("  • ⚠️  Win rate below target. Review SMC setups and AI decisions", "yellow")

    if len(winners) > 0 and len(losers) > 0:
        avg_win = winners['profit'].mean()
        avg_loss = abs(losers['profit'].mean())
        if avg_win / avg_loss >= 2.5:
            cprint("  • ✅ Excellent risk:reward ratio!", "green")
        elif avg_win / avg_loss >= 2.0:
            cprint("  • ✅ Good risk:reward ratio", "green")
        else:
            cprint("  • ⚠️  Consider increasing take profit targets (aim for 3R)", "yellow")

if ((current / initial) - 1) * 100 >= 15:
    cprint("  • 🚀 Strong performance! Consider scaling position sizes gradually", "green")

cprint("─" * 70 + "\n", "cyan")

cprint("🌙 Analysis complete!\n", "cyan", attrs=["bold"])
