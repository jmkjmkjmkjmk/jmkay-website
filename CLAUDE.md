# Memory

## ⚠️ DEPLOY SAFETY — read before touching any site file
There are TWO directories on this computer that look like the jmkay.com website. **Only one deploys.**
- **`~/Documents/GitHub/jmkay-website/`** — THIS repo. The real deploy clone, watched by GitHub Desktop. Push → Netlify (`jmkaydotcom`) auto-deploys in ~30 sec. **Always edit here.**
- `~/Desktop/CLAUDIUS/JMKay/Website/` — staging/working copy with a DIVERGENT orphan git history. **Never push from there** — it would blow away real launch commits (nearly happened Apr 22 2026).

Before committing: `git fetch origin && git log origin/main` to see real remote state. If GitHub Desktop refuses to commit ("lock file already exists"), the fix is to clear all three locks from a Terminal: `rm .git/index.lock .git/HEAD.lock .git/objects/maintenance.lock` then commit.

**Brand single source of truth:** `~/Desktop/CLAUDIUS/JMKay/Brand/Docs/BRAND-SYSTEM.md`. When the brand notes below disagree with it or the live site, BRAND-SYSTEM.md / the live site win.

## Me
Jonathan Michael Kay. Independent Story Producer building a solo consulting practice as J. M. Kay. Base rate $150/hr. Coding beginner — build things for me, don't explain how.

## File Organization Rules
Always save files to logical subfolders — never dump loose files at the top level. Current folder structure:

