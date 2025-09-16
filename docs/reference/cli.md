# CLI Reference

This document provides a complete reference for all Codomyrmex command-line interface (CLI) commands and options.

## 📋 Overview

The Codomyrmex CLI provides convenient access to all major functionality through the `codomyrmex` command. The CLI is organized into logical subcommands for different operations.

### Installation Verification

```bash
# Check if CLI is properly installed
codomyrmex --version

# Get basic help
codomyrmex --help
```

## 🔧 Core Commands

### **🎯 NEW: Orchestration Commands**

The following commands are part of the new Project Orchestration system:

### **`codomyrmex status`**
**NEW!** Display comprehensive system status with performance monitoring.

```bash
codomyrmex status [OPTIONS]

Options:
  --performance, -p    Enable performance monitoring display
  --modules, -m        Show detailed module status
  --resources, -r      Display resource usage information
  --json              Output in JSON format

Examples:
  codomyrmex status                    # Basic system status
  codomyrmex status --performance      # Status with performance metrics
  codomyrmex status --resources        # Include resource usage
```

### **`codomyrmex workflow`**
**NEW!** Manage and execute multi-module workflows.

```bash
codomyrmex workflow <action> [OPTIONS]

Actions:
  list                List all available workflows
  run <name>          Execute a specific workflow
  create <name>       Create a new workflow (interactive)

Options for 'run':
  --params, -p <json>  JSON parameters for the workflow
  --async, -a          Run workflow asynchronously
  --timeout, -t <sec>  Set workflow timeout in seconds

Options for 'create':
  --template <name>    Base workflow on existing template
  --interactive, -i    Use interactive creation mode

Examples:
  codomyrmex workflow list                                    # List workflows
  codomyrmex workflow run ai-analysis --params='{"path": "./src"}'  # Run workflow
  codomyrmex workflow create code-review --template basic     # Create workflow
```

### **`codomyrmex ai`**
**NEW!** AI-powered code operations.

```bash
codomyrmex ai <action> [OPTIONS]

Actions:
  generate <prompt>           Generate code from natural language
  refactor <file> <instruction>  Refactor existing code

Options for 'generate':
  --language, -l <lang>      Programming language (default: python)
  --provider <provider>      AI provider (openai, anthropic, google)
  --output, -o <file>        Save output to file

Options for 'refactor':
  --backup, -b              Create backup before refactoring
  --interactive, -i          Interactive refactoring mode

Examples:
  codomyrmex ai generate "Create a REST API endpoint for user management" --language python
  codomyrmex ai refactor main.py "Add error handling and logging"
```

### **`codomyrmex analyze`**
**NEW!** Code analysis operations.

```bash
codomyrmex analyze <target> <path> [OPTIONS]

Targets:
  code                 Static code analysis
  git                  Git repository analysis

Options:
  --output, -o <dir>   Output directory for reports
  --format <format>    Report format (json, html, markdown)
  --include <types>    Analysis types to include
  --exclude <types>    Analysis types to exclude

Examples:
  codomyrmex analyze code ./src --output ./reports    # Analyze code
  codomyrmex analyze git --repo ./project             # Analyze git history
```

### **`codomyrmex build`**
**NEW!** Build and synthesis operations.

```bash
codomyrmex build <action> [OPTIONS]

Actions:
  project             Build entire project

Options:
  --config, -c <file>  Build configuration file
  --output, -o <dir>   Output directory
  --parallel, -j <n>   Number of parallel jobs

Examples:
  codomyrmex build project --config build.json       # Build with config
```

### **`codomyrmex module`**
**NEW!** Module-specific operations.

```bash
codomyrmex module <action> <name> [OPTIONS]

Actions:
  test                Run module tests
  demo                Run module demonstration

Options:
  --verbose, -v       Verbose output
  --coverage          Generate coverage report (for tests)

Examples:
  codomyrmex module test data_visualization           # Test module
  codomyrmex module demo ai_code_editing              # Run demo
```

### **`codomyrmex shell`**
**NEW!** Launch interactive shell with all modules loaded.

