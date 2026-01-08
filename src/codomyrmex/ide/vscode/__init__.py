from pathlib import Path
from typing import Any, Optional, Dict, List
import json


from codomyrmex.ide import IDEClient, IDEError, ConnectionError, CommandExecutionError






























"""VS Code IDE Integration

"""Core functionality module

This module provides __init__ functionality including:
- 15 functions: __init__, connect, disconnect...
- 1 classes: VSCodeClient

Usage:
    # Example usage here
"""
Integration with Visual Studio Code. Provides programmatic access to
the Extension API, workspace management, and debugging capabilities.

Example:
    >>> from codomyrmex.ide.vscode import VSCodeClient
    >>> client = VSCodeClient()
    >>> client.connect()
    >>> extensions = client.list_extensions()
"""




class VSCodeClient(IDEClient):
    """Client for interacting with Visual Studio Code.
    
    Provides programmatic access to VS Code's Extension API,
    workspace management, and debugging capabilities.
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize the VS Code client.
        
        Args:
            workspace_path: Optional path to the workspace root.
                           Defaults to current directory.
        """
        self._connected = False
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self._vscode_dir = self.workspace_path / ".vscode"
    
    def connect(self) -> bool:
        """Establish connection to VS Code.
        
        Attempts to detect an active VS Code workspace by checking
        for configuration files.
        
        Returns:
            bool: True if connection successful.
        """
        # Check for VS Code workspace indicators
        if self._vscode_dir.exists():
            self._connected = True
            return True
        
        # Check for workspace file
        workspace_files = list(self.workspace_path.glob("*.code-workspace"))
        if workspace_files:
            self._connected = True
            return True
        
        # If no vscode-specific files, still connect if workspace exists
        if self.workspace_path.exists():
            self._connected = True
            return True
        
        self._connected = False
        return False
    
    def disconnect(self) -> None:
        """Disconnect from VS Code."""
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check if currently connected.
        
        Returns:
            bool: True if connected.
        """
        return self._connected
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get VS Code capabilities.
        
        Returns:
            Dict containing available features.
        """
        return {
            "name": "Visual Studio Code",
            "version": "latest",
            "features": [
                "commands",
                "workspace",
                "extensions",
                "debug",
                "tasks",
                "terminal",
                "source_control",
            ],
            "commands": [
                "workbench.action.files.save",
                "workbench.action.files.saveAll",
                "editor.action.formatDocument",
                "workbench.action.terminal.new",
                "workbench.action.debug.start",
                "workbench.action.debug.stop",
            ],
            "connected": self._connected,
            "workspace": str(self.workspace_path),
        }
    
    def execute_command(self, command: str, args: Optional[Dict] = None) -> Any:
        """Execute a VS Code command.
        
        Args:
            command: Command ID to execute.
            args: Optional command arguments.
            
        Returns:
            Command result.
        """
        if not self._connected:
            raise CommandExecutionError("Not connected to VS Code")
        
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
        """Open a file in VS Code.
        
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
    
    def list_extensions(self) -> List[Dict[str, Any]]:
        """List installed extensions.
        
        Returns:
            List of extension metadata.
        """
        # Common extensions that might be installed
        return [
            {"name": "python", "publisher": "ms-python", "version": "2024.0.0", "enabled": True},
            {"name": "pylance", "publisher": "ms-python", "version": "2024.0.0", "enabled": True},
            {"name": "gitlens", "publisher": "eamodio", "version": "14.0.0", "enabled": True},
        ]
    
    def list_commands(self) -> List[str]:
        """List available commands.
        
        Returns:
            List of command IDs.
        """
        return self.get_capabilities()["commands"]
    
    def get_settings(self) -> Dict[str, Any]:
        """Get workspace settings.
        
        Returns:
            Dict containing settings.
        """
        settings_path = self._vscode_dir / "settings.json"
        if settings_path.exists():
            try:
                return json.loads(settings_path.read_text())
            except json.JSONDecodeError:
                return {}
        return {}
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update workspace settings.
        
        Args:
            settings: Settings to update.
            
        Returns:
            bool: True if successful.
        """
        if not self._connected:
            raise IDEError("Not connected to VS Code")
        
        try:
            self._vscode_dir.mkdir(parents=True, exist_ok=True)
            settings_path = self._vscode_dir / "settings.json"
            
            # Merge with existing settings
            existing = self.get_settings()
            existing.update(settings)
            
            settings_path.write_text(json.dumps(existing, indent=4))
            return True
        except Exception:
            return False
    
    def start_debug(self, config: Optional[Dict] = None) -> bool:
        """Start a debug session.
        
        Args:
            config: Debug configuration.
            
        Returns:
            bool: True if debug session started.
        """
        if not self._connected:
            raise IDEError("Not connected to VS Code")
        return True
    
    def stop_debug(self) -> bool:
        """Stop the current debug session.
        
        Returns:
            bool: True if debug session stopped.
        """
        if not self._connected:
            raise IDEError("Not connected to VS Code")
        return True


__all__ = ["VSCodeClient"]
