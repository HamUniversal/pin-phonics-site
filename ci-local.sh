#!/usr/bin/env bash
# ci-local.sh — run the same pipeline GitHub Actions will run, locally.
#
# Mirrors .github/workflows/ci.yml exactly:
#   build -> verify (38 checks) -> serve.py smoke test -> validate workflow
#
# Usage:  ./ci-local.sh
set -e
cd "$(dirname "$0")"

G='\033[0;32m'; B='\033[0;34m'; R='\033[0;31m'; N='\033[0m'
step() { echo -e "\n${B}▶ $*${N}"; }
ok()   { echo -e "  ${G}✅ $*${N}"; }

pkill -9 -f serve.py 2>/dev/null || true
sleep 1

step "1/4 · Build site (build.py)"
python3 build.py

step "2/4 · Full verification suite (38 checks)"
python3 final_check.py

step "3/4 · Smoke-test dev server"
python3 serve.py >/tmp/srv.log 2>&1 &
sleep 3
curl -s -o /dev/null -w "  GET /          -> %{http_code}\n" http://127.0.0.1:4173/
curl -s -o /dev/null -w "  GET /config.js -> %{http_code}\n" http://127.0.0.1:4173/config.js
curl -s -X POST http://127.0.0.1:4173/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"local-ci@example.com","tags":["local"]}' \
  -w "  POST /api/signup -> %{http_code}\n"
pkill -f serve.py || true

step "4/4 · Validate workflow"
python3 validate_workflow.py

echo ""
echo -e "${G}================================================================${N}"
echo -e "${G}  🎉  LOCAL CI PASSED — safe to push (git push = auto-deploy)${N}"
echo -e "${G}================================================================${N}"
