import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


class EchoHandler(BaseHTTPRequestHandler):
    """
    HTTP Handler that echoes back the request details in JSON format.
    Supports GET, POST, PUT, DELETE, and header inspection.
    Mimics httpbin.org functionality locally.
    """

    def _send_response_json(self, data: dict[str, Any], status_code: int = 200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        # Handle specific status codes
        if self.path.startswith("/status/"):
            try:
                code = int(self.path.split("/")[-1])
                self.send_response(code)
                self.end_headers()
                return
            except ValueError:
                pass

        # Echo request details
        data = {
            "url": f"http://{self.headers.get('Host')}{self.path}",
            "headers": dict(self.headers),
            "args": {},  # Query params parsing could be added if needed
            "origin": self.client_address[0]
        }
        self._send_response_json(data)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            json_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            json_data = None

        data = {
            "url": f"http://{self.headers.get('Host')}{self.path}",
            "headers": dict(self.headers),
            "data": post_data.decode('utf-8'),
            "json": json_data,
            "origin": self.client_address[0]
        }
        self._send_response_json(data)

    def do_PUT(self):
        self.do_POST() # Same logic for echo

    def do_DELETE(self):
        data = {
             "url": f"http://{self.headers.get('Host')}{self.path}",
             "headers": dict(self.headers),
             "origin": self.client_address[0]
        }
        self._send_response_json(data)


class EphemeralServer:
    """
    Context manager for a temporary local HTTP server.
    """
    def __init__(self, host="127.0.0.1", port=0):
        self.server = HTTPServer((host, port), EchoHandler)
        self.host, self.port = self.server.server_address
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"
