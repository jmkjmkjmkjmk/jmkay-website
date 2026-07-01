# Private reading pages — how to use

Unlisted pages that share select chapters of *The Approved Version*. Readers are
organized into **groups**; each group has its own secret link showing only the
chapters chosen for it. Hand a group's link to anyone you want in that group.
Not indexed by Google, not in the site nav or sitemap.

## Current groups
- **Group 1 — A taste**: Prologue + Production Week
- **Group 2 — The sampler**: Prologue + Production Week + Sunday + India
- **Group 3 — The deeper cut**: + Bugis + Chinese New Year

## To add a group or change a group's chapters
1. Open `scripts/build_reading_pages.py`.
2. Find the `ROSTER` block near the top. Each entry is one group, e.g.:
   ```
   "Group 4 — Close readers": {"slug": "tav-close-x7q2m9", "chapters": ["prologue", "ch01", "sunday", "india", "cny"]},
   ```
   - `slug` is the secret folder in the link. Make it random and hard to guess
     (any unique string works; leave it `""` and the script invents one).
   - `chapters` picks from the pool: `prologue`, `ch01` (Production Week),
     `bugis`, `sunday`, `india`, `cny` (Chinese New Year). To offer more, add a
     row to the `CHAPTERS` block (file, heading number, title, book-order index).
   - The group label is internal only — it tags feedback so you know which set a
     response came from. Readers never see it.
3. In Terminal: `cd ~/Documents/GitHub/jmkay-website && python3 scripts/build_reading_pages.py`
   (needs `pip3 install markdown` once.)
4. Commit + push in GitHub Desktop. Live in ~30 seconds.
5. The script prints each group's full link — copy it from there to share.

## Note: two stale sample folders
`reading/tav-9k2m4xq7/` and `reading/tav-3p8w1ztc/` were early samples, now
neutralized (they show only an "incomplete link" message). Safe to delete the two
folders in Finder whenever — they don't affect anything.

## Where reader feedback goes
The comment box uses Netlify Forms. After the first deploy, go to your Netlify
dashboard → **Forms** → `reading-feedback` to read submissions. Turn on
**form notifications** there to get an email each time someone responds. Every
submission is tagged with the reader's name so you know who it's from.

## Privacy
- Pages are `noindex` (meta tag + `_headers` rule) and `Disallow`-ed in `robots.txt`.
- Not linked anywhere on the site and not in `sitemap.xml`.
- Each page only contains that reader's chapters — even view-source shows nothing
  about the others.
- The only way in is the exact secret link. Treat the links like passwords.
