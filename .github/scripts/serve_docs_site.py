"""Serve a static build the way GitHub Pages does.

Two behaviours matter for an honest Lighthouse reading:

* the site is served under its /codomyrmex/ base path (the layout is prepared by
  the shell wrapper, which symlinks the build into place);
* text assets are gzipped when the client accepts it. GitHub Pages compresses
  these responses; Python's http.server does not, and serving 1.76 MB of
  uncompressed JavaScript over a 1.6 Mbps emulated link turns a transfer
  question into a false conclusion about the site.
"""

import gzip
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

ROOT = os.path.abspath(sys.argv[1])
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 4173
COMPRESSIBLE = {".html", ".js", ".css", ".json", ".svg", ".xml", ".txt", ".map"}
_cache = {}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):  # noqa: N802 - http.server API
        path = self.translate_path(urlsplit(self.path).path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        extension = os.path.splitext(path)[1].lower()
        accepts_gzip = "gzip" in self.headers.get("Accept-Encoding", "").lower()
        if accepts_gzip and extension in COMPRESSIBLE and os.path.isfile(path):
            body = _cache.get(path)
            if body is None:
                with open(path, "rb") as handle:
                    body = gzip.compress(handle.read(), 9)
                _cache[path] = body
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *args):  # keep the collector's output readable
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
