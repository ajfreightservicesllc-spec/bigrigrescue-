# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Projects in this repo

- **FlexWorkspace** (`workspace-source/`) — active. Alabama workspace directory
  at flexworkspace.online. **Read `HANDOFF.md` first** for full state.
- **Big Rig Rescue** (`rigrescue-source/`, `bigrigrescue-redirect/`) — the
  owner's earlier I-40 truck repair directory. Unrelated; don't disturb.

## Working rules

- **Data integrity:** listings are real businesses only. Never invent phones,
  ratings, or prices — leave blank if unverified. No scraped photos (copyright);
  operator-supplied or self-taken only.
- **Deploy:** push to `workspace-source/` — GitHub Actions builds and deploys.
- **Owner works in the browser**, not a terminal. Prefer browser-based steps.

## Applied Learning

When something fails repeatedly, when I have to re-explain something, or when a
workaround is found for a tool limitation, add a one-line bullet here. Keep each
bullet under 15 words, no explanations. Only add things that will save time in
future sessions.

- Claude creates Gmail drafts but cannot send; user sends manually.
- Existing Gmail drafts keep original From address; switch via compose dropdown.
- Web sessions cannot run `firebase deploy`; push to GitHub, Actions deploys.
- Run `git add` from repo root; paths break when run inside `workspace-source/`.
- Owner uses Windows PowerShell: `py` not `python3`; scripts disabled by default.
- New agent definitions register only in a new session, not the current one.
- Sandbox lacks pandoc, pdftoppm, working LibreOffice; verify docx via XML extraction.
- Verify scraped emails before sending; template placeholders like `myemail@` bounce.
