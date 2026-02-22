import time
from codomyrmex.ide.antigravity.agent_relay import AgentRelay

class ExternalAgentClient:
    def __init__(self, relay: AgentRelay, identity: str, timeout: float = 300.0):
        self.relay = relay
        self.identity = identity
        self.timeout = timeout
        self.cursor = relay.get_latest_cursor()

    def execute_with_session(self, request, session=None):
        start = time.time()
        while time.time() - start < self.timeout:
            for msg in self.relay.poll_messages(since_cursor=self.cursor):
                self.cursor = max(self.cursor, msg.cursor)
                if msg.sender == self.identity and msg.is_chat:
                    class Resp:
                        content = msg.content
                    return Resp()
            time.sleep(1.0)
        raise TimeoutError("Waiting for external agent on relay timed out")

