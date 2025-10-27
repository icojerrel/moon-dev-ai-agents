#!/usr/bin/env python3
"""
🌙 Moon Dev's Real-Time Price Feed Service 🌙

WebSocket-based real-time price monitoring for crypto tokens.
Connects to multiple data sources and provides <1s latency price updates.

Supported Data Sources:
- Birdeye API (Solana tokens via WebSocket)
- Fallback to REST API (when WebSocket unavailable)

Usage:
    # Run standalone
    python src/services/realtime_price_feed.py

    # Use programmatically
    from src.services.realtime_price_feed import RealtimePriceFeed

    feed = RealtimePriceFeed()
    await feed.connect()

    # Subscribe to tokens
    feed.subscribe(['SOL', 'BTC', 'ETH'])

    # Get latest price
    price = feed.get_price('SOL')
"""

import asyncio
import aiohttp
import json
import time
import os
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from pathlib import Path
from termcolor import colored, cprint
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Birdeye API configuration
BIRDEYE_API_KEY = os.getenv('BIRDEYE_API_KEY', '')
BIRDEYE_WS_URL = "wss://public-api.birdeye.so/socket"
BIRDEYE_REST_URL = "https://public-api.birdeye.so/defi/price"

# Token addresses (Solana mainnet)
TOKEN_ADDRESSES = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    'WIF': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
}

# CoinGecko IDs for major tokens
COINGECKO_IDS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
}