```bash
codomyrmex shell [OPTIONS]

Options:
  --performance, -p    Enable performance monitoring
  --preload <modules>  Preload specific modules

Examples:
  codomyrmex shell                          # Basic interactive shell
  codomyrmex shell --performance            # Shell with perf monitoring
```

### **Global Options**

All commands support these global options:

```bash
Global Options:
  --verbose, -v        Enable verbose output
  --performance, -p    Enable performance monitoring
  --help, -h          Show help message
  --version           Show version information

Examples:
  codomyrmex --verbose status              # Verbose system status
  codomyrmex --performance workflow run ai-analysis  # With perf monitoring
```

### **`codomyrmex check`**
Verifies system setup and module health.

```bash
codomyrmex check [OPTIONS]

Options:
  --detailed, -d    Show detailed diagnostic information
  --modules, -m     Check specific modules only
  --fix, -f         Attempt to fix common issues automatically
  --quiet, -q       Suppress output except for errors

Examples:
  codomyrmex check                    # Basic health check
  codomyrmex check --detailed         # Detailed diagnostic output
  codomyrmex check -m ai_code_editing # Check specific module
  codomyrmex check --fix              # Try to fix issues
```

### **`codomyrmex info`**
Display project information and module status.

```bash
codomyrmex info [OPTIONS]

Options:
  --modules, -m     Show module information
  --version, -v     Show version information
  --stats, -s       Show usage statistics
  --json           Output in JSON format

Examples:
  codomyrmex info                     # Basic project information
  codomyrmex info --modules           # Module status overview
  codomyrmex info --json              # JSON output for scripting
```

### **`codomyrmex setup`**
Interactive setup wizard for development environment.

```bash
codomyrmex setup [OPTIONS]

Options:
  --interactive, -i  Interactive setup wizard
  --dev             Setup development environment
  --api-keys        Configure API keys for AI services
  --docker          Setup Docker for code execution
  --force, -f       Force reconfiguration

Examples:
  codomyrmex setup                    # Basic setup
  codomyrmex setup --dev              # Development environment
  codomyrmex setup --api-keys         # Configure AI service keys
  codomyrmex setup --force            # Reconfigure everything
```

## 🤖 AI and Code Generation Commands

### **`codomyrmex generate`**
Generate code using AI services.

```bash
codomyrmex generate [OPTIONS] PROMPT

Arguments:
  PROMPT          The code generation prompt

Options:
  --language, -l   Target programming language (default: python)
  --provider, -p   AI provider (openai, anthropic, google)
  --model, -m      Specific model to use
  --output, -o     Output file path
  --context, -c    Context file to include

Examples:
  codomyrmex generate "Create a sorting function" --language python
  codomyrmex generate "REST API endpoint" --provider openai --output api.py
  codomyrmex generate "Data processing" --context data.py --model gpt-4
```

### **`codomyrmex refactor`**
Refactor existing code with AI assistance.

```bash
codomyrmex refactor [OPTIONS] FILE

Arguments:
  FILE            File to refactor

Options:
  --instruction, -i Instructions for refactoring
  --provider, -p    AI provider to use
  --backup, -b      Create backup before refactoring
  --in-place       Modify file in place

Examples:
  codomyrmex refactor code.py --instruction "Add type hints"
  codomyrmex refactor module.py --provider anthropic --backup
  codomyrmex refactor app.py -i "Improve error handling" --in-place
```

## 📊 Analysis and Visualization Commands

### **`codomyrmex analyze`**
Perform static analysis on code files or projects.

```bash
codomyrmex analyze [OPTIONS] PATH

Arguments:
  PATH            File or directory to analyze

Options:
  --type, -t       Analysis type (quality, security, complexity)
  --format, -f     Output format (json, html, text)
  --output, -o     Output file path
  --config, -c     Configuration file
  --verbose, -v    Verbose output

Examples:
  codomyrmex analyze src/                         # Analyze directory
  codomyrmex analyze code.py --type security     # Security analysis
  codomyrmex analyze . --format html -o report.html # HTML report
```

### **`codomyrmex visualize`**
Create data visualizations and plots.

