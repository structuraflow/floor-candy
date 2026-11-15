# Lead routing and conversion tracking

_Rewritten 30 Sep 2026. The previous version described the pre-rebuild site's
events and no longer matched `main.js`._

## Where form leads go

Both quote forms (`#home-quote` on `/`, `#contact-quote` on `/contact`) post to
**Formspree form `mrpeeawq`** — `FORM_ENDPOINT` in `tools/build-site.py`. Created by Zach
on 7 Oct 2026, replacing `xqerqnyv` (the July form from commit `b343ab9`). The 21 Sep rebuild shipped the
forms with **no action**, so from 21 Sep to the next deploy the forms could not
send anything; visitors got a "call or email" fallback message.

**Unverified: which inbox Formspree delivers to.** It is not
zachjamesriley12@gmail.com. Log in to Formspree (probably the
structuraflow@gmail.com account), open form `mrpeeawq`, and confirm the target
email is one Jarrod reads within the hour — ideally floorcandyepoxy@gmail.com
plus a copy to Zach. Then send one real test from the live site.

- JS submits with `fetch` and shows an inline confirmation; without JS the form
  POSTs natively and Formspree shows its own thank-you page.
- `_gotcha` honeypot and `_subject` are included.
- There is **no file field**: Formspree rejects uploads on free plans, which
  would have lost the whole lead. Visitors are asked to text photos instead.
- UTM / gclid / fbclid, page URL and referrer travel with every submission.

## Analytics

Nothing is loaded until IDs are set in `tools/build-site.py`:

- `GA4_ID = "G-…"` → renders the gtag snippet on every page.
- `GSC_TOKEN = "…"` → renders the `google-site-verification` meta tag
  (not needed if the property is verified by DNS).

Rebuild with `python3 tools/build-site.py`, then deploy.

## Events (`main.js`, pushed to `dataLayer` and `gtag` if present)

| Event | Fires when |
|---|---|
| `generate_lead` | Formspree accepted a quote form. **Mark as a key event.** |
| `form_start` | First focus into a quote form (once per form). |
| `form_error` | Formspree or the network rejected a submission. |
| `click_call` | Any `tel:` link. **Mark as a key event.** |
| `click_sms` | Any `sms:` link. |
| `click_email` | Any `mailto:` link. |
| `click_whatsapp` | Any `wa.me` link. |
| `quote_cta_click` | Any link to `/contact` or `#quote`. |

Click events carry `link_url` and `page_path`.