| Folder | What goes here |
|--------|---------------|
| **JMKay launch/Content/** | Post drafts, editorial calendar, spotlight strategy, any written deliverables |
| **JMKay launch/Strategy/** | Prompt engine, project description, strategic planning docs |
| **JMKay launch/Tracker/** | Launch Command Center (.xlsx), any tracking/status tools |
| **JMKay launch/Resources/** | Source material — LinkedIn data export, Goodreads, Authory portfolio |
| **JMKay launch/Site Files/** | Staging area for website files before they go into the repo |
| **GitHub/jmkay-website/** | Live site repo (deployed via Netlify). Connect with `~/Documents/GitHub` |

When creating new files: pick the right subfolder. If none fits, create a new named subfolder rather than saving at root.

## Website Infrastructure (jmkay.com)
| Item | Detail |
|------|--------|
| Hosting | Netlify (site name: `jmkaydotcom`) |
| Repo | `~/Documents/GitHub/jmkay-website` (GitHub → Netlify auto-deploys) |
| Domain registrar | Squarespace (DNS only — not hosting) |
| Deploy workflow | Edit files locally → commit in GitHub Desktop → push → live in ~30 seconds |
| GA4 Measurement ID | `G-6XM6RT038M` (present on every HTML page — count grows as essays/sections are added) |
| Google Search Console | Verified via DNS/CNAME. Sitemap submitted. Update `sitemap.xml` lastmod on any page change. |
| Perspectives section | `writing.html` index + `writing/` folder for essay pages |
| Nav order | Work, Perspectives, Services, About, Contact |
| CSS font stack | Kay Display (wordmark), Instrument Serif (headlines), DM Sans (body), Space Mono (labels) |
| Warm White | `--warm-white` #FDFBF7 (site background). #F5F0E8 is Cream (secondary ground). |

**Published Perspectives pages (keep current):**
- Post 01 "The Work Had a Name" → `writing/jmkay.html` (Mar 12)
- Post 02 "A Cancer Pioneer Whose Life Was Tragically Cut Short" → `writing/baselga-documentary.html` (Apr 6)
- Post 03 "Properly Excavate, Before Building Anything" → `writing/excavating-a-life.html` (Apr 22/23)
- Post 04 "On briefing, in any era." → `writing/briefing-in-any-era.html` (May 26; slug `briefing-in-any-era`)
- Post 05 "What Nearly Two Decades in Healthcare Taught Me About Story" → `writing/two-decades-healthcare-story.html` (Jun 11; slug `two-decades-healthcare-story`)
- Cinema page → `cinema/index.html` (Bethesda Cinematheque, unlisted/noindex)
- Private reading share → `reading/<slug>/index.html` (select chapters of the novel *The Approved Version*, unlisted/noindex; one per-group secret link; Netlify-Forms comment box `reading-feedback`; build via `scripts/build_reading_pages.py`, see `scripts/READING_PAGES_README.md`; `/reading/` in robots.txt + _headers; NOT in nav/sitemap. Staged 2026-06-29 — live on push.)
- Groundwork / Juno partnership pack → `future/` (hub + `future/board|plan|sell-in/`, unlisted/noindex; `Disallow: /future/` sits INSIDE the User-agent group in robots.txt and a `/future/*` block in `_headers` carries noindex, noarchive, `Cache-Control: private, no-store`; NOT in nav/sitemap; **no password — unlisted is not private**, and the sell-in cockpit is JK-private content living there by explicit instruction. Do NOT hand-edit these pages: rebuild with `Collab with Juno/01_Opportunity-Universe/_bench/publish_to_site.py`, which regenerates all four and re-runs the pack's refusals. The board is regenerated daily — re-publish after any rebuild. Staged 2026-08-27 — live on push.)

(There are also the AAS + Aradhana case-study pages. Page count is no longer "6" — verify against the live sitemap, not this note.)

## Brand
**Single source of truth: `~/Desktop/CLAUDIUS/JMKay/Brand/Docs/BRAND-SYSTEM.md`** (and the live site CSS). Read it for any brand-adjacent change; the values below are a quick index and the SSOT wins on any conflict. Current era is **KayDisplay v4** + the **D2.1** subtitle treatment (the old v2 / Josefin / O-ring specs are retired).

| Term | Meaning |
|------|---------|
| Terracotta | #C2603F — primary brand color |
| Warm White | `--warm-white` #FDFBF7 — site background ground |
| Cream | #F5F0E8 — secondary ground |
| Ink | #1C1917 — body text |
| Teal | #1A4A4A — accent |
| The dots | Structural, not decorative — brand principle |
| Wordmark font | **KayDisplay v4** (custom CFF OpenType, 58 glyphs; surgical K/Y/Q/R correction over v3, locked Apr 21 2026). Site-local `KayDisplay-Regular.otf` is a copy of v4 — keep md5-matched to `Brand/Font/KayDisplay-v4.otf`. |
| Subtitle | "STORY PRODUCER" — **Space Mono 400, 13px, letter-spacing 0.28em, color `--ink`**. The O is replaced by a filled terracotta diamond (**D2.1**: 6.2×6.2px, rotate 45°, border-radius 1.35px; locked May 26 2026). |
| Hero separator dot | CSS square, 14×14px, terracotta, rotate 45° (nav scale 5×5px). Not an SVG ring. |
| Wordmark | J.M.KAY only (dots + letters). LinkedIn assets, banners, nav. |
| Lockup | J.M.KAY + STORY PRODUCER combined unit. Hero, formal applications. |
| Full-name rule | "Jonathan Michael Kay" is STATIC ONLY — never animated. Only abbreviated J.M.Kay gets sting. |

(Retired: KayDisplay v2, Josefin Sans subtitle, O-rings, the Mar/Apr 8 dot-geometry locks, and the "Still OPEN (Apr 8)" list — all superseded by the v3→v4 migration. See BRAND-SYSTEM.md for the full current spec + lock history.)

## Key People
| Who | Role |
|-----|------|
| **Nick Szpara** | FDMlife production partner |
| **Chris Valentino** | Director, Baselga documentary |
| **Eleanor Duff** | Previous manager at AstraZeneca |
| **Khadija Bhuiyan** | Production, Baselga project |

## Active Projects
| Name | What |
|------|------|
| **LinkedIn Activation** | 27-post calendar. Cadence: alternating 1-week / 2-week gaps. Posts 01–05 published; Phase-2 reshape May 26 2026 re-dated Posts 05–27 (Jun 2026 → Jan 2027). Post 05 LIVE Jun 11; Post 06 next (scheduled Wed Jun 17 — verify live). |
| **jmkay.com Perspectives** | Essay pages synced from published posts. Live: Posts 01–05 (see Published Perspectives list above). Deployed via Netlify from this repo. |
| **Spotlight the Process** | "Made With" collaborator credits at the bottom of case-study pages (not a testimonials page). |
| **FDMlife** | Production partnership with Nick Szpara |
| **Aradhana Award** | First client project under J.M.Kay (~$19–21K budget; Jonathan billed ~$5K+, ~25%+). |

## Voice Rules
Warm but not soft. Confident but not boastful. Precise but not cold. Short sentences that land, then breathe. The restraint IS the statement.

### Non-Negotiable Rules (locked after Post 02 iteration)
1. **Own the leadership.** "I led a team that produced..." is stronger than "We produced..."
2. **No straw-man comparisons.** Never write "most people would..." to make Jonathan look better by contrast. Show what he does, not what others don't.
3. **No exclamation points.** Ever.
4. **No marketing clichés.** Banned: "excited," "leverage," "pivot," "synergy," "passionate," "thrilled," "game-changer," "deep dive," "journey."
5. **Minimize em dashes.** Max 2 per post. Heavy em dash usage reads as AI-generated. Use commas, semicolons, periods, or restructure.
6. **Humanize institutions.** AstraZeneca isn't a faceless corporation; it's a group of people who cared about a colleague.
7. **Define technical terms.** LinkedIn audiences are general. "Precision oncology" needs a plain-language gloss in the same sentence.
8. **Name collaborators.** Credit directors, editors, partners by first and last name. It's generous and builds goodwill.
9. **Center the people.** Families, colleagues, subjects of the stories. Human stakes are always the lead, not production logistics.
10. **Be precise about production realities.** Don't say "we filmed in three countries" if the pandemic meant virtual interviews and archival footage.
11. **Fact-check all specific claims.** Drug approvals, award credits, institutional roles — verify before including. If uncertain, soften or flag.
12. **Soft CTAs only.** Never "the full case study is on my site." Instead: "Hear more about how we worked across..." or "Here's how the story developed..."
13. **Semicolons for rhythm.** Can replace periods when two thoughts are closely linked. Paragraphs beginning with "And" are fine for emotional beats. Closing should connect back to Story Producer positioning without repeating it verbatim.
14. **No "LinkedIn twat."** LinkedIn includes Jonathan's personal contacts (old classmates, doc subjects, family friends) who clock anything performative. Disqualifying: "thrilled to share," "humbled to announce," "X lessons I learned," declaratory thesis sentences, process-flex, hashtag parades, "thinking partner," "journey," "reply below" CTAs, humble-brags. Sound like someone talking to a professionally-curious friend.
15. **Two-lane copy.** jmkay.com Perspectives = professional-facing, confident, methodology-forward. LinkedIn = softer, more elliptical, cut the declaration. Shared: title, covers, themes, date, hero imagery. May differ: subhead, body voice, length. (Full rule in the master CLAUDIUS CLAUDE.md.)

## Preferences
- Word (.docx) for all text deliverables — no .md files for final outputs
- Microsoft suite preferred (Excel, Planner)
- Don't explain code — just build it
- Files in logical subfolders, never loose at top level
