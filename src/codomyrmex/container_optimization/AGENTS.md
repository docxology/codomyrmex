# Codomyrmex Agents — container_optimization

## Operating Contracts
- **Zero-Mock Policy**: Strictly avoid mocks, patches, and magic-mock objects in tests. Use real Docker environments or functional alternatives.
- **Documentation First**: Maintain parity between `SPEC.md`, `README.md`, and the implementation.
- **Performance**: Optimization operations should be efficient and provide actionable feedback.
- **MCP Tools**: Tools must be registered via the `@mcp_tool` decorator in `mcp_tools.py` for auto-discovery.

## Active Tasks
- [x] Module initialization
- [x] Implement `ContainerOptimizer`
- [x] Implement `ResourceTuner`
- [x] Add zero-mock tests
- [x] Create orchestrator script
