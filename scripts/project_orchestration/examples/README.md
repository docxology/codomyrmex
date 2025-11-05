# Codomyrmex Project Orchestration Examples

This directory contains comprehensive examples demonstrating the Project Orchestration capabilities of Codomyrmex. These examples show how multiple Codomyrmex modules work together to create powerful analysis and improvement workflows.

## Overview

The Project Orchestration module enables you to:

- **Chain workflows** across multiple Codomyrmex modules
- **Coordinate complex analysis pipelines** with AI, static analysis, visualization, and Git operations
- **Monitor performance** across all operations
- **Manage projects** with templates and automated workflows
- **Generate comprehensive reports** combining insights from all modules

## Examples Included

### 1. Comprehensive Workflow Demo (`comprehensive_workflow_demo.py`)

A complete demonstration showing how to:
- Perform static code analysis
- Generate AI-powered recommendations
- Create data visualizations
- Run improvement workflows
- Monitor performance
- Generate comprehensive reports

**Features Demonstrated:**
- ✅ Multi-module integration
- ✅ AI-driven code improvement
- ✅ Performance monitoring
- ✅ Automated report generation
- ✅ Error handling and recovery
- ✅ Results visualization

## Quick Start

### Prerequisites

1. **Install Codomyrmex** with orchestration support:
   ```bash
   # Install from source with development dependencies
   pip install -e .
   
   # Or install specific orchestration requirements
   pip install -r requirements.txt
   ```

2. **Set up environment** (optional):
   ```bash
   export CODOMYRMEX_ORCHESTRATION_DIR=./orchestration
   export CODOMYRMEX_MAX_WORKERS=8
   ```

3. **Verify installation**:
   ```bash
   python -c "import codomyrmex; print('✅ Codomyrmex installed')"
   ```

### Running the Comprehensive Demo

#### Option 1: Use with your own project
```bash
# Analyze your existing project
python comprehensive_workflow_demo.py --project-path ./your_project --output-dir ./results

# With verbose logging
python comprehensive_workflow_demo.py --project-path ./your_project --verbose
```

#### Option 2: Use with auto-generated sample project
```bash
# Create and analyze a sample project
python comprehensive_workflow_demo.py --create-sample-project

# This will:
# 1. Create a sample Python project with intentional issues
# 2. Run comprehensive analysis workflows
# 3. Generate AI-powered improvement suggestions
# 4. Create visualizations and reports
```

#### Option 3: Quick demo with defaults
```bash
# Simplest usage - creates sample project and analyzes it
python comprehensive_workflow_demo.py --create-sample-project --verbose
```

## What the Demo Does

### Workflow 1: Comprehensive Code Analysis
1. **Static Analysis** - Analyzes code quality, security, complexity
2. **Git Analysis** - Reviews repository history and development patterns
3. **Data Visualization** - Creates quality metrics charts and dashboards
4. **AI Recommendations** - Generates improvement suggestions using AI
5. **Report Generation** - Creates comprehensive analysis reports

### Workflow 2: AI-Driven Code Improvement  
1. **Initial Assessment** - Baseline code quality analysis
2. **Improvement Planning** - AI-generated step-by-step improvement plan
3. **Simulated Improvements** - Shows before/after quality comparisons
4. **Impact Analysis** - Calculates ROI and time savings
5. **Progress Tracking** - Monitors improvement metrics

### Workflow 3: Performance Monitoring
1. **Operation Tracking** - Monitors execution times across all workflows
2. **Resource Usage** - Tracks memory and CPU utilization
3. **Performance Analytics** - Provides optimization recommendations
4. **Bottleneck Identification** - Identifies slow operations

## Expected Output

After running the demo, you'll find these files in your output directory:

### Analysis Results
- `comprehensive_report.json` - Detailed analysis results
- `improvement_report.json` - Code improvement analysis
- `demo_summary.json` - Overall workflow summary

### AI-Generated Content
- `ai_recommendations.md` - AI-powered improvement suggestions
- `improvement_plan.md` - Detailed step-by-step improvement plan

### Visualizations
- `quality_metrics.png` - Code quality metrics chart
- `improvement_comparison.png` - Before/after comparison
- `project_dashboard.html` - Interactive project dashboard

### Logs and Monitoring
- `workflow_demo.log` - Detailed execution log
- `performance_stats.json` - Performance monitoring data

## Customization

### Using with Your Project Structure

The demo is designed to work with any Python project structure. For best results, ensure your project has:

- **Python source files** (`.py`) for static analysis
- **Git repository** for development pattern analysis
- **README or documentation** for context
- **Requirements or setup files** for dependency analysis

### Modifying Workflows

You can customize the workflows by:

