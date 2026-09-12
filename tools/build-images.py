#!/usr/bin/env python3
"""Derive the site's responsive image set from the original captures.

Sources live outside the repo (Downloads); the outputs in assets/img are what
ships. Re-run after adding a new original. Provenance for every source file is
recorded in docs/ASSET-PROVENANCE.md.
"""
from PIL import Image
from pathlib import Path

SRC = Path("/Users/zachriley1206/Downloads/floor candy")
HF = Path("/Users/zachriley1206/Downloads/hf_20260815_085454_fa1de56c-6133-4b4f-9d44-3677af6866dc.png")
OUT = Path(__file__).resolve().parent.parent / "assets" / "img"

# Genuine Floor Candy captures. The two before/after pairs were confirmed as the
# same property by matching fixed features (rock retaining wall on the driveway;
# ceiling truss rack and louvre door in the garage).
JOBS = {
    "ba-drive-before":   "758730892_122137168059197682_4444640278416839127_n.jpg",
    "ba-drive-after":    "758543278_122137168143197682_4627813577670998218_n.jpg",
    "ba-garage-before":  "766748054_122138262423197682_776134694277648459_n.jpg",
    "ba-garage-after":   "764850005_122138262471197682_5997885061591671474_n.jpg",
    "work-flake-garage": "766797908_122138397675197682_9054427849340171851_n.jpg",
    "work-drive-dark":   "758216980_122137168101197682_6394352264705105128_n.jpg",
    "work-flake-cream":  "749329984_122135617971197682_4470955539274186871_n.jpg",
    "work-alfresco":     "774575417_122139640395197682_8344087232596062597_n.jpg",
    "work-flake-tan":    "774173037_122139640737197682_8246132017377654636_n.jpg",
    "work-flake-brick":  "770919249_122139640521197682_4231726085946889890_n.jpg",
    "work-path-light":   "621809877_122109580401197682_2551109649450473223_n.jpg",
    "work-drive-blue":   "619669544_122109580473197682_5767530575579350438_n.jpg",
    # Solid-colour (non-flake) coating on an alfresco slab. Masking tape is
    # still down at the edges, and the caption says so.
    "finish-solid":      "774178748_122139640437197682_1213576438287910503_n.jpg",
}
PREP_HI = "774512745_122139640347197682_8579019277707021752_n.jpg"


def emit(im, stem, widths, quality=(78, 82, 52)):
    jq, wq, aq = quality
    made = []
    for w in widths:
        if w > im.width:
            r = im
            w = im.width
        else:
            r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(OUT / f"{stem}-{w}.jpg", quality=jq, optimize=True, progressive=True)
        r.save(OUT / f"{stem}-{w}.webp", quality=wq, method=6)
        try:
            r.save(OUT / f"{stem}-{w}.avif", quality=aq)
        except Exception as e:
            print("  avif skipped", stem, w, e)
        made.append(w)
    return made


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # Hero. AI-generated atmosphere, never captioned as Floor Candy's own work.
    hero = Image.open(HF).convert("RGB")
    emit(hero, "hero-garage", [720, 1080, 1376, 1920], quality=(76, 80, 48))
    print("hero-garage from", HF.name, hero.size)

    # Job photographs. Sources are 414px social exports, so they are emitted at
    # native size only -- upscaling would just add weight and softness.
    for stem, fn in JOBS.items():
        p = SRC / fn
        if not p.exists():
            print("  MISSING", fn)
            continue
        im = Image.open(p).convert("RGB")
        emit(im, stem, [im.width])
        print(f"{stem:20s} {im.size} <- {fn[:16]}")

    # The one full-resolution capture: grinding a driveway, dust extractor hose
    # in frame. Cropped to a workable landscape band from the 3:4 original.
    hi = Image.open(SRC / PREP_HI).convert("RGB")
    w, h = hi.size
    band = hi.crop((0, int(h * 0.28), w, int(h * 0.90)))
    emit(band, "prep-grind", [600, 900, 1200])
    print("prep-grind", band.size, "<-", PREP_HI[:16])

    # Open Graph card, 1200x630, from the hero.
    og = hero.resize((1200, round(hero.height * 1200 / hero.width)), Image.LANCZOS)
    top = max(0, (og.height - 630) // 2)
    og.crop((0, top, 1200, top + 630)).save(
        OUT / "og-floor-candy.jpg", quality=84, optimize=True)
    print("og-floor-candy.jpg 1200x630")


if __name__ == "__main__":
    main()
