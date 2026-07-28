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
| `data/workspace_seed_sample.csv` | Sample **seed** schema (crawler input). Replace with a real Google Places export for your metro. |
| `data/workspace_enriched_sample.csv` | Sample **enriched** output so the generator runs out of the box. |
| `public/` | Generated site (git-ignored; run the generator to (re)build). |

> The bundled Raleigh, NC rows are **fictional sample data** to demonstrate the
> pipeline — not real business listings. Replace them with your metro's data.

## The conversion difference

Big Rig Rescue monetizes an emergency "call now" button. This niche monetizes
**tracked referral leads**, so every page is built around a
**"Request pricing & a tour"** form. Each submission includes hidden fields
(`space_name`, `space_address`, `source`, `metro`) so you can attribute — and
get paid for — referral commissions. There's also a `/list-your-space/` page
that feeds operator sign-ups (free listings, featured placement, referral deals).

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
- [x] Pipeline verified end-to-end on sample data
- [ ] Seed your metro to ~100% coverage (needs a real Google Places export)
- [ ] Wire `LEAD_ENDPOINT` + tracking phone
- [ ] Sign referral agreements with operators (offline — see the launch plan)
