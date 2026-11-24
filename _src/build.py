# -*- coding: utf-8 -*-
"""Builds every page of the static preview from content.py.  Run: python3 preview/_src/build.py"""
import os, re, json, html
import content as S  # all business text lives in content.py

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
_KIT_PARTS = (".claude", "skills", "design-taste-frontend", "assets", "icons", "demo")
KIT = next((d for d in (os.path.join(OUT, *_KIT_PARTS), os.path.join(OUT, "..", *_KIT_PARTS)) if os.path.isdir(d)), os.path.join(OUT, *_KIT_PARTS))
e = html.escape


def ui(name, cls=""):
    """Inline a UI icon from the Taste Skill kit (decorative)."""
    svg = open(os.path.join(KIT, "ui-" + name + ".svg"), encoding="utf-8").read()
    svg = svg.replace("<svg ", '<svg aria-hidden="true" focusable="false" ' + (f'class="{cls}" ' if cls else ""), 1)
    return svg.replace(' width="24" height="24"', ' width="20" height="20"', 1)


def photo(stem, alt, w, h, sizes="(max-width: 860px) 92vw, 760px", cls="", style=""):
    """A real photograph (800/1600 widths)."""
    return (f'<img class="{cls}" src="assets/img/{stem}-1600.webp" '
            f'srcset="assets/img/{stem}-800.webp 800w, assets/img/{stem}-1600.webp 1600w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{e(alt)}" loading="lazy" decoding="async"{f' style="{style}"' if style else ""}>')


def lifestyle(stem="life-meeting", alt="A woman in an office holding a tan HiNoterBook folio and a pencil, with colleagues working at a table behind her",
              w=1536, h=1024, eyebrow="In the room", h2="Made for the meeting room",
              p="Walk in with the folio under your arm. The AI listening device is built in, so you just write down what you want to remember. Your notes arrive in your inbox when the meeting ends.",
              pos=""):
    style = f"object-position:{pos}" if pos else ""
    return f"""<div class="feature-photo">
  <div class="fp-img">{photo(stem, alt, w, h, "(max-width: 860px) 92vw, 1200px", "", style)}</div>
  <div class="glass">
    <span class="eyebrow">{e(eyebrow)}</span>
    <h2>{e(h2)}</h2>
    <p>{e(p)}</p>
    <a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a>
  </div>
</div>"""


def inside(slides=None, stem="folio-open", alt="The tan folio lying open on a wooden desk, showing its built-in AI listening device, a pen loop and a cream notebook under the snap flap", w=1600, h=2142):
    items = [
        ("AI listening device", "Built into the folio. It listens during the meeting, then your notes go to your inbox."),
        ("Power bank", "Included, to keep the listening device charged."),
        ("Notebook", "A lined notepad for the thoughts you want to keep by hand."),
        ("Pen loop", "Your pen stays with your notes."),
        ("Snap closure", "The flap closes with a press stud."),
    ]
    lis = "".join(f"<li><b>{e(h)}</b><span>{e(p)}</span></li>" for h, p in items)
    return f"""<div class="split inside">
  <div>
    <span class="eyebrow">Inside the folio</span>
    <h2>Everything you carry into a meeting, in one place</h2>
    <p class="lede">Open the flap and the listening device, notebook and pen are side by side, ready when the meeting starts.</p>
    <ul class="dot-list">{lis}</ul>
  </div>
  {slideshow(slides) if slides else '<div class="inside-img">' + photo(stem, alt, w, h, "(max-width: 860px) 92vw, 560px") + '</div>'}
</div>"""


def slideshow(slides):
    """Photos that fade from one to the next every few seconds, with dots and a pause button."""
    imgs, dots = "", ""
    for i, (stem, alt) in enumerate(slides):
        imgs += photo(stem, alt, 1600, 2142, "(max-width: 860px) 92vw, 560px", "slide" + (" on" if i == 0 else ""))
        dots += (f'<button class="slide-dot" type="button" aria-label="Show photo {i + 1} of {len(slides)}"'
                 f'{" aria-current=\"true\"" if i == 0 else ""}><i></i></button>')
    return (f'<div class="inside-img slideshow" data-slideshow>{imgs}'
            f'<div class="slide-ctrl"><div class="slide-dots" role="group" aria-label="Photos">{dots}</div>'
            '<button class="slide-pause" type="button" aria-pressed="false" aria-label="Pause photos" data-slide-pause>'
            '<svg class="i-pause" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>'
            '<svg class="i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.9l10-6.5a1 1 0 0 0 0-1.7l-10-6.6A1 1 0 0 0 8 5.5z"/></svg>'
            '</button></div></div>')


def price_block():
    """Full price; when the scratch-card reward is saved, it shows crossed out next to the reward price."""
    return (f'<span class="p-was">{S.PRICE}</span><span class="p-now">{S.PRICE_REWARD}</span>'
            f'<span class="p-badge">{S.REWARD} off</span>')


TOP_SCRIPT = '<script>/* Always open a page at the top (unless the link points to a spot on the page) */\ntry{if("scrollRestoration" in history)history.scrollRestoration="manual";}catch(e){}\n(function(){function top(){if(!location.hash){document.documentElement.style.scrollBehavior="auto";window.scrollTo(0,0);document.documentElement.style.scrollBehavior="";}}\ndocument.addEventListener("DOMContentLoaded",top);window.addEventListener("load",top);window.addEventListener("pageshow",function(e){if(e.persisted)top();});})();</script>\n'

def scratch_group():
    """One scratch card with its Reveal / Claim buttons."""
    return f"""<div data-scratch-group>
    <div class="scratch" data-scratch>
      <div class="scratch-under" aria-hidden="true">
        <span class="k">Your reward</span>
        <span class="v">{S.REWARD.rstrip('%')}<small>% off</small></span>
        <span class="s">You pay {S.PRICE_REWARD} instead of {S.PRICE} RRP</span>
      </div>
      <canvas aria-label="Scratch card. Scratch to reveal your reward, or use the Reveal button below." role="img"></canvas>
      <div class="confetti" aria-hidden="true"></div>
    </div>
    <div class="scratch-tools">
      <button class="btn btn-ghost before" type="button" data-reveal>Reveal my reward</button>
      <a class="btn btn-primary reward-won" href="pre-order.html">Claim {S.REWARD} with my pre-order {ARR}</a>
    </div>
    </div>"""


def promo():
    """Welcome pop-up with its own scratch card (shown once, by site.js)."""
    return f"""<div class="promo" id="promo" hidden>
  <div class="promo-backdrop" data-promo-close></div>
  <div class="promo-card" role="dialog" aria-modal="true" aria-labelledby="promo-title" aria-describedby="promo-desc">
    <button class="promo-x" type="button" aria-label="Close" data-promo-close>{ui("x")}</button>
    <span class="promo-tag">{ui("gift")}Welcome gift</span>
    <h2 id="promo-title">Scratch to reveal your {S.REWARD} off</h2>
    <p id="promo-desc">A thank-you for being early. Scratch the card and pay {S.PRICE_REWARD} instead of {S.PRICE} RRP, plus {S.GIFT} worth {S.GIFT_VALUE}.</p>
    {scratch_group()}
    <button class="promo-later" type="button" data-promo-close>Maybe later</button>
  </div>
</div>
"""


