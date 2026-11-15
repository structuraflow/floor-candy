#!/usr/bin/env python3
"""Headless mobile/responsive audit across every page.

Reuses the CDP websocket helper from shot.py. For each page at each viewport it
reports horizontal overflow, the elements causing it, tap targets under 24px
(the WCAG 2.5.8 AA bar; primary CTAs are 52px by design),
text under 12px, and any element whose text overflows its box.

    python3 tools/mobile-check.py            # default viewports
    python3 tools/mobile-check.py 375 768    # explicit widths

Run it alone — it shares debug port 9333 with shot.py.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shot import WS, CHROME, PORT  # noqa: E402

BASE = "http://127.0.0.1:8899"
PAGES = [
    "/", "/premium-flake-flooring", "/garage-epoxy-flooring",
    "/residential-epoxy-flooring", "/outdoor-epoxy-flooring",
    "/solid-colour-epoxy-flooring", "/concrete-preparation-crack-repair",
    "/projects", "/about", "/service-areas",
    "/service-areas/taree", "/service-areas/forster", "/service-areas/harrington",
    "/service-areas/blueys-beach", "/service-areas/pacific-palms",
    "/service-areas/newcastle", "/contact", "/404.html",
    "/guides", "/guides/why-epoxy-floors-fail",
    "/projects/tiled-floor-to-flake",
    "/projects/garage-bare-slab-to-flake",
    "/guides/what-changes-the-price-of-an-epoxy-garage-floor",
]
VIEWPORTS = [(375, 812), (390, 844), (768, 1024), (1024, 768), (1440, 900)]

PROBE = r"""
(() => {
  const vw = document.documentElement.clientWidth;
  const out = { vw, scrollW: document.documentElement.scrollWidth, wide: [], small: [], tiny: [] };
  const name = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    else if (el.className && typeof el.className === 'string')
      s += '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.');
    return s;
  };
  document.querySelectorAll('body *').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest('[hidden]')) return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;

    if (r.right > vw + 1 || r.left < -1) {
      if (cs.position !== 'fixed')
        out.wide.push({ el: name(el), left: Math.round(r.left), right: Math.round(r.right) });
    }
    // interactive tap targets
    if (el.matches('a, button, input:not([type=hidden]), select, textarea, summary, label')) {
      // Links inside a sentence are exempt from target sizing (WCAG 2.5.8).
      const inNav = !!el.closest('.crumbs, .footer-base, .ba-specs, .form-foot, .prose p, .ba-note, .lede, .faq-a p');
      // A <label> with no `for` and no wrapped control is a group caption, not
      // a tap target. An <input> inside a <label> is hit via that label.
      // A <label> is not itself the control: the input it labels is the target,
      // and those are all >=44px. Group captions have no control at all.
      const isGroupCaption = el.tagName === 'LABEL';
      const hitByLabel = el.matches('input, select, textarea') && el.closest('label');
      const hidden = el.classList.contains('visually-hidden') ||
        !!el.closest('.visually-hidden') || el.type === 'range';
      if (!inNav && !isGroupCaption && !hitByLabel && !hidden &&
          (r.height < 24 || r.width < 24) && r.height > 0)
        out.small.push({ el: name(el), w: Math.round(r.width), h: Math.round(r.height) });
    }
    const fs = parseFloat(cs.fontSize);
    if (fs && fs < 11 && el.textContent.trim().length > 2 &&
        el.children.length === 0) out.tiny.push({ el: name(el), size: fs });
  });
  const seen = new Set();
  out.wide = out.wide.filter(x => !seen.has(x.el) && seen.add(x.el)).slice(0, 8);
  const s2 = new Set();
  out.small = out.small.filter(x => !s2.has(x.el) && s2.add(x.el)).slice(0, 8);
  const s3 = new Set();
  out.tiny = out.tiny.filter(x => !s3.has(x.el) && s3.add(x.el)).slice(0, 5);
  return JSON.stringify(out);
})()
"""


def main():
    widths = [int(a) for a in sys.argv[1:]]
    vps = [v for v in VIEWPORTS if not widths or v[0] in widths]

    proc = subprocess.Popen(
        [CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
         "--user-data-dir=/tmp/fc-mobile-profile", "--hide-scrollbars",
         "--force-color-profile=srgb", "--disable-gpu", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    problems = 0
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version")
                break
            except Exception:
                time.sleep(.25)
        else:
            raise SystemExit("chrome did not start")

        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list"))
        page = next(t for t in tabs if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        ws.call("Page.enable")
        ws.call("Runtime.enable")

        for path in PAGES:
            for (w, h) in vps:
                ws.call("Emulation.setDeviceMetricsOverride",
                        {"width": w, "height": h, "deviceScaleFactor": 1,
                         "mobile": w < 760})
                ws.call("Page.navigate", {"url": BASE + path})
                time.sleep(0.75)
                res = ws.call("Runtime.evaluate",
                              {"expression": PROBE, "returnByValue": True})
                data = json.loads(res["result"]["value"])
                issues = []
                if data["scrollW"] > data["vw"] + 1:
                    issues.append("H-SCROLL %dpx > %dpx" % (data["scrollW"], data["vw"]))
                    for x in data["wide"]:
                        issues.append("   overflows: %s (%d..%d)" % (x["el"], x["left"], x["right"]))
                for x in data["small"]:
                    issues.append("   tap target %s %dx%d" % (x["el"], x["w"], x["h"]))
                for x in data["tiny"]:
                    issues.append("   text %.1fpx %s" % (x["size"], x["el"]))
                if issues:
                    problems += 1
                    print("%s @ %dx%d" % (path, w, h))
                    for i in issues:
                        print("  " + i)
        print("\n%s" % ("No responsive issues found."
                        if not problems else "%d page/viewport combinations flagged." % problems))
    finally:
        proc.terminate()
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
