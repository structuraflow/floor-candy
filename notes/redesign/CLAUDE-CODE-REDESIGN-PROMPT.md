# Floor Candy homepage redesign: look like a $20k site

You are redesigning the Floor Candy site I already have in this repo. I am building it myself in Claude Code. The quality bar is my own Northcote & Co concept site (screenshots in `notes/redesign/northcote/`). This has to feel like a $20k premium studio site, not a tidy trade template. Desktop and phone must be equally good.

Do not start writing code until Step 0 is done and I have answered your questions.

## Ground rules

- **Work in** `~/Projects/floor-candy`. Plain HTML, CSS and JS. No build step, no framework, no npm. GSAP + ScrollTrigger from a CDN is allowed, same as Northcote.
- **Facts only.** Use the real photos, prices, reviews, hours, phone, email and areas already on the site. Never invent reviews, review counts, years in business, warranties, insurance, licences, cure times or testimonials. If a fact is not in the current pages or `PLACEHOLDERS.md`, leave it out or ask.
- **Placeholders stay placeholders.** `PIXEL_ID`, `GA4_ID`, warranty terms, ABN, job suburbs, floor sizes, days on site, walk-on and drive-on times, and the $250 offer wording still waiting on Jarrod: do not fill them with guesses. Read `PLACEHOLDERS.md` and `docs/QUESTIONS-FOR-JARROD.md`.
- **No em dashes** in any site copy. Use a full stop, a comma or a colon. Hyphens in phone numbers and ranges (Mon-Fri, 7am-7pm, $2,450) are fine.
- **Do not copy Northcote's name, logo, copy, photos or sample ratings.** Take its typographic system, spacing, grid, buttons and motion discipline, then apply them to Floor Candy.
- **Do not copy code, images or logos from any reference site.** Inspiration only.
- Keep existing pages, URLs, SEO (titles, meta, canonical, og, sitemap, robots), schema, `?h=a/b/c` headline variants, Formspree, thank-you redirect and event tracking working.
- The public email is `floorcandyepoxy@gmail.com`, the phone is `0435 193 845`, hours are Mon-Fri, 7am-7pm, and there is no public showroom. Do not revert to older draft addresses.

## Why the current page fails the bar

Look at the current homepage and at the Northcote frames side by side. The gap is structural, not a missing hover state.

- Northcote uses sentence-case, two-weight headlines at display size, with tight tracking and a lot of quiet paper around them. Floor Candy shouts in all-caps Archivo and paints the second line magenta.
- Northcote's buttons are small rounded rectangles with a clear primary and a hairline or solid partner. Floor Candy's are large pink and grey pills.
- Northcote gives you one place to look: a single hero image, then a statement, then work, then a form. Floor Candy repeats itself (hero slider, then two more sliders, then two "what you get" blocks) and buries the form.
- Northcote's pain and proof are typographic. Floor Candy falls into the slop pattern of three identical outlined cards, the same radius on every box, and frosted ghost buttons.
- At 1440px the current page has empty bands under the hero and under the checklist. Northcote never leaves a blank scene.

Rebuild the system, then the page. Do not run "make it better" loops against the current CSS.

## Step 0: read, outline, ask, wait

1. Read `index.html`, `styles.css`, `main.js`, `PLACEHOLDERS.md`, `notes/`, `docs/QUESTIONS-FOR-JARROD.md` and `docs/ASSET-PROVENANCE.md`.
2. The Northcote reference screenshots are already in `notes/redesign/northcote/` (desktop 1440 and phone 390 frames). Read every one of them. Score the current Floor Candy homepage against them before you propose anything.
3. Reply with a section-by-section outline: new scroll order, the one place the eye should land in each section, proposed headlines (existing copy kept where it is already strong), the design-system tokens you will implement, and the motion list. Then ask your clarifying questions. **Wait for my OK before changing any code.**

Questions you must ask, unless I have already answered them in this chat:

- Confirm we drop the "$2,600" regional starting price so the only published start is "Double garages from $2,450" plus "new customers save $250".
- Confirm we do not publish a Google review count until I have checked the live profile. Last noted figure (5.0 from 3, 10 August 2026) is stale. The landing page currently shows two coating reviews and withholds the stone-polishing one. Do not invent a number.
- Confirm the hero focal element is the existing same-position garage before/after slider, not a generated or stock image.
- Confirm the sticky mobile bar stays Call, Text and Get my free quote, with WhatsApp remaining in the footer, the menu and the floating button.

