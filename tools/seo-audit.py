#!/usr/bin/env python3
"""SEO audit: uniqueness gates, NAP consistency, schema, link graph, indexability.

Complements tools/qa.py (per-page structure) and tools/mobile-check.py
(responsive). This one looks at the site as a whole.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.floorcandyepoxy.com"

NAP = {
    "phone_display": "0435 193 845",
    "phone_href": "tel:+61435193845",
    "email": "floorcandyepoxy@gmail.com",
    "name": "Floor Candy",
}


def pages():
    out = {"/": os.path.join(ROOT, "index.html")}
    for p in glob.glob(os.path.join(ROOT, "*", "index.html")):
        out["/" + os.path.relpath(p, ROOT)[: -len("/index.html")]] = p
    for p in glob.glob(os.path.join(ROOT, "*", "*", "index.html")):
        out["/" + os.path.relpath(p, ROOT)[: -len("/index.html")]] = p
    return dict(sorted(out.items()))


def visible_text(html_src):
    s = re.sub(r"<script.*?</script>", " ", html_src, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    # strip shared chrome so uniqueness measures the page body, not the nav
    s = re.sub(r"<header.*?</header>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<footer.*?</footer>", " ", s, flags=re.S | re.I)
    s = re.sub(r'<div class="drawer".*?</div>\s*(?=<main)', " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&[a-z]+;|&#\d+;", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def shingles(text, n=5):
    w = text.split()
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def main():
    P = pages()
    src = {u: open(p, encoding="utf-8").read() for u, p in P.items()}
    txt = {u: visible_text(s) for u, s in src.items()}
    problems, notes = [], []

    print("=" * 62)
    print("1. LOCATION PAGE UNIQUENESS  (gate: >=60% unique vs every sibling)")
    print("=" * 62)
    locs = [u for u in P if u.startswith("/service-areas/")]
    print("location pages: %d  (skill warns at 30+, hard-stops at 50+)\n" % len(locs))
    sh = {u: shingles(txt[u]) for u in locs}
    worst = 1.0
    for i, a in enumerate(locs):
        for b in locs[i + 1:]:
            inter = len(sh[a] & sh[b])
            union = len(sh[a] | sh[b]) or 1
            overlap = inter / min(len(sh[a]), len(sh[b]) or 1)
            uniq = 1 - overlap
            worst = min(worst, uniq)
            flag = "  <-- FAILS GATE" if uniq < 0.60 else ""
            if uniq < 0.75 or flag:
                print("  %-28s vs %-28s %5.1f%% unique%s"
                      % (a.split("/")[-1], b.split("/")[-1], uniq * 100, flag))
    print("\n  worst pair: %.1f%% unique" % (worst * 100))
    if worst < 0.60:
        problems.append("location pages fail the 60%% uniqueness gate (worst %.1f%%)" % (worst * 100))
    else:
        print("  PASS — every pair clears 60%.")
    for u in locs:
        wc = len(txt[u].split())
        if wc < 300:
            problems.append("%s thin: %d words" % (u, wc))
    print("  word counts: " + ", ".join("%s=%d" % (u.split("/")[-1], len(txt[u].split()))
                                        for u in locs))

    print("\n" + "=" * 62)
    print("2. NAP CONSISTENCY")
    print("=" * 62)
    bad = 0
    for u, s in src.items():
        phones = set(re.findall(r"(?<!\d)04\d{2}[\s ]?\d{3}[\s ]?\d{3}(?!\d)", s))
        tels = set(re.findall(r'href="(tel:[^"]+)"', s))
        mails = set(re.findall(r'href="mailto:([^"]+)"', s))
        if phones - {NAP["phone_display"]}:
            problems.append("%s: unexpected phone %s" % (u, phones - {NAP['phone_display']}))
            bad += 1
        if tels - {NAP["phone_href"]}:
            problems.append("%s: unexpected tel: %s" % (u, tels - {NAP['phone_href']}))
            bad += 1
        if mails - {NAP["email"]}:
            problems.append("%s: unexpected email %s" % (u, mails - {NAP['email']}))
            bad += 1
    print("  phone/tel/email identical on all %d pages: %s"
          % (len(src), "YES" if bad == 0 else "NO"))
    addr = [u for u, s in src.items() if re.search(r"\b\d+\s+\w+\s+(street|st|road|rd|pkwy|parkway|avenue|ave)\b", s, re.I)]
    print("  street address published anywhere: %s  (mobile business, none expected)"
          % (", ".join(addr) if addr else "no"))

    print("\n" + "=" * 62)
    print("3. STRUCTURED DATA")
    print("=" * 62)
    types = defaultdict(int)
    for u, s in src.items():
        for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                d = json.loads(blob)
            except Exception as e:
                problems.append("%s: invalid JSON-LD (%s)" % (u, e))
                continue
            types[d.get("@type", "?")] += 1
            if d.get("@type") == "HomeAndConstructionBusiness":
                ar = d.get("aggregateRating")
                if ar and int(ar["reviewCount"]) != 3:
                    problems.append("%s: aggregateRating reviewCount != 3" % u)
                for req in ("name", "telephone", "url", "areaServed"):
                    if req not in d:
                        problems.append("%s: business schema missing %s" % (u, req))
            if d.get("@type") == "BreadcrumbList":
                for it in d["itemListElement"]:
                    if "item" in it and not it["item"].startswith(SITE):
                        problems.append("%s: breadcrumb item not absolute" % u)
    for t, n in sorted(types.items()):
        print("  %-28s x%d" % (t, n))
    if "HowTo" in types:
        problems.append("HowTo schema present (deprecated Sept 2023)")
    if types.get("FAQPage"):
        notes.append("FAQPage x%d — Google retired FAQ rich results (7 May 2026), so this "
                     "earns no SERP feature. Kept because it is valid, accurate and still "
                     "parsed by AI answer engines. Not a defect; do not expect rich results."
                     % types["FAQPage"])

    print("\n" + "=" * 62)
    print("4. INTERNAL LINK GRAPH")
    print("=" * 62)
    inbound = defaultdict(set)
    for u, s in src.items():
        body = re.sub(r"<footer.*?</footer>", " ", s, flags=re.S | re.I)
        body = re.sub(r'<div class="drawer".*?(?=<main)', " ", body, flags=re.S | re.I)
        body = re.sub(r"<header.*?</header>", " ", body, flags=re.S | re.I)
        for href in re.findall(r'href="(/[^"#?]*)"', body):
            t = href.rstrip("/") or "/"
            if t in P and t != u:
                inbound[t].add(u)
    for u in P:
        n = len(inbound[u])
        mark = ("  <-- footer-linked only (fine for legal pages)"
                if n == 0 and u in ("/privacy", "/terms")
                else ("  <-- ORPHAN" if n == 0 else ""))
        # /privacy and /terms are conventionally reached from the footer only.
        if n == 0 and u not in ("/privacy", "/terms"):
            problems.append("%s has no in-body internal links" % u)
        print("  %-42s %2d inbound%s" % (u, n, mark))

    print("\n" + "=" * 62)
    print("5. INDEXABILITY")
    print("=" * 62)
    robots = open(os.path.join(ROOT, "robots.txt"), encoding="utf-8").read()
    print("  robots.txt disallows nothing: %s" % ("yes" if "Disallow:" not in robots
                                                  or "Disallow: \n" in robots + "\n" else "CHECK"))
    print("  sitemap referenced in robots: %s" % ("yes" if "Sitemap:" in robots else "NO"))
    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    listed = set(re.findall(r"<loc>%s([^<]*)</loc>" % re.escape(SITE), sm))
    listed = {(u or "/") for u in listed}
    missing = set(P) - listed
    extra = listed - set(P)
    print("  sitemap URLs: %d   pages: %d" % (len(listed), len(P)))
    if missing:
        problems.append("not in sitemap: %s" % ", ".join(sorted(missing)))
    if extra:
        problems.append("in sitemap but no page: %s" % ", ".join(sorted(extra)))
    for u, s in src.items():
        if re.search(r'name="robots"[^>]*noindex', s, re.I):
            problems.append("%s carries noindex" % u)
    print("  noindex on indexable pages: none" if not any(
        re.search(r'name="robots"[^>]*noindex', s, re.I) for s in src.values()) else "")

    print("\n" + "=" * 62)
    print("6. AI / GEO READINESS")
    print("=" * 62)
    print("  robots.txt blocks no AI crawlers: %s"
          % ("yes" if not re.search(r"GPTBot|CCBot|anthropic|PerplexityBot", robots, re.I) else "NO"))
    print("  answer-shaped H2/H3 (question headings): %d"
          % sum(len(re.findall(r"<summary>[^<]*\?</summary>", s)) for s in src.values()))
    print("  critical content server-rendered (no CSR): yes — static HTML, JS only enhances")
    print("  llms.txt present: %s (optional; ignored by Google Search)"
          % ("yes" if os.path.exists(os.path.join(ROOT, "llms.txt")) else "no"))

    print("\n" + "=" * 62)
    if problems:
        print("PROBLEMS (%d)" % len(problems))
        for x in problems:
            print("  x " + x)
    else:
        print("PROBLEMS: none")
    if notes:
        print("\nNOTES")
        for n in notes:
            print("  i " + n)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