1. **Editing the demo script** to add/remove analysis steps
2. **Configuring AI providers** (OpenAI, Anthropic, local models)
3. **Adjusting analysis parameters** (security focus, complexity thresholds)
4. **Customizing output formats** (JSON, HTML, PDF reports)

### Example Customizations

```python
# Focus on security analysis
analysis_result = modules['static_analyzer'].analyze_code_quality(
    code_path=project_path,
    include_security=True,
    security_focus=True,
    include_compliance_check=True
)

# Use different AI provider
ai_result = modules['ai_helper'].generate_code_snippet(
    prompt=improvement_prompt,
    language="python",
    provider="anthropic",  # or "openai", "local"
    model="claude-3"
)

# Create custom visualizations
custom_chart = modules['data_visualizer'].create_custom_chart(
    chart_type="radar",
    data=analysis_metrics,
    style="modern",
    output_path="./custom_analysis.png"
)
```

## Integration with CLI

The orchestration examples integrate seamlessly with the Codomyrmex CLI:

```bash
# Run through CLI
codomyrmex workflow run comprehensive-analysis --params='{"project_path": "./your_project"}'

# Check workflow status
codomyrmex workflow list

# Monitor system performance
codomyrmex status --performance
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Module Import Errors
```bash
# Ensure proper installation
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 2. AI Provider Configuration
```bash
# Set API keys
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Or use local models
export AI_PROVIDER="local"
export LOCAL_MODEL_PATH="/path/to/model"
```

#### 3. Performance Issues
```bash
# Reduce parallel workers
export CODOMYRMEX_MAX_WORKERS=4

# Use resource-limited mode
python comprehensive_workflow_demo.py --project-path ./small_project
```

#### 4. Visualization Creation Failures
```bash
# Install visualization dependencies
pip install matplotlib seaborn plotly

# Check display environment
export MPLBACKEND=Agg  # For headless environments
```

### Debug Mode

Run with maximum verbosity for troubleshooting:

```bash
python comprehensive_workflow_demo.py \
    --create-sample-project \
    --verbose \
    --project-path ./debug_project \
    --output-dir ./debug_results
```

## Advanced Usage

### Running Multiple Projects in Parallel

```python
import concurrent.futures
from pathlib import Path

projects = [
    "./project1",
    "./project2", 
    "./project3"
]

def analyze_project(project_path):
    from comprehensive_workflow_demo import WorkflowDemoRunner
    
    runner = WorkflowDemoRunner(
        project_path=project_path,
        output_dir=f"./results/{Path(project_path).name}"
    )
    
    return runner.run_comprehensive_analysis_workflow()

# Analyze all projects in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(analyze_project, projects))

print(f"Analyzed {len([r for r in results if r['success']])} projects successfully")
```

### Custom Workflow Definition

```python
from comprehensive_workflow_demo import WorkflowDemoRunner

class CustomWorkflowRunner(WorkflowDemoRunner):
    def run_security_focused_workflow(self):
        """Custom workflow focusing on security analysis."""
        # Your custom workflow implementation
        pass
    
    def run_performance_optimization_workflow(self):
        """Custom workflow for performance optimization."""
        # Your custom workflow implementation
        pass
```

## Contributing

To contribute new orchestration examples:

1. **Follow the pattern** established in `comprehensive_workflow_demo.py`
2. **Include error handling** and graceful fallbacks
3. **Add comprehensive logging** and status reporting
4. **Create documentation** explaining the workflow
5. **Add tests** in the test directory
6. **Update this README** with your new example

### Example Template

```python
#!/usr/bin/env python3
"""
New Orchestration Example - Description

This example demonstrates [specific capability].
"""

import sys
import os
from pathlib import Path

# Add imports and setup following the established pattern

class NewWorkflowRunner:
    """Runs the new workflow demonstration."""
    
    def __init__(self, project_path: str, output_dir: str):
        # Setup following the established pattern
        pass
    
    def run_new_workflow(self):
        """Run the new workflow."""
        # Implementation with proper error handling
        pass

def main():
    """Main function following the established CLI pattern."""
    # CLI argument parsing and execution
    pass

if __name__ == "__main__":
    main()
```

## Resources

- **Main Documentation**: `../../docs/modules/overview.md`
- **API Reference**: `../../docs/reference/api.md`
- **Orchestration Specification**: `../src/codomyrmex/project_orchestration/API_SPECIFICATION.md`
- **Usage Examples**: `../src/codomyrmex/project_orchestration/USAGE_EXAMPLES.md`

---

**Note**: These examples are designed to showcase the full capabilities of Codomyrmex Project Orchestration. Start with the comprehensive demo and then explore customization options based on your specific needs.

For support or questions, please check the main project documentation or open an issue in the repository.
