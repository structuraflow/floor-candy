#!/usr/bin/env node
/* Floor Candy — static page generator.
   Dev-time only. Emits plain HTML; the deployed site has no build dependency.
   index.html and floor-assessment.html are hand-authored; if the shared header
   or footer changes here, mirror it in those two files. */

const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

const PHONE_HREF = 'tel:+61435193845';
const PHONE_TEXT = '0435 193 845';
const AREA = 'Servicing Newcastle &amp; the Hunter Region';

const arrow = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M1 7h11M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

const header = (cur, depth = 0) => {
  const p = depth ? '../' : '';
  const on = (h) => (cur === h ? ' aria-current="page"' : '');
  return `<header class="hdr">
  <div class="container hdr-in">
    <a class="brand" href="${p || '/'}"><img src="${p}assets/logo-mark.png" alt="" width="26" height="26">Floor <span>Candy</span></a>
    <nav class="nav" aria-label="Primary">
      <a href="/garage-floor-coating"${on('garage')}>Garage floors</a>
      <a href="/projects"${on('projects')}>Projects</a>
      <a href="/process"${on('process')}>Process</a>
      <a href="/about"${on('about')}>About</a>
    </nav>
    <div class="hdr-cta">
      <a class="hdr-phone" href="${PHONE_HREF}">0435&nbsp;193&nbsp;845</a>
      <a class="btn" href="/floor-assessment">Free floor assessment</a>
      <button class="burger" id="burger" aria-expanded="false" aria-controls="drawer" aria-label="Menu"><span></span></button>
    </div>
  </div>
</header>

<div class="drawer" id="drawer">
  <a href="/garage-floor-coating">Garage floors</a>
  <a href="/projects">Projects</a>
  <a href="/process">Process</a>
  <a href="/about">About</a>
  <a href="/floor-assessment" class="btn btn--lg">Book a free floor assessment</a>
  <a href="${PHONE_HREF}" class="btn btn--ghost btn--lg">Call Jarrod — ${PHONE_TEXT}</a>
  <p class="drawer-meta">${AREA}<br>Mon–Fri, 7am–7pm</p>
</div>`;
};

const footer = (depth = 0) => {
  const p = depth ? '../' : '';
  return `<footer class="ftr">
  <div class="container">
    <div class="ftr-grid">
      <div>
        <a class="brand" href="${p || '/'}"><img src="${p}assets/logo-mark.png" alt="" width="26" height="26">Floor <span>Candy</span></a>
        <p class="small" style="margin-top:var(--s-4);max-width:34ch">Epoxy and concrete floor coatings, owner-led, servicing Newcastle and the Hunter Region.</p>
      </div>
      <div>
        <p class="ftr-head">Services</p>
        <ul>
          <li><a href="/garage-floor-coating">Garage floor coatings</a></li>
          <li><a href="/floor-assessment">Driveways &amp; exterior</a></li>
          <li><a href="/floor-assessment">Polished &amp; sealed concrete</a></li>
          <li><a href="/floor-assessment">Natural stone polishing</a></li>
        </ul>
      </div>
      <div>
        <p class="ftr-head">Company</p>
        <ul>
          <li><a href="/projects">Projects</a></li>
          <li><a href="/process">Process</a></li>
          <li><a href="/about">About</a></li>
          <li><a href="/floor-assessment">Free floor assessment</a></li>
        </ul>
      </div>
      <div>
        <p class="ftr-head">Contact</p>
        <ul>
          <li><a href="${PHONE_HREF}">${PHONE_TEXT}</a></li>
          <li><a href="mailto:admin@floorcandyepoxy.com">admin@floorcandyepoxy.com</a></li>
        </ul>
        <p class="xs" style="margin-top:var(--s-4)">Servicing Newcastle, Lake Macquarie, Maitland &amp; surrounding parts of the Hunter Region.<br>Mon–Fri, 7am–7pm</p>
      </div>
    </div>
    <div class="ftr-bar">
      <p>© <span id="yr">2026</span> Floor Candy. All rights reserved.</p>
      <p><a href="/privacy">Privacy</a> &nbsp;·&nbsp; <a href="/terms">Terms</a></p>
    </div>
  </div>
</footer>

<div class="mbar">
  <a href="${PHONE_HREF}">Call Jarrod</a>
  <a href="/floor-assessment" class="is-primary">Free assessment</a>
</div>`;
};