## Design system (lock this, then build)

Adapt Northcote's system. Do not copy its green accent or Inter Tight. Floor Candy keeps its own logo and its magenta, used the way Northcote uses green: tiny, not as a second headline colour.

### Colour

```css
:root {
  --paper:      #F7F5F2;  /* warm off-white page */
  --paper-2:    #EFECE7;  /* alternate band */
  --ink:        #0C0B0C;  /* logo ground, primary text */
  --ink-2:      #1A1A1A;
  --ink-3:      #2A2A2C;
  --muted:      #6B6B6B;
  --muted-dark: #A8A6A1;
  --line:       #E4E0DA;
  --line-dark:  #33333A;
  --pink:       #F9019F;  /* logo magenta: dots, selected, one accent word max */
  --pink-btn:   #DB008B;  /* accessible button fill, white label 4.79:1 */
  --pink-deep:  #C7007F;  /* hover / active */
  --pink-ink:   #FFFFFF;
}
```

Dark bands use `--ink`, not a tinted purple-black. No gradients, no indigo, no frost.

### Type

Self-host woff2 files (same pattern as the current Archivo setup). Both faces are SIL Open Font License, fine for commercial use. Check the licence files are in the repo.

- **Headlines:** Bricolage Grotesque, weights 400 and 700 mixed inside one line (bold first thought, light second thought), letter-spacing `-0.04em`, line-height `0.95`, sentence case. Never all-caps headlines.
- **Body, UI, buttons, form:** Source Sans 3, 400 and 600, line-height 1.6.
- Using one family at one weight for everything is a fail.

```css
  --fs-micro: 0.75rem;     /* 12px labels, sentence case, colour --muted, tracking 0.02em max */
  --fs-small: 0.875rem;    /* 14px */
  --fs-base:  1.0625rem;   /* 17px */
  --fs-lead:  1.25rem;
  --fs-h3:    clamp(1.25rem, 1.1rem + 0.6vw, 1.75rem);
  --fs-h2:    clamp(2.25rem, 1.4rem + 3vw, 4.25rem);
  --fs-h1:    clamp(3rem, 1.6rem + 6vw, 7rem);
  --fs-stat:  clamp(2rem, 1.4rem + 2vw, 3.25rem);
```

### Space, grid, hairlines, radius

```css
  --sp-1: 0.5rem;  --sp-2: 1rem;   --sp-3: 1.5rem;
  --sp-4: 2.5rem;  --sp-5: 4rem;   --sp-6: 6rem;
  --sp-7: 8rem;
  --wrap: 1440px;
  --gutter: clamp(1.25rem, 4vw, 3rem);
  --header-h: 72px;
  --radius-btn: 6px;
  --radius-card: 0px;     /* editorial, hairline-framed, not rounded tiles */
  --radius-media: 2px;    /* images and sliders share this, always */
  --hairline: 1px solid var(--line);
  --ease: cubic-bezier(0.2, 0, 0.2, 1);
```

12-column asymmetric grid, like Northcote. Generous whitespace, but no dead bands. Section padding is `--sp-6` (tighter on phone: `--sp-5`). Do not invent min-heights, pinned spacer scroll, or reveal transforms that leave a blank strip under a section.

1px hairlines only. Do not use the same large corner radius on every box. Do not put the three pain points in three identical outlined cards.

### Buttons

Rebuild all buttons. The current full-pill, 52px, one-size-shouts-pink set is part of why this does not look like Northcote. Every button in a set is the same height. Style, not size, marks the primary action. Min tap height 48px (52px on phone).

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  min-height: 48px; padding: 12px 22px;
  font-family: "Source Sans 3", system-ui, sans-serif;
  font-size: 0.9375rem; font-weight: 600; letter-spacing: 0;
  text-transform: none; text-decoration: none;
  border: 1px solid transparent; border-radius: var(--radius-btn);
  cursor: pointer;
  transition: background-color .2s var(--ease), color .2s var(--ease),
              border-color .2s var(--ease), transform .12s var(--ease);
}
.btn:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
.btn:active { transform: scale(0.98); }

