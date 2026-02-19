"""Autonomous Agent Implementation.

Provides a long-lived, autonomous agent class that can execute in a loop,
respond to messages on a relay channel, and maintain a persona.
"""

import time
import logging
import threading
from typing import Optional, Callable

from codomyrmex.ide.antigravity.live_bridge import ClaudeCodeEndpoint
from codomyrmex.agents.llm_client import get_llm_client, AgentRequest

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """A long-lived autonomous agent connected to a Relay Channel.
    
    Attributes:
        identity: The agent's name/ID on the channel.
        persona: Description of the agent's role/personality.
        channel: The relay channel ID to connect to.
        poll_interval: How often to check for messages (seconds).
        think_time: Artificial delay before responding (seconds).
    """
    
    def __init__(
        self,
        identity: str,
        persona: str,
        channel: str,
        poll_interval: float = 1.0,
        think_time: float = 2.0,
        model: str | None = None
    ):
        self.identity = identity
        self.persona = persona
        self.channel = channel
        self.poll_interval = poll_interval
        self.think_time = think_time
        self.running = False
        
        # Initialize Client
        self.client = get_llm_client(identity)
        
        # Initialize Endpoint (wrapper around Relay)
        # We use ClaudeCodeEndpoint because it has good polling/event logic
        # But we disable auto-respond to inject our own logic
        self.endpoint = ClaudeCodeEndpoint(
            channel,
            identity=identity,
            poll_interval=poll_interval,
            claude_client=self.client,
            auto_respond=False
        )
        
        self.endpoint.on_message(self._handle_message)

    def start(self, background: bool = True) -> None:
        """Start the agent loop."""
        logger.info(f"[{self.identity}] Starting Autonomous Agent ({self.persona})")
        self.running = True
        self.endpoint.start()
        
        if not background:
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Stop the agent loop."""
        logger.info(f"[{self.identity}] Stopping...")
        self.running = False
        self.endpoint.stop()

    def send(self, message: str) -> None:
        """Send a message to the channel."""
        logger.info(f"[{self.identity}] Sending: {message[:50]}...")
        self.endpoint.relay.post_message(self.identity, message)

    def _handle_message(self, msg) -> None:
        """Handle incoming messages."""
        if not self.running: return
        
        # Ignore self-messages and system messages (unless specific)
        if msg.sender == self.identity:
            return
            
        if not msg.is_chat:
            return

        logger.info(f"[{self.identity}] Received from {msg.sender}: {msg.content[:50]}...")
        
        # Thinking Delay
        if self.think_time > 0:
            logger.info(f"[{self.identity}] Thinking ({self.think_time}s)...")
            time.sleep(self.think_time)
            
        if not self.running: return

        # Generate Reply
        try:
            prompt = (
                f"System: You are {self.identity}. Persona: {self.persona}.\n"
                f"Reflect on the message and provide a thoughtful response.\n"
                f"User: {msg.content}"
            )
            req = AgentRequest(prompt=prompt)
            resp = self.client.execute_with_session(req)
            
            reply = resp.content.strip()
            self.send(reply)
            
        except Exception as e:
            logger.error(f"[{self.identity}] Generation error: {e}")
