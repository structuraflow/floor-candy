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

## Coastal Grain redesign

| Asset | What it is | Honest? |
|---|---|---|
| Build-up cutaway (inline SVG, homepage §7) | A schematic drawing of the five layers of a coated floor, authored by hand. Carries no thicknesses, no product names and no performance figures, and is captioned "A cutaway, not to scale." | Yes — a diagram of a generic build-up, not a depiction of a specific Floor Candy job. |
| `finish-solid-414.*` ← `774178748_1221396404371976 82_…jpg` | Genuine Floor Candy job photo (414px social export). A solid-colour coating on an alfresco slab, masking tape still down at the edges. | Yes. The tape is visible and the image carries a "masking still down" plate, in the same spirit as the garage before/after labelled "during prep". |

The drawn metallic and non-slip specimens that appeared in the first draft of
the finish tabs have been **removed** — see `QUESTIONS-FOR-JARROD.md` §4.5.
Every one of the four finishes now shown is a Floor Candy photograph.

No stock photography, no AI-generated imagery and no competitor photographs were
added in this pass. The hero (Higgsfield still) and the four before/after images
(Higgsfield 2K upscales) are unchanged from the previous build — their entries
above still stand.

---

## Update — 21 September 2026 (production rebuild)

The site was rebuilt. **Every image referenced by the built HTML is now genuine
Floor Candy photography.** Verified mechanically:

```
grep -rho 'src="/assets/img/[^"]*"' . --include="*.html"
```

returns 26 distinct files, all from the genuine set listed above.

### Generated imagery removed from the site

| Asset | Was | Now |
|---|---|---|
| `hero-garage-*` (Higgsfield text-to-image) | Homepage hero background | **Not referenced on any page** |
| `hero-poster-*` | Hero poster frame | **Not referenced** |
| `og-floor-candy.jpg` (crop of the generated hero) | `og:image` on every page, and `image` in LocalBusiness schema | **Not referenced** |

The homepage hero is now `garage-flake-finished-*` — a genuine photograph of a
completed Floor Candy flake garage floor. `og:image` sitewide, and the `image`
property of the business schema, now point at the same genuine photograph.

This resolves question 4.6 in `QUESTIONS-FOR-JARROD.md`: the undisclosed
generated hero is no longer on the site, so there is nothing left to disclose.
The files remain in `assets/img/` and in git history; they are simply unused.

### Still carrying a caveat

`ba-garage-before/after-414` and `ba-drive-before/after-414` are **genuine job
photographs that were AI-upscaled** from 414px social exports (recorded above).
The content is real and was verified against source for invented detail. They
are used in the before/after sliders on the homepage and `/projects`.

**Action:** replace with original-resolution photographs off Jarrod's phone when
available. The `garage-epoxy-floor-before/after-*` pair (client-supplied,
1024×768, not upscaled) is the better asset and is the one used as the primary
before/after on the homepage.

### Rule unchanged

Only genuine Floor Candy photography may be presented as project proof. The
build has no code path that renders a stock or generated image as a project —
`tools/build-site.py` draws project imagery from a fixed table of verified files.

---

## Update 2 — 21 September 2026 (logo + hero, on Zach's instruction)

> **Superseded in part.** The first pass used the wrong file
> (`floor_candy_logo_design.png` — an isometric FC hexagon with a pink→orange
> gradient). The correct artwork is
> `~/Downloads/floor candy/new logo new logo.png`. See Update 3.

### Superseded logo attempt

Source: `~/Downloads/floor_candy_logo_design.png` (1254×1254, opaque dark ground).
Two transparent assets were cut from it and are now used sitewide:

| File | Use | Size |
|---|---|---|
| `assets/logo-mark.{webp,png}` | Header, 40×34 | 4.2 KB / 13.5 KB |
| `assets/logo-lockup.{webp,png}` | Footer, 480px wide | 20.6 KB / 92.7 KB |

