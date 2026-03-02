# Softmax Opt Module -- PAI Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## PAI Algorithm Phase Mapping

### BUILD Phase

**Tools**: `compute_softmax`

- Compute probability distributions from logits during model pipeline construction
- Select appropriate softmax variant (standard, log, online) for the use case
- Apply temperature scaling for inference-time control

### VERIFY Phase

**Tools**: `compute_softmax`

- Validate numerical stability with extreme input values
- Check sum-to-one property across different input distributions
- Compare online vs standard softmax correctness (max error < 1e-6)
- Verify entropy values are within expected bounds

### EXECUTE Phase

**Tools**: `compute_softmax`

- Run softmax computations as part of agent inference workflows
- Provide probability distributions to downstream decision-making modules

## MCP Tool Summary

| Tool | Category | Trust Required |
|------|----------|---------------|
| `compute_softmax` | softmax_opt | OBSERVED |

## Integration Notes

- This module is compute-only with no side effects (no file I/O, no network)
- All tools are safe (read-only computation) and require no elevated trust
- NumPy is the only dependency (part of core codomyrmex dependencies)
- The online softmax variant is particularly relevant for Flash Attention implementations