MARK = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/>'
        '<path d="M3.5 7.5 12 13l8.5-5.5"/><circle cx="12" cy="16.4" r="1.35" fill="#fff" stroke="none"/></svg>')
ARR = '<span class="arr" aria-hidden="true">→</span>'


def img(stem, alt, sizes="(max-width: 700px) 90vw, 600px", cls="", eager=False, idattr=""):
    return (f'<img {idattr}class="{cls}" src="assets/img/{stem}-1200.webp" '
            f'srcset="assets/img/{stem}-640.webp 640w, assets/img/{stem}-1200.webp 1200w" sizes="{sizes}" '
            f'width="1200" height="990" alt="{e(alt)}" {"" if eager else "loading=\"lazy\" "}decoding="async">')


def head(title, desc, path):
    full = f"{title} | {S.BRAND}" if path != "index.html" else f"{S.BRAND} — {S.TAGLINE}"
    url = S.DOMAIN + "/" + ("" if path == "index.html" else path)
    return f"""<!doctype html>
<html lang="en-ZA">
<head>
<meta charset="utf-8">{'<base href="/">' if path == "404.html" else ""}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#1f5bd6">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(S.BRAND)}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{S.DOMAIN}/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="favicon-64.png" sizes="64x64" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@500;600&display=swap">
<link rel="stylesheet" href="assets/css/site.css">
<script>window.SITE={json.dumps({"brand": S.BRAND, "price": S.PRICE, "priceReward": S.PRICE_REWARD, "reward": S.REWARD, "gift": S.GIFT + " worth " + S.GIFT_VALUE, "whatsapp": S.WHATSAPP, "email": S.EMAIL})};</script>
{TOP_SCRIPT}<script defer src="assets/js/site.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(path):
    links = "".join(
        f'<a href="{f}"{" aria-current=\"page\"" if f == path else ""}>{e(l)}</a>' for f, l in S.NAV)
    mlinks = "".join(
        f'<a class="m-link" href="{f}"{" aria-current=\"page\"" if f == path else ""}>{e(l)}<span aria-hidden="true">→</span></a>'
        for f, l in S.NAV + [("contact.html", "Contact")])
    return f"""<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="index.html" aria-label="{e(S.BRAND)} home"><img class="brand-logo" src="assets/img/logo-outline.png" alt="{e(S.BRAND)}" width="337" height="220"></a>
    <nav class="nav-pill" aria-label="Main">{links}</nav>
    <div class="head-actions">
      <a class="btn btn-white btn-sm" href="pre-order.html">Pre-order<span class="long">&nbsp;· {S.PRICE}</span></a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu"><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu">
  <nav aria-label="Mobile">{mlinks}</nav>
  <a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a>
  <p class="m-contact">Questions? <a class="link" href="https://wa.me/{S.WHATSAPP}">WhatsApp us</a> or call <a class="link" href="tel:{S.PHONE_TEL}">{S.PHONE_DISPLAY}</a>.</p>
</div>
"""


def footer():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="f-top">
      <div>
        <a class="brand" href="index.html" aria-label="{e(S.BRAND)} home"><img class="brand-logo" src="assets/img/logo.png" alt="{e(S.BRAND)}" width="337" height="220"></a>
        <p>A stitched folio with a built-in AI listening device. Made for people who live in meetings.</p>
        <a class="btn btn-primary btn-sm f-cta" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a>
      </div>
      <div class="f-col"><h2>Product</h2><ul>
        <li><a href="product.html">The notebook</a></li>
        <li><a href="how-it-works.html">How it works</a></li>
        <li><a href="integrations.html">Integrations</a></li>
        <li><a href="pricing.html">Pricing</a></li>
      </ul></div>
      <div class="f-col"><h2>Help</h2><ul>
        <li><a href="faq.html">FAQ</a></li>
        <li><a href="contact.html">Contact us</a></li>
        <li><a href="pre-order.html">Pre-order</a></li>
      </ul></div>
      <div class="f-col"><h2>Talk to us</h2><ul>
        <li><a href="https://wa.me/{S.WHATSAPP}">WhatsApp {S.WHATSAPP_DISPLAY}</a></li>
        <li><a href="tel:{S.PHONE_TEL}">Call {S.PHONE_DISPLAY}</a></li>
        <li><a href="mailto:{S.EMAIL}">{S.EMAIL}</a></li>
      </ul></div>
    </div>
    <div class="f-bottom">
      <span>© 2026 {e(S.BRAND)}. Prices in South African Rand.</span>
      <span><a href="privacy.html">Privacy Policy (POPIA)</a> · <a href="terms.html">Pre-order terms</a></span>
      <span>Tool icons: gilbarbara/logos and Simple Icons (CC0). Names belong to their owners.</span>
    </div>
  </div>
</footer>
<div class="sr-only" aria-live="polite" id="scratch-live"></div>
</body>
</html>
"""


def page(path, title, desc, body):
    pop = "" if path in ("pre-order.html", "privacy.html", "terms.html", "404.html") else promo()
    return head(title, desc, path) + header(path) + '<main id="main">' + body + "</main>\n" + pop + footer()


def page_hero(crumb, h1, lede, actions=True, extra=""):
    acts = (f'<div class="actions"><a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a>'
            f'<a class="btn btn-white" href="contact.html">Ask a question</a></div>') if actions else ""
    return f"""<section class="sky page-hero"><div class="wrap" data-enter>
  <span class="crumb">{e(crumb)}</span>
  <h1>{h1}</h1>
  <p class="lede">{lede}</p>
  {acts}{extra}
</div></section>"""


def close_band(h2="Be in the room. Let the notebook keep the notes.",
               p=f"Pre-order yours for {S.PRICE}. Our team will contact you with the next steps."):
    return f"""<section class="sky close"><div class="wrap">
  <h2>{h2}</h2>
  <p>{p}</p>
  <div class="actions"><a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a>
  <a class="btn btn-white" href="https://wa.me/{S.WHATSAPP}">Chat on WhatsApp</a></div>
</div></section>"""


def faq_block(items, idp, heading="Frequently asked questions", aside=True):
    rows = ""
    for i, (q, a) in enumerate(items):
        rows += f"""<div class="acc-item"><h3><button class="acc-btn" type="button" aria-expanded="false" aria-controls="{idp}-{i}" id="{idp}-b{i}">{e(q)}<span class="pm" aria-hidden="true"></span></button></h3>
<div class="acc-panel" id="{idp}-{i}" role="region" aria-labelledby="{idp}-b{i}" aria-hidden="true"><div><p>{e(a)}</p></div></div></div>"""
    side = (f'<div><span class="eyebrow">FAQ</span><h2>{heading}</h2>'
            f'<a class="btn btn-primary" href="contact.html">Ask a question {ARR}</a></div>') if aside else ""
    return f'<div class="faq">{side}<div class="acc">{rows}</div></div>'


# ---------- Shared components ----------

