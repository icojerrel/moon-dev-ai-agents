"""
🌙 Moon Dev's DeepSeek Trading Director Agent
==============================================
Autonomous AI Trading Director using DeepSeek-R1 reasoning

This agent serves as the "brain" of the autonomous trading system:
- Analyzes market conditions with deep reasoning
- Selects optimal strategies from 23-strategy library
- Approves/rejects all trades with explainable reasoning
- Coordinates other agents (risk, sentiment, whale, etc.)
- Manages portfolio allocation dynamically
- Provides autonomous decision-making with human oversight

DeepSeek-R1's reasoning capabilities make it ideal for:
- Complex market regime detection
- Multi-factor strategy selection
- Risk-aware trade approval
- Adaptive portfolio management
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from termcolor import cprint
from typing import Dict, List, Optional, Tuple
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.models.model_factory import model_factory
from src.config import *
from src.nice_funcs import (
    get_account_balance,
    get_all_open_positions,
    token_price,
    token_overview
)


class DeepSeekTradingDirector:
    """
    DeepSeek Trading Director - Autonomous AI Trading System Leader

    Responsibilities:
    1. Market Regime Detection - Analyze market conditions (trending/ranging/volatile)
    2. Strategy Selection - Choose from 23 strategy templates based on regime
    3. Portfolio Allocation - Distribute capital across selected strategies
    4. Trade Approval - Approve/reject all trades with reasoning
    5. Agent Coordination - Orchestrate risk, sentiment, whale, strategy agents
    6. Risk Oversight - Monitor portfolio risk and adjust dynamically
    7. Performance Monitoring - Track strategy performance and adapt

    Architecture:
        DeepSeek Director (this agent) → Coordinates → [Risk, Strategy, Trading, Sentiment, Whale agents]
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize DeepSeek Trading Director

        Args:
            config: Optional configuration dict with:
                - max_strategies: Maximum concurrent strategies (default: 3)
                - rebalance_threshold: Trigger rebalance at this deviation (default: 0.10)
                - risk_tolerance: 'low', 'medium', 'high' (default: 'medium')
                - reasoning_temperature: DeepSeek temperature (default: 0.3)
                - enable_trade_approval: Require approval for all trades (default: True)
        """
        # Load configuration
        self.config = config or {}
        self.max_strategies = self.config.get('max_strategies', 3)
        self.rebalance_threshold = self.config.get('rebalance_threshold', 0.10)
        self.risk_tolerance = self.config.get('risk_tolerance', 'medium')
        self.reasoning_temperature = self.config.get('reasoning_temperature', 0.3)
        self.enable_trade_approval = self.config.get('enable_trade_approval', True)

        # Initialize AI model via OpenRouter (unified API for all LLMs)
        cprint("🧠 Initializing AI Trading Director via OpenRouter...", "cyan", attrs=['bold'])

        # Try OpenRouter first (RECOMMENDED), fallback to direct DeepSeek if needed
        self.model = model_factory.get_model('openrouter', model_name='deepseek/deepseek-chat')

        if not self.model:
            cprint("⚠️ OpenRouter not available, trying direct DeepSeek API...", "yellow")
            self.model = model_factory.get_model('deepseek', model_name='deepseek-chat')

        if not self.model:
            raise Exception("❌ No AI model available! Add OPENROUTER_API_KEY or DEEPSEEK_KEY to .env")

        cprint(f"✅ AI model loaded: {self.model.model_name}", "green")

        # Director state
        self.current_regime = None
        self.selected_strategies = []
        self.portfolio_allocation = {}
        self.approved_tokens = []
        self.last_regime_update = None
        self.decision_history = []

        # Strategy library (from TASK-012)
        self.strategy_library = {
            # Momentum strategies
            'momentum_base': {'type': 'momentum', 'risk': 'medium', 'best_for': 'trending'},
            'momentum_aggressive': {'type': 'momentum', 'risk': 'high', 'best_for': 'strong_trend'},
            'momentum_conservative': {'type': 'momentum', 'risk': 'low', 'best_for': 'weak_trend'},
            'momentum_scalping': {'type': 'momentum', 'risk': 'very_high', 'best_for': 'strong_trend'},

            # Mean reversion strategies
            'mean_reversion_base': {'type': 'mean_reversion', 'risk': 'medium', 'best_for': 'ranging'},
            'mean_reversion_tight': {'type': 'mean_reversion', 'risk': 'high', 'best_for': 'tight_range'},
            'mean_reversion_wide': {'type': 'mean_reversion', 'risk': 'low', 'best_for': 'wide_range'},
            'mean_reversion_divergence': {'type': 'mean_reversion', 'risk': 'medium', 'best_for': 'ranging'},

            # Breakout strategies
            'breakout_base': {'type': 'breakout', 'risk': 'medium', 'best_for': 'consolidation'},
            'breakout_aggressive': {'type': 'breakout', 'risk': 'high', 'best_for': 'tight_consolidation'},
            'breakout_conservative': {'type': 'breakout', 'risk': 'low', 'best_for': 'wide_consolidation'},
            'breakout_range_expansion': {'type': 'breakout', 'risk': 'medium', 'best_for': 'compression'},

            # Grid strategies
            'grid_base': {'type': 'grid', 'risk': 'medium', 'best_for': 'ranging'},
            'grid_tight': {'type': 'grid', 'risk': 'high', 'best_for': 'tight_range'},
            'grid_wide': {'type': 'grid', 'risk': 'low', 'best_for': 'wide_range'},
            'grid_range_detection': {'type': 'grid', 'risk': 'medium', 'best_for': 'confirmed_range'},
        }

        cprint(f"📊 Strategy library loaded: {len(self.strategy_library)} strategies available", "green")

    def analyze_market_regime(self, market_data: Dict) -> Dict:
        """
        Analyze market conditions to detect regime using DeepSeek reasoning

        Args:
            market_data: Dict with market indicators:
                - tokens: List of token data (price, volume, change_24h)
                - sentiment: Market sentiment score
                - whale_activity: Recent whale transactions
                - positions: Current open positions
                - balance: Account balance

        Returns:
            Dict with:
                - regime: 'trending_bullish', 'trending_bearish', 'ranging', 'volatile', 'uncertain'
                - confidence: 0-100 confidence score
                - reasoning: DeepSeek's reasoning process
                - indicators: Key indicators that led to decision
        """
        cprint("\n🔍 Analyzing market regime with DeepSeek reasoning...", "cyan", attrs=['bold'])

        # Prepare analysis prompt for DeepSeek
        system_prompt = """You are an expert cryptocurrency market analyst. Analyze the provided market data and determine the current market regime.