The dark ground was removed by ramping alpha on the max channel (background is
`#0C0B0C`, everything in the mark is either white or saturated), so both assets
sit on any surface. WebP is served with a PNG fallback.

**Colourway, sampled from the source rather than estimated:**

| Token | Value | Where it came from |
|---|---|---|
| `--ink` | `#0C0B0C` | logo background |
| `--pink` | `#F33852` | start of the wordmark gradient |
| `--orange` | `#FA721E` | end of the wordmark gradient |
| `--grad` | `linear-gradient(100deg, #F33852, #F7522F, #FA721E)` | the CANDY wordmark and the hexagon C |

The site header is now dark so the full-colour mark sits in its native context,
and the gradient drives primary CTAs, the offer flag, eyebrow rules, the
after tag on before/after sliders and the sticky mobile quote button.

### Hero reverted to the generated still

The homepage hero is the **Higgsfield text-to-image** `hero-garage-*` again, on
Zach's explicit instruction of 21 September 2026. This reverses the change made
earlier the same day.

Guard rails kept in place, so the illustration is never passed off as a job:

- `alt=""` — it is decorative, not a project, and carries no project caption
- **`og:image` remains `garage-flake-finished-1440.jpg`**, a genuine Floor Candy
  flake floor, so link previews show real work
- The `image` property of the LocalBusiness schema likewise remains the genuine
  photograph
- It appears in no gallery, no project block and no before/after

Every other image on the site remains genuine Floor Candy photography. The only
generated asset referenced anywhere is this hero backdrop.


---

## Update 3 — 21 September 2026 (correct logo)

**Source: `~/Downloads/floor candy/new logo new logo.png`** (1254×1254, already
has an alpha channel). Brush-script wordmark with a crown, plus an
`EPOXY FLOORING` strapline.

| File | Use | Size |
|---|---|---|
| `assets/logo-head.{webp,png}` | Header — crown + FLOOR CANDY, strapline cropped off so it stays legible at 108px | 23.1 KB / 72.9 KB |
| `assets/logo-full.{webp,png}` | Footer — full lockup including the strapline | 56.6 KB / 231.4 KB |

Both are straight crops at display resolution; the source already had
transparency, so no background removal was needed. WebP with PNG fallback.

**Colourway, measured from the artwork by histogram of saturated pixels — a
single flat hot magenta, no gradient:**

| Token | Value | Contrast |
|---|---|---|
| `--ink` | `#0C0B0C` | — |
| `--pink` | `#F9019F` | 5.18:1 on ink · 4.90:1 for near-black labels on it |
| `--pink-deep` | `#C7007F` | 5.62:1 on white · 5.12:1 on off-white — the only magenta used as text on light |

`#F9019F` is **3.80:1 on white**, so it is never used for text on a light
surface. The earlier `#F33852 → #FA721E` gradient was taken from the wrong
artwork and has been removed entirely.

The logo carries a dark outline around the white lettering, so it is used only
on dark surfaces (header and footer), which is how it was drawn.

---

## Update 4 — 21 September 2026 (new job photographs)

Nine files were added to `~/Downloads/floor candy` on 21 Sep 2026, 09:54–11:44.
They are **not** all job photography — sorted before use:

### Genuine job photographs — now on the site ✅

One commercial shop fit-out, documented through the job. Same room in all of
them, matched by the pendant lights, the window and the white brick wall.

| Source | Shows | Used as |
|---|---|---|
| `BA291B76…jpeg` (1242×897) | Old tiled floor, dust extractor in shot | `shopfit-tiled-before-*` — **before** frame of the homepage/projects slider |
| `B762C6AC…jpeg` (1218×885) | Finished cream and tan flake floor | `shopfit-flake-after-*` — **after** frame, and the work grid |
| `BB6CE6D1…jpeg` (1242×897) | Same room part-way through preparation | `shopfit-prepped-*` — available, not yet placed |
| `0A07FEA9…jpeg` (1206×1599) | Floor ground back, extractor in shot | `shopfit-substrate-*` — work grid |
| `2AB9CA11…jpeg` (1242×1609) | Tiled floor, masking up | `shopfit-masked-*` — available, not yet placed |
| `F9A175FE…jpeg` (1218×1593) | Shop frontage, tiled floor | `shopfit-frontage-*` — **not placed**, see note |

