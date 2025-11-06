"""
🌙 Moon Dev's Position Sizing Calculator
Professional position sizing for different account sizes
"""

from typing import Dict


class PositionSizer:
    """Calculate optimal position sizes based on account size and risk"""

    @staticmethod
    def calculate_lot_size(account_balance: float, risk_percentage: float,
                          stop_loss_pips: float, symbol: str = "EURUSD") -> float:
        """
        Calculate position size in lots based on risk parameters

        Args:
            account_balance: Account balance in USD
            risk_percentage: Risk per trade (e.g., 0.01 for 1%)
            stop_loss_pips: Stop loss distance in pips
            symbol: Trading symbol (for pip value calculation)

        Returns:
            Position size in lots
        """
        # Risk amount in USD
        risk_amount = account_balance * risk_percentage

        # Pip value calculation (for standard lot = 100,000 units)
        # For EURUSD, GBPUSD: 1 pip = $10 per standard lot
        # For USDJPY: 1 pip = $9.09 per standard lot (approximate)
        if "JPY" in symbol:
            pip_value_per_lot = 9.09
        else:
            pip_value_per_lot = 10.0

        # Calculate lot size
        if stop_loss_pips <= 0:
            return 0.01  # Minimum lot size

        lot_size = risk_amount / (stop_loss_pips * pip_value_per_lot)

        # Round to 2 decimal places (mini lots)
        lot_size = round(lot_size, 2)

        # Apply limits based on account size
        min_lot, max_lot = PositionSizer.get_lot_limits(account_balance)
        lot_size = max(min_lot, min(lot_size, max_lot))

        return lot_size

    @staticmethod
    def get_lot_limits(account_balance: float) -> tuple:
        """
        Get min/max lot sizes based on account balance

        Args:
            account_balance: Account balance in USD

        Returns:
            Tuple of (min_lot, max_lot)
        """
        if account_balance < 1000:
            return (0.01, 0.05)  # Micro account
        elif account_balance < 5000:
            return (0.01, 0.10)  # Small account
        elif account_balance < 10000:
            return (0.01, 0.25)  # Medium account
        elif account_balance < 50000:
            return (0.05, 1.0)   # Large account
        elif account_balance < 100000:
            return (0.10, 2.0)   # Very large account
        else:
            return (0.20, 5.0)   # Professional account ($100k+)

    @staticmethod
    def get_risk_params(account_balance: float) -> Dict:
        """
        Get recommended risk parameters based on account size

        Args:
            account_balance: Account balance in USD

        Returns:
            Dict with risk parameters
        """
        if account_balance < 10000:
            # Conservative for small accounts
            return {
                'risk_per_trade': 0.01,  # 1%
                'max_positions': 2,
                'max_daily_loss': 0.03,  # 3%
                'take_profit_r': 2.0,    # 2R
                'stop_loss_r': 1.0,      # 1R
                'min_confidence': 80
            }
        elif account_balance < 50000:
            # Balanced approach
            return {
                'risk_per_trade': 0.01,  # 1%
                'max_positions': 3,
                'max_daily_loss': 0.04,  # 4%
                'take_profit_r': 2.5,    # 2.5R
                'stop_loss_r': 1.0,      # 1R
                'min_confidence': 75
            }
        elif account_balance < 100000:
            # Aggressive growth
            return {
                'risk_per_trade': 0.015, # 1.5%
                'max_positions': 4,
                'max_daily_loss': 0.05,  # 5%
                'take_profit_r': 3.0,    # 3R
                'stop_loss_r': 1.0,      # 1R
                'min_confidence': 75
            }
        else:
            # Professional ($100k+)
            return {
                'risk_per_trade': 0.01,  # 1% (conservative with large capital)
                'max_positions': 5,
                'max_daily_loss': 0.04,  # 4%
                'take_profit_r': 3.0,    # 3R
                'stop_loss_r': 1.0,      # 1R
                'min_confidence': 75
            }

    @staticmethod
    def calculate_stop_loss_pips(entry_price: float, stop_loss_price: float,
                                 symbol: str = "EURUSD") -> float:
        """
        Calculate stop loss distance in pips

        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            symbol: Trading symbol

        Returns:
            Stop loss distance in pips
        """
        if "JPY" in symbol:
            # JPY pairs: 1 pip = 0.01
            pip_size = 0.01
        else:
            # Most pairs: 1 pip = 0.0001
            pip_size = 0.0001

        distance = abs(entry_price - stop_loss_price)
        pips = distance / pip_size

        return pips


# Example usage and testing
if __name__ == "__main__":
    from termcolor import cprint

    cprint("\n💰 Position Sizing Calculator Test\n", "cyan", attrs=["bold"])

    # Test different account sizes
    account_sizes = [1000, 10000, 50000, 150000, 500000]

    for balance in account_sizes:
        cprint(f"\n{'='*60}", "cyan")
        cprint(f"Account Balance: ${balance:,}", "white", attrs=["bold"])
        cprint(f"{'='*60}", "cyan")

        # Get risk parameters
        params = PositionSizer.get_risk_params(balance)

        cprint("\n📊 Risk Parameters:", "yellow")
        cprint(f"  Risk per trade: {params['risk_per_trade']*100}%", "white")
        cprint(f"  Max positions: {params['max_positions']}", "white")
        cprint(f"  Max daily loss: {params['max_daily_loss']*100}%", "white")
        cprint(f"  Take profit: {params['take_profit_r']}R", "white")
        cprint(f"  Stop loss: {params['stop_loss_r']}R", "white")
        cprint(f"  Min confidence: {params['min_confidence']}%", "white")

        # Calculate position size for example trade
        stop_loss_pips = 30
        lot_size = PositionSizer.calculate_lot_size(
            balance,
            params['risk_per_trade'],
            stop_loss_pips
        )

        risk_amount = balance * params['risk_per_trade']
        position_value = lot_size * 100000  # Standard lot value

        cprint("\n💼 Example Trade (30 pip SL):", "yellow")
        cprint(f"  Risk amount: ${risk_amount:,.2f}", "white")
        cprint(f"  Lot size: {lot_size}", "green", attrs=["bold"])
        cprint(f"  Position value: ${position_value:,.2f}", "white")
        cprint(f"  Max loss if SL hit: ${stop_loss_pips * 10 * lot_size:,.2f}", "red")
        cprint(f"  Expected profit (2R): ${stop_loss_pips * 10 * lot_size * 2:,.2f}", "green")

    cprint("\n✅ Position sizing calculator ready!\n", "green", attrs=["bold"])
