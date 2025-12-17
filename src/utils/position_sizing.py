"""
🌙 Moon Dev's Position Sizing Module
Built with love by Moon Dev 🚀

Implements Kelly Criterion and other position sizing algorithms
for optimal risk-adjusted returns.

The Kelly Criterion maximizes long-term growth by sizing positions
based on win rate and risk/reward ratio.

Usage:
    from src.utils.position_sizing import kelly_criterion, position_size_usd

    # Calculate optimal position fraction
    kelly_frac = kelly_criterion(
        win_rate=0.60,          # 60% win rate
        avg_win_pct=0.15,       # Average win: +15%
        avg_loss_pct=0.10,      # Average loss: -10%
        fraction=0.25           # Use 1/4 Kelly (conservative)
    )

    # Convert to USD position size
    position_usd = position_size_usd(
        kelly_fraction=kelly_frac,
        capital_usd=10000,
        max_position_pct=0.20   # Cap at 20% of capital
    )

    print(f"Position size: ${position_usd:.2f}")
"""

from decimal import Decimal
from typing import Union, Optional
from termcolor import cprint


def kelly_criterion(
    win_rate: float,
    avg_win_pct: float,
    avg_loss_pct: float,
    fraction: float = 0.25
) -> float:
    """
    Calculate optimal position size using Kelly Criterion

    The Kelly Criterion formula: f* = (p * b - q) / b
    where:
        p = probability of winning (win_rate)
        q = probability of losing (1 - win_rate)
        b = ratio of average win to average loss
        f* = optimal fraction of capital to risk

    We use "Fractional Kelly" (typically 1/4 to 1/2) to reduce variance
    and account for estimation errors in win rate and avg returns.

    Args:
        win_rate: Probability of winning trade (0-1, e.g., 0.60 for 60%)
        avg_win_pct: Average winning trade return (e.g., 0.15 for +15%)
        avg_loss_pct: Average losing trade return (e.g., 0.10 for -10%)
        fraction: Fraction of Kelly to use (default 0.25 = "Quarter Kelly")
                 Common values:
                 - 1.0 = Full Kelly (aggressive, high volatility)
                 - 0.5 = Half Kelly (balanced)
                 - 0.25 = Quarter Kelly (conservative, recommended)

    Returns:
        Optimal position size as fraction of capital (0-1)
        Returns 0 if Kelly would be negative (unfavorable odds)

    Example:
        >>> kelly_criterion(0.60, 0.15, 0.10, fraction=0.25)
        0.175  # Risk 17.5% of capital on this trade

    References:
        - Kelly, J. L. (1956). "A New Interpretation of Information Rate"
        - Thorp, Edward O. (2006). "The Kelly Criterion in Blackjack Sports Betting, and the Stock Market"
    """
    # Validate inputs
    if not 0 <= win_rate <= 1:
        raise ValueError(f"win_rate must be between 0 and 1, got {win_rate}")

    if avg_win_pct <= 0:
        raise ValueError(f"avg_win_pct must be positive, got {avg_win_pct}")

    if avg_loss_pct <= 0:
        raise ValueError(f"avg_loss_pct must be positive, got {avg_loss_pct}")

    if not 0 < fraction <= 1:
        raise ValueError(f"fraction must be between 0 and 1, got {fraction}")

    # Kelly Criterion calculation
    p = win_rate
    q = 1 - win_rate
    b = avg_win_pct / avg_loss_pct  # Win/loss ratio

    # f* = (p * b - q) / b
    kelly = (p * b - q) / b

    # Apply fractional Kelly (reduce volatility)
    fractional_kelly = kelly * fraction

    # Never go negative (unfavorable odds)
    return max(0.0, fractional_kelly)


def half_kelly(win_rate: float, avg_win_pct: float, avg_loss_pct: float) -> float:
    """
    Half Kelly - balanced between growth and risk

    Args:
        win_rate: Probability of winning (0-1)
        avg_win_pct: Average win percentage
        avg_loss_pct: Average loss percentage

    Returns:
        Position size as fraction of capital
    """
    return kelly_criterion(win_rate, avg_win_pct, avg_loss_pct, fraction=0.5)


