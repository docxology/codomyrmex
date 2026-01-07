# Documentation Maintenance Guide

This guide explains the Codomyrmex documentation maintenance system designed to prevent errors from accumulating across versions.

## Overview

Codomyrmex uses a dual documentation system:
1. **Module-local documentation**: Each module maintains its own documentation files
2. **Aggregated documentation**: Centralized documentation website built from module docs

To prevent documentation drift and maintain quality, we've implemented automated validation systems.

## Validation Systems

### 1. Pre-commit Hooks

A pre-commit hook automatically validates documentation when you commit changes:

```bash
# The hook runs automatically on commit
git add .
git commit -m "Update documentation"
# Hook validates docs and blocks commit if issues found
```

The hook performs:
- Documentation aggregation
- Version consistency validation
- Quality checks
- Freshness validation

### 2. CI/CD Validation

GitHub Actions workflow validates documentation on every push/PR:

```yaml
# .github/workflows/documentation-validation.yml
- Validates documentation structure
- Checks version consistency
- Validates cross-references
- Performs link checking
```

### 3. Manual Validation Tools

Run validation manually using the documentation website script:

```bash
cd src/codomyrmex/documentation

# Validate version consistency
python documentation_website.py validate_docs

# Aggregate documentation
python documentation_website.py aggregate_docs

# Run comprehensive quality check
python scripts/validate_docs_quality.py
```

## Quality Checks Performed

### Structure Validation
- Ensures all modules have required documentation files
- Validates `docs/` directory structure
- Checks for `technical_overview.md`
- Verifies `tutorials/` directory exists and has content

### Version Consistency
- Compares source vs aggregated documentation
- Validates CHANGELOG.md format consistency
- Checks file modification times
- Detects documentation drift

### Cross-reference Validation
- Validates internal relative links
- Checks for broken references
- Ensures link integrity across modules

### Format Validation
- Validates CHANGELOG.md follows Keep a Changelog format
- Checks for proper version headers
- Ensures "Unreleased" sections exist

## Preventing Documentation Drift

### The Problem
Without proper controls, documentation drift occurs when:
- Source documentation is updated but aggregation is forgotten
- Version numbers get out of sync
- Links become broken over time
- Format inconsistencies accumulate

### The Solution

Our multi-layered approach prevents drift:

1. **Automated Aggregation**: Pre-commit hooks ensure docs are always aggregated
2. **Version Validation**: CI/CD catches version mismatches
3. **Freshness Checks**: Modification time comparison detects stale docs
4. **Quality Gates**: Comprehensive validation prevents common issues

## Best Practices

### For Module Maintainers

1. **Always update CHANGELOG.md** when making changes:
   ```markdown
   ## [Unreleased]

   ### Added
   - New feature description

   ### Changed
   - Modified behavior description

   ### Fixed
   - Bug fix description
   ```

2. **Keep documentation current** with code changes

3. **Test documentation locally** before committing:
   ```bash
   cd src/codomyrmex/documentation
   python documentation_website.py validate_docs
   ```

4. **Use relative links** for cross-references within modules

### For Documentation Maintainers

1. **Run full validation** before releases:
   ```bash
   cd src/codomyrmex/documentation
   python scripts/validate_docs_quality.py
   ```

2. **Update aggregated docs** when restructuring:
   ```bash
   python documentation_website.py aggregate_docs
   ```

3. **Review validation failures** carefully

4. **Keep sidebar navigation** synchronized with new modules

## Troubleshooting

### Common Issues

#### "Documentation validation failed!"
- Check that all required files exist in your module
- Ensure CHANGELOG.md follows the correct format
- Verify aggregated docs are up to date

#### "Module X: Missing required file Y"
- Create the missing documentation file
- Follow the established format from other modules

#### "Broken relative link"
- Fix the link path
- Ensure target file exists
- Use relative paths from the source file location

#### "Documentation drift detected"
- Run aggregation: `python documentation_website.py aggregate_docs`
- Commit the updated aggregated files

### Validation Scripts

#### Quick Validation
```bash
cd src/codomyrmex/documentation
python documentation_website.py validate_docs
```

#### Comprehensive Validation
```bash
cd src/codomyrmex/documentation
python scripts/validate_docs_quality.py
```

#### Manual Aggregation
```bash
cd src/codomyrmex/documentation
python documentation_website.py aggregate_docs
```

## Integration with Development Workflow

### Feature Development
1. Develop feature
2. Update module documentation
3. Update CHANGELOG.md
4. Commit (pre-commit hook validates)
5. Push (CI/CD validates)

### Documentation Updates
1. Update source documentation
2. Run validation locally
3. Commit (hook aggregates and validates)
4. CI/CD performs final checks

### Release Process
1. Run comprehensive validation
2. Update version numbers in pyproject.toml
3. Update CHANGELOG.md with release notes
4. Build and deploy documentation website

## Configuration

### Customizing Validation

The validation system is configurable through the `DocumentationValidator` class in `scripts/validate_docs_quality.py`:

```python
# Add custom file patterns
self.required_files = ['README.md', 'CHANGELOG.md', 'CUSTOM_FILE.md']

# Modify validation rules
def custom_validation(self) -> List[str]:
    # Your custom validation logic
    pass
```

### Hook Configuration

Modify `scripts/git-hooks/pre-commit` to adjust validation behavior:

```bash
# Add custom validation commands
python3 custom_validation_script.py
```

## Monitoring and Maintenance

### Validation Reports

The validation system provides detailed reports:

```
✓ All documentation validation checks passed!

# Or detailed error report:
✗ Found 3 documentation issues:
  STRUCTURE ISSUES:
    - Module ai_code_editing: Missing docs/technical_overview.md
  VERSION CONSISTENCY ISSUES:
    - Module data_visualization: CHANGELOG.md differs between source and aggregated docs
```

### Regular Maintenance Tasks

1. **Weekly**: Review validation reports from CI/CD
2. **Monthly**: Run comprehensive validation across all modules
3. **Quarterly**: Review and update documentation standards
4. **Pre-release**: Always run full validation

## Conclusion

This comprehensive validation system ensures that:

- Documentation stays synchronized with code
- Version consistency is maintained
- Quality standards are enforced
- Errors cannot accumulate undetected
- The documentation website always reflects current state

By integrating validation into the development workflow, we prevent documentation from becoming outdated or inconsistent across versions.


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
