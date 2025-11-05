# ⚠️ Examples Directory - MIGRATED

**This directory has been reorganized into the `scripts/` directory structure.**

## New Locations

All examples have been moved to organized locations in `scripts/`:

### Example Scripts
- **Basic Examples**: `scripts/examples/basic/`
- **Integration Examples**: `scripts/examples/integration/`
- **Orchestration Examples**: `scripts/project_orchestration/examples/`

### Integration Scripts
- **Ollama Integration**: `scripts/ollama_integration/`
- **Fabric Integration**: `scripts/fabric_integration/`

### Development Utilities
- **Development Scripts**: `scripts/development/`
  - `run_all_examples.sh` - Run all examples
  - `test_examples.sh` - Test all examples
  - `select_example.sh` - Interactive example selector
  - `check_prerequisites.sh` - Prerequisites checker
  - `example_usage.py` - Basic usage examples

### Documentation
- **Advanced Orchestrators Guide**: `scripts/docs/advanced_orchestrators_guide.md`
- **Orchestrator Status Report**: `scripts/docs/orchestrator_status_report.md`

## Quick Start

```bash
# Check prerequisites
./scripts/development/check_prerequisites.sh

# Run a basic example
./scripts/examples/basic/data-visualization-demo.sh

# Run all examples
./scripts/development/run_all_examples.sh

# Test all examples
./scripts/development/test_examples.sh
```

## Migration Summary

All examples have been reorganized into the `scripts/` directory to:
- ✅ Better align with the modular script structure
- ✅ Improve discoverability and organization
- ✅ Unify examples with orchestration scripts
- ✅ Maintain clear separation of concerns

## Output

Generated output files remain in `examples/output/` at the project root (unchanged).

---

**See `scripts/examples/README.md` for the complete examples guide.**
