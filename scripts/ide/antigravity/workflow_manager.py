#!/usr/bin/env python3
"""
Workflow Manager for Antigravity
Demonstrates creating and managing task artifacts programmatically.
"""

import sys
import time
from pathlib import Path
import logging

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ide.antigravity import AntigravityClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("antigravity.workflow")

def run_workflow():
    client = AntigravityClient()
    
    if not client.connect():
        logger.error("❌ Not connected to Antigravity.")
        return False
        
    logger.info(f"Using Conversation: {client.get_conversation_id()}")
    
    # 1. Create a Task
    task_name = f"automated_task_{int(time.time())}"
    logger.info(f"\n1. Creating Task: {task_name}...")
    
    content = f"""# Automated Task: {task_name}

- [ ] Initialize system
- [ ] Perform analysis
- [ ] Report results
"""
    
    try:
        artifact = client.create_artifact(
            name=task_name,
            content=content,
            artifact_type="task"
        )
        logger.info(f"   ✅ Created artifact at: {artifact['path']}")
    except Exception as e:
        logger.error(f"   ❌ Failed to create task: {e}")
        return False

    # 2. Simulate Work & Update Task
    logger.info("\n2. Simulating work (Marking item 1 complete)...")
    time.sleep(1)
    
    updated_content = content.replace("- [ ] Initialize system", "- [x] Initialize system")
    
    try:
        client.update_artifact(task_name, updated_content)
        logger.info("   ✅ Updated task artifact")
    except Exception as e:
        logger.error(f"   ❌ Failed to update task: {e}")
        return False

    # 3. Verify
    logger.info("\n3. Verifying Update...")
    fetched = client.get_artifact(task_name)
    if fetched and "- [x] Initialize system" in fetched["content"]:
        logger.info("   ✅ Verification Successful: Content updated on disk")
    else:
        logger.error("   ❌ Verification Failed: Content mismatch")
        return False
        
    logger.info("\n✨ Workflow demonstration complete!")
    return True

if __name__ == "__main__":
    if run_workflow():
        sys.exit(0)
    else:
        sys.exit(1)