const page = ({ file, title, desc, cur, body, depth = 0, noindex = false, bare = false, schema = '' }) => {
  const p = depth ? '../' : '';
  const canonical = 'https://www.floorcandyepoxy.com/' + file.replace(/\.html$/, '').replace(/^index$/, '');
  return `<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<meta name="description" content="${desc}">
${noindex ? '<meta name="robots" content="noindex, nofollow">\n' : `<link rel="canonical" href="${canonical}">\n`}<meta name="theme-color" content="#0B0B0C">
<meta property="og:type" content="website">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${desc}">
<meta property="og:image" content="https://www.floorcandyepoxy.com/assets/img/og-floor-candy.jpg">
<meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="${p}assets/fonts/archivo-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="${p}styles.css">
<link rel="icon" type="image/png" sizes="32x32" href="${p}assets/favicon-32.png">
<link rel="apple-touch-icon" href="${p}assets/apple-touch-icon.png">
${schema}</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

${bare ? '' : header(cur, depth)}

<main id="main">
${body}
</main>

${bare ? '' : footer(depth)}

<script src="${p}main.js" defer></script>
</body>
</html>
`;
};

/* ---------- Shared blocks ---------- */
const ctaBand = `
  <section class="section">
    <div class="container center">
      <div class="stack" data-reveal style="justify-items:center">
        <p class="eyebrow eyebrow--plain">Newcastle &amp; the Hunter Region</p>
        <h2 class="h-display" style="max-width:16ch">Start with the slab.</h2>
        <p class="lead measure" style="margin-inline:auto">Book a free on-site assessment and find out what your concrete actually needs — before anyone quotes you a number.</p>
        <div class="btn-row" style="justify-content:center;margin-top:var(--s-4)">
          <a class="btn btn--lg" href="/floor-assessment">Book a free floor assessment</a>
          <a class="btn btn--ghost btn--lg" href="${PHONE_HREF}">Call Jarrod — ${PHONE_TEXT}</a>
        </div>
      </div>
    </div>
  </section>`;

const reviewsBlock = `
  <section class="section section--surface section--line">
    <div class="container">
      <div class="section-head" data-reveal>
        <p class="eyebrow">What customers say</p>
        <div class="gsum">
          <span class="gsum-score">5.0</span>
          <span><span class="stars" aria-hidden="true">★★★★★</span><span class="small" style="display:block">from 3 Google reviews</span></span>
        </div>
        <p class="small measure">We are a small operation and these are all of them, in full, exactly as they were written.</p>
      </div>
      <div class="grid grid-3">
        <article class="review" data-reveal>
          <span class="stars" aria-hidden="true">★★★★★</span>
          <blockquote>“Jarrod and his team did a fantastic job at my house very satisfied with the results and how professional he is , would highly recommend this company”</blockquote>
          <footer><p class="review-name">Reece Hawes</p><p class="review-meta">Google review</p></footer>
        </article>
        <article class="review" data-reveal data-d="1">
          <span class="stars" aria-hidden="true">★★★★★</span>
          <blockquote>“We had an epoxy floor installed in our shed conversion and it’s completely transformed the space. It looks great and is super easy to maintain. Jarrod was super helpful and efficient, the finish is high quality. Really happy with the result and would definitely recommend.”</blockquote>
          <footer><p class="review-name">Miranda</p><p class="review-meta">Google review</p></footer>
        </article>
        <article class="review" data-reveal data-d="2">
          <span class="stars" aria-hidden="true">★★★★★</span>
          <blockquote>“I recently had the pleasure of working with Jarred from Floor Candy and I couldn’t be happier with the results. His expertise in natural stone polishing is outstanding—he restored our stone surfaces to a beautiful, high-quality finish that…”</blockquote>
          <p class="xs">Shown as Google truncates it.</p>
          <footer><p class="review-name">Miranda Bell</p><p class="review-meta">Google review</p></footer>
        </article>
      </div>
      <p class="xs" data-reveal style="margin-top:var(--s-5)">Rating and review count verified on the Floor Candy Google Business Profile, 10 August 2026.</p>
    </div>
  </section>`;

