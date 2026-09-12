# 🚀 Final Deployment — Pin Phonics

Everything is built, verified, and packaged. Here's the exact path from "finished"
to a live site at **pinphonics.com**.

## What you have (already done)

```
pinphonics-site-deploy.zip   ← 27 MB  drag this to Netlify  →  instant HTTPS URL
pinphonics-complete.zip       ← 63 MB  full project (source + all guides)
```

Both zips were created by `finalize.sh` after `final_check.py` passed 32/32 checks.

## The 4-step finish line

### Step 1 — Register the domain (~$12/yr)
- **Cloudflare Registrar** (cheapest, free DNS + SSL forever): cloudflare.com/registrar
- Or Namecheap / Porkbun
- Search **`pinphonics.com`** → buy it
- ⚠️ Verify availability at checkout + ICANN RDAP — **none of the 3 originals were confirmed free** earlier

### Step 2 — Deploy the static site (free, ~2 min)

**Option A — Netlify Drop (fastest, zero config):**
1. Unzip `pinphonics-site-deploy.zip`
2. Go to **app.netlify.com/drop**
3. **Drag the folder** → instant HTTPS URL like `brave-curie-123456.netlify.app`
4. Done. Site is live.

**Option B — Netlify + GitHub auto-deploy (recommended for ongoing edits):**
1. Unzip `pinphonics-complete.zip`
2. `cd pin-phonics && git init && git add . && git commit -m "Initial"`
3. Create repo on GitHub → `git remote add origin <url> && git push -u origin main`
4. **app.netlify.com → Import from Git** → connect repo
   - Build command: `python3 build.py`
   - Publish dir: `pinphonics-site`
5. Add secrets (GitHub → Settings → Secrets): `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`
6. Every `git push` → auto-deploys in ~1 min

**Option C — Vercel:** `vercel deploy --prod` (uses the included `vercel.json`)

### Step 3 — Point pinphonics.com at it
1. In Netlify: **Domain settings → Add custom domain → pinphonics.com**
2. At your registrar: change nameservers to Netlify's (or add the CNAME shown)
3. Netlify auto-provisions **free Let's Encrypt SSL** — usually < 1 hour
4. Visit `https://pinphonics.com` ✅

### Step 4 — Activate the backend (when ready)
Edit `config.js` (already gitignored, lives in the complete zip):

```js
window.PIN_CONFIG = {
  MAILCHIMP: { url: "https://YOUR_DC_LIST-MANAGE.COM/subscribe/post?u=XXX&id=YYY" },  // embedded-form URL
  GUMROAD:   { paymentLink: "https://gumroad.com/l/YOUR_SHORTCODE" },                  // handbook product
  STRIPE:    { paymentLink: "" }  // optional alternative
};
```

| Service | Free tier | Get the value from |
|---------|-----------|---------------------|
| Mailchimp | 500 contacts | Audience → Signup forms → Embedded forms → copy `action=` |
| Gumroad | Free (10% per sale) | New product "Pin Phonics Handbook" $29 → Share → Short URL |

> **Without Step 4 the site still works perfectly** — emails just log to console and the buy button scrolls to the purchase section. So you can **launch today, monetize later**.

## Cost recap
| Item | Cost |
|------|------|
| `pinphonics.com` | ~$12/yr |
| Static hosting (Netlify) | **$0** |
| SSL certificate | **$0** (auto, Let's Encrypt) |
| Email (Mailchimp, ≤500 contacts) | **$0** |
| Handbook delivery (Gumroad) | **$0** + 10% per sale |

**Total to go live: ~$12.** No monthly hosting bill. Ever.

## Verification status
```
✅ Build              → 12.2 MB bundle, 14 SVGs, green CTA, Aesop hook
✅ Dev server         → port-fallback works (4173→4174 if occupied)
✅ Endpoints          → GET /, /config.js, /api/config · POST /api/signup
✅ test_backend.py    → 14/14 passed
✅ Bundle validation  → all wiring present, JS parses clean
✅ Repo manifest      → 18 files, config.js properly gitignored
```

See `GITHUB_QUICKSTART.md` for the CI/CD deep dive and `BACKEND_INTEGRATION.md` for the full Mailchimp/Gumroad/Stripe architecture.
