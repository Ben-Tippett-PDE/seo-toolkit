#!/usr/bin/env python3
"""
Keyword Density Analyser
Built by Perth Digital Edge (https://perthdigitaledge.com.au)

Analyses keyword usage and density across any webpage to help
optimise on-page SEO without over-optimising.
"""

import argparse
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "this", "that",
    "these", "those", "i", "you", "he", "she", "it", "we", "they", "me",
    "him", "her", "us", "them", "my", "your", "his", "its", "our", "their",
    "not", "no", "so", "if", "as", "up", "out", "about", "into", "over",
    "after", "all", "also", "just", "more", "than", "very", "what", "which",
    "who", "when", "where", "how", "each", "every", "both", "few", "many",
}


def extract_text(soup):
    """Extract visible text from a page, excluding scripts and styles."""
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text


def analyse_density(text, target_keyword=None):
    """Analyse keyword density in text."""
    words = re.findall(r"[a-z]+", text.lower())
    total_words = len(words)

    if total_words == 0:
        return {"error": "No text content found on page."}

    # Word frequency (excluding stop words)
    content_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    word_freq = Counter(content_words)

    # Two-word phrases
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)
               if words[i] not in STOP_WORDS and words[i+1] not in STOP_WORDS]
    bigram_freq = Counter(bigrams)

    # Three-word phrases
    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words) - 2)]
    trigram_freq = Counter(trigrams)

    results = {
        "total_words": total_words,
        "unique_words": len(set(words)),
        "top_keywords": [
            {"keyword": word, "count": count, "density": round((count / total_words) * 100, 2)}
            for word, count in word_freq.most_common(20)
        ],
        "top_phrases_2word": [
            {"phrase": phrase, "count": count, "density": round((count / total_words) * 100, 2)}
            for phrase, count in bigram_freq.most_common(10)
        ],
        "top_phrases_3word": [
            {"phrase": phrase, "count": count, "density": round((count / total_words) * 100, 2)}
            for phrase, count in trigram_freq.most_common(10)
        ],
    }

    # Target keyword analysis
    if target_keyword:
        target = target_keyword.lower().strip()
        target_count = text.lower().count(target)
        target_words = len(target.split())
        target_density = round((target_count / total_words) * 100, 2) if total_words > 0 else 0

        # Check placement
        title = ""
        h1 = ""
        meta_desc = ""

        results["target_keyword"] = {
            "keyword": target_keyword,
            "occurrences": target_count,
            "density": target_density,
            "recommendation": get_density_recommendation(target_density),
        }

    return results


def get_density_recommendation(density):
    """Provide a recommendation based on keyword density."""
    if density == 0:
        return "Keyword not found. Consider adding it naturally to your content."
    elif density < 0.5:
        return "Low density. Consider using the keyword more frequently."
    elif density <= 2.5:
        return "Good density range. This looks natural and well-optimised."
    elif density <= 4.0:
        return "Slightly high. Consider reducing usage to avoid over-optimisation."
    else:
        return "Too high! This may trigger keyword stuffing penalties. Reduce usage."


def print_results(results, url=None):
    """Print density analysis results."""
    green = Fore.GREEN if HAS_DEPS else ""
    yellow = Fore.YELLOW if HAS_DEPS else ""
    red = Fore.RED if HAS_DEPS else ""
    reset = Style.RESET_ALL if HAS_DEPS else ""

    print(f"\n{'='*60}")
    print(f"  Keyword Density Report â Perth Digital Edge")
    if url:
        print(f"  {url}")
    print(f"{'='*60}\n")

    print(f"  Total words: {results['total_words']:,}")
    print(f"  Unique words: {results['unique_words']:,}")
    print()

    # Target keyword
    if "target_keyword" in results:
        tk = results["target_keyword"]
        density = tk["density"]
        colour = green if 0.5 <= density <= 2.5 else (yellow if density < 0.5 else red)
        print(f"  TARGET KEYWORD: \"{tk['keyword']}\"")
        print(f"  Occurrences: {tk['occurrences']}")
        print(f"  {colour}Density: {tk['density']}%{reset}")
        print(f"  {tk['recommendation']}")
        print()

    # Top keywords
    print(f"  TOP SINGLE KEYWORDS:")
    print(f"  {'Keyword':<25} {'Count':>6} {'Density':>8}")
    print(f"  {'-'*42}")
    for kw in results["top_keywords"][:15]:
        print(f"  {kw['keyword']:<25} {kw['count']:>6} {kw['density']:>7}%")
    print()

    # Top 2-word phrases
    if results["top_phrases_2word"]:
        print(f"  TOP 2-WORD PHRASES:")
        print(f"  {'Phrase':<30} {'Count':>6} {'Density':>8}")
        print(f"  {'-'*47}")
        for p in results["top_phrases_2word"][:10]:
            print(f"  {p['phrase']:<30} {p['count']:>6} {p['density']:>7}%")
        print()

    print(f"  Powered by Perth Digital Edge")
    print(f"  https://perthdigitaledge.com.au")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Keyword Density Analyser by Perth Digital Edge (https://perthdigitaledge.com.au)"
    )
    parser.add_argument("url", help="URL to analyse")
    parser.add_argument("--keyword", "-k", help="Target keyword to check density for")
    parser.add_argument("--json", dest="json_file", help="Export results to JSON file")
    args = parser.parse_args()

    if not HAS_DEPS:
        print("Missing dependencies. Run: pip install -r requirements.txt")
        sys.exit(1)

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"Analysing {url}...")

    try:
        headers = {"User-Agent": "SEO-Toolkit/1.0 (Perth Digital Edge; https://perthdigitaledge.com.au)"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        text = extract_text(soup)
        results = analyse_density(text, args.keyword)
        print_results(results, url)

        if args.json_file:
            with open(args.json_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.json_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