const pageHero = (eyebrow, h1, lead) => `
  <section class="section" style="padding-top:calc(76px + var(--section-y));padding-bottom:var(--s-8)">
    <div class="container">
      <div class="stack" data-reveal>
        <p class="eyebrow">${eyebrow}</p>
        <h1 class="h1" style="max-width:18ch">${h1}</h1>
        <p class="lead measure">${lead}</p>
      </div>
    </div>
  </section>`;

const tenSteps = `
        <ol class="steps" data-reveal data-d="1">
          <li><div><h3>Inspect the concrete</h3><p>We look at the slab and at how the space is actually used — parked on, walked on, washed down, or all three.</p></div></li>
          <li><div><h3>Assess the surface</h3><p>Cracks, damage, contamination and potential moisture concerns. This is where the system gets specified.</p></div></li>
          <li><div><h3>Diamond-grind mechanically</h3><p>Weak surface material comes off and the slab is profiled so the coating has something to key into.</p></div></li>
          <li><div><h3>Extract and clean</h3><p>Industrial dust extraction through the grind, then a thorough clean of the prepared surface.</p></div></li>
          <li><div><h3>Repair where appropriate</h3><p>Cracks, chips and damaged areas made good. Existing or moving cracks can be repaired — they cannot be permanently eliminated, and we will say so on site.</p></div></li>
          <li><div><h3>Prime or base-coat</h3><p>The primer or base system specified for your concrete and its intended use.</p></div></li>
          <li><div><h3>Apply the finish</h3><p>Your selected finish, including a full flake broadcast where that is the system chosen.</p></div></li>
          <li><div><h3>Refine before topcoat</h3><p>Excess flake removed and the surface refined, then the protective topcoat goes on.</p></div></li>
          <li><div><h3>Final inspection and walkthrough</h3><p>We walk the finished floor with you before the balance is paid.</p></div></li>
          <li><div><h3>Handover guidance</h3><p>System-specific advice on curing, when vehicles can go back on, cleaning and maintenance.</p></div></li>
        </ol>`;

/* ---------- Pages ---------- */
const pages = [];

