#!/usr/bin/env python3
"""Final all-in-one verification.

Spawns serve.py as a clean child process, reads the EXACT URL it prints on
startup (it may fall back to 4174–4177 if 4173 is busy), hits every endpoint,
runs the full test suite, validates the bundle, then stops the server.

Exits 0 only if EVERY check passes.

Usage:  python3 final_check.py
"""
import os, sys, json, re, time, subprocess, urllib.request, urllib.error

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

PASS, FAIL = [], []

def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name}{(' — ' + detail) if detail else ''}")

# ---- 0. Kill any leftover server -------------------------------------------
subprocess.run("pkill -9 -f serve.py 2>/dev/null; true", shell=True)
time.sleep(1)

# ---- 1. Build ---------------------------------------------------------------
print("\n[1/6] Build")
import build
check("build produced pinphonics-site/index.html", os.path.exists("pinphonics-site/index.html"))

# ---- 2. Start server ---------------------------------------------------------
print("\n[2/6] Start serve.py")
proc = subprocess.Popen([sys.executable, "serve.py"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        bufsize=1, text=True)
base = None
# Read startup lines until we see the "Endpoints:" banner (or 3s timeout).
import select
while True:
    ready = select.select([proc.stdout], [], [], 3.0)[0]
    if not ready:
        break  # no more output within 3s → assume startup done
    line = proc.stdout.readline()
    if not line:
        break
    line = line.strip()
    print("     [serve.py]", line)
    m = re.search(r"localhost:(\d{4,5})", line)
    if m:
        base = f"http://127.0.0.1:{m.group(1)}"
    if "Endpoints:" in line or "dev server:" in line.lower():
        break

# No fallback — if serve.py didn't print a URL we treat it as a failure.
up = base is not None
check("server started and printed a URL", up, f"pid={proc.pid} base={base}")
if not up:
    err = proc.stderr.read()
    print("   server stderr:\n", err.decode(errors="ignore")[:600])

def fetch(path, method="GET", body=None):
    req = urllib.request.Request(
        f"{base}{path}", method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"} if body else {})
    try:
        return urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as e:
        return e  # carries .status and .read()

def txt(r):
    try: return r.read().decode("utf-8", "ignore")
    except Exception: return ""

# ---- 3. Endpoints ------------------------------------------------------------
print("\n[3/6] HTTP endpoints")
r = fetch("/"); check("GET /          → 200", r.status == 200, f"{len(r.read()):,} B")
r = fetch("/config.js"); check("GET /config.js → 200", r.status == 200, f"{len(txt(r)):,} B")
r = fetch("/api/config"); cfg = json.loads(txt(r)) if r.status == 200 else {}
check("GET /api/config → 200 + hasMailchimp key", r.status == 200 and "hasMailchimp" in cfg, str(cfg))
r = fetch("/api/signup", "POST", {"email": "parent@example.com", "tags": ["pin-gift"]})
j = json.loads(txt(r)) if r.status == 200 else {}
check("POST /api/signup (valid)   → 200 ok", r.status == 200 and j.get("ok") is True, str(j))
r = fetch("/api/signup", "POST", {"email": "not-an-email"})
check("POST /api/signup (invalid) → 400", r.status == 400, f"status={r.status}")

# ---- 4. test_backend.py ------------------------------------------------------
print("\n[4/6] test_backend.py")
r = subprocess.run([sys.executable, "test_backend.py"], capture_output=True, text=True)
for l in r.stdout.strip().splitlines(): print("     " + l)
check("test_backend.py exits 0", r.returncode == 0)

# ---- 5. Bundle validation ---------------------------------------------------
print("\n[5/6] Bundle validation")
html = open("pinphonics-site/index.html", encoding="utf-8").read()
for n in ['<!DOCTYPE html', 'id="giftForm"', 'data-buy', 'captureEmail',
          'openHandbookCheckout', 'initBackend']:
    check(f"contains {n}", n in html)
# config.js is loaded by serve.py at runtime (gitignored, holds real keys),
# so it must NOT be inlined into the static bundle.
check("config.js NOT inlined into bundle (loaded at runtime)", 'src="config.js"' not in html)
check("no broken ref (e.currentCurrentTarget)", "e.currentCurrentTarget" not in html)
check(">= 6 SVGs", html.count("<svg") >= 6, f"{html.count('<svg')} found")
scripts = "\n".join(re.findall(r"<script>(.*?)</script>", html, re.S))
r = subprocess.run(["node", "--check", "-"], input=scripts, text=True, capture_output=True)
check("all inline JS parses (node --check)", r.returncode == 0, r.stderr.strip() or "ok")

# ---- 6. Repo manifest --------------------------------------------------------
print("\n[6/6] Repo manifest")
expected = ["updated.html", "build.py", "serve.py", "server.js", "config.js",
            "config.example.js", "test_backend.py", "final_check.py",
            "package.json", "README.md", "BACKEND_INTEGRATION.md", "GITHUB_QUICKSTART.md",
            "REDEPLOY.md", "PROJECT_MAP.md", "DEPLOY_AND_DOMAIN_GUIDE.md",
            ".github/workflows/ci.yml", ".gitignore", "setup.sh", "finish.sh"]
for f in expected:
    check(f"present: {f}", os.path.exists(f))
check("config.js is gitignored", "config.js" in open(".gitignore", encoding="utf-8").read())

# ---- Stop --------------------------------------------------------------------
proc.terminate()
try: proc.wait(timeout=3)
except subprocess.TimeoutExpired: proc.kill()
print("\n🛑 server stopped")

# ---- Summary -----------------------------------------------------------------
print("\n" + "=" * 54)
print(f"  PASSED: {len(PASS)}    FAILED: {len(FAIL)}")
print("=" * 54)
if FAIL:
    for f in FAIL: print(f"  ❌ {f}")
    sys.exit(1)
print("  🎉 ALL CHECKS PASSED — ready to push & deploy")
