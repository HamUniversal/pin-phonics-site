#!/usr/bin/env bash
# test_setup.sh — verify setup-github.sh's replacement logic without pushing.
#
# Strategy: copy CODEOWNERS + SECURITY.md to a temp dir, run the SAME sed
# commands the real script uses, then assert the result. The real source files
# are NEVER modified by this test.
set -e
cd "$(dirname "$0")"

TMP=$(mktemp -d)
cp CODEOWNERS SECURITY.md "$TMP/"
HANDLE="TestHandle"
EMAIL="test@pinphonics.com"

# --- exact logic copied from setup-github.sh (keep in sync) -----------------
replace() {
  local file="$1"
  sed -i.bak \
    -e "s|@pinphonics-owner|@${HANDLE}|g" \
    -e "s|@pinphonics-security|@${HANDLE}|g" \
    -e "s|@pinphonics-maintainers|@${HANDLE}|g" \
    "$file"
  rm -f "${file}.bak"
}
replace "$TMP/CODEOWNERS"
replace "$TMP/SECURITY.md"
sed -i.bak "s|SECURITY_EMAIL_PLACEHOLDER|${EMAIL}|g" "$TMP/SECURITY.md"
rm -f "$TMP/SECURITY.md.bak"
# ---------------------------------------------------------------------------

G='\033[0;32m'; R='\033[0;31m'; N='\033[0m'
pass=0; fail=0
check() {
  if eval "$2" >/dev/null 2>&1; then
    echo -e "  ${G}✅${N} $1"; pass=$((pass+1))
  else
    echo -e "  ${R}❌${N} $1"; fail=$((fail+1))
  fi
}

echo "Validating replacement logic..."
check "CODEOWNERS: all 3 placeholders replaced" \
  "[ \"\$(grep -c @pinphonics- \"$TMP/CODEOWNERS\")\" = \"0\" ] && [ \"\$(grep -c @TestHandle \"$TMP/CODEOWNERS\")\" -ge 35 ]"
check "CODEOWNERS: no @pinphonics-owner remains" \
  "[ \"\$(grep -c @pinphonics-owner \"$TMP/CODEOWNERS\")\" = \"0\" ]"
check "CODEOWNERS: no @pinphonics-security remains" \
  "[ \"\$(grep -c @pinphonics-security \"$TMP/CODEOWNERS\")\" = \"0\" ]"
check "CODEOWNERS: no @pinphonics-maintainers remains" \
  "[ \"\$(grep -c @pinphonics-maintainers \"$TMP/CODEOWNERS\")\" = \"0\" ]"
check "CODEOWNERS: @TestHandle appears 36+ times" \
  "[ \"\$(grep -c @TestHandle \"$TMP/CODEOWNERS\")\" -ge 36 ]"
check "SECURITY.md: placeholder email fully replaced (0 remain)" \
  "[ \"\$(grep -c SECURITY_EMAIL_PLACEHOLDER \"$TMP/SECURITY.md\")\" = \"0\" ]"
check "SECURITY.md: real email present (line 26)" \
  "grep -q 'test@pinphonics.com' \"$TMP/SECURITY.md\""
check "Original source files untouched" \
  "[ \"\$(grep -c @pinphonics-owner CODEOWNERS)\" -ge 1 ] && [ \"\$(grep -c SECURITY_EMAIL_PLACEHOLDER SECURITY.md)\" -ge 1 ]"

rm -rf "$TMP"
echo ""
echo "  passed: $pass    failed: $fail"
[ "$fail" = "0" ]
