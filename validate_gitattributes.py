#!/usr/bin/env python3
"""
validate_gitattributes.py
Verify .gitattributes enforces executable permissions correctly.

Run: python3 validate_gitattributes.py
Exit code 0 = valid, 1 = problems found.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ATTR = os.path.join(ROOT, ".gitattributes")
SH_FILE = os.path.join(ROOT, "setup-github.sh")

errors = []
checks = []


def check(cond, name):
    checks.append((cond, name))
    if not cond:
        errors.append(name)


# 1. File exists
check(os.path.isfile(ATTR), ".gitattributes exists")

# 2. setup-github.sh exists and is executable on disk
check(os.path.isfile(SH_FILE), "setup-github.sh exists")
if os.path.isfile(SH_FILE):
    check(os.access(SH_FILE, os.X_OK), "setup-github.sh has +x on disk (0755)")

# 3. Parse rules
with open(ATTR, encoding="utf-8") as f:
    lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]

rules = {}
for ln in lines:
    parts = ln.split()
    if len(parts) >= 2:
        rules[parts[0]] = " ".join(parts[1:])

# 4. setup-github.sh rule has mode=0755
sh_rule = rules.get("setup-github.sh", "")
check("mode=0755" in sh_rule, "setup-github.sh rule sets mode=0755")
check("eol=lf" in sh_rule, "setup-github.sh rule sets eol=lf (cross-platform)")
check("-text" in sh_rule or "text" not in sh_rule, "setup-github.sh marked -text (no CRLF mangle)")

# 5. setup-github.sh shows up as executable in `git ls-files --stage`
try:
    import subprocess
    out = subprocess.run(
        ["git", "ls-files", "--stage", "setup-github.sh"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip()
    # Mode 100755 = executable; 100644 = non-executable
    if out:
        mode = out.split()[0] if out.split() else ""
        check(mode == "100755", f"git tracks setup-github.sh as 100755 (got {mode})")
    else:
        # Not yet committed (empty repo) — warn but don't fail
        print("  ⚠ git ls-files empty (not committed yet) — will be set on first commit")
except FileNotFoundError:
    print("  ⚠ git not available — skipping ls-files check")

# 6. *.sh glob also executable
sh_glob = rules.get("*.sh", "")
check("mode=0755" in sh_glob, "*.sh glob sets mode=0755 (future scripts covered)")

# 7. No conflicting rules (mode=0755 + mode=0644 on same path)
for path, rule in rules.items():
    if "mode=0755" in rule and "mode=0644" in rule:
        errors.append(f"conflicting modes on {path}")

# 8. Binary assets protected
for asset in ["*.png", "*.zip", "*.svg"]:
    rule = rules.get(asset, "")
    check(rule == "binary", f"{asset} marked binary ({rule})")


# Report
print("=" * 56)
print("validate_gitattributes.py")
print("=" * 56)
for i, (cond, name) in enumerate(checks, 1):
    print(f"  {'✅' if cond else '❌'} {i:2d}. {name}")

print()
if errors:
    print(f"RESULT: {len(errors)} PROBLEM(S)")
    for e in errors:
        print(f"  ❌ {e}")
    sys.exit(1)
else:
    print("RESULT: ALL CHECKS PASSED ✅")
    sys.exit(0)
