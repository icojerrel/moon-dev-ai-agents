#!/usr/bin/env python3
"""
LIVE VALIDATION PROTOCOL
========================

No more backtesting lottery - real-time strategy validation
Paper trading with real market data for accurate performance measurement
"""

import asyncio
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from enum import Enum
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ValidationStatus(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PROFITABLE = "PROFITABLE"
    LOSING = "LOSING"
    TERMINATED = "TERMINATED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"

@dataclass
class TradeSignal:
    """Trading signal to be validated"""
    signal_id: str
    strategy_type: str
    token: str
    action: str  # 'LONG' or 'SHORT'
    confidence: float
    entry_price: float
    position_size: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    entry_time: datetime
    max_duration_hours: int = 24  # Auto-close after 24 hours

@dataclass
class ValidationTrade:
    """Live trade being validated"""
    trade_id: str
    signal: TradeSignal
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    exit_price: Optional[float]
    exit_time: Optional[datetime]
    status: ValidationStatus
    max_unrealized_pnl: float
    min_unrealized_pnl: float
    duration_minutes: int
    exit_reason: str = ""

class LiveValidationProtocol:
    """
    Real-time strategy validation - no backtesting bias
    """

    def __init__(self, portfolio_value: float = 10000):
        self.portfolio_value = portfolio_value
        self.active_trades: Dict[str, ValidationTrade] = {}
        self.completed_trades: List[ValidationTrade] = []

        # Validation parameters
        self.min_trades_for_validation = 20
        self.validation_confidence_threshold = 60
        self.max_concurrent_validations = 10
        self.max_validation_duration_hours = 48

        # Database setup
        self.db_path = "data/validation_results.db"
        self.setup_database()

        # Performance tracking
        self.total_signals_received = 0
        self.total_trades_executed = 0
        self.validation_results = {}

    def setup_database(self):
        """Setup SQLite database for validation results"""
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_trades (
                trade_id TEXT PRIMARY KEY,
                signal_id TEXT,
                strategy_type TEXT,
                token TEXT,
                action TEXT,
                entry_price REAL,
                exit_price REAL,
                position_size REAL,
                unrealized_pnl REAL,
                realized_pnl REAL,
                confidence INTEGER,
                entry_time TEXT,
                exit_time TEXT,
                duration_minutes INTEGER,
                status TEXT,
                exit_reason TEXT,
                max_unrealized_pnl REAL,
                min_unrealized_pnl REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_validation (
                strategy_type TEXT PRIMARY KEY,
                total_trades INTEGER,
                profitable_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                avg_return REAL,
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                validation_status TEXT,
                last_updated TEXT,
                sample_size INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def print_message(self, message, msg_type="info"):
        """Print without Unicode issues"""
        if msg_type == "success":
            print(f"[SUCCESS] {message}")
        elif msg_type == "warning":
            print(f"[WARNING] {message}")
        elif msg_type == "error":
            print(f"[ERROR] {message}")
        elif msg_type == "alert":
            print(f"[ALERT] {message}")
        else:
            print(f"[INFO] {message}")

    def receive_signal(self, signal_data: Dict) -> str:
        """
        Receive new trading signal for validation
        """
        try:
            # Generate unique signal ID
            signal_id = f"signal_{int(time.time() * 1000)}"

            # Create TradeSignal object
            signal = TradeSignal(
                signal_id=signal_id,
                strategy_type=signal_data.get('strategy_type', 'unknown'),
                token=signal_data.get('token', 'UNKNOWN'),
                action=signal_data.get('action', 'LONG'),
                confidence=signal_data.get('confidence', 0),
                entry_price=signal_data.get('entry_price', 0),
                position_size=signal_data.get('position_size', 0),
                stop_loss=signal_data.get('stop_loss'),
                take_profit=signal_data.get('take_profit'),
                entry_time=datetime.now()
            )

            self.total_signals_received += 1

            # Check if we should validate this signal
            if len(self.active_trades) >= self.max_concurrent_validations:
                self.print_message(f"Max concurrent validations reached ({self.max_concurrent_validations})", "warning")
                return signal_id

            if signal.confidence < self.validation_confidence_threshold:
                self.print_message(f"Signal confidence too low: {signal.confidence}%", "warning")
                return signal_id

            # Start validation
            self.start_validation(signal)

            self.print_message(f"Started validation for {signal.token} {signal.action} signal (ID: {signal_id[:8]})", "success")

            return signal_id

        except Exception as e:
            self.print_message(f"Error receiving signal: {e}", "error")
            return None

    def start_validation(self, signal: TradeSignal):
        """
        Start live validation of a trading signal
        """
        trade_id = f"trade_{int(time.time() * 1000)}"

        validation_trade = ValidationTrade(
            trade_id=trade_id,
            signal=signal,
            current_price=signal.entry_price,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            exit_price=None,
            exit_time=None,
            status=ValidationStatus.ACTIVE,
            max_unrealized_pnl=0.0,
            min_unrealized_pnl=0.0,
            duration_minutes=0
        )

        self.active_trades[trade_id] = validation_trade
        self.total_trades_executed += 1

    def update_trade_prices(self, market_prices: Dict[str, float]):
        """
        Update current prices for all active trades
        """
        for trade_id, trade in list(self.active_trades.items()):
            token = trade.signal.token

            if token in market_prices:
                old_price = trade.current_price
                new_price = market_prices[token]
                trade.current_price = new_price

                # Calculate unrealized PnL
                if trade.signal.action == 'LONG':
                    trade.unrealized_pnl = (new_price - trade.signal.entry_price) / trade.signal.entry_price * trade.signal.position_size
                else:  # SHORT
                    trade.unrealized_pnl = (trade.signal.entry_price - new_price) / trade.signal.entry_price * trade.signal.position_size

                # Update max/min PnL
                trade.max_unrealized_pnl = max(trade.max_unrealized_pnl, trade.unrealized_pnl)
                trade.min_unrealized_pnl = min(trade.min_unrealized_pnl, trade.unrealized_pnl)

                # Update duration
                trade.duration_minutes = int((datetime.now() - trade.signal.entry_time).total_seconds() / 60)

                # Check exit conditions
                self.check_exit_conditions(trade, old_price, new_price)

    def check_exit_conditions(self, trade: ValidationTrade, old_price: float, new_price: float):
        """
        Check if trade should be closed based on stop loss, take profit, or time
        """
        exit_reason = None
        should_exit = False

        # Stop loss check
        if trade.signal.stop_loss is not None:
            if trade.signal.action == 'LONG' and new_price <= trade.signal.stop_loss:
                should_exit = True
                exit_reason = "Stop Loss Hit"
            elif trade.signal.action == 'SHORT' and new_price >= trade.signal.stop_loss:
                should_exit = True
                exit_reason = "Stop Loss Hit"

        # Take profit check
        if trade.signal.take_profit is not None and not should_exit:
            if trade.signal.action == 'LONG' and new_price >= trade.signal.take_profit:
                should_exit = True
                exit_reason = "Take Profit Hit"
            elif trade.signal.action == 'SHORT' and new_price <= trade.signal.take_profit:
                should_exit = True
                exit_reason = "Take Profit Hit"

        # Time-based exit
        if not should_exit:
            if trade.duration_minutes >= trade.signal.max_duration_hours * 60:
                should_exit = True
                exit_reason = "Time Exit"

        # Maximum validation duration
        if not should_exit:
            if trade.duration_minutes >= self.max_validation_duration_hours * 60:
                should_exit = True
                exit_reason = "Max Validation Time"

        # Execute exit
        if should_exit:
            self.close_trade(trade, exit_reason)

    def close_trade(self, trade: ValidationTrade, exit_reason: str):
        """
        Close a validation trade and record results
        """
        trade.exit_price = trade.current_price
        trade.exit_time = datetime.now()
        trade.realized_pnl = trade.unrealized_pnl
        trade.exit_reason = exit_reason

        # Determine final status
        if trade.realized_pnl > 0:
            trade.status = ValidationStatus.PROFITABLE
        elif trade.realized_pnl < 0:
            trade.status = ValidationStatus.LOSING
        else:
            trade.status = ValidationStatus.TERMINATED

        # Move to completed trades
        self.completed_trades.append(trade)
        del self.active_trades[trade.trade_id]

        # Save to database
        self.save_trade_to_db(trade)

        # Update strategy validation
        self.update_strategy_validation(trade.signal.strategy_type)

        self.print_message(f"Trade closed: {trade.signal.token} {trade.signal.action} | P&L: ${trade.realized_pnl:.2f} | Reason: {exit_reason}",
                         "success" if trade.realized_pnl > 0 else "warning")

    def save_trade_to_db(self, trade: ValidationTrade):
        """
        Save trade results to database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO validation_trades
                (trade_id, signal_id, strategy_type, token, action, entry_price, exit_price,
                 position_size, unrealized_pnl, realized_pnl, confidence, entry_time,
                 exit_time, duration_minutes, status, exit_reason, max_unrealized_pnl, min_unrealized_pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id,
                trade.signal.signal_id,
                trade.signal.strategy_type,
                trade.signal.token,
                trade.signal.action,
                trade.signal.entry_price,
                trade.exit_price,
                trade.signal.position_size,
                trade.unrealized_pnl,
                trade.realized_pnl,
                trade.signal.confidence,
                trade.signal.entry_time.isoformat(),
                trade.exit_time.isoformat() if trade.exit_time else None,
                trade.duration_minutes,
                trade.status.value,
                trade.exit_reason,
                trade.max_unrealized_pnl,
                trade.min_unrealized_pnl
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.print_message(f"Error saving trade to database: {e}", "error")

    def update_strategy_validation(self, strategy_type: str):
        """
        Update strategy validation statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all trades for this strategy
            cursor.execute('''
                SELECT realized_pnl, duration_minutes, status
                FROM validation_trades
                WHERE strategy_type = ? AND realized_pnl IS NOT NULL
            ''', (strategy_type,))

            trades = cursor.fetchall()

            if len(trades) < 5:  # Need minimum trades for validation
                conn.close()
                return

            # Calculate statistics
            total_trades = len(trades)
            profits = [t[0] for t in trades if t[0] > 0]
            losses = [t[0] for t in trades if t[0] < 0]

            profitable_trades = len(profits)
            losing_trades = len(losses)
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0

            avg_return = statistics.mean([t[0] for t in trades]) if trades else 0
            total_return = sum(t[0] for t in trades)

            # Calculate Sharpe ratio (simplified)
            if len(trades) > 1:
                returns = [t[0] / 1000 for t in trades]  # Normalize by $1000 position
                avg_daily_return = statistics.mean(returns)
                std_return = statistics.stdev(returns) if len(returns) > 1 else 0
                sharpe_ratio = avg_daily_return / std_return if std_return > 0 else 0
            else:
                sharpe_ratio = 0

            # Calculate max drawdown
            cumulative_returns = np.cumsum([t[0] for t in trades])
            peak = np.maximum.accumulate(cumulative_returns)
            drawdown = (peak - cumulative_returns) / peak * 100
            max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

            # Determine validation status
            if total_trades >= self.min_trades_for_validation:
                if win_rate >= 0.55 and avg_return > 0 and sharpe_ratio > 0.5:
                    validation_status = "VALIDATED"
                elif win_rate < 0.4 or avg_return < 0:
                    validation_status = "REJECTED"
                else:
                    validation_status = "PENDING"
            else:
                validation_status = "INSUFFICIENT_DATA"

            # Update database
            cursor.execute('''
                INSERT OR REPLACE INTO strategy_validation
                (strategy_type, total_trades, profitable_trades, losing_trades, win_rate,
                 avg_return, total_return, sharpe_ratio, max_drawdown, validation_status,
                 last_updated, sample_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strategy_type, total_trades, profitable_trades, losing_trades, win_rate,
                avg_return, total_return, sharpe_ratio, max_drawdown, validation_status,
                datetime.now().isoformat(), total_trades
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.print_message(f"Error updating strategy validation: {e}", "error")

    def get_validation_report(self) -> Dict:
        """
        Generate comprehensive validation report
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get strategy validations
            cursor.execute('SELECT * FROM strategy_validation ORDER BY total_trades DESC')
            strategies = cursor.fetchall()

            strategy_report = []
            for strategy in strategies:
                strategy_report.append({
                    'strategy_type': strategy[0],
                    'total_trades': strategy[1],
                    'win_rate': strategy[4],
                    'avg_return': strategy[5],
                    'sharpe_ratio': strategy[7],
                    'validation_status': strategy[9],
                    'sample_size': strategy[11]
                })

            # Get recent trades
            cursor.execute('''
                SELECT strategy_type, token, action, realized_pnl, exit_reason, entry_time
                FROM validation_trades
                WHERE realized_pnl IS NOT NULL
                ORDER BY entry_time DESC
                LIMIT 10
            ''')
            recent_trades = cursor.fetchall()

            conn.close()

            # Calculate portfolio metrics
            total_completed = len(self.completed_trades)
            total_pnl = sum(t.realized_pnl for t in self.completed_trades)
            win_trades = len([t for t in self.completed_trades if t.realized_pnl > 0])
            overall_win_rate = win_trades / total_completed if total_completed > 0 else 0

            return {
                'total_signals_received': self.total_signals_received,
                'total_trades_executed': self.total_trades_executed,
                'active_validations': len(self.active_trades),
                'completed_trades': total_completed,
                'total_pnl': total_pnl,
                'overall_win_rate': overall_win_rate,
                'strategy_validations': strategy_report,
                'recent_trades': recent_trades
            }

        except Exception as e:
            self.print_message(f"Error generating validation report: {e}", "error")
            return {}

    def print_validation_dashboard(self):
        """
        Print comprehensive validation dashboard
        """
        report = self.get_validation_report()

        print(f"\nLIVE VALIDATION DASHBOARD")
        print("=" * 60)

        # Overview
        print(f"Signals Received: {report.get('total_signals_received', 0)}")
        print(f"Trades Executed: {report.get('total_trades_executed', 0)}")
        print(f"Active Validations: {report.get('active_validations', 0)}")
        print(f"Completed Trades: {report.get('completed_trades', 0)}")

        if report.get('completed_trades', 0) > 0:
            total_pnl = report.get('total_pnl', 0)
            win_rate = report.get('overall_win_rate', 0) * 100

            pnl_color = "GREEN" if total_pnl > 0 else "RED"
            print(f"Total P&L: ${total_pnl:.2f} [{pnl_color}]")
            print(f"Win Rate: {win_rate:.1f}%")

        # Strategy validation
        print(f"\nSTRATEGY VALIDATION STATUS:")
        print("-" * 40)

        for strategy in report.get('strategy_validations', []):
            status_color = {
                'VALIDATED': 'GREEN',
                'PENDING': 'YELLOW',
                'REJECTED': 'RED',
                'INSUFFICIENT_DATA': 'GRAY'
            }.get(strategy['validation_status'], 'WHITE')

            print(f"{strategy['strategy_type']}:")
            print(f"  Trades: {strategy['total_trades']} | Win Rate: {strategy['win_rate']*100:.1f}%")
            print(f"  Avg Return: ${strategy['avg_return']:.2f} | Sharpe: {strategy['sharpe_ratio']:.2f}")
            print(f"  Status: {strategy['validation_status']} [{status_color}]")
            print()

        # Active trades
        if self.active_trades:
            print(f"ACTIVE VALIDATIONS:")
            print("-" * 40)

            for trade_id, trade in list(self.active_trades.items())[:5]:  # Show top 5
                pnl_color = "GREEN" if trade.unrealized_pnl > 0 else "RED"
                print(f"{trade.signal.token} {trade.signal.action}: ${trade.unrealized_pnl:.2f} [{pnl_color}] ({trade.duration_minutes} min)")

async def main():
    """Test the live validation protocol"""
    print("LIVE VALIDATION PROTOCOL")
    print("=" * 40)
    print("Real-time strategy validation - no backtesting bias")

    validator = LiveValidationProtocol(portfolio_value=10000)

    try:
        # Simulate receiving some signals
        print("\n[DEMO] Simulating signal reception...")

        mock_signals = [
            {
                'strategy_type': 'carry_trade',
                'token': 'BTC',
                'action': 'SHORT',
                'confidence': 75,
                'entry_price': 45000,
                'position_size': 1000,
                'stop_loss': 46000,
                'take_profit': 44000
            },
            {
                'strategy_type': 'liquidity_hunting',
                'token': 'SOL',
                'action': 'LONG',
                'confidence': 65,
                'entry_price': 65,
                'position_size': 800,
                'stop_loss': 62,
                'take_profit': 70
            },
            {
                'strategy_type': 'microstructure',
                'token': 'ETH',
                'action': 'LONG',
                'confidence': 55,
                'entry_price': 2400,
                'position_size': 600,
                'stop_loss': 2350,
                'take_profit': 2450
            }
        ]

        # Process signals
        for signal in mock_signals:
            signal_id = validator.receive_signal(signal)
            await asyncio.sleep(0.1)  # Small delay

        # Simulate price updates
        print("\n[DEMO] Simulating market price updates...")

        price_updates = [
            {'BTC': 44800, 'SOL': 66, 'ETH': 2410},  # BTC down, SOL up, ETH up
            {'BTC': 44700, 'SOL': 67, 'ETH': 2420},  # Continue trend
            {'BTC': 45200, 'SOL': 64, 'ETH': 2395},  # BTC reverses, SOL down, ETH down
        ]

        for i, prices in enumerate(price_updates):
            validator.update_trade_prices(prices)
            print(f"Price update {i+1}: {prices}")
            await asyncio.sleep(1)

        # Simulate time passing (close some trades)
        print("\n[DEMO] Simulating time progression...")

        for trade_id, trade in list(validator.active_trades.items())[:2]:
            trade.duration_minutes = 180  # 3 hours
            validator.check_exit_conditions(trade, trade.current_price, trade.current_price * 1.01)

        # Print final dashboard
        validator.print_validation_dashboard()

        return validator

    except Exception as e:
        validator.print_message(f"Validation protocol failed: {e}", "error")
        return validator

if __name__ == "__main__":
    import os
    validator = asyncio.run(main())