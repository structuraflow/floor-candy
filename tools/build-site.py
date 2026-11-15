#!/usr/bin/env python3
"""Floor Candy static site generator.

Renders every page from the data below into plain HTML. There is no runtime
dependency: the deployed artefact is static files. Run from the repo root:

    python3 tools/build-site.py

Design rules enforced here, not by hand:
  * Any field whose value is None is NOT rendered. Credentials and project
    specifications we cannot verify simply do not appear, there is no way to
    ship "TBC", "XXm2" or a placeholder to production.
  * Every page gets a unique title, meta description, canonical, OG data,
    one H1, breadcrumbs (except home) and the shared header/footer/CTA.
  * Asset cache-busting is a single constant, ASSET_V.
"""

import html
import json
import os
import re
import shutil
from urllib.parse import quote_plus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.floorcandyepoxy.com"
ASSET_V = 18  # bump on any CSS/JS change or returning visitors keep the old file

# --------------------------------------------------------------------------
# VERIFIED BUSINESS FACTS
# Every value here is confirmed. Do not add anything that is not.
# --------------------------------------------------------------------------
SOCIAL = {
    "facebook": "https://www.facebook.com/p/FLOOR-CANDY-61585930480462/",
}
GOOGLE_REVIEWS_URL = "https://www.google.com/maps?cid=5048866325392205442"
# "Ask for reviews" link copied from the GBP dashboard, 19 Oct 2026.
GOOGLE_WRITE_REVIEW_URL = "https://g.page/r/CYImb0MsLRFGEBM/review"

# Profiles that go into schema sameAs. None = not rendered. Fill each in only
# once the listing is live and verifiably Floor Candy's.
SAME_AS_PENDING = {
    "localsearch": None,  # TODO_LOCALSEARCH_URL
    "hotfrog": None,      # TODO_HOTFROG_URL
    "instagram": None,    # TODO_INSTAGRAM_URL
}

# Owner. Given name is verified; surname and photo are not supplied yet.
# None = not rendered. Photo: set "photo" to a base name and provide
# assets/img/<base>.webp + assets/img/<base>.jpg at photo_w x photo_h.
OWNER = {
    "given": "Jarrod",
    "surname": None,      # TODO_SURNAME
    "photo": None,        # TODO_JARROD_PHOTO
    "photo_w": 800, "photo_h": 1000,
}
OWNER_ID = "https://www.floorcandyepoxy.com/about#jarrod"

# Exact written warranty terms. None = keep the honest "no written warranty
# yet" wording on /about and in the FAQ. Never paraphrase or invent terms.
WARRANTY_TERMS = None     # TODO_WARRANTY_TERMS

# Which case study is nearest each town. None = suburbs of the jobs are not
# confirmed, so both case studies are linked from Taree and Forster only and
# neither is described as a job in that town.
PROJECT_SUBURBS = None    # TODO_PROJECT_SUBURBS, e.g. {"taree": ["garage-bare-slab-to-flake"]}

# Natural stone polishing page. Built only if Jarrod confirms the service.
CONFIRM_STONE_POLISHING = None  # TODO_CONFIRM_STONE_POLISHING ("yes" to build)

WHATSAPP = ("https://wa.me/61435193845?text="
            "Hi%20Jarrod%2C%20I%27d%20like%20a%20quote%20on%20a%20floor.")

BIZ = {
    "name": "Floor Candy",
    "legal": "Floor Candy",
    "owner": "Jarrod",
    "phone_display": "0435 193 845",
    "phone_href": "+61435193845",
    "email": "floorcandyepoxy@gmail.com",
    "hours": "Mon–Fri, 7am–7pm",
    "maps_cid": "5048866325392205442",
    "rating": "5.0",
    "review_count": 3,
    "rating_checked": "10 August 2026",
}

# Pending confirmation from Jarrod. None = not rendered anywhere.
# Fill a value in and it appears in the trust strip, footer and schema.
CREDENTIALS = {
    "abn": None,
    "licence_number": None,
    "public_liability": None,
    "insurer": None,
    "warranty": None,
    "years_operating": None,
    "accreditations": [],
}

PRICING = {
    "double_garage_from": 2450,
    "regional_from": 2600,
    "per_sqm_from": None,  # no per-m2 figure published until costed
    "qualifier": "Final pricing depends on floor size, existing condition, "
                 "preparation requirements, finish and location.",
    "regional_note": "Regional and travel-heavy jobs need to be commercially "
                     "viable and generally start around $2,600.",
}

OFFER = {"saving": 250, "label": "New customers save $250"}

# --------------------------------------------------------------------------
# LEAD ROUTING + MEASUREMENT
# FORM_ENDPOINT is Formspree form mrpeeawq, created by Zach 7 Oct 2026 to
# replace xqerqnyv (the July form, whose destination inbox was never confirmed).
# GA4_ID / GSC_TOKEN: None = nothing rendered. Paste the real values to turn on.
# --------------------------------------------------------------------------
FORM_ENDPOINT = "https://formspree.io/f/mrpeeawq"
GA4_ID = None        # e.g. "G-XXXXXXXXXX" from GA4 > Admin > Data streams
GSC_TOKEN = None     # content value of the google-site-verification meta tag
PIXEL_ID = None      # Meta Pixel ID (digits) from Events Manager. None = no pixel.

# --------------------------------------------------------------------------
# JOB FACTS, pending Jarrod. None = the sentence that needs it is not
# rendered. Fill a value in (plain words, e.g. "2 days", "24 hours") and it
# appears in the hero, process timeline, FAQ and thank-you page.
# --------------------------------------------------------------------------
JOB_FACTS = {
    "days_on_site": None,    # TODO_DAYS_ON_SITE   e.g. "2 days"
    "walk_on": None,         # TODO_WALK_ON        e.g. "24 hours"
    "drive_on": None,        # TODO_DRIVE_ON       e.g. "72 hours"
    "response_time": None,   # TODO_RESPONSE_TIME  e.g. "one business day"
    "booking_month": None,   # TODO_BOOKING_MONTH  e.g. "January" (capacity line)
}

# --------------------------------------------------------------------------
# HEADLINE VARIANTS for the Meta ads. Each ad links to /?h=a, /?h=b or /?h=c.
# The variant is swapped in before first paint and sent with the lead.
# "A" is the default and what search engines see.
# --------------------------------------------------------------------------
HEADLINES = {
    "a": "A garage floor you’ll actually want to show off.",
    "b": "Mid North Coast garage floors from $2,450. New customers save $250.",
    "c": "Sick of a cracked, oil-stained garage floor?",
}

# Quote-form step 1. (value sent to Formspree, label, icon key)
FLOOR_TYPES = [
    ("Single garage", "Single garage", "g1"),
    ("Double garage", "Double garage", "g2"),
    ("Triple garage", "Triple garage", "g3"),
    ("Patio or alfresco", "Patio or alfresco", "patio"),
    ("Shed or workshop", "Shed or workshop", "shed"),
    ("Inside the home", "Inside the home", "home"),
    ("Commercial", "Commercial", "comm"),
    ("Other", "Something else", "other"),
]
SIZES = ["Under 20m²", "20 to 40m²", "40 to 60m²", "Over 60m²", "Not sure"]
TIMINGS = ["ASAP", "Within a month", "1 to 3 months", "Just researching"]
HEARD = ["Facebook or Instagram ad", "Google search", "Google Maps", "Friend or family",
         "Saw a job or the van", "Other"]

REVIEWS = [
    {
        "name": "Reece Hawes",
        "source": "Google review",
        "stars": 5,
        "text": "Jarrod and his team did a fantastic job at my house very satisfied "
                "with the results and how professional he is , would highly "
                "recommend this company",
    },
    {
        "name": "Miranda",
        "source": "Google review",
        "stars": 5,
        "text": "We had an epoxy floor installed in our shed conversion and it’s "
                "completely transformed the space. It looks great and is super easy "
                "to maintain. Jarrod was super helpful and efficient, the finish is "
                "high quality. Really happy with the result and would definitely "
                "recommend.",
    },
    {
        "name": "Miranda Bell",
        "source": "Google review",
        "stars": 5,
        "topic": "stone",  # stone polishing, not a floor coating: kept off the landing page
        "text": "I recently had the pleasure of working with Jarred from Floor Candy "
                "and I couldn’t be happier with the results. His expertise in natural "
                "stone polishing is outstanding—he restored our stone surfaces to a "
                "beautiful, high-quality finish that…",
    },
]

# --------------------------------------------------------------------------
# IMAGES, genuine Floor Candy photography only.
# See docs/ASSET-PROVENANCE.md. Nothing generated is used as project proof.
# --------------------------------------------------------------------------
IMG = {
    # Generated illustration (Higgsfield), used as the hero backdrop only, on
    # Zach's explicit instruction. It is NEVER presented as a Floor Candy job:
    # it carries no project caption and is not used as og:image. See
    # docs/ASSET-PROVENANCE.md.
    "hero_generated": {"base": "hero-garage", "w": [720, 1080, 1376],
                       "avif": [720, 1080, 1376], "ratio": (1376, 768),
                       "alt": ""},
    "flake_hero":  {"base": "garage-flake-finished", "w": [720, 1080, 1440, 1920],
                    "avif": [1080, 1440, 1920], "ratio": (1920, 864),
                    "alt": "Completed grey flake epoxy garage floor by Floor Candy"},
    "flake_wide":  {"base": "garage-flake-finished", "w": [480, 720, 1080, 1440],
                    "avif": [1080, 1440], "ratio": (1440, 648),
                    "alt": "Finished flake epoxy garage floor, grey blend"},
    "prep_grind":  {"base": "prep-grind", "w": [600, 900, 1200], "avif": [600, 900, 1200],
                    "ratio": (1200, 992),
                    "alt": "Floor Candy grinding a concrete driveway with dust extraction running"},
    "prep_extract": {"base": "prep-grinding-extraction", "w": [400, 600, 900], "avif": [],
                     "ratio": (900, 2000),
                     "alt": "Floor grinder and dust extractor in use on a Floor Candy job"},
    "polished":    {"base": "polished-concrete-finished", "w": [400, 600, 900], "avif": [],
                    "ratio": (900, 2000),
                    "alt": "Finished polished concrete interior floor by Floor Candy"},
    "driveway":    {"base": "driveway-sealed", "w": [600, 900, 1440], "avif": [],
                    "ratio": (1440, 648),
                    "alt": "Sealed concrete driveway completed by Floor Candy"},
    "solid":       {"base": "finish-solid-414", "w": [], "avif": True, "ratio": (414, 414),
                    "alt": "Solid colour coating on an alfresco slab, masking still down"},
}

# Square 414px work photos, all genuine.
HERO_PICTURE = """<picture>
<source media="(max-width: 860px)" type="image/webp" srcset="/assets/img/hero-garage-portrait-414.webp 414w, /assets/img/hero-garage-portrait-600.webp 600w, /assets/img/hero-garage-portrait-752.webp 752w, /assets/img/hero-garage-portrait-1128.webp 1128w" sizes="100vw">
<source media="(max-width: 860px)" type="image/jpeg" srcset="/assets/img/hero-garage-portrait-414.jpg 414w, /assets/img/hero-garage-portrait-600.jpg 600w, /assets/img/hero-garage-portrait-752.jpg 752w, /assets/img/hero-garage-portrait-1128.jpg 1128w" sizes="100vw">
<source type="image/avif" srcset="/assets/img/hero-garage-720.avif 720w, /assets/img/hero-garage-1080.avif 1080w, /assets/img/hero-garage-1376.avif 1376w" sizes="100vw">
<source type="image/webp" srcset="/assets/img/hero-garage-720.webp 720w, /assets/img/hero-garage-1080.webp 1080w, /assets/img/hero-garage-1376.webp 1376w" sizes="100vw">
<img src="/assets/img/hero-garage-1376.jpg" width="1376" height="768" alt="Illustration of a garage with a high-gloss flake epoxy floor" fetchpriority="high" decoding="async">
</picture>"""

WORK = [
    ("shopfit-flake-after", "Cream and tan flake floor"),
    ("work-flake-garage", "Flake epoxy garage floor"),
    ("work-flake-cream",  "Cream flake epoxy floor"),
    ("work-flake-tan",    "Tan flake epoxy floor"),
    ("work-flake-brick",  "Flake epoxy floor beside brickwork"),
    ("work-drive-dark",   "Dark sealed concrete driveway"),
    ("work-drive-blue",   "Sealed concrete driveway"),
    ("work-path-light",   "Sealed concrete path"),
    ("work-alfresco",     "Coated alfresco slab"),
    ("shopfit-substrate", "Existing floor ground back before coating"),
]

# --------------------------------------------------------------------------
# BEFORE / AFTER, verified pairs only.
# Any spec left None is omitted from the caption. No placeholders ship.
# --------------------------------------------------------------------------
BA = {
    "garage": {
        "before": "garage-epoxy-floor-before", "after": "garage-epoxy-floor-after",
        "w": [400, 600, 800, 1024], "avif": True, "ratio": (1024, 768),
        "title": "Garage: flake epoxy floor",
        "before_label": "Before", "after_label": "Completed",
        "alt_before": "Bare, stained concrete garage slab before coating",
        "alt_after": "The same garage finished in a grey flake epoxy floor",
        "note": "The same garage, photographed from the same position before and after.",
        "specs": {"Service": "Flake epoxy", "Suburb": None, "Floor size": None,
                  "System": None, "Existing condition": None},
    },
    "prep": {
        "before": "ba-garage-before", "after": "ba-garage-after",
        "w": [414], "avif": True, "ratio": (414, 414),
        "title": "Garage: during preparation, then finished",
        "before_label": "During prep", "after_label": "Completed",
        "alt_before": "Garage floor part-way through mechanical preparation",
        "alt_after": "The same garage floor finished in flake epoxy",
        "note": "The first frame is labelled during prep because the dust extractor "
                "is still in shot, it is not an untouched before.",
        "specs": {"Service": "Flake epoxy", "Suburb": None, "Floor size": None},
    },
    "shopfit": {
        "before": "shopfit-tiled-before", "after": "shopfit-flake-after",
        "w": [414, 600, 900, 1242], "avif": False, "ratio": (1242, 897),
        "title": "Tiled floor to flake",
        "before_label": "Before", "after_label": "Completed",
        "alt_before": "Old tiled floor before work started, dust extractor in shot",
        "alt_after": "The same room finished in a cream and tan flake floor",
        "note": "The same room, before the job and after it. The two frames are from "
                "slightly different positions, the finished shot is closer to the "
                "floor, so read it as the same space, not the same camera mark.",
        "specs": {"Service": "Flake epoxy", "Suburb": None, "Floor size": None,
                  "System": None, "Existing condition": None},
    },
}

# --------------------------------------------------------------------------
# CASE STUDIES
# The reusable project record. Every field below may be None, and the renderer
# omits anything without a value, so an unconfirmed suburb or floor size is
# structurally incapable of reaching the page. Fill a field in, rebuild, done.
# Suburbs are blank because these photographs came off a phone with no job
# record attached. Jarrod's Facebook page attributes jobs to Taree, Forster and
# Old Bar, which is the route to filling them in. See QUESTIONS-FOR-JARROD 5.3.
# --------------------------------------------------------------------------
CASES = [
    {
        "slug": "tiled-floor-to-flake",
        "title": "Tiled floor to flake",
        "h1": "A tiled floor taken back and re-laid in flake",
        "meta_title": "Case Study: Tiled Floor to Flake | Floor Candy",
        "meta": "A tiled floor ground back and finished in a cream and tan flake "
                "system, photographed at four stages, start to finish.",
        "lede": "The most completely documented job we have. A tired tiled floor, "
                "photographed before anything was touched, part-way through "
                "preparation, back to bare substrate, and finished.",
        "service": "premium-flake-flooring",
        "suburb": None, "region": None, "floor_size": None, "system": None,
        "install_date": None, "testimonial": None,
        "existing": "An old tiled floor, grouted, worn, in a space being brought back "
                    "into use.",
        "finish": "A cream and tan flake blend with a clear topcoat.",
        "ba": "shopfit",
        "stages": [
            ("shopfit-masked", "Before: the tiled floor as we found it",
             "The floor before anything was touched. Tiles across the full floor, with the "
             "extraction gear staged in the back corner ready to start."),
            ("shopfit-prepped", "Part-way through preparation",
             "The same room mid-preparation. This is the stage that does not appear on "
             "most flooring websites, because it is the stage that is neither the "
             "problem nor the result."),
            ("shopfit-substrate", "Back to substrate",
             "The old surface taken back so the new system had something real to bond "
             "to. Dust extraction running throughout, the extractor is visible at "
             "the back of frame."),
            ("shopfit-flake-after", "Finished: cream and tan flake",
             "The completed floor. One seamless surface across the room, with no grout "
             "lines left to collect anything."),
        ],
        "why": ("Why this one is worth showing",
                "<p>Because it is the argument this business is built on, in "
                "photographs. The finished floor took hours. Everything before it, "
                "the tiles coming off, the substrate being taken back, the dust being "
                "pulled out of the air, is what decides whether that floor is still "
                "there in ten years.</p>"
                "<p>It is also an honest answer to a question we get asked constantly: "
                "can you coat over tiles? We do not. Tiles move in ways coatings do not "
                "forgive. What we do is take the floor back to something that will "
                "hold, and this job is what that looks like.</p>"),
    },
    {
        "slug": "garage-bare-slab-to-flake",
        "title": "Garage: bare slab to flake",
        "h1": "Garage: a stained slab finished in grey flake",
        "meta_title": "Case Study: Garage Floor, Bare Slab to Flake | Floor Candy",
        "meta": "A stained, bare garage slab prepared and finished in a grey flake "
                "epoxy system. Photographed from the same position before and after.",
        "lede": "A standard double garage, photographed from the same spot before the "
                "job and after it. No staging, no brightening, no borrowed photographs.",
        "service": "garage-epoxy-flooring",
        "suburb": None, "region": None, "floor_size": None, "system": None,
        "install_date": None, "testimonial": None,
        "existing": "A bare, stained slab of the kind most garages have, never "
                    "sealed, and carrying everything that had been spilled on it.",
        "finish": "A grey flake blend with a clear topcoat.",
        "ba": "garage",
        "stages": [
            ("work-flake-garage", "The finished floor",
             "Flake broadcast through the coating and sealed under a clear topcoat, so "
             "the texture is in the floor rather than printed on it."),
        ],
        "why": ("Why this one is worth showing",
                "<p>Because it is the most ordinary job on this page, and that is the "
                "point. Most of what we do is exactly this: a slab nobody has ever "
                "looked after, in a garage that gets used.</p>"
                "<p>The pair is shot from the same position on two different days. "
                "That is a deliberately boring claim, and it is the one most "
                "before-and-afters on flooring websites cannot make.</p>"),
    },
]
CASE_BY_SLUG = {c["slug"]: c for c in CASES}