def app_frame():
    """Laptop screen: an email inbox with the notes email The HiNoterBook sends after a meeting (example)."""
    mails = [
        ("Your notes: Launch check-in", "Summary, 4 action items and a draft follow-up", "10:42", True, True),
        ("Your notes: Supplier call", "Supplier confirmed the new delivery window", "Yesterday", False, False),
        ("Your notes: Weekly team sync", "3 decisions, 6 action items", "Mon", False, False),
        ("Your notes: Board prep", "Open questions for Thursday", "Fri", False, False),
    ]
    rows = ""
    for subj, prev, t, unread, on in mails:
        rows += (f'<div class="mrow{" on" if on else ""}{" unread" if unread else ""}"><span class="mav"></span>'
                 f'<div class="mtx"><div class="mtop"><b>{e(S.BRAND)}</b><time>{t}</time></div>'
                 f'<div class="msub">{e(subj)}</div><div class="mprev">{e(prev)}</div></div></div>')
    return f"""<div class="laptop" role="img" aria-label="Example: an email inbox showing the email {e(S.BRAND)} sends after a meeting, with the summary, decisions and action items">
  <div class="lid"><div class="notch"></div><div class="screen"><div class="screen-fit">
    <div class="screen-wall"></div>
    <div class="app mail" aria-hidden="true">
      <div class="app-top"><div class="dots"><i></i><i></i><i></i></div>
        <b style="font-weight:600">Inbox</b>
        <div class="msearch">Search mail</div>
        <span class="newmail"><i></i>New notes just arrived</span></div>
      <div class="mail-body">
        <aside class="mlist"><div class="mlist-h">Inbox <span>1 new</span></div>{rows}</aside>
        <article class="mread">
          <div class="mhead">
            <span class="mlogo"><img src="assets/img/logo.png" alt=""></span>
            <div><h5>Your notes: Launch check-in</h5><p><b>{e(S.BRAND)}</b> to me · Today 10:42 · sent when your meeting ended</p></div>
          </div>
          <div class="mcard">
            <div class="mmeta"><span>Launch check-in</span><span>32 min</span><span>Thandi N., Pieter V., Aisha K.</span></div>
            <h6>Summary</h6>
            <p>The supplier is two weeks late, so the launch moves from February to 3 March.</p>
            <div class="mcols">
              <div><h6>Decisions</h6><ul><li>New launch date: 3 March</li><li>Current price holds for the first 100 orders</li></ul></div>
              <div><h6>Action items</h6><ul class="mtodo"><li><i></i>Update the pricing sheet<em>Pieter · Fri</em></li><li><i></i>Tell the launch partners<em>Aisha · Wed</em></li><li><i></i>Confirm who signs the contract<em>Thandi · Thu</em></li></ul></div>
            </div>
            <div class="mbtns"><span class="mb pri">Review notes</span><span class="mb">Send follow-up email</span><span class="mb">Full transcript</span></div>
          </div>
          <div class="mdraft"><h6>Draft follow-up email · ready to review</h6>
            <p>Hi both, thanks for today. Quick recap: the supplier needs two more weeks, so we're launching on 3 March. Pieter, please update the pricing sheet by Friday. Aisha, could you let the launch partners know by Wednesday?</p></div>
        </article>
      </div>
    </div>
  </div></div></div>
  <div class="base"></div>
</div>"""


def notes_examples(idp="ex"):
    return f"""<div class="notes-wrap">
  <div>
    <span class="eyebrow">After the meeting</span>
    <h2>Notes you can use the minute the call ends</h2>
    <p class="lede">When the meeting ends, every note is sent straight to your inbox for you to review: a short summary, who does what, and a follow-up email ready to check and send. Here is an example.</p>
    <div class="tablist" role="tablist" aria-label="Example outputs">
      <button class="tab" role="tab" id="{idp}-t1" aria-selected="true" aria-controls="{idp}-p1">Summary</button>
      <button class="tab" role="tab" id="{idp}-t2" aria-selected="false" aria-controls="{idp}-p2" tabindex="-1">Action items</button>
      <button class="tab" role="tab" id="{idp}-t3" aria-selected="false" aria-controls="{idp}-p3" tabindex="-1">Follow-up email</button>
    </div>
  </div>
  <div class="doc">
    <div class="doc-head">{ui("mail")}In your inbox · Notes: Launch check-in<span class="demo-tag">Example</span></div>
    <div class="doc-body">
      <div class="doc-panel" role="tabpanel" id="{idp}-p1" aria-labelledby="{idp}-t1" tabindex="0">
        <h3>Launch check-in</h3><p class="meta">Thandi N., Pieter V., Aisha K.</p>
        <h4>In one line</h4><p>The supplier is two weeks late, so the launch moves from February to 3 March.</p>
        <h4>Decisions</h4><ul><li>New launch date: 3 March.</li><li>Keep the current price for the first 100 orders.</li></ul>
        <h4>Still open</h4><ul><li>Who signs the supplier contract: Thandi to confirm.</li></ul>
      </div>
      <div class="doc-panel" role="tabpanel" id="{idp}-p2" aria-labelledby="{idp}-t2" tabindex="0" hidden>
        <h3>Action items</h3><p class="meta">3 people · 4 actions</p>
        <ul class="todo">
          <li><span class="box"></span><span>Update the pricing sheet for the new date</span><span class="owner">Pieter · Fri</span></li>
          <li><span class="box"></span><span>Tell the two launch partners about the change</span><span class="owner">Aisha · Wed</span></li>
          <li><span class="box"></span><span>Confirm who signs the supplier contract</span><span class="owner">Thandi · Thu</span></li>
          <li><span class="box"></span><span>Book the next check-in for after the supplier call</span><span class="owner">Thandi</span></li>
        </ul>
      </div>
      <div class="doc-panel email" role="tabpanel" id="{idp}-p3" aria-labelledby="{idp}-t3" tabindex="0" hidden>
        <div class="hdr"><span>To</span><b>Pieter, Aisha</b><span>Subject</span><b>Launch moves to 3 March: next steps</b></div>
        <p>Hi both,</p><p style="margin-top:10px">Thanks for today. Quick recap: the supplier needs two more weeks, so we're launching on 3 March. We keep the current price for the first 100 orders.</p>
        <p style="margin-top:10px">Pieter, please update the pricing sheet by Friday. Aisha, could you let the two launch partners know by Wednesday? I'll confirm who signs the supplier contract.</p>
        <p style="margin-top:10px">Thandi</p>
      </div>
    </div>
  </div>
</div>"""


