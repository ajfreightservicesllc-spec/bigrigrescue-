# Tracked Lead Flow

The revenue plumbing for the directory. Every "Request pricing & a tour" form
submits a fully-attributed lead so you can **prove which lead came from you** and
collect the referral commission without disputes.

## What gets captured on every lead

| Field | Where it comes from | Why it matters |
|---|---|---|
| `lead_id` | generated client-side (`HW-XXXX-XXXX`) | The reference number you and the operator both cite. Unique per submission. |
| `captured_at` | client timestamp (ISO) | When the lead was created. |
| `space_name`, `space_address` | the listing the visitor was on | Which operator the referral belongs to. |
| `source` | the page type (`space`, `neighborhood:downtown`, `bucket:private-office`, `operator`, …) | Which part of the site drove it. |
| `metro` | config | Multi-metro safe. |
| `page_url`, `page_path`, `referrer` | browser | Exact page + how they arrived. |
| `first_touch_at`, `landing_page` | first visit, persisted | Original entry point, even if they convert later. |
| `utm_source/medium/campaign/term/content`, `gclid` | first visit, persisted in `localStorage` | Marketing attribution (ads, email, partners) that survives navigation. |
| name, email, phone, space_type, team_size | the visitor | The actual enquiry. |

**First-touch attribution** is the key mechanic: UTMs and referrer are captured
on the visitor's *first* page and stored in `localStorage`, so a lead who finds
you via a Google search today and submits a form next week still carries
`utm_source=google` (or the campaign/partner that referred them). Each pageview
still gets a fresh `lead_id`.

All of this lives in `render_tracking_js()` in `workspace_generator.py`; the
hidden fields are injected into every form by `lead_form()`. Verified in a real
browser (Chromium) — UTM capture, persistence, and unique IDs all work.

## Wiring the backend (pick one)

The site is static, so a form backend receives the POST. Set `LEAD_ENDPOINT` in
the generator CONFIG to your endpoint. The form already sends `_next` (redirect
to `/thank-you/`), `_subject`, and a `_gotcha` honeypot for spam.

**Option A — Formspree (fastest to launch)**
1. Create a form at formspree.io; copy its endpoint into `LEAD_ENDPOINT`.
2. In form settings, allow the hidden fields (they pass through automatically).
3. Connect Formspree → Google Sheets (built-in) so every lead appends a row
   with all the fields above. That sheet is your ledger.

**Option B — Basin** — same idea (basin.com), also has Sheets/Zapier export and
a honeypot; drop-in compatible with the `_next`/`_subject` fields.

**Option C — Self-hosted (most control, no per-lead fees)** — a Cloudflare
Worker or Google Apps Script web app that accepts the POST and appends to a
Google Sheet / Airtable. Point `LEAD_ENDPOINT` at it. Use this once volume makes
per-lead pricing annoying.

> Whatever you choose, the destination must be a **spreadsheet or CRM you
> control** — that ledger is what you reconcile against operator move-ins.

## Call tracking (the other half of leads)

Phone calls convert too. Set `TRACKING_PHONE` to a **call-tracking number**
(CallRail, Phone.com, Google Voice) that forwards to you or the operator. Then
calls are logged with the same rigor as form leads. Leave it blank and each
listing shows the operator's own number (untracked — fine to start, but you
can't prove those referrals).

## GA4 conversions

Set `GA4_ID` in CONFIG. Then:
- Every page loads GA4.
- A `generate_lead` event fires on form submit **and** on the `/thank-you/`
  page view.
- In GA4 → Admin → Events, mark `generate_lead` as a **key event (conversion)**.
Now your analytics conversions and your lead ledger reconcile.

## The reconciliation workflow (how you actually get paid)

1. **Ledger:** every lead lands in your sheet with `lead_id`, `space_name`,
   `captured_at`, contact info, and source/UTM.
2. **Hand-off:** forward tour-ready leads to the operator (email/CRM), always
   referencing the `lead_id` and date.
3. **Match on close:** when an operator reports a new member/move-in, match it to
   your ledger by `lead_id` (or name + `space_name` + date window).
4. **Invoice:** bill the referral per your signed agreement (typically 10–15% of
   first-12-month contract value). The `lead_id` + timestamp + captured contact
   details are your evidence if attribution is questioned.
5. **Audit monthly:** compare your closed-referral count to each operator's
   move-ins to catch under-reporting.

## Test it before launch

Load any space page with fake UTMs and confirm the hidden fields populate, e.g.:

```
open  public/space/huntsville-west/index.html?utm_source=google&utm_medium=cpc&utm_campaign=test&gclid=ABC123
```

Inspect the form's hidden inputs (DevTools) — `lead_id`, `captured_at`,
`utm_source`, `gclid` should all be filled. Submit once with `LEAD_ENDPOINT` set
and confirm a fully-populated row lands in your sheet and you're redirected to
`/thank-you/`.
