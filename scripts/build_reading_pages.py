#!/usr/bin/env python3
"""
Build per-reader unlisted reading pages for The Approved Version.

Each reader in ROSTER gets their own self-contained HTML page at
  reading/<slug>/index.html
containing ONLY the chapters chosen for them, a warm reader-facing
framing, and a simple Netlify-Forms comment box tagged with their name.

To add or change a reader: edit ROSTER, rerun this script, push the repo.

Run:  python3 build_reading_pages.py
"""

import os
import re
import secrets
import shutil
from pathlib import Path

import markdown

# Reading sample omits in-chapter images (e.g. the Ch1 tweet graphic) so readers
# get a clean prose experience. Flip to True to render them as figures instead.
INCLUDE_IMAGES = False
IMAGES_TO_COPY = set()

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
# The chapter pool — key -> (file prefix, display heading, book-order index)
# Only chapters listed here can be assigned to a reader.
#
# VERSION-AGNOSTIC since 2026-07-01: the CURRENT canonical version of each
# chapter is derived at build time from concatenate_v2.py's CHAPTERS_V2 list
# (the manuscript's single source of truth), matched by file prefix. Rerun
# this script + push after any chapter-version-roll that touches these
# chapters — but never hand-edit a version number here again.
# ---------------------------------------------------------------------------
CHAPTER_PREFIXES = {
    "prologue": ("00_Frame_Prologue_Doha",   "Prologue",  "Doha, 2019", 0),
    "ch01":     ("Ch01_Production_Week",     "One",       "Production Week", 1),
    "bugis":    ("Ch07_Bugis",               "Five",      "Bugis", 6),
    "sunday":   ("Ch08_Sunday",              "Six",       "Sunday", 7),
    "india":    ("Ch13_India",               "Ten",       "India", 12),
    "cny":      ("Ch14_Chinese_New_Year",    "Eleven",    "Chinese New Year", 13),
}

def _canonical_files():
    """Read the canonical chapter filenames out of concatenate_v2.py."""
    src = (V2_DIR.parent / "_build" / "concatenate_v2.py").read_text(encoding="utf-8")
    return re.findall(r"'([A-Za-z0-9_]+_v\d+\.md)'", src)

def _resolve_chapters():
    canon = _canonical_files()
    resolved = {}
    for key, (prefix, num, title, order) in CHAPTER_PREFIXES.items():
        matches = [f for f in canon if f.startswith(prefix + "_v")]
        if len(matches) != 1:
            raise SystemExit(
                f"ERROR: expected exactly one canonical file for prefix '{prefix}', "
                f"found {matches!r} in concatenate_v2.py — fix the prefix or the build list."
            )
        resolved[key] = (matches[0], num, title, order)
    return resolved

CHAPTERS = _resolve_chapters()

# ---------------------------------------------------------------------------
# The roster — one entry per GROUP. Each group gets its own secret link
# (slug = the folder under /reading/) and its own set of chapters. Hand a
# group's link to anyone you want in that group. The label is internal only
# (it tags their feedback so you know which set they read) — readers never
# see it. slug: leave as "" to auto-generate one.
# ---------------------------------------------------------------------------
ROSTER = {
    "Group 1 — A taste": {
        "slug": "tav-taste-9k2m4xq7",
        "chapters": ["prologue", "ch01"],
    },
    "Group 2 — The sampler": {
        "slug": "tav-sampler-3p8w1ztc",
        "chapters": ["prologue", "ch01", "sunday", "india"],
    },
    "Group 3 — The deeper cut": {
        "slug": "tav-deeper-6r4n8vbd",
        "chapters": ["prologue", "ch01", "bugis", "sunday", "india", "cny"],
    },
}

# ===========================================================================
BOOK_TITLE = "The Approved Version"

READER_FRAMING = """\
<p>Thank you for reading some of this. It is a novel I have been working on for a
while, called <em>The Approved Version</em>.</p>

<p>It follows Daniel Reiss, an American who arrives in Singapore in 2012 on a work
contract he keeps meaning to leave, and the three years he ends up staying. His job is
a kind of translation, for companies. He sits in the room where something real gets
said, then he hands back the approved version that&rsquo;s safe to say out loud. The
book is about what a life like that does to a person, and about the one relationship he
could never find the words for, and lost.</p>

<p>What you have here is a sample, not the whole book: a few chapters, enough to get
a feel for the voice and what it is doing. They run in the book&rsquo;s order, so
there are gaps between them. That is normal for a sample.</p>

<p>If anything lands, or doesn&rsquo;t, I would love to hear it. There is a box at the
end &mdash; say as much or as little as you like. There are no wrong reactions.</p>

<p style="text-align:right;">&mdash; Jonathan</p>
"""

