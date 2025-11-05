"""
🌙 Moon Dev's MetaTrader 5 Integration
Built with love by Moon Dev 🚀

This module provides integration with MetaTrader 5 for forex and CFD trading.
Follows the same pattern as nice_funcs_hl.py for consistency.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from termcolor import cprint
from typing import Optional, Dict, List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# MT5 Configuration
MT5_LOGIN = int(os.getenv('MT5_LOGIN', '0'))
MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
MT5_SERVER = os.getenv('MT5_SERVER', '')
MT5_PATH = os.getenv('MT5_PATH', '')  # Path to MT5 terminal (Windows/Wine)


class MT5Connection:
    """Singleton MT5 connection manager"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MT5Connection, cls).__new__(cls)
        return cls._instance

    def initialize(self) -> bool:
        """Initialize MT5 connection"""
        if self._initialized:
            return True

        try:
            # Initialize MT5
            if MT5_PATH:
                if not mt5.initialize(MT5_PATH):
                    cprint(f"❌ MT5 initialize() failed, error code: {mt5.last_error()}", "red")
                    return False
            else:
                if not mt5.initialize():
                    cprint(f"❌ MT5 initialize() failed, error code: {mt5.last_error()}", "red")
                    return False

            # Login if credentials provided
            if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
                authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
                if not authorized:
                    cprint(f"❌ MT5 login failed, error code: {mt5.last_error()}", "red")
                    mt5.shutdown()
                    return False

                cprint(f"✅ Connected to MT5 account #{MT5_LOGIN} on {MT5_SERVER}", "green")
            else:
                cprint("✅ MT5 initialized (no login credentials)", "yellow")

            self._initialized = True
            return True

        except Exception as e:
            cprint(f"❌ MT5 initialization error: {str(e)}", "red")
            return False

    def shutdown(self):
        """Shutdown MT5 connection"""
        if self._initialized:
            mt5.shutdown()
            self._initialized = False
            cprint("👋 MT5 connection closed", "yellow")


def ensure_connection() -> bool:
    """Ensure MT5 is connected before operations"""
    conn = MT5Connection()
    return conn.initialize()


def get_account_info() -> Optional[Dict]:
    """
    Get MT5 account information

    Returns:
        Dict with account info or None if error
    """
    if not ensure_connection():
        return None

    try:
        account_info = mt5.account_info()
        if account_info is None:
            cprint(f"❌ Failed to get account info: {mt5.last_error()}", "red")
            return None

        return {
            'login': account_info.login,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'margin_level': account_info.margin_level,
            'profit': account_info.profit,
            'currency': account_info.currency,
            'leverage': account_info.leverage,
            'server': account_info.server,
            'company': account_info.company,
        }
    except Exception as e:
        cprint(f"❌ Error getting account info: {str(e)}", "red")
        return None


def get_symbol_info(symbol: str) -> Optional[Dict]:
    """
    Get information about a trading symbol

    Args:
        symbol: Symbol name (e.g., 'EURUSD', 'GBPUSD', 'BTCUSD')

    Returns:
        Dict with symbol info or None if error
    """
    if not ensure_connection():
        return None

    try:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            cprint(f"❌ Symbol {symbol} not found", "red")
            return None

        return {
            'name': symbol_info.name,
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'spread': symbol_info.spread,
            'digits': symbol_info.digits,
            'point': symbol_info.point,
            'trade_contract_size': symbol_info.trade_contract_size,
            'trade_tick_size': symbol_info.trade_tick_size,
            'trade_tick_value': symbol_info.trade_tick_value,
            'volume_min': symbol_info.volume_min,
            'volume_max': symbol_info.volume_max,
            'volume_step': symbol_info.volume_step,
            'currency_base': symbol_info.currency_base,
            'currency_profit': symbol_info.currency_profit,
            'currency_margin': symbol_info.currency_margin,
        }
    except Exception as e:
        cprint(f"❌ Error getting symbol info for {symbol}: {str(e)}", "red")
        return None


