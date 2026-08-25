# QA Report

Automated rendering QA run in headless Chrome (system Chrome via puppeteer-core) against a local server. **8 pages × 7 viewports = 56 combinations.**

**Result: 49/56 clean.** The 7 flags are one accepted item, explained below.

Viewports tested: 375×812 · 390×844 · 430×932 · 768×1024 · 1024×768 · 1440×900 · 1920×1080

---

## What was checked, on every combination

| Check | Result |
|---|---|
| Horizontal overflow (`scrollWidth` vs viewport) | ✅ 0 px on all 56 |
| Console errors / page errors | ✅ none |
| Failed requests (404s) | ✅ none |
| Exactly one `<h1>` per page | ✅ all pages |
| Heading order (no skipped levels) | ✅ all pages |
| Images with `alt` | ✅ all |
| Images with explicit `width`/`height` (CLS) | ✅ all |
| Title length ≤ 65 chars | ✅ all |
| Interactive targets ≥ 32 px tall | ⚠️ 1 accepted exception |

## Issues found and fixed during QA

1. **Hero CTAs fell below the fold at 1440×900.** The H1 was rendering at up to 76 px and wrapping to four lines, pushing both buttons and the review proof off-screen — a direct conflict with the brief's requirement that the quote CTA and click-to-call be immediately visible. Fixed by re-tuning the hero H1 clamp to `clamp(2.1rem, 1.05rem + 3.3vw, 3.9rem)` with a 16ch measure, and tightening hero padding.

   Verified after fix — distance from viewport top to the bottom of the primary CTA:

   | Viewport | Quote CTA | Call CTA | Google proof |
   |---|---|---|---|
   | 1920×1080 | 814 / 1080 ✅ | ✅ | ✅ |
   | 1440×900 | 634 / 900 ✅ | ✅ | ✅ |
   | 1024×768 | 515 / 768 ✅ | ✅ | ✅ |
   | 390×844 | 566 / 844 ✅ | ✅ | ✅ |
   | 375×812 | 534 / 812 ✅ | ✅ | ✅ |

2. **`favicon.ico` 404 on every page.** Chrome probes `/favicon.ico` regardless of declared PNG icons. Built a real `favicon.ico` (PNG-payload ICO) from `favicon-32.png`.

3. **Heading jump `h1 → h4`** caused by footer section headings. Footer headings changed from `<h4>` to `<p class="ftr-head">` — a footer nav label is not a document heading, and this removed the jump site-wide.

4. **Heading jump `h1 → h3` on the process page.** Added an `<h2>The ten steps</h2>` above the numbered list.

5. **Tap targets under 32 px** on footer links (16 px), brand lockup (26–28 px), header phone (14 px) and `.arrow-link` (28 px). Added vertical padding and a `min-height` so all now clear 32 px.

6. **Page titles 70–74 characters.** All trimmed to ≤ 65.

## Accepted exception

**Landing page — inline phone link at 14 px** (`lp@375/390/430/768`). This is a `tel:` link inside a sentence in a small print block. WCAG 2.5.8 explicitly exempts targets inline within a sentence, and the same page carries a full-size "Call 0435 193 845" button in the sticky header plus a 56 px sticky mobile call bar. No change made.

## Manual visual review

Full-viewport screenshots reviewed at: home 1440×900, home 390×844, assessment 1440×900 and 390×844, garage 1440×900, projects 1440×900, process 1440×900, lp 390×844.

Confirmed: hero contrast holds over the photograph at both scales; the two-tone H1 reads cleanly; mobile stacks CTAs full-width with hierarchy preserved; the sticky mobile bar does not obscure hero content (extra bottom padding added below 861 px); the footer grid reflows correctly at every breakpoint.

## Accessibility

- Semantic landmarks: `header` / `nav` / `main` / `footer`, one `h1` per page, `aria-current="page"` on active nav
- Skip link, visible focus rings (`:focus-visible`, 2 px accent outline, 3 px offset)
- Mobile drawer: `aria-expanded`, `aria-controls`, Escape closes and returns focus to the toggle
- Form: real `<label>` per field, `role="radiogroup"` with `aria-labelledby`, `role="alert"` error slots, `aria-invalid` toggling, focus moved to the step heading on step change
- Decorative imagery `aria-hidden`; hero video `aria-hidden` and never focusable
- `prefers-reduced-motion` disables all reveals, transitions and the hero video entirely
- Contrast: body `#F3F1EE` on `#0B0B0C` ≈ 17:1. Primary button uses near-black text on the accent (≈5.3:1) rather than white (which would be 3.97:1 and fail AA)

## Performance posture

Measured artefact sizes (not lab scores):

| Asset | Size |
|---|---|
| `styles.css` | 27 KB → **6.4 KB gzip** |
| `main.js` | 9.9 KB → **3.4 KB gzip** |
| `index.html` | 32 KB → **7.9 KB gzip** |
| Hero poster (AVIF 1920) | **113 KB** (target < 180 KB) |
| Hero loop MP4 | **2.8 MB** (target < 3 MB), deferred, desktop only |
| Font | **34 KB** self-hosted variable woff2, preloaded |

Design decisions supporting the Core Web Vitals targets:
- **LCP** — the hero poster is an AVIF preloaded with a viewport-matched `media` query and `fetchpriority="high"`. The video is never in the LCP path: `preload="none"`, attached only after `window.load` plus a 240 ms delay.
- **CLS** — every `<img>` has explicit `width`/`height`; the hero is a fixed `100svh`; the font is preloaded with `font-display: swap` on a single family.
- **INP** — one small script, no framework, no third-party JS, passive scroll listeners, IntersectionObserver for reveals.
- **Zero third-party origins.** No Google Fonts, no analytics, no tag manager, no chat widget.

**Not measured:** Lighthouse scores. Chrome's extension bridge was unavailable in this environment and I did not run a Lighthouse audit, so no score is claimed. Run it against the preview URL before launch.
