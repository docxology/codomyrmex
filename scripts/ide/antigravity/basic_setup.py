#!/usr/bin/env python3
"""
Basic Setup & Connection Verification for Antigravity
"""

import sys
from pathlib import Path
import logging

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ide.antigravity import AntigravityClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("antigravity.setup")

def verify_connection():
    """Verify connection to Antigravity session."""
    logger.info("Initializing Antigravity Client...")
    client = AntigravityClient()
    
    logger.info(f"Artifact Directory: {client.artifact_dir}")
    
    if client.connect():
        logger.info("✅ Successfully connected to Antigravity session!")
        logger.info(f"   Conversation ID: {client.get_conversation_id()}")
        
        caps = client.get_capabilities()
        logger.info(f"   Provider: {caps.get('provider')}")
        logger.info(f"   Status: {caps.get('status')}")
        
        return True
    else:
        logger.error("❌ Failed to connect to Antigravity session.")
        logger.info("   Ensure you have an active session and the artifact directory exists.")
        return False

if __name__ == "__main__":
    if verify_connection():
        sys.exit(0)
    else:
        sys.exit(1)
