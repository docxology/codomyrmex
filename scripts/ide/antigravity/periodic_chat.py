#!/usr/bin/env python3
"""
Periodic Chat Messaging for Antigravity.
Simulates a "Real IDE UX" by sending status updates or messages on a timer.
"""

import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ide.antigravity import AntigravityClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("antigravity.periodic")

def run_periodic_chat(interval: int, limit: int = -1, use_gui: bool = False):
    client = AntigravityClient()
    
    if not client.connect():
        logger.error("❌ Not connected to Antigravity.")
        return False
        
    logger.info(f"Connected to Conversation: {client.get_conversation_id()}")
    mode_str = "GUI" if use_gui else "CLI (cycling modes)"
    logger.info(f"Starting periodic chat loop ({mode_str}). Interval: {interval}s")
    
    modes = ["agent", "ask", "pyrefly"]
    
    count = 0
    try:
        while limit == -1 or count < limit:
            count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if use_gui:
                message = f"[{timestamp}] GUI Status update #{count}"
                logger.info(f"Sending via GUI: {message}")
                
                result = client.send_chat_gui(message)
                
                if result.success:
                    logger.info("   ✅ Sent successfully (via gui keystrokes)")
                else:
                    logger.error(f"   ❌ Failed: {result.error}")
            else:
                # Send to all modes to find the right one
                for mode in modes:
                    message = f"[{timestamp}] Status update #{count} (Mode: {mode})"
                    logger.info(f"Sending: {message}")
                    
                    result = client.send_chat_message(message, mode=mode)
                    
                    if result.success:
                        method = result.output.get("method", "unknown")
                        logger.info(f"   ✅ Sent successfully (via {method}, mode={mode})")
                    else:
                        logger.error(f"   ❌ Failed: {result.error}")
                
            if limit != -1 and count >= limit:
                break
                
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("\nStopping periodic chat.")
        
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send periodic chat messages to Antigravity.")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds (default: 60)")
    parser.add_argument("--limit", type=int, default=-1, help="Number of messages to send (default: infinite)")
    parser.add_argument("--gui", action="store_true", help="Use GUI automation instead of CLI")
    
    args = parser.parse_args()
    
    if run_periodic_chat(args.interval, args.limit, use_gui=args.gui):
        sys.exit(0)
    else:
        sys.exit(1)
