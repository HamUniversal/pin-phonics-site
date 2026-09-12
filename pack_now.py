#!/usr/bin/env python3
"""Regenerate pinphonics-site-deploy.zip and pinphonics-complete.zip.

Standalone, stdlib-only. Safe to run after a sandbox reset: it never imports
project modules, so a missing clean_tree.py or similar cannot break it.

Prerequisite: pinphonics-site/index.html must exist (run build.py first).
"""
import os
import zipfile
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "pinphonics-site")


def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def main():
    if not os.path.exists(os.path.join(SITE, "index.html")):
        fail("pinphonics-site/index.html missing -- run `python3 build.py` first")

    # Copy LAUNCH.txt into the site folder if build.py didn't already.
    launch_src = os.path.join(ROOT, "LAUNCH.txt")
    launch_dst = os.path.join(SITE, "LAUNCH.txt")
    if os.path.exists(launch_src) and not os.path.exists(launch_dst):
        shutil.copy(launch_src, launch_dst)

    # ---- Deploy zip: only files that belong on a static host. -------------
    keep = {
        "index.html",
        "200.html",
        "_redirects",
        "netlify.toml",
        "vercel.json",
        "source-original.html",
        "LAUNCH.txt",
    }
    deploy_zip = os.path.join(ROOT, "pinphonics-site-deploy.zip")
    with zipfile.ZipFile(deploy_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(SITE)):
            if fn in keep:
                z.write(os.path.join(SITE, fn), arcname=fn)

    # ---- Complete-project zip: whole tree minus build outputs + junk. -------
    # `.github` is explicitly preserved so the CI/CD workflow ships with the repo;
    # other dot-directories (e.g. .git) are still excluded.
    exclude_dirs = {"pinphonics-site", "__pycache__", "node_modules", ".git"}
    preserve_dotdirs = {".github"}
    exclude_files = {"config.js", "pinphonics-complete.zip", "pinphonics-site-deploy.zip"}
    complete_zip = os.path.join(ROOT, "pinphonics-complete.zip")
    with zipfile.ZipFile(complete_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [
                d for d in dirnames
                if d in preserve_dotdirs
                or (d not in exclude_dirs and not d.startswith("."))
            ]
            for fn in sorted(filename for filename in filenames if filename not in exclude_files):
                full = os.path.join(dirpath, fn)
                if os.path.isdir(full):
                    continue
                arc = os.path.relpath(full, ROOT)
                z.write(full, arc)

    # ---- Report -------------------------------------------------------------
    for path in (deploy_zip, complete_zip):
        size = os.path.getsize(path)
        print("OK  " + os.path.basename(path) + "  ({:.1f} MB)".format(size / 1024 / 1024))
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            print("    valid zip: " + str(bad is None) + "  files: " + str(len(z.namelist())))
            for n in sorted(z.namelist()):
                print("     " + n)


if __name__ == "__main__":
    main()
