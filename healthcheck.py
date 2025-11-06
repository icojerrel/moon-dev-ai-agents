#!/usr/bin/env python3
"""
Health Check Script for Moon Dev AI Trading Agents
Verifies that the main application process is running and responsive.
"""

import sys
import os
import subprocess
from pathlib import Path


def check_process_running():
    """Check if main.py process is running using ps command."""
    try:
        # Use ps to check for main.py process
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Look for main.py in the process list
        for line in result.stdout.splitlines():
            if 'main.py' in line and 'python' in line.lower():
                return True

        return False
    except Exception as e:
        print(f"Error checking process: {e}", file=sys.stderr)
        return False


def check_health_file():
    """Check if application health file exists and is recent."""
    health_file = Path('/app/.health')

    if not health_file.exists():
        # If health file doesn't exist, skip this check
        # (application might not be writing health files)
        return None

    try:
        # Check if health file was updated in the last 10 minutes
        import time
        file_age = time.time() - health_file.stat().st_mtime

        # If file is older than 10 minutes, consider it stale
        if file_age > 600:
            print(f"Health file is stale (age: {file_age:.0f}s)", file=sys.stderr)
            return False

        return True
    except Exception as e:
        print(f"Error checking health file: {e}", file=sys.stderr)
        return None


def main():
    """Main health check logic."""
    # Check if main.py process is running
    process_running = check_process_running()

    if not process_running:
        print("Health check FAILED: main.py process not found", file=sys.stderr)
        sys.exit(1)

    # Check health file if it exists
    health_file_status = check_health_file()

    if health_file_status is False:
        print("Health check FAILED: health file is stale", file=sys.stderr)
        sys.exit(1)

    # All checks passed
    print("Health check PASSED: application is running")
    sys.exit(0)


if __name__ == '__main__':
    main()
