"""Build a researcher card for every academic in heriot-watt.csv."""

import csv
import sys
from pathlib import Path

import requests

from fetch import fetch_page
from parse import parse_person
from write import write_card

INPUT = Path(__file__).parent / "heriot-watt.csv"
UNIVERSITY = "Heriot-Watt"
CARDS_DIR = Path(__file__).parent / "cards"


def main():
    """Fetch, parse and write a researcher card for every academic in the input CSV."""
    with open(INPUT, newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    for name, email, slug in rows:
        try:
            profile_html = fetch_page(slug, "profile")
            fingerprints_html = fetch_page(slug, "fingerprints")
        except (LookupError, RuntimeError, requests.RequestException) as error:
            print(f"{name} ({slug}): {error}", file=sys.stderr)
            continue

        card = {
            "name": name,
            "university": UNIVERSITY,
            "email": email,
            **parse_person(slug, profile_html, fingerprints_html),
        }
        card["completeness"] = completeness(card)
        write_card(card, CARDS_DIR / f"{slug}.md")

        print(f"{name} ({slug}): {card['completeness']} ({content_summary(card)})")


def completeness(card):
    """Rate a card thin, moderate or rich from the word count of its profile text."""
    words = sum(len((card[field] or "").split()) for field in ["biography", "interests", "grants"])
    if words < 30:
        return "thin"
    if words < 300:
        return "moderate"
    return "rich"


def content_summary(card):
    """Describe how much content a card holds: word counts for text, item counts for lists."""
    parts = []
    for field in ["biography", "interests", "grants", "keywords", "fingerprints", "selected_outputs"]:
        value = card[field]
        if value is None:
            continue
        size = f"{len(value.split())} words" if isinstance(value, str) else len(value)
        parts.append(f"{field} {size}")

    return ", ".join(parts) or "no content"


if __name__ == "__main__":
    main()