Your analysis should consider:
1. Price trends across major tokens (BTC, ETH, SOL)
2. Trading volume patterns
3. Market sentiment indicators
4. Whale activity
5. Volatility levels
6. Correlation between assets

Market Regimes:
- trending_bullish: Strong upward trend, high volume, positive sentiment
- trending_bearish: Strong downward trend, high volume, negative sentiment
- ranging: Sideways movement, price oscillating in range
- volatile: High volatility, rapid price swings, unpredictable
- uncertain: Mixed signals, unclear direction

Provide your analysis in JSON format with:
{
    "regime": "regime_name",
    "confidence": 0-100,
    "reasoning": "detailed explanation",
    "key_indicators": ["indicator1", "indicator2", ...],
    "recommended_risk_level": "low/medium/high"
}"""

        user_prompt = f"""Analyze this market data:

**Token Data:**
{json.dumps(market_data.get('tokens', []), indent=2)}

**Market Sentiment:**
{market_data.get('sentiment', 'N/A')}

**Whale Activity:**
{market_data.get('whale_activity', 'N/A')}

**Current Positions:**
{json.dumps(market_data.get('positions', []), indent=2)}

**Account Balance:** ${market_data.get('balance', 0):,.2f}

Provide your market regime analysis."""

        # Get DeepSeek analysis
        try:
            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_content=user_prompt,
                temperature=self.reasoning_temperature,
                max_tokens=2000
            )

            # Parse JSON response
            analysis = json.loads(response)

            # Store regime
            self.current_regime = analysis['regime']
            self.last_regime_update = datetime.now()

            # Display results
            cprint(f"\n📊 Market Regime: {analysis['regime'].upper()}", "yellow", attrs=['bold'])
            cprint(f"🎯 Confidence: {analysis['confidence']}%", "cyan")
            cprint(f"💡 Reasoning: {analysis['reasoning']}", "white")
            cprint(f"📈 Key Indicators: {', '.join(analysis['key_indicators'])}", "green")

            return analysis

        except Exception as e:
            cprint(f"❌ Error analyzing market regime: {str(e)}", "red")
            # Fallback to uncertain regime
            return {
                'regime': 'uncertain',
                'confidence': 0,
                'reasoning': f'Error in analysis: {str(e)}',
                'key_indicators': [],
                'recommended_risk_level': 'low'
            }

    def select_strategies(self, regime: str, risk_tolerance: str) -> List[Dict]:
        """
        Select optimal strategies based on market regime using DeepSeek

        Args:
            regime: Current market regime
            risk_tolerance: 'low', 'medium', 'high'

        Returns:
            List of selected strategies with allocations:
            [
                {'name': 'momentum_base', 'allocation': 0.40, 'reasoning': '...'},
                {'name': 'breakout_base', 'allocation': 0.30, 'reasoning': '...'},
                {'name': 'cash', 'allocation': 0.30, 'reasoning': '...'}
            ]
        """
        cprint("\n🎯 Selecting optimal strategies with DeepSeek...", "cyan", attrs=['bold'])

        system_prompt = f"""You are an expert trading strategy selector. Based on the market regime and risk tolerance, select the optimal strategies from the available library.

