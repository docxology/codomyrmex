#!/usr/bin/env python3
"""
Prompts Demo Script

Demonstrates prompt versioning, storage, and template management.
Shows how to organize and manage prompts for production LLM applications.

Features:
    - Prompt template loading and rendering
    - Version management
    - Variable substitution
    - Prompt library organization
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_warning


@dataclass
class PromptTemplate:
    """A versioned prompt template."""
    name: str
    content: str
    version: str = "1.0.0"
    description: str = ""
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        # Auto-detect variables from content
        if not self.variables:
            self.variables = list(set(re.findall(r'\{(\w+)\}', self.content)))
    
    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        result = self.content
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def validate(self, **kwargs) -> tuple[bool, List[str]]:
        """Validate that all required variables are provided."""
        provided = set(kwargs.keys())
        required = set(self.variables)
        missing = required - provided
        extra = provided - required
        
        issues = []
        if missing:
            issues.append(f"Missing variables: {', '.join(missing)}")
        if extra:
            issues.append(f"Extra variables (ignored): {', '.join(extra)}")
        
        return len(missing) == 0, issues


class PromptLibrary:
    """A collection of prompt templates."""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """Load built-in prompt templates."""
        self.add(PromptTemplate(
            name="code_review",
            content="""You are an expert code reviewer. Review the following {language} code:

```{language}
{code}
```

Provide feedback on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Suggestions for improvement

Be constructive and specific in your feedback.""",
            description="Code review prompt for any language",
            version="1.2.0"
        ))
        
        self.add(PromptTemplate(
            name="summarize",
            content="""Summarize the following text in a {style} style:

{text}

Provide a clear, concise summary that captures the main points.""",
            description="Text summarization with style option",
            version="1.0.0"
        ))
        
        self.add(PromptTemplate(
            name="explain",
            content="""Explain {topic} to someone who is {audience}.

Use appropriate language and examples for this audience level.
Be clear, engaging, and accurate.""",
            description="Explanation generator for different audiences",
            version="1.1.0"
        ))
        
        self.add(PromptTemplate(
            name="translate",
            content="""Translate the following {source_lang} text to {target_lang}:

{text}

Maintain the original meaning, tone, and style as closely as possible.""",
            description="Translation between languages",
            version="1.0.0"
        ))
        
        self.add(PromptTemplate(
            name="chain_of_thought",
            content="""Solve the following problem step by step:

{problem}

Think through this carefully:
1. First, understand what is being asked
2. Break down the problem into smaller parts
3. Solve each part systematically
4. Combine the parts into a final answer

Show your reasoning at each step.""",
            description="Chain-of-thought reasoning prompt",
            version="1.0.0"
        ))
    
    def add(self, template: PromptTemplate):
        """Add a template to the library."""
        self.templates[template.name] = template
    
    def get(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all template names."""
        return list(self.templates.keys())


def demo_template_rendering():
    """Demonstrate template loading and rendering."""
    print_info("📝 Template Rendering Demo\n")
    
    library = PromptLibrary()
    
    # Get and render code review template
    template = library.get("code_review")
    print(f"  Template: {template.name} (v{template.version})")
    print(f"  Description: {template.description}")
    print(f"  Variables: {', '.join(template.variables)}")
    
    rendered = template.render(
        language="Python",
        code="def hello():\n    print('Hello, World!')"
    )
    
    print(f"\n  Rendered prompt (first 200 chars):")
    print(f"  ---")
    print(f"  {rendered[:200]}...")
    print()


def demo_template_validation():
    """Demonstrate template validation."""
    print_info("✅ Template Validation Demo\n")
    
    library = PromptLibrary()
    template = library.get("explain")
    
    test_cases = [
        {"topic": "recursion", "audience": "beginners"},  # Valid
        {"topic": "quantum computing"},  # Missing audience
        {"topic": "AI", "audience": "experts", "extra": "ignored"},  # Extra
    ]
    
    for i, kwargs in enumerate(test_cases, 1):
        is_valid, issues = template.validate(**kwargs)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  Test {i}: {status}")
        print(f"    Provided: {kwargs}")
        for issue in issues:
            print(f"    ⚠️ {issue}")
        print()


def demo_prompt_library():
    """Demonstrate prompt library functionality."""
    print_info("📚 Prompt Library Demo\n")
    
    library = PromptLibrary()
    
    print("  Available templates:")
    for name in library.list_templates():
        template = library.get(name)
        print(f"    • {name} (v{template.version})")
        print(f"      {template.description}")
        print(f"      Variables: {', '.join(template.variables)}")
        print()


def demo_version_management():
    """Demonstrate version management."""
    print_info("🔄 Version Management Demo\n")
    
    # Simulate version history
    versions = [
        {"version": "1.0.0", "date": "2025-01-15", "changes": "Initial release"},
        {"version": "1.1.0", "date": "2025-06-20", "changes": "Added examples request"},
        {"version": "1.2.0", "date": "2026-01-10", "changes": "Added performance section"},
    ]
    
    print("  Template: code_review")
    print("  Version History:")
    for v in versions:
        print(f"    v{v['version']} ({v['date']}): {v['changes']}")
    print()
    
    print_warning("  💡 Tip: Version your prompts to track improvements and enable rollback!")


def main():
    """Main demonstration."""
    setup_logging()
    print("=" * 60)
    print("  Prompts Demo - Template Management & Versioning")
    print("=" * 60)
    print()
    
    demo_prompt_library()
    demo_template_rendering()
    demo_template_validation()
    demo_version_management()
    
    print_success("✅ Demo completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
