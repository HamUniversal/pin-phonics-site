# 🔌 Backend Integration — Pin Phonics

> **Headline:** the site runs **100% client-side**. No server is required to go
> live. Mailchimp (email) and Gumroad/Stripe (payments) both work from the
> browser via public-safe URLs. The Node server below is **optional** — only if
> you want to keep the Mailchimp API key secret or self-fulfill the PDF.

## Architecture (what's wired today)

```
┌──────────────┐   submit email    ┌────────────────────┐
│  Gift modal  │ ────────────────▶ │  Mailchimp audience │
│  (#giftForm) │   (embedded-form  │  (captures leads)   │
└──────────────┘    URL, public)   └────────────────────┘
        │
        │ on success → deliverBook() opens the 3D Aesop fable (client-side)
        ▼
┌──────────────┐   click "Buy"     ┌────────────────────┐
│  Buy buttons  │ ───────────────▶ │  Gumroad product    │
│  (data-buy)  │   (payment link) │  (hosts PDF + emails │
└──────────────┘                   │   download)         │
                                    └────────────────────┘
```

**All configuration lives in `config.js`** (gitignored). The site defines a safe
fallback (`window.PIN_CONFIG`) so it **never breaks** — in demo mode, emails log
to the browser console and the buy button just scrolls to the purchase section.

## Step 1 — Copy & fill `config.js`

```bash
cp config.example.js config.js
```

```js
// config.js  (NEVER commit — see .gitignore)
window.PIN_CONFIG = {
  MAILCHIMP: {
    // PUBLIC-safe: Mailchimp → Audience → Signup forms → Embedded forms → copy `action=`
    url: "https://YOUR_DC_LIST-MANAGE.COM/subscribe/post?u=XXX&id=YYY"
  },
  GUMROAD: {
    // Gumroad → New product "Pin Phonics Handbook" ($29) → Share → Short URL
    paymentLink: "https://gumroad.com/l/YOUR_SHORTCODE"
  },
  STRIPE: {
    // OR use a Stripe Payment Link (Dashboard → Payment Links). Leave empty if using Gumroad.
    paymentLink: ""
  }
};
```

| Service | Free tier | What to create | Where to find the value |
|---------|-----------|----------------|-------------------------|
| **Mailchimp** | 500 contacts | Audience → Signup forms → Embedded form | The form's `action=` URL |
| **Gumroad** | Free (payments only) | Product "Pin Phonics Handbook" $29 | Product → Share → Short URL |
| **Stripe** (alt) | 2.9%+30¢/sale | Payment Link | Dashboard → Payment Links |

## Step 2 — Test locally

```bash
python3 serve.py        # serves site + config.js at http://localhost:4173
# In another terminal:
curl -X POST http://localhost:4173/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","tags":["pin-gift"]}'
# → {"ok":true,"email":"test@example.com","mode":"dev"}
```

With demo `config.js` values, submitting the gift form prints to the browser
console instead of hitting the network — so you can develop offline.

## Step 3 (optional) — Run the Node server for secret-safe fulfillment

Only if you **don't** want to use Mailchimp's public embedded-form URL:

```bash
npm init -y
npm install express mailchimp-api-v3 cors body-parser
MAILCHIMP_KEY=sk_xxx MAILCHIMP_LIST_ID=yyy node server.js
```

Then point `config.js → MAILCHIMP.url` at `https://your-domain/api/signup`.
`server.js` handles adding to Mailchimp server-side (key stays secret) and can
receive Gumroad purchase webhooks to self-fulfill the PDF.

## Security notes ⚠️

- **`config.js` is public** (loaded by the browser). Never put a Mailchimp
  **API key** there — use the **embedded-form URL** instead. That's why the
  client-side path is the recommended default.
- For Stripe, always use **Stripe Payment Links** (client-safe), NOT the API.
- Real PDF fulfillment (sending the handbook) is handled by **Gumroad** — no
  server, no storage, no deliverability headaches.
- `config.js` is in `.gitignore`. **Never commit it.** `config.example.js` is
  the committed template with safe demo values.
