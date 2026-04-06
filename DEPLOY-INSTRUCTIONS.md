# jmkay.com — Deploy & Setup Guide

## How the site works

jmkay.com is a static site hosted on **Netlify** (site name: `jmkaydotcom`), deployed automatically from this GitHub repo. Domain registered through **Squarespace** (DNS only — Squarespace is not hosting anything).

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


## Adding a new Perspectives post

1. Create a new HTML file in `writing/` (use an existing essay as template)
2. Add the essay entry to `writing.html` (newest first)
3. Add the URL to `sitemap.xml`
4. Commit and push via GitHub Desktop


## Google Analytics 4

GA4 is active. Measurement ID `G-6XM6RT038M` is embedded in all 6 HTML files.
View analytics at analytics.google.com.


## Google Search Console (indexing)

Ownership verified via DNS/CNAME. Sitemap submitted at sitemap.xml.
View indexing status at search.google.com/search-console.
