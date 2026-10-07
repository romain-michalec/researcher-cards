"""Fetch Pure portal pages politely, keeping a month-long cache on disk."""

import time
from pathlib import Path

import requests

BASE_URL = "https://researchportal.hw.ac.uk/en/persons/"
CACHE_DIR = Path.home() / ".cache" / "researcher-cards"
MAX_AGE = 30 * 24 * 3600  # seconds, so that cards pick up profile updates within a month
HEADERS = {  # a real browser's user agent, since the portal sits behind Cloudflare
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
}
DELAY = 3  # seconds before every request, to stay polite
ATTEMPTS = 4


def fetch_page(slug, page):
    """Return the HTML of a person's "profile" or "fingerprints" page, from the cache if under a month old."""
    path = CACHE_DIR / slug / f"{page}.html"
    if path.exists() and time.time() - path.stat().st_mtime < MAX_AGE:
        return path.read_text(encoding="utf-8")

    url = f"{BASE_URL}{slug}/" if page == "profile" else f"{BASE_URL}{slug}/{page}/"
    html = download(url)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html


def download(url):
    """Fetch one portal page politely, retrying with backoff on transient errors."""
    print(f"Fetching {url}")
    for attempt in range(1, ATTEMPTS + 1):
        time.sleep(DELAY)

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
        except (requests.ConnectionError, requests.Timeout) as error:
            problem = str(error)
        else:
            if response.status_code == 404:
                raise LookupError(f"No page at {url}, check the slug in the CSV")

            if response.status_code == 429 or response.status_code >= 500:
                problem = f"HTTP {response.status_code}"
            else:
                response.raise_for_status()
                # A Cloudflare challenge can come back as a 200, and must not end up in the cache.
                if "rendering_person" not in response.text:
                    raise RuntimeError(f"{url} returned a page that is not a person page")
                return response.text

        if attempt == ATTEMPTS:
            raise RuntimeError(f"Gave up on {url} after {ATTEMPTS} attempts: {problem}")

        wait = 10 * 3 ** (attempt - 1)  # 10, 30, 90 seconds
        print(f"{url}: {problem}, retrying in {wait} s")
        time.sleep(wait)
