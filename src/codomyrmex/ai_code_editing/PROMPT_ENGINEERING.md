# AI Code Editing Prompt Engineering Guide

This guide covers the prompt engineering principles and best practices used in the Codomyrmex AI code editing module.

## Overview

The AI code editing module uses structured prompt composition to generate and refactor code through Large Language Models (LLMs). Prompts are composed from three main components:

1. **System Prompt** - Defines AI behavior and constraints
2. **Task Prompt** - Specifies the coding task and requirements
3. **Context Prompt** - Provides relevant code and environment information

## Prompt Composition Architecture

### Core Components

**Location**: `prompt_composition.py`

The main prompt composition utility:

```python
def compose_prompt(system: Optional[str], task: Optional[str], context: Optional[str]) -> str:
    """Compose a complete prompt from system, task, and context components."""
    parts = [p.strip() for p in ((system or ""), (task or ""), (context or "")) if p and p.strip()]
    return "

".join(parts)
```

### Template System

**Location**: `prompt_templates/`

Three template files provide structured prompt components:

- **`system_template.md`** - Base AI behavior and safety instructions
- **`task_template.md`** - Task definition and success criteria
- **`context_template.md`** - Code context and environment details

## System Prompt Engineering

The system prompt establishes the AI's role and behavioral constraints:

### Current System Template

```markdown
# System Prompt

Follow project rules. Be precise, safe, and testable.
```

### Best Practices

**Security First**:
- Always include input validation requirements
- Specify safe code generation boundaries
- Require security scanning integration

**Quality Standards**:
- Mandate comprehensive error handling
- Require proper logging and monitoring
- Enforce code style and documentation standards

**Execution Safety**:
- Include timeout and resource limits
- Require sandboxed execution verification
- Mandate human review for production deployment

## Task Prompt Engineering

Task prompts define specific coding objectives and success criteria.

### Current Task Template

```markdown
# Task Prompt

Describe the goal, constraints, and success criteria.
```

### Task Types

**Code Generation Tasks**:
- Function implementation
- Class creation
- Module scaffolding
- Test case generation

**Code Refactoring Tasks**:
- Performance optimization
- Code structure improvement
- Security vulnerability fixes
- Documentation enhancement

### Success Criteria

Each task prompt should include:

1. **Clear Objective** - What needs to be accomplished
2. **Technical Constraints** - Language, framework, compatibility requirements
3. **Quality Standards** - Testing, documentation, security requirements
4. **Acceptance Criteria** - How to validate successful completion

## Context Prompt Engineering

Context provides the AI with necessary information about the codebase and environment.

### Current Context Template

```markdown
# Context

Include relevant files, interfaces, and environment details.
```

### Context Components

**Code Context**:
- Existing function signatures and interfaces
- Import statements and dependencies
- Related classes and modules
- Coding patterns and conventions

**Environment Context**:
- Python version and runtime environment
- Available libraries and frameworks
- Project structure and organization
- Testing and deployment requirements

**Domain Context**:
- Business logic and requirements
- Performance and scalability needs
- Security and compliance constraints
- Integration requirements

## Prompt Engineering Workflow

### 1. Template Customization

For each AI coding task:

1. **Select Base Templates** - Start with standardized templates
2. **Customize System Prompt** - Add project-specific constraints
3. **Define Task Prompt** - Specify exact coding objective
4. **Gather Context** - Collect relevant code and environment data

### 2. Prompt Composition

```python
from codomyrmex.ai_code_editing.prompt_composition import compose_prompt

# Example composition
system = "You are a Python expert. Generate secure, well-tested code."
task = "Create a function to validate user input with proper error handling."
context = "Python 3.11, use typing hints, follow PEP 8, include docstrings."

complete_prompt = compose_prompt(system, task, context)
```

### 3. Quality Validation

Before sending to LLM:

1. **Security Review** - Check for injection vulnerabilities
2. **Completeness Check** - Ensure all required information included
3. **Clarity Assessment** - Verify prompt is unambiguous
4. **Constraint Validation** - Confirm all constraints are specified

## Advanced Prompt Engineering Techniques

### Chain-of-Thought Prompting

Guide the AI through step-by-step reasoning:

```markdown
Analyze the existing codebase, then:
1. Identify the design pattern used
2. Determine performance bottlenecks
3. Propose refactoring improvements
4. Generate the refactored code
5. Create corresponding tests
```

### Few-Shot Learning

Provide examples in the prompt:

```markdown
Example Input: def add(a, b): return a + b
Example Output: def add(a: int, b: int) -> int:
    \"\"\"Add two integers.\"\"\"
    return a + b

Now refactor: def multiply(x, y): return x * y
```

### Constraint-Based Generation

Specify multiple constraint types:

```markdown
Constraints:
- Type Safety: Use typing hints
- Error Handling: Include try/except blocks
- Documentation: Add docstrings
- Testing: Include doctest examples
- Performance: Optimize for O(n) complexity
```

## Integration with AI Code Editing

### Code Generation Flow

1. **Prompt Composition** - Combine system, task, and context
2. **LLM Processing** - Send to appropriate AI model
3. **Code Validation** - Run static analysis and security checks
4. **Test Generation** - Create unit tests for generated code
5. **Integration Testing** - Verify in sandbox environment

### Refactoring Flow

1. **Code Analysis** - Understand existing code structure
2. **Improvement Identification** - Detect optimization opportunities
3. **Refactoring Prompt** - Generate specific refactoring instructions
4. **Incremental Changes** - Apply changes with validation
5. **Regression Testing** - Ensure functionality preserved

## Best Practices

### Prompt Design

1. **Be Specific** - Avoid vague requirements
2. **Provide Context** - Include relevant examples and constraints
3. **Define Success** - Specify measurable completion criteria
4. **Include Examples** - Show expected input/output format

### Quality Assurance

1. **Review Generated Code** - Always validate AI output
2. **Test Thoroughly** - Run comprehensive test suites
3. **Security Scan** - Check for vulnerabilities
4. **Performance Test** - Verify efficiency requirements

### Continuous Improvement

1. **Track Success Rate** - Monitor prompt effectiveness
2. **Refine Templates** - Update based on results
3. **Collect Feedback** - Learn from successful patterns
4. **Update Guidelines** - Evolve best practices

## Real-World Examples

### Function Generation

**Task Prompt**:
```markdown
Create a secure password validation function that:
- Accepts string input
- Validates length (8-128 characters)
- Requires at least one uppercase, lowercase, digit, and special character
- Returns boolean result
- Includes proper error handling
- Follows PEP 8 style guidelines
```

### Code Refactoring

**Task Prompt**:
```markdown
Refactor this function for better performance and readability:
- Optimize algorithm complexity
- Add type hints
- Improve variable naming
- Add comprehensive docstring
- Include error handling
- Maintain backward compatibility
```

## Utilities and Tools

**Real utilities** are implemented in `prompt_composition.py` and provide:

- **Prompt Composition** - Structured prompt building
- **Template Loading** - Dynamic template integration
- **Validation** - Prompt completeness checking
- **Optimization** - Prompt size and clarity optimization

**Templates** in `prompt_templates/` contain:

- **System Templates** - Base AI behavior definitions
- **Task Templates** - Standardized task formats
- **Context Templates** - Environment information structures

**All handlers** are real, executable implementations with proper error handling and logging.

## Related Documentation

- [README.md](README.md) - Module overview and usage
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage examples
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
