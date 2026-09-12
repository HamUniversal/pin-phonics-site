#!/usr/bin/env python3
"""Package the built static site into a clean zip for deployment.

Produces: pinphonics-site-deploy.zip
Contains: index.html + hosting configs (netlify.toml, vercel.json, _redirects,
          200.html, source-original.html, LAUNCH.txt)

Usage:
  python3 build.py            # ensure pinphonics-site/ is fresh
  python3 pack_site.py        # creates the deploy zip
  # Then: drag the zip contents into app.netlify.com/drop
"""
import os, zipfile, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "pinphonics-site")
OUT  = os.path.join(ROOT, "pinphonics-site-deploy.zip")

assert os.path.isdir(SRC), f"No build output at {SRC} — run build.py first"
launch = os.path.join(SRC, "LAUNCH.txt")
if not os.path.exists(launch):
    # build.py normally copies LAUNCH.txt in; fall back to a direct copy so
    # pack never fails even if the build step was skipped.
    src = os.path.join(ROOT, "LAUNCH.txt")
    if os.path.exists(src):
        shutil.copy(src, launch)

# Only ship the files that belong on a static host
KEEP = {"index.html", "200.html", "_redirects", "netlify.toml",
        "vercel.json", "source-original.html", "LAUNCH.txt"}

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(SRC)):
        if fn in KEEP:
            z.write(os.path.join(SRC, fn), arcname=fn)

size = os.path.getsize(OUT)
print(f"✅ {OUT}  ({size:,} bytes, {size/1024:.1f} KB)")
print("📦 Ready to deploy — unzip and:")
print("   • Netlify Drop:  app.netlify.com/drop  (drag the folder)")
print("   • Vercel:        vercel deploy --prod")
print("   • Cloudflare:    wrangler pages publish pinphonics-site")
print("   • GitHub Actions: push to main (see GITHUB_QUICKSTART.md)")
print("   Launch guide inside the zip:  LAUNCH.txt")
