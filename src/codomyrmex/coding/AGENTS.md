# Agent Guidelines - Coding

## Module Overview

Code generation, editing, and transformation utilities.

## Key Classes

- **CodeGenerator** — Generate code from specs
- **CodeEditor** — Edit existing code
- **CodeTransformer** — AST-based transforms
- **DiffApplier** — Apply code diffs

## Agent Instructions

1. **Parse before edit** — Use AST for safe edits
2. **Preserve formatting** — Maintain style
3. **Generate tests** — Create tests with code
4. **Validate output** — Syntax check generated code
5. **Document changes** — Explain transformations

## Common Patterns

```python
from codomyrmex.coding import (
    CodeGenerator, CodeEditor, CodeTransformer, DiffApplier
)

# Generate code
generator = CodeGenerator()
code = generator.generate_function(
    name="calculate_tax",
    params=["amount", "rate"],
    return_type="float",
    docstring="Calculate tax amount"
)

# Edit code
editor = CodeEditor("src/main.py")
editor.add_import("from datetime import datetime")
editor.add_method("MyClass", method_code)
editor.save()

# Transform code
transformer = CodeTransformer()
new_code = transformer.rename_function(code, "old_name", "new_name")
new_code = transformer.add_type_hints(code)

# Apply diffs
applier = DiffApplier()
result = applier.apply(original, diff)
```

## Testing Patterns

```python
# Verify code generation
gen = CodeGenerator()
code = gen.generate_function("foo", ["x"])
assert "def foo(x):" in code

# Verify transformation
transformer = CodeTransformer()
result = transformer.rename_function("def old(): pass", "old", "new")
assert "def new():" in result
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
