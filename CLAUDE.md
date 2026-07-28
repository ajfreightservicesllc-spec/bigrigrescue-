# CLAUDE.md — Rufus Jones / working context

Always give me the next concrete action I can take today. Never tell me to
interview people, survey, or do market research — I learn by shipping, not
talking.

This file gives Claude Code standing context about who I am and what I'm
building, so every session starts already knowing the setup. Read it first.

---

## How I like to work

- **Be concise.** No filler, no preamble, no flattery — straight to the point,
  fewer words. When I ask a question, answer it directly first, then add detail
  only if needed.
- **Handle it end to end.** Don't ask technical questions — do the setup, run
  it, fix errors, and report back in plain English.
- **Blunt and direct.** If something's fake, broken, or useless, say so plainly
  — no sugarcoating, no theater.
- Tell me what it costs and what it produced in plain numbers.
- **Protect me legally** — voluntary-sale clauses, employment disclaimers,
  per-call definitions that hold up in a dispute.

## Check my email every session

At the start of every session, check my email and surface anything significant,
then continue.

- **Desktop sessions:** rufus@aiansweragency.com over IMAP (imap.gmail.com),
  app password in user env var `RUFUS_MAIL_APP_PW` (support@ is the same inbox).
- **Cloud sessions:** that env var and IMAP don't exist — use the **Gmail
  connector** (`mcp__Gmail__*`), which reaches the same inbox, or run the
  `inbox-manager` agent (`.claude/agents/inbox-manager.md`).

**Significant** = real replies from people, security alerts, receipts/invoices,
bounces, and anything about active deals/clients (ZeroBounce, Beyond Trash, West
Power, Reddit, etc.). Filter OUT marketing/newsletter noise (Quora, vendor
newsletters, Skool, HeyGen/Vapi promos, community-points spam).

Trashing the marketing noise is fine when I ask — move to Gmail Trash only.
**Never empty Trash and never permanently delete an email.**

## Definition of done

- It actually works, not just looks like it works. A trading bot isn't done
  until it places a real order; an app button isn't done until it does something
  real.
- The deliverable file exists and I can open it (PDF, docx, CSV, deployed site).
- Results reported in plain English: how many, how much, what it cost, what's
  still open.
- Any remaining blanks or blockers are named explicitly.

## Who I am

- Rufus Jones, based in Madison, AL.
- 20+ years in trucking and operations; hands-on with tech but not an engineer.
- **Give me complete, paste-ready files — never snippets.** I run them as-is on
  Windows/PowerShell. Partial code or "add this to line X" causes errors I can't
  debug. Whole file, every time.
- I run several businesses in parallel (below). I move fast and try a lot of
  things; help me point effort at what's actually close to money.
- Entities: **AJ Freight Services LLC** (freight) and **Alpha Kilo Logistics**
  (trucking company, employs drivers e.g. Julian Bell, separate office
  address/phone).
- Work with a builder/contractor known as **"Buzzard"** who set up some of the
  sites and apps.

## My businesses

**1. Logistics operations** — my day-job background. Transitioning from Peak
Logistics to Alpha Kilo / Shockoe Express under new ownership. Built a Firebase
terminal-management system, driver app, and Capacitor mobile conversion for it
(FleetOps Platform).

Current active projects across all ventures:

- **RigRescue** — directory of emergency truck repair shops along I-40, built by
  scraping Google Maps via the Outscraper API.
- **FleetOps Platform / Shockoe Express** — driver app (PWA on Firebase).
- **Lead-gen deal (West Power / Jeff Skinner)** — per-qualified-call pricing
  model with retainer + setup fee, tracked via CallRail.
- **Buzzard Trading** — Reddit (Devvit) app tracking stock mentions.
- **Stock-trading bot on Alpaca** — under scrutiny; flagged as not actually
  placing real trades yet.

**2. AI Answer Agency** — AI voice agents + SEO audits for local businesses.

- Multi-agent SEO audit pipeline (controller agent "Buzzard" dispatching
  sub-agents) that produces client-ready .docx reports.
- Live audits done on: westpowerservices.com, madisonappliance.com,
  classicintown.com.
