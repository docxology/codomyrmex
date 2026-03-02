#!/usr/bin/env python3
"""
Web scraping utilities.

Usage:
    python scrape_utils.py <url> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import urllib.request
import urllib.error
import re
import json
from html.parser import HTMLParser


class LinkExtractor(HTMLParser):
    """Extract links from HTML."""
    
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_tag = None
        self.current_text = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append({"href": href, "text": ""})
                self.current_tag = "a"
    
    def handle_data(self, data):
        if self.current_tag == "a" and self.links:
            self.links[-1]["text"] = data.strip()
    
    def handle_endtag(self, tag):
        if tag == "a":
            self.current_tag = None


class MetaExtractor(HTMLParser):
    """Extract meta tags from HTML."""
    
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.title = ""
        self.in_title = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            attrs_dict = dict(attrs)
            name = attrs_dict.get("name") or attrs_dict.get("property")
            content = attrs_dict.get("content")
            if name and content:
                self.meta[name] = content
        elif tag == "title":
            self.in_title = True
    
    def handle_data(self, data):
        if self.in_title:
            self.title = data.strip()
    
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False


def fetch_url(url: str, timeout: int = 30) -> dict:
    """Fetch URL content."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "codomyrmex-scraper/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                "status": response.status,
                "content": response.read().decode(errors="ignore"),
                "headers": dict(response.headers),
                "url": response.url
            }
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": str(e.reason)}
    except Exception as e:
        return {"error": str(e)}


def extract_text(html: str) -> str:
    """Extract text from HTML, removing tags."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="Web scraping utilities")
    parser.add_argument("url", nargs="?", help="URL to scrape")
    parser.add_argument("--links", "-l", action="store_true", help="Extract links")
    parser.add_argument("--meta", "-m", action="store_true", help="Extract meta tags")
    parser.add_argument("--text", "-t", action="store_true", help="Extract text content")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Save to file")
    args = parser.parse_args()
    
    if not args.url:
        print("🌐 Scrape Utilities\n")
        print("Usage:")
        print("  python scrape_utils.py https://example.com")
        print("  python scrape_utils.py https://example.com --links")
        print("  python scrape_utils.py https://example.com --meta")
        print("  python scrape_utils.py https://example.com --text")
        return 0
    
    print(f"🌐 Fetching: {args.url}\n")
    
    result = fetch_url(args.url)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return 1
    
    html = result.get("content", "")
    output = {"url": args.url, "status": result["status"]}
    
    if args.links:
        extractor = LinkExtractor()
        extractor.feed(html)
        output["links"] = extractor.links
        
        if not args.json:
            print(f"🔗 Links ({len(extractor.links)}):\n")
            for link in extractor.links[:20]:
                text = link["text"][:30] if link["text"] else "(no text)"
                print(f"   {text} → {link['href'][:60]}")
    
    if args.meta:
        extractor = MetaExtractor()
        extractor.feed(html)
        output["title"] = extractor.title
        output["meta"] = extractor.meta
        
        if not args.json:
            print(f"📄 Title: {extractor.title}\n")
            print("📋 Meta tags:")
            for key, value in list(extractor.meta.items())[:15]:
                print(f"   {key}: {value[:60]}")
    
    if args.text:
        text = extract_text(html)
        output["text"] = text[:5000]
        
        if not args.json:
            print(f"📝 Text ({len(text)} chars):\n")
            print(f"   {text[:500]}...")
    
    if not args.links and not args.meta and not args.text:
        print(f"✅ Status: {result['status']}")
        print(f"   Content length: {len(html)} chars")
    
    if args.json:
        print(json.dumps(output, indent=2))
    
    if args.output:
        Path(args.output).write_text(json.dumps(output, indent=2))
        print(f"\n💾 Saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
