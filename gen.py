# Generates the static site. Netlify parses HTML at deploy time, so every slot
# and every form field must exist in the file — nothing rendered by JS.
import html, urllib.parse, io

PHONE = "13478316599"
PHONE_DISPLAY = "347-831-6599"

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
TYPES = ["Pop-up", "Tube frame", "Panel", "Wood", "Custom", "Not sure"]

def wa(day, time):
    msg = "Hi, I'd like to book my sukkah for %s, %s." % (day, time)
    return "https://wa.me/%s?text=%s" % (PHONE, urllib.parse.quote(msg))

def e(s):
    return html.escape(str(s), quote=True)

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
  .wrap{max-width:640px;margin:0 auto}
  .eyebrow{
    font-family:"Space Mono",ui-monospace,monospace;font-size:11px;font-weight:700;
    letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 8px;
  }
  h1{
    font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;
    letter-spacing:.005em;font-size:clamp(34px,9vw,54px);line-height:.98;
    margin:0 0 14px;text-wrap:balance;
  }
  h2.sec{
    font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;
    font-size:26px;line-height:1;margin:36px 0 6px;letter-spacing:.005em;
  }
  .how{border-left:3px solid var(--accent);padding:2px 0 2px 13px;margin:0 0 8px;font-size:15.5px}
  .countdown{
    font-family:"Space Mono",ui-monospace,monospace;font-size:12px;font-weight:700;
    letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
    margin:0 0 26px;font-variant-numeric:tabular-nums;
  }
  .lede{color:var(--muted);margin:0 0 18px;font-size:15px}

  .day{border:1px solid var(--rule-2);background:var(--panel);margin-bottom:14px}
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
  a.slot{
    background:var(--panel);color:inherit;text-decoration:none;
    display:flex;align-items:center;justify-content:space-between;gap:12px;
    padding:15px;min-height:56px;
  }
  a.slot .t{
    font-family:"Space Mono",ui-monospace,monospace;font-size:14px;font-weight:700;
    letter-spacing:.02em;font-variant-numeric:tabular-nums;
  }
  a.slot .go{
    font-family:"Space Mono",ui-monospace,monospace;font-size:10.5px;font-weight:700;
    letter-spacing:.08em;text-transform:uppercase;color:var(--accent);white-space:nowrap;
  }
  a.slot:hover,a.slot:focus-visible{background:var(--accent);color:var(--on-accent)}
  a.slot:hover .go,a.slot:focus-visible .go{color:var(--on-accent)}

  form{border:1px solid var(--rule-2);background:var(--panel);padding:16px;display:grid;gap:12px}
  label{display:grid;gap:5px;font-size:13px;font-weight:600}
  input,select,textarea{
    font-family:inherit;font-size:16px;padding:11px;width:100%;
    background:var(--field);color:var(--ink);border:1px solid var(--rule-2);border-radius:0;
  }
  textarea{min-height:78px;resize:vertical}
  button{
    font-family:"Space Mono",ui-monospace,monospace;font-size:12px;font-weight:700;
    letter-spacing:.09em;text-transform:uppercase;padding:14px;cursor:pointer;
    background:var(--accent);color:var(--on-accent);border:1px solid var(--accent);
  }
  button:hover{opacity:.9}
  .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}

  .foot{border-top:2px solid var(--ink);margin-top:34px;padding-top:18px}
  .foot .lbl{
    font-family:"Space Mono",ui-monospace,monospace;font-size:11px;font-weight:700;
    letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 6px;
  }
  .foot a.tel{
    font-family:Anton,Impact,sans-serif;font-size:clamp(34px,9vw,48px);line-height:1;
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
    o.write('<p class="how">Tap the time that works for you &mdash; it opens a WhatsApp '
            'message to us with that time already filled in. Times that are already taken '
            'are not shown.</p>\n')
    o.write('<p class="countdown" id="countdown"></p>\n')

    for label, slots, tag in DAYS:
        o.write('<section class="day">\n<div class="day-hd"><h3>%s</h3>' % e(label))
        if tag:
            o.write('<span class="tag">%s</span>' % e(tag))
        o.write('</div>\n<div class="times">\n')
        for s in slots:
            t = SLOTS[s]
            key = "%s, %s" % (label, t)
            o.write('<a class="slot" data-slot="%s" href="%s" target="_blank" '
                    'rel="noopener noreferrer">'
                    '<span class="t">%s</span><span class="go">Request &rarr;</span></a>\n'
                    % (e(key), e(wa(label, t)), e(t)))
        o.write('</div>\n</section>\n')

    # Static form — Netlify parses this at deploy; nothing here is JS-generated.
    o.write('<h2 class="sec">Or send your details</h2>\n')
    o.write('<p class="lede">Prefer a form? Send your name and the time you want and '
            'we&rsquo;ll lock it in.</p>\n')
    o.write('<form name="sukkah-booking" method="POST" data-netlify="true" '
            'netlify-honeypot="bot-field" action="/thanks.html">\n')
    o.write('  <p class="hp"><label>Skip this field <input name="bot-field" '
            'tabindex="-1" autocomplete="off"></label></p>\n')
    o.write('  <label>Your name<input type="text" name="name" required '
            'autocomplete="name"></label>\n')
    o.write('  <label>Phone<input type="tel" name="phone" required '
            'autocomplete="tel"></label>\n')
    o.write('  <label>Which time?<select name="preferred_time" id="time-select" required>\n')
    o.write('    <option value="">Choose a time</option>\n')
    for label, slots, _tag in DAYS:
        for sl in slots:
            v = "%s, %s" % (label, SLOTS[sl])
            o.write('    <option data-slot="%s">%s</option>\n' % (e(v), e(v)))
    o.write('  </select></label>\n')
    o.write('  <label>Anything else?<textarea name="notes"></textarea></label>\n')
    o.write('  <button type="submit">Send my request</button>\n')
    o.write('</form>\n')

    o.write('<div class="foot">\n<p class="lbl">Or just call</p>\n')
    o.write('<a class="tel" href="tel:+%s">%s</a>\n' % (PHONE, e(PHONE_DISPLAY)))
    o.write('<p>Free estimate. We build across Brooklyn, Monsey and the tri-state area.</p>\n')
    o.write('</div>\n</div>\n')

    o.write("""<script>
(function(){
  // Hide slots already taken. booked.json is a plain list you edit; if it is
  // missing or unreadable every slot stays visible, which fails safe.
  fetch("booked.json", {cache:"no-store"}).then(function(r){
    return r.ok ? r.json() : null;
  }).then(function(data){
    var full = (data && data.full) || [];
    if (!full.length) return;
    full.forEach(function(key){
      document.querySelectorAll('[data-slot="' + CSS.escape(key) + '"]').forEach(function(el){
        el.remove();
      });
    });
    document.querySelectorAll("section.day").forEach(function(sec){
      if (!sec.querySelector("a.slot")) sec.remove();
    });
  }).catch(function(){ /* keep every slot visible */ });

  var start = new Date(2026, 8, 25);   // Fri Sep 25 2026 — Sukkos begins that evening
  var now = new Date();
  var days = Math.round((start - new Date(now.getFullYear(), now.getMonth(), now.getDate())) / 86400000);
  var el = document.getElementById("countdown");
  if (!el) return;
  el.textContent = days > 1 ? days + " days until Sukkos"
                 : days === 1 ? "Sukkos begins tomorrow evening"
                 : days === 0 ? "Sukkos begins this evening" : "";
})();
</script>
</body>
</html>
""")
    return o.getvalue()

def build_thanks():
    o = io.StringIO()
    o.write(HEAD % {"title": "Thanks | C.H. Sukkah Building",
                    "desc": "We got your request.", "css": CSS})
    o.write('<div class="wrap">\n')
    o.write('<p class="eyebrow">C.H. Sukkah Building &middot; Brooklyn, New York</p>\n')
    o.write('<h1>We got it</h1>\n')
    o.write('<p class="how">We&rsquo;ll be in touch shortly to confirm your time and give you '
            'a price. If it&rsquo;s urgent, call or WhatsApp us.</p>\n')
    o.write('<div class="foot" style="margin-top:26px">\n<p class="lbl">Call or WhatsApp</p>\n')
    o.write('<a class="tel" href="tel:+%s">%s</a>\n' % (PHONE, e(PHONE_DISPLAY)))
    o.write('<p><a href="/" style="color:inherit">&larr; Back to the times</a></p>\n')
    o.write('</div>\n</div>\n</body>\n</html>\n')
    return o.getvalue()

open("index.html", "w").write(build_index())
open("thanks.html", "w").write(build_thanks())

n_slots = sum(len(s) for _l, s, _t in DAYS)
print("index.html  %6d bytes" % len(open("index.html").read()))
print("thanks.html %6d bytes" % len(open("thanks.html").read()))
print("%d slots rendered statically" % n_slots)
