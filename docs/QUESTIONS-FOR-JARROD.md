# Questions for Jarrod

Nothing in this list has been guessed at or filled in on the site. Every item
below is either **missing** from the live site or **marked TODO** in the source.
Answers unlock the items listed under each heading.

Last updated: 21 September 2026.

---

## 1. Business details still missing from the site

These are the fields a local-SEO setup normally wants. None have been invented.

| # | Question | What it unlocks |
|---|---|---|
| 1.1 | Is there a **public business address** customers may visit, or is Floor Candy entirely mobile? | `address` in LocalBusiness schema; whether the map keeps its current framing. The site currently states there is **no public showroom**. |
| 1.2 | The Google Business Profile pin sits on a **residential street (Hilltop Pkwy, Tallwoods Village)**. Is Jarrod comfortable with the supplied map embed centring there? | Whether the homepage/service-areas map stays as supplied, is swapped for a service-area map, or is removed. **See the warning in §4.** |
| 1.3 | Is `admin@floorcandyepoxy.com` the correct **public** enquiry address? | It is already published on the site and in schema — confirm it is monitored. |
| 1.4 | Are the opening hours **Mon–Fri 7am–7pm** still accurate? Any Saturday work? | `openingHoursSpecification`; the "Mon–Fri, 7am–7pm" line repeated across every page. |
| 1.5 | **ABN**? | Footer legal line; trust signal; some directory listings require it. |
| 1.6 | Public **Google Business Profile short link** (the `g.page/...` or `maps.app.goo.gl/...` one)? | Replaces the CID-derived Maps link currently used; a "leave us a review" link. |
| 1.7 | **Social profiles** — Facebook, Instagram, anything else? | `sameAs` in schema; footer links. None are currently claimed. |
| 1.8 | Any **licences, accreditations, insurance or manufacturer training** worth naming? | A credentials block. Nothing is claimed today. |

## 2. Services — what is actually offered

The site currently commits to garage floors, driveways/exterior concrete, and
concrete preparation. These need confirming before any new service page is built.

| # | Question | What it unlocks |
|---|---|---|
| 2.1 | Is **metallic epoxy** offered? Have you installed one? | The Metallic Epoxy Flooring page and project. **No metallic page will be built until there are genuine metallic photographs** — the grey flake garage will not be relabelled. |
| 2.2 | Is **polished concrete** still offered? (It is in the reviews and old copy but not in the current service list.) | Whether it returns as a service page. |
| 2.3 | Is **natural stone polishing** still offered? A Google review specifically praises it. | It was removed from the footer service list in this pass — put back only if confirmed. |
| 2.4 | Do you do **concrete sealing** as a standalone job, separate from coating? | A Concrete Sealing page, or a section on the driveways page. |
| 2.5 | Do you take **commercial / industrial** work, or residential only? | Whether commercial keywords are worth targeting at all. |
| 2.6 | **Residential interior** floors — living areas, not just garages? | A Residential Epoxy Flooring page. |
| 2.7 | Do you remove **failed DIY or existing coatings** as a standalone job? | High-intent page: "epoxy floor repair / removal". |

## 3. Process and product specifics (needed before any guide is published)

The guides in `CONTENT-BRIEFS.md` cannot be written honestly without these.

| # | Question |
|---|---|
| 3.1 | What **grinder and extraction** do you run? (A Hilti VC 40-U is visible in one job photo — is that current?) |
| 3.2 | What **coating systems** do you use — brand and product family — and do you vary them by job? |
| 3.3 | How do you **test for moisture** in a slab, and what do you do when you find it? |
| 3.4 | What are your actual **cure and return-to-service times** — foot traffic, then vehicles? |
| 3.5 | What is the typical **job duration** for a standard double garage, start to handover? |
| 3.6 | How do you handle **cracks** — what gets repaired, what gets disclosed as permanent? |
| 3.7 | What **flake and colour options** are available, and how do customers choose? |
| 3.8 | Do you offer a **warranty**? If so, what does it cover, for how long, in writing? *(Nothing is claimed on the site today.)* |
| 3.9 | Is there a **minimum job size** or minimum charge? |
| 3.10 | What is the **deposit** arrangement, and what triggers the final balance? |
| 3.11 | What actually happens during a **floor assessment**, step by step, and how long does it take? |
| 3.12 | **Polyaspartic** — do you use it, and what would you tell a customer who asks about it versus epoxy? |
| 3.13 | What are the two or three **most common reasons** you have to turn a job down or re-do someone else's? |

## 4. ⚠️ Decisions that need a human call

**4.1 — The map centres on a residential street.**
The supplied embed is the verified Floor Candy Google listing, and it has been
implemented exactly as instructed. Rendered, it centres on Hilltop Pkwy,
Tallwoods Village. No address is stated anywhere in the copy or in the
structured data, and the page explicitly says Floor Candy is mobile with no
public showroom — but the map itself points at a house. **Jarrod should decide
whether he is comfortable with that being on the homepage.** Options: keep it,
zoom it out to a regional view, or remove the embed and keep the text-based
service-area lists.

