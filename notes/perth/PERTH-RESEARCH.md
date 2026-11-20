# Floor Candy Perth: competitor research, structure, offer analysis
Researched 20 Nov 2026 with Firecrawl (web search, Google Maps data, page scrapes).

## 1. Who is performing best in Perth

| Company | Google rating / reviews | Organic visibility | Prices on site? | Warranty claim |
|---|---|---|---|---|
| Shimicoat | 4.9 / 155 | Maps | No (manufacturer + store, not a like-for-like installer) | n/a |
| Conjoint Industries | 5.0 / 42 | Maps | No | n/a |
| Hawk Concrete Floor Coatings | 4.7 / 35 | Maps | No, says so in its FAQ | 2 yr, up to 10 for specialised |
| Westcoat Epoxy | 5.0 / 33 | Maps | No | "10Y+" stat |
| Gard Coatings | 5.0 / 27 | #4 for "epoxy flooring Perth" | No | Written 5-yr workmanship |
| **Perth Concrete Care** | **5.0 / 23** | Ranks for flake, metallic and cost searches | **Yes, full table** | Not stated |
| iCOAT WA | 5.0 / 17 | #1 for "flake garage floor coating Perth" | No | n/a |
| West Coast Epoxy Flooring | n/a | Ranks for "epoxy flooring Perth" + cost FAQ | Yes ($60-160/m²) | 5 yr |
| Apex Epoxy Perth | 5.0 / 8 | Cost-guide blog ranks | Blog range only | 5 yr |

**Model chosen: Perth Concrete Care (perthconcretecare.com.au).** It has solid reviews, ranks across the money searches (flake, metallic, cost), and is the most complete conversion site in the market. It is also the closest business model to Floor Candy: one owner-operator ("Rob"), mobile, no showroom, residential garages first. The bigger review counts belong to commercial or industrial crews or a product manufacturer, so they are a different business.

## 2. Their homepage structure (what the Perth page now follows)
1. Top bar: service area · email · phone
2. Nav with **Pricing** and **FAQ** as top-level items
3. Hero: Google 5-star link, keyword H1 ("... Epoxy Flooring Perth"), one-line sub, 3 service bullets, 2 CTAs (quote / call), trust chips
4. Services grid: each card has 3 bullets and a link
5. Before & after
6. Recent projects, each captioned *finish – suburb*
7. **Pricing section**: price cards per finish, what's included, fine print on what moves the price, and a "which finish is right" comparison table
8. Service areas: regions plus suburb links, with fact chips
9. Quote form: fixed written quote, no obligation, reply within 24h, photo upload
10. Google reviews ("check us on Google before you book") and the **owner block** ("You deal with Rob from quote to handover")
11. Technical FAQ (CSP, slip ratings, cure times, cost drivers)
12. "Still have questions? Call Rob", then the footer with ABN and credentials

**Copywriting traits we adopted:** plain and specific; prices out in the open; prep and technical detail as proof; owner named in every CTA; "no hard sell"; telling people when a cheaper option will do.
**Not copied:** their text (all copy is original), and any claim Floor Candy can't verify (insurance, police clearance, Australian Standards, HEPA, 24h reply, warranty, ABN).

## 3. Perth prices found

| Source | Figure |
|---|---|
| Perth Concrete Care | Flake **$100-120/m²**, metallic $220-280, hone & seal $80-100, polished $140-220 |
| West Coast Epoxy Flooring | $60-160/m²; garages quoted at **$2,500-$4,500** (also $2,500-$3,500) |
| Apex Epoxy Perth (blog) | $40-120+/m² garages |
| GoPoxy (commercial) | From $55/m² + GST; factory from $65 |
| hipages (national) | Flake $40-60/m² |
| Epoxy Warehouse (Perth DIY) | Full-flake garage **kit $1,150-$1,292** |
| Hawk, Gard, iCOAT, Westcoat | No prices published |

## 4. Offer analysis: Floor Candy vs Perth

**Current offer:** double garage from $2,450, "new customers save $250", free on-site look, fixed written price, walkthrough before the balance.

- **$2,450 is the cheapest published professional double-garage price in Perth.** A double garage is roughly 36-40m², so that works out to about $61-68/m². Perth Concrete Care would be about $3,600-$4,800 for the same floor, and West Coast quotes $2,500-$4,500. Floor Candy comes in under the whole published market and only about $1,150 above a DIY kit.
- **Risk: it was costed for Taree, not Perth.** Perth labour, fuel and a metro area 120km+ end to end all push costs up. At that price, the risk is either margin or looking like the cheap option. **Jarrod must re-cost before this goes live.** A $2,950-$3,450 "from" price would still undercut the leader and leave room for travel.
- **Drop "new customers save $250" in Perth.** In a new market every customer is new, so it reads as a permanent discount, not an offer. It has been removed from the Perth page. If Jarrod wants a launch hook, make it real and limited, e.g. "first 10 Perth garages: $X off in exchange for before/after photos and a Google review". That also fixes the review gap.
- **Warranty is table stakes in Perth.** Gard, West Coast and Apex all advertise 5-year workmanship warranties, and Hawk advertises 2-10 years. Floor Candy publishes none, which is the biggest hole in the offer. Get written terms from Jarrod, then add a warranty line to the hero, pricing card and FAQ.
- **Where Floor Candy is stronger:** a published price (most rivals hide theirs), the walkthrough before the balance (nobody else offers it), drag before/after sliders (only PCC has one, a static pair), and owner-operated (matches PCC).
- **Cheap to add if Jarrod agrees:** daily progress photos during the job (Gard's angle), a reply-time promise (PCC promises 24h), and a flake colour range shown online (PCC has 22 named blends plus a visualiser).

## 5. Must-fix before Perth goes live (blocked on Jarrod)
1. **Perth pricing**: confirm or re-cost the $2,450 double-garage figure.
2. **Google Business Profile**: still registered in Tallwoods Village NSW. Move the service area to Perth, or Maps visibility is zero.
3. **Warranty terms** in writing.
4. **ABN, public liability insurance** (and police clearance if held). Perth Concrete Care shows its ABN in the footer.
5. **Which suburbs** he will actually cover, and where he is based. The page lists metro regions as a placeholder.
6. **Topcoat UV stability.** Perth competitors all push "won't yellow in the Perth sun" (polyaspartic or PU). The FAQ is written so it makes no claim until he confirms his system.
7. **First Perth jobs** photographed and captioned with system and suburb, to replace the NSW work over time.

## 6. What was built
- `perth/index.html` + `perth/perth.css`: a standalone Perth homepage in the structure above, reusing `home.css`, `main.js`, `home.js` and genuine job photos only. It is `noindex` while it is a draft. The form posts to the same Formspree form, with subject "New PERTH quote request" and a hidden `market=Perth` field.
- The NSW homepage and inner pages are untouched.
- QA screenshots: `notes/perth/qa/`.
