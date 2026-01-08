# Tutorial Template

**Template For**: Creating step-by-step tutorial examples

## Overview

This template provides a structured approach for creating interactive, educational tutorial examples that guide users through Codomyrmex module functionality step by step.

## Template Structure

### Core Components

1. **TutorialStep Class**
   - Represents individual tutorial steps
   - Includes explanation, code, expected output, and hints
   - Supports interactive execution with error handling

2. **Tutorial Class**
   - Manages the complete tutorial workflow
   - Tracks progress and completion
   - Provides comprehensive results and analytics

3. **Configuration**
   - YAML-based configuration for tutorial settings
   - Support for interactive/non-interactive modes
   - Performance monitoring and error handling options

### Key Features

- **Interactive Learning**: Step-by-step guidance with user prompts
- **Error Recovery**: Comprehensive error handling with retry mechanisms
- **Progress Tracking**: Detailed completion metrics and analytics
- **Flexible Configuration**: Customizable settings for different learning styles
- **Comprehensive Logging**: Full audit trail of tutorial execution

## Usage

### Creating a New Tutorial

1. Copy the template files:
   ```bash
   cp tutorial_template.py examples/{module}/tutorial_step_by_step.py
   cp tutorial_template_config.yaml examples/{module}/tutorial_config.yaml
   cp tutorial_template_README.md examples/{module}/tutorial_README.md
   ```

2. Customize the template:
   - Replace `{ModuleName}` with actual module name
   - Replace `{module}` with module identifier
   - Update imports and function calls
   - Modify tutorial steps for specific module

3. Update the `create_steps()` method:
   - Add module-specific steps
   - Include realistic code examples
   - Provide helpful hints and explanations
   - Define expected outputs

### Configuration Options

```yaml
tutorial:
  interactive: true          # Enable user prompts
  verbose: true             # Detailed output
  save_progress: false      # Resume capability

module:
  name: "Custom Module"    # Display name
  demo_mode: true          # Use mock data
  enable_advanced: false   # Advanced features

error_handling:
  continue_on_failure: true # Don't stop on errors
  max_retries: 3           # Retry failed steps
  retry_delay: 1.0         # Delay between retries
```

## Tutorial Flow

### 1. Initialization
- Load configuration
- Setup logging
- Initialize tutorial state

### 2. Step Execution
- Display step information
- Show code examples
- Execute code with error handling
- Validate results
- Provide feedback

### 3. Progress Tracking
- Track completed/failed steps
- Calculate completion metrics
- Generate performance analytics

### 4. Results Summary
- Comprehensive completion report
- Performance statistics
- Recommendations for improvement

## Step Structure

Each tutorial step should include:

```python
TutorialStep(
    number=1,
    title="Descriptive Title",
    explanation="Clear explanation of what this step teaches",
    code="""# Executable code example
result = function_call()
print(f"Result: {result}")""",
    expected_output="Result: expected_value",
    hints=[
        "Helpful tip 1",
        "Helpful tip 2",
        "Troubleshooting advice"
    ]
)
```

## Error Handling

The template includes comprehensive error handling:

- **Step-Level Errors**: Individual step failures with retry logic
- **Tutorial-Level Errors**: Graceful tutorial termination
- **Configuration Errors**: Fallback to default settings
- **Import Errors**: Clear error messages with troubleshooting tips

## Analytics and Reporting

The template provides detailed analytics:

- **Completion Metrics**: Steps completed vs total steps
- **Performance Data**: Execution time per step and total
- **Error Statistics**: Failed steps and error types
- **Progress Tracking**: Detailed step-by-step results

## Best Practices

### Tutorial Design
- Start with basic concepts, progress to advanced
- Include realistic, copy-pasteable code examples
- Provide helpful hints without giving away solutions
- Test tutorials in both interactive and automated modes

### Code Quality
- Use clear, readable code examples
- Include proper error handling in examples
- Document all configuration options
- Follow consistent naming conventions

### User Experience
- Provide clear progress indicators
- Include encouraging success messages
- Offer helpful error messages and hints
- Support different learning paces

## Integration with Examples

Tutorials complement basic examples by:

- **Teaching Concepts**: Explain why and how, not just what
- **Guided Learning**: Step-by-step progression through complexity
- **Interactive Experience**: User engagement and feedback
- **Reference Material**: Quick refreshers for experienced users

## Testing and Validation

### Automated Testing
- Run tutorials in non-interactive mode
- Validate step completion and results
- Check error handling paths
- Verify configuration loading

### Manual Testing
- Test interactive mode thoroughly
- Validate user experience and flow
- Check error recovery mechanisms
- Verify tutorial completion logic

## File Structure

```
examples/{module}/
├── tutorial_step_by_step.py     # Main tutorial implementation
├── tutorial_config.yaml         # Tutorial configuration
├── tutorial_README.md           # Tutorial documentation
└── output/
    └── tutorial_results.json    # Execution results
```

## Related Documentation

- **[Basic Examples](../README.md)** - Standard example format
- **[Module Documentation](../../src/codomyrmex/{{module}}/ <!-- replace with actual module name -->)** - Detailed API docs
- **[Testing Framework](../../../src/codomyrmex/tests)** - Unit test references
