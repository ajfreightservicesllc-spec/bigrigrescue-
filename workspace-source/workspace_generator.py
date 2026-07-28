#!/usr/bin/env python3
"""
FlexWorkspace — Multi-Market Static Site Generator
--------------------------------------------------
Generates flexworkspace.online: a directory of coworking, private offices and
meeting rooms across Alabama's markets.

Structure:
  /                          brand homepage (market picker)
  /<market>/                 market homepage (browse by type/neighborhood)
  /<market>/space/<slug>/    individual space pages (lead form + schema.org)
  /<market>/<bucket>/        space-type pages (private-office, coworking, ...)
  /<market>/neighborhood/<n>/
  /<market>/amenity/<a>/
  /<market>/guides/...       SEO guides (per-market)
  /list-your-space/          operator sign-up (brand-level)
  /thank-you/                post-submit page (noindex, fires GA4 conversion)

Market data lives in data/markets/<slug>.csv (same columns as the original
huntsville_enriched.csv). A market with no CSV (or no rows) is shown as
"coming soon" on the brand homepage and generates no pages.

Every lead form posts to LEAD_ENDPOINT with full attribution (lead_id,
first-touch UTMs, page, referrer) — see LEAD-TRACKING.md.
"""

import csv
import json
import re
from pathlib import Path
from urllib.parse import quote
from collections import defaultdict

from guides_content import GUIDES

# --------------------------------------------------------------------------- #
# CONFIG
# --------------------------------------------------------------------------- #
BRAND = "FlexWorkspace"
BRAND_TAGLINE = "Coworking, private offices & meeting rooms across Alabama"
BASE_URL = "https://flexworkspace.online"           # no trailing slash

# Markets, in display order. A market renders only if data/markets/<slug>.csv
# exists and has at least one row; otherwise it appears as "coming soon".
MARKETS = [
    {"slug": "huntsville",  "name": "Huntsville",
     "tagline": "The Rocket City — aerospace, defense and the state's fastest-growing tech scene"},
    {"slug": "birmingham",  "name": "Birmingham",
     "tagline": "Alabama's largest metro — banking, medicine and the Magic City startup scene"},
    {"slug": "mobile",      "name": "Mobile",
     "tagline": "The Port City — shipbuilding, aviation and Gulf Coast commerce"},
    {"slug": "montgomery",  "name": "Montgomery",
     "tagline": "The Capital City — government, Maxwell AFB and river-region business"},
    {"slug": "tuscaloosa",  "name": "Tuscaloosa",
     "tagline": "Home of the University of Alabama and a growing manufacturing corridor"},
    {"slug": "auburn",      "name": "Auburn–Opelika",
     "tagline": "University-driven growth on the plains"},
    {"slug": "decatur",     "name": "Decatur",
     "tagline": "River City industry, minutes from Huntsville"},
    {"slug": "dothan",      "name": "Dothan",
     "tagline": "Hub of the Wiregrass"},
    {"slug": "florence",    "name": "Florence–Muscle Shoals",
     "tagline": "The Shoals — music heritage, UNA and North Alabama commerce"},
    {"slug": "fairhope",    "name": "Fairhope–Daphne",
     "tagline": "Baldwin County's Eastern Shore — one of the fastest-growing areas in the Southeast"},
]

# Lead capture backend (Google Apps Script web app) — see LEAD-TRACKING.md.
LEAD_ENDPOINT = ("https://script.google.com/macros/s/"
                 "AKfycby6nRfjsZegwjur-bg2hrlVcFQokEulMgwCVVAYbcyPz9vbT4K8ceqn9XzUX0_uQxYo7Q/exec")
LEAD_REDIRECT = "/thank-you/"
LEAD_SUBJECT = "New workspace lead"

# GA4 measurement id.
GA4_ID = "G-T5F8V3Y1XY"

# Tracked phone number (call-tracking line). Blank = show operator's number.
TRACKING_PHONE = ""

# Google Search Console HTML-file verification token (emitted at site root).
GOOGLE_SITE_VERIFICATION = "googleaf127d96642b3615"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MARKETS_DIR = DATA_DIR / "markets"
OUTPUT_DIR = BASE_DIR / "public"


# --------------------------------------------------------------------------- #
# Taxonomy
# --------------------------------------------------------------------------- #

SPACE_TOKEN_TO_BUCKET = {
    "private_office": "private-office",
    "dedicated_desk": "coworking",
    "hot_desk": "coworking",
    "coworking": "coworking",
    "meeting_room": "meeting-rooms",
    "virtual_office": "virtual-office",
    "day_pass": "day-pass",
    "event_space": "event-space",
}

SPACE_BUCKETS = {
    "private-office": ("Private Offices",
                       "Lockable private offices and team suites"),
    "coworking": ("Coworking & Desks",
                  "Hot desks, dedicated desks and open coworking"),
    "meeting-rooms": ("Meeting Rooms",
                      "Bookable meeting, conference and boardrooms"),
    "virtual-office": ("Virtual Offices",
                       "Business address, mail handling and reception"),
    "day-pass": ("Day Passes",
                 "Drop-in day access with no long-term commitment"),
    "event-space": ("Event Space",
                    "Event venues, workshop and media rooms"),
}

