import os
for path in [
    "src/codomyrmex/documentation/docs/modules/llm/mcp_tool_specification.md",
    "src/codomyrmex/documentation/docs/modules/data_visualization/usage_examples.md",
    "src/codomyrmex/llm/README.md",
    "src/codomyrmex/llm/MCP_TOOL_SPECIFICATION.md",
    "src/codomyrmex/llm/ollama/AGENTS.md",
    "src/codomyrmex/data_visualization/USAGE_EXAMPLES.md"
]:
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()

        # for plot_outputs/ -> plot_output/
        content = content.replace("plot_outputs/", "plot_output/")

        # for outputs/ -> output/
        content = content.replace("outputs/", "output/")

        with open(path, "w") as f:
            f.write(content)
print("Updated docs")
