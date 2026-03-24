#!/usr/bin/env python3
"""
Sitemap Validator - XML Sitemap Checker
Built by Perth Digital Edge (https://perthdigitaledge.com.au)

Validates XML sitemaps for:
- Correct XML structure
- URL accessibility (status codes)
- Lastmod date formatting
- Sitemap size limits
"""

import argparse
import json
import sys
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


MAX_URLS_PER_SITEMAP = 50000
MAX_SITEMAP_SIZE_MB = 50


def fetch_sitemap(url):
    """Fetch and parse an XML sitemap."""
    headers = {
        "User-Agent": "SEO-Toolkit/1.0 (Perth Digital Edge; https://perthdigitaledge.com.au)"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response


def validate_sitemap(url, check_urls=True, max_check=100):
    """Validate an XML sitemap and return results."""
    results = {
        "url": url,
        "issues": [],
        "warnings": [],
        "passed": [],
        "urls_found": 0,
        "urls_checked": 0,
        "urls_broken": [],
    }

    response = fetch_sitemap(url)
    size_mb = len(response.content) / (1024 * 1024)

    if size_mb > MAX_SITEMAP_SIZE_MB:
        results["issues"].append(f"Sitemap exceeds {MAX_SITEMAP_SIZE_MB}MB limit ({size_mb:.1f}MB).")
    else:
        results["passed"].append(f"Sitemap size OK ({size_mb:.2f}MB).")

    # Check content type
    content_type = response.headers.get("Content-Type", "")
    if "xml" in content_type or url.endswith(".xml"):
        results["passed"].append("Content type is XML.")
    else:
        results["warnings"].append(f"Content-Type is '{content_type}', expected XML.")

    soup = BeautifulSoup(response.text, "lxml-xml")

    # Check for sitemap index
    sitemaps = soup.find_all("sitemap")
    if sitemaps:
        results["type"] = "sitemap_index"
        results["passed"].append(f"Valid sitemap index with {len(sitemaps)} sitemaps.")
        for sm in sitemaps:
            loc = sm.find("loc")
            if loc:
                results["passed"].append(f"  Sub-sitemap: {loc.text}")
        return results

    # Regular sitemap
    urls = soup.find_all("url")
    results["urls_found"] = len(urls)
    results["type"] = "urlset"

    if len(urls) == 0:
        results["issues"].append("No <url> entries found in sitemap.")
        return results

    if len(urls) > MAX_URLS_PER_SITEMAP:
        results["issues"].append(f"Sitemap exceeds {MAX_URLS_PER_SITEMAP} URL limit ({len(urls)} URLs).")
    else:
        results["passed"].append(f"URL count within limits ({len(urls)}/{MAX_URLS_PER_SITEMAP}).")

    # Validate entries
    missing_loc = 0
    invalid_dates = 0
    checked = 0

    for entry in urls:
        loc = entry.find("loc")
        if not loc or not loc.text.strip():
            missing_loc += 1
            continue

        # Validate lastmod
        lastmod = entry.find("lastmod")
        if lastmod and lastmod.text.strip():
            try:
                date_str = lastmod.text.strip()

                if "T" in date_str:
                    datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                invalid_dates += 1

        # Check URL accessibility
        if check_urls and checked < max_check:
            try:
                headers = {"User-Agent": "SEO-Toolkit/1.0 (Perth Digital Edge)"}
                r = requests.head(loc.text.strip(), headers=headers, timeout=10, allow_redirects=True)
                if r.status_code >= 400:
                    results["urls_broken"].append({"url": loc.text.strip(), "status": r.status_code})
                checked += 1
            except requests.exceptions.RequestException:
                results["urls_broken"].append({"url": loc.text.strip(), "status": "ERROR"})
                checked += 1

    results["urls_checked"] = checked

    if missing_loc > 0:
        results["issues"].append(f"{missing_loc} entries missing <loc> element.")
    if invalid_dates > 0:
        results["warnings"].append(f"{invalid_dates} entries have invalid <lastmod> date format.")
    if results["urls_broken"]:
        results["issues"].append(f"{len(results['urls_broken'])} URLs returned errors.")
    else:
        results["passed"].append("All checked URLs are accessible.")

    return results


def print_results(results):
    """Print validation results."""
    print(f"\n{'='*60}")
    print(f"  Sitemap Validation Report â Perth Digital Edge")
    print(f"  {results['url']}")
    print(f"{'='*60}\n")

    print(f"  Type: {results.get('type', 'unknown')}")
    print(f"  URLs found: {results['urls_found']}")
    print(f"  URLs checked: {results['urls_checked']}")
    print()

    if results["issues"]:
        if HAS_DEPS:
            print(f"{Fore.RED}  ISSUES ({len(results['issues'])}){Style.RESET_ALL}")
        for issue in results["issues"]:
            print(f"  â {issue}")
        print()

    if results["warnings"]:
        if HAS_DEPS:
            print(f"{Fore.YELLOW}  WARNINGS ({len(results['warnings'])}){Style.RESET_ALL}")
        for warning in results["warnings"]:
            print(f"  ! {warning}")
        print()

    if results["passed"]:
        if HAS_DEPS:
            print(f"{Fore.GREEN}  PASSED ({len(results['passed'])}){Style.RESET_ALL}")
        for passed in results["passed"]:
            print(f"  â {passed}")
        print()

    if results["urls_broken"]:
        print("  BROKEN URLs:")
        for broken in results["urls_broken"]:
            print(f"    [{broken['status']}] {broken['url']}")
        print()

    print(f"  Powered by Perth Digital Edge")
    print(f"  https://perthdigitaledge.com.au")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Sitemap Validator by Perth Digital Edge (https://perthdigitaledge.com.au)"
    )
    parser.add_argument("url", help="Sitemap URL to validate")
    parser.add_argument("--no-check", action="store_true", help="Skip URL accessibility checks")
    parser.add_argument("--max-check", type=int, default=100, help="Max URLs to check (default: 100)")
    parser.add_argument("--json", dest="json_file", help="Export results to JSON file")
    args = parser.parse_args()

    if not HAS_DEPS:
        print("Missing dependencies. Run: pip install -r requirements.txt")
        sys.exit(1)

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        results = validate_sitemap(url, check_urls=not args.no_check, max_check=args.max_check)
        print_results(results)

        if args.json_file:
            with open(args.json_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to {args.json_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
