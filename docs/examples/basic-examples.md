# Basic Examples Guide

Documentation for basic single-module examples demonstrating individual Codomyrmex capabilities.

## Overview

Basic examples showcase individual module capabilities without requiring complex multi-module coordination. These examples are ideal for:
- Learning individual module features
- Testing module functionality
- Understanding module APIs
- Quick demonstrations

## Available Examples

### 1. Data Visualization Demo

**File**: `scripts/examples/basic/data-visualization-demo.sh`

**Purpose**: Demonstrates Codomyrmex's data visualization capabilities by creating various types of charts and plots.

**Capabilities Demonstrated**:
- Creating line plots, bar charts, scatter plots
- Different visualization formats (PNG, SVG, HTML)
- Custom styling and color palettes
- Integration with data analysis workflows

**Configuration**: None required (uses default settings)

**Execution**:
```bash
./scripts/examples/basic/data-visualization-demo.sh
```

**Options**:
- `--non-interactive`: Run without user prompts
- `--help`: Show help message

**Expected Output**:
- Generated plots in `scripts/output/data-visualization/`
- Multiple chart types (line, bar, scatter, etc.)
- Styled visualizations with different color palettes

**Duration**: ~3 minutes

**Troubleshooting**:
- If plots fail to generate, check matplotlib installation
- Verify output directory permissions
- Check Python environment has required packages

### 2. Static Analysis Demo

**File**: `scripts/examples/basic/static-analysis-demo.sh`

**Purpose**: Demonstrates static code analysis capabilities including quality checks, security scanning, and complexity analysis.

**Capabilities Demonstrated**:
- Code quality analysis
- Security vulnerability scanning
- Complexity metrics
- Multi-language support
- Report generation

**Configuration**: None required (analyzes current directory by default)

**Execution**:
```bash
./scripts/examples/basic/static-analysis-demo.sh
```

**Options**:
- `--non-interactive`: Run without user prompts
- `--target=PATH`: Specify target directory for analysis
- `--help`: Show help message

**Expected Output**:
- Analysis reports in `scripts/output/static-analysis/`
- Quality metrics and scores
- Security findings
- Complexity analysis results

**Duration**: ~2-5 minutes (depends on codebase size)

**Troubleshooting**:
- Ensure target directory contains code files
- Check that required analysis tools are installed
- Verify Python environment configuration

### 3. Advanced Data Visualization Demo

**File**: `scripts/examples/basic/advanced_data_visualization_demo.sh`

**Purpose**: Demonstrates advanced data visualization features including interactive dashboards, advanced plot types, and complex data transformations.

**Capabilities Demonstrated**:
- Interactive dashboards
- Advanced plot types (heatmaps, 3D plots, etc.)
- Complex data transformations
- Multi-dataset visualizations
- Export to multiple formats

**Configuration**: None required

**Execution**:
```bash
./scripts/examples/basic/advanced_data_visualization_demo.sh
```

**Options**:
- `--non-interactive`: Run without user prompts
- `--help`: Show help message

**Expected Output**:
- Advanced visualizations in `scripts/output/advanced-data-visualization/`
- Interactive HTML dashboards
- Multiple chart types
- Complex data visualizations

**Duration**: ~4 minutes

**Troubleshooting**:
- Check plotly installation for interactive features
- Verify sufficient memory for complex visualizations
- Ensure output directory has write permissions

## Common Configuration

All basic examples share common configuration patterns:

### Output Directory

Examples output to `scripts/output/{example-name}/` by default.

### Environment Setup

Examples automatically:
- Check Python environment
- Verify required modules
- Set up logging
- Create output directories

### Error Handling

All examples:
- Exit on errors (`set -e`)
- Provide error messages
- Clean up on failure
- Log execution details

## Running All Basic Examples

```bash
# Run all basic examples sequentially
for example in scripts/examples/basic/*.sh; do
    echo "Running $(basename $example)..."
    "$example" --non-interactive
done
```

## Expected Outcomes

### Data Visualization Demo

- ✅ Multiple chart files generated
- ✅ Different visualization formats available
- ✅ Styled plots with custom colors
- ✅ Output directory populated

### Static Analysis Demo

- ✅ Analysis reports generated
- ✅ Quality metrics calculated
- ✅ Security findings identified
- ✅ Complexity scores computed

### Advanced Data Visualization Demo

- ✅ Interactive dashboards created
- ✅ Advanced plot types displayed
- ✅ Multiple export formats available
- ✅ Complex visualizations generated

## Troubleshooting Common Issues

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'codomyrmex'`

**Solution**:
```bash
# Install Codomyrmex
pip install -e .
# Or use uv
uv pip install -e .
```

### Permission Denied

**Error**: Permission denied when creating output files

**Solution**:
```bash
# Check directory permissions
chmod -R 755 scripts/output/
# Or run with appropriate permissions
```

### Missing Dependencies

**Error**: Missing required packages

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt
# Or use uv
uv pip install -r requirements.txt
```

## Related Documentation

- [Integration Examples Guide](./integration-examples.md)
- [Data Visualization Module](../../src/codomyrmex/data_visualization/README.md)
- [Static Analysis Module](../../src/codomyrmex/static_analysis/README.md)

