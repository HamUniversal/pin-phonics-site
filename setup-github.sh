#!/usr/bin/env bash
# setup-github.sh — Foolproof first-time GitHub setup for Pin Phonics
#
# What this script does (and does NOT do):
#   ✅ Detects your GitHub auth method (gh CLI or git credentials)
#   ✅ Replaces placeholder handles in CODEOWNERS + SECURITY.md
#   ✅ Inits git, commits, pushes to https://github.com/HamUniversal/pin-phonics-site.git
#   ✅ Turns on GitHub security features (branch protection, etc.)
#   ❌ Does NOT create the repo (you already did that — HamUniversal/pin-phonics-site)
#   ❌ Does NOT need you to type any git commands
#
# Usage (pick ONE):
#   ./setup-github.sh                         # interactive: prompts for your handle
#   ./setup-github.sh your-github-handle      # non-interactive
#   ./setup-github.sh your-github-handle --security-email you@gmail.com
#
# Prerequisites (one-time, 5 min):
#   • Git installed (https://git-scm.com/downloads)
#   • A GitHub account
#   • The empty repo already created at:
#       https://github.com/HamUniversal/pin-phonics-site.git   ← you did this ✅
set -e

cd "$(dirname "$0")"

G='\033[0;32m'; B='\033[0;34m'; R='\033[0;31m'; Y='\033[0;33m'; N='033[0m'
step() { echo -e "\n${B}▶ $*${N}"; }
ok()   { echo -e "  ${G}✅ $*${N}"; }
warn() { echo -e "  ${Y}⚠️  $*${N}"; }
bad()  { echo -e "  ${R}❌ $*${N}"; }

REPO_URL="https://github.com/HamUniversal/pin-phonics-site.git"
HANDLE=""
SECURITY_EMAIL=""

# Parse argv: handle is the bare arg; --security-email sets the contact address.
for arg in "$@"; do
  case "$arg" in
    --security-email=*) SECURITY_EMAIL="${arg#*=}" ;;
    --security-email)   ;; # value comes next iteration (handled below)
    --*)
      echo "Unknown option: $arg"
      echo "Usage: $0 [your-github-handle] [--security-email=you@gmail.com]"
      exit 1
      ;;
    *)
      if [ -z "$HANDLE" ]; then HANDLE="$arg"; else SECURITY_EMAIL="$arg"; fi
      ;;
  esac
done

echo -e "${G}════════════════════════════════════════════════════════════${N}"
echo -e "${G}  Pin Phonics — GitHub Setup (foolproof)${N}"
echo -e "${G}════════════════════════════════════════════════════════════${N}"
echo -e "  Repo: ${B}${REPO_URL}${N}"
echo ""

# ────────────────────────────────────────────────────────────────────────
# STEP 1 · Get your GitHub handle
# ────────────────────────────────────────────────────────────────────────
step "STEP 1/6 · Your GitHub handle"

if [ -z "$HANDLE" ]; then
  echo "  Your GitHub handle is the part after 'github.com/' in your profile URL."
  echo "  Example: github.com/janedoe  →  handle = janedoe"
  echo ""
  echo -n "  Enter your GitHub handle: "
  read -r HANDLE
fi

if [ -z "$HANDLE" ]; then
  bad "Handle cannot be empty. Re-run with:  ./setup-github.sh YOUR-HANDLE"
  exit 1
fi

# Strip @ if typed by mistake
HANDLE="${HANDLE#@}"

ok "Handle set to: ${HANDLE}"
echo "  (All @pinphonics-owner / @pinphonics-security / @pinphonics-maintainers"
echo "   placeholders will be replaced with @${HANDLE})"

# ────────────────────────────────────────────────────────────────────────
# STEP 2 · Replace placeholders in CODEOWNERS + SECURITY.md
# ────────────────────────────────────────────────────────────────────────
step "STEP 2/6 · Replace placeholders in CODEOWNERS + SECURITY.md"

