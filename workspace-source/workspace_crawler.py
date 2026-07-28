#!/usr/bin/env python3
"""
Workspace Directory Deep Web Crawler
------------------------------------
Adapted from the Big Rig Rescue crawler for a coworking / flexible-office /
meeting-room directory.

Reads a seed CSV of workspace locations (name, phone, website, city, state,
address, rating, ...), fetches each operator's website, and extracts enriched
attributes relevant to a flex-office directory:

  - Space types offered (private office, dedicated desk, hot desk / coworking,
    meeting/conference rooms, virtual office, day pass, event space)
  - Amenities (24/7 access, parking, high-speed wifi, coffee, phone booths,
    mail/reception, kitchen, pet-friendly, showers)
  - Pricing signals (day-pass pricing, monthly pricing when published)
  - Whether the operator advertises tours / free-trial day (conversion hooks)

Writes results progressively to CSV and checkpoints progress so the crawl can
resume. Paths are relative to this file so it runs on any machine.
"""

import csv
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Seed CSV of workspace locations for your target metro (Google Places export
# or hand-built). Prefers the Huntsville seed, then the generic sample.
SEED_CSV = DATA_DIR / "huntsville_seed.csv"
if not SEED_CSV.exists():
    SEED_CSV = DATA_DIR / "workspace_seed_sample.csv"
RESULTS_CSV = DATA_DIR / "workspace_enriched.csv"
PROGRESS_FILE = DATA_DIR / "crawl_progress.json"

TIMEOUT = 15
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# How many locations to process per run (keeps runs short + resumable).
BATCH_SIZE = 50


# --------------------------------------------------------------------------- #
# Taxonomy: what we detect on each operator's site
# --------------------------------------------------------------------------- #

SPACE_TYPE_KEYWORDS = {
    "private_office": ["private office", "private suite", "team office",
                       "dedicated office", "office space"],
    "dedicated_desk": ["dedicated desk", "fixed desk", "reserved desk",
                       "permanent desk"],
    "hot_desk": ["hot desk", "hot-desk", "open desk", "flexible desk",
                 "shared desk", "coworking desk"],
    "coworking": ["coworking", "co-working", "shared workspace",
                  "shared office", "open workspace"],
    "meeting_room": ["meeting room", "conference room", "boardroom",
                     "meeting space", "training room"],
    "virtual_office": ["virtual office", "business address",
                       "mailing address", "registered agent"],
    "day_pass": ["day pass", "day-pass", "drop in", "drop-in", "daily rate"],
    "event_space": ["event space", "event venue", "workshop space",
                    "podcast studio", "media room"],
}

AMENITY_KEYWORDS = {
    "access_24_7": ["24/7", "24 hours", "24-hour", "24/7 access",
                    "around the clock", "keyless entry"],
    "parking": ["parking", "free parking", "on-site parking", "garage"],
    "high_speed_wifi": ["gigabit", "high-speed wifi", "high speed internet",
                        "fiber internet", "fast wifi"],
    "coffee": ["free coffee", "coffee bar", "barista", "espresso",
               "complimentary coffee"],
    "phone_booths": ["phone booth", "call booth", "privacy booth",
                     "phone room"],
    "mail_reception": ["mail handling", "reception", "front desk",
                       "package handling", "mail service"],
    "kitchen": ["kitchen", "kitchenette", "cafe", "lounge"],
    "pet_friendly": ["pet friendly", "pet-friendly", "dog friendly",
                     "dogs welcome"],
    "showers": ["shower", "showers", "bike storage", "wellness room"],
}

# Conversion hooks: does the operator invite tours / free trials? These signal
# openness to referral deals and inform the "Request a tour" CTA copy.
TOUR_KEYWORDS = ["book a tour", "schedule a tour", "request a tour",
                 "free day pass", "free trial", "try us free", "book a visit"]

PRICE_DAY_RE = re.compile(r"\$\s?(\d{1,3})\s?(?:/|per)\s?day", re.IGNORECASE)
PRICE_MONTH_RE = re.compile(r"\$\s?(\d{2,4})\s?(?:/|per)\s?(?:mo|month)",
                            re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Seed loading + progress
# --------------------------------------------------------------------------- #

def load_locations():
    """Load workspace locations from the seed CSV.

    A row is used if it has a name, a phone, and a website to crawl. (Rows
    without a website still make good listings — they just skip enrichment.)
    """
    if not SEED_CSV.exists():
        raise SystemExit(
            f"Seed CSV not found: {SEED_CSV}\n"
            f"Create it from a Google Places export for your metro. "
            f"See data/workspace_seed_sample.csv for the columns."
        )
    locations = []
    with open(SEED_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Need a name; a website lets us enrich (phone is optional and
            # usually filled from a Google Places export, not scraped).
            if row.get("name", "").strip():
                locations.append(row)
    return locations


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"processed": 0, "failed": 0, "high_confidence": 0,
            "medium_confidence": 0, "low_confidence": 0}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


# --------------------------------------------------------------------------- #
# Fetch + parse
# --------------------------------------------------------------------------- #

def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def extract_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = " ".join(chunk for chunk in chunks if chunk)
    return text[:6000]  # a bit more than trucking — office sites are wordier


def find_secondary_page(base_url):
    """Try to fetch a pricing / membership / spaces page for more signal."""
    candidates = [
        "/pricing", "/plans", "/membership", "/memberships", "/spaces",
        "/private-offices", "/coworking", "/meeting-rooms", "/amenities",
        "/pricing/", "/membership/", "/spaces/",
    ]
    for path in candidates:
        html = fetch_page(urljoin(base_url, path))
        if html:
            return html
    return None


def detect(text_lower, keyword_map):
    """Return list of keys whose any keyword appears in the text."""
    found = []
    for key, keywords in keyword_map.items():
        if any(kw in text_lower for kw in keywords):
            found.append(key)
    return found


def extract_prices(text):
    day = PRICE_DAY_RE.search(text)
    month = PRICE_MONTH_RE.search(text)
    return (
        f"${day.group(1)}/day" if day else "",
        f"${month.group(1)}/mo" if month else "",
    )


# --------------------------------------------------------------------------- #
# Per-location enrichment
# --------------------------------------------------------------------------- #

def crawl_location(loc):
    result = {
        # passthrough identity/contact fields from the seed
        "name": loc.get("name", "").strip(),
        "phone": loc.get("phone", "").strip(),
        "website": loc.get("website", "").strip(),
        "city": loc.get("city", "").strip(),
        "state": loc.get("state", "").strip(),
        "full_address": loc.get("full_address", loc.get("full address", "")).strip(),
        "neighborhood": loc.get("neighborhood", "").strip(),
        "google_rating": loc.get("google_rating", loc.get("google rating", "")).strip(),
        "review_count": loc.get("review_count", loc.get("review count", "")).strip(),
        "latitude": loc.get("latitude", "").strip(),
        "longitude": loc.get("longitude", "").strip(),
        "zip": loc.get("zip", "").strip(),
        # enriched fields
        "description": "",
        "space_types": "",
        "amenities": "",
        "price_day": "",
        "price_month": "",
        "offers_tour": "no",
        "data_confidence": "low",
    }

    website = result["website"]
    if not website:
        return result  # keep as a basic listing, no enrichment

    homepage_html = fetch_page(website)
    if not homepage_html:
        return result

    text = extract_text(homepage_html)
    secondary_html = find_secondary_page(website)
    if secondary_html:
        text = text + " " + extract_text(secondary_html)
    text_lower = text.lower()

    space_types = detect(text_lower, SPACE_TYPE_KEYWORDS)
    amenities = detect(text_lower, AMENITY_KEYWORDS)
    price_day, price_month = extract_prices(text)
    offers_tour = any(kw in text_lower for kw in TOUR_KEYWORDS)

    result["space_types"] = ",".join(space_types)
    result["amenities"] = ",".join(amenities)
    result["price_day"] = price_day
    result["price_month"] = price_month
    result["offers_tour"] = "yes" if offers_tour else "no"

    # Short description from the first couple of sentences.
    snippet = ".".join(text[:600].split(".")[:2]).strip()
    if snippet:
        result["description"] = (snippet[:200] + "...") if len(snippet) > 200 else snippet

    # Confidence: more signal captured -> higher confidence.
    signal = len(space_types) + len(amenities) + (1 if price_month or price_day else 0)
    if signal >= 4:
        result["data_confidence"] = "high"
    elif signal >= 1:
        result["data_confidence"] = "medium"

    return result


def append_result(result):
    file_exists = RESULTS_CSV.exists()
    with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)


def main():
    print("=" * 60)
    print("WORKSPACE DIRECTORY DEEP WEB CRAWLER")
    print("=" * 60)

    locations = load_locations()
    progress = load_progress()
    total = len(locations)
    start_idx = progress["processed"]

    print(f"\nLoaded {total} workspace locations")
    print(f"Resuming from location {start_idx + 1} / {total}")

    batch_end = min(start_idx + BATCH_SIZE, total)
    print(f"\nCrawling {start_idx + 1}-{batch_end}...\n")

    for i in range(start_idx, batch_end):
        loc = locations[i]
        label = loc.get("name", "")[:40]
        print(f"[{i + 1}/{total}] {label:40s} ({loc.get('city','')}, {loc.get('state','')}) ",
              end="", flush=True)
        try:
            result = crawl_location(loc)
            append_result(result)
            progress["processed"] += 1
            conf = result["data_confidence"]
            progress[f"{conf}_confidence"] += 1
            print({"high": "✓ HIGH", "medium": "◐ MEDIUM",
                   "low": "○ LOW"}[conf])
            if (i - start_idx + 1) % 5 == 0:
                save_progress(progress)
        except Exception as e:
            progress["failed"] += 1
            print(f"✗ ERROR: {str(e)[:30]}")
        time.sleep(0.5)

    save_progress(progress)

    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print("=" * 60)
    print(f"Total processed: {progress['processed']}/{total}")
    print(f"  High: {progress['high_confidence']}  "
          f"Medium: {progress['medium_confidence']}  "
          f"Low: {progress['low_confidence']}  "
          f"Failed: {progress['failed']}")
    remaining = total - progress["processed"]
    if remaining > 0:
        print(f"\nRemaining: {remaining}. Run again to continue.")
    else:
        print(f"\n✓ CRAWL COMPLETE. Enriched data -> {RESULTS_CSV}")


if __name__ == "__main__":
    main()
