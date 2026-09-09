# C.H. Sukkah Building — booking site

Static pages plus two Netlify Functions. No build step for the HTML; Netlify
installs the function dependencies from `package.json`.

## How a booking claims its time, automatically

1. Someone submits the `sukkah-booking` form.
2. Netlify fires the `submission-created` event.
3. `netlify/functions/submission-created.mjs` runs, reads the chosen time out of
   the submission, and increments its count in the Netlify Blobs store.
4. `netlify/functions/booked.mjs` serves those counts at
   `/.netlify/functions/booked`.
5. The page reads that on load. A time at 2 disappears; when every time on a day
   is gone, the whole day disappears.

Nothing to accept and nothing to edit by hand.

## Marking a time taken yourself

`booked.json` still works as a manual override — useful for a job booked over the
phone:

```json
{ "taken": { "Tue Sep 15, 8:00 AM – 12:00 PM": 1 } }
```

`1` leaves the time up with one slot left, `2` removes it. The page merges this
with the live counts and takes whichever is higher, so a manual entry can only
ever remove availability, never add it back.

If both the function and `booked.json` fail, every time stays visible. It fails
toward showing too much rather than hiding a time you could work.

## Where submissions land

Netlify dashboard → **Forms** → `sukkah-booking` and `sukkah-other-time`.
Form detection must stay enabled, and it only applies to builds made after it was
switched on.

## Changing dates, times, or slots

Edit `DAYS`, `SLOTS` and `PER_SLOT` at the top of `gen.py`, then:

```
python3 gen.py
```

That rewrites `index.html` and `thanks.html`. Commit both.
