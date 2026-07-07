#!/usr/bin/env python3
"""
Build the hidden-URL "share surface" on jmkay.com for select Butterfly
(Juno x Google) working documents.

Reads a manifest that lives WITH the project:
    Work/Juno-Google-RFP/_command/share_manifest.json
and renders a page per document under the deploy repo:
    share/<project_slug>/<doc-id>/index.html
plus a landing page listing whatever is currently live:
    share/<project_slug>/index.html

SAFETY MODEL (read this before touching anything):
  - ONLY docs with "live": true render a page. A live:false doc produces
    NO published HTML anywhere on disk — flipping it off truly removes it.
  - Toggling = edit the manifest ("live": true/false), rerun this script,
    commit, push. The manual edit + push is deliberate friction; that
    friction is a feature for confidential client work.
  - Every rendered page is noindex; /share/ is Disallow-ed in robots.txt
    and X-Robots-Tag: noindex in _headers; /share/ is never in the sitemap.
  - The surface carries NO Google branding, only a quiet "prepared by
    J.M.Kay for Juno Collective" line.

Also emits a status sidecar back into the project so the internal
Butterfly Send Queue dashboard can show live/off per doc:
    Work/Juno-Google-RFP/_command/butterfly-share-status.js

Run (Mac):  cd ~/Documents/GitHub/jmkay-website && python3 scripts/build_butterfly_share.py
Needs:  pip3 install markdown  (once) ; pandoc on PATH for .docx conversion.
"""

import html
import json
import os
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

import markdown

# ---------------------------------------------------------------------------
# Paths — resolve in both Mac and sandbox topologies.
# ---------------------------------------------------------------------------
def _first_existing(*candidates):
    import glob as _glob
    for c in candidates:
        hits = sorted(_glob.glob(c)) if any(ch in c for ch in "*?[") else (
            [c] if Path(c).exists() else [])
        if hits:
            return Path(hits[0])
    return Path(candidates[-1])

SITE_DIR = _first_existing(
    os.path.expanduser("~/Documents/GitHub/jmkay-website"),
    "/sessions/*/mnt/jmkay-website",
)
PROJECT_DIR = _first_existing(
    os.path.expanduser("~/Desktop/CLAUDIUS/Work/Juno-Google-RFP"),
    "/sessions/*/mnt/CLAUDIUS/Work/Juno-Google-RFP",
    "/sessions/*/mnt/Google Data Centers",
)
MANIFEST = PROJECT_DIR / "_command" / "share_manifest.json"
SIDECAR = PROJECT_DIR / "_command" / "butterfly-share-status.js"


