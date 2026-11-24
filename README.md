# The HiNoterBook website

A complete static website (plain HTML, CSS and JavaScript). There is **no build step**, so Vercel serves the files exactly as they are. One small server function (`api/pre-order.js`) sends the pre-order emails.

## Deploying on Vercel (for the team)

1. In Vercel, choose **Add New → Project** and import `sabrokingmarketing/hi-notebook`.
2. **Framework Preset:** `Other`.
3. **Build Command:** leave empty. **Output Directory:** leave empty (the site is in the repository root). **Install Command:** leave empty.
4. **Environment variable:** `RESEND_API_KEY` (your Resend API key) for Production. It powers the pre-order emails. Without it the site still works, and customers get a WhatsApp/email fallback instead.
5. Deploy.

## Pre-order emails (Resend)

`api/pre-order.js` runs on Vercel when someone sends the pre-order form. It:
- emails the full order to **info@survivalguide.co.za** (reply goes straight to the customer), and
- emails the customer a branded thank-you with what they'll get and what happens next (replies go to info@survivalguide.co.za).

Emails are sent from **orders@hinoterbook.co.za**, so the domain `hinoterbook.co.za` must be verified in Resend (Resend → Domains). To change the addresses, edit the top of `api/pre-order.js`.

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

## Search (SEO)

- Live address: **https://hinoterbook.co.za** (set as `DOMAIN` in `_src/content.py`). Every page points Google to this address.
- Each page's search title and description live in the `SEO` list in `_src/content.py`.
- Built in: structured data for the business, product (price, pre-order), FAQ, video and breadcrumbs; `sitemap.xml` (with images), `robots.txt`, `site.webmanifest` and `llms.txt` (a plain summary for AI assistants).
- After the domain is live: add it to Google Search Console and Bing Webmaster Tools, verify with a DNS record, and submit `https://hinoterbook.co.za/sitemap.xml`.