/* Garage floor coating */
pages.push({
  file: 'garage-floor-coating.html', cur: 'garage',
  title: 'Garage Floor Coatings | Newcastle &amp; Hunter | Floor Candy',
  desc: 'Flake epoxy and sealed garage floors across Newcastle, Lake Macquarie and Maitland. Diamond-ground preparation, owner-led, free on-site assessment.',
  body: `
  ${pageHero('Garage floors · Newcastle &amp; the Hunter', 'Garage floor coatings, ground back and done once.',
    'The most common job we take on, and the one where preparation matters most. A garage slab gets hot tyres, dropped tools, oil and water — a coating only survives that if it is bonded to properly prepared concrete.')}

  <section class="section--tight">
    <div class="container">
      <figure class="fig ar-wide" data-reveal>
        <div class="fig-media">
          <picture>
            <source type="image/avif" srcset="assets/img/garage-flake-finished-1440.avif">
            <source type="image/webp" srcset="assets/img/garage-flake-finished-1440.webp 1440w, assets/img/garage-flake-finished-1080.webp 1080w" sizes="100vw">
            <img src="assets/img/garage-flake-finished-1440.jpg" alt="Completed flake epoxy garage floor by Floor Candy" width="1440" height="648" loading="lazy" decoding="async">
          </picture>
        </div>
        <figcaption><p class="fig-title">Flake epoxy garage floor</p><p class="fig-meta">Full flake broadcast, ground back and topcoated. A genuine Floor Candy project.</p></figcaption>
      </figure>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="split">
        <div class="stack" data-reveal>
          <p class="eyebrow">The honest version</p>
          <h2 class="h2">Why garage floors fail.</h2>
          <p class="lead measure-tight">Almost always the bond. A coating rolled onto a sealed, dusty or contaminated slab has nothing to hold to, and the first hot summer tyre lifts it.</p>
          <p class="small measure">Grinding is the fix, and it is the step that disappears from a sharpened quote — because nobody can see it once the floor is finished. That is exactly why we photograph it.</p>
        </div>
        <div class="fail" data-reveal data-d="1">
          <div class="fail-row"><div><p class="fail-term">Hot-tyre pickup</p></div><div><p class="fail-desc">Warm tyres soften a weakly bonded coating and pull it off in patches where you park.</p></div></div>
          <div class="fail-row"><div><p class="fail-term">Lifting at the door</p></div><div><p class="fail-desc">The threshold takes sun, rain and traffic. It is the first place a shortcut shows.</p></div></div>
          <div class="fail-row"><div><p class="fail-term">Dusting</p></div><div><p class="fail-desc">A weak surface layer left in place keeps shedding fine grit no matter how often you sweep.</p></div></div>
          <div class="fail-row"><div><p class="fail-term">Peeling after a DIY kit</p></div><div><p class="fail-desc">Kits go straight onto the slab as it is. If yours has failed, the old coating comes off as part of our preparation.</p></div></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--surface section--line">
    <div class="container">
      <div class="split" style="align-items:flex-start">
        <div class="sticky-col stack" data-reveal>
          <p class="eyebrow">Our method</p>
          <h2 class="h2">The Floor Candy Surface Preparation System.</h2>
          <p class="lead measure-tight">Ten steps, in order, on every floor. What changes between jobs is the system specified at step&nbsp;2 — that depends on your concrete, not on a package.</p>
        </div>
        ${tenSteps}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container narrow">
      <div class="section-head" data-reveal><p class="eyebrow">Garage questions</p><h2 class="h2">What people ask before booking.</h2></div>
      <div class="faq" data-reveal data-d="1">
        <details><summary>How much does a garage floor cost?</summary><div class="faq-body"><p>We do not publish prices, because the honest answer depends on the slab — its size, its condition, whether there is an existing coating to remove, access, and the finish you choose. You get a fixed itemised price in writing after we have seen it.</p></div></details>
        <details><summary>Do I need to empty the garage?</summary><div class="faq-body"><p>Yes — we need clear access to the whole slab to grind it properly. We will talk through what that means for your space at the assessment.</p></div></details>
        <details><summary>My existing coating is peeling. Can you go over it?</summary><div class="faq-body"><p>Not over it. A failing coating has to come off as part of the preparation, or the new floor inherits the same problem. Removal is assessed and priced as part of the job.</p></div></details>
        <details><summary>Is a flake finish slippery?</summary><div class="faq-body"><p>A full flake broadcast has noticeably more texture underfoot than a smooth gloss. Tell us how the space gets used — wet feet, dogs, a workshop — and we will talk through the trade-off honestly on site.</p></div></details>
        <details><summary>How long before I can park on it?</summary><div class="faq-body"><p>That depends on the system specified for your slab, so we give you the actual figures for your floor at handover rather than a blanket promise here.</p></div></details>
      </div>
    </div>
  </section>
  ${reviewsBlock}
  ${ctaBand}`
});

/* Projects */
pages.push({
  file: 'projects.html', cur: 'projects',
  title: 'Projects | Genuine Floor Candy Work | Newcastle',
  desc: 'Real Floor Candy projects — flake epoxy garage floors, sealed driveways, polished concrete and preparation work, photographed as they are.',
  body: `
  ${pageHero('Our work', 'Real floors, photographed as they are.',
    'Every image on this page is a genuine Floor Candy job. No stock photography, no renders, and nothing generated. When we have fewer projects to show than a franchise, we would rather show fewer.')}

  <section class="section--tight">
    <div class="container">
      <div class="grid grid-2">

        <figure class="fig ar-wide" data-reveal>
          <div class="fig-media">
            <picture>
              <source type="image/webp" srcset="assets/img/garage-flake-finished-1080.webp">
              <img src="assets/img/garage-flake-finished-1080.jpg" alt="Finished flake epoxy garage floor with grey and charcoal flake" width="1080" height="608" loading="lazy" decoding="async">
            </picture>
          </div>
          <figcaption><p class="fig-title">Flake epoxy garage floor</p><p class="fig-meta">Full flake broadcast, ground back and topcoated.</p></figcaption>
        </figure>

        <figure class="fig ar-wide" data-reveal data-d="1">
          <div class="fig-media">
            <picture>
              <source type="image/webp" srcset="assets/img/driveway-sealed-1440.webp">
              <img src="assets/img/driveway-sealed-1440.jpg" alt="Sealed concrete driveway running up to a modern Australian home" width="1440" height="648" loading="lazy" decoding="async">
            </picture>
          </div>
          <figcaption><p class="fig-title">Sealed concrete driveway</p><p class="fig-meta">Resurfaced and sealed, kerb to garage door.</p></figcaption>
        </figure>

        <figure class="fig ar-port" data-reveal>
          <div class="fig-media">
            <picture>
              <source type="image/webp" srcset="assets/img/polished-concrete-finished-900.webp">
              <img src="assets/img/polished-concrete-finished-900.jpg" alt="Finished polished concrete interior floor" width="900" height="1200" loading="lazy" decoding="async">
            </picture>
          </div>
          <figcaption><p class="fig-title">Polished concrete interior</p><p class="fig-meta">Ground back and sealed to a low-sheen finish.</p></figcaption>
        </figure>

        <figure class="fig ar-port" data-reveal data-d="1">
          <div class="fig-media">
            <picture>
              <source type="image/webp" srcset="assets/img/prep-grinding-extraction-900.webp">
              <img src="assets/img/prep-grinding-extraction-900.jpg" alt="Floor grinder and industrial dust extractor part-way through preparing a slab" width="900" height="1200" loading="lazy" decoding="async">
            </picture>
          </div>
          <figcaption><p class="fig-title">Preparation in progress</p><p class="fig-meta">Mechanical grinding with industrial dust extraction — the stage that decides whether the floor lasts.</p></figcaption>
        </figure>

      </div>

      <p class="note" data-reveal style="margin-top:var(--s-7)">We are building this gallery out as jobs complete. If you want to see work closer to your own project, ask at the assessment — we will show you what we have.</p>
    </div>
  </section>
  ${reviewsBlock}
  ${ctaBand}`
});

