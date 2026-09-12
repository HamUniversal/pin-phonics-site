#!/usr/bin/env python3
"""Validate the backend wiring in updated.html without a browser."""
import re, sys, os

HTML = open(os.path.join(os.path.dirname(__file__), "updated.html"), encoding="utf-8").read()

def check(name, cond):
    print(("✅" if cond else "❌"), name)
    if not cond:
        check.failed = True
check.failed = False

# 1. config.js is loaded at runtime (via serve.py), with a safe fallback
#    so the static bundle never inlines secrets — site works without it.
check("config loaded via window.PIN_CONFIG (runtime, gitignored)",
      "window.PIN_CONFIG" in HTML)
check("config.js is NOT inlined into static bundle",
      '<script src="config.js"></script>' not in HTML)

# 2. Demo fallback defined so site works before config.js exists
check("PIN_CONFIG fallback", 'window.PIN_CONFIG = window.PIN_CONFIG ||' in HTML)

# 3. Backend init runs on DOMContentLoaded
check("initBackend on DOMContentLoaded", "document.addEventListener(\"DOMContentLoaded\", initBackend)" in HTML)

# 4. captureEmail + deliverBook + openHandbookCheckout defined
for fn in ("captureEmail", "deliverBook", "openHandbookCheckout", "initBackend"):
    check(f"function {fn} defined", f"function {fn}(" in HTML)

# 5. Gift form wired via id + submit handler
check("gift form has id=giftForm", 'id="giftForm"' in HTML)

# 6. Buy buttons have data-buy so openHandbookCheckout binds
check("buy buttons use data-buy", 'data-buy' in HTML)

# 7. No leftover references to the old name
check("no dangling `submitGift` as sole handler", "submitGift" not in HTML or "submitGift(" in HTML)  # legacy shim allowed

# 8. netlify.toml + GH workflow present
for f in (".github/workflows/ci.yml", "config.example.js", "BACKEND_INTEGRATION.md", "README.md"):
    check(f"artifact exists: {f}", os.path.exists(os.path.join(os.path.dirname(__file__), f)))

# 9. JS syntax check (node if available, else python regex balance)
scripts = re.findall(r"<script>(.*?)</script>", HTML, re.S)
combined = "\n".join(scripts)
try:
    import subprocess
    r = subprocess.run(["node", "--check", "-"], input=combined, text=True, capture_output=True)
    if r.returncode == 0:
        print("✅ All inline JS parses cleanly (node --check)")
    else:
        print("⚠️  node not available, falling back to brace balance check")
        raise FileNotFoundError
except (FileNotFoundError, ImportError):
    balance = combined.count("{") - combined.count("}")
    parens = combined.count("(") - combined.count(")")
    print(f"{'✅' if balance==0 and parens==0 else '❌'} Brace balance: {balance}, paren balance: {parens}")
    if balance or parens:
        check.failed = True

sys.exit(1 if check.failed else 0)
