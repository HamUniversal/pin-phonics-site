# 🐙 GitHub Repo & CI/CD — Complete Guide

This guide picks up where **[`GITHUB_QUICKSTART.md`](./GITHUB_QUICKSTART.md)**
leaves off: it covers the **full GitHub workflow** — repo setup, branching,
PRs, secrets, the auto-deploy pipeline, rollbacks, and day-to-day habits.

---

## 1. The repo

**Recommended name:** `pin-phonics-site` (GitHub allows dashes; it's the
convention for project repos). Keep it under your personal account or create
a `pinphonics` organisation — either works.

| Setting | Recommendation |
|---|---|
| Visibility | **Public** (required for free GitHub Pages) |
| Init | **Don't** add README / LICENSE / .gitignore — keep it empty |
| Branch | `main` (already the default in `init-repo.sh`) |

> The repo must be created **on github.com first** (the API isn't authenticated
> here). `init-repo.sh` will then push to it.

---

## 2. First-time push (two options)

### Option A — automated script (recommended)

```bash
./init-repo.sh https://github.com/<YOU>/pin-phonics-site.git
```

The script: verifies no existing `.git`, inits `main`, adds + commits
everything (respecting `.gitignore`), wires the remote, and pushes. It prints
the Actions URL at the end.

### Option B — manual

```bash
git init -b main
git add .
git commit -m "Initial commit: Pin Phonics site + CI/CD auto-deploy pipeline"
git remote add origin https://github.com/<YOU>/pin-phonics-site.git
git push -u origin main
```

> 🔒 `config.js` and `*.zip` are gitignored — `git status` should show
> **no** `.zip` and **no** `config.js` files. If it does, stop and check
> `.gitignore`.

---

## 3. The pipeline (`.github/workflows/ci.yml`)

```
push / PR  ──▶  build-and-test  ──▶  upload-artifact (pinphonics-site, 30d)
                                    │
              ┌─────────────────────┴─────────────────────┐
              ▼                                           ▼
        push to main?                                 secrets set?
              │                                           │
              ▼                                           ▼
      deploy-netlify (primary)                 deploy-pages (fallback)
              │                                           │
              ▼                                           ▼
        netlify URL / pinphonics.com            https://<user>.github.io/<repo>/
```

### Jobs

| Job | Runs on | What it does |
|---|---|---|
| `build-and-test` | every push + every PR | `build.py` → `final_check.py` (38 checks) → `serve.py` smoke test → uploads artifact |
| `deploy-netlify` | push to `main` **only** | Deploys `pinphonics-site/` via `nwtgck/actions-netlify` |
| `deploy-pages` | push to `main`, **only if Netlify secrets are empty** | Falls back to GitHub Pages |
| `report` | always (final) | Prints bundle SHA + job results |

**Key behaviours:**
- **PRs never deploy** — they only run build + tests, so a bad change can't go live.
- **The build artifact is retained 30 days** — you can download a known-good
  bundle from any run and re-upload it manually if needed.
- **Pages fallback** means you get a live URL **even with zero configuration**.
  Once you add the two Netlify secrets, the Pages job auto-skips and Netlify
  becomes primary.

### Required secrets (for Netlify)

In **Settings → Secrets and variables → Actions**, add:

```
NETLIFY_AUTH_TOKEN   # Netlify → User settings → Applications → create token
NETLIFY_SITE_ID      # Netlify site → Site settings → General → Site ID
```

That's it — the workflow reads them automatically. **No code change needed.**

---

## 4. Daily workflow

```bash
# Make a change
$EDITOR updated.html

# (optional) build + verify locally — CI runs this anyway
python3 build.py && python3 final_check.py

# Commit + push → auto-deploy
git add updated.html
git commit -m "Add: new hero copy"
git push
```

Within **~1 minute** the live site updates. Watch it at the repo's
**Actions** tab.

### Branch + PR workflow (recommended for anything non-trivial)

