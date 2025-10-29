"""
🌙 Moon Dev's Error Handling Utilities
Built with love by Moon Dev 🚀

Provides standardized error handling patterns for all agents.
"""

from functools import wraps
import logging
import time
from typing import Any, Callable, Optional, Type, Union, Tuple
from termcolor import cprint


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_on_error(
    max_retries: int = 3,
    delay_seconds: float = 2,
    backoff: float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator to retry a function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry (exponential backoff)
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called before each retry

    Usage:
        @retry_on_error(max_retries=3, delay_seconds=2)
        def fetch_token_data(token_address):
            return api.get_token(token_address)

    Example with custom exceptions:
        @retry_on_error(max_retries=5, exceptions=(ConnectionError, TimeoutError))
        def fetch_with_timeout(url):
            return requests.get(url, timeout=5)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    is_last_attempt = (attempt == max_retries - 1)

                    if is_last_attempt:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    # Calculate wait time with exponential backoff
                    wait_time = delay_seconds * (backoff ** attempt)

                    cprint(
                        f"⚠️ {func.__name__} attempt {attempt + 1}/{max_retries} failed: {e}",
                        "yellow"
                    )
                    cprint(f"🔄 Retrying in {wait_time:.1f} seconds...", "cyan")

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.warning(f"Retry callback failed: {callback_error}")

                    time.sleep(wait_time)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def safe_api_call(
    default_return: Any = None,
    log_errors: bool = True,
    suppress_exceptions: bool = False
):
    """
    Decorator for safe API calls that won't crash the agent on failure.

    Args:
        default_return: Value to return if the function fails
        log_errors: Whether to log errors when they occur
        suppress_exceptions: If True, always return default_return. If False, re-raise after logging

    Usage:
        @safe_api_call(default_return={})
        def get_token_data(token_address):
            return risky_api_call(token_address)

        @safe_api_call(default_return=0.0, suppress_exceptions=True)
        def get_token_price(token_address):
            # Even if this crashes, it returns 0.0 instead of crashing the agent
            return api.get_price(token_address)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                if log_errors:
                    logger.error(f"❌ {func.__name__} failed: {type(e).__name__}: {e}")
                    cprint(f"❌ {func.__name__} failed: {e}", "red")

                if suppress_exceptions:
                    cprint(f"↩️ Returning default value: {default_return}", "yellow")
                    return default_return
                else:
                    # Log but still raise
                    raise

        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log how long a function takes to execute.

    Usage:
        @log_execution_time
        def slow_function():
            time.sleep(5)
            return "done"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        cprint(f"⏱️ Starting {func.__name__}...", "cyan")

        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            cprint(
                f"✅ {func.__name__} completed in {elapsed_time:.2f} seconds",
                "green"
            )
            return result

        except Exception as e:
            elapsed_time = time.time() - start_time
            cprint(
                f"❌ {func.__name__} failed after {elapsed_time:.2f} seconds: {e}",
                "red"
            )
            raise

    return wrapper


def handle_api_errors(
    error_messages: Optional[dict] = None,
    default_message: str = "An API error occurred"
):
    """
    Decorator to handle common API errors with custom messages.

    Args:
        error_messages: Dictionary mapping exception types to error messages
        default_message: Default message for uncaught exception types

    Usage:
        @handle_api_errors({
            ConnectionError: "Failed to connect to API",
            TimeoutError: "API request timed out",
            ValueError: "Invalid API response"
        })
        def fetch_data():
            return api.get_data()
    """
    if error_messages is None:
        error_messages = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                # Check if we have a custom message for this exception type
                error_message = error_messages.get(type(e), default_message)

                # Log the error
                logger.error(f"{func.__name__}: {error_message} - {e}")
                cprint(f"❌ {error_message}: {e}", "red")

                # Re-raise the original exception
                raise

        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry behavior."""

    # Network/API related retries - more aggressive
    NETWORK = {
        'max_retries': 5,
        'delay_seconds': 2,
        'backoff': 2,
        'exceptions': (ConnectionError, TimeoutError)
    }

    # LLM API calls - moderate retries
    LLM_API = {
        'max_retries': 3,
        'delay_seconds': 5,
        'backoff': 1.5,
        'exceptions': (Exception,)
    }

    # Data fetching - quick retries
    DATA_FETCH = {
        'max_retries': 3,
        'delay_seconds': 1,
        'backoff': 2,
        'exceptions': (Exception,)
    }

    # Trading operations - conservative (fewer retries, longer delays)
    TRADING = {
        'max_retries': 2,
        'delay_seconds': 10,
        'backoff': 1,
        'exceptions': (Exception,)
    }


def retry_network_call(func: Callable) -> Callable:
    """Convenience decorator for network calls with pre-configured retry logic."""
    return retry_on_error(**RetryConfig.NETWORK)(func)


def retry_llm_call(func: Callable) -> Callable:
    """Convenience decorator for LLM API calls with pre-configured retry logic."""
    return retry_on_error(**RetryConfig.LLM_API)(func)


def retry_data_fetch(func: Callable) -> Callable:
    """Convenience decorator for data fetching with pre-configured retry logic."""
    return retry_on_error(**RetryConfig.DATA_FETCH)(func)


# Example usage
if __name__ == "__main__":
    # Example 1: Retry with exponential backoff
    @retry_on_error(max_retries=3, delay_seconds=1)
    def flaky_api_call():
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise ConnectionError("API temporarily unavailable")
        return {"status": "success"}

    # Example 2: Safe API call with default return
    @safe_api_call(default_return=0.0)
    def get_price():
        raise ValueError("Price not available")

    # Example 3: Log execution time
    @log_execution_time
    def slow_operation():
        time.sleep(2)
        return "done"

    # Example 4: Combine decorators
    @log_execution_time
    @retry_on_error(max_retries=2)
    @safe_api_call(default_return={})
    def complex_operation():
        return {"data": "important"}

    # Test the examples
    print("\n🧪 Testing error handling utilities...\n")

    try:
        result = flaky_api_call()
        cprint(f"✅ Flaky API call succeeded: {result}", "green")
    except Exception as e:
        cprint(f"❌ Flaky API call failed: {e}", "red")

    price = get_price()
    cprint(f"💰 Price (with default): {price}", "cyan")

    result = slow_operation()
    cprint(f"🐌 Slow operation result: {result}", "cyan")