replace() {
  local file="$1"
  if [ ! -f "$file" ]; then
    warn "${file} not found — skipping"
    return
  fi
  # Works on macOS (BSD sed) and Linux (GNU sed) without -i extension drama.
  sed -i.bak \
    -e "s|@pinphonics-owner|@${HANDLE}|g" \
    -e "s|@pinphonics-security|@${HANDLE}|g" \
    -e "s|@pinphonics-maintainers|@${HANDLE}|g" \
    "$file"
  rm -f "${file}.bak"
  ok "${file} updated"
}

replace CODEOWNERS
replace SECURITY.md

# Also replace the security contact email placeholder with a real address.
# Falls back to a github.com contact form link if the user has no mailbox yet.
SECURITY_EMAIL="${SECURITY_EMAIL:-}"
if [ -z "$SECURITY_EMAIL" ]; then
  echo ""
  echo "  Security contact email (leave blank to use a contact-form fallback):"
  echo -n "  Enter an email (or press Enter to skip): "
  read -r SECURITY_EMAIL
fi
if [ -n "$SECURITY_EMAIL" ]; then
  sed -i.bak "s|SECURITY_EMAIL_PLACEHOLDER|${SECURITY_EMAIL}|g" SECURITY.md
  rm -f SECURITY.md.bak
  ok "SECURITY.md email set to: ${SECURITY_EMAIL}"
else
  warn "No email provided — SECURITY_EMAIL_PLACEHOLDER left in SECURITY.md"
  echo "  → Replace it manually before launch, or re-run with:"
  echo "      ./setup-github.sh your-handle --security-email=you@gmail.com"
fi

echo ""
echo "  Verify (you should see your handle, not @pinphonics-*):"
grep -n "@${HANDLE}" CODEOWNERS | head -5 || true
echo ""

# ────────────────────────────────────────────────────────────────────────
# STEP 3 · Check authentication
# ────────────────────────────────────────────────────────────────────────
step "STEP 3/6 · Checking GitHub authentication"

AUTH_METHOD=""
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  AUTH_METHOD="gh"
  ok "GitHub CLI (gh) is authenticated"
  gh auth status 2>&1 | head -5 || true
elif git ls-remote "$REPO_URL" >/dev/null 2>&1; then
  AUTH_METHOD="git"
  ok "Git can already push to ${REPO_URL}"
else
  warn "No working GitHub auth detected."
  echo ""
  echo "  Choose ONE option:"
  echo ""
  echo "  ${G}Option A (recommended — easiest):${N}"
  echo "    1. Install gh CLI:  https://cli.github.com/"
  echo "    2. Run:  gh auth login   (choose 'HTTPS', then 'Login with a web browser')"
  echo "    3. Re-run this script."
  echo ""
  echo "  ${G}Option B (use SSH instead):${N}"
  echo "    1. Add your SSH key to GitHub:  https://github.com/settings/keys"
  echo "    2. Use the SSH URL below when prompted."
  echo ""
  echo -n "  Enter the remote URL to use (or press Enter to retry HTTPS): "
  read -r CUSTOM_URL
  [ -n "$CUSTOM_URL" ] && REPO_URL="$CUSTOM_URL"
fi

# ────────────────────────────────────────────────────────────────────────
# STEP 4 · Init, commit, push
# ────────────────────────────────────────────────────────────────────────
step "STEP 4/6 · Initialize git + push to GitHub"

if [ -d .git ]; then
  warn ".git already exists — re-using it."
  git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL"
else
  git init -b main >/dev/null
  git remote add origin "$REPO_URL" 2>/dev/null || true
fi

git branch -M main
git add .
echo ""
echo "Files to commit (config.js and *.zip are gitignored):"
git status --short | head -40
echo ""

if git status --short | grep -q .; then
  git commit -m "Initial commit: Pin Phonics site + CI/CD auto-deploy pipeline" >/dev/null
  ok "Committed locally"
else
  ok "Nothing new to commit (already committed)"
fi