# --------------------------------------------------------------------------
# SERVICES
# --------------------------------------------------------------------------
SERVICES = [
    {
        "slug": "premium-flake-flooring",
        "nav": "Premium flake",
        "short": "Premium flake flooring",
        "h1": "Premium flake flooring",
        "title": "Premium Flake Flooring Taree & Forster | Floor Candy",
        "meta": "Premium flake epoxy flooring for garages and homes across Taree, "
                "Forster and the Mid North Coast. Double garages from $2,450*. "
                "Free on-site quote.",
        "lede": "The finish most people picture when they think of a coated garage "
                "floor, a hard-wearing base, flake broadcast through it, and a "
                "clear topcoat over the lot.",
        "img": "flake_wide",
        "intent": "premium flake flooring",
        "primary": True,
        "body": [
            ("What a flake floor actually is",
             ["<p>A flake floor is built in layers. The coating goes down, decorative "
              "flake is broadcast into it while it is still wet, and a clear topcoat "
              "seals everything in. The flake is what gives the floor its depth and "
              "its texture underfoot, it is not a pattern printed on the surface, it "
              "is suspended in the floor itself.</p>",
              "<p>It is the most popular choice for garages because it hides the "
              "ordinary marks a working garage collects, gives grip underfoot, and "
              "does not show every speck of dust the way a plain colour does.</p>"]),
            ("Choosing a colour and blend",
             ["<p>Flake comes in blends rather than single colours: greys, creams, "
              "tans and mixes of them. We will bring what we have to the on-site "
              "quote so you can look at the options against your own walls and light, "
              "which is the only way to judge it properly. Photographs of floors on a "
              "screen are not a reliable guide.</p>"]),
            ("Where the result is actually decided",
             ["<p>The visible part of a flake floor takes hours. What decides whether "
              "it is still there in ten years is the preparation underneath it, and "
              "that happens before any coating comes out of the tin. We will not quote "
              "a flake floor without looking at the slab first.</p>"]),
        ],
        "faqs": [
            ("Is a flake floor slippery?",
             "The flake gives the surface texture, which helps underfoot compared with "
             "a smooth gloss finish. Any floor is more slippery wet than dry. Tell us "
             "how the space is used at the quote and we will talk through the finish "
             "that suits it."),
            ("Can I pick the flake colour?",
             "Yes. Flake comes in blends, and we bring the options to the on-site quote "
             "so you can see them in your own space rather than on a screen."),
            ("Will it hide marks in the concrete?",
             "A flake floor is much better at disguising ordinary variation in a slab "
             "than a solid colour is. It does not make structural problems disappear, "
             "cracks and damage are dealt with during preparation, and we will tell you "
             "at the quote what can be repaired and what will still be visible."),
        ],
        "related": ["garage-epoxy-flooring", "concrete-preparation-crack-repair", "residential-epoxy-flooring"],
    },
    {
        "slug": "garage-epoxy-flooring",
        "nav": "Garage floors",
        "short": "Garage epoxy flooring",
        "h1": "Garage epoxy flooring",
        "title": "Garage Epoxy Flooring Taree & Forster | Floor Candy",
        "meta": "Epoxy garage floor coatings across Taree, Forster, Harrington and the "
                "Mid North Coast. Double garages from $2,450*. Mechanically prepared "
                "concrete, fixed written price.",
        "lede": "Garage floors are the bulk of what we do, single, double and "
                "oversized, in new builds and in slabs that have been worked on for "
                "twenty years.",
        "img": "flake_hero",
        "intent": "garage epoxy flooring",
        "body": [
            ("What a garage floor has to survive",
             ["<p>A garage slab takes more abuse than almost any other floor in a "
              "house. Hot tyres sit on it, oil and fuel land on it, things get dropped "
              "on it, and it is usually the least sealed concrete on the property, so "
              "it holds dust and stains.</p>",
              "<p>A coating fixes all of that, but only if it stays stuck down. Tyre "
              "pickup, peeling and lifting are almost always a preparation problem, "
              "not a product problem.</p>"]),
            ("What we will want to see",
             ["<p>At the quote we look at what the slab is actually doing: whether "
              "there is an existing coating or sealer, whether there are cracks and "
              "how they are moving, whether there is any sign of moisture coming "
              "through, and how you use the space. A garage that stores a boat and a "
              "workbench is a different job to one that parks two cars.</p>"]),
        ],
        "faqs": [
            ("How much is a double garage?",
             "Double garage floors start from approximately $2,450. Final pricing "
             "depends on floor size, existing condition, preparation requirements, "
             "finish and location."),
            ("Do I need to empty the garage?",
             "Yes. The floor needs to be completely clear, vehicles, shelving, "
             "anything standing on the slab. We will tell you at the quote how much "
             "time to allow."),
            ("Can you coat over an existing epoxy or paint?",
             "Sometimes, and sometimes the existing coating has to come off first. It "
             "depends on what is on there and how well it is stuck down. That is one "
             "of the things we check on site before quoting."),
        ],
        "related": ["premium-flake-flooring", "concrete-preparation-crack-repair", "solid-colour-epoxy-flooring"],
    },
    {
        "slug": "residential-epoxy-flooring",
        "nav": "Residential",
        "short": "Residential epoxy flooring",
        "h1": "Residential epoxy flooring",
        "title": "Residential Epoxy Flooring Taree & Forster | Floor Candy",
        "meta": "Epoxy and concrete floor coatings for interiors, sheds and converted "
                "spaces across the Mid North Coast and NSW. Free on-site assessment, "
                "fixed written price.",
        "lede": "Interiors, sheds, studios and converted spaces, anywhere the concrete "
                "is the floor you are keeping rather than something you cover up.",
        "img": "polished",
        "intent": "residential epoxy flooring",
        "body": [
            ("Rooms that suit a coated floor",
             ["<p>Shed conversions, studios, laundries, rumpus rooms and workshops all "
              "work well. The floor is seamless, so there is no grout to clean and "
              "nowhere for dust to collect, and it takes furniture and foot traffic "
              "without much thought.</p>",
              "<p>One of our Google reviews is a shed conversion, and it is a fair "
              "description of what this service is for: a space that was concrete and "
              "is now a room.</p>"]),
            ("Living with it",
             ["<p>An interior floor gets looked at more closely than a garage floor, in "
              "better light, by people who are not wearing boots. We will talk through "
              "the finish and the level of sheen at the quote, because the same "
              "system can read very differently in a north-facing room than it does in "
              "a shed.</p>"]),
        ],
        "faqs": [
            ("Can you coat over tiles or timber?",
             "We coat concrete. Tiles and timber move in ways that coatings do not "
             "cope with, so if there is something over the slab we will tell you at "
             "the quote what the options are, in most cases the existing surface needs "
             "to come up first."),
            ("How long before we can use the room?",
             "It depends on the system and the conditions on the day. We will give you "
             "the timeline in writing with your quote rather than a general figure "
             "here, because temperature and humidity genuinely change it."),
        ],
        "related": ["premium-flake-flooring", "solid-colour-epoxy-flooring", "concrete-preparation-crack-repair"],
    },
    {
        "slug": "outdoor-epoxy-flooring",
        "nav": "Outdoor",
        "short": "Outdoor epoxy flooring",
        "h1": "Outdoor concrete coatings",
        "title": "Outdoor Concrete Coatings Taree & Forster | Floor Candy",
        "meta": "Driveways, paths, patios and alfresco slabs sealed and coated across "
                "Taree, Forster and the Mid North Coast. Free on-site assessment.",
        "lede": "Driveways, paths, patios and alfresco slabs, the concrete that takes "
                "the weather and usually looks it.",
        "img": "driveway",
        "intent": "outdoor concrete coating",
        "body": [
            ("Coastal concrete has a harder time",
             ["<p>Outdoor slabs on this coast deal with salt air, hard sun and heavy "
              "rain in the same year. Untreated concrete is porous, so it takes up "
              "water and whatever is dissolved in it, and that is what produces the "
              "staining and surface breakdown people usually call us about.</p>",
              "<p>Sealing closes the surface. It also makes the slab far easier to "
              "wash down, which matters more than most people expect on a driveway "
              "under trees.</p>"]),
            ("Grip matters more outside",
             ["<p>An outdoor surface gets wet, so finish and texture are a safety "
              "decision rather than a style one. We will talk through it on site, a "
              "pool surround, a steep driveway and a covered alfresco are three "
              "different problems.</p>"]),
        ],
        "faqs": [
            ("Will sealing stop my driveway cracking?",
             "No. Sealing protects the surface; it does not change what the slab is "
             "doing structurally. Existing cracks are repaired where appropriate "
             "during preparation, and we will tell you honestly which ones will still "
             "be visible."),
            ("Can you do pool surrounds and patios?",
             "Yes, those are outdoor concrete like any other, though grip and finish "
             "need more thought. Send photos and we will tell you whether it suits."),
        ],
        "related": ["concrete-preparation-crack-repair", "solid-colour-epoxy-flooring", "premium-flake-flooring"],
    },
    {
        "slug": "solid-colour-epoxy-flooring",
        "nav": "Solid colour",
        "short": "Solid colour epoxy",
        "h1": "Solid colour epoxy flooring",
        "title": "Solid Colour Epoxy Flooring Taree & Forster | Floor Candy",
        "meta": "Solid colour epoxy floors for garages, sheds and alfresco slabs across "
                "the Mid North Coast and NSW. Free on-site assessment, fixed written price.",
        "lede": "A single, even colour with nothing broadcast through it. Cleaner and "
                "more uniform than flake, and less forgiving, which is worth knowing "
                "before you choose it.",
        "img": "solid",
        "intent": "solid colour epoxy flooring",
        "body": [
            ("When solid colour is the right call",
             ["<p>Solid colour suits spaces where you want the floor to read as one "
              "clean surface, an alfresco slab, a laundry, a shed you want to feel "
              "finished rather than industrial.</p>",
              "<p>It is worth being straight about the trade-off: a solid colour shows "
              "dust, marks and any variation in the slab more than a flake floor does. "
              "If the space is a working garage, flake is usually the better choice, "
              "and we will say so.</p>"]),
        ],
        "faqs": [
            ("Solid colour or flake?",
             "Flake hides ordinary marks and gives more grip; solid colour looks "
             "cleaner and more uniform but shows more. For a working garage we "
             "usually suggest flake. For an alfresco or a laundry, solid colour often "
             "reads better."),
        ],
        "related": ["premium-flake-flooring", "residential-epoxy-flooring", "outdoor-epoxy-flooring"],
    },
    {
        "slug": "concrete-preparation-crack-repair",
        "nav": "Preparation & repair",
        "short": "Concrete preparation & crack repair",
        "h1": "Concrete preparation & crack repair",
        "title": "Concrete Preparation & Crack Repair Taree & Forster | Floor Candy",
        "meta": "Mechanical concrete preparation and crack repair before coating. The "
                "stage that decides whether an epoxy floor lasts. Mid North Coast & NSW.",
        "lede": "The part of the job nobody photographs, and the part that decides "
                "whether the floor is still stuck down in ten years.",
        "img": "prep_grind",
        "intent": "concrete preparation and crack repair",
        "body": [
            ("Why coatings fail",
             ["<p>When a coated floor lifts, peels or picks up under tyres, the cause "
              "is almost never the coating itself. It is that the coating was put onto "
              "a surface it could not properly key into, a sealed slab, a dusty slab, "
              "a slab with an old coating still on it, or one with moisture moving "
              "through it.</p>",
              "<p>Preparation is how that is dealt with. The slab is mechanically "
              "prepared rather than just cleaned, so the new system has something "
              "real to bond to.</p>"]),
            ("Cracks",
             ["<p>Cracks are repaired where appropriate. We are deliberately careful "
              "with that wording: a repair stops a crack being an open path through "
              "the coating, but it does not undo whatever the slab is doing "
              "structurally, and a repaired crack can still be visible in the finished "
              "floor.</p>",
              "<p>We would rather tell you that at the quote than have you find out "
              "after the job.</p>"]),
            ("What you get either way",
             ["<p>The on-site assessment is free, and you get our written read on the "
              "concrete whether or not you go ahead with us. If the honest answer is "
              "that your slab needs something we do not do, you will be told.</p>"]),
        ],
        "faqs": [
            ("Do you repair cracks before coating?",
             "Cracks are repaired where appropriate as part of preparation. A repair "
             "stops the crack being an open path through the coating, but it does not "
             "change what the slab is doing structurally, and it can still be visible "
             "in the finished floor. We tell you which is which at the quote."),
            ("What preparation is required on my floor?",
             "That depends entirely on the slab, its age, whether anything has been "
             "put on it before, how it has been used and whether there is any moisture "
             "moving through it. It is the main thing the free on-site assessment is "
             "for, and it is why we do not quote from a photo alone."),
        ],
        "related": ["premium-flake-flooring", "garage-epoxy-flooring", "outdoor-epoxy-flooring"],
    },
]
SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}

# --------------------------------------------------------------------------
# SERVICE AREAS
# Each page is written individually. No suburb-swapped duplicates.
# --------------------------------------------------------------------------
LOCATIONS = [
    {
        "slug": "taree",
        "name": "Taree",
        "region": "Manning Valley",
        "title": "Epoxy Flooring Taree | Garage & Concrete Coatings | Floor Candy",
        "meta": "Epoxy and flake flooring in Taree and the Manning Valley. Garage "
                "floors, driveways and interiors. Double garages from $2,450*. Free "
                "on-site quote.",
        "h1": "Epoxy flooring Taree",
        "lede": "Premium flake and epoxy flooring for garages, homes and suitable "
                "commercial spaces across Taree and the Manning Valley.",
        "intro": [
            "<p>Taree is close to home for us, which means a Taree job does not carry "
            "the travel loading that a job three hours away does. If you are in town "
            "or anywhere in the Manning Valley, we can usually get to you for an "
            "on-site look without much notice.</p>",
            "<p>Most of what we are asked for here is garage floors, both in the "
            "newer estates on the edges of town and in older houses where the slab has "
            "been bare for decades. Those are quite different jobs, and the difference "
            "shows up in the preparation rather than in the coating.</p>",
        ],
        "local": ("What we see on Taree slabs",
                  "<p>Older Taree garages often have a slab that has never been sealed "
                  "and has spent years absorbing whatever landed on it. Newer builds "
                  "more often have a curing compound on the surface that has to be "
                  "removed before anything will bond. Neither is a problem, but they "
                  "need different preparation, and that is decided on site, not from a "
                  "photograph.</p>"),
        "nearby": ["Wingham", "Old Bar", "Cundletown", "Tinonee", "Harrington", "Forster"],
        "services": ["premium-flake-flooring", "garage-epoxy-flooring", "outdoor-epoxy-flooring",
                     "concrete-preparation-crack-repair"],
        "faqs": [
            ("Do you charge travel to Taree?",
             "Taree is one of our core areas, so pricing here is our standard pricing. "
             "Double garage floors start from approximately $2,450."),
            ("How quickly can you look at my floor?",
             "Taree and the Manning Valley are close enough that we can usually "
             "arrange a free on-site assessment without a long wait. Call "
             "0435 193 845 and we will tell you honestly what the current timing is."),
        ],
    },
    {
        "slug": "forster",
        "name": "Forster",
        "region": "Great Lakes",
        "title": "Epoxy Flooring Forster & Tuncurry | Garage Floors | Floor Candy",
        "meta": "Epoxy and flake flooring in Forster, Tuncurry and the Great Lakes. "
                "Garage floors, driveways and coastal concrete. Double garages from "
                "$2,450*. Free on-site quote.",
        "h1": "Epoxy flooring Forster",
        "lede": "Premium flake and epoxy flooring for garages, homes and suitable "
                "commercial spaces across Forster, Tuncurry and surrounding areas.",
        "intro": [
            "<p>Forster and Tuncurry sit either side of the water, and between them "
            "they cover most of what we get asked for in the Great Lakes, garages in "
            "permanent homes, floors in holiday houses being tidied up between "
            "seasons, and outdoor concrete that has taken more salt air than it was "
            "ever sealed for.</p>",
            "<p>The coastal position genuinely changes the job. Concrete this close to "
            "the water spends its life damp and salted, and both of those affect how a "
            "coating bonds.</p>",
        ],
        "local": ("Salt air, humidity and holiday houses",
                  "<p>Two things come up repeatedly in Forster. The first is moisture: "
                  "a slab that never fully dries out is a slab a coating can lift off, "
                  "so it is one of the things we look for before quoting. The second is "
                  "access, a lot of Forster and Tuncurry work is in houses that are "
                  "only occupied part of the year, and it is usually easier to do a "
                  "floor properly when nobody is living around it.</p>"),
        "nearby": ["Tuncurry", "Pacific Palms", "Blueys Beach", "Smiths Lake", "Green Point", "Taree"],
        "services": ["premium-flake-flooring", "garage-epoxy-flooring", "outdoor-epoxy-flooring",
                     "residential-epoxy-flooring"],
        "faqs": [
            ("Do you cover Tuncurry as well as Forster?",
             "Yes, Forster and Tuncurry are the same trip for us, and both are core "
             "service areas."),
            ("Can you work on a holiday house while we are not there?",
             "Usually, yes, provided access is arranged and the floor is clear. Tell "
             "us at the quote how the property is used and we will work around it."),
        ],
    },
    {
        "slug": "harrington",
        "name": "Harrington",
        "region": "Manning Valley",
        "title": "Epoxy Flooring Harrington NSW | Floor Candy",
        "meta": "Epoxy and flake flooring in Harrington and the lower Manning. Garage "
                "floors, driveways and coastal concrete. Free on-site quote, fixed "
                "written price.",
        "h1": "Epoxy flooring Harrington",
        "lede": "Premium flake and epoxy flooring for garages, homes and suitable "
                "commercial spaces in Harrington and the lower Manning.",
        "intro": [
            "<p>Harrington is a small town, and small towns are often badly served for "
            "trades like this, the work is real but there is not enough of it in one "
            "spot to interest an operator based two hours away. We are close enough "
            "that a Harrington job is a normal job.</p>",
            "<p>Being at the river mouth, a lot of the concrete here is exposed and "
            "weathered, and driveways and paths come up as often as garages do.</p>",
        ],
        "local": ("River-mouth exposure",
                  "<p>Concrete at Harrington gets sun, salt and wind in combination, "
                  "and outdoor slabs show it faster than they do further inland. Sealing "
                  "will not reverse weathering that has already happened, but on a slab "
                  "that is still sound it closes the surface and makes it far easier to "
                  "keep clean.</p>"),
        "nearby": ["Crowdy Head", "Coopernook", "Taree", "Old Bar", "Wingham"],
        "services": ["outdoor-epoxy-flooring", "garage-epoxy-flooring", "premium-flake-flooring",
                     "concrete-preparation-crack-repair"],
        "faqs": [
            ("Is Harrington too small a job to bother with?",
             "No. Harrington is inside our core service area and is priced as such."),
            ("My driveway is weathered rather than cracked, is that fixable?",
             "Often, yes. Surface weathering on a slab that is otherwise sound is "
             "exactly what sealing is for. We will look at it and tell you honestly "
             "whether it is worth doing."),
        ],
    },
    {
        "slug": "blueys-beach",
        "name": "Blueys Beach",
        "region": "Great Lakes",
        "title": "Epoxy Flooring Blueys Beach | Floor Candy",
        "meta": "Epoxy and flake flooring at Blueys Beach and the surrounding Great "
                "Lakes coast. Garage floors, alfresco slabs and outdoor concrete. Free "
                "on-site quote.",
        "h1": "Epoxy flooring Blueys Beach",
        "lede": "Premium flake and epoxy flooring for garages, homes and outdoor "
                "concrete at Blueys Beach and along the Great Lakes coast.",
        "intro": [
            "<p>Blueys is holiday-house country, and the floors follow from that: "
            "garages that sit unused for months, alfresco slabs that do a lot of "
            "entertaining in a short window, and outdoor concrete permanently within "
            "reach of sea air.</p>",
            "<p>Houses here are often architect-designed and finished to a standard "
            "that makes a bare or patchy slab stand out. That is usually why people "
            "call.</p>",
        ],
        "local": ("Floors that sit empty, then get hammered",
                  "<p>A holiday-house floor has an unusual life, long quiet periods, "
                  "then heavy use. It is a good argument for doing the preparation "
                  "properly, because the failure mode on a neglected slab tends to show "
                  "up exactly when the house is full.</p>"),
        "nearby": ["Pacific Palms", "Boomerang Beach", "Elizabeth Beach", "Smiths Lake", "Forster"],
        "services": ["premium-flake-flooring", "outdoor-epoxy-flooring", "residential-epoxy-flooring",
                     "solid-colour-epoxy-flooring"],
        "faqs": [
            ("Can you quote while we are not at the property?",
             "Yes, provided we can get access to the floor. Send photos first and we "
             "will tell you what else we need."),
            ("Does sea air affect the finished floor?",
             "It affects the concrete underneath more than the finished coating. A "
             "sealed floor is easier to keep clean in a salt-air environment, which is "
             "part of the point."),
        ],
    },
    {
        "slug": "pacific-palms",
        "name": "Pacific Palms",
        "region": "Great Lakes",
        "title": "Epoxy Flooring Pacific Palms | Floor Candy",
        "meta": "Epoxy and flake flooring at Pacific Palms and the Great Lakes coast. "
                "Garage floors, alfresco slabs and driveways. Free on-site quote, fixed "
                "written price.",
        "h1": "Epoxy flooring Pacific Palms",
        "lede": "Premium flake and epoxy flooring for garages, homes and outdoor "
                "concrete across Pacific Palms and the surrounding coast.",
        "intro": [
            "<p>Pacific Palms covers a scattered run of houses between the lake and the "
            "beaches, and access is often the first thing worth talking about, steep "
            "driveways, long approaches and tight garages are normal here.</p>",
            "<p>Outdoor work comes up as often as garages: driveways that drop away "
            "sharply, and alfresco slabs that are the main living space for half "
            "the year.</p>",
        ],
        "local": ("Steep driveways and grip",
                  "<p>On a sloped driveway the finish is a safety decision, not a "
                  "styling one. A slick sealed surface on a steep approach is a genuine "
                  "problem in wet weather, so grip is something we raise before you have "
                  "to ask.</p>"),
        "nearby": ["Blueys Beach", "Boomerang Beach", "Smiths Lake", "Forster", "Tuncurry"],
        "services": ["outdoor-epoxy-flooring", "premium-flake-flooring", "garage-epoxy-flooring",
                     "solid-colour-epoxy-flooring"],
        "faqs": [
            ("My driveway is steep, will a sealed surface be slippery?",
             "It is the right question to ask. Finish and texture are chosen with the "
             "slope and the weather in mind, and we will raise it at the quote."),
            ("Do you cover Boomerang and Elizabeth Beach?",
             "Yes, they are the same trip as Pacific Palms and Blueys."),
        ],
    },
    {
        "slug": "newcastle",
        "name": "Newcastle",
        "region": "Hunter",
        "title": "Epoxy Flooring Newcastle & Hunter | Floor Candy",
        "meta": "Floor Candy takes selected epoxy and flake flooring projects in "
                "Newcastle and the Hunter. Garage floors and concrete coatings. Talk to "
                "us about size and timing.",
        "h1": "Epoxy flooring Newcastle",
        "lede": "We take selected projects in Newcastle and the Hunter, decided by job "
                "size and timing rather than offered as a standing local service.",
        "intro": [
            "<p>We should be straight about how Newcastle works for us. Floor Candy is "
            "based on the Mid North Coast, so Newcastle and the Hunter are travel "
            "jobs rather than a local run. We do take them, and we have taken them, "
            "but whether we can depends on the size of the floor and what else is "
            "scheduled that week.</p>",
            "<p>If you are in Newcastle, the honest position is this: ask. If it works, "
            "you get the same job anyone else gets. If it does not, we will tell you "
            "quickly rather than string it out.</p>",
        ],
        "local": ("What makes a Newcastle job work",
                  "<p>Travel has to be commercially viable, which in practice means "
                  "Newcastle and Hunter jobs generally start around $2,600 and larger "
                  "floors are easier to make work than small ones. If you have "
                  "neighbours or a couple of properties wanting the same thing, that "
                  "changes the maths considerably, it is worth mentioning when you "
                  "call.</p>"),
        "nearby": ["Maitland", "Lake Macquarie", "Port Stephens", "Hunter Region"],
        "services": ["premium-flake-flooring", "garage-epoxy-flooring",
                     "concrete-preparation-crack-repair", "residential-epoxy-flooring"],
        "faqs": [
            ("Do you actually service Newcastle?",
             "We take selected projects there. It is not a standing local service, and "
             "we would rather say so than pretend otherwise. Call and we will tell you "
             "straight away whether your job works."),
            ("Why is there a higher starting price for Newcastle?",
             "Travel has to be commercially viable. Regional and travel-heavy jobs "
             "generally start around $2,600, against approximately $2,450 for a double "
             "garage in our core area."),
        ],
    },
]
LOCATION_BY_SLUG = {l["slug"]: l for l in LOCATIONS}