# ---------------------------------------------------------------------------
def load_chapter_html(filename):
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
        # render as a centered figure; rewrite to a web asset path + queue copy
        def _img(m):
            alt, src = m.group(1), m.group(2)
            fname = Path(src).name
            IMAGES_TO_COPY.add(fname)
            return f'\n\n<figure class="ms-figure"><img src="/reading/_assets/{fname}" alt="{alt}"></figure>\n\n'
        raw = re.sub(r"!\[([^\]]*)\]\(([^)]+?)\)(?:\{[^}]*\})?", _img, raw)
    else:
        # strip in-chapter images entirely (incl. any pandoc {..} attribute)
        raw = re.sub(r"!\[[^\]]*\]\([^)]+?\)(?:\{[^}]*\})?\s*", "", raw)

    raw = raw.strip()
    html = markdown.markdown(raw, extensions=["smarty"])
    return html


def chapter_block(key):
    filename, num, title, _ = CHAPTERS[key]
    body = load_chapter_html(filename)
    return f"""
  <section class="chapter">
    <header class="chapter-head">
      <span class="chapter-num">{num}</span>
      <h2 class="chapter-title">{title}</h2>
    </header>
    <div class="prose">
      {body}
    </div>
  </section>"""


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>{book} &mdash; a reading</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&family=Space+Mono:wght@400&display=swap" rel="stylesheet">
<style>
  @font-face {{
    font-family: 'Kay Display';
    src: url('/KayDisplay-Regular.otf') format('opentype');
    font-weight: 400; font-style: normal;
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

  /* slim top bar — wordmark only, deliberately quiet */
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

  .wrap {{ max-width:680px; margin:0 auto; padding:0 28px; }}

  /* book title / framing */
  .intro {{ padding:84px 0 8px; }}
  .eyebrow {{
    font-family:'Space Mono',monospace; font-size:12px; letter-spacing:0.22em;
    text-transform:uppercase; color:var(--terracotta); margin-bottom:18px;
  }}
  .book-title {{
    font-family:'Instrument Serif',serif; font-size:48px; line-height:1.05;
    font-weight:400; letter-spacing:-0.01em; margin-bottom:10px;
  }}
  .byline {{
    font-family:'Space Mono',monospace; font-size:12.5px; letter-spacing:0.16em;
    text-transform:uppercase; color:var(--ink-muted); margin-bottom:40px;
  }}
  .framing {{
    border-top:1px solid var(--line); border-bottom:1px solid var(--line);
    padding:32px 0; margin-bottom:8px;
  }}
  .framing p {{
    font-size:16.5px; color:var(--ink-light); margin-bottom:16px;
  }}
  .framing p:last-child {{ margin-bottom:0; }}
  .framing em {{ font-style:italic; }}

  /* chapters */
  .chapter {{ padding:64px 0 8px; }}
  .chapter-head {{ text-align:center; margin-bottom:44px; }}
  .chapter-num {{
    display:block; font-family:'Space Mono',monospace; font-size:12px;
    letter-spacing:0.28em; text-transform:uppercase; color:var(--terracotta);
    margin-bottom:12px;
  }}
  .chapter-title {{
    font-family:'Instrument Serif',serif; font-weight:400; font-size:34px;
    line-height:1.1; letter-spacing:-0.01em;
  }}
  .prose {{
    font-family:'EB Garamond',serif; font-size:20px; line-height:1.66;
    color:#26211d;
  }}
  .prose p {{ margin-bottom:1.05em; }}
  .prose p:first-of-type {{ text-indent:0; }}
  .prose p + p {{ text-indent:1.4em; }}
  .prose em {{ font-style:italic; }}
  .prose hr {{
    border:none; text-align:center; margin:34px 0; overflow:visible;
  }}
  .prose hr::before {{
    content:'\\002A \\00A0\\00A0 \\002A \\00A0\\00A0 \\002A';
    color:var(--stone); letter-spacing:0.1em; font-family:'EB Garamond',serif;
    font-size:17px;
  }}
  .prose figure.ms-figure {{ margin:6px 0 30px; }}
  .prose figure.ms-figure img {{
    width:100%; height:auto; display:block; border-radius:4px;
    box-shadow:0 6px 22px rgba(28,25,23,0.10);
  }}

  /* feedback */
  .feedback {{
    margin:72px 0 0; padding:40px 0 0; border-top:1px solid var(--line);
  }}
  .feedback h3 {{
    font-family:'Instrument Serif',serif; font-weight:400; font-size:26px;
    margin-bottom:8px;
  }}
  .feedback .lead {{ color:var(--ink-light); margin-bottom:24px; font-size:16px; }}
  .field {{ margin-bottom:18px; }}
  .field label {{
    display:block; font-family:'Space Mono',monospace; font-size:11px;
    letter-spacing:0.14em; text-transform:uppercase; color:var(--ink-muted);
    margin-bottom:7px;
  }}
  .field input, .field textarea {{
    width:100%; font-family:'DM Sans',sans-serif; font-size:16px; color:var(--ink);
    background:var(--warm-white); border:1px solid var(--sand); border-radius:4px;
    padding:12px 14px; line-height:1.5;
  }}
  .field textarea {{ min-height:150px; resize:vertical; }}
  .field input:focus, .field textarea:focus {{
    outline:none; border-color:var(--terracotta);
  }}
  .hp {{ position:absolute; left:-9999px; }}
  button.send {{
    font-family:'DM Sans',sans-serif; font-size:15px; font-weight:500;
    color:#fff; background:var(--deep-teal); border:none; border-radius:4px;
    padding:13px 30px; cursor:pointer; letter-spacing:0.01em;
  }}
  button.send:hover {{ background:var(--terracotta); }}
  .thanks {{ display:none; color:var(--deep-teal); font-size:16.5px; padding:8px 0; }}

  footer {{
    margin-top:80px; padding:34px 0 60px; border-top:1px solid var(--line);
    text-align:center; color:var(--ink-muted); font-size:13px;
    font-family:'Space Mono',monospace; letter-spacing:0.06em;
  }}

  @media (max-width:640px) {{
    .book-title {{ font-size:36px; }}
    .prose {{ font-size:18.5px; }}
    .chapter-title {{ font-size:28px; }}
    .intro {{ padding:60px 0 8px; }}
  }}
</style>
</head>
<body>

<div class="topbar">
  <a class="wordmark" href="https://jmkay.com">J<span class="dot"></span>M<span class="dot"></span>KAY</a>
</div>

<div class="wrap">

  <div class="intro">
    <div class="eyebrow">A reading &middot; in confidence</div>
    <h1 class="book-title">{book}</h1>
    <div class="byline">a novel &middot; Jonathan Michael Kay</div>
    <div class="framing">
      {framing}
    </div>
  </div>

  {chapters}

  <div class="feedback">
    <h3>Tell me what you think</h3>
    <p class="lead">Anything at all &mdash; a line that stuck, a place you drifted, a feeling. No need to be tidy about it.</p>
    <form name="reading-feedback" method="POST" data-netlify="true" netlify-honeypot="bot-field" id="fbform">
      <input type="hidden" name="form-name" value="reading-feedback">
      <input type="hidden" name="reader" value="{reader}">
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

<script>
  var f = document.getElementById('fbform');
  f.addEventListener('submit', function(e){{
    e.preventDefault();
    var data = new URLSearchParams(new FormData(f)).toString();
    fetch('/', {{method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}}, body:data}})
      .then(function(){{
        f.querySelector('button.send').style.display='none';
        document.getElementById('thoughts').closest('.field').style.display='none';
        document.getElementById('who').closest('.field').style.display='none';
        document.getElementById('thanks').style.display='block';
      }})
      .catch(function(){{ document.getElementById('thanks').textContent='Hmm, that did not send — you can also just email me.'; document.getElementById('thanks').style.display='block'; }});
  }});
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


