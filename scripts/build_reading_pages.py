#!/usr/bin/env python3
"""
Build per-group unlisted reading pages for The Approved Version.

RELIFT 2026-08-26 (Handover_Reading_Guides_Relift_2026-08-26.md): the pages are
now reading GUIDES, not chapter dumps —
  Lane A: sticky contents + progress bar + continue-where-you-left-off +
          type size / light-dark controls + chapter interstitials.
  Lane B: rewritten framing letter (per-tier), factual gap notes between
          non-adjacent chapters, a closing what-happens-next note.
  Lane C: per-chapter tap reactions (leaned in / drifted + optional line),
          a reader-initiated "where I got to" send, the end box rewritten
          around the fresh-eyes questions. Everything posts to the same
          Netlify form (reading-feedback), tagged with group + chapter.
          NO passive tracking of any kind — every signal is reader-initiated.
  Also:   chapter display numbers + titles now AUTO-DERIVE from
          concatenate_v2.py's CHAPTERS_V2 tuples (the V2->V3 numbering drift
          class is closed for good), the Ch1 tweets graphic is restored as a
          figure, and each group gets a build-side EPUB.

Each group in ROSTER gets its own self-contained HTML page at
  reading/<slug>/index.html
plus an EPUB of the same sample at
  reading/<slug>/the-approved-version-sample.epub

The pages are BUILT ARTIFACTS — never hand-edit them; edit this script and
rerun. To add or change a group: edit ROSTER, rerun, push the repo.
Existing slugs are immutable (links are in the wild).

Run:  python3 build_reading_pages.py
"""

import os
import re
import secrets
import shutil
import uuid
import zipfile
from pathlib import Path

import markdown

# Ch1's tweets graphic is a designed beat — restored as a figure 2026-08-26
# (relift gate 3). Flip False to strip in-chapter images again.
INCLUDE_IMAGES = True
IMAGES_TO_COPY = set()

WPM = 220  # reading-time estimate

# ---------------------------------------------------------------------------
# Paths (work in both sandbox + Mac topologies)
# ---------------------------------------------------------------------------
def _first_existing(*candidates):
    import glob as _glob
    for c in candidates:
        hits = sorted(_glob.glob(c)) if any(ch in c for ch in "*?[") else ([c] if Path(c).exists() else [])
        if hits:
            return Path(hits[0])
    return Path(candidates[-1])

V2_DIR = _first_existing(
    os.path.expanduser("~/Desktop/CLAUDIUS/CASA FORTUNA/08_DRAFTS/v2"),
    "/sessions/*/mnt/CLAUDIUS/CASA FORTUNA/08_DRAFTS/v2",
    "/sessions/*/mnt/CASA FORTUNA/08_DRAFTS/v2",
)
SITE_DIR = _first_existing(
    os.path.expanduser("~/Documents/GitHub/jmkay-website"),
    "/sessions/*/mnt/jmkay-website",
)
READING_DIR = SITE_DIR / "reading"
ASSET_DIR = READING_DIR / "_assets"
BUILD_DIR = V2_DIR.parent / "_build"   # where chapter image assets (e.g. ch1_tweets.png) live

# ---------------------------------------------------------------------------
# The chapter pool — key -> file prefix. That is ALL that is hand-carried now.
#
# Display number, display title, and book-order position are derived at build
# time from concatenate_v2.py's CHAPTERS_V2 tuples (display_name, title,
# filename) — the manuscript's single source of truth. The 2026-08-26 drift
# (V2-era "Six/Seven/Twelve/Thirteen" surviving the V3 renumber) came from
# hand-carried display strings; nothing here carries them anymore.
# ---------------------------------------------------------------------------
CHAPTER_PREFIXES = {
    "prologue": "00_Frame_Prologue_Doha",
    "ch01":     "Ch01_Production_Week",
    "bugis":    "Ch07_Bugis",
    "sunday":   "Ch08_Sunday",
    "india":    "Ch13_India",
    "cny":      "Ch14_Chinese_New_Year",
}

def _canonical_rows():
    """Read the canonical (display_name, title, filename) rows out of
    concatenate_v2.py's CHAPTERS_V2 list, in book order."""
    src = (BUILD_DIR / "concatenate_v2.py").read_text(encoding="utf-8")
    m = re.search(r"CHAPTERS_V2\s*=\s*\[(.*?)\n\]", src, flags=re.DOTALL)
    if not m:
        raise SystemExit("ERROR: could not locate CHAPTERS_V2 in concatenate_v2.py")
    body = m.group(1)
    # drop comment-only lines so retired rows in comments can never match
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    rows = re.findall(
        r"\(\s*(None|'[^']*')\s*,\s*'([^']+)'\s*,\s*'([A-Za-z0-9_]+_v\d+\.md)'\s*[\),]",
        body,
    )
    out = []
    for disp, title, fname in rows:
        disp = None if disp == "None" else disp.strip("'")
        out.append((disp, title, fname))
    if len(out) < 10:
        raise SystemExit(f"ERROR: only parsed {len(out)} CHAPTERS_V2 rows — regex drift, fix before building.")
    return out

def _resolve_chapters():
    rows = _canonical_rows()
    resolved = {}
    for key, prefix in CHAPTER_PREFIXES.items():
        matches = [(i, d, t, f) for i, (d, t, f) in enumerate(rows) if f.startswith(prefix + "_v")]
        if len(matches) != 1:
            raise SystemExit(
                f"ERROR: expected exactly one canonical row for prefix '{prefix}', "
                f"found {[m[3] for m in matches]!r} in concatenate_v2.py."
            )
        i, disp, title, fname = matches[0]
        resolved[key] = {"order": i, "num": disp or "", "title": title, "file": fname}
    return resolved

CHAPTERS = _resolve_chapters()