def resolve_source(p: str) -> Path:
    """A manifest source_path may be written for the Mac. Fall back to the
    sandbox mount if the literal path isn't present."""
    p = os.path.expanduser(p)
    cand = Path(p)
    if cand.exists():
        return cand
    # Map ~/Desktop/CLAUDIUS/... to the mounted CLAUDIUS
    m = re.search(r"CLAUDIUS/(.*)$", p)
    if m:
        alt = _first_existing("/sessions/*/mnt/CLAUDIUS/" + m.group(1))
        if alt.exists():
            return alt
    return cand


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&family=Space+Mono:wght@400&display=swap" rel="stylesheet">
<style>
  @font-face {{
    font-family:'Kay Display';
    src:url('/KayDisplay-Regular.otf') format('opentype');
    font-weight:400; font-style:normal;
  }}
  :root {{
    --warm-white:#FDFBF7; --cream:#F5F0E8; --sand:#D4C5A9;
    --ink:#1C1917; --ink-light:#44403C; --ink-muted:#78716C; --stone:#A8A29E;
    --terracotta:#C2603F; --deep-teal:#1A4A4A; --line:#E4DDD0;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{
    font-family:'DM Sans',sans-serif; background:var(--warm-white); color:var(--ink);
    font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased;
  }}
  .topbar {{
    padding:22px 32px; display:flex; align-items:center; justify-content:center;
    border-bottom:1px solid var(--line);
  }}
  .wordmark {{
    font-family:'Kay Display',serif; font-size:19px; text-transform:uppercase;
    letter-spacing:0.04em; color:var(--ink); text-decoration:none;
  }}
  .dot {{
    display:inline-block; width:5px; height:5px; background:var(--terracotta);
    transform:rotate(45deg); border-radius:1px; margin:0 4px; vertical-align:middle;
  }}
  .wrap {{ max-width:720px; margin:0 auto; padding:0 28px; }}
  .intro {{ padding:72px 0 8px; }}
  .eyebrow {{
    font-family:'Space Mono',monospace; font-size:12px; letter-spacing:0.22em;
    text-transform:uppercase; color:var(--terracotta); margin-bottom:18px;
  }}
  .page-title {{
    font-family:'Instrument Serif',serif; font-size:44px; line-height:1.06;
    font-weight:400; letter-spacing:-0.01em; margin-bottom:10px;
  }}
  .page-sub {{
    font-size:17px; color:var(--ink-light); margin-bottom:30px; max-width:60ch;
  }}
  .divide {{ border-top:1px solid var(--line); margin:8px 0 40px; }}
  .doc-list {{ list-style:none; padding:0; margin:0; }}
  .doc-list li {{ border-bottom:1px solid var(--line); }}
  .doc-list a {{
    display:block; padding:22px 4px; text-decoration:none; color:var(--ink);
  }}
  .doc-list a:hover {{ background:var(--cream); }}
  .doc-list .dt {{
    font-family:'Instrument Serif',serif; font-size:24px; line-height:1.15;
    margin-bottom:4px;
  }}
  .doc-list .ds {{ font-size:14.5px; color:var(--ink-muted); }}
  .empty {{ color:var(--ink-muted); font-size:16.5px; padding:20px 0 8px; }}
  .prose {{
    font-family:'EB Garamond',serif; font-size:19.5px; line-height:1.66; color:#26211d;
    padding-top:6px;
  }}
  .prose h1 {{ font-family:'Instrument Serif',serif; font-weight:400; font-size:32px;
    line-height:1.15; margin:30px 0 12px; }}
  .prose h2 {{ font-family:'Instrument Serif',serif; font-weight:400; font-size:26px;
    line-height:1.2; margin:28px 0 10px; }}
  .prose h3 {{ font-family:'DM Sans',sans-serif; font-weight:500; font-size:17px;
    text-transform:uppercase; letter-spacing:0.08em; color:var(--ink-light);
    margin:24px 0 8px; }}
  .prose p {{ margin-bottom:1.0em; }}
  .prose ul, .prose ol {{ margin:0 0 1em 1.4em; }}
  .prose li {{ margin-bottom:0.4em; }}
  .prose blockquote {{
    border-left:3px solid var(--sand); padding:2px 0 2px 18px; margin:14px 0;
    color:var(--ink-light); font-style:italic;
  }}
  .prose table {{ width:100%; border-collapse:collapse; margin:16px 0; font-size:15px;
    font-family:'DM Sans',sans-serif; }}
  .prose th, .prose td {{ border:1px solid var(--line); padding:8px 10px; text-align:left;
    vertical-align:top; }}
  .prose th {{ background:var(--cream); font-weight:500; }}
  .prose code {{ font-family:'Space Mono',monospace; font-size:14px; background:var(--cream);
    padding:1px 5px; border-radius:3px; }}
  .prose pre {{ background:var(--cream); padding:14px 16px; border-radius:5px;
    overflow-x:auto; margin:14px 0; }}
  .prose pre code {{ background:none; padding:0; }}
  .prose hr {{ border:none; border-top:1px solid var(--line); margin:28px 0; }}
  .prose em {{ font-style:italic; }}
  .backlink {{ display:inline-block; margin:34px 0 0; font-family:'Space Mono',monospace;
    font-size:12.5px; letter-spacing:0.06em; color:var(--deep-teal); text-decoration:none; }}
  .backlink:hover {{ color:var(--terracotta); }}
  footer {{
    margin-top:70px; padding:30px 0 60px; border-top:1px solid var(--line);
    text-align:center; color:var(--ink-muted); font-size:12.5px;
    font-family:'Space Mono',monospace; letter-spacing:0.06em;
  }}
  @media (max-width:640px) {{
    .page-title {{ font-size:34px; }}
    .prose {{ font-size:18px; }}
  }}
