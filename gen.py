# Generates the static site. Netlify parses HTML at deploy time, so every time
# window and every form field must exist in the file — nothing rendered by JS.
import html, io

PHONE = "13478316599"
PHONE_DISPLAY = "347-831-6599"
PER_SLOT = 2                      # jobs that fit in one time window

SLOTS = {
    "am":  "8:00 AM – 12:00 PM",
    "mid": "12:00 PM – 4:00 PM",
    "pm":  "4:00 PM – 8:00 PM",
}
DAYS = [
    ("Tue Sep 15", ["am", "mid", "pm"], None),
    ("Wed Sep 16", ["am", "mid", "pm"], None),
    ("Thu Sep 17", ["am", "mid", "pm"], None),
    ("Fri Sep 18", ["am"],              "Half day"),
    ("Tue Sep 22", ["am", "mid", "pm"], None),
    ("Wed Sep 23", ["am", "mid", "pm"], None),
    ("Thu Sep 24", ["am", "mid", "pm"], None),
]

def e(s):
    return html.escape(str(s), quote=True)

WINDOWS = [(lbl, SLOTS[s]) for lbl, sl, _t in DAYS for s in sl]
TOTAL_SLOTS = len(WINDOWS) * PER_SLOT

CSS = """
  :root{
    --paper:#ede5cf; --panel:#e4dabd; --ink:#17130f; --accent:#46215f;
    --muted:#857f70; --rule:rgba(23,19,15,.20); --rule-2:rgba(23,19,15,.34);
    --tag-bg:rgba(199,154,61,.22); --tag-fg:#6b4d13;
    --field:#f3ecda; --on-accent:#ede5cf;
  }
  @media (prefers-color-scheme:dark){
    :root:not([data-theme="light"]){
      --paper:#17130f; --panel:#221c16; --ink:#ede5cf; --accent:#c79a3d;
      --muted:#9b9282; --rule:rgba(237,229,207,.18); --rule-2:rgba(237,229,207,.32);
      --tag-bg:rgba(199,154,61,.28); --tag-fg:#f0d089;
      --field:#2b241c; --on-accent:#17130f;
    }
  }
  :root[data-theme="dark"]{
    --paper:#17130f; --panel:#221c16; --ink:#ede5cf; --accent:#c79a3d;
    --muted:#9b9282; --rule:rgba(237,229,207,.18); --rule-2:rgba(237,229,207,.32);
    --tag-bg:rgba(199,154,61,.28); --tag-fg:#f0d089;
    --field:#2b241c; --on-accent:#17130f;
  }

  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{
    margin:0; background:var(--paper); color:var(--ink);
    font-family:"Work Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
    font-size:16px; line-height:1.55; padding:26px 18px 56px;
  }
  .wrap{max-width:900px;margin:0 auto}
  .eyebrow{
    font-family:"Space Mono",ui-monospace,monospace;font-size:11px;font-weight:700;
    letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 8px;
  }
  h1{
    font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;
    letter-spacing:.005em;font-size:clamp(34px,7vw,54px);line-height:.98;
    margin:0 0 14px;text-wrap:balance;
  }
  h2.sec{
    font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;
    font-size:27px;line-height:1;margin:38px 0 6px;letter-spacing:.005em;
  }
  .how{border-left:3px solid var(--accent);padding:2px 0 2px 13px;margin:0 0 22px;font-size:15.5px}
  .lede{color:var(--muted);margin:0 0 16px;font-size:15px}

  .stats{
    display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
    background:var(--rule);border:1px solid var(--rule);margin:0 0 26px;
  }
  .stat{background:var(--paper);padding:14px 16px}
  .stat .n{
    font-family:Anton,Impact,sans-serif;font-size:36px;line-height:1;display:block;
    margin-bottom:5px;font-variant-numeric:tabular-nums;
  }
  .stat.hot .n{color:var(--accent)}
  .stat .k{font-size:12px;color:var(--muted)}

  .board{display:grid;grid-template-columns:repeat(auto-fill,minmax(252px,1fr));gap:16px}
  .day{border:1px solid var(--rule-2);background:var(--panel)}
  .day-hd{
    padding:12px 15px;border-bottom:1px solid var(--rule-2);
    display:flex;align-items:baseline;justify-content:space-between;gap:10px;
  }
  .day-hd h3{
    font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;
    font-size:22px;line-height:1;margin:0;letter-spacing:.01em;
  }
  .tag{
    font-family:"Space Mono",ui-monospace,monospace;font-size:10px;font-weight:700;
    letter-spacing:.09em;text-transform:uppercase;color:var(--tag-fg);
    background:var(--tag-bg);padding:4px 7px;white-space:nowrap;
  }
  .times{display:flex;flex-direction:column;gap:1px;background:var(--rule)}
  button.slot{
    background:var(--panel);color:inherit;border:0;width:100%;text-align:left;
    display:flex;align-items:center;justify-content:space-between;gap:12px;
    padding:15px;min-height:56px;cursor:pointer;font-family:inherit;
  }
  button.slot:hover,button.slot:focus-visible{background:var(--accent);color:var(--on-accent)}
  button.slot:hover .go,button.slot:focus-visible .go{color:var(--on-accent)}
  button.slot[aria-pressed="true"]{background:var(--accent);color:var(--on-accent)}
  button.slot[aria-pressed="true"] .go{color:var(--on-accent)}
  .picked{
    font-family:"Space Mono",ui-monospace,monospace;font-size:13px;font-weight:700;
    background:var(--field);border:1px solid var(--rule-2);padding:11px;
  }
  .picked.none{color:var(--muted);font-weight:400}
  .slot .t{
    font-family:"Space Mono",ui-monospace,monospace;font-size:14px;font-weight:700;
    letter-spacing:.02em;font-variant-numeric:tabular-nums;
  }
  .slot .go{
    font-family:"Space Mono",ui-monospace,monospace;font-size:10.5px;font-weight:700;
    letter-spacing:.08em;text-transform:uppercase;color:var(--accent);white-space:nowrap;
  }


  form{border:1px solid var(--rule-2);background:var(--panel);padding:16px;display:grid;gap:12px}
  label{display:grid;gap:5px;font-size:13px;font-weight:600}
  input,select,textarea{
    font-family:inherit;font-size:16px;padding:11px;width:100%;
    background:var(--field);color:var(--ink);border:1px solid var(--rule-2);border-radius:0;
  }
  textarea{min-height:78px;resize:vertical}
  button[type=submit]{
    font-family:"Space Mono",ui-monospace,monospace;font-size:12px;font-weight:700;
    letter-spacing:.09em;text-transform:uppercase;padding:14px;cursor:pointer;
    background:var(--accent);color:var(--on-accent);border:1px solid var(--accent);
  }
  button[type=submit]:hover{opacity:.9}
  .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}

  .foot{border-top:2px solid var(--ink);margin-top:40px;padding-top:18px}
  .foot .lbl{
    font-family:"Space Mono",ui-monospace,monospace;font-size:11px;font-weight:700;
    letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 6px;
  }
  .foot a.tel{
    font-family:Anton,Impact,sans-serif;font-size:clamp(34px,8vw,48px);line-height:1;
    color:inherit;text-decoration:none;display:inline-block;font-variant-numeric:tabular-nums;
  }
  .foot a.tel:hover{color:var(--accent)}
  .foot p{color:var(--muted);font-size:14px;margin:10px 0 0}
  :focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Work+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap">
<style>%(css)s</style>
</head>
<body>
"""

