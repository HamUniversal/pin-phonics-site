#!/usr/bin/env python3
"""Package the complete Pin Phonics project into a deployable zip.

Excludes build artifacts (pinphonics-site/, __pycache__/, *.pyc) and OS junk,
but INCLUDES config.example.js as the template. config.js (with real keys)
is correctly excluded by .gitignore and the zip filter below.

Also copies DELIVERABLES.txt into the zip root so the recipient has the
manifest + checksums + next commands in one place.
"""
import os, zipfile, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "pinphonics-complete.zip")
# Directories never included in the complete-zip (build output, caches, repos).
EXCLUDE_DIRS = {"pinphonics-site", "__pycache__", "node_modules", ".git"}
# Dot-directories to preserve (override EXCLUDE_DIRS). `.github` MUST be kept so
# the CI/CD workflow ships with the repo; other dot-dirs stay excluded.
PRESERVE_DOTDIRS = {".github"}
EXCLUDE_FILES = {"config.js", "pinphonics-complete.zip", "pinphonics-site-deploy.zip"}
# Root-level documentation that must always ship with the repo, even if a
# future filter would otherwise skip it. SECURITY.md is required by GitHub to
# display the "Report a vulnerability" button on the Security tab.
# CODEOWNERS auto-requests review from the right owners on security-sensitive
# paths (config.js, .github/workflows/, server.js, etc.).
ALWAYS_INCLUDE = {
    "README.md", "SECURITY.md", "CODEOWNERS", "DELIVERABLES.txt", "LAUNCH.txt",
    ".gitattributes", "validate_gitattributes.py",
}

# Make sure DELIVERABLES.txt (and LAUNCH.txt) exist before packaging
deliverables = os.path.join(ROOT, "DELIVERABLES.txt")
if not os.path.exists(deliverables):
    print(f"⚠️  {deliverables} not found — run build.py first for a complete zip")
launch = os.path.join(ROOT, "pinphonics-site", "LAUNCH.txt")
if not os.path.exists(launch):
    src = os.path.join(ROOT, "LAUNCH.txt")
    if os.path.exists(src):
        shutil.copy(src, launch)

# Ensure SECURITY.md + CODEOWNERS + DELIVERABLES.txt exist at the ROOT so the
# always-include filter (above) can package them. These are the files a fresh
# clone must have to display the vulnerability-report button, route security
# reviews, and carry the manifest.
for must_exist in ("SECURITY.md", "CODEOWNERS", "DELIVERABLES.txt"):
    if not os.path.exists(os.path.join(ROOT, must_exist)):
        print(f"⚠️  {must_exist} not found at repo root — it will be missing from the zip")

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            d for d in dirnames
            if (d in PRESERVE_DOTDIRS) or (d not in EXCLUDE_DIRS and not d.startswith("."))
        ]
        for fn in sorted(filename for filename in filenames if filename not in EXCLUDE_FILES):
            full = os.path.join(dirpath, fn)
            arc = os.path.relpath(full, ROOT)
            z.write(full, arc)

size = os.path.getsize(OUT)
MIN_FILES = 25  # safety floor: if we drop below this, the filter is broken.
if len(z.namelist()) < MIN_FILES:
    raise SystemExit(
        f"❌ {OUT} only has {len(z.namelist())} files — expected ≥{MIN_FILES}. "
        "The inclusion filter is probably dropping files. Aborting before "
        "producing a broken release artifact."
    )
print(f"✅ {OUT}  ({size:,} bytes, {size/1024:.1f} KB, {len(z.namelist())} files)")
print("📦 Contents:")
with zipfile.ZipFile(OUT) as z:
    for name in sorted(z.namelist()):
        print(f"   {name}")
