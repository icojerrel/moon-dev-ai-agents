"""
🌙 Moon Dev's Configuration File
Built with love by Moon Dev 🚀
"""

# 💰 Trading Configuration
USDC_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # Never trade or close
SOL_ADDRESS = "So11111111111111111111111111111111111111111"   # Never trade or close

# Create a list of addresses to exclude from trading/closing
EXCLUDED_TOKENS = [USDC_ADDRESS, SOL_ADDRESS]

# Token List for Trading 📋
MONITORED_TOKENS = [
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump',    # 🌬️ FART
    # 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',    # 💵 USDC
    'HeLp6NuQkmYB4pYWo2zYs22mESHXPQYzXbB8n4V98jwC',    # 🤖 AI16Z
    # 'v62Jv9pwMTREWV9f6TetZfMafV254vo99p7HSF25BPr',     # 🎮 GG Solana
    # 'KENJSUYLASHUMfHyy5o4Hp2FdNqZg1AsUPhfH2kYvEP',   # GRIFFAIN
    # '8x5VqbHA8D7NkD52uNuS5nnt3PwA3pLD34ymskeSo2Wn',    # 🧠 ZEREBRO
    # 'Df6yfrKC8kZE3KNkrHERKzAetSxbrWeniQfyJY4Jpump',    # 😎 CHILL GUY
    # 'ED5nyyWEzpPPiWimP8vYm7sD7TD3LAt3Q3gRTWHzPJBY',    # 🌙 MOODENG
    # 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',    # 🐕 WIF
]

# Moon Dev's Token Trading List 🚀
# Each token is carefully selected by Moon Dev for maximum moon potential! 🌙
tokens_to_trade = MONITORED_TOKENS  # Using the same list for trading

# Token and wallet settings
symbol = '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'
address = '4wgfCBf2WwLSRKLef9iW7JXZ2AfkxUxGM4XcKpHm3Sin' # YOUR WALLET ADDRESS HERE

# Position sizing 🎯
usd_size = 25  # Size of position to hold
max_usd_order_size = 3  # Max order size
tx_sleep = 30  # Sleep between transactions
slippage = 199  # Slippage settings

# Risk Management Settings 🛡️
CASH_PERCENTAGE = 20  # Minimum % to keep in USDC as safety buffer (0-100)
MAX_POSITION_PERCENTAGE = 30  # Maximum % allocation per position (0-100)
STOPLOSS_PRICE = 1 # NOT USED YET 1/5/25    
BREAKOUT_PRICE = .0001 # NOT USED YET 1/5/25
SLEEP_AFTER_CLOSE = 600  # Prevent overtrading

MAX_LOSS_GAIN_CHECK_HOURS = 12  # How far back to check for max loss/gain limits (in hours)
SLEEP_BETWEEN_RUNS_MINUTES = 15  # How long to sleep between agent runs 🕒


# Max Loss/Gain Settings FOR RISK AGENT 1/5/25
USE_PERCENTAGE = False  # If True, use percentage-based limits. If False, use USD-based limits

# USD-based limits (used if USE_PERCENTAGE is False)
MAX_LOSS_USD = 25  # Maximum loss in USD before stopping trading
MAX_GAIN_USD = 25 # Maximum gain in USD before stopping trading

# USD MINIMUM BALANCE RISK CONTROL
MINIMUM_BALANCE_USD = 50  # If balance falls below this, risk agent will consider closing all positions
USE_AI_CONFIRMATION = True  # If True, consult AI before closing positions. If False, close immediately on breach

# Percentage-based limits (used if USE_PERCENTAGE is True)
MAX_LOSS_PERCENT = 5  # Maximum loss as percentage (e.g., 20 = 20% loss)
MAX_GAIN_PERCENT = 5  # Maximum gain as percentage (e.g., 50 = 50% gain)

# Transaction settings ⚡
slippage = 199  # 500 = 5% and 50 = .5% slippage
PRIORITY_FEE = 100000  # ~0.02 USD at current SOL prices
orders_per_open = 3  # Multiple orders for better fill rates

# Market maker settings 📊
buy_under = .0946
sell_over = 1

# Data collection settings 📈
DAYSBACK_4_DATA = 3
DATA_TIMEFRAME = '1H'  # 1m, 3m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 8H, 12H, 1D, 3D, 1W, 1M
SAVE_OHLCV_DATA = False  # 🌙 Set to True to save data permanently, False will only use temp data during run

# AI Model Settings 🤖
AI_MODEL = "claude-3-haiku-20240307"  # Model Options:
                                     # - claude-3-haiku-20240307 (Fast, efficient Claude model)
                                     # - claude-3-sonnet-20240229 (Balanced Claude model)
                                     # - claude-3-opus-20240229 (Most powerful Claude model)