**Market Regime:** {regime}
**Risk Tolerance:** {risk_tolerance}

**Available Strategies:**
{json.dumps(self.strategy_library, indent=2)}

**Rules:**
1. Select maximum {self.max_strategies} active strategies
2. Total allocation must sum to 1.0 (100%)
3. Include cash allocation for risk management (min 10%, max 50%)
4. Match strategies to regime ('best_for' field)
5. Respect risk tolerance (avoid 'very_high' risk if tolerance is 'low')
6. Diversify across strategy types when possible

Provide response in JSON format:
{{
    "strategies": [
        {{"name": "strategy_name", "allocation": 0.40, "reasoning": "why this strategy"}},
        {{"name": "cash", "allocation": 0.30, "reasoning": "why this cash allocation"}}
    ],
    "overall_reasoning": "overall portfolio logic"
}}"""

        try:
            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_content=f"Select optimal strategies for {regime} market with {risk_tolerance} risk tolerance.",
                temperature=self.reasoning_temperature,
                max_tokens=2000
            )

            selection = json.loads(response)
            self.selected_strategies = selection['strategies']
            self.portfolio_allocation = {s['name']: s['allocation'] for s in selection['strategies']}

            # Display selection
            cprint(f"\n✅ Strategy Selection Complete", "green", attrs=['bold'])
            cprint(f"📊 {len(self.selected_strategies)} strategies selected", "cyan")
            for strategy in self.selected_strategies:
                cprint(f"  • {strategy['name']}: {strategy['allocation']*100:.0f}% - {strategy['reasoning']}", "white")

            return self.selected_strategies

        except Exception as e:
            cprint(f"❌ Error selecting strategies: {str(e)}", "red")
            # Fallback to conservative allocation
            return [
                {'name': 'cash', 'allocation': 1.0, 'reasoning': 'Error in selection, staying in cash'}
            ]

    def approve_trade(self, trade_proposal: Dict) -> Tuple[bool, str]:
        """
        Approve or reject trade proposal using DeepSeek reasoning

        Args:
            trade_proposal: Dict with:
                - action: 'BUY' or 'SELL'
                - token: Token address or symbol
                - amount: USD amount
                - strategy: Strategy proposing the trade
                - reasoning: Strategy's reasoning

        Returns:
            Tuple of (approved: bool, reasoning: str)
        """
        if not self.enable_trade_approval:
            return True, "Trade approval disabled"

        cprint(f"\n🔐 Reviewing trade proposal with DeepSeek...", "yellow")

        system_prompt = f"""You are a risk-aware trade approval system. Review the trade proposal and decide whether to approve or reject it.