```bash
codomyrmex visualize [OPTIONS] DATA_FILE

Arguments:
  DATA_FILE       Data file to visualize

Options:
  --type, -t      Chart type (line, bar, scatter, histogram, pie)
  --output, -o    Output image file
  --title         Chart title
  --x-label       X-axis label
  --y-label       Y-axis label
  --config, -c    Configuration file

Examples:
  codomyrmex visualize data.csv --type line --output plot.png
  codomyrmex visualize results.json --type bar --title "Results"
```

## ⚙️ Execution and Testing Commands

### **`codomyrmex execute`**
Execute code safely in sandboxed environment.

```bash
codomyrmex execute [OPTIONS] CODE_FILE

Arguments:
  CODE_FILE       File containing code to execute

Options:
  --language, -l   Programming language
  --timeout, -t    Execution timeout in seconds
  --input, -i      Input data file
  --output, -o     Output file
  --sandbox        Sandbox environment type

Examples:
  codomyrmex execute script.py                    # Execute Python script
  codomyrmex execute code.js --language javascript --timeout 30
  codomyrmex execute app.py --input data.txt --output results.txt
```

### **`codomyrmex test`**
Run tests for modules or projects.

```bash
codomyrmex test [OPTIONS] [PATH]

Arguments:
  PATH            Path to test (default: current directory)

Options:
  --module, -m     Test specific module
  --coverage, -c   Generate coverage report
  --verbose, -v    Verbose output
  --parallel, -p   Run tests in parallel

Examples:
  codomyrmex test                                 # Run all tests
  codomyrmex test --module data_visualization     # Test specific module
  codomyrmex test --coverage --verbose            # Detailed coverage
```

## 🔧 Project and Module Management

### **`codomyrmex create`**
Create new modules or projects using templates.

```bash
codomyrmex create [OPTIONS] NAME

Arguments:
  NAME            Name of module or project to create

Options:
  --type, -t       Creation type (module, project)
  --template       Template to use
  --path, -p       Target path for creation
  --force, -f      Overwrite existing files

Examples:
  codomyrmex create my_module --type module       # Create new module
  codomyrmex create my_project --type project     # Create new project
  codomyrmex create analytics --template data     # Use specific template
```

### **`codomyrmex discover`**
Discover and analyze project structure and capabilities.

```bash
codomyrmex discover [OPTIONS] [PATH]

Arguments:
  PATH            Path to discover (default: current directory)

Options:
  --detailed, -d   Detailed analysis
  --modules, -m    Focus on modules only
  --output, -o     Output file for results
  --format, -f     Output format (json, yaml, text)

Examples:
  codomyrmex discover                             # Discover current project
  codomyrmex discover /path/to/project --detailed # Detailed discovery
  codomyrmex discover . --output inventory.json  # Save results
```

## 📚 Documentation and Help Commands

### **`codomyrmex docs`**
Generate or serve documentation.

```bash
codomyrmex docs [OPTIONS] COMMAND

Commands:
  build           Build documentation website
  serve           Serve documentation locally
  generate        Generate API documentation

Options:
  --port, -p      Port for local server (default: 3000)
  --output, -o    Output directory for built docs
  --watch, -w     Watch for changes and rebuild

Examples:
  codomyrmex docs build                           # Build documentation
  codomyrmex docs serve --port 8080               # Serve on custom port
  codomyrmex docs generate --output api-docs/    # Generate API docs
```

### **`codomyrmex examples`**
Run example workflows and demonstrations.

```bash
codomyrmex examples [OPTIONS] [EXAMPLE_NAME]

Arguments:
  EXAMPLE_NAME    Name of specific example to run

Options:
  --list, -l       List available examples
  --interactive, -i Interactive example selection
  --output, -o     Output directory for example results

Examples:
  codomyrmex examples --list                      # List all examples
  codomyrmex examples data-visualization          # Run specific example
  codomyrmex examples --interactive               # Interactive selection
```

## 🔍 Interactive and Shell Commands

### **`codomyrmex shell`**
Launch interactive exploration shell.

