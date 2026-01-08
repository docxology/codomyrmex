
import os
import time
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse

# Configuration
BASE_URL = "https://ai.google.dev/gemini-api/docs"
OUTPUT_DIR = "output/gemini_docs"
DELAY = 0.5  # Seconds between requests

visited_urls = set()
urls_to_visit = [BASE_URL]

def normalize_url(url):
    """Normalize URL to avoid duplicates (remove fragments, etc.)."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def is_valid_url(url):
    """Check if the URL belongs to the target domain and path."""
    return url.startswith(BASE_URL)

def save_content(url, content):
    """Save the content to a file structure mirroring the URL."""
    parsed = urlparse(url)
    path = parsed.path
    
    # Remove the base path prefix to get relative path
    base_path_prefix = "/gemini-api/docs"
    if path.startswith(base_path_prefix):
        rel_path = path[len(base_path_prefix):]
    else:
        rel_path = path

    # Handle root or empty path
    if not rel_path or rel_path == "/":
        rel_path = "/index"
    
    # Ensure no leading slash for joining
    if rel_path.startswith("/"):
        rel_path = rel_path[1:]

    # Construct file path
    file_path = os.path.join(OUTPUT_DIR, rel_path)
    if not file_path.endswith(".md"):
        file_path += ".md"
        
    # Create directories
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {file_path}")

def scrape_url(url):
    """Scrape a single URL and return found links."""
    try:
        print(f"Scraping: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main content (adjust selector based on site structure if needed)
        # For ai.google.dev, content is often in <main> or specifically marked containers.
        # We'll default to 'main' or 'body' if 'main' is missing.
        main_content = soup.find('main') or soup.body
        
        if not main_content:
            print(f"No content found for {url}")
            return []

        # Convert to Markdown
        markdown_content = md(str(main_content), heading_style="ATX", stripper_class=None)
        
        # Add metadata
        final_content = f"# Source: {url}\n\n{markdown_content}"
        save_content(url, final_content)

        # Find links
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            # Remove fragment for crawling logic
            normalized = normalize_url(full_url)
            
            if is_valid_url(normalized) and normalized not in visited_urls:
                links.append(normalized)
        
        return links

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scrape Gemini Docs")
    parser.add_argument("--check", action="store_true", help="Run in check mode (verify imports only)")
    args = parser.parse_args()

    if args.check:
        print("✅ Check mode: Imports and setup successful")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue
            
        visited_urls.add(current_url)
        
        new_links = scrape_url(current_url)
        
        # specialized logic: avoid adding too many if not needed, 
        # but here we want recursive BFS. 
        # We add unique new links to the list.
        for link in new_links:
            if link not in visited_urls and link not in urls_to_visit:
                urls_to_visit.append(link)
        
        time.sleep(DELAY)

if __name__ == "__main__":
    main()