def showcase(h2="A notebook worth carrying into the room", pid="show-img"):
    first = S.COLOURS[0]
    sw = ""
    for i, (k, n, hexv, stem, alt) in enumerate(S.COLOURS):
        sw += (f'<button class="swatch" type="button" role="radio" aria-checked="{"true" if i == 0 else "false"}" '
               f'tabindex="{0 if i == 0 else -1}" data-name="{n}" data-alt="{e(alt)}" '
               f'data-src="assets/img/{stem}-1200.webp" data-srcset="assets/img/{stem}-640.webp 640w, assets/img/{stem}-1200.webp 1200w">'
               f'<i style="background:{hexv}"></i>{n}</button>')
    return f"""<div class="show">
  <div class="show-stage">{img(first[3], first[4], "(max-width: 860px) 90vw, 640px", "", False, f'id="{pid}" ')}</div>
  <div>
    <span class="eyebrow" style="color:#6b5848">The folio</span>
    <h2>{h2}</h2>
    <p class="lede">An envelope flap, stitched edges and a soft leather finish that looks good on a boardroom table. Your paper notes stay in the folio. The assistant keeps the record.</p>
    <div class="swatches" role="radiogroup" aria-label="Folio colour" data-swatches="{pid}">{sw}</div>
    <ul class="points">
      <li>{ui("check")}<span>Four colours: Tan, Onyx, Stone and Blush.</span></li>
      <li>{ui("check")}<span>RRP {S.PRICE}, once-off. No payment on this website.</span></li>
      <li>{ui("gift")}<span>Includes {S.GIFT} worth {S.GIFT_VALUE}.</span></li>
    </ul>
    <div class="actions"><a class="btn btn-primary" href="pre-order.html">Pre-order in <span data-colour-name>{first[1]}</span> {ARR}</a></div>
  </div>
</div>"""


def hub():
    nodes = [  # icon, x%, y%, faint, hide on small
        ("openai", 22, 22, False, False), ("claude", 33, 60, False, False), ("gemini", 15, 78, True, True),
        ("zoom", 70, 18, False, False), ("google-meet", 64, 66, False, False), ("teams", 82, 52, False, False),
        ("google-calendar", 6, 40, True, True), ("slack", 92, 82, True, True), ("notion", 94, 22, True, True),
        ("gmail", 46, 86, True, True),
    ]
    names = {i[0]: i[1] for i in S.INTEGRATIONS}
    out = ""
    for k, x, y, faint, hide in nodes:
        cls = "node" + (" faint" if faint else "") + (" hide-sm" if hide else "")
        out += f'<span class="{cls}" style="left:{x}%;top:{y}%"><img src="assets/icons/{k}.svg" alt="{e(names[k])}" width="28" height="28"></span>'
    return f"""<div class="hub"><svg class="lines" aria-hidden="true"></svg>
  <div class="core"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 7.5 12 13l8.5-5.5"/><circle cx="12" cy="16.4" r="1.35" fill="#fff" stroke="none"/></svg><span class="sr-only">{e(S.BRAND)}</span></div>
  {out}</div>"""


def scratch_card():
    return f"""<div class="reward">
  <div>
    <span class="eyebrow">Rewards</span>
    <h2>Scratch the card for {S.REWARD} off your pre-order</h2>
    <p class="lede">A thank-you for being early. Scratch the card to reveal your reward.</p>
    <ul class="reward-steps">
      <li><b>Scratch</b><span>Use your finger or mouse.</span></li>
      <li><b>Saved</b><span>Added to your pre-order automatically.</span></li>
      <li><b>Applied</b><span>Our team confirms it with your order.</span></li>
    </ul>
  </div>
  <div>
    {scratch_group()}
  </div>
</div>"""


# ---------- Pages ----------

