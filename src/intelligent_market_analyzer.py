#!/usr/bin/env python3
"""
MARKET MICROSTRUCTURE ANALYZER
==============================

Vervangt de 1000+ loterij strategieën met échte marktanalyse.
Focus op liquiditeit, order flow en inefficiënties die daadwerkelijk voorspelbaar zijn.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import requests
from termcolor import cprint

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nice_funcs import token_overview, token_price, get_ohlcv_data
from agents.api import MoonDevAPI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class MarketInefficiency:
    """Represents a real market inefficiency worth exploiting"""
    type: str  # 'liquidity_gap', 'order_flow', 'funding_arbitrage', 'microstructure'
    token: str
    confidence: float  # 0-100
    expected_return: float  # Annualized %
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH'
    explanation: str
    metadata: dict

class MarketMicrostructureAnalyzer:
    """
    Real market microstructure analysis - no more backtesting lottery
    """

    def __init__(self):
        self.api = MoonDevAPI()
        self.inefficiencies = []
        self.last_analysis = None

    async def analyze_liquidity_gaps(self) -> List[MarketInefficiency]:
        """
        Find liquidity gaps - real edge in order book analysis
        """
        cprint("🔍 Analyzing liquidity gaps...", "cyan")
        gaps = []

        try:
            # Get liquidation data for liquidity gap analysis
            liq_data = self.api.get_liquidation_data()

            if liq_data and len(liq_data) > 0:
                for liq in liq_data[:5]:  # Top 5 most significant
                    if liq.get('liquidation_amount', 0) > 50000:  # $50k+ liquidations

                        # Calculate potential impact
                        price_impact = min(liq['liquidation_amount'] / 1000000 * 0.5, 5.0)  # Max 5% impact

                        gaps.append(MarketInefficiency(
                            type="liquidity_gap",
                            token=liq.get('token', 'UNKNOWN'),
                            confidence=min(liq['liquidation_amount'] / 100000 * 100, 85),
                            expected_return=price_impact * 252,  # Annualized (daily trading)
                            risk_level="MEDIUM",
                            explanation=f"${liq['liquidation_amount']:,.0f} liquidation pressure creates predictable price movement",
                            metadata={
                                'liquidation_amount': liq['liquidation_amount'],
                                'price_impact': price_impact,
                                'side': liq.get('side', 'unknown')
                            }
                        ))

        except Exception as e:
            cprint(f"❌ Error analyzing liquidity gaps: {e}", "red")

        cprint(f"✅ Found {len(gaps)} liquidity gap opportunities", "green")
        return gaps

    async def analyze_funding_arbitrage(self) -> List[MarketInefficiency]:
        """
        Identify funding rate arbitrage opportunities - most consistent strategy
        """
        cprint("💰 Analyzing funding arbitrage...", "cyan")
        arbitrages = []

        try:
            funding_data = self.api.get_funding_data()

            if funding_data and len(funding_data) > 0:
                for funding in funding_data:
                    rate = funding.get('funding_rate', 0)

                    # Look for extreme funding rates (>0.1% or <-0.1%)
                    if abs(rate) > 0.001:
                        # Calculate annualized return
                        annual_return = rate * 3 * 365  # 3x daily funding

                        # Funding arbitrage has historically high success rate
                        confidence = min(abs(rate) * 5000, 90)

                        arbitrages.append(MarketInefficiency(
                            type="funding_arbitrage",
                            token=funding.get('token', 'UNKNOWN'),
                            confidence=confidence,
                            expected_return=annual_return * 100,  # Convert to percentage
                            risk_level="LOW" if abs(rate) < 0.005 else "MEDIUM",
                            explanation=f"Funding rate {rate:.3%} creates {'short' if rate > 0 else 'long'} arbitrage opportunity",
                            metadata={
                                'funding_rate': rate,
                                'next_funding': funding.get('next_funding_time'),
                                'annualized_return': annual_return
                            }
                        ))

        except Exception as e:
            cprint(f"❌ Error analyzing funding arbitrage: {e}", "red")

        cprint(f"✅ Found {len(arbitrages)} funding arbitrage opportunities", "green")
        return arbitrages

    async def analyze_microstructure(self) -> List[MarketInefficiency]:
        """
        Analyze market microstructure patterns - bid-ask spreads, order flow
        """
        cprint("🏗️ Analyzing market microstructure...", "cyan")
        patterns = []

        try:
            # Get top tokens by volume
            monitored_tokens = ['SOL', 'BTC', 'ETH', 'BNB']

            for token in monitored_tokens:
                try:
                    # Get token overview for microstructure data
                    overview = token_overview(token)

                    if overview:
                        volume_24h = overview.get('volume_24h', 0)
                        spread = overview.get('spread_percentage', 0)
                        liquidity = overview.get('liquidity', 0)

                        # Look for inefficient spreads
                        if spread and spread > 0.5:  # >0.5% spread is inefficient
                            patterns.append(MarketInefficiency(
                                type="microstructure",
                                token=token,
                                confidence=min(spread * 20, 75),
                                expected_return=spread * 126,  # Twice daily trading
                                risk_level="LOW",
                                explanation=f"{spread:.2f}% bid-ask spread indicates market maker inefficiency",
                                metadata={
                                    'spread': spread,
                                    'volume_24h': volume_24h,
                                    'liquidity': liquidity
                                }
                            ))

                        # Look for high volume with low liquidity (arbitrage opportunity)
                        if volume_24h > 10000000 and liquidity < 500000:  # $10M+ volume, <$500k liquidity
                            inefficiency_score = (volume_24h / liquidity) * 0.1

                            patterns.append(MarketInefficiency(
                                type="microstructure",
                                token=token,
                                confidence=min(inefficiency_score * 15, 80),
                                expected_return=inefficiency_score * 63,  # Conservative estimate
                                risk_level="MEDIUM",
                                explanation=f"High volume (${volume_24h/1000000:.1f}M) with low liquidity (${liquidity/1000:.0f}k) creates arbitrage",
                                metadata={
                                    'volume_24h': volume_24h,
                                    'liquidity': liquidity,
                                    'inefficiency_score': inefficiency_score
                                }
                            ))

                except Exception as e:
                    cprint(f"⚠️ Error analyzing {token}: {e}", "yellow")
                    continue

        except Exception as e:
            cprint(f"❌ Error in microstructure analysis: {e}", "red")

        cprint(f"✅ Found {len(patterns)} microstructure patterns", "green")
        return patterns

    async def analyze_all_inefficiencies(self) -> List[MarketInefficiency]:
        """
        Run complete analysis - this replaces 1000+ backtesting strategies
        """
        cprint("🚀 Starting comprehensive market microstructure analysis", "magenta", attrs=['bold'])

        self.inefficiencies = []

        # Run all analysis types
        liquidity_gaps = await self.analyze_liquidity_gaps()
        funding_arb = await self.analyze_funding_arbitrage()
        microstructure = await self.analyze_microstructure()

        # Combine all inefficiencies
        self.inefficiencies = liquidity_gaps + funding_arb + microstructure

        # Sort by expected return (highest first)
        self.inefficiencies.sort(key=lambda x: x.expected_return, reverse=True)

        self.last_analysis = datetime.now()

        cprint(f"\n🎯 ANALYSIS COMPLETE: Found {len(self.inefficiencies)} real opportunities", "green", attrs=['bold'])

        return self.inefficiencies

    def print_top_opportunities(self, top_n: int = 10):
        """
        Print the most promising opportunities - this replaces backtesting results
        """
        if not self.inefficiencies:
            cprint("❌ No analysis results available", "red")
            return

        cprint(f"\n🏆 TOP {top_n} MARKET OPPORTUNITIES", "yellow", attrs=['bold'])
        cprint("=" * 80, "yellow")

        for i, ineff in enumerate(self.inefficiencies[:top_n], 1):
            risk_color = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red"}[ineff.risk_level]

            cprint(f"\n{i}. {ineff.token.upper()} - {ineff.type.replace('_', ' ').title()}", "white", attrs=['bold'])
            cprint(f"   💰 Expected Return: {ineff.expected_return:.1f}% annually", "green")
            cprint(f"   🎯 Confidence: {ineff.confidence:.0f}%")
            cprint(f"   ⚠️  Risk Level: ", end="", flush=True)
            cprint(f"{ineff.risk_level}", risk_color)
            cprint(f"   💡 {ineff.explanation}")

            # Show key metadata
            if 'funding_rate' in ineff.metadata:
                cprint(f"   📊 Funding Rate: {ineff.metadata['funding_rate']:.3%}")
            if 'spread' in ineff.metadata:
                cprint(f"   📈 Spread: {ineff.metadata['spread']:.2f}%")
            if 'liquidation_amount' in ineff.metadata:
                cprint(f"   💥 Liquidation: ${ineff.metadata['liquidation_amount']:,.0f}")

    def get_best_opportunities(self, min_confidence: float = 60, max_risk: str = "MEDIUM") -> List[MarketInefficiency]:
        """
        Get filtered opportunities for actual trading
        """
        risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        max_risk_level = risk_levels.get(max_risk, 2)

        filtered = [
            ineff for ineff in self.inefficiencies
            if ineff.confidence >= min_confidence and risk_levels[ineff.risk_level] <= max_risk_level
        ]

        return filtered

async def main():
    """
    Run the intelligent market analysis - this replaces 25+ containers
    """
    cprint("🧠 MARKET MICROSTRUCTURE ANALYZER", "cyan", attrs=['bold'])
    cprint("=" * 50, "cyan")
    cprint("Replacing 1000+ backtesting strategies with real intelligence", "white")

    analyzer = MarketMicrostructureAnalyzer()

    try:
        # Run comprehensive analysis
        opportunities = await analyzer.analyze_all_inefficiencies()

        # Display results
        analyzer.print_top_opportunities()

        # Get actionable opportunities
        actionable = analyzer.get_best_opportunities(min_confidence=60, max_risk="MEDIUM")

        cprint(f"\n✅ ACTIONABLE OPPORTUNITIES: {len(actionable)}", "green", attrs=['bold'])

        if actionable:
            cprint("\n🚀 READY FOR TRADING:", "white", attrs=['bold'])
            for opp in actionable:
                cprint(f"   • {opp.token}: {opp.expected_return:.1f}% annual return ({opp.confidence:.0f}% confidence)")

        return analyzer, opportunities

    except Exception as e:
        cprint(f"❌ Analysis failed: {e}", "red")
        return analyzer, []

if __name__ == "__main__":
    analyzer, opportunities = asyncio.run(main())