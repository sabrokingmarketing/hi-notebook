# -*- coding: utf-8 -*-
"""
ALL business text, contact details and brand colour live here.
Edit this file, then run:  python3 preview/_src/build.py
(When the site moves to Next.js, this becomes content/site.ts.)

Anything marked TODO is missing information. The site shows a safe stand-in until it is filled in.
"""

BRAND = "The HiNoterBook"
TAGLINE = "Your In-person AI NoteTaker"
BRAND_BLUE = "#1f5bd6"

PRICE_RAND = 7499           # RRP (recommended retail price) in Rand, once-off
REWARD_PCT = 10             # scratch-card reward = the maximum discount (10%)


def rand(n):
    """Write Rand the South African way: R7 499"""
    return "R" + f"{n:,}".replace(",", "\u00a0")  # non-breaking space keeps "R7 499" on one line


PRICE = rand(PRICE_RAND)                                        # "R7 499"
REWARD = f"{REWARD_PCT}%"                                       # "10%"
PRICE_REWARD = rand(round(PRICE_RAND * (100 - REWARD_PCT) / 100))  # "R6 749"
GIFT = "free HiNoter Earpods"
GIFT_VALUE = rand(999)                      # "R999"
SAVING = rand(PRICE_RAND - round(PRICE_RAND * (100 - REWARD_PCT) / 100))  # "R750"

# TODO: real WhatsApp number in international format, no plus, no leading 0 (e.g. 27821234567)
WHATSAPP = "27XXXXXXXXX"
WHATSAPP_DISPLAY = "+27 XX XXX XXXX"   # TODO
# TODO: real phone number for tap-to-call
PHONE_TEL = "+27XXXXXXXXX"
PHONE_DISPLAY = "+27 XX XXX XXXX"      # TODO
# TODO: real email inbox for pre-orders
EMAIL = "hello@hinoterbook.example"
# TODO: city or area the team works from (district only)
LOCATION = "South Africa"
# TODO: live domain, used for sitemap.xml and share links
DOMAIN = "https://hi-notebook.vercel.app"  # TODO: change to the real domain once it is connected in Vercel
# TODO: business hours
HOURS = "Monday to Friday, during business hours"

COLOURS = [
    # key, display name, swatch colour, image stem, alt text
    ("tan", "Tan", "#c99a6a", "folio-tan", "Tan leather folio with a stitched envelope flap"),
    ("onyx", "Onyx", "#1c1c1e", "folio-onyx", "Black leather folio with a stitched envelope flap"),
    ("stone", "Stone", "#a9a7a5", "folio-stone", "Stone grey leather folio with a stitched envelope flap"),
    ("blush", "Blush", "#dcaaa3", "folio-blush", "Blush pink leather folio with a stitched envelope flap"),
]
# TODO: confirm the official colour names (Tan, Onyx, Stone, Blush are working names)

# Pages in the main navigation: (file, label)
NAV = [
    ("index.html", "Home"),
    ("product.html", "Product"),
    ("how-it-works.html", "How it works"),
    ("integrations.html", "Integrations"),
    ("pricing.html", "Pricing"),
    ("faq.html", "FAQ"),
]

# Integrations. status: "planned" (on the roadmap) or "explore" (we are checking if it can be done).
# Nothing is "live" yet. Change a status only when it really works.
INTEGRATIONS = [
    ("openai", "ChatGPT", "AI tools", "planned", "Send a meeting's notes to ChatGPT to ask follow-up questions or reshape them."),
    ("claude", "Claude", "AI tools", "planned", "Hand a transcript to Claude for a longer read, a brief or a draft."),
    ("gemini", "Gemini", "AI tools", "planned", "Open notes in Gemini alongside your Google work."),
    ("zoom", "Zoom", "Meetings", "planned", "Let the assistant join scheduled Zoom calls and capture them."),
    ("google-meet", "Google Meet", "Meetings", "planned", "Capture Google Meet calls from your calendar."),
    ("teams", "Microsoft Teams", "Meetings", "planned", "Capture Teams meetings for work accounts."),
    ("google-calendar", "Google Calendar", "Calendar", "planned", "See upcoming meetings and choose which ones to capture."),
    ("gmail", "Gmail", "Follow-up", "explore", "Open the drafted follow-up email ready to send."),
    ("slack", "Slack", "Follow-up", "explore", "Post a short recap to a channel after the call."),
    ("notion", "Notion", "Notes", "explore", "Save the summary and action items to a Notion page."),
    ("google-docs", "Google Docs", "Notes", "explore", "Export the full notes as a document."),
]