- **Active warm deal: West Power Services** (owner Jeff Skinner, my old boss —
  biggest diesel/fleet/RV repair shop in Nashville). 6-month relationship.
  Proposal **SENT ~2026-07-18** — it is awaiting his reply. **Do NOT tell me to
  send it.** If it comes up, the useful question is whether Jeff has responded
  and whether a follow-up is due. Key finding: his homepage schema hard-codes ZIP
  37027 (Brentwood) while the shop is Nashville 37217 — suppressing local
  rankings. He still pays an older web-builder; pitch is complementary
  specialist work, not an attack on the incumbent.

**3. Lead-gen / lead reselling** — generate exclusive inbound calls, sell them to
ONE local company per area.

- Appliance repair (Alabama): established business, ~160-shop roster,
  exclusivity model, voice-AI intake.
- Dumpster rental (Huntsville first): $95/completed job, one company per area.
  6 real local prospects emailed; paid ads live in Huntsville/Madison.
- **Key constraint I need reminding of:** the exclusivity offer only works where
  I actually generate leads. A national list is inventory, not pipeline, until
  lead-gen is live in that market.

**4. Amazon affiliate sites** — everythingev.site (EV accessories, tag
everythingev-20) and mynailgun.co (coil nailers, tag mynailgun-20). Hosted on
Firebase project `aiansweragency-main`.

**5. Local business directories** — i40breakdown.com, bigrigrescue.co, and
**flexworkspace.online** (FlexWorkspace — coworking/office directory across 10
Alabama markets; built in this repo, see `HANDOFF.md`).

**6. Other builds** — a credit-recovery dashboard, a dividend-income investment
tool (Paycheck-to-Portfolio / GovTrade), a sweepstakes poker platform (Paradise
Poker). A book series under my name.

## My tooling & workflow

