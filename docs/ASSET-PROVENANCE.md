# Asset Provenance

Every visual asset in the deployed site, where it came from, and whether it may be presented as proof of Floor Candy's work.

**The rule this table enforces:** only genuine Floor Candy photography may be presented as a project, a result, or evidence of workmanship. Nothing generated or licensed may carry a project claim.

---

## Genuine Floor Candy photography — may be used as project proof ✅

| File(s) | Source | Type | Used on | Project proof? |
|---|---|---|---|---|
| `assets/images/fc4.jpg` → `assets/img/garage-flake-finished-*.{avif,webp,jpg}` | Genuine Floor Candy job photo (phone camera, 1423×640) | Finished flake epoxy garage floor | Home (services card, recent work), Garage floors, Projects, Ads LP, OG image | **Yes** |
| `assets/images/fc2.jpg` → `assets/img/prep-grinding-extraction-*.{webp,jpg}` | Genuine Floor Candy job photo (phone camera, 640×1422) | Preparation in progress — floor grinder + Hilti VC 40-U dust extractor | Home (preparation section), Process, Projects | **Yes** |
| `assets/images/fc1.jpg` → `assets/img/polished-concrete-finished-*.{webp,jpg}` | Genuine Floor Candy job photo (phone camera, 640×1422) | Finished polished concrete interior | Home (preparation section, services card), Projects | **Yes** |
| `assets/images/fc3.jpg` → `assets/img/driveway-sealed-*.{webp,jpg}` | Genuine Floor Candy job photo (phone camera, 1440×648) | Finished sealed concrete driveway | Home (services card, recent work), Projects | **Yes** |
| `assets/img/og-floor-candy.jpg` | Crop of fc4.jpg | Social share card | All pages (`og:image`) | Yes |

**Edits applied to the genuine set:** resize (Lanczos 3), mild unsharp mask, and AVIF/WebP/JPEG re-encoding only. **No content was altered** — the floors, finishes, geometry, lighting and settings are exactly as photographed.

---

## AI-generated — may NOT be used as project proof ⚠️

| File | Source | Type | Used on | Project proof? |
|---|---|---|---|---|
| `assets/videos/hero-loop.mp4` | **Higgsfield → Seedance 2.0**, image-to-video, `start_image` = genuine `fc4.jpg` | 12.08s silent loop, 1920×824, H.264, 2.8 MB | Homepage hero background (desktop only) | **No — motion only** |
| `assets/img/hero-poster-*.{avif,webp,jpg}` | First frame of `hero-loop.mp4` | Hero poster / LCP image | Homepage hero | **No — see note** |

**Generation record for `hero-loop.mp4`:**
- Platform: Higgsfield (Pro plan) · Model: `seedance_2_0` · Mode: image-to-video
- Job ID: `0ea4d960-8acc-4459-8aee-bde66754ece5` · Source media ID: `df62ce7b-6904-4818-84d9-06e1cc6af7f6`
- Settings: duration 6s, resolution 1080p, mode `std`, aspect `auto`, `generate_audio: false`, seed default
- Cost: **54 credits**
- Raw output: 2206×946, 6.04s, 15.2 Mbps, 11 MB (not committed)
- Post-processing (ffmpeg): scaled to 1920 wide, **palindrome concat** (forward + reversed) so the loop point is invisible, CRF 31, no audio track, `+faststart` → 12.08s / 2.8 MB
- Prompt: recorded in full in `OPENART-ASSET-PROMPTS.md`

**Why the hero is classified "motion only", and why that matters.** The clip is derived from a genuine Floor Candy floor and was inspected frame-by-frame before use: the floor finish, flake pattern, walls, doorway and steps are preserved, with a slow camera push added. It is not a fabricated space. But it *is* generated motion, so it is never captioned as a project, never labelled with a location, client or date, and carries `aria-hidden="true"`. All project claims on the site rest on the still photography above. The poster is the clip's own first frame, which closely matches `fc4.jpg`.

**Reduced-motion, mobile, save-data and slow connections never load the video** — they get the poster still.

---

## Quarantined — removed from the site entirely 🚫

Moved to `assets/_quarantine/` and referenced nowhere. These were on the previous site.

| File | Assessment |
|---|---|
| `hero-cinematic.jpg` / `-mobile` | **AI-generated CGI** (2304×1296). Fictional LED-lit luxury garage |
| `hero-frame1.jpg` / `-mobile` | First frame of the previous AI hero video — same fictional space |
| `lambo-garage.jpg` / `-mobile` | **AI-generated CGI**. A Lamborghini in a luxury garage. Not Floor Candy's work |
| `process-epoxy.jpg` / `-mobile` | **AI-generated CGI** (2304×1296) |
| `showroom-dark.jpg` / `-mobile` | **AI-generated CGI** (2304×1296) |
| `stone-polishing.jpg` | Suspected AI-generated (1792×1344) |
| `commercial-epoxy-flooring.jpg` | Stock / third-party |
| `garage-flooring-2025.jpg` | Stock / third-party |
| `how-to-apply-epoxy-floor-coating.jpg` | Stock — EXIF creator "Adobe Photoshop 22.3 (Windows)" |
| `manufacturing_facility_epoxy_flooring_jm_00.jpg` | Stock — EXIF creator "ACDSee Ultimate 2021" |
| `man-applying-epoxy-paint-for-concrete.webp` | Stock / third-party |

Also removed: `assets/videos/hero-transform-scrub.mp4` (8.5 MB) and `hero-transform-mobile.mp4` (1.8 MB) — the previous AI-generated, scroll-scrubbed hero.

**How AI/stock was identified:** `2304×1296` and `1792×1344` are characteristic generation output sizes and appear on none of the genuine phone photos; EXIF creator strings identified the stock files; and each was visually inspected. The genuine set carries phone-camera aspect ratios (640×1422 portrait, 1423×640 wide crops) and shows real Australian houses, real equipment (a branded Hilti VC 40-U extractor) and real site conditions.

---

## Other assets

| File | Source | Notes |
|---|---|---|
| `assets/fonts/archivo-var-latin.woff2` | Google Fonts — Archivo variable, latin subset, 34 KB | Self-hosted. SIL Open Font License |
| `assets/logo-mark.png`, `logo-full.png` | Client brand assets | Accent `#F0335F` sampled from the dominant logo colour (`#F03060`) |
| `favicon.ico`, `favicon-32.png`, `favicon.png`, `apple-touch-icon.png` | Client brand assets | `favicon.ico` newly built from `favicon-32.png` |

## Standing rules for future assets

1. Genuine photography only for projects, before/after, case studies and workmanship proof.
2. Generated imagery is permitted for atmosphere and motion only, must never carry a project claim, and must be recorded in this file with model, prompt, settings and job ID.
3. Never present a generated space as a Floor Candy location, and never attach a client, suburb or date to one.
4. Inspect every generated asset before it ships.
