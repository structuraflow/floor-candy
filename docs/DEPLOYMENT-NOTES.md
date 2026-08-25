# Deployment Notes

## Production is untouched

| | |
|---|---|
| Production branch | `main`, at commit `757a952` — **not modified** |
| Work branch | `redesign/phase3-premium` |
| Live domain | `https://www.floorcandyepoxy.com` — **not redeployed** |
| Vercel project | `prj_mH0vxpw7jtwjWi3lqQm26a6UlWrM` (team `team_5Zr8gdgFERAhRnaT82R74pE5`) |
| Git remote | `https://github.com/structuraflow/floor-candy.git` |

## Stack

Static HTML, CSS and vanilla JS. **No build step, no framework, no runtime dependencies.** `tools/build-pages.js` is a dev-time generator that emits plain HTML; it is excluded from deployment and never runs on Vercel.

## Deploying the preview

```bash
git checkout redesign/phase3-premium
vercel                    # preview deployment
```

Or push the branch and let the Git integration create the preview:

```bash
git push -u origin redesign/phase3-premium
```

## Promoting to production — do not run without sign-off

```bash
git checkout main
git merge --no-ff redesign/phase3-premium
git push origin main      # triggers the production deployment
```

Roll back with `vercel rollback`, or `git revert` the merge commit.

## Pre-launch checklist

- [ ] **Google Business Profile alignment.** The profile currently shows Tallwoods Village NSW 2430. The site says "servicing Newcastle and the Hunter Region" and claims no premises, so the two do not contradict — but the profile's address and service-area settings should be reviewed before driving traffic. This also determines whether the Newcastle map pack is reachable at all.
- [ ] **Test the form end-to-end.** The Formspree endpoint `https://formspree.io/f/xqerqnyv` was carried over from the previous site and **has not been test-submitted** — sending test data to a live client endpoint would create a junk lead. Submit one real test and confirm it arrives before launch.
- [ ] **Confirm the review count is still 5.0 from 3.** Verified 10 August 2026. If it has changed, update the figure in `index.html`, `tools/build-pages.js` (`reviewsBlock`), and the landing page, then regenerate.
- [ ] Verify redirects resolve: `/services`, `/gallery`, `/contact` → new URLs.
- [ ] Submit `sitemap.xml` in Search Console.
- [ ] Run Lighthouse against the preview URL.
- [ ] `/lp/garage-floors-newcastle` is `noindex, nofollow` and disallowed in `robots.txt` — keep it that way until the campaign is live and you want it crawled.

## Form

`floor-assessment.html` posts to Formspree via `fetch`, with a real success state and a real failure state that surfaces the phone number and email. **It never shows a false success** — the success panel only renders on an HTTP-OK response.

Captured automatically into every submission: `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `gclid`, `gbraid`, `wbraid`, `msclkid`, plus `landing_page`, `referrer` and a static `lead_source`. Attribution persists across the session in `sessionStorage`, so a visitor who arrives on an ad and converts two pages later is still attributed.

Spam protection: a `_gotcha` honeypot. No CAPTCHA — TSR's site demonstrates how much friction that adds to a lead form.

**Photo upload was deliberately omitted.** Formspree file uploads require a paid plan, and an unsupported attachment would fail the whole submission — losing the lead. Instead the form and the success state both ask for photos by email. If you upgrade Formspree, add a file input and it will work.

## Content changes

- **Pages generated from `tools/build-pages.js`** (garage, projects, process, about, lp, privacy, terms, 404): edit the generator and run `node tools/build-pages.js`.
- **`index.html` and `floor-assessment.html` are hand-authored.** If the shared header or footer changes in the generator, mirror it in those two files.

## Ads

Point campaigns at `/lp/garage-floors-newcastle`. Geo-target Newcastle, Lake Macquarie and Maitland with "presence: people in this location". Schedule ads to Mon–Fri 7am–7pm to match the answering hours on the Google profile. Configure call and form conversion tracking before spending.

## Removed from production

`services.html`, `gallery.html`, `contact.html` deleted (301s in place). Previous AI hero videos (`hero-transform-scrub.mp4` 8.5 MB, `hero-transform-mobile.mp4` 1.8 MB) deleted. 16 AI/stock images moved to `assets/_quarantine/`, which is excluded from deployment via `.vercelignore` along with `assets/images`, `tools` and `docs`.
