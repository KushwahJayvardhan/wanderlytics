"""
scrape_wikivoyage.py

Scrapes basic destination info (name, description, "see/do" highlights,
coordinates) from Wikivoyage destination pages.

Ethics / etiquette built in:
- Checks robots.txt before scraping any path
- Sends a descriptive User-Agent
- Rate-limits requests with a delay + jitter
- Retries transient failures with exponential backoff
- Writes raw output to disk so we never need to re-hit the source
  while developing the cleaning step

Usage:
    python scrape_wikivoyage.py
"""

import json
import random
import time
import urllib.robotparser
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://en.wikivoyage.org"
USER_AGENT = (
    "TripScopeLearningBot/1.0 "
    "(+https://github.com/jayvardhan-kushwah/tripscope; educational project)"
)
HEADERS = {"User-Agent": USER_AGENT}
RAW_OUTPUT_DIR = Path(__file__).parent / "raw_data"
RAW_OUTPUT_DIR.mkdir(exist_ok=True)

# A small, hand-picked starter list. Expand this as you go.
DESTINATIONS = [
    "Paris",
    "Tokyo",
    "Rome",
    "Bangkok",
    "New_York_City",
    "Cape_Town",
    "Sydney",
    "Barcelona",
    "Marrakesh",
    "Kyoto",
]


_robots_parser_cache: urllib.robotparser.RobotFileParser | None = None


def _get_robots_parser() -> urllib.robotparser.RobotFileParser:
    """
    Fetch and parse robots.txt once, reusing it for every URL check.

    We deliberately don't use RobotFileParser.read(), because it fetches
    robots.txt with urllib's default User-Agent header. Wikimedia's
    servers return 403 for that generic UA, and RobotFileParser treats
    a 403 as "disallow everything" (rp.disallow_all = True) rather than
    "couldn't check" -- so every can_fetch() call silently returns False
    even though the actual robots.txt permits scraping /wiki/ pages.
    Fetching it ourselves with our real headers avoids that trap.
    """
    global _robots_parser_cache
    if _robots_parser_cache is not None:
        return _robots_parser_cache

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{BASE_URL}/robots.txt")
    try:
        resp = requests.get(f"{BASE_URL}/robots.txt", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        rp.parse(resp.text.splitlines())
    except requests.RequestException as exc:
        print(f"[warn] couldn't fetch robots.txt ({exc}); assuming scraping is allowed")
        rp.parse([])  # empty ruleset -> can_fetch() defaults to allow

    _robots_parser_cache = rp
    return rp


def robots_allows(url: str) -> bool:
    """Check robots.txt before scraping the given URL."""
    return _get_robots_parser().can_fetch(USER_AGENT, url)


def fetch_with_retries(url: str, max_retries: int = 3) -> requests.Response | None:
    """GET a URL with exponential backoff on transient failures."""
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 500, 502, 503, 504):
                wait = 2 ** attempt
                print(f"  [retry] {url} -> {resp.status_code}, waiting {wait}s")
                time.sleep(wait)
                continue
            print(f"  [skip] {url} -> {resp.status_code}")
            return None
        except requests.RequestException as exc:
            wait = 2 ** attempt
            print(f"  [error] {url} -> {exc}, retrying in {wait}s")
            time.sleep(wait)
    return None


def parse_destination_page(html: str, name: str) -> dict:
    """Extract structured fields from a Wikivoyage destination page."""
    soup = BeautifulSoup(html, "html.parser")

    # First real paragraph = lead description
    description = ""
    for p in soup.select("div.mw-parser-output > p"):
        text = p.get_text(strip=True)
        if text and len(text) > 40:
            description = text
            break

    # "See" / "Do" section headings -> collect list items under them as highlights
    highlights = []
    for heading in soup.find_all(["h2", "h3"]):
        heading_text = heading.get_text(strip=True).lower()
        if heading_text.startswith("see") or heading_text.startswith("do"):
            sibling = heading.find_next_sibling()
            while sibling and sibling.name not in ("h2", "h3"):
                if sibling.name == "ul":
                    for li in sibling.find_all("li", recursive=False):
                        item_text = li.get_text(" ", strip=True)
                        if item_text:
                            highlights.append(item_text[:200])
                sibling = sibling.find_next_sibling()
            break

    # Coordinates often appear in a geo microformat span
    lat, lon = None, None
    geo = soup.select_one("span.geo")
    if geo:
        try:
            lat_str, lon_str = geo.get_text(strip=True).split(";")
            lat, lon = float(lat_str), float(lon_str)
        except (ValueError, AttributeError):
            pass

    return {
        "name": name.replace("_", " "),
        "description": description,
        "highlights": highlights[:8],
        "latitude": lat,
        "longitude": lon,
        "source_url": f"{BASE_URL}/wiki/{name}",
    }


def scrape_all(destinations: list[str] = DESTINATIONS) -> list[dict]:
    results = []
    for name in destinations:
        url = f"{BASE_URL}/wiki/{name}"

        if not robots_allows(url):
            print(f"[blocked by robots.txt] {url}")
            continue

        print(f"Scraping {name}...")
        resp = fetch_with_retries(url)
        if resp is None:
            continue

        record = parse_destination_page(resp.text, name)
        results.append(record)

        # Save raw HTML too, in case parsing logic needs to change later
        (RAW_OUTPUT_DIR / f"{name}.html").write_text(resp.text, encoding="utf-8")

        # Be polite: rate-limit with jitter between requests
        time.sleep(1.5 + random.random())

    return results


if __name__ == "__main__":
    data = scrape_all()
    out_path = RAW_OUTPUT_DIR / "destinations_raw.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {len(data)} destinations to {out_path}")
