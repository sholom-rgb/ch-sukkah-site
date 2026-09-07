# C.H. Sukkah Building — booking site

Static site. No build step. Netlify serves this folder as-is.

## Marking a time as taken

Edit `booked.json` and add the slot's exact text to the `full` list:

```json
{ "full": ["Tue Sep 15, 8:00 AM – 12:00 PM"] }
```

Copy the text verbatim from the page — the time range uses an en-dash (–), not a
hyphen. Commit and push; Netlify redeploys and the slot disappears from both the
tap-to-WhatsApp list and the form's dropdown. When every slot on a day is taken,
the whole day disappears.

If `booked.json` is missing or malformed the site shows every slot. It fails toward
showing too much, never toward hiding a time you could actually work.

## Where bookings arrive

Form submissions land in the Netlify dashboard under **Forms → sukkah-booking**.
Set up an email notification there so they reach you without checking the site.

Netlify detects the form by parsing the HTML at deploy time, which is why every
slot and field is written into `index.html` rather than generated in the browser.

## Changing dates, times, or slots

Edit the `DAYS`, `SLOTS`, and `TYPES` tables at the top of `gen.py`, then:

```
python3 gen.py
```

That rewrites `index.html` and `thanks.html`. Commit both.
