#!/usr/bin/env bash
# finish.sh — one command to end the process.
#   bash finish.sh    →  clean → build → full e2e check → pack both zips → verify
set -e
cd "$(dirname "$0")"

G='\033[0;32m'; B='\033[0;34m'; R='\033[0;31m'; N='\033[0m'
step() { echo -e "\n${B}▶ $*${N}"; }
ok()   { echo -e "  ${G}✅ $*${N}"; }
bad()  { echo -e "  ${R}❌ $*${N}"; }

step "1/8 · Clean tree + kill stragglers"
pkill -9 -f serve.py 2>/dev/null || true
sleep 1
[ -f clean_tree.py ] && python3 clean_tree.py || echo "  (clean_tree.py absent — skipping)"
ok "tree ready"

step "2/8 · Validate config + build"
python3 validate_config.py config.example.js
python3 build.py

step "3/8 · Validate GitHub Actions workflow + CODEOWNERS + .gitattributes"
if [ -f validate_workflow.py ]; then
  python3 validate_workflow.py
  ok "ci.yml structure valid"
else
  echo "  (validate_workflow.py absent — skipping)"
fi
if [ -f validate_codeowners.py ]; then
  python3 validate_codeowners.py
  ok "CODEOWNERS security paths covered"
else
  echo "  (validate_codeowners.py absent — skipping)"
fi
if [ -f validate_gitattributes.py ]; then
  python3 validate_gitattributes.py
  ok ".gitattributes enforces +x on setup-github.sh"
else
  echo "  (validate_gitattributes.py absent — skipping)"
fi

step "4/8 · Full e2e verification (38 checks)"
python3 final_check.py

step "5/8 · Pack deploy bundle"
python3 pack_site.py

step "6/8 · Pack complete project"
python3 pack.py

step "7/8 · Verify .gitattributes is included in complete zip"
python3 -c "
import zipfile, sys
z = zipfile.ZipFile('pinphonics-complete.zip')
names = z.namelist()
need = ['.gitattributes', 'validate_gitattributes.py']
missing = [n for n in need if n not in names]
if missing:
    print('  ❌ missing from zip:', missing); sys.exit(1)
print('  ✅ .gitattributes + validate_gitattributes.py present in complete zip')
"

step "8/8 · Verify release artifacts"
DEPLY_OK=false; FULL_OK=false
[ -f pinphonics-site-deploy.zip ] && [ "$(stat -c%s pinphonics-site-deploy.zip)" -gt 1000000 ] && DEPLY_OK=true
[ -f pinphonics-complete.zip ]   && [ "$(stat -c%s pinphonics-complete.zip)"   -gt 1000000 ] && FULL_OK=true
$DEPLY_OK && ok "pinphonics-site-deploy.zip present & ≥1MB" || { bad "deploy zip missing or too small"; exit 1; }
$FULL_OK && ok "pinphonics-complete.zip present & ≥1MB"     || { bad "complete zip missing or too small"; exit 1; }

echo ""
echo -e "${G}================================================================${N}"
echo -e "${G}  🎉  PROCESS FINISHED — READY TO SHIP${N}"
echo -e "${G}================================================================${N}"
for f in pinphonics-site-deploy.zip pinphonics-complete.zip; do
  echo -e "  ${G}✅${N} $f  ($(du -h "$f" | cut -f1))"
done
echo ""
echo "  ➤ git push  (GitHub Actions → ci.yml → Netlify auto-deploy in ~1 min)"
echo "  ➤ Or: upload pinphonics-site-deploy.zip to app.netlify.com/drop  (instant HTTPS)"
echo "  ➤ Then: register pinphonics.com → point DNS → go live"
echo ""
echo "  Repo guide: GITHUB_GUIDE.md    ·    Layout: PROJECT_MAP.md"
