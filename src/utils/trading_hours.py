"""
🌙 Moon Dev's Trading Hours & Volatility Filter
Built with love by Moon Dev 🚀

Intelligent filtering to only trade during optimal market conditions:
- High volatility sessions
- Best trading hours per asset
- Avoid low liquidity periods
- Market session awareness
- Day-of-week filtering
"""

from datetime import datetime, time
from typing import Dict, Tuple, Optional
import pytz
from enum import Enum


class MarketSession(Enum):
    """Market trading sessions"""
    ASIAN = "Asian Session"
    LONDON = "London Session"
    NEW_YORK = "New York Session"
    OVERLAP_LONDON_NY = "London/NY Overlap"
    OFF_HOURS = "Off Hours"


class TradingHoursFilter:
    """
    Filter trades based on optimal market hours and volatility

    Features:
    - Session-based filtering (London, NY, Asian)
    - Asset-specific optimal hours
    - Day-of-week filtering
    - Volatility requirements
    - News event awareness
    """

    def __init__(self):
        """Initialize trading hours filter"""
        # Timezone
        self.utc = pytz.UTC
        self.london_tz = pytz.timezone('Europe/London')
        self.ny_tz = pytz.timezone('America/New_York')
        self.tokyo_tz = pytz.timezone('Asia/Tokyo')
        self.amsterdam_tz = pytz.timezone('Europe/Amsterdam')  # Netherlands timezone

    def get_current_session(self, current_time: Optional[datetime] = None) -> MarketSession:
        """
        Get current market session

        Args:
            current_time: Optional datetime (uses now if None)

        Returns:
            Current market session
        """
        if current_time is None:
            current_time = datetime.now(self.utc)
        elif current_time.tzinfo is None:
            current_time = self.utc.localize(current_time)

        hour = current_time.hour

        # London/NY Overlap (most volatile!)
        # 13:00-17:00 UTC (8am-12pm EST, 1pm-5pm GMT)
        if 13 <= hour < 17:
            return MarketSession.OVERLAP_LONDON_NY

        # London Session (high volume)
        # 08:00-17:00 UTC
        elif 8 <= hour < 17:
            return MarketSession.LONDON

        # New York Session (high volume)
        # 13:00-22:00 UTC
        elif 13 <= hour < 22:
            return MarketSession.NEW_YORK

        # Asian Session (lower volume for most pairs)
        # 00:00-09:00 UTC
        elif 0 <= hour < 9:
            return MarketSession.ASIAN

        # Off hours
        else:
            return MarketSession.OFF_HOURS

    def is_optimal_trading_time(
        self,
        asset_class: str,
        current_time: Optional[datetime] = None,
        strict: bool = True
    ) -> Tuple[bool, str]:
        """
        Check if current time is optimal for trading

        Args:
            asset_class: Asset class (forex, metals, indices, stocks)
            current_time: Optional datetime
            strict: If True, only allow best hours. If False, allow good hours.

        Returns:
            Tuple of (is_optimal, reason)
        """
        if current_time is None:
            current_time = datetime.now(self.utc)
        elif current_time.tzinfo is None:
            current_time = self.utc.localize(current_time)

        session = self.get_current_session(current_time)
        hour = current_time.hour
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday

        # Weekend check (all assets)
        if weekday >= 5:  # Saturday or Sunday
            return False, "Weekend - Markets closed or low liquidity"

        # Asset-specific optimal hours
        if asset_class == 'forex':
            return self._is_optimal_forex_time(session, hour, weekday, strict)

        elif asset_class == 'metals':
            return self._is_optimal_metals_time(session, hour, weekday, strict)

        elif asset_class == 'indices':
            return self._is_optimal_indices_time(session, hour, weekday, strict)

        elif asset_class == 'stocks':
            return self._is_optimal_stocks_time(session, hour, weekday, strict)

        elif asset_class == 'crypto':
            return self._is_optimal_crypto_time(session, hour, weekday, strict)

        # Default: allow trading
        return True, "No specific restrictions for this asset class"

    def _is_optimal_forex_time(
        self,
        session: MarketSession,
        hour: int,
        weekday: int,
        strict: bool
    ) -> Tuple[bool, str]:
        """Check optimal forex trading time"""

        # Avoid Monday early (gaps from weekend)
        if weekday == 0 and hour < 8:
            return False, "Monday early morning - potential weekend gaps"

        # Avoid Friday late (positions held over weekend)
        if weekday == 4 and hour >= 20:
            return False, "Friday evening - avoid weekend risk"

        if strict:
            # STRICT: Only trade during highest volatility
            if session == MarketSession.OVERLAP_LONDON_NY:
                return True, "✅ London/NY Overlap - BEST forex hours (13:00-17:00 UTC)"

            elif session == MarketSession.LONDON and 8 <= hour < 12:
                return True, "✅ London Morning - High forex volatility"

            elif session == MarketSession.NEW_YORK and 13 <= hour < 16:
                return True, "✅ NY Morning - Good forex volatility"

            else:
                return False, "⏸️ Outside optimal forex hours (use strict=False for more flexibility)"

        else:
            # FLEXIBLE: Allow all major sessions
            if session == MarketSession.ASIAN:
                return False, "❌ Asian session - Low forex volatility"

            elif session == MarketSession.OFF_HOURS:
                return False, "❌ Off hours - No major market open"

            else:
                return True, "✅ Major forex session active"

    def _is_optimal_metals_time(
        self,
        session: MarketSession,
        hour: int,
        weekday: int,
        strict: bool
    ) -> Tuple[bool, str]:
        """Check optimal gold/silver trading time"""

        # Gold follows forex sessions but more active during NY
        if strict:
            # STRICT: NY session for gold (most volatile)
            if session == MarketSession.OVERLAP_LONDON_NY:
                return True, "✅ London/NY Overlap - BEST gold hours"

            elif session == MarketSession.NEW_YORK and 13 <= hour < 20:
                return True, "✅ NY Session - High gold volatility"

            else:
                return False, "⏸️ Outside optimal gold hours"

        else:
            # FLEXIBLE: Any major session
            if session == MarketSession.ASIAN:
                return False, "❌ Asian session - Low gold activity"

            elif session == MarketSession.OFF_HOURS:
                return False, "❌ Off hours"

            else:
                return True, "✅ Major session active"

    def _is_optimal_indices_time(
        self,
        session: MarketSession,
        hour: int,
        weekday: int,
        strict: bool
    ) -> Tuple[bool, str]:
        """Check optimal indices trading time"""

        # Indices trade during their regional hours
        if strict:
            # STRICT: Avoid first/last 30 minutes (too volatile/erratic)
            # US indices: 14:30-21:00 UTC (9:30am-4pm EST)

            # Avoid first 30 min
            if hour == 14 and 30 <= datetime.now(self.utc).minute < 60:
                return False, "⏸️ Market just opened - wait 30 min for volatility to settle"

            # Avoid last 30 min
            if hour == 20 and datetime.now(self.utc).minute >= 30:
                return False, "⏸️ Market closing soon - avoid end-of-day volatility"

            # Good trading hours: 15:00-20:00 UTC
            if 15 <= hour < 20:
                return True, "✅ US indices optimal hours (mid-day stable volatility)"

            else:
                return False, "⏸️ Outside optimal indices hours"

        else:
            # FLEXIBLE: Any time market is open
            # US market: 14:30-21:00 UTC
            if 14 <= hour < 21:
                return True, "✅ US indices market hours"
            else:
                return False, "❌ US indices market closed"

    def _is_optimal_stocks_time(
        self,
        session: MarketSession,
        hour: int,
        weekday: int,
        strict: bool
    ) -> Tuple[bool, str]:
        """Check optimal individual stocks trading time"""

        # Same as indices but even stricter
        if strict:
            # Avoid first hour (9:30-10:30 EST = 14:30-15:30 UTC)
            if hour == 14 or (hour == 15 and datetime.now(self.utc).minute < 30):
                return False, "⏸️ First hour - too erratic for stocks"

            # Avoid last hour (3:00-4:00 EST = 20:00-21:00 UTC)
            if hour >= 20:
                return False, "⏸️ Last hour - avoid closing volatility"

            # Good hours: 15:30-19:30 UTC (10:30am-2:30pm EST)
            if 15 <= hour < 20:
                return True, "✅ Stocks optimal hours (mid-day stable)"

            else:
                return False, "⏸️ Outside optimal stock hours"

        else:
            # FLEXIBLE: Market hours
            if 14 <= hour < 21:
                return True, "✅ US stock market hours"
            else:
                return False, "❌ Stock market closed"

    def _is_optimal_crypto_time(
        self,
        session: MarketSession,
        hour: int,
        weekday: int,
        strict: bool
    ) -> Tuple[bool, str]:
        """Check optimal crypto trading time"""

        # Crypto trades 24/7, but volatility varies
        if strict:
            # Higher volatility during US/Europe overlap
            if session == MarketSession.OVERLAP_LONDON_NY:
                return True, "✅ Highest crypto trading volume"

            elif session in [MarketSession.LONDON, MarketSession.NEW_YORK]:
                return True, "✅ Good crypto volatility"

            else:
                return False, "⏸️ Lower crypto activity (Asian session)"

        else:
            # FLEXIBLE: 24/7 trading
            return True, "✅ Crypto trades 24/7"

    def should_avoid_day(self, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Check if we should avoid trading today

        Args:
            current_time: Optional datetime

        Returns:
            Tuple of (should_avoid, reason)
        """
        if current_time is None:
            current_time = datetime.now(self.utc)
        elif current_time.tzinfo is None:
            current_time = self.utc.localize(current_time)

        weekday = current_time.weekday()

        # Weekend
        if weekday >= 5:
            return True, "Weekend - Markets closed"

        # Monday (optional - gaps from weekend)
        if weekday == 0:
            return False, "Monday - Be cautious of weekend gaps (not blocking)"

        # Friday (optional - weekend risk)
        if weekday == 4:
            return False, "Friday - Be cautious of holding over weekend (not blocking)"

        return False, "Normal trading day"

    def get_session_info(self, current_time: Optional[datetime] = None) -> Dict:
        """
        Get complete session information

        Args:
            current_time: Optional datetime

        Returns:
            Dict with session info
        """
        if current_time is None:
            current_time = datetime.now(self.utc)

        session = self.get_current_session(current_time)

        # Convert to Netherlands timezone for display
        nl_time = current_time.astimezone(self.amsterdam_tz)

        return {
            'current_time_utc': current_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'current_time_nl': nl_time.strftime('%Y-%m-%d %H:%M:%S CET/CEST'),
            'session': session.value,
            'hour_utc': current_time.hour,
            'hour_nl': nl_time.hour,
            'weekday': current_time.strftime('%A'),
            'is_weekend': current_time.weekday() >= 5,
        }

    def get_next_optimal_time(
        self,
        asset_class: str,
        current_time: Optional[datetime] = None
    ) -> str:
        """
        Get next optimal trading time

        Args:
            asset_class: Asset class
            current_time: Optional datetime

        Returns:
            Human-readable next optimal time
        """
        if current_time is None:
            current_time = datetime.now(self.utc)

        hour = current_time.hour
        weekday = current_time.weekday()

        if asset_class == 'forex':
            if hour < 8:
                return "Next optimal: 08:00 UTC (London open)"
            elif hour < 13:
                return "Next optimal: 13:00 UTC (London/NY overlap)"
            else:
                return "Next optimal: Tomorrow 08:00 UTC (London open)"

        elif asset_class in ['metals', 'indices', 'stocks']:
            if hour < 14:
                return "Next optimal: 14:30 UTC (US market open)"
            elif hour < 15:
                return "Wait 30 min: 15:00 UTC (post-opening volatility)"
            else:
                return "Next optimal: Tomorrow 14:30 UTC (US market open)"

        else:
            return "Crypto: Trading allowed 24/7"


# Singleton instance
trading_hours_filter = TradingHoursFilter()


# Convenience functions
def is_optimal_trading_time(
    asset_class: str,
    strict: bool = True,
    current_time: Optional[datetime] = None
) -> Tuple[bool, str]:
    """
    Check if current time is optimal for trading

    Args:
        asset_class: Asset class (forex, metals, indices, stocks, crypto)
        strict: If True, only best hours. If False, allow good hours.
        current_time: Optional datetime (uses now if None)

    Returns:
        Tuple of (is_optimal, reason)

    Example:
        >>> is_optimal, reason = is_optimal_trading_time('forex', strict=True)
        >>> if is_optimal:
        >>>     print("✅ Good time to trade!")
        >>> else:
        >>>     print(f"⏸️ Wait: {reason}")
    """
    return trading_hours_filter.is_optimal_trading_time(asset_class, current_time, strict)


def get_current_session() -> MarketSession:
    """Get current market session"""
    return trading_hours_filter.get_current_session()


def get_session_info() -> Dict:
    """Get complete session information"""
    return trading_hours_filter.get_session_info()


if __name__ == "__main__":
    """Test trading hours filter"""
    print("🌙 Testing Trading Hours & Volatility Filter\n")

    filter = TradingHoursFilter()

    # Test current session
    session_info = filter.get_session_info()
    print("📊 Current Session Info:")
    for key, value in session_info.items():
        print(f"  {key}: {value}")

    print("\n" + "="*60)

    # Test optimal times for each asset
    assets = ['forex', 'metals', 'indices', 'stocks', 'crypto']

    print("\n🕐 Optimal Trading Times (STRICT mode):\n")

    for asset in assets:
        is_optimal, reason = filter.is_optimal_trading_time(asset, strict=True)

        status = "✅" if is_optimal else "⏸️"
        print(f"{status} {asset.upper():10} - {reason}")

        if not is_optimal:
            next_time = filter.get_next_optimal_time(asset)
            print(f"   {next_time}")

    print("\n" + "="*60)
    print("\n🕐 Optimal Trading Times (FLEXIBLE mode):\n")

    for asset in assets:
        is_optimal, reason = filter.is_optimal_trading_time(asset, strict=False)

        status = "✅" if is_optimal else "❌"
        print(f"{status} {asset.upper():10} - {reason}")

    print("\n" + "="*60)

    # Test specific times
    print("\n📅 Testing Specific Times:\n")

    test_times = [
        (8, 30, "London Morning"),
        (13, 0, "London/NY Overlap Start"),
        (15, 30, "Mid-afternoon"),
        (20, 45, "Late Evening"),
        (2, 0, "Asian Session"),
    ]

    for hour, minute, description in test_times:
        test_time = datetime.now(pytz.UTC).replace(hour=hour, minute=minute)

        print(f"\n{description} ({hour:02d}:{minute:02d} UTC):")

        for asset in ['forex', 'indices']:
            is_optimal, reason = filter.is_optimal_trading_time(
                asset,
                current_time=test_time,
                strict=True
            )
            status = "✅" if is_optimal else "⏸️"
            print(f"  {status} {asset}: {reason}")

    print("\n✅ Trading hours filter test complete!")
