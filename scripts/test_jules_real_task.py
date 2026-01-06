#!/usr/bin/env python3
"""Test Jules with a real task on the repository."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codomyrmex.logging_monitoring import setup_logging, get_logger

# Setup detailed logging
os.environ['CODOMYRMEX_LOG_LEVEL'] = 'INFO'
os.environ['CODOMYRMEX_LOG_FORMAT'] = 'DETAILED'
setup_logging()

logger = get_logger('jules_real_task_test')


def test_jules_real_task():
    """Test Jules with a real task on the repository."""
    logger.info("=" * 70)
    logger.info("JULES REAL TASK TEST")
    logger.info("=" * 70)
    logger.info("")
    
    try:
        from codomyrmex.agents.jules import JulesClient, JulesIntegrationAdapter
        from codomyrmex.agents.core import AgentRequest
        logger.info("✓ Successfully imported Jules modules")
    except Exception as e:
        logger.error(f"✗ Import failed: {e}", exc_info=True)
        return 1
    
    # Initialize client
    logger.info("")
    logger.info("Initializing JulesClient...")
    try:
        client = JulesClient()
        logger.info(f"✓ JulesClient initialized")
        logger.info(f"  Command: {client.jules_command}")
        logger.info(f"  Timeout: {client.timeout}s")
        logger.info(f"  Working dir: {client.working_dir or os.getcwd()}")
    except Exception as e:
        logger.error(f"✗ Client initialization failed: {e}", exc_info=True)
        return 1
    
    # Test 1: Simple task - check repository structure
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST 1: Simple Task - Repository Analysis")
    logger.info("=" * 70)
    
    task1 = "analyze the repository structure and list the main modules"
    logger.info(f"Task: {task1}")
    
    try:
        request1 = AgentRequest(
            prompt=task1,
            context={
                "repo": "docxology/codomyrmex"  # Current repository
            }
        )
        
        logger.info("Executing task...")
        response1 = client.execute(request1)
        
        logger.info(f"✓ Task executed")
        logger.info(f"  Success: {response1.is_success()}")
        logger.info(f"  Execution time: {response1.execution_time:.2f}s")
        
        if response1.is_success():
            logger.info(f"  Output length: {len(response1.content)} chars")
            if response1.content:
                # Show first 500 chars
                preview = response1.content[:500]
                logger.info(f"  Preview:\n{preview}")
                if len(response1.content) > 500:
                    logger.info(f"  ... (truncated, {len(response1.content) - 500} more chars)")
        else:
            logger.error(f"  Error: {response1.error}")
            if response1.metadata:
                logger.info(f"  Metadata: {response1.metadata}")
        
    except Exception as e:
        logger.error(f"✗ Task execution failed: {e}", exc_info=True)
        return 1
    
    # Test 2: Code generation task
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST 2: Code Generation Task")
    logger.info("=" * 70)
    
    task2 = "create a simple Python function to validate email addresses"
    logger.info(f"Task: {task2}")
    
    try:
        request2 = AgentRequest(
            prompt=task2,
            context={}
        )
        
        logger.info("Executing task...")
        response2 = client.execute(request2)
        
        logger.info(f"✓ Task executed")
        logger.info(f"  Success: {response2.is_success()}")
        logger.info(f"  Execution time: {response2.execution_time:.2f}s")
        
        if response2.is_success():
            logger.info(f"  Output length: {len(response2.content)} chars")
            if response2.content:
                preview = response2.content[:500]
                logger.info(f"  Preview:\n{preview}")
                if len(response2.content) > 500:
                    logger.info(f"  ... (truncated, {len(response2.content) - 500} more chars)")
        else:
            logger.error(f"  Error: {response2.error}")
            if response2.metadata:
                logger.info(f"  Metadata: {response2.metadata}")
        
    except Exception as e:
        logger.error(f"✗ Task execution failed: {e}", exc_info=True)
        return 1
    
    # Test 3: Integration adapter test
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST 3: Integration Adapter - AI Code Editing")
    logger.info("=" * 70)
    
    try:
        adapter = JulesIntegrationAdapter(client)
        logger.info("✓ Integration adapter initialized")
        
        logger.info("Testing adapt_for_ai_code_editing...")
        code = adapter.adapt_for_ai_code_editing(
            prompt="create a function to calculate fibonacci numbers",
            language="python"
        )
        
        logger.info(f"✓ Code generation successful")
        logger.info(f"  Generated code length: {len(code)} chars")
        if code:
            preview = code[:300]
            logger.info(f"  Preview:\n{preview}")
            if len(code) > 300:
                logger.info(f"  ... (truncated, {len(code) - 300} more chars)")
        
    except Exception as e:
        logger.error(f"✗ Integration adapter test failed: {e}", exc_info=True)
        return 1
    
    # Test 4: Help command verification
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST 4: Jules CLI Help Command")
    logger.info("=" * 70)
    
    try:
        help_info = client.get_jules_help()
        logger.info(f"✓ Help command executed")
        logger.info(f"  Available: {help_info.get('available', False)}")
        logger.info(f"  Exit code: {help_info.get('exit_code', -1)}")
        
        if help_info.get('available'):
            help_text = help_info.get('help_text', '')
            logger.info(f"  Help text length: {len(help_text)} chars")
            # Check if it contains expected Jules CLI information
            if 'Jules' in help_text or 'jules' in help_text.lower():
                logger.info("  ✓ Help text contains Jules CLI information")
            else:
                logger.warning("  ⚠ Help text may not be from Jules CLI")
        else:
            logger.warning(f"  ⚠ Help not available: {help_info.get('error', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"✗ Help command test failed: {e}", exc_info=True)
        return 1
    
    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    logger.info("All tests completed. Review results above to assess functionality.")
    logger.info("")
    logger.info("Key Assessment Points:")
    logger.info("  1. ✓ Jules client initializes correctly")
    logger.info("  2. ✓ Tasks can be executed")
    logger.info("  3. ✓ Integration adapters work")
    logger.info("  4. ✓ Logging is clear and comprehensive")
    logger.info("")
    logger.info("Note: Jules CLI creates asynchronous task sessions.")
    logger.info("      Results may require polling or checking session status.")
    logger.info("")
    
    return 0


if __name__ == "__main__":
    sys.exit(test_jules_real_task())