/* Process */
pages.push({
  file: 'process.html', cur: 'process',
  title: 'Our Process | Floor Candy Surface Preparation',
  desc: 'How a Floor Candy floor gets done — assessment, diamond grinding, dust extraction, repair, priming, finish, topcoat, walkthrough and handover guidance.',
  body: `
  ${pageHero('How we work', 'The Floor Candy Surface Preparation System.',
    'Ten steps, in the same order, on every floor. The only thing that changes between jobs is the system specified after we have looked at your concrete — because that is what it should depend on.')}

  <section class="section--tight">
    <div class="container">
      <div class="split" style="align-items:flex-start">
        <div class="sticky-col stack" data-reveal>
          <h2 class="h3">The ten steps</h2>
          <figure class="fig">
            <div class="fig-media" style="aspect-ratio:3/4">
              <picture>
                <source type="image/webp" srcset="assets/img/prep-grinding-extraction-900.webp">
                <img src="assets/img/prep-grinding-extraction-900.jpg" alt="Floor grinder and Hilti industrial dust extractor mid-grind on a Floor Candy job" width="900" height="1200" loading="lazy" decoding="async">
              </picture>
            </div>
            <figcaption><p class="fig-meta">Steps three and four, on an actual job.</p></figcaption>
          </figure>
        </div>
        ${tenSteps}
      </div>
    </div>
  </section>

  <section class="section section--surface section--line">
    <div class="container">
      <div class="split">
        <div class="stack" data-reveal>
          <p class="eyebrow">What we commit to</p>
          <h2 class="h2">The parts that are not about chemistry.</h2>
          <p class="lead measure-tight">Most complaints about this trade are not about coatings. They are about people not turning up, mess left behind, and being asked to pay before you have seen the work.</p>
        </div>
        <div class="stack" data-reveal data-d="1">
          <div class="card"><h3 class="h3">A written scope before you commit</h3><p>You get the scope and the price in writing first. A booking deposit may be required to secure your date and order materials.</p></div>
          <div class="card"><h3 class="h3">We call before we arrive</h3><p>You are not left guessing which day, or sitting home for a no-show.</p></div>
          <div class="card"><h3 class="h3">We protect and clean up</h3><p>Dust is extracted at the grinder, and surrounds are protected. Concrete dust through a house is nobody's idea of a finished job.</p></div>
          <div class="card"><h3 class="h3">A final walkthrough</h3><p>Every project finishes with a final walkthrough, so you can inspect the completed surface before paying the remaining balance.</p></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container narrow">
      <div class="note" data-reveal>
        <strong>On warranty.</strong> Every coating system is specified according to the condition and intended use of the concrete. Warranty coverage depends on the selected system, substrate condition and product manufacturer. Any concern relating to Floor Candy's workmanship will be inspected and assessed directly.
      </div>
    </div>
  </section>
  ${ctaBand}`
});

