# Deploy — Firebase Hosting

The site deploys to the **`work-spacehuntsville`** Hosting site inside your
existing **`aiansweragency-main`** Firebase project (the same project that hosts
Big Rig Rescue). This config only references the `work-spacehuntsville` site, so
deploying here never touches your other sites.

Live URLs:
- https://work-spacehuntsville.web.app
- https://work-spacehuntsville.firebaseapp.com

> **Note:** the site shows Firebase's "Site Not Found" page until the first
> successful deploy. Cloud (web) Claude sessions can't deploy directly — they
> have no Firebase credentials — which is why auto-deploy below exists.

## Option A — Auto-deploy from GitHub (recommended, one-time setup)

`.github/workflows/deploy-workspace.yml` builds and deploys automatically on
every push that touches `workspace-source/`. One-time setup:

1. Open the [Firebase console](https://console.firebase.google.com) →
   `aiansweragency-main` → ⚙️ Project settings → **Service accounts** →
   **Generate new private key**. A JSON file downloads.
2. On GitHub: repo → Settings → Secrets and variables → **Actions** →
   **New repository secret**.
   - Name: `FIREBASE_SERVICE_ACCOUNT_AIANSWERAGENCY_MAIN`
   - Value: paste the *entire contents* of that JSON file.
3. Done. Every push now deploys; you can also trigger it manually from the
   Actions tab ("Run workflow").

> Treat that JSON key like a password: paste it only into GitHub's secret
> field — never commit it to the repo or share it in chat.

## Option B — Deploy from your computer

```bash
npm install -g firebase-tools   # once
firebase login                  # once

cd workspace-source
python3 workspace_generator.py                     # builds public/ (git-ignored)
firebase deploy --only hosting:work-spacehuntsville
```

Either option: the site is live at the URLs above within seconds of deploy.

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
