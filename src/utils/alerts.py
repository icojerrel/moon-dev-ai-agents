"""
🌙 Moon Dev's Alerting System
Built with love by Moon Dev 🚀

Multi-channel alerting for:
- Telegram notifications
- Discord webhooks
- Email alerts
- Trade notifications
- Error alerts
- System health alerts
"""

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "ℹ️ INFO"
    SUCCESS = "✅ SUCCESS"
    WARNING = "⚠️ WARNING"
    ERROR = "❌ ERROR"
    CRITICAL = "🚨 CRITICAL"
    TRADE = "💹 TRADE"


class AlertManager:
    """Centralized alert management"""

    def __init__(self):
        # Telegram configuration
        self.telegram_enabled = os.getenv('TELEGRAM_ALERTS_ENABLED', 'false').lower() == 'true'
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

        # Discord configuration
        self.discord_enabled = os.getenv('DISCORD_ALERTS_ENABLED', 'false').lower() == 'true'
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')

        # Email configuration
        self.email_enabled = os.getenv('EMAIL_ALERTS_ENABLED', 'false').lower() == 'true'
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email_from = os.getenv('EMAIL_FROM', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.email_to = os.getenv('EMAIL_TO', '')

        # Alert level filtering
        self.min_level = AlertLevel[os.getenv('MIN_ALERT_LEVEL', 'INFO')]

    def send_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        title: Optional[str] = None,
        data: Optional[Dict] = None,
        channels: Optional[List[str]] = None
    ):
        """
        Send alert to configured channels

        Args:
            message: Alert message
            level: Alert severity level
            title: Optional title (defaults to level name)
            data: Optional structured data
            channels: Optional list of channels ('telegram', 'discord', 'email')
                     If None, sends to all enabled channels
        """
        # Check if alert level is high enough
        alert_levels = list(AlertLevel)
        if alert_levels.index(level) < alert_levels.index(self.min_level):
            return

        # Default title
        if title is None:
            title = level.value

        # Determine channels
        if channels is None:
            channels = []
            if self.telegram_enabled:
                channels.append('telegram')
            if self.discord_enabled:
                channels.append('discord')
            if self.email_enabled:
                channels.append('email')

        # Send to each channel
        for channel in channels:
            try:
                if channel == 'telegram' and self.telegram_enabled:
                    self._send_telegram(message, level, title, data)
                elif channel == 'discord' and self.discord_enabled:
                    self._send_discord(message, level, title, data)
                elif channel == 'email' and self.email_enabled:
                    self._send_email(message, level, title, data)
            except Exception as e:
                print(f"Failed to send {channel} alert: {str(e)}")

    def _send_telegram(
        self,
        message: str,
        level: AlertLevel,
        title: str,
        data: Optional[Dict]
    ):
        """Send Telegram message"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return

        # Format message
        text = f"<b>{title}</b>\n\n{message}"

        if data:
            text += "\n\n<b>Details:</b>\n"
            for key, value in data.items():
                text += f"• {key}: {value}\n"

        text += f"\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"

        # Send request
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

    def _send_discord(
        self,
        message: str,
        level: AlertLevel,
        title: str,
        data: Optional[Dict]
    ):
        """Send Discord webhook message"""
        if not self.discord_webhook_url:
            return

        # Color coding based on level
        color_map = {
            AlertLevel.INFO: 0x3498db,      # Blue
            AlertLevel.SUCCESS: 0x2ecc71,   # Green
            AlertLevel.WARNING: 0xf39c12,   # Orange
            AlertLevel.ERROR: 0xe74c3c,     # Red
            AlertLevel.CRITICAL: 0x992d22,  # Dark red
            AlertLevel.TRADE: 0x9b59b6,     # Purple
        }

        # Build embed
        embed = {
            'title': title,
            'description': message,
            'color': color_map.get(level, 0x95a5a6),
            'timestamp': datetime.utcnow().isoformat(),
            'footer': {
                'text': '🌙 Moon Dev AI Agents'
            }
        }

        # Add fields for data
        if data:
            embed['fields'] = [
                {'name': key, 'value': str(value), 'inline': True}
                for key, value in data.items()
            ]

        # Send request
        payload = {
            'embeds': [embed],
            'username': 'Moon Dev Alerts'
        }

        response = requests.post(self.discord_webhook_url, json=payload, timeout=10)
        response.raise_for_status()

    def _send_email(
        self,
        message: str,
        level: AlertLevel,
        title: str,
        data: Optional[Dict]
    ):
        """Send email alert"""
        if not self.email_from or not self.email_to or not self.email_password:
            return

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[Moon Dev Alerts] {title}"
        msg['From'] = self.email_from
        msg['To'] = self.email_to

        # HTML body
        html = f"""
        <html>
        <head></head>
        <body>
            <h2>{title}</h2>
            <p>{message}</p>
        """

        if data:
            html += "<h3>Details:</h3><ul>"
            for key, value in data.items():
                html += f"<li><strong>{key}:</strong> {value}</li>"
            html += "</ul>"

        html += f"""
            <hr>
            <p><em>Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</em></p>
            <p><em>🌙 Moon Dev AI Trading System</em></p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # Send via SMTP
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)

    def trade_alert(
        self,
        action: str,
        symbol: str,
        amount: float,
        price: float,
        **kwargs
    ):
        """
        Send trade execution alert

        Args:
            action: Trade action (BUY/SELL/CLOSE)
            symbol: Trading symbol
            amount: Trade amount
            price: Execution price
            **kwargs: Additional trade data
        """
        # Build message
        if action == 'BUY':
            emoji = '🟢'
        elif action == 'SELL':
            emoji = '🔴'
        else:
            emoji = '⚪'

        message = f"{emoji} <b>{action}</b> {amount} {symbol} @ {price}"

        # Add optional data
        data = {
            'Symbol': symbol,
            'Action': action,
            'Amount': amount,
            'Price': price,
        }

        # Add extra fields
        for key, value in kwargs.items():
            data[key.replace('_', ' ').title()] = value

        self.send_alert(
            message=message,
            level=AlertLevel.TRADE,
            title=f"💹 Trade Executed: {action} {symbol}",
            data=data
        )

    def error_alert(
        self,
        error: str,
        context: Optional[str] = None,
        exception: Optional[Exception] = None
    ):
        """
        Send error alert

        Args:
            error: Error message
            context: Optional context (e.g., agent name, function)
            exception: Optional exception object
        """
        message = error

        data = {}
        if context:
            data['Context'] = context

        if exception:
            data['Exception Type'] = type(exception).__name__
            data['Exception Message'] = str(exception)

        self.send_alert(
            message=message,
            level=AlertLevel.ERROR,
            title="❌ Error Occurred",
            data=data
        )

    def system_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        **data
    ):
        """
        Send system alert

        Args:
            message: Alert message
            level: Alert level
            **data: Additional data fields
        """
        self.send_alert(
            message=message,
            level=level,
            data=data if data else None
        )

    def health_check_failed(
        self,
        component: str,
        reason: str,
        **data
    ):
        """
        Send health check failure alert

        Args:
            component: Component that failed (e.g., 'Database', 'API')
            reason: Failure reason
            **data: Additional diagnostic data
        """
        message = f"Health check failed for <b>{component}</b>\n\nReason: {reason}"

        alert_data = {
            'Component': component,
            'Reason': reason,
            **data
        }

        self.send_alert(
            message=message,
            level=AlertLevel.CRITICAL,
            title=f"🚨 Health Check Failed: {component}",
            data=alert_data
        )


