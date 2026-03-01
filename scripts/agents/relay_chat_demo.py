"""Relay Chat Demo — Long-Lived Discursive Interaction.

Demonstrates a permanent, ping-ponging conversation between two autonomous agents:
1. Antigravity Side (Simulated User/Agent)
2. Claude Code Side (Simulated Assistant)

Both sides use real LLM inference via `agent_utils`.
The conversation runs indefinitely until KeyboardInterrupt.
"""

"""Relay Chat Demo — Long-Lived Discursive Interaction.

Demonstrates a permanent, ping-ponging conversation between two autonomous agents:
1. Antigravity Side (Simulated User/Agent)
2. Claude Code Side (Simulated Assistant)

Uses the modular `AutonomousAgent` class from `codomyrmex.agents`.
"""

import time
import sys
from pathlib import Path

# Ensure src is in path if run directly
try:
    from codomyrmex.agents.autonomous import AutonomousAgent
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))
    from codomyrmex.agents.autonomous import AutonomousAgent

from codomyrmex.ide.antigravity.agent_relay import AgentRelay

CHANNEL = "demo-chat"
RUNNING = True

def main():
    global RUNNING
    # Clean up any previous run
    AgentRelay(CHANNEL).clear()
    
    print("=== Starting Long-Lived Relay Chat (Modular) ===")
    print("Press Ctrl+C to stop.")

    # 1. Create Agents
    # Antigravity Side
    ag_agent = AutonomousAgent(
        identity="antigravity",
        persona="Curious Scientist. Ask deep questions about the universe.",
        channel=CHANNEL,
        think_time=2.0
    )
    
    # Claude Side
    cc_agent = AutonomousAgent(
        identity="claude_code",
        persona="Wise Philosopher. Provide thoughtful, abstract answers.",
        channel=CHANNEL,
        think_time=2.0
    )

    # 2. Start Agents (in background threads)
    # The AutonomousAgent.start() method blocks if background=False
    # We want them parallel, so we run them in threads or async
    # AutonomousAgent uses ClaudeCodeEndpoint which is threaded, so .start() is non-blocking?
    # Let's check implementation. created file says: 
    # self.endpoint.start() ... if not background: while loop
    # So start(background=True) is non-blocking.
    
    ag_agent.start(background=True)
    cc_agent.start(background=True)

    # 3. Kickoff
    time.sleep(2)
    ag_agent.send("Hello! I am ready to explore the mysteries of the cosmos. What is your perspective on time?")

    # 4. Main Loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Interrupted! Shutting down...")
        
    ag_agent.stop()
    cc_agent.stop()
    print("\nDemo complete.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