```bash
git checkout -b tweak/hero-copy
$EDITOR updated.html
git add . && git commit -m "Tweak hero copy"
git push -u origin tweak/hero-copy
# → open a Pull Request on github.com
# → CI runs build + 38 checks
# → merge → auto-deploys to Netlify
```

This gives you a **green checkmark gate** before anything reaches the live site.

---

## 5. Rollbacks

**Fastest:** revert the commit and push.

```bash
git revert <BAD_COMMIT_SHA>
git push
```

The pipeline rebuilds and deploys the previous version in ~1 minute.

**Alternative:** download the good artifact from an earlier run
(Actions → run → *pinphonics-site* artifact) and re-upload it to Netlify
manually — useful if the build itself is broken.

---

## 6. Connecting `pinphonics.com`

1. Register `pinphonics.com` (~$12/yr) at Cloudflare / Namecheap / Porkbun.
2. In **Netlify → Domain settings → Add custom domain → pinphonics.com**.
3. At your registrar, set **Netlify nameservers** (or the CNAME shown).
4. Netlify auto-provisions **free SSL** (Let's Encrypt) — usually < 1 hour.

> If you use the **GitHub Pages** fallback instead, add `pinphonics.com` as a
> custom domain in *repo → Settings → Pages* and configure the same DNS records.

Full details: **[`DEPLOY_AND_DOMAIN_GUIDE.md`](./DEPLOY_AND_DOMAIN_GUIDE.md)**

---

## 7. Keeping secrets safe

- ✅ `config.js` is **gitignored** — never committed.
- ✅ The site uses **public-safe endpoints** (Mailchimp embedded-form URL);
  no secret keys live in the browser.
- ✅ For production email capture, run `server.js` (keys stay server-side,
  injected via GitHub Actions secrets).

When you **do** need a secret in CI:

```bash
# add it in the GitHub UI, then reference it in ci.yml as:
env:
  MY_SECRET: ${{ secrets.MY_SECRET }}
```

Never paste real keys into `config.js` and then commit — the gitignore
protects you, but double-check with `git status` first.

---

## 8. Repository layout

```
pin-phonics-site/
├── updated.html                 ← SOURCE (edit this)
├── build.py                     ← builds pinphonics-site/index.html
├── pinphonics-site/             ← BUILD OUTPUT (gitignored, regenerated)
├── config.example.js            ← safe template (committed)
├── config.js                    ← REAL KEYS (gitignored)
├── .github/
│   └── workflows/
│       └── ci.yml               ← CI/CD pipeline
├── serve.py                     ← local dev server + API
├── server.js                    ← optional Node backend
├── final_check.py               ← 38-assertion e2e suite
├── test_backend.py              ← 14 backend checks
├── validate_workflow.py         ← checks ci.yml structure
├── init-repo.sh                 ← one-shot git init + push
├── finish.sh                    ← clean → build → test → pack
├── .gitignore
├── README.md                    ← this repo's front page
├── GITHUB_QUICKSTART.md
├── GITHUB_GUIDE.md              ← this file
├── BACKEND_INTEGRATION.md
├── DEPLOY_AND_DOMAIN_GUIDE.md
├── PROJECT_MAP.md
└── REDEPLOY.md
```

---

## 9. Quick reference

| Goal | Command |
|---|---|
| Validate the workflow file | `python3 validate_workflow.py` |
| Full local build + test | `python3 build.py && python3 final_check.py` |
| Start dev server | `python3 serve.py` (→ http://127.0.0.1:4173) |
| Init repo + push | `./init-repo.sh <REPO_URL>` |
| Pack release zips | `bash finish.sh` |
| Watch deploys | github.com/\<YOU\>/pin-phonics-site/actions |
| Roll back | `git revert <SHA>` then `git push` |

---

**Total to launch: ~$12/yr** (just the domain). Hosting, CI/CD, and email are
all free.
