# Security Policy

## Supported versions

Pin Phonics is a static marketing + handbook site with an optional Node.js
backend (`server.js`) for email capture and fulfilment. We only maintain the
**current `main` branch** -- there are no long-term support releases.

| Version | Supported          | Notes                              |
| ------- | ------------------ | ---------------------------------- |
| main    | :white_check_mark: | Live site, auto-deployed from HEAD |
| older   | :x:                | Not patched; please upgrade       |

## Reporting a vulnerability

**Please do NOT open a public GitHub issue for security problems.**

Report privately via **one** of these routes, in order of preference:

1. **GitHub Security Advisory (preferred)**
   - Go to the repo → **Security** tab → **Report a vulnerability**
   - This opens a private draft advisory visible only to maintainers.
   - GitHub will automatically credit you once the advisory is published.

2. **Email**
   - `jiandaneducation@yahoo.com` (PGP optional; key fingerprint below)
   - If that address is not yet provisioned, fall back to the contact email
     listed in the site footer.

3. **Contact form**
   - The site's contact form accepts encrypted messages; mark the subject
     `[SECURITY]`.

### What to include

A minimal report needs:
- **Affected version / commit** (e.g. `git rev-parse HEAD`)
- **Steps to reproduce** (a short proof-of-concept is ideal)
- **Observed vs. expected behaviour**
- **Suggested severity** (see CVSS v3.1 or just "low/medium/high/critical")

You do NOT need to propose a fix -- but a patch is very welcome.

### PGP key (optional)

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
Comment: Pin Phonics security contact -- replace with a real key before publishing
Comment: Generate with:  gpg --full-generate-key --key-type=ed25519
Version: GnuPG v2

mQENBF...REPLACE_ME...=
-----END PGP PUBLIC KEY BLOCK-----
```

> **Action required before going live:** replace the placeholder block above
> with a real Ed25519 key (`gpg --armor --export <ID>`). Until then, rely on
> the GitHub Security Advisory route (option 1), which needs no key.

## Response timeline

We follow a 7-day first-response / 30-day resolution target:

| Step                       | Target         | What happens                                       |
| -------------------------- | -------------- | -------------------------------------------------- |
| **Acknowledgement**       | **≤ 2 days**   | We confirm receipt and assign a tracking ID.       |
| **Initial triage**         | **≤ 7 days**   | Severity assessed; reporter informed of acceptance.|
| **Fix development**        | **≤ 30 days**  | Patch landed on a private branch + regression test.|
| **Coordinated disclosure** | **≤ 30 days**  | Advisory published; credit given; CVE requested.    |
| **Release**                | Same day       | Tagged release + deployment; dependents notified.  |

Critical issues (active exploitation, data exposure, RCE) jump the queue and
are handled as fast as we can ship, typically within 48 hours.

## Scope

### In scope

- The deployed site at `pinphonics.com` and its staging/preview deployments
- The GitHub Actions workflows in `.github/workflows/`
- `config.js`, `server.js`, and any API endpoints (`/api/signup`, etc.)
- Third-party integrations: **Mailchimp**, **Gumroad**, **Stripe**, **Netlify**
  -- misconfigurations in *our* usage of them (exposed keys, webhook replay,
  etc.)
- Supply-chain: GitHub Actions action versions (monitored by Dependabot)
- DNS / domain takeover risks on `pinphonics.com`

### Out of scope

- **Social engineering** attacks against the maintainers or users.
- Issues requiring physical access or a compromised user account.
- **Self-hosted variants** running modified code.
- **Denial of service** without a demonstrated data-impact component.
- Theoretical weaknesses with no viable exploit path.
- Vulnerabilities in dependencies that have **no available patch** and are
  already tracked by Dependabot / GitHub Advisory Database.

## Dependabot & automated alerts

This repo uses **Dependabot** for GitHub Actions and npm dependency updates
(`.github/dependabot.yml`). Alerts are routed as follows:

| Alert type              | Routed to                                  | Action               |
| ----------------------- | ------------------------------------------ | -------------------- |
| **Critical / High**     | Repository admins (the "admin" team)       | **Same-day** review  |
| **Moderate / Low**      | Repository maintainers                     | **Weekly** triage    |
| **GitHub Actions**      | Admin team (auto-update PR is opened)      | Merge or dismiss     |
| **Private vulnerability**| Security advisory (private, 90-day embargo)| Coordinated disclosure|

To configure recipients in **Settings → Code security and analysis →
Dependabot alerts → Dependabot security updates**, set the notification
**"Security alerts"** option to **"Email each week"** (digest) for routine
issues and **"Email immediately"** for critical/high.

**We DO enable:**
- [x] Dependabot alerts
- [x] Dependabot security updates (auto-PR with patch)
- [x] GitHub Actions update monitoring
- [x] Secret scanning (push protection)
- [x] Code scanning (CodeQL) -- see `.github/workflows/ci.yml`

**We do NOT enable:** automatic merging of security PRs (all require review,
to protect the live `main` branch).

## Safe harbour

We consider security research conducted under this policy to be:

- **Authorised** when it complies with this policy.
- **Legal**, provided it does not exceed the stated scope or cause harm to
  users, data, or service availability.
- **Eligible for a thank-you** (swag or a discount on the handbook) for
  valid, reproducible reports -- at our discretion.

Please:
- Do not access, modify, or delete data that is not your own.
- Do not perform destructive actions (mass deletion, irreversible changes).
- Do not publicly disclose the issue until the coordinated-disclosure period
  ends (or the fix is released, whichever is sooner).

## Recognition

Reporters who follow this policy will be credited in the published security
advisory, unless they request anonymity.

---

**Contact for this policy:** jiandaneducation@yahoo.com (or use the GitHub
Security tab). Last reviewed: 2026-09-12.