</style>
</head>
<body>
<div class="topbar">
  <a class="wordmark" href="https://jmkay.com" target="_blank" rel="noopener">J<span class="dot"></span>M<span class="dot"></span>KAY</a>
</div>
<div class="wrap">
"""

FOOT = """
  <footer>{prepared_by} &middot; shared privately &middot; please don&rsquo;t forward</footer>
</div>
</body>
</html>
"""

# A neutral stub for /share/ itself and for the project landing when nothing
# is live — reveals nothing about what exists.
STUB = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>&nbsp;</title>
<style>body{font-family:Georgia,serif;background:#FDFBF7;color:#44403C;
display:flex;min-height:100vh;align-items:center;justify-content:center;
text-align:center;padding:40px;line-height:1.6}</style></head>
<body><div><p>This link looks incomplete.<br>Please use the full link you were sent,
or email Jonathan and he&rsquo;ll send a fresh one.</p></div></body></html>
"""


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def md_to_html(text: str) -> str:
    return markdown.markdown(
        text, extensions=["extra", "smarty", "sane_lists", "tables"])


def docx_to_html(src: Path) -> str:
    out = subprocess.run(
        ["pandoc", str(src), "-f", "docx", "-t", "html", "--wrap=none"],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"pandoc failed on {src.name}:\n{out.stderr}")
    return out.stdout


def render_doc_body(src: Path) -> str:
    ext = src.suffix.lower()
    if ext in (".md", ".markdown", ".txt"):
        return md_to_html(src.read_text(encoding="utf-8"))
    if ext == ".docx":
        return docx_to_html(src)
    return ""  # binary types handled by caller


def doc_page(doc, prepared_by, slug) -> str:
    title = html.escape(doc["title"])
    sub = html.escape(doc.get("subtitle", ""))
    src = resolve_source(doc["source_path"])
    ext = src.suffix.lower()

    parts = [HEAD.format(title=f"{title} — J.M.Kay")]
    parts.append('  <div class="intro">')
    parts.append('    <div class="eyebrow">Shared privately</div>')
    parts.append(f'    <h1 class="page-title">{title}</h1>')
    if sub:
        parts.append(f'    <p class="page-sub">{sub}</p>')
    parts.append('  </div>')
    parts.append('  <div class="divide"></div>')

    if ext in (".md", ".markdown", ".txt", ".docx"):
        parts.append(f'  <div class="prose">{render_doc_body(src)}</div>')
    else:
        # Binary (pptx/xlsx/pdf): copy the file in and offer a download card.
        fname = src.name.replace(" ", "_")
        parts.append(
            f'  <div class="prose"><p>This document is provided as a file '
            f'download.</p><p><a class="backlink" href="./{html.escape(fname)}" '
            f'download target="_blank" rel="noopener">Download &ldquo;{title}&rdquo; '
            f'&rarr;</a></p></div>')

    parts.append(f'  <a class="backlink" href="/share/{slug}/" '
                 f'target="_blank" rel="noopener">&larr; back to the list</a>')
    parts.append(FOOT.format(prepared_by=html.escape(prepared_by)))
    return "\n".join(parts)