# --------------------------------------------------------------------------
# Additional per-town content. Kept separate from the LOCATIONS table above so
# it is obvious this is the material that makes each page genuinely local —
# the uniqueness gate in tools/seo-audit.py enforces that it stays that way.
# --------------------------------------------------------------------------
_LOCAL_EXTRA = {
    "taree": {
        "intro3": "<p>Because we are close, we can also be practical about "
                  "timing. A Taree job does not have to be batched with three "
                  "others to be worth the drive, so small floors get the same "
                  "attention as large ones.</p>",
        "who": ("Who calls us in Taree",
                "<p>Three groups, mostly. Tradespeople with a workshop shed who "
                "are tired of sweeping dust that never stops coming; families in "
                "the newer estates on the edge of town who want the garage "
                "finished properly rather than left as builder&rsquo;s concrete; and "
                "people who have just bought an older place and discovered the "
                "slab under the boxes is stained, dusty and never sealed.</p>"
                "<p>Out towards Wingham and the rural blocks it is usually "
                "machinery sheds and large shed floors, where the priority is a "
                "surface that can be hosed rather than swept.</p>"),
        "faqs": [
            ("Do you do shed and workshop floors, not just garages?",
             "Yes. Shed and workshop slabs are common around Taree and the "
             "Manning Valley, and they are the same job as a garage floor, the "
             "preparation is what changes, because a shed slab has often had a "
             "harder life than a house garage."),
            ("Can you work around a slab that is still in use?",
             "Not really, the floor needs to be clear and stay clear while the "
             "system cures. What we can do is plan the timing around you, which "
             "is easier in Taree than anywhere else we work because we are not "
             "travelling in."),
        ],
    },
    "forster": {
        "intro3": "<p>Forster also has a lot of double and oversized garages "
                  "used as genuine storage (boats, trailers, fishing gear) "
                  "rather than just parking. That changes what the floor has to "
                  "put up with, and it is worth mentioning when you call.</p>",
        "who": ("Who calls us in Forster and Tuncurry",
                "<p>A lot of owner-occupiers finishing a garage they have been "
                "meaning to sort out for years, and a steady number of "
                "holiday-home owners who want the work done between tenancies. "
                "We also get people downsizing into low-maintenance places who "
                "want a floor they can mop rather than one that sheds dust into "
                "the house.</p>"
                "<p>Boat and trailer storage comes up more here than anywhere "
                "else we work. Hull supports, jockey wheels and dragged gear are "
                "point loads and scrapes rather than general wear, so it is worth "
                "telling us that is the plan before we specify anything.</p>"),
        "faqs": [
            ("Will the coating handle a boat trailer being dragged on it?",
             "Tell us that is the use before we quote. Point loads and dragging "
             "are different to tyre traffic, and it changes what makes sense for "
             "your floor. It is a normal request in Forster and Tuncurry."),
            ("Is humidity near the water a problem for the job?",
             "It affects timing more than outcome. Moisture in the slab and "
             "humidity on the day both matter, which is why we look at the "
             "concrete before quoting rather than after."),
        ],
    },
    "harrington": {
        "intro3": "<p>It is also a town where word travels. If a neighbour has "
                  "had a driveway done and you are considering the same, mention "
                  "it, doing two nearby properties in one trip is genuinely "
                  "easier for us and we would rather pass that on.</p>",
        "who": ("Who calls us in Harrington",
                "<p>Mostly long-term residents and retirees, and the work skews "
                "outdoors: driveways, paths and the concrete around the house "
                "rather than garage interiors. A lot of it is concrete that was "
                "poured decades ago, never sealed, and has spent every year since "
                "in sun and salt wind.</p>"
                "<p>The question we are usually asked here is whether a slab is "
                "worth treating at all or whether it is past it. That is a fair "
                "question and it deserves a straight answer, which is what the "
                "free on-site look is for.</p>"),
        "faqs": [
            ("How do I know if my old driveway is worth sealing?",
             "If the surface is weathered but the slab is structurally sound, "
             "sealing is usually worth doing. If the concrete is breaking up or "
             "moving, it may not be. We will tell you which one you have, and we "
             "will say so if the answer is no."),
            ("Can you do two properties in the same street together?",
             "Yes, and it helps. Neighbouring jobs on one trip are more efficient "
             "for us, which matters in a town the size of Harrington. Mention it "
             "when you call."),
        ],
    },
    "blueys-beach": {
        "intro3": "<p>Access and timing matter more here than the floor itself. "
                  "Most of the properties we look at are booked for large parts "
                  "of the year, so the work has to fit a window rather than the "
                  "other way round.</p>",
        "who": ("Who calls us at Blueys",
                "<p>Owners and, increasingly, the people who manage these houses "
                "on their behalf. The brief is usually the same: the house is "
                "finished to a high standard everywhere except the garage and the "
                "outdoor slab, and those two are letting it down in photographs "
                "as much as in use.</p>"
                "<p>Alfresco and outdoor concrete is a bigger share of the work "
                "at Blueys than it is inland. It is the part of a holiday house "
                "that actually gets used, and it is also the part taking the most "
                "weather.</p>"),
        "faqs": [
            ("We only get to the house occasionally, can you still quote?",
             "Yes. Send photos and your suburb first, and we will tell you what "
             "else we need. We will still want to see the slab before a final "
             "price, but we can do a lot of the groundwork before you are up."),
            ("Can the work be done between bookings?",
             "Usually. Tell us the window when you enquire and we will be honest "
             "about whether it is enough time for the floor you want, rather than "
             "starting something we cannot finish."),
        ],
    },
    "pacific-palms": {
        "intro3": "<p>Because properties here are spread out, we will usually "
                  "ask a couple of questions about access before booking a look, "
                  "not to put you off, just so we arrive with the right "
                  "gear.</p>",
        "who": ("Who calls us at Pacific Palms",
                "<p>A mix of permanent residents and part-time owners, and the "
                "work splits fairly evenly between garages and outdoor concrete. "
                "Houses here often sit below or above the road, so the driveway "
                "is a real piece of infrastructure rather than a strip of "
                "concrete, and it is frequently the thing people want "
                "addressed first.</p>"
                "<p>Alfresco slabs are the other common one. They tend to be the "
                "main living space through summer, which makes finish and grip a "
                "more considered decision than it would be in a garage.</p>"),
        "faqs": [
            ("Is access a problem for the equipment?",
             "Rarely, but it is worth talking about. Steep or long driveways and "
             "tight garages are normal around Pacific Palms, and knowing in "
             "advance means we turn up set up for it."),
            ("Can you match a finish to an existing outdoor area?",
             "We can talk through options at the quote and bring what we have so "
             "you can hold it against what is already there. Matching in daylight "
             "on site is the only reliable way to judge it."),
        ],
    },
    "newcastle": {
        "intro3": "<p>We would rather be useful than vague about this, so the "
                  "rest of this page explains what makes a Newcastle job work "
                  "and what does not, instead of implying we are around the "
                  "corner.</p>",
        "who": ("What we tend to take on in Newcastle",
                "<p>Larger residential floors, multiple floors at one property, "
                "or a couple of jobs that can be done on the same trip. Builders "
                "and renovators with more than one slab to coat are the easiest "
                "fit, because the travel is spread across the work.</p>"
                "<p>What rarely works is a single small garage on its own. It is "
                "not that we do not want it, it is that we would have to price "
                "it in a way that is not fair to you, and you will get a better "
                "deal from someone based in the Hunter. We will say that plainly "
                "rather than quote a number designed to be declined.</p>"),
        "faqs": [
            ("Would we be better off with a Newcastle-based installer?",
             "For a single small floor, quite possibly, and we will tell you so. "
             "For larger work, or several floors at once, we are genuinely "
             "competitive and we travel for it."),
            ("How far in advance do you need to know?",
             "More notice than in our core area, because a Newcastle trip has to "
             "be scheduled around Mid North Coast work. Call early and we can "
             "usually find a window."),
        ],
    },
}

for _l in LOCATIONS:
    _e = _LOCAL_EXTRA[_l["slug"]]
    _l["intro"] = _l["intro"] + [_e["intro3"]]
    _l["who"] = _e["who"]
    _l["faqs"] = _l["faqs"] + _e["faqs"]


AREA_LIST = ["Taree", "Forster", "Tuncurry", "Harrington", "Blueys Beach",
             "Pacific Palms", "Newcastle", "Hunter Region"]
AREA_LINKS = {"Taree": "taree", "Forster": "forster", "Harrington": "harrington",
              "Blueys Beach": "blueys-beach", "Pacific Palms": "pacific-palms",
              "Newcastle": "newcastle"}

# --------------------------------------------------------------------------
# GUIDES
# Called "Guides", not "Blog", see docs/CONTENT-BRIEFS.md. House rules from
# that brief are enforced here: no guide quotes a product name, a cure time or
# a warranty, because QUESTIONS-FOR-JARROD.md section 3 is unanswered. The one
# price that appears is the confirmed $2,450 double-garage starting figure.
# --------------------------------------------------------------------------
GUIDES = [
    {
        "slug": "what-changes-the-price-of-an-epoxy-garage-floor",
        "title": "What Changes the Price of an Epoxy Garage Floor | Floor Candy",
        "h1": "What changes the price of an epoxy garage floor",
        "meta": "Double garages start from approximately $2,450. Here is what moves "
                "the number up or down: size, existing condition, preparation, "
                "finish and location.",
        "lede": "Double garage floors start from approximately $2,450. That is a real "
                "starting point, not a teaser, but five things move it, and it is "
                "worth knowing which before you compare quotes.",
        "img": "flake_wide",
        "img_alt": "Finished flake epoxy garage floor by Floor Candy",
        "date": "2026-09-21",
        "body": [
            ("The short answer",
             ["<p>A double garage starts from approximately $2,450. Whether your floor "
              "lands near that or well above it comes down to five variables, and any "
              "quote that ignores them is guessing.</p>",
              "<p>We give you a fixed written price after looking at the slab. Not "
              "before, because until someone has stood on your concrete, nobody can "
              "tell you what it needs.</p>"]),
            ("1. Floor size",
             ["<p>The obvious one, and the least interesting. A bigger floor costs more, "
              "but not proportionally: the set-up, the preparation equipment and the "
              "travel are much the same whether the slab is 32m&sup2; or 42m&sup2;. This "
              "is why very small floors can feel expensive per square metre and large "
              "ones feel like better value.</p>"]),
            ("2. The condition it is in now",
             ["<p>This is the variable that moves a price most, and the one people are "
              "least able to judge from the doorway. A slab that has been sealed, "
              "painted or coated before has to have that dealt with first. So does one "
              "that is dusty, contaminated with oil, or carrying a curing compound from "
              "the day it was poured.</p>",
              "<p>Two garages that look identical can be very different jobs once you "
              "know what has been on the floor.</p>"]),
            ("3. How much preparation it needs",
             ["<p>Preparation is not a line item you can trim. It is the part of the job "
              "that decides whether the floor is still stuck down in ten years, which is "
              "why we treat it as the job rather than as preparation for it.</p>",
              "<p>Cracks are repaired where appropriate. Moisture moving through a slab "
              "is a different problem again, and one worth knowing about before you "
              "commit rather than after.</p>"]),
            ("4. The finish you choose",
             ["<p>A flake floor and a solid colour are different amounts of work. So is "
              "a floor that has to match something already in the space. We bring the "
              "options to the on-site quote so you can see them in your own light, "
              "screens are not a reliable guide to a floor.</p>"]),
            ("5. Where you are",
             ["<p>Taree, Forster, Tuncurry, Harrington, Blueys Beach and Pacific Palms "
              "are our core areas and are priced as such. Travel-heavy work, including "
              "Newcastle and the Hunter, has to be commercially viable and generally "
              "starts around $2,600.</p>"]),
            ("What a fair quote looks like",
             ["<p>It is written down. It follows someone actually looking at your slab. "
              "It says what preparation is included rather than leaving it vague. And "
              "it does not change on the day.</p>",
              "<p>If a quote arrives without anyone seeing the floor, what you have is "
              "an estimate with a price attached, and the gap between the two usually "
              "appears once work starts.</p>"]),
        ],
        "related": ["garage-epoxy-flooring", "premium-flake-flooring",
                    "concrete-preparation-crack-repair"],
    },
    {
        "slug": "why-epoxy-floors-fail",
        "title": "Why Epoxy Floors Fail (And What Prevents It) | Floor Candy",
        "h1": "Why epoxy floors fail",
        "meta": "Peeling, lifting and tyre pickup are almost never the coating's fault. "
                "What actually causes an epoxy floor to fail, and what prevents it.",
        "lede": "When a coated floor lifts, peels or picks up under hot tyres, the "
                "coating is almost never the problem. The problem is what it was asked "
                "to stick to.",
        "img": "prep_grind",
        "img_alt": "Floor Candy grinding a concrete surface with dust extraction running",
        "date": "2026-09-21",
        "body": [
            ("Failure is a bonding problem, not a product problem",
             ["<p>Coatings are engineered to stick to concrete. What they cannot do is "
              "stick to something sitting on top of concrete, a sealer, a curing "
              "compound, an old coating, dust, or a film of oil worked into the surface "
              "over years.</p>",
              "<p>Put a good system onto any of those and it will bond to the layer "
              "rather than the slab. It will look perfect on handover and let go "
              "later, usually in the busiest part of the floor first.</p>"]),
            ("The three ways it shows up",
             ["<p><strong>Peeling and flaking.</strong> The coating separates in sheets "
              "or patches. Almost always a bond failure at the slab.</p>",
              "<p><strong>Tyre pickup.</strong> Hot tyres lift the coating where a car "
              "parks. A garage-specific symptom, and again a bonding issue rather than "
              "a durability one.</p>",
              "<p><strong>Bubbling or blistering.</strong> Often moisture moving up "
              "through the slab with nowhere to go. This one is worth identifying "
              "before any coating goes down, because it does not resolve itself.</p>"]),
            ("What prevents it",
             ["<p>Preparing the slab mechanically rather than just cleaning it, so the "
              "system has raw concrete to key into. Dealing with whatever is already on "
              "the floor instead of coating over it. Repairing cracks where that is "
              "appropriate. And checking for moisture before, not after.</p>",
              "<p>None of that is visible in the finished floor, which is exactly why "
              "it is the first thing a cheap quote leaves out.</p>"]),
            ("How to tell whether a quote includes it",
             ["<p>Ask what preparation is included and listen for a specific answer. "
              "Ask what happens if there is an existing coating. Ask what they do if "
              "they find moisture.</p>",
              "<p>You are not testing their chemistry. You are testing whether they "
              "have looked at your floor and thought about it.</p>"]),
        ],
        "related": ["concrete-preparation-crack-repair", "garage-epoxy-flooring",
                    "premium-flake-flooring"],
    },
    {
        "slug": "flake-or-solid-colour",
        "title": "Flake or Solid Colour? Choosing an Epoxy Finish | Floor Candy",
        "h1": "Flake or solid colour?",
        "meta": "Flake hides marks and adds grip; solid colour reads cleaner but shows "
                "more. An honest comparison for garages, sheds and alfresco slabs.",
        "lede": "The two finishes people choose between most often. They are not better "
                "and worse, they are suited to different rooms, and the wrong one in "
                "the right room is the usual regret.",
        "img": "flake_wide",
        "img_alt": "Flake epoxy floor finished by Floor Candy",
        "date": "2026-09-21",
        "body": [
            ("What flake actually is",
             ["<p>Decorative flake is broadcast into the coating while it is still wet, "
              "then sealed under a clear topcoat. The flake sits <em>in</em> the floor "
              "rather than printed on it, which is where the depth and the texture "
              "underfoot come from.</p>"]),
            ("Where flake wins",
             ["<p>Working garages, sheds and workshops. It disguises the ordinary "
              "variation in a slab, hides the marks a busy floor collects, and the "
              "texture helps underfoot compared with a smooth gloss.</p>",
              "<p>It is also more forgiving of a slab that is sound but not "
              "beautiful, which describes most garage floors.</p>"]),
            ("Where solid colour wins",
             ["<p>Alfresco slabs, laundries, studios, and anywhere you want the floor "
              "to read as one clean surface rather than a texture.</p>",
              "<p>The trade-off is real and worth saying plainly: a solid colour shows "
              "dust, marks and any unevenness in the slab more than flake does. In a "
              "garage that gets used, most people are happier with flake, and we will "
              "say so at the quote even when solid colour was the original plan.</p>"]),
            ("Choosing a blend",
             ["<p>Flake comes in blends rather than single colours: greys, creams, "
              "tans and mixes of them. We bring what we have to the on-site quote, "
              "because the only reliable way to judge a floor finish is against your own "
              "walls, in your own light.</p>",
              "<p>A blend that looks perfect on a phone screen can read completely "
              "differently in a north-facing room.</p>"]),
            ("If you are still unsure",
             ["<p>Tell us how the space is actually used, parked on, worked in, "
              "entertained in, hosed down. That answers the question faster than a "
              "colour chart does.</p>"]),
        ],
        "related": ["premium-flake-flooring", "solid-colour-epoxy-flooring",
                    "residential-epoxy-flooring"],
    },
    {
        "slug": "questions-to-ask-before-accepting-an-epoxy-quote",
        "title": "7 Questions to Ask Before Accepting an Epoxy Quote | Floor Candy",
        "h1": "Seven questions to ask before you accept an epoxy quote",
        "meta": "How to compare epoxy flooring quotes properly, the questions that "
                "separate a real price from a number designed to win the job.",
        "lede": "Most epoxy quotes look alike on paper. These are the questions that "
                "tell you which one has actually been thought about, and you should "
                "ask us the same ones.",
        "img": "prep_extract",
        "img_alt": "Floor grinder and dust extractor in use on a Floor Candy job",
        "date": "2026-09-21",
        "body": [
            ("1. Have you seen the floor?",
             ["<p>The single most useful question. A price given without anyone standing "
              "on the slab is an estimate wearing a quote's clothing, and the difference "
              "shows up as a variation once work starts.</p>"]),
            ("2. What preparation is included?",
             ["<p>Listen for something specific about <em>your</em> floor rather than a "
              "general description of how coatings work. Preparation is where the money "
              "and the outcome both sit.</p>"]),
            ("3. What happens if you find an existing coating?",
             ["<p>Plenty of slabs have had something on them. The answer should already "
              "exist before the job starts, not be discovered on the day and priced as "
              "an extra.</p>"]),
            ("4. What happens if you find moisture?",
             ["<p>Moisture moving through a slab will defeat a coating regardless of "
              "how good the product is. A quoter who has not considered it has not "
              "finished looking at your floor.</p>"]),
            ("5. Is the price fixed?",
             ["<p>Ask directly, and ask what would change it. A fixed written price is "
              "a commitment; a starting price is a conversation.</p>"]),
            ("6. What will still be visible when it is finished?",
             ["<p>Cracks are repaired where appropriate, but a repair does not undo "
              "what the slab is doing structurally and some remain visible. You want "
              "that conversation before the job, not after.</p>"]),
            ("7. Who is actually doing the work?",
             ["<p>Worth asking of anyone, including us. We are owner-led and Jarrod is "
              "on the tools; we also use subcontractors on some jobs, and we would "
              "rather tell you that than promise something we cannot always guarantee.</p>"]),
            ("What we do with these",
             ["<p>Our free on-site assessment exists to answer one to six before you "
              "commit to anything, and you get that written read on your concrete "
              "whether or not you go ahead with us.</p>"]),
        ],
        "related": ["concrete-preparation-crack-repair", "garage-epoxy-flooring",
                    "premium-flake-flooring"],
    },
]
GUIDE_BY_SLUG = {g["slug"]: g for g in GUIDES}