def get_ohlcv_data(
    symbol: str,
    timeframe: str = '1H',
    bars: int = 1000,
    start_date: Optional[datetime] = None
) -> Optional[pd.DataFrame]:
    """
    Get OHLCV data from MT5

    Args:
        symbol: Symbol name (e.g., 'EURUSD')
        timeframe: Timeframe ('1m', '5m', '15m', '30m', '1H', '4H', '1D', '1W', '1M')
        bars: Number of bars to fetch
        start_date: Optional start date (if None, fetches most recent bars)

    Returns:
        DataFrame with OHLCV data or None if error
    """
    if not ensure_connection():
        return None

    # Map timeframe strings to MT5 constants
    timeframe_map = {
        '1m': mt5.TIMEFRAME_M1,
        '5m': mt5.TIMEFRAME_M5,
        '15m': mt5.TIMEFRAME_M15,
        '30m': mt5.TIMEFRAME_M30,
        '1H': mt5.TIMEFRAME_H1,
        '4H': mt5.TIMEFRAME_H4,
        '1D': mt5.TIMEFRAME_D1,
        '1W': mt5.TIMEFRAME_W1,
        '1M': mt5.TIMEFRAME_MN1,
    }

    if timeframe not in timeframe_map:
        cprint(f"❌ Invalid timeframe: {timeframe}", "red")
        return None

    mt5_timeframe = timeframe_map[timeframe]

    try:
        # Enable symbol for trading
        if not mt5.symbol_select(symbol, True):
            cprint(f"❌ Failed to select symbol {symbol}", "red")
            return None

        # Fetch rates
        if start_date:
            rates = mt5.copy_rates_from(symbol, mt5_timeframe, start_date, bars)
        else:
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars)

        if rates is None or len(rates) == 0:
            cprint(f"❌ No data received for {symbol}, error: {mt5.last_error()}", "red")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        # Rename columns to standard format
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume',
            'spread': 'Spread',
            'real_volume': 'Real_Volume'
        }, inplace=True)

        cprint(f"✅ Fetched {len(df)} bars for {symbol} ({timeframe})", "green")
        return df

    except Exception as e:
        cprint(f"❌ Error fetching OHLCV data for {symbol}: {str(e)}", "red")
        return None


def get_positions() -> Optional[pd.DataFrame]:
    """
    Get all open positions

    Returns:
        DataFrame with positions or None if error
    """
    if not ensure_connection():
        return None

    try:
        positions = mt5.positions_get()
        if positions is None:
            cprint(f"❌ Failed to get positions: {mt5.last_error()}", "red")
            return None

        if len(positions) == 0:
            return pd.DataFrame()

        # Convert to DataFrame
        positions_list = []
        for pos in positions:
            positions_list.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'swap': pos.swap,
                'comment': pos.comment,
                'time': datetime.fromtimestamp(pos.time),
            })

        df = pd.DataFrame(positions_list)
        return df

    except Exception as e:
        cprint(f"❌ Error getting positions: {str(e)}", "red")
        return None


def market_buy(
    symbol: str,
    volume: float,
    sl: float = 0.0,
    tp: float = 0.0,
    comment: str = "Moon Dev AI"
) -> Optional[int]:
    """
    Open a BUY position

    Args:
        symbol: Symbol to trade
        volume: Volume in lots (e.g., 0.01 = micro lot)
        sl: Stop loss price (0 = no SL)
        tp: Take profit price (0 = no TP)
        comment: Order comment

    Returns:
        Ticket number if successful, None if failed
    """
    if not ensure_connection():
        return None

    try:
        # Get symbol info for current price
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            cprint(f"❌ Symbol {symbol} not found", "red")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                cprint(f"❌ Failed to select symbol {symbol}", "red")
                return None

        # Prepare request
        price = symbol_info.ask
        deviation = 20  # Price deviation in points

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ BUY order failed, retcode={result.retcode}: {result.comment}", "red")
            return None

        cprint(f"✅ BUY {volume} lots of {symbol} at {price} (Ticket: {result.order})", "green")
        return result.order

    except Exception as e:
        cprint(f"❌ Error executing BUY order: {str(e)}", "red")
        return None


