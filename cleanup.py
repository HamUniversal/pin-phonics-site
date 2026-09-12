#!/usr/bin/env python3
"""Remove obsolete test/deploy artifacts. Safe to run anytime.

Keeps the essential tooling:
  build.py · serve.py · server.js · validate_config.py · final_check.py
  test_backend.py · pack.py · pack_site.py · setup.sh · finalize.sh
  config.example.js · package.json · .gitignore · all docs + workflows

Removes (if present):
  baseline.py · probe.py · repro.py · verify.py · test_full.py · test_port_fallback.py
  deploy.py · test_server.py · pack_it.py · test_final.py
  pinphonics-site.zip · pinphonics-site-deploy.zip · pinphonics-complete.zip (recreate with pack scripts)
"""
import os

KEEP = {
    "build.py", "serve.py", "server.js", "validate_config.py", "final_check.py",
    "test_backend.py", "pack.py", "pack_site.py", "setup.sh", "finalize.sh",
    "config.example.js", "config.js", "package.json", ".gitignore", "serve.py",
    "README.md", "REDEPLOY.md", "PROJECT_MAP.md", "BACKEND_INTEGRATION.md",
    "GITHUB_QUICKSTART.md", "DEPLOY_AND_DOMAIN_GUIDE.md",
    "Pin_Domain_Name_Recommendation.md",
    ".github", ".git", "pinphonics-site", "dr:174063", "__pycache__",
}

REMOVE_PATTERNS = (
    "baseline.py", "probe.py", "repro.py", "verify.py", "test_full.py",
    "test_port_fallback.py", "test_server.py", "test_final.py",
    "deploy.py", "pack_it.py",
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Remove scripts
for fn in os.listdir("."):
    if fn in REMOVE_PATTERNS or fn.endswith(".zip") or fn == "init_git.sh":
        if os.path.exists(fn):
            os.remove(fn)
            print(f"🗑️  {fn}")

# Assert keepers survived
missing = [f for f in KEEP if f.endswith((".py", ".sh", ".js", ".json")) and not os.path.exists(f)]
if missing:
    print("⚠️  unexpectedly missing:", missing)
else:
    print("✅ core tooling intact")

# Regenerate the two deliverable zips cleanly
print("\nRegenerating deploy artifacts:")
for script in ("pack_site.py", "pack.py"):
    if os.path.exists(script):
        os.system(f"python3 {script}")