FAQ_HOME = [
    ("Where do my notes go after a meeting?",
     "Straight to your email inbox. When the meeting ends, the assistant sends you the summary, action items and a draft follow-up email to review before you share anything."),
    ("Is the AI assistant available today?",
     "Not yet. Pre-orders are open now. When our team contacts you about your pre-order, they will share the timing for the folio and for assistant access."),
    (f"How does the {PRICE} pre-order work?",
     f"{PRICE} is the recommended retail price (RRP), paid once-off, and it includes {GIFT} worth {GIFT_VALUE}. Fill in the short pre-order form and send it. You don't pay anything on this website. Our team will contact you to confirm your colour, delivery and payment."),
    ("Which meeting apps will it work with?",
     "Zoom, Google Meet and Microsoft Teams are planned first. The integrations page shows each one's status, and nothing is marked live until it works."),
    ("Can I edit the notes before I share them?",
     "Yes, that is the plan. Summaries, action items and the follow-up email are drafts you check and change before anything goes out."),
    ("How do I use the 10% scratch-card reward?",
     f"Scratch the card on the homepage. The reward is saved on your device and applied to your pre-order automatically, so you pay {PRICE_REWARD} instead of {PRICE}."),
]

FAQ_MORE = [
    ("What comes in the box?",
     f"The folio with its built-in AI listening device, a power bank to keep the device charged, and {GIFT} worth {GIFT_VALUE}."),
    ("Is there a bigger discount?",
     f"No. {REWARD} off is the maximum discount, from the scratch card. Every pre-order also includes {GIFT} worth {GIFT_VALUE}."),
    ("Do I need my phone for it to listen?",
     "No. The AI listening device is built into the folio, so you just open it and start the meeting."),
    ("Does everyone in the meeting need to agree to being recorded?",
     "Yes. Tell people at the start when a meeting is being captured. South African law (POPIA) expects people to know how their personal information is used, and it's simply good manners."),
    ("Will it connect to ChatGPT, Claude and Gemini?",
     "That is planned, where each company's tools allow it. You would send a meeting's notes to the AI tool you already use. These connections are not live yet."),
    ("What colours can I choose?",
     "Four: Tan, Onyx, Stone and Blush. You choose one on the pre-order form."),
    ("Do I pay online?",
     "No. This website doesn't take payments. After you send your pre-order, our team contacts you with the payment details and next steps."),
    ("Can I change my colour after I pre-order?",
     "Yes. Tell our team when they contact you, or send us a WhatsApp message."),
    ("Where do you deliver?",
     "Our team will confirm delivery options for your area when they contact you."),
    ("Who is it for?",
     "People whose days are full of meetings: managers, sales teams, consultants, founders and anyone who takes minutes."),
]

# Open items for the owner (also listed in the build report)
TODO = [
    "WhatsApp number (international format, e.g. 27821234567)",
    "Phone number for tap-to-call",
    "Email address for pre-orders",
    "Live website address (domain) for sitemap and share links",
    "What the R7 499 pre-order includes, and delivery timing",
    "Official colour names",
    "Folio specifications: size and materials",
    "Listening device and power bank details (battery life, charging, how notes reach the inbox)",
    "Terms for the 10% reward (what it applies to, expiry)",
    "Company name and details for the Privacy Policy and pre-order terms",
    "Lifestyle photos of the folio in use (desk, meeting room)",
]