def quarter_kelly(win_rate: float, avg_win_pct: float, avg_loss_pct: float) -> float:
    """
    Quarter Kelly - conservative approach (RECOMMENDED)

    Reduces volatility significantly while still capturing most of
    the long-term growth. Best for real trading.

    Args:
        win_rate: Probability of winning (0-1)
        avg_win_pct: Average win percentage
        avg_loss_pct: Average loss percentage

    Returns:
        Position size as fraction of capital
    """
    return kelly_criterion(win_rate, avg_win_pct, avg_loss_pct, fraction=0.25)


def position_size_usd(
    kelly_fraction: float,
    capital_usd: Union[int, float, Decimal],
    max_position_pct: float = 0.20,
    min_position_usd: float = 10.0
) -> Decimal:
    """
    Convert Kelly fraction to USD position size with safety caps

    Args:
        kelly_fraction: Kelly criterion result (0-1)
        capital_usd: Total available capital in USD
        max_position_pct: Maximum position size as % of capital (default 20%)
        min_position_usd: Minimum position size in USD (default $10)

    Returns:
        Position size in USD (Decimal for precision)

    Example:
        >>> position_size_usd(0.15, 10000, max_position_pct=0.20)
        Decimal('1500.00')  # 15% of $10,000 = $1,500

        >>> position_size_usd(0.30, 10000, max_position_pct=0.20)
        Decimal('2000.00')  # Capped at 20% = $2,000
    """
    # Validate inputs
    if kelly_fraction < 0:
        raise ValueError(f"kelly_fraction cannot be negative: {kelly_fraction}")

    capital = Decimal(str(capital_usd))
    if capital <= 0:
        raise ValueError(f"capital_usd must be positive, got {capital_usd}")

    # Calculate position size
    position = capital * Decimal(str(kelly_fraction))

    # Apply maximum position cap (risk management)
    max_position = capital * Decimal(str(max_position_pct))
    position = min(position, max_position)

    # Apply minimum position (avoid dust trades)
    if position < Decimal(str(min_position_usd)):
        cprint(f"⚠️  Position ${position:.2f} below minimum ${min_position_usd}", "yellow")
        return Decimal('0')

    return position.quantize(Decimal('0.01'))  # Round to 2 decimal places


def fixed_fraction_sizing(
    capital_usd: Union[int, float, Decimal],
    fixed_pct: float = 0.02,
    max_position_pct: float = 0.20
) -> Decimal:
    """
    Simple fixed fraction position sizing (alternative to Kelly)

    Always risk a fixed percentage of capital per trade.
    Simpler than Kelly but doesn't optimize for win rate.

    Args:
        capital_usd: Total capital in USD
        fixed_pct: Fixed percentage to risk (default 2% = 0.02)
        max_position_pct: Maximum position cap (default 20%)

    Returns:
        Position size in USD

    Example:
        >>> fixed_fraction_sizing(10000, fixed_pct=0.02)
        Decimal('200.00')  # Always risk 2% = $200
    """
    capital = Decimal(str(capital_usd))
    position = capital * Decimal(str(fixed_pct))
    max_position = capital * Decimal(str(max_position_pct))

    return min(position, max_position).quantize(Decimal('0.01'))


def volatility_adjusted_sizing(
    capital_usd: Union[int, float, Decimal],
    target_volatility_pct: float = 0.10,
    realized_volatility_pct: float = 0.15,
    base_pct: float = 0.05
) -> Decimal:
    """
    Adjust position size based on volatility

    In high volatility environments, reduce position size.
    In low volatility, increase position size.

    Args:
        capital_usd: Total capital
        target_volatility_pct: Target portfolio volatility (default 10%)
        realized_volatility_pct: Current realized volatility (default 15%)
        base_pct: Base position size (default 5%)

    Returns:
        Volatility-adjusted position size in USD

    Example:
        >>> # High volatility (15%) > target (10%) → reduce position
        >>> volatility_adjusted_sizing(10000, 0.10, 0.15, 0.05)
        Decimal('333.33')  # Reduced from $500 base
    """
    capital = Decimal(str(capital_usd))

    # Adjust position inversely to volatility
    # If realized vol is 2x target, position is halved
    volatility_scalar = target_volatility_pct / realized_volatility_pct
    adjusted_pct = base_pct * volatility_scalar

    position = capital * Decimal(str(adjusted_pct))
    return position.quantize(Decimal('0.01'))


