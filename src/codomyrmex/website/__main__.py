"""Entry point for running the Codomyrmex web viewer.

Usage: python -m codomyrmex.website
"""

import os
import socketserver
from pathlib import Path

from .generator import WebsiteGenerator
from .server import WebsiteServer


def main(port: int = 8787) -> None:
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    output_dir = root_dir / "output" / "website"

    # Generate the static site
    generator = WebsiteGenerator(str(output_dir), str(root_dir))
    generator.generate()

    # Configure the server
    os.chdir(output_dir)
    WebsiteServer.root_dir = root_dir
    WebsiteServer.data_provider = generator.data_provider

    print(f"\n🌐 Codomyrmex viewer running at http://localhost:{port}")
    print("   Press Ctrl+C to stop\n")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), WebsiteServer) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n   Server stopped.")


if __name__ == "__main__":
    main()