These are the **highest-resolution genuine photographs the project has** — 885 to
1609px against the 414px social exports everything else came from. Derived with
`tools/add-photos.py` (headless-Chrome canvas; PIL is unavailable and `sips`
cannot write WebP), so this set is **JPEG + WebP, no AVIF**. The three landscape
frames were centre-cropped to a shared 1.385 aspect so the slider frames align;
nothing else was altered.

**The driveway before/after has been retired from the sliders** and replaced by
this pair, at Zach's request. The retired pair (`ba-drive-before/after-414`) were
AI-upscaled 414px exports; these are native resolution, which is a straight
upgrade in evidence quality.

**Caption honesty.** The two slider frames are *not* the same camera position —
the finished shot is closer to the floor. The caption says so rather than
claiming a matched viewpoint. The work-grid caption for `shopfit-substrate` says
"existing floor ground back", not "tiles removed", because the photograph does
not establish which.

### Not job photography — deliberately excluded ❌

| Source | What it is | Why excluded |
|---|---|---|
| `8940C69C…jpeg` | Marketing flyer: AI-generated red Ferrari in a neon garage | Generated interior, not a Floor Candy job |
| `BF598EF3…jpeg` | Marketing flyer: real "BEFORE" garage against an AI-generated Porsche "AFTER" captioned *"SAME GARAGE. TOTAL TRANSFORMATION."* | **The after is generated and is not that garage.** Using it would be a fabricated before/after |
| `1d64148e…png` | Duplicate of the logo | Already in use as `logo-head` / `logo-full` |

The flyers are flagged in the build report — they are a credibility risk if run
as advertising, independent of this website.

---

## Update 5 — 21 September 2026 (premium imagery + hero video)

All generated with Higgsfield on Zach's instruction, to lift the visual tier.
**Every item below is decorative. None carries a project caption, none appears
in a gallery, before/after or case study, and none is used as `og:image`.**

| Asset | Model | Use | Notes |
|---|---|---|---|
| `hero-garage-portrait-{414,600,752,1128}.{jpg,webp}` | `gpt_image_2_5`, 9:16 | Phone hero backdrop | Luxury garage interior, high-gloss flake floor. Art-directed: serves only at ≤860px; desktop keeps the earlier landscape still |
| `flake-macro-{600,900,1344}.{jpg,webp}` | `gpt_image_2_5`, 16:9 | Closing CTA band | Abstract macro of a flake surface. `aria-hidden`, behind a heavy scrim |
| `assets/videos/hero-portrait.mp4` | **`seedance_2_5`**, 9:16, 720p, 5s, no audio | Phone hero loop | Image-to-video from the hero still, so the poster and first frame match |

### How the video is shipped

3.24 MB against a ~58 KB critical path, so it is gated rather than assumed:

- The `<picture>` still remains the **LCP** and always paints. The video is a
  separate layer that fades in only once it can actually play.
- `main.js` attaches the source only when: `prefers-reduced-motion` is not
  `reduce`, `navigator.connection.saveData` is false, and `effectiveType` is
  not 2g/3g. It waits for `requestIdleCallback` so it never competes with the
  poster.
- `preload="none"`, `muted loop playsinline`, `aria-hidden`, `tabindex="-1"`.
- With JS off, or on a metered connection, the still simply stays. Nothing
  breaks and nothing is downloaded.

`unlim.available` was **false** for `seedance_2_5`, so this drew credits rather
than the free-trial allowance.

### What was deliberately NOT replaced

Service-page imagery, the gallery, both before/after sliders and both case
studies remain **genuine Floor Candy photography**, including the 414px social
exports. Generated imagery is better looking than some of those photographs;
using it there would trade the one thing the positioning rests on — that the
proof is real — for a nicer picture. The rule holds: real work outranks
decorative imagery.