def calculate_risk_per_trade(
    position_size_usd: Union[int, float, Decimal],
    entry_price: float,
    stop_loss_price: float
) -> Decimal:
    """
    Calculate actual dollar risk for a trade with stop loss

    Args:
        position_size_usd: Position size in USD
        entry_price: Entry price
        stop_loss_price: Stop loss price

    Returns:
        Risk in USD (how much you'll lose if stopped out)

    Example:
        >>> calculate_risk_per_trade(1000, 100, 95)
        Decimal('50.00')  # 5% loss on $1000 = $50 risk
    """
    position = Decimal(str(position_size_usd))

    # Calculate percentage loss if stopped out
    loss_pct = abs((stop_loss_price - entry_price) / entry_price)

    # Dollar risk
    risk_usd = position * Decimal(str(loss_pct))

    return risk_usd.quantize(Decimal('0.01'))


# ============================================
# 🧪 TESTING & EXAMPLES
# ============================================

def run_examples():
    """Run position sizing examples for educational purposes"""
    cprint("\n🌙 Moon Dev's Position Sizing Examples\n", "cyan", attrs=["bold"])

    # Example 1: Quarter Kelly (Conservative)
    cprint("Example 1: Quarter Kelly (Recommended)", "cyan")
    kelly_frac = quarter_kelly(
        win_rate=0.60,      # 60% win rate
        avg_win_pct=0.15,   # +15% average win
        avg_loss_pct=0.10   # -10% average loss
    )
    position = position_size_usd(kelly_frac, capital_usd=10000)
    cprint(f"  Win Rate: 60% | Avg Win: +15% | Avg Loss: -10%", "white")
    cprint(f"  Kelly Fraction: {kelly_frac:.4f} ({kelly_frac*100:.2f}%)", "green")
    cprint(f"  Position Size: ${position} (on $10,000 capital)\n", "green")

    # Example 2: Half Kelly (Balanced)
    cprint("Example 2: Half Kelly (Balanced)", "cyan")
    kelly_frac = half_kelly(
        win_rate=0.55,
        avg_win_pct=0.20,
        avg_loss_pct=0.15
    )
    position = position_size_usd(kelly_frac, capital_usd=10000)
    cprint(f"  Win Rate: 55% | Avg Win: +20% | Avg Loss: -15%", "white")
    cprint(f"  Kelly Fraction: {kelly_frac:.4f} ({kelly_frac*100:.2f}%)", "green")
    cprint(f"  Position Size: ${position}\n", "green")

    # Example 3: Position Capping
    cprint("Example 3: Position Capping (Risk Management)", "cyan")
    kelly_frac = 0.35  # Would suggest 35% position
    position = position_size_usd(kelly_frac, capital_usd=10000, max_position_pct=0.20)
    cprint(f"  Kelly suggests: 35% position", "white")
    cprint(f"  Max allowed: 20% (risk cap)", "yellow")
    cprint(f"  Actual position: ${position} (capped at 20%)\n", "green")

    # Example 4: Fixed Fraction Alternative
    cprint("Example 4: Fixed Fraction (Simple Alternative)", "cyan")
    position = fixed_fraction_sizing(capital_usd=10000, fixed_pct=0.02)
    cprint(f"  Always risk: 2% of capital", "white")
    cprint(f"  Position Size: ${position}\n", "green")

    # Example 5: Risk Calculation
    cprint("Example 5: Risk Per Trade with Stop Loss", "cyan")
    risk = calculate_risk_per_trade(
        position_size_usd=1500,
        entry_price=100,
        stop_loss_price=95
    )
    cprint(f"  Position: $1,500 | Entry: $100 | Stop: $95", "white")
    cprint(f"  Risk if stopped out: ${risk}", "red")
    cprint(f"  Risk as % of $10k capital: {(float(risk)/10000)*100:.2f}%\n", "red")


if __name__ == "__main__":
    run_examples()
