# Step 2 — Replace Placeholders & Push to GitHub

**Goal:** Replace the fake handles (`@pinphonics-owner`, etc.) with **your real GitHub handle**, then push the code to your empty repo at `github.com/HamUniversal/pin-phonics-site`.

> **Do this ONCE.** After today, you'll never touch CODEOWNERS or SECURITY.md again — you'll just edit `updated.html` and run `finish.sh`.

---

## 🧭 Big picture (read this first — 30 seconds)

Right now the files contain **placeholder text**, not real GitHub handles:

```
@pinphonics-owner        ← fake
@pinphonics-security     ← fake
@pinphonics-maintainers  ← fake
```

GitHub **ignores** these — they don't route reviews to anyone. You need them to say **your real handle** (e.g. `@HamUniversal`).

**You have TWO choices** to do the replacement. Pick **ONE**:

| | Option A — Run the script (recommended) | Option B — Edit by hand |
|---|---|---|
| **What** | One command does everything | Open 2 files in GitHub's web editor |
| **Where** | On your own computer (terminal) | In your browser |
| **Time** | 3 minutes | 5 minutes |
| **Best for** | You're comfortable with a terminal | You've never used a terminal |

---

## ✅ BEFORE YOU START — 3 one-time setups

Do these **once**, in order. Skip any you already have.

### ① Install Git
- **Mac:** already installed. Open Terminal, type `git --version` to check.
- **Windows:** download from https://git-scm.com/downloads → accept all defaults.
- **Verify:** `git --version` prints something like `git version 2.x.x`.

### ② Install the GitHub CLI (`gh`)
This makes authentication one-click instead of copy-pasting tokens.
- **Mac:** `brew install gh`
- **Windows:** `winget install --id GitHub.cli`
- **Linux:** `sudo apt install gh`
- **Verify:** `gh --version`

### ③ Log in to GitHub from your computer
```bash
gh auth login
```
When it asks:
1. **What account do you want to log into?** → `GitHub.com`
2. **How would you like to authenticate?** → `Login with a web browser` ✅ (easiest)
3. It prints a **one-time code** → press Enter → browser opens → paste the code → Authorize
4. **What is your preferred protocol?** → `HTTPS`

> 💡 **Stuck on `gh auth login`?** You can skip it — the script will fall back to your browser's saved GitHub login. But `gh` is smoother, so try it first.

---

## 🚀 Option A — Run the script (RECOMMENDED, 3 min)

### Step 1 — Download the project to your computer
You got `pinphonics-complete.zip` from me. Unzip it. Remember where it is.

**Example:** if you unzip to your `Downloads` folder, the folder is:
- Mac/Linux: `~/Downloads/pinphonics-complete/`
- Windows: `C:\Users\YOURNAME\Downloads\pinphonics-complete\`

### Step 2 — Open a terminal in that folder
- **Mac:** open Terminal → type `cd ` (with a space) → **drag the folder into the window** → press Enter
- **Windows:** in File Explorer, go into the folder → click the address bar → type `cmd` → press Enter
- **Verify you're in the right place:** type `ls` (Mac/Linux) or `dir` (Windows) — you should see `CODEOWNERS`, `SECURITY.md`, `setup-github.sh`, etc.

### Step 3 — Replace your handle + push
Run this **one command** (replace `HamUniversal` with YOUR real GitHub handle):

```bash
./setup-github.sh HamUniversal
```

That's it. The script:
1. ✅ Replaces all `@pinphonics-*` placeholders with `@HamUniversal`
2. ✅ Initializes git
3. ✅ Commits everything
4. ✅ Pushes to `https://github.com/HamUniversal/pin-phonics-site.git`
5. ✅ Turns on branch protection + Dependabot + secret scanning

**If it asks for a password or login:** that's just GitHub authenticating — log in via the browser popup.

### Step 4 — Check it worked
Open https://github.com/HamUniversal/pin-phonics-site — you should see all the files (`index.html`, `.github/`, `CODEOWNERS`, `SECURITY.md`, etc.).

🎉 **Done with Option A.** Jump to the **"AFTER BOTH OPTIONS"** section below.

---

## ✏️ Option B — Edit by hand in your browser (5 min)

Don't want to use a terminal? Edit the two files directly on GitHub.

