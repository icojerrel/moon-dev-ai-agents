"""
🌙 Moon Dev's Production Logging System
Built with love by Moon Dev 🚀

Structured logging with:
- Log rotation
- Multiple log levels
- Separate files for errors
- JSON formatting option
- Console and file output
- Agent-specific loggers
"""

import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from termcolor import colored


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'white',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red',
    }

    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        emoji = self.EMOJIS.get(levelname, '')
        color = self.COLORS.get(levelname, 'white')

        # Format the message
        record.levelname = colored(f"{emoji} {levelname}", color)

        # Add agent name if present
        if hasattr(record, 'agent_name'):
            record.msg = f"[{record.agent_name}] {record.msg}"

        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add extra fields
        if hasattr(record, 'agent_name'):
            log_data['agent_name'] = record.agent_name

        if hasattr(record, 'trade_data'):
            log_data['trade_data'] = record.trade_data

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class LoggerManager:
    """Centralized logger management"""

    _instance = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Create logs directory
        self.log_dir = Path(__file__).parent.parent.parent / 'logs'
        self.log_dir.mkdir(exist_ok=True)

        # Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.json_logs = os.getenv('JSON_LOGS', 'false').lower() == 'true'
        self.max_bytes = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
        self.backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))

        self._initialized = True

    def get_logger(
        self,
        name: str,
        agent_name: Optional[str] = None,
        log_to_file: bool = True
    ) -> logging.Logger:
        """
        Get or create a logger

        Args:
            name: Logger name (usually __name__)
            agent_name: Optional agent name for filtering
            log_to_file: Whether to log to files

        Returns:
            Configured logger instance
        """
        # Use cached logger if exists
        cache_key = f"{name}_{agent_name}"
        if cache_key in self._loggers:
            return self._loggers[cache_key]

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.log_level))
        logger.propagate = False

        # Clear existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        if self.json_logs:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_format = '%(asctime)s - %(levelname)s - %(message)s'
            console_handler.setFormatter(ColoredFormatter(console_format))

        logger.addHandler(console_handler)

        # File handlers
        if log_to_file:
            # Main log file (all levels)
            main_log_file = self.log_dir / 'moondev_agents.log'
            file_handler = logging.handlers.RotatingFileHandler(
                main_log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count
            )
            file_handler.setLevel(logging.DEBUG)

            if self.json_logs:
                file_handler.setFormatter(JSONFormatter())
            else:
                file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                file_handler.setFormatter(logging.Formatter(file_format))

            logger.addHandler(file_handler)

            # Error log file (errors only)
            error_log_file = self.log_dir / 'moondev_errors.log'
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count
            )
            error_handler.setLevel(logging.ERROR)

            if self.json_logs:
                error_handler.setFormatter(JSONFormatter())
            else:
                error_handler.setFormatter(logging.Formatter(file_format))

            logger.addHandler(error_handler)

            # Agent-specific log file
            if agent_name:
                agent_log_file = self.log_dir / f'{agent_name}.log'
                agent_handler = logging.handlers.RotatingFileHandler(
                    agent_log_file,
                    maxBytes=self.max_bytes,
                    backupCount=self.backup_count
                )
                agent_handler.setLevel(logging.DEBUG)

                if self.json_logs:
                    agent_handler.setFormatter(JSONFormatter())
                else:
                    agent_handler.setFormatter(logging.Formatter(file_format))

                # Add filter for agent-specific logs
                agent_handler.addFilter(lambda record: getattr(record, 'agent_name', None) == agent_name)
                logger.addHandler(agent_handler)

        # Cache logger
        self._loggers[cache_key] = logger

        return logger

    def log_trade(
        self,
        logger: logging.Logger,
        action: str,
        symbol: str,
        amount: float,
        price: float,
        **kwargs
    ):
        """
        Log trade execution with structured data

        Args:
            logger: Logger instance
            action: Trade action (BUY/SELL/CLOSE)
            symbol: Trading symbol
            amount: Trade amount
            price: Execution price
            **kwargs: Additional trade data
        """
        trade_data = {
            'action': action,
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }

        # Add trade data to log record
        extra = {'trade_data': trade_data}

        logger.info(
            f"{action} {amount} {symbol} @ {price}",
            extra=extra
        )

        # Also write to trades log file
        trades_log_file = self.log_dir / 'trades.log'
        with open(trades_log_file, 'a') as f:
            f.write(json.dumps(trade_data) + '\n')


# Singleton instance
logger_manager = LoggerManager()


def get_logger(name: str, agent_name: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a logger

    Args:
        name: Logger name (usually __name__)
        agent_name: Optional agent name

    Returns:
        Configured logger instance

    Example:
        from src.utils.logger import get_logger

        logger = get_logger(__name__, agent_name='mt5_agent')
        logger.info("Agent started")
        logger.error("Something went wrong", exc_info=True)
    """
    return logger_manager.get_logger(name, agent_name)


def log_trade(
    logger: logging.Logger,
    action: str,
    symbol: str,
    amount: float,
    price: float,
    **kwargs
):
    """
    Convenience function to log trades

    Example:
        from src.utils.logger import get_logger, log_trade

        logger = get_logger(__name__, 'mt5_agent')
        log_trade(
            logger=logger,
            action='BUY',
            symbol='EURUSD',
            amount=0.01,
            price=1.0850,
            sl=1.0800,
            tp=1.0900,
            confidence=85
        )
    """
    logger_manager.log_trade(logger, action, symbol, amount, price, **kwargs)


# Adapter class for backward compatibility with termcolor
class TermcolorAdapter:
    """
    Adapter to replace termcolor.cprint with logger
    Maintains backward compatibility while using proper logging
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def __call__(self, message: str, color: str = 'white', on_color: str = None):
        """
        Replace cprint calls with logger calls

        Maps colors to log levels:
        - red: ERROR
        - yellow: WARNING
        - green, cyan, white: INFO
        """
        # Map colors to log levels
        if color == 'red' or '❌' in message or 'error' in message.lower():
            self.logger.error(message)
        elif color == 'yellow' or '⚠️' in message or 'warning' in message.lower():
            self.logger.warning(message)
        else:
            self.logger.info(message)


if __name__ == "__main__":
    """Test logging system"""
    print("🌙 Testing Moon Dev Logging System\n")

    # Test basic logger
    logger = get_logger(__name__, agent_name='test_agent')

    logger.debug("Debug message - detailed information")
    logger.info("Info message - general information")
    logger.warning("Warning message - something to watch")
    logger.error("Error message - something went wrong")

    # Test trade logging
    log_trade(
        logger=logger,
        action='BUY',
        symbol='EURUSD',
        amount=0.01,
        price=1.0850,
        sl=1.0800,
        tp=1.0900,
        confidence=85,
        reasoning="Strong bullish momentum"
    )

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Caught an exception")

    print(f"\n✅ Logs written to: {logger_manager.log_dir}")
    print("\nLog files created:")
    for log_file in logger_manager.log_dir.glob('*.log'):
        print(f"  - {log_file.name}")
