#!/usr/bin/env python3
"""
SEO Audit Tool - Meta Tag Analyser & Page Checker
Built by Perth Digital Edge (https://perthdigitaledge.com.au)

Analyses any URL for SEO best practices including:
- Title tag length and quality
- Meta description analysis
- Open Graph tags
- Canonical URL validation
- Heading structure (H1-H6)
- Image alt text coverage
"""

import argparse
import json
import csv
import sys
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


TITLE_MIN = 30
TITLE_MAX = 60
DESC_MIN = 120
DESC_MAX = 160


def fetch_page(url):
    """Fetch a webpage and return the response."""
    headers = {
        "User-Agent": "SEO-Toolkit/1.0 (Perth Digital Edge; https://perthdigitaledge.com.au)"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response


def analyse_meta_tags(soup, url):
    """Analyse meta tags and return findings."""
    results = {
        "url": url,
        "issues": [],
        "warnings": [],
        "passed": [],
    }

    # Title tag
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        title = title_tag.string.strip()
        results["title"] = title
        title_len = len(title)
        if title_len < TITLE_MIN:
            results["issues"].append(f"Title too short ({title_len} chars). Aim for {TITLE_MIN}-{TITLE_MAX} characters.")
        elif title_len > TITLE_MAX:
            results["warnings"].append(f"Title may be truncated ({title_len} chars). Recommended: {TITLE_MIN}-{TITLE_MAX} characters.")
        else:
            results["passed"].append(f"Title length is good ({title_len} chars).")
    else:
        results["issues"].append("Missing <title> tag.")
        results["title"] = None

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc["content"].strip()
        results["meta_description"] = desc
        desc_len = len(desc)
        if desc_len < DESC_MIN:
            results["warnings"].append(f"Meta description short ({desc_len} chars). Aim for {DESC_MIN}-{DESC_MAX} characters.")
        elif desc_len > DESC_MAX:
            results["warnings"].append(f"Meta description may be truncated ({desc_len} chars). Recommended max: {DESC_MAX} characters.")
        else:
            results["passed"].append(f"Meta description length is good ({desc_len} chars).")
    else:
        results["issues"].append("Missing meta description.")
        results["meta_description"] = None

    # Canonical URL
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical and canonical.get("href"):
        results["canonical"] = canonical["href"]
        results["passed"].append(f"Canonical URL set: {canonical['href']}")
    else:
        results["warnings"].append("No canonical URL specified.")
        results["canonical"] = None

    # Open Graph tags
    og_tags = {}
    for og in soup.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")}):
        og_tags[og["property"]] = og.get("content", "")

    if "og:title" in og_tags:
        results["passed"].append("Open Graph title present.")
    else:
        results["warnings"].append("Missing og:title tag.")

    if "og:description" in og_tags:
        results["passed"].append("Open Graph description present.")
    else:
        results["warnings"].append("Missing og:description tag.")

    if "og:image" in og_tags:
        results["passed"].append("Open Graph image present.")
    else:
        results["warnings"].append("Missing og:image tag.")

    results["og_tags"] = og_tags

    # Heading structure
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        if tags:
            headings[f"h{level}"] = len(tags)

    h1_count = headings.get("h1", 0)
    if h1_count == 0:
        results["issues"].append("No H1 tag found on the page.")
    elif h1_count == 1:
        results["passed"].append("Single H1 tag present (good practice).")
    else:
        results["warnings"].append(f"Multiple H1 tags found ({h1_count}). Best practice is one H1 per page.")

    results["headings"] = headings

    # Image alt text
    images = soup.find_all("img")
    images_without_alt = [img.get("src", "unknown") for img in images if not img.get("alt")]
    total_images = len(images)
    missing_alt = len(images_without_alt)

    if total_images > 0:
        if missing_alt == 0:
            results["passed"].append(f"All {total_images} images have alt text.")
        else:
            pct = round((missing_alt / total_images) * 100)
            results["warnings"].append(f"{missing_alt}/{total_images} images missing alt text ({pct}%).")

    results["images_total"] = total_images
    results["images_missing_alt"] = missing_alt

    return results


def print_results(results):
    """Print results with colour formatting."""
    if not HAS_DEPS:
        print(json.dumps(results, indent=2))
        return

    print(f"\n{'='*60}")
    print(f"  SEO Audit Report — Perth Digital Edge")
    print(f"  {results['url']}")
    print(f"{'='*60}\n")

    if results.get("title"):
        print(f"  Title: {results['title']}")
    if results.get("meta_description"):
        desc = results["meta_description"]
        if len(desc) > 80:
            desc = desc[:77] + "..."
        print(f"  Description: {desc}")
    print()

    if results["issues"]:
        print(f"{Fore.RED}  ISSUES ({len(results['issues'])}){Style.RESET_ALL}")
        for issue in results["issues"]:
            print(f"  {Fore.RED}✗{Style.RESET_ALL} {issue}")
        print()

    if results["warnings"]:
        print(f"{Fore.YELLOW}  WARNINGS ({len(results['warnings'])}){Style.RESET_ALL}")
        for warning in results["warnings"]:
            print(f"  {Fore.YELLOW}!{Style.RESET_ALL} {warning}")
        print()

    if results["passed"]:
        print(f"{Fore.GREEN}  PASSED ({len(results['passed'])}){Style.RESET_ALL}")
        for passed in results["passed"]:
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {passed}")
        print()

    # Score
    total = len(results["issues"]) + len(results["warnings"]) + len(results["passed"])
    if total > 0:
        score = round((len(results["passed"]) / total) * 100)
        colour = Fore.GREEN if score >= 70 else (Fore.YELLOW if score >= 40 else Fore.RED)
        print(f"  {colour}SEO Score: {score}/100{Style.RESET_ALL}")

    print(f"\n  Powered by Perth Digital Edge")
    print(f"  https://perthdigitaledge.com.au")
    print(f"{'='*60}\n")


def export_json(results, filename):
    """Export results to JSON file."""
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filename}")


def export_csv(results, filename):
    """Export results to CSV file."""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Message"])
        for issue in results["issues"]:
            writer.writerow(["ISSUE", issue])
        for warning in results["warnings"]:
            writer.writerow(["WARNING", warning])
        for passed in results["passed"]:
            writer.writerow(["PASSED", passed])
    print(f"Results saved to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="SEO Audit Tool by Perth Digital Edge (https://perthdigitaledge.com.au)"
    )
    parser.add_argument("url", help="URL to audit")
    parser.add_argument("--json", dest="json_file", help="Export results to JSON file")
    parser.add_argument("--csv", dest="csv_file", help="Export results to CSV file")
    args = parser.parse_args()

    if not HAS_DEPS:
        print("Missing dependencies. Run: pip install -r requirements.txt")
        sys.exit(1)

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"Auditing {url}...")
    try:
        response = fetch_page(url)
        soup = BeautifulSoup(response.text, "lxml")
        results = analyse_meta_tags(soup, url)
        print_results(results)

        if args.json_file:
            export_json(results, args.json_file)
        if args.csv_file:
            export_csv(results, args.csv_file)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
