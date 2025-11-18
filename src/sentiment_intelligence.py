#!/usr/bin/env python3
"""
SENTIMENT INTELLIGENCE
======================

Real-time market sentiment analysis van Twitter, Reddit, news
Voorspelt marktbewegingen voordat prijs reactie geeft
"""

import asyncio
import json
import logging
import sqlite3
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from textblob import TextBlob
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentimentSource(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    TELEGRAM = "telegram"

class SentimentLabel(Enum):
    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"

@dataclass
class SentimentSignal:
    """Sentiment-based trading signal"""
    signal_id: str
    source: SentimentSource
    content: str
    sentiment_score: float  # -1 to 1
    sentiment_label: SentimentLabel
    confidence: float  # 0-100
    mention_tokens: List[str]
    timestamp: datetime
    influence_score: float  # 0-1 based on reach/engagement
    metadata: Dict[str, Any]

@dataclass
class SentimentAggregate:
    """Aggregated sentiment across sources"""
    aggregate_id: str
    token: str
    overall_sentiment: float  # -1 to 1
    sentiment_label: SentimentLabel
    confidence: float
    source_breakdown: Dict[SentimentSource, float]
    mention_count: int
    influence_weighted: float
    trend_direction: str  # 'improving', 'declining', 'stable'
    timestamp: datetime

class SentimentIntelligence:
    """
    Real-time sentiment analysis engine
    """

    def __init__(self):
        self.sentiment_db = []
        self.aggregated_sentiments = []
        self.influence_weights = {
            SentimentSource.TWITTER: 0.4,
            SentimentSource.REDDIT: 0.3,
            SentimentSource.NEWS: 0.2,
            SentimentSource.TELEGRAM: 0.1
        }

        # API endpoints (in productie: echte API keys)
        self.api_endpoints = {
            'twitter_search': 'https://api.twitter.com/2/tweets/search/recent',
            'reddit_search': 'https://oauth.reddit.com/hot',
            'news_api': 'https://newsapi.org/v2/everything'
        }

        # Crypto-related keywords
        self.crypto_keywords = {
            'BTC': ['bitcoin', 'btc', 'Bitcoin', 'BTC', '#bitcoin', '#btc'],
            'ETH': ['ethereum', 'eth', 'Ethereum', 'ETH', '#ethereum', '#eth'],
            'SOL': ['solana', 'sol', 'Solana', 'SOL', '#solana', '#sol'],
            'general': ['crypto', 'cryptocurrency', 'blockchain', 'altcoin', 'defi', 'nft']
        }

        # Sentiment modifiers
        self.positive_words = ['moon', 'pump', 'bull', 'buy', 'hold', 'hodl', 'diamond', 'rocket', 'lambo', 'gain', 'profit']
        self.negative_words = ['dump', 'bear', 'sell', 'crash', 'rekt', 'loss', 'fud', 'scam', 'bubble', 'correction']

        # Database setup
        self.db_path = "data/sentiment_intelligence.db"
        self.setup_database()

    def print_message(self, message, msg_type="info"):
        """Print zonder Unicode issues"""
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

    def setup_database(self):
        """Setup database voor sentiment data"""
        import os
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_signals (
                signal_id TEXT PRIMARY KEY,
                source TEXT,
                content TEXT,
                sentiment_score REAL,
                sentiment_label TEXT,
                confidence REAL,
                mention_tokens TEXT,
                timestamp TEXT,
                influence_score REAL,
                metadata TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_aggregates (
                aggregate_id TEXT PRIMARY KEY,
                token TEXT,
                overall_sentiment REAL,
                sentiment_label TEXT,
                confidence REAL,
                source_breakdown TEXT,
                mention_count INTEGER,
                influence_weighted REAL,
                trend_direction TEXT,
                timestamp TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def analyze_text_sentiment(self, text: str) -> Tuple[float, SentimentLabel]:
        """
        Analyseer sentiment van tekst met enhanced crypto-specific analysis
        """
        try:
            # Basic TextBlob analysis
            blob = TextBlob(text)
            base_sentiment = blob.sentiment.polarity

            # Crypto-specific sentiment enhancement
            text_lower = text.lower()
            crypto_boost = 0

            # Check for crypto-specific positive words
            for word in self.positive_words:
                if word in text_lower:
                    crypto_boost += 0.1

            # Check for crypto-specific negative words
            for word in self.negative_words:
                if word in text_lower:
                    crypto_boost -= 0.1

            # All caps modifier (excitement)
            if text.isupper():
                crypto_boost += 0.1

            # Emoji modifier (simplified)
            positive_emojis = ['🚀', '📈', '🌙', '💎', '🙌', '💰', '🔥']
            negative_emojis = ['📉', '🐻', '💩', '👎', '😢', '⚰️']

            for emoji in positive_emojis:
                if emoji in text:
                    crypto_boost += 0.15

            for emoji in negative_emojis:
                if emoji in text:
                    crypto_boost -= 0.15

            # Combine sentiment
            final_sentiment = np.clip(base_sentiment + crypto_boost, -1, 1)

            # Determine label
            if final_sentiment > 0.6:
                label = SentimentLabel.VERY_BULLISH
            elif final_sentiment > 0.2:
                label = SentimentLabel.BULLISH
            elif final_sentiment > -0.2:
                label = SentimentLabel.NEUTRAL
            elif final_sentiment > -0.6:
                label = SentimentLabel.BEARISH
            else:
                label = SentimentLabel.VERY_BEARISH

            return final_sentiment, label

        except Exception as e:
            self.print_message(f"Error analyzing text sentiment: {e}", "error")
            return 0.0, SentimentLabel.NEUTRAL

    def extract_mentioned_tokens(self, text: str) -> List[str]:
        """Extract mentioned crypto tokens from text"""
        mentioned_tokens = []
        text_lower = text.lower()

        for token, keywords in self.crypto_keywords.items():
            if token != 'general':  # Skip general keywords
                for keyword in keywords:
                    if keyword in text_lower:
                        mentioned_tokens.append(token)
                        break

        return list(set(mentioned_tokens))  # Remove duplicates

    def calculate_influence_score(self, content: str, source: SentimentSource, metadata: Dict = None) -> float:
        """
        Calculate influence score based on content characteristics
        """
        base_influence = {
            SentimentSource.TWITTER: 0.6,
            SentimentSource.REDDIT: 0.5,
            SentimentSource.NEWS: 0.8,
            SentimentSource.TELEGRAM: 0.4
        }.get(source, 0.5)

        # Content length modifier
        length_modifier = min(len(content) / 280, 1.0)  # Twitter character limit

        # Engagement modifiers (mock data)
        likes = metadata.get('likes', 0) if metadata else 0
        shares = metadata.get('shares', 0) if metadata else 0
        comments = metadata.get('comments', 0) if metadata else 0

        engagement_score = min((likes + shares * 2 + comments * 3) / 1000, 1.0)

        # Verified account modifier
        verified_modifier = 1.2 if metadata and metadata.get('verified', False) else 1.0

        # Follower count modifier
        followers = metadata.get('followers', 0) if metadata else 0
        follower_modifier = min(1 + (followers / 1000000), 2.0)  # Max 2x for 1M+ followers

        final_influence = base_influence * length_modifier * (1 + engagement_score) * verified_modifier * follower_modifier
        return min(final_influence, 1.0)

    def simulate_twitter_sentiment(self, token: str, hours_back: int = 2) -> List[SentimentSignal]:
        """
        Simuleer Twitter sentiment data
        In productie: gebruik echte Twitter API
        """
        mock_tweets = [
            {
                'content': 'Bitcoin is going to the moon! 🚀 BTC #crypto #bullrun',
                'likes': 245,
                'shares': 89,
                'comments': 34,
                'verified': False,
                'followers': 15000
            },
            {
                'content': 'BTC looking strong, might see new highs soon. Hold tight!',
                'likes': 156,
                'shares': 45,
                'comments': 28,
                'verified': False,
                'followers': 8000
            },
            {
                'content': 'Bearish on BTC until we clear 45k resistance. Too much overhead.',
                'likes': 89,
                'shares': 12,
                'comments': 45,
                'verified': False,
                'followers': 5000
            },
            {
                'content': 'Bitcoin dump incoming! Sell now before crash! 📉',
                'likes': 434,
                'shares': 178,
                'comments': 234,
                'verified': False,
                'followers': 25000
            },
            {
                'content': 'Just diamond handed my BTC position. Not selling! 💎🙌',
                'likes': 567,
                'shares': 234,
                'comments': 123,
                'verified': False,
                'followers': 35000
            }
        ]

        signals = []
        current_time = datetime.now()

        for i, tweet in enumerate(mock_tweets):
            # Calculate sentiment
            sentiment_score, sentiment_label = self.analyze_text_sentiment(tweet['content'])
            mentioned_tokens = self.extract_mentioned_tokens(tweet['content'])

            if token.lower() in [t.lower() for t in mentioned_tokens]:
                influence_score = self.calculate_influence_score(
                    tweet['content'],
                    SentimentSource.TWITTER,
                    tweet
                )

                signal = SentimentSignal(
                    signal_id=f"twitter_{uuid.uuid4().hex[:8]}",
                    source=SentimentSource.TWITTER,
                    content=tweet['content'],
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    confidence=min(100, abs(sentiment_score) * 100 + influence_score * 20),
                    mention_tokens=mentioned_tokens,
                    timestamp=current_time - timedelta(minutes=i*15),  # Spread over time
                    influence_score=influence_score,
                    metadata=tweet
                )
                signals.append(signal)

        return signals

    def simulate_reddit_sentiment(self, token: str, hours_back: int = 2) -> List[SentimentSignal]:
        """
        Simuleer Reddit sentiment data
        """
        mock_posts = [
            {
                'content': 'BTC Analysis: Technical indicators pointing to strong support at $42k. Bullish case intact.',
                'upvotes': 1245,
                'comments': 234,
                'subscribers': 500000  # Subreddit subscribers
            },
            {
                'content': 'I think Bitcoin is overvalued at current levels. Expecting a correction soon.',
                'upvotes': 892,
                'comments': 456,
                'subscribers': 500000
            },
            {
                'content': 'LFG! Bitcoin breakout confirmed! We are going to $100k this year! 🚀',
                'upvotes': 2341,
                'comments': 567,
                'subscribers': 500000
            }
        ]

        signals = []
        current_time = datetime.now()

        for i, post in enumerate(mock_posts):
            sentiment_score, sentiment_label = self.analyze_text_sentiment(post['content'])
            mentioned_tokens = self.extract_mentioned_tokens(post['content'])

            if token.lower() in [t.lower() for t in mentioned_tokens]:
                influence_score = self.calculate_influence_score(
                    post['content'],
                    SentimentSource.REDDIT,
                    {
                        'upvotes': post['upvotes'],
                        'comments': post['comments']
                    }
                )

                signal = SentimentSignal(
                    signal_id=f"reddit_{uuid.uuid4().hex[:8]}",
                    source=SentimentSource.REDDIT,
                    content=post['content'],
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    confidence=min(100, abs(sentiment_score) * 100 + influence_score * 15),
                    mention_tokens=mentioned_tokens,
                    timestamp=current_time - timedelta(minutes=i*20),
                    influence_score=influence_score,
                    metadata=post
                )
                signals.append(signal)

        return signals

    def simulate_news_sentiment(self, token: str, hours_back: int = 2) -> List[SentimentSignal]:
        """
        Simuleer news sentiment data
        """
        mock_news = [
            {
                'content': 'Major Financial Institution Announces Bitcoin Investment Fund, Price Surges',
                'publication': 'Bloomberg',
                'domain_authority': 95
            },
            {
                'content': 'Regulators Express Concern Over Cryptocurrency Market Volatility',
                'publication': 'Reuters',
                'domain_authority': 93
            },
            {
                'content': 'Bitcoin Adoption Accelerates in Developing Countries, Experts Say',
                'publication': 'Financial Times',
                'domain_authority': 94
            }
        ]

        signals = []
        current_time = datetime.now()

        for i, article in enumerate(mock_news):
            sentiment_score, sentiment_label = self.analyze_text_sentiment(article['content'])
            mentioned_tokens = self.extract_mentioned_tokens(article['content'])

            if token.lower() in [t.lower() for t in mentioned_tokens]:
                influence_score = self.calculate_influence_score(
                    article['content'],
                    SentimentSource.NEWS,
                    article
                )

                signal = SentimentSignal(
                    signal_id=f"news_{uuid.uuid4().hex[:8]}",
                    source=SentimentSource.NEWS,
                    content=article['content'],
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    confidence=min(100, abs(sentiment_score) * 100 + influence_score * 25),  # News gets higher base confidence
                    mention_tokens=mentioned_tokens,
                    timestamp=current_time - timedelta(hours=i),
                    influence_score=influence_score,
                    metadata=article
                )
                signals.append(signal)

        return signals

    def collect_sentiment_data(self, token: str, hours_back: int = 2) -> List[SentimentSignal]:
        """
        Collect sentiment data van alle bronnen
        """
        self.print_message(f"Collecting sentiment data for {token}...", "info")

        all_signals = []

        # Collect from different sources
        twitter_signals = self.simulate_twitter_sentiment(token, hours_back)
        reddit_signals = self.simulate_reddit_sentiment(token, hours_back)
        news_signals = self.simulate_news_sentiment(token, hours_back)

        all_signals.extend(twitter_signals)
        all_signals.extend(reddit_signals)
        all_signals.extend(news_signals)

        # Store in database
        self.store_sentiment_signals(all_signals)

        self.print_message(f"Collected {len(all_signals)} sentiment signals ({len(twitter_signals)} Twitter, {len(reddit_signals)} Reddit, {len(news_signals)} News)", "success")

        return all_signals

    def store_sentiment_signals(self, signals: List[SentimentSignal]):
        """Store sentiment signals in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for signal in signals:
            cursor.execute('''
                INSERT OR REPLACE INTO sentiment_signals
                (signal_id, source, content, sentiment_score, sentiment_label, confidence,
                 mention_tokens, timestamp, influence_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.signal_id,
                signal.source.value,
                signal.content,
                signal.sentiment_score,
                signal.sentiment_label.value,
                signal.confidence,
                json.dumps(signal.mention_tokens),
                signal.timestamp.isoformat(),
                signal.influence_score,
                json.dumps(signal.metadata)
            ))

        conn.commit()
        conn.close()

    def aggregate_sentiment(self, token: str, time_window_hours: int = 2) -> Optional[SentimentAggregate]:
        """
        Aggregate sentiment signals voor een token
        """
        # Get recent signals
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        recent_signals = [
            signal for signal in self.sentiment_db
            if token in signal.mention_tokens and signal.timestamp >= cutoff_time
        ]

        if len(recent_signals) < 3:  # Need minimum signals
            return None

        # Calculate weighted sentiment
        total_weight = 0
        weighted_sentiment = 0
        source_breakdown = {}

        for signal in recent_signals:
            weight = signal.influence_score * signal.confidence / 100
            weighted_sentiment += signal.sentiment_score * weight
            total_weight += weight

            # Source breakdown
            if signal.source not in source_breakdown:
                source_breakdown[signal.source] = []
            source_breakdown[signal.source].append(signal.sentiment_score)

        if total_weight == 0:
            return None

        overall_sentiment = weighted_sentiment / total_weight

        # Calculate source breakdown averages
        source_avg = {}
        for source, scores in source_breakdown.items():
            source_avg[source] = np.mean(scores)

        # Determine sentiment label
        if overall_sentiment > 0.6:
            label = SentimentLabel.VERY_BULLISH
        elif overall_sentiment > 0.2:
            label = SentimentLabel.BULLISH
        elif overall_sentiment > -0.2:
            label = SentimentLabel.NEUTRAL
        elif overall_sentiment > -0.6:
            label = SentimentLabel.BEARISH
        else:
            label = SentimentLabel.VERY_BEARISH

        # Calculate confidence based on signal count and consensus
        base_confidence = min(100, len(recent_signals) * 10)

        # Consensus calculation
        if len(recent_signals) > 1:
            sentiments = [s.sentiment_score for s in recent_signals]
            consensus = 1 - np.std(sentiments)  # Lower std = higher consensus
            consensus_confidence = consensus * 50
        else:
            consensus_confidence = 50

        final_confidence = (base_confidence + consensus_confidence) / 2

        # Calculate trend direction (compare with older period)
        older_time = datetime.now() - timedelta(hours=time_window_hours * 2)
        older_signals = [
            signal for signal in self.sentiment_db
            if token in signal.mention_tokens and older_time <= signal.timestamp < cutoff_time
        ]

        if len(older_signals) >= 2:
            older_avg = np.mean([s.sentiment_score for s in older_signals])
            if overall_sentiment > older_avg + 0.1:
                trend = "improving"
            elif overall_sentiment < older_avg - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        aggregate = SentimentAggregate(
            aggregate_id=f"agg_{uuid.uuid4().hex[:8]}",
            token=token,
            overall_sentiment=overall_sentiment,
            sentiment_label=label,
            confidence=final_confidence,
            source_breakdown=source_avg,
            mention_count=len(recent_signals),
            influence_weighted=sum(s.influence_score for s in recent_signals) / len(recent_signals),
            trend_direction=trend,
            timestamp=datetime.now()
        )

        # Store in database
        self.store_sentiment_aggregate(aggregate)

        return aggregate

    def store_sentiment_aggregate(self, aggregate: SentimentAggregate):
        """Store sentiment aggregate in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sentiment_aggregates
            (aggregate_id, token, overall_sentiment, sentiment_label, confidence,
             source_breakdown, mention_count, influence_weighted, trend_direction, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            aggregate.aggregate_id,
            aggregate.token,
            aggregate.overall_sentiment,
            aggregate.sentiment_label.value,
            aggregate.confidence,
            json.dumps({k.value: v for k, v in aggregate.source_breakdown.items()}),
            aggregate.mention_count,
            aggregate.influence_weighted,
            aggregate.trend_direction,
            aggregate.timestamp.isoformat()
        ))
        conn.commit()
        conn.close()

    def print_sentiment_dashboard(self, aggregates: List[SentimentAggregate]):
        """Print sentiment intelligence dashboard"""
        if not aggregates:
            print("Geen sentiment data beschikbaar")
            return

        print(f"\nSENTIMENT INTELLIGENCE DASHBOARD")
        print("=" * 60)

        for agg in aggregates:
            print(f"\n{agg.token} Sentiment Analysis")
            print(f"Overall Sentiment: {agg.overall_sentiment:.3f} ({agg.sentiment_label.value.upper()})")
            print(f"Confidence: {agg.confidence:.1f}%")
            print(f"Trend Direction: {agg.trend_direction.upper()}")
            print(f"Total Mentions: {agg.mention_count}")

            print(f"\nSource Breakdown:")
            for source, avg_sentiment in agg.source_breakdown.items():
                source_name = source.value.replace('_', ' ').title()
                print(f"  {source_name}: {avg_sentiment:.3f}")

            # Trading implication
            if agg.overall_sentiment > 0.3:
                implication = "STRONG BUY signal - Bullish sentiment across multiple sources"
            elif agg.overall_sentiment > 0.1:
                implication = "MODERATE BUY signal - Positive sentiment trend"
            elif agg.overall_sentiment > -0.1:
                implication = "HOLD signal - Neutral sentiment"
            elif agg.overall_sentiment > -0.3:
                implication = "MODERATE SELL signal - Negative sentiment developing"
            else:
                implication = "STRONG SELL signal - Bearish sentiment across sources"

            print(f"\nTrading Implication: {implication}")

async def main():
    """Test de Sentiment Intelligence system"""
    print("SENTIMENT INTELLIGENCE")
    print("=" * 40)
    print("Real-time market sentiment analysis")

    sentiment_engine = SentimentIntelligence()

    try:
        # Analyze sentiment voor verschillende tokens
        tokens_to_analyze = ['BTC', 'ETH', 'SOL']
        all_aggregates = []

        for token in tokens_to_analyze:
            print(f"\n[DEMO] Analyzing {token} sentiment...")

            # Collect sentiment data
            signals = sentiment_engine.collect_sentiment_data(token, hours_back=2)
            sentiment_engine.sentiment_db.extend(signals)

            # Aggregate sentiment
            aggregate = sentiment_engine.aggregate_sentiment(token, time_window_hours=2)
            if aggregate:
                all_aggregates.append(aggregate)

        # Print dashboard
        sentiment_engine.print_sentiment_dashboard(all_aggregates)

        # Save sentiment summary
        summary_data = []
        for agg in all_aggregates:
            summary_data.append({
                'timestamp': agg.timestamp.isoformat(),
                'token': agg.token,
                'overall_sentiment': agg.overall_sentiment,
                'sentiment_label': agg.sentiment_label.value,
                'confidence': agg.confidence,
                'trend_direction': agg.trend_direction,
                'mention_count': agg.mention_count
            })

        os.makedirs("data/sentiment", exist_ok=True)
        with open(f"data/sentiment/sentiment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(summary_data, f, indent=2)

        print(f"\n[SUCCESS] Sentiment analysis complete - {len(all_aggregates)} tokens analyzed")

        return sentiment_engine, all_aggregates

    except Exception as e:
        sentiment_engine.print_message(f"Sentiment analysis failed: {e}", "error")
        return sentiment_engine, []

if __name__ == "__main__":
    import os
    engine, aggregates = asyncio.run(main())