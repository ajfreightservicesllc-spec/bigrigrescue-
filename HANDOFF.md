# HANDOFF — this repo is Big Rig Rescue

**Updated:** 2026-07-31 · **Owner:** Rufus Jones (rufus@aiansweragency.com)

## FlexWorkspace moved out

The long FlexWorkspace handoff that used to be in this file is gone on purpose.
FlexWorkspace now lives in its own private repo:

> **`ajfreightservicesllc-spec/flex-workspace`**

Everything moved with it — `workspace_generator.py`, `data/markets/*.csv`,
`guides_content.py`, `lead-backend.gs`, `operator-outreach.md`,
`LEAD-TRACKING.md`, `DEPLOY.md`, and the Firebase deploy workflow. Its own
`README.md` and `CLAUDE.md` carry the state going forward. Ask for it by name in
a new session and it gets attached.

Verified after the split (2026-07-31): the deploy workflow in `flex-workspace`
has run green on every push to `main`, and flexworkspace.online serves from it.
Nothing in *this* repo touches that site.

## What's still here

| Path | What it is |
|---|---|
| `rigrescue-source/` | The I-40 truck repair directory — crawler, generator, built pages |
| `bigrigrescue-redirect/` | Redirect host for bigrigrescue.co |
| `business-niches-directory-ideas.md` | The 50-niche analysis that started FlexWorkspace |
| `office-space-directory-12-month-launch-plan.md` | The 12-month FlexWorkspace plan (kept as the origin doc) |
| `.claude/agents/inbox-manager.md` | Gmail triage agent — drafts only, never sends or deletes |
| `CLAUDE.md` | Standing working context — read first |

## Open item that is NOT in this repo

**The lead-backend dedupe fix is still not live.** `lead-backend.gs` in
`flex-workspace` dedupes on `lead_id`, but the *deployed* Apps Script behind
flexworkspace.online does not — confirmed 2026-07-30, when lead
`HW-MS7N7LV2-41LAG` produced two identical notification emails four minutes
apart. Fixing it is a manual paste into the Apps Script editor; a git push
cannot do it.
