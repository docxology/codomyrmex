"""Static site generator for the Codomyrmex website.

Provides WebsiteGenerator, which renders Jinja2 HTML templates with
data from DataProvider and copies static assets to produce a complete
static website.
"""

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from codomyrmex.logging_monitoring import get_logger

from .data_provider import DataProvider

logger = get_logger(__name__)


class WebsiteGenerator:
    """
    Generates the static website.
    """

    def __init__(self, output_dir: str, root_dir: str | None = None):

        self.output_dir = Path(output_dir)
        # Assuming we are running from project root, or passing it in.
        # Default to finding the project root relative to this file if not provided.
        if root_dir:
            self.root_dir = Path(root_dir)
        else:
            # src/codomyrmex/website/generator.py -> .../src/codomyrmex/website -> .../src/codomyrmex -> .../src -> .../root
            self.root_dir = Path(__file__).resolve().parent.parent.parent.parent

        self.module_dir = Path(__file__).resolve().parent
        self.templates_dir = self.module_dir / "templates"
        self.assets_dir = self.module_dir / "assets"

        self.data_provider = DataProvider(self.root_dir)

        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def generate(self) -> None:
        """Executes the generation process."""
        print(f"Generating website to {self.output_dir}...")

        # 1. Prepare output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)

        # 2. Collect Data
        context = {
            "system": self.data_provider.get_system_summary(),
            "modules": self.data_provider.get_modules(),
            "agents": self.data_provider.get_actual_agents(),
            "scripts": self.data_provider.get_available_scripts(),
            "config_files": self.data_provider.get_config_files(),
            "doc_tree": self.data_provider.get_doc_tree(),
            "pipelines": self.data_provider.get_pipeline_status(),
            "health": self.data_provider.get_health_status(),
            "awareness": self.data_provider.get_pai_awareness_data(),
        }

        # 3. Render Pages
        pages = [
            "index.html",
            "health.html",
            "modules.html",
            "tools.html",
            "scripts.html",
            "chat.html",
            "agents.html",
            "config.html",
            "docs.html",
            "pipelines.html",
            "awareness.html",
            "pai_control.html",
            "curriculum.html",
            "tutoring.html",
            "assessment.html",
            "content.html",
        ]
        for page in pages:
            try:
                self._render_page(page, context)
            except Exception as exc:
                logger.warning("Skipping %s: %s", page, exc)

        # 4. Copy Assets
        self._copy_assets()

        print("Website generation complete.")

    def _render_page(self, template_name: str, context: dict) -> None:
        """Render a Jinja2 template with the given context and write to output.

        Loads *template_name* from the templates directory, renders it with
        *context*, and writes the resulting HTML to the output directory.
        """
        template = self.env.get_template(template_name)
        output = template.render(**context)
        output_path = self.output_dir / template_name
        output_path.write_text(output, encoding="utf-8")
        print(f"Rendered {template_name}")

    def _copy_assets(self) -> None:
        """Copy static assets (CSS, JS) to the output directory."""
        if self.assets_dir.exists():
            shutil.copytree(self.assets_dir, self.output_dir / "assets")
            print("Copied assets")