```bash
codomyrmex shell [OPTIONS]

Options:
  --module, -m     Start in specific module context
  --debug, -d      Enable debug mode
  --history, -h    Load command history

Examples:
  codomyrmex shell                                # Launch interactive shell
  codomyrmex shell --module ai_code_editing       # Module-specific context
  codomyrmex shell --debug                        # Debug mode
```

### **`codomyrmex config`**
Manage configuration settings.

```bash
codomyrmex config [OPTIONS] COMMAND

Commands:
  get             Get configuration value
  set             Set configuration value
  list            List all configuration
  reset           Reset to defaults

Options:
  --global, -g     Global configuration
  --local, -l      Local project configuration

Examples:
  codomyrmex config list                          # Show all config
  codomyrmex config get api.openai.key           # Get specific value
  codomyrmex config set log.level DEBUG          # Set configuration
  codomyrmex config reset --global               # Reset global config
```

## 🚀 Advanced Usage

### **Environment Variables**

The CLI respects these environment variables:

```bash
# Logging configuration
export CODOMYRMEX_LOG_LEVEL=DEBUG
export CODOMYRMEX_LOG_FILE=/path/to/logfile.log

# API configuration
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"

# Performance configuration
export CODOMYRMEX_MAX_WORKERS=4
export CODOMYRMEX_TIMEOUT=300

# Development configuration
export CODOMYRMEX_DEBUG=true
export CODOMYRMEX_DEV_MODE=true
```

### **Configuration Files**

CLI behavior can be customized with configuration files:

```yaml
# codomyrmex.yaml (project root)
project:
  name: "My Project"
  version: "1.0.0"

modules:
  ai_code_editing:
    default_provider: "openai"
    default_model: "gpt-4"
  
  data_visualization:
    default_format: "png"
    default_dpi: 300

logging:
  level: "INFO"
  format: "json"

analysis:
  ignore_patterns:
    - "*.pyc"
    - "__pycache__/"
    - ".git/"
```

### **Scripting and Automation**

The CLI is designed for scripting and automation:

```bash
#!/bin/bash
# Automated workflow example

# Setup environment
codomyrmex setup --dev --quiet

# Generate code
codomyrmex generate "data processing function" \
  --language python \
  --output processor.py

# Analyze generated code
codomyrmex analyze processor.py \
  --type security \
  --format json \
  --output analysis.json

# Execute if analysis passes
if codomyrmex test processor.py --quiet; then
  echo "✅ Code generated and tested successfully"
  codomyrmex execute processor.py --input data.txt
else
  echo "❌ Generated code failed tests"
fi
```

### **Integration with Other Tools**

```bash
# Integration with Git
git add $(codomyrmex generate "commit script" --output commit.py)
codomyrmex analyze commit.py && git commit -m "Add generated script"

# Integration with CI/CD
codomyrmex test --coverage --format junit --output test-results.xml

# Integration with Docker
docker run -v $(pwd):/workspace codomyrmex analyze /workspace
```

## 🔧 Troubleshooting CLI Issues

### **Common Problems**

```bash
# CLI not found
pip install -e .  # Reinstall Codomyrmex
hash -r          # Refresh command cache

# Permission errors
codomyrmex setup --fix  # Fix common permission issues

# Module import errors
codomyrmex check --detailed  # Diagnose import problems

# Configuration issues
codomyrmex config reset      # Reset to defaults
codomyrmex setup --force     # Reconfigure everything
```

### **Debug Mode**

Enable debug mode for troubleshooting:

```bash
# Enable debug output
export CODOMYRMEX_DEBUG=true
codomyrmex --verbose command

# Or use debug flag
codomyrmex --debug command
```

### **Getting Help**

```bash
# General help
codomyrmex --help

# Command-specific help  
codomyrmex generate --help
codomyrmex analyze --help

# Show version and build info
codomyrmex --version --verbose
```

---

**Version**: 0.1.0  
**Last Updated**: Auto-generated from CLI implementation  
**For More Help**: See [Troubleshooting Guide](troubleshooting.md) or [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)
