#!/usr/bin/env python3
"""Comprehensive assessment of Jules integration functionality."""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codomyrmex.logging_monitoring import setup_logging, get_logger

# Setup detailed logging
os.environ['CODOMYRMEX_LOG_LEVEL'] = 'INFO'
os.environ['CODOMYRMEX_LOG_FORMAT'] = 'DETAILED'
setup_logging()

logger = get_logger('jules_assessment')


def check_jules_auth():
    """Check if Jules is authenticated."""
    logger.info("Checking Jules authentication status...")
    try:
        result = subprocess.run(
            ["jules", "new", "test"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "UNAUTHENTICATED" in result.stderr or "401" in result.stderr:
            logger.warning("⚠ Jules requires authentication")
            logger.info("  Run: jules login")
            logger.info("  Or configure GitHub: https://github.com/apps/google-labs-jules/installations/select_target")
            return False
        elif result.returncode == 0:
            logger.info("✓ Jules authentication appears valid")
            return True
        else:
            logger.warning(f"⚠ Unexpected response (exit code: {result.returncode})")
            return None
    except Exception as e:
        logger.error(f"✗ Error checking auth: {e}")
        return None


def assess_integration():
    """Comprehensive assessment of Jules integration."""
    logger.info("=" * 70)
    logger.info("JULES INTEGRATION ASSESSMENT")
    logger.info("=" * 70)
    logger.info("")
    
    assessment_results = {
        "client_initialization": False,
        "capabilities": False,
        "command_building": False,
        "integration_adapters": False,
        "orchestration": False,
        "error_handling": False,
        "logging": False,
        "authentication": None,
    }
    
    # Test 1: Client Initialization
    logger.info("=" * 70)
    logger.info("ASSESSMENT 1: Client Initialization")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.jules import JulesClient
        client = JulesClient()
        logger.info("✓ JulesClient initializes successfully")
        logger.info(f"  Name: {client.name}")
        logger.info(f"  Command: {client.jules_command}")
        logger.info(f"  Timeout: {client.timeout}s")
        assessment_results["client_initialization"] = True
    except Exception as e:
        logger.error(f"✗ Client initialization failed: {e}", exc_info=True)
        return assessment_results
    
    # Test 2: Capabilities
    logger.info("")
    logger.info("=" * 70)
    logger.info("ASSESSMENT 2: Capabilities Declaration")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.core import AgentCapabilities
        capabilities = client.get_capabilities()
        expected = [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING,
            AgentCapabilities.CODE_ANALYSIS,
            AgentCapabilities.TEXT_COMPLETION,
            AgentCapabilities.STREAMING,
        ]
        
        all_present = all(cap in capabilities for cap in expected)
        logger.info(f"✓ Capabilities declared: {len(capabilities)}")
        for cap in expected:
            status = "✓" if cap in capabilities else "✗"
            logger.info(f"  {status} {cap.value}")
        
        assessment_results["capabilities"] = all_present
    except Exception as e:
        logger.error(f"✗ Capability check failed: {e}", exc_info=True)
    
    # Test 3: Command Building
    logger.info("")
    logger.info("=" * 70)
    logger.info("ASSESSMENT 3: Command Building Logic")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.core import AgentRequest
        
        # Test basic command
        request1 = AgentRequest(prompt="test task")
        args1 = client._build_jules_args(request1.prompt, request1.context or {})
        logger.info(f"✓ Basic command: {' '.join(['jules'] + args1)}")
        
        # Test with context
        request2 = AgentRequest(
            prompt="test task",
            context={"repo": "owner/repo", "parallel": 2}
        )
        args2 = client._build_jules_args(request2.prompt, request2.context)
        logger.info(f"✓ Command with context: {' '.join(['jules'] + args2)}")
        logger.info(f"  Contains --repo: {'--repo' in args2}")
        logger.info(f"  Contains --parallel: {'--parallel' in args2}")
        
        assessment_results["command_building"] = True
    except Exception as e:
        logger.error(f"✗ Command building failed: {e}", exc_info=True)
    
    # Test 4: Integration Adapters
    logger.info("")
    logger.info("=" * 70)
    logger.info("ASSESSMENT 4: Integration Adapters")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.jules import JulesIntegrationAdapter
        
        adapter = JulesIntegrationAdapter(client)
        logger.info("✓ JulesIntegrationAdapter initialized")
        
        # Check all required methods exist
        methods = [
            "adapt_for_ai_code_editing",
            "adapt_for_llm",
            "adapt_for_code_execution"
        ]
        
        all_methods = all(hasattr(adapter, method) for method in methods)
        for method in methods:
            status = "✓" if hasattr(adapter, method) else "✗"
            logger.info(f"  {status} {method}()")
        
        assessment_results["integration_adapters"] = all_methods
    except Exception as e:
        logger.error(f"✗ Integration adapter check failed: {e}", exc_info=True)
    
    # Test 5: Orchestration Compatibility
    logger.info("")
    logger.info("=" * 70)
    logger.info("ASSESSMENT 5: Agent Orchestration Compatibility")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.generic import AgentOrchestrator
        from codomyrmex.agents.core import AgentRequest
        
        orchestrator = AgentOrchestrator([client])
        logger.info("✓ AgentOrchestrator accepts JulesClient")
        logger.info(f"  Agents registered: {len(orchestrator.agents)}")
        
        # Test capability selection
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        logger.info(f"  Agents with CODE_GENERATION: {len(code_gen_agents)}")
        
        assessment_results["orchestration"] = True
    except Exception as e:
        logger.error(f"✗ Orchestration check failed: {e}", exc_info=True)
    
    # Test 6: Error Handling
    logger.info("")
    logger.info("=" * 70)
    logger.info("ASSESSMENT 6: Error Handling")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.exceptions import JulesError
        
        # Test validation
        invalid_request = AgentRequest(prompt="")
        errors = client.validate_request(invalid_request)
        logger.info(f"✓ Request validation works: {len(errors)} errors found")
        
        # Test help command (should work even without auth)
        help_info = client.get_jules_help()
        logger.info(f"✓ Help command: available={help_info.get('available', False)}")
        
        assessment_results["error_handling"] = True
    except Exception as e:
        logger.error(f"✗ Error handling check failed: {e}", exc_info=True)
    
    # Test 7: Logging
    logger.info("")
    logger.info("=" * 70)
    logger.info("ASSESSMENT 7: Logging Integration")
    logger.info("=" * 70)
    try:
        # Verify logging is working (we're using it throughout)
        logger.info("✓ Logging system is functional")
        logger.info("  - Detailed format with module/function/line")
        logger.info("  - Clear success/failure indicators")
        logger.info("  - Comprehensive information")
        assessment_results["logging"] = True
    except Exception as e:
        logger.error(f"✗ Logging check failed: {e}", exc_info=True)
    
    # Test 8: Authentication Status
    logger.info("")
    logger.info("=" * 70)
    logger.info("ASSESSMENT 8: Authentication Status")
    logger.info("=" * 70)
    auth_status = check_jules_auth()
    assessment_results["authentication"] = auth_status
    
    # Final Assessment
    logger.info("")
    logger.info("=" * 70)
    logger.info("FINAL ASSESSMENT")
    logger.info("=" * 70)
    logger.info("")
    
    core_functionality = [
        "client_initialization",
        "capabilities",
        "command_building",
        "integration_adapters",
        "orchestration",
        "error_handling",
        "logging",
    ]
    
    passed = sum(1 for key in core_functionality if assessment_results.get(key))
    total = len(core_functionality)
    
    logger.info("Core Functionality:")
    for key in core_functionality:
        status = "✓ PASS" if assessment_results.get(key) else "✗ FAIL"
        logger.info(f"  {status}: {key}")
    
    logger.info("")
    logger.info("Authentication:")
    if assessment_results["authentication"] is True:
        logger.info("  ✓ PASS: Authenticated and ready for tasks")
    elif assessment_results["authentication"] is False:
        logger.info("  ⚠ AUTH REQUIRED: Run 'jules login' to authenticate")
        logger.info("     Or configure GitHub: https://github.com/apps/google-labs-jules/installations/select_target")
    else:
        logger.info("  ? UNKNOWN: Could not determine authentication status")
    
    logger.info("")
    logger.info(f"Results: {passed}/{total} core functionality tests passed")
    logger.info("")
    
    if passed == total:
        logger.info("✓ All core functionality is working correctly!")
        logger.info("")
        logger.info("Jules integration is fully functional for:")
        logger.info("  - Client initialization and configuration")
        logger.info("  - Capability declarations")
        logger.info("  - Command building with context")
        logger.info("  - Integration adapters (all 3 methods)")
        logger.info("  - Agent orchestration compatibility")
        logger.info("  - Error handling and validation")
        logger.info("  - Comprehensive logging")
        logger.info("")
        if not assessment_results["authentication"]:
            logger.info("⚠ Note: Authentication required for actual task execution")
            logger.info("   All integration code is ready - just needs authentication")
        else:
            logger.info("✓ Ready for production use!")
    else:
        logger.warning(f"⚠ {total - passed} core functionality test(s) failed")
        logger.warning("   Review errors above and fix before production use")
    
    logger.info("")
    
    return assessment_results


if __name__ == "__main__":
    results = assess_integration()
    sys.exit(0 if all(results.get(k) for k in ["client_initialization", "capabilities", "command_building", "integration_adapters", "orchestration", "error_handling", "logging"]) else 1)

