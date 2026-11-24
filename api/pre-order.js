/*
  The HiNoterBook — pre-order emails (Vercel serverless function, no packages needed).

  When someone sends the pre-order form, this function:
    1. emails the full order to the team (TEAM_TO), and
    2. emails the customer a thank-you that explains what they get and what happens next.

  It reads the Resend key from the Vercel environment variable RESEND_API_KEY.
  The key never appears in the website code.

  Emails are sent from FROM, which must be on a domain verified in Resend (hinoterbook.co.za).
*/

const TEAM_TO = "info@survivalguide.co.za";
const FROM = "The HiNoterBook <orders@hinoterbook.co.za>";
const REPLY_TO_TEAM = "info@survivalguide.co.za";

const BRAND = "The HiNoterBook";
const TAGLINE = "Your In-person AI NoteTaker";
const RRP = 7499;
const REWARD_PCT = 10;
const GIFT = "HiNoter Earpods";
const GIFT_VALUE = 999;
const COLOURS = ["Tan", "Onyx", "Stone", "Blush"];
const PROVINCES = ["Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga", "Northern Cape", "North West", "Western Cape"];

const BLUE = "#1f5bd6";
const INK = "#0b0d12";
const MUTED = "#59606d";
const LINE = "#e5e9f0";

/* Rand the South African way: R7 499 */
function rand(n) { return "R" + Math.round(n).toLocaleString("en-US").replace(/,/g, " "); }
function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
}
function clean(v, max) { return String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, max); }
function cleanMultiline(v, max) { return String(v == null ? "" : v).replace(/[\u0000-\u0009\u000b-\u001f\u007f]/g, " ").trim().slice(0, max); }

/* Very small abuse guard: at most 5 orders per address per 10 minutes, per server instance. */
const hits = new Map();
function tooMany(ip) {
  const now = Date.now(), win = 10 * 60 * 1000;
  const list = (hits.get(ip) || []).filter(function (t) { return now - t < win; });
  list.push(now); hits.set(ip, list);
  return list.length > 5;
}

function allowedOrigin(req) {
  const origin = req.headers.origin || "";
  if (!origin) return false;
  let host;
  try { host = new URL(origin).host; } catch (e) { return false; }
  const own = req.headers["x-forwarded-host"] || req.headers.host || "";
  return host === own || /(^|\.)hinoterbook\.co\.za$/.test(host) || /\.vercel\.app$/.test(host);
}

async function sendEmail(key, payload) {
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Authorization": "Bearer " + key, "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) {
    let detail = ""; try { detail = await r.text(); } catch (e) {}
    throw new Error("Resend " + r.status + ": " + detail.slice(0, 300));
  }
  return r.json();
}

/* ---------- Email layouts (tables + inline styles so they work in Gmail, Outlook and Apple Mail) ---------- */

