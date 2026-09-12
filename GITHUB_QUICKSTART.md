# 🐙 GitHub + Netlify — Auto-Deploy Quickstart

## One-time setup (≈10 minutes)

### 1. Create the GitHub repo
1. Go to **github.com/new**
2. Name it `pin-phonics-site` (public or private)
3. **Don't** initialize with README/LICENSE/.gitignore — keep it empty
4. Copy the repo URL (ends in `.git`)

### 2. Push this code
```bash
cd /path/to/this/folder
git init                      # if not already done
git add .
git commit -m "Initial commit: Pin Phonics site + deploy pipeline"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### 3. Connect Netlify (drag-drop = zero config, OR Git for auto-deploy)

**Option A — Netlify Drop (fastest, no CI needed):**
1. Go to **app.netlify.com/drop**
2. Drag the **`pinphonics-site`** folder in
3. Done — instant HTTPS URL

**Option B — Git auto-deploy (recommended, what the workflow enables):**
1. **app.netlify.com** → **Import from Git** → connect GitHub → pick `pin-phonics-site`
2. Build settings:
   | Setting | Value |
   |---------|-------|
   | Build command | `python3 build.py` |
   | Publish dir | `pinphonics-site` |
3. Click **Deploy** — first build takes ~1 min

### 4. Set secrets (for the GitHub Actions workflow)
In **GitHub repo → Settings → Secrets and variables → Actions**, add:
- `NETLIFY_AUTH_TOKEN` — Netlify → User settings → Applications → create token
- `NETLIFY_SITE_ID` — Netlify site → Site settings → General → Site ID

> ⚠️ These are only needed if you use **Option B (Git auto-deploy)**. For Netlify
> Drop (Option A), there's no CI — you'd re-upload the folder manually after changes.

## Daily workflow
```
edit updated.html
  ↓
python3 build.py      # (optional, CI also runs this) rebuild bundle
  ↓
git add . && git commit -m "..." && git push
  ↓
GitHub Actions: builds + tests → Netlify deploys → live in ~1 min
```

## Connect pinphonics.com
1. In Netlify: **Domain settings → Add custom domain → pinphonics.com**
2. At your registrar: set DNS to Netlify's nameservers (or add the CNAME they show)
3. Netlify auto-provisions **free SSL** (Let's Encrypt) — usually < 1 hour

## Where things go
| File | Purpose |
|------|---------|
| `updated.html` | Your source — edit this |
| `build.py` | Builds `pinphonics-site/index.html` |
| `config.js` | Real keys (gitignored) |
| `.github/workflows/ci.yml` | CI: builds + tests on every push |
| `serve.py` | Local dev server + dev API |
| `server.js` | Optional Node backend (Mailchimp server-side + Gumroad webhooks) |
| `BACKEND_INTEGRATION.md` | Mailchimp / Gumroad / Stripe wiring guide |
| `DEPLOY_AND_DOMAIN_GUIDE.md` | Full deploy + DNS walkthrough |

## Cost recap
| Item | Cost |
|------|------|
| `pinphonics.com` domain | ~$12/yr |
| Netlify hosting (static site) | **$0** |
| Mailchimp (up to 500 contacts) | **$0** |
| Gumroad (handbook delivery) | **$0** + 10% per sale (or $0/mo + fees) |
| Stripe (if used instead) | 2.9% + 30¢/sale |

**Total to go live: ~$12.** No monthly hosting bill.