AI_MAX_TOKENS = 1024  # Max tokens for response
AI_TEMPERATURE = 0.7  # Creativity vs precision (0-1)

# Trading Strategy Agent Settings - MAY NOT BE USED YET 1/5/25
ENABLE_STRATEGIES = True  # Set this to True to use strategies
STRATEGY_MIN_CONFIDENCE = 0.7  # Minimum confidence to act on strategy signals

# Sleep time between main agent runs
SLEEP_BETWEEN_RUNS_MINUTES = 15  # How long to sleep between agent runs 🕒

# in our nice_funcs in token over view we look for minimum trades last hour
MIN_TRADES_LAST_HOUR = 2


# Real-Time Clips Agent Settings 🎬
REALTIME_CLIPS_ENABLED = True
REALTIME_CLIPS_OBS_FOLDER = os.path.expanduser('~/Videos/OBS')  # OBS recording folder (cross-platform)
REALTIME_CLIPS_AUTO_INTERVAL = 120  # Check every N seconds (120 = 2 minutes)
REALTIME_CLIPS_LENGTH = 2  # Minutes to analyze per check
REALTIME_CLIPS_AI_MODEL = 'groq'  # Model type: groq, openai, claude, deepseek, xai, ollama
REALTIME_CLIPS_AI_MODEL_NAME = None  # None = use default for model type
REALTIME_CLIPS_TWITTER = True  # Auto-open Twitter compose after clip

# MetaTrader 5 Settings 💹
MT5_ENABLED = True  # Enable MT5 trading agent ✅

# Multi-Asset Trading Configuration
# Choose symbols from different asset classes based on your broker

# 🌍 FOREX PAIRS (Currency Trading)
MT5_FOREX_PAIRS = [
    'EURUSD',   # Euro vs US Dollar (most liquid)
    'GBPUSD',   # British Pound vs US Dollar (Cable)
    'USDJPY',   # US Dollar vs Japanese Yen
    'AUDUSD',   # Australian Dollar vs US Dollar (Aussie)
    'USDCAD',   # US Dollar vs Canadian Dollar (Loonie)
    'NZDUSD',   # New Zealand Dollar vs US Dollar (Kiwi)
    # 'USDCHF',   # US Dollar vs Swiss Franc
    # 'EURGBP',   # Euro vs British Pound
    # 'EURJPY',   # Euro vs Japanese Yen
]

# 🏆 PRECIOUS METALS (Commodities)
MT5_METALS = [
    'XAUUSD',   # Gold vs US Dollar (most popular)
    # 'XAGUSD',   # Silver vs US Dollar
    # 'XPTUSD',   # Platinum vs US Dollar
    # 'XPDUSD',   # Palladium vs US Dollar
]

# 📈 INDICES (Stock Market Indices)
MT5_INDICES = [
    'US30',     # Dow Jones Industrial Average (US stocks)
    'NAS100',   # NASDAQ 100 (tech stocks)
    'SPX500',   # S&P 500 (US large cap)
    # 'UK100',    # FTSE 100 (UK stocks)
    # 'GER40',    # DAX 40 (German stocks)
    # 'FRA40',    # CAC 40 (French stocks)
    # 'JPN225',   # Nikkei 225 (Japanese stocks)
    # 'AUS200',   # ASX 200 (Australian stocks)
]

# 📊 INDIVIDUAL STOCKS (if your broker supports)
MT5_STOCKS = [
    # US Tech Stocks (check exact symbols with your broker)
    # 'AAPL',     # Apple Inc.
    # 'MSFT',     # Microsoft Corporation
    # 'GOOGL',    # Alphabet Inc.
    # 'AMZN',     # Amazon.com Inc.
    # 'TSLA',     # Tesla Inc.
    # 'NVDA',     # NVIDIA Corporation
    # 'META',     # Meta Platforms Inc.
]

# ⚡ ENERGIES (Oil, Gas)
MT5_ENERGIES = [
    # 'XTIUSD',   # WTI Crude Oil
    # 'XBRUSD',   # Brent Crude Oil
    # 'XNGUSD',   # Natural Gas
]

# 🪙 CRYPTO (if your broker supports)
MT5_CRYPTO = [
    # 'BTCUSD',   # Bitcoin
    # 'ETHUSD',   # Ethereum
    # 'BNBUSD',   # Binance Coin
]

