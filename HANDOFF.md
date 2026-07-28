# HANDOFF — FlexWorkspace

**Updated:** 2026-07-28 · **Owner:** Rufus Jones (rufus@aiansweragency.com)
**Read `CLAUDE.md` first** for working style and business context.

---

## Where we started

Rufus asked for 50 business-niche ideas for a new directory site, building on
his proven Big Rig Rescue playbook (crawler → CSV → static site → Firebase).
That analysis is in `business-niches-directory-ideas.md`. He picked **coworking
/ flexible office space**, and we built it end to end in one session.

## Decisions locked in

| Decision | Rationale |
|---|---|
| **Niche: coworking / flex office** | High ticket (one private-office referral ≈ $1,000+), fragmented operators, weak local SEO to beat |
| **Huntsville first, then all 10 AL markets** | Own one metro before cloning; aerospace/defense growth |
| **One brand, market paths** (`/huntsville/`, `/birmingham/`…) | SEO authority compounds on one domain instead of splitting |
| **Domain: flexworkspace.online** | `.com` taken; name describes the product, no geographic ceiling |
| **Monetization: 10% of a referral's first 12 months** | Lower than the 10–15% range to close first agreements faster |
| **Referral fee only on closed customers** | Removes operator risk; listings stay free forever |
| **Never invent data** | Phones/ratings/prices blank unless verified; no scraped photos (copyright); guide prices as market ranges with disclaimer |
| **Auto-deploy via GitHub Actions** | Cloud sessions can't run `firebase deploy`; Rufus doesn't want a terminal |

## What shipped

- **Live site:** https://flexworkspace.online — 10 Alabama markets, 32 real
  operators, ~138 pages, 107 in sitemap, zero broken links.
- **Lead capture, tested end to end:** form → Google Apps Script → Sheet row +
  email, with `lead_id`, timestamps, and first-touch UTM attribution (persisted
  in localStorage) — the evidence chain for invoicing referrals.
- **GA4** `G-T5F8V3Y1XY` on every page, `generate_lead` event on submit and
  thank-you.
- **Search Console** verified; sitemap processed, 107 URLs discovered.
- **6 SEO guides** (Huntsville) with Article + FAQPage schema.
- **Auto-deploy** on every push to `workspace-source/`.
- **Outreach:** 14 of 32 operators emailed; one-page referral agreement (.docx)
  generated; playbook with per-operator openers written.
- **`inbox-manager` agent** — triages Gmail, drafts replies, never sends/deletes.
- **CLAUDE.md distributed to all 13 of Rufus's repos** (see "Session model").

## Key files

| File | What it is |
|---|---|
| `CLAUDE.md` | Standing context — read first |
| `workspace-source/workspace_generator.py` | The site generator; CONFIG block at top |
| `workspace-source/data/markets/<slug>.csv` | **The data** — edit here to add/fix listings |
| `workspace-source/guides_content.py` | SEO guide articles; add `"market": "<slug>"` to target a market |
| `workspace-source/operator-outreach.md` | Outreach playbook, contact roster, agreement terms |
| `workspace-source/LEAD-TRACKING.md` | Attribution fields + referral reconciliation workflow |
| `workspace-source/DEPLOY.md` | Deploy details |
| `.claude/agents/inbox-manager.md` | Email triage agent |
| `office-space-directory-12-month-launch-plan.md` | The 12-month plan we're executing |

Build: `cd workspace-source && python3 workspace_generator.py` → writes
`public/` (git-ignored). Push to deploy.

## Running state

- **Branch** `claude/business-niches-directory-79ex07`, **PR #1** open/draft,
  mergeable, no review comments. (Title still says "50 niches" — that's just how
  it started.)
- **Emailed (14):** Huntsville — Coin/Will, Huntsville West, Common Ground,
  Office Hub. Statewide — Forge, Innovation Depot, The EDGE, CoLab, Keystone,
  Fuse Factory, Container Yard Works, Wellness Oasis, JC Federal, BSA Center.
  **No replies yet as of handoff.**
- ⚠️ BSA Center and JC Federal each got the email **twice** (send from the gmail
  address, then again from the Rufus address).
- ⚠️ Daphne CoWork **bounced** — scraped address was a site-template
  placeholder. Reach at (251) 327-3723. Listing data since corrected.
- ⏳ **An inbox-manager run was launched and had not reported back** when this
  handoff was written. Re-run it in the new session.
- ⚠️ **Daily routine** "Daily inbox triage — FlexWorkspace" (7 AM Central) exists
  but **has no Gmail connector** — the org blocks attaching connectors via API.
  Rufus must attach Gmail in the claude.ai Routines UI or it will report
  "Gmail unavailable" every morning.

## What's left — highest value first

1. **Handle operator replies.** Run the inbox manager. When someone says "send
   the agreement," Rufus must attach the .docx — agents can't attach files.
2. **Day-3 bump emails** to non-responders (wording in the playbook).
3. **Phone outreach** — ~11 operators publish no email. Mobile first: Innovation
   Portal (251-202-7165), ProHQ (251-423-8245), plus Daphne CoWork.
4. **IWG partner referral program** — one application covers all 7 Regus /
   Spaces / HQ listings. Local managers can't sign custom deals.
5. **Deepen thin markets** — Tuscaloosa (1), Decatur (1), Florence (1),
   Dothan (2) need more operators researched.
6. **Birmingham guides** — guides drive the search traffic; only Huntsville has
   them.
7. **Photos** — as operators send them, drop into
   `workspace-source/assets/photos/<space-slug>.jpg`; they appear automatically.
8. **Later:** Google Places API to legitimately backfill phones/ratings/photos
   for operators who never reply.

## Open questions

- Has any operator replied? (Unknown at handoff — check inbox first thing.)
- Did Rufus attach Gmail to the daily routine, or should it be reconverted to a
  plain reminder?
- Wellness Oasis address conflict: listing says Kershaw Industrial Blvd, their
  domain says Pike Road. Their reply settles it.
- Daphne CoWork phone: their site says 251-327-3723, aggregators say
  251-517-9425. Confirm when calling.
- Should PR #1 be merged to `main`, or keep accumulating work on the branch?
- `business.md` (referenced in CLAUDE.md for strategy context) lives on Rufus's
  desktop and isn't in any repo — ask him to paste it if a decision needs it.

## Session model — important

Rufus works from a **Windows desktop** but these are **cloud sessions**: the repo
is cloned into a Linux container, and his desktop `~/.claude/CLAUDE.md` does
**not** load. That's why CLAUDE.md was copied into **all 13 of his repos**
(pushed to `main` in each, since cloud sessions clone `main`). They're now 13
independent copies — if one changes meaningfully, say "sync my CLAUDE.md to all
repos."

Other constraints: Claude can't send email (drafts only), can't attach files,
can't deploy Firebase from a cloud session, and can't see anything on `C:\`.