### Step 1 — Upload the files first
GitHub's empty-repo page has an **"uploading an existing file"** link. But that's tedious for 38 files. **Easier:** use GitHub Desktop (free, https://desktop.github.com):

1. Install GitHub Desktop → sign in
2. **File → Clone repository** → `HamUniversal/pin-phonics-site`
3. Copy ALL files from `pinphonics-complete/` into the cloned folder
4. **Commit → Push** (top right)

Now the repo has your code. **Or** just drag-and-drop the whole `pinphonics-complete` folder using the **"Add file → Upload files"** button on the repo page.

### Step 2 — Edit `CODEOWNERS`
1. On GitHub, click the file named **`CODEOWNERS`**
2. Click the **✏️ pencil icon** (Edit this file) — top right
3. Find every place that says `@pinphonics-owner`, `@pinphonics-security`, `@pinphonics-maintainers`
4. **Replace ALL THREE** with your handle, e.g. `@HamUniversal`
5. Scroll down → **Commit changes** (green button)

### Step 3 — Edit `SECURITY.md`
1. Click **`SECURITY.md`** → ✏️ pencil icon
2. Find `security@pinphonics.com` → replace with your **real email** (e.g. `you@gmail.com`)
3. Find the `REPLACE_ME` / PGP block → **leave it for now** (you can add a real PGP key later; the GitHub Advisory route still works without it)
4. **Commit changes**

### Step 4 — Verify
On the repo's main page, click **Settings → Code security**. You should see Dependabot options available.

🎉 **Done with Option B.**

---

## 🎯 AFTER BOTH OPTIONS — connect Netlify (so it actually deploys)

The repo is pushed, but it won't go live until you connect a host. **2 minutes:**

1. Go to **https://app.netlify.com** → sign up/log in (use your GitHub account)
2. Click **"Import from Git"** or **"Add new site → Import from a Git repository"**
3. **Authorize Netlify** to access your GitHub → select `HamUniversal/pin-phonics-site`
4. Build settings (Netlify auto-detects these from `netlify.toml`, but double-check):
   - **Build command:** `python3 build.py`
   - **Publish directory:** `pinphonics-site`
5. Click **Deploy site**

Within ~1 minute you'll get a URL like `https://amazing-name-123.netlify.app`. **It's live.**

### Add the 2 secrets (so auto-deploy keeps working)
In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | What to put |
|---|---|
| `NETLIFY_AUTH_TOKEN` | Netlify → User Settings → Applications → Personal access tokens → New token |
| `NETLIFY_SITE_ID` | Netlify → Site settings → General → Site ID |

After adding both, **push any small change** (edit `README.md`) to trigger the workflow — watch it deploy at https://github.com/HamUniversal/pin-phonics-site/actions.

---

## ✅ CHECKLIST — tick these off

```
□ Git installed (git --version works)
□ gh CLI installed (gh --version works)
□ gh auth login completed (logged in via browser)
□ CodeOWNERS placeholders replaced with @YourHandle
□ SECURITY.md email updated to your real email
□ Code pushed to github.com/HamUniversal/pin-phonics-site
□ Repo shows all files (not empty anymore)
□ Netlify connected to the repo
□ Build command = python3 build.py, Publish dir = pinphonics-site
□ Site deployed to a .netlify.app URL
□ NETLIFY_AUTH_TOKEN secret added
□ NETLIFY_SITE_ID secret added
□ A test push triggered the Actions workflow successfully
□ Domain pinphonics.com registered (Cloudflare/Namecheap/Porkbun, ~$12/yr)
□ In Netlify: Settings → Domain → add pinphonics.com → auto DNS + free SSL
```

---

## 🆘 TROUBLESHOOTING — common problems

| Problem | Fix |
|---------|-----|
| `gh auth login` says "command not found" | `gh` isn't installed — see "② Install gh CLI" above |
| `Authentication failed` when pushing | Re-run `gh auth login` and choose "HTTPS" + "web browser" |
| Repo already has a commit (not empty) | In the repo on GitHub: **Settings → General → Delete repository**, then recreate empty. Or use `git push --force` if you're sure |
| "Permission denied" on push | Your GitHub account doesn't own `HamUniversal/pin-phonics-site`. Check the repo URL matches YOUR account |
| Script says "config.js not found" | You're in the wrong folder — `ls` should show `setup-github.sh`. `cd` into the right one |
| Netlify deploy fails with "command not found: python3" | Change build command to `python build.py` (no `3`). Or use the "Build with: none" + publish `pinphonics-site` directly |
| CODEOWNERS shows `@pinphonics-owner` still | You edited the file but didn't push. Commit + push again |
| `setup-github.sh` permission denied | Run `chmod +x setup-github.sh` first (Mac/Linux) |
| Site works but `config.js` errors | That's fine — it's gitignored. Copy `config.example.js` → `config.js` and fill in keys when ready |

---

## 🤔 "Wait, what exactly did I just do?"

**In plain English:**

1. **GitHub** is just a folder in the cloud that tracks your files and runs automation (the CI/CD pipeline).
2. **`git push`** = "upload my local files to that cloud folder."
3. **CODEOWNERS** = a rule that says "if anyone changes these sensitive files, ask me to review first."
4. **But** right now those rules point to fake names (`@pinphonics-owner`). You changed them to **your real name** (`@HamUniversal`) so GitHub actually knows who to ask.
5. **Netlify** watches that folder — every time you push, it rebuilds and republishes the site. That's the "auto-deploy."

**You only do steps 1–5 once.** From tomorrow on, updating the site is just:

```bash
edit updated.html
bash finish.sh
git push
# → live in ~1 minute
```

---

## 🔐 Final checksums (verify your download is intact)

After unzipping `pinphonics-complete.zip`, run:

```bash
shasum -a 256 pinphonics-complete.zip
```

It should match the checksum printed in the console when the zip was built. If it doesn't, re-download.