def market_sell(
    symbol: str,
    volume: float,
    sl: float = 0.0,
    tp: float = 0.0,
    comment: str = "Moon Dev AI"
) -> Optional[int]:
    """
    Open a SELL position

    Args:
        symbol: Symbol to trade
        volume: Volume in lots
        sl: Stop loss price (0 = no SL)
        tp: Take profit price (0 = no TP)
        comment: Order comment

    Returns:
        Ticket number if successful, None if failed
    """
    if not ensure_connection():
        return None

    try:
        # Get symbol info for current price
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            cprint(f"❌ Symbol {symbol} not found", "red")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                cprint(f"❌ Failed to select symbol {symbol}", "red")
                return None

        # Prepare request
        price = symbol_info.bid
        deviation = 20

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ SELL order failed, retcode={result.retcode}: {result.comment}", "red")
            return None

        cprint(f"✅ SELL {volume} lots of {symbol} at {price} (Ticket: {result.order})", "green")
        return result.order

    except Exception as e:
        cprint(f"❌ Error executing SELL order: {str(e)}", "red")
        return None


def close_position(ticket: int) -> bool:
    """
    Close a position by ticket number

    Args:
        ticket: Position ticket number

    Returns:
        True if successful, False otherwise
    """
    if not ensure_connection():
        return False

    try:
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            cprint(f"❌ Position {ticket} not found", "red")
            return False

        position = position[0]
        symbol = position.symbol
        volume = position.volume

        # Determine close type (opposite of position type)
        if position.type == mt5.ORDER_TYPE_BUY:
            close_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info(symbol).bid
        else:
            close_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info(symbol).ask

        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close by Moon Dev AI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send close order
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ Close failed, retcode={result.retcode}: {result.comment}", "red")
            return False

        cprint(f"✅ Closed position {ticket} ({symbol})", "green")
        return True

    except Exception as e:
        cprint(f"❌ Error closing position: {str(e)}", "red")
        return False


def close_all_positions() -> int:
    """
    Close all open positions

    Returns:
        Number of positions closed
    """
    if not ensure_connection():
        return 0

    positions = get_positions()
    if positions is None or len(positions) == 0:
        cprint("ℹ️  No positions to close", "yellow")
        return 0

    closed = 0
    for _, pos in positions.iterrows():
        if close_position(pos['ticket']):
            closed += 1

    cprint(f"✅ Closed {closed}/{len(positions)} positions", "green")
    return closed


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to OHLCV DataFrame
    Same indicators as nice_funcs_hl.py for consistency

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with added indicators
    """
    try:
        # Simple Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

        return df

    except Exception as e:
        cprint(f"❌ Error adding indicators: {str(e)}", "red")
        return df


if __name__ == "__main__":
    """Test MT5 connection and functions"""
    cprint("\n🌙 Testing MT5 Connection...\n", "cyan")

    # Test connection
    if ensure_connection():
        # Test account info
        account = get_account_info()
        if account:
            cprint(f"\n💰 Account Info:", "cyan")
            for key, value in account.items():
                print(f"  {key}: {value}")

        # Test symbol info
        symbols = ['EURUSD', 'GBPUSD', 'BTCUSD']
        for symbol in symbols:
            info = get_symbol_info(symbol)
            if info:
                cprint(f"\n📊 {symbol} Info:", "cyan")
                print(f"  Bid: {info['bid']}")
                print(f"  Ask: {info['ask']}")
                print(f"  Spread: {info['spread']}")

        # Test OHLCV data
        df = get_ohlcv_data('EURUSD', timeframe='1H', bars=100)
        if df is not None:
            cprint(f"\n📈 EURUSD Data (last 5 bars):", "cyan")
            print(df.tail())

            # Add indicators
            df = add_technical_indicators(df)
            cprint(f"\n📊 With Indicators:", "cyan")
            print(df[['Close', 'SMA_20', 'RSI', 'MACD']].tail())

        # Test positions
        positions = get_positions()
        if positions is not None:
            if len(positions) > 0:
                cprint(f"\n🎯 Open Positions:", "cyan")
                print(positions)
            else:
                cprint(f"\nℹ️  No open positions", "yellow")

        # Cleanup
        MT5Connection().shutdown()
    else:
        cprint("❌ Failed to connect to MT5", "red")
