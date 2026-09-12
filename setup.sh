#!/usr/bin/env bash
# setup.sh — prepare the local environment for development.
#
# Installs the optional Node backend dependencies (only needed if you plan to
# run server.js for server-side Mailchimp / Gumroad webhooks). The Python build
# and test tooling uses only the standard library, so no pip install is required.
set -e
cd "$(dirname "$0")"

if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "Installing Node dependencies (server.js)..."
    npm install
  else
    echo "npm not found — skipping Node setup. The Python build/test pipeline"
    echo "does not require Node. Install it later if you enable server.js."
  fi
else
  echo "No package.json found — nothing to install."
fi

echo ""
echo "Python build & test tools need no installation (standard library only)."
echo "Quick check:"
python3 -c "print('  python3 ok')" 2>&1 || echo "  python3 not available"
