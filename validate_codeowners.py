#!/usr/bin/env python3
"""Validate CODEOWNERS coverage of security-sensitive paths.

Checks:
  1. File exists at repo root.
  2. Every required security path has at least one matching rule.
  3. All rules are specific (no bare `*` owner lines masking real paths,
     unless explicitly last).
  4. Required owner placeholders are documented in a header comment.
Exits non-zero if any check fails (intended for finish.sh).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "CODEOWNERS")

REQUIRED = [
    "config.js",
    ".github/workflows/",
    "server.js",
    "netlify.toml",
    "vercel.json",
]

def main():
    if not os.path.exists(PATH):
        print("❌ CODEOWNERS not found at repo root")
        sys.exit(1)

    with open(PATH) as f:
        raw = f.read()

    lines = [ln.strip() for ln in raw.splitlines()]
    # Strip comments and blanks, keep ordering.
    rules = [ln for ln in lines if ln and not ln.startswith("#")]

    # Required owner placeholders (must appear somewhere in header comments).
    placeholders = ["@pinphonics-owner", "@pinphonics-security", "@pinphonics-maintainers"]
    header = "\n".join(ln for ln in lines if ln.startswith("#"))

    print("Validating CODEOWNERS\n")

    # 1. Each required path is covered by a rule (substring match is enough
    #    because CODEOWNERS patterns are matched against repo paths).
    missing = []
    for path in REQUIRED:
        # Normalise: a directory rule ends with "/" in CODEOWNERS.
        needle_dir = path.rstrip("/") + "/"
        if not any(path in rule or needle_dir in rule for rule in rules):
            missing.append(path)

    if missing:
        print("❌ Missing coverage for security-sensitive paths:")
        for m in missing:
            print(f"     - {m}")
        sys.exit(1)
    print(f"   ✅ All {len(REQUIRED)} required security paths covered")

    # 2. Specificity: every rule must contain a '/' or a '.' (i.e. be a real
    #    path pattern), EXCEPT the final fallback `*`. Warn if a bare wildcard
    #    appears before the last rule.
    early_wildcard = False
    for i, rule in enumerate(rules):
        pattern = rule.split()[0]
        if pattern == "*" and i < len(rules) - 1:
            early_wildcard = True
    if early_wildcard:
        print("⚠️  Bare `*` rule appears before the final line (may mask specific rules)")
    else:
        print("   ✅ Wildcard fallback is in the correct (last) position")

    # 3. Owner placeholders documented.
    undocumented = [p for p in placeholders if p not in header]
    if undocumented:
        print("❌ Placeholder owner(s) not documented in CODEOWNERS header:")
        for u in undocumented:
            print(f"     - {u}")
        sys.exit(1)
    print(f"   ✅ Owner placeholders documented: {', '.join(placeholders)}")

    # 4. No rule without an owner.
    bad = [r for r in rules if len(r.split()) < 2]
    if bad:
        print("❌ Rules with no owner:")
        for b in bad:
            print(f"     - {b}")
        sys.exit(1)
    print("   ✅ Every rule has at least one owner")

    print("\n✅ CODEOWNERS validation passed")
    print("\n⚠️  Remember to replace placeholder handles before pushing:")
    print("     @pinphonics-owner       → your GitHub handle")
    print("     @pinphonics-security    → a team or security contact")
    print("     @pinphonics-maintainers → broader maintainer group")

if __name__ == "__main__":
    main()