def home():
    chat = json.dumps({
        "decide": "Two decisions: the launch moves to 3 March, and the current price holds for the first 100 orders.",
        "owe": "You own one action: confirm who signs the supplier contract, by Thursday.",
        "risk": "One risk came up: the supplier has slipped once already, so the new date depends on their next update.",
    })
    facts = f"""<div class="facts">
  <div class="fact"><span class="tag">RRP</span><span class="big">{S.PRICE}</span><p>Once-off. Reserve your folio now; you don't pay on this website.</p></div>
  <div class="fact"><span class="tag">Free with every order</span><span class="big">{S.GIFT_VALUE}</span><p>HiNoter Earpods worth {S.GIFT_VALUE}, included with your pre-order.</p></div>
  <div class="fact"><span class="tag">Early reward</span><span class="big">{S.REWARD}<small>off</small></span><p>Scratch the card further down this page to unlock it.</p></div>
</div>"""
    steps = [
        ("Step 1", "Before", "Connect your calendar", "Choose the meetings you want captured. The assistant reads the agenda and your notes from last time.",
         ["Launch check-in · 10:00", "Supplier call · 14:30", "Board prep · Thu"], "sky-soft"),
        ("Step 2", "During", "Stay in the conversation", "The assistant listens and writes as people talk, marking decisions, actions and open questions.",
         ["Decision: launch on 3 March", "Action: Pieter, pricing sheet", "Question: who signs?"], "sky-hero"),
        ("Step 3", "After", "Check your inbox", "Every note is sent straight to your inbox when the meeting ends: the summary, the action list and a draft follow-up, ready for you to review.",
         ["Notes sent to your inbox", "4 action items", "Follow-up email drafted"], "sky-soft"),
    ]
    cards, tabs = "", ""
    for i, (pill, when, h, p, items, bg) in enumerate(steps):
        lis = "".join(f'<li class="{"done" if i == 2 else ""}"><i></i>{e(t)}</li>' for t in items)
        cards += (f'<button type="button" class="step-card" data-pos="{i}" aria-label="Show {when.lower()} the meeting">'
                  f'<span class="bg" style="background-image:url(assets/img/{bg}-1200.webp)"></span>'
                  f'<span class="pill">{pill} · {when}</span><span class="ui"><h4>{e(h)}</h4><ul>{lis}</ul></span></button>')
        tabs += (f'<button class="step-tab" role="tab" id="st-t{i}" aria-selected="{"true" if i == 0 else "false"}" '
                 f'aria-controls="st-p{i}" tabindex="{0 if i == 0 else -1}">{when}<span class="long"> the meeting</span></button>')
    panels = "".join(
        f'<div role="tabpanel" id="st-p{i}" aria-labelledby="st-t{i}" {"hidden" if i else ""}><h3>{e(h)}</h3><p>{e(p)}</p></div>'
        for i, (_, _, h, p, _, _) in enumerate(steps))

    body = f"""
<section class="sky hero"><div class="wrap" data-enter>
  <span class="hero-fact"><b>New</b>Pre-orders open · Free HiNoter Earpods</span>
  <h1>The leather notebook that takes your meeting notes</h1>
  <p class="lede">A stitched folio with a built-in AI listening device. It takes every note and sends them straight to your inbox after the meeting, so you can stay in the conversation.</p>
  <div class="actions"><a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a><a class="btn btn-white" href="how-it-works.html">See how it works</a></div>
</div>
<div class="stage">{app_frame()}<img class="folio-float" src="assets/img/folio-trio-1600.webp" srcset="assets/img/folio-trio-800.webp 800w, assets/img/folio-trio-1600.webp 1400w" sizes="(max-width: 700px) 56vw, 460px" width="1400" height="946" alt="HiNoterBook folios in tan, black and blush" decoding="async"></div>
</section>

<section class="section film-sec"><div class="wrap">
  <div class="s-head"><span class="eyebrow">See it in action</span><h2>Open it, and it starts listening</h2><p>Thirty seconds on a real boardroom table: lift the flap, and the built-in listening device is ready for the meeting.</p></div>
  <div class="film" data-film>
    <video muted loop playsinline preload="none" poster="assets/img/film-poster-1600.webp" aria-label="Video: a hand opens the tan HiNoterBook folio on a boardroom table, showing the built-in listening device, notebook and pen. Caption: Your notebook starts listening.">
      <source src="assets/video/folio-film-960.mp4" type="video/mp4" media="(max-width: 760px)">
      <source src="assets/video/folio-film-1600.mp4" type="video/mp4">
    </video>
    <div class="film-ctrl">
      <button class="film-btn" type="button" data-film-play aria-label="Pause video" aria-pressed="false">
        <svg class="i-pause" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>
        <svg class="i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.9l10-6.5a1 1 0 0 0 0-1.7l-10-6.6A1 1 0 0 0 8 5.5z"/></svg>
      </button>
      <button class="film-btn" type="button" data-film-sound aria-label="Turn sound on" aria-pressed="false">
        <svg class="i-off" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H3v6h3l5 4V5z"/><path d="m22 9-6 6M16 9l6 6"/></svg>
        <svg class="i-on" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H3v6h3l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/></svg>
      </button>
    </div>
    <button class="film-big" type="button" data-film-start aria-label="Play video"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.9l10-6.5a1 1 0 0 0 0-1.7l-10-6.6A1 1 0 0 0 8 5.5z"/></svg></button>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="s-head"><h2>Every meeting, kept in one place</h2><p>What was said, what was decided and who owes what, in one record you can search and share.</p></div>
  <div class="duo">
    <div class="fcard tint-blue">
      <div class="panel"><b style="display:block;font-size:17px;margin-bottom:16px">Live transcript</b>
        <div class="tr-row"><span class="a" style="background:#d28f5a">TN</span><div><b>Thandi</b><p>The supplier needs two more weeks, so February won't hold.</p></div><time>00:00</time></div>
        <div class="tr-row"><span class="a" style="background:#6aa0a0">PV</span><div><b>Pieter</b><p>Then let's go for 3 March. I'll redo the pricing sheet.</p></div><time>00:21</time></div>
      </div>
      <div class="txt"><h3>Everything in context</h3><p class="d">Each line is tied to who said it and when, so a decision never loses its reason.</p></div>
    </div>
    <div class="fcard tint-gold">
      <div class="panel"><div class="chat" data-chat='{e(chat)}'>
        <div class="bubble me">What did we decide?</div>
        <div class="bubble ai" aria-live="polite">Two decisions: the launch moves to 3 March, and the current price holds for the first 100 orders.</div>
        <div class="prompts" aria-label="Try a question">
          <button class="prompt" type="button" data-prompt="decide" aria-pressed="true">What did we decide?</button>
          <button class="prompt" type="button" data-prompt="owe" aria-pressed="false">What do I owe?</button>
          <button class="prompt" type="button" data-prompt="risk" aria-pressed="false">Any risks?</button>
        </div>
      </div></div>
      <div class="txt"><span class="demo-tag">Example answers</span><h3 style="margin-top:12px">Ask your meeting anything</h3><p class="d">Get a straight answer from the record instead of scrolling through an hour of transcript.</p></div>
    </div>
  </div>
</div></section>

<section class="section ground-surface"><div class="wrap">
  <div class="s-head"><h2>Before, during and after the meeting</h2><p>The assistant takes the notes, then sends them to your inbox when the call ends. You just review them.</p></div>
  <div class="steps-stage" data-steps>{cards}</div>
  <div class="step-copy">
    <div class="step-ctrl"><div class="step-tabs" role="tablist" aria-label="Meeting stages" data-steps-tabs>{tabs}</div><button class="step-pause" type="button" aria-pressed="false" aria-label="Pause automatic steps" data-steps-pause><svg class="i-pause" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg><svg class="i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.9l10-6.5a1 1 0 0 0 0-1.7l-10-6.6A1 1 0 0 0 8 5.5z"/></svg></button></div>
    <div style="margin-top:22px">{panels}</div>
  </div>
</div></section>

<section class="section"><div class="wrap">{notes_examples()}</div></section>

<section class="section ground-sand"><div class="wrap">{showcase()}</div></section>

<section class="section"><div class="wrap">{lifestyle()}</div></section>

<section class="section ground-surface"><div class="wrap">{inside([
    ("folio-wood", "The tan folio lying open on a dark wooden boardroom table, showing its built-in AI listening device, a pen loop and a lined notepad, with a pen and coffee mug beside it and a city view behind"),
    ("folio-cafe", "The tan folio standing open on a cafe table, showing its built-in AI listening device, a pen in its loop and a notepad with handwritten meeting notes, next to a cappuccino"),
    ("folio-studio", "The tan folio lying open on a plain grey background, showing its built-in AI listening device, a pen loop, a lined notepad and the snap-button flap"),
])}</div></section>

<section class="section ground-soft"><div class="wrap">
  <div class="s-head"><h2>Quiet the noise. Keep the details.</h2></div>
  {facts}
</div></section>

<section class="section"><div class="wrap">
  <div class="s-head"><h2>Connect it to the tools you already use</h2></div>
  {hub()}
  <p class="hub-note">Planned connections include ChatGPT, Claude, Gemini, Zoom, Google Meet and Microsoft Teams. None are live yet. <a class="link" href="integrations.html">See each one's status</a>.</p>
</div></section>

<section class="section ground-soft" id="rewards"><div class="wrap">{scratch_card()}</div></section>

<section class="section"><div class="wrap">{faq_block(S.FAQ_HOME, "hf")}</div></section>

{close_band()}
"""
    return page("index.html", "Home",
                f"{S.BRAND} pairs a stitched leather folio with an AI meeting assistant that takes every note and sends it to your inbox after the meeting. Pre-order for {S.PRICE}.",
                body)


