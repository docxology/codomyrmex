#!/usr/bin/env python3
"""
OpenRouter Long Output Generator - Extended Content Creation

Generates extremely long outputs (essays, dissertations, books) using OpenRouter's
free models with configurable chunking and continuation strategies.

Features:
    - Iterative generation with automatic continuation
    - Configurable output length (pages/words/tokens target)
    - Multiple output formats (markdown, plain text, LaTeX)
    - Progress tracking and resumption
    - Preset templates (dissertation, essay, story, documentation)

API Key Sources:
    1. --api-key command line argument
    2. OPENROUTER_API_KEY environment variable
    3. ~/.config/openrouter/api_key config file

Usage:
    # Generate a 5-page essay
    python openrouter_long_output.py --topic "Climate Change" --pages 5
    
    # Generate PhD dissertation outline
    python openrouter_long_output.py --template dissertation --topic "AI Ethics"
    
    # Generate with word count target
    python openrouter_long_output.py --topic "History of Python" --words 5000
    
    # Full PhD dissertation (extremely long)
    python openrouter_long_output.py --template dissertation --topic "Machine Learning" --pages 100 --output thesis.md
"""

import sys
import os
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.llm.providers import (
    get_provider,
    ProviderType,
    ProviderConfig,
    Message,
    OpenRouterProvider,
)

# Default config file locations
CONFIG_PATHS = [
    Path.home() / ".config" / "openrouter" / "api_key",
    Path.home() / ".openrouter_api_key",
]


# ~250 words per page, ~1.3 tokens per word
WORDS_PER_PAGE = 250
TOKENS_PER_WORD = 1.3

# Templates for different document types
TEMPLATES = {
    "essay": {
        "system": """You are an expert academic writer. Write comprehensive, 
well-structured essays with clear thesis statements, supporting arguments, 
and proper citations. Use formal academic language.""",
        "structure": """Write a comprehensive essay on the topic: {topic}

Structure your essay with:
1. Introduction with clear thesis
2. Multiple body paragraphs with evidence
3. Counter-arguments and rebuttals
4. Strong conclusion

Current section: {section}
Target length: approximately {target_words} words for this section.

{continuation_context}""",
        "sections": ["Introduction", "Background", "Main Arguments", "Counter-Arguments", "Conclusion"],
    },
    
    "dissertation": {
        "system": """You are an expert PhD dissertation writer. Write comprehensive, 
rigorous academic content suitable for a doctoral thesis. Include proper academic 
structure, literature references (use placeholder citations like [Author, Year]), 
methodology discussions, and critical analysis.""",
        "structure": """Write a section for a PhD dissertation on: {topic}

Dissertation Chapter: {section}
Target length: approximately {target_words} words.

Guidelines:
- Use formal academic language
- Include placeholder citations [Author, Year]
- Be thorough and rigorous
- Include subsections as appropriate

{continuation_context}""",
        "sections": [
            "Abstract",
            "Chapter 1: Introduction",
            "Chapter 2: Literature Review", 
            "Chapter 3: Theoretical Framework",
            "Chapter 4: Methodology",
            "Chapter 5: Results and Analysis",
            "Chapter 6: Discussion",
            "Chapter 7: Conclusion",
            "References (Placeholder)",
        ],
    },
    
    "story": {
        "system": """You are a creative fiction writer. Write engaging, 
immersive stories with vivid descriptions, compelling characters, 
and engaging plot development.""",
        "structure": """Continue writing the story about: {topic}

Current chapter: {section}
Target length: approximately {target_words} words.

{continuation_context}""",
        "sections": ["Prologue", "Chapter 1", "Chapter 2", "Chapter 3", "Chapter 4", "Epilogue"],
    },
    
    "documentation": {
        "system": """You are a technical documentation expert. Write clear, 
comprehensive documentation with examples, code snippets, and proper structure.""",
        "structure": """Write documentation for: {topic}

Section: {section}
Target length: approximately {target_words} words.

Include:
- Clear explanations
- Code examples where appropriate
- Best practices
- Common pitfalls

{continuation_context}""",
        "sections": ["Overview", "Installation", "Quick Start", "Core Concepts", "API Reference", "Examples", "Troubleshooting"],
    },
    
    "custom": {
        "system": "You are a helpful writing assistant.",
        "structure": """Write about: {topic}

Section: {section}
Target length: approximately {target_words} words.

{continuation_context}""",
        "sections": ["Part 1", "Part 2", "Part 3"],
    },
}


def get_api_key(cli_key: str | None = None) -> str | None:
    """Get API key from multiple sources."""
    if cli_key:
        return cli_key
    env_key = os.environ.get("OPENROUTER_API_KEY")
    if env_key:
        return env_key
    for path in CONFIG_PATHS:
        try:
            if path.exists():
                content = path.read_text().strip()
                if content.startswith("OPENROUTER_API_KEY="):
                    return content.split("=", 1)[1].strip().strip('"').strip("'")
                return content
        except Exception:
            pass
    return None


