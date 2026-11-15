# Floor Candy landing upgrade: research + audit (15 Nov 2026)

Branch `landing-upgrade`, checkpoint tag `pre-landing-upgrade` (238a10b). Nothing below is built yet.

## 1. Live site today (www.floorcandyepoxy.com, scraped 15 Nov)

Live is the 11 Oct deploy (v=16). The 1 Nov SEO/perf pass is local only.

Home section order (live): hero (H1 "Epoxy floors worth showing off", from $2,450, save $250) > trust strip
(5.0 on Google, free assessment, fixed price, owner-led) > **quote form (2nd section)** > 4 promises > before/after x2
> premium flake > preparation > 6 services > 5-step process > recent work grid (8 x 414px) > pricing > reviews x3 >
service areas + map > FAQ x10 > closer CTA > footer. Sticky mobile bar: Call | Get a quote. WhatsApp float.

Form (one long form, Formspree `mrpeeawq`): name, mobile, email, suburb, area_type (5 radios), approx_size, details,
contact_preference, page_url, referrer, honeypot. UTM/gclid/fbclid are captured in main.js.
Tracking scripts: none (as expected).

## 2. What the best competitors do (patterns only)

**Bedrock Garage Floors (Austin)**: the sharpest landing page in the set.
- H1 sells the outcome + speed: "A showroom garage floor by tomorrow night."
- Price in the first sentence ($8/sq ft), then a **size slider that shows a live ballpark** ($4,000 for 500 sq ft).
- Owner named under the CTA ("You talk to Grant, the owner"), plus hours and a missed-call text promise.
- 4-chip risk strip: firm written price, 15-yr written warranty, insured, done in 1 day.
- Before/after drag slider in the hero itself.
- **3-step booking form**: what are we coating (cards) > pick a day + time > name/phone/address.
- "Kit vs us" comparison table (box-store epoxy vs our system).
- "What you get before you pay a dollar" block. FAQ answers objections bluntly, including the uncomfortable one (licensing).
- Note: its imagery is AI-generated (hf_ filenames) and labelled "Example". Not a model for Floor Candy's proof.

**Ironclad Floors (Sydney)**
- Before/after sliders captioned **system · m² · suburb** with a one-line job story.
- Trust row in the hero: since 2011, 10-yr warranty, $20m public liability.
- Prep section: "The job is won or lost in the preparation". Floor Candy already owns this angle.
- Price in the meta description ("garage floors from $40/m²").
- Form asks space type, system, m², condition, suburb, timeline.

**Bestcoat Epoxy**: blocks automated access, so it couldn't be reviewed. The flake-library idea from the brief is covered by Bedrock's finishes grid.

**Northcote & Co (our own concept)**, worth borrowing:
- 4-step card form with GSAP slide transitions and height reservation (no layout jump), focus management on the done step.
- Word-by-word scroll reveal on a statement line; `once:true` fade-ups; reduced-motion respected.
- Project cards with stat lines.

## 3. Gaps vs the brief (and vs Bedrock, the bar to beat)

| # | Gap | Fix | Blocked on |
|---|-----|-----|-----------|
| 1 | Hero is an AI still of a sports-car garage, the first thing every ad click sees | Real job photo, or a before/after in the hero (Bedrock pattern) | Full-res originals. Every real photo is a 414px social export |
| 2 | H1 is SEO-shaped ("Epoxy & flake garage floors in Taree…"), not an outcome promise | Ad-matched headline variants via `?h=a/b/c`; keep the geo phrase in the eyebrow + title tag | – |
| 3 | No owner name/face above the fold | "Jarrod quotes every job himself" line | Jarrod photo (optional) |
| 4 | Form is one long screen | 4-step tap-card form, "Step X of 4", ballpark after step 2, localStorage resume | – |
| 5 | No ballpark tool | Size chips > "double garages start from $2,450 before your $250 saving" | Real per-m² rate for a true slider |
| 6 | No thank-you page, so Meta has nothing to optimise on | /thank-you (noindex) + Lead event with event_id | Pixel ID, GA4 ID |
| 7 | Stone-polishing review shown on a garage page | Move it lower / drop it from the garage landing; keep 2 relevant ones | – |
| 8 | No "kit vs Floor Candy" comparison | Add, using only true claims (diamond grind, crack repair, full broadcast, clear topcoat) | – |
| 9 | No timeline / cure times | FAQ + process slots | **Days on site, walk-on, drive-on times** |
| 10 | No warranty, ABN, insurance | Slots only render when filled | Jarrod |
| 11 | Recent-work grid is 8 tiny 414px images | Fewer, bigger, captioned project cards | Suburb per photo |
| 12 | Unused 2.9MB `hero-loop.mp4` in assets | Delete | – |
| 13 | 6 decorative `alt=""` | Correct as-is for decorative; check the rest | – |
| 14 | No Tuncurry page (listed but unlinked) | Add from area template | – |
| 15 | No step tracking, no tel/sms/wa click events | dataLayer events (already vendor-neutral) | IDs |

## 4. What I need from Jarrod (fastest wins first)
1. 5–10 original full-res photos off his phone (finished garages, wide shots). **This is the single biggest upgrade.**
2. Typical days on site, walk-on time, drive-on time.
3. Is the free measure/quote and free flake sample true? (Both currently implied.)
4. Suburb for each before/after job.
5. Warranty terms, ABN, public liability amount (render only when supplied).
