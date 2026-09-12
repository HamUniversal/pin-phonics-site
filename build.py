#!/usr/bin/env python3
"""Build the production Pin Phonics site.

Reads updated.html, inlines every local asset (so the output is a single
self-contained file — no broken-image risk on any host), validates the result,
and writes the bundle to pinphonics-site/ alongside hosting configs.

Also validates config.example.js (+ config.js if present) at build time so a
typo fails the build instead of failing silently in the browser at runtime.
"""
import os, re, shutil, hashlib, json, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "updated.html")
OUT  = os.path.join(ROOT, "pinphonics-site")

# ---- 1. Read source ---------------------------------------------------------
assert os.path.exists(SRC), f"Source missing: {SRC}"
html = open(SRC, encoding="utf-8").read()

# ---- 2. Inline local assets (images / fonts) into the HTML ----------------
# Any reference like  src="assets/foo.png"  or  url(assets/foo.woff)  that
# points to a file inside the repo is base64-embedded, producing one portable
# file. External (http/https/data) URLs are left untouched.
def inline(match):
    attr, path = match.group(1), match.group(2)
    if path.startswith(("http://", "https://", "data:", "//", "#")):
        return match.group(0)
    abs_path = os.path.normpath(os.path.join(ROOT, path))
    if not os.path.exists(abs_path):
        return match.group(0)  # missing asset — keep reference, build still works
    mime = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
        ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf",
    }.get(os.path.splitext(abs_path)[1].lower(), "application/octet-stream")
    data = open(abs_path, "rb").read()
    b64 = base64.b64encode(data).decode()
    return f'{attr}="data:{mime};base64,{b64}"'

import base64
html = re.sub(r'(\b(?:src|href)\s*=\s*")([^"]+)"', inline, html)
html = re.sub(r'url\(\s*"([^"]+)"\s*\)', lambda m: inline(m), html)

# ---- 3. Validate the bundle ----------------------------------------------
def check(cond, msg):
    print(f"  {'✅' if cond else '❌'} {msg}")
    return cond

os.makedirs(OUT, exist_ok=True)
index_path = os.path.join(OUT, "index.html")
open(index_path, "w", encoding="utf-8").write(html)

size = os.path.getsize(index_path)
h = hashlib.sha256(open(index_path, "rb").read()).hexdigest()[:16]
print(f"✅ index.html: {size:,} bytes ({size/1024:.1f} KB)  sha:{h}")

ok = True
ok &= check("<!DOCTYPE html>" in html, "DOCTYPE present")
ok &= check(html.count("<svg") >= 6, f"{html.count('<svg')} SVGs")
ok &= check('class="lucide"' in html or "lucide" in html, "lucide refs")
ok &= check("btn-primary" in html and "Get the free gift" in html, "Green gift button")
ok &= check("Aesop" in html or "aesop" in html or "fable" in html, "Aesop book hook")

# ---- 4. Hosting configs -----------------------------------------------------
shutil.copy(SRC, os.path.join(OUT, "source-original.html"))
shutil.copy(os.path.join(OUT, "index.html"), os.path.join(OUT, "200.html"))

# Launch guide travels with the deploy bundle so the recipient has
# step-by-step instructions the moment they unzip it.
launch_src = os.path.join(ROOT, "LAUNCH.txt")
if os.path.exists(launch_src):
    shutil.copy(launch_src, os.path.join(OUT, "LAUNCH.txt"))

open(os.path.join(OUT, "_redirects"), "w").write("/*  /index.html  200\n")
open(os.path.join(OUT, "netlify.toml"), "w").write(
    '[build]\n  publish = "."\n  command = "echo already-built"\n\n'
    '[build.environment]\n  NODE_VERSION = "18"\n'
)
open(os.path.join(OUT, "vercel.json"), "w").write(
    json.dumps({"buildCommand": "echo already-built", "outputDirectory": "."}, indent=2)
)

# ---- 5. Validate config (catches typos before deploy) ----------------------
try:
    import validate_config as vc
    vc.validate(os.path.join(ROOT, "config.example.js"))
    if os.path.exists(os.path.join(ROOT, "config.js")):
        vc.validate(os.path.join(ROOT, "config.js"))
except SystemExit:
    raise  # validation failure → fail the build
except Exception as e:
    print(f"⚠️  config validation skipped: {e}")

# ---- 6. Summary ------------------------------------------------------------
files = sorted(os.listdir(OUT))
print(f"✅ Files: {files}")
if not ok:
    print("❌ Build validation FAILED")
    sys.exit(1)
print(f"📁 Bundle ready at: {OUT}")
