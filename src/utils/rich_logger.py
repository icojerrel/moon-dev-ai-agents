"""
🌙 Moon Dev's Rich Logging System
Enhanced console output with panels, themes, and structured events
Built with love by Moon Dev 🚀

Based on patterns from autonomous-researcher with Moon Dev enhancements.
"""

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from rich.logging import RichHandler
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import logging
import os
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Moon Dev custom theme - matching our trading bot aesthetic
moondev_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "bold green",
    "trade": "bold yellow",
    "whale": "bold blue",
    "risk": "bold red on white",
    "moon": "bold cyan",
    "profit": "bold green",
    "loss": "bold red",
})

# Global console instance
console = Console(theme=moondev_theme)

def setup_logging(agent_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup file + console logging for an agent

    Args:
        agent_name: Name of the agent (e.g., "trading_agent")
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger instance configured for both file and console output
    """
    log_dir = f"src/data/{agent_name}/logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(agent_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler (detailed logs)
    file_handler = logging.FileHandler(f"{log_dir}/{agent_name}.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Rich console handler (beautiful terminal output)
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_time=True,
        show_path=False
    )
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger


def print_panel(content: str, title: str, style: str = "info", expand: bool = False):
    """
    Print content in a styled Rich panel

    Args:
        content: Text to display
        title: Panel title (will be prefixed with 🌙)
        style: Color style from theme
        expand: Whether to expand panel to full width
    """
    console.print(Panel(
        content,
        title=f"🌙 {title}",
        border_style=style,
        expand=expand
    ))


def print_status(message: str, style: str = "info"):
    """
    Print status message with style

    Args:
        message: Status message
        style: Color style from theme
    """
    console.print(f"[{style}]{message}[/{style}]")


def print_trade_result(action: str, token: str, amount_usd: float, price: float, success: bool = True):
    """
    Print formatted trade result

    Args:
        action: BUY or SELL
        token: Token address or symbol
        amount_usd: Trade amount in USD
        price: Execution price
        success: Whether trade was successful
    """
    style = "success" if success else "error"
    symbol = "✅" if success else "❌"

    table = Table(show_header=False, box=None)
    table.add_row("Action:", f"[trade]{action}[/trade]")
    table.add_row("Token:", token[:8] + "..." if len(token) > 20 else token)
    table.add_row("Amount:", f"${amount_usd:,.2f}")
    table.add_row("Price:", f"${price:,.6f}")
    table.add_row("Status:", f"[{style}]{symbol} {'Success' if success else 'Failed'}[/{style}]")

    console.print(Panel(
        table,
        title=f"🌙 Trade Executed",
        border_style=style
    ))


def print_portfolio_summary(positions: list, total_value: float, pnl_24h: float):
    """
    Print formatted portfolio summary

    Args:
        positions: List of position dicts
        total_value: Total portfolio value in USD
        pnl_24h: 24h profit/loss in USD
    """
    pnl_style = "profit" if pnl_24h >= 0 else "loss"
    pnl_symbol = "📈" if pnl_24h >= 0 else "📉"

    table = Table(title="Portfolio Overview")
    table.add_column("Token", style="cyan")
    table.add_column("Position", justify="right", style="yellow")
    table.add_column("Value (USD)", justify="right", style="green")
    table.add_column("PnL %", justify="right")

    for pos in positions:
        pnl_pct = pos.get('pnl_percentage', 0)
        pnl_color = "profit" if pnl_pct >= 0 else "loss"
        table.add_row(
            pos['token'][:8] + "...",
            f"{pos['size']:.4f}",
            f"${pos['value_usd']:,.2f}",
            f"[{pnl_color}]{pnl_pct:+.2f}%[/{pnl_color}]"
        )

    console.print(table)
    console.print(f"\n💰 Total Value: [success]${total_value:,.2f}[/success]")
    console.print(f"{pnl_symbol} 24h PnL: [{pnl_style}]${pnl_24h:+,.2f}[/{pnl_style}]\n")


def emit_event(event_type: str, data: Dict[str, Any]):
    """
    Emit structured event for web UI consumption

    Events are only emitted when MOONDEV_ENABLE_EVENTS environment variable is set.
    This keeps CLI output clean while enabling rich web UI integration.

    Args:
        event_type: Type of event (e.g., TRADE_EXECUTED, WHALE_DETECTED)
        data: Event data dictionary

    Event format:
        ::MOONDEV_EVENT::{"type": "TRADE_EXECUTED", "timestamp": "...", "data": {...}}
    """
    if not os.environ.get("MOONDEV_ENABLE_EVENTS"):
        return

    payload = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }

    # Use special prefix that frontend can parse
    print(f"::MOONDEV_EVENT::{json.dumps(payload)}")
    sys.stdout.flush()


def log_step(step_name: str, status: str = "INFO", logger: Optional[logging.Logger] = None):
    """
    Log a step to file (and optionally console)

    Args:
        step_name: Name of the step/operation
        status: Status or description
        logger: Optional logger instance (creates default if not provided)
    """
    if logger is None:
        # Use root logger if none provided
        logger = logging.getLogger("moondev")

    logger.info(f"[{step_name}] {status}")


# Backwards compatibility with termcolor.cprint
def cprint_compat(message: str, color: str, **kwargs):
    """
    Backwards compatible with termcolor.cprint()

    Allows gradual migration: existing code keeps working,
    new code uses Rich features.

    Args:
        message: Message to print
        color: Color name (cyan, yellow, red, green, blue)
    """
    style_map = {
        "cyan": "info",
        "yellow": "warning",
        "red": "error",
        "green": "success",
        "blue": "whale",
        "white": "moon"
    }

    style = style_map.get(color, "info")
    console.print(f"[{style}]{message}[/{style}]")


def create_progress_bar(description: str = "Processing") -> Progress:
    """
    Create a Rich progress bar for long-running operations

    Args:
        description: Description of the operation

    Returns:
        Progress instance (use with context manager)

    Example:
        with create_progress_bar("Analyzing tokens") as progress:
            task = progress.add_task("[cyan]Processing...", total=len(tokens))
            for token in tokens:
                # Do work
                progress.update(task, advance=1)
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )


def print_agent_header(agent_name: str, status: str = "STARTING"):
    """
    Print agent header banner

    Args:
        agent_name: Name of the agent
        status: Current status
    """
    console.print("\n" + "═" * 60, style="moon")
    console.print(f"🌙 {agent_name.upper()} - {status}", style="bold moon")
    console.print("═" * 60 + "\n", style="moon")


def print_error_panel(error: Exception, context: str = ""):
    """
    Print detailed error panel with traceback

    Args:
        error: Exception instance
        context: Additional context about where error occurred
    """
    import traceback

    error_details = f"""
Error Type: {type(error).__name__}
Message: {str(error)}

Context: {context}

Traceback:
{traceback.format_exc()}
    """.strip()

    print_panel(error_details, "ERROR DETAILS", style="error", expand=False)


# Export main functions
__all__ = [
    'console',
    'setup_logging',
    'print_panel',
    'print_status',
    'print_trade_result',
    'print_portfolio_summary',
    'emit_event',
    'log_step',
    'cprint_compat',
    'create_progress_bar',
    'print_agent_header',
    'print_error_panel',
]
