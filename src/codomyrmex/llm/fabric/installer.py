import subprocess
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class FabricInstaller:
    """Manages automatic installation of the Fabric CLI via uv and configures its API keys."""

    def __init__(self, config_manager=None):
        from codomyrmex.llm.fabric.fabric_config_manager import FabricConfigManager
        self.config_manager = config_manager or FabricConfigManager()
        self.fabric_env_path = Path.home() / ".config" / "fabric" / ".env"

    def is_installed(self) -> bool:
        """Check if Fabric is already installed in the current PATH."""
        try:
            result = subprocess.run(["fabric", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def install_via_uv(self) -> bool:
        """
        Attempts to install Daniel Miessler's fabric via uv tool install.
        Requires uv to be available on the system.
        """
        logger.info("Attempting to install fabric automatically with uv...")
        try:
            # First verify uv exists
            subprocess.run(["uv", "--version"], check=True, capture_output=True)

            # Install fabric using uv tool.
            # Note: We use the repository endpoint which natively bridges installation.
            install_cmd = ["uv", "tool", "install", "--force", "git+https://github.com/danielmiessler/fabric.git"]

            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Fabric successfully installed via uv tool.")
                return True
            else:
                logger.error(f"Fabric uv installation failed: {result.stderr}")
                return False

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Failed to execute uv to install fabric: {e}")
            return False

    def configure_api_keys(self) -> bool:
        """
        Populate ~/.config/fabric/.env with the API key from Codomyrmex's FabricConfigManager.
        This ensures the CLI tool operates with the correct authentication.
        """
        api_key = self.config_manager.config.api_key
        if not api_key:
            logger.warning("No API key tracked in FabricConfigManager. Cannot map to ~/.config/fabric/.env")
            return False

        try:
            self.fabric_env_path.parent.mkdir(parents=True, exist_ok=True)

            # Read existing env if present to avoid overwriting everything
            env_vars = {}
            if self.fabric_env_path.exists():
                with open(self.fabric_env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_vars[k.strip()] = v.strip()

            # Upsert the OPENAI_API_KEY
            env_vars["OPENAI_API_KEY"] = api_key

            # Write back
            with open(self.fabric_env_path, "w") as f:
                for k, v in env_vars.items():
                    f.write(f"{k}={v}\n")

            logger.info(f"Successfully configured API keys in {self.fabric_env_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to configure API keys for fabric: {e}")
            return False

    def ensure_ready(self) -> bool:
        """High-level orchestration to ensure fabric is installed and configured."""
        installed = self.is_installed()
        if not installed:
            installed = self.install_via_uv()

        if installed:
            self.configure_api_keys()

        return installed

def setup_fabric():
    """Convenience function to set up fabric."""
    installer = FabricInstaller()
    return installer.ensure_ready()
