#!/usr/bin/env python3
"""Derive responsive variants for new job photographs.

Replaces the PIL pipeline in build-images.py, which cannot run here (system
Python is 3.9 with no Pillow). Resizing and encoding happen in headless Chrome's
canvas, which gives JPEG and WebP without installing anything. AVIF is not
available from canvas, so this set ships JPEG + WebP only.

Sources live outside the repo. Provenance for every file is recorded in
docs/ASSET-PROVENANCE.md before it is used.

    python3 tools/add-photos.py
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shot import WS, CHROME, PORT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.expanduser("~/Downloads/floor candy")

# name -> (source file, target aspect or None to keep, widths)
JOBS = {
    # One commercial fit-out, photographed through the job. Same room in all four.
    "shopfit-tiled-before":  ("BA291B76-4118-4B79-8DC3-9A4375507926.jpeg", 1.385,
                              [414, 600, 900, 1242]),
    "shopfit-flake-after":   ("B762C6AC-F0AF-4B62-96ED-1938AC078E17.jpeg", 1.385,
                              [414, 600, 900, 1242]),
    "shopfit-prepped":       ("BB6CE6D1-88F8-41FC-A221-6D7C19EC71C4.jpeg", 1.385,
                              [414, 600, 900, 1242]),
    "shopfit-substrate":     ("0A07FEA9-8491-4CA8-A69D-E6DBE83E7164.jpeg", None,
                              [414, 600, 900]),
    "shopfit-masked":        ("2AB9CA11-57D5-44DE-8CFF-678AAB1EF80E.jpeg", None,
                              [414, 600, 900]),
    "shopfit-frontage":      ("F9A175FE-6EB2-4E91-917B-A1D5AE637BC3.jpeg", None,
                              [414, 600, 900]),
}


def main():
    missing = [f for _, (f, _, _) in JOBS.items() if not os.path.exists(os.path.join(SRC, f))]
    if missing:
        raise SystemExit("missing sources:\n  " + "\n  ".join(missing))

    payload = {}
    for name, (fname, aspect, widths) in JOBS.items():
        with open(os.path.join(SRC, fname), "rb") as fh:
            payload[name] = {
                "b64": base64.b64encode(fh.read()).decode(),
                "aspect": aspect,
                "widths": widths,
            }

    html = "<body style='margin:0'></body>"
    open("/tmp/photos.html", "w").write(html)

    proc = subprocess.Popen(
        [CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
         "--user-data-dir=/tmp/fc-photos", "--disable-gpu", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version")
                break
            except Exception:
                time.sleep(.25)
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list"))
        ws = WS(next(t for t in tabs if t["type"] == "page")["webSocketDebuggerUrl"])
        ws.call("Page.enable")
        ws.call("Runtime.enable")
        ws.call("Page.navigate", {"url": "file:///tmp/photos.html"})
        time.sleep(0.8)

        out_dir = os.path.join(ROOT, "assets", "img")
        total = 0
        for name, spec in payload.items():
            expr = """
            (async () => {
              const spec = %s;
              const img = new Image();
              img.src = 'data:image/jpeg;base64,' + spec.b64;
              await img.decode();
              let sx=0, sy=0, sw=img.naturalWidth, sh=img.naturalHeight;
              if (spec.aspect) {           // centre-crop to a shared aspect
                const cur = sw/sh;
                if (cur > spec.aspect) { const nw = Math.round(sh*spec.aspect); sx = Math.round((sw-nw)/2); sw = nw; }
                else { const nh = Math.round(sw/spec.aspect); sy = Math.round((sh-nh)/2); sh = nh; }
              }
              const out = {};
              for (const w of spec.widths) {
                const c = document.createElement('canvas');
                c.width = w; c.height = Math.round(sh * (w/sw));
                const ctx = c.getContext('2d');
                ctx.imageSmoothingQuality = 'high';
                ctx.drawImage(img, sx, sy, sw, sh, 0, 0, c.width, c.height);
                out[w] = { jpg: c.toDataURL('image/jpeg', 0.82),
                           webp: c.toDataURL('image/webp', 0.80),
                           h: c.height };
              }
              return JSON.stringify(out);
            })()
            """ % json.dumps(spec)
            r = ws.call("Runtime.evaluate",
                        {"expression": expr, "awaitPromise": True, "returnByValue": True})
            data = json.loads(r["result"]["value"])
            for w, v in sorted(data.items(), key=lambda kv: int(kv[0])):
                for ext in ("jpg", "webp"):
                    raw = base64.b64decode(v[ext].split(",", 1)[1])
                    path = os.path.join(out_dir, f"{name}-{w}.{ext}")
                    open(path, "wb").write(raw)
                    total += len(raw)
            first = sorted(data.items(), key=lambda kv: int(kv[0]))[-1]
            print("  %-24s %s widths, largest %sx%s" %
                  (name, len(data), first[0], first[1]["h"]))
        print("\n  %d files, %.1f KB total" % (
            sum(len(v["widths"]) * 2 for v in payload.values()), total / 1024))
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