/* About */
pages.push({
  file: 'about.html', cur: 'about',
  title: 'About | Owner-Led Concrete Coatings | Floor Candy',
  desc: 'Floor Candy is an owner-led concrete coating business servicing Newcastle and the Hunter Region. Jarrod quotes the work, sets the preparation standard and signs it off.',
  body: `
  ${pageHero('About', 'Owner-led, and small on purpose.',
    'Floor Candy is run by Jarrod. He quotes the work, sets the preparation standard, handles the communication and signs the floor off with you at the end. Trusted additional help comes in when a project needs it — but the standard and the accountability stay in one place.')}

  <section class="section--tight">
    <div class="container">
      <div class="split">
        <div class="stack" data-reveal>
          <h2 class="h2">Why that matters here.</h2>
          <p class="lead measure-tight">Concrete coating is a trade where the most important work is invisible by the time you see the result. Once the topcoat is down, a floor that was properly ground and a floor that was rushed look identical — for about a season.</p>
          <p class="small measure">Being small means the person who assessed your slab is the person answerable for how it was prepared. It also means we take on fewer jobs than a franchise, and we would rather say that plainly than pretend to a scale we do not have.</p>
        </div>
        <div class="stack" data-reveal data-d="1">
          <div class="card">
            <h3 class="h3">Where we work</h3>
            <p>Newcastle, Lake Macquarie, Maitland and surrounding parts of the Hunter Region. Port Stephens, Cessnock and projects further out are considered depending on the size and requirements of the job.</p>
          </div>
          <div class="card">
            <h3 class="h3">What we take on</h3>
            <p>Garage floors, driveways and exterior concrete, interior and shed slabs, polished and sealed concrete, and natural stone polishing. Selected commercial work where the scope suits a small owner-led operation.</p>
          </div>
          <div class="card">
            <h3 class="h3">How we quote</h3>
            <p>On site, after looking at the actual concrete. We do not price floors over the phone, because the slab is the thing that decides the job.</p>
          </div>
        </div>
      </div>
    </div>
  </section>
  ${reviewsBlock}
  ${ctaBand}`
});

