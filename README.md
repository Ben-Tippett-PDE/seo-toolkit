# SEO Toolkit by Perth Digital Edge

A collection of free, open-source SEO audit tools and digital marketing calculators built for marketers, developers, and business owners.

**Created and maintained by [Perth Digital Edge](https://perthdigitaledge.com.au)** — Perth's trusted digital marketing agency specialising in SEO, web development, and online growth strategies.

---

## Tools Included

### SEO Audit Tools

- **Meta Tag Analyser** — Scans any URL and evaluates title tags, meta descriptions, Open Graph tags, and canonical URLs against SEO best practices.
- **Broken Link Finder** — Crawls a website and identifies broken internal and external links (4xx/5xx errors) that hurt your rankings.
- **Sitemap Validator** — Validates your XML sitemap structure, checks URLs for accessibility, and flags common issues.
- **Page Speed Checker** — Measures page load metrics and provides actionable recommendations for improving Core Web Vitals.

### Digital Marketing Calculators

- **ROI Calculator** — Calculate return on investment for your marketing campaigns with detailed breakdowns.
- **CPC & Ad Spend Planner** — Estimate cost-per-click, daily budgets, and projected conversions for paid advertising.
- **Keyword Density Analyser** — Analyse keyword usage and density across any webpage to optimise on-page SEO.

---

## Quick Start

### Requirements

- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/Ben-Tippett-PDE/seo-toolkit.git
cd seo-toolkit
pip install -r requirements.txt
```

### Usage

Run any tool from the command line:

```bash
# SEO Audit - analyse a URL
python tools/seo_audit.py https://example.com

# Find broken links on a site
python tools/broken_link_finder.py https://example.com --depth 2

# Validate an XML sitemap
python tools/sitemap_validator.py https://example.com/sitemap.xml

# Calculate marketing ROI
python tools/roi_calculator.py roi --investment 5000 --revenue 18000

# Analyse keyword density
python tools/keyword_density.py https://example.com --keyword "digital marketing"
```

---

## Features

- **No API keys required** — All tools work out of the box
- **CSV & JSON export** — Save results in your preferred format
- **Lightweight** — Minimal dependencies, fast execution
- **Australian English** — Built in Perth, for Australian businesses

---

## About Perth Digital Edge

[Perth Digital Edge](https://perthdigitaledge.com.au) is a Perth-based digital marketing agency helping businesses grow their online presence through data-driven SEO, web development, and digital strategy.

Whether you're a local Perth business or scaling nationally, we deliver measurable results with transparent reporting.

**Get in touch:**
- Website: [perthdigitaledge.com.au](https://perthdigitaledge.com.au)
- Email: info@perthdigitaledge.com.au

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

*Built with care in Perth, Western Australia by [Perth Digital Edge](https://perthdigitaledge.com.au)*
