# 🚀 Deploy & Domain Guide — Pin Phonics

## ✅ STATUS: Site built and validated
- **Bundle:** `pinphonics-site/index.html` (single self-contained file, 11.9 MB — all images inlined)
- **Local preview:** running at `http://localhost:4173` (HTTP 200 confirmed)
- **Production configs included:** `netlify.toml`, `vercel.json`, `_redirects`, `200.html`

---

## STEP 1 — Register the domain (you, ~10 min, ~$12/yr)

1. Go to **Cloudflare Registrar** (cheapest, at-cost) or **Namecheap / Porkbun**.
2. Search **`pinphonics.com`** → if available, buy it.
   - ⚠️ If taken: grab `pinreading.com` (your #2) or `pinsounds.com` from the suggestion list.
3. **DO NOT buy hosting** — you only need the domain. Hosting is free (Step 2).

---

## STEP 2 — Deploy the site FREE (I provide the file, you drag-and-drop)

### Option A: Netlify Drop (fastest — no account needed beyond free signup)
1. Go to **app.netlify.com/drop**
2. **Drag the entire `pinphonics-site` folder** into the box
3. Done — you get a live URL like `xxx.netlify.app` instantly (HTTPS by default)

### Option B: Vercel
1. Go to **vercel.com**, import as a new project, choose the folder
2. Framework preset: **Other / Static**, Output dir: `.`
3. Deploy

### Option C: Cloudflare Pages (recommended if you registered domain via Cloudflare)
1. Connect GitHub repo (or upload folder) → project → deploy
2. Free, global CDN, SSL, custom domain in 1 click

> **Cost:** $0/month on any of these. The site is fully static (one HTML file).

---

## STEP 3 — Point `pinphonics.com` at the deployed site

In your domain registrar's DNS settings, add these records (copy-paste):

| Type | Name | Value / Target |
|------|------|----------------|
| CNAME | `www` | `<your-netlify-or-vercel-url>` |
| ALIAS / ANAME | `@` (root) | `<your-netlify-or-vercel-url>` |

- On **Netlify:** Site settings → Domain management → Add `pinphonics.com` → it auto-generates the DNS records for you. Easiest path.
- On **Cloudflare:** Pages → Custom domain → enter `pinphonics.com` → done (proxy + SSL automatic).

⏱ Propagation: 5 min – 24 hrs (usually < 1 hr).

---

## STEP 4 — Add the "real" backend (when ready)

The current gift-signup opens a demo book. To make it **actually capture emails + deliver**:
- **Email capture:** Mailchimp / ConvertKit (free tier) — replace `submitGift()` in the HTML
- **Payments (handbook $29):** Stripe Payment Links (no backend code needed) — point the buy button at a Stripe link
- **Download delivery:** Gumroad or SendOwl (hosts the PDF, sends email automatically)

---

## 📁 FILES YOU NEED
| File | Purpose |
|------|---------|
| `pinphonics-site/index.html` | **The whole website** — upload this |
| `pinphonics-site/netlify.toml` | Netlify config (auto-redirects) |
| `pinphonics-site/vercel.json` | Vercel config |
| `pinphonics-site/_redirects` | Generic SPA redirects |
| `updated.html` | Your working source (keep editing this, re-build with `python3 build.py`) |

---

## 🔁 Re-deploying after changes
1. Edit `updated.html`
2. Run `python3 build.py` (regenerates `pinphonics-site/index.html`)
3. Re-upload / push to your host

That's it. Total cost to go live: **~$12 (domain only)**. Hosting = $0.