**Current Market Regime:** {self.current_regime}
**Portfolio Allocation:** {json.dumps(self.portfolio_allocation, indent=2)}
**Risk Tolerance:** {self.risk_tolerance}

**Approval Criteria:**
1. Trade aligns with current market regime
2. Trade fits within strategy allocation
3. Risk is acceptable given regime and tolerance
4. Position sizing is appropriate
5. No obvious red flags (pump/dump, manipulation, etc.)

Provide response in JSON format:
{{
    "approved": true/false,
    "reasoning": "detailed explanation of decision",
    "concerns": ["concern1", "concern2"] or [],
    "suggested_adjustments": "suggestions if rejected"
}}"""

        user_prompt = f"""Review this trade proposal:

**Action:** {trade_proposal['action']}
**Token:** {trade_proposal['token']}
**Amount:** ${trade_proposal['amount']:,.2f}
**Strategy:** {trade_proposal.get('strategy', 'unknown')}
**Strategy Reasoning:** {trade_proposal.get('reasoning', 'N/A')}

Should this trade be approved?"""

        try:
            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_content=user_prompt,
                temperature=self.reasoning_temperature,
                max_tokens=1000
            )

            decision = json.loads(response)
            approved = decision['approved']
            reasoning = decision['reasoning']

            # Log decision
            self.decision_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'trade_approval',
                'proposal': trade_proposal,
                'decision': decision
            })

            # Display decision
            if approved:
                cprint(f"✅ Trade APPROVED", "green", attrs=['bold'])
            else:
                cprint(f"❌ Trade REJECTED", "red", attrs=['bold'])

            cprint(f"💡 Reasoning: {reasoning}", "white")

            if decision.get('concerns'):
                cprint(f"⚠️  Concerns: {', '.join(decision['concerns'])}", "yellow")

            return approved, reasoning

        except Exception as e:
            cprint(f"❌ Error in trade approval: {str(e)}", "red")
            # Fail safe: reject on error
            return False, f"Trade rejected due to approval error: {str(e)}"

    def coordinate_agents(self, regime: str) -> Dict:
        """
        Determine which agents should run based on market regime

        Args:
            regime: Current market regime

        Returns:
            Dict with agent priorities:
            {
                'risk': True,  # Always run
                'sentiment': True,
                'whale': False,  # Skip in this regime
                'strategy': True,
                'trading': True
            }
        """
        cprint("\n🎛️  Coordinating agent execution...", "cyan")

        # Base configuration: risk agent always runs
        agent_config = {
            'risk': True,  # Always monitor risk
            'sentiment': False,
            'whale': False,
            'strategy': False,
            'trading': False,
            'copybot': False
        }

        # Regime-specific agent coordination
        if regime in ['trending_bullish', 'trending_bearish']:
            agent_config['sentiment'] = True  # Sentiment matters in trends
            agent_config['whale'] = True  # Watch whale activity
            agent_config['strategy'] = True  # Execute strategies
            agent_config['trading'] = True  # Allow trading

        elif regime == 'ranging':
            agent_config['strategy'] = True  # Mean reversion/grid strategies
            agent_config['trading'] = True  # Allow trading
            agent_config['sentiment'] = False  # Less relevant in range

        elif regime == 'volatile':
            agent_config['sentiment'] = True  # Monitor sentiment shifts
            agent_config['whale'] = True  # Watch for manipulation
            agent_config['strategy'] = False  # Reduce trading in volatility
            agent_config['trading'] = False  # Pause trading

        elif regime == 'uncertain':
            agent_config['sentiment'] = True  # Gather information
            agent_config['whale'] = True  # Monitor activity
            agent_config['strategy'] = False  # Don't trade yet
            agent_config['trading'] = False  # Stay in cash

        cprint(f"✅ Agent configuration for {regime}:", "green")
        for agent, enabled in agent_config.items():
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            cprint(f"  • {agent.title()}: {status}", "white")

        return agent_config

    def run_director_cycle(self) -> Dict:
        """
        Execute one complete director cycle

        Steps:
        1. Gather market data
        2. Analyze market regime
        3. Select optimal strategies
        4. Coordinate agent execution
        5. Monitor and log decisions

        Returns:
            Dict with cycle results
        """
        cprint("\n" + "="*80, "cyan")
        cprint("🧠 DEEPSEEK TRADING DIRECTOR - CYCLE START", "cyan", attrs=['bold'])
        cprint("="*80, "cyan")
        cprint(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "white")

        try:
            # Step 1: Gather market data
            cprint("📊 Step 1: Gathering market data...", "cyan", attrs=['bold'])
            market_data = self._gather_market_data()

            # Step 2: Analyze market regime
            cprint("\n🔍 Step 2: Analyzing market regime...", "cyan", attrs=['bold'])
            regime_analysis = self.analyze_market_regime(market_data)

            # Step 3: Select strategies
            cprint("\n🎯 Step 3: Selecting strategies...", "cyan", attrs=['bold'])
            strategies = self.select_strategies(
                regime_analysis['regime'],
                regime_analysis['recommended_risk_level']
            )

            # Step 4: Coordinate agents
            cprint("\n🎛️  Step 4: Coordinating agents...", "cyan", attrs=['bold'])
            agent_config = self.coordinate_agents(regime_analysis['regime'])

            # Compile cycle results
            cycle_results = {
                'timestamp': datetime.now().isoformat(),
                'regime': regime_analysis,
                'strategies': strategies,
                'agent_config': agent_config,
                'success': True
            }

            # Export results
            self._export_director_state(cycle_results)

            cprint("\n" + "="*80, "green")
            cprint("✅ DIRECTOR CYCLE COMPLETE", "green", attrs=['bold'])
            cprint("="*80, "green")

            return cycle_results

        except Exception as e:
            cprint(f"\n❌ Error in director cycle: {str(e)}", "red")
            return {
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }

    def _gather_market_data(self) -> Dict:
        """Gather current market data for analysis"""
        try:
            # Get account info
            balance = get_account_balance()
            positions = get_all_open_positions()

            # Get token data for monitored tokens (sample 5 for performance)
            tokens_data = []
            for token in MONITORED_TOKENS[:5]:
                if token in EXCLUDED_TOKENS:
                    continue
                try:
                    overview = token_overview(token)
                    if overview:
                        tokens_data.append(overview)
                except:
                    pass

            return {
                'balance': balance,
                'positions': positions,
                'tokens': tokens_data,
                'sentiment': 'neutral',  # Placeholder, would come from sentiment_agent
                'whale_activity': 'normal'  # Placeholder, would come from whale_agent
            }

        except Exception as e:
            cprint(f"⚠️  Error gathering market data: {str(e)}", "yellow")
            return {
                'balance': 0,
                'positions': [],
                'tokens': [],
                'sentiment': 'unknown',
                'whale_activity': 'unknown'
            }

    def _export_director_state(self, results: Dict):
        """Export director state to file"""
        try:
            output_dir = Path("src/data/deepseek_director")
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = output_dir / f"director_state_{timestamp}.json"

            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)

            cprint(f"\n📁 Director state exported: {filepath}", "green")

        except Exception as e:
            cprint(f"⚠️  Could not export director state: {str(e)}", "yellow")


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Run DeepSeek Trading Director standalone
    """
    cprint("\n🌙 Moon Dev DeepSeek Trading Director", "white", "on_blue", attrs=['bold'])
    cprint("Autonomous AI Trading System Leader\n", "white", "on_blue")

    # Initialize director
    director = DeepSeekTradingDirector(config={
        'max_strategies': 3,
        'risk_tolerance': 'medium',
        'enable_trade_approval': True
    })

    # Run one director cycle
    results = director.run_director_cycle()

    # Display summary
    if results['success']:
        cprint(f"\n✅ Director cycle completed successfully", "green", attrs=['bold'])
        cprint(f"📊 Market Regime: {results['regime']['regime']}", "cyan")
        cprint(f"🎯 Strategies Selected: {len(results['strategies'])}", "cyan")
        cprint(f"🎛️  Active Agents: {sum(results['agent_config'].values())}", "cyan")
    else:
        cprint(f"\n❌ Director cycle failed: {results.get('error')}", "red")