---

## Update 6 — 21 September 2026 (Ferrari hero, trimmed footer, rebuilt drawer)

The phone hero imagery was regenerated again on Zach's instruction: hyper-real,
with a Ferrari and a spectacular flake floor.

| Asset | Model | Notes |
|---|---|---|
| `hero-garage-portrait-*.{jpg,webp}` | `gpt_image_2_5`, 9:16 | Replaces the previous luxury-garage still. Red Ferrari parked back-right, its reflection running the full length of a mirror-gloss charcoal/silver/bronze flake floor with individual chips readable in the foreground |
| `assets/videos/hero-portrait.mp4` | `seedance_2_5`, 9:16, 720p, 5s, no audio, **3.07 MB** | Regenerated image-to-video from the Ferrari still so poster and first frame match |

**Trademark note for Zach:** the car is a recognisable Ferrari. Using a
recognisable marque in advertising imagery for an unrelated business is a
small but real trademark exposure. It is decorative and makes no endorsement
claim, but it is his call whether to keep it. Swapping the prompt to an
unbadged supercar removes the question entirely.

Unchanged: this is a decorative backdrop. It carries `alt=""`, no project
caption, and `og:image` remains a genuine Floor Candy photograph.

**A trap worth recording.** The video layer sits over the still, so after
regenerating the hero image the page still showed the *old* car — the stale
video was playing on top. Regenerating the still without regenerating the video
will silently show the wrong image. Both must move together.

## Update 21 Nov 2026: homepage photos enhanced with Higgsfield (on Zach's instruction)

Eight genuine job photos shown on the homepage were upscaled to 2K with **Higgsfield → `bytedance_image_upscale`**
(2 credits each). Each result was compared side by side with its source before use: same scene, same objects, no
added or removed features. Fine surface texture (concrete speckle, flake edges) is smoothed or sharpened by the model,
which is invisible at display size. The ba-garage pair was already a Higgsfield 2K upscale (25 Aug) and was not redone.

| Source (pre-upscale copy in `assets/_originals/pre-higgsfield-2026-11-21/`) | Job ID | 2K master (`assets/_originals/higgsfield-2k-2026-11-21/`) |
|---|---|---|
| garage-epoxy-floor-before-1024 | 67191cf8-83d0-4454-8308-312709a89123 | garage-epoxy-floor-before-2k.jpg (2880×2160) |
| garage-epoxy-floor-after-1024 | bc6bcfc2-3804-40e5-9ca7-3af3e376a968 | garage-epoxy-floor-after-2k.jpg (2880×2160) |
| shopfit-tiled-before-1242 | a5ecc68a-c743-4043-9f68-651fdf8e6527 | shopfit-tiled-before-2k.jpg (2976×2160) |
| shopfit-flake-after-1242 | be3faa86-d2c9-4985-bb89-861ed3a3e368 | shopfit-flake-after-2k.jpg (2992×2160) |
| garage-flake-finished-1920 | 231f6b8f-553b-47bd-bd31-b12c68ccb743 | garage-flake-finished-2k.jpg (4800×2160) |
| work-flake-brick-414 | c55103e5-e992-412a-9847-158660201294 | work-flake-brick-2k.jpg (2160×2160) |
| work-flake-garage-414 | 5cc7504d-e214-4f42-9003-6bd0a561d15a | work-flake-garage-2k.jpg (2160×2160) |
| finish-solid-414 | c44d4399-adbc-4fe6-9858-d3670c1d0232 | finish-solid-2k.jpg (2160×2160) |

Web variants were regenerated at the existing sizes; the homepage references them under new `-hd-` names because
`/assets/img/*` is served `immutable` for a year (same-name replacements would never reach returning visitors).
New sizes: `garage-epoxy-floor-{before,after}-hd-1600` and `{work-flake-brick,work-flake-garage,finish-solid}-hd-900`.
