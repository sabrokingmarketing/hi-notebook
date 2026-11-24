# HiNote Book website

A complete static website (plain HTML, CSS and JavaScript). There is **no build step**, so Vercel serves the files exactly as they are.

## Deploying on Vercel (for the team)

1. In Vercel, choose **Add New → Project** and import `sabrokingmarketing/hi-notebook`.
2. **Framework Preset:** `Other`.
3. **Build Command:** leave empty. **Output Directory:** leave empty (the site is in the repository root). **Install Command:** leave empty.
4. Deploy. No environment variables, API keys or secrets are needed.

`index.html` is the homepage and `404.html` is shown automatically for missing pages.
`.vercelignore` keeps the source and project files (`_src`, `.claude`, `CLAUDE.md`, this README) off the live site.

## Editing the text, prices and contact details

All business text, prices, contact details and the to-do list live in **`_src/content.py`**.
After editing it, rebuild the pages (needs Python 3, nothing to install):

```
python3 _src/build.py
```

Then commit and push. Vercel redeploys automatically.

Layout, colours and behaviour live in `assets/css/site.css` and `assets/js/site.js`.

## Still to fill in before going live

See the `TODO` list at the bottom of `_src/content.py`. Most important: the real **WhatsApp number, phone number and email**.
Until those are filled in, pre-orders and questions cannot reach the team.
