"""
🌙 Moon Dev's Mock MT5 Simulator
Built with love by Moon Dev 🚀

Simulates MT5 trading for sandbox testing without a real broker.
Perfect for testing strategies, risk management, and system functionality.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import random


@dataclass
class MockPosition:
    """Simulated MT5 position"""
    ticket: int
    symbol: str
    type: str  # 'BUY' or 'SELL'
    volume: float
    price_open: float
    price_current: float
    sl: float
    tp: float
    profit: float
    swap: float
    comment: str
    time: datetime


@dataclass
class MockAccount:
    """Simulated MT5 account"""
    login: int = 12345678
    balance: float = 10000.0
    equity: float = 10000.0
    margin: float = 0.0
    margin_free: float = 10000.0
    margin_level: float = 0.0
    profit: float = 0.0
    currency: str = 'USD'
    leverage: int = 100
    server: str = 'MockBroker-Demo'
    company: str = 'Moon Dev Mock Broker'


class MockMT5Simulator:
    """
    Simulates MetaTrader 5 trading environment

    Features:
    - Realistic price generation with trends and volatility
    - Position management (open, close, modify)
    - P&L calculation
    - Spread simulation
    - Account balance tracking
    - Historical data generation
    """

    def __init__(
        self,
        starting_balance: float = 10000.0,
        spread_pips: Dict[str, float] = None
    ):
        """
        Initialize mock MT5 simulator

        Args:
            starting_balance: Starting account balance
            spread_pips: Dict of symbol -> spread in pips
        """
        self.account = MockAccount(balance=starting_balance, equity=starting_balance)
        self.positions: Dict[int, MockPosition] = {}
        self.next_ticket = 100001
        self.trade_history: List[Dict] = []

        # Default spreads per asset class
        self.spread_pips = spread_pips or {
            'EURUSD': 1.5,
            'GBPUSD': 2.0,
            'USDJPY': 1.8,
            'AUDUSD': 1.7,
            'USDCAD': 2.0,
            'NZDUSD': 2.2,
            'XAUUSD': 30.0,
            'XAGUSD': 40.0,
            'US30': 5.0,
            'NAS100': 2.0,
            'SPX500': 0.5,
            'AAPL': 0.1,
            'MSFT': 0.1,
            'BTCUSD': 50.0,
        }

        # Current prices (will be updated)
        self.current_prices = {
            'EURUSD': 1.0850,
            'GBPUSD': 1.2650,
            'USDJPY': 148.50,
            'AUDUSD': 0.6580,
            'USDCAD': 1.3520,
            'NZDUSD': 0.6120,
            'XAUUSD': 2050.00,
            'XAGUSD': 24.50,
            'US30': 38500.0,
            'NAS100': 16800.0,
            'SPX500': 4950.0,
            'AAPL': 185.0,
            'MSFT': 420.0,
            'BTCUSD': 65000.0,
        }

    def get_account_info(self) -> Dict:
        """Get account information"""
        return {
            'login': self.account.login,
            'balance': self.account.balance,
            'equity': self.account.equity,
            'margin': self.account.margin,
            'free_margin': self.account.margin_free,
            'margin_level': self.account.margin_level,
            'profit': self.account.profit,
            'currency': self.account.currency,
            'leverage': self.account.leverage,
            'server': self.account.server,
            'company': self.account.company,
        }

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if symbol not in self.current_prices:
            return None

        base_price = self.current_prices[symbol]
        spread = self.spread_pips.get(symbol, 2.0)

        # Calculate point size
        if 'JPY' in symbol:
            point = 0.01
            digits = 2
        elif 'XAU' in symbol or 'XAG' in symbol:
            point = 0.01
            digits = 2
        elif symbol in ['US30', 'NAS100', 'SPX500']:
            point = 1.0
            digits = 0
        elif symbol in ['AAPL', 'MSFT', 'GOOGL', 'TSLA']:
            point = 0.01
            digits = 2
        else:
            point = 0.0001
            digits = 4

        spread_points = spread * 10  # Convert pips to points

        return {
            'name': symbol,
            'bid': base_price,
            'ask': base_price + (spread_points * point),
            'spread': int(spread_points),
            'digits': digits,
            'point': point,
            'trade_contract_size': 100000,
            'trade_tick_size': point,
            'trade_tick_value': 10.0,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01,
            'currency_base': symbol[:3],
            'currency_profit': symbol[3:6] if len(symbol) >= 6 else 'USD',
            'currency_margin': symbol[:3],
        }

    def generate_ohlcv_data(
        self,
        symbol: str,
        timeframe: str = '1H',
        bars: int = 200,
        trend: str = 'random'  # 'random', 'bullish', 'bearish', 'ranging'
    ) -> pd.DataFrame:
        """
        Generate realistic OHLCV data

        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1H, 4H, 1D)
            bars: Number of bars to generate
            trend: Market trend type

        Returns:
            DataFrame with OHLCV data
        """
        # Timeframe to minutes
        tf_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1H': 60, '4H': 240, '1D': 1440
        }

        minutes = tf_minutes.get(timeframe, 60)

        # Get starting price
        base_price = self.current_prices.get(symbol, 100.0)

        # Volatility per asset class
        if 'XAU' in symbol:
            volatility = 0.015  # 1.5% per bar
        elif 'XAG' in symbol:
            volatility = 0.025
        elif symbol in ['US30', 'NAS100', 'SPX500']:
            volatility = 0.010
        elif 'BTC' in symbol:
            volatility = 0.030
        else:  # Forex
            volatility = 0.005

        # Generate timestamps
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=minutes * bars)
        timestamps = pd.date_range(start=start_time, end=end_time, periods=bars)

        # Generate prices
        prices = [base_price]

        for i in range(1, bars):
            # Trend bias
            if trend == 'bullish':
                drift = 0.0002
            elif trend == 'bearish':
                drift = -0.0002
            elif trend == 'ranging':
                drift = 0.0
            else:  # random
                drift = random.choice([-0.0001, 0.0, 0.0001])

            # Random walk with drift
            change = np.random.normal(drift, volatility)
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)

        # Generate OHLC from prices
        data = []
        for i, timestamp in enumerate(timestamps):
            close = prices[i]
            high = close * (1 + abs(np.random.normal(0, volatility/2)))
            low = close * (1 - abs(np.random.normal(0, volatility/2)))
            open_price = prices[i-1] if i > 0 else close
            volume = np.random.randint(1000, 10000)

            data.append({
                'time': timestamp,
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close,
                'Volume': volume,
                'Spread': self.spread_pips.get(symbol, 2.0),
            })

        df = pd.DataFrame(data)
        df.set_index('time', inplace=True)

        # Update current price
        self.current_prices[symbol] = prices[-1]

        return df

    def market_buy(
        self,
        symbol: str,
        volume: float,
        sl: float = 0.0,
        tp: float = 0.0,
        comment: str = "Mock Buy"
    ) -> Optional[int]:
        """Open a BUY position"""
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            return None

        price = symbol_info['ask']

        position = MockPosition(
            ticket=self.next_ticket,
            symbol=symbol,
            type='BUY',
            volume=volume,
            price_open=price,
            price_current=price,
            sl=sl,
            tp=tp,
            profit=0.0,
            swap=0.0,
            comment=comment,
            time=datetime.now()
        )

        self.positions[self.next_ticket] = position
        self.next_ticket += 1

        # Update account
        self._update_account()

        return position.ticket

    def market_sell(
        self,
        symbol: str,
        volume: float,
        sl: float = 0.0,
        tp: float = 0.0,
        comment: str = "Mock Sell"
    ) -> Optional[int]:
        """Open a SELL position"""
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            return None

        price = symbol_info['bid']

        position = MockPosition(
            ticket=self.next_ticket,
            symbol=symbol,
            type='SELL',
            volume=volume,
            price_open=price,
            price_current=price,
            sl=sl,
            tp=tp,
            profit=0.0,
            swap=0.0,
            comment=comment,
            time=datetime.now()
        )

        self.positions[self.next_ticket] = position
        self.next_ticket += 1

        # Update account
        self._update_account()

        return position.ticket

    def close_position(self, ticket: int) -> bool:
        """Close a position"""
        if ticket not in self.positions:
            return False

        position = self.positions[ticket]

        # Calculate final profit
        symbol_info = self.get_symbol_info(position.symbol)
        if symbol_info is None:
            return False

        if position.type == 'BUY':
            close_price = symbol_info['bid']
        else:
            close_price = symbol_info['ask']

        position.price_current = close_price
        profit = self._calculate_profit(position)

        # Update balance
        self.account.balance += profit

        # Record trade history
        self.trade_history.append({
            'ticket': ticket,
            'symbol': position.symbol,
            'type': position.type,
            'volume': position.volume,
            'open_price': position.price_open,
            'close_price': close_price,
            'profit': profit,
            'open_time': position.time,
            'close_time': datetime.now(),
        })

        # Remove position
        del self.positions[ticket]

        # Update account
        self._update_account()

        return True

    def get_positions(self) -> pd.DataFrame:
        """Get all open positions"""
        if not self.positions:
            return pd.DataFrame()

        # Update current prices and profits
        self._update_positions()

        positions_list = []
        for ticket, pos in self.positions.items():
            positions_list.append({
                'ticket': ticket,
                'symbol': pos.symbol,
                'type': pos.type,
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'swap': pos.swap,
                'comment': pos.comment,
                'time': pos.time,
            })

        return pd.DataFrame(positions_list)

    def _calculate_profit(self, position: MockPosition) -> float:
        """Calculate position profit"""
        symbol_info = self.get_symbol_info(position.symbol)
        if symbol_info is None:
            return 0.0

        # Get current price
        if position.type == 'BUY':
            current_price = symbol_info['bid']
            price_diff = current_price - position.price_open
        else:
            current_price = symbol_info['ask']
            price_diff = position.price_open - current_price

        # Calculate in pips
        point = symbol_info['point']
        pips = price_diff / point

        # Calculate profit (simplified: $10 per pip for 1 lot)
        profit_per_pip = 10.0 * position.volume
        profit = pips * profit_per_pip

        return profit

    def _update_positions(self):
        """Update all position current prices and profits"""
        for ticket, position in self.positions.items():
            symbol_info = self.get_symbol_info(position.symbol)
            if symbol_info:
                if position.type == 'BUY':
                    position.price_current = symbol_info['bid']
                else:
                    position.price_current = symbol_info['ask']

                position.profit = self._calculate_profit(position)

    def _update_account(self):
        """Update account equity, margin, etc."""
        # Update positions
        self._update_positions()

        # Calculate total profit
        total_profit = sum(pos.profit for pos in self.positions.values())

        # Update account
        self.account.profit = total_profit
        self.account.equity = self.account.balance + total_profit

        # Simplified margin calculation
        self.account.margin = len(self.positions) * 100.0  # $100 margin per position
        self.account.margin_free = self.account.equity - self.account.margin

        if self.account.margin > 0:
            self.account.margin_level = (self.account.equity / self.account.margin) * 100
        else:
            self.account.margin_level = 0.0

    def simulate_market_move(self, symbol: str, pips: float):
        """
        Simulate a market move for testing

        Args:
            symbol: Symbol to move
            pips: Number of pips to move (positive = up, negative = down)
        """
        if symbol in self.current_prices:
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info:
                point = symbol_info['point']
                self.current_prices[symbol] += (pips * point * 10)
                self._update_account()


if __name__ == "__main__":
    """Test mock MT5 simulator"""
    print("🌙 Testing Mock MT5 Simulator\n")

    # Create simulator
    sim = MockMT5Simulator(starting_balance=10000)

    # Test account info
    account = sim.get_account_info()
    print("💰 Account Info:")
    print(f"  Balance: ${account['balance']:.2f}")
    print(f"  Server: {account['server']}")

    # Test symbol info
    print("\n📊 Symbol Info (EURUSD):")
    symbol_info = sim.get_symbol_info('EURUSD')
    print(f"  Bid: {symbol_info['bid']:.5f}")
    print(f"  Ask: {symbol_info['ask']:.5f}")
    print(f"  Spread: {symbol_info['spread']} points")

    # Test OHLCV data generation
    print("\n📈 Generating OHLCV Data:")
    df = sim.generate_ohlcv_data('EURUSD', timeframe='1H', bars=100, trend='bullish')
    print(f"  Generated {len(df)} bars")
    print(f"  Price range: {df['Low'].min():.5f} - {df['High'].max():.5f}")
    print(f"\n  Last 5 bars:")
    print(df[['Open', 'High', 'Low', 'Close']].tail())

    # Test trading
    print("\n🟢 Opening BUY position:")
    ticket = sim.market_buy('EURUSD', volume=0.01, sl=1.0800, tp=1.0900)
    print(f"  Ticket: {ticket}")

    # Check positions
    positions = sim.get_positions()
    print(f"\n📋 Open Positions: {len(positions)}")
    if not positions.empty:
        print(positions[['symbol', 'type', 'volume', 'price_open', 'profit']])

    # Simulate market move
    print("\n📊 Simulating +50 pip move...")
    sim.simulate_market_move('EURUSD', 50)

    # Check updated positions
    positions = sim.get_positions()
    if not positions.empty:
        print(f"  Updated Profit: ${positions.iloc[0]['profit']:.2f}")

    # Update account
    account = sim.get_account_info()
    print(f"\n💰 Updated Account:")
    print(f"  Balance: ${account['balance']:.2f}")
    print(f"  Equity: ${account['equity']:.2f}")
    print(f"  Profit: ${account['profit']:.2f}")

    # Close position
    print(f"\n⚪ Closing position {ticket}...")
    sim.close_position(ticket)

    # Final account state
    account = sim.get_account_info()
    print(f"\n💰 Final Account:")
    print(f"  Balance: ${account['balance']:.2f}")
    print(f"  Equity: ${account['equity']:.2f}")
    print(f"  Total Trades: {len(sim.trade_history)}")

    print("\n✅ Mock MT5 Simulator test complete!")
