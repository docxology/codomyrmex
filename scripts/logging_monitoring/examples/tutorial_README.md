# Logging Monitoring Tutorial

**Tutorial**: Step-by-step guide to logging and monitoring

## Overview

This interactive tutorial walks you through Codomyrmex logging and monitoring functionality step by step. Learn how to set up centralized logging, create hierarchical loggers, use different log levels, implement structured logging, handle errors properly, and monitor performance.

## What You'll Learn

- **Centralized Logging**: Set up and configure the logging system
- **Logger Hierarchy**: Create and manage loggers for different components
- **Log Levels**: Understand when to use DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Structured Logging**: Add contextual data to log messages
- **Error Handling**: Properly log exceptions and errors
- **Performance Monitoring**: Track application performance through logs

## Tutorial Steps

### Step 1: Basic Logging Setup
Learn how to import and initialize the logging system with default configuration.

**Key Concepts**:
- Importing logging modules
- Setting up the logging system
- Creating your first logger

### Step 2: Creating Loggers
Understand how to create loggers for different parts of your application.

**Key Concepts**:
- Hierarchical logger naming
- Logger inheritance
- Component-specific logging

### Step 3: Log Levels and Their Use Cases
Master the different log levels and when to use each one.

**Key Concepts**:
- DEBUG: Detailed diagnostics
- INFO: General operational information
- WARNING: Unexpected but non-critical events
- ERROR: Failures requiring attention
- CRITICAL: System-threatening errors

### Step 4: Structured Logging with Context
Learn how to add structured data to log messages for better analysis.

**Key Concepts**:
- Using the `extra` parameter
- Adding contextual information
- Structured data for log analysis

### Step 5: Error Handling and Exception Logging
Properly handle and log errors and exceptions.

**Key Concepts**:
- Exception logging with stack traces
- Error context and metadata
- Different error severity levels

### Step 6: Performance Logging and Monitoring
Track application performance through logging.

**Key Concepts**:
- Timing operations
- Performance metrics
- Resource usage logging

## Running the Tutorial

### Interactive Mode (Recommended)

```bash
cd examples/logging_monitoring
python tutorial_step_by_step.py
```

Choose "Step-by-step" mode for guided learning with explanations and prompts.

### Automated Mode

```bash
cd examples/logging_monitoring
python tutorial_step_by_step.py  # Choose "Run all" when prompted
```

Runs all steps automatically without user interaction.

### Non-Interactive Mode

Modify `tutorial_config.yaml`:
```yaml
tutorial:
  interactive: false
```

Then run:
```bash
python tutorial_step_by_step.py
```

## Configuration

The tutorial can be configured via `tutorial_config.yaml`:

```yaml
tutorial:
  interactive: true          # Enable user prompts
  verbose: true             # Detailed output
  save_progress: false      # Resume capability

logging:
  level: INFO               # Tutorial log level
  file: logs/tutorial.log   # Log file location

error_handling:
  continue_on_failure: true # Don't stop on step failures
  max_retries: 3           # Retry failed steps
```

## Expected Output

After completing the tutorial, you should see:

```
================================================================================
TUTORIAL COMPLETED
================================================================================
Steps completed: 6/6
Completion rate: 100.0%
Total duration: 45.23 seconds
Average step duration: 7.54 seconds
🎉 Congratulations! You completed the entire tutorial!
```

## Learning Outcomes

By the end of this tutorial, you will be able to:

1. **Set up centralized logging** in any Python application
2. **Create hierarchical loggers** for different application components
3. **Choose appropriate log levels** for different types of messages
4. **Implement structured logging** with contextual data
5. **Handle errors and exceptions** properly in logs
6. **Monitor application performance** through logging

## Code Examples

### Basic Logging Setup
```python
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Setup logging
setup_logging()

# Create logger
logger = get_logger('myapp')
logger.info("Application started")
```

### Structured Logging
```python
logger.info("User login successful", extra={
    'user_id': 'user_12345',
    'ip_address': '192.168.1.100',
    'timestamp': time.time()
})
```

### Error Logging
```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure Codomyrmex is properly installed
- Check Python path includes the src directory
- Verify all dependencies are installed

**Permission Errors**
- Check write permissions for log directories
- Ensure the user can create log files
- Verify directory paths exist

**Configuration Errors**
- Validate YAML syntax in config files
- Check file paths are correct
- Ensure required configuration keys are present

### Getting Help

If you encounter issues:

1. Check the tutorial output for specific error messages
2. Review the configuration file for syntax errors
3. Ensure all prerequisites are met
4. Check the main logging example for reference
5. Review the Codomyrmex logging documentation

## Prerequisites

- Python 3.8+
- Codomyrmex package installed
- Basic understanding of Python logging concepts
- Familiarity with JSON data structures

## Files

- `tutorial_step_by_step.py` - Main tutorial implementation
- `tutorial_config.yaml` - Tutorial configuration
- `tutorial_README.md` - This documentation
- `output/tutorial_logging_results.json` - Tutorial results

## Related Resources

- **[Basic Example](example_basic.py)** - Comprehensive logging example
- **[Logging Documentation](../../../src/codomyrmex/logging_monitoring/README.md)** - Full API documentation
- **[Configuration Guide](../../docs/)** - Documentation site
- **[Best Practices](../BEST_PRACTICES.md)** - Example best practices

## Next Steps

After completing this tutorial:

1. **Apply logging to your projects** using the patterns learned
2. **Explore advanced logging features** in the basic example
3. **Set up centralized logging** in your development environment
4. **Implement structured logging** in your applications
5. **Monitor performance** using logging techniques

## Contributing

To improve this tutorial:

1. Report issues or unclear steps
2. Suggest additional examples or use cases
3. Propose better explanations or code samples
4. Submit pull requests with improvements

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
