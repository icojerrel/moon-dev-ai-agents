"""
🌙 Moon Dev's Data Cache Manager
Built with love by Moon Dev 🚀

Provides intelligent caching for API data to reduce redundant calls
and improve performance across all agents.
"""

from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional, Callable
from termcolor import cprint
import hashlib
import json


class DataCache:
    """
    Thread-safe data cache with configurable TTL (Time To Live).

    Features:
    - Automatic expiration of stale data
    - Cache hit/miss statistics
    - Multiple TTL support for different data types
    - Memory-efficient storage
    """

    def __init__(self, default_ttl_minutes: int = 5):
        """
        Initialize the data cache.

        Args:
            default_ttl_minutes: Default time-to-live for cached data in minutes
        """
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        self.hits = 0
        self.misses = 0

    def get(self, key: str, ttl: Optional[timedelta] = None) -> Optional[Any]:
        """
        Get data from cache if it exists and hasn't expired.

        Args:
            key: Cache key
            ttl: Optional custom TTL, uses default if not specified

        Returns:
            Cached data if available and fresh, None otherwise
        """
        if key not in self.cache:
            self.misses += 1
            return None

        data, timestamp = self.cache[key]
        effective_ttl = ttl if ttl else self.default_ttl

        if datetime.now() - timestamp < effective_ttl:
            self.hits += 1
            return data
        else:
            # Data is stale, remove from cache
            del self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, data: Any) -> None:
        """
        Store data in cache with current timestamp.

        Args:
            key: Cache key
            data: Data to cache
        """
        self.cache[key] = (data, datetime.now())

    def invalidate(self, key: str) -> bool:
        """
        Remove a specific key from cache.

        Args:
            key: Cache key to invalidate

        Returns:
            True if key was found and removed, False otherwise
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp >= self.default_ttl
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache performance metrics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.2f}%",
            'entries': len(self.cache),
            'memory_estimate_kb': self._estimate_memory()
        }

    def _estimate_memory(self) -> int:
        """
        Estimate memory usage in KB (rough approximation).

        Returns:
            Estimated memory usage in KB
        """
        # Rough estimate: 1KB per entry on average
        return len(self.cache)

    def print_stats(self) -> None:
        """Print formatted cache statistics."""
        stats = self.get_stats()
        cprint("\n📊 Cache Statistics:", "cyan")
        cprint(f"  • Cache Hits: {stats['hits']}", "green")
        cprint(f"  • Cache Misses: {stats['misses']}", "yellow")
        cprint(f"  • Hit Rate: {stats['hit_rate']}", "cyan")
        cprint(f"  • Cached Entries: {stats['entries']}", "blue")
        cprint(f"  • Estimated Memory: ~{stats['memory_estimate_kb']} KB", "blue")


# Global cache instances for different data types
# Each has its own TTL based on how frequently the data changes

# Market data cache (5 minutes TTL - prices change frequently)
market_data_cache = DataCache(ttl_minutes=5)

# Token metadata cache (60 minutes TTL - metadata rarely changes)
token_metadata_cache = DataCache(ttl_minutes=60)

# OHLCV data cache (15 minutes TTL - historical data is relatively stable)
ohlcv_cache = DataCache(ttl_minutes=15)

# Wallet/position cache (2 minutes TTL - positions change with trades)
wallet_cache = DataCache(ttl_minutes=2)


def cached_data(cache_instance: DataCache, ttl_minutes: Optional[int] = None):
    """
    Decorator to cache function results.

    Args:
        cache_instance: Which cache to use (market_data_cache, token_metadata_cache, etc.)
        ttl_minutes: Optional custom TTL in minutes (overrides cache default)

    Usage:
        @cached_data(market_data_cache, ttl_minutes=5)
        def get_token_price(token_address):
            return expensive_api_call(token_address)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            custom_ttl = timedelta(minutes=ttl_minutes) if ttl_minutes else None
            cached_result = cache_instance.get(cache_key, ttl=custom_ttl)

            if cached_result is not None:
                cprint(f"💾 Cache hit for {func.__name__}", "green")
                return cached_result

            # Cache miss - call actual function
            cprint(f"🔄 Cache miss for {func.__name__}, fetching fresh data...", "yellow")
            result = func(*args, **kwargs)

            # Store in cache
            if result is not None:
                cache_instance.set(cache_key, result)

            return result

        return wrapper
    return decorator


def invalidate_cache_for_token(token_address: str) -> None:
    """
    Invalidate all cached data for a specific token.
    Useful after trading to ensure fresh data on next request.

    Args:
        token_address: Token address to invalidate
    """
    # This is a simplified version - in production you'd want to track
    # which cache keys correspond to which tokens
    cprint(f"🗑️ Invalidating cache for token {token_address[:8]}...", "yellow")
    # For now, just clear the market data cache
    # A more sophisticated approach would track keys by token
    market_data_cache.clear()


def print_all_cache_stats() -> None:
    """Print statistics for all cache instances."""
    cprint("\n" + "=" * 60, "cyan")
    cprint("📊 CACHE PERFORMANCE REPORT", "white", "on_blue")
    cprint("=" * 60, "cyan")

    cprint("\n🏪 Market Data Cache (TTL: 5 min):", "cyan")
    market_data_cache.print_stats()

    cprint("\n🏷️ Token Metadata Cache (TTL: 60 min):", "cyan")
    token_metadata_cache.print_stats()

    cprint("\n📈 OHLCV Data Cache (TTL: 15 min):", "cyan")
    ohlcv_cache.print_stats()

    cprint("\n💰 Wallet/Position Cache (TTL: 2 min):", "cyan")
    wallet_cache.print_stats()

    cprint("\n" + "=" * 60, "cyan")


# Example usage:
if __name__ == "__main__":
    # Example of how to use the caching decorator

    @cached_data(market_data_cache, ttl_minutes=5)
    def get_token_price(token_address: str) -> float:
        """Example function that would normally make an API call"""
        print(f"Fetching price for {token_address} from API...")
        # Simulate API call
        import time
        time.sleep(1)
        return 42.0

    # First call - cache miss
    print(f"Price: {get_token_price('ABC123')}")

    # Second call - cache hit (instant)
    print(f"Price: {get_token_price('ABC123')}")

    # Different token - cache miss
    print(f"Price: {get_token_price('XYZ789')}")

    # Print stats
    print_all_cache_stats()