def landing_page(manifest, live_docs) -> str:
    title = html.escape(manifest.get("landing_title", "Selected documents"))
    note = html.escape(manifest.get("landing_note", ""))
    prepared_by = manifest.get("prepared_by_line", "Prepared by J.M.Kay")
    slug = manifest["project_slug"]

    parts = [HEAD.format(title=f"{title} — J.M.Kay")]
    parts.append('  <div class="intro">')
    parts.append('    <div class="eyebrow">Shared privately &middot; in confidence</div>')
    parts.append(f'    <h1 class="page-title">{title}</h1>')
    if note:
        parts.append(f'    <p class="page-sub">{note}</p>')
    parts.append('  </div>')
    parts.append('  <div class="divide"></div>')

    if live_docs:
        parts.append('  <ul class="doc-list">')
        for d in live_docs:
            dt = html.escape(d["title"])
            ds = html.escape(d.get("subtitle", ""))
            parts.append(
                f'    <li><a href="/share/{slug}/{d["id"]}/" target="_blank" '
                f'rel="noopener"><div class="dt">{dt}</div>'
                + (f'<div class="ds">{ds}</div>' if ds else "")
                + '</a></li>')
        parts.append('  </ul>')
    else:
        parts.append('  <p class="empty">Nothing is currently shared here.</p>')

    parts.append(FOOT.format(prepared_by=html.escape(prepared_by)))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
def main():
    if not MANIFEST.exists():
        raise SystemExit(f"Manifest not found: {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    slug = manifest["project_slug"]
    prepared_by = manifest.get("prepared_by_line", "Prepared by J.M.Kay")

    share_root = SITE_DIR / "share"
    proj_dir = share_root / slug

    # Clean the project dir each build so a doc flipped live:false leaves no
    # orphan page behind. (Only this project's slug folder is touched.)
    # The Cowork sandbox mount is write-once and cannot delete — that's fine,
    # the real build runs Mac-side; warn and continue if deletion is blocked.
    if proj_dir.exists():
        try:
            shutil.rmtree(proj_dir)
        except OSError as e:
            print(f"  WARN: could not fully clear {proj_dir} ({e}). "
                  f"Stale pages may remain — rerun on the Mac to prune them.")
    proj_dir.mkdir(parents=True, exist_ok=True)

    # Neutral stub at /share/ so the bare directory reveals nothing.
    share_root.mkdir(parents=True, exist_ok=True)
    (share_root / "index.html").write_text(STUB, encoding="utf-8")

    live_docs = [d for d in manifest["docs"] if d.get("live") is True]

    for d in live_docs:
        src = resolve_source(d["source_path"])
        if not src.exists():
            raise SystemExit(
                f"live doc '{d['id']}' source missing: {d['source_path']}")
        doc_dir = proj_dir / d["id"]
        doc_dir.mkdir(parents=True, exist_ok=True)
        (doc_dir / "index.html").write_text(
            doc_page(d, prepared_by, slug), encoding="utf-8")
        # copy binary originals in for the download card
        if src.suffix.lower() not in (".md", ".markdown", ".txt", ".docx"):
            shutil.copy(src, doc_dir / src.name.replace(" ", "_"))

    # Landing page at the project slug.
    (proj_dir / "index.html").write_text(
        landing_page(manifest, live_docs), encoding="utf-8")

    # Status sidecar for the internal Send Queue dashboard (Pattern B).
    status = {
        "generated": str(date.today()),
        "project_slug": slug,
        "base_url": f"https://jmkay.com/share/{slug}/",
        "docs": [
            {
                "id": d["id"],
                "title": d["title"],
                "live": bool(d.get("live")),
                "url": (f"https://jmkay.com/share/{slug}/{d['id']}/"
                        if d.get("live") else None),
                "audience_note": d.get("audience_note", ""),
            }
            for d in manifest["docs"]
        ],
    }
    SIDECAR.write_text(
        "window.BUTTERFLY_SHARE_STATUS = "
        + json.dumps(status, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    # Report
    print(f"Built share surface at {proj_dir}")
    print(f"  Landing: https://jmkay.com/share/{slug}/")
    if live_docs:
        for d in live_docs:
            print(f"  LIVE  {d['id']:<24} https://jmkay.com/share/{slug}/{d['id']}/")
    else:
        print("  (no docs live — landing shows 'nothing currently shared')")
    off = [d for d in manifest["docs"] if not d.get("live")]
    for d in off:
        print(f"  off   {d['id']:<24} (no page rendered)")
    print(f"  Sidecar: {SIDECAR}")


if __name__ == "__main__":
    main()
