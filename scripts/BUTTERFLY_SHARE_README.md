# Butterfly share surface — how to use

A hidden-URL surface for sharing *select* Juno × Google working documents at
an unguessable jmkay.com URL — no email attachments, easy on/off per document.
Not indexed by Google, not in the site nav or sitemap. Slug-only (the URL is
the key); no password.

**The project slug is secret. Treat the base URL like a password.**
Base URL: `https://jmkay.com/share/1806aca63077/`

## How the toggle works
- The manifest lives WITH the project (not in this repo):
  `~/Desktop/CLAUDIUS/Work/Juno-Google-RFP/_command/share_manifest.json`
- **Only docs with `"live": true` render a page.** A `live:false` doc produces
  **no page at all** — flipping it off truly removes it from the web.
- To flip a doc on or off: edit its `"live"` in the manifest, then rebuild + push.

## To put a document live (or take one down)
1. Open `_command/share_manifest.json` in the project.
2. Set the doc's `"live"` to `true` (or `false`).
   - Before going live, make sure the `source_path` points at a **clean,
     for-client version** — not an internal working draft. Run it through
     citation-guard first. Get David's OK before anything Google-adjacent goes
     on a URL Google didn't provision.
3. In Terminal:
   `cd ~/Documents/GitHub/jmkay-website && python3 scripts/build_butterfly_share.py`
   (needs `pip3 install markdown` once; `pandoc` on PATH for .docx.)
4. Commit + push in GitHub Desktop. Live in ~30 seconds.
5. The script prints each live doc's full link — copy it from there to share.

## To add a new document
Add a row to `"docs"` in the manifest:
```json
{
  "id": "short-slug-no-spaces",
  "title": "Human Title",
  "subtitle": "One line under the title (optional)",
  "source_path": "~/Desktop/CLAUDIUS/Work/Juno-Google-RFP/_methodology/Your-Doc.md",
  "live": false,
  "audience_note": "Who this is for + any gate before it goes live.",
  "added": "2026-07-06"
}
```
Supported source types: `.md` / `.txt` (rendered inline), `.docx` (rendered
inline via pandoc), `.pptx` / `.xlsx` / `.pdf` (offered as a download card).

## Confidentiality — standing rules
- Default audience is **internal-Juno** (David / Sapir / Nick). Any Google-visible
  use is a separate per-doc decision, flagged to David first.
- **Never publish:** the SOW / budget / rate, Google-internal materials,
  meeting transcripts or recordings, the trackers, partner-intel with
  named-candidate scoring, anything marked confidential, anything citing
  unresolved Claims/Gap items.
- Publishable class: Jonathan-authored, for-client-register,
  citation-guard-cleared documents only.

## Privacy mechanics
- Every page is `noindex` (meta tag + `_headers` `X-Robots-Tag` on `/share/*`)
  and `Disallow`-ed in `robots.txt`. Never added to `sitemap.xml`.
- `/share/index.html` is a neutral "incomplete link" stub — the bare directory
  reveals nothing.
- The only way in is the exact secret link.

## Internal dashboard link
The generator also writes `_command/butterfly-share-status.js` next to the
Butterfly Send Queue dashboard — a per-doc live/off status sidecar the dashboard
can load to light up its "public candidate" chips. (Wiring the chips to it is a
small follow-on; the sidecar is ready.)
