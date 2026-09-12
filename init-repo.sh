#!/usr/bin/env bash
# init-repo.sh — initialize a fresh git repo, commit everything, and push to GitHub.
#
# Usage:
#   ./init-repo.sh                                    # prompts for the repo URL
#   ./init-repo.sh https://github.com/YOU/pin-phonics-site.git
#
# Prerequisite: create the (empty) repo once at github.com/new first. This script
# cannot create the GitHub repo for you (no authenticated API call), but it does
# everything else and waits for you to paste the URL if you forget.
set -e
cd "$(dirname "$0")"

REMOTE="${1:-}"
if [ -z "$REMOTE" ]; then
  echo -n "Paste your GitHub repo URL (https://github.com/.../pin-phonics-site.git): "
  read -r REMOTE
fi

if [ -z "$REMOTE" ]; then
  echo "ERROR: no remote URL given."
  echo "  1) Create the repo at github.com/new (name: pin-phonics-site, leave empty)."
  echo "  2) Re-run:  ./init-repo.sh <YOUR_GITHUB_REPO_URL>"
  exit 1
fi

if [ -d .git ]; then
  echo "ERROR: .git already exists. Current remotes:"
  git remote -v
  echo ""
  echo "This script is for a fresh init. To re-wire, run:"
  echo "  git remote set-url origin <NEW_URL>"
  echo "or:"
  echo "  rm -rf .git && ./init-repo.sh"
  exit 1
fi

echo "▶ Initializing git repo..."
git init -b main >/dev/null
git add .

echo ""
echo "Files to be committed (config.js and *.zip are gitignored):"
git status --short
echo ""

git commit -m "Initial commit: Pin Phonics site + CI/CD auto-deploy pipeline" >/dev/null

git remote add origin "$REMOTE"
git branch -M main

echo "▶ Pushing to $REMOTE ..."
echo "  (first push may prompt you to log in / authenticate)"
if git push -u origin main; then
  echo ""
  echo "OK  Push succeeded."
  echo "  Watch the first deploy at: ${REMOTE%.git}/actions"
else
  echo ""
  echo "WARN Push failed. Common causes:"
  echo "   1) Repo does not exist yet at $REMOTE"
  echo "      -> Create it at github.com/new (leave empty), then re-run this script."
  echo "   2) Authentication failed"
  echo "      -> Run:  gh auth login   (install gh CLI first if needed)"
  echo "      or push over SSH instead:  git remote set-url origin git@github.com:YOU/pin-phonics-site.git"
  echo ""
  echo "The commit is saved locally. Fix the remote and run:"
  echo "  git push -u origin main"
  exit 1
fi
