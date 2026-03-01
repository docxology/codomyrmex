#!/usr/bin/env python3
"""
GUI Chat Automation for Antigravity using AppleScript.
Sends keystrokes directly to the active window/pane.
"""

import sys
import subprocess
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("antigravity.gui")

def send_gui_message(message: str, app_name: str = "Antigravity"):
    """
    Sends a message to the specified application using AppleScript keystrokes.
    """
    apple_script = f'''
    tell application "{app_name}"
        activate
    end tell
    
    delay 0.5
    
    tell application "System Events"
        tell process "{app_name}"
            -- Type the message
            keystroke "{message}"
            delay 0.1
            -- Press Return
            key code 36
        end tell
    end tell
    '''
    
    try:
        subprocess.run(["osascript", "-e", apple_script], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ AppleScript failed: {e.stderr.decode()}")
        return False

def is_app_running(app_name: str) -> bool:
    """Check if an application is running using AppleScript."""
    apple_script = f'''
    tell application "System Events"
        set appRunning to (name of processes) contains "{app_name}"
        return appRunning
    end tell
    '''
    try:
        result = subprocess.run(["osascript", "-e", apple_script], 
                                capture_output=True, text=True, timeout=5)
        return result.stdout.strip() == "true"
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send GUI chat message to Antigravity.")
    parser.add_argument("--message", "-m", default="Hello from orchestrator test",
                        help="Message to send (default: test message)")
    parser.add_argument("--app", default="Antigravity", help="Application name (default: Antigravity)")
    
    args = parser.parse_args()
    
    # Check if app is running first
    if not is_app_running(args.app):
        logger.info(f"ℹ️  {args.app} is not running - skipping GUI automation (success).")
        sys.exit(0)
    
    logger.info(f"Sending to {args.app}: '{args.message}'")
    if send_gui_message(args.message, args.app):
        logger.info("✅ Sent successfully via GUI")
        sys.exit(0)
    else:
        sys.exit(1)