AMENITY_LABELS = {
    "access_24_7": "24/7 Access",
    "parking": "Parking",
    "high_speed_wifi": "Gigabit WiFi",
    "coffee": "Coffee Bar",
    "phone_booths": "Phone Booths",
    "mail_reception": "Mail & Reception",
    "kitchen": "Kitchen / Lounge",
    "pet_friendly": "Pet Friendly",
    "showers": "Showers / Bike",
}
AMENITY_PAGES = ["access_24_7", "parking", "pet_friendly"]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def slugify(text):
    return quote(text.lower().strip(), safe="").replace("%20", "-")


def load_market_spaces(market):
    path = MARKETS_DIR / f"{market['slug']}.csv"
    if not path.exists():
        return []
    spaces = []
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("name", "").strip():
                spaces.append(row)
    return spaces


def space_slug(space):
    return slugify(space["name"])


def tokens(space, field):
    return [t for t in space.get(field, "").split(",") if t.strip()]


def space_buckets(space):
    seen = []
    for tok in tokens(space, "space_types"):
        bucket = SPACE_TOKEN_TO_BUCKET.get(tok)
        if bucket and bucket not in seen:
            seen.append(bucket)
    return seen


def price_summary(space):
    parts = []
    if space.get("price_day", "").strip():
        parts.append(f"Day pass from {space['price_day'].strip()}")
    if space.get("price_month", "").strip():
        parts.append(f"Memberships from {space['price_month'].strip()}")
    return " · ".join(parts) if parts else "Pricing on request"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# --------------------------------------------------------------------------- #
# Shared HTML: analytics, tracking, header/footer, components
# --------------------------------------------------------------------------- #

def render_ga4():
    if not GA4_ID:
        return ""
    return f"""    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA4_ID}');
    </script>
"""


def render_tracking_js():
    """First-touch attribution + lead-form field population (verified in
    Chromium: UTM capture, localStorage persistence, unique lead ids)."""
    return """    <script>
    (function () {
      var KEY = 'hw_attr';
      var UTM = ['utm_source','utm_medium','utm_campaign','utm_term','utm_content','gclid'];
      function parseUTM() {
        var p = new URLSearchParams(location.search), o = {};
        UTM.forEach(function (k) { if (p.get(k)) o[k] = p.get(k); });
        return o;
      }
      var attr;
      try { attr = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
      if (!attr) {
        attr = {
          first_touch_at: new Date().toISOString(),
          landing_page: location.pathname,
          referrer: document.referrer || 'direct',
          utm: parseUTM()
        };
        try { localStorage.setItem(KEY, JSON.stringify(attr)); } catch (e) {}
      }
      function genId() {
        return 'HW-' + Date.now().toString(36).toUpperCase() +
               '-' + Math.random().toString(36).slice(2, 7).toUpperCase();
      }
      function fill(form) {
        function set(name, val) {
          var el = form.querySelector('[name="' + name + '"]');
          if (el && !el.value) el.value = val || '';
        }
        set('lead_id', genId());
        set('captured_at', new Date().toISOString());
        set('page_url', location.href);
        set('page_path', location.pathname);
        set('referrer', attr.referrer);
        set('first_touch_at', attr.first_touch_at);
        set('landing_page', attr.landing_page);
        var u = attr.utm || {};
        UTM.forEach(function (k) { set(k, u[k]); });
      }
      document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('form[data-lead]').forEach(function (f) {
          fill(f);
          f.addEventListener('submit', function () {
            fill(f);
            var sn = f.querySelector('[name="space_name"]');
            var sc = f.querySelector('[name="source"]');
            if (window.gtag) gtag('event', 'generate_lead', {
              space: sn ? sn.value : '', source: sc ? sc.value : ''
            });
          });
        });
      });
    })();
    </script>
"""


def nav_links(market):
    """Market-scoped nav when inside a market; brand-level nav otherwise."""
    if market:
        p = f"/{market['slug']}"
        return (f'<a href="{p}/private-office/">Offices</a>'
                f'<a href="{p}/coworking/">Coworking</a>'
                f'<a href="{p}/meeting-rooms/">Meeting Rooms</a>'
                f'<a href="{p}/">{market["name"]}</a>')
    return ('<a href="/#markets">Markets</a>'
            '<a href="/huntsville/">Huntsville</a>'
            '<a href="/list-your-space/">List your space</a>')


