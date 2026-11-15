#!/usr/bin/env python3
"""Structural QA for the generated site. Run from the repo root after build-site.py.

Checks, per page: one H1, unique title/description within bounds, canonical,
OG tags, heading order, image alt text, valid JSON-LD, resolvable internal
links, and the absence of placeholder or unverified-claim text.
"""
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Strings that must never reach production.
FORBIDDEN = [
    r"\bTBC\b", r"\bXX\s*m", r"LOCATION TBD", r"\blorem ipsum\b",
    r"\[Business Name\]", r"\[City\]", r"REPLACE_", r"\bTODO\b",
    r"Project Name", r"\bplaceholder\b",
]
# Claims we have no evidence for. Guard against regressions.
UNVERIFIED = [
    r"\bABN\s*\d", r"licence\s*(?:no\.?|number)?\s*[:#]?\s*\d",
    r"\b\d+\s*[- ]year\s+warranty\b", r"\bfully insured\b",
    r"\b\d+\s*\+?\s*years?\s+(?:of\s+)?experience\b",
    r"\b\d{2,}\s*\+?\s*(?:projects|floors|jobs)\s+(?:completed|installed)",
    r"\bno subcontractors\b", r"\bCSP\s*\d", r"\bdiamond[- ]ground\b",
    r"\b\d+\s*year\s+guarantee\b", r"\baward[- ]winning\b",
    r"\b(?:master builders|sika|haccp)\b",
]
BANNED_COPY = [
    r"transform your space", r"elevate your space", r"experience the difference",
    r"unparalleled quality", r"premium solutions", r"your trusted partner",
    r"where craftsmanship meets innovation",
]


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h = []          # (level, text)
        self.imgs = []       # (alt_present, alt_text, has_dims)
        self.links = []
        self.title = None
        self.meta = {}
        self.canonical = None
        self.ld = []
        self._grab = None
        self._buf = []
        self._in_ld = False
        self.inputs_without_label = 0
        self.labels_for = set()
        self.field_ids = set()
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._grab = int(tag[1]); self._buf = []
        elif tag == "title":
            self._grab = "title"; self._buf = []
        elif tag == "img":
            self.imgs.append(("alt" in a, a.get("alt", ""),
                              bool(a.get("width") and a.get("height"))))
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "meta":
            if a.get("name"):
                self.meta[a["name"]] = a.get("content", "")
            if a.get("property"):
                self.meta[a["property"]] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True; self._buf = []
        elif tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        elif tag in ("input", "select", "textarea"):
            t = a.get("type", "text")
            if t not in ("hidden", "submit", "button", "radio", "range") and a.get("id"):
                self.field_ids.add(a["id"])

    def handle_data(self, d):
        if self._grab is not None or self._in_ld:
            self._buf.append(d)

    def handle_endtag(self, tag):
        if self._in_ld and tag == "script":
            self.ld.append("".join(self._buf)); self._in_ld = False; self._buf = []
        elif self._grab == "title" and tag == "title":
            self.title = "".join(self._buf).strip(); self._grab = None
        elif isinstance(self._grab, int) and tag == "h%d" % self._grab:
            self.h.append((self._grab, "".join(self._buf).strip())); self._grab = None


def page_paths():
    out = [os.path.join(ROOT, "index.html"), os.path.join(ROOT, "404.html")]
    out += sorted(glob.glob(os.path.join(ROOT, "*", "index.html")))
    out += sorted(glob.glob(os.path.join(ROOT, "*", "*", "index.html")))
    return [p for p in out if os.path.exists(p) and "/assets/" not in p
            and "/tools/" not in p and "/docs/" not in p and "/node_modules/" not in p]


def url_of(path):
    rel = os.path.relpath(path, ROOT)
    if rel == "index.html":
        return "/"
    if rel == "404.html":
        return "/404"
    return "/" + rel[: -len("/index.html")]


def main():
    paths = page_paths()
    problems, warnings = [], []
    titles, descs = {}, {}
    known = {url_of(p) for p in paths} | {"/404"}

    for p in paths:
        u = url_of(p)
        raw = open(p, encoding="utf-8").read()
        d = Doc(); d.feed(raw)
        tag = lambda m: problems.append("%s: %s" % (u, m))
        warn = lambda m: warnings.append("%s: %s" % (u, m))

        if d.lang != "en-AU":
            tag("html lang is %r, expected en-AU" % d.lang)

        h1s = [t for lvl, t in d.h if lvl == 1]
        if len(h1s) != 1:
            tag("%d H1s (expected exactly 1)" % len(h1s))

        if not d.title:
            tag("missing <title>")
        else:
            if not (15 <= len(d.title) <= 65):
                warn("title %d chars: %r" % (len(d.title), d.title))
            titles.setdefault(d.title, []).append(u)

        desc = d.meta.get("description", "")
        if not desc:
            tag("missing meta description")
        else:
            if not (70 <= len(desc) <= 175):
                warn("meta description %d chars" % len(desc))
            descs.setdefault(desc, []).append(u)

        if not d.canonical:
            tag("missing canonical")
        elif u == "/404":
            pass
        elif not d.canonical.endswith(u if u != "/" else "/"):
            tag("canonical %r does not match %r" % (d.canonical, u))

        for og in ("og:title", "og:description", "og:image", "og:url", "og:type"):
            if u != "/404" and og not in d.meta:
                tag("missing %s" % og)

        # heading order
        lvls = [lvl for lvl, _ in d.h]
        for a, b in zip(lvls, lvls[1:]):
            if b > a + 1:
                warn("heading jumps h%d -> h%d" % (a, b))
                break

        for has_alt, alt, dims in d.imgs:
            if not has_alt:
                tag("img without alt attribute")
            if not dims:
                warn("img without width/height (CLS risk)")

        for blob in d.ld:
            try:
                json.loads(blob)
            except Exception as e:
                tag("invalid JSON-LD: %s" % e)

        for f in d.field_ids:
            if f not in d.labels_for:
                tag("form field #%s has no <label for>" % f)

        text = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        for pat in FORBIDDEN:
            if re.search(pat, text, re.I):
                tag("forbidden placeholder text matches /%s/" % pat)
        for pat in UNVERIFIED:
            m = re.search(pat, text, re.I)
            if m:
                tag("UNVERIFIED CLAIM %r matches /%s/" % (m.group(0), pat))
        for pat in BANNED_COPY:
            if re.search(pat, text, re.I):
                tag("banned filler phrase /%s/" % pat)

        for href in d.links:
            if href.startswith(("http", "tel:", "sms:", "mailto:", "#")):
                continue
            base = href.split("#")[0].split("?")[0].rstrip("/") or "/"
            if base not in known:
                tag("broken internal link -> %s" % href)

    for t, us in titles.items():
        if len(us) > 1:
            problems.append("duplicate <title> %r on %s" % (t, ", ".join(us)))
    for dsc, us in descs.items():
        if len(us) > 1:
            problems.append("duplicate meta description on %s" % ", ".join(us))

    print("Checked %d pages\n" % len(paths))
    if problems:
        print("PROBLEMS (%d)" % len(problems))
        for p in problems:
            print("  x " + p)
    else:
        print("PROBLEMS: none")
    if warnings:
        print("\nWARNINGS (%d)" % len(warnings))
        for w in warnings[:40]:
            print("  ! " + w)
        if len(warnings) > 40:
            print("  … %d more" % (len(warnings) - 40))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