# Combined symbol list (used by agent)
MT5_SYMBOLS = (
    MT5_FOREX_PAIRS +
    MT5_METALS +
    MT5_INDICES +
    MT5_STOCKS +
    MT5_ENERGIES +
    MT5_CRYPTO
)

# Position Sizing (per asset class)
MT5_POSITION_SIZES = {
    'forex': 0.01,      # 0.01 lots = 1,000 units (micro lot)
    'metals': 0.01,     # Gold: 0.01 lots = 1 oz
    'indices': 0.10,    # Indices often need larger lot sizes
    'stocks': 1,        # Individual stocks: 1 share
    'energies': 0.01,   # Oil: 0.01 lots = 1 barrel
    'crypto': 0.01,     # BTC: 0.01 lots = 0.01 BTC
}

# Risk Management per Asset Class
MT5_RISK_PARAMS = {
    'forex': {
        'max_spread_pips': 3,      # Skip if spread > 3 pips
        'min_stop_loss_pips': 20,  # Minimum SL distance
        'max_stop_loss_pips': 100, # Maximum SL distance
        'default_tp_ratio': 2.0,   # TP = SL * 2 (risk:reward)
    },
    'metals': {
        'max_spread_pips': 50,     # Gold has wider spreads
        'min_stop_loss_pips': 100, # Larger moves in gold
        'max_stop_loss_pips': 500,
        'default_tp_ratio': 2.5,
    },
    'indices': {
        'max_spread_pips': 50,
        'min_stop_loss_pips': 50,
        'max_stop_loss_pips': 300,
        'default_tp_ratio': 2.0,
    },
    'stocks': {
        'max_spread_pips': 100,
        'min_stop_loss_pips': 50,
        'max_stop_loss_pips': 500,
        'default_tp_ratio': 2.5,
    },
}

# Timeframes per Asset Class
MT5_TIMEFRAMES = {
    'forex': '1H',      # Forex: hourly charts
    'metals': '4H',     # Gold: 4-hour charts (slower moves)
    'indices': '1H',    # Indices: hourly charts
    'stocks': '1D',     # Stocks: daily charts
}

# Global MT5 Settings
MT5_MAX_POSITION_SIZE = 1.0     # Maximum position size in lots
MT5_MAX_POSITIONS = 1           # ⚠️ MAXIMUM 1 POSITION AT A TIME (strict risk control)
MT5_MAX_POSITIONS_PER_SYMBOL = 1  # Max positions per symbol
MT5_MODEL_TYPE = 'openrouter'   # AI model provider: openrouter (unified), anthropic, openai, deepseek, groq
MT5_MODEL_NAME = 'deepseek/deepseek-chat-v3-0324'  # Primary model (powerful & affordable!)
MT5_FALLBACK_MODEL = 'anthropic/claude-sonnet-4.5'  # Fallback model if primary fails
MT5_MIN_CONFIDENCE = 75         # Minimum AI confidence % to execute trade (0-100)

# Trading Hours & Volatility Filter ⏰
MT5_USE_TRADING_HOURS_FILTER = True  # Enable optimal trading hours filter
MT5_STRICT_HOURS = True               # True = only best hours, False = allow good hours
# When enabled, system will ONLY trade during high-volatility periods:
# - Forex: London/NY overlap (13:00-17:00 UTC) + London morning (08:00-12:00 UTC)
# - Gold: NY session (13:00-20:00 UTC)
# - Indices: Mid-day stable hours (15:00-20:00 UTC), avoiding first/last 30min
# - Stocks: Mid-day hours (15:30-19:30 UTC), avoiding opening/closing volatility

MT5_AVOID_MONDAY_EARLY = True        # Avoid Monday before 08:00 UTC (weekend gaps)
MT5_AVOID_FRIDAY_LATE = True         # Avoid Friday after 20:00 UTC (weekend risk)
MT5_AVOID_LOW_VOLATILITY = True      # Skip trades during Asian session (low vol)

# Sandbox/Test Mode Settings 🧪
SANDBOX_MODE = True             # Enable for testing without real broker
SANDBOX_STARTING_BALANCE = 150000  # Virtual account balance for sandbox (150k)
SANDBOX_USE_MOCK_DATA = False   # Use generated mock market data
SANDBOX_SIMULATE_TRADES = True  # Simulate trade execution without MT5

# Future variables (not active yet) 🔮
sell_at_multiple = 3
USDC_SIZE = 1
limit = 49
timeframe = '15m'
stop_loss_perctentage = -.24
EXIT_ALL_POSITIONS = False
DO_NOT_TRADE_LIST = ['777']
CLOSED_POSITIONS_TXT = '777'
minimum_trades_in_last_hour = 777
