#!/usr/bin/env python3
"""
Chat Messaging Demo for Antigravity
Demonstrates sending messages to the Antigravity chat interface.
"""

import logging
import sys
from pathlib import Path

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ide.antigravity import AntigravityClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("antigravity.chat")

def demo_chat():
    client = AntigravityClient()

    if not client.connect():
        logger.error("❌ Not connected to Antigravity.")
        return False

    logger.info(f"Connected to Conversation: {client.get_conversation_id()}\n")

    # Send a simple message
    msg = "This is a programmatic message from the `chat_demo.py` script."
    logger.info(f"Sending message: '{msg}'")

    result = client.send_chat_message(msg)

    if result.success:
        logger.info("✅ Message sent successfully!")
        logger.info(f"   Command: {result.command}")
        logger.info(f"   Args: {result.output.get('args')}")
    else:
        logger.error(f"❌ Failed to send message: {result.error}")
        return False

    return True


    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ide" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/ide/config.yaml")

if __name__ == "__main__":
    if demo_chat():
        sys.exit(0)
    else:
        sys.exit(1)
