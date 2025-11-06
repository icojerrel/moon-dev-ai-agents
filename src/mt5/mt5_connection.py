"""
🌙 Moon Dev's MT5 Connection Module
Built with love by Moon Dev 🚀

Handles MetaTrader 5 connection with PAPER TRADING mode support.
"""

import MetaTrader5 as mt5
from typing import Optional, Dict, List, Tuple
from termcolor import cprint
import pandas as pd
from datetime import datetime
import json
from pathlib import Path


class MT5Connection:
    """MetaTrader 5 connection handler with paper trading mode"""

    def __init__(self, paper_trading: bool = True, virtual_balance: float = 10000.0):
        """
        Initialize MT5 connection

        Args:
            paper_trading: If True, don't execute real trades (default: True)
            virtual_balance: Starting balance for paper trading (default: $10,000)
        """
        self.paper_trading = paper_trading
        self.virtual_balance = virtual_balance
        self.initial_balance = virtual_balance
        self.connected = False

        # Paper trading state
        self.virtual_positions = []  # List of open positions
        self.trade_history = []  # All trades executed

        # Data directory for storing paper trades
        self.data_dir = Path(__file__).parent.parent / "data" / "mt5_paper"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if paper_trading:
            cprint("📝 PAPER TRADING MODE - No real trades will be executed!", "yellow", attrs=["bold"])
            cprint(f"💰 Virtual balance: ${virtual_balance:,.2f}", "cyan")
        else:
            cprint("⚠️  LIVE TRADING MODE - Real money at risk!", "red", attrs=["bold"])

    def connect(self, login: Optional[int] = None,
                password: Optional[str] = None,
                server: Optional[str] = None) -> bool:
        """
        Connect to MT5 terminal

        Args:
            login: MT5 account number
            password: MT5 account password
            server: MT5 server name

        Returns:
            True if connected successfully
        """
        if self.paper_trading:
            cprint("✅ Paper trading mode - skipping MT5 connection", "green")
            self.connected = True
            return True

        # Initialize MT5
        if not mt5.initialize():
            cprint(f"❌ MT5 initialization failed: {mt5.last_error()}", "red")
            return False

        # Login if credentials provided
        if login and password and server:
            authorized = mt5.login(login, password=password, server=server)
            if not authorized:
                cprint(f"❌ MT5 login failed: {mt5.last_error()}", "red")
                mt5.shutdown()
                return False
            cprint(f"✅ Connected to MT5 account: {login}", "green")
        else:
            cprint("✅ MT5 initialized (using default account)", "green")

        self.connected = True
        return True

    def disconnect(self):
        """Disconnect from MT5"""
        if not self.paper_trading and self.connected:
            mt5.shutdown()
            cprint("👋 Disconnected from MT5", "yellow")
        self.connected = False

    def get_account_info(self) -> Dict:
        """Get account information"""
        if self.paper_trading:
            total_pl = sum(pos['profit'] for pos in self.virtual_positions)
            return {
                'balance': self.virtual_balance,
                'equity': self.virtual_balance + total_pl,
                'margin': 0,
                'free_margin': self.virtual_balance,
                'margin_level': 0,
                'profit': total_pl,
                'paper_trading': True
            }

        account_info = mt5.account_info()
        if account_info is None:
            return {}

        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'margin_level': account_info.margin_level,
            'profit': account_info.profit,
            'paper_trading': False
        }

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if self.paper_trading:
            # Return mock data for paper trading
            return {
                'symbol': symbol,
                'bid': 1.0,
                'ask': 1.0,
                'spread': 0.0,
                'digits': 5,
                'trade_tick_size': 0.00001,
                'trade_contract_size': 100000,
                'paper_trading': True
            }

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return None

        return {
            'symbol': symbol,
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'spread': symbol_info.spread,
            'digits': symbol_info.digits,
            'trade_tick_size': symbol_info.trade_tick_size,
            'trade_contract_size': symbol_info.trade_contract_size,
            'paper_trading': False
        }

    def get_price(self, symbol: str) -> Optional[Tuple[float, float]]:
        """Get current bid/ask price"""
        if self.paper_trading:
            # For paper trading, use mock price or try to get real price
            tick = mt5.symbol_info_tick(symbol) if not self.paper_trading else None
            if tick:
                return (tick.bid, tick.ask)
            # Mock price if MT5 not available
            return (1.0, 1.0)

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        return (tick.bid, tick.ask)

    def open_position(self, symbol: str, order_type: str, volume: float,
                     sl: Optional[float] = None, tp: Optional[float] = None,
                     comment: str = "Moon Dev AI") -> Dict:
        """
        Open a position

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            order_type: "BUY" or "SELL"
            volume: Position size in lots
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment

        Returns:
            Dict with order result
        """
        prices = self.get_price(symbol)
        if not prices:
            return {'success': False, 'error': 'Could not get price'}

        bid, ask = prices
        entry_price = ask if order_type == "BUY" else bid

        if self.paper_trading:
            # Paper trading: Just record the position
            position = {
                'ticket': len(self.trade_history) + 1,
                'symbol': symbol,
                'type': order_type,
                'volume': volume,
                'entry_price': entry_price,
                'sl': sl,
                'tp': tp,
                'open_time': datetime.now(),
                'profit': 0.0,
                'comment': comment
            }

            self.virtual_positions.append(position)
            self.trade_history.append({**position, 'status': 'OPEN'})

            cprint(f"📝 Paper trade opened:", "green")
            cprint(f"   Symbol: {symbol}", "white")
            cprint(f"   Type: {order_type}", "white")
            cprint(f"   Volume: {volume} lots", "white")
            cprint(f"   Entry: {entry_price}", "white")
            cprint(f"   SL: {sl if sl else 'None'}", "white")
            cprint(f"   TP: {tp if tp else 'None'}", "white")

            self._save_paper_trades()

            return {
                'success': True,
                'ticket': position['ticket'],
                'entry_price': entry_price,
                'paper_trading': True
            }

        # Real trading
        order_type_mt5 = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type_mt5,
            "price": entry_price,
            "sl": sl if sl else 0.0,
            "tp": tp if tp else 0.0,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            cprint(f"❌ Order failed: {result.comment}", "red")
            return {'success': False, 'error': result.comment}

        cprint(f"✅ Order executed: {symbol} {order_type} {volume} lots @ {entry_price}", "green")

        return {
            'success': True,
            'ticket': result.order,
            'entry_price': entry_price,
            'paper_trading': False
        }

    def close_position(self, ticket: int) -> Dict:
        """Close a position by ticket"""
        if self.paper_trading:
            # Find position in virtual positions
            position = next((p for p in self.virtual_positions if p['ticket'] == ticket), None)

            if not position:
                return {'success': False, 'error': 'Position not found'}

            # Get current price
            prices = self.get_price(position['symbol'])
            if not prices:
                return {'success': False, 'error': 'Could not get price'}

            bid, ask = prices
            exit_price = bid if position['type'] == "BUY" else ask

            # Calculate profit
            if position['type'] == "BUY":
                profit = (exit_price - position['entry_price']) * position['volume'] * 100000  # Assuming standard lot
            else:
                profit = (position['entry_price'] - exit_price) * position['volume'] * 100000

            # Update virtual balance
            self.virtual_balance += profit

            # Remove from open positions
            self.virtual_positions.remove(position)

            # Add to history
            close_record = {
                **position,
                'exit_price': exit_price,
                'close_time': datetime.now(),
                'profit': profit,
                'status': 'CLOSED'
            }
            self.trade_history.append(close_record)

            cprint(f"📝 Paper position closed:", "green")
            cprint(f"   Ticket: {ticket}", "white")
            cprint(f"   Exit: {exit_price}", "white")
            cprint(f"   P/L: ${profit:,.2f}", "green" if profit > 0 else "red")
            cprint(f"   New balance: ${self.virtual_balance:,.2f}", "cyan")

            self._save_paper_trades()

            return {
                'success': True,
                'profit': profit,
                'exit_price': exit_price,
                'paper_trading': True
            }

        # Real trading
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return {'success': False, 'error': 'Position not found'}

        position = position[0]

        # Close position
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": close_type,
            "position": ticket,
            "deviation": 20,
            "magic": 234000,
            "comment": "Moon Dev AI close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {'success': False, 'error': result.comment}

        return {
            'success': True,
            'profit': position.profit,
            'paper_trading': False
        }

    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        if self.paper_trading:
            # Update profits for virtual positions
            for pos in self.virtual_positions:
                prices = self.get_price(pos['symbol'])
                if prices:
                    bid, ask = prices
                    current_price = bid if pos['type'] == "BUY" else ask

                    if pos['type'] == "BUY":
                        pos['profit'] = (current_price - pos['entry_price']) * pos['volume'] * 100000
                    else:
                        pos['profit'] = (pos['entry_price'] - current_price) * pos['volume'] * 100000

            return self.virtual_positions

        positions = mt5.positions_get()
        if positions is None:
            return []

        return [
            {
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'entry_price': pos.price_open,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'open_time': datetime.fromtimestamp(pos.time)
            }
            for pos in positions
        ]

    def _save_paper_trades(self):
        """Save paper trading history to file"""
        if not self.paper_trading:
            return

        filepath = self.data_dir / "paper_trades.json"

        data = {
            'initial_balance': self.initial_balance,
            'current_balance': self.virtual_balance,
            'open_positions': self.virtual_positions,
            'trade_history': [
                {**trade, 'open_time': trade['open_time'].isoformat() if 'open_time' in trade else None,
                 'close_time': trade.get('close_time').isoformat() if trade.get('close_time') else None}
                for trade in self.trade_history
            ],
            'last_updated': datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def get_trade_history(self) -> List[Dict]:
        """Get all trade history"""
        if self.paper_trading:
            return self.trade_history

        # Get deals from MT5
        from_date = datetime(2020, 1, 1)
        to_date = datetime.now()

        deals = mt5.history_deals_get(from_date, to_date)
        if deals is None:
            return []

        return [
            {
                'ticket': deal.order,
                'symbol': deal.symbol,
                'type': 'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL',
                'volume': deal.volume,
                'price': deal.price,
                'profit': deal.profit,
                'time': datetime.fromtimestamp(deal.time)
            }
            for deal in deals
        ]

    def get_candles(self, symbol: str, timeframe: str = "H1", count: int = 100) -> Optional[pd.DataFrame]:
        """
        Get OHLC candlestick data

        Args:
            symbol: Trading symbol
            timeframe: Timeframe (M1, M5, M15, H1, H4, D1, etc.)
            count: Number of candles

        Returns:
            DataFrame with OHLC data or None
        """
        # Map timeframe string to MT5 constant
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
        }

        mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)

        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)

        if rates is None:
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.rename(columns={
            'time': 'datetime',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume'
        }, inplace=True)

        return df[['datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]


# Example usage
if __name__ == "__main__":
    # Paper trading mode
    mt5_conn = MT5Connection(paper_trading=True, virtual_balance=10000)

    if mt5_conn.connect():
        # Get account info
        account = mt5_conn.get_account_info()
        cprint(f"\n💰 Account Info:", "cyan", attrs=["bold"])
        cprint(f"  Balance: ${account['balance']:,.2f}", "white")
        cprint(f"  Equity: ${account['equity']:,.2f}", "white")

        # Open a test position
        result = mt5_conn.open_position(
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            sl=1.0800,
            tp=1.1200,
            comment="Test trade"
        )

        if result['success']:
            cprint(f"\n✅ Position opened: Ticket {result['ticket']}", "green")

        # Check positions
        positions = mt5_conn.get_positions()
        cprint(f"\n📊 Open Positions: {len(positions)}", "cyan")

        for pos in positions:
            cprint(f"  Ticket: {pos['ticket']} | {pos['symbol']} {pos['type']} | P/L: ${pos['profit']:,.2f}", "white")

        mt5_conn.disconnect()