# ---------------------------------------------------------------------------
# Gap notes — factual, two sentences max, no synopsis-voice. Keyed by the
# (previous_key, next_key) pair as they will sit on the page. The build WARNS
# if a non-adjacent pair has no note, so roster changes can't silently skip.
# On-page identifiers only (real-names lock applies to every visible word).
# ---------------------------------------------------------------------------
GAP_NOTES = {
    ("ch01", "bugis"):
        "Between these two chapters the book goes back two years, to Daniel&rsquo;s "
        "first months in Singapore. Three chapters are not included here; this one "
        "picks up how he and Arjun met.",
    ("ch01", "sunday"):
        "Between these two chapters the book goes back two years, to Daniel&rsquo;s "
        "arrival in Singapore and the start of things with Arjun. Four chapters are "
        "not included here; this one is a Sunday from the middle of those years.",
    ("sunday", "india"):
        "A stretch of the book sits between these two, covering the back half "
        "of 2014. This one is December: Chennai, a family wedding, Daniel as "
        "not-quite-a-plus-one.",
}

# ---------------------------------------------------------------------------
# The roster — one entry per GROUP. Each group gets its own secret link
# (slug = the folder under /reading/) and its own set of chapters. Hand a
# group's link to anyone you want in that group. The label is internal only
# (it tags their feedback so you know which set they read) — readers never
# see it. slug: leave as "" to auto-generate one. SLUGS ARE IMMUTABLE once
# a link has been sent.
# ---------------------------------------------------------------------------
ROSTER = {
    "Group 1 — A taste": {
        "slug": "tav-taste-9k2m4xq7",
        "chapters": ["prologue", "ch01"],
        "holding": (
            "What you have here is the opening of the book, the prologue and the "
            "first chapter &mdash; about {time} of reading."
        ),
    },
    "Group 2 — The sampler": {
        "slug": "tav-sampler-3p8w1ztc",
        "chapters": ["prologue", "ch01", "sunday", "india"],
        "holding": (
            "What you have here is a sample: the opening of the book plus two "
            "chapters from the middle years, about {time} of reading in all. The "
            "chapters run in the book&rsquo;s order, and where some are skipped a "
            "short note says what the gap holds."
        ),
    },
    "Group 3 — The deeper cut": {
        "slug": "tav-deeper-6r4n8vbd",
        "chapters": ["prologue", "ch01", "bugis", "sunday", "india", "cny"],
        "holding": (
            "What you have here is the longer sample: the opening of the book plus "
            "four chapters from across the three years, about {time} of reading in "
            "all. The chapters run in the book&rsquo;s order, and where some are "
            "skipped a short note says what the gap holds."
        ),
    },
}

# ===========================================================================
BOOK_TITLE = "The Approved Version"
EPUB_NAME = "the-approved-version-sample.epub"

# The framing letter — Jonathan's signed voice, close-friend plain register.
# {holding} is the per-group paragraph above; {time} inside it is computed.
READER_FRAMING = """\
<p>Thank you for reading some of this. The book is a novel called
<em>The Approved Version</em>.</p>

<p>It follows Daniel Reiss, an American who moves to Singapore in 2012 for a
two-year job and stays three. His work is making things safe to say: he sits in
the room where the real thing gets said, then hands back the version that can go
out. While he is there, a television crew films his life, and the version they
air is missing someone. The book is about the years that version covers, and the
person it leaves out.</p>

<p>{holding}</p>

<p>Read it however you like, in one sitting or five &mdash; the page remembers
where you stopped. If you want to tell me something along the way, each chapter
has a small row at the end for it, and there is a box at the very end for
anything bigger. You can also just text me.</p>

<p style="text-align:right;">&mdash; Jonathan</p>
"""

CLOSING_NOTE = """\
<p>That is the end of this sample. There is a whole book on the other side of
it; if you want the rest, say so below and I will send it.</p>
"""

# ---------------------------------------------------------------------------
def load_chapter(filename):
    """Return (html, word_count) for a canonical chapter file."""
    raw = (V2_DIR / filename).read_text(encoding="utf-8")
    # strip leading YAML frontmatter
    if raw.startswith("---"):
        m = re.match(r"^---\n.*?\n---\n", raw, flags=re.DOTALL)
        if m:
            raw = raw[m.end():]
    # cut draft notes (and anything after)
    raw = re.split(r"\n#{1,6}\s*Draft notes", raw, maxsplit=1)[0]
    # remove the file's own leading H1 title line (we supply our own heading)
    raw = re.sub(r"^\s*#\s+.*?\n", "", raw, count=1)

    # images
    if INCLUDE_IMAGES:
        def _img(m):
            alt, src = m.group(1), m.group(2)
            fname = Path(src).name
            IMAGES_TO_COPY.add(fname)
            return f'\n\n<figure class="ms-figure"><img src="/reading/_assets/{fname}" alt="{alt}" /></figure>\n\n'
        raw = re.sub(r"!\[([^\]]*)\]\(([^)]+?)\)(?:\{[^}]*\})?", _img, raw)
    else:
        raw = re.sub(r"!\[[^\]]*\]\([^)]+?\)(?:\{[^}]*\})?\s*", "", raw)

    raw = raw.strip()
    words = len(re.findall(r"\S+", re.sub(r"<[^>]+>", " ", raw)))
    html = markdown.markdown(raw, extensions=["smarty"])
    return html, words


def nice_time(words):
    mins = max(1, round(words / WPM))
    if mins < 60:
        m = max(5, 5 * round(mins / 5))
        return f"{m} minutes"
    halves = round(mins / 30) / 2
    if halves == int(halves):
        h = int(halves)
        return f"{h} hour" + ("s" if h != 1 else "")
    whole = int(halves)
    if whole == 0:
        return "45 minutes"
    return f"{whole}½ hours"