function shell(logoUrl, preheader, inner) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(BRAND)}</title></head>
<body style="margin:0;padding:0;background:#eef3fb;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">${esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef3fb;"><tr><td align="center" style="padding:28px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:20px;overflow:hidden;font-family:Inter,Segoe UI,Helvetica,Arial,sans-serif;color:${INK};">
<tr><td style="background:${BLUE};background-image:linear-gradient(160deg,#3a7ff0,#1d4fa8);padding:26px 32px;" align="left">
<img src="${esc(logoUrl)}" width="132" alt="${esc(BRAND)}" style="display:block;height:auto;border:0;">
</td></tr>
${inner}
<tr><td style="padding:22px 32px 28px;border-top:1px solid ${LINE};font-size:12px;line-height:1.6;color:${MUTED};">
${esc(BRAND)} · ${esc(TAGLINE)}<br>Prices in South African Rand. Nothing has been charged.
</td></tr>
</table></td></tr></table></body></html>`;
}

function row(label, value) {
  return `<tr><td style="padding:10px 0;border-bottom:1px solid ${LINE};font-size:14px;color:${MUTED};width:38%;vertical-align:top;">${esc(label)}</td>
<td style="padding:10px 0;border-bottom:1px solid ${LINE};font-size:14px;color:${INK};font-weight:600;vertical-align:top;">${value}</td></tr>`;
}

function customerEmail(o, logoUrl) {
  const priceLine = o.reward
    ? `<span style="text-decoration:line-through;color:${MUTED};font-weight:400;">${rand(RRP)}</span>&nbsp; ${rand(o.price)} <span style="color:#11623b;">(${REWARD_PCT}% reward applied)</span>`
    : `${rand(RRP)} (RRP)`;
  const gets = [
    [`${BRAND} folio in ${o.colour}`, "Stitched leather with an envelope flap and snap closure."],
    ["Built-in AI listening device", "It listens during your meeting and sends every note to your inbox afterwards: a summary, action items and a draft follow-up email."],
    ["Power bank", "Included, to keep the listening device charged."],
    ["Notepad and pen loop", "For the thoughts you still want to write by hand."],
    [`Free ${GIFT}`, `Worth ${rand(GIFT_VALUE)}, included with your pre-order.`]
  ].map(function (g) {
    return `<tr><td width="28" style="vertical-align:top;padding:8px 0;"><div style="width:10px;height:10px;border-radius:50%;background:${BLUE};margin-top:6px;"></div></td>
<td style="padding:8px 0;font-size:15px;line-height:1.5;"><b>${esc(g[0])}</b><br><span style="color:${MUTED};">${esc(g[1])}</span></td></tr>`;
  }).join("");
  const steps = [
    ["Our team contacts you", "We'll reach out on the email or phone number you gave us."],
    ["We confirm the details", "Your colour, delivery and how to pay."],
    ["You pay, we deliver", "Only once everything is confirmed with you."]
  ].map(function (s, i) {
    return `<tr><td width="34" style="vertical-align:top;padding:8px 0;"><div style="width:24px;height:24px;border-radius:50%;background:#eaf1fe;color:${BLUE};font-size:13px;font-weight:700;line-height:24px;text-align:center;">${i + 1}</div></td>
<td style="padding:8px 0;font-size:15px;line-height:1.5;"><b>${esc(s[0])}</b><br><span style="color:${MUTED};">${esc(s[1])}</span></td></tr>`;
  }).join("");

  const inner = `
<tr><td style="padding:32px 32px 8px;">
<p style="margin:0 0 6px;font-size:13px;font-weight:600;color:${BLUE};letter-spacing:.04em;text-transform:uppercase;">Pre-order received</p>
<h1 style="margin:0;font-size:28px;line-height:1.2;letter-spacing:-.02em;font-weight:600;">Thank you, ${esc(o.firstName)}.</h1>
<p style="margin:14px 0 0;font-size:16px;line-height:1.6;color:#2a2f3a;">Your pre-order for ${esc(BRAND)} is in. <b>Our team will be in touch soon</b> to confirm the details with you. Nothing has been charged.</p>
</td></tr>
<tr><td style="padding:20px 32px 4px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f8fc;border-radius:14px;"><tr><td style="padding:6px 20px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
${row("Colour", esc(o.colour))}
${row("Price", priceLine)}
${row("Free gift", `${esc(GIFT)} (worth ${rand(GIFT_VALUE)})`)}
<tr><td style="padding:10px 0;font-size:14px;color:${MUTED};">Reference</td><td style="padding:10px 0;font-size:14px;font-weight:600;">${esc(o.ref)}</td></tr>
</table></td></tr></table>
</td></tr>
<tr><td style="padding:24px 32px 0;"><h2 style="margin:0 0 6px;font-size:18px;font-weight:600;">What you'll get</h2>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">${gets}</table></td></tr>
<tr><td style="padding:22px 32px 8px;"><h2 style="margin:0 0 6px;font-size:18px;font-weight:600;">What happens next</h2>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">${steps}</table></td></tr>
<tr><td style="padding:16px 32px 28px;font-size:15px;line-height:1.6;color:#2a2f3a;">Questions in the meantime? Just reply to this email.<br><br>Warm regards,<br><b>The ${esc(BRAND.replace(/^The /, ""))} team</b></td></tr>`;

  const text = [
    `Thank you, ${o.firstName}.`, "",
    `Your pre-order for ${BRAND} is in. Our team will be in touch soon to confirm the details with you. Nothing has been charged.`, "",
    `Colour: ${o.colour}`,
    `Price: ${o.reward ? rand(o.price) + " (" + rand(RRP) + " RRP less " + REWARD_PCT + "% reward)" : rand(RRP) + " (RRP)"}`,
    `Free gift: ${GIFT} (worth ${rand(GIFT_VALUE)})`,
    `Reference: ${o.ref}`, "",
    "WHAT YOU'LL GET",
    `- ${BRAND} folio in ${o.colour}: stitched leather, envelope flap, snap closure`,
    "- Built-in AI listening device: every note sent to your inbox after the meeting",
    "- Power bank to keep it charged",
    "- Notepad and pen loop",
    `- Free ${GIFT}, worth ${rand(GIFT_VALUE)}`, "",
    "WHAT HAPPENS NEXT",
    "1. Our team contacts you.", "2. We confirm your colour, delivery and how to pay.", "3. You pay and we deliver, only once everything is confirmed.", "",
    "Questions? Just reply to this email.", "", `The ${BRAND.replace(/^The /, "")} team`
  ].join("\n").replace(/ /g, " ");

  return { html: shell(logoUrl, `Thank you for your pre-order. Here's what you'll get and what happens next.`, inner), text };
}

function teamEmail(o, logoUrl) {
  const inner = `
<tr><td style="padding:28px 32px 6px;">
<p style="margin:0 0 6px;font-size:13px;font-weight:600;color:${BLUE};letter-spacing:.04em;text-transform:uppercase;">New pre-order · ${esc(o.ref)}</p>
<h1 style="margin:0;font-size:24px;line-height:1.25;font-weight:600;">${esc(o.name)} pre-ordered in ${esc(o.colour)}</h1>
<p style="margin:10px 0 0;font-size:15px;color:${MUTED};">Received ${esc(o.when)} (South African time). Reply to this email to answer the customer directly.</p>
</td></tr>
<tr><td style="padding:16px 32px 8px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">
${row("Name", esc(o.name))}
${row("Email", `<a href="mailto:${esc(o.email)}" style="color:${BLUE};">${esc(o.email)}</a>`)}
${row("Phone", `<a href="tel:${esc(o.phoneTel)}" style="color:${BLUE};">${esc(o.phone)}</a>`)}
${row("Colour", esc(o.colour))}
${row("Province", esc(o.province || "Not given"))}
${row("Price", o.reward ? `${rand(o.price)} once-off <span style="color:${MUTED};font-weight:400;">(${rand(RRP)} RRP less ${REWARD_PCT}% scratch-card reward)</span>` : `${rand(RRP)} once-off (RRP)`)}
${row("Scratch-card reward", o.reward ? `Yes, ${REWARD_PCT}%` : "No")}
${row("Free gift", `${esc(GIFT)} (worth ${rand(GIFT_VALUE)})`)}
${row("Notes", o.notes ? esc(o.notes).replace(/\n/g, "<br>") : "None")}
${row("Consent (POPIA)", "Agreed to be contacted about this pre-order")}
</table></td></tr>
<tr><td style="padding:12px 32px 26px;font-size:14px;line-height:1.6;color:#2a2f3a;"><b>Next step:</b> contact the customer to confirm colour, delivery and payment. They have been sent a thank-you email.</td></tr>`;

  const text = [
    `New pre-order ${o.ref}`, `Received: ${o.when} (SAST)`, "",
    `Name: ${o.name}`, `Email: ${o.email}`, `Phone: ${o.phone}`, `Colour: ${o.colour}`, `Province: ${o.province || "Not given"}`,
    `Price: ${o.reward ? rand(o.price) + " once-off (" + rand(RRP) + " RRP less " + REWARD_PCT + "% reward)" : rand(RRP) + " once-off (RRP)"}`,
    `Scratch-card reward: ${o.reward ? "Yes, " + REWARD_PCT + "%" : "No"}`, `Free gift: ${GIFT} (worth ${rand(GIFT_VALUE)})`,
    `Notes: ${o.notes || "None"}`, "Consent (POPIA): agreed to be contacted about this pre-order", "",
    "Next step: contact the customer to confirm colour, delivery and payment."
  ].join("\n").replace(/ /g, " ");

  return { html: shell(logoUrl, `${o.name} pre-ordered in ${o.colour}. ${o.email}, ${o.phone}`, inner), text };
}

/* ---------- Request handler ---------- */

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") { res.setHeader("Allow", "POST"); return res.status(405).json({ ok: false, error: "Use POST." }); }
  if (!allowedOrigin(req)) return res.status(403).json({ ok: false, error: "Not allowed." });

  const key = process.env.RESEND_API_KEY;
  if (!key) { console.error("RESEND_API_KEY is not set"); return res.status(500).json({ ok: false, error: "Email is not set up yet." }); }

  const ip = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim() || "unknown";
  if (tooMany(ip)) return res.status(429).json({ ok: false, error: "Too many attempts. Please try again in a few minutes." });

  let b = req.body;
  if (typeof b === "string") { try { b = JSON.parse(b); } catch (e) { b = {}; } }
  b = b || {};

  /* Honeypot: real people never fill this hidden field. Pretend success for bots. */
  if (clean(b.website, 200)) return res.status(200).json({ ok: true });

  const name = clean(b.name, 120);
  const email = clean(b.email, 200).toLowerCase();
  const phone = clean(b.phone, 40);
  const colour = clean(b.colour, 20);
  const province = clean(b.province, 40);
  const notes = cleanMultiline(b.notes, 1500);
  const reward = b.reward === true;
  const digits = phone.replace(/\D/g, "");

  const errors = [];
  if (!name) errors.push("name");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) errors.push("email");
  if (digits.length < 9 || digits.length > 12) errors.push("phone");
  if (COLOURS.indexOf(colour) === -1) errors.push("colour");
  if (province && PROVINCES.indexOf(province) === -1) errors.push("province");
  if (b.consent !== true) errors.push("consent");
  if (errors.length) return res.status(400).json({ ok: false, error: "Please check: " + errors.join(", ") + ".", fields: errors });

  const price = reward ? Math.round(RRP * (100 - REWARD_PCT) / 100) : RRP;
  const now = new Date();
  const ref = "HNB-" + now.toISOString().slice(2, 10).replace(/-/g, "") + "-" + Math.random().toString(36).slice(2, 6).toUpperCase();
  const when = now.toLocaleString("en-ZA", { timeZone: "Africa/Johannesburg", dateStyle: "medium", timeStyle: "short" });
  const host = req.headers["x-forwarded-host"] || req.headers.host;
  const logoUrl = "https://" + host + "/assets/img/logo-outline.png";
  const phoneTel = digits.startsWith("0") ? "+27" + digits.slice(1) : (digits.startsWith("27") ? "+" + digits : digits);

  const o = { name, firstName: name.split(/\s+/)[0], email, phone, phoneTel, colour, province, notes, reward, price, ref, when };

  try {
    const team = teamEmail(o, logoUrl);
    await sendEmail(key, {
      from: FROM, to: [TEAM_TO], reply_to: email,
      subject: `New pre-order: ${name} (${colour}) · ${ref}`,
      html: team.html, text: team.text,
      tags: [{ name: "type", value: "pre_order_team" }]
    });
  } catch (err) {
    console.error("Team email failed:", err.message);
    return res.status(502).json({ ok: false, error: "We couldn't send your pre-order just now." });
  }

  let customerSent = true;
  try {
    const cust = customerEmail(o, logoUrl);
    await sendEmail(key, {
      from: FROM, to: [email], reply_to: REPLY_TO_TEAM,
      subject: `Thank you for your pre-order, ${o.firstName}`,
      html: cust.html, text: cust.text,
      tags: [{ name: "type", value: "pre_order_customer" }]
    });
  } catch (err) {
    customerSent = false;
    console.error("Customer email failed:", err.message);
  }

  return res.status(200).json({ ok: true, ref, customerSent });
};
