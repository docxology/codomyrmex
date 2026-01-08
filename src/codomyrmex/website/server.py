import http.server
import socketserver
import json
import subprocess
import os
import sys
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

from .data_provider import DataProvider
from codomyrmex.logging_monitoring import get_logger


logger = get_logger(__name__)

class WebsiteServer(http.server.SimpleHTTPRequestHandler):
    """
    Enhanced HTTP server that supports API endpoints for dynamic functionality.
    """
    
    # Class-level configuration to be set before starting the server
    root_dir: Path = Path(".")
    data_provider: Optional[DataProvider] = None
    
    def __init__(self, *args, **kwargs):
        # Ensure we serve files from the output directory
        # The 'directory' argument is set by the socketserver/HTTPServer logic usually,
        # but SimpleHTTPRequestHandler defaults to cwd using os.getcwd() if not specified in newer pythons
        # or just os.getcwd() in older ones. 
        # For this implementation, we expect the cwd to be set to the website output directory by the caller.
        """Brief description of __init__."""
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle API requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/api/execute":
            self.handle_execute()
        elif parsed_path.path == "/api/chat":
            self.handle_chat()
        elif parsed_path.path == "/api/refresh":
            self.handle_refresh()
        elif parsed_path.path.startswith("/api/config"):
            self.handle_config_save()
        else:
            self.send_error(404, "Endpoint not found")

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/api/config":
            self.handle_config_list()
        elif parsed_path.path.startswith("/api/config/"):
            self.handle_config_get(parsed_path.path)
        elif parsed_path.path == "/api/docs":
            self.handle_docs_list()
        elif parsed_path.path.startswith("/api/docs/"):
            # If requesting a specific doc, return it rendered?
            pass
        elif parsed_path.path == "/api/pipelines":
            self.handle_pipelines_list()
        else:
            super().do_GET()

    def handle_config_list(self):
        """Brief description of handle_config_list."""
        if self.data_provider:
            data = self.data_provider.get_config_files()
            self.send_json_response(data)
        else:
            self.send_error(500)

    def handle_config_get(self, path: str):
        """Brief description of handle_config_get."""
        filename = path.replace("/api/config/", "")
        if self.data_provider:
            try:
                content = self.data_provider.get_config_content(filename)
                self.send_json_response({"content": content})
            except Exception as e:
                self.send_error(404, str(e))

    def handle_config_save(self):
        """Brief description of handle_config_save."""
        parsed_path = urlparse(self.path)
        filename = parsed_path.path.replace("/api/config/", "")
         
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
         
        if self.data_provider:
            try:
                self.data_provider.save_config_content(filename, data.get('content'))
                self.send_json_response({"success": True})
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)

    def handle_docs_list(self):
        """Brief description of handle_docs_list."""
        if self.data_provider:
            data = self.data_provider.get_doc_tree()
            self.send_json_response(data)
        else:
            self.send_error(500)

    def handle_pipelines_list(self):
        """Brief description of handle_pipelines_list."""
        if self.data_provider:
            data = self.data_provider.get_pipeline_status()
            self.send_json_response(data)
        else:
            self.send_error(500)


    def handle_execute(self):
        """Execute a script from the scripts directory."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        script_name = data.get('script')
        args = data.get('args', [])
        
        if not script_name:
            self.send_error(400, "Script name required")
            return

        # Security check: ensure script is within scripts dir
        script_path = (self.root_dir / "scripts" / script_name).resolve()
        scripts_root = (self.root_dir / "scripts").resolve()
        
        if not str(script_path).startswith(str(scripts_root)) or not script_path.exists():
            self.send_error(403, f"Invalid script path: {script_name}")
            return

        try:
            # Run the script using the current python executable
            cmd = [sys.executable, str(script_path)] + args
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            # Ensure we capture both stdout and stderr
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=self.root_dir, # Run from project root
                timeout=300 # 5 minute timeout safety
            )
            
            response = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
            self.send_json_response(response)
            
        except subprocess.TimeoutExpired:
            self.send_json_response({
                "success": False, 
                "error": "Script execution timed out after 300 seconds",
                "stderr": "TimeoutExpired"
            }, status=504)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, status=500)

    def handle_chat(self):
        """Proxy chat requests to Ollama."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        ollama_url = "http://localhost:11434/api/chat"
        
        # Get the message from frontend
        user_message = data.get('message', '')
        model = data.get('model', 'llama3')  # Default to llama3
        
        # Format for Ollama API
        ollama_payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "stream": False  # Non-streaming for simplicity
        }
        
        # If the frontend already sends proper format, use it
        if 'messages' in data:
            ollama_payload = {
                "model": data.get('model', 'llama3'),
                "messages": data['messages'],
                "stream": False
            }
        
        try:
            ollama_resp = requests.post(ollama_url, json=ollama_payload, timeout=60)
            
            if ollama_resp.status_code == 200:
                result = ollama_resp.json()
                # Extract the assistant's message
                response_text = result.get('message', {}).get('content', 'No response')
                
                self.send_json_response({
                    "response": response_text,
                    "model": model,
                    "success": True
                })
            else:
                self.send_json_response({
                    "error": f"Ollama error: {ollama_resp.status_code} - {ollama_resp.text[:200]}"
                }, status=502)

        except requests.exceptions.ConnectionError:
            self.send_json_response({"error": "Ollama service not reachable. Is it running?"}, status=503)
        except requests.exceptions.Timeout:
            self.send_json_response({"error": "Ollama request timed out"}, status=504)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_refresh(self):
        """Refresh system data."""
        if self.data_provider:
            data = {
                "system": self.data_provider.get_system_summary(),
                "agents": self.data_provider.get_agents_status(),
                "scripts": self.data_provider.get_available_scripts()
            }
            self.send_json_response(data)
        else:
            self.send_error(500, "Data provider not initialized")

    def send_json_response(self, data, status=200):
        """Brief description of send_json_response."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
