# Codomyrmex Agents — container_optimization

## Operating Contracts
- **Zero-Mock Policy**: Strictly avoid mocks, patches, and magic-mock objects in tests. Use real Docker environments or functional alternatives.
- **Documentation First**: Maintain parity between `SPEC.md`, `README.md`, and the implementation.
- **Performance**: Optimization operations should be efficient and provide actionable feedback.

## Active Tasks
- [x] Module initialization
- [x] Implement `ContainerOptimizer`
- [x] Implement `ResourceTuner`
- [x] Add zero-mock tests
- [x] Create orchestrator script
- [x] Expose functionality via `mcp_tools.py` using `@mcp_tool`
- [x] Add zero-mock tests for `mcp_tools.py`
