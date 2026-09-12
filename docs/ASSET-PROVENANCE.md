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

### Added 25 August 2026 — the social-export set

Thirty-four job photographs supplied by the owner, exported from Floor Candy's
own social posts. Fourteen are used; the rest are held in `~/Downloads/floor candy/`.

| File(s) | Source | Type | Used on | Project proof? |
|---|---|---|---|---|
| `ba-drive-before-414.*` / `ba-drive-after-414.*` | Genuine job photos, same property | Driveway before coating / after coating | Home (before-and-after slider) | **Yes** |
| `ba-garage-before-414.*` / `ba-garage-after-414.*` | Genuine job photos, same property | Garage mid-preparation / completed flake floor | Home (before-and-after slider) | **Yes** |
| `work-flake-garage`, `work-drive-dark`, `work-flake-cream`, `work-alfresco`, `work-flake-brick`, `work-flake-tan`, `work-drive-blue`, `work-path-light` (all `-414.{avif,webp,jpg}`) | Genuine job photos | Finished floors, driveways, paths | Home (recent work grid) | **Yes** |
| `prep-grind-{600,900,1200}.{avif,webp,jpg}` | Genuine job photo, 1536×2048 original | Grinding a driveway, extraction hose in frame | Home (mechanism section) | **Yes** |

**How the two before/after pairs were verified as genuine pairs.** Each pair was
checked side by side against fixed features in frame before being presented as
the same floor: the driveway pair shares the same rock retaining wall, brick
facade and kerb line; the garage pair shares the same ceiling truss rack, wall
doors and louvre door. The garage "before" is labelled **During prep**, not
"Before", because a dust extractor is visible in shot — the slab is already
part-way through preparation. Nothing is presented as a same-frame comparison.

### Added 9 September 2026 — the garage transformation pair

| File(s) | Source | Type | Used on | Project proof? |
|---|---|---|---|---|
| `garage-epoxy-floor-before-{400,600,800,1024}.{avif,webp,jpg}` | Client-supplied photograph, 1024×768 PNG | Bare garage slab before coating | Home (featured project slider + JS-off fallback) | **Yes** |
| `garage-epoxy-floor-after-{400,600,800,1024}.{avif,webp,jpg}` | Client-supplied photograph, 1024×768 PNG | Completed grey flake epoxy garage floor | Home (featured project slider, recent-work grid, JS-off fallback) | **Yes** |

**How this pair was verified as the same garage.** Both frames share the same
side window and its external blind, the same two internal doors either side of
the back wall, the same pair of ceiling fluorescent tubes, and the same red
opener pull-cord hanging in the same position. The photographer's vantage point
differs slightly — the "before" is taken from just outside the roller door and
the "after" from inside it — so **neither frame has been cropped**. Both are
emitted at full 4:3 frame and the slider renders them at 4:3, so the comparison
applies identical framing treatment to both sides. Nothing has been brightened,
straightened or retouched.

The unfinished "before" frame is used **only** inside the labelled comparison and
its fallback. The recent-work grid and any promotional surface use the finished
frame only. Both sides are generated from one source file each by
`tools/build-garage-project.py`; the uploads are not duplicated in the repo.

**Still outstanding (client requests not yet actionable):**

- **Pathway photographs.** The client has asked for the existing pathway images
  (`work-path-light-414.*`) to be replaced once better ones are supplied. Not
  supplied as at 9 September 2026 — the current image remains in place.
- **Metallic epoxy project.** No metallic photography has been supplied. The grey
  flake garage above is **not** to be relabelled as metallic. A separate project
  and, if warranted, a separate service page are to be created once genuine
  metallic photographs exist.

**Resolution caveat.** These are 414×414 social exports, not originals. The
recent-work grid is emitted at native size and displayed no larger. Only
`prep-grind-*` came through at full size (1536×2048).

### AI upscaling — the four before/after images only ⚠️

