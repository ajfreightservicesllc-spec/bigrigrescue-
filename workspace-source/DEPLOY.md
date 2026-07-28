# Deploy — Firebase Hosting

The site deploys to the **`work-spacehuntsville`** Hosting site inside your
existing **`aiansweragency-main`** Firebase project (the same project that hosts
Big Rig Rescue). This config only references the `work-spacehuntsville` site, so
deploying here never touches your other sites.

Live URLs:
- https://work-spacehuntsville.web.app
- https://work-spacehuntsville.firebaseapp.com

## First-time setup (once)

```bash
npm install -g firebase-tools   # if you don't have it
firebase login
```

## Deploy (every time)

The generated site (`public/`) is git-ignored, so **build first, then deploy**:

```bash
cd workspace-source
python3 workspace_generator.py                     # builds public/
firebase deploy --only hosting:work-spacehuntsville
```

That's it — the site is live at the URLs above within a few seconds.

## Before your real launch

Edit the CONFIG block in `workspace_generator.py` and re-run the generator so
the deployed site is fully wired:

- `LEAD_ENDPOINT` — your form backend (leads must land somewhere you control).
- `GA4_ID` — your GA4 measurement id (then mark `generate_lead` a key event).
- `TRACKING_PHONE` — a call-tracking number.

`BASE_URL` is already set to `https://work-spacehuntsville.web.app`. When you
connect a custom domain (e.g. `huntsvilleworkspaces.com`) in the Firebase
console, update `BASE_URL` to the custom domain and regenerate so canonical
tags, the sitemap, and the lead-form redirect use it.

## Notes

- `trailingSlash: true` matches the generator's directory-style URLs
  (`/space/<name>/`, `/neighborhood/<name>/`).
- To preview locally before deploying: `firebase emulators:start --only hosting`
  (or just open `public/index.html`).
- If you later want a custom domain: Firebase console → Hosting →
  `work-spacehuntsville` → Add custom domain, then update `BASE_URL`.
