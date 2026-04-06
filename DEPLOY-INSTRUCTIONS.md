# jmkay.com — Deploy & Setup Guide

## How the site works

jmkay.com is a static site hosted on **Netlify** (site name: `neon-crostata-b5ef97`), deployed automatically from this GitHub repo. Domain registered through **Squarespace** (DNS only — Squarespace is not hosting anything).

**Deploy workflow:** Edit files locally → commit in GitHub Desktop → push → Netlify auto-deploys within ~30 seconds.


## File structure

```
jmkay-website/
├── index.html                      ← Homepage (jmkay.com)
├── writing.html                    ← Writing section index
├── writing/
│   ├── the-reveal.html             ← Post 01 essay
│   └── baselga-documentary.html    ← Post 02 essay
├── baselga-case-study.html         ← Baselga documentary case study
├── ask-a-scientist-case-study.html ← Ask a Scientist case study
├── sitemap.xml                     ← For Google indexing
├── robots.txt                      ← For Google indexing
├── KayDisplay-Regular.otf          ← Custom wordmark font
├── og-image.png                    ← Social sharing image
├── linkedin-featured-thumbnail.png
├── baselga-thumb.jpg               ← Homepage thumbnail
├── aas-thumb.jpg                   ← Homepage thumbnail
├── aas-thumb-new.jpg               ← Updated AAS thumbnail
├── JK profile.jpg                  ← About section photo
└── img/
    └── baselga/                    ← Case study images (10 files)
```


## Adding a new Writing post

1. Create a new HTML file in `writing/` (use an existing essay as template)
2. Add the essay entry to `writing.html` (newest first)
3. Add the URL to `sitemap.xml`
4. Commit and push via GitHub Desktop


## Google Analytics 4

All pages include a GA4 snippet with placeholder `G-XXXXXXXXXX`. To activate:

1. Go to analytics.google.com → create account → create property → choose "Web"
2. Enter https://jmkay.com → copy your Measurement ID (G-XXXXXXX)
3. Find-and-replace `G-XXXXXXXXXX` across all HTML files with your real ID
4. Commit and push


## Google Search Console (indexing)

1. Go to search.google.com/search-console
2. Add property → URL prefix → https://jmkay.com
3. Verify ownership (HTML file method or DNS)
4. Go to Sitemaps → submit "sitemap.xml"
5. Google will begin indexing within a few days
