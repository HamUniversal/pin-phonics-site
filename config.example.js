/**
 * Pin Phonics — Site Configuration
 * Copy this file to `config.js` and fill in your real values.
 * `config.js` is gitignored and never committed (see .gitignore).
 *
 * In demo/local mode, leave these as-is — the site will log to console
 * instead of making real network calls, so the build never breaks.
 */
window.PIN_CONFIG = {
  // ---- Email capture (Mailchimp) ---------------------------------
  // Option A (recommended): the embedded-form POST URL — PUBLIC, safe in browser.
  //   Found at: Audience → Signup forms → Embedded forms → copy the `action=` value.
  MAILCHIMP: {
    url: "https://httpbin.org/post",   // <-- replace with your Mailchimp form URL
    // formUrl: "https://YOUR_DOMAIN.LIST-MANAGE.COM/subscribe/post?u=XXX&id=YYY"
  },

  // ---- Handbook payment (Gumroad) --------------------------------
  // Create a product "Pin Phonics Handbook" ($29), copy its short URL.
  // Gumroad auto-delivers the PDF + emails the download — no server needed.
  GUMROAD: {
    paymentLink: "#demo-handbook"      // <-- replace with https://gumroad.com/l/XXXX
  },

  // ---- Optional: Stripe Payment Link (alternative to Gumroad) ----
  STRIPE: {
    paymentLink: ""                    // e.g. https://buy.stripe.com/xxx
  }
};
