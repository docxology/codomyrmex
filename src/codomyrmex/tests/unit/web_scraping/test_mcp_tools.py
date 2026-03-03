import http.server
import socketserver
import threading
import time

import pytest

from codomyrmex.web_scraping.mcp_tools import (
    scraping_extract_links,
    scraping_fetch_page,
    scraping_get_text,
)


class MockServerRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/test.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Page</title>
                <script>var x = 1;</script>
                <style>body { color: black; }</style>
            </head>
            <body>
                <h1>Hello World</h1>
                <p>This is a <b>test</b> page.</p>
                <a href="/link1">Link 1</a>
                <a href="https://example.com">External Link</a>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode("utf-8"))
        elif self.path == "/error":
            self.send_response(500)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress logging
        pass


@pytest.fixture(scope="module")
def local_server():
    # Set up a local HTTP server
    handler = MockServerRequestHandler
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to start
    time.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    httpd.shutdown()
    httpd.server_close()
    server_thread.join()


def test_scraping_fetch_page_success(local_server):
    url = f"{local_server}/test.html"
    result = scraping_fetch_page(url)

    assert result["status"] == "success"
    assert "url" in result
    assert result["url"] == url
    assert "<html>" in result["html"]
    assert "Test Page" in result["html"]


def test_scraping_fetch_page_error(local_server):
    url = f"{local_server}/error"
    result = scraping_fetch_page(url)

    assert result["status"] == "error"
    assert "message" in result
    assert "HTTP Error 500" in result["message"]


def test_scraping_fetch_page_invalid_url():
    result = scraping_fetch_page("http://invalid.domain.that.does.not.exist.codomyrmex")
    assert result["status"] == "error"


def test_scraping_extract_links(local_server):
    url = f"{local_server}/test.html"
    result = scraping_extract_links(url)

    assert result["status"] == "success"
    assert "links" in result

    links = result["links"]
    assert len(links) == 2
    assert any(link == f"{local_server}/link1" for link in links)
    assert any(link == "https://example.com" for link in links)


def test_scraping_extract_links_error(local_server):
    url = f"{local_server}/error"
    result = scraping_extract_links(url)

    assert result["status"] == "error"
    assert "message" in result


def test_scraping_get_text(local_server):
    url = f"{local_server}/test.html"
    result = scraping_get_text(url)

    assert result["status"] == "success"
    assert "text" in result

    text = result["text"]

    # Check that text is extracted
    assert "Hello World" in text
    assert "This is a test page." in text

    # Check that script/style/title contents are excluded
    assert "var x = 1" not in text
    assert "color: black" not in text
    assert "Test Page" not in text


def test_scraping_get_text_error(local_server):
    url = f"{local_server}/error"
    result = scraping_get_text(url)

    assert result["status"] == "error"
    assert "message" in result
