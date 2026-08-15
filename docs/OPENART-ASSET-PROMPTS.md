# Generated Asset Prompts

Production-ready prompts and settings for Floor Candy's generated media.

**What actually happened.** OpenArt was checked first and was authenticated, but on the **Free plan with 40 credits** no video was affordable — Seedance 2.0 image-to-video costs **400 credits** at minimum config and **1200** at the 1080p/6s spec, and the cheapest video of any model was 50. The hero was therefore generated on **Higgsfield (Pro)** with the same underlying model, **Seedance 2.0**, for **54 credits**.

---

## 1. Hero loop — GENERATED ✅

**Status: complete, inspected and deployed** → `assets/videos/hero-loop.mp4`

| Setting | Value |
|---|---|
| Platform | Higgsfield (Pro) |
| Model | `seedance_2_0` |
| Mode | image-to-video (`start_image`) |
| Start image | `assets/images/fc4.jpg` — **genuine Floor Candy flake epoxy garage floor** |
| Duration | 6s (post-processed to a 12.08s palindrome loop) |
| Resolution | 1080p · Mode `std` · Aspect `auto` (preserves source framing) |
| Audio | `generate_audio: false` |
| Cost | 54 credits |
| Job ID | `0ea4d960-8acc-4459-8aee-bde66754ece5` |

**Prompt used, verbatim:**

> Preserve the exact floor finish, geometry, walls, doorway, steps and roller-door opening from the source image without alteration. Add only a slow, controlled low-angle camera push forward with a slight lateral drift. Natural early-morning light moves gently across the surface, revealing the flake texture without changing its colour or pattern. Premium construction photography, realistic exposure, physically accurate reflections, subtle depth of field, calm atmosphere. Maintain generous darker negative space on the left for white website headline text. No people, no tools, no vehicles appearing, no text, no logos, no structural changes, no surface transformation, no excessive shine, no liquid-looking floor, no warped lines, no flicker, no camera shake. Finish on a composition that can transition smoothly back to the opening frame.

**Why `aspect: auto` rather than 16:9.** The source is 2.22:1. Forcing 16:9 would make the model invent floor area to fill the frame — inventing floor is exactly the fabrication this project avoids. `auto` preserved the real framing; the hero crops with CSS `object-fit: cover`.

**Post-processing (reproducible):**

```bash
ffmpeg -i hero-loop-raw.mp4 \
  -filter_complex "[0:v]scale=1920:-2,setsar=1,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]" \
  -map "[v]" -an -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 31 -preset slow \
  -movflags +faststart -r 24 hero-loop.mp4
```

The palindrome matters: Seedance's first and last frames differ (the camera has pushed in), so a hard loop visibly jumps. Playing it forward then reversed makes the loop point invisible and reads as a calm push-and-settle.

**Inspection performed before use:** four frames extracted and reviewed. Floor finish, flake pattern, walls, doorway and steps preserved; no warping, no liquid appearance, no invented objects, no people, no text. Frame 1 matches the source photograph.

**Result:** 12.08s · 1920×824 · 24fps · no audio track · faststart · **2.8 MB** (target was under 3 MB).

### To regenerate or improve it

Same settings. Worth trying if you want a variant:
- `duration: 8` for a slower push (costs more; check with `get_cost` first)
- `bitrate_mode: "high"` if you intend to re-encode harder afterwards
- A different genuine source image as `start_image` — any wide, well-lit finished floor works

---

## 2. Mobile hero loop — DELIBERATELY NOT GENERATED

**Status: not produced, by design.**

The brief allows using the poster on mobile if a good 9:16 crop is not possible. It is not: the genuine source is 2.22:1, and cropping to 9:16 would discard almost all of the floor sweep that makes the shot work, leaving a narrow vertical slice of nothing.

`main.js` therefore serves **poster-only** below 861px, which is also the better performance decision on mobile data. No mobile video is needed or wanted.

If a genuinely vertical source photo is captured on a future job, the prompt would be:

> Preserve the genuine Floor Candy project exactly. Use a restrained forward camera movement focused on the finished surface and lower garage architecture. Maintain a clean darker text-safe area in the upper third. No new objects, people, logos, writing, structural changes or alterations to the floor finish.

Settings: `seedance_2_0`, image-to-video, 9:16, 1080p, 6s, `generate_audio: false`. Target under 1.5 MB after the same palindrome treatment.

---

## 3. Optional atmospheric stills — NOT GENERATED

**Status: not produced. Judged unnecessary rather than blocked.**

The genuine photography covers every slot on the site — hero, preparation proof, garage, driveway, polished concrete. The remaining texture work is handled in CSS, which is lighter and sharper than any image would be. Generating decorative stills would have added page weight for no conversion gain.

If you later want an abstract macro texture for section backgrounds, these are ready to run. **All three are non-representational and must never be captioned as a project:**

**A. Flake macro texture**
> Extreme macro photograph of a decorative flake floor coating surface, grey charcoal and white vinyl flake suspended in a clear satin topcoat, raking low-angle light, shallow depth of field, fine grain, no people, no text, no logos, no horizon, abstract surface study, neutral colour, physically accurate.

**B. Ground concrete surface study**
> Extreme macro photograph of freshly diamond-ground concrete, exposed fine aggregate, matte surface, soft directional light from one side, subtle dust, neutral grey, abstract texture study, no people, no tools, no text, no logos.

**C. Dark atmospheric ground plane (non-project)**
> Abstract low-angle study of a dark satin floor surface receding into shadow, single soft light source raking from the right, generous unlit negative space on the left, no walls, no doors, no identifiable architecture, no people, no vehicles, no text, calm, restrained, physically accurate reflection falloff.

Suggested: Higgsfield `nano_banana_pro` or `gpt_image_2`, 21:9 or 16:9, then convert to AVIF/WebP.

---

## Drop-in locations

| Asset | Path | Wiring |
|---|---|---|
| Desktop hero loop | `assets/videos/hero-loop.mp4` | **Live.** `index.html` `#heroVideo` `data-src` |
| Hero poster | `assets/img/hero-poster-{1920,1440,1080,720}.{avif,webp,jpg}` | **Live.** Regenerate from frame 1 if the clip changes |
| Mobile loop (if ever made) | `assets/videos/hero-loop-mobile.mp4` | Add a `data-src-mobile` branch in `main.js` and lift the 861px cutoff |
| Atmospheric stills | `assets/img/texture-*.{avif,webp}` | Not referenced yet |