PROCESS = [
    ("Tell us about the floor",
     "Call, or send the form and text us a couple of photos. Photos help us understand the "
     "existing floor and the preparation it is likely to need before we turn up."),
    ("We assess what it needs",
     "A free on-site look at the slab, its condition, any existing coating, cracks, "
     "and how the space is used. You get a written read on your concrete and a fixed "
     "price, whether or not you go ahead with us."),
    ("Preparation comes first",
     "The slab is mechanically prepared so the system has something to bond to, and "
     "cracks are repaired where appropriate. This is the stage that decides the "
     "outcome."),
    ("The flooring system goes down",
     "The coating is applied, flake is broadcast if that is the finish you have "
     "chosen, and a clear topcoat seals it in."),
    ("Final handover",
     "We walk the finished floor with you before the balance is paid, and tell you "
     "when it is ready to use."),
]

HOME_FAQS = [
    ("How much does epoxy flooring cost?",
     "It depends on the size of the floor, the condition it is in, how much "
     "preparation it needs, the finish you choose and where you are. Double garage "
     "floors start from approximately $2,450. We give you a fixed written price after "
     "looking at the slab, and we do not publish a per-square-metre rate we cannot "
     "stand behind."),
    ("How much is a double garage?",
     "From approximately $2,450. Final pricing depends on floor size, existing "
     "condition, preparation requirements, finish and location. Regional and "
     "travel-heavy jobs generally start around $2,600."),
    ("How long does installation take?",
     "It varies with the size of the floor, its condition and the weather, "
     "preparation on a difficult slab can take longer than the coating does. You get "
     "the timeline for your floor in writing with your quote rather than a general "
     "figure here."),
    ("How long does an epoxy floor last?",
     ("A properly prepared floor lasts for many years. The honest answer depends "
      "almost entirely on the preparation underneath and how the floor is used. "
      "Our written warranty terms: " + WARRANTY_TERMS) if WARRANTY_TERMS else
     ("A properly prepared floor lasts for many years. We are not putting a number on "
      "it, because the honest answer depends almost entirely on the preparation "
      "underneath and how the floor is used, and because we have no written warranty "
      "terms to point you at yet.")),
    ("Is epoxy flooring slippery?",
     "A smooth gloss finish is more slippery wet than dry. A flake floor has texture "
     "through it, which helps. Tell us how the space is used and we will talk through "
     "the finish that suits it, it matters more outdoors and on slopes."),
    ("Do you repair cracks first?",
     "Cracks are repaired where appropriate as part of preparation. A repair stops the "
     "crack being an open path through the coating, but it does not change what the "
     "slab is doing structurally and it can still be visible. We tell you which is "
     "which before you commit."),
    ("What preparation is required?",
     "That depends on your slab, its age, whether anything has been applied to it "
     "before, how it has been used, and whether moisture is moving through it. "
     "Establishing that is the main purpose of the free on-site assessment, and it is "
     "why we will not quote a floor from photos alone."),
    ("Can I choose colours or flake finishes?",
     "Yes. Flake comes in blends of greys, creams, tans and mixes, and solid colours "
     "are available too. We bring the options to the on-site quote so you can see them "
     "in your own space and light."),
    ("What areas do you service?",
     "Taree, Forster, Tuncurry, Harrington, Blueys Beach, Pacific Palms and the "
     "Mid North Coast are our core areas. We take selected projects in Newcastle and "
     "the Hunter, decided by job size and timing. Not sure if we cover you? Send your "
     "postcode."),
    ("Can I send photos for a quote?",
     "Please do. Text them to 0435 193 845 or attach them to an email. Photos help us understand "
     "the existing floor and the preparation required, and they make the on-site visit "
     "faster. They do not replace it: we quote off the slab, not off a picture."),
]


# ==========================================================================
# RENDER HELPERS
# ==========================================================================
GOOGLE_G = ('<svg class="g-mark" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
            '<path fill="#4285F4" d="M45.1 24.5c0-1.6-.1-2.8-.4-4H24v7.4h12.1c-.2 2-1.6 5-4.5 7l-.1.3 6.5 5 .5.1c4.1-3.8 6.6-9.4 6.6-15.8"/>'
            '<path fill="#34A853" d="M24 46c5.9 0 10.9-2 14.5-5.3l-6.9-5.4c-1.9 1.3-4.4 2.2-7.6 2.2-5.8 0-10.7-3.8-12.5-9.1l-.3.1-6.8 5.2-.1.2C7.9 41 15.4 46 24 46"/>'
            '<path fill="#FBBC05" d="M11.5 28.4c-.5-1.4-.7-2.9-.7-4.4s.3-3 .7-4.4v-.3l-6.9-5.3-.2.1C2.9 17 2 20.4 2 24s.9 7 2.4 10z"/>'
            '<path fill="#EA4335" d="M24 10.5c4.1 0 6.9 1.8 8.5 3.3l6.2-6C34.9 4.3 29.9 2 24 2 15.4 2 7.9 7 4.4 14l7.1 5.5c1.8-5.3 6.7-9 12.5-9"/>'
            '</svg>')
GOOGLE_G_LG = GOOGLE_G.replace('class="g-mark"', 'class="g-mark g-mark--lg"')
WHATSAPP_ICON = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">'
                 '<path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm4.52 13.99c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.24-.64.8-.78.97-.15.16-.29.18-.53.06-.25-.13-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.01-.38.11-.5.11-.11.25-.29.37-.44.13-.15.17-.25.25-.41.09-.17.04-.31-.02-.44-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43h-.47c-.16 0-.43.06-.65.31-.22.25-.85.84-.85 2.04 0 1.2.87 2.36.99 2.53.12.16 1.71 2.61 4.15 3.66.58.25 1.03.4 1.39.51.58.19 1.11.16 1.53.1.47-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.15-1.18-.06-.11-.22-.17-.47-.29Z"/>'
                 '</svg>')

FACEBOOK_ICON = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">'
                 '<path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.96h-1.51c-1.49 0-1.96.93-1.96 1.89v2.26h3.33l-.53 3.49h-2.8V24C19.61 23.1 24 18.1 24 12.07"/>'
                 '</svg>')


def esc(s):
    return html.escape(str(s), quote=True)


def v(asset):
    return "%s?v=%d" % (asset, ASSET_V)


def picture(key, sizes, cls="", loading="lazy", fetchpriority=None, alt=None):
    """Responsive <picture> from the IMG table."""
    d = IMG[key]
    base, widths, ratio = d["base"], d["w"], d["ratio"]
    alt = alt if alt is not None else d["alt"]
    avif = d.get("avif")
    out = ["<picture>"]

    if widths:
        if avif and avif is not True:
            srcs = ", ".join("/assets/img/%s-%d.avif %dw" % (base, w, w) for w in avif)
            out.append('<source type="image/avif" srcset="%s" sizes="%s">' % (srcs, sizes))
        srcs = ", ".join("/assets/img/%s-%d.webp %dw" % (base, w, w) for w in widths)
        out.append('<source type="image/webp" srcset="%s" sizes="%s">' % (srcs, sizes))
        jpgs = ", ".join("/assets/img/%s-%d.jpg %dw" % (base, w, w) for w in widths)
        src = "/assets/img/%s-%d.jpg" % (base, widths[-1])
        attrs = 'srcset="%s" sizes="%s" src="%s"' % (jpgs, sizes, src)
    else:
        if avif:
            out.append('<source type="image/avif" srcset="/assets/img/%s.avif">' % base)
        out.append('<source type="image/webp" srcset="/assets/img/%s.webp">' % base)
        attrs = 'src="/assets/img/%s.jpg"' % base

    extra = ' fetchpriority="%s"' % fetchpriority if fetchpriority else ""
    load = "" if loading == "eager" else ' loading="lazy" decoding="async"'
    out.append('<img %s width="%d" height="%d" alt="%s"%s%s%s>' %
               (attrs, ratio[0], ratio[1], esc(alt),
                (' class="%s"' % cls) if cls else "", load, extra))
    out.append("</picture>")
    return "".join(out)


NO_AVIF = ("shopfit-",)


def square(base, alt, sizes="(min-width:900px) 260px, 45vw"):
    avif = "" if base.startswith(NO_AVIF) else (
        '<source type="image/avif" srcset="/assets/img/%s-414.avif" sizes="%s">' % (base, sizes))
    return ("<picture>" + avif +
            '<source type="image/webp" srcset="/assets/img/%s-414.webp" sizes="%s">'
            '<img src="/assets/img/%s-414.jpg" width="414" height="414" alt="%s" '
            'loading="lazy" decoding="async"></picture>'
            % (base, sizes, base, esc(alt)))


def ba_block(key, heading_level="h3", sizes="(min-width:900px) 560px, 92vw", lazy=True):
    """Before/after comparison. Specs with a None value are omitted entirely."""
    d = BA[key]
    w, ratio = d["w"], d["ratio"]
    biggest = w[-1]
    sfx = lambda name, ext: "/assets/img/%s-%d.%s" % (name, biggest, ext) if len(w) > 1 \
        else "/assets/img/%s-%d.%s" % (name, w[0], ext)

    def srcset(name, ext):
        return ", ".join("/assets/img/%s-%d.%s %dw" % (name, x, ext, x) for x in w)

    def frame(name, alt, cls=""):
        avif = ('<source type="image/avif" srcset="%s" sizes="%s">'
                % (srcset(name, "avif"), sizes)) if d.get("avif") else ""
        return ("<picture>" + avif +
                '<source type="image/webp" srcset="%s" sizes="%s">'
                '<img srcset="%s" sizes="%s" src="%s" width="%d" height="%d" alt="%s"'
                '%s%s></picture>'
                % (srcset(name, "webp"), sizes,
                   srcset(name, "jpg"), sizes, sfx(name, "jpg"),
                   ratio[0], ratio[1], esc(alt),
                   ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"',
                   (' class="%s"' % cls) if cls else ""))

    specs = [(k, val) for k, val in d["specs"].items() if val]
    spec_html = ""
    if specs:
        spec_html = ('<ul class="ba-specs">%s</ul>'
                     % "".join("<li>%s: %s</li>" % (esc(k), esc(val)) for k, val in specs))

    uid = "ba-" + key
    return """<figure class="ba-item">
<div class="ba" data-ba>
<div class="ba-frame">%s<div class="ba-after">%s</div><div class="ba-handle" style="left:50%%"></div></div>
<span class="ba-tag ba-tag--before">%s</span><span class="ba-tag ba-tag--after">%s</span>
<label class="visually-hidden" for="%s">Reveal the finished floor</label>
<input id="%s" type="range" min="0" max="100" value="50" step="1" aria-label="Reveal the finished floor">
</div>
<figcaption class="ba-caption">
<%s>%s</%s>%s
<p class="ba-note">%s</p>
</figcaption>
</figure>""" % (frame(d["before"], d["alt_before"]),
                frame(d["after"], d["alt_after"]),
                esc(d["before_label"]), esc(d["after_label"]),
                uid, uid,
                heading_level, esc(d["title"]), heading_level, spec_html,
                esc(d["note"]))


ICONS = {
    # 24x24 line icons, stroke = currentColor. Decorative only.
    "g1": '<path d="M3 10 12 4l9 6v10H3z"/><rect x="7" y="12" width="10" height="8"/>',
    "g2": '<path d="M2 10 12 4l10 6v10H2z"/><rect x="4.5" y="12" width="6.5" height="8"/><rect x="13" y="12" width="6.5" height="8"/>',
    "g3": '<path d="M1.5 10 12 4l10.5 6v10h-21z"/><rect x="3" y="12" width="5" height="8"/><rect x="9.5" y="12" width="5" height="8"/><rect x="16" y="12" width="5" height="8"/>',
    "patio": '<path d="M3 20h18M5 20v-6h14v6M4 14l8-6 8 6M12 8V4"/>',
    "shed": '<path d="M4 20V9l8-5 8 5v11zM9 20v-6h6v6"/>',
    "home": '<path d="M3 11 12 4l9 7M5 10v10h14V10M10 20v-5h4v5"/>',
    "comm": '<path d="M3 20V8h18v12zM3 8l3-4h12l3 4M8 20v-6h8v6"/>',
    "other": '<circle cx="12" cy="12" r="8"/><path d="M12 8v8M8 12h8"/>',
}


def icon(key):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linejoin="round" stroke-linecap="round" aria-hidden="true" '
            'focusable="false">%s</svg>' % ICONS[key])


def chips(name, options, required=False):
    return "".join(
        '<label class="chip"><input type="radio" name="%s" value="%s"%s><span>%s</span></label>'
        % (name, esc(o), " required" if required and i == 0 else "", esc(o))
        for i, o in enumerate(options))


def quote_form(form_id="quote", heading="Get my free quote"):
    """Four-step lead form, under a minute on a phone.

    Progressive enhancement: without JS every step is visible and the form
    posts to Formspree like any other form. main.js turns it into a stepper,
    saves progress to localStorage, sends with fetch, and redirects to
    /thank-you. No file field: Formspree's free plan rejects uploads, and a
    rejected upload would lose the whole lead. Photos go by text instead."""
    fid = form_id
    cards = "".join(
        '<label class="tcard"><input type="radio" name="floor_type" value="%s"%s>'
        '<span class="tcard-in">%s<span>%s</span></span></label>'
        % (esc(val), " required" if i == 0 else "", icon(ic), esc(lab))
        for i, (val, lab, ic) in enumerate(FLOOR_TYPES))
    towns = "".join('<option value="%s">' % esc(t) for t in
                    ["Taree", "Forster", "Tuncurry", "Harrington", "Old Bar", "Wingham",
                     "Blueys Beach", "Pacific Palms", "Hallidays Point", "Diamond Beach",
                     "Tallwoods Village", "Coopernook", "Krambach", "Gloucester",
                     "Newcastle", "Port Macquarie"])
    heard = "".join('<option value="%s">%s</option>' % (esc(h), esc(h)) for h in HEARD)
    ballpark = ("Ballpark: double garages start from <strong>$%s</strong>, before your $%d "
                "new-customer saving. Your exact price comes after a free on-site look."
                % ("{:,}".format(PRICING["double_garage_from"]), OFFER["saving"]))
    return """<form class="qform" id="%(fid)s" data-quote data-steps action="%(action)s" method="POST" novalidate>
<div class="qform-head">
<h2 class="qform-title">%(heading)s</h2>
<p class="qform-sub">Four quick taps. Under a minute. No obligation.</p>
<div class="qprog" aria-hidden="true"><span class="qprog-bar"></span></div>
<p class="qstep-count" aria-live="polite">Step <span data-step-now>1</span> of 4</p>
</div>

<fieldset class="qstep" data-step="1">
<legend class="qstep-q">What are we coating?</legend>
<div class="tcards">%(cards)s</div>
</fieldset>

<fieldset class="qstep" data-step="2">
<legend class="qstep-q">Roughly how big, and when?</legend>
<p class="qlab" id="%(fid)s-size-l">Rough size</p>
<div class="chips" role="radiogroup" aria-labelledby="%(fid)s-size-l">%(sizes)s</div>
<p class="qlab" id="%(fid)s-when-l">When are you after it?</p>
<div class="chips" role="radiogroup" aria-labelledby="%(fid)s-when-l">%(timings)s</div>
<p class="ballpark" data-ballpark>%(ballpark)s</p>
</fieldset>

<fieldset class="qstep" data-step="3">
<legend class="qstep-q">Where is the floor?</legend>
<div class="field"><label for="%(fid)s-suburb">Suburb or postcode <span class="req">*</span></label>
<input id="%(fid)s-suburb" name="suburb" type="text" list="%(fid)s-towns" autocomplete="address-level2" required>
<datalist id="%(fid)s-towns">%(towns)s</datalist></div>
<div class="field"><label for="%(fid)s-detail">Anything we should know? <span class="hint">Optional. Old coating, cracks, oil stains, how it&rsquo;s used.</span></label>
<textarea id="%(fid)s-detail" name="project_details" rows="3"></textarea></div>
<p class="qnote">Got photos? Text them to <a href="sms:%(phone_href)s"><strong>%(phone)s</strong></a> after you send this. It speeds up the quote.</p>
</fieldset>

<fieldset class="qstep" data-step="4">
<legend class="qstep-q">Where should Jarrod send your quote?</legend>
<div class="field-row">
<div class="field"><label for="%(fid)s-name">First name <span class="req">*</span></label>
<input id="%(fid)s-name" name="name" type="text" autocomplete="given-name" required></div>
<div class="field"><label for="%(fid)s-mobile">Mobile <span class="req">*</span></label>
<input id="%(fid)s-mobile" name="mobile" type="tel" autocomplete="tel" inputmode="tel" required pattern="^\\s*(\\+?61|0)\\s*4(\\s*\\d){8}\\s*$" data-msg="Please enter an Australian mobile number starting with 04."></div>
</div>
<div class="field"><label for="%(fid)s-email">Email <span class="hint">Optional</span></label>
<input id="%(fid)s-email" name="email" type="email" autocomplete="email"></div>
<p class="qlab" id="%(fid)s-pref-l">Best way to reach you</p>
<div class="chips" role="radiogroup" aria-labelledby="%(fid)s-pref-l">
<label class="chip"><input type="radio" name="contact_preference" value="Call" checked><span>Call</span></label>
<label class="chip"><input type="radio" name="contact_preference" value="SMS"><span>Text</span></label>
<label class="chip"><input type="radio" name="contact_preference" value="WhatsApp"><span>WhatsApp</span></label>
</div>
<div class="field"><label for="%(fid)s-heard">How did you hear about us? <span class="hint">Optional</span></label>
<select id="%(fid)s-heard" name="heard_about"><option value="">Choose one</option>%(heard)s</select></div>
</fieldset>

<input type="hidden" name="_subject" value="New quote request: floorcandyepoxy.com">
<p class="hp" aria-hidden="true"><label>Leave this empty <input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></p>
<input type="hidden" name="page_url" value="">
<input type="hidden" name="referrer" value="">
<input type="hidden" name="landing_page" value="">
<input type="hidden" name="headline_variant" value="">
<input type="hidden" name="event_id" value="">

<div class="qnav">
<button class="btn btn--ghost qback" type="button" data-back hidden>Back</button>
<button class="btn btn--primary qnext" type="button" data-next hidden>Next</button>
<button class="btn btn--primary qsubmit" type="submit">Get my free quote</button>
</div>
<p class="qfoot">Free on-site assessment &middot; Fixed written price &middot; Or call <a href="tel:%(phone_href)s">%(phone)s</a></p>
<p class="form-status" role="status" aria-live="polite"></p>
</form>""" % {
        "fid": fid, "action": FORM_ENDPOINT, "heading": esc(heading), "cards": cards,
        "sizes": chips("approx_size", SIZES), "timings": chips("timing", TIMINGS),
        "ballpark": ballpark, "towns": towns, "heard": heard,
        "phone_href": BIZ["phone_href"], "phone": BIZ["phone_display"]}