The four slider images are displayed up to ~880 px, so the 414 px source was
being stretched 2×. They were upscaled to 2160×2160 with **Higgsfield →
`bytedance_image_upscale`** (2K, 2 credits each, 25 Aug 2026) and the web set is
derived from that. Job IDs: `82334bfa`, `47d2dacf`, `f84add0f`, `9990e7f2`.
2K masters kept in `assets/_originals/` (not deployed).

**This is a generative process, so each result was compared against its source
before use.** All four resolve real detail rather than inventing it — the
driveway pair preserves the brick courses, rock wall, planting and the exact
staining pattern on the slab; the garage pair preserves the dust extractor, its
hose routing, the ceiling truss rack, the wall doors and the slab's marks.
Nothing was added, removed or restaged. **The remaining job photographs are not
upscaled** — only these four, because only these are displayed large enough to
need it.

If original-resolution files ever come off the owner's phone, they should replace
these outright: a real pixel beats a reconstructed one, and it removes a
generative step from the proof imagery.

| `assets/img/og-floor-candy.jpg` | Crop of the hero still | Social share card | All pages (`og:image`) | **No — illustration** |

**Edits applied to the genuine set:** resize (Lanczos 3), crop (`prep-grind` only), and AVIF/WebP/JPEG re-encoding. **No content was altered** — no brightening of "after" shots, no colour grading, no retouching. The floors, finishes, geometry, lighting and settings are exactly as photographed.

---

## AI-generated — may NOT be used as project proof ⚠️

| File | Source | Type | Used on | Project proof? |
|---|---|---|---|---|
| `assets/img/hero-garage-{720,1080,1376}.{avif,webp,jpg}` | **Higgsfield**, text-to-image, `hf_20260815_085454_fa1de56c…png`, 1376×768 | Dark flake floor in a modern concrete garage | Homepage hero background | **No — illustration** |
| `assets/img/og-floor-candy.jpg` | 1200×630 crop of the above | Social share card | All pages (`og:image`) | **No — illustration** |
| ~~`assets/videos/hero-loop.mp4`~~ | Higgsfield → Seedance 2.0 | 12.08s silent loop | **Retired 25 Aug 2026.** In git history; excluded from deploy via `.vercelignore` | — |
| ~~`assets/img/hero-poster-*`~~ | First frame of the above | Hero poster | **Retired 25 Aug 2026.** Same as above | — |

**The hero is disclosed on the page itself.** Directly beneath the hero copy:
*"This hero image is an illustration. Every other photograph on this page is a
Floor Candy job."* This is deliberate. The image is a wholly generated space —
not derived from a Floor Candy floor, unlike the retired video — so leaving it
unlabelled would imply a project claim the business cannot support. Labelling it
converts a liability into a trust signal, and it is the only generated asset that
ships. It carries an empty `alt` and is never captioned with a location, client
or date.

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

## Coastal Grain redesign — new non-photographic assets

| Asset | What it is | Honest? |
|---|---|---|
| Build-up cutaway (inline SVG, homepage §7) | A schematic drawing of the five layers of a coated floor, authored by hand. Carries no thicknesses, no product names and no performance figures, and is captioned "A cutaway, not to scale." | Yes — a diagram of a generic build-up, not a depiction of a specific Floor Candy job. |
| `swatch--metallic` (CSS gradient, finish tabs) | A drawn impression of a metallic finish. Labelled **"illustration — samples shown on site"** on the image itself. | Honest as an illustration. It is **not** evidence Floor Candy installs metallic floors — see `QUESTIONS-FOR-JARROD.md` §4.5. |
| `swatch--nonslip` (CSS gradient, finish tabs) | A drawn impression of a broadcast-aggregate texture, labelled the same way. | Same caveat as above. |

No stock photography, no AI-generated imagery and no competitor photographs were
added in this pass. The hero (Higgsfield still) and the four before/after images
(Higgsfield 2K upscales) are unchanged from the previous build — their entries
above still stand.
