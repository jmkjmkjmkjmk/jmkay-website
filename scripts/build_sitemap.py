#!/usr/bin/env python3
"""
build_sitemap.py -- jmkay.com sitemap.xml, derived, never typed.

The sitemap is not a list somebody maintains. It is a view over three things
that already exist in this repo:

  1. git       -- which HTML files are tracked, and when each last changed
  2. robots.txt -- which paths are Disallowed
  3. _headers   -- which paths carry an X-Robots-Tag noindex

plus a fourth signal read from each page itself: a <meta name="robots" ...>
containing noindex.

A page is listed ONLY if all four say it may be. Any one of them saying no is
final. That is why the sitemap cannot drift out of step with robots.txt again:
the exclusion list is not copied here, it is read from the file that owns it.

lastmod is the date of the file's last commit, per page. Never a bulk stamp.

Usage
    python3 scripts/build_sitemap.py            # show the diff, write nothing
    python3 scripts/build_sitemap.py --write    # write sitemap.xml
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import date

BASE = "https://jmkay.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Always out, whatever the signals say.
HARD_EXCLUDE = {"404.html"}

# changefreq / priority by path. First matching prefix wins; last entry is the
# default. These are hints to crawlers, not facts, so typing them is fine.
RULES = [
    ("index.html",   "monthly", "1.0"),
    ("writing.html", "weekly",  "0.9"),
    ("standard/",    "yearly",  "0.9"),
    ("writing/",     "monthly", "0.8"),
    ("museums/",     "monthly", "0.7"),
    ("culture/",     "weekly",  "0.7"),
    ("",             "monthly", "0.8"),   # default, incl. the case studies
]


def run(*args):
    return subprocess.run(
        args, cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def tracked_html():
    out = run("git", "ls-files", "*.html")
    return sorted(p for p in out.splitlines() if p.strip())


def robots_disallowed():
    """Disallow prefixes from robots.txt, read from the User-agent: * group."""
    path = os.path.join(ROOT, "robots.txt")
    if not os.path.exists(path):
        return []
    rules, in_group = [], False
    for raw in open(path, encoding="utf-8"):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "user-agent":
            in_group = val == "*"
        elif key == "disallow" and in_group and val and val != "/":
            rules.append(val)
    return rules


def headers_noindex():
    """Path patterns in _headers whose block carries a noindex X-Robots-Tag."""
    path = os.path.join(ROOT, "_headers")
    if not os.path.exists(path):
        return []
    blocked, current = [], None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            current = line.strip()
        elif current and "noindex" in line.lower():
            blocked.append(current)
            current = None
    return blocked


def pattern_hits(url_path, pattern):
    """/kit/* and /kit/ both cover /kit/index.html; /juno.html is exact."""
    p = pattern.rstrip("*")
    return url_path == pattern or url_path.startswith(p)


def page_noindex(rel):
    """A <meta name="robots"> on the page itself saying noindex."""
    try:
        head = open(os.path.join(ROOT, rel), encoding="utf-8",
                    errors="replace").read(8000)
    except OSError:
        return False
    for tag in re.findall(r"<meta\b[^>]*>", head, re.I):
        if re.search(r'name\s*=\s*["\']?robots', tag, re.I) \
           and "noindex" in tag.lower():
            return True
    return False


def url_for(rel):
    """index.html becomes the directory URL; everything else keeps its name."""
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def lastmod(rel):
    out = run("git", "log", "-1", "--format=%cs", "--", rel).strip()
    return out or date.today().isoformat()


def rule_for(rel):
    for prefix, freq, prio in RULES:
        if prefix and rel.startswith(prefix):
            return freq, prio
        if prefix == rel or prefix == "":
            return freq, prio
    return "monthly", "0.5"


def collect():
    disallow = robots_disallowed()
    noindex_hdr = headers_noindex()
    kept, dropped = [], []

    for rel in tracked_html():
        url_path = url_for(rel)
        why = None
        if rel in HARD_EXCLUDE:
            why = "hard-excluded"
        else:
            for d in disallow:
                if pattern_hits(url_path, d):
                    why = f"robots.txt Disallow: {d}"
                    break
            if not why:
                for h in noindex_hdr:
                    if pattern_hits(url_path, h):
                        why = f"_headers noindex: {h}"
                        break
            if not why and page_noindex(rel):
                why = "page meta robots noindex"

        if why:
            dropped.append((rel, why))
        else:
            freq, prio = rule_for(rel)
            kept.append({
                "loc": BASE + url_path,
                "lastmod": lastmod(rel),
                "changefreq": freq,
                "priority": prio,
                "rel": rel,
            })

    # Homepage first, then by descending priority, then by URL.
    kept.sort(key=lambda e: (e["loc"] != BASE + "/",
                             -float(e["priority"]), e["loc"]))
    return kept, dropped


def render(entries):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for e in entries:
        out += ["  <url>",
                f"    <loc>{e['loc']}</loc>",
                f"    <lastmod>{e['lastmod']}</lastmod>",
                f"    <changefreq>{e['changefreq']}</changefreq>",
                f"    <priority>{e['priority']}</priority>",
                "  </url>"]
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def current_locs():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        return []
    return re.findall(r"<loc>([^<]+)</loc>",
                      open(path, encoding="utf-8").read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="write sitemap.xml (default: dry run)")
    args = ap.parse_args()

    kept, dropped = collect()
    if not kept:
        print("REFUSED: no pages survived the filters. Not writing.")
        return 1

    before, after = set(current_locs()), {e["loc"] for e in kept}
    added, removed = sorted(after - before), sorted(before - after)

    print(f"{len(kept)} pages in, {len(dropped)} excluded.\n")
    for e in kept:
        mark = "+" if e["loc"] in added else " "
        print(f" {mark} {e['lastmod']}  {e['priority']}  {e['loc']}")
    if removed:
        print("\nDropping (was in sitemap.xml, excluded now):")
        for loc in removed:
            print(f"   - {loc}")
    print("\nExcluded, and why:")
    for rel, why in dropped:
        print(f"   {rel:<50} {why}")

    xml = render(kept)
    if args.write:
        with open(os.path.join(ROOT, "sitemap.xml"), "w",
                  encoding="utf-8") as fh:
            fh.write(xml)
        print(f"\nWrote sitemap.xml -- {len(kept)} URLs, "
              f"{len(added)} added, {len(removed)} removed.")
    else:
        print("\nDry run. Nothing written. Add --write to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