/* Google Ads landing page */
pages.push({
  file: 'lp/garage-floors-newcastle.html', depth: 1, bare: true, noindex: true,
  title: 'Garage Floor Coating Newcastle | Floor Candy',
  desc: 'Garage floor coatings across Newcastle, Lake Macquarie and Maitland. Diamond-ground preparation, fixed itemised pricing, free on-site assessment.',
  body: `
  <div style="position:sticky;top:0;z-index:90;background:rgba(11,11,12,.92);backdrop-filter:blur(14px);border-bottom:1px solid var(--hairline-soft)">
    <div class="container hdr-in">
      <span class="brand"><img src="../assets/logo-mark.png" alt="" width="26" height="26">Floor <span>Candy</span></span>
      <a class="btn" href="${PHONE_HREF}">Call ${PHONE_TEXT}</a>
    </div>
  </div>

  <section class="section" style="padding-top:var(--s-8)">
    <div class="container">
      <div class="split" style="align-items:flex-start">
        <div class="stack">
          <p class="eyebrow">Newcastle · Lake Macquarie · Maitland</p>
          <h1 class="h1">Garage floor coating in Newcastle.</h1>
          <p class="lead measure-tight">Diamond-ground preparation, a system specified for your slab, and a fixed itemised price in writing. Free on-site assessment.</p>
          <div class="hero-proof" style="margin-top:var(--s-5)">
            <span class="stars" aria-hidden="true">★★★★★</span>
            <span class="small"><strong>5.0</strong> from 3 Google reviews</span>
          </div>
          <div class="btn-row" style="margin-top:var(--s-6)">
            <a class="btn btn--lg" href="#lp-form">Book my free assessment</a>
            <a class="btn btn--ghost btn--lg" href="${PHONE_HREF}">Call Jarrod — ${PHONE_TEXT}</a>
          </div>

          <figure class="fig ar-wide" style="margin-top:var(--s-7)">
            <div class="fig-media">
              <picture>
                <source type="image/webp" srcset="../assets/img/garage-flake-finished-1080.webp">
                <img src="../assets/img/garage-flake-finished-1080.jpg" alt="Completed flake epoxy garage floor by Floor Candy" width="1080" height="608" fetchpriority="high" decoding="async">
              </picture>
            </div>
            <figcaption><p class="fig-meta">A genuine Floor Candy garage floor. Not a render, not stock.</p></figcaption>
          </figure>
        </div>

        <div id="lp-form" class="callout">
          <h2 class="h3" style="margin-bottom:var(--s-2)">Free on-site floor assessment</h2>
          <p class="small" style="margin-bottom:var(--s-5)">Written slab assessment, the system specified for it, and a fixed price — yours whether you go ahead or not.</p>
          <a class="btn btn--lg btn--block" href="/floor-assessment">Start my assessment request</a>
          <p class="xs" style="margin-top:var(--s-4);text-align:center">Or call Jarrod directly on <a href="${PHONE_HREF}">${PHONE_TEXT}</a>, Mon–Fri 7am–7pm.</p>
          <hr class="hr" style="margin-block:var(--s-6)">
          <ul>
            <li><span class="tick" aria-hidden="true">✓</span><span>Mechanical diamond grinding with industrial dust extraction</span></li>
            <li><span class="tick" aria-hidden="true">✓</span><span>System specified after we see your slab, not from a package</span></li>
            <li><span class="tick" aria-hidden="true">✓</span><span>Owner-led — Jarrod quotes it and signs it off</span></li>
            <li><span class="tick" aria-hidden="true">✓</span><span>Final walkthrough before the remaining balance is paid</span></li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--surface section--line">
    <div class="container">
      <div class="section-head" data-reveal><p class="eyebrow">Why floors fail</p><h2 class="h2">A cheap floor costs more the second time.</h2></div>
      <div class="fail" data-reveal>
        <div class="fail-row"><div><p class="fail-term">Hot-tyre pickup</p></div><div><p class="fail-desc">Warm tyres lift a weakly bonded coating in patches where you park.</p></div></div>
        <div class="fail-row"><div><p class="fail-term">Lifting &amp; peeling</p></div><div><p class="fail-desc">The coating never keyed in — usually acid etching instead of mechanical grinding.</p></div></div>
        <div class="fail-row"><div><p class="fail-term">Dusting</p></div><div><p class="fail-desc">A weak surface layer left in place keeps shedding grit.</p></div></div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container narrow">
      <div class="section-head" data-reveal><p class="eyebrow">Straight answers</p><h2 class="h2">Before you call.</h2></div>
      <div class="faq" data-reveal>
        <details><summary>What does it cost?</summary><div class="faq-body"><p>It depends on the slab — size, condition, whether there is an existing coating to remove, access and finish. You get a fixed itemised price in writing after the assessment, not a range that moves on the day.</p></div></details>
        <details><summary>Do you cover my suburb?</summary><div class="faq-body"><p>Newcastle, Lake Macquarie, Maitland and surrounding parts of the Hunter Region. Port Stephens, Cessnock and further out are considered depending on the job.</p></div></details>
        <details><summary>My DIY kit peeled. Can you fix it?</summary><div class="faq-body"><p>Yes. The failed coating comes off as part of the preparation rather than being coated over.</p></div></details>
        <details><summary>When do I pay?</summary><div class="faq-body"><p>Written scope and quote first. A booking deposit may be required to secure your date and order materials. Every project finishes with a final walkthrough, so you can inspect the completed surface before paying the remaining balance.</p></div></details>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container center">
      <div class="stack" style="justify-items:center">
        <h2 class="h2" style="max-width:18ch">Get your slab looked at.</h2>
        <div class="btn-row" style="justify-content:center">
          <a class="btn btn--lg" href="/floor-assessment">Book my free assessment</a>
          <a class="btn btn--ghost btn--lg" href="${PHONE_HREF}">Call ${PHONE_TEXT}</a>
        </div>
      </div>
    </div>
  </section>

  <footer class="ftr" style="padding-block:var(--s-7) var(--s-5)">
    <div class="container">
      <p class="xs">Floor Candy — epoxy and concrete floor coatings, servicing Newcastle and the Hunter Region. © <span id="yr">2026</span>. <a href="/privacy">Privacy</a></p>
    </div>
  </footer>

  <div class="mbar">
    <a href="${PHONE_HREF}">Call Jarrod</a>
    <a href="/floor-assessment" class="is-primary">Free assessment</a>
  </div>`
});

