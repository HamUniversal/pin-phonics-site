#!/usr/bin/env python3
"""Validate config.js / config.example.js structure (key presence + basic shape).

Runs at build time so a typo in config.js fails the build instead of failing
silently in the browser at runtime.

Usage:  python3 validate_config.py [path/to/config.js]
        python3 -c "import validate_config; validate_config.validate('config.js')"
"""
import os, re, sys

DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.example.js")


def validate(path=None):
    """Validate a config file. Returns True on success, raises SystemExit on failure."""
    target = path or DEFAULT
    if not os.path.exists(target):
        print(f"⚠️  {target} not found — skipping config validation")
        return False

    src = open(target, encoding="utf-8").read()
    errors = []

    # 1. Required top-level keys
    for key in ("MAILCHIMP", "GUMROAD", "STRIPE"):
        if f"{key}:" not in src and f"{key} :" not in src:
            errors.append(f"missing top-level key: {key}")

    # 2. MAILCHIMP.url should be present (URL or demo placeholder)
    m = re.search(r"MAILCHIMP:\s*\{(.*?)\}", src, re.S)
    if m:
        block = m.group(1)
        if "url:" not in block and '"url"' not in block:
            errors.append("MAILCHIMP.url missing")
        elif "httpbin" not in block and "http" not in block and "LIST-MANAGE" not in block:
            print("  ℹ️  MAILCHIMP.url is neither the demo (httpbin) nor an obvious Mailchimp URL — verify manually")

    # 3. GUMROAD.paymentLink should be present
    g = re.search(r"GUMROAD:\s*\{(.*?)\}", src, re.S)
    if g and "paymentLink:" not in g.group(1):
        errors.append("GUMROAD.paymentLink missing")

    if errors:
        print(f"❌ {target} validation FAILED:")
        for e in errors: print(f"   • {e}")
        sys.exit(1)

    print(f"✅ {target} — structure valid (MAILCHIMP / GUMROAD / STRIPE all present)")
    return True


if __name__ == "__main__":
    validate(sys.argv[1] if len(sys.argv) > 1 else None)
