# Conversion tracking

## What is installed

**No analytics library is loaded by this site.** There is no GA4 tag, no Google
Tag Manager container, and no third-party pixel. That was true before this pass
and is still true — nothing was removed, and nothing was added with a made-up
measurement ID.

What *was* added is a vendor-neutral event layer in `main.js`. Every conversion
action now calls `track(name, params)`, which:

1. pushes `{ event: name, ...params }` onto `window.dataLayer`, and
2. calls `window.gtag('event', name, params)` if `gtag` exists.

Both calls are wrapped in `try/catch`, so tracking can never break the page.

## To turn it on

Add **one** of the following to every page's `<head>`. Do not add both.

**Google Tag Manager** — paste the container snippet. `dataLayer` is already
being populated, so the events below are immediately available as GTM triggers.

**GA4 directly** — paste the `gtag.js` snippet with the real measurement ID.
`track()` will forward to it with no further changes.

## Events being fired

| Event | Fires when |
|---|---|
| `click_to_call` | Any `tel:` link is clicked — header, hero, sticky bar, footer, in-copy. |
| `whatsapp_click` | Any WhatsApp link is clicked — drawer, footer, desktop float. |
| `google_maps_click` | The "Open Floor Candy on Google Maps" link is clicked. |
| `assessment_form_start` | First real interaction with either lead form. Fires once per form. |
| `assessment_form_submit` | Formspree returns success. Fires once. |
| `before_after_interaction` | First drag, touch or arrow-key use of any before/after slider. Once per slider; `method` records how. |
| `project_view` | A project link in the recent-work grid is clicked. |
| `assessment_cta_*` | Which assessment CTA was clicked — `hero`, `header`, `sticky`, `offer`, `problem`, `project`, `final`, `extended`. |

Every event carries `page_path`; link events also carry `link_text` and `link_url`.

## Recommended GA4 conversions

Mark `assessment_form_submit`, `click_to_call` and `whatsapp_click` as key
events. `assessment_form_start` is the denominator for form drop-off, and the
`assessment_cta_*` split shows which placement actually drives bookings.

## Form delivery

Both forms post to the same Formspree endpoint (`xqerqnyv`), unchanged. UTM,
GCLID and referrer are captured on landing into `sessionStorage` and merged into
the payload at submit, so lead source survives a multi-page visit.

**Double submission** is now blocked by an in-flight flag on each form, in
addition to the disabled button — the flag is cleared only on failure, so a slow
network cannot produce two leads.

## Secrets

None. The Formspree endpoint is a public form ID by design. No keys or private
endpoints appear in client-side code.