def main():
    READING_DIR.mkdir(parents=True, exist_ok=True)
    (READING_DIR / "index.html").write_text(ROOT_STUB, encoding="utf-8")

    built = []
    for reader, cfg in ROSTER.items():
        slug = cfg.get("slug") or ("tav-" + secrets.token_hex(5))
        keys = sorted(cfg["chapters"], key=lambda k: CHAPTERS[k][3])  # book order
        chapters_html = "\n".join(chapter_block(k) for k in keys)
        page = PAGE_TEMPLATE.format(
            book=BOOK_TITLE,
            framing=READER_FRAMING,
            chapters=chapters_html,
            reader=reader.replace('"', "'"),
        )
        out = READING_DIR / slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(page, encoding="utf-8")
        built.append((reader, f"https://jmkay.com/reading/{slug}/", keys))

    # copy any referenced chapter images into the web asset folder
    if IMAGES_TO_COPY:
        ASSET_DIR.mkdir(parents=True, exist_ok=True)
        for fn in sorted(IMAGES_TO_COPY):
            for cand in (V2_DIR / fn, BUILD_DIR / fn):
                if cand.exists():
                    shutil.copy(cand, ASSET_DIR / fn)
                    break

    print(f"Built {len(built)} reading page(s) into {READING_DIR}\n")
    for reader, url, keys in built:
        titles = ", ".join(CHAPTERS[k][2] for k in keys)
        print(f"  {reader}")
        print(f"    {url}")
        print(f"    chapters: {titles}\n")


if __name__ == "__main__":
    main()