def chapter_section(key, meta, body_html, first):
    num = meta["num"]
    title = meta["title"]
    num_html = f'<span class="chapter-num">{num}</span>' if num else ""
    divider = "" if first else '<div class="divider" aria-hidden="true"><span class="dmark"></span></div>'
    return f"""
  {divider}
  <section class="chapter" id="ch-{key}" data-title="{title}">
    <header class="chapter-head">
      {num_html}
      <h2 class="chapter-title">{title}</h2>
    </header>
    <div class="prose">
      {body_html}
    </div>
    <div class="cr" data-chapter="{title}" hidden>
      <div class="cr-row">
        <span class="cr-q">This chapter &middot;</span>
        <button type="button" class="cr-btn" data-r="leaned in">I leaned in</button>
        <button type="button" class="cr-btn" data-r="drifted">I drifted</button>
      </div>
      <div class="cr-more" hidden>
        <input class="cr-line" type="text" maxlength="500" placeholder="a line about it, if you like (optional)">
        <button type="button" class="cr-send">Send</button>
      </div>
      <p class="cr-done" hidden></p>
    </div>
  </section>"""


def gap_note_html(text):
    return f"""
  <aside class="gap-note">
    <p>{text}</p>
  </aside>"""


def toc_item(key, meta, time_label):
    num = f'<span class="toc-num">{meta["num"]}</span>' if meta["num"] else '<span class="toc-num"></span>'
    return (f'<button type="button" class="toc-item" data-target="ch-{key}">'
            f'{num}<span class="toc-title">{meta["title"]}</span>'
            f'<span class="toc-time">~{time_label}</span></button>')


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>@@BOOK@@ &mdash; a reading</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&family=Space+Mono:wght@400&display=swap" rel="stylesheet">
<style>
  @font-face {
    font-family: 'Kay Display';
    src: url('/KayDisplay-Regular.otf') format('opentype');
    font-weight: 400; font-style: normal;
  }
  :root {
    --warm-white:#FDFBF7; --cream:#F5F0E8; --sand:#D4C5A9;
    --ink:#1C1917; --ink-light:#44403C; --ink-muted:#78716C; --stone:#A8A29E;
    --terracotta:#C2603F; --deep-teal:#1A4A4A; --line:#E4DDD0;
    --prose-ink:#26211d; --panel:#FFFFFF;
  }
  html[data-theme="dark"] {
    --warm-white:#191613; --cream:#211D18; --sand:#4A4238;
    --ink:#EAE3D8; --ink-light:#C9C1B2; --ink-muted:#948C7E; --stone:#6E6659;
    --line:#332E27; --prose-ink:#DFD8CB; --panel:#211D18;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body {
    font-family:'DM Sans',sans-serif; background:var(--warm-white); color:var(--ink);
    font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased;
    transition:background 0.25s ease, color 0.25s ease;
  }
  button { font-family:inherit; }

  /* reading progress */
  .progress { position:fixed; top:0; left:0; height:3px; width:0%;
    background:var(--terracotta); z-index:80; transition:width 0.1s linear; }

  /* sticky top bar */
  .topbar {
    position:sticky; top:0; z-index:70;
    padding:14px 18px; display:flex; align-items:center; justify-content:space-between;
    border-bottom:1px solid var(--line);
    background:color-mix(in srgb, var(--warm-white) 88%, transparent);
    -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px);
  }
  @supports not (background: color-mix(in srgb, red 50%, blue)) {
    .topbar { background:var(--warm-white); }
  }
  .wordmark {
    font-family:'Kay Display',serif; font-size:18px; text-transform:uppercase;
    letter-spacing:0.04em; color:var(--ink); text-decoration:none;
    position:absolute; left:50%; transform:translateX(-50%);
  }
  .dot {
    display:inline-block; width:5px; height:5px; background:var(--terracotta);
    transform:rotate(45deg); border-radius:1px; margin:0 4px; vertical-align:middle;
  }
  .tb-btn {
    font-family:'Space Mono',monospace; font-size:11px; letter-spacing:0.14em;
    text-transform:uppercase; color:var(--ink-muted); background:none;
    border:1px solid var(--line); border-radius:4px; padding:7px 12px; cursor:pointer;
  }
  .tb-btn:hover { color:var(--ink); border-color:var(--sand); }

  /* panels */
  .panel {
    display:none; position:fixed; top:58px; z-index:75;
    background:var(--panel); border:1px solid var(--line); border-radius:8px;
    box-shadow:0 12px 40px rgba(28,25,23,0.14); padding:14px;
    max-width:340px; width:calc(100% - 28px);
  }
  .panel.open { display:block; }
  #tocPanel { left:14px; }
  #typePanel { right:14px; }
  .panel-label {
    font-family:'Space Mono',monospace; font-size:10.5px; letter-spacing:0.18em;
    text-transform:uppercase; color:var(--ink-muted); margin:2px 4px 10px;
  }
  .toc-item {
    display:flex; align-items:baseline; gap:10px; width:100%; text-align:left;
    background:none; border:none; padding:9px 8px; border-radius:5px; cursor:pointer;
    color:var(--ink); font-size:15px;
  }
  .toc-item:hover { background:var(--cream); }
  .toc-item.current { background:var(--cream); }
  .toc-item.current .toc-title { color:var(--terracotta); }
  .toc-num {
    font-family:'Space Mono',monospace; font-size:10px; letter-spacing:0.12em;
    text-transform:uppercase; color:var(--ink-muted); min-width:46px;
  }
  .toc-title { font-family:'Instrument Serif',serif; font-size:17px; flex:1; }
  .toc-time { font-family:'Space Mono',monospace; font-size:10px; color:var(--stone); }
  .toc-foot { border-top:1px solid var(--line); margin-top:10px; padding-top:12px; }
  .spot-btn {
    width:100%; background:none; border:1px dashed var(--sand); border-radius:5px;
    padding:10px; cursor:pointer; color:var(--ink-light); font-size:13.5px;
  }
  .spot-btn:hover { border-color:var(--terracotta); color:var(--ink); }
  .spot-done { font-size:13px; color:var(--deep-teal); padding:8px 2px 2px; display:none; }
  html[data-theme="dark"] .spot-done { color:#7FB5B5; }

  .type-row { display:flex; align-items:center; justify-content:space-between;
    gap:10px; padding:6px 4px; }
  .type-row .t-label { font-size:13.5px; color:var(--ink-light); }
  .seg { display:flex; gap:6px; }
  .seg button {
    background:none; border:1px solid var(--line); border-radius:4px;
    padding:6px 12px; cursor:pointer; color:var(--ink); font-size:14px;
  }
  .seg button:hover { border-color:var(--sand); }
  .seg button.on { border-color:var(--terracotta); color:var(--terracotta); }

  .wrap { max-width:680px; margin:0 auto; padding:0 28px; }

  /* book title / framing */
  .intro { padding:72px 0 8px; }
  .eyebrow {
    font-family:'Space Mono',monospace; font-size:12px; letter-spacing:0.22em;
    text-transform:uppercase; color:var(--terracotta); margin-bottom:18px;
  }
  .book-title {
    font-family:'Instrument Serif',serif; font-size:48px; line-height:1.05;
    font-weight:400; letter-spacing:-0.01em; margin-bottom:10px;
  }
  .byline {
    font-family:'Space Mono',monospace; font-size:12.5px; letter-spacing:0.16em;
    text-transform:uppercase; color:var(--ink-muted); margin-bottom:40px;
  }
  .framing {
    border-top:1px solid var(--line); border-bottom:1px solid var(--line);
    padding:32px 0; margin-bottom:8px;
  }
  .framing p { font-size:16.5px; color:var(--ink-light); margin-bottom:16px; }
  .framing p:last-child { margin-bottom:0; }
  .framing em { font-style:italic; }
  .epub-line {
    font-size:13.5px; color:var(--ink-muted); padding:14px 2px 0; text-align:center;
  }
  .epub-line a { color:var(--deep-teal); }
  html[data-theme="dark"] .epub-line a { color:#7FB5B5; }

  /* chapters */
  .divider { text-align:center; padding:58px 0 0; }
  .dmark {
    display:inline-block; width:9px; height:9px; background:var(--terracotta);
    transform:rotate(45deg); border-radius:1.5px;
  }
  .chapter { padding:56px 0 8px; }
  .chapter-head { text-align:center; margin-bottom:44px; }
  .chapter-num {
    display:block; font-family:'Space Mono',monospace; font-size:12px;
    letter-spacing:0.28em; text-transform:uppercase; color:var(--terracotta);
    margin-bottom:12px;
  }
  .chapter-title {
    font-family:'Instrument Serif',serif; font-weight:400; font-size:34px;
    line-height:1.1; letter-spacing:-0.01em;
  }
  .prose {
    font-family:'EB Garamond',serif; font-size:20px; line-height:1.66;
    color:var(--prose-ink);
  }
  .prose p { margin-bottom:1.05em; }
  .prose p:first-of-type { text-indent:0; }
  .prose p + p { text-indent:1.4em; }
  .prose em { font-style:italic; }
  .prose hr { border:none; text-align:center; margin:34px 0; overflow:visible; }
  .prose hr::before {
    content:'\\002A \\00A0\\00A0 \\002A \\00A0\\00A0 \\002A';
    color:var(--stone); letter-spacing:0.1em; font-family:'EB Garamond',serif;
    font-size:17px;
  }
  .prose figure.ms-figure { margin:6px 0 30px; }
  .prose figure.ms-figure img {
    width:100%; height:auto; display:block; border-radius:4px;
    box-shadow:0 6px 22px rgba(28,25,23,0.10);
  }
  html[data-theme="dark"] .prose figure.ms-figure img {
    box-shadow:0 6px 22px rgba(0,0,0,0.4);
  }

  /* gap notes */
  .gap-note { padding:58px 0 0; text-align:center; }
  .gap-note p {
    display:inline-block; max-width:460px; font-size:14px; font-style:italic;
    color:var(--ink-muted); line-height:1.55;
    border-top:1px solid var(--line); border-bottom:1px solid var(--line);
    padding:14px 6px;
  }

  /* per-chapter reactions */
  .cr { margin-top:44px; text-align:center; }
  .cr-row { display:flex; align-items:center; justify-content:center; gap:10px;
    flex-wrap:wrap; }
  .cr-q {
    font-family:'Space Mono',monospace; font-size:10.5px; letter-spacing:0.16em;
    text-transform:uppercase; color:var(--stone);
  }
  .cr-btn {
    background:none; border:1px solid var(--line); border-radius:16px;
    padding:7px 16px; cursor:pointer; color:var(--ink-light); font-size:13.5px;
  }
  .cr-btn:hover { border-color:var(--sand); color:var(--ink); }
  .cr-btn.on { border-color:var(--terracotta); color:var(--terracotta); }
  .cr-more { display:flex; gap:8px; justify-content:center; margin-top:12px;
    flex-wrap:wrap; }
  .cr-more[hidden] { display:none; }
  .cr-line {
    width:min(340px, 100%); font-family:'DM Sans',sans-serif; font-size:14px;
    color:var(--ink); background:var(--warm-white); border:1px solid var(--sand);
    border-radius:16px; padding:8px 14px;
  }
  .cr-line:focus { outline:none; border-color:var(--terracotta); }
  .cr-send {
    background:var(--deep-teal); color:#fff; border:none; border-radius:16px;
    padding:8px 18px; cursor:pointer; font-size:13.5px;
  }
  .cr-send:hover { background:var(--terracotta); }
  .cr-done { font-size:13.5px; color:var(--deep-teal); margin-top:10px; }
  html[data-theme="dark"] .cr-done { color:#7FB5B5; }

  /* closing + feedback */
  .closing { margin-top:72px; padding-top:32px; border-top:1px solid var(--line); }
  .closing p { font-size:16.5px; color:var(--ink-light); }
  .feedback { margin:40px 0 0; padding:40px 0 0; border-top:1px solid var(--line); }
  .feedback h3 {
    font-family:'Instrument Serif',serif; font-weight:400; font-size:26px;
    margin-bottom:8px;
  }
  .feedback .lead { color:var(--ink-light); margin-bottom:24px; font-size:16px; }
  .field { margin-bottom:18px; }
  .field label {
    display:block; font-family:'Space Mono',monospace; font-size:11px;
    letter-spacing:0.14em; text-transform:uppercase; color:var(--ink-muted);
    margin-bottom:7px;
  }
  .field input, .field textarea {
    width:100%; font-family:'DM Sans',sans-serif; font-size:16px; color:var(--ink);
    background:var(--warm-white); border:1px solid var(--sand); border-radius:4px;
    padding:12px 14px; line-height:1.5;
  }
  .field textarea { min-height:150px; resize:vertical; }
  .field input:focus, .field textarea:focus { outline:none; border-color:var(--terracotta); }
  .hp { position:absolute; left:-9999px; }
  button.send {
    font-family:'DM Sans',sans-serif; font-size:15px; font-weight:500;
    color:#fff; background:var(--deep-teal); border:none; border-radius:4px;
    padding:13px 30px; cursor:pointer; letter-spacing:0.01em;
  }
  button.send:hover { background:var(--terracotta); }
  .thanks { display:none; color:var(--deep-teal); font-size:16.5px; padding:8px 0; }
  html[data-theme="dark"] .thanks { color:#7FB5B5; }

  /* continue pill */
  .pill {
    display:none; position:fixed; bottom:26px; left:50%; transform:translateX(-50%);
    z-index:65; background:var(--ink); color:var(--warm-white);
    border:none; border-radius:22px; padding:11px 22px; cursor:pointer;
    font-size:14px; box-shadow:0 8px 28px rgba(28,25,23,0.25);
  }
  .pill.show { display:block; }
  html[data-theme="dark"] .pill { background:var(--cream); color:var(--ink); }

  footer {
    margin-top:80px; padding:34px 0 60px; border-top:1px solid var(--line);
    text-align:center; color:var(--ink-muted); font-size:13px;
    font-family:'Space Mono',monospace; letter-spacing:0.06em;
  }

  @media (max-width:640px) {
    .book-title { font-size:36px; }
    .prose { font-size:18.5px; }
    .chapter-title { font-size:28px; }
    .intro { padding:56px 0 8px; }
    .tb-btn { padding:6px 9px; font-size:10px; }
  }
</style>
</head>
<body>

<div class="progress" id="progress" aria-hidden="true"></div>

<div class="topbar">
  <button type="button" class="tb-btn" id="tocBtn" aria-expanded="false">Contents</button>
  <a class="wordmark" href="https://jmkay.com">J<span class="dot"></span>M<span class="dot"></span>KAY</a>
  <button type="button" class="tb-btn" id="typeBtn" aria-expanded="false">Aa</button>
</div>

<div class="panel" id="tocPanel" role="menu">
  <div class="panel-label">Contents</div>
  @@TOC_ITEMS@@
  <div class="toc-foot">
    <button type="button" class="spot-btn" id="spotBtn">Stopping for now? Tap to let Jonathan know where you got to.</button>
    <p class="spot-done" id="spotDone">Sent &mdash; thank you for reading this far.</p>
  </div>
</div>

<div class="panel" id="typePanel">
  <div class="panel-label">Reading settings</div>
  <div class="type-row">
    <span class="t-label">Text size</span>
    <span class="seg"><button type="button" id="sizeDown" aria-label="Smaller text">&minus;</button><button type="button" id="sizeUp" aria-label="Larger text">+</button></span>
  </div>
  <div class="type-row">
    <span class="t-label">Theme</span>
    <span class="seg"><button type="button" id="themeLight">Light</button><button type="button" id="themeDark">Dark</button></span>
  </div>
</div>

<div class="wrap">

  <div class="intro" id="top">
    <div class="eyebrow">A reading &middot; in confidence</div>
    <h1 class="book-title">@@BOOK@@</h1>
    <div class="byline">a novel &middot; Jonathan Michael Kay</div>
    <div class="framing">
      @@FRAMING@@
    </div>
    <p class="epub-line">Prefer an e-reader? <a href="@@EPUB@@" download>Download this sample as an EPUB</a>.</p>
  </div>

  @@CHAPTERS@@

  <div class="closing">
    @@CLOSING@@
  </div>

  <div class="feedback">
    <h3>Tell me what you think</h3>
    <p class="lead">Where did you lean in, where did you drift, and how did the
    last chapter sit with you? Say as much or as little as you like &mdash;
    nothing is too small, and no need to be tidy about it.</p>
    <form name="reading-feedback" method="POST" data-netlify="true" netlify-honeypot="bot-field" id="fbform">
      <input type="hidden" name="form-name" value="reading-feedback">
      <input type="hidden" name="reader" value="@@READER@@">
      <input type="hidden" name="chapter" value="the end box">
      <input type="hidden" name="reaction" value="">
      <p class="hp"><label>Leave this empty <input name="bot-field"></label></p>
      <div class="field">
        <label for="thoughts">Your thoughts</label>
        <textarea id="thoughts" name="thoughts" required></textarea>
      </div>
      <div class="field">
        <label for="who">Your name (optional)</label>
        <input id="who" name="who" type="text">
      </div>
      <button class="send" type="submit">Send to Jonathan</button>
      <p class="thanks" id="thanks">Thank you &mdash; that came through. It means a lot that you read it.</p>
    </form>
  </div>

  <footer>The Approved Version &middot; shared privately &middot; please don&rsquo;t forward</footer>

</div>

<button type="button" class="pill" id="pill">Continue where you left off &darr;</button>

<script>
(function () {
  var SLUG = '@@SLUG@@';
  var READER = '@@READER@@';

  function store(k, v) { try { localStorage.setItem('tav:' + SLUG + ':' + k, v); } catch (e) {} }
  function read(k) { try { return localStorage.getItem('tav:' + SLUG + ':' + k); } catch (e) { return null; } }

  function post(fields) {
    fields['form-name'] = 'reading-feedback';
    fields['reader'] = READER;
    var data = new URLSearchParams(fields).toString();
    return fetch('/', { method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: data });
  }

  /* ---- theme + text size ---- */
  var sizes = [17, 18.5, 20, 21.5, 23];
  var sizeIdx = parseInt(read('size') || '2', 10);
  if (isNaN(sizeIdx) || sizeIdx < 0 || sizeIdx > 4) sizeIdx = 2;
  function applySize() {
    document.querySelectorAll('.prose').forEach(function (p) {
      p.style.fontSize = sizes[sizeIdx] + 'px';
    });
  }
  document.getElementById('sizeDown').addEventListener('click', function () {
    if (sizeIdx > 0) { sizeIdx--; applySize(); store('size', sizeIdx); }
  });
  document.getElementById('sizeUp').addEventListener('click', function () {
    if (sizeIdx < sizes.length - 1) { sizeIdx++; applySize(); store('size', sizeIdx); }
  });
  if (sizeIdx !== 2) applySize();

  var themeL = document.getElementById('themeLight');
  var themeD = document.getElementById('themeDark');
  function applyTheme(t) {
    if (t === 'dark') { document.documentElement.setAttribute('data-theme', 'dark'); }
    else { document.documentElement.removeAttribute('data-theme'); }
    themeD.classList.toggle('on', t === 'dark');
    themeL.classList.toggle('on', t !== 'dark');
  }
  themeL.addEventListener('click', function () { applyTheme('light'); store('theme', 'light'); });
  themeD.addEventListener('click', function () { applyTheme('dark'); store('theme', 'dark'); });
  applyTheme(read('theme') === 'dark' ? 'dark' : 'light');

  /* ---- panels ---- */
  var tocBtn = document.getElementById('tocBtn'), tocPanel = document.getElementById('tocPanel');
  var typeBtn = document.getElementById('typeBtn'), typePanel = document.getElementById('typePanel');
  function closePanels() {
    tocPanel.classList.remove('open'); typePanel.classList.remove('open');
    tocBtn.setAttribute('aria-expanded', 'false'); typeBtn.setAttribute('aria-expanded', 'false');
  }
  tocBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    var open = tocPanel.classList.contains('open');
    closePanels();
    if (!open) { tocPanel.classList.add('open'); tocBtn.setAttribute('aria-expanded', 'true'); }
  });
  typeBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    var open = typePanel.classList.contains('open');
    closePanels();
    if (!open) { typePanel.classList.add('open'); typeBtn.setAttribute('aria-expanded', 'true'); }
  });
  document.addEventListener('click', function (e) {
    if (!tocPanel.contains(e.target) && !typePanel.contains(e.target)) closePanels();
  });

  /* ---- chapters / TOC position ---- */
  var chapters = Array.prototype.slice.call(document.querySelectorAll('.chapter'));
  var tocItems = Array.prototype.slice.call(document.querySelectorAll('.toc-item'));
  tocItems.forEach(function (b) {
    b.addEventListener('click', function () {
      var t = document.getElementById(b.getAttribute('data-target'));
      closePanels();
      if (t) t.scrollIntoView({ behavior: 'smooth' });
    });
  });
  function currentChapter() {
    var y = window.scrollY + 140, cur = null;
    chapters.forEach(function (c) { if (c.offsetTop <= y) cur = c; });
    return cur;
  }
  function markCurrent() {
    var cur = currentChapter();
    tocItems.forEach(function (b) {
      b.classList.toggle('current', !!cur && b.getAttribute('data-target') === cur.id);
    });
  }

  /* ---- progress + position memory ---- */
  var bar = document.getElementById('progress');
  var saveTimer = null;
  function onScroll() {
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var pct = max > 0 ? Math.min(1, window.scrollY / max) : 0;
    bar.style.width = (pct * 100) + '%';
    markCurrent();
    if (saveTimer) return;
    saveTimer = setTimeout(function () {
      saveTimer = null;
      if (window.scrollY > 300) { store('pos', String(window.scrollY)); store('pct', String(Math.round(pct * 100))); }
    }, 800);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var pill = document.getElementById('pill');
  var savedPos = parseInt(read('pos') || '0', 10);
  var savedPct = parseInt(read('pct') || '0', 10);
  if (savedPos > 900 && savedPct < 97 && window.scrollY < 300) {
    pill.classList.add('show');
    pill.addEventListener('click', function () {
      pill.classList.remove('show');
      window.scrollTo({ top: savedPos, behavior: 'smooth' });
    });
    setTimeout(function () { pill.classList.remove('show'); }, 12000);
    window.addEventListener('scroll', function hidePill() {
      if (window.scrollY > 600) { pill.classList.remove('show'); window.removeEventListener('scroll', hidePill); }
    }, { passive: true });
  }

  /* ---- per-chapter reactions (reader-initiated only) ---- */
  document.querySelectorAll('.cr').forEach(function (cr) {
    cr.removeAttribute('hidden');
    var chapter = cr.getAttribute('data-chapter');
    var done = cr.querySelector('.cr-done');
    var more = cr.querySelector('.cr-more');
    var line = cr.querySelector('.cr-line');
    var prior = read('r:' + chapter);
    if (prior) {
      cr.querySelector('.cr-row').style.display = 'none';
      done.textContent = 'You said: ' + prior + '. Thank you.';
      done.removeAttribute('hidden');
      return;
    }
    var choice = null;
    cr.querySelectorAll('.cr-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        choice = b.getAttribute('data-r');
        cr.querySelectorAll('.cr-btn').forEach(function (x) { x.classList.toggle('on', x === b); });
        more.removeAttribute('hidden');
        line.focus();
      });
    });
    cr.querySelector('.cr-send').addEventListener('click', function () {
      if (!choice) return;
      post({ chapter: chapter, reaction: choice, thoughts: line.value || '' })
        .then(function () {
          store('r:' + chapter, choice);
          cr.querySelector('.cr-row').style.display = 'none';
          more.setAttribute('hidden', '');
          done.textContent = 'Noted — thank you.';
          done.removeAttribute('hidden');
        })
        .catch(function () {
          done.textContent = 'That did not send — the box at the end works too.';
          done.removeAttribute('hidden');
        });
    });
  });

  /* ---- "where I got to" (reader-initiated) ---- */
  var spotBtn = document.getElementById('spotBtn');
  spotBtn.addEventListener('click', function () {
    var cur = currentChapter();
    var pct = read('pct') || '0';
    post({
      chapter: cur ? cur.getAttribute('data-title') : 'the letter',
      reaction: 'stopped here',
      thoughts: 'Reader marked their spot: about ' + pct + '% down the page.'
    }).then(function () {
      spotBtn.style.display = 'none';
      document.getElementById('spotDone').style.display = 'block';
    }).catch(function () {
      spotBtn.textContent = 'That did not send — the box at the end works too.';
    });
  });

  /* ---- end box ---- */
  var f = document.getElementById('fbform');
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var data = new URLSearchParams(new FormData(f)).toString();
    fetch('/', { method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: data })
      .then(function () {
        f.querySelector('button.send').style.display = 'none';
        document.getElementById('thoughts').closest('.field').style.display = 'none';
        document.getElementById('who').closest('.field').style.display = 'none';
        document.getElementById('thanks').style.display = 'block';
      })
      .catch(function () {
        var t = document.getElementById('thanks');
        t.textContent = 'Hmm, that did not send — you can also just email me.';
        t.style.display = 'block';
      });
  });
})();
</script>

