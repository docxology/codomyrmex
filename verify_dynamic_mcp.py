"""
Verify Dynamic MCP Tool Discovery.

Checks if tools exposed via @mcp_tool in various modules are correctly
discovered and registered by the MCP Bridge.
"""

import sys
import logging
from codomyrmex.agents.pai.mcp_bridge import get_tool_registry, call_tool

# Configure logging to see discovery debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("codomyrmex")
logger.setLevel(logging.DEBUG)

def verify():
    print("=== Dynamic MCP Discovery Verification ===\n")
    
    # 1. Check Registry
    print("1. Initializing Registry...")
    try:
        registry = get_tool_registry()
        tools = registry.list_tools()
        print(f"Total Tools Found: {len(tools)}")
        print(f"Tools: {', '.join(tools)}\n")
        
        # 2. Verify Specific Dynamic Tools
        expected = [
        # Visualization
        "codomyrmex.create_line_plot",
        "codomyrmex.create_bar_chart",
        "codomyrmex.create_pie_chart",
        "codomyrmex.create_git_branch_diagram",
        "codomyrmex.create_git_workflow_diagram",
        "codomyrmex.create_repository_structure_diagram",
        "codomyrmex.create_commit_timeline_diagram",
        # Terminal
        "codomyrmex.create_ascii_art",
        # LLM
        "codomyrmex.ask",
        "codomyrmex.generate_report",
        # Memory
        "codomyrmex.add_memory",
        "codomyrmex.search_memory",
        # Security
        "codomyrmex.scan_project_security",
        "codomyrmex.security_audit_code",
        # Git Operations
        "codomyrmex.initialize_git_repository",
        "codomyrmex.clone_repository",
        "codomyrmex.create_branch",
        "codomyrmex.commit_changes",
        "codomyrmex.push_changes",
        "codomyrmex.get_commit_history",
        # Coding
        "codomyrmex.execute_code",
        # Analysis
        "codomyrmex.analyze_file",
        "codomyrmex.analyze_project",
        # Documentation
        "codomyrmex.generate_documentation",
    ]      
        
        missing = []
        for name in expected:
            if name in tools:
                print(f"✅ Found: {name}")
                # Check schema
                tool = registry.get(name)
                print(f"   Schema: {tool['schema']['inputSchema'].get('required', [])}")
            else:
                print(f"❌ MISSING: {name}")
                missing.append(name)
                
        if missing:
            print(f"\nFAILED: Missing {len(missing)} tools.")
            sys.exit(1)
            
        # 3. Test Invocation (Dry Run / Safe)
        print("\n3. Testing Invocation (llm.ask - check args)...")
        # We won't actually call LLM due to API key, but we check if handler is callable
        # We can call it with invalid key to verify it runs the function
        
        result = call_tool("codomyrmex.ask", question="Test", model="test-model")
        print(f"Result (Expected Error): {result}")
        
        if "OPENROUTER_API_KEY" in str(result) or "Error" in str(result):
             print("✅ Invocation reached function body.")
        else:
             print("❌ Invocation failed to return expected error.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify()