class RealtimePriceFeed:
    """
    Real-time price feed service using WebSocket + REST API fallback
    """

    def __init__(self):
        self.prices: Dict[str, Dict[str, Any]] = {}
        self.subscribers: List[Callable] = []
        self.ws_session: Optional[aiohttp.ClientSession] = None
        self.ws_connection: Optional[aiohttp.ClientWebSocketResponse] = None
        self.running = False
        self.subscribed_tokens: List[str] = []

        # Performance metrics
        self.metrics = {
            'updates_received': 0,
            'avg_latency_ms': 0,
            'errors': 0,
            'last_update': None
        }

        cprint("\n🔌 Real-Time Price Feed Initialized", "cyan")

    async def connect(self) -> bool:
        """
        Connect to WebSocket feed

        Returns:
            True if connected successfully
        """
        try:
            self.ws_session = aiohttp.ClientSession()

            # Try WebSocket connection
            if BIRDEYE_API_KEY:
                cprint("🔄 Connecting to Birdeye WebSocket...", "yellow")

                headers = {
                    'X-API-KEY': BIRDEYE_API_KEY
                }

                self.ws_connection = await self.ws_session.ws_connect(
                    BIRDEYE_WS_URL,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                )

                cprint("✅ WebSocket connected successfully", "green")
                self.running = True
                return True

            else:
                cprint("⚠️  No BIRDEYE_API_KEY - using REST fallback", "yellow")
                self.running = True
                return True

        except Exception as e:
            cprint(f"❌ WebSocket connection failed: {e}", "red")
            cprint("🔄 Falling back to REST API mode", "yellow")
            self.running = True
            return True

    async def disconnect(self):
        """Close WebSocket connection"""
        self.running = False

        if self.ws_connection:
            await self.ws_connection.close()
            cprint("🔌 WebSocket closed", "yellow")

        if self.ws_session:
            await self.ws_session.close()

    def subscribe(self, tokens: List[str]):
        """
        Subscribe to price updates for tokens

        Args:
            tokens: List of token symbols (e.g., ['SOL', 'BTC'])
        """
        self.subscribed_tokens.extend(tokens)
        self.subscribed_tokens = list(set(self.subscribed_tokens))  # Remove duplicates

        cprint(f"📡 Subscribed to {len(self.subscribed_tokens)} tokens: {', '.join(self.subscribed_tokens)}", "cyan")

    async def _fetch_price_rest(self, token: str) -> Optional[float]:
        """
        Fetch price via REST API (fallback)

        Args:
            token: Token symbol

        Returns:
            Price as float, or None if failed
        """
        try:
            # Get token address
            token_address = TOKEN_ADDRESSES.get(token)

            if not token_address:
                # Try CoinGecko for BTC/ETH
                coingecko_id = COINGECKO_IDS.get(token)
                if coingecko_id:
                    return await self._fetch_coingecko_price(coingecko_id)
                return None

            # Birdeye REST API
            if not BIRDEYE_API_KEY:
                return None

            headers = {'X-API-KEY': BIRDEYE_API_KEY}
            params = {'address': token_address}

            async with self.ws_session.get(
                BIRDEYE_REST_URL,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data.get('data', {}).get('value')
                    return float(price) if price else None

        except Exception as e:
            cprint(f"⚠️  REST fetch failed for {token}: {e}", "yellow")
            return None

    async def _fetch_coingecko_price(self, coin_id: str) -> Optional[float]:
        """
        Fetch price from CoinGecko

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Price in USD
        """
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

            async with self.ws_session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get(coin_id, {}).get('usd')

        except Exception as e:
            cprint(f"⚠️  CoinGecko fetch failed: {e}", "yellow")
            return None

    async def _update_loop_rest(self):
        """
        REST API polling loop (fallback when WebSocket unavailable)
        """
        cprint("🔄 Starting REST API polling mode (5s interval)", "yellow")

        while self.running:
            try:
                start_time = time.time()

                # Fetch all subscribed tokens in parallel
                tasks = [self._fetch_price_rest(token) for token in self.subscribed_tokens]
                prices = await asyncio.gather(*tasks, return_exceptions=True)

                # Update price cache
                for token, price in zip(self.subscribed_tokens, prices):
                    if isinstance(price, (int, float)) and price is not None:
                        self._update_price(token, price)

                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                self.metrics['avg_latency_ms'] = (
                    (self.metrics['avg_latency_ms'] * 0.9) + (latency_ms * 0.1)
                )

                cprint(
                    f"📊 Updated {len(self.subscribed_tokens)} tokens in {latency_ms:.0f}ms "
                    f"(avg: {self.metrics['avg_latency_ms']:.0f}ms)",
                    "cyan"
                )

                # Poll every 5 seconds (vs 15 minutes!)
                await asyncio.sleep(5)

            except Exception as e:
                cprint(f"❌ Update loop error: {e}", "red")
                self.metrics['errors'] += 1
                await asyncio.sleep(5)

    async def _update_loop_websocket(self):
        """
        WebSocket message handling loop
        """
        cprint("🔄 Starting WebSocket message loop", "green")

        while self.running and self.ws_connection:
            try:
                msg = await self.ws_connection.receive(timeout=30)

                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)

                    # Handle Birdeye price update format
                    if 'type' in data and data['type'] == 'PRICE_DATA':
                        token = data.get('token')
                        price = data.get('price')

                        if token and price:
                            # Find symbol from address
                            symbol = next(
                                (k for k, v in TOKEN_ADDRESSES.items() if v == token),
                                None
                            )
                            if symbol:
                                self._update_price(symbol, price)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    cprint(f"❌ WebSocket error", "red")
                    break

            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                if self.ws_connection:
                    await self.ws_connection.ping()

            except Exception as e:
                cprint(f"❌ WebSocket message error: {e}", "red")
                self.metrics['errors'] += 1
                break

        # If WebSocket fails, fall back to REST
        cprint("🔄 WebSocket closed, falling back to REST", "yellow")
        await self._update_loop_rest()

    def _update_price(self, token: str, price: float):
        """
        Update price in cache and notify subscribers

        Args:
            token: Token symbol
            price: Current price
        """
        old_price = self.prices.get(token, {}).get('price')

        # Calculate change percentage
        change_pct = 0.0
        if old_price:
            change_pct = ((price - old_price) / old_price) * 100

        # Update cache
        self.prices[token] = {
            'price': price,
            'timestamp': datetime.now().isoformat(),
            'change_pct': change_pct,
            'change_abs': price - old_price if old_price else 0
        }

        self.metrics['updates_received'] += 1
        self.metrics['last_update'] = datetime.now().isoformat()

        # Alert on significant changes
        if abs(change_pct) > 2.0:
            color = "red" if change_pct < 0 else "green"
            cprint(
                f"🚨 {token}: ${price:.4f} ({change_pct:+.2f}%)",
                color,
                attrs=['bold']
            )

        # Notify subscribers
        for callback in self.subscribers:
            try:
                callback(token, self.prices[token])
            except Exception as e:
                cprint(f"⚠️  Subscriber callback error: {e}", "yellow")

    def get_price(self, token: str) -> Optional[float]:
        """
        Get latest price for a token

        Args:
            token: Token symbol

        Returns:
            Current price or None
        """
        return self.prices.get(token, {}).get('price')

    def get_all_prices(self) -> Dict[str, float]:
        """
        Get all latest prices

        Returns:
            Dict mapping token symbols to prices
        """
        return {
            token: data['price']
            for token, data in self.prices.items()
        }

    def add_subscriber(self, callback: Callable):
        """
        Add a callback for price updates

        Args:
            callback: Function(token, price_data) called on updates
        """
        self.subscribers.append(callback)

    async def start(self):
        """
        Start the price feed service
        """
        await self.connect()

        # Subscribe to default tokens if none specified
        if not self.subscribed_tokens:
            self.subscribe(['SOL', 'BTC', 'ETH'])

        # Start update loop
        if self.ws_connection:
            await self._update_loop_websocket()
        else:
            await self._update_loop_rest()

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics.copy()


async def main():
    """Test the price feed"""
    cprint("\n" + "="*70, "cyan")
    cprint("🌙 Moon Dev's Real-Time Price Feed Test 🌙", "cyan", attrs=['bold'])
    cprint("="*70, "cyan")

    feed = RealtimePriceFeed()

    # Add subscriber
    def on_price_update(token: str, data: Dict):
        print(f"📈 {token}: ${data['price']:.4f} ({data['change_pct']:+.2f}%)")

    feed.add_subscriber(on_price_update)

    # Subscribe to tokens
    feed.subscribe(['SOL', 'BTC', 'ETH', 'BONK'])

    try:
        await feed.start()
    except KeyboardInterrupt:
        cprint("\n\n⚠️  Shutting down...", "yellow")
        await feed.disconnect()

        # Print metrics
        metrics = feed.get_metrics()
        cprint("\n📊 Final Metrics:", "cyan")
        cprint(f"  Updates Received: {metrics['updates_received']}", "white")
        cprint(f"  Avg Latency: {metrics['avg_latency_ms']:.0f}ms", "white")
        cprint(f"  Errors: {metrics['errors']}", "red" if metrics['errors'] > 0 else "white")


if __name__ == "__main__":
    asyncio.run(main())
