# Maintenance Scripts

This directory contains scripts for maintaining code quality and project structure.

## Scripts

- **`add_logging.py`** - Automatically injects logging statements across modules following project patterns
- **`fix_imports_simple.py`** - Performs basic import statement cleanup and optimization (sorting and organization)
- **`fix_imports.py`** - Advanced import management including unused import detection and circular import analysis
- **`fix_syntax_errors.py`** - Detects and automatically repairs common syntax errors in Python files

## Usage

### Adding Logging

```bash
# Add logging to a specific module
python scripts/maintenance/add_logging.py --file src/codomyrmex/module_name.py

# Add logging to an entire directory
python scripts/maintenance/add_logging.py --path src/codomyrmex/some_module/

# Dry run to see what would be changed
python scripts/maintenance/add_logging.py --dry-run --path src/codomyrmex/
```

### Fixing Imports

```bash
# Simple import sorting and organization
python scripts/maintenance/fix_imports_simple.py --path src/codomyrmex/

# Advanced import analysis (detects unused imports, missing imports, circular imports)
python scripts/maintenance/fix_imports.py --path src/codomyrmex/

# Fix imports in a single file
python scripts/maintenance/fix_imports_simple.py --file src/codomyrmex/specific_file.py
```

### Fixing Syntax Errors

```bash
# Check and fix syntax errors in a directory
python scripts/maintenance/fix_syntax_errors.py --path src/codomyrmex/

# Check a single file for syntax errors
python scripts/maintenance/fix_syntax_errors.py --file src/codomyrmex/problematic_file.py

# Dry run to see what would be fixed
python scripts/maintenance/fix_syntax_errors.py --dry-run --path src/codomyrmex/
```

## Integration with Makefile

All these scripts can be run via the project's Makefile:

```bash
# Run all maintenance scripts
make maintenance

# Or run individual ones
make add-logging
make fix-imports
make fix-syntax
```

## Notes

- Always run with `--dry-run` first to see what changes would be made
- These scripts are designed to be safe and non-destructive
- Changes are applied in-place, so make sure you have backups or use version control
- The scripts respect Python coding standards and the project's style guide
