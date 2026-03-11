# Deploying jmkay.com to Vercel

## What's in this folder

This is a clean deploy package — only the files that should go live:

```
index.html                  ← your homepage (jmkay.com)
baselga-case-study.html     ← the case study subpage
baselga-thumb.jpg           ← homepage thumbnail for Baselga project
aas-thumb.jpg               ← homepage thumbnail for Ask a Scientist
img/baselga/                ← all case study images (11 files)
```

There's also a `jmkay-live-deploy.zip` in this folder if you want to drag-and-drop deploy.


## Option A: Vercel (Recommended — free, fast, custom domain support)

### First-time setup

1. Go to **vercel.com** and click **Sign Up** → sign in with your **GitHub** account (or email)
2. Once logged in, click **"Add New…" → "Project"**
3. Instead of connecting a Git repo, scroll down and look for **"Or import a third-party Git repository"** — skip that too
4. Actually the easiest way: just go to **vercel.com/new** and look for the option to **deploy without a repo**

### The drag-and-drop method (easiest)

1. Go to **vercel.com/new**
2. You should see an area that says **"Import Project"**
3. At the bottom, click **"Browse for files"** or just drag the entire `jmkay-live-deploy` folder onto the page
4. Vercel will auto-detect it as a static site (no framework)
5. Click **Deploy**
6. In about 30 seconds you'll get a live URL like `jmkay-live-deploy.vercel.app`

### Connecting your custom domain (jmkay.com)

1. In your Vercel project dashboard, go to **Settings → Domains**
2. Type `jmkay.com` and click **Add**
3. Vercel will show you DNS records to add. You'll need to go to wherever you bought `jmkay.com` (GoDaddy, Namecheap, Google Domains, Squarespace, etc.)
4. In your domain registrar's DNS settings, add the records Vercel gives you. Typically:
   - **A Record**: `@` → `76.76.21.21`
   - **CNAME Record**: `www` → `cname.vercel-dns.com`
5. DNS can take 5 minutes to a few hours to propagate
6. Vercel auto-provisions HTTPS (SSL certificate) — no action needed


## Option B: Netlify (also free, also easy)

1. Go to **app.netlify.com** → sign up or log in
2. Look for **"Deploy manually"** or the drag-and-drop area
3. Drag the `jmkay-live-deploy` folder onto it
4. Same custom domain process: Settings → Domain management → Add custom domain → update DNS


## Future updates

When you want to update the site:

- **Vercel**: Go to your project → Deployments → drag the updated folder again (or connect a Git repo for automatic deploys)
- **Netlify**: Go to Deploys → drag to redeploy

The key thing is: always deploy the entire folder, not individual files.


## File structure reference

```
jmkay-live-deploy/
├── index.html                          ← Homepage
├── baselga-case-study.html             ← Case study
├── baselga-thumb.jpg                   ← Thumbnail (homepage)
├── aas-thumb.jpg                       ← Thumbnail (homepage)
└── img/
    └── baselga/
        ├── hero-title.png              ← Hero background
        ├── jk-silvia-candid.jpg        ← Photo grid
        ├── premiere-screens.jpg        ← Photo grid
        ├── premiere-auditorium.jpg     ← Photo grid (wide)
        ├── jk-silvia-aacr.jpg         ← AACR inline photo
        ├── premiere-frontrow.jpg       ← Premiere inline photo
        ├── laurel-selection-white.png  ← BIFF laurel
        ├── laurel-honorable-white.png  ← BIFF laurel
        ├── laurel-winner-white.png     ← BIFF laurel
        ├── laurel-spain-iff.png        ← Spain IFF logo
        └── filmmakerlife-feature.png   ← Magazine feature
```
