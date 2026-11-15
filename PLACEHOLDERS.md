# What's still waiting on someone

Nothing below appears on the site as a visible `[placeholder]`. Each one is a `None` slot
in `tools/build-site.py`: the sentence that needs it is not rendered until it is filled.
Fill the value, run `python3 tools/build-site.py`, then `tools/qa.py` + `tools/seo-audit.py`.

## From Jarrod
| Slot | Where it shows once filled | Example |
|---|---|---|
| `JOB_FACTS["days_on_site"]` | hero ("Done in 2 days."), process timeline, FAQ | `"2 days"` |
| `JOB_FACTS["walk_on"]` | timeline, "When can I walk and drive on it?" FAQ | `"24 hours"` |
| `JOB_FACTS["drive_on"]` | timeline, same FAQ | `"72 hours"` |
| `JOB_FACTS["response_time"]` | quote "what happens next", thank-you page | `"one business day"` |
| `JOB_FACTS["booking_month"]` | green "Now booking … jobs" capacity line (only if true) | `"January"` |
| `WARRANTY_TERMS` | "No surprises" block, warranty FAQ | his written terms, verbatim |
| `CREDENTIALS` (abn, public_liability, licence…) | footer, schema | – |
| `BA[...]["specs"]` Suburb / Floor size | before/after captions | `"Taree"`, `"36m²"` |
| `PROJECT_SUBURBS`, `OWNER` surname/photo | area pages, about | – |
| Full-res job photos (5–10, straight off his phone) | hero, work grid, project cards | biggest single upgrade |
| Is "New customers save $250" auto-applied, or "mention it"? | offer copy | copy currently says "on their first floor" |

## From Zach
| Slot | What it turns on |
|---|---|
| `PIXEL_ID` | Meta Pixel PageView on every page, Lead (with eventID) on /thank-you, Contact on tel/sms/WhatsApp taps |
| `GA4_ID` | GA4; events already pushed: form_start, form_step, form_floor_type, form_submit, generate_lead, click_call, click_sms, click_whatsapp |
| Meta Conversions API | Not built. Pixel Lead already carries `eventID` = the form's `event_id`, so a CAPI event (Meta's no-code CAPI setup, or a Formspree webhook to a small function) can be deduplicated against it |
| Privacy page | Add Meta Pixel + Google Analytics wording when either ID goes live |

## Ad links
- `/?h=a` "A garage floor you'll actually want to show off." (default)
- `/?h=b` "Mid North Coast garage floors from $2,450. New customers save $250."
- `/?h=c` "Sick of a cracked, oil-stained garage floor?"

The variant sticks for the session and is sent with the lead as `headline_variant`.
