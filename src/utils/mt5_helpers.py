"""
🌙 Moon Dev's MT5 Helper Utilities
Built with love by Moon Dev 🚀

Helper functions for MT5 multi-asset trading
"""

from typing import Dict, Tuple


def detect_asset_class(symbol: str) -> str:
    """
    Detect asset class from symbol name

    Args:
        symbol: Trading symbol (e.g., 'EURUSD', 'XAUUSD', 'US30')

    Returns:
        Asset class: 'forex', 'metals', 'indices', 'stocks', 'energies', 'crypto'
    """
    symbol = symbol.upper()

    # Forex pairs (6-7 characters, currency codes)
    forex_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF']
    if len(symbol) in [6, 7]:
        # Check if first 3 and last 3 are currency codes
        if symbol[:3] in forex_currencies and symbol[-3:] in forex_currencies:
            return 'forex'

    # Precious metals (start with X)
    if symbol.startswith('XAU') or symbol.startswith('XAG') or \
       symbol.startswith('XPT') or symbol.startswith('XPD'):
        return 'metals'

    # Energies (oil, gas)
    if symbol.startswith('XTI') or symbol.startswith('XBR') or symbol.startswith('XNG'):
        return 'energies'

    # Indices (contain numbers or known index prefixes)
    index_prefixes = ['US', 'NAS', 'SPX', 'UK', 'GER', 'FRA', 'JPN', 'AUS', 'HK']
    for prefix in index_prefixes:
        if symbol.startswith(prefix):
            return 'indices'

    # Crypto (BTC, ETH, etc.)
    crypto_symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE']
    for crypto in crypto_symbols:
        if crypto in symbol:
            return 'crypto'

    # Individual stocks (if none of above, assume stocks)
    # Most stocks are 1-5 letter symbols
    if len(symbol) <= 5 and symbol.isalpha():
        return 'stocks'

    # Default to forex
    return 'forex'


def get_asset_params(symbol: str, config_module) -> Dict:
    """
    Get asset-specific parameters from config

    Args:
        symbol: Trading symbol
        config_module: Config module (import src.config)

    Returns:
        Dict with asset-specific parameters
    """
    asset_class = detect_asset_class(symbol)

    # Get position size
    position_size = config_module.MT5_POSITION_SIZES.get(
        asset_class,
        0.01
    )

    # Get risk params
    risk_params = config_module.MT5_RISK_PARAMS.get(
        asset_class,
        {
            'max_spread_pips': 10,
            'min_stop_loss_pips': 20,
            'max_stop_loss_pips': 100,
            'default_tp_ratio': 2.0,
        }
    )

    # Get timeframe
    timeframe = config_module.MT5_TIMEFRAMES.get(
        asset_class,
        '1H'
    )

    return {
        'asset_class': asset_class,
        'position_size': position_size,
        'timeframe': timeframe,
        **risk_params
    }


def calculate_position_size(
    symbol: str,
    account_balance: float,
    risk_percent: float,
    stop_loss_pips: float,
    asset_class: str = None
) -> float:
    """
    Calculate position size based on risk management

    Args:
        symbol: Trading symbol
        account_balance: Account balance in USD
        risk_percent: Risk per trade as % (e.g., 1.0 = 1%)
        stop_loss_pips: Stop loss distance in pips
        asset_class: Asset class (auto-detected if None)

    Returns:
        Position size in lots
    """
    if asset_class is None:
        asset_class = detect_asset_class(symbol)

    # Risk amount in USD
    risk_amount = account_balance * (risk_percent / 100)

    # Pip values per lot (approximate)
    pip_values = {
        'forex': 10,      # $10 per pip for 1 standard lot
        'metals': 100,    # Gold: $100 per pip for 1 lot
        'indices': 10,    # Varies by index
        'stocks': 1,      # $1 per point per share
        'energies': 10,   # Oil: $10 per pip for 1 lot
        'crypto': 10,     # BTC: varies widely
    }

    pip_value = pip_values.get(asset_class, 10)

    # Position size = Risk / (SL pips * pip value)
    position_size = risk_amount / (stop_loss_pips * pip_value)

    # Round to standard lot sizes
    if asset_class == 'stocks':
        return max(1, round(position_size))  # Minimum 1 share
    elif asset_class in ['forex', 'metals', 'energies', 'crypto']:
        return round(position_size, 2)  # 0.01 lot precision
    else:
        return round(position_size, 1)  # 0.1 lot precision for indices


