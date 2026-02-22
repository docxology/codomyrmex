import os
from codomyrmex.agents.orchestrator import _create_llm_client, AgentSpec

os.environ["ANTHROPIC_API_KEY"] = "fake-api-key"

spec = AgentSpec(identity="reviewer", persona="coder", provider="antigravity")
client = _create_llm_client(spec)

print(f"Client type: {type(client).__name__}")
if hasattr(client, "client"):
    print(f"Inner client type: {type(client.client).__name__}")
    if hasattr(client.client, "_tools"):
        print(f"Registered tools: {len(client.client._tools)}")
