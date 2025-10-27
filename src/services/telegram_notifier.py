#!/usr/bin/env python3
"""
🌙 Moon Dev's Telegram Notifier 🌙

Send real-time trading alerts to Telegram

Setup:
    1. Create Telegram bot with @BotFather
    2. Get bot token
    3. Get your chat ID (send /start to @userinfobot)
    4. Add to .env:
       TELEGRAM_BOT_TOKEN=your_bot_token
       TELEGRAM_CHAT_ID=your_chat_id

Usage:
    from src.services.telegram_notifier import TelegramNotifier

    notifier = TelegramNotifier()
    await notifier.send_alert("🚀 SOL just pumped 10%!")
"""

import os
import asyncio
import aiohttp
from typing import Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()


class TelegramNotifier:
    """
    Send trading alerts to Telegram

    Supports:
    - Price alerts
    - Trade notifications
    - Risk warnings
    - System status updates
    """

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.enabled = bool(self.bot_token and self.chat_id)

        if not self.enabled:
            print("⚠️  Telegram notifier disabled (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send message to Telegram

        Args:
            text: Message text (supports HTML or Markdown)
            parse_mode: "HTML" or "Markdown"

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/sendMessage"

                payload = {
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': parse_mode
                }

                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error = await response.text()
                        print(f"❌ Telegram send failed: {error}")
                        return False

        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False

    async def send_alert(self, message: str, level: str = "INFO"):
        """
        Send alert with emoji prefix

        Args:
            message: Alert message
            level: "INFO", "WARNING", "ERROR", "SUCCESS"
        """
        emojis = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅"
        }

        emoji = emojis.get(level, "📢")
        timestamp = datetime.now().strftime("%H:%M:%S")

        formatted = f"{emoji} <b>{level}</b>\n{message}\n\n<i>{timestamp}</i>"

        await self.send_message(formatted)

    async def send_price_alert(self, token: str, price: float, change_pct: float):
        """
        Send price movement alert

        Args:
            token: Token symbol
            price: Current price
            change_pct: Percentage change
        """
        emoji = "🚀" if change_pct > 0 else "📉"
        sign = "+" if change_pct > 0 else ""

        message = f"""
{emoji} <b>Price Alert: {token}</b>

Current: ${price:.4f}
Change: {sign}{change_pct:.2f}%
Time: {datetime.now().strftime("%H:%M:%S")}
"""

        level = "SUCCESS" if abs(change_pct) > 5 else "WARNING"
        await self.send_alert(message, level)

    async def send_trade_notification(self, action: str, token: str, amount: float,
                                     price: float, total_usd: float):
        """
        Send trade execution notification

        Args:
            action: "BUY" or "SELL"
            token: Token symbol
            amount: Amount traded
            price: Execution price
            total_usd: Total USD value
        """
        emoji = "🟢" if action == "BUY" else "🔴"

        message = f"""
{emoji} <b>{action} Executed</b>

Token: {token}
Amount: {amount:.4f}
Price: ${price:.4f}
Total: ${total_usd:.2f}

Time: {datetime.now().strftime("%H:%M:%S")}
"""

        await self.send_alert(message, "SUCCESS")

    async def send_risk_warning(self, warning_type: str, details: str):
        """
        Send risk management warning

        Args:
            warning_type: Type of risk warning
            details: Additional details
        """
        message = f"""
🚨 <b>RISK WARNING</b>

Type: {warning_type}
Details: {details}

Action: Review positions immediately
Time: {datetime.now().strftime("%H:%M:%S")}
"""

        await self.send_alert(message, "ERROR")

    async def send_system_status(self, status: str, metrics: dict):
        """
        Send system status update

        Args:
            status: Overall status ("RUNNING", "STOPPED", "ERROR")
            metrics: Performance metrics dict
        """
        emoji = "✅" if status == "RUNNING" else "⚠️"

        metrics_text = "\n".join([f"  • {k}: {v}" for k, v in metrics.items()])

        message = f"""
{emoji} <b>System Status: {status}</b>

Metrics:
{metrics_text}

Time: {datetime.now().strftime("%H:%M:%S")}
"""

        level = "SUCCESS" if status == "RUNNING" else "WARNING"
        await self.send_alert(message, level)

    async def send_daily_summary(self, pnl: float, trades: int, win_rate: float,
                                best_trade: str, worst_trade: str):
        """
        Send daily trading summary

        Args:
            pnl: Total PnL for the day
            trades: Number of trades
            win_rate: Win rate percentage
            best_trade: Best trade description
            worst_trade: Worst trade description
        """
        emoji = "🎉" if pnl > 0 else "😔"

        message = f"""
{emoji} <b>Daily Summary</b>

PnL: ${pnl:+.2f}
Trades: {trades}
Win Rate: {win_rate:.1f}%

Best Trade: {best_trade}
Worst Trade: {worst_trade}

Date: {datetime.now().strftime("%Y-%m-%d")}
"""

        level = "SUCCESS" if pnl > 0 else "INFO"
        await self.send_alert(message, level)


# Example usage and testing
async def test_telegram_notifier():
    """Test Telegram notifier"""
    notifier = TelegramNotifier()

    if not notifier.enabled:
        print("❌ Telegram not configured")
        print("\nSetup instructions:")
        print("1. Create bot with @BotFather")
        print("2. Get chat ID from @userinfobot")
        print("3. Add to .env:")
        print("   TELEGRAM_BOT_TOKEN=your_token")
        print("   TELEGRAM_CHAT_ID=your_chat_id")
        return

    print("🧪 Testing Telegram notifier...")

    # Test basic message
    await notifier.send_message("🌙 Moon Dev Trading Bot - Test Message")

    # Test price alert
    await notifier.send_price_alert("SOL", 145.50, 5.2)

    # Test trade notification
    await notifier.send_trade_notification("BUY", "SOL", 10.0, 145.50, 1455.00)

    # Test risk warning
    await notifier.send_risk_warning(
        "MAX_LOSS_EXCEEDED",
        "Daily loss limit of $1000 reached. Trading halted."
    )

    # Test system status
    await notifier.send_system_status("RUNNING", {
        "Uptime": "2h 34m",
        "Trades": 5,
        "PnL": "+$234.56",
        "Errors": 0
    })

    print("✅ Test messages sent!")


if __name__ == "__main__":
    asyncio.run(test_telegram_notifier())