def product():
    cards = [
        ("notebook-pen", "Paper for your own thinking", "Sketch, jot and doodle in the folio. Writing by hand is still the best way to think in a meeting."),
        ("audio-lines", "A listening device built in", "The device inside the folio listens to the meeting and keeps the full record, so your own notes can be about ideas, not minutes."),
        ("mail", "Notes in your inbox", "After each meeting, the summary, actions and a draft follow-up land in your inbox, ready to review."),
    ]
    c = "".join(f'<div class="card"><span class="ic">{ui(i)}</span><h3>{e(h)}</h3><p>{e(p)}</p></div>' for i, h, p in cards)
    specs = [
        ("Design", "Envelope flap with stitched edges"),
        ("Finish", "Soft leather finish"),
        ("Inside", "Built-in AI listening device, notebook, pen loop"),
        ("In the box", "Folio with built-in listening device, a power bank, and " + S.GIFT + " worth " + S.GIFT_VALUE),
        ("Closure", "Snap-button flap"),
        ("Colours", "Tan, Onyx, Stone, Blush"),
        ("RRP", S.PRICE + " once-off"),
        ("Maximum discount", S.REWARD + " off with the scratch card"),
        ("Size and materials", "Confirmed by our team when they contact you"),
        ("Delivery", "Confirmed by our team when they contact you"),
    ]
    rows = "".join(f"<li><b style='min-width:11rem;display:inline-block'>{e(k)}</b><span>{e(v)}</span></li>" for k, v in specs)
    body = f"""
{page_hero("The notebook", "A stitched folio with an assistant inside the work", "Paper for the ideas you want to keep by hand. An AI assistant for everything that was said.", True, '<div class="hero-shot float">' + photo("folio-trio", "Three HiNoterBook folios side by side in tan, black and blush", 1400, 946, "(max-width: 960px) 92vw, 880px") + '</div>')}
<section class="section ground-sand"><div class="wrap">{showcase("Choose the colour you'll carry every day", "prod-img")}</div></section>
<section class="section"><div class="wrap">{inside(None, "folio-studio", "The tan folio lying open on a plain grey background, showing its built-in AI listening device, a pen loop, a lined notepad and the snap-button flap", 1600, 2142)}</div></section>
<section class="section ground-surface"><div class="wrap">{lifestyle()}</div></section>
<section class="section"><div class="wrap">
  <div class="s-head"><h2>Paper and software, each doing its part</h2><p>The folio is for you. The assistant is for the record.</p></div>
  <div class="cards3">{c}</div>
</div></section>
<section class="section ground-surface"><div class="wrap">
  <div class="split">
    <div><h2>The details</h2><p class="lede">What we can confirm today. Anything not listed yet, our team will confirm with you before you pay.</p>
      <div class="actions" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:26px"><a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a><a class="btn btn-ghost" href="faq.html">Read the FAQ</a></div></div>
    <ul class="checks" style="margin:0">{rows}</ul>
  </div>
</div></section>
{close_band()}
"""
    return page("product.html", "The notebook",
                f"{S.BRAND} folio: envelope flap, stitched edges and four leather colours, paired with an AI meeting assistant. Pre-order for {S.PRICE}.",
                body)


def how():
    tl = [
        ("Before", "Connect and prepare", "Link your calendar and pick the meetings to capture.",
         ["Pick meetings from your calendar", "See the agenda and last meeting's actions", "Tell attendees the meeting will be captured"]),
        ("During", "Listen, don't type", "The listening device built into the folio captures the meeting and the assistant writes as people talk.",
         ["Live transcript with speaker names", "Decisions, actions and risks marked as they happen", "Your handwritten notes stay in the folio"]),
        ("After", "Review from your inbox", "When the call ends, every note is sent straight to your inbox. Review it, change anything, then share it.",
         ["Summary and full notes emailed to you", "Action list with owners and dates", "Follow-up email drafted for you"]),
    ]
    t = ""
    for when, h, p, items in tl:
        lis = "".join(f"<li>{e(x)}</li>" for x in items)
        t += f'<div class="tl"><span class="when">{when} the meeting</span><h3>{e(h)}</h3><p>{e(p)}</p><ul>{lis}</ul></div>'
    uc = [
        ("users", "Managers", "Run the weekly one-to-ones and team check-ins without losing the thread between them."),
        ("handshake", "Sales teams", "Capture what the client asked for and send the follow-up while the call is still fresh."),
        ("briefcase" if False else "building-2", "Consultants", "Keep an exact record of client meetings and what was agreed."),
        ("clipboard-list", "Minute takers", "Boards, committees and school governing bodies: a first draft of the minutes, done."),
    ]
    u = "".join(f'<div class="uc"><span class="ic">{ui(i)}</span><h3>{e(h)}</h3><p>{e(p)}</p></div>' for i, h, p in uc)
    body = f"""
{page_hero("How it works", "Before, during and after every meeting", "Three simple stages. You stay in the conversation; your notes arrive in your inbox afterwards.")}
<section class="section"><div class="wrap"><div class="timeline">{t}</div></div></section>
<section class="section ground-surface"><div class="wrap">{lifestyle("folio-wood", "The tan folio lying open on a dark wooden boardroom table, showing its built-in AI listening device, a pen loop and a lined notepad, with a pen and coffee mug beside it and a city view behind", 1600, 2142, "Set up in seconds", "Open the folio and start the meeting", "The listening device is built in, your notebook lies flat and your pen is in its loop. Nothing to set up on the table.", "50% 68%")}</div></section>
<section class="section ground-surface"><div class="wrap">{notes_examples("hw")}</div></section>
<section class="section"><div class="wrap">
  <div class="s-head"><h2>Made for people who live in meetings</h2><p>If your calendar is full of calls, this is for you.</p></div>
  <div class="usecases">{u}</div>
</div></section>
{close_band()}
"""
    return page("how-it-works.html", "How it works",
                f"How {S.BRAND} works: it takes every note during the meeting and sends the summary, action items and a draft follow-up to your inbox afterwards.",
                body)


def integrations():
    lab = {"planned": "Planned", "explore": "Exploring", "live": "Live"}
    g = ""
    for k, n, cat, st, d in S.INTEGRATIONS:
        g += (f'<div class="int"><div class="int-top"><img src="assets/icons/{k}.svg" alt="" width="36" height="36">'
              f'<h3>{e(n)}</h3><span class="status {st}">{lab[st]}</span></div><p>{e(d)}</p>'
              f'<span style="font-size:13px;color:var(--muted)">{e(cat)}</span></div>')
    body = f"""
{page_hero("Integrations", "Built to work with the tools you already use", "Here is what we plan to connect, and the honest status of each one.")}
<section class="section"><div class="wrap">
  <div class="legend"><span><span class="status planned">Planned</span> on our roadmap</span><span><span class="status explore">Exploring</span> checking if it can be done well</span><span><span class="status live">Live</span> works today (none yet)</span></div>
  <div class="int-grid">{g}</div>
</div></section>
<section class="section ground-soft"><div class="wrap">
  <div class="s-head"><h2>How ChatGPT, Claude and Gemini fit in</h2><p>Your meeting record becomes something you can take to the AI tool you already trust: ask questions, write a brief, plan the next step.</p></div>
  {hub()}
  <p class="hub-note">These connections depend on what each company's tools allow. We'll only mark one as live when it works. Names and logos belong to their owners.</p>
</div></section>
{close_band()}
"""
    return page("integrations.html", "Integrations",
                f"Planned {S.BRAND} integrations with ChatGPT, Claude, Gemini, Zoom, Google Meet and Microsoft Teams, with an honest status for each.",
                body)


