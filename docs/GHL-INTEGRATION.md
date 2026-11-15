# GoHighLevel integration

The quote forms are built and validated but **not connected**. This document is
the whole job of connecting them.

Current behaviour: every `<form data-quote>` has **no `action` attribute**.
`main.js` detects that, blocks the submit, and shows the phone number and email
address instead. Nobody ever gets a silent failure or a 404 — but nobody's
enquiry reaches a CRM either. Until this is wired, **the phone number is the
lead channel**.

---

## 1. What the form already sends

Every field below is already in the markup with the `name` shown. Create a
custom field in GoHighLevel for anything that is not a standard contact field.

| `name` | Field | Required | GHL mapping |
|---|---|---|---|
| `name` | Full name | yes | Contact → First/Last Name |
| `mobile` | Mobile | yes | Contact → Phone |
| `email` | Email | no | Contact → Email |
| `suburb` | Suburb or postcode | yes | Custom field `suburb` |
| `area_type` | Garage / Home / Outdoor / Commercial / Other | yes | Custom field `area_type` |
| `approx_size` | Approximate size | no | Custom field `approx_size` |
| `project_details` | About the floor | no | Custom field `project_details` |
| `photos` | Photos of the floor (multiple) | no | File upload field |
| `contact_preference` | Call / Text / Email | no | Custom field `contact_preference` |
| `page_url` | Page the form was submitted from | auto | Custom field `page_url` |
| `referrer` | `document.referrer` | auto | Custom field `referrer` |
| `utm_source` `utm_medium` `utm_campaign` `utm_term` `utm_content` | Campaign attribution | auto | Attribution fields |
| `gclid` | Google click ID | auto | Custom field `gclid` |
| `fbclid` | Meta click ID | auto | Custom field `fbclid` |

**Attribution is persisted.** `main.js` reads the UTM/GCLID parameters from the
landing URL, stores them in `sessionStorage`, and stamps them onto the form even
if the visitor browses several pages before enquiring. Without that, every
enquiry that did not convert on the landing page would report as direct traffic.

---

## 2. Connecting it

Two options. **A** is simpler; **B** keeps the styled form.

### A — Replace with the GHL embed

Paste the GHL form embed in place of the `quote_form()` output. Simplest, but
you inherit GHL's markup and styling, and you lose the current accessibility
work, the inline validation and the sticky attribution.

### B — Point the existing form at GHL (recommended)

1. In GHL, create the form and its custom fields to match the table above.
2. Get the form's POST endpoint.
3. In `tools/build-site.py`, find `quote_form()` and add the action:

   ```python
   return """<form class="form-card" id="%s" data-quote novalidate
     action="https://services.leadconnectorhq.com/…" method="post"
     enctype="multipart/form-data">
   ```

   `enctype="multipart/form-data"` is required or the photo upload will not send.
4. Rebuild: `python3 tools/build-site.py`
5. In `main.js`, the `if (!form.getAttribute("action"))` block becomes dead code
   once an action exists. It is safe to leave — it only fires when the action is
   missing — and it is a useful guard if the endpoint is ever removed.
6. Decide where the browser lands after submit. GHL can redirect to a thank-you
   URL; if you use one, create `/thank-you/` as a page and add it to
   `build_sitemap_robots()` with `noindex`.

### Test before trusting it

- Submit with a photo attached and confirm the file arrives in GHL.
- Submit from `/?utm_source=test&utm_medium=cpc&gclid=abc123`, then navigate to
  another page and submit from there. The contact must still carry
  `utm_source=test` and `gclid=abc123` — that is the sessionStorage path.
- Submit with required fields blank and confirm the browser never posts.

---

## 3. Suggested pipeline

```
NEW LEAD  →  CONTACTED  →  QUOTE REQUIRED  →  QUOTE SENT  →  FOLLOW-UP  →  WON / LOST
```

Notes on fit with how the business actually runs:

- **QUOTE REQUIRED** is the on-site assessment being booked, not the quote being
  written. The site promises a free on-site look, so this stage is a visit.
- **QUOTE SENT** should carry the fixed written price, because the site commits
  to a fixed price before the customer commits.
- Record the **$250 new-customer saving** as a field on the opportunity, not as
  a pipeline stage. It applies to a first job and is claimed at enquiry — see
  `/terms`.
- Regional and travel-heavy enquiries (Newcastle, Hunter, outside the core area)
  are worth a tag, because they are qualified on job size and timing rather than
  handled like a local job.

No automation copy has been written. That was deliberate — the brief said not to
invent it.

---

## 4. Analytics

Separate from GHL, and also not connected. `main.js` pushes vendor-neutral
events to `window.dataLayer` and calls `gtag` if it exists:

| Event | Fires on |
|---|---|
| `generate_lead` | Valid quote-form submission |
| `click_call` | Any `tel:` link |
| `click_email` | Any `mailto:` link |

**No analytics library is loaded by the site.** Adding GA4 or GTM means adding
the tag and a real measurement ID. See `docs/TRACKING.md`. Nothing will be
recorded until then, including the events above.
