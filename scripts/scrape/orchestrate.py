#!/usr/bin/env python3
"""
Scrape Module Orchestrator

Thin orchestrator script providing CLI access to scrape module functionality.
Calls actual module functions from codomyrmex.scrape.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
    )

# Import module functions
from codomyrmex import scrape

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Retrieving scrape module information")

        info = {
            "module": "scrape",
            "description": "Web scraping tools with Firecrawl integration",
            "version": getattr(scrape, "__version__", "0.1.0"),
            "path": getattr(scrape, "__path__", ["unknown"])[0],
            "available_classes": ["Scraper", "ScrapeOptions", "ScrapeFormat"],
            "available_methods": ["scrape", "crawl", "map", "search", "extract"],
        }

        print_section("Scrape Module Information")
        print(format_output(info, format_type="json"))
        print_section("", separator="")

        print_success("Information retrieved")
        return True

    except Exception as e:
        logger.exception("Unexpected error retrieving information")
        print_error("Unexpected error retrieving information", exception=e)
        return False


def handle_scrape(args):
    """Handle scrape command - scrape a URL and optionally save to output directory."""
    try:
        url = args.url
        output_dir = Path(args.output_dir).resolve()
        output_format = args.format
        verbose = getattr(args, "verbose", False)
        
        if verbose:
            logger.info(f"Scraping URL: {url}")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Format: {output_format}")

        print_section(f"Scraping: {url}")

        # Import scraping classes
        from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

        # Determine formats to request
        format_map = {
            "markdown": [ScrapeFormat.MARKDOWN],
            "html": [ScrapeFormat.HTML],
            "json": [ScrapeFormat.JSON],
            "all": [ScrapeFormat.MARKDOWN, ScrapeFormat.HTML],
        }
        formats = format_map.get(output_format, [ScrapeFormat.MARKDOWN])
        
        # Create scraper and options
        try:
            scraper_instance = Scraper()
        except Exception as e:
            print_error(f"Failed to initialize scraper: {e}")
            print("\nNote: Firecrawl requires an API key.")
            print("Set FIRECRAWL_API_KEY environment variable or install firecrawl-py package.")
            return False
        
        options = ScrapeOptions(formats=formats)
        
        # Perform scrape
        result = scraper_instance.scrape(url, options)
        
        if not result.success:
            print_error(f"Scrape failed: {result.error}")
            return False

        # Prepare output
        output_data = {
            "url": result.url,
            "content": result.content,
            "status_code": result.status_code,
            "metadata": result.metadata,
            "formats": result.formats,
            "scraped_at": datetime.now().isoformat(),
        }

        print_success(f"Scraped {url} (status: {result.status_code})")
        
        # Show preview
        preview = result.content[:500] + "..." if len(result.content) > 500 else result.content
        print(f"\nContent preview:\n{preview}\n")

        # Save to output directory if specified
        if args.save:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            from urllib.parse import urlparse
            parsed = urlparse(url)
            safe_host = parsed.netloc.replace(".", "_").replace(":", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON result
            json_file = output_dir / f"{safe_host}_{timestamp}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, default=str)
            print_success(f"Saved JSON: {json_file}")
            
            # Save markdown content
            if result.content:
                md_file = output_dir / f"{safe_host}_{timestamp}.md"
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(f"# Scraped from {url}\n\n")
                    f.write(f"Scraped at: {datetime.now().isoformat()}\n\n")
                    f.write("---\n\n")
                    f.write(result.content)
                print_success(f"Saved Markdown: {md_file}")
            
            # Save HTML if available
            html_content = result.formats.get("html")
            if html_content:
                html_file = output_dir / f"{safe_host}_{timestamp}.html"
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print_success(f"Saved HTML: {html_file}")

        return True

    except Exception as e:
        logger.exception(f"Error scraping URL: {e}")
        print_error(f"Failed to scrape URL: {e}")
        return False


def handle_crawl(args):
    """Handle crawl command - crawl a website starting from URL."""
    try:
        url = args.url
        limit = args.limit
        output_dir = Path(args.output_dir).resolve()
        verbose = getattr(args, "verbose", False)
        
        if verbose:
            logger.info(f"Crawling URL: {url} (limit: {limit})")

        print_section(f"Crawling: {url} (limit: {limit})")

        from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat
        
        try:
            scraper_instance = Scraper()
        except Exception as e:
            print_error(f"Failed to initialize scraper: {e}")
            return False
        
        options = ScrapeOptions(limit=limit, formats=[ScrapeFormat.MARKDOWN])
        result = scraper_instance.crawl(url, options)
        
        print_success(f"Crawl job created: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Total pages: {result.total}, Completed: {result.completed}")
        
        if args.save and result.results:
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save crawl results summary
            summary_file = output_dir / f"crawl_{timestamp}.json"
            summary = {
                "job_id": result.job_id,
                "status": result.status,
                "total": result.total,
                "completed": result.completed,
                "results": [{"url": r.url, "content_length": len(r.content)} for r in result.results],
                "crawled_at": datetime.now().isoformat(),
            }
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            print_success(f"Saved crawl summary: {summary_file}")

        return True

    except Exception as e:
        logger.exception(f"Error crawling URL: {e}")
        print_error(f"Failed to crawl URL: {e}")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Scrape operations - web scraping with Firecrawl integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
  %(prog)s scrape https://example.com
  %(prog)s scrape https://example.com --save --output-dir output/scrape
  %(prog)s scrape https://example.com --format html --save
  %(prog)s crawl https://example.com --limit 10 --save
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get scrape module information")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape a single URL")
    scrape_parser.add_argument("url", help="URL to scrape")
    scrape_parser.add_argument(
        "--output-dir", "-o",
        default="output/scrape",
        help="Output directory for saved files (default: output/scrape)"
    )
    scrape_parser.add_argument(
        "--format", "-f",
        choices=["markdown", "html", "json", "all"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    scrape_parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save scraped content to output directory"
    )

    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a website from a starting URL")
    crawl_parser.add_argument("url", help="Starting URL to crawl")
    crawl_parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Maximum number of pages to crawl (default: 10)"
    )
    crawl_parser.add_argument(
        "--output-dir", "-o",
        default="output/scrape",
        help="Output directory for saved files (default: output/scrape)"
    )
    crawl_parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save crawl results to output directory"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "info": handle_info,
        "scrape": handle_scrape,
        "crawl": handle_crawl,
    }

    handler = handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print_error("Unknown command", context=args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())