def pricing():
    checks = [
        "The folio in the colour you choose, with its built-in AI listening device",
        "A power bank to keep it charged",
        f"{S.GIFT[0].upper() + S.GIFT[1:]} worth {S.GIFT_VALUE}",
        "A place on the early-access list for the assistant",
        f"Your {S.REWARD} scratch-card reward, if you've revealed it",
        "A call or message from our team to confirm everything",
    ]
    cl = "".join(f"<li>{ui('check')}<span>{e(c)}</span></li>" for c in checks)
    body = f"""
{page_hero("Pricing", f"RRP {S.PRICE}, once-off", f"Includes {S.GIFT} worth {S.GIFT_VALUE}. No subscriptions and no payment online. Reserve yours and we'll take it from there.", False)}
<section class="section"><div class="wrap">
  <div class="price-wrap">
    <div class="price-card"><span class="tag">Pre-order</span><div class="price">{price_block()}</div><p class="sub p-note-base">RRP, once-off. Includes {S.GIFT} worth {S.GIFT_VALUE}. Reserve now; our team confirms the details before you pay.</p><p class="sub p-note-reward">Your {S.REWARD} scratch-card reward is applied: you save {S.SAVING}. Includes {S.GIFT} worth {S.GIFT_VALUE}. Our team confirms the details before you pay.</p>
      <ul class="checks">{cl}</ul>
      <a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a></div>
    <div class="after-card"><h3>What happens next</h3><ol>
      <li><div><b>Send your pre-order</b><span>It takes about a minute: your name, contact details and colour.</span></div></li>
      <li><div><b>Our team contacts you</b><span>We confirm your colour, delivery and how to pay.</span></div></li>
      <li><div><b>You pay and we deliver</b><span>Only once everything is confirmed with you.</span></div></li>
    </ol></div>
  </div>
</div></section>
<section class="section ground-surface"><div class="wrap">{faq_block(S.FAQ_HOME[2:3] + S.FAQ_MORE[0:1] + S.FAQ_HOME[5:6] + S.FAQ_MORE[5:8], "pf", "Questions about pre-ordering")}</div></section>
{close_band()}
"""
    return page("pricing.html", "Pricing",
                f"Pre-order {S.BRAND} for {S.PRICE}. No payment online: our team contacts you to confirm colour, delivery and payment.", body)


def faq():
    body = f"""
{page_hero("FAQ", "Questions, answered plainly", "If yours isn't here, ask us on WhatsApp or send us a message.")}
<section class="section"><div class="wrap">{faq_block(S.FAQ_HOME + S.FAQ_MORE, "fq", "Everything people ask us")}</div></section>
{close_band()}
"""
    return page("faq.html", "FAQ", f"Answers about {S.BRAND}: the AI assistant, the {S.PRICE} pre-order, integrations, recording consent and the scratch-card reward.", body)


def preorder():
    opts = ""
    for i, (k, n, hexv, stem, alt) in enumerate(S.COLOURS):
        opts += (f'<label><input type="radio" name="colour" value="{n}"{" checked" if i == 0 else ""}>'
                 f'<img src="assets/img/{stem}-640.webp" alt="" width="640" height="528" loading="lazy"><span>{n}</span></label>')
    provinces = ["Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga", "Northern Cape", "North West", "Western Cape"]
    po = "".join(f"<option>{p}</option>" for p in provinces)
    body = f"""
{page_hero("Pre-order", f"Reserve yours for {S.PRICE}", f"RRP, with {S.GIFT} worth {S.GIFT_VALUE} included. Send your details and our team will contact you with the next steps. You don't pay anything on this website.", False)}
<section class="section-tight"><div class="wrap">
<div class="form-shell" data-form-shell>
  <div class="form-card">
    <form id="preorder-form" novalidate>
      <h2>Your pre-order</h2>
      <p class="lede">All fields are required unless marked optional.</p>
      <div class="reward-banner">{ui("gift")}<span>Your {S.REWARD} scratch-card reward will be added to this pre-order.</span></div>
      <input type="hidden" name="reward" value="">
      <div class="fields">
        <div class="field full"><label for="name">Full name</label><input id="name" name="name" autocomplete="name" required><span class="err" role="alert"></span></div>
        <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" inputmode="email" required><span class="err" role="alert"></span></div>
        <div class="field"><label for="phone">Mobile number</label><input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required><span class="err" role="alert"></span></div>
        <fieldset class="field full" data-colour-field><legend>Colour</legend><div class="colour-pick">{opts}</div><span class="err" role="alert">Please choose a colour.</span></fieldset>
        <div class="field full"><label for="province">Province <span class="opt">(optional)</span></label><select id="province" name="province" autocomplete="address-level1"><option value="">Choose a province</option>{po}</select></div>
        <div class="field full"><label for="notes">Anything we should know? <span class="opt">(optional)</span></label><textarea id="notes" name="notes" placeholder="For example, a company order or a delivery question"></textarea></div>
        <div class="field full"><label class="consent"><input type="checkbox" name="consent" id="consent"><span>I agree that {e(S.BRAND)} may use these details to contact me about my pre-order, as set out in the <a class="link" href="privacy.html">Privacy Policy</a>.</span></label><span class="err" role="alert"></span></div>
      </div>
      <div class="form-foot"><button class="btn btn-primary" type="submit">Place my pre-order {ARR}</button><small>No payment now. Our team contacts you first.</small></div>
    </form>
    <div class="success" role="status">
      <div class="tick">{ui("check")}</div>
      <h2>Thank you. One last step.</h2>
      <p>Send your pre-order to our team below. Once it arrives, <b>our team will contact you with the next steps</b>: confirming your colour, delivery and payment.</p>
      <div class="summary"><dl data-summary></dl></div>
      <div class="form-foot"><a class="btn btn-primary" data-send-wa href="#" target="_blank" rel="noopener">Send on WhatsApp {ARR}</a><a class="btn btn-ghost" data-send-mail href="#">Send by email</a></div>
      <div class="form-foot"><button class="btn btn-ghost btn-sm" type="button" data-edit>Change my details</button></div>
    </div>
  </div>
  <aside class="side-card" aria-label="Order summary">
    {photo("folio-lineup", "HiNoterBook folios in tan, black and blush", 906, 650, "(max-width: 860px) 90vw, 420px", "lineup")}
    <div class="p">{price_block()}</div><p class="p-note-base">RRP, once-off. Includes {S.GIFT} worth {S.GIFT_VALUE}. Nothing is charged on this website.</p><p class="p-note-reward">Your {S.REWARD} scratch-card reward is applied: you save {S.SAVING}. Includes {S.GIFT} worth {S.GIFT_VALUE}. Nothing charged on this website.</p>
    <ul><li>Our team confirms colour, delivery and payment with you</li><li>Change your colour any time before it ships</li><li>Questions? <a class="link" href="https://wa.me/{S.WHATSAPP}">WhatsApp us</a></li></ul>
  </aside>
</div>
</div></section>
"""
    return page("pre-order.html", "Pre-order", f"Pre-order {S.BRAND} for {S.PRICE}. Choose your colour and send your details; our team will contact you with the next steps.", body)


