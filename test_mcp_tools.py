from codomyrmex.agents.pai.mcp_bridge import get_skill_manifest, call_tool
from codomyrmex.agents.pai.trust_gateway import trust_all
import json

def test_tools():
    manifest = get_skill_manifest()
    tools = manifest.get("tools", [])
    print(f"Total tools discovered: {len(tools)}")
    tool_names = [t["name"] for t in tools]
    
    # Check for memory_put
    memory_tools = [n for n in tool_names if 'memory' in n]
    print(f"Memory tools found: {memory_tools}")
    
    trust_all()
    
    # Test pai_status
    print("\nTesting pai_status...")
    try:
        status = call_tool("codomyrmex.pai_status")
        print(json.dumps(status, indent=2))
    except Exception as e:
        print(f"Error calling pai_status: {e}")
        
    # Test pai_awareness
    print("\nTesting pai_awareness...")
    try:
        awareness = call_tool("codomyrmex.pai_awareness")
        if isinstance(awareness, dict):
             if "error" in awareness:
                 print(f"Awareness returned error: {awareness['error']}")
             else:
                 print({k: type(v).__name__ for k, v in awareness.items()})
                 if "metrics" in awareness:
                      print("\nAwareness payload length check:")
                      print(f"Missions: {len(awareness.get('missions', []))}")
                      print(f"Projects: {len(awareness.get('projects', []))}")
                      print(f"Tasks: {len(awareness.get('tasks', []))}")
        else:
             print("Awareness was not a dict:", type(awareness))
    except Exception as e:
        print(f"Error calling pai_awareness: {e}")

if __name__ == "__main__":
    test_tools()