def format_asset_name(symbol: str) -> Tuple[str, str]:
    """
    Format asset name for display

    Args:
        symbol: Trading symbol

    Returns:
        Tuple of (formatted_name, emoji)
    """
    asset_class = detect_asset_class(symbol)

    # Asset class emojis
    emojis = {
        'forex': '💱',
        'metals': '🏆',
        'indices': '📈',
        'stocks': '📊',
        'energies': '⚡',
        'crypto': '🪙',
    }

    # Format names
    names = {
        'EURUSD': 'EUR/USD',
        'GBPUSD': 'GBP/USD',
        'USDJPY': 'USD/JPY',
        'AUDUSD': 'AUD/USD',
        'USDCAD': 'USD/CAD',
        'NZDUSD': 'NZD/USD',
        'XAUUSD': 'Gold',
        'XAGUSD': 'Silver',
        'US30': 'Dow Jones',
        'NAS100': 'NASDAQ 100',
        'SPX500': 'S&P 500',
        'UK100': 'FTSE 100',
        'GER40': 'DAX 40',
    }

    formatted_name = names.get(symbol, symbol)
    emoji = emojis.get(asset_class, '📊')

    return formatted_name, emoji


def get_market_context(symbol: str, asset_class: str = None) -> str:
    """
    Get market context for AI analysis

    Args:
        symbol: Trading symbol
        asset_class: Asset class (auto-detected if None)

    Returns:
        Market context string for AI prompt
    """
    if asset_class is None:
        asset_class = detect_asset_class(symbol)

    contexts = {
        'forex': """
This is a forex (currency) pair. Key factors to consider:
- Central bank policies and interest rate differentials
- Economic data releases (GDP, employment, inflation)
- Geopolitical events affecting currencies
- Risk sentiment (safe haven vs risk currencies)
- Correlation with commodity prices and stock markets
- Trading sessions (London, New York, Asian overlaps)
""",
        'metals': """
This is a precious metal (commodity). Key factors to consider:
- US Dollar strength (inverse correlation with gold)
- Real interest rates and inflation expectations
- Central bank monetary policy
- Geopolitical risk and safe-haven demand
- Jewelry and industrial demand
- Mining supply dynamics
- Technical support/resistance levels
""",
        'indices': """
This is a stock market index. Key factors to consider:
- Overall stock market sentiment and risk appetite
- Economic growth indicators (GDP, PMI)
- Corporate earnings season
- Central bank policy (QE, rate changes)
- Sector rotation and leadership
- Volatility (VIX) levels
- Correlation with bonds and commodities
""",
        'stocks': """
This is an individual stock. Key factors to consider:
- Company-specific news and earnings
- Sector performance and rotation
- Overall market trend
- Technical price action
- Volume and liquidity
- Support/resistance levels
- Relative strength vs market
""",
        'energies': """
This is an energy commodity (oil/gas). Key factors to consider:
- Supply/demand dynamics (OPEC, production data)
- Geopolitical events (Middle East, Russia, etc.)
- Economic growth indicators
- US Dollar strength
- Inventory reports (EIA, API)
- Seasonal patterns
- Alternative energy trends
""",
        'crypto': """
This is a cryptocurrency. Key factors to consider:
- Overall crypto market sentiment
- Bitcoin dominance and correlation
- On-chain metrics and whale activity
- Regulatory news and developments
- Technical levels and trends
- Volume and liquidity
- Market manipulation risks
""",
    }

    return contexts.get(asset_class, "")


if __name__ == "__main__":
    """Test MT5 helpers"""
    print("🌙 Testing MT5 Helper Functions\n")

    # Test asset detection
    test_symbols = [
        'EURUSD', 'GBPUSD', 'XAUUSD', 'XAGUSD',
        'US30', 'NAS100', 'SPX500',
        'AAPL', 'TSLA', 'GOOGL',
        'BTCUSD', 'ETHUSD'
    ]

    for symbol in test_symbols:
        asset_class = detect_asset_class(symbol)
        name, emoji = format_asset_name(symbol)
        print(f"{emoji} {symbol:10} → {asset_class:10} ({name})")

    # Test position sizing
    print("\n💰 Position Size Calculation:")
    print(f"  Account: $10,000")
    print(f"  Risk: 1% ($100)")
    print(f"  SL: 50 pips")

    for symbol in ['EURUSD', 'XAUUSD', 'US30']:
        size = calculate_position_size(symbol, 10000, 1.0, 50)
        asset = detect_asset_class(symbol)
        print(f"  {symbol}: {size} lots ({asset})")
