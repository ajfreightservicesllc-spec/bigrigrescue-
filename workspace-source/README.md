# Workspace Directory — Q1 Build & Seed

A coworking / flexible-office / meeting-room directory built on the same
crawler → enriched-CSV → static-site pipeline as Big Rig Rescue, but aimed at a
high-ticket B2B niche. This is the tech for **Quarter 1** of the launch plan
(`../office-space-directory-12-month-launch-plan.md`): adapt the crawler to
workspace data, reach full local coverage, and ship a conversion-focused site.

## What's here

| File | Purpose |
|---|---|
| `workspace_crawler.py` | Reads a seed CSV of workspace locations, fetches each operator's site, and extracts space types, amenities, pricing signals, and tour offers. Resumable, checkpointed. |
| `workspace_generator.py` | Turns the enriched CSV into a static SEO site: homepage, space-type pages, neighborhood pages, amenity pages, individual space pages, sitemap + robots. |
| `data/huntsville_seed.csv` | **Real Huntsville, AL seed** — 8 actual coworking operators (crawler input). |
| `data/huntsville_enriched.csv` | Curated Huntsville enriched data the generator builds from (reproducible, tracked). |
| `data/workspace_seed_sample.csv` | Generic **seed** schema example (fictional). |
| `data/workspace_enriched_sample.csv` | Generic **enriched** example (fictional fallback). |
| `public/` | Generated site (git-ignored; run the generator to (re)build). |

> **Active metro: Huntsville, AL.** `huntsville_seed.csv` lists 8 real operators
> (Coin, Common Ground, Huntsville Hub, Office Hub, Spaces, Regus, Huntsville
> West). Space types/amenities in `huntsville_enriched.csv` come from crawling
> the reliable sites plus published info for the JS-rendered ones (Coin, Spaces,
> Regus). **Phone, ratings and pricing are intentionally blank** — fill them
> from a Google Places export and each operator's current rate card; don't
> publish unverified prices for real businesses.

## The conversion difference

Big Rig Rescue monetizes an emergency "call now" button. This niche monetizes
**tracked referral leads**, so every page is built around a
**"Request pricing & a tour"** form. Each submission carries a full attribution
payload — a unique `lead_id`, timestamp, the space, page, referrer, and
first-touch UTMs — so you can prove which lead came from you and collect the
referral commission. See **`LEAD-TRACKING.md`** for the field list, backend
setup (Formspree/Basin/self-hosted), GA4 conversions, and the reconciliation
workflow. There's also a `/list-your-space/` page that feeds operator sign-ups
(free listings, featured placement, referral deals).

## Run it

```bash
pip install beautifulsoup4 requests

# 1. Seed: put your metro's workspaces in data/workspace_seed_sample.csv
#    (or export from Google Places / Maps). Columns are documented in that file.

# 2. Enrich: crawl operator sites (resumable — run repeatedly until done)
python3 workspace_crawler.py     # writes data/workspace_enriched.csv

# 3. Generate the static site
python3 workspace_generator.py   # writes public/
```

If `data/workspace_enriched.csv` doesn't exist yet, the generator falls back to
the bundled sample so you can preview immediately.

## Before launch — edit the CONFIG block in `workspace_generator.py`

- `BRAND`, `METRO`, `METRO_TAGLINE`, `BASE_URL`
- `LEAD_ENDPOINT` — your form backend (Formspree/Basin/your own). **This is the
  revenue plumbing — wire it up before driving traffic.**
- `TRACKING_PHONE` — a call-tracking number (optional but recommended for
  referral attribution).

## Q1 checklist status

- [x] Crawler adapted to workspace data (space types, amenities, pricing, tours)
- [x] Conversion-focused static site generator (tracked lead form on every page)
- [x] Pipeline verified end-to-end — crawled the 8 real Huntsville sites live
- [x] Metro chosen + seeded: **Huntsville, AL** (8 operators, 6 neighborhoods)
- [x] Tracked lead flow: unique lead id, first-touch UTM attribution, GA4
      `generate_lead` conversion, thank-you page (browser-verified) — see
      `LEAD-TRACKING.md`
- [ ] Verify & fill phone, ratings (Google Places export) and pricing per operator
- [ ] Wire `LEAD_ENDPOINT` (form backend) + `GA4_ID` + tracking phone in CONFIG
- [ ] Sign referral agreements with operators (offline — see the launch plan)