def contact():
    body = f"""
{page_hero("Contact", "Talk to a person, not a form", "WhatsApp is the quickest way to reach us. Email and phone work too.", False)}
<section class="section-tight"><div class="wrap">
  <div class="contact-grid">
    <a class="c-card" href="https://wa.me/{S.WHATSAPP}"><span class="ic" style="background:#e9f8ef">{'<img src="assets/icons/whatsapp.svg" alt="" width="22" height="22">'}</span><b>WhatsApp</b><span class="v">{S.WHATSAPP_DISPLAY}</span><span>Usually the fastest reply</span></a>
    <a class="c-card" href="tel:{S.PHONE_TEL}"><span class="ic">{ui("phone")}</span><b>Call us</b><span class="v">{S.PHONE_DISPLAY}</span><span>{e(S.HOURS)}</span></a>
    <a class="c-card" href="mailto:{S.EMAIL}"><span class="ic">{ui("mail")}</span><b>Email</b><span class="v" style="word-break:break-all">{S.EMAIL}</span><span>We reply within business hours</span></a>
  </div>
</div></section>
<section class="section ground-surface"><div class="wrap wrap-narrow">
<div data-form-shell>
  <div class="form-card">
    <form id="contact-form" novalidate>
      <h2>Send us a question</h2><p class="lede">We'll open your message in WhatsApp or email so it reaches us straight away.</p>
      <div class="fields">
        <div class="field"><label for="cname">Your name</label><input id="cname" name="cname" autocomplete="name"><span class="err" role="alert"></span></div>
        <div class="field"><label for="cemail">Email</label><input id="cemail" name="cemail" type="email" autocomplete="email"><span class="err" role="alert"></span></div>
        <div class="field full"><label for="cmsg">Your question</label><textarea id="cmsg" name="cmsg"></textarea><span class="err" role="alert"></span></div>
      </div>
      <div class="form-foot"><button class="btn btn-primary" type="submit">Prepare my message {ARR}</button></div>
    </form>
    <div class="success" role="status"><div class="tick">{ui("check")}</div><h2>Your message is ready</h2><p>Choose how to send it. We'll get back to you as soon as we can.</p>
      <div class="form-foot"><a class="btn btn-primary" data-send-wa href="#" target="_blank" rel="noopener">Send on WhatsApp {ARR}</a><a class="btn btn-ghost" data-send-mail href="#">Send by email</a></div></div>
  </div>
</div>
</div></section>
"""
    return page("contact.html", "Contact", f"Contact {S.BRAND} team on WhatsApp, by phone or by email about pre-orders and the AI meeting notebook.", body)


def privacy():
    body = f"""
{page_hero("Privacy", "Privacy Policy", "How we handle your personal information under South Africa's Protection of Personal Information Act (POPIA).", False)}
<section class="section"><div class="wrap"><div class="prose">
<h2>Who we are</h2><p>{e(S.BRAND)} is the business behind this website and the pre-order offer. You can reach us at <a class="link" href="mailto:{S.EMAIL}">{S.EMAIL}</a> or on WhatsApp at {S.WHATSAPP_DISPLAY}.</p>
<h2>What we collect</h2><p>When you send a pre-order or a question, we receive the details you choose to share: your name, email address, mobile number, colour choice, province and any note you add.</p><p>This website does not ask for card or banking details, and it does not use advertising trackers.</p>
<h2>Why we use it</h2><ul><li>To contact you about your pre-order and confirm colour, delivery and payment.</li><li>To answer questions you send us.</li><li>To apply a reward you have revealed on the website.</li></ul><p>We will not sell your information or use it for anything you haven't agreed to.</p>
<h2>Your consent</h2><p>We only use your details after you tick the consent box on our pre-order form, or when you contact us yourself. You can withdraw consent at any time by telling us.</p>
<h2>Your rights under POPIA</h2><p>You may ask us what information we hold about you, ask us to correct or delete it, and object to how we use it. You can also complain to the Information Regulator of South Africa.</p>
<h2>How long we keep it</h2><p>We keep your details only as long as we need them to handle your pre-order and any follow-up, or as the law requires.</p>
<h2>Meetings and recordings</h2><p>When the assistant launches, captured meetings will contain other people's personal information. Always tell people when a meeting is being captured. We will publish full details on how recordings are stored and deleted before the assistant is available.</p>
<h2>Small details stored on your device</h2><p>If you reveal the scratch-card reward, your browser remembers it so it can be added to your pre-order form. This stays on your device and is not sent to us until you send your pre-order.</p>
<h2>Changes</h2><p>We may update this policy. The latest version is always on this page.</p>
<p class="note-box" style="margin-top:32px">Last updated: November 2026.</p>
</div></div></section>
"""
    return page("privacy.html", "Privacy Policy (POPIA)", f"How {S.BRAND} collects, uses and protects your personal information in line with POPIA.", body)


def terms():
    body = f"""
{page_hero("Pre-order terms", "Pre-order terms", "The simple rules behind the pre-order, in plain English.", False)}
<section class="section"><div class="wrap"><div class="prose">
<h2>The pre-order</h2><p>The recommended retail price (RRP) is {S.PRICE}, once-off, and includes {S.GIFT} worth {S.GIFT_VALUE}. Sending a pre-order reserves your place. It is not a payment and it is not a binding purchase until our team has confirmed the details with you and you have paid.</p>
<h2>What happens next</h2><p>Our team contacts you to confirm your colour, delivery and how to pay. If anything about the product or timing changes, we'll tell you before you pay.</p>
<h2>The {S.REWARD} reward</h2><p>The scratch-card reward is {S.REWARD} off your pre-order, so you pay {S.PRICE_REWARD} instead of {S.PRICE}. This is the maximum discount; it cannot be combined with other discounts. One reward per customer. Our team confirms the final amount with you before payment.</p>
<h2>Changing your mind</h2><p>You can cancel a pre-order at any time before you pay, by WhatsApp or email. After payment, the Consumer Protection Act and your other legal rights still apply.</p>
<h2>The AI assistant</h2><p>Features and integrations described on this website are planned and may change. We mark integrations as live only when they work.</p>
<p class="note-box" style="margin-top:32px">Last updated: November 2026.</p>
</div></div></section>
"""
    return page("terms.html", "Pre-order terms", f"{S.BRAND} pre-order terms: {S.PRICE}, no payment online, how the {S.REWARD} reward works and how to cancel.", body)


def notfound():
    body = f"""
<section class="sky page-hero" style="min-height:100svh;display:flex;align-items:center"><div class="wrap" data-enter>
  <span class="crumb">Page not found</span>
  <h1>This page has gone missing</h1>
  <p class="lede">The link may be old or mistyped. Try the homepage, or go straight to your pre-order.</p>
  <div class="actions"><a class="btn btn-primary" href="pre-order.html">Pre-order for {S.PRICE} {ARR}</a><a class="btn btn-white" href="index.html">Go to the homepage</a></div>
</div></section>
"""
    return page("404.html", "Page not found", f"This page could not be found. Visit {S.BRAND} homepage or pre-order for {S.PRICE}.", body)


PAGES = {
    "index.html": home, "product.html": product, "how-it-works.html": how, "integrations.html": integrations,
    "pricing.html": pricing, "faq.html": faq, "pre-order.html": preorder, "contact.html": contact,
    "privacy.html": privacy, "terms.html": terms, "404.html": notfound,
}

if __name__ == "__main__":
    for name, fn in PAGES.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(fn())
    urls = "".join(f"<url><loc>{S.DOMAIN}/{'' if n == 'index.html' else n}</loc></url>" for n in PAGES if n != "404.html")
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {S.DOMAIN}/sitemap.xml\n")
    print("built", len(PAGES), "pages")
