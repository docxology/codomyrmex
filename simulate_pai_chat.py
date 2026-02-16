"""
Simulate PAI Chat User Interface.

A CLI tool to simulate a user chatting with PAI in Claude Code.
It uses the PAISimulator to resolve slash commands and execute their workflows.
"""

import argparse
import sys
from pathlib import Path

# Ensure src is in path
sys.path.append(str(Path(__file__).parent / "src"))

from codomyrmex.tests.simulation.pai_simulator import PAISimulator
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Simulate PAI/Claude Code interaction.")
    parser.add_argument("--skill-path", default="~/.claude/skills/Codomyrmex", help="Path to PAI skill")
    parser.add_argument("--command", required=True, help="Slash command to simulate (e.g., /codomyrmexVerify)")
    
    args = parser.parse_args()
    
    print(f"\n🚀 Starting PAI Simulation Engine...")
    print(f"📂 Loading Skill: {args.skill_path}")
    
    try:
        simulator = PAISimulator(args.skill_path)
        print(f"✅ Skill Loaded: {simulator.skill_name}")
        print(f"   Registered Commands: {list(simulator.triggers.keys())}\n")
        
        print(f"💬 User says: {args.command}")
        
        success = simulator.execute_command(args.command)
        
        if success:
            print("\n✅ Simulation Completed Successfully")
            sys.exit(0)
        else:
            print("\n❌ Simulation Failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n🔥 Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
