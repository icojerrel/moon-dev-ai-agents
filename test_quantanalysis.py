"""
🧪 Test script for QuantAnalysis Agent
Quick test to verify the multi-agent system works correctly
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.quantanalysis_agent import QuantAnalysisAgent
from termcolor import cprint

def test_quantanalysis():
    """Test QuantAnalysis agent on a single symbol"""

    cprint("\n" + "="*70, "cyan")
    cprint("🧪 TESTING QUANTANALYSIS AGENT", "cyan")
    cprint("="*70 + "\n", "cyan")

    try:
        # Initialize agent
        cprint("1️⃣ Initializing QuantAnalysis Agent...", "yellow")
        agent = QuantAnalysisAgent()
        cprint("✅ Agent initialized successfully!\n", "green")

        # Test on BTC (HyperLiquid symbol)
        symbol = "BTC"
        timeframe = "1H"
        bars = 100

        cprint(f"2️⃣ Running analysis on {symbol} ({timeframe}, {bars} bars)...", "yellow")
        result = agent.analyze(symbol, timeframe=timeframe, bars=bars)

        if result:
            cprint("\n" + "="*70, "green")
            cprint("✅ TEST PASSED - Analysis Complete!", "green")
            cprint("="*70, "green")

            cprint(f"\n📊 RESULTS for {symbol}:", "cyan")
            cprint("-" * 70, "cyan")
            cprint(f"  Action:         {result['action']}", "white")
            cprint(f"  Confidence:     {result['confidence']}%", "white")
            cprint(f"  Position:       {result.get('position_type', 'N/A')}", "white")
            cprint(f"  Timeframe:      {result['timeframe']}", "white")
            cprint(f"  Analysis Time:  {result['analysis_time_seconds']}s", "white")
            cprint(f"\n  Reasoning:", "white")
            cprint(f"  {result['reasoning']}", "yellow")

            cprint(f"\n  Stop Loss:      {result['stop_loss']}", "white")
            cprint(f"  Take Profit:    {result['take_profit']}", "white")

            # Component analyses
            if 'component_analyses' in result:
                cprint(f"\n  🔵 Indicator Agent:", "blue")
                ind = result['component_analyses'].get('indicator', {})
                cprint(f"     Direction: {ind.get('direction', 'N/A')} "
                      f"(Confidence: {ind.get('confidence', 0)}%)", "blue")

                cprint(f"\n  🟢 Pattern Agent:", "green")
                pat = result['component_analyses'].get('pattern', {})
                cprint(f"     Pattern: {pat.get('pattern', 'N/A')}", "green")
                cprint(f"     Direction: {pat.get('direction', 'N/A')} "
                      f"(Confidence: {pat.get('confidence', 0)}%)", "green")

                cprint(f"\n  🟡 Trend Agent:", "yellow")
                trend = result['component_analyses'].get('trend', {})
                cprint(f"     Direction: {trend.get('direction', 'N/A')}", "yellow")
                cprint(f"     Strength: {trend.get('strength', 'N/A')} "
                      f"(Confidence: {trend.get('confidence', 0)}%)", "yellow")

            cprint("\n" + "="*70 + "\n", "green")

            return True
        else:
            cprint("\n❌ TEST FAILED - No results returned", "red")
            return False

    except Exception as e:
        cprint(f"\n❌ TEST FAILED - Error: {str(e)}", "red")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    cprint("\n🌙 Moon Dev's QuantAnalysis Agent Test", "cyan")
    cprint("Testing the 4-agent system: Indicator → Pattern → Trend → Decision\n", "cyan")

    success = test_quantanalysis()

    if success:
        cprint("\n🎉 All tests passed! QuantAnalysis agent is ready to use.", "green")
        cprint("\nNext steps:", "cyan")
        cprint("  1. Enable in config.py: ENABLE_QUANTANALYSIS = True", "yellow")
        cprint("  2. Enable in main.py: ACTIVE_AGENTS['quantanalysis'] = True", "yellow")
        cprint("  3. Run: python src/main.py", "yellow")
    else:
        cprint("\n❌ Tests failed. Please check the errors above.", "red")

    cprint("\n" + "="*70 + "\n", "cyan")
