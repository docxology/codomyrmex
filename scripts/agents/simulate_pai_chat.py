"""
Simulate PAI Chat User Interface.

A CLI tool to simulate a user chatting with PAI in Claude Code.
It uses the PAISimulator to resolve slash commands and execute their workflows.
"""

import argparse
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from codomyrmex.tests.simulation.pai_simulator import PAISimulator
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Simulate PAI/Claude Code interaction.")
    parser.add_argument("--skill-path", default="~/.claude/skills/Codomyrmex", help="Path to PAI skill")
    parser.add_argument("--command", required=True, help="Slash command to simulate (e.g., /codomyrmexVerify)")

    args = parser.parse_args()

    print_info("Starting PAI Simulation Engine...")
    print_info(f"Loading Skill: {args.skill_path}")

    try:
        simulator = PAISimulator(args.skill_path)
        print_success(f"Skill Loaded: {simulator.skill_name}")
        print_info(f"Registered Commands: {list(simulator.triggers.keys())}")

        print_info(f"User says: {args.command}")

        success = simulator.execute_command(args.command)

        if success:
            print_success("Simulation Completed Successfully")
            return 0
        else:
            print_error("Simulation Failed")
            return 1

    except Exception as e:
        print_error(f"Critical Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
