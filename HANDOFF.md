# FlexWorkspace — Session Handoff

**Last updated:** 2026-07-28 · **Owner:** Rufus (rufus@aiansweragency.com)

Read this first in a new session. It covers what exists, where it lives, what
state it's in, and what to do next.

---

## 1. What this is

**FlexWorkspace** (flexworkspace.online) — a directory of coworking, private
offices and meeting rooms across **10 Alabama markets**. Revenue model, in
priority order:

1. **Broker referral commissions** — the money engine. **10% of a referred
   customer's first 12 months**; nothing on leads that don't close.
2. **Featured listings / operator subscriptions** — $39–$99/mo (not yet sold).
3. **Ads / affiliates** — later.

Built on the same pipeline as the owner's earlier project, Big Rig Rescue
(also in this repo): **crawler → enriched CSV → static site generator → Firebase**.

**Strategy:** don't fight LiquidSpace/Coworker nationally. Own Alabama market by
market, starting with Huntsville. Full 12-month plan in
`office-space-directory-12-month-launch-plan.md`.

---

## 2. Live infrastructure

| Thing | Where | State |
|---|---|---|
| **Primary site** | https://flexworkspace.online | ✅ live (200) |
| Firebase URL (same site) | https://work-spacehuntsville.web.app | ✅ live, redirects intact |
| **Firebase project** | `aiansweragency-main`, hosting site `work-spacehuntsville` | ✅ |
| **Auto-deploy** | `.github/workflows/deploy-workspace.yml` | ✅ every push to `workspace-source/` |
| Deploy secret | GitHub secret `FIREBASE_SERVICE_ACCOUNT_AIANSWERAGENCY_MAIN` | ✅ set |
| **Analytics** | GA4 `G-T5F8V3Y1XY` | ✅ on every page |
| **Search Console** | property on the site; sitemap processed | ✅ 107–108 URLs discovered |
| **Lead ledger** | Google Sheet "Huntsville Workspaces — Leads" | ✅ receiving |
| **Lead backend** | Google Apps Script web app (`/exec`), source in `workspace-source/lead-backend.gs` | ✅ tested end-to-end |
| **Email** | sends as `rufus@aiansweragency.com` from the connected Gmail | ✅ alias verified |

**Deploy is automatic.** Push anything under `workspace-source/` and the site
rebuilds and publishes in ~1 minute. Nobody needs to run Firebase CLI.

---

## 3. The codebase

Everything for this project is under **`workspace-source/`**:

| File | Purpose |
|---|---|
| `workspace_generator.py` | The static site generator. CONFIG block at the top holds brand, markets, `LEAD_ENDPOINT`, `GA4_ID`, verification token. |
| `guides_content.py` | SEO guide articles (6 Huntsville guides). Each has `slug/title/meta/h1/intro/sections/faq`. Add `"market": "<slug>"` to target another market. |
| `workspace_crawler.py` | Enriches operator data by crawling their sites (space types, amenities, prices, tour offers). Resumable. |
| `data/markets/<slug>.csv` | **The data.** One CSV per market — this is what you edit to add/fix listings. |
| `lead-backend.gs` | Google Apps Script source for the lead backend (already deployed). |
| `LEAD-TRACKING.md` | How lead attribution works + reconciliation workflow. |
| `DEPLOY.md` | Deploy details and custom-domain notes. |
| `operator-outreach.md` | Outreach playbook: template, per-operator openers, contact roster, cadence, agreement terms. |
| `assets/photos/` | Drop `<space-slug>.jpg` here → appears on that listing automatically. |

**Build locally:** `cd workspace-source && python3 workspace_generator.py`
(writes `public/`, which is git-ignored).

**Site structure:** `/` (market picker) → `/<market>/` → `/<market>/space/<slug>/`,
plus `/<market>/{private-office,coworking,meeting-rooms,virtual-office,day-pass,event-space}/`,
`/<market>/neighborhood/<n>/`, `/<market>/guides/<slug>/`.

---

## 4. Markets & data (32 operators)

| Market | Operators | Notes |
|---|---|---|
| Huntsville | 8 | Flagship. Has all 6 SEO guides. |
| Mobile | 7 | Incl. Regus Battle House, 2× HQ |
| Birmingham | 4 | Forge, Innovation Depot, Thrive, Execusuites |
| Montgomery | 4 | Regus RSA Dexter, Wellness Oasis, JC Federal, BSA Center |
| Auburn–Opelika | 2 | CoLab, Connect Workspace |
| Dothan | 2 | Just Relax, Poplar Building |
| Fairhope–Daphne | 2 | Magnolia, Daphne CoWork |
| Tuscaloosa | 1 | The EDGE (UA center) |
| Decatur | 1 | Garden Coworking |
| Florence–Shoals | 1 | Keystone Business Centre |

**Data integrity rules that have been followed — keep following them:**
- Every listing is a **real business** from published sources.
- **Phone / ratings / prices are left blank unless verified.** Never invent them.
  The site shows "Pricing on request" rather than a wrong number.
- **No scraped photos** — copyright. Only operator-supplied or self-taken.
- Guide prices are stated as *market ranges* with a disclaimer, never as a
  specific operator's rate.

**Thin markets** (Tuscaloosa, Decatur, Florence, Dothan) need deeper research.
Empty space-type pages render `noindex` with a concierge pitch so nav never 404s.

---