**4.2 — WhatsApp on mobile.**
The sticky mobile bar was reduced to the two actions specified in the brief
(Call Jarrod · Free assessment). WhatsApp is still reachable on mobile from the
menu drawer and the footer, but it is no longer a permanent third button. If
WhatsApp is a meaningful lead source, say so and it can come back as an
icon-only third slot.

**4.3 — Pathway photographs.**
Still waiting on the improved images. The existing pathway photo remains live
until they arrive.

**4.4 — Prices.**
Still nothing published, deliberately. The cost guide in `CONTENT-BRIEFS.md`
cannot be written as a price guide without real figures, and will not be
published with invented ones.

**4.5 — The four finishes on the new homepage. RESOLVED, no longer blocking.**
The first draft of this section carried *metallic marble* and *commercial
non-slip* — both taken from the design brief rather than from anything Floor
Candy has shown. Reviewing all 34 genuine job photographs in the source folder
settles it:

* **Flake** — many photographs, grey, cream and tan blends. Evidenced.
* **Sealed exterior** — many photographs, driveways and paths. Evidenced.
* **Polished concrete look** — `fc1.jpg`, a genuine finished interior.
  Evidenced.
* **Solid colour** — the alfresco slab, masking still down. Evidenced.
* **Metallic marble** — *no Floor Candy photograph exists.*
* **Commercial non-slip** — *no Floor Candy photograph exists.* The only
  commercial epoxy images in the folder are stock, and they are already in
  `assets/_quarantine`.

So the page now shows the four finishes above, each with a real Floor Candy
photograph and no drawn specimens anywhere. Nothing is claimed that the work
does not already demonstrate, and nothing is blocking deployment.

Questions 2.1 and 2.5 still stand as *business* questions — if Jarrod does
offer metallic or commercial work, those tabs can be added the moment there are
photographs of a finished job. Until then the page does not raise them.

**4.6 — The hero image is still the Higgsfield still.**
Unchanged by the redesign, and still running without a disclosure label, per
Jarrod's and Zach's earlier decision. The new hero shows more of it than the old
one did, because the scrim is lighter. Recorded in `ASSET-PROVENANCE.md`.


---

## 5. Blocking the production rebuild (21 September 2026)

The site was rebuilt for production on 21 September 2026. These are the items
that are **built but empty** — the components exist and will render the moment
a value is supplied, and render nothing until then.

### 5.1 Credentials — the biggest competitive gap

`tools/build-site.py` has a `CREDENTIALS` dict. Every key is `None`, so nothing
renders in the trust strip, the footer or the schema. Competitors publish all of
this (see `COMPETITIVE-BLUEPRINT.md`).

| Field | Needed for |
|---|---|
| `abn` | Footer legal line, `identifier` in LocalBusiness schema |
| `licence_number` | Footer, credibility against competitors who publish theirs |
| `public_liability` | Trust strip — Ironclad publishes "$20 million public liability" |
| `insurer` | Supporting detail |
| `warranty` | The single largest gap. Competitors advertise 5 and 10 year warranties. We claim none, correctly, because there are no written terms |
| `years_operating` | Trust strip |
| `accreditations` | `hasCredential` in schema |

**Fill the dict, rebuild, done.** No template work required.

### 5.2 Per-square-metre pricing

`PRICING["per_sqm_from"]` is `None` and no per-m² figure appears anywhere. Two
of the strongest competitors publish one ($50–120/m² and $90–100/m²) and both
rank top three in their own area. The confirmed `$2,450*` double-garage
starting price **is** published, with the qualifier, sitewide.

### 5.3 Project suburbs and specifications

`BA[...]["specs"]` carries `Suburb`, `Floor size`, `System` and
`Existing condition` keys set to `None`. Any spec with a value renders; any spec
without one is omitted from the caption entirely. Nothing reads "TBC" or "XXm²"
because the renderer cannot emit a key with no value.

`/projects` explains in plain English why no suburbs appear. Individual project
pages (`/projects/<slug>/`) are **not** generated — the brief said not to create
empty project pages, and there is not yet a single job record complete enough to
justify one.

**To unlock:** tag each job photograph with its suburb, floor size and system.
One completed record is enough to publish the first project page.

### 5.4 Still open from earlier sections

- **1.2 / 4.1 — the map.** No map embed appears anywhere on the rebuilt site.
  The residential-pin problem is therefore dormant rather than solved. If a map
  is wanted, the §4.1 decision is still required first.
- **2.1 / 2.5 — metallic and commercial.** Unchanged. No page, tab or photograph
  claims either. Six competitors sell metallic epoxy; we have no photograph of
  one, so we do not offer it on the site.
- **3.x — process and product specifics.** The preparation copy deliberately
  says the slab is "mechanically prepared" and never names a grind profile,
  product or cure time. Competitors name specs like "diamond grinding to
  CSP 2–3". We will not until 3.1–3.12 are answered.
- **4.2 — WhatsApp.** Not on the rebuilt site at all. The sticky mobile bar is
  Call + Get quote. Say the word if WhatsApp should return.