def quote_entry(heading="Get a free quote on your floor"):
    """Compact entry: the step-1 cards as links into the full form on /contact.
    Used on every service, area, project and guide page via closer()."""
    links = "".join(
        '<a class="tcard tcard--link" href="/contact?type=%s#quote" data-ev="quote_entry">'
        '<span class="tcard-in">%s<span>%s</span></span></a>'
        % (quote_plus(val), icon(ic), esc(lab)) for val, lab, ic in FLOOR_TYPES)
    return """<div class="qentry">
<p class="qentry-q">%s <span>What are we coating?</span></p>
<div class="tcards tcards--entry">%s</div>
</div>""" % (esc(heading), links)


def faq_block(items, heading="Common questions", eyebrow_num=None, lede=None):
    inner = "".join(
        "<details><summary>%s</summary><div class=\"faq-a\"><p>%s</p></div></details>"
        % (esc(q), esc(a)) for q, a in items)
    eb = '<p class="eyebrow">FAQ</p>'
    ld = '<p class="lede">%s</p>' % esc(lede) if lede else ""
    return """<section class="section" aria-labelledby="faq-h">
<div class="wrap">
<div class="sec-head"><div>%s<h2 id="faq-h">%s</h2></div><div>%s</div></div>
<div class="faq">%s</div>
</div>
</section>""" % (eb, esc(heading), ld, inner)


def faq_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in items],
    }


MAP_EMBED = """<div class="map-frame">
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3381.609637146134!2d152.50482557524393!3d-32.052756027302344!2m3!1f0!2f0!3f0!3m2!1i1024!1i768!4f13.1!3m3!1m2!1s0x6b7435ea57496b4d%%3A0x46112d2c436f2682!2sFloor%%20Candy!5e0!3m2!1sen!2sau!4v1788943461550!5m2!1sen!2sau" loading="lazy" title="Floor Candy on Google Maps" width="100%%" height="300" style="border:0" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>
</div>
<p class="small muted mt-3"><a class="tlink" href="%s" rel="noopener">Get directions / see reviews</a> &middot; Floor Candy is a mobile operation with no public showroom, we come to the floor.</p>""" % GOOGLE_REVIEWS_URL


def map_section(heading="Floor Candy on Google"):
    return """<section class="section" aria-labelledby="map-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Google Business Profile</p><h2 id="map-h">%s</h2></div></div>
%s
</div>
</section>""" % (esc(heading), MAP_EMBED)


def areas_block(current=None, dark=False, heading="Where we work", num=None,
                show_map=False):
    items = []
    for a in AREA_LIST:
        slug = AREA_LINKS.get(a)
        if slug and slug != current:
            items.append('<li><a href="/service-areas/%s">%s</a></li>' % (slug, esc(a)))
        elif slug and slug == current:
            items.append("<li><span>%s</span></li>" % esc(a))
        else:
            items.append("<li><span>%s</span></li>" % esc(a))
    eb = '<p class="eyebrow">Service areas</p>'
    return """<section class="section %s" aria-labelledby="areas-h">
<div class="wrap">
<div class="sec-head"><div>%s<h2 id="areas-h">%s</h2></div>
<div><p class="lede">Taree, Forster, Tuncurry, Harrington, Blueys Beach, Pacific Palms and the Mid North Coast are our core areas. Newcastle and the Hunter are selected projects, decided by job size and timing.</p></div></div>
<ul class="areas">%s</ul>
<p class="small muted mt-3">Not sure if we cover your area? Send us your postcode and we&rsquo;ll let you know. <a class="tlink" href="/contact">Get in touch</a>.</p>
%s
</div>
</section>""" % ("band--ink" if dark else "", eb, esc(heading), "".join(items),
                 ('<div class="mt-4">%s</div>' % MAP_EMBED) if show_map else "")


def reviews_block(num=None, coatings_only=False, heading="What our customers say"):
    cards = []
    for r in REVIEWS:
        if coatings_only and r.get("topic"):
            continue
        cards.append("""<article class="review">
<div class="review-top">%s<span class="stars" aria-label="%d out of 5 stars">%s</span></div>
<blockquote>&ldquo;%s&rdquo;</blockquote>
<footer><span class="r-name">%s</span><span class="r-src">%s</span></footer>
</article>""" % (GOOGLE_G, r["stars"], "\u2605" * r["stars"], esc(r["text"]),
                 esc(r["name"]), esc(r["source"])))
    return """<section class="section" aria-labelledby="rev-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Reviews</p>
<h2 id="rev-h">%s</h2></div>
<div><p class="lede">Verified reviews from our Google Business Profile.</p></div></div>

<div class="rating-bar">
<div class="rating-badge">
%s
<div class="rb-body">
<span class="rb-score">%s<span class="rb-out">/ 5</span></span>
<span class="rb-stars" aria-label="Rated %s out of 5">%s</span>
<span class="rb-src">Google Reviews</span>
</div>
</div>
<div class="btn-row rating-cta">
<a class="btn btn--ghost" href="%s" rel="noopener">Read our Google reviews</a>
<a class="btn btn--primary" href="%s" rel="noopener" data-ev="review_click">Leave Jarrod a Google review</a>
</div>
</div>

<div class="reviews">%s</div>
</div>
</section>""" % (esc(heading), GOOGLE_G_LG, BIZ["rating"], BIZ["rating"], "\u2605" * 5,
                 GOOGLE_REVIEWS_URL, GOOGLE_WRITE_REVIEW_URL, "".join(cards))


def price_block(num=None, regional=True):
    eb = '<p class="eyebrow">Pricing</p>'
    reg = ('<p class="small muted mt-3">%s</p>' % esc(PRICING["regional_note"])) if regional else ""
    return """<section class="section band--paper2" aria-labelledby="price-h">
<div class="wrap">
<div class="sec-head"><div>%s<h2 id="price-h">What will my floor cost?</h2></div>
<div><p class="lede">A real starting point, and an honest note about what moves it.</p></div></div>
<div class="price-grid">
<div class="price-card">
<span class="p-lab">Double garage</span>
<p class="p-num">From $%s<sup>*</sup></p>
<p>%s</p>
%s
</div>
<div class="offer-card">
<span class="o-head">First Floor Candy job?</span>
<p class="o-save">Save $%d</p>
<p>New customers save $%d on their first floor. Mention it when you get in touch.</p>
<a class="btn btn--primary" href="/contact">Get an exact quote</a>
</div>
</div>
</div>
</section>""" % (eb, "{:,}".format(PRICING["double_garage_from"]),
                 esc(PRICING["qualifier"]), reg, OFFER["saving"], OFFER["saving"])


def closer(title="Get a fixed price on your floor", lede=None, ps=False):
    """Closing CTA on every page. Carries the compact quote entry (step-1 cards
    linking into the full form), so every service and area page has a one-tap
    route into the quote. The homepage passes ps=True for the P.S. recap."""
    lede = lede or ("Free on-site assessment. A written read on your concrete and a "
                    "fixed price, whether or not you go ahead with us.")
    ps_html = ""
    if ps:
        ps_html = ("""<div class="ps"><p><strong>P.S.</strong> Quick recap, in case you skipped
to the bottom: double garages start from <strong>$%s</strong>, new customers save
<strong>$%d</strong> on their first floor, and the on-site quote is free with a fixed written
price. Tap what you want coated above and it takes under a minute.</p></div>"""
                   % ("{:,}".format(PRICING["double_garage_from"]), OFFER["saving"]))
    return """<section class="section closer">
<div class="closer-media"><picture>
<source type="image/webp" srcset="/assets/img/flake-macro-600.webp 600w, /assets/img/flake-macro-900.webp 900w, /assets/img/flake-macro-1344.webp 1344w" sizes="100vw">
<img src="/assets/img/flake-macro-1344.jpg" width="1344" height="752" alt="" loading="lazy" decoding="async">
</picture></div>
<div class="wrap">
<h2>%s</h2>
<p class="lede">%s</p>
%s
<p class="closer-note">Rather talk? <a href="tel:%s">Call %s</a> &middot; %s &middot; New customers save $%d</p>
%s
</div>
</section>""" % (esc(title), esc(lede), quote_entry(""), BIZ["phone_href"], BIZ["phone_display"],
                 BIZ["hours"], OFFER["saving"], ps_html)


# ---------------------------------------------------------------- chrome ---
def nav_items(active):
    items = [("/premium-flake-flooring", "Premium flake"),
             ("/garage-epoxy-flooring", "Garage floors"),
             ("/projects", "Projects"),
             ("/guides", "Guides"),
             ("/service-areas", "Service areas"),
             ("/about", "About"),
             ("/contact", "Contact")]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if active == href else ""
        out.append('<li><a href="%s"%s>%s</a></li>' % (href, cur, esc(label)))
    return "".join(out)


def header(active):
    sub = "".join('<li><a href="/%s">%s</a></li>' % (s["slug"], esc(s["short"])) for s in SERVICES)
    loc = "".join('<li><a href="/service-areas/%s">%s</a></li>' % (l["slug"], esc(l["name"]))
                  for l in LOCATIONS)
    return """<header class="site-header">
<div class="wrap header-inner">
<a class="brand" href="/"><picture><source type="image/webp" srcset="/assets/logo-head.webp"><img src="/assets/logo-head.png" width="108" height="80" alt="Floor Candy"></picture></a>
<nav class="nav" aria-label="Main"><ul>%s</ul></nav>
<div class="header-cta">
<a class="header-tel" href="tel:%s">%s</a>
<a class="btn btn--primary" href="/contact">Free quote</a>
</div>
<button class="burger" type="button" aria-expanded="false" aria-controls="drawer"><span></span><span class="visually-hidden">Menu</span></button>
</div>
</header>
<div class="drawer" id="drawer" hidden>
<div class="drawer-in">
<div class="drawer-actions">
<a class="btn btn--primary btn--full" href="/contact">Get a free quote</a>
<a class="btn btn--ghost btn--full" href="tel:%s">Call %s</a>
</div>
<nav class="drawer-nav" aria-label="Site">
<ul>
<li><a href="/">Home</a></li>
<li>
<details class="drawer-group">
<summary>Services<span class="chev" aria-hidden="true"></span></summary>
<ul class="drawer-sub">%s</ul>
</details>
</li>
<li><a href="/projects">Projects</a></li>
<li><a href="/guides">Guides</a></li>
<li>
<details class="drawer-group">
<summary>Service areas<span class="chev" aria-hidden="true"></span></summary>
<ul class="drawer-sub">%s<li><a href="/service-areas">All service areas</a></li></ul>
</details>
</li>
<li><a href="/about">About</a></li>
<li><a href="/contact">Contact</a></li>
</ul>
</nav>
<div class="drawer-foot">
<a class="drawer-wa" href="%s" rel="noopener">%s Message us on WhatsApp</a>
<p class="drawer-meta">%s &middot; mobile service, no showroom<br>Taree &middot; Forster &middot; Harrington &middot; Blueys Beach &middot; Pacific Palms</p>
</div>
</div>
</div>
""" % (nav_items(active), BIZ["phone_href"], BIZ["phone_display"],
             BIZ["phone_href"], BIZ["phone_display"], sub, loc,
             WHATSAPP, WHATSAPP_ICON, BIZ["hours"])


def credential_lines():
    """Only renders what is confirmed. Everything unconfirmed stays invisible."""
    out = []
    c = CREDENTIALS
    if c["abn"]:
        out.append("ABN %s" % esc(c["abn"]))
    if c["licence_number"]:
        out.append("Licence %s" % esc(c["licence_number"]))
    if c["public_liability"]:
        out.append("%s public liability" % esc(c["public_liability"]))
    if c["warranty"]:
        out.append(esc(c["warranty"]))
    for a in c["accreditations"]:
        out.append(esc(a))
    return out


def footer():
    """Deliberately lean: brand, how to reach us, one column of links, legals.
    The six service pages and six town pages are reachable from the main nav and
    from their own index pages, so repeating all twelve here was weight without
    much benefit. tools/seo-audit.py checks nothing became an orphan."""
    creds = credential_lines()
    cred_html = ('<p class="small" style="margin-top:.5rem">%s</p>' % " \u00b7 ".join(creds)) if creds else ""
    return """<footer class="site-footer">
<div class="wrap">
<div class="footer-grid">
<div class="footer-brand">
<h2 class="visually-hidden">Floor Candy</h2>
<picture><source type="image/webp" srcset="/assets/logo-full.webp"><img class="footer-logo" src="/assets/logo-full.png" width="460" height="384" alt="Floor Candy epoxy flooring" loading="lazy" decoding="async"></picture>
<p class="small">Epoxy and concrete floor coatings across Taree, Forster, Harrington, Blueys Beach and the Mid North Coast.</p>
%s
</div>
<div class="footer-links">
<h3>Explore</h3>
<ul>
<li><a href="/premium-flake-flooring">Services</a></li>
<li><a href="/projects">Projects</a></li>
<li><a href="/guides">Guides</a></li>
<li><a href="/service-areas">Service areas</a></li>
<li><a href="/about">About</a></li>
<li><a href="/contact">Contact</a></li>
</ul>
</div>
<div class="footer-reach">
<h3>Get in touch</h3>
<div class="footer-contact">
<a href="tel:%s">%s</a>
<a href="mailto:%s">%s</a>
<a href="%s" rel="noopener">WhatsApp</a>
<span>%s &middot; mobile service, no showroom</span>
</div>
<ul class="social">
<li><a href="%s" rel="noopener" aria-label="Floor Candy on Facebook">%s<span>Facebook</span></a></li>
<li><a href="%s" rel="noopener" aria-label="Floor Candy reviews on Google">%s<span>Google</span></a></li>
</ul>
</div>
</div>
<div class="footer-base">
<p>&copy; 2026 Floor Candy. All rights reserved.</p>
<ul><li><a href="/privacy">Privacy</a></li><li><a href="/terms">Terms</a></li></ul>
</div>
</div>
</footer>
<a class="wa-float" href="%s" rel="noopener" data-ev="whatsapp_click">
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm0 18.15h-.01a8.2 8.2 0 0 1-4.19-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.18 8.18 0 0 1-1.26-4.38c0-4.54 3.7-8.23 8.25-8.23 2.2 0 4.27.86 5.83 2.41a8.18 8.18 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23Zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.24-.64.8-.78.97-.15.16-.29.18-.53.06-.25-.13-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.01-.38.11-.5.11-.11.25-.29.37-.44.13-.15.17-.25.25-.41.09-.17.04-.31-.02-.44-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43h-.47c-.16 0-.43.06-.65.31-.22.25-.85.84-.85 2.04 0 1.2.87 2.36.99 2.53.12.16 1.71 2.61 4.15 3.66.58.25 1.03.4 1.39.51.58.19 1.11.16 1.53.1.47-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.15-1.18-.06-.11-.22-.17-.47-.29Z"/></svg>
<span class="wa-label">WhatsApp us</span>
<span class="visually-hidden">Message Floor Candy on WhatsApp</span>
</a>
<div class="mobar">
<a href="tel:%s"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2Z"/></svg>Call</a>
<a href="sms:%s"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>Text</a>
<a class="mobar-cta" href="/contact#quote" data-quote-link>Get my free quote</a>
</div>""" % (cred_html, BIZ["phone_href"], BIZ["phone_display"], BIZ["email"], BIZ["email"],
             WHATSAPP, BIZ["hours"], SOCIAL["facebook"], FACEBOOK_ICON,
             GOOGLE_REVIEWS_URL, GOOGLE_G, WHATSAPP, BIZ["phone_href"], BIZ["phone_href"])


def crumbs(trail):
    """trail: list of (href|None, label). Last item is current."""
    lis, items = [], []
    for i, (href, label) in enumerate(trail):
        if href:
            lis.append('<li><a href="%s">%s</a></li>' % (href, esc(label)))
        else:
            lis.append('<li><span aria-current="page">%s</span></li>' % esc(label))
        items.append({"@type": "ListItem", "position": i + 1, "name": label,
                      **({"item": SITE + href} if href else {})})
    nav = ('<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap"><ol>%s</ol></div></nav>'
           % "".join(lis))
    schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}
    return nav, schema


def business_schema():
    node = {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "@id": SITE + "/#business",
        "name": BIZ["name"],
        "description": ("Epoxy flooring, flake flooring, concrete coatings and mechanical "
                        "concrete preparation servicing Taree, Forster, Harrington, Blueys "
                        "Beach and the Mid North Coast, with selected projects in Newcastle "
                        "and the Hunter."),
        "url": SITE + "/",
        "telephone": "+" + BIZ["phone_href"].lstrip("+"),
        "email": BIZ["email"],
        "image": SITE + "/assets/img/garage-flake-finished-1440.jpg",
        "logo": SITE + "/assets/logo-full.png",
        "hasMap": "https://www.google.com/maps?cid=" + BIZ["maps_cid"],
        "sameAs": [SOCIAL["facebook"], GOOGLE_REVIEWS_URL]
                  + [u for u in SAME_AS_PENDING.values() if u],
        "founder": {"@id": OWNER_ID},
        "currenciesAccepted": "AUD",
        "areaServed": [{"@type": "City", "name": n, "containedInPlace": NSW_PLACE}
                       for n in ["Taree", "Forster", "Tuncurry", "Harrington", "Blueys Beach",
                                 "Pacific Palms", "Newcastle"]]
        + [{"@type": "AdministrativeArea", "name": n, "containedInPlace": NSW_PLACE}
           for n in ["Mid North Coast", "Hunter Region"]],
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "07:00", "closes": "19:00"}],
        "makesOffer": [{"@type": "Offer",
                        "itemOffered": {"@type": "Service", "name": s["short"],
                                        "serviceType": s["short"]}} for s in SERVICES],
    }
    if CREDENTIALS["abn"]:
        node["identifier"] = {"@type": "PropertyValue", "name": "ABN", "value": CREDENTIALS["abn"]}
    if CREDENTIALS["accreditations"]:
        node["hasCredential"] = CREDENTIALS["accreditations"]
    return node


NSW_PLACE = {"@type": "State", "name": "New South Wales",
             "containedInPlace": {"@type": "Country", "name": "Australia"}}


def owner_name():
    return " ".join(x for x in (OWNER["given"], OWNER["surname"]) if x)


def person_schema(context=True):
    node = {"@type": "Person", "@id": OWNER_ID, "name": owner_name(),
            "givenName": OWNER["given"], "jobTitle": "Owner",
            "worksFor": {"@id": SITE + "/#business"}, "url": SITE + "/about"}
    if context:
        node = {"@context": "https://schema.org", **node}
    if OWNER["surname"]:
        node["familyName"] = OWNER["surname"]
    if OWNER["photo"]:
        node["image"] = SITE + "/assets/img/%s.jpg" % OWNER["photo"]
    return node