.btn--primary { background: var(--pink-btn); color: #fff; border-color: var(--pink-btn); }
.btn--primary:hover { background: var(--pink-deep); border-color: var(--pink-deep); color: #fff; }
.btn--primary:active { background: #B00072; border-color: #B00072; }

.btn--secondary { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.btn--secondary:hover { background: var(--ink-2); border-color: var(--ink-2); color: var(--paper); }
.btn--secondary:active { background: #000; }

/* On dark bands, secondary flips to a solid white fill */
.band--ink .btn--secondary,
.hero--dark .btn--secondary {
  background: #fff; color: var(--ink); border-color: #fff;
}
.band--ink .btn--secondary:hover,
.hero--dark .btn--secondary:hover { background: var(--paper); }

.btn--ghost { background: transparent; color: var(--ink); border-color: var(--ink); }
.btn--ghost:hover { background: rgba(12, 11, 12, 0.06); }
.band--ink .btn--ghost,
.hero--dark .btn--ghost { color: #fff; border-color: rgba(255,255,255,.55); }
.band--ink .btn--ghost:hover,
.hero--dark .btn--ghost:hover { background: rgba(255,255,255,.08); }
```

No `backdrop-filter` on buttons or cards. Frosted glass is a fail, even though Northcote used it on sample rating cards. Floor Candy trust and rating modules are solid surfaces with a 1px hairline.

Specific CTAs only. Keep "Get my free quote" and "Call 0435 193 845". Never "Get started" or "Learn more".

### Phone (390)

Must look as resolved as the 1440 layout, not a squeezed desktop.

- Hero stacks: eyebrow, H1, price, two full-width buttons, then the slider at the width of the page.
- Trust strip can wrap to two lines; it must not overflow.
- Pain statement can break across lines but must not crop mid-word.
- Form cards sit two per row (one per row when the label is long), minimum 48px tall tap target.
- Showcase sliders stack, same component as desktop, full width, handles easy to drag.
- Sticky `.mobar` is always visible, with `env(safe-area-inset-bottom)`, and no page content hides behind it (`padding-bottom` on `body` stays).
- The WhatsApp float stays clear of the bar and must not cover a button label.

## New homepage structure

The current page wanders: trust is crammed into the hero, two more sliders repeat the hero, "what's included" and "what you get before you commit" say the same thing, a kit-vs-us block and a services grid interrupt the path, and the form arrives late. Rebuild the homepage in this order. One thought per section. One place to look.

1. **Nav.** Logo left, links, phone, primary "Get my free quote". Sticky. Invert to light type on dark bands (ScrollTrigger or a small IntersectionObserver). Phone: logo, quote button, menu icon, full-screen menu. Eye: the logo, then the quote button.
2. **Hero.** One focal element only: the existing same-position garage before/after slider (the one already captioned "photographed from the same position"). Short eyebrow that does not wrap, e.g. "Garage, patio and shed floors across the Mid North Coast". Keep the current H1: "A garage floor you'll actually want to show off." Price anchor in the hero: "Double garages from $2,450" and "New customers save $250". Two CTAs: Get my free quote (primary, jumps to `#quote`) and Call 0435 193 845 (secondary). Owner line can stay: "You deal directly with Jarrod, the owner." Asymmetric split, Northcote-style: type one side, large media the other. On phone, type first, slider under the CTAs, full width, nothing clipped. Eye: the before/after, then the price, then the primary button.
3. **Trust strip.** A quiet hairline row, not three feature cards: 5.0 on Google (no count unless I confirm one), free on-site assessment, fixed written price, owner-led. Eye: the four facts as one line.
4. **Pain.** Name the pain first. Keep the thought "The garage is the biggest room in the house. It's also the worst floor." Set it as a two-weight statement, not all-caps, not a pink second line shouting at the same size as the first. Under it, a hairline list (not three identical cards) for cracked stained concrete, dust through the house, and a room you keep shut. Eye: the statement.
5. **Showcase of real jobs.** This replaces "The same floor, twice" as a dumping ground. One featured slider plus a small set of genuine project photographs already on the site (the work grid). Captions are short and public. The two current sliders stay, but they must share one component: same aspect ratio, same `--radius-media`, same handle, same label style, same alignment on the grid. No offset, no one-rounded-one-square pair. Eye: the finished floor in the first slider.
6. **What's included, plus one consistent price.** Merge "Everything that goes into your floor" and "What you get before you commit" into one section. Checklist can stay (assessment, mechanical grind, crack repair where needed, base coat, flake broadcast, clear topcoat, walkthrough). One price card: "From $2,450", "New customer saving -$250". Small print may say the exact price depends on size, slab condition, preparation, finish and location, and is given as a fixed written price after a free on-site look. It may say travel-heavy jobs can cost more. It must not publish a second starting price. Eye: the $2,450 figure, then the checklist.
7. **Process.** Five steps already on the site, tightened: tell us about the floor, we assess, preparation, the system goes down, handover. Do not invent days on site or cure times. Those are still empty slots. If you keep the "DIY kit or a cheap quote" versus "A Floor Candy floor" comparison, fold it in here as a short hairline pair, not a new full-width section. Only claim what the current copy already claims (mechanical grind, crack repair, full broadcast, clear topcoat). Eye: step 1, then the sequence.
8. **Reviews, real only.** Heading can stay close to "What customers say about Jarrod". Show only the two coating reviews already on the homepage (Reece Hawes and Miranda). The Miranda Bell natural-stone review stays off this landing page because it is not a floor coating; do not quietly drop it from the data, and do not present it as epoxy proof. Do not add stars, counts or names that are not in the source. "Read our Google reviews" may keep the existing Maps CID link; "Leave Jarrod a Google review" may keep the existing `g.page` link. Eye: the first quoted sentence.
9. **Service areas.** Taree, Forster, Tuncurry, Harrington, Blueys Beach, Pacific Palms and the Mid North Coast, with selected work in Newcastle and the Hunter. Text and links only. Do not put back a map pin. There is still no `/service-areas/tuncurry/` page; do not invent one. Eye: the area list.
10. **Tap-card quote form** (`#quote`). Keep the existing 4-step form and field names. Steps: what are we coating; roughly how big and when; where is the floor; where should Jarrod send the quote. Card tap selects, 250ms auto-advance, reserved height so the page does not jump, focus management, back button, "Step X of 4". After size is chosen, keep the honest ballpark already used: double garages start from $2,450, before the $250 new-customer saving, exact price after a free on-site look. POST stays on Formspree `https://formspree.io/f/mrpeeawq` with the same hidden fields (`_subject`, `_gotcha`, `page_url`, `referrer`, `landing_page`, `headline_variant`, `event_id`). Successful submit still goes to `/thank-you`. Do not empty the action in favour of the old GHL notes; that doc is stale. Eye: the current step's cards.
11. **FAQ.** Keep the current ten questions and their honest answers, including the warranty answer that admits terms are not published yet. Update only if a price sentence would otherwise disagree with the single $2,450 start. Eye: the first question.
12. **Footer.** Logo, short area line, explore links, 0435 193 845, floorcandyepoxy@gmail.com, WhatsApp, hours, mobile service / no showroom, Facebook, Google, Privacy, Terms. Eye: contact details.
13. **Sticky mobile bar** (existing `.mobar`). Call, Text, Get my free quote. Quote links to `#quote` on the homepage and `/contact#quote` on inner pages. Sits above the safe area. Keep the WhatsApp float clear of it, as now.

After the homepage is signed off, roll the same tokens, type, buttons, header, footer and mobile bar to the inner pages. Do not restyle inner pages first.

The homepage HTML is currently emitted by `tools/build-site.py`. For this pass, treat `index.html`, `styles.css` and `main.js` as the source of truth. Update or retire the homepage template in `tools/build-site.py` so a later regenerate cannot wipe the redesign. Do not run a full site regenerate until that is safe.

## Motion

Every moving piece has a job. If it is only decoration, cut it. Respect `prefers-reduced-motion: reduce`: no pins, no rolls, no scrub, no stagger; just show the content. Aim for 60fps; animate transform and opacity only.

| Motion | Job |
|---|---|
| Hero type fade/slide on load (once) | Let the H1 land, then the eye go to the slider |
| Hero slider scrubs from before to after as the hero enters, then becomes a normal drag slider | Prove the work without a second explanation |
| Nav colour invert on dark bands | Keep the bar readable |
| Pain statement word or line reveal on scroll, `once: true` | Deliver the one thought of that section |
| Showcase images fade up once | Let the floors be seen, not the animation |
| Form steps slide, height reserved | Make the four taps feel like one control |
| Selected form card: hairline + check, then advance | Confirm the tap |
| Sticky bar present on phone from the start | Call, text or quote are always reachable |

No looping background motion, no hover-lift on every card, no parallax for its own sake, no second hero 3D object.

## Fixes that must ship with the redesign

1. **Captions that read like internal notes.** Replace them with short public lines, and stay honest:
   - Tiled slider: "Same room, before and after." (It is allowed to be a slightly different camera position; do not pretend otherwise, and do not narrate the camera notes.)
   - Prep slider: "During preparation, then finished." (Keep the "During prep" label on the first frame. Do not call it an untouched before.)
2. **One price.** Remove "generally start around $2,600" everywhere it appears, including schema FAQ text if needed. The only start is $2,450, with the $250 new-customer saving.
3. **Empty gaps on desktop.** There are large blank bands under the hero and under the checklist. Find and remove the cause (oversized section padding, reveal classes, reserved min-heights, a pin that never fills). The page must feel tight and intentional, like Northcote, not like a slide with a missing scene.
4. **Hero eyebrow wrap.** The current "Taree, Forster & the Mid / North Coast" break is a fail. Shorten or reflow so it stays on one or two clean lines at 1440 and 390.
5. **Mismatched sliders.** One component, one radius, one alignment.
6. **"5.0 on Google" with no count.** Leave the count off until I confirm it. Do not write "from 3 reviews" from old notes.

## Keep, exactly

- Real Floor Candy photographs only as proof of work. No AI, stock or generated image presented as a job. The Higgsfield hero still must not return as a project photo. `og:image` stays a real finished floor.
- Published prices: double garages from $2,450; new customers save $250 on their first floor; free on-site quote and fixed written price.
- Reviews listed above, verbatim, including original punctuation.
- Formspree endpoint, field names, honeypot, UTM / gclid / fbclid capture in `main.js`, and dataLayer events already pushed (`form_start`, `form_step`, `form_floor_type`, `form_submit`, `generate_lead`, `click_call`, `click_sms`, `click_whatsapp`).
- `/thank-you`, `404.html`, `vercel.json`, `sitemap.xml`, `robots.txt`.
- Ad headline variants already in the page: `?h=a` default H1, `?h=b` price-led, `?h=c` pain-led. The chosen variant still sticks for the session and is posted with the lead as `headline_variant`.
- Services and area URLs already in the repo. Existing inner-page content stays factual. The logo files stay as they are; do not redraw them.

## QA (do this before you show me the work)

1. Run the site locally (the repo's `python3 tools/dev-server.py` on port 8899 is fine).
2. Screenshot every section at 1440 and 390. Ignore any right-edge clip that is clearly a screenshot-tool artefact; still check on a real 390 viewport that nothing runs off.
3. Score each section pass or fail against the Northcote frames in `notes/redesign/northcote/` and against this 8-point $10k checklist: point of view, typography, colour, hierarchy, imagery, motion, mobile, polish.
4. Fail and fix, do not "improve" in vague loops, any of: all-caps headlines, pink used as a second display colour, identical card trios, identical fat radii, frosted glass, generic CTAs, invented facts, layout gaps, clipped type, mismatched sliders, a second starting price, or a review count I did not confirm.
5. Then run Lighthouse on the local or preview URL and fix obvious accessibility, contrast and performance issues. Self-host the new fonts; do not leave a render-blocking Google Fonts CSS request in the head if you can avoid it.

Show me the 1440 and 390 screenshots, the pass/fail scores, and the Lighthouse notes when you are done.

## Reference pack (21st.dev and premium sites)

Read `notes/redesign/references/INSPO.md` before the outline. It lists ranked picks for each homepage section, with vanilla rebuild notes and links.
- `references/21st/*.tsx` is React source for patterns only. Rebuild each one in plain HTML, CSS and JS: no React, no Tailwind, no build step. Keep each MIT credit in a code comment.
  - WorkPageHero: the pinned inset-to-full-bleed hero expand.
  - Magnetic Button: subtle pull, disabled under reduced motion.
  - ibelick Image Comparison: the single shared before/after slider used everywhere.
  - Motion scroll word reveal: for the pain statement.
- `references/sites/*.jpg` are premium studio and flooring sites. Use them for mood only, alongside Northcote. Never copy their images, copy or logos.
- Northcote stays the gold standard. Where a reference disagrees with it, Northcote wins.