</body>
</html>
"""

ROOT_STUB = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Reading</title>
<style>body{font-family:Georgia,serif;background:#FDFBF7;color:#44403C;
display:flex;min-height:100vh;align-items:center;justify-content:center;
text-align:center;padding:40px;line-height:1.6}</style></head>
<body><div><p>This link looks incomplete.<br>Please use the full link you were sent,
or email Jonathan and he&rsquo;ll send a fresh one.</p></div></body></html>
"""

# ---------------------------------------------------------------------------
# EPUB
# ---------------------------------------------------------------------------
_ENTITY_MAP = {
    "&ldquo;": "“", "&rdquo;": "”", "&lsquo;": "‘",
    "&rsquo;": "’", "&mdash;": "—", "&ndash;": "–",
    "&hellip;": "…", "&nbsp;": " ", "&middot;": "·",
}

def _xhtml(s):
    for k, v in _ENTITY_MAP.items():
        s = s.replace(k, v)
    return s


def build_epub(out_path, group_label, pieces, framing_html):
    """pieces: list of dicts {id, num, title, html, gap_note(or None), image(or None)}"""
    css = """
body { font-family: serif; line-height: 1.6; }
h1 { font-weight: normal; font-size: 1.7em; text-align: center; margin: 1.4em 0 0.3em; }
.num { text-align: center; letter-spacing: 0.2em; text-transform: uppercase;
  font-size: 0.75em; color: #C2603F; margin-top: 2.5em; }
.gap { font-style: italic; font-size: 0.9em; color: #555; text-align: center;
  margin: 2em 8% 1em; }
p { margin: 0 0 0.9em; }
hr { border: none; text-align: center; margin: 1.6em 0; }
img { max-width: 100%; }
.framing { margin: 1.5em 0; }
.sig { text-align: right; }
"""
    uid = str(uuid.uuid5(uuid.NAMESPACE_URL, "jmkay.com/reading/" + out_path.parent.name))

    def xhtml_doc(title, body):
        return (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
            f'<head><title>{title}</title>'
            '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
            f'<body>{body}</body>\n</html>'
        )

    files = []  # (id, href, media-type, spine?)
    docs = {}

    letter_body = '<h1>A note from Jonathan</h1><div class="framing">' + _xhtml(framing_html) + "</div>"
    docs["letter.xhtml"] = xhtml_doc("A note from Jonathan", letter_body)
    files.append(("letter", "letter.xhtml", "application/xhtml+xml", True))

    images = set()
    for p in pieces:
        body = ""
        if p["gap_note"]:
            body += f'<p class="gap">{_xhtml(p["gap_note"])}</p>'
        if p["num"]:
            body += f'<p class="num">{p["num"]}</p>'
        body += f'<h1>{p["title"]}</h1>'
        html = _xhtml(p["html"])
        # EPUB-local image paths + XHTML self-closing tags
        html = html.replace('src="/reading/_assets/', 'src="images/')
        html = re.sub(r"<(hr|br|img)\b([^>]*?)\s*/?>", r"<\1\2/>", html)
        body += html
        href = p["id"] + ".xhtml"
        docs[href] = xhtml_doc(p["title"], body)
        files.append((p["id"], href, "application/xhtml+xml", True))
        if p["image"]:
            images.add(p["image"])

    nav_lis = '<li><a href="letter.xhtml">A note from Jonathan</a></li>' + "".join(
        f'<li><a href="{p["id"]}.xhtml">{p["title"]}</a></li>' for p in pieces
    )
    nav = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
        "<head><title>Contents</title></head>\n"
        '<body><nav epub:type="toc"><h1>Contents</h1><ol>' + nav_lis + "</ol></nav></body>\n</html>"
    )

    manifest_items = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                      '<item id="css" href="style.css" media-type="text/css"/>']
    spine_items = []
    for fid, href, mt, in_spine in files:
        manifest_items.append(f'<item id="{fid}" href="{href}" media-type="{mt}"/>')
        if in_spine:
            spine_items.append(f'<itemref idref="{fid}"/>')
    for i, img in enumerate(sorted(images)):
        ext = img.rsplit(".", 1)[-1].lower()
        mt = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "image/png")
        manifest_items.append(f'<item id="img{i}" href="images/{img}" media-type="{mt}"/>')

    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'<dc:identifier id="uid">urn:uuid:{uid}</dc:identifier>\n'
        f"<dc:title>{BOOK_TITLE} — a reading</dc:title>\n"
        "<dc:creator>Jonathan Michael Kay</dc:creator>\n"
        "<dc:language>en</dc:language>\n"
        '<meta property="dcterms:modified">2026-08-26T00:00:00Z</meta>\n'
        "</metadata>\n"
        "<manifest>" + "".join(manifest_items) + "</manifest>\n"
        '<spine>' + "".join(spine_items) + "</spine>\n"
        "</package>"
    )

    container = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>\n'
        "</container>"
    )

    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", css, compress_type=zipfile.ZIP_DEFLATED)
        for href, doc in docs.items():
            z.writestr("OEBPS/" + href, doc, compress_type=zipfile.ZIP_DEFLATED)
        for img in sorted(images):
            for cand in (V2_DIR / img, BUILD_DIR / img):
                if cand.exists():
                    z.write(cand, "OEBPS/images/" + img, compress_type=zipfile.ZIP_DEFLATED)
                    break


