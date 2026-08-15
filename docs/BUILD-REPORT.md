# Build Report — Phase 3

Rebuild of floorcandyepoxy.com on branch `redesign/phase3-premium`. Production untouched.

## What was built

A 10-page static site with a custom design system, built on the existing stack (HTML/CSS/vanilla JS, Vercel). No framework was introduced — the site ships **zero JavaScript dependencies and zero third-party origins**.

| Page | Path | Purpose |
|---|---|---|
| Home | `/` | Full conversion narrative, 12 sections |
| Garage floor coatings | `/garage-floor-coating` | Primary service, primary organic target |
| Projects | `/projects` | Genuine work only |
| Process | `/process` | The ten-step system + conduct commitments |
| About | `/about` | Owner-led positioning |
| Floor assessment | `/floor-assessment` | 3-step form, the conversion page |
| Google Ads LP | `/lp/garage-floors-newcastle` | `noindex`, minimal nav, single path |
| Privacy · Terms · 404 | | Supporting |

## Design system

- **One typeface** — Archivo variable (400–900), self-hosted, latin subset, **34 KB**, preloaded. No Google Fonts origin.
- **One accent** — `#F0335F`, sampled programmatically from the dominant colour in `logo-mark.png` (`#F03060`). The logo's pink→orange gradient was deliberately *not* reproduced as a gradient; the brief called for one controlled accent, and gradient washes are what make trade sites look cheap.
- **Accessible primary button** — near-black text on the accent (≈5.3:1). White on the accent would be 3.97:1 and fail AA, so the more distinctive option was also the correct one.
- Full token set: surfaces, hairlines, fluid type scale, spacing, radii (2–5 px — restraint reads as premium), motion tokens, media aspect ratios.
- Components: buttons (3 variants × 2 sizes), arrow links, cards, service cards, figures, numbered steps, failure grid, review cards, FAQ, callout, form controls, choice chips, step bar, trust strip, mobile sticky bar.

## Homepage structure

1. Hero — genuine floor, location eyebrow, H1, dual equal-weight CTAs, verified Google proof
2. Trust strip — owner-led · free assessment · diamond-ground prep · final walkthrough
3. Preparation → finished (genuine photography, honestly captioned)
4. What we coat — garage / driveway / interior
5. Why floors fail — five named failure modes
6. The Floor Candy Surface Preparation System — ten steps
7. Recent work
8. Genuine Google reviews
9. The free floor assessment offer
10. Objection-led FAQ (8 questions)
11. Final CTA
12. Service-area footer

## Hero

**Generated** on Higgsfield with Seedance 2.0, image-to-video from the genuine `fc4.jpg` garage floor. 54 credits. Post-processed into a 12.08s palindrome loop so the loop point is invisible — **2.8 MB, 1920×824, no audio track, faststart**.

The poster is the clip's own first frame, so there is no visible swap: **113 KB AVIF at 1920**.

Behaviour: poster carries LCP; video is `preload="none"` and attached only after `window.load` + 240 ms; skipped entirely on mobile (<861 px), save-data, 2G, and `prefers-reduced-motion`; removed from the DOM if playback fails. **The hero is designed as a still first, with motion added on top.**

The previous scroll-scrubbed hero — which the brief explicitly rules out — has been removed, along with its 8.5 MB desktop video.

## Source-of-truth compliance

Every claim traces to `strategy/unknowns-to-confirm.md`.

**Published:** "Servicing Newcastle and the Hunter Region" · 5.0 from 3 Google reviews (verified 10 Aug 2026, count always shown) · all three reviews verbatim · owner-led framing · the approved final-walkthrough sentence · the approved interim warranty position · free assessment offer · the ten-step system.

**Not published anywhere:** warranty duration · installation time · years of experience · project totals · team size · licences · certifications · prices · product-performance, chemical-resistance, UV or slip-rating claims · one-day installation · lifetime warranty · permanent crack elimination · physical address · customer locations · commercial experience · finance options.

**Removed:** the "20-year workmanship guarantee" (4 placements), "200+ Projects", "Licensed & Insured", "5-Star Rated" without a count, "Australia-Wide", the animated stat counters that rendered as zeros, the price estimator that invented "$3,900–$5,400", and the three fabricated testimonials — confirmed as placeholder "Sample content" in the original Google AI Studio design prompt.

Two honesty constraints are carried in the copy: cracks are "repaired where appropriate", never eliminated; and the deposit is stated plainly rather than implying nothing is payable up front.

## Assets

Genuine photography is `fc1`–`fc4` only. 16 AI/stock files were identified and quarantined — including the previous hero, which was AI-generated CGI of a fictional luxury garage. Full detail in `ASSET-PROVENANCE.md`.

The most valuable find: **`fc2` is a genuine preparation photograph** — a floor grinder and Hilti VC 40-U dust extractor mid-job. Phase 2 recorded that this imagery did not exist. It is now the visual proof for the section the entire positioning rests on.

All genuine images derived to AVIF/WebP/JPEG at multiple widths via sharp. Edits limited to resize, mild sharpen and re-encode — no content altered.

## Technical

Semantic HTML · one `h1` per page · skip link · visible focus rings · `aria-current` nav · accessible drawer with Escape and focus return · explicit image dimensions (CLS) · `prefers-reduced-motion` fully respected · canonical URLs · Open Graph · `LocalBusiness` schema with `areaServed` and opening hours · `sitemap.xml` · `robots.txt` (LP disallowed) · 301s for the three removed pages · security headers (HSTS, nosniff, frame options, referrer policy, permissions policy) · immutable cache headers on fonts, images and video.

`aggregateRating` was deliberately left out of the schema — Google discourages self-serving review markup on `LocalBusiness`, and the rating is displayed on-page instead.

## Form

3 steps: the floor → where and when → contact. Inline validation with real messages, `role="alert"` error slots, focus management between steps, loading state, genuine success and genuine failure states. **Never shows a false success.**

Captures UTM, GCLID, gbraid, wbraid, msclkid, landing page and referrer, persisted in `sessionStorage` so cross-page conversions stay attributed. Honeypot spam protection, no CAPTCHA.

## Known gaps

1. **Before/after slider built but not populated.** The component is complete — drag, touch, keyboard (arrows/Home/End), labels, fixed aspect ratio. It is not used, because no *matched* before/after pair of the same floor from the same angle exists. `fc1` and `fc2` may be the same room but that cannot be verified, so they are presented as two separate captioned photographs instead. Populate `[data-ba]` the moment a genuine matched pair is shot.
2. **Form endpoint untested** — see `DEPLOYMENT-NOTES.md`.
3. **No Lighthouse run.** Artefact sizes are measured and reported; scores are not claimed.
4. **Projects page is thin** — four genuine images. That is all the genuine work available, and padding it with stock would defeat the point.
5. **21st.dev MCP unavailable** — not connected to this session, and React components would have introduced a bundler into a zero-dependency static site.
