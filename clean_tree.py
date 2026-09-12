#!/usr/bin/env python3
"""Reset the project to a clean state before a fresh finalize run."""
import os, shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))

shutil.rmtree("pinphonics-site", ignore_errors=True)
shutil.rmtree("__pycache__", ignore_errors=True)

for f in ("pinphonics-complete.zip", "pinphonics-site-deploy.zip"):
    try: os.remove(f)
    except FileNotFoundError: pass

# Research artefacts that shouldn't ship in the final zip
shutil.rmtree("dr:174063", ignore_errors=True)

for f in ("gitignore", "CLEANUP.py", "init_git.sh"):
    try: os.remove(f)
    except FileNotFoundError: pass

print("✅ tree cleaned — run:  bash finalize.sh")