def render_header(title, description, canonical_path="/", noindex=False,
                  market=None):
    canonical = BASE_URL + canonical_path
    robots = '\n    <meta name="robots" content="noindex,follow">' if noindex else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="theme-color" content="#1e2a4a">
    <link rel="canonical" href="{canonical}">{robots}
{render_ga4()}{render_tracking_js()}    <style>
        :root {{
            --navy:#1e2a4a; --navy-2:#2b3c66; --accent:#3b82f6;
            --accent-2:#06b6d4; --ink:#1f2733; --muted:#5b6675;
            --bg:#f6f8fc; --card:#ffffff; --line:#e4e9f2;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        html {{ scroll-behavior:smooth; }}
        body {{ font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
            color:var(--ink); background:var(--bg); line-height:1.6; }}
        a {{ color:var(--accent); text-decoration:none; }}
        a:hover {{ text-decoration:underline; }}
        .container {{ max-width:1140px; margin:0 auto; padding:0 20px; }}
        header.site {{ background:var(--navy); color:#fff; padding:16px 0;
            position:sticky; top:0; z-index:50; box-shadow:0 2px 10px rgba(0,0,0,.12); }}
        header.site .container {{ display:flex; align-items:center; justify-content:space-between; }}
        header.site a.brand {{ color:#fff; font-weight:800; font-size:20px; letter-spacing:-.3px; }}
        header.site nav a {{ color:#cdd6ea; margin-left:20px; font-size:14px; font-weight:600; }}
        header.site nav a:hover {{ color:#fff; text-decoration:none; }}
        .hero {{ background:linear-gradient(135deg,var(--navy) 0%,var(--navy-2) 60%,#33507f 100%);
            color:#fff; padding:64px 0 56px; }}
        .hero h1 {{ font-size:42px; font-weight:800; letter-spacing:-1px; margin-bottom:14px; }}
        .hero p {{ font-size:19px; color:#d6deee; max-width:640px; }}
        .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-top:36px; max-width:720px; }}
        .stat {{ background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14);
            border-radius:12px; padding:18px; }}
        .stat .n {{ font-size:30px; font-weight:800; color:#fff; }}
        .stat .l {{ font-size:12px; text-transform:uppercase; letter-spacing:.5px; color:#aeb9d4; margin-top:4px; }}
        h2.section {{ font-size:26px; font-weight:800; letter-spacing:-.4px; margin:44px 0 18px; }}
        .breadcrumb {{ font-size:13px; color:var(--muted); margin:22px 0 6px; }}
        .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:18px; }}
        .tile {{ display:block; background:var(--card); border:1px solid var(--line);
            border-radius:12px; padding:20px 22px; transition:transform .15s, box-shadow .15s; }}
        .tile:hover {{ transform:translateY(-3px); box-shadow:0 12px 30px rgba(30,42,74,.12); text-decoration:none; }}
        .tile h3 {{ font-size:18px; color:var(--ink); margin-bottom:4px; }}
        .tile .sub {{ font-size:13px; color:var(--muted); }}
        .tile .count {{ display:inline-block; margin-top:10px; font-size:12px; font-weight:700;
            color:var(--accent); background:#eaf1fe; padding:3px 10px; border-radius:20px; }}
        .tile.soon {{ opacity:.65; }}
        .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px;
            padding:22px 24px; margin-bottom:18px; box-shadow:0 2px 10px rgba(30,42,74,.05); }}
        .card h3 {{ font-size:20px; margin-bottom:2px; }}
        .card h3 a {{ color:var(--ink); }}
        .card .meta {{ font-size:13px; color:var(--muted); margin:4px 0 10px; }}
        .card .price {{ font-size:14px; font-weight:700; color:var(--navy-2); margin:6px 0; }}
        .rating {{ font-size:13px; color:#b7791f; font-weight:700; }}
        .badges {{ margin:12px 0 4px; }}
        .badge {{ display:inline-block; font-size:12px; font-weight:600; color:#33507f;
            background:#eef3fb; border:1px solid #dbe6f7; padding:5px 11px; border-radius:20px; margin:0 6px 6px 0; }}
        .badge.type {{ color:#0b7285; background:#e6fbff; border-color:#c5f0f7; }}
        .btn {{ display:inline-block; background:var(--accent); color:#fff; font-weight:700;
            padding:12px 22px; border-radius:10px; border:none; cursor:pointer; font-size:15px; }}
        .btn:hover {{ background:#2f6fe0; text-decoration:none; }}
        .btn.alt {{ background:#fff; color:var(--accent); border:2px solid var(--accent); }}
        .btn.wide {{ display:block; width:100%; text-align:center; }}
        .split {{ display:grid; grid-template-columns:1fr 380px; gap:28px; align-items:start; }}
        .lead {{ background:var(--card); border:1px solid var(--line); border-radius:14px;
            padding:24px; position:sticky; top:84px; box-shadow:0 8px 30px rgba(30,42,74,.10); }}
        .lead h3 {{ font-size:19px; margin-bottom:4px; }}
        .lead p.small {{ font-size:13px; color:var(--muted); margin-bottom:14px; }}
        .lead label {{ display:block; font-size:13px; font-weight:600; margin:10px 0 4px; }}
        .lead input, .lead select, .lead textarea {{ width:100%; padding:11px; border:1px solid var(--line);
            border-radius:9px; font-size:14px; font-family:inherit; }}
        .lead input:focus, .lead select:focus, .lead textarea:focus {{ outline:none; border-color:var(--accent);
            box-shadow:0 0 0 3px rgba(59,130,246,.15); }}
        .lead .btn {{ margin-top:16px; }}
        .callbar {{ margin-top:12px; text-align:center; font-size:14px; color:var(--muted); }}
        .callbar a {{ font-weight:800; font-size:16px; }}
        footer.site {{ background:var(--navy); color:#c9d3e8; margin-top:64px; padding:36px 0; font-size:13px; }}
        footer.site a {{ color:#fff; }}
        .disclosure {{ font-size:12px; color:#93a0bd; margin-top:10px; max-width:720px; }}
        @media (max-width:860px) {{
            .split {{ grid-template-columns:1fr; }}
            .lead {{ position:static; }}
            .stats {{ grid-template-columns:repeat(2,1fr); }}
            .hero h1 {{ font-size:32px; }}
        }}
    </style>
</head>
<body>
    <header class="site">
        <div class="container">
            <a class="brand" href="/">{BRAND}</a>
            <nav>{nav_links(market)}</nav>
        </div>
    </header>
"""


def render_footer():
    market_links = " · ".join(
        f'<a href="/{m["slug"]}/">{m["name"]}</a>' for m in MARKETS[:5])
    return f"""    <footer class="site">
        <div class="container">
            <strong>{BRAND}</strong> — {BRAND_TAGLINE}<br>
            {market_links} · <a href="/">All markets</a><br>
            <a href="/sitemap.xml">Sitemap</a> ·
            <a href="/list-your-space/">List your space</a>
            <p class="disclosure">{BRAND} is an independent directory. We may earn a
            referral fee when you book or tour a space through us — it never changes
            your price. We list every workspace we can find in each market,
            sponsored or not.</p>
        </div>
    </footer>
</body>
</html>
"""


def type_badges(space):
    return "".join(f'<span class="badge type">{SPACE_BUCKETS[b][0]}</span>'
                   for b in space_buckets(space))


def amenity_badges(space):
    out = []
    for tok in tokens(space, "amenities"):
        label = AMENITY_LABELS.get(tok)
        if label:
            out.append(f'<span class="badge">{label}</span>')
    return "".join(out)


def callbar(space=None):
    phone = TRACKING_PHONE or (space.get("phone", "") if space else "")
    if not phone:
        return ""
    tel = re.sub(r"[^\d+]", "", phone)
    return f'<div class="callbar">or call <a href="tel:{tel}">{phone}</a></div>'


def lead_form(space=None, source="directory", market=None):
    space_name = space["name"] if space else ""
    space_addr = space.get("full_address", "") if space else ""
    metro = market["name"] if market else "Alabama"
    heading = "Request pricing & a tour" if space else "Find your space — free"
    sub = ("Tell us what you need and we'll line up pricing and a tour, usually "
           "same day. No cost to you.")
    return f"""
        <div class="lead">
            <h3>{heading}</h3>
            <p class="small">{sub}</p>
            <form action="{LEAD_ENDPOINT}" method="POST" data-lead>
                <input type="hidden" name="_next" value="{BASE_URL}{LEAD_REDIRECT}">
                <input type="hidden" name="_subject" value="{LEAD_SUBJECT} — {metro}">
                <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">
                <input type="hidden" name="space_name" value="{space_name}">
                <input type="hidden" name="space_address" value="{space_addr}">
                <input type="hidden" name="source" value="{source}">
                <input type="hidden" name="metro" value="{metro}">
                <input type="hidden" name="lead_id" value="">
                <input type="hidden" name="captured_at" value="">
                <input type="hidden" name="page_url" value="">
                <input type="hidden" name="page_path" value="">
                <input type="hidden" name="referrer" value="">
                <input type="hidden" name="first_touch_at" value="">
                <input type="hidden" name="landing_page" value="">
                <input type="hidden" name="utm_source" value="">
                <input type="hidden" name="utm_medium" value="">
                <input type="hidden" name="utm_campaign" value="">
                <input type="hidden" name="utm_term" value="">
                <input type="hidden" name="utm_content" value="">
                <input type="hidden" name="gclid" value="">
                <label>Your name</label>
                <input type="text" name="name" required>
                <label>Email</label>
                <input type="email" name="email" required>
                <label>Phone</label>
                <input type="tel" name="phone">
                <label>What do you need?</label>
                <select name="space_type">
                    <option value="">Any / not sure</option>
                    <option>Private office</option>
                    <option>Dedicated desk</option>
                    <option>Hot desk / coworking</option>
                    <option>Meeting room</option>
                    <option>Virtual office</option>
                    <option>Day pass</option>
                </select>
                <label>Team size</label>
                <select name="team_size">
                    <option>Just me</option>
                    <option>2–5</option>
                    <option>6–15</option>
                    <option>16+</option>
                </select>
                <button class="btn wide" type="submit">Get pricing &amp; tour</button>
            </form>
            {callbar(space)}
        </div>
"""


def space_card(space, market):
    p = f"/{market['slug']}"
    slug = space_slug(space)
    rating = space.get("google_rating", "").strip()
    reviews = space.get("review_count", "").strip()
    rating_html = (f'<span class="rating">★ {rating}</span> '
                   f'<span class="meta">({reviews} reviews)</span>') if rating else ""
    return f"""
        <div class="card">
            <h3><a href="{p}/space/{slug}/">{space['name']}</a></h3>
            <div class="meta">{space.get('neighborhood','')} · {space.get('city','')}, {space.get('state','')}</div>
            {rating_html}
            <div class="price">{price_summary(space)}</div>
            <div class="badges">{type_badges(space)}</div>
            <div class="badges">{amenity_badges(space)}</div>
            <a class="btn alt" href="{p}/space/{slug}/">View &amp; request tour →</a>
        </div>
"""


# --------------------------------------------------------------------------- #
# Brand-level pages
# --------------------------------------------------------------------------- #

def generate_brand_homepage(market_data):
    """Root page: market picker + brand pitch."""
    live = [(m, d) for m, d in market_data if d["spaces"]]
    total_spaces = sum(len(d["spaces"]) for _, d in live)
    desc = (f"{BRAND_TAGLINE}. Compare {total_spaces} workspaces across "
            f"{len(live)} Alabama markets and book a tour, free.")
    html = render_header(f"{BRAND} — {BRAND_TAGLINE}", desc, "/")
    html += f"""
    <section class="hero">
        <div class="container">
            <h1>Find the right workspace, anywhere in Alabama</h1>
            <p>Compare private offices, coworking, meeting rooms and virtual offices
               in every Alabama market — pricing, amenities and tours, all in one place.</p>
            <div class="stats">
                <div class="stat"><div class="n">{total_spaces}</div><div class="l">Workspaces</div></div>
                <div class="stat"><div class="n">{len(live)}</div><div class="l">Markets live</div></div>
                <div class="stat"><div class="n">{len(MARKETS)}</div><div class="l">Markets tracked</div></div>
                <div class="stat"><div class="n">Free</div><div class="l">Tour concierge</div></div>
            </div>
        </div>
    </section>
    <div class="container">
        <h2 class="section" id="markets">Pick your market</h2>
        <div class="grid">
"""
    for m, d in market_data:
        count = len(d["spaces"])
        if count:
            html += f"""            <a class="tile" href="/{m['slug']}/">
                <h3>{m['name']}</h3><div class="sub">{m['tagline']}</div>
                <span class="count">{count} workspaces</span>
            </a>
"""
        else:
            html += f"""            <div class="tile soon">
                <h3>{m['name']}</h3><div class="sub">{m['tagline']}</div>
                <span class="count">Coming soon</span>
            </div>
"""
    html += """        </div>
        <h2 class="section">Popular guides</h2>
        <div class="grid">
"""
    for g in GUIDES[:3]:
        gm = g.get("market", "huntsville")
        html += f"""            <a class="tile" href="/{gm}/guides/{g['slug']}/">
                <h3>{g['h1']}</h3><div class="sub">{g['meta']}</div>
            </a>
"""
    html += "        </div>\n    </div>\n" + render_footer()
    write(OUTPUT_DIR / "index.html", html)


def generate_list_your_space():
    html = render_header(
        f"List your space on {BRAND}",
        f"Get tour-ready leads from professionals searching for workspace "
        f"across Alabama. Free basic listing; referral and featured options.",
        "/list-your-space/")
    html += f"""
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> / List your space</div>
        <div class="split">
            <div>
                <h2 class="section">Get tour-ready leads</h2>
                <p style="color:var(--muted); margin-bottom:14px">
                   {BRAND} sends workspace-seekers straight to your front desk. Start
                   with a free listing; upgrade to featured placement or our referral
                   program and only pay when a lead becomes a member.</p>
                <div class="card"><h3>Free listing</h3><div class="meta">Name, location, amenities, map. Always free.</div></div>
                <div class="card"><h3>Featured</h3><div class="meta">Top placement in your market's neighborhood and space-type pages.</div></div>
                <div class="card"><h3>Referral</h3><div class="meta">We send tracked tour leads; you pay a referral fee only on closed members.</div></div>
            </div>
            {lead_form(source='operator')}
        </div>
    </div>
"""
    html += render_footer()
    write(OUTPUT_DIR / "list-your-space" / "index.html", html)


def generate_thank_you():
    html = render_header(
        f"Thanks — we'll be in touch | {BRAND}",
        "Your workspace request was received.",
        "/thank-you/", noindex=True)
    fire = (f"""    <script>
      if (window.gtag) gtag('event', 'generate_lead', {{ page: 'thank_you' }});
    </script>
""" if GA4_ID else "")
    html += f"""
    <div class="container">
        <div class="card" style="margin-top:40px; text-align:center">
            <h2 class="section" style="margin-top:6px">Thanks — request received ✅</h2>
            <p style="color:var(--muted); max-width:560px; margin:0 auto 8px">
               We're matching you with the right workspace and will follow
               up shortly with pricing and tour options — usually the same day.</p>
            <p style="margin-top:16px"><a class="btn" href="/">← Back to {BRAND}</a></p>
        </div>
    </div>
{fire}"""
    html += render_footer()
    write(OUTPUT_DIR / "thank-you" / "index.html", html)


# --------------------------------------------------------------------------- #
# Market-level pages
# --------------------------------------------------------------------------- #

def generate_market_homepage(market, d):
    p = f"/{market['slug']}"
    spaces, buckets_index, hoods_index = d["spaces"], d["buckets"], d["hoods"]
    market_guides = [g for g in GUIDES
                     if g.get("market", "huntsville") == market["slug"]]
    desc = (f"Coworking, private offices & meeting rooms in {market['name']}, AL. "
            f"Compare {len(spaces)} workspaces, pricing and amenities, and book a tour.")
    html = render_header(
        f"{market['name']} Coworking & Office Space | {BRAND}",
        desc, f"{p}/", market=market)
    html += f"""
    <section class="hero">
        <div class="container">
            <h1>Find the right workspace in {market['name']}</h1>
            <p>{market['tagline']}. Compare private offices, coworking, meeting rooms
               and virtual offices — pricing, amenities and tours in one place.</p>
            <div class="stats">
                <div class="stat"><div class="n">{len(spaces)}</div><div class="l">Workspaces</div></div>
                <div class="stat"><div class="n">{len(hoods_index)}</div><div class="l">Neighborhoods</div></div>
                <div class="stat"><div class="n">{len(buckets_index)}</div><div class="l">Space types</div></div>
                <div class="stat"><div class="n">Free</div><div class="l">Tour concierge</div></div>
            </div>
        </div>
    </section>
    <div class="container">
        <h2 class="section">Browse by space type</h2>
        <div class="grid">
"""
    for slug, (label, blurb) in SPACE_BUCKETS.items():
        count = len(buckets_index.get(slug, []))
        if not count:
            continue
        html += f"""            <a class="tile" href="{p}/{slug}/">
                <h3>{label}</h3><div class="sub">{blurb}</div>
                <span class="count">{count} spaces</span>
            </a>
"""
    html += """        </div>
        <h2 class="section">Browse by neighborhood</h2>
        <div class="grid">
"""
    for hood in sorted(hoods_index):
        html += f"""            <a class="tile" href="{p}/neighborhood/{slugify(hood)}/">
                <h3>{hood}</h3><div class="sub">Workspaces in {hood}</div>
                <span class="count">{len(hoods_index[hood])} spaces</span>
            </a>
"""
    html += "        </div>\n"
    if market_guides:
        html += f"""        <h2 class="section">{market['name']} workspace guides</h2>
        <div class="grid">
"""
        for g in market_guides[:3]:
            html += f"""            <a class="tile" href="{p}/guides/{g['slug']}/">
                <h3>{g['h1']}</h3><div class="sub">{g['meta']}</div>
            </a>
"""
        html += f"""            <a class="tile" href="{p}/guides/">
                <h3>All guides →</h3><div class="sub">Costs, comparisons and neighborhood breakdowns.</div>
            </a>
        </div>
"""
    html += """        <h2 class="section">Featured workspaces</h2>
"""
    featured = sorted(spaces, key=lambda s: float(s.get("google_rating") or 0),
                      reverse=True)[:6]
    for s in featured:
        html += space_card(s, market)
    html += "    </div>\n" + render_footer()
    write(OUTPUT_DIR / market["slug"] / "index.html", html)


def generate_bucket_page(market, slug, group):
    p = f"/{market['slug']}"
    label, blurb = SPACE_BUCKETS[slug]
    # Empty buckets still render (keeps market nav consistent) but are
    # noindexed and pitch the concierge instead of listings.
    html = render_header(
        f"{label} in {market['name']}, AL | {BRAND}",
        f"{blurb} in {market['name']}. Compare {len(group)} options and book a tour.",
        f"{p}/{slug}/", noindex=not group, market=market)
    count_line = (f"{blurb} — {len(group)} workspaces." if group else
                  f"{blurb}. No listed spaces in {market['name']} yet — tell us "
                  f"what you need and we'll source options for you, free.")
    html += f"""
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> / <a href="{p}/">{market['name']}</a> / {label}</div>
        <h2 class="section">{label} in {market['name']}</h2>
        <p class="meta">{count_line}</p>
        <div class="split">
            <div>
"""
    for s in sorted(group, key=lambda x: x["name"]):
        html += space_card(s, market)
    if not group:
        html += ("<div class='card'><h3>We'll find it for you</h3>"
                 "<div class='meta'>Our concierge knows the local market — "
                 "use the form and we'll come back with real options, usually "
                 "the same day.</div></div>\n")
    html += "            </div>\n"
    html += lead_form(source=f"bucket:{slug}", market=market)
    html += "        </div>\n    </div>\n" + render_footer()
    write(OUTPUT_DIR / market["slug"] / slug / "index.html", html)


def generate_neighborhood_page(market, hood, group):
    p = f"/{market['slug']}"
    html = render_header(
        f"Coworking & Office Space in {hood}, {market['name']} | {BRAND}",
        f"Workspaces in {hood}, {market['name']} — compare {len(group)} options and book a tour.",
        f"{p}/neighborhood/{slugify(hood)}/", market=market)
    html += f"""
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> / <a href="{p}/">{market['name']}</a> / {hood}</div>
        <h2 class="section">Workspaces in {hood}</h2>
        <p class="meta">{len(group)} workspaces in {hood}, {market['name']}.</p>
        <div class="split">
            <div>
"""
    for s in sorted(group, key=lambda x: x["name"]):
        html += space_card(s, market)
    html += "            </div>\n"
    html += lead_form(source=f"neighborhood:{slugify(hood)}", market=market)
    html += "        </div>\n    </div>\n" + render_footer()
    write(OUTPUT_DIR / market["slug"] / "neighborhood" / slugify(hood) / "index.html", html)


def generate_amenity_page(market, token, group):
    p = f"/{market['slug']}"
    label = AMENITY_LABELS[token]
    html = render_header(
        f"{label} Coworking in {market['name']} | {BRAND}",
        f"{market['name']} workspaces with {label.lower()} — compare {len(group)} options.",
        f"{p}/amenity/{slugify(token)}/", market=market)
    html += f"""
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> / <a href="{p}/">{market['name']}</a> / {label}</div>
        <h2 class="section">{market['name']} workspaces with {label}</h2>
        <p class="meta">{len(group)} workspaces offer {label.lower()}.</p>
        <div class="split">
            <div>
"""
    for s in sorted(group, key=lambda x: x["name"]):
        html += space_card(s, market)
    html += "            </div>\n"
    html += lead_form(source=f"amenity:{token}", market=market)
    html += "        </div>\n    </div>\n" + render_footer()
    write(OUTPUT_DIR / market["slug"] / "amenity" / slugify(token) / "index.html", html)


def generate_space_page(market, space):
    p = f"/{market['slug']}"
    slug = space_slug(space)
    name = space["name"]
    addr = space.get("full_address", "").strip()
    rating = space.get("google_rating", "").strip()
    reviews = space.get("review_count", "").strip()
    hood = space.get("neighborhood", "").strip() or market["name"]
    title = f"{name} — {hood} {market['name']} Coworking & Offices | {BRAND}"
    desc = (space.get("description", "").strip()
            or f"{name} in {hood}, {market['name']}. {price_summary(space)}.")[:160]

    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": name,
        "telephone": space.get("phone", ""),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": addr.split(",")[0] if "," in addr else addr,
            "addressLocality": space.get("city", ""),
            "addressRegion": space.get("state", ""),
            "postalCode": space.get("zip", ""),
            "addressCountry": "US",
        },
    }
    if space.get("latitude") and space.get("longitude"):
        try:
            schema["geo"] = {"@type": "GeoCoordinates",
                             "latitude": float(space["latitude"]),
                             "longitude": float(space["longitude"])}
        except ValueError:
            pass
    if rating:
        try:
            schema["aggregateRating"] = {"@type": "AggregateRating",
                                         "ratingValue": rating,
                                         "reviewCount": int(float(reviews or 0))}
        except ValueError:
            pass

    rating_html = (f'<span class="rating">★ {rating}</span> '
                   f'<span class="meta">({reviews} Google reviews)</span>') if rating else ""

    html = render_header(title, desc, f"{p}/space/{slug}/", market=market)
    html += f"""
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="{p}/">{market['name']}</a> / <a href="{p}/neighborhood/{slugify(hood)}/">{hood}</a> / {name}
        </div>
        <div class="split">
            <div>
                <h2 class="section" style="margin-top:22px">{name}</h2>
                <div class="meta">{addr}</div>
                {rating_html}
                <div class="price">{price_summary(space)}</div>
                <p style="margin:14px 0; color:var(--muted)">{space.get('description','')}</p>

                <h3 style="margin-top:20px">Space types</h3>
                <div class="badges">{type_badges(space) or '<span class="meta">Contact for details</span>'}</div>

                <h3 style="margin-top:16px">Amenities</h3>
                <div class="badges">{amenity_badges(space) or '<span class="meta">Contact for details</span>'}</div>

                <h3 style="margin-top:16px">Location</h3>
                <p><a class="btn alt" target="_blank"
                   href="https://www.google.com/maps/search/{quote(addr or name)}">Open in Google Maps →</a></p>
            </div>
            {lead_form(space, source='space', market=market)}
        </div>
        <script type="application/ld+json">
{json.dumps(schema, indent=2)}
        </script>
    </div>
"""
    html += render_footer()
    write(OUTPUT_DIR / market["slug"] / "space" / slug / "index.html", html)


def market_link_prefix(html_fragment, market):
    """Guide content is authored with market-relative links (href='/space/...');
    rewrite them to the market's path at render time."""
    return re.sub(r"href='/", f"href='/{market['slug']}/", html_fragment)


def generate_guide_page(market, guide):
    p = f"/{market['slug']}"
    slug = guide["slug"]
    path = f"{p}/guides/{slug}/"
    html = render_header(guide["title"], guide["meta"], path, market=market)

    body = ""
    for heading, section_html in guide["sections"]:
        body += (f"<h3 style='margin:26px 0 10px;font-size:20px'>{heading}</h3>\n"
                 f"{market_link_prefix(section_html, market)}\n")
    intro = market_link_prefix(guide["intro"], market)

    faq_html = ""
    if guide.get("faq"):
        faq_html = "<h3 style='margin:26px 0 10px;font-size:20px'>Frequently asked questions</h3>"
        for q, a in guide["faq"]:
            faq_html += (f"<div class='card' style='padding:16px 18px'>"
                         f"<strong>{q}</strong>"
                         f"<p style='color:var(--muted);margin-top:6px'>{a}</p></div>")

    schema = [{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": guide["h1"],
        "description": guide["meta"],
        "author": {"@type": "Organization", "name": BRAND},
        "publisher": {"@type": "Organization", "name": BRAND},
        "mainEntityOfPage": BASE_URL + path,
    }]
    if guide.get("faq"):
        schema.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            } for q, a in guide["faq"]],
        })

    html += f"""
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> / <a href="{p}/">{market['name']}</a> / <a href="{p}/guides/">Guides</a> / {guide['h1']}</div>
        <div class="split">
            <div>
                <h2 class="section" style="margin-top:18px">{guide['h1']}</h2>
                {intro}
                {body}
                {faq_html}
                <p style="margin-top:22px"><a class="btn alt" href="{p}/guides/">← All {market['name']} workspace guides</a></p>
            </div>
            {lead_form(source=f'guide:{slug}', market=market)}
        </div>
        <script type="application/ld+json">
{json.dumps(schema, indent=2)}
        </script>
    </div>
"""
    html += render_footer()
    write(OUTPUT_DIR / market["slug"] / "guides" / slug / "index.html", html)


def generate_guides_hub(market, market_guides):
    p = f"/{market['slug']}"
    html = render_header(
        f"{market['name']} Workspace Guides | {BRAND}",
        f"Local guides to coworking, offices and meeting rooms in {market['name']}: "
        f"costs, comparisons and neighborhood breakdowns.",
        f"{p}/guides/", market=market)
    html += f"""
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> / <a href="{p}/">{market['name']}</a> / Guides</div>
        <h2 class="section">{market['name']} workspace guides</h2>
        <div class="grid">
"""
    for g in market_guides:
        html += f"""            <a class="tile" href="{p}/guides/{g['slug']}/">
                <h3>{g['h1']}</h3><div class="sub">{g['meta']}</div>
            </a>
"""
    html += "        </div>\n    </div>\n" + render_footer()
    write(OUTPUT_DIR / market["slug"] / "guides" / "index.html", html)


# --------------------------------------------------------------------------- #
# Sitemap / robots / verification
# --------------------------------------------------------------------------- #

def generate_sitemap(market_data):
    urls = ["/", "/list-your-space/"]
    for m, d in market_data:
        if not d["spaces"]:
            continue
        p = f"/{m['slug']}"
        urls.append(f"{p}/")
        urls += [f"{p}/{b}/" for b in d["buckets"]]
        urls += [f"{p}/neighborhood/{slugify(h)}/" for h in d["hoods"]]
        urls += [f"{p}/amenity/{slugify(t)}/" for t in d["amenities"]
                 if t in AMENITY_PAGES]
        urls += [f"{p}/space/{space_slug(s)}/" for s in d["spaces"]]
        mg = [g for g in GUIDES if g.get("market", "huntsville") == m["slug"]]
        if mg:
            urls.append(f"{p}/guides/")
            urls += [f"{p}/guides/{g['slug']}/" for g in mg]
    body = "".join(
        f"    <url><loc>{BASE_URL}{u}</loc><changefreq>weekly</changefreq>"
        f"<priority>{'1.0' if u == '/' else '0.7'}</priority></url>\n" for u in urls)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               f"{body}</urlset>\n")
    write(OUTPUT_DIR / "sitemap.xml", sitemap)
    write(OUTPUT_DIR / "robots.txt",
          f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    if GOOGLE_SITE_VERIFICATION:
        fname = f"{GOOGLE_SITE_VERIFICATION}.html"
        write(OUTPUT_DIR / fname, f"google-site-verification: {fname}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def index_market(spaces):
    buckets = defaultdict(list)
    hoods = defaultdict(list)
    amenities = defaultdict(list)
    for s in spaces:
        for b in space_buckets(s):
            buckets[b].append(s)
        hoods[s.get("neighborhood", "").strip() or "Other"].append(s)
        for t in tokens(s, "amenities"):
            amenities[t].append(s)
    return {"spaces": spaces, "buckets": buckets, "hoods": hoods,
            "amenities": amenities}


def main():
    market_data = []
    for m in MARKETS:
        spaces = load_market_spaces(m)
        market_data.append((m, index_market(spaces)))
        print(f"{m['name']:24s} {len(spaces)} spaces")

    print("Generating brand homepage + shared pages...")
    generate_brand_homepage(market_data)
    generate_list_your_space()
    generate_thank_you()

    for m, d in market_data:
        if not d["spaces"]:
            continue
        print(f"Generating {m['name']}...")
        generate_market_homepage(m, d)
        for slug in SPACE_BUCKETS:
            generate_bucket_page(m, slug, d["buckets"].get(slug, []))
        for hood, group in d["hoods"].items():
            generate_neighborhood_page(m, hood, group)
        for t in AMENITY_PAGES:
            if d["amenities"].get(t):
                generate_amenity_page(m, t, d["amenities"][t])
        for s in d["spaces"]:
            generate_space_page(m, s)
        mg = [g for g in GUIDES if g.get("market", "huntsville") == m["slug"]]
        for g in mg:
            generate_guide_page(m, g)
        if mg:
            generate_guides_hub(m, mg)

    generate_sitemap(market_data)
    total = sum(len(d["spaces"]) for _, d in market_data)
    live = sum(1 for _, d in market_data if d["spaces"])
    print(f"\n✓ Site generated -> {OUTPUT_DIR}")
    print(f"  {total} spaces across {live} live markets "
          f"({len(MARKETS)} tracked)")


if __name__ == "__main__":
    main()
