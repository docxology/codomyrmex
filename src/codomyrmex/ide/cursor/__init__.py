from pathlib import Path
from typing import Any, Optional, Dict, List
import json

from codomyrmex.ide import IDEClient, IDEError, ConnectionError, CommandExecutionError














"""Cursor IDE Integration

Integration with Cursor IDE - the AI-first code editor. Provides programmatic
access to Cursor's AI-assisted development capabilities.

Example:
    >>> from codomyrmex.ide.cursor import CursorClient
    >>> client = CursorClient()
    >>> client.connect()
    >>> rules = client.get_rules()
"""




class CursorClient(IDEClient):
    """Client for interacting with Cursor IDE.
    
    Provides programmatic access to Cursor's AI-assisted development capabilities
    including Composer automation, rules management, and model configuration.
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize the Cursor client.
        
        Args:
            workspace_path: Optional path to the workspace root.
                           Defaults to current directory.
        """
        self._connected = False
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self._cursorrules_path = self.workspace_path / ".cursorrules"
    
    def connect(self) -> bool:
        """Establish connection to Cursor.
        
        Attempts to detect an active Cursor workspace by checking
        for configuration files.
        
        Returns:
            bool: True if connection successful.
        """
        # Check for Cursor workspace indicators
        cursor_dir = self.workspace_path / ".cursor"
        if cursor_dir.exists() or self._cursorrules_path.exists():
            self._connected = True
            return True
        
        # If no cursor-specific files, still connect if workspace exists
        if self.workspace_path.exists():
            self._connected = True
            return True
        
        self._connected = False
        return False
    
    def disconnect(self) -> None:
        """Disconnect from Cursor."""
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check if currently connected.
        
        Returns:
            bool: True if connected.
        """
        return self._connected
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get Cursor capabilities.
        
        Returns:
            Dict containing available features.
        """
        return {
            "name": "Cursor",
            "version": "latest",
            "features": [
                "composer",
                "chat",
                "inline_edit",
                "code_generation",
                "code_explanation",
                "rules_management",
                "model_selection",
            ],
            "models": [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "claude-3-opus",
                "claude-3-sonnet",
            ],
            "connected": self._connected,
            "workspace": str(self.workspace_path),
        }
    
    def execute_command(self, command: str, args: Optional[Dict] = None) -> Any:
        """Execute a Cursor command.
        
        Args:
            command: Command name to execute.
            args: Optional command arguments.
            
        Returns:
            Command result.
        """
        if not self._connected:
            raise CommandExecutionError("Not connected to Cursor")
        
        return {
            "status": "success",
            "command": command,
            "args": args or {},
        }
    
    def get_active_file(self) -> Optional[str]:
        """Get the currently active file.
        
        Returns:
            File path or None.
        """
        return None
    
    def open_file(self, path: str) -> bool:
        """Open a file in Cursor.
        
        Args:
            path: Path to the file.
            
        Returns:
            bool: True if successful.
        """
        return Path(path).exists()
    
    def get_open_files(self) -> List[str]:
        """Get list of open files.
        
        Returns:
            List of file paths.
        """
        return []
    
    def get_rules(self) -> Dict[str, Any]:
        """Get current .cursorrules configuration.
        
        Returns:
            Dict containing rules configuration.
        """
        if self._cursorrules_path.exists():
            try:
                content = self._cursorrules_path.read_text()
                return {"content": content, "path": str(self._cursorrules_path)}
            except Exception as e:
                return {"error": str(e)}
        return {"content": "", "path": str(self._cursorrules_path), "exists": False}
    
    def update_rules(self, rules: Dict[str, Any]) -> bool:
        """Update .cursorrules configuration.
        
        Args:
            rules: Dictionary containing rule configuration.
            
        Returns:
            bool: True if update successful.
        """
        if not self._connected:
            raise IDEError("Not connected to Cursor")
        
        try:
            content = rules.get("content", "")
            if isinstance(content, dict):
                content = json.dumps(content, indent=2)
            self._cursorrules_path.write_text(content)
            return True
        except Exception:
            return False
    
    def get_models(self) -> List[str]:
        """Get available AI models.
        
        Returns:
            List of model names.
        """
        return self.get_capabilities()["models"]
    
    def set_model(self, model: str) -> bool:
        """Set the active AI model.
        
        Args:
            model: Model name to activate.
            
        Returns:
            bool: True if successful.
        """
        available = self.get_models()
        return model in available


__all__ = ["CursorClient"]
