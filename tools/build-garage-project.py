#!/usr/bin/env python3
"""Derive the Garage Epoxy Flooring Transformation image set.

Source: two client-supplied photographs of the SAME garage (matched on the
window, both internal doors, the twin fluorescent tubes and the red opener
pull-cord). Both originals are 1024x768. They are emitted at full frame — no
selective cropping — so the comparison shows identical framing treatment on
both sides. The slider renders them at 4:3 to match.
"""
from PIL import Image
from pathlib import Path

DL = Path("/Users/zachriley1206/Downloads")
OUT = Path(__file__).resolve().parent.parent / "assets" / "img"

PAIR = {
    "garage-epoxy-floor-before": "att.SR6KRH_xrYkNSATTp5SPqAZLNCr9MnLNhZhdwT_ldJw.dat.png",
    "garage-epoxy-floor-after":  "att.ZHD1g7vqBvOcw4ZGFeT7tYM_fYZODmd2Wnjk-zC_qcQ.dat.png",
}
WIDTHS = [1024, 800, 600, 400]


def emit(im, stem, widths, quality=(80, 84, 55)):
    jq, wq, aq = quality
    for w in widths:
        if w >= im.width:
            r, w = im, im.width
        else:
            r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(OUT / f"{stem}-{w}.jpg", quality=jq, optimize=True, progressive=True)
        r.save(OUT / f"{stem}-{w}.webp", quality=wq, method=6)
        try:
            r.save(OUT / f"{stem}-{w}.avif", quality=aq)
        except Exception as e:
            print("  avif skipped", stem, w, e)
        print(f"  {stem}-{w}  {r.size}")


def main():
    for stem, src in PAIR.items():
        p = DL / src
        if not p.exists():
            raise SystemExit(f"missing source: {p}")
        im = Image.open(p).convert("RGB")
        print(f"{stem} from {src} {im.size}")
        emit(im, stem, WIDTHS)


if __name__ == "__main__":
    main()
