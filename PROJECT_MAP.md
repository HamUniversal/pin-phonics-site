# 📂 Project Map — Pin Phonics

```
pin-phonics/
├── 📄 updated.html              ← YOUR SOURCE. Edit this. Everything starts here.
├── 🔨 build.py                 ← Builds pinphonics-site/index.html (inlines assets, validates config)
├── 🧪 test_backend.py          ← 14-assertion unit suite (runs in <1s, no server)
├── ✅ final_check.py           ← Full e2e: builds → starts server → hits endpoints → validates
├── 🌐 serve.py                ← Dev server: GET /, /config.js, /api/config · POST /api/signup
├── 🟢 server.js               ← Optional Node backend (Mailchimp server-side + Gumroad webhooks)
├── ⚙️  config.example.js       ← Template (committed). Copy → config.js, fill keys.
├── 🔒 config.js               ← Real keys (GITIGNORED). Never commit.
├── 📦 pack_site.py            ← → pinphonics-site-deploy.zip (drag to Netlify)
├── 📦 pack.py                 ← → pinphonics-complete.zip (full project)
├── 🏁 finalize.sh             ← ./finalize.sh = build + check + pack (ONE COMMAND TO SHIP)
│
├── 📖 README.md
├── 🚀 REDEPLOY.md             ← 4 steps: register domain → deploy → DNS → activate backend
├── 🐙 GITHUB_QUICKSTART.md    ← GitHub + Netlify CI/CD walkthrough
├── 🔌 BACKEND_INTEGRATION.md  ← Mailchimp + Gumroad + Stripe architecture
├── 🌍 DEPLOY_AND_DOMAIN_GUIDE.md
├── 🏷️  Pin_Domain_Name_Recommendation.md
│
├── ⚙️  package.json            ← npm scripts: build / test / check / serve / finalize
├── 🐍 .github/workflows/ci.yml ← GitHub Actions: build + test on every push
├── 🚫 .gitignore
└── 📁 pinphonics-site/         ← BUILD OUTPUT (gitignored). Don't edit here — edit updated.html.
```

## The 3 layers

| Layer | Files | Purpose |
|-------|-------|---------|
| **Source** | `updated.html` | The actual site. Single file, all CSS/JS inline, 14 Lucide SVGs. |
| **Build** | `build.py`, `validate_config.py`, `test_backend.py` | Turn source → production bundle + catch errors before deploy. |
| **Runtime** | `serve.py` (dev) · `server.js` (optional prod) · `config.js` | Serve the site + handle email/payment. **All optional — site works static.** |

## The data flow

```
User clicks "Get free gift"
  → openGift() shows modal
  → user submits email
  → captureEmail()  →  Mailchimp (embedded-form URL, public-safe)
  → deliverBook()   →  opens 3D Aesop fable (client-side)

User clicks "Get Premium Handbook"
  → openHandbookCheckout()
  → Gumroad product page (auto-delivers PDF + emails download)
  → (or Stripe Payment Link as fallback)
```

## Daily workflow

```bash
edit updated.html
./finalize.sh          # builds, tests, packs — one command
git push               # auto-deploys via GitHub Actions → live in ~1 min
```

## Key safety properties

- ✅ **`config.js` is gitignored** — real keys never hit GitHub
- ✅ **Safe demo fallback** — site works with placeholder keys (emails log to console)
- ✅ **No API keys in browser** — Mailchimp uses public embedded-form URL
- ✅ **Build-time config validation** — typos fail `build.py` before deploy
- ✅ **Port fallback** — `serve.py` tries 4173→4177 if a port is occupied

## What's deliberately NOT here

- ❌ No database (Mailchimp + Gumroad handle persistence)
- ❌ No server required in production (fully static + third-party APIs)
- ❌ No build tools / bundlers (plain Python + one file)
- ❌ No monthly hosting cost (Netlify free tier)
