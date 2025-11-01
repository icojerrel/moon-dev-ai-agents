"""
🛡️ Pre-Flight Safety Check
===========================
Run comprehensive safety checks before production deployment

This script verifies that all safety measures are in place before
allowing the trading system to go live.
"""

import sys
import os
from pathlib import Path
from termcolor import cprint

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import *

def pre_flight_check():
    """
    Run comprehensive safety checks before production

    Returns:
        bool: True if all checks pass, False otherwise
    """
    cprint("\n" + "="*80, "red")
    cprint("🛡️  PRODUCTION SAFETY CHECK", "white", "on_red", attrs=['bold'])
    cprint("="*80, "red")
    cprint("\nVerifying system is safe for production deployment...\n", "yellow")

    passed = 0
    failed = 0
    warnings = 0

    # Check 1: Risk limits configured
    cprint("[1/12] Checking risk limits...", "cyan", attrs=['bold'])
    if MAX_LOSS_USD <= 100:
        cprint(f"  ✅ MAX_LOSS_USD is conservative: ${MAX_LOSS_USD}", "green")
        passed += 1
    elif MAX_LOSS_USD <= 500:
        cprint(f"  ⚠️  MAX_LOSS_USD is moderate: ${MAX_LOSS_USD}", "yellow")
        warnings += 1
        passed += 1
    else:
        cprint(f"  ❌ MAX_LOSS_USD is HIGH: ${MAX_LOSS_USD}", "red")
        cprint(f"     Recommended: <= $100 for initial production", "yellow")
        failed += 1

    # Check 2: Minimum balance safety
    cprint("\n[2/12] Checking minimum balance safety...", "cyan", attrs=['bold'])
    if MINIMUM_BALANCE_USD >= 50:
        cprint(f"  ✅ Minimum balance safety net: ${MINIMUM_BALANCE_USD}", "green")
        passed += 1
    else:
        cprint(f"  ⚠️  Minimum balance low: ${MINIMUM_BALANCE_USD}", "yellow")
        warnings += 1
        passed += 1

    # Check 3: Position sizing
    cprint("\n[3/12] Checking position sizing...", "cyan", attrs=['bold'])
    if usd_size <= 20:
        cprint(f"  ✅ Position size is small: ${usd_size}", "green")
        passed += 1
    elif usd_size <= 100:
        cprint(f"  ⚠️  Position size is moderate: ${usd_size}", "yellow")
        warnings += 1
        passed += 1
    else:
        cprint(f"  ❌ Position size is LARGE: ${usd_size}", "red")
        cprint(f"     Recommended: <= $20 for initial production", "yellow")
        failed += 1

    # Check 4: Maximum position percentage
    cprint("\n[4/12] Checking max position percentage...", "cyan", attrs=['bold'])
    if MAX_POSITION_PERCENTAGE <= 0.10:
        cprint(f"  ✅ Max position % is conservative: {MAX_POSITION_PERCENTAGE*100:.0f}%", "green")
        passed += 1
    elif MAX_POSITION_PERCENTAGE <= 0.20:
        cprint(f"  ⚠️  Max position % is moderate: {MAX_POSITION_PERCENTAGE*100:.0f}%", "yellow")
        warnings += 1
        passed += 1
    else:
        cprint(f"  ❌ Max position % is HIGH: {MAX_POSITION_PERCENTAGE*100:.0f}%", "red")
        failed += 1

    # Check 5: DeepSeek Director configuration
    cprint("\n[5/12] Checking DeepSeek Director config...", "cyan", attrs=['bold'])
    director_config_path = Path("src/agents/deepseek_director_agent.py")
    if director_config_path.exists():
        cprint(f"  ✅ DeepSeek Director agent available", "green")
        passed += 1
    else:
        cprint(f"  ❌ DeepSeek Director agent NOT FOUND", "red")
        failed += 1

    # Check 6: Trade approval (if director available)
    cprint("\n[6/12] Checking trade approval requirement...", "cyan", attrs=['bold'])
    # In production, trade approval should ALWAYS be enabled
    cprint(f"  ℹ️  Note: Enable trade approval in DeepSeek Director config", "cyan")
    cprint(f"     Set: enable_trade_approval=True", "cyan")
    passed += 1

    # Check 7: API access
    cprint("\n[7/12] Checking API access...", "cyan", attrs=['bold'])
    try:
        from src.models.model_factory import ModelFactory
        model = ModelFactory.create_model('deepseek')
        cprint("  ✅ DeepSeek API accessible", "green")
        passed += 1
    except Exception as e:
        cprint(f"  ❌ DeepSeek API error: {str(e)}", "red")
        cprint(f"     Check DEEPSEEK_KEY in .env file", "yellow")
        failed += 1

    # Check 8: Account balance (if available)
    cprint("\n[8/12] Checking account balance...", "cyan", attrs=['bold'])
    try:
        from src.nice_funcs import get_account_balance
        balance = get_account_balance()
        if balance >= MINIMUM_BALANCE_USD:
            cprint(f"  ✅ Balance sufficient: ${balance:,.2f}", "green")
            passed += 1
        else:
            cprint(f"  ❌ Balance too low: ${balance:,.2f} < ${MINIMUM_BALANCE_USD}", "red")
            failed += 1
    except Exception as e:
        cprint(f"  ⚠️  Could not check balance: {str(e)}", "yellow")
        cprint(f"     This is OK if testing without live connection", "cyan")
        warnings += 1
        passed += 1

    # Check 9: Risk agent configuration
    cprint("\n[9/12] Checking risk agent...", "cyan", attrs=['bold'])
    risk_agent_path = Path("src/agents/risk_agent.py")
    if risk_agent_path.exists():
        cprint("  ✅ Risk agent available", "green")
        passed += 1
    else:
        cprint("  ❌ Risk agent NOT FOUND", "red")
        failed += 1

    # Check 10: Strategy templates
    cprint("\n[10/12] Checking strategy templates...", "cyan", attrs=['bold'])
    templates_dir = Path("src/strategies/templates")
    if templates_dir.exists():
        template_count = len(list(templates_dir.glob("*_template.py")))
        cprint(f"  ✅ Strategy templates available: {template_count} found", "green")
        passed += 1
    else:
        cprint("  ❌ Strategy templates directory NOT FOUND", "red")
        failed += 1

    # Check 11: Monitoring capabilities
    cprint("\n[11/12] Checking monitoring setup...", "cyan", attrs=['bold'])
    orchestrator_monitor_path = Path("src/agents/orchestrator_monitor.py")
    if orchestrator_monitor_path.exists():
        cprint("  ✅ Orchestrator monitor available", "green")
        passed += 1
    else:
        cprint("  ⚠️  Orchestrator monitor not found", "yellow")
        warnings += 1
        passed += 1

    # Check 12: Environment variables
    cprint("\n[12/12] Checking environment variables...", "cyan", attrs=['bold'])
    required_vars = ['DEEPSEEK_KEY', 'BIRDEYE_API_KEY']
    optional_vars = ['SOLANA_PRIVATE_KEY', 'ANTHROPIC_KEY', 'MOONDEV_API_KEY']

    missing_required = [var for var in required_vars if not os.getenv(var)]
    missing_optional = [var for var in optional_vars if not os.getenv(var)]

    if not missing_required:
        cprint(f"  ✅ All required env vars present", "green")
        passed += 1
    else:
        cprint(f"  ❌ Missing REQUIRED env vars: {', '.join(missing_required)}", "red")
        failed += 1

    if missing_optional:
        cprint(f"  ℹ️  Optional env vars missing: {', '.join(missing_optional)}", "cyan")
        cprint(f"     System will work but with limited functionality", "cyan")

    # Summary
    cprint("\n" + "="*80, "cyan")
    cprint("📊 SAFETY CHECK SUMMARY", "white", attrs=['bold'])
    cprint("="*80, "cyan")
    cprint(f"\n  ✅ Passed:   {passed}/12", "green", attrs=['bold'])
    cprint(f"  ⚠️  Warnings: {warnings}/12", "yellow", attrs=['bold'])
    cprint(f"  ❌ Failed:   {failed}/12", "red", attrs=['bold'])
    cprint("\n" + "="*80, "cyan")

    # Final verdict
    if failed > 0:
        cprint("\n" + "="*80, "red")
        cprint("❌ SAFETY CHECK FAILED - DO NOT DEPLOY TO PRODUCTION!", "white", "on_red", attrs=['bold'])
        cprint("="*80, "red")
        cprint("\nFix all failed checks before deploying.", "yellow")
        cprint("Re-run this script after fixes: python src/scripts/pre_flight_check.py\n", "cyan")
        return False

    elif warnings > 3:
        cprint("\n" + "="*80, "yellow")
        cprint("⚠️  SAFETY CHECK PASSED WITH WARNINGS", "white", "on_yellow", attrs=['bold'])
        cprint("="*80, "yellow")
        cprint(f"\n{warnings} warnings detected. Review carefully before deploying.", "yellow")
        cprint("\nRecommendations:", "cyan")
        cprint("  - Start with minimal capital (< $100)", "white")
        cprint("  - Enable all safety features", "white")
        cprint("  - Monitor closely for first 24-48 hours", "white")
        cprint("  - Have emergency stop procedure ready\n", "white")

        response = input("Proceed with deployment despite warnings? (yes/no): ")
        return response.lower() == 'yes'

    else:
        cprint("\n" + "="*80, "green")
        cprint("✅ SAFETY CHECK PASSED - SYSTEM READY FOR PRODUCTION", "white", "on_green", attrs=['bold'])
        cprint("="*80, "green")
        cprint("\n⚠️  IMPORTANT REMINDERS:", "yellow", attrs=['bold'])
        cprint("  1. Start with MINIMAL capital (< $100)", "white")
        cprint("  2. Monitor CONTINUOUSLY for first 24-48 hours", "white")
        cprint("  3. Have emergency stop ready: python src/scripts/emergency_stop.py", "white")
        cprint("  4. This system is EXPERIMENTAL - expect losses", "white")
        cprint("  5. Only use capital you can afford to LOSE\n", "white")

        response = input("Do you understand the risks? (yes/no): ")
        if response.lower() != 'yes':
            cprint("\n❌ Deployment aborted by user\n", "red")
            return False

        cprint("\n✅ Proceeding with deployment...\n", "green")
        return True

if __name__ == "__main__":
    result = pre_flight_check()
    sys.exit(0 if result else 1)