# Singleton instance
alert_manager = AlertManager()


# Convenience functions
def send_alert(message: str, level: AlertLevel = AlertLevel.INFO, **kwargs):
    """Send alert to all enabled channels"""
    alert_manager.send_alert(message, level, **kwargs)


def trade_alert(action: str, symbol: str, amount: float, price: float, **kwargs):
    """Send trade execution alert"""
    alert_manager.trade_alert(action, symbol, amount, price, **kwargs)


def error_alert(error: str, context: Optional[str] = None, exception: Optional[Exception] = None):
    """Send error alert"""
    alert_manager.error_alert(error, context, exception)


def system_alert(message: str, level: AlertLevel = AlertLevel.INFO, **data):
    """Send system alert"""
    alert_manager.system_alert(message, level, **data)


if __name__ == "__main__":
    """Test alerting system"""
    print("🌙 Testing Moon Dev Alerting System\n")

    # Check configuration
    if not alert_manager.telegram_enabled and not alert_manager.discord_enabled:
        print("⚠️  No alert channels configured!")
        print("\nTo test alerts, set these environment variables:")
        print("  TELEGRAM_ALERTS_ENABLED=true")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  TELEGRAM_CHAT_ID=your_chat_id")
        print("\nOr for Discord:")
        print("  DISCORD_ALERTS_ENABLED=true")
        print("  DISCORD_WEBHOOK_URL=your_webhook_url")
        exit(1)

    # Test different alert types
    print("Sending test alerts...\n")

    # Info alert
    send_alert(
        "System started successfully",
        level=AlertLevel.SUCCESS,
        title="✅ System Started"
    )

    # Trade alert
    trade_alert(
        action='BUY',
        symbol='EURUSD',
        amount=0.01,
        price=1.0850,
        sl=1.0800,
        tp=1.0900,
        confidence=85,
        reasoning="Strong bullish momentum"
    )

    # Error alert
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_alert(
            "Test error occurred during startup",
            context="Test Script",
            exception=e
        )

    # System alert
    system_alert(
        "High memory usage detected",
        level=AlertLevel.WARNING,
        memory_usage="85%",
        available_memory="1.2 GB"
    )

    print("\n✅ Test alerts sent!")
    print("Check your Telegram/Discord to verify delivery.")