def build_index():
    o = io.StringIO()
    o.write(HEAD % {
        "title": "Book Your Sukkah | C.H. Sukkah Building",
        "desc": "Pick a time and we'll build your sukkah. Brooklyn, Monsey and the tri-state area.",
        "css": CSS,
    })
    o.write('<div class="wrap">\n')
    o.write('<p class="eyebrow">C.H. Sukkah Building &middot; Brooklyn, New York</p>\n')
    o.write('<h1>Pick a time for your sukkah</h1>\n')
    o.write('<p class="how">Tap the time you want, then fill in your details below. '
            'We&rsquo;ll confirm it.</p>\n')
    o.write('<div class="stats" id="stats"></div>\n')

    o.write('<div class="board">\n')
    for label, slots, tag in DAYS:
        o.write('<section class="day">\n<div class="day-hd"><h3>%s</h3>' % e(label))
        if tag:
            o.write('<span class="tag">%s</span>' % e(tag))
        o.write('</div>\n<div class="times">\n')
        for s in slots:
            t = SLOTS[s]
            key = "%s, %s" % (label, t)
            o.write('<button type="button" class="slot" data-slot="%s" aria-pressed="false">'
                    '<span class="t">%s</span><span class="go">Choose</span></button>\n'
                    % (e(key), e(t)))
        o.write('</div>\n</section>\n')
    o.write('</div>\n')

    o.write('<h2 class="sec">Your details</h2>\n')
    o.write('<p class="lede">Tap a time above, then fill this in.</p>\n')
    o.write('<form name="sukkah-booking" method="POST" data-netlify="true" '
            'netlify-honeypot="bot-field" action="/thanks.html">\n')
    o.write('  <p class="hp"><label>Skip this field <input name="bot-field" '
            'tabindex="-1" autocomplete="off"></label></p>\n')
    o.write('  <label>Time you picked\n')
    o.write('    <div class="picked none" id="picked">No time chosen yet &mdash; '
            'tap one above</div>\n')
    o.write('    <input type="hidden" name="time" id="time-field" value="">\n')
    o.write('  </label>\n')
    o.write('  <label>Your name<input type="text" name="name" required '
            'autocomplete="name"></label>\n')
    o.write('  <label>Phone number<input type="tel" name="phone" required '
            'autocomplete="tel"></label>\n')
    o.write('  <label>Address where the sukkah goes<input type="text" name="address" '
            'required autocomplete="street-address"></label>\n')
    o.write('  <label>Anything else?<textarea name="notes"></textarea></label>\n')
    o.write('  <button type="submit">Book this time</button>\n')
    o.write('</form>\n')

    o.write('<h2 class="sec">None of these times work?</h2>\n')
    o.write('<p class="lede">Tell us the days and times that suit you and we&rsquo;ll '
            'do our best to fit you in.</p>\n')
    o.write('<form name="sukkah-other-time" method="POST" data-netlify="true" '
            'netlify-honeypot="bot-field" action="/thanks.html">\n')
    o.write('  <p class="hp"><label>Skip this field <input name="bot-field" '
            'tabindex="-1" autocomplete="off"></label></p>\n')
    o.write('  <label>Your name<input type="text" name="name" required '
            'autocomplete="name"></label>\n')
    o.write('  <label>Phone<input type="tel" name="phone" required '
            'autocomplete="tel"></label>\n')
    o.write('  <label>When would work for you?<textarea name="when_works" required '
            'placeholder="For example: any morning the week of Sep 21, or Sunday '
            'afternoon"></textarea></label>\n')
    o.write('  <button type="submit">Send my request</button>\n')
    o.write('</form>\n')

    o.write('<div class="foot">\n<p class="lbl">For any questions or more '
            'information</p>\n')
    o.write('<a class="tel" href="tel:+%s">%s</a>\n' % (PHONE, e(PHONE_DISPLAY)))
    o.write('<p>Call or text anytime.</p>\n')
    o.write('</div>\n</div>\n')

    o.write("""<script>
(function(){
  var PER_SLOT = %(per)d;
  var stats = document.getElementById("stats");

  // Recomputed from today's date on every load, so it stays right on its own.
  function daysToSukkos(){
    var start = new Date(2026, 8, 25);   // Fri Sep 25 2026 — Sukkos begins that evening
    var now = new Date();
    return Math.round((start - new Date(now.getFullYear(), now.getMonth(), now.getDate())) / 86400000);
  }
  function dayLabel(d){
    if (d > 1)   return { n: d, k: "Days to erev Sukkos" };
    if (d === 1) return { n: 1, k: "Day to erev Sukkos" };
    if (d === 0) return { n: 0, k: "Erev Sukkos is today" };
    return { n: 0, k: "Sukkos has begun" };
  }
  // Each visible window still holds PER_SLOT jobs, minus any already taken.
  function renderStats(taken){
    taken = taken || {};
    var open = 0;
    document.querySelectorAll("button.slot").forEach(function(el){
      var n = taken[el.getAttribute("data-slot")] || 0;
      open += Math.max(0, PER_SLOT - n);
    });
    var d = dayLabel(daysToSukkos());
    stats.innerHTML =
      '<div class="stat"><span class="n">' + open + '</span>' +
      '<span class="k">Slots still open</span></div>' +
      '<div class="stat hot"><span class="n">' + d.n + '</span>' +
      '<span class="k">' + d.k + '</span></div>';
  }
  renderStats();

  // A window with all its slots taken comes off the board. Missing or bad
  // file: everything stays visible, which fails toward showing too much.
  fetch("booked.json", {cache:"no-store"}).then(function(r){
    return r.ok ? r.json() : null;
  }).then(function(data){
    var taken = (data && data.taken) || {};
    Object.keys(taken).forEach(function(key){
      if ((taken[key] || 0) < PER_SLOT) return;
      document.querySelectorAll('[data-slot="' + CSS.escape(key) + '"]').forEach(function(el){
        el.remove();
      });
    });
    document.querySelectorAll("section.day").forEach(function(sec){
      if (!sec.querySelector("button.slot")) sec.remove();
    });
    renderStats(taken);
  }).catch(function(){ /* leave every time showing */ });

  // Tapping a time fills the booking form.
  var picked = document.getElementById("picked");
  var field  = document.getElementById("time-field");
  var form   = document.querySelector('form[name="sukkah-booking"]');
  document.addEventListener("click", function(ev){
    var btn = ev.target.closest("button.slot");
    if (!btn) return;
    document.querySelectorAll("button.slot").forEach(function(b){
      b.setAttribute("aria-pressed", b === btn ? "true" : "false");
    });
    var val = btn.getAttribute("data-slot");
    field.value = val;
    picked.textContent = val;
    picked.classList.remove("none");
    form.scrollIntoView({ behavior: "smooth", block: "start" });
    var first = form.querySelector('input[name="name"]');
    if (first) setTimeout(function(){ first.focus({ preventScroll: true }); }, 420);
  });
  form.addEventListener("submit", function(ev){
    if (field.value) return;
    ev.preventDefault();
    picked.textContent = "Please tap a time above first";
    picked.classList.remove("none");
    document.querySelector(".board").scrollIntoView({ behavior:"smooth", block:"start" });
  });
})();
</script>
</body>
</html>
""" % {"per": PER_SLOT})
    return o.getvalue()

def build_thanks():
    o = io.StringIO()
    o.write(HEAD % {"title": "Thanks | C.H. Sukkah Building",
                    "desc": "We got your request.", "css": CSS})
    o.write('<div class="wrap">\n')
    o.write('<p class="eyebrow">C.H. Sukkah Building &middot; Brooklyn, New York</p>\n')
    o.write('<h1>We got it</h1>\n')
    o.write('<p class="how">We&rsquo;ll confirm your time shortly. If you need to change it '
            'or something comes up, call or text us.</p>\n')
    o.write('<div class="foot" style="margin-top:26px">\n<p class="lbl">For any questions '
            'or more information</p>\n')
    o.write('<a class="tel" href="tel:+%s">%s</a>\n' % (PHONE, e(PHONE_DISPLAY)))
    o.write('<p><a href="/" style="color:inherit">&larr; Back to the times</a></p>\n')
    o.write('</div>\n</div>\n</body>\n</html>\n')
    return o.getvalue()

open("index.html", "w").write(build_index())
open("thanks.html", "w").write(build_thanks())

print("index.html  %6d bytes" % len(open("index.html").read()))
print("%d time windows x %d = %d bookable slots" % (len(WINDOWS), PER_SLOT, TOTAL_SLOTS))