/* Privacy */
pages.push({
  file: 'privacy.html', cur: '',
  title: 'Privacy Policy | Floor Candy',
  desc: 'How Floor Candy collects, uses and stores the information you provide through this website.',
  body: `
  ${pageHero('Legal', 'Privacy policy.', 'What we collect, why, and what we do not do with it.')}
  <section class="section--tight">
    <div class="container narrow stack">
      <div class="stack-sm"><h2 class="h3">What we collect</h2><p class="small">When you submit a floor assessment request we collect your name, phone number, email address, suburb or postcode, and the details you give us about your floor. If you arrive from an advertisement or a search, we also record basic campaign information so we know which channels are working.</p></div>
      <div class="stack-sm"><h2 class="h3">Why we collect it</h2><p class="small">To contact you about your enquiry, arrange an assessment, and prepare a quote. That is the whole purpose.</p></div>
      <div class="stack-sm"><h2 class="h3">What we do not do</h2><p class="small">We do not sell your information, add you to marketing lists you did not ask for, or share it with third parties for their own use.</p></div>
      <div class="stack-sm"><h2 class="h3">How it reaches us</h2><p class="small">Form submissions are delivered by a third-party form service and by email. Those providers process the data on our behalf in order to deliver it.</p></div>
      <div class="stack-sm"><h2 class="h3">Access and removal</h2><p class="small">Email <a href="mailto:admin@floorcandyepoxy.com">admin@floorcandyepoxy.com</a> and we will tell you what we hold or delete it.</p></div>
      <div class="stack-sm"><h2 class="h3">Contact</h2><p class="small">Floor Candy · <a href="${PHONE_HREF}">${PHONE_TEXT}</a> · <a href="mailto:admin@floorcandyepoxy.com">admin@floorcandyepoxy.com</a></p></div>
    </div>
  </section>`
});

/* Terms */
pages.push({
  file: 'terms.html', cur: '',
  title: 'Terms of Use | Floor Candy',
  desc: 'Terms of use for the Floor Candy website.',
  body: `
  ${pageHero('Legal', 'Terms of use.', 'The basis on which this website is provided.')}
  <section class="section--tight">
    <div class="container narrow stack">
      <div class="stack-sm"><h2 class="h3">About this site</h2><p class="small">This website describes the services Floor Candy offers and lets you request a free floor assessment. Nothing on it is a quote, an offer, or a contract.</p></div>
      <div class="stack-sm"><h2 class="h3">Quotes and scope</h2><p class="small">Pricing and the coating system for any floor are determined after an on-site assessment of the concrete, and are set out in the written scope and quote provided to you.</p></div>
      <div class="stack-sm"><h2 class="h3">Imagery</h2><p class="small">Project photographs on this site are genuine Floor Candy work. Results vary with substrate condition, preparation requirements and the finish selected.</p></div>
      <div class="stack-sm"><h2 class="h3">Contact</h2><p class="small">Floor Candy · <a href="${PHONE_HREF}">${PHONE_TEXT}</a> · <a href="mailto:admin@floorcandyepoxy.com">admin@floorcandyepoxy.com</a></p></div>
    </div>
  </section>`
});

/* 404 */
pages.push({
  file: '404.html', cur: '', noindex: true,
  title: 'Page not found | Floor Candy',
  desc: 'That page does not exist.',
  body: `
  <section class="section" style="padding-top:calc(76px + var(--section-y));min-height:70svh;display:grid;align-items:center">
    <div class="container center">
      <div class="stack" style="justify-items:center">
        <p class="eyebrow eyebrow--plain">404</p>
        <h1 class="h-display" style="max-width:14ch">That page isn't here.</h1>
        <p class="lead measure" style="margin-inline:auto">The link may be old, or the page may have moved. The floors are all still here though.</p>
        <div class="btn-row" style="justify-content:center;margin-top:var(--s-4)">
          <a class="btn btn--lg" href="/">Back to home</a>
          <a class="btn btn--ghost btn--lg" href="/floor-assessment">Book a floor assessment</a>
        </div>
      </div>
    </div>
  </section>`
});

/* ---------- Emit ---------- */
let n = 0;
for (const p of pages) {
  const out = path.join(ROOT, p.file);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, page(p));
  n++;
  console.log('wrote', p.file);
}
console.log('\n' + n + ' pages generated');