- Two computers (desktop + laptop), Google Drive in mirror mode syncing
  `C:\New folder\Projects\`.
- Windows / PowerShell, Python 3.14 at `C:\Python314\`.
- Lead-gen scripts live in `C:\dumpster\`.
- I split work: Chat-Claude for strategy, fact-checking, and writing prompts →
  Claude Code for builds, edits, and deploys.
- `web_fetch` serves stale/cached pages — hard-refresh (Ctrl+Shift+R) to confirm
  a deploy actually landed.
- Firebase hosting under `aiansweragency-main`, targets: i40breakdown,
  bigrigrescue, everythingev, **work-spacehuntsville** (FlexWorkspace).
- Desktop: HP custom build, NVIDIA Quadro P2000, 16GB RAM.

## The lead-gen toolkit in C:\dumpster

A pipeline of Python scripts (all paste-ready, no API cost unless noted):

- **build_list.py** — pulls a company list from Google Places (New) for a set of
  cities. Set `QUERIES` at top for the industry. Needs `GOOGLE_MAPS_API_KEY`.
  Free (Google's $200/mo tier). Classifies each result local / national / broker
  so I don't waste research on non-prospects. Variants:
  `build_list_appliance.py`, `build_list_national.py` (508 cities).
- **scrape_emails.py** — free HTTP+regex email scraper for any CSV with name +
  website columns. ~26% hit on appliance, higher on dumpster. Flags `[offsite!]`
  when the email domain ≠ the site domain (catches web-developer addresses).
  Saves after every row, resumes on Ctrl+C.
- **review_prospects.py** — filters a company list to a "pain band" (rating
  3.8–4.4, 20+ reviews) THEN scrapes — for a Google-review-engine outreach play.
- **dumpster_recon.py / dumpster_recon_prompt.md** — Claude agent that researches
  a company (pricing, hours, FMCSA fleet size, contacts, broker flags). Costs API
  credits (~10–20 web calls each). This is the expensive step.
- **dumpster_outreach.py / dumpster_outreach_prompt.md** — reads recon output,
  drafts one email per company, auto-skips brokers/nationals/junk. Drafts to CSV
  for review — never auto-sends.
- **one_lookup.py** — runs a single company through an existing agent (used for
  the West Power SEO audit; agent + environment IDs are in the file).

Output files: `*_companies.csv` = raw lists; `scraped_emails.csv` /
`review_prospects.csv` = scraped emails; `*_drafts.csv` = outreach drafts.

Sequence that keeps cost down: build list (free) → scrape emails (free) → run
the paid recon agent ONLY on companies that came back empty and sit in a market
I can serve.

## How to help me best

- Paste-ready whole files, always. Assume Windows/PowerShell.
- When I paste a giant block into PowerShell and it breaks on a `>>` prompt,
  it's the multi-line loop choking — give me a single-line version or a file to
  run, not a bigger paste.
- Downloads to my machine sometimes fail or cache a duplicate under a `(1)` name;
  when a file "won't download," it's usually that, not the file.
- Keep me honest about spending effort on inventory vs. closing warm deals. My
  three things closest to money are usually: the West Power SEO deal, the
  Huntsville dumpster shops, and the existing Alabama appliance business.
- I paste live API keys into terminals by accident — remind me to revoke and set
  them permanently with `[Environment]::SetEnvironmentVariable(...)`.

## Strategic context

When I ask anything strategic or growth-related, read `business.md` first for
context. *(Note: `business.md` is not in this repo — it lives on the desktop.
In a cloud session, ask me to paste it if a decision hinges on it.)*

## Decisions log

Whenever we make a meaningful architectural or strategic decision, log it to
`C:\Users\Rufus Jones\decisions\log.md` — date, the decision, the reasoning, and
the context. Log decisions, not conversations: skip routine builds, bug fixes,
and one-off tasks; only durable calls that would matter to revisit later.

*Cloud sessions can't write to `C:\`. Log to `decisions/log.md` in this repo
instead and tell me to sync it, or hand me the entry to paste.*

---

## Cloud vs. desktop sessions — what changes

This repo is usually worked on in **cloud sessions** (repo cloned into a Linux
container). What that means:

- My global `~/.claude/CLAUDE.md` on the desktop **does not load** — that's why
  this file exists in the repo. Keep it updated here.
- Nothing outside the repo persists. `C:\dumpster\`, `business.md`, the
  decisions log, env vars — none of it is reachable.
- Claude **cannot deploy Firebase from a cloud session** (no credentials). Push
  to `workspace-source/` and GitHub Actions deploys.
- Claude **cannot send email** — Gmail drafts only; I send.
- Paths are Linux (`/home/user/<repo>/`), not `C:\`.

## This repo

- **FlexWorkspace** (`workspace-source/`) — active. Alabama workspace directory
  at flexworkspace.online. **Read `HANDOFF.md`** for full state: infrastructure,
  data, outreach status, next actions.
- **Big Rig Rescue** (`rigrescue-source/`, `bigrigrescue-redirect/`) — the
  earlier I-40 truck repair directory. Don't disturb.

**Directory data rules:** listings are real businesses only. Never invent phones,
ratings, or prices — leave blank if unverified. No scraped photos (copyright);
operator-supplied or self-taken only.

---

## Applied Learning

When something fails repeatedly, when I have to re-explain something, or when a
workaround is found for a tool limitation, add a one-line bullet here. Keep each
bullet under 15 words, no explanations. Only add things that will save time in
future sessions.

- "How did emails do" usually means SCRAPED, not sent or received. Ask.
- Check what's actually built/deployed before summarizing a project's status.
- Scraped emails from font foundries are CSS artifacts, not real contacts.
- Never cold-email a list without screening out my own clients first.
- Claude creates Gmail drafts but cannot send; user sends manually.
- Existing Gmail drafts keep original From address; switch via compose dropdown.
- Cloud sessions cannot run `firebase deploy`; push to GitHub, Actions deploys.
- Run `git add` from repo root; paths break when run inside subdirectories.
- New agent definitions register only in a new session, not the current one.
- Cloud sandbox lacks pandoc, pdftoppm, working LibreOffice; verify docx via XML.
- Verify scraped emails before sending; template placeholders like `myemail@` bounce.
- Global desktop CLAUDE.md never loads in cloud sessions; keep it in the repo.
