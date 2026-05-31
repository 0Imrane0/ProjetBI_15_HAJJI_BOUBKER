#!/usr/bin/env python3
"""
Run Phase 6 checks in the expected order.
"""

import subprocess
import sys


COMMANDS = [
    ("Unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
    ("Integration checks", [sys.executable, "tests/integration_check.py"]),
    ("Synthetic E2E check", [sys.executable, "tests/e2e_rabbitmq_to_recommendations.py"]),
    ("Stress check", [sys.executable, "tests/stress_check.py"]),
]


def main():
    for label, command in COMMANDS:
        print(f"\n=== {label} ===", flush=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            print(f"\n[FAIL] {label} failed", flush=True)
            return completed.returncode

    print("\n[PASS] Phase 6 test suite passed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