def page(path, title, meta, body, schemas=(), og_image="/assets/img/garage-flake-finished-1440.jpg",
         og_type="website", active="", preload=None, noindex=False, head_extra=""):
    """Write one page. path '' = home; otherwise 'slug' or 'a/b'."""
    canonical = SITE + ("/" if not path else "/" + path)
    schema_html = "".join(
        '<script type="application/ld+json">%s</script>'
        % json.dumps(s, ensure_ascii=False, separators=(",", ":")) for s in schemas)
    pre = ('<link rel="preload" as="image" href="%s" fetchpriority="high">' % preload) if preload else ""
    measure = ""
    if GSC_TOKEN:
        measure += '<meta name="google-site-verification" content="%s">\n' % esc(GSC_TOKEN)
    if GA4_ID:
        measure += ('<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n'
                    '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
                    'gtag("js",new Date());gtag("config","%s");</script>\n' % (GA4_ID, GA4_ID))
    if PIXEL_ID:
        # Meta Pixel base code + PageView. Lead fires only on /thank-you, with
        # an eventID so a later Conversions API event can be deduplicated.
        measure += ("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
                    "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;"
                    "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
                    "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,"
                    "document,'script','https://connect.facebook.net/en_US/fbevents.js');"
                    "fbq('init','%s');fbq('track','PageView');</script>\n" % esc(PIXEL_ID))
    if noindex:
        measure += '<meta name="robots" content="noindex, follow">\n'
    measure += head_extra

    doc = """<!DOCTYPE html>
<html lang="en-AU" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta name="theme-color" content="#0C0B0C">
<meta name="format-detection" content="telephone=no">
<link rel="preconnect" href="%s">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/archivo-var-latin.woff2" crossorigin>
%s<link rel="stylesheet" href="%s">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="icon" href="/assets/favicon-16.png" type="image/png" sizes="16x16">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:type" content="%s">
<meta property="og:site_name" content="Floor Candy">
<meta property="og:locale" content="en_AU">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s">
<meta property="og:image:width" content="1440">
<meta property="og:image:height" content="648">
<meta property="og:image:alt" content="A completed flake epoxy garage floor by Floor Candy">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="%s">
%s%s</head>
<body>
<a class="skip" href="#main">Skip to content</a>
%s
<main id="main">
%s
</main>
%s
<script src="%s" defer></script>
</body>
</html>
""" % (esc(title), esc(meta), canonical, SITE, pre, v("/styles.css"), og_type,
       esc(title), esc(meta), canonical, SITE + og_image,
       esc(title), esc(meta), SITE + og_image,
       measure, schema_html, header(active), body, footer(), v("/main.js"))

    out = os.path.join(ROOT, "index.html") if not path \
        else os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return canonical


# ==========================================================================
# PAGES
# ==========================================================================
LAYERS_SVG = """<svg class="layers" viewBox="0 0 560 300" role="img" aria-labelledby="layers-t layers-d">
<title id="layers-t">The five layers of a Floor Candy floor</title>
<desc id="layers-d">Cross-section from the bottom up: ground concrete slab, crack repair, base coat, flake, clear topcoat.</desc>
<defs>
<pattern id="agg" width="22" height="18" patternUnits="userSpaceOnUse"><circle cx="5" cy="6" r="2.2" class="l-agg"/><circle cx="15" cy="13" r="1.6" class="l-agg"/><circle cx="18" cy="4" r="1" class="l-agg"/></pattern>
<pattern id="flk" width="16" height="10" patternUnits="userSpaceOnUse"><rect x="1" y="2" width="5" height="2.4" rx=".6" class="l-f1" transform="rotate(-12 3 3)"/><rect x="9" y="5" width="4" height="2" rx=".6" class="l-f2" transform="rotate(18 11 6)"/><rect x="5" y="7" width="3" height="1.6" rx=".5" class="l-f3"/></pattern>
</defs>
<g class="l-stack">
<rect x="20" y="196" width="330" height="84" class="l-slab"/><rect x="20" y="196" width="330" height="84" fill="url(#agg)"/>
<path d="M150 280 L158 250 L150 226 L160 196" class="l-crack"/>
<rect x="20" y="178" width="330" height="18" class="l-base" data-layer="3"/>
<rect x="20" y="160" width="330" height="18" class="l-flakebg" data-layer="4"/><rect x="20" y="160" width="330" height="18" fill="url(#flk)"/>
<rect x="20" y="140" width="330" height="20" class="l-top" data-layer="5"/>
<path d="M30 146 H340" class="l-sheen"/>
</g>
<g class="l-labels">
<line x1="350" y1="150" x2="380" y2="150"/><text x="388" y="146">5 &middot; Clear topcoat</text><text x="388" y="162" class="l-sub">seals it, wipes clean</text>
<line x1="350" y1="169" x2="380" y2="186"/><text x="388" y="190">4 &middot; Flake</text><text x="388" y="206" class="l-sub">colour, texture, grip</text>
<line x1="350" y1="187" x2="380" y2="226"/><text x="388" y="230">3 &middot; Base coat</text><text x="388" y="246" class="l-sub">the structural layer</text>
<line x1="158" y1="240" x2="380" y2="262" class="l-dash"/><text x="388" y="266">2 &middot; Crack repair</text>
<line x1="350" y1="276" x2="380" y2="290"/><text x="388" y="294">1 &middot; Ground slab</text>
</g>
</svg>"""


HOME_FAQS_LP = [
    ("How much does it cost?",
     "Double garages start from approximately $2,450, and new customers save $250 on "
     "their first floor. Your exact price depends on size, the condition of the slab, "
     "how much preparation it needs, the finish and where you are. You get it as a "
     "fixed written price after a free on-site look."),
    ("How long does it take?",
     ("Most floors are done in %s on site. A difficult slab can take longer, and "
      "you get the timeline for your floor in writing with your quote." % JOB_FACTS["days_on_site"])
     if JOB_FACTS["days_on_site"] else
     ("It depends on the size of the floor, its condition and the weather. Preparing "
      "a difficult slab can take longer than coating it. You get the timeline for "
      "your floor in writing with your quote.")),
    ("When can I walk and drive on it?",
     ("Usually walk on it after %s and drive on it after %s. Cure times move with "
      "temperature, so we confirm yours on the day."
      % (JOB_FACTS["walk_on"], JOB_FACTS["drive_on"]))
     if JOB_FACTS["walk_on"] and JOB_FACTS["drive_on"] else
     ("Cure times depend on the system and the temperature on the day. Jarrod tells "
      "you exactly when it is ready for feet and when it is ready for the car before "
      "he leaves.")),
    ("Will it peel or lift under hot tyres?",
     "Hot tyre lifting is almost always a preparation failure: a coating rolled onto "
     "dusty or sealed concrete never properly bonds. That is why every slab is "
     "mechanically ground before anything goes down."),
    ("What about oil stains and cracks?",
     "Both get looked at during the free assessment. Cracks are repaired where "
     "appropriate before coating. A repair stops a crack being an open path through "
     "the floor, but it does not change what the slab is doing structurally, and we "
     "tell you which is which before you commit."),
    ("Is it slippery when wet?",
     "A smooth gloss finish is more slippery wet than dry. A flake floor has texture "
     "through it, which helps. If the floor gets wet often or sits on a slope, tell "
     "us and we will talk through the right finish."),
    ("Do I need to empty the garage?",
     "The floor has to be clear to be ground and coated. If that is a problem, "
     "mention it when you book and we will work it out with you."),
    ("Which areas do you cover?",
     "Taree, Forster, Tuncurry, Harrington, Blueys Beach, Pacific Palms and the "
     "Mid North Coast are our core areas. We take selected projects in Newcastle and "
     "the Hunter, depending on job size and timing. Not sure? Send your postcode."),
    ("Can I choose the colour?",
     "Yes. Flake comes in blends of greys, creams, tans and mixes, and solid colours "
     "are available too. We bring real samples to the on-site quote so you pick in "
     "your own light, not off a screen."),
    ("Is there a warranty?",
     ("Yes. " + WARRANTY_TERMS) if WARRANTY_TERMS else
     ("We are not publishing warranty terms until they are written down properly. "
      "Ask Jarrod at the quote and he will tell you exactly what he stands behind.")),
]


def build_home():
    svc_rows = []
    for i, s in enumerate(SERVICES, 1):
        svc_rows.append("""<a class="svc svc--compact" href="/%s">
<span class="svc-n">%02d</span>
<span><h3>%s</h3></span>
<span class="svc-go" aria-hidden="true">&rarr;</span>
</a>""" % (s["slug"], i, esc(s["short"])))

    steps = "".join("""<div class="step"><span class="step-n">%02d</span>
<div><h3>%s</h3><p>%s</p></div></div>""" % (i, esc(t), esc(d))
                    for i, (t, d) in enumerate(PROCESS, 1))

    work = "".join('<figure class="proj">%s<figcaption class="proj-meta">%s</figcaption></figure>'
                   % (square(b, a), esc(a)) for b, a in WORK[:6])

    jf = JOB_FACTS
    timeline = ""
    bits = []
    if jf["days_on_site"]:
        bits.append("<li><strong>%s</strong><span>on site</span></li>" % esc(jf["days_on_site"]))
    if jf["walk_on"]:
        bits.append("<li><strong>%s</strong><span>to walk on</span></li>" % esc(jf["walk_on"]))
    if jf["drive_on"]:
        bits.append("<li><strong>%s</strong><span>to drive on</span></li>" % esc(jf["drive_on"]))
    if bits:
        timeline = '<ul class="timeline">%s</ul>' % "".join(bits)

    hero_days = (" Done in %s." % esc(jf["days_on_site"])) if jf["days_on_site"] else ""
    capacity = ('<p class="capacity"><span class="dot" aria-hidden="true"></span>Now booking '
                '%s jobs</p>' % esc(jf["booking_month"])) if jf["booking_month"] else ""
    reply = ("within %s" % esc(jf["response_time"])) if jf["response_time"] else "to book a time"
    warranty_li = ('<li><h3>Written warranty</h3><p>%s</p></li>' % esc(WARRANTY_TERMS)) \
        if WARRANTY_TERMS else ""

    price = "{:,}".format(PRICING["double_garage_from"])
    swap = ("<script>(function(){try{var H=%s,q=new URLSearchParams(location.search).get('h');"
            "if(q&&H[q]){sessionStorage.setItem('fc_h',q)}else{q=sessionStorage.getItem('fc_h')}"
            "if(q&&H[q]&&q!=='a'){document.getElementById('hero-h1').textContent=H[q]}"
            "}catch(e){}})()</script>" % json.dumps(HEADLINES, ensure_ascii=False))

    body = """<section class="hero hero--lp">
<div class="wrap hero-grid">
<div class="hero-copy">
<p class="eyebrow">Garage, patio &amp; shed floors &middot; Taree, Forster &amp; the Mid North Coast</p>
<h1 id="hero-h1">%(h1)s</h1>
%(swap)s
<p class="lede">Ground back, cracks repaired, flake broadcast through a tough base coat and sealed under a clear topcoat.%(hero_days)s You deal directly with Jarrod, the owner.</p>
<div class="hero-price">
<span class="price-tag">Double garages from $%(price)s<sup>*</sup></span>
<span class="offer-flag">New customers save $%(save)d</span>
</div>
<div class="btn-row">
<a class="btn btn--primary btn--lg" href="#quote">Get my free quote</a>
<a class="btn btn--ghost btn--lg" href="tel:%(tel)s">Call %(phone)s</a>
</div>
%(capacity)s
<ul class="hero-proof">
<li><a href="%(greviews)s" rel="noopener">%(gmark)s<strong>%(rating)s</strong> on Google</a></li>
<li>Free on-site assessment</li>
<li>Fixed written price</li>
<li>Owner-led</li>
</ul>
</div>
<div class="hero-ba">
%(hero_ba)s
</div>
</div>
</section>

<section class="section pain" aria-labelledby="pain-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Sound familiar?</p>
<h2 id="pain-h">The garage is the biggest room in the house. <em>It&rsquo;s also the worst floor.</em></h2></div></div>
<ul class="pain-grid reveal-group">
<li class="reveal"><span class="pain-n">01</span><h3>Cracked, stained concrete</h3><p>Oil drips, tyre marks and hairline cracks that no amount of pressure washing shifts.</p></li>
<li class="reveal"><span class="pain-n">02</span><h3>Dust through the house</h3><p>Bare concrete sheds a fine grey dust that ends up on shoes, in the car and on the hallway floor.</p></li>
<li class="reveal"><span class="pain-n">03</span><h3>A room you keep shut</h3><p>The door stays down when people come over, and the space never gets used the way it could be.</p></li>
</ul>
<p class="pain-turn">A properly prepared flake floor deals with all three. Here&rsquo;s what that looks like on real Floor Candy jobs.</p>
</div>
</section>

<section class="section band--paper2" aria-labelledby="ba-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Real before &amp; after</p>
<h2 id="ba-h">The same floor, twice</h2></div>
<div><p class="lede">Our own jobs. Nothing staged, nothing brightened, nobody else&rsquo;s work. Drag the handle.</p></div></div>
<div class="grid-2 ba-pair">
%(ba1)s
%(ba2)s
</div>
</div>
</section>

<section class="section" aria-labelledby="offer-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">What you get</p>
<h2 id="offer-h">Everything that goes into your floor. <em>One fixed price.</em></h2></div>
<div><p class="lede">No cheap kit, no shortcuts on the part you can&rsquo;t see. This is what&rsquo;s in every Floor Candy flake floor.</p></div></div>
<div class="offer">
<ol class="inc reveal-group">
<li class="reveal"><span class="tick-i" aria-hidden="true"></span><div><h3>Free on-site assessment</h3><p>A written read on your slab and what it needs, whether or not you go ahead.</p></div></li>
<li class="reveal"><span class="tick-i" aria-hidden="true"></span><div><h3>Mechanical grind</h3><p>Opens up the concrete so the coating bonds to the slab, not to dust or old sealer.</p></div></li>
<li class="reveal"><span class="tick-i" aria-hidden="true"></span><div><h3>Crack repair, where it&rsquo;s needed</h3><p>Stops cracks becoming open paths through your new floor.</p></div></li>
<li class="reveal"><span class="tick-i" aria-hidden="true"></span><div><h3>Tough base coat</h3><p>The layer that does the structural work.</p></div></li>
<li class="reveal"><span class="tick-i" aria-hidden="true"></span><div><h3>Flake broadcast through it</h3><p>Colour and texture right through the surface. Hides the marks a working garage collects and grips better than smooth gloss.</p></div></li>
<li class="reveal"><span class="tick-i" aria-hidden="true"></span><div><h3>Clear topcoat</h3><p>Locks the flake in. Spills and tyre marks wipe off.</p></div></li>
<li class="reveal"><span class="tick-i" aria-hidden="true"></span><div><h3>Walkthrough before the balance</h3><p>We check the finished floor together before you pay the balance.</p></div></li>
</ol>
<aside class="price-box" aria-labelledby="pb-h">
<p class="pb-lab" id="pb-h">Double garage, all of the above</p>
<p class="pb-num">From $%(price)s<sup>*</sup></p>
<div class="pb-save"><span>New customer saving</span><strong>&minus;$%(save)d</strong></div>
<a class="btn btn--primary btn--full btn--lg" href="#quote">Get my free quote</a>
<p class="pb-fine">*%(qualifier)s %(regional)s</p>
</aside>
</div>
</div>
</section>

<section class="section band--ink" aria-labelledby="prep-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Why floors fail</p>
<h2 id="prep-h">Epoxy floors don&rsquo;t fail. <em>Poor preparation does.</em></h2></div>
<div><p class="lede">When a coated floor lifts, peels or picks up under hot tyres, the coating is almost never the problem. The problem is what it was asked to stick to.</p></div></div>
<div class="vs reveal-group">
<div class="vs-col vs-col--them reveal">
<h3>DIY kit or a cheap quote</h3>
<ul>
<li>Rolled onto the slab with little or no preparation</li>
<li>A thin coat over dust, sealer or old paint, so it never properly bonds</li>
<li>Hot tyres pull it up where it hasn&rsquo;t stuck</li>
<li>Your weekend, your knees, and your problem when it fails</li>
</ul>
</div>
<div class="vs-col vs-col--us reveal">
<h3>A Floor Candy floor</h3>
<ul>
<li>Slab mechanically ground first, so the system has something to bond to</li>
<li>Cracks repaired where appropriate before anything goes down</li>
<li>Base coat, flake and clear topcoat, built as one system</li>
<li>Fixed written price, and a walkthrough before you pay the balance</li>
</ul>
</div>
</div>
<div class="prep-strip">
<div class="prep-img">%(prep_img)s</div>
<p>Preparation is the stage nobody photographs and the stage a cheap quote leaves out. It&rsquo;s also the stage that decides whether your floor is still stuck down in ten years. <a class="tlink" href="/concrete-preparation-crack-repair">How we prepare concrete</a></p>
</div>
</div>
</section>

<section class="section" aria-labelledby="proc-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">How it works</p>
<h2 id="proc-h">Five layers. <em>Five steps. No surprises.</em></h2></div></div>
<div class="proc">
<div class="proc-art">%(layers)s%(timeline)s</div>
<div class="steps steps--light">%(steps)s</div>
</div>
</div>
</section>

<section class="section band--paper2" aria-labelledby="work-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Recent work</p>
<h2 id="work-h">Genuine Floor Candy floors</h2></div>
<div><p class="lede">Every photograph in this section is our own work. <a class="tlink" href="/projects">See the projects</a>.</p></div></div>
<div class="grid-3 work-grid">%(work)s</div>
</div>
</section>

%(reviews)s

<section class="section band--paper2" aria-labelledby="promise-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">No surprises</p>
<h2 id="promise-h">What you get before you commit</h2></div></div>
<ul class="promise reveal-group">
<li class="reveal"><h3>A free, honest assessment</h3><p>Jarrod looks at the actual slab and tells you what it needs, whether or not you go ahead.</p></li>
<li class="reveal"><h3>A fixed written price</h3><p>Written down after we&rsquo;ve seen the floor. No variations invented on the day.</p></li>
<li class="reveal"><h3>A walkthrough at the end</h3><p>The finished floor gets checked together before the balance is paid.</p></li>
%(warranty_li)s
</ul>
</div>
</section>

%(faq)s

<section class="section band--ink quote-band" id="quote" aria-label="Free quote">
<div class="wrap">
<div class="quote-shell">
%(form)s
<div class="quote-side">
<p class="eyebrow">What happens next</p>
<h2 class="qs-h">Three steps to a fixed price</h2>
<ol class="next-steps">
<li><span>1</span><div><h3>Jarrod gets in touch</h3><p>A call or text %(reply)s, whichever you prefer.</p></div></li>
<li><span>2</span><div><h3>A free look at the floor</h3><p>On site, at a time that suits you. Real flake samples in your own light.</p></div></li>
<li><span>3</span><div><h3>Your fixed written price</h3><p>With the $%(save)d new-customer saving taken off. No pressure, no obligation.</p></div></li>
</ol>
%(capacity)s
<p class="qs-call">Rather talk now? <a href="tel:%(tel)s">%(phone)s</a><br><span>%(hours)s</span></p>
</div>
</div>
</div>
</section>

%(areas)s

<section class="section" aria-labelledby="svc-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">What we do</p>
<h2 id="svc-h">Services</h2></div>
<div><p class="lede">Six things, done properly, on concrete. If your floor needs something we don&rsquo;t do, we&rsquo;ll tell you.</p></div></div>
<div class="svc-list svc-list--compact">%(svc)s</div>
</div>
</section>

%(closer)s
""" % {
        "h1": esc(HEADLINES["a"]), "swap": swap, "hero_days": hero_days,
        "price": price, "save": OFFER["saving"], "tel": BIZ["phone_href"],
        "phone": BIZ["phone_display"], "hours": esc(BIZ["hours"]), "capacity": capacity,
        "greviews": GOOGLE_REVIEWS_URL, "gmark": GOOGLE_G, "rating": BIZ["rating"],
        "hero_ba": ba_block("garage", heading_level="p", sizes="(min-width:960px) 520px, 92vw", lazy=False),
        "ba1": ba_block("shopfit", sizes="(min-width:900px) 560px, 92vw"),
        "ba2": ba_block("prep", sizes="(min-width:900px) 560px, 92vw"),
        "qualifier": esc(PRICING["qualifier"]), "regional": esc(PRICING["regional_note"]),
        "prep_img": picture("prep_grind", "(min-width:900px) 320px, 92vw"),
        "layers": LAYERS_SVG, "timeline": timeline, "steps": steps, "work": work,
        "reviews": reviews_block(coatings_only=True,
                                 heading="What customers say about Jarrod"),
        "warranty_li": warranty_li,
        "faq": faq_block(HOME_FAQS_LP, "Straight answers"),
        "form": quote_form("home-quote"), "reply": reply,
        "areas": areas_block(dark=False, show_map=True),
        "svc": "".join(svc_rows),
        "closer": closer("Get a floor worth showing off", ps=True),
    }

    page("", "Epoxy Garage Floors Taree, Forster & Mid North Coast | Floor Candy",
         "Flake epoxy garage, patio and shed floors across Taree, Forster and the Mid North "
         "Coast. Double garages from $2,450, new customers save $250. Free on-site quote.",
         body,
         schemas=[business_schema(),
                  {"@context": "https://schema.org", "@type": "WebSite",
                   "@id": SITE + "/#website", "url": SITE + "/", "name": "Floor Candy",
                   "publisher": {"@id": SITE + "/#business"}},
                  faq_schema(HOME_FAQS_LP)],
         active="/", preload=None)


