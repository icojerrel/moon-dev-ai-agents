"""
🌙 Moon Dev's MetaTrader 5 Utilities
Shared MT5 functions for all agents
Windows-only (requires MetaTrader5 Python library)
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from termcolor import cprint
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing MT5 (will only work on Windows)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    cprint("⚠️ MetaTrader5 library not available. Install with: pip install MetaTrader5", "yellow")
    cprint("⚠️ Note: MT5 library only works on Windows!", "yellow")

# Import config
from src.config import (
    MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, MT5_PATH,
    MT5_MAGIC_NUMBER, MT5_SLIPPAGE, MT5_LOT_SIZE,
    MT5_USE_STOP_LOSS, MT5_STOP_LOSS_POINTS,
    MT5_USE_TAKE_PROFIT, MT5_TAKE_PROFIT_POINTS,
)

# Timeframe mapping
MT5_TIMEFRAMES = {
    'M1': mt5.TIMEFRAME_M1 if MT5_AVAILABLE else None,
    'M5': mt5.TIMEFRAME_M5 if MT5_AVAILABLE else None,
    'M15': mt5.TIMEFRAME_M15 if MT5_AVAILABLE else None,
    'M30': mt5.TIMEFRAME_M30 if MT5_AVAILABLE else None,
    'H1': mt5.TIMEFRAME_H1 if MT5_AVAILABLE else None,
    'H4': mt5.TIMEFRAME_H4 if MT5_AVAILABLE else None,
    'D1': mt5.TIMEFRAME_D1 if MT5_AVAILABLE else None,
    'W1': mt5.TIMEFRAME_W1 if MT5_AVAILABLE else None,
    'MN1': mt5.TIMEFRAME_MN1 if MT5_AVAILABLE else None,
}


class MT5Connection:
    """Manages MT5 connection and operations"""

    def __init__(self):
        self.connected = False
        self.account_info = None

    def connect(self) -> bool:
        """Initialize connection to MT5"""
        if not MT5_AVAILABLE:
            cprint("❌ MT5 library not available (Windows only)", "red")
            return False

        # Initialize MT5
        if MT5_PATH:
            if not mt5.initialize(MT5_PATH):
                cprint(f"❌ Failed to initialize MT5 at {MT5_PATH}", "red")
                cprint(f"Error: {mt5.last_error()}", "red")
                return False
        else:
            if not mt5.initialize():
                cprint(f"❌ Failed to initialize MT5", "red")
                cprint(f"Error: {mt5.last_error()}", "red")
                return False

        # Login to account
        login = int(os.getenv('MT5_LOGIN', MT5_LOGIN))
        password = os.getenv('MT5_PASSWORD', MT5_PASSWORD)
        server = os.getenv('MT5_SERVER', MT5_SERVER)

        if not login or not password or not server:
            cprint("❌ MT5 credentials not configured in .env", "red")
            cprint("Set: MT5_LOGIN, MT5_PASSWORD, MT5_SERVER", "yellow")
            mt5.shutdown()
            return False

        authorized = mt5.login(login=login, password=password, server=server)

        if not authorized:
            cprint(f"❌ Failed to login to MT5 account {login}", "red")
            cprint(f"Error: {mt5.last_error()}", "red")
            mt5.shutdown()
            return False

        # Get account info
        self.account_info = mt5.account_info()
        if self.account_info is None:
            cprint("❌ Failed to get account info", "red")
            mt5.shutdown()
            return False

        self.connected = True
        cprint(f"✅ Connected to MT5 account: {login}", "green")
        cprint(f"📊 Server: {server}", "cyan")
        cprint(f"💰 Balance: ${self.account_info.balance:.2f}", "cyan")
        cprint(f"💵 Equity: ${self.account_info.equity:.2f}", "cyan")

        return True

    def disconnect(self):
        """Close MT5 connection"""
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            self.connected = False
            cprint("👋 Disconnected from MT5", "yellow")

    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.connected:
            return None

        info = mt5.account_info()
        if info is None:
            return None

        return {
            'balance': info.balance,
            'equity': info.equity,
            'profit': info.profit,
            'margin': info.margin,
            'margin_free': info.margin_free,
            'margin_level': info.margin_level if info.margin != 0 else 0,
            'leverage': info.leverage,
            'currency': info.currency,
        }

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if not self.connected:
            return None

        info = mt5.symbol_info(symbol)
        if info is None:
            cprint(f"❌ Symbol {symbol} not found", "red")
            return None

        return {
            'symbol': info.name,
            'bid': info.bid,
            'ask': info.ask,
            'spread': info.spread,
            'digits': info.digits,
            'point': info.point,
            'trade_contract_size': info.trade_contract_size,
            'volume_min': info.volume_min,
            'volume_max': info.volume_max,
            'volume_step': info.volume_step,
        }

    def get_ohlcv(self, symbol: str, timeframe: str = 'H1', bars: int = 100) -> Optional[pd.DataFrame]:
        """Get OHLCV data for symbol"""
        if not self.connected:
            return None

        tf = MT5_TIMEFRAMES.get(timeframe)
        if tf is None:
            cprint(f"❌ Invalid timeframe: {timeframe}", "red")
            return None

        # Get rates
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)

        if rates is None or len(rates) == 0:
            cprint(f"❌ Failed to get data for {symbol}", "red")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        return df

    def get_positions(self, symbol: str = None) -> List[Dict]:
        """Get open positions"""
        if not self.connected:
            return []

        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()

        if positions is None:
            return []

        result = []
        for pos in positions:
            result.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'sl': pos.sl,
                'tp': pos.tp,
                'time': datetime.fromtimestamp(pos.time),
            })

        return result

    def get_orders(self, symbol: str = None) -> List[Dict]:
        """Get pending orders"""
        if not self.connected:
            return []

        if symbol:
            orders = mt5.orders_get(symbol=symbol)
        else:
            orders = mt5.orders_get()

        if orders is None:
            return []

        result = []
        for order in orders:
            result.append({
                'ticket': order.ticket,
                'symbol': order.symbol,
                'type': order.type,
                'volume': order.volume,
                'price_open': order.price_open,
                'sl': order.sl,
                'tp': order.tp,
                'time_setup': datetime.fromtimestamp(order.time_setup),
            })

        return result

    def market_buy(self, symbol: str, lot_size: float = None,
                   sl: float = None, tp: float = None,
                   comment: str = "Moon Dev Bot") -> Optional[int]:
        """Open a BUY position"""
        if not self.connected:
            cprint("❌ Not connected to MT5", "red")
            return None

        lot_size = lot_size or MT5_LOT_SIZE

        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            cprint(f"❌ Symbol {symbol} not found", "red")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                cprint(f"❌ Failed to select {symbol}", "red")
                return None

        # Prepare request
        price = mt5.symbol_info_tick(symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl or 0,
            "tp": tp or 0,
            "deviation": MT5_SLIPPAGE,
            "magic": MT5_MAGIC_NUMBER,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result is None:
            cprint(f"❌ Order failed: No result", "red")
            return None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ Order failed: {result.comment}", "red")
            return None

        cprint(f"✅ BUY {symbol}: {lot_size} lots @ {price:.5f}", "green")
        cprint(f"📈 Position opened: #{result.order}", "cyan")

        return result.order

    def market_sell(self, symbol: str, lot_size: float = None,
                    sl: float = None, tp: float = None,
                    comment: str = "Moon Dev Bot") -> Optional[int]:
        """Open a SELL position"""
        if not self.connected:
            cprint("❌ Not connected to MT5", "red")
            return None

        lot_size = lot_size or MT5_LOT_SIZE

        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            cprint(f"❌ Symbol {symbol} not found", "red")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                cprint(f"❌ Failed to select {symbol}", "red")
                return None

        # Prepare request
        price = mt5.symbol_info_tick(symbol).bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl or 0,
            "tp": tp or 0,
            "deviation": MT5_SLIPPAGE,
            "magic": MT5_MAGIC_NUMBER,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result is None:
            cprint(f"❌ Order failed: No result", "red")
            return None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ Order failed: {result.comment}", "red")
            return None

        cprint(f"✅ SELL {symbol}: {lot_size} lots @ {price:.5f}", "green")
        cprint(f"📉 Position opened: #{result.order}", "cyan")

        return result.order

    def close_position(self, ticket: int) -> bool:
        """Close a position by ticket"""
        if not self.connected:
            cprint("❌ Not connected to MT5", "red")
            return False

        # Get position
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            cprint(f"❌ Position {ticket} not found", "red")
            return False

        position = position[0]

        # Prepare close request
        price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": price,
            "deviation": MT5_SLIPPAGE,
            "magic": MT5_MAGIC_NUMBER,
            "comment": "Close by Moon Dev Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result is None:
            cprint(f"❌ Failed to close position {ticket}", "red")
            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ Failed to close position: {result.comment}", "red")
            return False

        cprint(f"✅ Closed position #{ticket}: Profit ${position.profit:.2f}", "green")

        return True

    def close_all_positions(self, symbol: str = None) -> int:
        """Close all positions (optionally filtered by symbol)"""
        if not self.connected:
            return 0

        positions = self.get_positions(symbol)
        closed = 0

        for pos in positions:
            if self.close_position(pos['ticket']):
                closed += 1

        cprint(f"✅ Closed {closed} positions", "green")
        return closed

    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """Modify stop loss and take profit of a position"""
        if not self.connected:
            return False

        # Get position
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            cprint(f"❌ Position {ticket} not found", "red")
            return False

        position = position[0]

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position.symbol,
            "position": ticket,
            "sl": sl if sl is not None else position.sl,
            "tp": tp if tp is not None else position.tp,
        }

        result = mt5.order_send(request)

        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ Failed to modify position: {result.comment if result else 'Unknown'}", "red")
            return False

        cprint(f"✅ Modified position #{ticket}: SL={sl}, TP={tp}", "green")
        return True

    def get_history_deals(self, days_back: int = 7) -> List[Dict]:
        """Get trading history"""
        if not self.connected:
            return []

        # Get deals from last N days
        from_date = datetime.now() - timedelta(days=days_back)
        to_date = datetime.now()

        deals = mt5.history_deals_get(from_date, to_date)

        if deals is None:
            return []

        result = []
        for deal in deals:
            result.append({
                'ticket': deal.ticket,
                'order': deal.order,
                'time': datetime.fromtimestamp(deal.time),
                'symbol': deal.symbol,
                'type': deal.type,
                'volume': deal.volume,
                'price': deal.price,
                'profit': deal.profit,
                'commission': deal.commission,
                'swap': deal.swap,
                'comment': deal.comment,
            })

        return result

    def calculate_lot_size(self, symbol: str, risk_percent: float, stop_loss_points: int) -> float:
        """Calculate position size based on risk"""
        if not self.connected:
            return MT5_LOT_SIZE

        account_info = self.get_account_info()
        if not account_info:
            return MT5_LOT_SIZE

        symbol_info = self.get_symbol_info(symbol)
        if not symbol_info:
            return MT5_LOT_SIZE

        # Calculate risk amount
        balance = account_info['balance']
        risk_amount = balance * (risk_percent / 100)

        # Calculate lot size
        point_value = symbol_info['point']
        contract_size = symbol_info['trade_contract_size']

        lot_size = risk_amount / (stop_loss_points * point_value * contract_size)

        # Round to symbol step
        volume_step = symbol_info['volume_step']
        lot_size = round(lot_size / volume_step) * volume_step

        # Ensure within limits
        lot_size = max(symbol_info['volume_min'], min(lot_size, symbol_info['volume_max']))

        return lot_size


# Singleton instance
_mt5_connection = None

def get_mt5_connection() -> MT5Connection:
    """Get or create MT5 connection singleton"""
    global _mt5_connection
    if _mt5_connection is None:
        _mt5_connection = MT5Connection()
    return _mt5_connection


if __name__ == "__main__":
    """Test MT5 connection"""
    cprint("\n🌙 Moon Dev's MT5 Connection Test", "cyan")

    mt5_conn = get_mt5_connection()

    if mt5_conn.connect():
        # Show account info
        info = mt5_conn.get_account_info()
        if info:
            cprint(f"\n💰 Account Balance: ${info['balance']:.2f}", "green")
            cprint(f"💵 Equity: ${info['equity']:.2f}", "green")
            cprint(f"📊 Margin Level: {info['margin_level']:.2f}%", "green")

        # Test symbol info
        symbol = 'EURUSD'
        sym_info = mt5_conn.get_symbol_info(symbol)
        if sym_info:
            cprint(f"\n📈 {symbol}:", "cyan")
            cprint(f"   Bid: {sym_info['bid']:.5f}", "yellow")
            cprint(f"   Ask: {sym_info['ask']:.5f}", "yellow")
            cprint(f"   Spread: {sym_info['spread']} points", "yellow")

        # Test positions
        positions = mt5_conn.get_positions()
        cprint(f"\n📊 Open Positions: {len(positions)}", "cyan")
        for pos in positions:
            cprint(f"   {pos['type']} {pos['symbol']}: {pos['volume']} lots, P&L: ${pos['profit']:.2f}", "yellow")

        mt5_conn.disconnect()
    else:
        cprint("\n❌ Failed to connect to MT5", "red")
        cprint("Make sure:", "yellow")
        cprint("1. MT5 is installed and running", "yellow")
        cprint("2. Credentials are set in .env file", "yellow")
        cprint("3. You're running on Windows", "yellow")
