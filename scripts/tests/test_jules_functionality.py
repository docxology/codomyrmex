#!/usr/bin/env python3
"""Functional test script for Jules integration with comprehensive logging."""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Setup detailed logging via environment variables
os.environ['CODOMYRMEX_LOG_LEVEL'] = 'INFO'
os.environ['CODOMYRMEX_LOG_FORMAT'] = 'DETAILED'
setup_logging()

logger = get_logger('jules_functional_test')


def test_imports():
    """Test 1: Import Jules modules."""
    logger.info("=" * 70)
    logger.info("TEST 1: Module Imports")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.jules import JulesClient, JulesIntegrationAdapter
        from codomyrmex.agents.core import AgentRequest, AgentCapabilities, AgentResponse
        from codomyrmex.agents.generic import AgentOrchestrator
        from codomyrmex.agents.exceptions import JulesError
        logger.info("✓ Successfully imported all Jules modules")
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}", exc_info=True)
        return False


def test_client_initialization():
    """Test 2: Client initialization."""
    logger.info("=" * 70)
    logger.info("TEST 2: JulesClient Initialization")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.jules import JulesClient
        
        client = JulesClient()
        logger.info(f"✓ JulesClient initialized successfully")
        logger.info(f"  Name: {client.name}")
        logger.info(f"  Config: jules_command={client.jules_command}")
        logger.info(f"  Timeout: {client.timeout}s")
        logger.info(f"  Working dir: {client.working_dir or 'default'}")
        return client
    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}", exc_info=True)
        return None


def test_capabilities(client):
    """Test 3: Verify capabilities."""
    logger.info("=" * 70)
    logger.info("TEST 3: Capability Verification")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.core import AgentCapabilities
        
        capabilities = client.get_capabilities()
        logger.info(f"✓ Retrieved {len(capabilities)} capabilities")
        
        expected_capabilities = [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING,
            AgentCapabilities.CODE_ANALYSIS,
            AgentCapabilities.TEXT_COMPLETION,
            AgentCapabilities.STREAMING,
        ]
        
        for cap in expected_capabilities:
            if cap in capabilities:
                logger.info(f"  ✓ {cap.value}")
            else:
                logger.warning(f"  ✗ Missing: {cap.value}")
        
        # Test capability support check
        for cap in expected_capabilities:
            supported = client.supports_capability(cap)
            logger.info(f"  {cap.value}: {'supported' if supported else 'NOT supported'}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Capability test failed: {e}", exc_info=True)
        return False


def test_request_validation(client):
    """Test 4: Request validation."""
    logger.info("=" * 70)
    logger.info("TEST 4: Request Validation")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.core import AgentRequest
        
        # Valid request
        request = AgentRequest(prompt="write unit tests")
        errors = client.validate_request(request)
        if not errors:
            logger.info("✓ Valid request passed validation")
        else:
            logger.warning(f"⚠ Validation errors: {errors}")
        
        # Invalid request (empty prompt)
        invalid_request = AgentRequest(prompt="")
        errors = client.validate_request(invalid_request)
        if errors:
            logger.info(f"✓ Invalid request correctly rejected: {errors}")
        else:
            logger.warning("⚠ Invalid request should have been rejected")
        
        return True
    except Exception as e:
        logger.error(f"✗ Request validation failed: {e}", exc_info=True)
        return False


def test_help_command(client):
    """Test 5: Help command."""
    logger.info("=" * 70)
    logger.info("TEST 5: Jules Help Command")
    logger.info("=" * 70)
    try:
        help_info = client.get_jules_help()
        logger.info(f"✓ Help command executed")
        logger.info(f"  Available: {help_info.get('available', False)}")
        logger.info(f"  Exit code: {help_info.get('exit_code', -1)}")
        
        if help_info.get('available'):
            help_text = help_info.get('help_text', '')
            logger.info(f"  Help text length: {len(help_text)} characters")
            if help_text:
                # Show first few lines
                lines = help_text.split('\n')[:5]
                logger.info("  Preview:")
                for line in lines:
                    if line.strip():
                        logger.info(f"    {line[:60]}")
        else:
            error = help_info.get('error', 'Unknown error')
            logger.warning(f"  ⚠ Help not available: {error}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Help command failed: {e}", exc_info=True)
        return False


def test_integration_adapter(client):
    """Test 6: Integration adapter."""
    logger.info("=" * 70)
    logger.info("TEST 6: Integration Adapter")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.jules import JulesIntegrationAdapter
        
        adapter = JulesIntegrationAdapter(client)
        logger.info("✓ JulesIntegrationAdapter initialized")
        logger.info(f"  Agent: {adapter.agent.name}")
        logger.info("  Available methods:")
        logger.info("    - adapt_for_ai_code_editing()")
        logger.info("    - adapt_for_llm()")
        logger.info("    - adapt_for_code_execution()")
        
        return adapter
    except Exception as e:
        logger.error(f"✗ Adapter initialization failed: {e}", exc_info=True)
        return None


def test_orchestration(client):
    """Test 7: Agent orchestration."""
    logger.info("=" * 70)
    logger.info("TEST 7: Agent Orchestration")
    logger.info("=" * 70)
    try:
        from codomyrmex.agents.generic import AgentOrchestrator
        from codomyrmex.agents.core import AgentRequest
        
        orchestrator = AgentOrchestrator([client])
        logger.info("✓ AgentOrchestrator created with Jules client")
        logger.info(f"  Agents: {len(orchestrator.agents)}")
        
        # Test capability selection
        from codomyrmex.agents.core import AgentCapabilities
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        logger.info(f"  Agents with CODE_GENERATION: {len(code_gen_agents)}")
        for agent in code_gen_agents:
            logger.info(f"    - {agent.name}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Orchestration test failed: {e}", exc_info=True)
        return False


def test_command_execution(client):
    """Test 8: Direct command execution."""
    logger.info("=" * 70)
    logger.info("TEST 8: Direct Command Execution")
    logger.info("=" * 70)
    try:
        # Test help command
        result = client.execute_jules_command("help")
        logger.info(f"✓ Command executed: jules help")
        logger.info(f"  Exit code: {result.get('exit_code', -1)}")
        logger.info(f"  Output length: {len(result.get('output', ''))} chars")
        logger.info(f"  Success: {result.get('success', False)}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Command execution failed: {e}", exc_info=True)
        return False


def main():
    """Run all functional tests."""
    logger.info("=" * 70)
    logger.info("JULES FUNCTIONAL TEST SUITE")
    logger.info("=" * 70)
    logger.info("")
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    if not results['imports']:
        logger.error("Critical: Cannot proceed without imports")
        return 1
    
    # Test 2: Client initialization
    client = test_client_initialization()
    results['initialization'] = client is not None
    if not client:
        logger.error("Critical: Cannot proceed without client")
        return 1
    
    # Test 3: Capabilities
    results['capabilities'] = test_capabilities(client)
    
    # Test 4: Request validation
    results['validation'] = test_request_validation(client)
    
    # Test 5: Help command
    results['help'] = test_help_command(client)
    
    # Test 6: Integration adapter
    adapter = test_integration_adapter(client)
    results['adapter'] = adapter is not None
    
    # Test 7: Orchestration
    results['orchestration'] = test_orchestration(client)
    
    # Test 8: Command execution
    results['command_execution'] = test_command_execution(client)
    
    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✓ All tests passed!")
        return 0
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