SERVICE_CASES = {
    "garage-epoxy-flooring": ["garage-bare-slab-to-flake"],
    "premium-flake-flooring": ["garage-bare-slab-to-flake", "tiled-floor-to-flake"],
    "concrete-preparation-crack-repair": ["garage-bare-slab-to-flake"],
    "residential-epoxy-flooring": ["tiled-floor-to-flake"],
}


def case_cards(slugs, eyebrow="See a real job", desc=True):
    out = []
    for slug in slugs:
        c = CASE_BY_SLUG[slug]
        thumb = c["stages"][-1][0]
        alt = c["stages"][-1][1]
        avif = "" if thumb.startswith(NO_AVIF) else (
            '<source type="image/avif" srcset="/assets/img/%s-414.avif">' % thumb)
        out.append("""<a class="case-card" href="/projects/%s">
<picture>%s<source type="image/webp" srcset="/assets/img/%s-414.webp"><img src="/assets/img/%s-414.jpg" width="414" height="414" alt="%s" loading="lazy" decoding="async"></picture>
<span><span class="eyebrow">%s</span><h3>%s</h3>%s</span>
</a>""" % (slug, avif, thumb, thumb, esc(alt), esc(eyebrow), esc(c["title"]),
           ("<p>%s</p>" % esc(c["meta"])) if desc else ""))
    return '<div class="case-cards">%s</div>' % "".join(out)


def build_service(s):
    nav, bc = crumbs([("/", "Home"), (None, s["short"])])
    sections = "".join("""<section class="section%s"><div class="wrap"><div class="prose">
<h2>%s</h2>%s</div></div></section>"""
                       % (" band--paper2" if i % 2 else "", esc(t), "".join(ps))
                       for i, (t, ps) in enumerate(s["body"]))

    rel = "".join('<li><a href="/%s">%s</a></li>' % (r, esc(SERVICE_BY_SLUG[r]["short"]))
                  for r in s["related"] if r in SERVICE_BY_SLUG)
    loc_links = "".join('<li><a href="/service-areas/%s">%s</a></li>' % (l["slug"], esc(l["name"]))
                        for l in LOCATIONS[:4])

    img_html = picture(s["img"], "(min-width:900px) 560px, 92vw") if s["img"] in IMG else ""
    cases = SERVICE_CASES.get(s["slug"], [])
    case_html = ""
    if cases:
        case_html = """<section class="section band--paper2">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Case study</p><h2>See a real job</h2></div>
<div><p class="lede">Start to finish, photographed on the day, including the preparation most sites leave out.</p></div></div>
%s
</div>
</section>""" % case_cards(cases)

    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Service</p>
<h1>%s</h1>
<p class="lede">%s</p>
<div class="btn-row">
<a class="btn btn--primary" href="/contact">Get a free quote</a>
<a class="btn btn--ghost" href="tel:%s">Call %s</a>
</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="split">
<div class="split-media">%s</div>
<div class="split-body">
<p class="eyebrow">From $%s<sup>*</sup></p>
<h2>Double garage floors from $%s<sup>*</sup></h2>
<p>%s</p>
<p class="small muted">%s</p>
<div class="btn-row"><a class="btn btn--ink" href="/contact">Get an exact quote</a></div>
</div>
</div>
</div>
</section>

%s

%s

<section class="section band--ink">
<div class="wrap">
<div class="split split--reverse">
<div class="split-media">%s</div>
<div class="split-body">
<h2>Epoxy floors don&rsquo;t fail.<br>Poor preparation does.</h2>
<p>The coating is the visible layer. What decides whether it lasts is the slab underneath it, whether it was sealed, dusty, already coated, or moving moisture. Preparing it mechanically is how a system gets something real to bond to.</p>
<div class="btn-row"><a class="btn btn--primary" href="/concrete-preparation-crack-repair">How we prepare concrete</a></div>
</div>
</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Real work</p><h2>Our own floors</h2></div>
<div><p class="lede">Every photograph is a Floor Candy job. <a class="tlink" href="/projects">See more</a>.</p></div></div>
<div class="grid-3">%s</div>
</div>
</section>

%s

<section class="section band--paper2">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Keep reading</p><h2>Related</h2></div></div>
<div class="split">
<div><h3>Other services</h3><ul class="areas" style="margin-top:1rem">%s</ul></div>
<div><h3>Where we work</h3><ul class="areas" style="margin-top:1rem">%s</ul></div>
</div>
</div>
</section>

%s
%s
""" % (nav, esc(s["h1"]), esc(s["lede"]), BIZ["phone_href"], BIZ["phone_display"],
       img_html,
       "{:,}".format(PRICING["double_garage_from"]), "{:,}".format(PRICING["double_garage_from"]),
       esc(PRICING["qualifier"]), esc(PRICING["regional_note"]),
       case_html, sections,
       picture("prep_extract", "(min-width:900px) 460px, 90vw"),
       "".join('<figure class="proj">%s<figcaption class="proj-meta">%s</figcaption></figure>'
               % (square(b, a), esc(a)) for b, a in WORK[:4]),
       faq_block(s["faqs"], "About %s" % s["short"].lower()),
       rel, loc_links,
       price_block(regional=True),
       closer())

    svc_schema = {
        "@context": "https://schema.org", "@type": "Service",
        "name": s["short"], "serviceType": s["short"],
        "provider": {"@id": SITE + "/#business"},
        "areaServed": [{"@type": "City", "name": n, "containedInPlace": NSW_PLACE}
                       for n in ["Taree", "Forster", "Harrington", "Blueys Beach", "Pacific Palms"]],
        "url": SITE + "/" + s["slug"],
        "description": s["meta"],
    }
    page(s["slug"], s["title"], s["meta"], body,
         schemas=[bc, svc_schema, faq_schema(s["faqs"])], active="")


def build_location(l):
    nav, bc = crumbs([("/", "Home"), ("/service-areas", "Service areas"), (None, l["name"])])
    svc_cards = "".join("""<a class="svc svc--plain" href="/%s">
<span class="svc-n">%02d</span>
<span><h3>%s</h3><p>%s</p></span>
<span class="svc-go" aria-hidden="true">&rarr;</span></a>"""
                        % (sl, i, esc(SERVICE_BY_SLUG[sl]["short"]),
                           esc(SERVICE_BY_SLUG[sl]["lede"].split(".")[0] + "."))
                        for i, sl in enumerate(l["services"], 1))
    nearby = "".join("<li><span>%s</span></li>" % esc(n) if n not in AREA_LINKS
                     else '<li><a href="/service-areas/%s">%s</a></li>' % (AREA_LINKS[n], esc(n))
                     for n in l["nearby"])
    local_h, local_p = l["local"]
    if PROJECT_SUBURBS:
        near = PROJECT_SUBURBS.get(l["slug"], [])
        near_note = ""
    else:
        near = [c["slug"] for c in CASES] if l["slug"] in ("taree", "forster") else []
        near_note = ('<p class="small muted mt-3">The suburbs of these jobs aren&rsquo;t '
                     'confirmed yet, so neither is presented as a %s job.</p>' % esc(l["name"]))
    recent_html = ""
    if near:
        recent_html = ('<h3 class="mt-4" style="margin-bottom:1rem">Recent work</h3>%s%s'
                       % (case_cards(near, "Recent work", desc=False), near_note))
    map_html = map_section("Floor Candy on Google Maps") if l["slug"] in ("taree", "forster") else ""

    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Service area: %s</p>
<h1>%s</h1>
<p class="lede">%s</p>
<div class="btn-row">
<a class="btn btn--primary" href="/contact">Get a free quote</a>
<a class="btn btn--ghost" href="tel:%s">Call %s</a>
</div>
</div>
</section>

<section class="section">
<div class="wrap"><div class="prose">%s</div></div>
</section>

<section class="section band--paper2">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Local detail</p><h2>%s</h2></div></div>
<div class="prose">%s</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Locally</p><h2>%s</h2></div></div>
<div class="prose">%s</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Available here</p><h2>Services in %s</h2></div>
<div><p class="lede">Everything below is available in %s. Prices start from the same place as anywhere in our core area.</p></div></div>
<div class="svc-list">%s</div>
</div>
</section>

<section class="section band--ink">
<div class="wrap">
<div class="split">
<div class="split-media">%s</div>
<div class="split-body">
<h2>Epoxy floors don&rsquo;t fail.<br>Poor preparation does.</h2>
<p>Whatever the slab is doing in %s, sealed, dusty, already coated, or holding moisture, it has to be dealt with before a coating goes anywhere near it. That is what the free on-site assessment is for, and it is why we won&rsquo;t quote your floor from a photograph alone.</p>
<div class="btn-row"><a class="btn btn--primary" href="/concrete-preparation-crack-repair">How we prepare concrete</a></div>
</div>
</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Real work</p><h2>Floors we&rsquo;ve finished</h2></div>
<div><p class="lede">Genuine Floor Candy jobs, shown without a suburb.</p></div></div>
<div class="grid-3">%s</div>
%s
<p class="small muted mt-3"><a class="tlink" href="/projects">See all projects</a></p>
</div>
</section>

%s

%s

<section class="section band--paper2">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Nearby</p><h2>Areas near %s</h2></div>
<div><p class="lede">Not sure if we cover your area? Send us your postcode and we&rsquo;ll let you know.</p></div></div>
<ul class="areas">%s</ul>
<p class="small muted mt-3"><a class="tlink" href="/service-areas">All service areas</a></p>
</div>
</section>

%s
%s
""" % (nav, esc(l["region"]), esc(l["h1"]), esc(l["lede"]),
       BIZ["phone_href"], BIZ["phone_display"],
       "".join(l["intro"]),
       esc(local_h), local_p,
       esc(l["who"][0]), l["who"][1],
       esc(l["name"]), esc(l["name"]), svc_cards,
       picture("prep_grind", "(min-width:900px) 520px, 92vw"),
       esc(l["name"]),
       "".join('<figure class="proj">%s<figcaption class="proj-meta">%s</figcaption></figure>'
               % (square(b, a), esc(a)) for b, a in WORK[:4]),
       recent_html, map_html,
       price_block(regional=(l["slug"] == "newcastle")),
       esc(l["name"]), nearby,
       faq_block(l["faqs"], "Questions about %s" % l["name"]),
       closer("Get a fixed price in %s" % l["name"]))

    loc_schema = {
        "@context": "https://schema.org", "@type": "Service",
        "name": "Epoxy flooring in %s" % l["name"],
        "serviceType": "Epoxy flooring",
        "provider": {"@id": SITE + "/#business"},
        "areaServed": {"@type": "City", "name": l["name"],
                       "containedInPlace": NSW_PLACE},
        "url": SITE + "/service-areas/" + l["slug"],
        "description": l["meta"],
    }
    page("service-areas/" + l["slug"], l["title"], l["meta"], body,
         schemas=[bc, loc_schema, faq_schema(l["faqs"])], active="")


def build_areas_index():
    nav, bc = crumbs([("/", "Home"), (None, "Service areas")])
    cards = "".join("""<a class="svc svc--plain" href="/service-areas/%s">
<span class="svc-n">%02d</span>
<span><h3>%s</h3><p>%s</p></span>
<span class="svc-go" aria-hidden="true">&rarr;</span></a>"""
                    % (l["slug"], i, esc(l["name"]), esc(l["lede"]))
                    for i, l in enumerate(LOCATIONS, 1))
    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Service areas</p>
<h1>Where Floor Candy works</h1>
<p class="lede">Taree, Forster, Tuncurry, Harrington, Blueys Beach, Pacific Palms and the Mid North Coast are our core areas. Newcastle and the Hunter are selected projects, decided by job size and timing.</p>
<div class="btn-row"><a class="btn btn--primary" href="/contact">Get a free quote</a>
<a class="btn btn--ghost" href="tel:%s">Call %s</a></div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Towns</p><h2>Pick your area</h2></div>
<div><p class="lede">Each page covers what we actually see on slabs in that area, they&rsquo;re not the same page with the name swapped.</p></div></div>
<div class="svc-list">%s</div>
</div>
</section>

<section class="section band--paper2">
<div class="wrap">
<div class="prose">
<h2>Somewhere else?</h2>
<p>The list above is where we work regularly, not a boundary fence. Floor Candy is a mobile operation with no public showroom, we come to the floor.</p>
<p>If you&rsquo;re outside these towns, send us your postcode and a couple of photos. We&rsquo;ll tell you honestly whether the job works. Travel-heavy jobs need to be commercially viable and generally start around $%s, so larger floors travel better than small ones.</p>
</div>
</div>
</section>

%s
%s
""" % (nav, BIZ["phone_href"], BIZ["phone_display"], cards,
       "{:,}".format(PRICING["regional_from"]),
       areas_block(dark=True, show_map=True), closer())
    page("service-areas",
         "Service Areas | Epoxy Flooring Mid North Coast | Floor Candy",
         "Where Floor Candy works: Taree, Forster, Tuncurry, Harrington, Blueys Beach, "
         "Pacific Palms and the Mid North Coast, plus selected projects in Newcastle and "
         "the Hunter.",
         body, schemas=[bc], active="/service-areas")


def case_spec_list(c):
    """Only fields with a value render. A blank suburb cannot reach the page."""
    rows = [("Service", SERVICE_BY_SLUG[c["service"]]["short"] if c.get("service") else None),
            ("Suburb", c.get("suburb")),
            ("Region", c.get("region")),
            ("Floor size", c.get("floor_size")),
            ("System", c.get("system")),
            ("Existing condition", c.get("existing")),
            ("Finish", c.get("finish")),
            ("Installed", c.get("install_date"))]
    rows = [(k, v) for k, v in rows if v]
    return "".join("<div class=\"spec\"><dt>%s</dt><dd>%s</dd></div>"
                   % (esc(k), esc(v)) for k, v in rows)


def build_case(c):
    nav, bc = crumbs([("/", "Home"), ("/projects", "Projects"), (None, c["title"])])
    stages = "".join("""<figure class="stage">
<div class="stage-media">%s</div>
<figcaption><h3>%s</h3><p>%s</p></figcaption>
</figure>""" % (square(base, cap, sizes="(min-width:900px) 540px, 92vw"), esc(cap), esc(txt))
                     for base, cap, txt in c["stages"])
    why_h, why_b = c["why"]
    svc = SERVICE_BY_SLUG[c["service"]]
    others = [x for x in CASES if x["slug"] != c["slug"]]
    more = "".join('<li><a href="/projects/%s">%s</a></li>' % (o["slug"], esc(o["title"]))
                   for o in others)

    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Case study</p>
<h1>%s</h1>
<p class="lede">%s</p>
</div>
</section>

<section class="section">
<div class="wrap">
<dl class="spec-grid">%s</dl>
</div>
</section>

<section class="section band--paper2">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Before &amp; after</p>
<h2>Drag to compare</h2></div></div>
%s
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Stage by stage</p>
<h2>How it went</h2></div>
<div><p class="lede">Every photograph on this page is our own work on this job.</p></div></div>
<div class="stage-list">%s</div>
</div>
</section>

<section class="section band--ink">
<div class="wrap"><div class="prose">
<h2>%s</h2>%s
</div></div>
</section>

<section class="section band--paper2">
<div class="wrap">
<div class="split">
<div><h2>The service</h2><p class="lede">%s</p>
<div class="btn-row mt-3"><a class="btn btn--ink" href="/%s">%s</a></div></div>
<div><h2>Other case studies</h2><ul class="aside-list mt-3">%s</ul>
<p class="small muted mt-3"><a class="tlink" href="/projects">All projects</a></p></div>
</div>
</div>
</section>

%s
""" % (nav, esc(c["h1"]), esc(c["lede"]),
       case_spec_list(c), ba_block(c["ba"], "h3"), stages,
       esc(why_h), why_b,
       esc(svc["lede"]), svc["slug"], esc("About " + svc["short"].lower()), more,
       closer())

    schema = {
        "@context": "https://schema.org", "@type": "CreativeWork",
        "name": c["title"], "description": c["meta"],
        "about": {"@type": "Service", "name": svc["short"]},
        "creator": {"@id": SITE + "/#business"},
        "url": SITE + "/projects/" + c["slug"],
    }
    page("projects/" + c["slug"], c["meta_title"], c["meta"], body,
         schemas=[bc, schema], active="/projects")


def build_projects():
    nav, bc = crumbs([("/", "Home"), (None, "Projects")])
    work = "".join('<figure class="proj">%s<figcaption class="proj-meta">%s</figcaption></figure>'
                   % (square(b, a), esc(a)) for b, a in WORK)
    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Projects</p>
<h1>Real Floor Candy work</h1>
<p class="lede">Every photograph on this page is a floor we finished. No stock imagery, no competitor work, and nothing generated.</p>
<div class="btn-row"><a class="btn btn--primary" href="/contact">Get a free quote</a></div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Before &amp; after</p><h2>The same floor, twice</h2></div>
<div><p class="lede">Photographed from the same position, on two different days. Nothing staged, nothing brightened.</p></div></div>
<div class="grid-3" style="gap:2rem">%s%s%s</div>
</div>
</section>

<section class="section band--paper2">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Case studies</p><h2>Two jobs in full</h2></div>
<div><p class="lede">Start to finish, with the stages most flooring sites leave out.</p></div></div>
<div class="svc-list">%s</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Gallery</p><h2>Finished floors</h2></div>
<div><p class="lede">Flake garages, sealed driveways, paths and alfresco slabs.</p></div></div>
<div class="grid-3">%s</div>
</div>
</section>

<section class="section">
<div class="wrap"><div class="prose">
<h2>Why there are no suburbs on these</h2>
<p>Most flooring sites caption their gallery with a town. We only publish a detail we can stand behind, and the job records behind these photographs don&rsquo;t all carry a confirmed suburb yet.</p>
<p>Rather than guess, or quietly attribute a floor to whichever town we&rsquo;d like to rank for, we leave it off, the same reason we publish <a href="/about">what we will and won&rsquo;t claim</a>. As job records are confirmed, individual project pages will be added here with the service, suburb, floor size, existing condition, preparation performed and finished system, and not before.</p>
</div></div>
</section>

%s
%s
""" % (nav, ba_block("garage", "h3"), ba_block("prep", "h3"), ba_block("shopfit", "h3"),
       "".join("""<a class="svc svc--plain" href="/projects/%s">
<span class="svc-n">%02d</span><span><h3>%s</h3><p>%s</p></span>
<span class="svc-go" aria-hidden="true">&rarr;</span></a>"""
               % (c["slug"], i, esc(c["title"]), esc(c["lede"]))
               for i, c in enumerate(CASES, 1)),
       work, reviews_block(), closer())
    page("projects", "Projects | Genuine Floor Candy Epoxy & Concrete Work",
         "Real Floor Candy projects, flake epoxy garage floors, sealed driveways and "
         "coated alfresco slabs, with genuine before and after photography.",
         body, schemas=[bc], active="/projects")


def build_about():
    nav, bc = crumbs([("/", "Home"), (None, "About")])
    creds = credential_lines()
    cred_block = ""
    if creds:
        cred_block = """<section class="section band--paper2"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Credentials</p><h2>The paperwork</h2></div></div>
