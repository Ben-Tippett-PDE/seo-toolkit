#!/usr/bin/env python3
"""
Broken Link Finder - Website Link Checker
Built by Perth Digital Edge (https://perthdigitaledge.com.au)

Crawls a website and identifies broken internal and external links
that negatively impact SEO and user experience.
"""

import argparse
import json
import csv
import sys
from urllib.parse import urlparse, urljoin
from collections import defaultdict

try:
    import requests
    from bs4 import BeautifulSoup
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


def get_all_links(url, soup):
    """Extract all links from a page."""
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute_url = urljoin(url, href)
        links.append({
            "url": absolute_url,
            "anchor_text": tag.get_text(strip=True)[:100],
            "source_page": url,
        })
    return links


def check_url(url, timeout=10):
    """Check if a URL is accessible. Returns status code."""
    headers = {
        "User-Agent": "SEO-Toolkit/1.0 (Perth Digital Edge; https://perthdigitaledge.com.au)"
    }
    try:
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        if response.status_code == 405:
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        return response.status_code
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR"
    except requests.exceptions.RequestException:
        return "ERROR"


def crawl_site(start_url, max_depth=2, max_pages=50):
    """Crawl a website and check all links."""
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc

    visited = set()
    to_visit = [(start_url, 0)]
    all_results = []
    broken_links = []

    print(f"\nCrawling {start_url} (max depth: {max_depth}, max pages: {max_pages})...\n")

    while to_visit and len(visited) < max_pages:
        current_url, depth = to_visit.pop(0)

        if current_url in visited:
            continue
        visited.add(current_url)

        print(f"  Checking: {current_url[:80]}...")

        headers = {
            "User-Agent": "SEO-Toolkit/1.0 (Perth Digital Edge; https://perthdigitaledge.com.au)"
        }

        try:
            response = requests.get(current_url, headers=headers, timeout=15)
        except requests.exceptions.RequestException as e:
            broken_links.append({
                "url": current_url,
                "status": "ERROR",
                "source_page": "start",
                "anchor_text": "",
            })
            continue

        if response.status_code >= 400:
            broken_links.append({
                "url": current_url,
                "status": response.status_code,
                "source_page": "direct",
                "anchor_text": "",
            })
            continue

        soup = BeautifulSoup(response.text, "lxml")
        links = get_all_links(current_url, soup)

        for link in links:
            link_url = link["url"]
            status = check_url(link_url)
            result = {**link, "status": status}
            all_results.append(result)

            if isinstance(status, int) and status >= 400:
                broken_links.append(result)
                if HAS_DEPS:
                    print(f"  {Fore.RED}â [{status}]{Style.RESET_ALL} {link_url[:70]}")
            elif isinstance(status, str):
                broken_links.append(result)
                if HAS_DEPS:
                    print(f"  {Fore.RED}â [{status}]{Style.RESET_ALL} {link_url[:70]}")

            # Queue internal links for further crawling
            parsed_link = urlparse(link_url)
            if (parsed_link.netloc == base_domain
                    and link_url not in visited
                    and depth < max_depth):
                to_visit.append((link_url, depth + 1))

    return all_results, broken_links, len(visited)


def print_report(broken_links, total_checked, pages_crawled):
    """Print the broken link report."""
    print(f"\n{'='*60}")
    print(f"  Broken Link Report â Perth Digital Edge")
    print(f"{'='*60}\n")
    print(f"  Pages crawled: {pages_crawled}")
    print(f"  Total links checked: {total_checked}")
    print(f"  Broken links found: {len(broken_links)}\n")

    if broken_links:
        if HAS_DEPS:
            print(f"{Fore.RED}  BROKEN LINKS:{Style.RESET_ALL}\n")
        else:
            print("  BROKEN LINKS:\n")

        for link in broken_links:
            print(f"  [{link['status']}] {link['url']}")
            if link.get("anchor_text"):
                print(f"       Anchor: \"{link['anchor_text'][:60]}\"")
            if link.get("source_page"):
                print(f"       Found on: {link['source_page'][:70]}")
            print()
    else:
        if HAS_DEPS:
            print(f"  {Fore.GREEN}No broken links found!{Style.RESET_ALL}\n")
        else:
            print("  No broken links found!\n")

    print(f"  Powered by Perth Digital Edge")
    print(f"  https://perthdigitaledge.com.au")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Broken Link Finder by Perth Digital Edge (https://perthdigitaledge.com.au)"
    )
    parser.add_argument("url", help="Website URL to check for broken links")
    parser.add_argument("--depth", type=int, default=2, help="Maximum crawl depth (default: 2)")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to crawl (default: 50)")
    parser.add_argument("--json", dest="json_file", help="Export results to JSON file")
    parser.add_argument("--csv", dest="csv_file", help="Export results to CSV file")
    args = parser.parse_args()

    if not HAS_DEPS:
        print("Missing dependencies. Run: pip install -r requirements.txt")
        sys.exit(1)

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    all_results, broken_links, pages_crawled = crawl_site(url, args.depth, args.max_pages)
    print_report(broken_links, len(all_results), pages_crawled)

    if args.json_file:
        with open(args.json_file, "w") as f:
            json.dump({"broken_links": broken_links, "total_checked": len(all_results)}, f, indent=2)
        print(f"Results saved to {args.json_file}")

    if args.csv_file:
        with open(args.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Status", "Anchor Text", "Source Page"])
            for link in broken_links:
                writer.writerow([link["url"], link["status"], link.get("anchor_text", ""), link.get("source_page", "")])
        print(f"Results saved to {args.csv_file}")


if __name__ == "__main__":
    main()
