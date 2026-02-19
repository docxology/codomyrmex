"""Recursive Task Delegation — Nested agent collaboration.

Demonstrates a scenario where Agent A (Manager) delegates a task to 
Agent B (Worker). Agent B then asks Agent A for clarification,
Agent A responds, and Agent B completes the task.

Flow:
1. Manager -> Worker: "Generate a report for project X"
2. Worker -> Manager: "What is the deadline?" (Clarification)
3. Manager -> Worker: "Friday"
4. Worker -> Manager: "Report generated..."
"""

import time
import threading
from codomyrmex.ide.antigravity.live_bridge import ClaudeCodeEndpoint
from codomyrmex.ide.antigravity.agent_relay import AgentRelay
from codomyrmex.agents.core import AgentRequest

from agent_utils import get_llm_client

CHANNEL = "recursive-task"

class TaskAgent:
    """Helper to run a task agent with a specific persona."""
    def __init__(self, identity, system_prompt):
        self.identity = identity
        self.system_prompt = system_prompt
        self.client = get_llm_client(identity=identity)
        
        self.endpoint = ClaudeCodeEndpoint(
            CHANNEL,
            identity=identity,
            poll_interval=0.5,
            claude_client=self.client,
            auto_respond=False  # We handle messages manually to inject system prompt
        )
        # Register handler
        self.endpoint.on_message(self._handle_message)

    def start(self):
        self.endpoint.start()

    def stop(self):
        self.endpoint.stop()

    def send(self, message):
        self.endpoint.send(message)

    def _handle_message(self, msg):
        print(f"\n[{self.identity.title()}] Received from {msg.sender}: {msg.content}")
        
        # Construct prompt with system instruction
        # We wrap the user message with the system context
        full_prompt = f"System: {self.system_prompt}\n\nUser: {msg.content}"
        
        request = AgentRequest(prompt=full_prompt, context=msg.metadata)
        
        try:
            # We explicitly invoke the client with our constructed request
            response = self.client.execute_with_session(request, session=None)
            
            if hasattr(response, 'is_success') and response.is_success():
                return response.content
            elif hasattr(response, 'error'):
                return f"Error: {response.error}"
            return str(response.content)
            
        except Exception as e:
            return f"Error executing agent: {e}"

def run_manager():
    """Manager Agent (Alice)."""
    system_prompt = (
        "You are a project manager named Alice. You delegated a task 'Generate a report for project X'. "
        "If the worker asks for clarification (like deadline), provide reasonable answers (e.g. 'Friday'). "
        "keep your answers short (max 1 sentence)."
        "If they complete the task, thank them and end the conversation with 'Good job'."
    )
    agent = TaskAgent("manager", system_prompt)
    agent.start()
    
    # Manager initiates
    time.sleep(2)
    print("\n[Manager] Delegating task...")
    agent.send("Generate a report for project X.")
    
    time.sleep(15)
    agent.stop()

def run_worker():
    """Worker Agent (Bob)."""
    system_prompt = (
        "You are a worker named Bob. You received a task. "
        "If the task is missing details (like specifically the deadline), ask 'What is the deadline?'. "
        "Once you have the deadline, say 'Report generated' and complete the task. "
        "Keep your answers short (max 1 sentence)."
    )
    agent = TaskAgent("worker", system_prompt)
    agent.start()
    
    # Worker runs longer to listen
    time.sleep(16)
    agent.stop()

def main():
    AgentRelay(CHANNEL).clear()
    
    t1 = threading.Thread(target=run_manager)
    t2 = threading.Thread(target=run_worker)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print("\nRecursive task demo complete.")

if __name__ == "__main__":
    main()