<ul class="areas">%s</ul></div></section>""" % "".join("<li><span>%s</span></li>" % c for c in creds)

    if OWNER["photo"]:
        b = OWNER["photo"]
        about_media = ('<figure class="owner-photo"><picture><source type="image/webp" '
                       'srcset="/assets/img/%s.webp"><img src="/assets/img/%s.jpg" width="%d" '
                       'height="%d" alt="%s, owner of Floor Candy" loading="lazy" decoding="async">'
                       '</picture></figure>' % (b, b, OWNER["photo_w"], OWNER["photo_h"],
                                                esc(owner_name())))
    else:
        about_media = picture("prep_extract", "(min-width:900px) 460px, 90vw")
    if WARRANTY_TERMS:
        warranty_step = ('<h3>Our written warranty</h3><p>%s</p>' % esc(WARRANTY_TERMS))
    else:
        warranty_step = ('<h3>We don&rsquo;t publish a warranty we haven&rsquo;t written</h3>'
                         '<p>Plenty of competitors advertise a five or ten year warranty. We '
                         'don&rsquo;t have written terms yet, so we don&rsquo;t claim one. When '
                         'there are terms, they will be published in full.</p>')

    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">About</p>
<h1>Owner-led, and straight with you</h1>
<p class="lede" id="jarrod">Floor Candy is %s&rsquo;s business. When you call, you get the person who will be standing on your slab.</p>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="split">
<div class="split-media">%s</div>
<div class="split-body">
<h2>A small operation, on purpose</h2>
<p>Floor Candy coats concrete on the Mid North Coast, garages, driveways, alfresco slabs and interiors. It is owner-led, and Jarrod is on the tools rather than running a sales team.</p>
<p>We use subcontractors on some jobs. We mention that because a lot of flooring sites promise the opposite and it is rarely true. What we will say is that the standard doesn&rsquo;t change with who is holding the grinder.</p>
<p>We are a mobile operation with no public showroom. We come to the floor, look at the slab, and price it from what is actually there.</p>
</div>
</div>
</div>
</section>

<section class="section band--ink">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">How we work</p><h2>What we will and won&rsquo;t say</h2></div>
<div><p class="lede">A short list, because it is easier to trust a business that tells you what it doesn&rsquo;t know.</p></div></div>
<div class="steps">
<div class="step"><span class="step-n">01</span><div>%s</div></div>
<div class="step"><span class="step-n">02</span><div><h3>We don&rsquo;t promise cracks will disappear</h3><p>Cracks are repaired where appropriate. A repair stops the crack being an open path through the coating; it does not change what the slab is doing. Some stay visible, and we say which.</p></div></div>
<div class="step"><span class="step-n">03</span><div><h3>Three reviews, shown in full</h3><p>We have three Google reviews. Competitors in Newcastle have hundreds. Ours are all on this site, complete, including the one Google truncates.</p></div></div>
<div class="step"><span class="step-n">04</span><div><h3>We quote off the slab, not the photo</h3><p>Photos help and we ask for them. They don&rsquo;t replace standing on the floor, and a quote given without that is a guess dressed up as a price.</p></div></div>
</div>
</div>
</section>

%s

<section class="section">
<div class="wrap">
<div class="split split--reverse">
<div class="split-media">%s</div>
<div class="split-body">
<h2>Preparation is the whole argument</h2>
<p>If there is one idea this business is built on, it is that a coated floor succeeds or fails underneath the coating. Everything else, the flake blend, the sheen, the colour, is chosen after that is sorted.</p>
<div class="btn-row"><a class="btn btn--ink" href="/concrete-preparation-crack-repair">How we prepare concrete</a></div>
</div>
</div>
</div>
</section>

%s
%s
%s
""" % (nav, esc(owner_name()),
       about_media, warranty_step,
       cred_block,
       picture("polished", "(min-width:900px) 460px, 90vw"),
       reviews_block(), areas_block(), closer())
    page("about", "About Floor Candy | Owner-Led Epoxy Flooring, Mid North Coast",
         "Floor Candy is an owner-led epoxy and concrete flooring business on the Mid North "
         "Coast. What we claim, what we don't, and why preparation decides the result.",
         body, schemas=[bc, person_schema()], active="/about")


def build_contact():
    nav, bc = crumbs([("/", "Home"), (None, "Contact")])
    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Contact</p>
<h1>Get a free quote</h1>
<p class="lede">Free on-site assessment, a written read on your concrete, and a fixed price before you commit, whether or not you go ahead with us.</p>
</div>
</section>

<section class="section" id="quote">
<div class="wrap">
<div class="quote-shell">
%s
<div>
<h2>Or reach us directly</h2>
<ul class="quote-points mt-3">
<li><span class="qp-n">&#9742;</span><div><h3><a href="tel:%s">%s</a></h3><p>%s. If we&rsquo;re on a floor, leave a message and we&rsquo;ll call back.</p></div></li>
<li><span class="qp-n">&#9993;</span><div><h3><a href="mailto:%s">%s</a></h3><p>Attach photos of the floor and your suburb, and we&rsquo;ll come back to you.</p></div></li>
<li><span class="qp-n">&#9873;</span><div><h3>Mobile service</h3><p>Floor Candy has no public showroom. We come to the floor across Taree, Forster, Harrington, Blueys Beach, Pacific Palms and the Mid North Coast.</p></div></li>
<li><span class="qp-n">$</span><div><h3>Double garages from $%s<sup>*</sup></h3><p>%s New customers save $%d on their first floor.</p></div></li>
</ul>
</div>
</div>
</div>
</section>

<section class="section band--paper2" aria-labelledby="rev-ask-h">
<div class="wrap">
<div class="review-ask">
<div><h2 id="rev-ask-h">Already had a floor done?</h2>
<p>A Google review is the single most useful thing you can do for a small local business.</p></div>
<a class="btn btn--primary" href="%s" rel="noopener" data-ev="review_click">Leave Jarrod a Google review</a>
</div>
</div>
</section>

%s
%s
""" % (nav, quote_form("contact-quote"),
       BIZ["phone_href"], BIZ["phone_display"], BIZ["hours"],
       BIZ["email"], BIZ["email"],
       "{:,}".format(PRICING["double_garage_from"]), esc(PRICING["qualifier"]), OFFER["saving"],
       GOOGLE_WRITE_REVIEW_URL,
       areas_block(dark=True, show_map=True), closer("Send the floor over"))
    page("contact", "Contact Floor Candy | Free Epoxy Flooring Quote, Mid North Coast",
         "Get a free on-site floor assessment and a fixed written price. Call 0435 193 845 "
         "or send photos of your floor. Taree, Forster and the Mid North Coast.",
         body, schemas=[bc,
                        {"@context": "https://schema.org", "@type": "ContactPage",
                         "url": SITE + "/contact",
                         "mainEntity": {"@id": SITE + "/#business"}}],
         active="/contact")


def build_guide(g):
    nav, bc = crumbs([("/", "Home"), ("/guides", "Guides"), (None, g["h1"])])
    sections = "".join(
        "<h2>%s</h2>%s" % (esc(t), "".join(ps)) for t, ps in g["body"])
    rel = "".join('<li><a href="/%s">%s</a></li>' % (r, esc(SERVICE_BY_SLUG[r]["short"]))
                  for r in g["related"] if r in SERVICE_BY_SLUG)
    others = [x for x in GUIDES if x["slug"] != g["slug"]][:3]
    more = "".join('<li><a href="/guides/%s">%s</a></li>' % (o["slug"], esc(o["h1"]))
                   for o in others)

    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Guide</p>
<h1>%s</h1>
<p class="lede">%s</p>
<p class="byline">By <a href="/about#jarrod" rel="author">%s</a>, owner of Floor Candy &middot; <time datetime="%s">%s</time></p>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="guide-layout">
<article class="prose">
<figure class="guide-fig">%s<figcaption>%s</figcaption></figure>
%s
</article>
<aside class="guide-aside">
<div class="aside-card">
<h2>Get a fixed price</h2>
<p class="small">Free on-site assessment. A written read on your concrete and a fixed price, whether or not you go ahead with us.</p>
<a class="btn btn--primary btn--full" href="/contact">Get a free quote</a>
<a class="btn btn--ghost btn--full mt-3" href="tel:%s">Call %s</a>
</div>
<div class="aside-card">
<h2>Related services</h2>
<ul class="aside-list">%s</ul>
</div>
<div class="aside-card">
<h2>More guides</h2>
<ul class="aside-list">%s</ul>
</div>
</aside>
</div>
</div>
</section>

%s
""" % (nav, esc(g["h1"]), esc(g["lede"]),
       esc(owner_name()), g["date"], human_date(g["date"]),
       picture(g["img"], "(min-width:900px) 720px, 92vw", alt=g["img_alt"]),
       esc(g["img_alt"] + ". A genuine Floor Candy job."),
       sections, BIZ["phone_href"], BIZ["phone_display"], rel, more,
       closer())

    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": g["h1"],
        "description": g["meta"],
        "datePublished": g["date"],
        "dateModified": g["date"],
        "author": person_schema(context=False),
        "publisher": {"@id": SITE + "/#business"},
        "mainEntityOfPage": SITE + "/guides/" + g["slug"],
        "image": SITE + "/assets/img/garage-flake-finished-1440.jpg",
    }
    page("guides/" + g["slug"], g["title"], g["meta"], body,
         schemas=[bc, article], og_type="article", active="/guides")


def human_date(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def build_guides_index():
    nav, bc = crumbs([("/", "Home"), (None, "Guides")])
    rows = "".join("""<a class="svc svc--plain" href="/guides/%s">
<span class="svc-n">%02d</span>
<span><h3>%s</h3><p>%s</p></span>
<span class="svc-go" aria-hidden="true">&rarr;</span></a>"""
                   % (g["slug"], i, esc(g["h1"]), esc(g["lede"]))
                   for i, g in enumerate(GUIDES, 1))
    body = """%s
<section class="page-hero">
<div class="wrap">
<p class="eyebrow">Guides</p>
<h1>Straight answers about concrete floors</h1>
<p class="lede">What a floor costs, why coatings fail, how to choose a finish, and what to ask before you accept anyone&rsquo;s quote, including ours.</p>
</div>
</section>

<section class="section" aria-labelledby="guides-h">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">All guides</p>
<h2 id="guides-h">Four things worth knowing</h2></div>
<div><p class="lede">Each one answers its question in the first two paragraphs. None of them quote a product or a cure time.</p></div></div>
<div class="svc-list">%s</div>
</div>
</section>

<section class="section band--paper2">
<div class="wrap"><div class="prose">
<h2>What you won&rsquo;t find here</h2>
<p>No product names, no cure times and no warranty claims. Those depend on specifics we are not prepared to state until they are confirmed in writing, and a guide that invents them is worse than no guide.</p>
<p>What is here is what we can stand behind: how pricing actually works, why floors fail, and how to compare quotes properly.</p>
</div></div>
</section>

%s
%s
""" % (nav, rows, areas_block(), closer())
    page("guides", "Epoxy Flooring Guides | Floor Candy",
         "Straight answers about concrete floors, what changes the price, why epoxy "
         "floors fail, flake versus solid colour, and what to ask before accepting a quote.",
         body, schemas=[bc], active="/guides")


def build_thankyou():
    """Lead confirmation. noindex, not in the sitemap. main.js redirects here
    after a successful Formspree submit, passing first name + event_id in
    sessionStorage (never the URL). The Lead event fires here only."""
    jf = JOB_FACTS
    when = ("within %s" % esc(jf["response_time"])) if jf["response_time"] else "shortly"
    heard = "".join('<button class="chip chip--btn" type="button" data-heard="%s">%s</button>'
                    % (esc(h), esc(h)) for h in HEARD)
    body = """<section class="page-hero ty">
<div class="wrap">
<p class="eyebrow">Quote request received</p>
<h1 data-ty-name>Thanks, your quote request is in.</h1>
<p class="lede">Jarrod will be in touch %s by your preferred method. Want it faster? Text a few photos of the floor to <a href="sms:%s"><strong>%s</strong></a>.</p>
<div class="btn-row">
<a class="btn btn--primary" href="sms:%s">Text photos now</a>
<a class="btn btn--ghost" href="tel:%s">Call %s</a>
</div>
</div>
</section>
<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">What happens now</p><h2>Three steps to a fixed price</h2></div></div>
<ol class="next-steps next-steps--light">
<li><span>1</span><div><h3>We call or text you</h3><p>To book a time for the free on-site look.</p></div></li>
<li><span>2</span><div><h3>Free on-site assessment</h3><p>Jarrod looks at the slab, talks finishes and brings real flake samples.</p></div></li>
<li><span>3</span><div><h3>Your fixed written price</h3><p>With your $%d new-customer saving taken off.</p></div></li>
</ol>
<div class="ty-heard" data-ty-heard hidden>
<h2 class="h3">One quick question: how did you hear about us?</h2>
<div class="chips">%s</div>
<p class="small muted" data-ty-heard-done hidden>Thanks, that helps.</p>
</div>
</div>
</section>
""" % (when, BIZ["phone_href"], BIZ["phone_display"], BIZ["phone_href"],
       BIZ["phone_href"], BIZ["phone_display"], OFFER["saving"], heard)
    page("thank-you", "Thanks, your quote request is in | Floor Candy",
         "Your Floor Candy quote request has been received. Jarrod will be in touch to book "
         "your free on-site assessment.", body,
         noindex=True, head_extra='<meta name="fc-endpoint" content="%s">\n' % FORM_ENDPOINT)


def build_404():
    body = """<section class="page-hero">
<div class="wrap">
<p class="eyebrow">404</p>
<h1>That page isn&rsquo;t here</h1>
<p class="lede">The link may be out of date. Everything Floor Candy does is one of the links below.</p>
<div class="btn-row"><a class="btn btn--primary" href="/">Back to the homepage</a>
<a class="btn btn--ghost" href="/contact">Get a free quote</a></div>
</div>
</section>
<section class="section">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Services</p><h2>What we do</h2></div></div>
<ul class="areas">%s</ul>
<div class="sec-head mt-4"><div><p class="eyebrow">Service areas</p><h2>Where we work</h2></div></div>
<ul class="areas">%s</ul>
</div>
</section>
%s""" % ("".join('<li><a href="/%s">%s</a></li>' % (s["slug"], esc(s["short"])) for s in SERVICES),
         "".join('<li><a href="/service-areas/%s">%s</a></li>' % (l["slug"], esc(l["name"]))
                 for l in LOCATIONS),
         closer())
    doc_path = os.path.join(ROOT, "404.html")
    canonical = SITE + "/404"
    doc = """<!DOCTYPE html>
<html lang="en-AU" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | Floor Candy</title>
<meta name="description" content="That page isn't here. Find Floor Candy's epoxy flooring services and service areas.">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="%s">
<meta name="theme-color" content="#0C0B0C">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/archivo-var-latin.woff2" crossorigin>
<link rel="stylesheet" href="%s">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/assets/favicon-32.png" type="image/png">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
%s
<main id="main">%s</main>
%s
<script src="%s" defer></script>
</body>
</html>
""" % (canonical, v("/styles.css"), header(""), body, footer(), v("/main.js"))
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc)


LEGAL_META = {
    "privacy": "How Floor Candy collects, uses and stores the details you send through "
               "the quote form, by phone or by email. We do not sell your information.",
    "terms": "Terms of use for the Floor Candy website, including how indicative pricing, "
             "the new customer saving and project photography should be understood.",
}


def build_legal():
    for slug, title, heading, paras in [
        ("privacy", "Privacy Policy | Floor Candy", "Privacy policy", [
            "<p>Floor Candy collects the details you send through the quote form or by "
            "phone and email, your name, contact details, suburb and whatever you tell "
            "us about your floor, including photographs, for the sole purpose of "
            "quoting and carrying out flooring work.</p>",
            "<p>We do not sell your details to anyone. We do not share them except where "
            "it is necessary to do the job you have asked us to do.</p>",
            "<p>Quote form submissions are delivered to us by email through Formspree, a "
            "form-handling service, which processes them on our behalf.</p>",
            "<h2>Analytics</h2>",
            "<p>This website records basic interaction events (for example, tapping the "
            "phone number or submitting the quote form) and may use Google Analytics, which "
            "sets cookies, so we can understand which pages "
            "generate enquiries. Where a marketing campaign sends you here, the campaign "
            "reference travels with the enquiry so we know which advert produced it.</p>",
            "<h2>Contact</h2>",
            "<p>To ask what we hold about you, or to have it deleted, email "
            "<a href=\"mailto:%s\">%s</a> or call <a href=\"tel:%s\">%s</a>.</p>"
            % (BIZ["email"], BIZ["email"], BIZ["phone_href"], BIZ["phone_display"]),
        ]),
        ("terms", "Terms of Use | Floor Candy", "Terms of use", [
            "<p>This website is published by Floor Candy. The information on it is "
            "provided in good faith and is general in nature.</p>",
            "<h2>Pricing</h2>",
            "<p>Prices shown, including &ldquo;double garage floors from approximately "
            "$%s&rdquo;, are indicative starting points and not offers or quotations. Final "
            "pricing depends on floor size, existing condition, preparation requirements, "
            "finish and location, and is confirmed in writing after an on-site "
            "assessment.</p>" % "{:,}".format(PRICING["double_garage_from"]),
            "<h2>New customer saving</h2>",
            "<p>The $%d new customer saving applies to a first Floor Candy job and must "
            "be raised at the time of enquiry. It cannot be applied retrospectively.</p>"
            % OFFER["saving"],
            "<h2>Photographs</h2>",
            "<p>Photographs presented on this site as Floor Candy projects are of work "
            "carried out by Floor Candy. Any illustrative imagery is identified as such "
            "and is never presented as a completed Floor Candy job.</p>",
            "<h2>Contact</h2>",
            "<p>Questions about these terms: <a href=\"mailto:%s\">%s</a>.</p>"
            % (BIZ["email"], BIZ["email"]),
        ]),
    ]:
        nav, bc = crumbs([("/", "Home"), (None, heading)])
        body = """%s
<section class="page-hero"><div class="wrap"><p class="eyebrow">Legal</p><h1>%s</h1></div></section>
<section class="section"><div class="wrap"><div class="prose">%s</div></div></section>
%s""" % (nav, esc(heading), "".join(paras), closer())
        page(slug, title, LEGAL_META[slug], body, schemas=[bc], active="")


def build_sitemap_robots():
    urls = [("/", "1.0"), ("/contact", "0.9"), ("/projects", "0.8"),
            ("/service-areas", "0.8"), ("/guides", "0.7"), ("/about", "0.6")]
    for i, s in enumerate(SERVICES):
        urls.append(("/" + s["slug"], "0.9" if s.get("primary") else "0.8"))
    for l in LOCATIONS:
        urls.append(("/service-areas/" + l["slug"], "0.8"))
    for g in GUIDES:
        urls.append(("/guides/" + g["slug"], "0.6"))
    for c in CASES:
        urls.append(("/projects/" + c["slug"], "0.7"))
    urls += [("/privacy", "0.2"), ("/terms", "0.2")]

    body = "\n".join(
        '  <url><loc>%s%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>'
        % (SITE, "" if u == "/" else u, p) for u, p in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + body + "\n</urlset>\n")

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
    return [u for u, _ in urls]


def build_vercel():
    cfg = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "cleanUrls": True,
        "trailingSlash": False,
        "redirects": [
            {"source": "/garage-floor-coating", "destination": "/garage-epoxy-flooring", "permanent": True},
            {"source": "/garage-floor-coating.html", "destination": "/garage-epoxy-flooring", "permanent": True},
            {"source": "/floor-assessment", "destination": "/contact", "permanent": True},
            {"source": "/floor-assessment.html", "destination": "/contact", "permanent": True},
            {"source": "/process", "destination": "/concrete-preparation-crack-repair", "permanent": True},
            {"source": "/process.html", "destination": "/concrete-preparation-crack-repair", "permanent": True},
            {"source": "/lp/garage-floors-newcastle", "destination": "/service-areas/newcastle", "permanent": True},
            {"source": "/services", "destination": "/premium-flake-flooring", "permanent": True},
            {"source": "/services.html", "destination": "/premium-flake-flooring", "permanent": True},
            {"source": "/gallery", "destination": "/projects", "permanent": True},
            {"source": "/gallery.html", "destination": "/projects", "permanent": True},
            {"source": "/projects/shop-fit-out-tiled-floor-to-flake",
             "destination": "/projects/tiled-floor-to-flake", "permanent": True},
        ],
        "headers": [
            {"source": "/(.*)", "headers": [
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
                {"key": "Permissions-Policy",
                 "value": "camera=(), microphone=(), geolocation=(), interest-cohort=()"},
                {"key": "Strict-Transport-Security",
                 "value": "max-age=31536000; includeSubDomains"}]},
            {"source": "/assets/fonts/(.*)",
             "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/assets/img/(.*)",
             "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
        ],
    }
    with open(os.path.join(ROOT, "vercel.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def clean_old():
    """Remove pages replaced by the new architecture."""
    for old in ["garage-floor-coating.html", "floor-assessment.html", "process.html",
                "projects.html", "service-areas.html", "about.html",
                "privacy.html", "terms.html"]:
        p = os.path.join(ROOT, old)
        if os.path.exists(p):
            os.remove(p)
    lp = os.path.join(ROOT, "lp")
    if os.path.isdir(lp):
        shutil.rmtree(lp)


def main():
    clean_old()
    build_home()
    for s in SERVICES:
        build_service(s)
    for l in LOCATIONS:
        build_location(l)
    build_areas_index()
    build_projects()
    for c in CASES:
        build_case(c)
    build_guides_index()
    for g in GUIDES:
        build_guide(g)
    build_about()
    build_contact()
    build_legal()
    build_404()
    build_thankyou()
    urls = build_sitemap_robots()
    build_vercel()
    print("Built %d pages (asset v=%d)" % (len(urls) + 1, ASSET_V))
    for u in urls:
        print("  " + u)


if __name__ == "__main__":
    main()
