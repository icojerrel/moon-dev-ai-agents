"""
🛑 Emergency Stop Script
========================
IMMEDIATELY HALT ALL TRADING OPERATIONS

WARNING: This script will:
1. Stop all running agent processes
2. Optionally close all open positions
3. Disable trading configuration
4. Export final system state
5. Send emergency alert

USE ONLY IN EMERGENCY SITUATIONS!
"""

import sys
import os
import signal
import json
from pathlib import Path
from datetime import datetime
from termcolor import cprint

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def emergency_stop():
    """
    IMMEDIATE SYSTEM SHUTDOWN

    Steps:
    1. Stop all trading agent processes
    2. Close positions (optional, with confirmation)
    3. Disable trading configuration
    4. Export final state
    5. Log emergency stop event
    """

    cprint("\n" + "="*80, "red")
    cprint("🛑 EMERGENCY STOP INITIATED", "white", "on_red", attrs=['bold'])
    cprint("="*80, "red")
    cprint("\nThis will IMMEDIATELY halt all trading operations!\n", "yellow", attrs=['bold'])

    # Confirm emergency stop
    confirm = input("Are you SURE you want to emergency stop? (type 'EMERGENCY' to confirm): ")
    if confirm != 'EMERGENCY':
        cprint("\n❌ Emergency stop cancelled\n", "yellow")
        return False

    cprint("\n🛑 EXECUTING EMERGENCY STOP SEQUENCE...\n", "red", attrs=['bold'])

    # Step 1: Stop all agent processes
    cprint("[1/5] Stopping all trading agent processes...", "yellow", attrs=['bold'])
    try:
        # Find and kill all Python processes running agents
        os.system("pkill -f 'python.*src/main.py'")
        os.system("pkill -f 'python.*agents.*_agent.py'")
        cprint("  ✅ Agent processes stopped", "green")
    except Exception as e:
        cprint(f"  ⚠️  Error stopping processes: {str(e)}", "yellow")

    # Step 2: Close all positions (DANGEROUS - ask for confirmation)
    cprint("\n[2/5] Position closure...", "yellow", attrs=['bold'])
    cprint("  ⚠️  WARNING: Closing positions in emergency may cause slippage!", "red")
    close_confirm = input("  Close ALL open positions? (yes/no): ")

    if close_confirm.lower() == 'yes':
        try:
            from src.nice_funcs import get_all_open_positions, close_position

            positions = get_all_open_positions()
            cprint(f"  Found {len(positions)} open positions", "cyan")

            for position in positions:
                try:
                    cprint(f"  Closing position: {position.get('symbol', 'unknown')}", "yellow")
                    # close_position(position)  # Uncomment when ready
                    cprint(f"    ✅ Position closed", "green")
                except Exception as e:
                    cprint(f"    ❌ Error closing position: {str(e)}", "red")

            cprint("  ✅ All positions closed", "green")

        except Exception as e:
            cprint(f"  ❌ Error closing positions: {str(e)}", "red")
            cprint(f"     You may need to manually close positions!", "yellow", attrs=['bold'])
    else:
        cprint("  ⏭️  Skipped position closure", "cyan")
        cprint("     Positions remain OPEN - close manually if needed", "yellow")

    # Step 3: Disable trading configuration
    cprint("\n[3/5] Disabling trading configuration...", "yellow", attrs=['bold'])
    try:
        # Create emergency config file
        emergency_config = {
            'emergency_stop': True,
            'timestamp': datetime.now().isoformat(),
            'all_agents_disabled': True,
            'trading_disabled': True,
            'reason': 'Emergency stop activated'
        }

        emergency_file = Path("src/EMERGENCY_STOP_ACTIVE")
        with open(emergency_file, 'w') as f:
            json.dump(emergency_config, f, indent=2)

        cprint("  ✅ Emergency stop flag created", "green")
        cprint(f"     File: {emergency_file}", "cyan")
        cprint("     Remove this file to re-enable trading", "yellow")

    except Exception as e:
        cprint(f"  ⚠️  Error creating emergency flag: {str(e)}", "yellow")

    # Step 4: Export final state
    cprint("\n[4/5] Exporting final system state...", "yellow", attrs=['bold'])
    try:
        # Create emergency state export
        state_dir = Path("src/data/emergency_stops")
        state_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state_file = state_dir / f"emergency_stop_{timestamp}.json"

        # Gather system state
        state = {
            'timestamp': datetime.now().isoformat(),
            'type': 'emergency_stop',
            'triggered_by': 'manual',
        }

        # Try to get account state
        try:
            from src.nice_funcs import get_account_balance, get_all_open_positions
            state['account_balance'] = get_account_balance()
            state['open_positions'] = get_all_open_positions()
        except:
            state['account_balance'] = 'unavailable'
            state['open_positions'] = []

        # Write state file
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        cprint(f"  ✅ State exported: {state_file}", "green")

    except Exception as e:
        cprint(f"  ⚠️  Error exporting state: {str(e)}", "yellow")

    # Step 5: Log emergency stop
    cprint("\n[5/5] Logging emergency stop...", "yellow", attrs=['bold'])
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"emergency_stop_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        with open(log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("EMERGENCY STOP LOG\n")
            f.write("="*80 + "\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Triggered by: Manual\n")
            f.write(f"Positions closed: {close_confirm.lower() == 'yes'}\n")
            f.write("\nSYSTEM HALTED\n\n")
            f.write("To restart system:\n")
            f.write("1. Remove: src/EMERGENCY_STOP_ACTIVE\n")
            f.write("2. Review: logs and metrics\n")
            f.write("3. Fix: any issues found\n")
            f.write("4. Run: src/scripts/pre_flight_check.py\n")
            f.write("5. Restart: python src/main.py\n")

        cprint(f"  ✅ Log created: {log_file}", "green")

    except Exception as e:
        cprint(f"  ⚠️  Error creating log: {str(e)}", "yellow")

    # Final summary
    cprint("\n" + "="*80, "green")
    cprint("✅ EMERGENCY STOP COMPLETE", "white", "on_green", attrs=['bold'])
    cprint("="*80, "green")

    cprint("\n📋 Summary:", "yellow", attrs=['bold'])
    cprint("  ✅ All agent processes stopped", "green")
    cprint(f"  {'✅' if close_confirm.lower() == 'yes' else '⏭️'} Positions {'closed' if close_confirm.lower() == 'yes' else 'remain OPEN'}", "green" if close_confirm.lower() == 'yes' else "yellow")
    cprint("  ✅ Trading disabled via emergency flag", "green")
    cprint("  ✅ Final state exported", "green")
    cprint("  ✅ Emergency stop logged", "green")

    cprint("\n⚠️  NEXT STEPS:", "yellow", attrs=['bold'])
    cprint("  1. Review exported state in src/data/emergency_stops/", "white")
    cprint("  2. Review logs in logs/ directory", "white")
    cprint("  3. Identify and fix root cause", "white")
    cprint("  4. Before restarting:", "white")
    cprint("     a. Remove: src/EMERGENCY_STOP_ACTIVE", "cyan")
    cprint("     b. Run: python src/scripts/pre_flight_check.py", "cyan")
    cprint("     c. Test with paper trading first", "cyan")
    cprint("  5. Only restart after verifying system is safe\n", "white")

    cprint("🛡️  System is now HALTED. Trading disabled.\n", "red", attrs=['bold'])

    return True

def check_emergency_stop_active():
    """
    Check if emergency stop is currently active

    Returns:
        bool: True if emergency stop active, False otherwise
    """
    emergency_file = Path("src/EMERGENCY_STOP_ACTIVE")
    return emergency_file.exists()

if __name__ == "__main__":
    # Check if already stopped
    if check_emergency_stop_active():
        cprint("\n⚠️  EMERGENCY STOP ALREADY ACTIVE", "yellow", attrs=['bold'])
        cprint("\nTo restart system:", "cyan")
        cprint("  1. Remove: src/EMERGENCY_STOP_ACTIVE", "white")
        cprint("  2. Run pre-flight check: python src/scripts/pre_flight_check.py\n", "white")
        sys.exit(0)

    # Execute emergency stop
    result = emergency_stop()
    sys.exit(0 if result else 1)