# ---------------------------------------------------------------------------
def main():
    READING_DIR.mkdir(parents=True, exist_ok=True)
    (READING_DIR / "index.html").write_text(ROOT_STUB, encoding="utf-8")

    # load every pooled chapter once
    loaded = {}
    for key, meta in CHAPTERS.items():
        html, words = load_chapter(meta["file"])
        loaded[key] = {"html": html, "words": words}

    built = []
    warnings = []
    for reader, cfg in ROSTER.items():
        slug = cfg.get("slug") or ("tav-" + secrets.token_hex(5))
        keys = sorted(cfg["chapters"], key=lambda k: CHAPTERS[k]["order"])
        total_words = sum(loaded[k]["words"] for k in keys)
        time_label = nice_time(total_words)

        # page body: gap notes between non-adjacent selections
        sections = []
        toc = []
        epub_pieces = []
        prev = None
        for i, k in enumerate(keys):
            meta = CHAPTERS[k]
            gap = None
            if prev is not None and meta["order"] - CHAPTERS[prev]["order"] > 1:
                gap = GAP_NOTES.get((prev, k))
                if gap is None:
                    warnings.append(
                        f"[{reader}] no gap note for non-adjacent pair ({prev} -> {k}) — add one to GAP_NOTES."
                    )
            if gap:
                sections.append(gap_note_html(gap))
            sections.append(chapter_section(k, meta, loaded[k]["html"], first=(i == 0)))
            toc.append(toc_item(k, meta, nice_time(loaded[k]["words"])))
            img = "ch1_tweets.png" if (k == "ch01" and INCLUDE_IMAGES) else None
            epub_pieces.append({
                "id": k, "num": meta["num"], "title": meta["title"],
                "html": loaded[k]["html"], "gap_note": gap, "image": img,
            })
            prev = k

        framing = READER_FRAMING.replace("{holding}", cfg["holding"].replace("{time}", time_label))

        page = (PAGE_TEMPLATE
                .replace("@@BOOK@@", BOOK_TITLE)
                .replace("@@FRAMING@@", framing)
                .replace("@@CLOSING@@", CLOSING_NOTE)
                .replace("@@CHAPTERS@@", "\n".join(sections))
                .replace("@@TOC_ITEMS@@", "\n  ".join(toc))
                .replace("@@READER@@", reader.replace('"', "'"))
                .replace("@@SLUG@@", slug)
                .replace("@@EPUB@@", EPUB_NAME))

        out = READING_DIR / slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(page, encoding="utf-8")
        build_epub(out / EPUB_NAME, reader, epub_pieces, framing)
        built.append((reader, f"https://jmkay.com/reading/{slug}/", keys, time_label))

    # copy any referenced chapter images into the web asset folder
    if IMAGES_TO_COPY:
        ASSET_DIR.mkdir(parents=True, exist_ok=True)
        for fn in sorted(IMAGES_TO_COPY):
            for cand in (V2_DIR / fn, BUILD_DIR / fn):
                if cand.exists():
                    shutil.copy(cand, ASSET_DIR / fn)
                    break
            else:
                warnings.append(f"image '{fn}' referenced but not found in v2/ or _build/")

    print(f"Built {len(built)} reading page(s) + EPUBs into {READING_DIR}\n")
    for reader, url, keys, time_label in built:
        titles = ", ".join(CHAPTERS[k]["title"] for k in keys)
        print(f"  {reader}  (~{time_label})")
        print(f"    {url}")
        print(f"    chapters: {titles}\n")
    for w in warnings:
        print(f"  WARNING: {w}")
    if warnings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