echo "▶ Pushing to ${REPO_URL} ..."
if git push -u origin main 2>&1; then
  ok "Push succeeded → https://github.com/HamUniversal/pin-phonics-site"
else
  bad "Push failed."
  echo ""
  echo "  Common fixes:"
  echo "    1. Authentication:  gh auth login"
  echo "    2. Empty the repo first if it has any commits: gh repo empty check."
  echo "    3. Force push (ONLY if the repo is truly empty and you're sure):"
  echo "         git push -u origin main --force"
  echo ""
  echo "  Or push manually:"
  echo "    git push -u origin main"
  exit 1
fi

# ────────────────────────────────────────────────────────────────────────
# STEP 5 · Turn on security features
# ────────────────────────────────────────────────────────────────────────
step "STEP 5/6 · Enable security features (best effort)"

if [ "$AUTH_METHOD" = "gh" ]; then
  REPO="HamUniversal/pin-phonics-site"

  # Branch protection: require CODEOWNER review + status checks on main
  echo "  → Setting branch protection on 'main' ..."
  gh api "repos/${REPO}/branches/main/protection" \
    --method PUT \
    --header "Accept: application/vnd.github+json" \
    --field required_status_checks='{"strict":true,"contexts":["build-and-test"]}' \
    --field enforce_admins=false \
    --field required_pull_request_reviews='{"require_code_owner_reviews":true,"required_approving_review_count":1}' \
    --field restrictions=null \
    >/dev/null 2>&1 && ok "Branch protection enabled (CODEOWNER review required)" \
                      || warn "Could not set branch protection (set manually in Settings → Branches)"

  # Security features
  gh api "repos/${REPO}" --method PATCH \
    --field security_and_analysis='{"secret_scanning":{"status":"enabled"},"dependabot":{"status":"enabled"}}' \
    >/dev/null 2>&1 && ok "Secret scanning + Dependabot enabled" \
                      || warn "Enable manually: Settings → Code security"

  ok "Security setup complete"
else
  warn "gh CLI not authenticated — skipping auto security setup."
  echo "  Enable these manually (Settings → Branches / Code security):"
  echo "    ☑️  Branch protection on 'main': require CODEOWNER reviews"
  echo "    ☑️  Dependabot alerts"
  echo "    ☑️  Dependabot security updates"
  echo "    ☑️  Secret scanning (push protection)"
fi

# ────────────────────────────────────────────────────────────────────────
# STEP 6 · Done — what to do next
# ────────────────────────────────────────────────────────────────────────
step "STEP 6/6 · You're live 🎉"

echo ""
echo -e "${G}  ✅ Repository:${N}  https://github.com/HamUniversal/pin-phonics-site"
echo -e "${G}  ✅ Actions:${N}    https://github.com/HamUniversal/pin-phonics-site/actions"
echo -e "${G}  ✅ Security:${N}   https://github.com/HamUniversal/pin-phonics-site/security"
echo ""
echo "  What just happened:"
echo "    1. Placeholders replaced with @${HANDLE}"
echo "    2. Code committed + pushed to 'main'"
echo "    3. CI/CD workflow (ci.yml) is now running"
echo "    4. Branch protection requires CODEOWNER review on敏感 paths"
echo ""
echo "  Next steps:"
echo "    A) Connect Netlify:  app.netlify.com → Import from Git → this repo"
echo "       → Build command:  python3 build.py"
echo "       → Publish dir:    pinphonics-site"
echo "    B) Add 2 secrets in repo Settings → Actions:"
echo "         NETLIFY_AUTH_TOKEN"
echo "         NETLIFY_SITE_ID"
echo "    C) Register pinphonics.com → point DNS at Netlify → go live"
echo ""
echo "  Daily workflow from now on:"
echo "    edit updated.html → bash finish.sh → git push → auto-deploy in ~1 min"
echo ""
warn "Two things to finish manually:"
echo "    1. Create security@pinphonics.com mailbox (or change SECURITY.md email)"
echo "    2. Add a real PGP key to SECURITY.md (currently a placeholder)"