## 5. Lead flow (the revenue plumbing)

Visitor → "Request pricing & a tour" form → Apps Script → **Google Sheet row +
email to `ajfreightservicesllc@gmail.com`** → visitor lands on `/thank-you/`
(fires GA4 `generate_lead`).

Every lead carries: `lead_id`, `captured_at`, space name/address, `source`,
`metro`, contact details, page/referrer, and **first-touch UTMs** (persisted in
localStorage, so a lead converting weeks later still credits the original
campaign). That `lead_id` is the evidence you invoice referrals against.

**Verified working end-to-end** (test lead landed in Sheet + inbox).

⚠️ Known test rows to ignore in the ledger: `HW-TEST-0002`, and one from
"JONES RUFUS TODD".

---

## 6. Outreach status — 14 of 32 operators contacted

**✅ Emailed (14).** Huntsville (4, sent earlier): Coin/Will, Huntsville West,
Common Ground, Office Hub. Statewide (10, sent 2026-07-28 from the Rufus
address): Forge, Innovation Depot, The EDGE, CoLab, Keystone, Fuse Factory,
Container Yard Works, Wellness Oasis, JC Federal, BSA Center.

**⚠️ Notes on that batch:**
- **BSA Center and JC Federal each got the email twice** (an earlier send from
  the gmail address, then the Rufus version). If they reply confused, that's why.
- **Daphne CoWork bounced** — the crawled address was a website-template
  placeholder. Reach them at **(251) 327-3723** or their contact form. Their
  listing data has since been corrected.

**📞 Not yet contacted — no published email (~11):** Innovation Portal
(251-202-7165), ProHQ (251-423-8245), Thrive, Execusuites, Wellness-adjacent
Montgomery gaps, Garden Coworking (Facebook), Just Relax, Poplar Building,
Connect Workspace, Magnolia, Daphne CoWork.

**🏢 IWG partner program — not yet applied.** One application covers all 7
Regus / Spaces / HQ listings across Huntsville, Mobile, Montgomery. Local
managers cannot sign custom referral deals, so this is the only route for them.

**Referral agreement:** a one-page Word doc was generated for sending when an
operator says "send the agreement." It is **not committed to the repo** — it
lives in the owner's downloads from the chat. Regenerate if needed; terms are
documented in `operator-outreach.md`. Owner should have a lawyer review before
first signing.

---

## 7. Automation in place

- **Auto-deploy** on push (see above).
- **`inbox-manager` agent** — `.claude/agents/inbox-manager.md`. Triages Gmail,
  labels/archives, and **drafts** replies to operator mail with full business
  context. Hard rules: never send, never delete, never touch financial/legal/
  security mail. Invoke with `subagent_type: "inbox-manager"`.
- **Daily routine** "Daily inbox triage — FlexWorkspace", 7:00 AM Central.
  ⚠️ **Currently missing the Gmail connector** — the org doesn't allow attaching
  connectors via the API. Owner must attach Gmail to it in the claude.ai
  Routines UI, or it will just report that Gmail is unavailable.

---

## 8. Next actions, highest value first

1. **Handle operator replies** — run the inbox manager; draft responses; when
   someone says "send the agreement," attach the .docx (agents can't attach).
2. **Day-3 bump emails** to non-responders (playbook has the wording).
3. **Phone outreach** to the ~11 operators with no email — Mobile first (4 of
   them, all with published numbers).
4. **Apply to the IWG partner referral program** — unlocks 7 listings at once.
5. **Deepen thin markets** — Tuscaloosa, Decatur, Florence, Dothan need more
   operators researched and seeded.
6. **Write guides for market #2** (Birmingham) — guides are what pull search
   traffic; only Huntsville has them. Add `"market": "birmingham"` to entries in
   `guides_content.py`.
7. **Backfill photos** as operators send them → `assets/photos/<space-slug>.jpg`.
8. **Later:** Google Places API to backfill phones/ratings/photos legitimately
   for operators who never reply (needs billing enabled; ~$0 at this volume).

---

## 9. Repo / PR state

- **Branch:** `claude/business-niches-directory-79ex07` (23 commits ahead of `main`)
- **PR #1** — open, draft, mergeable, no review comments. Title still says
  "Add 50 directory business niche ideas" because that's how the work started;
  it has since grown into the whole FlexWorkspace build.
- Also in the repo: the original **Big Rig Rescue** site (`rigrescue-source/`,
  `bigrigrescue-redirect/`) — unrelated to FlexWorkspace, don't disturb it.
- Strategy docs at repo root: `business-niches-directory-ideas.md` (the original
  50-niche analysis) and `office-space-directory-12-month-launch-plan.md`.

---

## 10. Gotchas for the next session

- **Gmail connector reaches `ajfreightservicesllc@gmail.com`**, which is where
  Rufus mail arrives and where the Sheet/Apps Script live. Send-as alias means
  outbound shows `rufus@aiansweragency.com`.
- **Claude cannot send email** — drafts only, by design. Same for attachments.
- **Claude cannot run `firebase deploy`** from a web session (no credentials) —
  that's exactly why auto-deploy via GitHub Actions exists. Just push.
- **Existing Gmail drafts keep their original From address**; the alias only
  applies to newly composed mail. Switch it in the compose From dropdown.
- The owner works on **Windows/PowerShell** and prefers browser-based workflows
  over local terminal commands.
