# Memory

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
| GA4 Measurement ID | `G-6XM6RT038M` (in all 6 HTML pages) |
| Google Search Console | Verified via DNS/CNAME. Sitemap submitted. |
| Perspectives section | `writing.html` index + `writing/` folder for essay pages |
| Nav order | Work, Perspectives, Services, About, Contact |
| CSS font stack | Kay Display (wordmark), Instrument Serif (headlines), DM Sans (body), Space Mono (labels) |
| Warm White | #FDFBF7 (site background — note: slightly different from earlier brand docs) |

**Published Perspectives pages:**
- Post 01 "The Work Had a Name" → `writing/jmkay.html` (published Mar 12)
- Post 02 "A Cancer Pioneer Whose Life Was Tragically Cut Short" → `writing/baselga-documentary.html` (published Apr 6)

## Brand
| Term | Meaning |
|------|---------|
| Terracotta | #C2603F — primary brand color |
| Warm White | #F7F3EC — background (brand docs). Note: site CSS uses #FDFBF7 as `--warm-white`. |
| Ink | #1C1917 — body text |
| Teal | #1A4A4A — accent |
| The dots | Structural, not decorative — brand principle |
| Wordmark font | KayDisplay v2 (custom CFF OpenType). Upgraded from v1 Apr 8. Equalized diagonals, 48 GPOS kern pairs, soft diamond dots baked in. |
| J tail | Option B (+5 units left). Locked Mar 12. |
| Dot position | top: 22px, centered in 20px well (left: 5.5px). 9px diameter. Locked Mar 11. |
| Dot radius | r=4.0 (SVG units), with 0.6 stroke ring matching letter color. Font dots: soft diamond (r=44, corner=7 bezier). |
| K correction | KAY margin-left: −4px (optical fix for M/K side bearing asymmetry) |
| KAY kerning | Tightened ~14% (K +11, A +10, Y +9 net shift). |
| Subtitle | "STORY PRODUCER" — Josefin Sans 350, letter-spacing 0.22em, 72% opacity. O's in terracotta with ring. |
| Asset library | JMKay launch/Resources/JMKay-Asset-Library.xlsx — master file/status tracker. |
| Wordmark | J.M.KAY only (dots + letters). Used for LinkedIn assets, banners, nav. |
| Lockup | J.M.KAY + STORY PRODUCER combined unit. Used for hero, formal brand applications. |
| Asset files | JMKay launch/Resources/JMKay logo/ — filenames use `-wordmark-` or `-lockup-` to distinguish. |
| LinkedIn banners | Should use wordmark (not lockup). Can be abstracted/inspired rather than literal. |
| Full-name rule | "Jonathan Michael Kay" is STATIC ONLY — never animated. Only abbreviated J.M.Kay gets sting. |

### Still OPEN (as of Apr 8)
- Ghost Michael vs. Dots-Carry-It (static cold-open lockup)
- Sting v4 sign-off (typebar-cursor hybrid at 120%)
- Services & Rate Card confirmation
- STORY PRODUCER subtitle weight — currently 350 (same as wordmark). Consider 400–500 for more visual mass at small size, especially next to the fully opaque O rings. Compare side by side when ready.
- M inner diagonals (20–25u) — thinnest in the set, may need widening to match v2 equalization logic

### Locked (Mar 12)
- J tail: Option B (+5 units left)
- Dot outline: 0.6 stroke ring
- KAY kerning: tightened ~14%
- STORY/PRODUCER opacity: 0.72
- O rings: outer r=5.8, inner r=4.0, terracotta fill

### Locked (Apr 8)
- KayDisplay v2: equalized diagonal weights across K, A, Y, V, X, W, N
- Soft diamond dots baked into font (period, comma, exclam, question)
- 48 GPOS kern pairs (AV, AW, AY, AT, FA, KA, LT, LV, etc.)
- Font file: KayDisplay-Regular.otf (v2 replaces v1 in-place; original archived in CLAUDIUS/KayDisplay/)

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
| **LinkedIn Activation** | 27-post editorial calendar, Mar–Dec 2026. Weekly then biweekly. |
| **jmkay.com Perspectives** | Essay pages synced from published LinkedIn posts. 2 live (Post 01, Post 02). Deployed via Netlify from GitHub repo. |
| **Spotlight the Process** | Testimonial strand — collaborator quotes on methodology |
| **FDMlife** | Production partnership with Nick Szpara |
| **Aradhana Award** | First client project ($15K budget, 16% to J.M.Kay) |

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

## Preferences
- Word (.docx) for all text deliverables — no .md files for final outputs
- Microsoft suite preferred (Excel, Planner)
- Don't explain code — just build it
- Files in logical subfolders, never loose at top level