@dataclass
class GenerationConfig:
    """Configuration for long output generation."""
    topic: str
    template: str = "essay"
    target_pages: int | None = None
    target_words: int | None = None
    model: str = "openrouter/free"
    max_tokens_per_chunk: int = 2000
    temperature: float = 0.7
    output_file: str | None = None
    output_format: str = "markdown"
    custom_sections: list[str] | None = None
    custom_system: str | None = None
    stream: bool = True
    verbose: bool = False
    
    @property
    def total_target_words(self) -> int:
        """Calculate total target words."""
        if self.target_words:
            return self.target_words
        if self.target_pages:
            return self.target_pages * WORDS_PER_PAGE
        return 1000  # Default ~4 pages
    
    @property
    def sections(self) -> list[str]:
        """Get sections for this template."""
        if self.custom_sections:
            return self.custom_sections
        return TEMPLATES.get(self.template, TEMPLATES["custom"])["sections"]


class LongOutputGenerator:
    """Generates long-form content with automatic continuation."""
    
    def __init__(self, provider, config: GenerationConfig):
        self.provider = provider
        self.config = config
        self.generated_content: list[dict] = []
        self.total_words = 0
        self.total_tokens = 0
        
        template = TEMPLATES.get(config.template, TEMPLATES["custom"])
        self.system_prompt = config.custom_system or template["system"]
        self.structure_template = template["structure"]
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def _get_continuation_context(self) -> str:
        """Get context from previous generation for continuation."""
        if not self.generated_content:
            return "This is the beginning of the document."
        
        # Get last ~500 words for context
        last_content = self.generated_content[-1]["content"]
        words = last_content.split()
        if len(words) > 200:
            context = " ".join(words[-200:])
            return f"Continue from the previous section. Last 200 words for context:\n...{context}"
        return f"Continue from:\n{last_content[-1000:]}"
    
    def generate_section(self, section: str, target_words: int) -> str:
        """Generate a single section."""
        prompt = self.structure_template.format(
            topic=self.config.topic,
            section=section,
            target_words=target_words,
            continuation_context=self._get_continuation_context(),
        )
        
        messages = [
            Message(role="system", content=self.system_prompt),
            Message(role="user", content=prompt),
        ]
        
        if self.config.stream:
            content = ""
            for chunk in self.provider.complete_stream(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens_per_chunk,
            ):
                print(chunk, end="", flush=True)
                content += chunk
            print()  # Newline after streaming
        else:
            response = self.provider.complete(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens_per_chunk,
            )
            content = response.content
            if self.config.verbose:
                print(content)
        
        return content
    
    def generate(self) -> str:
        """Generate the full document."""
        sections = self.config.sections
        words_per_section = self.config.total_target_words // len(sections)
        
        print("=" * 70)
        print("  OpenRouter Long Output Generator")
        print("=" * 70)
        print(f"\n📝 Topic: {self.config.topic}")
        print(f"📋 Template: {self.config.template}")
        print(f"📊 Target: ~{self.config.total_target_words:,} words ({len(sections)} sections)")
        print(f"🤖 Model: {self.config.model}")
        print("-" * 70 + "\n")
        
        start_time = time.time()
        
        for i, section in enumerate(sections, 1):
            print(f"\n{'='*60}")
            print(f"📖 Section {i}/{len(sections)}: {section}")
            print(f"   Target: ~{words_per_section} words")
            print("=" * 60 + "\n")
            
            try:
                content = self.generate_section(section, words_per_section)
                word_count = self._count_words(content)
                self.total_words += word_count
                
                self.generated_content.append({
                    "section": section,
                    "content": content,
                    "word_count": word_count,
                    "timestamp": datetime.now().isoformat(),
                })
                
                print(f"\n✅ Section complete: {word_count} words | Total: {self.total_words:,} words")
                
                # Rate limit awareness - brief pause between sections
                if i < len(sections):
                    time.sleep(1)
                    
            except Exception as e:
                print(f"\n❌ Error generating section '{section}': {e}")
                self.generated_content.append({
                    "section": section,
                    "content": f"[Error: {e}]",
                    "word_count": 0,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                })
        
        elapsed = time.time() - start_time
        
        # Combine all sections
        full_document = self._format_document()
        
        print("\n" + "=" * 70)
        print("📊 Generation Complete!")
        print("=" * 70)
        print(f"   Total words: {self.total_words:,}")
        print(f"   Sections: {len(self.generated_content)}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Rate: {self.total_words / (elapsed / 60):.0f} words/minute")
        
        # Save if output file specified
        if self.config.output_file:
            self._save(full_document)
        
        return full_document
    
    def _format_document(self) -> str:
        """Format the complete document."""
        lines = []
        
        if self.config.output_format == "markdown":
            lines.append(f"# {self.config.topic}\n")
            lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
            lines.append(f"*Template: {self.config.template} | Words: ~{self.total_words:,}*\n")
            lines.append("---\n")
            
            for section_data in self.generated_content:
                lines.append(f"\n## {section_data['section']}\n")
                lines.append(section_data["content"])
                lines.append("\n")
        
        elif self.config.output_format == "latex":
            lines.append(f"\\documentclass{{article}}\n\\title{{{self.config.topic}}}\n\\begin{{document}}\n\\maketitle\n")
            for section_data in self.generated_content:
                lines.append(f"\n\\section{{{section_data['section']}}}\n")
                lines.append(section_data["content"].replace("_", "\\_"))
                lines.append("\n")
            lines.append("\\end{document}")
        
        else:  # plain text
            lines.append(f"{self.config.topic}\n{'=' * len(self.config.topic)}\n")
            for section_data in self.generated_content:
                lines.append(f"\n{section_data['section']}\n{'-' * len(section_data['section'])}\n")
                lines.append(section_data["content"])
                lines.append("\n")
        
        return "\n".join(lines)
    
    def _save(self, content: str) -> None:
        """Save generated content to file."""
        output_path = Path(self.config.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Also save metadata
        meta_path = output_path.with_suffix(".meta.json")
        metadata = {
            "topic": self.config.topic,
            "template": self.config.template,
            "model": self.config.model,
            "total_words": self.total_words,
            "sections": [
                {"name": s["section"], "words": s["word_count"]}
                for s in self.generated_content
            ],
            "generated_at": datetime.now().isoformat(),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n💾 Saved to: {output_path}")
        print(f"📋 Metadata: {meta_path}")


def main():
    parser = argparse.ArgumentParser(
        description="OpenRouter Long Output Generator - Extended Content Creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Templates:
  essay         Academic essay (~5 sections)
  dissertation  PhD thesis structure (9 chapters)
  story         Creative fiction (6 chapters)
  documentation Technical docs (7 sections)
  custom        Basic structure (3 parts)

Examples:
  # 5-page essay
  python openrouter_long_output.py --topic "AI Ethics" --pages 5
  
  # PhD dissertation (~100 pages)
  python openrouter_long_output.py --template dissertation --topic "ML Safety" --pages 100
  
  # 10,000 word story
  python openrouter_long_output.py --template story --topic "Space Exploration" --words 10000
  
  # Custom sections
  python openrouter_long_output.py --topic "Python Guide" --sections "Basics" "Advanced" "Examples"
        """
    )
    
    # Required (unless listing)
    parser.add_argument("--topic", "-t", type=str, default=None,
                        help="Main topic for content generation")
    
    # Length targets (mutually exclusive)
    length_group = parser.add_mutually_exclusive_group()
    length_group.add_argument("--pages", "-p", type=int, default=None,
                              help="Target number of pages (~250 words/page)")
    length_group.add_argument("--words", "-w", type=int, default=None,
                              help="Target word count")
    
    # Template and structure
    parser.add_argument("--template", type=str, default="essay",
                        choices=list(TEMPLATES.keys()),
                        help="Document template (default: essay)")
    parser.add_argument("--sections", nargs="+", type=str, default=None,
                        help="Custom section names (overrides template)")
    parser.add_argument("--system", type=str, default=None,
                        help="Custom system prompt (overrides template)")
    
    # Model settings
    parser.add_argument("--model", "-m", type=str, default="openrouter/free",
                        help="Model to use (default: openrouter/free)")
    parser.add_argument("--max-tokens", type=int, default=2000,
                        help="Max tokens per chunk (default: 2000)")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Generation temperature (default: 0.7)")
    
    # Output
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path")
    parser.add_argument("--format", "-f", type=str, default="markdown",
                        choices=["markdown", "latex", "text"],
                        help="Output format (default: markdown)")
    
    # Behavior
    parser.add_argument("--no-stream", action="store_true",
                        help="Disable streaming output")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    
    # API key
    parser.add_argument("--api-key", "-k", type=str, default=None,
                        help="OpenRouter API key")
    
    # List options
    parser.add_argument("--list-templates", action="store_true",
                        help="List available templates")
    parser.add_argument("--list-models", action="store_true",
                        help="List available free models")
    
    args = parser.parse_args()
    
    if args.list_templates:
        print("\n📋 Available Templates:\n")
        for name, template in TEMPLATES.items():
            print(f"  {name}:")
            print(f"    Sections: {', '.join(template['sections'][:3])}...")
            print()
        return 0
    
    if args.list_models:
        print("\n📋 Available Free Models:\n")
        for m in OpenRouterProvider.FREE_MODELS:
            print(f"  • {m}")
        return 0
    
    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        print("   Get your free API key at: https://openrouter.ai/keys")
        return 1
    
    # Validate topic is provided for generation
    if not args.topic:
        print("❌ --topic is required for content generation")
        print("   Example: python openrouter_long_output.py --topic 'AI Ethics'")
        return 1
    
    # Create config
    config = GenerationConfig(
        topic=args.topic,
        template=args.template,
        target_pages=args.pages,
        target_words=args.words,
        model=args.model,
        max_tokens_per_chunk=args.max_tokens,
        temperature=args.temperature,
        output_file=args.output,
        output_format=args.format,
        custom_sections=args.sections,
        custom_system=args.system,
        stream=not args.no_stream,
        verbose=args.verbose,
    )
    
    # Generate
    provider_config = ProviderConfig(api_key=api_key, timeout=180.0)
    
    with get_provider(ProviderType.OPENROUTER, config=provider_config) as provider:
        generator = LongOutputGenerator(provider, config)
        generator.generate()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
