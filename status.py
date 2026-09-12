#!/usr/bin/env python3
"""status.py — instant project health check (no build, no server).

Run anytime to see the current state:
    python3 status.py
"""
import os, sys, json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

ESSENTIAL = [
    "updated.html", "build.py", "finish.py", "serve.py", "server.js",
    "validate_config.py", "final_check.py", "test_backend.py",
    "pack_site.py", "pack.py", "config.example.js", "package.json",
    ".gitignore", ".github/workflows/ci.yml", "README.md", "REDEPLOY.md",
    "PROJECT_MAP.md", "BACKEND_INTEGRATION.md", "GITHUB_QUICKSTART.md",
    "DEPLOY_AND_DOMAIN_GUIDE.md", "finish.sh",
]
OPTIONAL = ["config.js", "pinphonics-site-deploy.zip", "pinphonics-complete.zip"]
GUIDES = [f for f in ESSENTIAL if f.endswith(".md")]

print("=" * 56)
print("  Pin Phonics — Project Status")
print("=" * 56)

missing = [f for f in ESSENTIAL if not os.path.exists(f)]
for f in ESSENTIAL:
    mark = "✅" if os.path.exists(f) else "❌ MISSING"
    print(f"  {mark} {f}")

print()
print("  Artifacts:")
for f in OPTIONAL:
    if os.path.exists(f):
        print(f"    ✅ {f}  ({os.path.getsize(f)/1024/1024:.1f} MB)")
    else:
        print(f"    ⚪ {f}  (not generated yet)")

print()
print("  Documentation guides:")
for f in GUIDES:
    if os.path.exists(f):
        print(f"    📖 {f}")

print()
if missing:
    print(f"  ❌ {len(missing)} essential file(s) missing: {missing}")
    print("     Run:  python3 finish.py")
    sys_exit = True
else:
    print("  ✅ All essential files present")
    sys_exit = False

# config.js status
if os.path.exists("config.js"):
    print("  ✅ config.js present (gitignored, holds real keys)")
else:
    print("  ⚪ config.js not created yet — copy config.example.js → config.js")

# build output
if os.path.exists("pinphonics-site/index.html"):
    sz = os.path.getsize("pinphonics-site/index.html")
    print(f"  ✅ Build output: pinphonics-site/index.html ({sz/1024/1024:.1f} MB)")
else:
    print("  ⚪ Not built yet — run:  python3 finish.py")

print()
print("  Next:  bash finish.sh    (clean → build → test → pack → done)")
if sys_exit:
    sys.exit(1)
