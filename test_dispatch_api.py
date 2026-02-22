import pytest
import threading
import time
import requests
from codomyrmex.website.server import WebsiteServer
from codomyrmex.website.data_provider import DataProvider
import http.server

from pathlib import Path

def test_dispatch_endpoint():
    WebsiteServer.data_provider = DataProvider(Path("."))
    
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), WebsiteServer)
    port = server.server_address[1]
    
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    
    try:
        url = f"http://127.0.0.1:{port}"
        payload = {
            "prompt": "Test dispatch",
            "todo_path": "TO-DO.md",
            "context_files": [],
            "architect": "ollama",
            "developer": "ollama",
            "reviewer": "ollama"
        }
        
        headers = {"Origin": "http://localhost:8000"}
        
        response = requests.post(f"{url}/api/agent/dispatch", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True
        
        time.sleep(1)
        status_response = requests.get(f"{url}/api/agent/dispatch/status", headers=headers)
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "summary" in status_data
        
        # Cleanup
        WebsiteServer._dispatch_orch.stop()
        
    finally:
        server.shutdown()
        server.server_close()

