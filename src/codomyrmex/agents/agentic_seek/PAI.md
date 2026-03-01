# PAI Integration - agenticSeek

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.agentic_seek`

## PAI Context

The agenticSeek integration provides PAI with access to a fully-local autonomous agent system. Key PAI-relevant capabilities:

### Agent Routing

- Automatic task classification into specialised agent types
- Complexity estimation (LOW/HIGH) for workload planning
- Deterministic heuristic routing (no ML dependency)

### Code Execution

- Multi-language support (Python, C, Go, Java, Bash)
- Code block extraction from LLM responses
- Structured execution results with success/failure tracking

### Task Planning

- JSON-based multi-step plan decomposition
- Dependency graph validation with cycle detection
- Topological execution ordering

### Browser Automation

- URL and form field extraction from text
- Search and navigation prompt construction
- Privacy-first: all browsing via local SearxNG

## Integration Points

- **Dispatch**: agenticSeek's planner maps to PAI dispatch workflows
- **Memory**: `AgenticSeekMemoryEntry` aligns with PAI conversation persistence
- **Config**: `AgenticSeekConfig` provides typed access to all settings

## Security Notes

- All execution is local (no cloud API calls unless explicitly configured)
- Subprocess execution is sandboxed by working directory configuration
- Docker isolation available for full agenticSeek deployment
