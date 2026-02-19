"""Discursive Debate — Multi-agent dialectic.

Demonstrates two agents (Optimist vs Pessimist) debating a topic
via the relay until a turn limit is reached.

Flow:
1. Moderator -> Optimist: "Topic: Future of AI..."
2. Optimist -> Relay (broadcast): "AI is great..."
3. Pessimist -> Relay (broadcast): "AI is dangerous..."
"""

import time
import threading
from codomyrmex.ide.antigravity.live_bridge import ClaudeCodeEndpoint
from codomyrmex.ide.antigravity.agent_relay import AgentRelay
from codomyrmex.agents.core import AgentRequest

from agent_utils import get_llm_client

CHANNEL = "debate-club"

class DebaterAgent:
    """Run a debater agent with a specific stance."""
    def __init__(self, identity, stance, duration=15):
        self.identity = identity
        self.stance = stance
        self.duration = duration
        self.client = get_llm_client(identity=identity)
        
        self.endpoint = ClaudeCodeEndpoint(
            CHANNEL,
            identity=identity,
            poll_interval=0.5,
            claude_client=self.client,
            auto_respond=False
        )
        self.endpoint.on_message(self._handle_message)

    def start(self):
        self.endpoint.start()
        time.sleep(self.duration)
        self.endpoint.stop()

    def _handle_message(self, msg):
        print(f"\n[{self.identity.title()}] Received from {msg.sender}: {msg.content}")
        
        # Don't reply to self! (Already filtered by endpoint but good to be safe logic-wise)
        if msg.sender == self.identity:
            return None

        # Moderator starts it
        # Or other debater replies
        
        # System Prompt construction
        full_prompt = (
            f"System: You are an {self.stance.title()} debating the topic 'Future of AI'. "
            f"Your opponent just said: '{msg.content}'. "
            "Respond with a counter-argument consistent with your stance. "
            "Keep it short (max 2 sentences). "
            "If the moderator spoke, start your opening statement."
            f"\n\nUser: {msg.content}"
        )
        
        request = AgentRequest(prompt=full_prompt, context=msg.metadata)
        
        try:
            response = self.client.execute_with_session(request, session=None)
            if hasattr(response, 'is_success') and response.is_success():
                return response.content
            return f"Error: {response.error}" if hasattr(response, 'error') else str(response.content)
        except Exception as e:
            return f"Error executing agent: {e}"

def run_debater(identity, stance):
    agent = DebaterAgent(identity, stance, duration=20)
    agent.start()

def main():
    AgentRelay(CHANNEL).clear()
    
    # Start agents
    t1 = threading.Thread(target=run_debater, args=("optimist", "optimist"))
    t2 = threading.Thread(target=run_debater, args=("pessimist", "pessimist"))
    
    t1.start()
    t2.start()
    
    # Kick it off manually
    time.sleep(2)
    relay = AgentRelay(CHANNEL)
    print("\n[Moderator] Topic: The Future of AI. Optimist, start.")
    relay.post_message("moderator", "Topic: The Future of AI. Optimist, please start.")
    
    t1.join()
    t2.join()
    print("\nDebate concluded.")

if __name__ == "__main__":
    main()
