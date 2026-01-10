import shutil
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .data_provider import DataProvider
from codomyrmex.logging_monitoring import get_logger


logger = get_logger(__name__)
class WebsiteGenerator:
    """
    Generates the static website.
    """

    def __init__(self, output_dir: str, root_dir: Optional[str] = None):


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
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate(self):
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
            "pipelines": self.data_provider.get_pipeline_status()
        }

        # 3. Render Pages
        pages = ["index.html", "modules.html", "scripts.html", "chat.html", "agents.html", "config.html", "docs.html", "pipelines.html"]
        for page in pages:
            self._render_page(page, context)
        
        # 4. Copy Assets
        self._copy_assets()
        
        print("Website generation complete.")

    def _render_page(self, template_name: str, context: dict):


        template = self.env.get_template(template_name)
        output = template.render(**context)
        output_path = self.output_dir / template_name
        output_path.write_text(output, encoding="utf-8")
        print(f"Rendered {template_name}")

    def _copy_assets(self):
        """Brief description of _copy_assets."""
        if self.assets_dir.exists():
            shutil.copytree(self.assets_dir, self.output_dir / "assets")
            print("Copied assets")
