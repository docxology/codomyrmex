from pathlib import Path
from typing import Dict, List, Optional
import json

from codomyrmex.logging_monitoring import get_logger



"""
Fabric Configuration Manager for Codomyrmex Integration

Manages Fabric configuration, patterns, and integration settings.
"""




class FabricConfigManager:
    """Manages Fabric configuration and integration settings."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize Fabric configuration manager.

        Args:
            config_dir: Custom configuration directory (default: ~/.config/fabric)
        """
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".config" / "fabric"
        self.patterns_dir = self.config_dir / "patterns"
        self.contexts_dir = self.config_dir / "contexts"
        self.logger = get_logger(__name__)

    def ensure_directories(self) -> bool:
        """Ensure all required directories exist."""
        dirs = [self.config_dir, self.patterns_dir, self.contexts_dir]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Fabric directories ensured at: {self.config_dir}")
        return True

    def list_available_patterns(self) -> List[str]:
        """List all available Fabric patterns."""
        if not self.patterns_dir.exists():
            return []

        patterns = []
        for item in self.patterns_dir.iterdir():
            if item.is_dir() and (item / "system.md").exists():
                patterns.append(item.name)

        return sorted(patterns)

    def create_custom_pattern(
        self,
        name: str,
        system_prompt: str,
        description: str = ""
    ) -> bool:
        """
        Create a custom Fabric pattern.

        Args:
            name: Pattern name
            system_prompt: System prompt content
            description: Optional description

        Returns:
            True if successful
        """
        pattern_dir = self.patterns_dir / name
        pattern_dir.mkdir(exist_ok=True)

        # Create system.md file
        system_file = pattern_dir / "system.md"
        with open(system_file, 'w') as f:
            f.write(system_prompt)

        # Create README.md if description provided
        if description:
            readme_file = pattern_dir / "README.md"
            with open(readme_file, 'w') as f:
                f.write(f"# {name}\n\n{description}\n")

        self.logger.info(f"Created custom pattern: {name}")
        return True

    def create_codomyrmex_patterns(self) -> bool:
        """Create Codomyrmex-specific Fabric patterns."""
        # Pattern for code analysis integration
        code_analysis_prompt = """# IDENTITY and PURPOSE
You are an expert code analyst working with the Codomyrmex framework. Your role is to analyze code and provide insights that integrate well with Codomyrmex's static analysis and visualization capabilities.

# STEPS
- Analyze the provided code for quality, security, and maintainability issues
- Identify patterns that could benefit from Codomyrmex module integration
- Provide specific recommendations for improvements
- Generate metrics that can be visualized using Codomyrmex's data visualization module

# OUTPUT INSTRUCTIONS
- Provide analysis in structured JSON format for easy integration
- Include severity levels (low, medium, high, critical)
- Add specific recommendations for each issue found
- Include suggested Codomyrmex modules for further analysis

# OUTPUT EXAMPLE
```json
{
  "analysis": {
    "quality_score": 85,
    "issues": [
      {
        "type": "complexity",
        "severity": "medium", 
        "message": "Function has high cyclomatic complexity",
        "line": 15,
        "recommendation": "Consider breaking into smaller functions"
      }
    ],
    "codomyrmex_suggestions": [
      "Use static_analysis module for detailed complexity metrics",
      "Apply data_visualization to show complexity trends"
    ]
  }
}
```
"""

        self.create_custom_pattern(
            "codomyrmex_code_analysis",
            code_analysis_prompt,
            "Code analysis pattern optimized for Codomyrmex integration"
        )

        # Pattern for workflow orchestration
        workflow_prompt = """# IDENTITY and PURPOSE
You are a workflow orchestration expert specializing in AI-augmented development processes. You help design and optimize workflows that combine multiple AI tools and development modules.

# STEPS
- Analyze the provided workflow requirements or existing workflow
- Identify opportunities for AI integration and automation
- Suggest optimal sequencing of tools and processes
- Provide implementation guidance for workflow orchestration

# OUTPUT INSTRUCTIONS
- Structure output as actionable workflow steps
- Include tool recommendations and integration points
- Provide estimated timeframes and resource requirements
- Include error handling and fallback strategies

# OUTPUT FORMAT
Provide a structured workflow plan with:
1. **Workflow Overview**: High-level description and objectives
2. **Steps**: Detailed step-by-step process
3. **Integration Points**: Where AI tools and modules connect
4. **Success Metrics**: How to measure workflow effectiveness
5. **Optimization Opportunities**: Areas for future improvement
"""

        self.create_custom_pattern(
            "codomyrmex_workflow_design",
            workflow_prompt,
            "Workflow design pattern for AI-augmented development processes"
        )

        self.logger.info("Created Codomyrmex-specific Fabric patterns")
        return True

    def export_configuration(self, output_file: str) -> bool:
        """
        Export current Fabric configuration.

        Args:
            output_file: Path to output JSON file

        Returns:
            True if successful
        """
        config_data = {
            "config_dir": str(self.config_dir),
            "patterns": self.list_available_patterns(),
            "directories": {
                "patterns": str(self.patterns_dir),
                "contexts": str(self.contexts_dir)
            }
        }

        try:
            with open(output_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            self.logger.info(f"Configuration exported to: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False


