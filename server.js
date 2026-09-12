/**
 * Optional Node/Express backend for Pin Phonics.
 *
 * Why optional: the site works fully client-side (Mailchimp embedded form +
 * Gumroad/Stripe Payment Links need no server). This file is ONLY needed if you
 * want to (a) keep your Mailchimp API key secret (server-side), or (b) handle
 * Gumroad webhooks to fulfill the PDF download yourself.
 *
 * Endpoints:
 *   POST /api/signup      → adds the email to your Mailchimp audience
 *   POST /api/gumroad     → receives Gumroad's purchase webhook, sends the PDF
 *
 * Usage:
 *   npm init -y && npm install express mailchimp-api-v3 cors body-parser
 *   MAILCHIMP_KEY=xxx MAILCHIMP_LIST_ID=yyy node server.js
 */
const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const Mailchimp = require("mailchimp-api-v3");

const app = express();
app.use(cors());
app.use(bodyParser.json({ limit: "10kb" }));

const mc = new Mailchimp(process.env.MAILCHIMP_KEY || "");

/* Add an email to the Mailchimp audience. */
app.post("/api/signup", async (req, res) => {
  const email = (req.body.email || "").trim();
  const tags = req.body.tags || ["pin-gift"];
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    return res.status(400).json({ ok: false, error: "invalid_email" });
  try {
    await mc.post(`/lists/${process.env.MAILCHIMP_LIST_ID}/members`, {
      email_address: email, status: "subscribed", tags
    });
    res.json({ ok: true });
  } catch(err){
    console.warn("[signup] Mailchimp error:", err.message);
    res.status(502).json({ ok: false, error: err.message });
  }
});

/* Gumroad purchase webhook — fulfill the handbook PDF here. */
app.post("/api/gumroad", (req, res) => {
  const { email, product_permalink, purchaser_id } = req.body || {};
  console.log("[gumroad] purchase", { email, product_permalink, purchaser_id });
  // TODO: generate a signed download link for the PDF, email it to `email`.
  res.json({ ok: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Pin Phonics API listening on :${PORT}`));
