#!/usr/bin/env python3
"""
Orchestrator script for generating the Codomyrmex website.
Can also serve the website and open it in the default browser.
Supports automatic port discovery if the default port is in use.
"""
import argparse
import socket
import sys
import socketserver
import functools
import webbrowser
import threading
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.website.generator import WebsiteGenerator
from codomyrmex.website.server import WebsiteServer
from codomyrmex.website.data_provider import DataProvider


def log_info(message: str) -> None:
    """Print an info message with prefix."""
    print(f"[INFO] {message}")


def log_success(message: str) -> None:
    """Print a success message with prefix."""
    print(f"[SUCCESS] {message}")


def log_error(message: str) -> None:
    """Print an error message with prefix to stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def is_port_available(port: int, host: str = "") -> bool:
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_open_port(start_port: int, max_attempts: int = 10) -> int:
    """
    Find an open port starting from start_port.
    
    Args:
        start_port: The preferred port to start searching from.
        max_attempts: Maximum number of ports to try.
        
    Returns:
        An available port number.
        
    Raises:
        RuntimeError: If no open port is found within max_attempts.
    """
    for offset in range(max_attempts):
        port = start_port + offset
        if is_port_available(port):
            return port
        log_info(f"Port {port} is in use, trying next...")
    
    raise RuntimeError(
        f"Could not find an open port in range {start_port}-{start_port + max_attempts - 1}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate and optionally serve the Codomyrmex website."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output/website",
        help="Directory to write the generated website to."
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve the website after generation."
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the website in the default browser (implies --serve)."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Preferred port to serve on (default: 8000). Will auto-discover if in use."
    )
    parser.add_argument(
        "--max-port-attempts",
        type=int,
        default=10,
        help="Maximum number of ports to try if preferred port is in use (default: 10)."
    )
    
    args = parser.parse_args()
    
    output_path = Path(args.output_dir).resolve()
    
    # 1. Generate Website
    log_info(f"Output directory: {output_path}")
    try:
        generator = WebsiteGenerator(output_dir=output_path, root_dir=PROJECT_ROOT)
        generator.generate()
        log_success(f"Website generated at: {output_path}/index.html")
    except Exception as e:
        log_error(f"Failed to generate website: {e}")
        sys.exit(1)

    # 2. Serve and/or Open
    if args.serve or args.open:
        # Find an available port
        try:
            port = find_open_port(args.port, args.max_port_attempts)
            if port != args.port:
                log_info(f"Using port {port} (preferred port {args.port} was in use)")
        except RuntimeError as e:
            log_error(str(e))
            sys.exit(1)

        # Configure Server
        WebsiteServer.root_dir = PROJECT_ROOT
        WebsiteServer.data_provider = DataProvider(PROJECT_ROOT)
        WebsiteServer.website_dir = output_path
        
        # Create handler using partial to pass the directory
        handler = functools.partial(WebsiteServer, directory=str(output_path))
        
        try:
            with socketserver.TCPServer(("", port), handler) as httpd:
                url = f"http://localhost:{port}"
                log_success(f"Server running at {url}")
                log_info(f"Serving content from: {output_path}")
                log_info("API endpoints active via WebsiteServer")
                log_info("Press Ctrl+C to stop.")
                
                if args.open:
                    log_info(f"Opening browser at {url}...")
                    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
                
                httpd.serve_forever()
        except OSError as e:
            log_error(f"Failed to start server: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            log_info("Shutting down server.")


if __name__ == "__main__":
    main()
